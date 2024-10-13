import whisper

# Load the Whisper model
model = whisper.load_model("base", device="cuda")  # Ensure GPU usage

# Transcribe the recorded audio file
result = model.transcribe("recordings/static_test.wav")
print(f"Transcription result: {result['text']}")
