# Stateful-core FULL: direct GPU launch recipe (fire AFTER the re-smoke verdict)

Cell: `experiments/exp_stateful_core_situation_model_v1.py`. FULL config: `--full --seed 7
--n-random-init-seeds 5 --device cuda`. This cell is argparse-flag-gated (`SystemExit` with no
flag), so it CANNOT go through the standard queue runner (the runner spawns the script with no CLI
flag). FULL is therefore a DIRECT detached invocation on the GPU host, mirroring the smoke's
detached launch. The device arg is now honored (was hardcoded cpu); `--device cuda` fails loud with
`SystemExit` if cuda is unavailable, so a GPU dispatch can never silently run on cpu.

Host `marsh@home`, remote repo `C:\dev\hd-instrument`, venv `.venv\Scripts\python.exe`.

## PRECONDITION (Orchestrator, one-time before firing)
1. Push the device-plumbing commit to origin/main (exp_dev cannot push).
2. Sync remote to it: `bash tools/remote_sync.sh` -> confirm `[remote_sync] already at origin/main`
   (or reset-to) shows the fix commit hash.
3. Confirm CUDA is visible in the AUTONOMOUS venv on the host (PROT-020 item 7):
   `ssh marsh@home "C:\dev\hd-instrument\.venv\Scripts\python.exe -c \"import torch;print(torch.cuda.is_available())\""`
   -> must print `True`.

## FIRE (verbatim, detached; survives ssh disconnect via Win32_Process)
The launch body is committed as `tools/_launch_full_stateful_core.bat` (lands on remote via the
sync above), so the fire is one WMI Create:

```
ssh marsh@home "powershell -NoProfile -Command \"Invoke-WmiMethod -Class Win32_Process -Name Create -ArgumentList 'cmd /c C:\dev\hd-instrument\tools\_launch_full_stateful_core.bat'\""
```

The `.bat` runs the FULL invocation with stdout/stderr redirected and writes a done-sentinel:
- stdout: `data\_full_stateful_core.out`
- stderr: `data\_full_stateful_core.err`
- done sentinel (written on process exit, contains exit code): `data\_full_stateful_core.done`

## OUTPUT / metrics
- FULL metrics (no suffix): `data\exp_stateful_core_situation_model_v1\metrics.json`
  (verdict `FULL_COMPLETE`; carries `results`, `arm_b_minus_a`, `random_init_core_worst`,
  `device` == `cuda:0`).
- start marker: `data\exp_stateful_core_situation_model_v1\_start_marker.json`
- heartbeat: `data\exp_stateful_core_situation_model_v1\_heartbeat.jsonl`

## VERIFY-ALIVE (not the heartbeat alone -- see CLAUDE.md liveness rule)
Progressing IFF: `_start_marker.json` present + `_heartbeat.jsonl` growing + `nvidia-smi` shows the
`.venv` python at high util (this cell exercises cuda: encoder fwd/bwd + WM recurrence, ~25M-param
unfrozen fine-tune) + on completion `metrics.json.device == "cuda:0"`. If nvidia-smi util is ~0%
with python absent from compute-apps, the run is on cpu -> abort (should be impossible now: the
`SystemExit` guard fails loud, but verify).

## NOTES on the config
- OOM-class-free: the only encoder forward is `model.pooled(t)` -> `[B, d]`; NO `mlm_logits` /
  `[B, L, vocab]` tensor is ever materialized. The objective is the PE/surprise term +
  cross-entropy on the tiny `[B, 2]` judge head. Safe on the 8GB-class GPU.
- autocast/AMP: NOT added. The forward is dominated by HRR bind/unbind + `F.normalize` + cosine
  (`surprise = 1 - cos`) over an ~11-step recurrence; fp16 autocast on normalize/cosine risks
  NaN/instability for little gain on a ~25M-param model, and fp32 cuda already dwarfs cpu wall.
  Correctness-on-cuda was prioritized per task scope; AMP can be a later perf pass if FULL wall
  proves long.
- expected units: 2 arms x (1 trained + 5 random-init-core) per construction (MES, KD).
