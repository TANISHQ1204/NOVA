import pyautogui
import pygetwindow as gw
import time
import subprocess

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
    

if __name__ == "__main__":
    open_notepad()
    type_text("Hello from NOVA!")