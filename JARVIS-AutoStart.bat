@echo off
cd /d "%~dp0"
start "JARVIS - Voz" /min cmd /k "call .venv\Scripts\activate.bat && python main.py --mode voice"
start "JARVIS - Web" /min cmd /k "call .venv\Scripts\activate.bat && python -m jarvis.web.server"
