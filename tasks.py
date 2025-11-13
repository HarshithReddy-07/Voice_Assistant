import webbrowser
import os
import smtplib
from dotenv import load_dotenv
from utils import *
from youtube_search import YoutubeSearch
from youtube_downloader import download_video
from weather import get_weather
from task_manager import run_task, announce_active_tasks, recover_unfinished_youtube_downloads
from news import get_headlines

load_dotenv("config.env")

EMAIL_ID = os.getenv("EMAIL_ID", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")

def send_email(to, content):
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_ID, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ID, to, content)
        server.close()
    except Exception as e:
        print(e)
        speak("Sorry, I couldn't send the email.")


def perform_task(query: str):
    """Perform web or system tasks with tracking."""

    # 🧭 Active task report
    if "show my task" in query or "what's running" in query:
        announce_active_tasks()
        return

    # 🌐 Browsing
    elif "search in browser" in query:
        search = query.replace("search in browser", "").strip()
        run_task(f"Searching for {search} in browser", webbrowser.open, f"https://www.google.com/search?q={search}")

    elif "open browser" in query:
        run_task("Opening Chrome browser", os.startfile, "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe")

    elif "search in youtube" in query:
        search = query.replace("search in youtube", "").strip()
        run_task(f"Searching YouTube for {search}", webbrowser.open, f"https://www.youtube.com/results?search_query={search}")

    # 🎵 YouTube actions
    elif "play in youtube" in query:
        song = query.replace("play in youtube", "").strip()
        def play_video():
            results = YoutubeSearch(song, max_results=1).to_dict()
            if results:
                url = "https://www.youtube.com" + results[0]["url_suffix"] # pyright: ignore[reportArgumentType]
                webbrowser.open(url)
                speak("Playing it on YouTube.")
        run_task(f"Playing {song} on YouTube", play_video)

    elif "download from youtube" in query:
        song = query.replace("download from youtube", "").strip()
        speak(f"Searching YouTube for {song}")

        def yt_download():
            results = YoutubeSearch(song, max_results=1).to_dict()
            if results:
                url = "https://www.youtube.com" + results[0]["url_suffix"] # pyright: ignore[reportArgumentType]
                url = url.split("&list")[0]
                run_task(f"Downloading {song} from YouTube", download_video, url, metadata={"url": url})
            else:
                speak("Video not found.")

        yt_download()

    # 💻 App launch
    elif "open vs" in query:
        run_task("Opening Visual Studio Code", os.startfile, r"C:\Users\harsh\AppData\Local\Programs\Microsoft VS Code\Code.exe")

    elif "open whatsapp" in query:
        run_task("Opening WhatsApp", os.system, "start whatsapp:")

    # 🎧 Music
    elif "play music" in query:
        run_task("Playing your music sequentially", play_music)   

    elif "pause music" in query:
        speak("Pausing music.")
        run_task("Pausing music in Windows Media Player", pause_music)

    elif "resume music" in query or "continue music" in query:
        speak("Resuming your music.")
        run_task("Resuming music in Windows Media Player", resume_music)

    elif "stop music" in query or "end music" in query:
        speak("Stopping music.")
        run_task("Stopping Windows Media Player music", stop_music)
    
    elif "recover unfinished downloads" in query:
        run_task("Recovering unfinished tasks", recover_unfinished_youtube_downloads)

    # 📧 Email
    elif "send an email" in query:
        speak("Enter recipient address: ")
        to = input("Enter recipient address: ")
        speak("Enter email content")
        content = input("Enter email content: ")
        run_task(f"Sending email to {to}", send_email, to, content)

    # 🌦 Weather
    elif "get weather" in query or "check weather" in query:
        city = query.split()[-1]
        print(query)
        def fetch_weather():
            temp = get_weather(city)
            if temp is not None:
                speak(f"Temperature in {city} is {temp} degrees Celsius.")
        run_task(f"Fetching weather for {city}", fetch_weather)

    # 💡 System controls
    elif "increase brightness" in query:
        try:
            step = int(query.split()[-1])
        except:
            step = 10    
        run_task(f"Increasing brightness by {step}", increase_brightness, step)

    elif "decrease brightness" in query:
        try:
            step = int(query.split()[-1])
        except:
            step = 10
        run_task(f"Decreasing brightness by {step}", decrease_brightness, step)

    elif "unmute volume" in query:
        run_task("Unmuting system volume", unmute_volume)
        
    elif "mute volume" in query:
        run_task("Muting system volume", mute_volume)

    elif "shutdown pc" in query:
        run_task("Shutting down PC", shutdown_pc)

    elif "restart pc" in query:
        run_task("Restarting PC", restart_pc)

    elif "get headlines" in query:
        run_task("Getting top headlines", get_headlines, 10)    

    elif "take screenshot" in query or "capture screen" in query:
        run_task("Taking a screenshot", take_screenshot)

    else:
        speak("Task Not found")
        
