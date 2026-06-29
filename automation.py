import pyautogui
import pygetwindow as gw
import time
import subprocess
import psutil
import os

pyautogui.FAILSAFE=True
pyautogui.PAUSE=0.5

def open_notepad():
    pyautogui.hotkey('win', 'r')
    time.sleep(0.5)
    pyautogui.typewrite('notepad',interval=0.05)
    pyautogui.press('enter')
    time.sleep(2)
    notepad=gw.getWindowsWithTitle('Notepad')[0]
    notepad.activate()
    time.sleep(0.5)

def type_text(text):
    pyautogui.typewrite(text,interval=0.05)

def take_screenshot(filename='screenshot.png'):
    screenshot=pyautogui.screenshot()
    screenshot.save(filename)
    print(f"Screenshot saved: {filename}")

def close_notepad():
    notepad=gw.getWindowsWithTitle('Notepad')
    if notepad:
        notepad[0].close()

def open_browser():
    subprocess.Popen(['start', 'msedge'], shell=True)
    
def open_app(app_name):
    pyautogui.hotkey('win', 's')
    time.sleep(0.5)
    pyautogui.typewrite(app_name, interval=0.05)
    time.sleep(1)
    pyautogui.press('enter')

def shutdown_pc():
    os.system('shutdown /s /t 5')

def restart_pc():
    os.system('shutdown /r /t 5')

def get_battery():
    battery=psutil.sensors_battery()
    if battery is None:
        return "No battery detected - desktop PC"
    percent=battery.percent
    plugged="charging" if battery.power_plugged else "not charging"
    return f"Battery at {percent}%, {plugged}."

def get_system_info():
    cpu=psutil.cpu_percent(interval=1)
    ram=psutil.virtual_memory().percent
    battery=get_battery()
    return f"CPU at {cpu}%, RAM at {ram}%. {battery}"

def volume_up():
    for _ in range(5):
        pyautogui.press('volumeup')

def volume_down():
    for _ in range(5):
        pyautogui.press('volumedown')

def volume_mute():
    pyautogui.press('volumemute')

if __name__ == "__main__":
    open_notepad()
    type_text("Hello from NOVA!")