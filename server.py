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
        <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap" rel="stylesheet">
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
                top: 0; left: 0;
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
                padding: 20px;
            }
            .header h1 {
                font-family: 'Orbitron', sans-serif;
                font-weight: 900;
                font-size: 36px;
                text-shadow: 0 0 20px #00ffff;
                letter-spacing: 12px;
            }
            .main {
                flex: 1;
                display: grid;
                grid-template-columns: 1fr 1.2fr 1fr;
                gap: 20px;
                padding: 0 30px 30px 30px;
                min-height: 0;
            }
            .panel {
                border: 1px solid #00ffff;
                border-radius: 4px;
                padding: 20px;
                background: rgba(0,20,20,0.3);
                box-shadow: 0 0 15px rgba(0,255,255,0.15);
                position: relative;
                display: flex;
                flex-direction: column;
                min-height: 0;
            }
            .panel::before, .panel::after {
                content: '';
                position: absolute;
                width: 14px;
                height: 14px;
                border: 2px solid #ff6600;
            }
            .panel::before {
                top: -2px; left: -2px;
                border-right: none;
                border-bottom: none;
            }
            .panel::after {
                bottom: -2px; right: -2px;
                border-left: none;
                border-top: none;
            }
            .panel h2 {
                font-family: 'Orbitron', sans-serif;
                font-size: 14px;
                margin-bottom: 15px;
                color: #ff9933;
                text-shadow: 0 0 8px #ff6600;
                letter-spacing: 2px;
            }
            .core-panel {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
            }
            .orb-wrapper {
                position: relative;
                width: 200px;
                height: 200px;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .reactor-outer {
                width: 170px;
                height: 170px;
                border-radius: 50%;
                background: #0a1414;
                box-shadow:
                    0 0 4px 2px #00ffff,
                    0 0 25px 8px rgba(0,255,255,0.5),
                    inset 0 0 20px 5px rgba(0,255,255,0.4);
                display: flex;
                align-items: center;
                justify-content: center;
                animation: pulse 2.2s ease-in-out infinite;
            }
            .reactor-mid {
                width: 110px;
                height: 110px;
                border-radius: 50%;
                background: #0a1414;
                box-shadow:
                    0 0 4px 2px #ff6600,
                    0 0 20px 6px rgba(255,102,0,0.5),
                    inset 0 0 15px 4px rgba(255,102,0,0.4);
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .reactor-core {
                width: 55px;
                height: 55px;
                border-radius: 50%;
                background: #ffffff;
                box-shadow:
                    0 0 10px 4px #ffffff,
                    0 0 25px 10px #00ffff,
                    0 0 45px 18px rgba(0,255,255,0.6);
            }
            @keyframes pulse {
                0%, 100% { box-shadow: 0 0 4px 2px #00ffff, 0 0 25px 8px rgba(0,255,255,0.5), inset 0 0 20px 5px rgba(0,255,255,0.4); }
                50% { box-shadow: 0 0 6px 3px #00ffff, 0 0 35px 12px rgba(0,255,255,0.7), inset 0 0 25px 7px rgba(0,255,255,0.5); }
            }
            .ring {
                position: absolute;
                border-radius: 50%;
                border-style: solid;
            }
            .ring1 {
                width: 160px; height: 160px;
                border-width: 1px;
                border-color: rgba(0,255,255,0.5) transparent rgba(0,255,255,0.5) transparent;
                animation: spin 7s linear infinite;
            }
            .ring2 {
                width: 195px; height: 195px;
                border-width: 1px;
                border-color: transparent rgba(255,102,0,0.4) transparent rgba(255,102,0,0.4);
                animation: spin 10s linear infinite reverse;
            }
            @keyframes spin {
                from { transform: rotate(0deg); }
                to { transform: rotate(360deg); }
            }
            .core-label {
                margin-top: 25px;
                font-family: 'Orbitron', sans-serif;
                font-size: 13px;
                letter-spacing: 4px;
            }
            .pulse-dot {
                width: 8px; height: 8px;
                background: #00ff00;
                border-radius: 50%;
                display: inline-block;
                margin-right: 8px;
                box-shadow: 0 0 8px #00ff00;
                animation: blink 1.5s infinite;
            }
            @keyframes blink {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.3; }
            }
            .stat-row {
                display: flex;
                justify-content: space-between;
                margin-bottom: 10px;
                font-size: 13px;
            }
            .bar-bg {
                background: #1a1a1a;
                height: 5px;
                border-radius: 3px;
                margin-top: 4px;
                margin-bottom: 14px;
            }
            .bar-fill {
                background: linear-gradient(90deg, #00ffff, #ff6600);
                height: 5px;
                border-radius: 3px;
                box-shadow: 0 0 8px #00ffff;
                transition: width 0.5s ease;
            }
            .chat-log {
                flex: 1;
                overflow-y: auto;
                font-size: 12px;
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
            <h1>N O V A</h1>
        </div>
        <div class="main">
            <div class="panel">
                <h2>SYSTEM STATS</h2>
                <div class="stat-row"><span>CPU</span><span id="cpu-val">0%</span></div>
                <div class="bar-bg"><div class="bar-fill" id="cpu-bar" style="width:0%"></div></div>
                <div class="stat-row"><span>RAM</span><span id="ram-val">0%</span></div>
                <div class="bar-bg"><div class="bar-fill" id="ram-bar" style="width:0%"></div></div>
                <div class="stat-row"><span>BATTERY</span><span id="battery-val">N/A</span></div>
                <div class="bar-bg"><div class="bar-fill" id="battery-bar" style="width:0%"></div></div>
            </div>
            <div class="panel core-panel">
                <div class="orb-wrapper">
                <div class="ring ring2"></div>
                <div class="ring ring1"></div>
                <div class="reactor-outer">
                    <div class="reactor-mid">
                        <div class="reactor-core"></div>
                    </div>
                </div>
            </div>
                <div class="core-label"><span class="pulse-dot"></span>ONLINE</div>
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