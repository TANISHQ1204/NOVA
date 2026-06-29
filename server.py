from fastapi import FastAPI
from pydantic import BaseModel
from brain import detect_intent, route_intent
from memory import update_session

app=FastAPI()

class Command(BaseModel):
    message:str

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