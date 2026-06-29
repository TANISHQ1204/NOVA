from dotenv import load_dotenv
import os
import time
from voice import hear
from speaker import speak
from hotkey import start_hotkey_listener, stop_hotkey_listener
from api_test import get_weather
from brain import ask_nova, detect_intent, route_intent
from memory import update_session

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
    update_session()
    print(f"Initializing {assistant_name} v{version}...")
    speak(f"Welcome back {owner_name}.")
    print(f"-"*40)

def respond(user_input):
    user_input=user_input.lower().strip()

    if not user_input:
        return f"I didn't hear anything, {owner_name}."

    if "quit" in user_input or "exit" in user_input:
        return "EXIT"
    
    if "sleep" in user_input or "stop listening" in user_input:
        return "SLEEP"

    intent = detect_intent(user_input)
    return route_intent(intent, user_input)
    
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