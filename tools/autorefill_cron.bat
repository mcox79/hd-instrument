@echo off
REM Scheduled-task launcher for tools/autorefill_watcher.py.
REM Uses pythonw.exe (WINDOWS subsystem) so NO console window is allocated.
REM Combined with task Hidden=$true + S4U logon (see register_autorefill_task_
REM elevated.ps1) = zero popup, disconnect-safe (survives SSH/Claude-Code session
REM ending; parented to the Task Scheduler service, not any interactive shell).
REM
REM One pass per invocation -- Task Scheduler owns the cadence (recommended: 5min).
REM The script itself no-ops instantly unless data/autorefill_enabled.flag exists.
"C:\AI\hd-instrument\.venv\Scripts\pythonw.exe" "C:\AI\hd-instrument\tools\autorefill_watcher.py" >> "C:\AI\hd-instrument\data\logs\autorefill_watcher_cron.log" 2>&1
