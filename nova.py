from dotenv import load_dotenv
import os

load_dotenv()

assistant_name=os.getenv("ASSISTANT_NAME","NOVA")
owner_name=os.getenv("OWNER_NAME","SIR")
version=os.getenv("VERSION","1.0")

def greet():
    print(f"Initializing {assistant_name} v{version}...")
    print(f"Welcome back {owner_name}.")
    print(f"-"*40)

def respond(user_input):
    user_input=user_input.lower().strip()

    if not user_input:
        return f"I didn't hear anything, {owner_name}."
    
    for keyword in responses:
        if keyword in user_input:
            if responses[keyword]=="fetching_time":
                import datetime
                now=datetime.datetime.now()
                return f"Current time is {now.strftime('%H:%M')}, {owner_name}."
            return responses[keyword]
    
    return f"I don't know how to respond to that yet, {owner_name}. I'm still learning."

responses = {
    "hello": f"Hello, {owner_name}. How can I assist you today?",
    "how are you": f"All systems functioning perfectly, {owner_name}.",
    "your name": f"I am {assistant_name}, your personal AI assistant.",
    "what can you do": "Right now I can answer basic questions. I am still learning, sir.",
    "time": "fetching_time",
    "good morning": f"Good Morning!, {owner_name}.",
    "weather": f"I can't check weather yet but will learn soon.",
    "joke": f"sarcastic laugh.",
    "quit": f"EXIT",
}
    
def main():
    greet()

    while True:
        user_input=input(f"\n{owner_name}: ")
        response=respond(user_input)

        if response=="EXIT":
            print(f"\n NOVA : Shutting Down. Goodbye, {owner_name}.")
            break

        print(f"\n NOVA: {response}")

if __name__=="__main__":
    main()