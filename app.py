import streamlit as st
import sounddevice as sd
import numpy as np
import queue
import threading
import whisper
import openai
from scipy.io.wavfile import write
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Global variables
audio_queue = queue.Queue()
pause_flag = threading.Event()
model = whisper.load_model("base", device="cuda" if whisper.available_devices() else "cpu")

def capture_system_audio(chunk_duration, sample_rate, device_index):
    def callback(indata, frames, time, status):
        if status:
            st.warning(f"Warning: {status}")
        audio_chunk = indata.copy()
        if not audio_queue.full():
            audio_queue.put(audio_chunk)

    with sd.InputStream(callback=callback, device=device_index, channels=1, samplerate=sample_rate, blocksize=int(sample_rate * chunk_duration)):
        while True:
            if st.session_state.get('stop_capture'):
                break
            sd.sleep(int(chunk_duration * 1000))

def summarize_with_openai(transcription):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Summarize the following transcript into key points:\n\n{transcription}\n\nSummarized important notes:"}
        ],
        max_tokens=150,
        temperature=0.5,
    )
    return response['choices'][0]['message']['content'].strip()

def transcribe_audio_chunk(audio_chunk):
    temp_wav_file = "temp_audio_chunk.wav"
    write(temp_wav_file, 44100, audio_chunk)
    result = model.transcribe(temp_wav_file)
    transcription = result['text']
    important_notes = summarize_with_openai(transcription)
    return transcription, important_notes

def process_audio_queue():
    while True:
        if st.session_state.get('stop_processing'):
            break
        if not audio_queue.empty() and not pause_flag.is_set():
            audio_chunk = audio_queue.get()
            transcription, summary = transcribe_audio_chunk(audio_chunk)
            st.session_state.full_transcription += transcription + "\n"
            st.session_state.important_notes += summary + "\n"

def main():
    st.title("Real-time Audio Transcription App")

    if 'full_transcription' not in st.session_state:
        st.session_state.full_transcription = ""
    if 'important_notes' not in st.session_state:
        st.session_state.important_notes = ""
    if 'processing' not in st.session_state:
        st.session_state.processing = False

    devices = sd.query_devices()
    device_options = {f"{i}: {device['name']}": i for i, device in enumerate(devices)}
    selected_device = st.selectbox("Select audio device:", list(device_options.keys()))
    device_index = device_options[selected_device]

    if st.button("Start Transcription"):
        st.session_state.processing = True
        st.session_state.stop_capture = False
        st.session_state.stop_processing = False

        capture_thread = threading.Thread(target=capture_system_audio, args=(5, 44100, device_index))
        process_thread = threading.Thread(target=process_audio_queue)

        capture_thread.start()
        process_thread.start()

    if st.button("Stop Transcription"):
        st.session_state.stop_capture = True
        st.session_state.stop_processing = True
        st.session_state.processing = False

    if st.session_state.processing:
        st.write("Transcription in progress...")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Full Transcription")
        st.text_area("", value=st.session_state.full_transcription, height=300)

    with col2:
        st.subheader("Important Notes")
        st.text_area("", value=st.session_state.important_notes, height=300)

if __name__ == "__main__":
    main()