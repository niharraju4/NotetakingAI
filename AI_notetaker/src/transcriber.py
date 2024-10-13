import whisper
import numpy as np
import openai
from scipy.io.wavfile import write
import os
from dotenv import load_dotenv
from src.capture_audio import audio_queue

# Load the .env file to get environment variables
load_dotenv()

# Load the Whisper model and use GPU (cuda) if available
model = whisper.load_model("base", device="cuda")

# Set your OpenAI API key from the .env file
openai.api_key = os.getenv("OPENAI_API_KEY")

def summarize_with_openai(transcription):
    """Send transcription to OpenAI GPT model and return the summarized important notes."""
    response = openai.ChatCompletion.create(
        model="gpt-4",  # You can use gpt-3.5-turbo for a cheaper option
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Summarize the following transcript into key points:\n\n{transcription}\n\nSummarized important notes:"}
        ],
        max_tokens=150,  # Adjust based on how much detail you want
        temperature=0.5,  # Controls randomness, 0.5 is fairly balanced
    )
    
    # Extract the summarized response from the API result
    important_notes = response['choices'][0]['message']['content'].strip()
    return important_notes

def transcribe_audio_chunk(audio_chunk):
    """Transcribes a single audio chunk."""
    print("Starting transcription for a new audio chunk...")

    # Save the audio chunk temporarily as a WAV file (if needed for Whisper input)
    temp_wav_file = "temp_audio_chunk.wav"
    write(temp_wav_file, 44100, audio_chunk)

    # Transcribe the audio chunk using Whisper
    result = model.transcribe(temp_wav_file)
    transcription = result['text']

    # Use OpenAI GPT to summarize important notes
    important_notes = summarize_with_openai(transcription)

    # Print transcription and summary for debugging
    print(f"Complete transcription: {transcription}")
    print(f"Important notes: {important_notes}")

    return transcription, important_notes

def process_audio_queue():
    """Process the audio queue for transcription."""
    complete_transcription_file = os.path.join(os.path.dirname(__file__), '../transcriptions/complete_transcription.txt')
    important_notes_file = os.path.join(os.path.dirname(__file__), '../transcriptions/important_notes.txt')
    
    while True:
        if not audio_queue.empty():
            audio_chunk = audio_queue.get()
            print(f"Processing audio chunk of size: {len(audio_chunk)}")

            # Transcribe and summarize the chunk
            complete_transcription, important_notes = transcribe_audio_chunk(audio_chunk)

            # Write full transcription to the complete transcription file
            if complete_transcription.strip():
                with open(complete_transcription_file, "a") as f:
                    f.write(complete_transcription + "\n")
                print(f"Complete transcription written: {complete_transcription}")
            else:
                print("No transcription available for this chunk.")

            # Write important notes to the important notes file
            if important_notes.strip():
                with open(important_notes_file, "a") as f:
                    f.write(important_notes + "\n")
                print(f"Important notes written: {important_notes}")
            else:
                print("No important notes found for this chunk.")
