# JARVIS

Asistente personal por voz/texto que controla tu computador, impulsado por Claude (Anthropic).

## Qué puede hacer

- Conversar por texto o por voz (wake word "jarvis").
- Abrir aplicaciones, archivos, carpetas y URLs.
- Ejecutar comandos de PowerShell.
- Controlar mouse y teclado.
- Buscar archivos, listar/cerrar procesos, consultar CPU/RAM/disco, tomar capturas de pantalla.
- Pide confirmación antes de ejecutar acciones riesgosas (comandos de sistema, cerrar procesos, borrar archivos).

## Instalación

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Copia `.env.example` a `.env` y coloca tu API key de [console.anthropic.com](https://console.anthropic.com):

```
ANTHROPIC_API_KEY=sk-ant-...
```

## Uso

Modo texto (recomendado para empezar):

```bash
python main.py --mode text
```

Modo voz (requiere micrófono):

```bash
python main.py --mode voice
```

Di "jarvis" para activarlo, luego da tu instrucción. Di "salir" en cualquier modo para terminar.

## Notas sobre acentos/ñ en la consola

Si usas `cmd.exe` clásico y ves símbolos raros en vez de tildes, corre antes:

```bash
chcp 65001
```

(Windows Terminal / PowerShell moderno normalmente no lo necesitan).

## Notas sobre pyaudio en Windows

Si `pip install pyaudio` falla, instala el wheel precompilado:

```bash
pip install pipwin
pipwin install pyaudio
```

## Seguridad

Las acciones marcadas como riesgosas (`run_command`, `kill_process`, `delete_path`) piden confirmación
explícita antes de ejecutarse, tanto en modo texto (s/n) como en modo voz (di "sí" o "no").
