from threading import Thread
from src.capture_audio import capture_system_audio_in_chunks, list_audio_devices
from src.transcriber import process_audio_queue
from src.typer import type_transcription_in_real_time
from src.controller import transcribe_in_control, pause_transcription, resume_transcription
import os
import time
from dotenv import load_dotenv

# Load the .env file to get environment variables
load_dotenv()

def main():
    # List devices to find the WASAPI loopback device index
    list_audio_devices()

    # Set the device index to the WASAPI loopback device
    device_index = 50  # Example: WASAPI loopback device for speakers (update based on your device index)

    # Ensure transcription file and folder exist
    transcription_file = os.path.join(os.path.dirname(__file__), 'transcriptions/live_transcription.txt')
    os.makedirs(os.path.dirname(transcription_file), exist_ok=True)
    with open(transcription_file, "a") as f:
        f.write("")  # Create an empty file if it doesn't exist

    # Start capturing system audio in chunks
    audio_capture_thread = Thread(target=capture_system_audio_in_chunks, args=(5, 44100, device_index))
    audio_capture_thread.start()

    # Start transcription process in control (with pause/resume)
    transcription_thread = Thread(target=transcribe_in_control)
    transcription_thread.start()

    # Start typing transcription in real-time
    typing_thread = Thread(target=type_transcription_in_real_time)
    typing_thread.start()

    # Simulate pause/resume control after a few seconds (you can adjust the timing)
    time.sleep(60)  # Wait for 60 seconds
    pause_transcription()
    time.sleep(10)  # Pause for 10 seconds
    resume_transcription()

if __name__ == "__main__":
    main()
