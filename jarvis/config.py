import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
WAKE_WORD = os.getenv("WAKE_WORD", "jarvis").lower()

# Voz neuronal (edge-tts) usada por Speaker. Lista de voces: `edge-tts --list-voices`.
VOICE_NAME = os.getenv("JARVIS_VOICE", "es-AR-TomasNeural")
VOICE_RATE = os.getenv("JARVIS_VOICE_RATE", "+0%")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-haiku-4-5")

# Token requerido para usar JARVIS desde la interfaz web (modo teléfono)
WEB_TOKEN = os.getenv("JARVIS_WEB_TOKEN", "")

# Calibración del micrófono (generados por `python -m jarvis.voice.calibrate`)
_mic_index = os.getenv("MIC_DEVICE_INDEX", "").strip()
MIC_DEVICE_INDEX = int(_mic_index) if _mic_index.isdigit() else None

_energy_threshold = os.getenv("ENERGY_THRESHOLD", "").strip()
ENERGY_THRESHOLD = float(_energy_threshold) if _energy_threshold else None

# Herramientas que requieren confirmación explícita del usuario antes de ejecutarse
DANGEROUS_TOOLS = {
    "run_command",
    "kill_process",
    "delete_path",
}
