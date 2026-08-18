"""Estética de 'terminal neuronal' para el modo voz: mismos colores (cian/violeta)
que la interfaz web, usando códigos ANSI de color verdadero (24-bit)."""
import sys

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
CYAN_BRIGHT = "\033[38;2;125;249;255m"
CYAN = "\033[38;2;34;211;238m"
VIOLET = "\033[38;2;129;140;248m"
GRAY = "\033[38;2;125;146;179m"

_enabled = False


def enable_ansi():
    """Habilita el procesamiento de secuencias ANSI en la consola de Windows.
    Windows Terminal / PowerShell moderno ya lo soportan; cmd.exe clásico
    necesita que se active explícitamente (no tiene efecto en otros SO)."""
    global _enabled
    if _enabled:
        return
    _enabled = True
    if sys.platform != "win32":
        return
    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
        mode = ctypes.c_uint32()
        kernel32.GetConsoleMode(handle, ctypes.byref(mode))
        kernel32.SetConsoleMode(handle, mode.value | 0x0004)  # ENABLE_VIRTUAL_TERMINAL_PROCESSING
    except Exception:
        pass


def banner():
    letters = list("JARVIS")
    colors = [CYAN_BRIGHT, CYAN_BRIGHT, CYAN, CYAN, VIOLET, VIOLET]
    title = " ".join(f"{c}{ch}{RESET}" for ch, c in zip(letters, colors))
    line = f"{DIM}{'─' * 46}{RESET}"
    print()
    print(line)
    print(f"  {CYAN_BRIGHT}◉{RESET}  {BOLD}{title}{RESET}   {DIM}· terminal neuronal{RESET}")
    print(line)
    print()


def status(text: str):
    print(f"{GRAY}{text}{RESET}")


def user_line(text: str):
    print(f"{VIOLET}Tú:{RESET} {text}")


def jarvis_line(text: str):
    print(f"{CYAN_BRIGHT}JARVIS:{RESET} {text}")
