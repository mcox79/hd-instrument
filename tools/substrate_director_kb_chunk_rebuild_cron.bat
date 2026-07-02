@echo off
REM Scheduled-task launcher for chunk KB rebuild.
REM Uses pythonw.exe (WINDOWS subsystem) so NO console window is allocated.
REM Combined with task Hidden=$true + S4U logon = zero popup (per
REM feedback_all_scheduled_tasks_and_subprocesses_must_be_windowless_USER_2026-06-28).
REM
REM Recommended cadence: nightly (e.g. 03:00) — full rebuild ~7.5 min per
REM 2026-06-27 manifest (n_chunks=136873; elapsed_s=451.3). Cheap enough for
REM nightly, too expensive for 6h. Adjust if substrate growth pushes >15 min.
REM
REM Output: overwrites data/substrate_director_kb_chunk_v1/ (canonical path).
REM Log:    data/logs/substrate_director_kb_chunk_rebuild_cron.log
REM
REM To enable (one-time, elevated):
REM   schtasks /Create /TN "hd-instrument\substrate_chunk_kb_rebuild" ^
REM     /TR "D:\AI\hd-instrument\tools\substrate_director_kb_chunk_rebuild_cron.bat" ^
REM     /SC DAILY /ST 03:00 /RL HIGHEST /F
REM Then apply the S4U + Hidden fix so it stays popup-free:
REM   powershell -File D:\AI\hd-instrument\tools\hide_all_tasks_elevated.ps1
"D:\AI\hd-instrument\.venv\Scripts\pythonw.exe" "D:\AI\hd-instrument\tools\build_substrate_director_kb_chunk_v1.py" >> "D:\AI\hd-instrument\data\logs\substrate_director_kb_chunk_rebuild_cron.log" 2>&1
