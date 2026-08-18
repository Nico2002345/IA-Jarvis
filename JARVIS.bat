@echo off
chcp 65001 >nul
color 0B
title JARVIS
cd /d "%~dp0"
call .venv\Scripts\activate.bat
python main.py --mode voice
pause
