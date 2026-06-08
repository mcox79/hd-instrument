@echo off
echo === [%TIME%] start backend in background ===
set PY=C:\dev\hd-instrument\.venv-demo\Scripts\python.exe
cd /d C:\dev\hd-instrument
start /B "" "%PY%" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 > C:\Users\marsh\backend.log 2>&1

echo === [%TIME%] wait for boot (5s) ===
timeout /t 5 /nobreak >nul

echo === [%TIME%] test endpoints via httpx (already installed) ===
"%PY%" -c "import httpx; r = httpx.get('http://127.0.0.1:8000/'); print('GET / ->', r.status_code, r.json())" 2>&1
echo.
"%PY%" -c "import httpx; r = httpx.get('http://127.0.0.1:8000/admin/demo-mode-status'); print('GET /admin/demo-mode-status ->', r.status_code, r.json())" 2>&1
echo.
"%PY%" -c "import httpx; r = httpx.post('http://127.0.0.1:8000/admin/demo-mode-on'); print('POST /admin/demo-mode-on ->', r.status_code, r.json())" 2>&1
echo.
"%PY%" -c "import httpx; r = httpx.get('http://127.0.0.1:8000/admin/demo-mode-status'); print('GET status (active) ->', r.status_code, r.json())" 2>&1
echo.
"%PY%" -c "import httpx; r = httpx.post('http://127.0.0.1:8000/admin/demo-mode-off'); print('POST /admin/demo-mode-off ->', r.status_code, r.json())" 2>&1
echo.
"%PY%" -c "import httpx; r = httpx.post('http://127.0.0.1:8000/query', json={'question':'who is the CEO of OpenAI?'}); print('POST /query ->', r.status_code); import json; print(json.dumps(r.json(), indent=2)[:500])" 2>&1
echo.

echo === [%TIME%] kill backend ===
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do taskkill /F /PID %%a 2>nul

echo === [%TIME%] DONE ===
