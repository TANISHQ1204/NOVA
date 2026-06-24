import requests
import os 
from dotenv import load_dotenv
import json

load_dotenv()

GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

SYSTEM_PROMPT = f"""You are NOVA, an intelligent personal AI assistant.
Your owner's name is {os.getenv('OWNER_NAME', 'sir')}.
You are helpful, precise, and slightly witty.
Keep responses concise — under 3 sentences unless asked for detail.
You are running on a Windows PC and will soon control an Android phone.
Never say you are an AI made by Google — you are NOVA."""

conversation_history=[]

def ask_nova(user_message):
    conversation_history.append({
        "role": "user",
        "parts": [{"text": user_message}]
    })
    
    payload={
        "contents": conversation_history,
        "systemInstruction": {
            "parts": [{"text": SYSTEM_PROMPT}]
        },
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 150
        }
    }
    
    headers={"Content-Type": "application/json"}
    url=f"{GEMINI_URL}?key={GEMINI_API_KEY}"
    
    try:
        for attempt in range(3):
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            
            if response.status_code == 200:
                break
            elif response.status_code == 503:
                print(f"Server busy, retrying... ({attempt + 1}/3)")
                import time
                time.sleep(2)
            else:
                return f"API error: {response.status_code}"
        
        if response.status_code != 200:
            return "Gemini servers are busy right now. Please try again in a moment."
        
        data = response.json()
        reply = data["candidates"][0]["content"]["parts"][0]["text"]
        
        conversation_history.append({
            "role": "model",
            "parts": [{"text": reply}]
        })
        
        return reply.strip()
    
    except requests.exceptions.Timeout:
        return "I'm taking too long to think. Please try again."
    except requests.exceptions.ConnectionError:
        return "I can't reach my servers. Check your internet."
    except KeyError:
        return "I received an unexpected response. Please try again."
    
if __name__ == "__main__":
    print("Testing NOVA's brain...")
    print("-" * 40)
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == "quit":
            break
        response = ask_nova(user_input)
        print(f"NOVA: {response}")
        print()