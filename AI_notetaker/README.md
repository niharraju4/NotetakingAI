Certainly! Below is a merged README file that combines the detailed explanations of all the modules and the `main.py` file into one cohesive document.

---

# Project Overview

This project captures system audio, transcribes it using a speech recognition model, summarizes the transcription using a language model, and types the transcription in real-time into a text editor like WordPad. The project is divided into several modules, each responsible for a specific task.

## Table of Contents

1. [Introduction](#introduction)
2. [Capture Audio](#capture-audio)
    - [Imports](#imports)
    - [Global Variables](#global-variables)
    - [Capture System Audio in Chunks](#capture-system-audio-in-chunks)
    - [List Audio Devices](#list-audio-devices)
3. [Controller](#controller)
    - [Imports](#imports-1)
    - [Global Variables](#global-variables-1)
    - [Pause Transcription](#pause-transcription)
    - [Resume Transcription](#resume-transcription)
    - [Transcribe in Control](#transcribe-in-control)
4. [Record Audio](#record-audio)
    - [Imports](#imports-2)
    - [Record Audio to File](#record-audio-to-file)
5. [Transcribe Static](#transcribe-static)
    - [Imports](#imports-3)
    - [Transcribe Recorded Audio File](#transcribe-recorded-audio-file)
6. [Transcriber](#transcriber)
    - [Imports](#imports-4)
    - [Global Variables](#global-variables-2)
    - [Summarize with OpenAI](#summarize-with-openai)
    - [Transcribe Audio Chunk](#transcribe-audio-chunk)
    - [Process Audio Queue](#process-audio-queue)
7. [Typer](#typer)
    - [Imports](#imports-5)
    - [Global Variables](#global-variables-3)
    - [Type Text](#type-text)
    - [Type Transcription in Real Time](#type-transcription-in-real-time)
8. [Main](#main)
    - [Imports](#imports-6)
    - [Global Variables](#global-variables-4)
    - [Main Function](#main-function)
        - [List Audio Devices](#list-audio-devices-1)
        - [Set Device Index](#set-device-index)
        - [Ensure Transcription File and Folder Exist](#ensure-transcription-file-and-folder-exist)
        - [Start Capturing System Audio in Chunks](#start-capturing-system-audio-in-chunks)
        - [Start Transcription Process in Control](#start-transcription-process-in-control)
        - [Start Typing Transcription in Real-Time](#start-typing-transcription-in-real-time)
        - [Simulate Pause/Resume Control](#simulate-pause-resume-control)

---

## Capture Audio

### Imports
```python
import sounddevice as sd
from queue import Queue
import numpy as np
```

### Global Variables
```python
audio_queue = Queue()
```

### Capture System Audio in Chunks
```python
def capture_system_audio_in_chunks(chunk_duration=5, sample_rate=44100, device_index=None):
    """Capture system audio in chunks and store them in the audio queue."""

    def callback(indata, frames, time, status):
        if status:
            print(f"Warning: {status}")
        audio_chunk = indata.copy()  # Capture current chunk

        # Print first few audio samples for debugging
        print(f"First few audio samples: {audio_chunk[:10]}")

        if not audio_queue.full():
            audio_queue.put(audio_chunk)
            print(f"Captured audio chunk of size: {len(audio_chunk)}")
        else:
            print("Warning: Audio queue is full, skipping chunk...")

    # Start streaming system audio with WASAPI loopback
    with sd.InputStream(callback=callback, device=device_index, channels=1, samplerate=sample_rate, blocksize=int(sample_rate * chunk_duration)):
        print("Recording system audio in chunks...")
        while True:
            sd.sleep(int(chunk_duration * 1000))  # Sleep for chunk duration in milliseconds
```

### List Audio Devices
```python
def list_audio_devices():
    """List all available audio devices."""
    print(sd.query_devices())
```

---

## Controller

### Imports
```python
import threading
import time
from src.transcriber import process_audio_queue
```

### Global Variables
```python
pause_flag = threading.Event()  # Event flag to pause/resume
```

### Pause Transcription
```python
def pause_transcription():
    """Pause the transcription."""
    pause_flag.set()
```

### Resume Transcription
```python
def resume_transcription():
    """Resume the transcription."""
    pause_flag.clear()
```

### Transcribe in Control
```python
def transcribe_in_control():
    """Handle transcription with pause/resume control."""
    while True:
        if not pause_flag.is_set():
            process_audio_queue()  # Continue transcription if not paused
        time.sleep(1)
```

---

## Record Audio

### Imports
```python
import sounddevice as sd
from scipy.io.wavfile import write
```

### Record Audio to File
```python
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
```

---

## Transcribe Static

### Imports
```python
import whisper
```

### Transcribe Recorded Audio File
```python
# Load the Whisper model
model = whisper.load_model("base", device="cuda")  # Ensure GPU usage

# Transcribe the recorded audio file
result = model.transcribe("recordings/static_test.wav")
print(f"Transcription result: {result['text']}")
```

---

## Transcriber

### Imports
```python
import whisper
import numpy as np
import openai
from scipy.io.wavfile import write
import os
from dotenv import load_dotenv
from src.capture_audio import audio_queue
```

### Global Variables
```python
# Load the .env file to get environment variables
load_dotenv()

# Load the Whisper model and use GPU (cuda) if available
model = whisper.load_model("base", device="cuda")

# Set your OpenAI API key from the .env file
openai.api_key = os.getenv("OPENAI_API_KEY")
```

### Summarize with OpenAI
```python
def summarize_with_openai(transcription):
    """Send transcription to OpenAI GPT model and return the summarized important notes."""
    response = openai.ChatCompletion.create(
        model="gpt-4",  # You can use gpt-3.5-turbo for a cheaper option
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Summarize the following transcript into key points:\n\n{transcription}\n\nSummarized important notes:"}
        ],
        max_tokens=150,  # Adjust based on how much detail you want
        temperature=0.5,  # Controls randomness, 0.5 is fairly balanced
    )

    # Extract the summarized response from the API result
    important_notes = response['choices'][0]['message']['content'].strip()
    return important_notes
```

### Transcribe Audio Chunk
```python
def transcribe_audio_chunk(audio_chunk):
    """Transcribes a single audio chunk."""
    print("Starting transcription for a new audio chunk...")

    # Save the audio chunk temporarily as a WAV file (if needed for Whisper input)
    temp_wav_file = "temp_audio_chunk.wav"
    write(temp_wav_file, 44100, audio_chunk)

    # Transcribe the audio chunk using Whisper
    result = model.transcribe(temp_wav_file)
    transcription = result['text']

    # Use OpenAI GPT to summarize important notes
    important_notes = summarize_with_openai(transcription)

    # Print transcription and summary for debugging
    print(f"Complete transcription: {transcription}")
    print(f"Important notes: {important_notes}")

    return transcription, important_notes
```

### Process Audio Queue
```python
def process_audio_queue():
    """Process the audio queue for transcription."""
    complete_transcription_file = os.path.join(os.path.dirname(__file__), '../transcriptions/complete_transcription.txt')
    important_notes_file = os.path.join(os.path.dirname(__file__), '../transcriptions/important_notes.txt')

    while True:
        if not audio_queue.empty():
            audio_chunk = audio_queue.get()
            print(f"Processing audio chunk of size: {len(audio_chunk)}")

            # Transcribe and summarize the chunk
            complete_transcription, important_notes = transcribe_audio_chunk(audio_chunk)

            # Write full transcription to the complete transcription file
            if complete_transcription.strip():
                with open(complete_transcription_file, "a") as f:
                    f.write(complete_transcription + "\n")
                print(f"Complete transcription written: {complete_transcription}")
            else:
                print("No transcription available for this chunk.")

            # Write important notes to the important notes file
            if important_notes.strip():
                with open(important_notes_file, "a") as f:
                    f.write(important_notes + "\n")
                print(f"Important notes written: {important_notes}")
            else:
                print("No important notes found for this chunk.")
```

---

## Typer

### Imports
```python
import keyboard
import time
import os
```

### Global Variables
```python
# Define the correct path for the live_transcription.txt file
transcription_file = os.path.join(os.path.dirname(__file__), '../transcriptions/live_transcription.txt')
```

### Type Text
```python
def type_text(text):
    """Simulates typing the transcription into WordPad."""
    for char in text:
        keyboard.write(char)
        time.sleep(0.01)  # Simulate typing speed
```

### Type Transcription in Real Time
```python
def type_transcription_in_real_time():
    """Reads transcription from file and types it."""
    while True:
        with open(transcription_file, "r") as file:
            text = file.read()  # Read the latest transcription
            if text:
                type_text(text)
        time.sleep(5)  # Wait and check for more text every 5 seconds
```

---

## Main

### Imports
```python
from threading import Thread
from src.capture_audio import capture_system_audio_in_chunks, list_audio_devices
from src.transcriber import process_audio_queue
from src.typer import type_transcription_in_real_time
from src.controller import transcribe_in_control, pause_transcription, resume_transcription
import os
import time
from dotenv import load_dotenv
```

### Global Variables
```python
# Load the .env file to get environment variables
load_dotenv()
```

### Main Function
```python
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
```

#### List Audio Devices
```python
list_audio_devices()
```
This function lists all available audio devices to help identify the WASAPI loopback device index.

#### Set Device Index
```python
device_index = 50  # Example: WASAPI loopback device for speakers (update based on your device index)
```
This sets the device index to the WASAPI loopback device. You should update this index based on your specific device configuration.

#### Ensure Transcription File and Folder Exist
```python
transcription_file = os.path.join(os.path.dirname(__file__), 'transcriptions/live_transcription.txt')
os.makedirs(os.path.dirname(transcription_file), exist_ok=True)
with open(transcription_file, "a") as f:
    f.write("")  # Create an empty file if it doesn't exist
```
This ensures that the transcription file and its containing folder exist. If the file does not exist, it creates an empty file.

#### Start Capturing System Audio in Chunks
```python
audio_capture_thread = Thread(target=capture_system_audio_in_chunks, args=(5, 44100, device_index))
audio_capture_thread.start()
```
This starts a thread to capture system audio in chunks. The `capture_system_audio_in_chunks` function is called with the specified chunk duration, sample rate, and device index.

#### Start Transcription Process in Control
```python
transcription_thread = Thread(target=transcribe_in_control)
transcription_thread.start()
```
This starts a thread to handle the transcription process with pause/resume control. The `transcribe_in_control` function is called to manage the transcription process.

#### Start Typing Transcription in Real-Time
```python
typing_thread = Thread(target=type_transcription_in_real_time)
typing_thread.start()
```
This starts a thread to type the transcription in real-time. The `type_transcription_in_real_time` function is called to handle the typing process.

#### Simulate Pause/Resume Control
```python
time.sleep(60)  # Wait for 60 seconds
pause_transcription()
time.sleep(10)  # Pause for 10 seconds
resume_transcription()
```
This simulates pausing and resuming the transcription process after a specified duration. The `pause_transcription` and `resume_transcription` functions are called to control the transcription process.

---

### Running the Main Function
```python
if __name__ == "__main__":
    main()
```
This ensures that the `main` function is called when the script is executed directly.

---

This merged README file should provide a comprehensive overview of the entire project, including detailed explanations of each module and the `main.py` file.
