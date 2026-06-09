@echo off
echo === backend.err FULL ===
powershell -Command "Get-Content C:\Users\marsh\backend.err -EA SilentlyContinue"
echo.
echo === backend.log FULL ===
powershell -Command "Get-Content C:\Users\marsh\backend.log -EA SilentlyContinue"
echo.
echo === pid 195860 alive? ===
wmic process where (ProcessId=195860) get ProcessId,WorkingSetSize 2>nul | findstr 195860
echo.
echo === all python procs ===
wmic process where (name="python.exe") get ProcessId,WorkingSetSize 2>nul | findstr Process
