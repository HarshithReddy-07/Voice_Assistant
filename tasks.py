# tasks.py
import webbrowser
import os
import smtplib
from dotenv import load_dotenv
from utils import *
from youtube_search import YoutubeSearch
from youtube_downloader import download_video
from weather import get_weather
from task_manager import run_task, announce_active_tasks
from news import get_headlines
from music_player import play_youtube_audio, pause_audio, stop_audio

load_dotenv("config.env")
EMAIL_ID = os.getenv("EMAIL_ID", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")

# ——— LLM ACTION HANDLER ———
def handle_task_action(action: dict):
    cmd = action.get("action")

    # ——— BROWSER & SEARCH ———
    if cmd == "search in browser":
        query = action.get("query")
        if query and query != "None":
            run_task(f"Searching browser for {query}", webbrowser.open, f"https://www.google.com/search?q={query}")
        return

    elif cmd == "open browser":
        run_task("Opening Chrome", os.startfile, r"C:\Program Files\Google\Chrome\Application\chrome.exe")
        return

    elif cmd in ["search in youtube", "play in youtube"]:
        query = action.get("query")
        if query and query != "None":
            url = f"https://www.youtube.com/results?search_query={query}"
            if cmd == "play in youtube":
                results = YoutubeSearch(query, max_results=1).to_dict()
                if results:
                    url = "https://www.youtube.com" + results[0]["url_suffix"] # pyright: ignore[reportArgumentType]
            run_task(f"YouTube: {query}", webbrowser.open, url)
        return

    elif cmd == "download from youtube":
        query = action.get("query")
        if query and query != "None":
            def yt_download():
                results = YoutubeSearch(query, max_results=1).to_dict()
                if results:
                    url = "https://www.youtube.com" + results[0]["url_suffix"].split("&list")[0] # pyright: ignore[reportArgumentType]
                    run_task(f"Downloading {query}", download_video, url, metadata={"url": url})
                else:
                    speak("Video not found.")
            yt_download()
        return

    # ——— APPS ———
    elif cmd == "open vs":
        run_task("Opening VS Code", os.startfile, r"C:\Users\harsh\AppData\Local\Programs\Microsoft VS Code\Code.exe")
        return

    elif cmd == "open whatsapp":
        run_task("Opening WhatsApp", os.system, "start whatsapp:")
        return ""

    # ——— MUSIC ———
    elif cmd == "play music":
        query = action.get("query")
        if query and query != "None":
            results = YoutubeSearch(query, max_results=1).to_dict()
            if results:
                url = "https://www.youtube.com" + results[0]["url_suffix"]
                url = url.split("&list")[0]
                play_youtube_audio(url)
            else:
                speak("Could not find that song on YouTube.")
        return

    elif cmd in ["pause music"]:
        pause_audio()
        speak("Music paused")
        return

    elif cmd in ["end music" , "stop music"]:
        stop_audio()
        speak("Music stopped")
        return    
    
    elif cmd in ["resume music", "continue music"]:
        speak("Music resumed")
        pause_audio()
        return

    # ——— EMAIL ———
    elif cmd == "send an email":
        speak("Recipient email?")
        to = input("Email: ")
        speak("Message?")
        content = input("Message: ")
        run_task(f"Sending email to {to}", send_email, to, content)

    # ——— WEATHER ———
    elif cmd == "get weather":
        city = action.get("city", "nuzvid")
        def fetch():
            temp = get_weather(city)
            speak(f"Temperature in {city} is {temp} degrees Celsius." if temp else "Weather unavailable.")
        run_task(f"Weather for {city}", fetch)
        return

    # ——— SYSTEM ———
    elif cmd == "increase brightness":
        step = action.get("step", 10)
        run_task(f"Brightness +{step}", increase_brightness, step)
        return
    
    elif cmd == "decrease brightness":
        step = action.get("step", 10)
        run_task(f"Brightness -{step}", decrease_brightness, step)
        return
    
    elif cmd == "mute volume":
        run_task("Muting", mute_volume)
        return
    
    elif cmd == "unmute volume":
        run_task("Unmuting", unmute_volume)
        return
    
    elif cmd == "shutdown pc":
        run_task("Shutdown", shutdown_pc)
        return
    
    elif cmd == "restart pc":
        run_task("Restart", restart_pc)
        return

    # ——— NEWS ———
    elif cmd == "get headlines":
        count = action.get("count", 10)
        run_task(f"Getting {count} headlines", lambda: [speak(h) for h in get_headlines(count)])
        return

    # ——— SCREENSHOT ———
    elif cmd in ["take screenshot", "capture screen"]:
        run_task("Taking screenshot", take_screenshot)
        return

    # ——— TASKS ———
    elif cmd == "show my tasks":
        announce_active_tasks()
        return

def send_email(to, content):
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_ID, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ID, to, content)
        server.close()
        speak("Email sent.")
        return
    except Exception as e:
        speak("Failed to send email.")
    return    
