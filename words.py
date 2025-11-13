import random
from PyDictionary import PyDictionary
import plyer as pl
from utils import speak

dictionary = PyDictionary()

def word_for_the_day():
    try:
        with open("words.txt", "r") as f:
            words = f.readlines()
    except FileNotFoundError:
        speak("Word file not found.")
        return

    while True:
        word = random.choice(words).strip()
        meanings = dictionary.meaning(word)
        if meanings:
            meaning_text = next(iter(meanings.values()))[0]
            notification = pl.facades.Notification()
            notification.notify(
                title="Word for the Day",
                message=f"{word.capitalize()}: {meaning_text}",
                timeout=60
            )
            speak(f"Today's word is {word}. It means {meaning_text}.")
            break
