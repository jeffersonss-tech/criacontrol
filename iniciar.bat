@echo off
cd /d "%~dp0"
venv\Scripts\python.exe venv\Scripts\streamlit.exe  run app.py
pause