import argparse
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stdin.reconfigure(encoding="utf-8")

from jarvis.config import ANTHROPIC_API_KEY
from jarvis.brain import Brain
from jarvis.tools import quick_commands

EXIT_WORDS = {"salir", "exit", "quit", "adiós", "adios", "hasta luego"}


def check_api_key():
    if not ANTHROPIC_API_KEY:
        print(
            "Falta ANTHROPIC_API_KEY. Copia .env.example a .env y pon tu API key "
            "de console.anthropic.com antes de continuar."
        )
        sys.exit(1)


def run_text_mode():
    def confirm(desc: str) -> bool:
        answer = input(f"\n[JARVIS quiere ejecutar: {desc}] ¿Confirmas? (s/n): ").strip().lower()
        return answer in ("s", "si", "sí", "y", "yes")

    brain = Brain(confirm_callback=confirm)
    print("JARVIS listo (modo texto). Escribe 'salir' para terminar.\n")
    while True:
        try:
            user_text = input("Tú: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nHasta luego.")
            break
        if not user_text:
            continue
        if user_text.lower() in EXIT_WORDS:
            print("JARVIS: Hasta luego.")
            break
        quick_reply = quick_commands.handle(user_text, confirm_callback=confirm)
        if quick_reply is not None:
            print(f"JARVIS: {quick_reply}\n")
            continue
        reply = brain.ask(user_text)
        print(f"JARVIS: {reply}\n")


def run_voice_mode():
    from jarvis.voice.listener import Listener
    from jarvis.voice.speaker import Speaker

    speaker = Speaker()
    listener = Listener()

    def confirm(desc: str) -> bool:
        speaker.say(f"¿Confirmas que ejecute {desc}? Di sí o no.")
        for _ in range(2):
            answer = listener.listen_command(timeout=6, phrase_time_limit=4)
            if any(w in answer for w in ("sí", "si", "afirmativo", "dale", "confirmo")):
                return True
            if any(w in answer for w in ("no", "cancela", "negativo")):
                return False
        return False

    brain = Brain(confirm_callback=confirm)
    speaker.say("JARVIS en línea.")
    print("JARVIS listo (modo voz). Ctrl+C para terminar.\n")

    CONVERSATION_TIMEOUT = 10  # segundos de silencio antes de volver a pedir la palabra clave

    while True:
        try:
            if not listener.wait_for_wake_word():
                continue
            speaker.say("Dime.")
            while True:
                user_text = listener.listen_command(timeout=CONVERSATION_TIMEOUT)
                if not user_text:
                    speaker.say("Te dejo, decí 'jarvis' cuando quieras seguir hablando.")
                    break
                print(f"Tú: {user_text}")
                if user_text.lower() in EXIT_WORDS:
                    speaker.say("Hasta luego.")
                    return
                quick_reply = quick_commands.handle(user_text, confirm_callback=confirm)
                if quick_reply is not None:
                    speaker.say(quick_reply)
                    continue
                try:
                    reply = brain.ask(user_text)
                except Exception as e:
                    print(f"Error al consultar a Claude: {e}")
                    reply = "Tuve un error interno procesando eso. Probá de nuevo."
                speaker.say(reply or "No tengo una respuesta para eso.")
        except KeyboardInterrupt:
            print("\nHasta luego.")
            break


def main():
    parser = argparse.ArgumentParser(description="JARVIS - asistente personal")
    parser.add_argument("--mode", choices=["text", "voice"], default="text", help="Modo de interacción")
    args = parser.parse_args()

    check_api_key()

    if args.mode == "voice":
        run_voice_mode()
    else:
        run_text_mode()


if __name__ == "__main__":
    main()
