@echo off
cd /d "%~dp0"
start "Flask - Job Tracker" python -m flask --app app run --host=0.0.0.0 --port=5000
timeout /t 2 /nobreak >nul
start http://localhost:5000