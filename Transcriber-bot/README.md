transcriber-bot/
│
├── recordings/                   # Folder to store the captured audio
│   └── live_audio.wav            # Example audio file from system recording
│
├── transcriptions/               # Folder to store transcriptions
│   └── live_transcription.txt    # Real-time transcription storage
│
├── src/                          # Folder for source code
│   ├── capture_audio.py          # Captures system audio in chunks (real-time)
│   ├── transcriber.py            # Transcribes audio chunks in real-time
│   ├── typer.py                  # Types the transcription to WordPad or any text editor
│   └── controller.py             # Pause/resume functionality and chunk-based processing
│
├── requirements.txt              # File listing dependencies
├── main.py                       # Main script for combining everything
└── README.md                     # Documentation
