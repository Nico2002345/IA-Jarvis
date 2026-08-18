import os
import subprocess
import urllib.parse
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
    "visual studio": "devenv.exe",
}


def _find_shortcut(query: str):
    """Busca un acceso directo (.lnk) en el Menú Inicio cuyo nombre coincida con la consulta."""
    query_lower = query.strip().lower()
    search_dirs = [
        Path(os.environ.get("ProgramData", "")) / "Microsoft/Windows/Start Menu/Programs",
        Path(os.environ.get("APPDATA", "")) / "Microsoft/Windows/Start Menu/Programs",
    ]
    best = None
    for base in search_dirs:
        if not base.exists():
            continue
        try:
            for p in base.rglob("*.lnk"):
                name = p.stem.lower()
                if name == query_lower:
                    return p
                if query_lower in name and best is None:
                    best = p
        except PermissionError:
            continue
    return best


def _find_uwp_app(query: str):
    """Busca una app instalada desde Microsoft Store (UWP), que no tiene acceso directo
    tradicional en el Menú Inicio, y devuelve su AppID para poder lanzarla."""
    query_lower = query.strip().lower()
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "Get-StartApps | ForEach-Object { \"$($_.Name)|$($_.AppID)\" }"],
            capture_output=True, text=True, timeout=15,
        )
    except Exception:
        return None
    best = None
    for line in result.stdout.splitlines():
        if "|" not in line:
            continue
        app_name, app_id = line.rsplit("|", 1)
        app_name = app_name.strip().lower()
        app_id = app_id.strip()
        if not app_id:
            continue
        if app_name == query_lower:
            return app_id
        if query_lower in app_name and best is None:
            best = app_id
    return best


def _launch_uwp_app(app_id: str) -> None:
    subprocess.Popen(["explorer.exe", f"shell:AppsFolder\\{app_id}"])


def open_application(name: str) -> str:
    """Abre una aplicación por nombre. Prueba, en orden: alias de ejecutables conocidos,
    accesos directos del Menú Inicio, y apps instaladas desde Microsoft Store."""
    key = name.strip().lower()
    if key in APP_ALIASES:
        try:
            subprocess.Popen(f'start "" "{APP_ALIASES[key]}"', shell=True)
            return f"Abriendo {name}."
        except Exception as e:
            return f"No pude abrir {name}: {e}"

    shortcut = _find_shortcut(name)
    if shortcut:
        try:
            os.startfile(str(shortcut))
            return f"Abriendo {name}."
        except Exception as e:
            return f"No pude abrir {name}: {e}"

    app_id = _find_uwp_app(name)
    if app_id:
        try:
            _launch_uwp_app(app_id)
            return f"Abriendo {name}."
        except Exception as e:
            return f"No pude abrir {name}: {e}"

    try:
        subprocess.Popen(f'start "" "{name}"', shell=True)
        return f"Abriendo {name}."
    except Exception as e:
        return f"No pude abrir {name}: {e}"


def open_whatsapp() -> str:
    """Abre la app de escritorio de WhatsApp (acceso directo o app de Store); si no está
    instalada, usa la versión web."""
    shortcut = _find_shortcut("whatsapp")
    if shortcut:
        try:
            os.startfile(str(shortcut))
            return "Abriendo WhatsApp."
        except Exception:
            pass

    app_id = _find_uwp_app("whatsapp")
    if app_id:
        try:
            _launch_uwp_app(app_id)
            return "Abriendo WhatsApp."
        except Exception:
            pass

    return open_path("https://web.whatsapp.com")


def search_youtube(query: str) -> str:
    """Busca algo en YouTube y abre los resultados en el navegador."""
    url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote(query)
    webbrowser.open(url)
    return f'Buscando "{query}" en YouTube.'


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


def create_excel_chart(title: str, categories: list, values: list, chart_type: str = "bar") -> str:
    """Crea un archivo Excel (.xlsx) con una tabla de datos y una gráfica, y lo abre.
    chart_type: 'bar', 'line' o 'pie'."""
    import datetime
    from openpyxl import Workbook
    from openpyxl.chart import BarChart, LineChart, PieChart, Reference

    if not categories or not values:
        return "Faltan datos: necesito categorías y valores para armar la gráfica."
    if len(categories) != len(values):
        return "La cantidad de categorías y de valores no coincide."

    wb = Workbook()
    ws = wb.active
    ws.title = "Datos"
    ws.append(["Categoría", "Valor"])
    for cat, val in zip(categories, values):
        ws.append([str(cat), val])

    chart_classes = {"bar": BarChart, "line": LineChart, "pie": PieChart}
    chart = chart_classes.get(chart_type, BarChart)()
    chart.title = title
    data = Reference(ws, min_col=2, min_row=1, max_row=len(categories) + 1)
    cats = Reference(ws, min_col=1, min_row=2, max_row=len(categories) + 1)
    chart.add_data(data, titles_from_data=True)
    chart.set_categories(cats)
    ws.add_chart(chart, "D2")

    save_path = Path.home() / "Documents" / f"jarvis_grafica_{datetime.datetime.now():%Y%m%d_%H%M%S}.xlsx"
    save_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        wb.save(save_path)
        os.startfile(save_path)
        return f"Gráfica creada y abierta en Excel: {save_path}"
    except Exception as e:
        return f"No pude crear o abrir el archivo: {e}"
