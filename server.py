from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from brain import detect_intent, route_intent
from memory import update_session

app=FastAPI()

class Command(BaseModel):
    message:str

connected_clients=[]

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
            print(f"Received: {data}")
            intent=detect_intent(data)
            response=route_intent(intent,data)
            await websocket.send_text(response)
    except WebSocketDisconnect:
        connected_clients.remove(websocket)
        print("Client Disconnected")