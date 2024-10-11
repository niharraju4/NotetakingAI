import threading
import time
from src.transcriber import process_audio_queue

pause_flag = threading.Event()  # Event flag to pause/resume

def pause_transcription():
    """Pause the transcription."""
    pause_flag.set()

def resume_transcription():
    """Resume the transcription."""
    pause_flag.clear()

def transcribe_in_control():
    """Handle transcription with pause/resume control."""
    while True:
        if not pause_flag.is_set():
            process_audio_queue()  # Continue transcription if not paused
        time.sleep(1)
