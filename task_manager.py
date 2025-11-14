# task_manager.py
import threading, json, os
from utils import speak
from datetime import datetime
from youtube_downloader import download_video  # for resuming
import time

TASK_STATE_FILE = "task_state.json"
active_tasks = {}

def load_task_state():
    if not os.path.exists(TASK_STATE_FILE):
        return []
    try:
        with open(TASK_STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_task_state(tasks):
    with open(TASK_STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2)

def update_task(description, status, url=None):
    tasks = load_task_state()
    found = False
    for t in tasks:
        if t["description"] == description and t["status"] == "running":
            t["status"] = status
            t["completed_at"] = datetime.now().isoformat()
            if url:
                t["url"] = url
            found = True
            break
    if not found:
        new_task = {
            "description": description,
            "status": status,
            "timestamp": datetime.now().isoformat(),
        }
        if url:
            new_task["url"] = url
        tasks.append(new_task)
    save_task_state(tasks)

def run_task(description: str, func, *args, metadata=None):
    """
    Run a function in background with persistence and optional metadata (like URLs).
    """
    def wrapper():
        speak(f"Started: {description}")
        update_task(description, "running", url=metadata.get("url") if metadata else None)
        try:
            func(*args)
            speak(f"Finished: {description}")
            update_task(description, "done")
        except Exception as e:
            speak(f"Task '{description}' failed.")
            update_task(description, "failed")
        finally:
            if threading.get_ident() in active_tasks:
                del active_tasks[threading.get_ident()]

    t = threading.Thread(target=wrapper, daemon=True)
    t.start()
    active_tasks[t.ident] = {"description": description, "status": "running", "thread": t}
    return t

def list_active_tasks():
    return [t["description"] for t in active_tasks.values() if t["thread"].is_alive()]

def announce_active_tasks():
    running = list_active_tasks()
    if not running:
        past = load_task_state()
        unfinished = [t["description"] for t in past if t["status"] == "running"]
        if unfinished:
            speak("Last session had some unfinished tasks:")
            for t in unfinished:
                speak(t)
        else:
            speak("No active or unfinished tasks.")
    else:
        speak("Currently running tasks are:")
        for task in running:
            speak(task)

def recover_unfinished_youtube_downloads():
    """
    Resume any unfinished YouTube downloads automatically.
    """
    past = load_task_state()
    unfinished = [t for t in past if t["status"] == "running"]
    if unfinished:
        speak("You have unfinished tasks from last session.")
        for task in unfinished:
            desc = task["description"]
            url = task.get("url")
            if "download" in desc.lower() and url:
                speak(f"Resuming YouTube download: {desc}")
                run_task(desc + " (resumed)", download_video, url, metadata={"url": url})
                time.sleep(2)
            else:
                speak(f"{desc} was not completed last time.")
