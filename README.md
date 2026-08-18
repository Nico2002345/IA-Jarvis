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

Modo web (para controlar JARVIS desde el teléfono):

```bash
python -m jarvis.web.server
```

o hacé doble clic en `JARVIS-Web.bat`.

## Modo web / usar JARVIS desde el celular

Este modo levanta un pequeño servidor en tu PC con una página de chat pensada para el navegador del teléfono.
La PC sigue siendo la que ejecuta todo (abrir apps, PowerShell, mouse/teclado); el teléfono solo envía y recibe mensajes.

1. Agrega un token secreto en tu `.env` (ya viene uno generado automáticamente, pero podés cambiarlo):
   ```
   JARVIS_WEB_TOKEN=una-clave-larga-y-dificil-de-adivinar
   ```
2. Corre `JARVIS-Web.bat` (o `python -m jarvis.web.server`). La consola te va a mostrar algo como:
   ```
   http://192.168.1.147:8765
   ```
3. Con el teléfono conectado a **la misma red WiFi** que la PC, abre esa dirección en el navegador.
4. Ingresa el token cuando te lo pida (se guarda en el teléfono, no hace falta repetirlo cada vez).
5. Chatea normalmente. Si JARVIS necesita ejecutar algo riesgoso (`run_command`, `kill_process`, `delete_path`),
   te va a mostrar un cuadro de confirmación con Sí/No antes de hacerlo, igual que en modo texto/voz.

**Importante:** este modo no tiene cifrado (HTTP simple) y depende solo del token para protegerse, así que
úsalo únicamente dentro de tu red WiFi de confianza (no lo expongas a internet sin agregar algo como Tailscale
o una VPN de por medio). La PC debe estar prendida y corriendo el servidor para que el teléfono pueda usarlo.

Para acceder desde fuera de casa (por ejemplo con datos móviles), instala [Tailscale](https://tailscale.com/)
en la PC y en el teléfono: te da una IP privada estable a la que podés conectarte desde cualquier lado sin
exponer nada públicamente.

## Respaldo local gratuito (sin créditos de Claude)

JARVIS resuelve localmente y sin llamar a ninguna API los comandos básicos (abrir apps,
subir/bajar volumen, apagar/reiniciar el PC, cerrar apps, decir la hora — ver `jarvis/tools/quick_commands.py`).

Para todo lo demás (preguntas abiertas, tareas que requieren razonar), si la API de Claude falla por
cualquier motivo (sin créditos, sin internet, rate limit), JARVIS cambia automáticamente a un modelo de
IA local y gratuito corriendo en tu propia PC con [Ollama](https://ollama.com), sin que tengas que hacer nada.

Instalación (una sola vez):

```bash
winget install --id Ollama.Ollama -e
ollama pull llama3.2:3b
```

En `.env` podés elegir el modelo local con `OLLAMA_MODEL` (por defecto `llama3.2:3b`, rápido y liviano;
`qwen2.5:7b` da mejores respuestas pero es más lento). El modelo local también puede usar las mismas
herramientas que Claude (abrir apps, PowerShell, etc.), aunque con menor precisión.

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
