# YouTube YT-DLP Chapter MP3 Downloader
A Python application that downloads audio from YouTube videos and automatically splits it into MP3 segments based on the video chapters.

---

## Requirements

- Python 3.7 or higher  
- `yt_dlp` library  
- `ffmpeg` installed and added to your system PATH  
- `tkinter` (usually included with Python)  
- `colorama` (optional, for console output styling)  

---

## Installation

1. Install Python packages:

```bash
pip install yt-dlp colorama
```

2. Download and install `ffmpeg` from:  
https://ffmpeg.org/download.html  
Make sure to add it to your system PATH.

---

## Running the Program

Run the program with:

```bash
python yt-dlp-chapter-mp3-downloader.py
```

---

## Creating an Executable (Windows) - Optional

You can create a standalone executable using PyInstaller:

1. Install PyInstaller:

```bash
pip install pyinstaller
```

2. From your project folder, run:

```bash
pyinstaller --onefile --noconsole yt-dlp-chapter-mp3-downloader.py
```

- `--onefile`: Creates a single executable file  
- `--noconsole`: Hides the console window (useful for GUI apps)  

3. The executable will be created inside the `dist` folder as `yt-dlp-chapter-mp3-downloader.exe`.

---

## Notes
- Simply enter the YouTube video URL and click "Start".  
---

## License

Feel free to use and modify as you wish.

---

## Contact

If you have any issues or suggestions, please open an issue on the repository.
