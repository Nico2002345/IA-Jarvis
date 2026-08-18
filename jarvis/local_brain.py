import json
import re
import urllib.error
import urllib.request

from jarvis.config import OLLAMA_HOST, OLLAMA_MODEL
from jarvis.tools.registry import TOOLS, execute_tool, is_dangerous, describe_call

_TOOL_NAMES = {t["name"] for t in TOOLS}
_LOOKS_LIKE_TOOL_CALL_RE = re.compile(r'^\s*\{.*"name"\s*:\s*"[a-zA-Z_]+".*\}\s*$', re.S)
_UNQUOTED_VALUE_RE = re.compile(r':\s*~\s*([,}])')

SYSTEM_PROMPT = """Eres JARVIS, un asistente personal por voz/texto que corre en el computador del usuario.
Estás funcionando en modo local de respaldo (un modelo gratuito en esta misma PC, sin conexión a Claude),
así que sé breve y directo. Tienes acceso a herramientas que te permiten abrir aplicaciones, archivos y
carpetas, ejecutar comandos del sistema, controlar el mouse y el teclado, buscar archivos y obtener
información del sistema.

Reglas:
- Responde siempre en español, de forma breve y natural (esto se lee en voz alta, evita listas largas o markdown).
- Usa las herramientas cuando el usuario te pida hacer algo en el computador, no solo describir cómo hacerlo.
- Antes de ejecutar acciones destructivas o irreversibles, asegúrate de que la intención del usuario sea clara.
- Si una herramienta fue bloqueada porque el usuario no confirmó, no insistas, solo infórmalo brevemente.
"""

_MAX_TOOL_HOPS = 6


def _tools_to_ollama_format():
    return [
        {
            "type": "function",
            "function": {
                "name": t["name"],
                "description": t["description"],
                "parameters": t["input_schema"],
            },
        }
        for t in TOOLS
    ]


_OLLAMA_TOOLS = _tools_to_ollama_format()


class LocalBrain:
    """Respaldo 100% local y gratuito (Ollama) para cuando la API de Claude falla:
    sin créditos, sin internet, rate limit, etc. No depende de ninguna cuenta."""

    def __init__(self, confirm_callback=None):
        self.history = []
        self.confirm_callback = confirm_callback or (lambda desc: True)
        self.model = OLLAMA_MODEL
        self.host = OLLAMA_HOST.rstrip("/")

    def _run_tool_with_confirmation(self, tool_name: str, tool_input: dict) -> str:
        if is_dangerous(tool_name):
            desc = describe_call(tool_name, tool_input)
            if not self.confirm_callback(desc):
                return f"Acción cancelada por el usuario: {desc}"
        return execute_tool(tool_name, tool_input)

    def _try_recover_leaked_tool_call(self, text: str):
        """Un modelo local a veces, en vez de usar el mecanismo real de tool_calls,
        escribe la llamada a la herramienta como texto plano (JSON). Si detectamos
        ese patrón, intentamos ejecutar la herramienta igual en lugar de mostrarle
        al usuario el JSON crudo."""
        if not _LOOKS_LIKE_TOOL_CALL_RE.match(text):
            return None
        fixed = _UNQUOTED_VALUE_RE.sub(r': "~"\1', text)
        try:
            call = json.loads(fixed)
        except ValueError:
            return None
        name = call.get("name")
        args = call.get("parameters") or call.get("arguments") or {}
        if name not in _TOOL_NAMES or not isinstance(args, dict):
            return None
        return self._run_tool_with_confirmation(name, args)

    def _chat(self, messages: list) -> dict:
        payload = {
            "model": self.model,
            "messages": messages,
            "tools": _OLLAMA_TOOLS,
            "stream": False,
        }
        req = urllib.request.Request(
            f"{self.host}/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def ask(self, user_text: str) -> str:
        snapshot = len(self.history)
        self.history.append({"role": "user", "content": user_text})
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + self.history

        try:
            for _ in range(_MAX_TOOL_HOPS):
                data = self._chat(messages)
                msg = data.get("message", {}) or {}
                tool_calls = msg.get("tool_calls") or []

                if not tool_calls:
                    text = (msg.get("content") or "").strip()
                    recovered = self._try_recover_leaked_tool_call(text)
                    if recovered is not None:
                        self.history.append({"role": "assistant", "content": recovered})
                        return recovered
                    self.history.append({"role": "assistant", "content": text})
                    return text or "No tengo una respuesta para eso."

                messages.append(msg)
                self.history.append(msg)
                for call in tool_calls:
                    fn = call.get("function", {}) or {}
                    name = fn.get("name")
                    args = fn.get("arguments") or {}
                    if isinstance(args, str):
                        try:
                            args = json.loads(args)
                        except ValueError:
                            args = {}
                    result = self._run_tool_with_confirmation(name, args)
                    tool_msg = {"role": "tool", "content": str(result), "name": name}
                    messages.append(tool_msg)
                    self.history.append(tool_msg)

            return "No pude completar esa tarea en modo local (demasiados pasos)."
        except (urllib.error.URLError, TimeoutError, OSError, ValueError):
            self.history = self.history[:snapshot]
            return (
                "Claude no está disponible y tampoco pude usar la IA local de respaldo. "
                "Verificá que Ollama esté instalado y corriendo (ollama serve)."
            )
