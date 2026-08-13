import speech_recognition as sr
from jarvis.config import ENERGY_THRESHOLD, MIC_DEVICE_INDEX, WAKE_WORD

# "Jarvis" no es una palabra española: Google STT (es-ES) suele oírlo como
# estas variantes fonéticas. Se aceptan todas como activación.
WAKE_WORD_VARIANTS = {WAKE_WORD, "harvey", "harbi", "jarbis", "yarvis", "jarves", "jarvi"}


class Listener:
    def __init__(self, language: str = "es-ES"):
        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = 0.8
        self.microphone = sr.Microphone(device_index=MIC_DEVICE_INDEX)
        self.language = language
        if ENERGY_THRESHOLD is not None:
            # El valor guardado es el nivel de ruido ambiente medido; se le da
            # margen para que no dispare con el propio ruido de fondo. Se deja
            # fijo (dynamic_energy_threshold=False) porque el ajuste en vivo
            # lo iba erosionando de nuevo hacia el ruido ambiente, causando
            # activaciones falsas constantes.
            self.recognizer.energy_threshold = ENERGY_THRESHOLD * 1.5
            self.recognizer.dynamic_energy_threshold = False
        else:
            with self.microphone as source:
                print("Calibrando micrófono para ruido ambiente...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            # Sin calibración guardada, sí conviene seguir ajustándose en vivo.
            self.recognizer.dynamic_energy_threshold = True

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
        while True:
            text = self._listen_once(timeout=None, phrase_time_limit=4)
            if any(variant in text for variant in WAKE_WORD_VARIANTS):
                return True

    def listen_command(self, timeout=6, phrase_time_limit=12) -> str:
        print("Te escucho...")
        return self._listen_once(timeout=timeout, phrase_time_limit=phrase_time_limit)
