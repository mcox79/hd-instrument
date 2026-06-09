@echo off
echo === kill old chain (PID 70412) ===
taskkill /F /PID 70412 2>nul
echo.
echo === clear logs ===
del C:\Users\marsh\extraction_chain.log 2>nul
del C:\Users\marsh\extraction_chain.err 2>nul
echo.
echo === launch chain watcher with all 4 extracts ===
wmic process call create "C:\Users\marsh\tmp_run_extraction_chain.bat" | findstr "ProcessId"
echo.
ping 127.0.0.1 -n 5 >nul
echo === chain log tail ===
type C:\Users\marsh\extraction_chain.log 2>nul
echo.
echo === ingest count ===
powershell -Command "(Get-Content C:\dev\hd-instrument\data\substrate_state\wikipedia_100k\facts.jsonl -EA SilentlyContinue | Measure-Object -Line).Lines"
