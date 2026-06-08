@echo off
echo === backend.log (last 30 lines) ===
powershell -Command "Get-Content C:\Users\marsh\backend.log -Tail 30 -EA SilentlyContinue"
echo.
echo === backend.err (last 30 lines) ===
powershell -Command "Get-Content C:\Users\marsh\backend.err -Tail 30 -EA SilentlyContinue"
echo.
echo === backend status: ===
netstat -ano | findstr :8000
echo.
echo === GPU ===
nvidia-smi --query-gpu=memory.used,memory.free,utilization.gpu --format=csv
