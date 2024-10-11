import keyboard
import time

def type_text(text):
    """Simulates typing the transcription into WordPad."""
    for char in text:
        keyboard.write(char)
        time.sleep(0.01)  # Simulate typing speed

def type_transcription_in_real_time():
    """Reads transcription from file and types it."""
    while True:
        with open("transcriptions/live_transcription.txt", "r") as file:
            text = file.read()  # Read the latest transcription
            if text:
                type_text(text)
        time.sleep(5)  # Wait and check for more text every 5 seconds
