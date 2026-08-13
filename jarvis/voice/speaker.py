import asyncio
import os
import tempfile
import threading

import edge_tts
import pygame

from jarvis.config import VOICE_NAME, VOICE_RATE

_lock = threading.Lock()


class Speaker:
    def __init__(self, voice: str = VOICE_NAME, rate: str = VOICE_RATE):
        self.voice = voice
        self.rate = rate
        pygame.mixer.init()
        self._fallback_engine = None  # pyttsx3, solo si edge-tts falla (sin internet)

    def say(self, text: str):
        if not text:
            return
        with _lock:
            print(f"JARVIS: {text}")
            try:
                self._say_edge(text)
            except Exception as e:
                print(f"edge-tts falló ({e}), usando voz local de respaldo.")
                self._say_fallback(text)

    def _say_edge(self, text: str):
        fd, path = tempfile.mkstemp(suffix=".mp3")
        os.close(fd)
        try:
            asyncio.run(self._synthesize(text, path))
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)
            pygame.mixer.music.unload()
        finally:
            os.remove(path)

    async def _synthesize(self, text: str, path: str):
        communicate = edge_tts.Communicate(text, self.voice, rate=self.rate)
        await communicate.save(path)

    def _say_fallback(self, text: str):
        if self._fallback_engine is None:
            import pyttsx3

            self._fallback_engine = pyttsx3.init()
        self._fallback_engine.say(text)
        self._fallback_engine.runAndWait()
