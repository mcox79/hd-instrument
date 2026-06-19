@echo off
REM Launcher for heartbeat_watchdog, called by Windows Task Scheduler.
REM
REM Same pattern as gpu_runner_0_launcher.bat / cpu_runner_0_launcher.bat /
REM cpu_runner_local_launcher.bat / hd_remote_state_emitter task -- supervisor
REM wrapper for a persistent infra process.
REM
REM This process SCPs marsh@home:C:/dev/hd-instrument/data/remote_state_cache.json
REM to local data/remote_state_cache.json every ~30s (per its config).
REM Without it, get_metrics across all sessions returns stale data (DECISION 204
REM 13-day silent staleness; 86th audit-discipline instance type).
REM
REM Singleton: heartbeat_watchdog has no explicit PID-file guard; the
REM scheduled task's IgnoreNew MultipleInstances setting prevents dup-spawn.
"D:\AI\hd-instrument\.venv\Scripts\python.exe" -X utf8 "D:\AI\hd-instrument\tools\orchestrator\heartbeat_watchdog.py" >> "D:\AI\hd-instrument\data\logs\heartbeat_watchdog.log" 2>&1
