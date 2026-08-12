import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
WAKE_WORD = os.getenv("WAKE_WORD", "jarvis").lower()
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-opus-4-8")

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
