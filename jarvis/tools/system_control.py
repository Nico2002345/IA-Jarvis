import os
import subprocess
import webbrowser
import psutil
from pathlib import Path

# Alias en español/inglés -> ejecutable o comando real de Windows
APP_ALIASES = {
    "explorador": "explorer.exe",
    "explorer": "explorer.exe",
    "calculadora": "calc.exe",
    "calculator": "calc.exe",
    "bloc de notas": "notepad.exe",
    "notepad": "notepad.exe",
    "paint": "mspaint.exe",
    "cmd": "cmd.exe",
    "consola": "cmd.exe",
    "terminal": "wt.exe",
    "powershell": "powershell.exe",
    "panel de control": "control.exe",
    "administrador de tareas": "taskmgr.exe",
    "task manager": "taskmgr.exe",
    "word": "winword.exe",
    "excel": "excel.exe",
    "powerpoint": "powerpnt.exe",
    "chrome": "chrome.exe",
    "navegador": "chrome.exe",
    "edge": "msedge.exe",
    "spotify": "spotify.exe",
    "vscode": "code.exe",
    "visual studio code": "code.exe",
    "code": "code.exe",
}


def open_application(name: str) -> str:
    """Abre una aplicación por nombre (usa el comando 'start' de Windows)."""
    key = name.strip().lower()
    target = APP_ALIASES.get(key, name)
    try:
        subprocess.Popen(f'start "" "{target}"', shell=True)
        return f"Abriendo {name}."
    except Exception as e:
        return f"No pude abrir {name}: {e}"


def open_path(path: str) -> str:
    """Abre un archivo, carpeta o URL con la aplicación predeterminada del sistema."""
    try:
        if path.startswith(("http://", "https://")):
            webbrowser.open(path)
            return f"Abriendo {path} en el navegador."
        p = Path(path).expanduser()
        if not p.exists():
            return f"La ruta no existe: {path}"
        os.startfile(str(p))
        return f"Abriendo {path}."
    except Exception as e:
        return f"No pude abrir {path}: {e}"


def run_command(command: str) -> str:
    """Ejecuta un comando en PowerShell y devuelve su salida. Acción riesgosa: requiere confirmación."""
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", command],
            capture_output=True,
            text=True,
            timeout=30,
        )
        output = (result.stdout or "") + (result.stderr or "")
        output = output.strip()
        return output[:3000] if output else "Comando ejecutado sin salida."
    except subprocess.TimeoutExpired:
        return "El comando tardó demasiado y fue cancelado."
    except Exception as e:
        return f"Error ejecutando comando: {e}"


def list_processes(filter_name: str = "") -> str:
    """Lista procesos en ejecución, opcionalmente filtrados por nombre."""
    procs = []
    for p in psutil.process_iter(["pid", "name"]):
        try:
            name = p.info["name"] or ""
            if filter_name.lower() in name.lower():
                procs.append(f"{p.info['pid']}: {name}")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    if not procs:
        return "No se encontraron procesos."
    return "\n".join(procs[:50])


def kill_process(name_or_pid: str) -> str:
    """Cierra un proceso por nombre o PID. Acción riesgosa: requiere confirmación."""
    killed = []
    try:
        pid = int(name_or_pid)
        p = psutil.Process(pid)
        p.terminate()
        return f"Proceso {pid} ({p.name()}) cerrado."
    except ValueError:
        pass
    except psutil.NoSuchProcess:
        return f"No existe un proceso con PID {name_or_pid}."

    for p in psutil.process_iter(["pid", "name"]):
        try:
            if name_or_pid.lower() in (p.info["name"] or "").lower():
                p.terminate()
                killed.append(p.info["name"])
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    if killed:
        return f"Cerrados: {', '.join(killed)}"
    return f"No se encontró ningún proceso llamado '{name_or_pid}'."


def get_system_info() -> str:
    """Devuelve uso de CPU, memoria y disco del sistema."""
    cpu = psutil.cpu_percent(interval=0.5)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("C:\\")
    return (
        f"CPU: {cpu}%\n"
        f"Memoria: {mem.percent}% usada ({mem.used // (1024**2)} MB / {mem.total // (1024**2)} MB)\n"
        f"Disco C: {disk.percent}% usado ({disk.used // (1024**3)} GB / {disk.total // (1024**3)} GB)"
    )


def search_files(query: str, root: str = "") -> str:
    """Busca archivos por nombre bajo una carpeta raíz (por defecto la carpeta de usuario)."""
    base = Path(root).expanduser() if root else Path.home()
    if not base.exists():
        return f"La carpeta no existe: {base}"
    matches = []
    query_lower = query.lower()
    try:
        for p in base.rglob("*"):
            if query_lower in p.name.lower():
                matches.append(str(p))
                if len(matches) >= 30:
                    break
    except PermissionError:
        pass
    if not matches:
        return f"No se encontraron archivos que coincidan con '{query}' en {base}."
    return "\n".join(matches)


def delete_path(path: str) -> str:
    """Elimina un archivo o carpeta. Acción riesgosa: requiere confirmación."""
    import shutil

    p = Path(path).expanduser()
    if not p.exists():
        return f"La ruta no existe: {path}"
    try:
        if p.is_dir():
            shutil.rmtree(p)
        else:
            p.unlink()
        return f"Eliminado: {path}"
    except Exception as e:
        return f"No pude eliminar {path}: {e}"
