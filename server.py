from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from brain import detect_intent, route_intent, conversation_history, full_chat_log
from memory import update_session
from monitor import start_monitoring, set_notifier
import asyncio
from contextlib import asynccontextmanager
from fastapi.responses import HTMLResponse
from files import get_disk_space, get_system_info
import psutil
import webbrowser
from speaker import speak
import threading
from fastapi.staticfiles import StaticFiles

webbrowser.open("http://localhost:8000/dashboard")

@asynccontextmanager
async def lifespan(app:FastAPI):
    set_notifier(lambda msg:asyncio.create_task(push_to_clients(msg)))
    start_monitoring()
    yield

app=FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")

class Command(BaseModel):
    message:str

connected_clients=[]

async def push_to_clients(message):
    for client in connected_clients:
        try:
            await client.send_text(message)
        except Exception:
            connected_clients.remove(client)

@app.get("/dashboard")
def dashboard():
    return HTMLResponse(content='<meta http-equiv="refresh" content="0;url=/static/dashboard.html">')

@app.get("/stats")
def stats():
    cpu = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory().percent
    battery = psutil.sensors_battery()
    battery_percent = battery.percent if battery else None
    return {
        "cpu": cpu,
        "ram": ram,
        "battery": battery_percent
    }

@app.get("/history")
def history():
    return {"messages": full_chat_log}

@app.get("/")
def root():
    return {"Status: NOVA Online"}

@app.get("/ping")
def ping():
    return {"response: pong"}

@app.post("/command")
def handle_command(cmd: Command):
    update_session()
    intent=detect_intent(cmd.message)
    response=route_intent(intent,cmd.message)
    return {"intent":intent, "response":response}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    print("Client Connected via WebSocket")
    try:
        while True:
            data=await websocket.receive_text()
            intent=detect_intent(data)
            response=route_intent(intent,data)
            await websocket.send_text(response)
            threading.Thread(target=speak, args=(response,), daemon=True).start()
    except WebSocketDisconnect:
        connected_clients.remove(websocket)
        print("Client Disconnected")