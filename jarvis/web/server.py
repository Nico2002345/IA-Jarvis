import os
import socket
import threading

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from jarvis.brain import Brain
from jarvis.config import WEB_TOKEN

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
PORT = 8765

app = FastAPI()

_state_lock = threading.Lock()
_pending = {"desc": None, "event": threading.Event(), "answer": None}


def _web_confirm(desc: str) -> bool:
    with _state_lock:
        _pending["desc"] = desc
        _pending["answer"] = None
        _pending["event"].clear()
    got_answer = _pending["event"].wait(timeout=90)
    with _state_lock:
        _pending["desc"] = None
        approved = got_answer and bool(_pending["answer"])
    return approved


brain = Brain(confirm_callback=_web_confirm)
_chat_lock = threading.Lock()


def _check_auth(authorization: str | None):
    if not WEB_TOKEN:
        raise HTTPException(500, "Falta JARVIS_WEB_TOKEN en .env")
    token = (authorization or "").removeprefix("Bearer ").strip()
    if token != WEB_TOKEN:
        raise HTTPException(401, "Token inválido")


class ChatIn(BaseModel):
    message: str


class ConfirmIn(BaseModel):
    approved: bool


@app.get("/")
def index():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


@app.post("/api/chat")
def chat(body: ChatIn, authorization: str | None = Header(default=None)):
    _check_auth(authorization)
    with _chat_lock:
        try:
            reply = brain.ask(body.message)
        except Exception as e:
            reply = f"Tuve un error interno procesando eso ({e}). Probá de nuevo."
    return {"reply": reply}


@app.get("/api/pending")
def get_pending(authorization: str | None = Header(default=None)):
    _check_auth(authorization)
    return {"desc": _pending["desc"]}


@app.post("/api/confirm")
def confirm(body: ConfirmIn, authorization: str | None = Header(default=None)):
    _check_auth(authorization)
    with _state_lock:
        _pending["answer"] = body.approved
        _pending["event"].set()
    return {"ok": True}


def _local_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


def main():
    import uvicorn

    if not WEB_TOKEN:
        print(
            "Falta JARVIS_WEB_TOKEN en .env. Agrega una clave secreta propia, ej.:\n"
            "  JARVIS_WEB_TOKEN=una-clave-larga-y-dificil-de-adivinar\n"
        )
        raise SystemExit(1)

    ip = _local_ip()
    print("JARVIS Web escuchando.")
    print(f"Desde tu teléfono, en la MISMA red WiFi, abre en el navegador:\n")
    print(f"  http://{ip}:{PORT}\n")
    print("Ingresa el token configurado en JARVIS_WEB_TOKEN para entrar.")
    print("Ctrl+C para detener.\n")
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="warning")


if __name__ == "__main__":
    main()
