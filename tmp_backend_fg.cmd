@echo off
cd /d C:\dev\hd-instrument
echo === starting uvicorn FOREGROUND with full output ===
C:\dev\hd-instrument\.venv-demo\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --log-level info 2>&1
echo === uvicorn exited with %ERRORLEVEL% ===
