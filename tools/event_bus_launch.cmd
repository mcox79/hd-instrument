@echo off
REM Launcher for the single-producer event bus (session-independent).
REM Singleton-locked inside event_bus.sh, so re-launches are harmless.
"C:\Program Files\Git\usr\bin\bash.exe" -lc "cd /d/AI/hd-instrument && exec bash tools/event_bus.sh >> data/logs/event_bus.out 2>&1"
