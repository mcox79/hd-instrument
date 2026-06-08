@echo off
REM Cleanup any prior runs
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do taskkill /F /PID %%a 2>nul
taskkill /F /IM cloudflared.exe 2>nul
del C:\Users\marsh\backend.log C:\Users\marsh\backend.err C:\Users\marsh\cloudflared.log C:\Users\marsh\cloudflared.err C:\Users\marsh\public_url.txt 2>nul

REM Use wmic process call create with simple batch wrappers (no quoting issues)
wmic process call create "C:\Users\marsh\tmp_run_backend.bat" | findstr "ProcessId"
ping 127.0.0.1 -n 7 >nul

wmic process call create "C:\Users\marsh\tmp_run_cloudflared.bat" | findstr "ProcessId"

REM Poll for the trycloudflare URL
echo Waiting for tunnel URL...
set TRIES=0
:WAIT_URL
ping 127.0.0.1 -n 4 >nul
set /a TRIES+=1
findstr /R "https://.*trycloudflare\.com" C:\Users\marsh\cloudflared.err 2>nul > C:\Users\marsh\public_url.txt
for %%i in (C:\Users\marsh\public_url.txt) do if %%~zi gtr 0 goto FOUND
if %TRIES% lss 15 goto WAIT_URL
echo TUNNEL TIMED OUT after 60s; check C:\Users\marsh\cloudflared.err
goto END

:FOUND
echo === PUBLIC URL FOUND ===
type C:\Users\marsh\public_url.txt

:END
echo === port 8000 listener ===
netstat -ano | findstr :8000 | findstr LISTENING
echo === processes ===
tasklist | findstr /I "python cloudflared"
echo === DONE ===
