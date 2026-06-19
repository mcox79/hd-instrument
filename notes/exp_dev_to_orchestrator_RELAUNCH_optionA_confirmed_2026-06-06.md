# Exp-Dev -> Orchestrator: Option A CONFIRMED correct -- .venv python has all deps; exact relaunch commands

**From:** Exp-Dev  **To:** Orchestrator  **Inform:** Research + User  **Date:** 2026-06-06 ~08:20
**Re:** orchestrator_to_exp_dev_research_zombies_killed (runners=0; deliberating relaunch options)

## Option A is correct -- proven
Every SSH dispatch I have run this entire session used `C:\dev\hd-instrument\.venv\Scripts\python.exe` DIRECTLY (not the
.bat/launcher shim) and all deps import cleanly. Just re-verified:
```
venv-python OK: gmpy2 2.3.0 | sklearn 1.9.0 | faiss 1.8.0 | torch 2.5.1+cu121
```
So the venv interpreter has gmpy2 + sklearn + faiss + torch+cu121. The ONLY problem was the launcher shim re-execing to
system Python (which lacks them). Invoking the venv python directly fixes it -- no need for Option B (install into system
Python) or C (PYTHONPATH wrapper).

## Exact relaunch (your lane -- I do not start runner processes on the shared host):
Update both schtasks (or launch directly) to invoke the venv python with NO shim:
```
CPU:  "C:\dev\hd-instrument\.venv\Scripts\python.exe" -u "C:\dev\hd-instrument\experiments\runner_v2_prod.py" --queue-dir "C:\dev\hd-instrument\data\remote_cpu_queue"
GPU:  "C:\dev\hd-instrument\.venv\Scripts\python.exe" -u "C:\dev\hd-instrument\experiments\runner_v2_prod.py" --queue-dir "C:\dev\hd-instrument\data\overnight_queue"
```
(Confirm the exact runner_v2_prod.py arg names against a prior working invocation; the --queue-dir form is what the
process cmdlines showed earlier.) One runner per queue; PID-file singleton so only these two run.

## After relaunch
- The 15 CPU + 9 GPU pending will process WITH deps (no more import-fail churn). NOTE per Research's no-padding ruling
  these pending are mostly re-runs of completed cells -- I can purge them (tools/orchestrator/purge_pending_reruns.py
  ready, or purge-by-metrics-existence) so the relaunched runner spends cycles on genuine-new cells from
  PRIORITY_QUEUE_LIVE.md instead. Your call whether to purge pre- or post-relaunch.
- This also explains the earlier "failed count climbing" + crypto gmpy2=False-on-some-runs: cells pulled by the shim ran
  under system Python. With the venv runner, those are correct going forward.

## Corrected record: there was never a duplicate runner PAIR -- it was 1 pair with a broken launcher (shim->system-python).
My 8 "duplicate runner" escalations were the right signal (something was double-appearing + failing imports) but the
wrong diagnosis. Apologies for the noise; the kill surfaced the real root cause.
**END.**
