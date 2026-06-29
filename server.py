from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from brain import detect_intent, route_intent
from memory import update_session
from monitor import start_monitoring, set_notifier
import asyncio
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app:FastAPI):
    set_notifier(lambda msg:asyncio.create_task(push_to_clients(msg)))
    start_monitoring()
    yield

app=FastAPI(lifespan=lifespan)

class Command(BaseModel):
    message:str

connected_clients=[]

async def push_to_clients(message):
    for client in connected_clients:
        try:
            await client.send_text(message)
        except Exception:
            connected_clients.remove(client)

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
    except WebSocketDisconnect:
        connected_clients.remove(websocket)
        print("Client Disconnected")