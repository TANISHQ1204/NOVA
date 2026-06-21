import edge_tts
import asyncio
import pygame
import os
import tempfile
import time
from dotenv import load_dotenv

load_dotenv()

VOICE="en-US-GuyNeural"
OUTPUT_FILE=tempfile.gettempdir()+"\\nova_speech.mp3"

async def _generate_speech(text):
    communicate=edge_tts.Communicate(text, VOICE)
    await communicate.save(OUTPUT_FILE)

def _play_audio():
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(OUTPUT_FILE)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        pygame.mixer.quit()

def speak(text):
    print(f"NOVA: {text}")
    asyncio.run(_generate_speech(text))
    _play_audio()