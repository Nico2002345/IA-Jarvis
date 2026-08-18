"""
Comandos básicos que JARVIS resuelve localmente, SIN llamar a la API de Claude.
Así siguen funcionando aunque se acaben los créditos.
"""
import re
import subprocess
import unicodedata
from datetime import datetime

from jarvis.tools import system_control as sc
from jarvis.tools import input_control as ic


def _normalize(text: str) -> str:
    text = text.strip().lower()
    text = "".join(c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn")
    return text


# Frase/palabra clave -> acción a ejecutar cuando el usuario pide "abrir" algo
# El orden importa: se usa el primer trigger que aparezca como substring del texto,
# por eso las frases más específicas (ej. "visual studio code") van antes que las
# genéricas (ej. "visual studio").
_APP_TRIGGERS = {
    "youtube": lambda: sc.open_path("https://youtube.com"),
    "google": lambda: sc.open_path("https://google.com"),
    "spotify": lambda: sc.open_application("spotify"),
    "whatsapp": lambda: sc.open_whatsapp(),
    "chrome": lambda: sc.open_application("chrome"),
    "bloc de notas": lambda: sc.open_application("bloc de notas"),
    "notepad": lambda: sc.open_application("notepad"),
    "visual studio code": lambda: sc.open_application("visual studio code"),
    "vscode": lambda: sc.open_application("visual studio code"),
    "vs code": lambda: sc.open_application("visual studio code"),
    "visual studio": lambda: sc.open_application("visual studio"),
    "excel": lambda: sc.open_application("excel"),
    "word": lambda: sc.open_application("word"),
    "android studio": lambda: sc.open_application("android studio"),
    "valorant": lambda: sc.open_application("valorant"),
    "teams": lambda: sc.open_application("teams"),
    "virtualdj": lambda: sc.open_application("virtualdj"),
    "virtual dj": lambda: sc.open_application("virtualdj"),
    "instagram": lambda: sc.open_path("https://www.instagram.com"),
    "facebook": lambda: sc.open_path("https://www.facebook.com"),
}

# Frase/palabra clave -> nombre de proceso a buscar cuando el usuario pide "cerrar" algo.
# No incluye youtube/google: no son procesos propios, viven dentro del navegador.
_CLOSE_TARGETS = {
    "spotify": "spotify",
    "whatsapp": "whatsapp",
    "chrome": "chrome",
    "bloc de notas": "notepad",
    "notepad": "notepad",
    "visual studio code": "code",
    "vscode": "code",
    "vs code": "code",
    "visual studio": "devenv",
    "excel": "excel",
    "word": "winword",
    "android studio": "studio",
    "valorant": "valorant",
    "teams": "teams",
    "virtualdj": "virtualdj",
    "virtual dj": "virtualdj",
}

_OPEN_VERB_RE = re.compile(r"\b(abre|abrir|abreme|abrime|inicia|iniciar|ejecuta|ejecutar)\b")
_CLOSE_VERB_RE = re.compile(r"\b(cierra|cierre|cerrar|cierrame|cierralo|finaliza|finalizar)\b")

_TIME_PATTERNS = ("que hora es", "que hora tienes", "dime la hora", "sabes que hora es")

_SHUTDOWN_PATTERNS = (
    "apaga el computador", "apaga la computadora", "apaga el pc", "apaga la pc",
    "apagar el computador", "apagar la computadora", "apagar el pc", "apagar la pc",
    "apaga windows",
)

_RESTART_PATTERNS = (
    "reinicia el computador", "reinicia la computadora", "reinicia el pc", "reinicia la pc",
    "reiniciar el computador", "reiniciar la computadora", "reiniciar el pc", "reiniciar la pc",
)

_VOLUME_UP_PATTERNS = (
    "sube el volumen", "sube volumen", "subir el volumen", "subir volumen",
    "aumenta el volumen", "aumenta volumen", "aumentar el volumen", "mas volumen",
    "súbele al volumen", "subele al volumen", "subele el volumen",
)

_VOLUME_DOWN_PATTERNS = (
    "baja el volumen", "baja volumen", "bajar el volumen", "bajar volumen",
    "disminuye el volumen", "disminuye volumen", "reduce el volumen", "reduce volumen",
    "bájale al volumen", "bajale al volumen", "bajale el volumen", "menos volumen",
)

_MUTE_PATTERNS = (
    "silencia el volumen", "silencia el sonido", "pon en silencio", "mutea el volumen",
    "mutea el sonido", "quita el sonido", "sin sonido",
)

_UNMUTE_PATTERNS = (
    "quita el silencio", "activa el sonido", "quita el mute", "vuelve a poner el sonido",
    "pon el sonido",
)

_PLAY_VERB_RE = re.compile(r"\b(pon|ponme|poner|reproduce|reproducir|toca|tocame|tocar)\b")
_PLAY_KEYWORD_RE = re.compile(r"\b(musica|música|cancion(?:es)?|canción(?:es)?)\b")
_PLAY_FILLER_WORDS = {
    "pon", "ponme", "poner", "reproduce", "reproducir", "toca", "tocame", "tocar",
    "musica", "cancion", "canciones", "de", "un", "una", "algo",
    "la", "el", "los", "las",
}
_PLAY_TRAILING_FILLER_WORDS = {"por", "favor"}


def _extract_song_query(norm: str) -> str:
    """Quita el verbo ('pon', 'reproduce'...) y muletillas ('musica de', 'por favor')
    del texto normalizado, dejando solo lo que se debe buscar en YouTube."""
    words = norm.split()
    start = 0
    while start < len(words) and words[start] in _PLAY_FILLER_WORDS:
        start += 1
    end = len(words)
    while end > start and words[end - 1] in _PLAY_TRAILING_FILLER_WORDS:
        end -= 1
    return " ".join(words[start:end]).strip()


def _match_open_app(norm: str):
    if not _OPEN_VERB_RE.search(norm):
        return None
    for trigger, action in _APP_TRIGGERS.items():
        if trigger in norm:
            return action
    return None


def _match_close_app(norm: str):
    if not _CLOSE_VERB_RE.search(norm):
        return None
    for trigger, process_name in _CLOSE_TARGETS.items():
        if trigger in norm:
            return process_name
    return None


def handle(text: str, confirm_callback=None):
    """Intenta resolver el comando localmente. Devuelve la respuesta (str) si lo manejó,
    o None si no coincide con ningún comando básico y debe pasar a la IA.
    confirm_callback(desc: str) -> bool, se usa para confirmar apagar/reiniciar."""
    confirm_callback = confirm_callback or (lambda desc: True)
    norm = _normalize(text)

    if any(p in norm for p in _TIME_PATTERNS):
        return f"Son las {datetime.now().strftime('%H:%M')}."

    if any(p in norm for p in _SHUTDOWN_PATTERNS):
        if not confirm_callback("apagar el computador"):
            return "Apagado cancelado."
        subprocess.Popen(["shutdown", "/s", "/t", "5"])
        return "Apagando el computador en 5 segundos."

    if any(p in norm for p in _RESTART_PATTERNS):
        if not confirm_callback("reiniciar el computador"):
            return "Reinicio cancelado."
        subprocess.Popen(["shutdown", "/r", "/t", "5"])
        return "Reiniciando el computador en 5 segundos."

    if any(p in norm for p in _VOLUME_UP_PATTERNS):
        return ic.volume_up()

    if any(p in norm for p in _VOLUME_DOWN_PATTERNS):
        return ic.volume_down()

    if any(p in norm for p in _MUTE_PATTERNS):
        return ic.volume_mute_toggle()

    if any(p in norm for p in _UNMUTE_PATTERNS):
        return ic.volume_mute_toggle()

    if _PLAY_VERB_RE.search(norm) and _PLAY_KEYWORD_RE.search(norm):
        query = _extract_song_query(norm)
        if query:
            return sc.search_youtube(query)

    action = _match_open_app(norm)
    if action:
        return action()

    process_name = _match_close_app(norm)
    if process_name:
        if not confirm_callback(f"cerrar {process_name}"):
            return "Cierre cancelado."
        return sc.kill_process(process_name)

    return None
