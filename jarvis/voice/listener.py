import speech_recognition as sr
from jarvis.config import WAKE_WORD


class Listener:
    def __init__(self, language: str = "es-ES"):
        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = 0.8
        self.microphone = sr.Microphone()
        self.language = language
        with self.microphone as source:
            print("Calibrando micrófono para ruido ambiente...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)

    def _listen_once(self, timeout=None, phrase_time_limit=None) -> str:
        with self.microphone as source:
            try:
                audio = self.recognizer.listen(
                    source, timeout=timeout, phrase_time_limit=phrase_time_limit
                )
            except sr.WaitTimeoutError:
                return ""
        try:
            return self.recognizer.recognize_google(audio, language=self.language).lower()
        except (sr.UnknownValueError, sr.RequestError):
            return ""

    def wait_for_wake_word(self) -> bool:
        print(f"Escuchando... (di '{WAKE_WORD}' para activar)")
        text = self._listen_once(timeout=None, phrase_time_limit=4)
        return WAKE_WORD in text

    def listen_command(self, timeout=6, phrase_time_limit=12) -> str:
        print("Te escucho...")
        return self._listen_once(timeout=timeout, phrase_time_limit=phrase_time_limit)
