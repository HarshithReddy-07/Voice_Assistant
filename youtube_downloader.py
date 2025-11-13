# youtube_downloader.py
from yt_dlp import YoutubeDL
from utils import speak
import os, json
from datetime import datetime

TASK_STATE_FILE = "task_state.json"

# Ensure downloads directory exists
DOWNLOADS_DIR = os.path.join(os.getcwd(), "downloads")
os.makedirs(DOWNLOADS_DIR, exist_ok=True)


def update_task_status(url: str, status: str):
    """Update a download's task status in task_state.json."""
    try:
        if not os.path.exists(TASK_STATE_FILE):
            return
        with open(TASK_STATE_FILE, "r", encoding="utf-8") as f:
            tasks = json.load(f)
        for t in tasks:
            if t.get("url") == url:
                t["status"] = status
                t["updated_at"] = datetime.now().isoformat()
        with open(TASK_STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(tasks, f, indent=2)
    except Exception as e:
        print(f"⚠️ Could not update task status: {e}")


def download_video(url: str) -> None:
    """Download YouTube video with progress tracking and resume support."""
    speak(f"Starting download for {url}")

    def progress_hook(d):
        if d["status"] == "downloading":
            percent = d.get("_percent_str", "").strip()
            filename = d.get("filename", "")
            print(f"⬇️  Downloading: {filename} - {percent}")
        elif d["status"] == "finished":
            filename = d.get("filename", "")
            print(f"✅ Finished downloading {filename}")
            speak("Download complete.")
            update_task_status(url, "done")

    ydl_opts = {
        "outtmpl": os.path.join(DOWNLOADS_DIR, "%(title)s.%(ext)s"),
        "progress_hooks": [progress_hook],
        "noplaylist": True,
        "continuedl": True,       # resume partial downloads
        "ignoreerrors": True,
        "quiet": True,
        "no_warnings": True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl: # pyright: ignore[reportArgumentType]
            ydl.download([url])
            update_task_status(url, "done")
    except Exception as e:
        speak("An error occurred while downloading.")
        print(f"❌ Download failed: {e}")
        update_task_status(url, "failed")
