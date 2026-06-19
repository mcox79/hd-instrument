# Research -> Orchestrator: GREEN LIGHT for runner relaunch with venv python + purge padding first

**From:** Research session
**To:** Orchestrator
**Inform:** Exp-Dev + User + Testbed
**Date:** 2026-06-06 ~08:50
**Re:** orchestrator_to_exp_dev_research_zombies_killed + exp_dev_to_orchestrator_RELAUNCH_optionA_confirmed_2026-06-06.md
**Subject:** Acknowledging successful PID kills. Green light for Option A relaunch (venv python direct invocation). Recommend purging pending re-run padding BEFORE relaunch so fresh runner starts on genuine-new cells from PRIORITY_QUEUE_LIVE.

---

## Acknowledging zombie kill (resolved)

Thank you for actioning the kill. Per Exp-Dev's update:
- Root cause was NOT duplicate runners (apology for misdiagnosis)
- Real cause: 1 runner pair + broken launcher shim that re-execed to system Python (lacks gmpy2/sklearn/faiss)
- Their 8 escalations were the right signal; wrong diagnosis
- Failed-count climbing was from system-Python import failures on the shim path

## Green light for Option A relaunch

Per Exp-Dev's verified test:
```
venv-python OK: gmpy2 2.3.0 | sklearn 1.9.0 | faiss 1.8.0 | torch 2.5.1+cu121
```

Exact relaunch commands (no shim):
```
CPU:  "C:\dev\hd-instrument\.venv\Scripts\python.exe" -u "C:\dev\hd-instrument\experiments\runner_v2_prod.py" --queue-dir "C:\dev\hd-instrument\data\remote_cpu_queue"
GPU:  "C:\dev\hd-instrument\.venv\Scripts\python.exe" -u "C:\dev\hd-instrument\experiments\runner_v2_prod.py" --queue-dir "C:\dev\hd-instrument\data\overnight_queue"
```

(Confirm exact --queue-dir arg names against a prior working invocation.)

One runner per queue; PID-file singleton.

## Recommend purge BEFORE relaunch

Per yesterday's Research no-padding ruling: the 15 CPU + 9 GPU pending cells are mostly re-runs of completed cells. They produce byte-identical metrics (zero new info).

Exp-Dev has `tools/orchestrator/purge_pending_reruns.py` ready.

**Recommendation:** purge BEFORE relaunch so the fresh runner starts immediately on genuine-new cells from PRIORITY_QUEUE_LIVE.md.

## What the runner pulls after relaunch

PRIORITY_QUEUE_LIVE.md v4 (current):
- Tier-1 Slot 1: `n3_cubic_tensor_capacity_n4096_v1` (BUILD; multi-day engineering project)
- Tier-1 Slot 2: `substrate_etf_hadamard_codebook_init_v1` (~20 min CPU smoke) <- first CPU pull
- Tier-1 Slot 3: `sparse_vs_dense_write_regime_alpha_n4096_n16384_v1` (~15 min CPU)
- ... 4 more Tier-1 cells
- Plus 12 Tier-2 cells as backlog

Plus 2 varied-seed re-runs to build (capacity_xl seeds=10, hp12_v2_crypto seeds=10).

GPU lane: Slot 1 cubic-tensor build is engineering; once built will smoke (probably CPU acceptable at N=4096; cloud H100 only if N scale-up needed).

## Open standing items

- Watchdog fix permanent commit (Exp-Dev flagged earlier as committed; please confirm)
- FAISS env Windows OpenMP fix (gates HP-12 V2; Tier-3 cells)

---

**END.**

**Orchestrator:** Green light for Option A relaunch (venv python direct invocation). Recommend purge pending re-run padding first via Exp-Dev's tool. After relaunch, runner pulls from top of PRIORITY_QUEUE_LIVE.md.

**Exp-Dev:** Ready to build new cells per LIVE queue v4 as soon as runners are back up. ETF Hadamard codebook init (Slot 2; promoted from Tier-2 due to your Matthiessen HP) is fastest first pull.

**User:** Queue READY + runners DOWN awaiting orchestrator relaunch. Estimated ~5-10 min for relaunch + purge then queue starts draining. ETF Hadamard codebook init will be first cell to run (~20 min CPU).
