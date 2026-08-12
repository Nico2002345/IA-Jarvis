from anthropic import Anthropic
from jarvis.config import ANTHROPIC_API_KEY, CLAUDE_MODEL
from jarvis.tools.registry import TOOLS, execute_tool, is_dangerous, describe_call

SYSTEM_PROMPT = """Eres JARVIS, un asistente personal por voz/texto que corre en el computador del usuario.
Tienes acceso a herramientas que te permiten abrir aplicaciones, archivos y carpetas, ejecutar comandos
del sistema, controlar el mouse y el teclado, buscar archivos y obtener información del sistema.

Reglas:
- Responde siempre en español, de forma breve y natural (esto se lee en voz alta, evita listas largas o markdown).
- Usa las herramientas cuando el usuario te pida hacer algo en el computador, no solo describir cómo hacerlo.
- Antes de ejecutar acciones destructivas o irreversibles, asegúrate de que la intención del usuario sea clara.
- Si una herramienta fue bloqueada porque el usuario no confirmó, no insistas, solo infórmalo brevemente.
- Sé proactivo pero no ejecutes múltiples acciones grandes sin que el usuario lo haya pedido.
"""


class Brain:
    def __init__(self, confirm_callback=None):
        """confirm_callback(description: str) -> bool. Si es None, todo se aprueba automáticamente."""
        self.client = Anthropic(api_key=ANTHROPIC_API_KEY)
        self.history = []
        self.confirm_callback = confirm_callback or (lambda desc: True)

    def _run_tool_with_confirmation(self, tool_name: str, tool_input: dict) -> str:
        if is_dangerous(tool_name):
            desc = describe_call(tool_name, tool_input)
            approved = self.confirm_callback(desc)
            if not approved:
                return f"Acción cancelada por el usuario: {desc}"
        return execute_tool(tool_name, tool_input)

    def ask(self, user_text: str) -> str:
        self.history.append({"role": "user", "content": user_text})

        while True:
            response = self.client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                tools=TOOLS,
                messages=self.history,
            )

            self.history.append({"role": "assistant", "content": response.content})

            if response.stop_reason != "tool_use":
                return "".join(b.text for b in response.content if b.type == "text").strip()

            tool_results = []
            for block in response.content:
                if block.type != "tool_use":
                    continue
                result = self._run_tool_with_confirmation(block.name, block.input)
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": str(result),
                    }
                )

            self.history.append({"role": "user", "content": tool_results})
