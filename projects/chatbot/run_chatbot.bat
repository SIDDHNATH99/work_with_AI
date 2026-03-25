@echo off
cd /d "%~dp0"
echo Starting CortexChat...
uvicorn main:app --host 127.0.0.1 --port 8001
pause