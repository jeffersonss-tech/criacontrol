@echo off
cd /d "%~dp0"
venv\Scripts\python.exe venv\Scripts\streamlit.exe run app.py --server.address=0.0.0.0 --server.port=8501
pause