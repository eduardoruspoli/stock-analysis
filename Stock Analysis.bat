@echo off
title Stock Analysis
cd /d "%~dp0"
echo Starting Stock Analysis...
echo Close this window to stop the app.
echo.
"venv\Scripts\python.exe" -m streamlit run app.py
pause
