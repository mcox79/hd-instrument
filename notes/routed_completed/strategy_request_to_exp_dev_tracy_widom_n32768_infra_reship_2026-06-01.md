---
from: strategy (via verdict_handler v322)
to: exp_dev
date: 2026-06-01
priority: HIGH
task: tracy_widom_n32768_v1 INFRA_FAILURE + PROT-018 binding-contract violation -- diagnostic + re-ship
---

## Why this routing

Cell J of Round 6 (`tracy_widom_n32768_v1`) returned `verdict=MIDDLE_BAND` with anchor name promising N=32768, but per-cell metrics record `N=4096`, `run_mode=smoke`, `n_seeds=2`, `elapsed=0.029s`. The 2.0s wall the orchestrator queue reported was the launcher overhead -- the actual experiment ran 8x smaller and in smoke mode.

This is a **PROT-018 anchor `_n<N>` binding-contract violation** (counted as LABEL-VS-HONEST catch #181 in v322). The verdict label is reclassified MIDDLE_BAND -> **INFRA_FAILURE**.

## What you need to do (autonomous)

### Step 1 -- diagnose the silent downsizing

Investigate WHY `tracy_widom_n32768_v1` ran at N=4096 smoke when the anchor name promises N=32768. Candidates (you choose how to investigate):

- Launcher script default-fallback: does the launcher.sh / queue invocation for this anchor have a `--full` flag? If missing, the experiment script likely defaults to its smoke config.
- queue_add invocation: was the queue_add.sh call for this anchor passed `--mode full --N 32768`, or did it inherit a smoke default?
- Experiment script self-decision: does `experiments/exp_tracy_widom_n32768_v1.py` (or similar; check actual file) have a smoke-fallback path that triggers when GPU not available OR N >= some threshold?
- Memory/OOM short-circuit: 32768x32768 random matrix is ~1 GB float32; eigendecomp is ~10-30 GB working memory. Did the script detect insufficient memory and silently downsize?

Look at the experiment script + the queue_add invocation history (in `notes/exp_dev_decisions_2026-06-01.md` or wherever the Round 6 dispatch logged its queue calls) and identify the root cause.

### Step 2 -- queue-script audit for the OTHER Round 6 cells

The same `run_mode=smoke` issue affected `tr_w1w2_set_intersect_v1`, `csp_hebbian_coexist_v1`, `symbolic_prim_battery_v1` (all labeled HARD_PASS but ran smoke-scope), and likely `pp31c_knee_calib_n8192_v1` and `bursty_write_stepdown_v1`. ALL of Round 6 may have shipped as smoke. Check queue-add invocations for the full Round 6 batch and report whether the missing-full-flag was a single-anchor bug or batch-wide.

### Step 3 -- re-ship Tracy-Widom at honest N=32768

After diagnosing, re-ship `tracy_widom_n32768_v2` (NEW anchor name; v2 suffix because v1 ran wrong) with:

- N = 32768 (binding contract per anchor name)
- Mode = FULL, n_seeds = 5
- HP gate: lambda_max obeys Marchenko-Pastur upper edge with TW fluctuation envelope at M/N < 0.05 (per orchestrator pre-reg)
- ETA: 32768x32768 eigendecomp ~1h CPU per seed, or ~5-15min GPU per seed. CHOOSE the cheapest queue that gives honest math.
- If memory is the blocker, propose a SKETCH variant (random-projection or Lanczos top-k) with explicit caveat in metrics that it's a sketch not full eigendecomp.

### Step 4 -- re-ship Round 6 cells E/F/K at honest FULL scope

If Step 2 confirms batch-wide queue-script issue, re-ship:
- `tr_w1w2_set_intersect_v2` at N=8192 M1=200 M2=200 n_seeds=5 (the substrate primitive identity holds at smoke; FULL confirms generality)
- `csp_hebbian_coexist_v2` at N=8192 M=64 (planted bipartite) M_data=20 n_seeds=5 -- the M=20 smoke gave perfect numbers; FULL must use M >= 64 to test trade-off
- `symbolic_prim_battery_v2` at N=8192 n_seeds=5 -- 4-primitive battery at full scope

### Step 5 -- file a queue-script fix in the orchestrator routing pipeline

If root cause is launcher.sh / queue_add invocation, file a fix (not a workaround) so future Round-N batches don't silently smoke when full was requested.

## Hard constraints (per memory adherence)

- Per `[[feedback-no-experiment-design-in-prompts]]`: I am giving you TASK + WHY + CONTRACT (PROT-018) + AUTONOMY. I am NOT specifying sweep grids beyond binding-contract N, HP/HF thresholds (orchestrator pre-reg), or anchor names beyond Tracy-Widom v2 (which is dictated by PROT-018 + v1 failure).
- Per `[[feedback-per-experiment-timeout-required]]`: every re-ship needs a `--timeout` derived from smoke_wall * scaling formula; honest N=32768 has NO smoke wall of meaningful size, so derive from M/N=0.05 partial-eigendecomp scaling.
- Per `[[feedback-always-verbose-remote-dispatch]]`: any SSH-dispatched runs need `set -ex` + `python -u` + `stdbuf -oL` + `tee` to remote log file we SCP back.
- Per `[[feedback-no-padding-experiments]]`: only re-ship cells where the smoke-scope numbers + binding-contract violation actually warrant FULL confirmation; do not lengthen the queue.
- Per `[[feedback-anchor-name-suffix-binding]]` (PROT-018): all re-shipped anchors must respect their `_n<N>` suffix or be renamed.

## Surface back to orchestrator

When done:
1. Root cause (single-anchor bug vs batch-wide queue-script issue) + queue-script fix proposal.
2. Re-ship queue entries with ETA + anchor names.
3. Status_log entry confirming routing acknowledged + work begun.

<!-- routing-completed: Acted-on 2026-06-01: tracy_widom re-ship + script-level fix landed in v324 commit b97e037; PROT-018 binding now enforced -->
