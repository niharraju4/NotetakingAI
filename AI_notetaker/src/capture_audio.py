import sounddevice as sd
from queue import Queue
import numpy as np

# Queue to store audio chunks for transcription
audio_queue = Queue()

def capture_system_audio_in_chunks(chunk_duration=5, sample_rate=44100, device_index=None):
    """Capture system audio in chunks and store them in the audio queue."""
    
    def callback(indata, frames, time, status):
        if status:
            print(f"Warning: {status}")
        audio_chunk = indata.copy()  # Capture current chunk

        # Print first few audio samples for debugging
        print(f"First few audio samples: {audio_chunk[:10]}")

        if not audio_queue.full():
            audio_queue.put(audio_chunk)
            print(f"Captured audio chunk of size: {len(audio_chunk)}")
        else:
            print("Warning: Audio queue is full, skipping chunk...")

    # Start streaming system audio with WASAPI loopback
    with sd.InputStream(callback=callback, device=device_index, channels=1, samplerate=sample_rate, blocksize=int(sample_rate * chunk_duration)):
        print("Recording system audio in chunks...")
        while True:
            sd.sleep(int(chunk_duration * 1000))  # Sleep for chunk duration in milliseconds


def list_audio_devices():
    """List all available audio devices."""
    print(sd.query_devices())
