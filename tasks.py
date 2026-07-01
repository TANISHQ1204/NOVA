import pyautogui
import time
import subprocess
import pygetwindow as gw

pyautogui.FAILSAFE=True
pyautogui.PAUSE=0.3

def send_whatsapp_message(contact, message):
    pyautogui.hotkey('win','s')
    time.sleep(0.5)
    pyautogui.typewrite('Whatsapp', interval=0.05)
    time.sleep(1)
    pyautogui.press('enter')
    time.sleep(3)

    pyautogui.hotkey('ctrl','f')
    time.sleep(0.5)
    pyautogui.typewrite(contact, interval=0.05)
    time.sleep(2)
    pyautogui.press('enter')
    time.sleep(1)

    pyautogui.hotkey('ctrl','a')
    pyautogui.typewrite(message, interval=0.05)
    time.sleep(0.5)
    pyautogui.press('enter')
    return f"Message sent to {contact} on WhatsApp"

def search_youtube(query):
    subprocess.Popen(['start','msedge','https://www.youtube.com'],shell=True)
    time.sleep(3)

    pyautogui.hotkey('ctrl','l')
    time.sleep(0.5)
    pyautogui.typewrite(f'https://www.youtube.com/results?search_query={query.replace(" ","+")}',interval=0.02)
    pyautogui.press('enter')
    return f"Searching YouTube for {query}."

def search_google(query):
    subprocess.Popen(['start','msedge',f'https://www.google.com/search?q={query.replace(" ","+")}'],shell=True)
    return f"Searching Google for {query}."