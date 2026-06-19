@echo off
echo === remove demo_mode files + clear flags ===
del /Q C:\dev\hd-instrument\backend\admin\demo_mode.py 2>nul
del /Q C:\dev\hd-instrument\backend\admin\__init__.py 2>nul
rmdir /S /Q C:\dev\hd-instrument\backend\admin\__pycache__ 2>nul
rmdir C:\dev\hd-instrument\backend\admin 2>nul
del C:\dev\hd-instrument\data\demo_mode_active.flag 2>nul
del C:\dev\hd-instrument\data\orchestrator_paused.flag 2>nul
del C:\dev\hd-instrument\data\demo_mode_watchdog_heartbeat 2>nul
del C:\dev\hd-instrument\data\demo_mode_state_log.jsonl 2>nul
echo.
echo === verify gone ===
if exist C:\dev\hd-instrument\backend\admin (echo ADMIN_DIR_STILL_EXISTS) else (echo ADMIN_DIR_GONE)
if exist C:\dev\hd-instrument\data\demo_mode_active.flag (echo DEMO_FLAG_STILL_PRESENT) else (echo DEMO_FLAG_GONE)
if exist C:\dev\hd-instrument\data\orchestrator_paused.flag (echo ORCH_FLAG_STILL_PRESENT) else (echo ORCH_FLAG_GONE)
echo.
echo done
