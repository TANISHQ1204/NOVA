import requests
import os 
from dotenv import load_dotenv
import json
import datetime 
from api_test import get_weather

load_dotenv()

GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent"

SYSTEM_PROMPT = f"""You are NOVA, an intelligent personal AI assistant.
Your owner's name is {os.getenv('OWNER_NAME', 'sir')}.
You are helpful, precise, and slightly witty.
Keep responses concise — under 3 sentences unless asked for detail.
You are running on a Windows PC and will soon control an Android phone.
Never say you are an AI made by Google — you are NOVA."""

INTENT_PROMPT = """You are an intent classifier for an AI assistant called NOVA.
Given a user message, classify it into exactly one of these intents:

GET_TIME - user wants to know the current time
GET_WEATHER - user wants weather information
TELL_JOKE - user wants to hear something funny
PC_CONTROL - user wants to control their computer
GENERAL - anything else

Rules:
- Reply with ONLY the intent label
- No explanation, no punctuation, no extra words
- Just one label from the list above

User message: {message}
Intent:"""

conversation_history=[]

def detect_intent(user_message):
    prompt=INTENT_PROMPT.format(message=user_message)

    payload={
        "contents":[
            {"role": "user", "parts": [{"text": prompt}]}
        ],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 10
        }
    }

    headers={"Content-Type": "application/json"}
    url=f"{GEMINI_URL}?key={GEMINI_API_KEY}"

    try:
        response=requests.post(url, headers=headers, json=payload, timeout=10)
        data = response.json()

        if response.status_code!=200:
            return "GENERAL"
        
        data=response.json()
        intent=data["candidates"][0]["content"]["parts"][0]["text"].strip().upper()

        valid_intents=["GET_TIME","GET_WEATHER","TELL_JOKE","PC_CONTROL","GENERAL"]

        if intent not in valid_intents:
            return "GENERAL"
        return intent
    
    except Exception:
        return "GENERAL"
    
def route_intent(intent, user_message):
    if intent == "GET_TIME":
        now = datetime.datetime.now()
        return f"Current time is {now.strftime('%H:%M')}, {os.getenv('OWNER_NAME', 'sir')}."
    
    elif intent == "GET_WEATHER":
        city = extract_city(user_message)
        result = get_weather(city)
        if result is None:
            return f"I couldn't fetch the weather right now."
        return f"Current weather in {city} — {result['description']}, {result['temperature']} degrees celsius, feels like {result['feels_like']} degrees, humidity {result['humidity']} percent."
    
    elif intent == "TELL_JOKE":
        return ask_nova("Tell me a short funny joke. One liner preferred.")
    
    elif intent == "PC_CONTROL":
        return "PC control is coming soon. I'll be able to control your computer shortly."
    
    else:
        return ask_nova(user_message)
    
def extract_city(user_message):
    prompt = f"""Extract the city name from this message.
If no city is mentioned, reply with 'Delhi'.
Reply with ONLY the city name, nothing else.

Message: {user_message}
City:"""

    payload = {
        "contents": [
            {"role": "user", "parts": [{"text": prompt}]}
        ],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 10
        }
    }

    headers = {"Content-Type": "application/json"}
    url = f"{GEMINI_URL}?key={GEMINI_API_KEY}"

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code != 200:
            return "Delhi"
        data = response.json()
        city = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        return city if city else "Delhi"
    except Exception:
        return "Delhi"

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
    tests = [
        'check the clock for me',
        'how is the weather outside'
    ]
    for test in tests:
        intent = detect_intent(test)
        print(f"'{test}' → {intent}")