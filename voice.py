import speech_recognition as sr
from dotenv import load_dotenv
import os

load_dotenv()
recognizer=sr.Recognizer()

assistant_name=os.getenv("ASSISTANT_NAME", "NOVA")
owner_name=os.getenv("OWNER_NAME", "sir")

def listen():
    with sr.Microphone() as mic:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(mic, duration=1)
        audio=recognizer.listen(mic)

    return audio

def recognize(audio):
    try:
        text=recognizer.recognize_google(audio)
        return text.lower().strip()
    except sr.UnknownValueError:
        return "__unknown__"
    except sr.RequestError:
        return "__error__"
    
def hear():
    audio=listen()
    text=recognize(audio)
    return text