from dotenv import load_dotenv
import os
import time
import datetime
from voice import hear
from speaker import speak
from hotkey import start_hotkey_listener, stop_hotkey_listener
from api_test import get_weather

load_dotenv()

assistant_name=os.getenv("ASSISTANT_NAME","NOVA")
owner_name=os.getenv("OWNER_NAME","SIR")
version=os.getenv("VERSION","1.0")
voice_mode=True
nova_active=False

def activate_nova():
    global nova_active
    if not nova_active:
        nova_active = True

def greet():
    print(f"Initializing {assistant_name} v{version}...")
    speak(f"Welcome back {owner_name}.")
    print(f"-"*40)

responses = {
    "hello": f"Hello, {owner_name}. How can I assist you today?",
    "how are you": f"All systems functioning perfectly, {owner_name}.",
    "your name": f"I am {assistant_name}, your personal AI assistant.",
    "what can you do": "Right now I can answer basic questions. I am still learning, sir.",
    "time": "fetching_time",
    "good morning": f"Good Morning!, {owner_name}.",
    "weather": f"fetching_weather",
    "joke": f"sarcastic laugh.",
    "quit": "EXIT",
    "sleep": "SLEEP",
    "stop listening": "SLEEP",
}

def respond(user_input):
    user_input=user_input.lower().strip()

    if not user_input:
        return f"I didn't hear anything, {owner_name}."
    
    for keyword in responses:
        if keyword in user_input:
            if responses[keyword]=="fetching_time":
                now=datetime.datetime.now()
                return f"Current time is {now.strftime('%H:%M')}, {owner_name}."
            
            if responses[keyword]=="fetching_weather":
                city="Delhi"
                result=get_weather(city)
                if result is None:
                    return f"I couldn't fetch the weather right now, {owner_name}."
                return f"Current weather in {city} — {result['description']}, {result['temperature']} degrees celsius, feels like {result['feels_like']} degrees, humidity {result['humidity']} percent."

            return responses[keyword]
    
    return f"I don't know how to respond to that yet, {owner_name}. I'm still learning."
    
def main():
    global nova_active
    greet()
    start_hotkey_listener(activate_nova)
    speak("Press F9 to activate me.")
    
    while True:
        try:
            if voice_mode and nova_active:
                speak("Yes? I'm listening.")
                time.sleep(0.5)
                while nova_active:
                    user_input=hear()

                    if user_input=="__unknown__":
                        speak(f"I couldn't understand that, {owner_name}. Please try again.")
                        continue
                    elif user_input=="__error__":
                        speak(f"I'm having trouble reaching my servers, {owner_name}. Check your internet.")
                        continue

                    response=respond(user_input)

                    if response=="EXIT":
                        speak(f"Shutting down. Goodbye, {owner_name}.")
                        stop_hotkey_listener()
                        return
                    
                    if response=="SLEEP":
                        speak(f"Going to sleep. Press F9 to wake me up {owner_name}.")
                        nova_active=False
                        break

                    speak(response)
                    time.sleep(0.3)

                    
            elif voice_mode and not nova_active:
                time.sleep(0.1)
                continue

            else:
                user_input = input(f"\n{owner_name}: ")
                
                if not user_input:
                    continue
                
                response = respond(user_input)
                
                if response == "EXIT":
                    speak(f"Shutting down. Goodbye, {owner_name}.")
                    stop_hotkey_listener()
                    break
                
                if response == "SLEEP":
                    speak(f"Going to sleep, {owner_name}.")
                    continue
                
                speak(response)

        except KeyboardInterrupt:
            speak(f"Emergency shutdown detected. Goodbye, {owner_name}.")
            stop_hotkey_listener()
            break
        except Exception as e:
            speak(f"Something went wrong. Error: {e}")
            speak("Restarting loop...")

if __name__=="__main__":
    main()