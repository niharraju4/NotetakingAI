import whisper
import numpy as np
from scipy.io.wavfile import write
import os
from src.capture_audio import audio_queue
# Import the audio queue from capture_audio.py



# Load the Whisper model and use GPU (cuda) if available
model = whisper.load_model("base", device="cuda")

def resample_audio(audio_data, orig_sample_rate, target_sample_rate=16000):
    """Resample the audio to the target sample rate."""
    duration = audio_data.shape[0] / orig_sample_rate
    new_length = int(duration * target_sample_rate)
    resampled_audio = np.interp(
        np.linspace(0, duration, new_length),
        np.linspace(0, duration, audio_data.shape[0]),
        audio_data
    )
    return resampled_audio


def transcribe_audio_chunk(audio_chunk):
    """Transcribes a single audio chunk."""
    print("Starting transcription for a new audio chunk...")

    # Save the audio chunk temporarily as a WAV file (if needed for Whisper input)
    temp_wav_file = "temp_audio_chunk.wav"
    from scipy.io.wavfile import write
    write(temp_wav_file, 44100, audio_chunk)

    # Transcribe the audio chunk using Whisper
    result = model.transcribe(temp_wav_file)
    
    # Print transcription result for debugging
    print(f"Transcription result: {result['text']}")

    return result['text']


# Buffer to collect audio chunks for better transcription
audio_buffer = []

def process_audio_queue():
    """Process the audio queue for transcription."""
    transcription_file = os.path.join(os.path.dirname(__file__), '../transcriptions/live_transcription.txt')
    
    while True:
        if not audio_queue.empty():
            audio_chunk = audio_queue.get()
            print(f"Processing audio chunk of size: {len(audio_chunk)}")  # Confirm chunk processing
            
            # Add chunk to the buffer
            audio_buffer.append(audio_chunk)
            
            # Once we have 5 chunks (or 5 seconds of audio), process them together
            if len(audio_buffer) >= 5:
                # Concatenate audio chunks
                combined_audio = np.concatenate(audio_buffer, axis=0)
                
                # Transcribe the combined audio chunk
                transcription = transcribe_audio_chunk(combined_audio)
                
                # Write transcription to file if it's non-empty
                if transcription.strip():  # Check if transcription is non-empty
                    with open(transcription_file, "a") as f:
                        f.write(transcription + "\n")
                    print(f"Transcription written: {transcription}")
                else:
                    print("No transcription available for this chunk.")
                
                # Clear buffer after processing
                audio_buffer.clear()
