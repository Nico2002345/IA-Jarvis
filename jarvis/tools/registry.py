from jarvis.tools import system_control as sc
from jarvis.tools import input_control as ic
from jarvis.config import DANGEROUS_TOOLS

TOOLS = [
    {
        "name": "open_application",
        "description": "Abre una aplicación instalada en el computador por su nombre (ej. 'chrome', 'notepad', 'calculadora').",
        "input_schema": {
            "type": "object",
            "properties": {"name": {"type": "string", "description": "Nombre de la aplicación a abrir"}},
            "required": ["name"],
        },
    },
    {
        "name": "open_path",
        "description": "Abre un archivo, carpeta o URL con la aplicación predeterminada del sistema.",
        "input_schema": {
            "type": "object",
            "properties": {"path": {"type": "string", "description": "Ruta de archivo/carpeta o URL"}},
            "required": ["path"],
        },
    },
    {
        "name": "run_command",
        "description": "Ejecuta un comando de PowerShell en el sistema y devuelve su salida. Usar con cuidado: puede modificar el sistema.",
        "input_schema": {
            "type": "object",
            "properties": {"command": {"type": "string", "description": "Comando de PowerShell a ejecutar"}},
            "required": ["command"],
        },
    },
    {
        "name": "list_processes",
        "description": "Lista los procesos en ejecución, opcionalmente filtrados por nombre.",
        "input_schema": {
            "type": "object",
            "properties": {"filter_name": {"type": "string", "description": "Texto para filtrar por nombre de proceso"}},
            "required": [],
        },
    },
    {
        "name": "kill_process",
        "description": "Cierra un proceso en ejecución por nombre o PID.",
        "input_schema": {
            "type": "object",
            "properties": {"name_or_pid": {"type": "string", "description": "Nombre del proceso o PID"}},
            "required": ["name_or_pid"],
        },
    },
    {
        "name": "get_system_info",
        "description": "Devuelve el uso actual de CPU, memoria RAM y disco.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "search_files",
        "description": "Busca archivos por nombre dentro de una carpeta (por defecto la carpeta de usuario).",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Texto a buscar en el nombre del archivo"},
                "root": {"type": "string", "description": "Carpeta raíz donde buscar (opcional)"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "delete_path",
        "description": "Elimina permanentemente un archivo o carpeta.",
        "input_schema": {
            "type": "object",
            "properties": {"path": {"type": "string", "description": "Ruta del archivo o carpeta a eliminar"}},
            "required": ["path"],
        },
    },
    {
        "name": "mouse_move",
        "description": "Mueve el cursor del mouse a una coordenada absoluta de pantalla.",
        "input_schema": {
            "type": "object",
            "properties": {"x": {"type": "integer"}, "y": {"type": "integer"}},
            "required": ["x", "y"],
        },
    },
    {
        "name": "mouse_click",
        "description": "Hace clic con el mouse, opcionalmente moviéndolo primero a una coordenada.",
        "input_schema": {
            "type": "object",
            "properties": {
                "x": {"type": "integer"},
                "y": {"type": "integer"},
                "button": {"type": "string", "enum": ["left", "right", "middle"]},
                "clicks": {"type": "integer"},
            },
            "required": [],
        },
    },
    {
        "name": "keyboard_type",
        "description": "Escribe texto en la ventana/aplicación actualmente enfocada.",
        "input_schema": {
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
        },
    },
    {
        "name": "keyboard_hotkey",
        "description": "Presiona una combinación de teclas, ej. ['ctrl','c'] o ['alt','tab'].",
        "input_schema": {
            "type": "object",
            "properties": {"keys": {"type": "array", "items": {"type": "string"}}},
            "required": ["keys"],
        },
    },
    {
        "name": "get_screen_size",
        "description": "Devuelve el tamaño de la pantalla en píxeles.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "take_screenshot",
        "description": "Toma una captura de pantalla completa y la guarda en disco.",
        "input_schema": {
            "type": "object",
            "properties": {"save_path": {"type": "string", "description": "Ruta donde guardar (opcional)"}},
            "required": [],
        },
    },
]

_DISPATCH = {
    "open_application": lambda i: sc.open_application(i["name"]),
    "open_path": lambda i: sc.open_path(i["path"]),
    "run_command": lambda i: sc.run_command(i["command"]),
    "list_processes": lambda i: sc.list_processes(i.get("filter_name", "")),
    "kill_process": lambda i: sc.kill_process(i["name_or_pid"]),
    "get_system_info": lambda i: sc.get_system_info(),
    "search_files": lambda i: sc.search_files(i["query"], i.get("root", "")),
    "delete_path": lambda i: sc.delete_path(i["path"]),
    "mouse_move": lambda i: ic.mouse_move(i["x"], i["y"]),
    "mouse_click": lambda i: ic.mouse_click(i.get("x"), i.get("y"), i.get("button", "left"), i.get("clicks", 1)),
    "keyboard_type": lambda i: ic.keyboard_type(i["text"]),
    "keyboard_hotkey": lambda i: ic.keyboard_hotkey(i["keys"]),
    "get_screen_size": lambda i: ic.get_screen_size(),
    "take_screenshot": lambda i: ic.take_screenshot(i.get("save_path", "")),
}


def describe_call(tool_name: str, tool_input: dict) -> str:
    args = ", ".join(f"{k}={v}" for k, v in tool_input.items())
    return f"{tool_name}({args})"


def is_dangerous(tool_name: str) -> bool:
    return tool_name in DANGEROUS_TOOLS


def execute_tool(tool_name: str, tool_input: dict) -> str:
    handler = _DISPATCH.get(tool_name)
    if handler is None:
        return f"Herramienta desconocida: {tool_name}"
    try:
        return handler(tool_input)
    except Exception as e:
        return f"Error ejecutando {tool_name}: {e}"
