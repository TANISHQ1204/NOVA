from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from brain import detect_intent, route_intent, conversation_history
from memory import update_session
from monitor import start_monitoring, set_notifier
import asyncio
from contextlib import asynccontextmanager
from fastapi.responses import HTMLResponse
from files import get_disk_space, get_system_info
import psutil

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

@app.get("/dashboard")
def dashboard():
    return HTMLResponse(content="""
    <html>
    <head>
        <title>NOVA Dashboard</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                background:
                    linear-gradient(rgba(0,255,255,0.03) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(0,255,255,0.03) 1px, transparent 1px),
                    #050505;
                background-size: 40px 40px;
                color: #00ffff;
                font-family: 'Courier New', monospace;
                height: 100vh;
                display: flex;
                flex-direction: column;
                overflow: hidden;
            }
            .scanline {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 2px;
                background: rgba(0,255,255,0.4);
                box-shadow: 0 0 10px #00ffff;
                animation: scan 4s linear infinite;
                pointer-events: none;
            }
            @keyframes scan {
                0% { top: 0%; }
                100% { top: 100%; }
            }
            .header {
                text-align: center;
                padding: 30px;
            }
            .header h1 {
                font-size: 50px;
                text-shadow: 0 0 20px #00ffff;
                letter-spacing: 10px;
            }
            .pulse {
                width: 10px;
                height: 10px;
                background: #00ff00;
                border-radius: 50%;
                display: inline-block;
                margin-right: 8px;
                box-shadow: 0 0 10px #00ff00;
                animation: blink 1.5s infinite;
            }
            @keyframes blink {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.3; }
            }
            .main {
                flex: 1;
                display: flex;
                gap: 20px;
                padding: 0 30px 30px 30px;
                min-height: 0;
            }
            .panel {
                flex: 1;
                border: 1px solid #00ffff;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 0 15px rgba(0,255,255,0.2);
                background: rgba(0,20,20,0.3);
                display: flex;
                flex-direction: column;
                min-height: 0;
            }
            .panel h2 {
                font-size: 18px;
                margin-bottom: 15px;
                border-bottom: 1px solid #00ffff;
                padding-bottom: 10px;
                text-shadow: 0 0 8px #00ffff;
            }
            .stat-row {
                display: flex;
                justify-content: space-between;
                margin-bottom: 12px;
                font-size: 14px;
            }
            .bar-bg {
                background: #1a1a1a;
                height: 6px;
                border-radius: 3px;
                margin-top: 5px;
            }
            .bar-fill {
                background: #00ffff;
                height: 6px;
                border-radius: 3px;
                box-shadow: 0 0 8px #00ffff;
                transition: width 0.5s ease;
            }
            .chat-log {
                flex: 1;
                overflow-y: auto;
                font-size: 13px;
            }
            .chat-line {
                margin-bottom: 8px;
                padding-bottom: 8px;
                border-bottom: 1px solid rgba(0,255,255,0.1);
            }
            .chat-line.user { color: #ffffff; }
            .chat-line.nova { color: #00ffff; }
        </style>
    </head>
    <body>
        <div class="scanline"></div>
        <div class="header">
            <h1>NOVA</h1>
            <div><span class="pulse"></span>System Online</div>
        </div>
        <div class="main">
            <div class="panel">
                <h2>SYSTEM STATS</h2>
                <div class="stat-row">
                    <span>CPU</span><span id="cpu-val">0%</span>
                </div>
                <div class="bar-bg"><div class="bar-fill" id="cpu-bar" style="width:0%"></div></div>
                <div class="stat-row" style="margin-top:15px;">
                    <span>RAM</span><span id="ram-val">0%</span>
                </div>
                <div class="bar-bg"><div class="bar-fill" id="ram-bar" style="width:0%"></div></div>
                <div class="stat-row" style="margin-top:15px;">
                    <span>BATTERY</span><span id="battery-val">N/A</span>
                </div>
                <div class="bar-bg"><div class="bar-fill" id="battery-bar" style="width:0%"></div></div>
            </div>
            <div class="panel">
                <h2>CONVERSATION LOG</h2>
                <div class="chat-log" id="chat-log">
                    <div class="chat-line nova">NOVA: Awaiting input...</div>
                </div>
            </div>
        </div>
        <script>
            async function updateStats() {
                const res = await fetch('/stats');
                const data = await res.json();
                document.getElementById('cpu-val').innerText = data.cpu + '%';
                document.getElementById('cpu-bar').style.width = data.cpu + '%';
                document.getElementById('ram-val').innerText = data.ram + '%';
                document.getElementById('ram-bar').style.width = data.ram + '%';
                if (data.battery !== null) {
                    document.getElementById('battery-val').innerText = data.battery + '%';
                    document.getElementById('battery-bar').style.width = data.battery + '%';
                } else {
                    document.getElementById('battery-val').innerText = 'No Battery';
                }
            }
            async function updateHistory() {
                const res = await fetch('/history');
                const data = await res.json();
                const log = document.getElementById('chat-log');
                log.innerHTML = '';
                data.messages.forEach(msg => {
                    const div = document.createElement('div');
                    const role = msg.role === 'user' ? 'user' : 'nova';
                    const text = msg.parts[0].text;
                    div.className = 'chat-line ' + role;
                    div.innerText = (role === 'user' ? 'You: ' : 'NOVA: ') + text;
                    log.appendChild(div);
                });
                log.scrollTop = log.scrollHeight;
            }

            updateStats();
            updateHistory();
            setInterval(updateStats, 2000);
            setInterval(updateHistory, 2000);
        </script>
    </body>
    </html>
    """)

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
    return {"messages": conversation_history}

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