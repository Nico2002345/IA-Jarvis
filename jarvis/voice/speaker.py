import pyttsx3
import threading

_lock = threading.Lock()


class Speaker:
    def __init__(self, rate: int = 185, voice_hint: str = "spanish"):
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", rate)
        self._select_voice(voice_hint)

    def _select_voice(self, hint: str):
        hint = hint.lower()
        for voice in self.engine.getProperty("voices"):
            name = (voice.name or "").lower()
            langs = " ".join(str(l) for l in (voice.languages or [])).lower()
            if hint in name or hint in langs or "es" in voice.id.lower():
                self.engine.setProperty("voice", voice.id)
                return

    def say(self, text: str):
        if not text:
            return
        with _lock:
            print(f"JARVIS: {text}")
            self.engine.say(text)
            self.engine.runAndWait()
