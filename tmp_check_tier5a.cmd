@echo off
echo === backend log tail ===
powershell -Command "Get-Content C:\Users\marsh\backend.log -Tail 30 -EA SilentlyContinue"
echo.
echo === backend.err tail ===
powershell -Command "Get-Content C:\Users\marsh\backend.err -Tail 30 -EA SilentlyContinue"
echo.
echo === port 8000 ===
netstat -ano | findstr :8000
echo.
echo === GPU ===
nvidia-smi --query-gpu=memory.used,memory.free,utilization.gpu --format=csv
echo.
echo === Get fresh tunnel URL ===
type C:\Users\marsh\public_url.txt
