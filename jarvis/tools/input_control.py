import pyautogui

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.05


def mouse_move(x: int, y: int) -> str:
    """Mueve el mouse a una coordenada absoluta de pantalla."""
    pyautogui.moveTo(x, y, duration=0.2)
    return f"Mouse movido a ({x}, {y})."


def mouse_click(x: int = None, y: int = None, button: str = "left", clicks: int = 1) -> str:
    """Hace clic con el mouse, opcionalmente moviéndolo primero a (x, y)."""
    if x is not None and y is not None:
        pyautogui.moveTo(x, y, duration=0.2)
    pyautogui.click(button=button, clicks=clicks)
    return f"Clic {button} realizado" + (f" en ({x}, {y})." if x is not None else ".")


def keyboard_type(text: str) -> str:
    """Escribe texto en la ventana activa, como si fuera tecleado."""
    pyautogui.write(text, interval=0.02)
    return f"Texto escrito: {text[:50]}"


def keyboard_hotkey(keys: list) -> str:
    """Presiona una combinación de teclas, ej. ['ctrl', 'c']."""
    pyautogui.hotkey(*keys)
    return f"Combinación de teclas: {'+'.join(keys)}"


def get_screen_size() -> str:
    """Devuelve el tamaño de la pantalla en píxeles."""
    w, h = pyautogui.size()
    return f"{w}x{h}"


def take_screenshot(save_path: str = "") -> str:
    """Toma una captura de pantalla y la guarda en disco."""
    from pathlib import Path
    import datetime

    if not save_path:
        save_path = str(
            Path.home() / "Pictures" / f"jarvis_screenshot_{datetime.datetime.now():%Y%m%d_%H%M%S}.png"
        )
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    img = pyautogui.screenshot()
    img.save(save_path)
    return f"Captura guardada en {save_path}"
