import datetime, os, json, time
from utils import speak, take_command
from reminders import set_reminder, check_reminders
from tasks import perform_task
from news import get_headlines
from task_manager import run_task

today = datetime.datetime.today()
yesterday = today - datetime.timedelta(days=1)
today = today.strftime('%Y-%m-%d')
yesterday = yesterday.strftime('%Y-%m-%d')

FIRST_RUN_FILE = f"{today}.json"

def wish_me(start=True):
    hour = datetime.datetime.now().hour
    if start:
        greet = "Good Morning" if hour < 12 else "Good Afternoon" if hour < 18 else "Good Evening"
        speak(f"{greet}! I am Jarvis, your desktop voice assistant.")
    else:
        speak("Goodbye sir.")
        if hour < 12:
            speak("Have a good day!")
        else:
            speak("Have a good night!")

def handle_first_run():
    if os.path.exists(f"{yesterday}.json"):
        os.remove(f"{yesterday}.json")

    if not os.path.exists(FIRST_RUN_FILE):
        speak("This seems to be your first time starting me!")
        speak("Here are today's top headlines:")
        get_headlines(5)

        with open(FIRST_RUN_FILE, "w") as f:
            json.dump({"first_run": False}, f)
    else:
        speak("Welcome back sir!")


def main():
    wish_me()
    handle_first_run()
    run_task("Checking reminders",check_reminders)

    INTRO_TEXT = "Hi Sir, I am Jarvis your desktop voice assistant. I can perform basic tasks for you."

    while True:
        query = take_command()
        if query == "None":
            time.sleep(1)
            continue

        if "hello jar" in query:
            speak("Hi sir! How can I help you?")

            while True:
                query = take_command()
                if query is None:
                    continue

                if "set reminder" in query:
                    set_reminder()

                elif "introduce yourself" in query:
                    speak(INTRO_TEXT)

                elif "thank you jarv" in query or "go to sleep" in query:
                    speak("You're welcome sir!")
                    break

                elif "goodbye" in query:
                    wish_me(False)
                    exit(0)

                else:
                    perform_task(query)

        elif "goodbye" in query:
            wish_me(False)
            exit(0)

if __name__ == "__main__":
    main()
