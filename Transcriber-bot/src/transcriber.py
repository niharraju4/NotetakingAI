import whisper
import numpy as np
from src.capture_audio import audio_queue  # Import the audio queue from capture_audio.py

model = whisper.load_model("base")

def transcribe_audio_chunk(chunk):
    """Transcribe a chunk of audio using Whisper."""
    # Whisper expects audio in a NumPy array format
    chunk = np.mean(chunk, axis=1)  # Convert stereo to mono
    result = model.transcribe(chunk)  # Whisper can take audio file paths or NumPy arrays
    return result["text"]

def process_audio_queue():
    """Process the audio queue for transcription."""
    while True:
        if not audio_queue.empty():
            audio_chunk = audio_queue.get()
            transcription = transcribe_audio_chunk(audio_chunk)
            with open("transcriptions/live_transcription.txt", "a") as f:
                f.write(transcription + "\n")
