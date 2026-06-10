@echo off
cd /d C:\dev\hd-instrument
set SKIP_KB_AUTOLOAD=1
C:\dev\hd-instrument\.venv-demo\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 < NUL > C:\Users\marsh\backend.log 2> C:\Users\marsh\backend.err
