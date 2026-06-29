import json
import os
import datetime
from dotenv import load_dotenv

load_dotenv()

MEMORY_FILE="nova_memory.json"

DEFAULT_MEMORY = {
    "owner_name": os.getenv("OWNER_NAME", "sir"),
    "city": "Fatehpur",
    "preferences": {},
    "important_facts": [],
    "last_session": None,
    "conversation_count": 0
}

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE,"r") as f:
                data=json.load(f)
                return data
        except json.JSONDecodeError:
            print("Memory file corrupted. Starting fresh.")
            return DEFAULT_MEMORY.copy()
    else:
        return DEFAULT_MEMORY.copy()
    
def save_memory(memory):
    try:
        with open(MEMORY_FILE,"w") as f:
            json.dump(memory,f,indent=2)
    except Exception as e:
        print(f"Could not save memory: {e}")

def update_memory(key, value):
    memory=load_memory()

    if key=="important facts":
        if value not in memory["important facts"]:
            memory["important facts"].append(value)
    elif key=="preferences":
        memory["preferences"].update(value)
    else:
        memory[key]=value

    save_memory(memory)

def get_memory_context():
    memory=load_memory()
    
    context_parts=[]
    
    if memory["important_facts"]:
        facts="\n".join(f"- {fact}" for fact in memory["important_facts"])
        context_parts.append(f"Important facts about the owner:\n{facts}")
    
    if memory["preferences"]:
        prefs="\n".join(f"- {k}: {v}" for k, v in memory["preferences"].items())
        context_parts.append(f"Owner preferences:\n{prefs}")
    
    if memory["last_session"]:
        context_parts.append(f"Last session: {memory['last_session']}")
    
    context_parts.append(f"Total conversations: {memory['conversation_count']}")
    
    return "\n\n".join(context_parts) if context_parts else "No memory yet."

def update_session():
    memory=load_memory()
    memory["last_session"]=datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    memory["conversation_count"]+=1
    save_memory(memory)
