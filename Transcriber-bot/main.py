from src.capture_audio import capture_system_audio_in_chunks
from src.transcriber import process_audio_queue
from src.typer import type_transcription_in_real_time
from src.controller import transcribe_in_control, pause_transcription, resume_transcription
import threading

def main():
    # Start capturing audio in chunks
    audio_capture_thread = threading.Thread(target=capture_system_audio_in_chunks)
    audio_capture_thread.start()

    # Start transcription process in control (with pause/resume)
    transcription_thread = threading.Thread(target=transcribe_in_control)
    transcription_thread.start()

    # Start typing transcription in real-time
    typing_thread = threading.Thread(target=type_transcription_in_real_time)
    typing_thread.start()

    # Simulate pause/resume control
    time.sleep(60)  # Wait for 60 seconds and then pause
    pause_transcription()
    time.sleep(10)  # Pause for 10 seconds
    resume_transcription()

if __name__ == "__main__":
    main()
