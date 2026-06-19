@echo off
REM Truly detached start: cmd's "start" with no window survives the SSH parent.
REM Logs to user home for external polling.

REM Cleanup first
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do taskkill /F /PID %%a 2>nul
taskkill /F /IM cloudflared.exe 2>nul
del C:\Users\marsh\backend.log C:\Users\marsh\backend.err C:\Users\marsh\cloudflared.log C:\Users\marsh\cloudflared.err C:\Users\marsh\public_url.txt 2>nul

REM Start backend via wmic (truly detached) and capture PID
wmic process call create "cmd /c C:\dev\hd-instrument\.venv-demo\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 > C:\Users\marsh\backend.log 2> C:\Users\marsh\backend.err","C:\dev\hd-instrument" | findstr "ProcessId"

REM Wait for backend to boot
ping 127.0.0.1 -n 6 >nul

REM Start cloudflared (no auth needed for trycloudflare quick mode)
wmic process call create "cmd /c \"\"C:\Program Files (x86)\cloudflared\cloudflared.exe\" tunnel --url http://localhost:8000 > C:\Users\marsh\cloudflared.log 2> C:\Users\marsh\cloudflared.err\"","C:\Users\marsh" | findstr "ProcessId"

REM Wait for cloudflared to provision URL (typical 5-15 sec)
echo Waiting up to 40s for tunnel URL...
set TRIES=0
:WAIT_URL
ping 127.0.0.1 -n 4 >nul
set /a TRIES+=1
type C:\Users\marsh\cloudflared.err 2>nul | findstr "trycloudflare.com" > C:\Users\marsh\url_match.txt
for %%i in (C:\Users\marsh\url_match.txt) do if %%~zi gtr 0 goto FOUND
if %TRIES% lss 12 goto WAIT_URL
echo TIMED OUT
goto END

:FOUND
echo === PUBLIC URL ===
type C:\Users\marsh\url_match.txt
echo.
type C:\Users\marsh\cloudflared.err | findstr /R "https://.*trycloudflare\.com" > C:\Users\marsh\public_url.txt
type C:\Users\marsh\public_url.txt

:END
echo === port 8000 listener ===
netstat -ano | findstr :8000 | findstr LISTENING

echo === backend.log tail ===
type C:\Users\marsh\backend.log 2>nul

echo === DONE ===
