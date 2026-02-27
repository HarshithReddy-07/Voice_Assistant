import speech_recognition as sr
import subprocess
import screen_brightness_control as sbc
from pycaw.pycaw import AudioUtilities
import os
import subprocess
import pyautogui
import win32com.client
import pythoncom
import datetime
import threading

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
        # os.startfile(filepath)

        # Copy path to clipboard
        import pyperclip
        pyperclip.copy(filepath)

        speak(f"Screenshot captured. Path copied to clipboard.")
        print(f"Screenshot saved at: {filepath}")
    except Exception as e:
        print(f"Screenshot failed: {e}")
        speak("Sorry sir, I couldn't take the screenshot.")


# def close_youtube_tab():
#     """Attempt to find a browser window with YouTube and close the tab."""
#     def callback(hwnd, _):
#         if win32gui.IsWindowVisible(hwnd):
#             title = win32gui.GetWindowText(hwnd)
#             # Check for YouTube in title (common in Chrome, Edge, Firefox)
#             if "YouTube" in title:
#                 try:
#                     # Bring window to front
#                     win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
#                     win32gui.SetForegroundWindow(hwnd)
#                     time.sleep(0.5) # Wait for focus
#                     pyautogui.hotkey('ctrl', 'w')
#                     print(f"Closed YouTube tab in: {title}")
#                 except Exception as e:
#                     print(f"Failed to close YouTube tab: {e}")
#                 return # Stop after finding first logic
    
#     try:
#         win32gui.EnumWindows(callback, None)
#     except Exception as e:
#         print(f"Window enumeration failed: {e}")

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