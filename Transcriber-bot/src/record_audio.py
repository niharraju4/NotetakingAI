import sounddevice as sd
from scipy.io.wavfile import write

def record_audio_to_file(duration=10, filename="recordings/static_test.wav", fs=44100):
    """Record audio and save to a .wav file."""
    print(f"Recording audio for {duration} seconds...")
    audio_data = sd.rec(int(duration * fs), samplerate=fs, channels=2)
    sd.wait()  # Wait for the recording to finish
    write(filename, fs, audio_data)
    print(f"Audio saved to {filename}")

# Test the function
if __name__ == "__main__":
    record_audio_to_file(duration=10)
