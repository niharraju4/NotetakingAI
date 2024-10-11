import whisper
import numpy as np
from scipy.io.wavfile import write
import os  # For handling file paths
import librosa  # For audio processing like resampling
from src.capture_audio import audio_queue  # Import the audio queue from capture_audio.py

# Load the Whisper model and use GPU (cuda) if available
model = whisper.load_model("base", device="cuda")

def transcribe_audio_chunk(chunk, sample_rate=44100):
    """Transcribe a chunk of audio using Whisper."""
    chunk = np.mean(chunk, axis=1)  # Convert stereo to mono
    chunk_resampled = librosa.resample(chunk, orig_sr=sample_rate, target_sr=16000)  # Resample to 16kHz
    
    # Save chunk to a temporary wav file for Whisper processing
    temp_wav_file = "temp_chunk.wav"
    write(temp_wav_file, 16000, chunk_resampled.astype(np.float32))
    
    # Transcribe the audio chunk using Whisper
    result = model.transcribe(temp_wav_file)
    
    transcription = result["text"]
    print(f"Whisper transcription result: {transcription}")  # Print the transcription result
    
    # Clean up the temporary file after transcription
    if os.path.exists(temp_wav_file):
        os.remove(temp_wav_file)
    
    return transcription


def process_audio_queue():
    """Process the audio queue for transcription."""
    transcription_file = os.path.join(os.path.dirname(__file__), '../transcriptions/live_transcription.txt')
    
    while True:
        if not audio_queue.empty():
            audio_chunk = audio_queue.get()
            print(f"Processing audio chunk of size: {len(audio_chunk)}")  # Print to confirm chunk processing
            
            # Transcribe the audio chunk
            transcription = transcribe_audio_chunk(audio_chunk)
            
            # Write transcription to file if it's non-empty
            if transcription.strip():  # Check if transcription is non-empty
                with open(transcription_file, "a") as f:
                    f.write(transcription + "\n")
                print(f"Transcription written: {transcription}")
            else:
                print("No transcription available for this chunk.")
