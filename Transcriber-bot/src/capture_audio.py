import sounddevice as sd
from queue import Queue
import numpy as np

# Queue to store audio chunks for transcription
audio_queue = Queue()

def capture_system_audio_in_chunks(chunk_duration=1, sample_rate=44100):
    """Capture system audio in chunks and store them in the audio queue."""
    
    def callback(indata, frames, time, status):
        if status:
            print(f"Warning: {status}")
        audio_chunk = indata.copy()  # Capture current chunk
        if not audio_queue.full():
            audio_queue.put(audio_chunk)
            print(f"Captured audio chunk of size: {len(audio_chunk)}")
        else:
            print("Warning: Audio queue is full, skipping chunk...")

    # Start streaming system audio with the provided sample rate and chunk duration
    with sd.InputStream(callback=callback, channels=2, samplerate=sample_rate, blocksize=int(sample_rate * chunk_duration)):
        print("Recording system audio in chunks...")
        while True:
            sd.sleep(int(chunk_duration * 1000))  # Sleep for chunk duration in milliseconds

