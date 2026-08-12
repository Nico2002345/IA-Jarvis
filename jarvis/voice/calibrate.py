"""Herramienta interactiva para calibrar el micrófono de JARVIS.

Permite elegir el dispositivo de entrada correcto y ajustar el
energy_threshold (sensibilidad) hasta que detecte bien la voz sin
dispararse con ruido de fondo. El resultado se guarda en .env.
"""
import sys
from pathlib import Path

import speech_recognition as sr
from dotenv import set_key

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ENV_PATH = Path(__file__).resolve().parent.parent.parent / ".env"


def elegir_microfono() -> int | None:
    nombres = sr.Microphone.list_microphone_names()
    print("\nMicrófonos disponibles:")
    for i, nombre in enumerate(nombres):
        print(f"  [{i}] {nombre}")
    print("  [Enter] usar el dispositivo por defecto del sistema")

    while True:
        eleccion = input("\nElige el número del micrófono a usar: ").strip()
        if eleccion == "":
            return None
        if eleccion.isdigit() and 0 <= int(eleccion) < len(nombres):
            return int(eleccion)
        print("Opción inválida, intenta de nuevo.")


def calibrar_ruido_ambiente(recognizer: sr.Recognizer, microphone: sr.Microphone) -> None:
    print("\nGuarda silencio por 3 segundos, midiendo ruido ambiente...")
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source, duration=3)
    print(f"Umbral base tras ruido ambiente: {recognizer.energy_threshold:.0f}")


def probar_y_ajustar(recognizer: sr.Recognizer, microphone: sr.Microphone) -> None:
    recognizer.dynamic_energy_threshold = False
    while True:
        print(f"\nUmbral actual: {recognizer.energy_threshold:.0f}")
        input("Presiona Enter y di una frase de prueba (tienes 5 segundos)...")
        with microphone as source:
            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            except sr.WaitTimeoutError:
                print("No se detectó ninguna voz (el umbral puede estar muy alto).")
                audio = None

        texto = ""
        if audio is not None:
            try:
                texto = recognizer.recognize_google(audio, language="es-ES")
            except sr.UnknownValueError:
                texto = ""
            except sr.RequestError as e:
                print(f"Error consultando el reconocimiento de voz: {e}")

        print(f"Reconocido: {texto!r}" if texto else "No se entendió nada.")

        respuesta = input(
            "\n¿Cómo estuvo? [b]ien / muy [s]ensible (se activa con ruido) / "
            "poco [d]etecta mi voz / [r]epetir sin cambios: "
        ).strip().lower()

        if respuesta == "b":
            return
        elif respuesta == "s":
            recognizer.energy_threshold *= 1.4
        elif respuesta == "d":
            recognizer.energy_threshold *= 0.7
        # 'r' o cualquier otra cosa: repetir la prueba sin cambiar el umbral


def guardar_configuracion(device_index: int | None, energy_threshold: float) -> None:
    if not ENV_PATH.exists():
        ENV_PATH.touch()

    if device_index is None:
        set_key(str(ENV_PATH), "MIC_DEVICE_INDEX", "")
    else:
        set_key(str(ENV_PATH), "MIC_DEVICE_INDEX", str(device_index))

    set_key(str(ENV_PATH), "ENERGY_THRESHOLD", f"{energy_threshold:.0f}")
    print(f"\nGuardado en {ENV_PATH.name}: MIC_DEVICE_INDEX y ENERGY_THRESHOLD.")


def main():
    print("=== Calibración del micrófono de JARVIS ===")

    device_index = elegir_microfono()
    microphone = sr.Microphone(device_index=device_index)
    recognizer = sr.Recognizer()

    calibrar_ruido_ambiente(recognizer, microphone)
    probar_y_ajustar(recognizer, microphone)
    guardar_configuracion(device_index, recognizer.energy_threshold)

    print("\nListo. La próxima vez que ejecutes JARVIS usará esta calibración.")


if __name__ == "__main__":
    main()
