@echo off
echo === all uvicorn / backend.main python procs ===
wmic process where "name='python.exe'" get ProcessId,CommandLine /format:list 2>nul | findstr /I "uvicorn backend.main"
echo.
echo === port 8000 (LISTENING or TIME_WAIT) ===
netstat -ano | findstr :8000
echo.
echo === cloudflared status ===
tasklist | findstr cloudflared
echo.
echo === backend.log FULL ===
powershell -Command "Get-Content C:\Users\marsh\backend.log -EA SilentlyContinue"
echo.
echo === backend.err FULL ===
powershell -Command "Get-Content C:\Users\marsh\backend.err -EA SilentlyContinue"
