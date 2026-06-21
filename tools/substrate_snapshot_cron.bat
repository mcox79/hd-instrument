@echo off
REM Scheduled-task launcher for substrate_snapshot_extractor.
REM Uses pythonw.exe (WINDOWS subsystem) so NO console window is allocated.
REM Combined with task Hidden=$true + S4U logon = zero popup.
REM
REM Cadence: every 20 minutes (set in the task itself).
REM Output: d:/AI/hd-instrument/data/substrate_snapshot.json
REM Cost: ~1-3 sec per run (pure I/O; no subprocess spawns).
REM --min-degree 3 keeps the snapshot renderable in the browser:
REM full corpus is ~177k atoms (3d-force-graph chokes >10k); filtering to
REM nodes with 3+ connections drops to ~5-15k while preserving the structural
REM backbone (hubs, clusters, well-connected primitives). User can still run
REM manually with --min-degree 0 for the full graph if needed.
"D:\AI\hd-instrument\.venv\Scripts\pythonw.exe" "D:\AI\hd-instrument\tools\substrate_snapshot_extractor.py" --min-degree 3 >> "D:\AI\hd-instrument\data\logs\substrate_snapshot_cron.log" 2>&1
