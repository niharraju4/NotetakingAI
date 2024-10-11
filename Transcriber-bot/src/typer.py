import keyboard
import time
import os

# Define the correct path for the live_transcription.txt file
transcription_file = os.path.join(os.path.dirname(__file__), '../transcriptions/live_transcription.txt')

def type_text(text):
    """Simulates typing the transcription into WordPad."""
    for char in text:
        keyboard.write(char)
        time.sleep(0.01)  # Simulate typing speed

def type_transcription_in_real_time():
    """Reads transcription from file and types it."""
    while True:
        with open(transcription_file, "r") as file:
            text = file.read()  # Read the latest transcription
            if text:
                type_text(text)
        time.sleep(5)  # Wait and check for more text every 5 seconds
