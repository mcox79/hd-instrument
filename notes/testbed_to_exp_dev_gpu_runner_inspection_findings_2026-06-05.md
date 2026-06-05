# Testbed -> Exp-Dev: GPU runner inspection findings (Action 3)

**From:** Testbed  **To:** Exp-Dev (primary)  **Inform:** User + Orchestrator + Research  **Date:** 2026-06-05
**Re:** `research_to_testbed_3_authorizations_pertoken_kgqa_gpu_2026-06-05.md` (Action 3) + your 03:45 capacity-comp silent-failure report

## Headline findings (3 actionable)

### 1. Runner repo is 646 COMMITS BEHIND origin/main (CRITICAL)

```
cd C:\dev\hd-instrument
git rev-list --count HEAD..origin/main  -> 646 (after fetch)
git log --oneline -1                    -> 6927efc "Add BE-1 precision sweep..."
```

The runner's checkout has not been pulled since ~05-30. **My Pythia per-token augmentation (commit `34137e9`), datasets delivery note + script, Llama v8 patches, cornerstone hyperprobe fixes — none are on the runner yet.** The Pythia per-token queue command in `testbed_to_exp_dev_pythia160m_per_token_ready_to_queue_2026-06-05.md` requires `git pull` first.

Recommendation: run `git -C C:\dev\hd-instrument pull origin main --ff-only` at the next runner-side window. Resolve any conflicts that may emerge from local-only changes. Re-verify per-doc Pythia partial paths post-pull (the script's ckpt_prefix now includes a `perdoc/pertoken` tag — if existing partials don't match the new prefix the runner will re-extract from scratch; alternative is to manually rename them).

### 2. 6 stale Python procs present; 3 are likely zombies

```
PID 165388:  1,060,100 KB  CPU 0:02:04   <- ACTIVE: likely current GPU job
PID 186888:     73,072 KB  CPU 0:06:34   <- long-running; heartbeat? watcher?
PID 222804:     18,412 KB  CPU 0:03:00   <- helper
PID 112456:        880 KB  CPU 0:00:00   <- ZOMBIE
PID 151052:        912 KB  CPU 0:00:00   <- ZOMBIE
PID 108140:      4,032 KB  CPU 0:00:00   <- ZOMBIE
```

The 3 zombies (low memory + 0 CPU time) are likely leftover from killed-but-not-cleaned procs. These match the "stale processes from killed runs" the diagnostic prompt mentions.

Recommendation: kill the 3 zombies. The active + 2 long-running procs look legitimate (heartbeat, schtask launcher) but worth cross-checking against your runner state.

```powershell
Stop-Process -Id 112456,151052,108140 -Force -ErrorAction SilentlyContinue
```

### 3. Capacity-comp dirs from 06-02/06-03 exist with COMPLETE metrics; no newer dirs

```
exp_capacity_phase_boundary_fine_grid_v2_n4096   <- 06-02 23:21; metrics.json 2,278 bytes; 5 partial_metrics
exp_capacity_phase_boundary_larger_n_v2_n8192    <- 06-03 01:17; metrics.json 25,026 bytes; 5 partial_metrics
exp_capacity_cliff_graceful_v1/full_v2/full_v3   <- all 06-02/06-03
exp_capacity_phase_boundary_under_rram_noise_v1_n4096
```

**No capacity-comp anchor dirs from 06-04 or 06-05.** This means the recent failed runs (your 03:45 note: "capacity-comp N=4096/N=8192 GPU failed 3x with no logs/metrics") **crashed BEFORE creating their output dir + writing any partial**.

Failure modes that match this signature:
1. **Import-time crash** (e.g., CUDA OOM at first allocation; module not found)
2. **TOKENIZERS_PARALLELISM fork deadlock** (same as Llama v6/v7 hangs; even though capacity-comp doesn't use HF tokenizers, a subprocess that DOES could deadlock the parent)
3. **Schtask launcher script crashes before invoking the python script** (wrong python path, environment activation failure)
4. **Silent process kill** (OOM-killer style) before any I/O syscalls land on disk

## GPU healthy

```
NVIDIA GeForce RTX 4060 Ti, Driver 591.86, CUDA 13.1, WDDM
Memory: 1981 MiB / 8188 MiB used (76% FREE: 6.2 GB available)
GPU-Util: 28%
Power: 19W / 160W (low; not under heavy load)
Temp: 35C
```

Plenty of headroom; OOM at allocation is UNLIKELY but possible if a capacity-comp run requests >6 GB single-allocation.

## Disk healthy

```
C: 1,273 GB free of 1,863 GB total (68% free)
```

Not a disk-space problem.

## Recommended diagnostic recipe for next capacity-comp attempt

Per [[feedback-always-verbose-remote-dispatch]] (already in memory):

```powershell
# Wrap the actual capacity-comp dispatch in verbose tracing:
$Env:TOKENIZERS_PARALLELISM = "false"
$Env:PYTHONUNBUFFERED = "1"
$ANCHOR = "capacity_comp_n4096_v_diagnostic"
$LOG = "C:\dev\hd-instrument\data\debug_$($ANCHOR)_$(Get-Date -Format yyyyMMddHHmmss).log"
& python -u "C:\dev\hd-instrument\experiments\exp_capacity_phase_boundary_fine_grid_v2_n4096.py" `
  2>&1 | Tee-Object -FilePath $LOG -Append
```

Key points:
- `python -u` -> unbuffered stdout/stderr
- `Tee-Object -FilePath` -> capture log even on hard crash before any in-script logging
- `TOKENIZERS_PARALLELISM=false` -> defensive against fork deadlock (carry over Llama v6/v7 lesson)
- `PYTHONUNBUFFERED=1` -> flush all I/O immediately

If THIS still produces no output, the crash is happening BEFORE Python even starts (schtask layer, env activation, etc.).

## Combined recommendation

**Highest priority**: `git pull` the runner to get my Pythia per-token + datasets + audit fixes onto the runner. Without this, my Action 1 + Action 2 work is invisible to the runner's queue dispatcher.

**Second priority**: clean the 3 zombie Python procs (low risk).

**Third priority** (when GPU is next free): run a single capacity-comp anchor under the verbose tee diagnostic recipe above; if it still fails silently, the next investigation target is the schtask layer (we already learned this lesson with `feedback_runner_schtask_path_drift`).

## What I did NOT do

- Did NOT git-pull on the runner (your lane; you control runner state).
- Did NOT taskkill any procs (your lane; you know which are intentional).
- Did NOT re-queue capacity-comp (no GPU dispatch authority without your queue control + diagnostic recipe agreement).

## Action 3 wrap

Diagnostic + recipe documented. Ball is in your court for the actual runner-side actions. If you want me to run any further remote inspection commands (e.g., dump the schtask config, check Windows Event Viewer for python.exe crashes, inspect heartbeat_watchdog state), ping me with specifics.

---

**END.**

**Exp-Dev:** 3 actionable findings; the 646-commits-behind runner state is highest-priority for unblocking Pythia per-token + datasets work. Capacity-comp silent failures look like pre-write crash (no anchor dir); verbose tee diagnostic recipe above will localize.

**User:** all 3 user-authorized Actions complete (Action 1 per-token Pythia, Action 2 KG/QA datasets, Action 3 GPU inspection). Findings logged. Awaiting Exp-Dev next-cadence to apply runner-side fixes.

**Research:** Action 3 findings documented; the runner-stale issue may explain why earlier Pythia per-doc queue dispatches were slow to roll out — the runner was already several commits behind at queue-add time.
