import datetime
import dateparser
from utils import speak, take_command
from time import sleep
from win10toast import ToastNotifier

reminders = []
toaster = ToastNotifier()

def set_reminder():
    speak("At what time should I remind you?")
    while True:
        time_text = take_command()
        dt = dateparser.parse(time_text)
        
        if dt:
            sleep(1)
            speak("What should I remind you of?")
            content = take_command()
            reminders.append([dt.hour, dt.minute, content])
            speak("Reminder set successfully.")
            break
        else:
            speak("Sorry, I couldn't understand the time. Can you say again?")

def check_reminders():
    """Notify when reminder time is reached."""
    while True:
        now = datetime.datetime.now()
        for r in reminders[:]:
            if now.hour == r[0] and now.minute == r[1]:
                toaster.show_toast(
                    "⏰ Reminder!",
                    msg = r[2],
                    duration = 10,      
                    threaded = True     
                )
                speak(f"Sir, this is your reminder to {r[2]}")
                reminders.remove(r)
