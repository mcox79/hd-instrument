@echo off
echo === port 8000 listener (any) ===
netstat -ano | findstr "8000"
echo.
echo === all python procs and parents ===
wmic process where (name='python.exe') get ProcessId,ParentProcessId,WorkingSetSize,CommandLine /format:list 2>nul | findstr "ProcessId Parent Working CommandLine"
echo.
echo === backend.log tail ===
powershell -Command "Get-Content C:\Users\marsh\backend.log -Tail 6 -EA SilentlyContinue"
echo.
echo === local curl to 127.0.0.1:8000 ===
curl.exe -sS -o NUL -w "HTTP %%{http_code} time %%{time_total}s\n" http://127.0.0.1:8000/api 2>nul
