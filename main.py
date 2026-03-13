# main.py
import datetime, os, json, time, threading, dateparser
from utils import speak, take_command
from reminders import check_reminders
from news import get_headlines
from task_manager import run_task
from llm_handler import process_with_llm
from reminders import reminders

today = datetime.datetime.today()
yesterday = today - datetime.timedelta(days=1)
today = today.strftime('%Y-%m-%d')
yesterday = yesterday.strftime('%Y-%m-%d')

FIRST_RUN_FILE = f"{today}.json"

# Global state (lightweight)
reminder_thread = None

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
        headlines = get_headlines(5)
        for i, headline in enumerate(headlines, start=1):
            speak(f"Headline {i}: {headline}")

        with open(FIRST_RUN_FILE, "w") as f:
            json.dump({"first_run": False}, f)
    else:
        speak("Welcome back sir!")

def start_reminder_setup():
    """Start reminder in background so main loop isn't blocked"""
    global reminder_thread
    speak("At what time should I remind you?")
    
    def reminder_flow():
        time_text = take_command()
        if time_text == "cancel_command":
            handle_cancel()
            return
        
        speak("What should I remind you of?")
        content = take_command()
        if content == "cancel_command":
            handle_cancel()
            return
        
        # Save reminder
        import dateparser
        dt = dateparser.parse(time_text)
        if dt:
            reminders.append([dt.hour, dt.minute, content])
            speak("Reminder set successfully.")
        else:
            speak("Sorry, I couldn't understand the time.")
    
    reminder_thread = threading.Thread(target=reminder_flow, daemon=True)
    reminder_thread.start()

def handle_cancel():
    speak("Okay, canceling the previous command.")

# ——————— MAIN LOOP ———————
def main():
    wish_me()
    handle_first_run()
    run_task("Checking reminders",check_reminders)

    INTRO_TEXT = "Hi Sir, I am Jarvis your desktop voice assistant. I can perform basic tasks for you."

    while True:
        query : str = take_command().lower()   # Use voice only when idle
        # query = input().lower()  #testing without voice
        if query in ["none", ""]:
            time.sleep(0.5)
            continue

        # ——— ROUTE THROUGH LLM ———
        actions = process_with_llm(query)  # pyright: ignore[reportOptionalOperand] # ← This returns list of dicts

        if not actions:
            speak("I didn't understand that.")
            continue

        # ——— EXECUTE ACTIONS IN ORDER ———
        for action in actions:
            print(action)
            cmd = action.get("action")

            # CANCEL FIRST (always)
            if cmd == "cancel":
                handle_cancel()
                continue  # Skip rest of actions if cancel was first

            elif cmd == "respond":
                speak(action.get("text", "Okay."))

            # ——— COMMAND ROUTING ———
            elif cmd == "introduce yourself":
                speak(INTRO_TEXT)

            elif cmd == "set reminder":
                time_str = action.get("time")
                content = action.get("content")
                if time_str and content:
                    dt = dateparser.parse(time_str)
                    if dt:
                        reminders.append([dt.hour, dt.minute, content])
                        speak(f"Reminder set for {dt.strftime('%I:%M %p')} to {content}")
                    else:
                        speak("Sorry, I couldn't understand the time.")

            elif cmd == "get time":
                from datetime import datetime
                current = datetime.now().strftime("%I:%M %p")
                speak(f"Sir, the time is {current}")

            elif cmd == "goodbye":
                wish_me(False)
                exit(0)

            elif cmd == "go to sleep":
                speak("Going to sleep. Wake me with 'hello jarvis'.")
                while "hello jar" not in take_command().lower():
                    time.sleep(1)
                speak("I'm back!")

            elif cmd == "unknown":
                speak(action.get("response", "I didn't understand that."))

            else:
                # All other tasks → send to tasks.py
                from tasks import handle_task_action
                handle_task_action(action)
            break    

if __name__ == "__main__":
    main()