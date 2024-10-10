import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import queue

# Queue to hold the chunks of audio data
audio_queue = queue.Queue()

def capture_system_audio_in_chunks(chunk_duration=5, fs=44100):
    """Captures system audio in real-time and sends chunks to a queue."""
    print("Recording system audio in chunks...")

    def callback(indata, frames, time, status):
        if status:
            print(status)
        audio_queue.put(indata.copy())

    with sd.InputStream(callback=callback, channels=2, samplerate=fs):
        while True:
            sd.sleep(int(chunk_duration * 1000))

# Example usage: capture 5-second chunks
if __name__ == "__main__":
    capture_system_audio_in_chunks()
