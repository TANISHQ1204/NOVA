import threading
from pynput import keyboard

_callback = None
_listener = None

def _on_press(key):
    try:
        if key==keyboard.Key.f9:
            if _callback is not None:
                threading.Thread(target=_callback, daemon=True).start()
    except Exception:
        pass

def start_hotkey_listener(callback):
    global _callback, _listener
    _callback=callback
    _listener=keyboard.Listener(on_press=_on_press)
    _listener.start()
    print("Hotkey listener started. Press F9 to activate NOVA.")

def stop_hotkey_listener():
    global _listener
    if _listener is not None:
        _listener.stop()
        _listener = None
        print("Hotkey listener stopped.")