import speech_recognition as sr
import subprocess
import screen_brightness_control as sbc
from pycaw.pycaw import AudioUtilities
import os
import subprocess
import time
from mutagen.mp3 import MP3
import random
import pyautogui
import win32com.client
import pythoncom
import datetime
import threading
import time
from pycaw.pycaw import AudioUtilities

music_state = {
    "stop": False,
    "pause": False
}


# Global SAPI voice object — thread-safe, no runAndWait() deadlock
_sapi_voice = None
_sapi_lock = threading.Lock()

def _get_sapi():
    global _sapi_voice
    with _sapi_lock:
        if _sapi_voice is None:
            pythoncom.CoInitialize()
            _sapi_voice = win32com.client.Dispatch("SAPI.SpVoice")
            # Optional: Set voice (uncomment to pick specific voice)
            # voices = _sapi_voice.GetVoices()
            # _sapi_voice.Voice = voices.Item(0)  # First voice
        return _sapi_voice

def speak(text: str):
    """Speak text IMMEDIATELY and RELIABLY using raw SAPI."""
    if not text.strip():
        return
    try:
        voice = _get_sapi()
        with _sapi_lock:
            voice.Speak(text, 1)  # 1 = async (non-blocking), 0 = sync
            # Use 0 for sync if you want to wait
    except Exception as e:
        print(f"[SAPI SPEAK ERROR]: {e}")

def stop_speech():
    """Stop any ongoing speech."""
    try:
        with _sapi_lock:
            if _sapi_voice:
                _sapi_voice.Speak("", 3)  # 3 = purge before speak
    except:
        pass

def take_screenshot():
    """Capture the screen and save with timestamp in user's Pictures."""
    try:
        screenshots_dir = os.path.join(os.path.expanduser("~"), "Pictures", "Jarvis Screenshots")
        os.makedirs(screenshots_dir, exist_ok=True)

        filename = f"jarvis_screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(screenshots_dir, filename)

        image = pyautogui.screenshot()
        image.save(filepath)

        # Open it
        os.startfile(filepath)

        # Copy path to clipboard
        import pyperclip
        pyperclip.copy(filepath)

        speak(f"Screenshot captured and opened. Path copied to clipboard.")
        print(f"Screenshot saved at: {filepath}")
    except Exception as e:
        print(f"Screenshot failed: {e}")
        speak("Sorry sir, I couldn't take the screenshot.")


def get_wmp_player():
    """Return a handle to the running Windows Media Player instance."""
    try:
        return win32com.client.Dispatch("WMPlayer.OCX")
    except Exception:
        return None

def pause_music():
    music_state["pause"] = True
    pyautogui.press('playpause')
    speak("Music paused.")

def resume_music():
    music_state["pause"] = False
    pyautogui.press('playpause')
    speak("Music resumed.")

def stop_music():
    music_state["stop"] = True
    pyautogui.press('playpause')   # or pyautogui.press('stop') if supported
    speak("Music stopped.")


def play_music():
    music_state["stop"] = False
    music_state["pause"] = False
    music_dir = r"C:\Users\harsh\Music"

    songs = [f for f in os.listdir(music_dir) if f.lower().endswith(('.mp3', '.wav', '.aac', '.wma', '.m4a'))]
    if not songs:
        speak("No music files found in your Music folder.")
        return
    speak(f"Playing {len(songs)} songs from your music folder, one after another.")
    random.shuffle(songs)
    for song in songs:
        if music_state["stop"]:
            speak("Stopped playing music.")
            break

        file_path = os.path.join(music_dir, song)
        os.startfile(file_path)

        duration = 180  # default 3 min fallback
        try:
            audio = MP3(file_path)
            duration = int(audio.info.length)
        except Exception:
            pass

        elapsed = 0
        while elapsed < duration:
            if music_state["pause"] or music_state["stop"]:
                time.sleep(1)
                continue

            time.sleep(1)
            elapsed += 1
        # subprocess.Popen(['cmd', '/c', 'start', '', file_path], shell=True)
        # time.sleep(duration + 2)

    speak("All songs finished playing.")


def increase_brightness(step: int = 10):
    sbc.set_brightness(f"+{step}")

def decrease_brightness(step: int = 10):
    sbc.set_brightness(f"-{step}")    

def mute_volume():
    speakers = AudioUtilities.GetSpeakers()
    volume = speakers.EndpointVolume # pyright: ignore[reportOptionalMemberAccess]
    volume.SetMute(1, None)

def unmute_volume():
    speakers = AudioUtilities.GetSpeakers()
    volume = speakers.EndpointVolume # pyright: ignore[reportOptionalMemberAccess]
    volume.SetMute(0, None)  

def shutdown_pc():
    subprocess.run(["shutdown", "/s", "/t", "0"], check=False)

def restart_pc():
    subprocess.run(["shutdown", "/r", "/t", "0"], check=False)

def take_command():
    """Listen for voice input and return recognized text."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("🎤 Listening...")
        recognizer.pause_threshold = 1
        audio = recognizer.listen(source)

    try:
        print("🧠 Recognizing...")
        query = recognizer.recognize_google(audio, language='en-in') # pyright: ignore[reportAttributeAccessIssue]
        print(f"User said: {query}")
        return query.lower()
    except sr.UnknownValueError:
        print("❌ Could not understand audio.")
    except sr.RequestError:
        print("⚠️ Speech service unavailable.")
    return "None"

if __name__ == "__main__" :
    speak("Hello I am Jarivs")
    take_screenshot()