import psutil
import time
import threading

notifier=None

def set_notifier(fn):
    global notifier
    notifier=fn

def push(message):
    if notifier:
        notifier(message)
    else:
        print(f"NOVA alert: {message}")

def monitor_battery():
    while True:
        battery=psutil.sensors_battery()
    if battery:
        if not battery.power_plugged and battery.percent<=20:
            push(f"Battery low - {battery.percent}% remaining. Please plug in.")
        time.sleep(60)

def monitor_cpu():
    while True:
        cpu=psutil.cpu_percent(interval=1)
        if cpu>=85:
            push(f"CPU usage critical - {cpu}%. Consider closing some apps.")
        time.sleep(30)

def start_monitoring():
    battery_thread=threading.Thread(target=monitor_battery, daemon=True)
    cpu_thread=threading.Thread(target=monitor_cpu, daemon=True)
    battery_thread.start()
    cpu_thread.start()
    print("Background monitoring started.")