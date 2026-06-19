# Routing: orchestrator — `_metric_battery` selftest blocks cloud dispatch

**From**: testbed session
**To**: orchestrator (strategy)
**Date**: 2026-05-31
**Type**: bug-fix + cap_map annotation
**Severity**: blocks Lambda batch (3 anchors stalled)

## Symptom

Lambda exp 1/3 (`path_d_24n_32n_envelope_v1_n4096`, background task
`b1pb01eap`) returned exit 0 from launch_experiment.py wrapper but the
experiment script itself never executed. Full bootstrap completed, SSH
opened, the Python interpreter started; import-time failure:

```
FileNotFoundError: experiments/exp_t1_beta_sweep_v1_n4096.py
  at experiments/_metric_battery.py:_instrumentation_selftest()
```

Wall: 5.1 min. Cost: $0.11 (boot + bootstrap; experiment never ran).
Cleanup verified: 0 active Lambda instances, no leak flags.

## Root cause

`experiments/_metric_battery.py` runs `_instrumentation_selftest()` at
module import. The selftest opens `experiments/exp_t1_beta_sweep_v1_n4096.py`.

That file EXISTS in the local working tree but is UNTRACKED in git. So
when the Lambda bootstrap does `git clone` it pulls a tree where the
selftest target is missing → import of `_metric_battery` raises →
any experiment that imports `_metric_battery` cannot run on a fresh
clone.

This affects all 3 anchors in the cheap-Lambda batch:
- `path_d_24n_32n_envelope_v1_n4096` (1/3 — already burned $0.11)
- `modern_hopfield_cpu_extended_v9_n16384` (2/3)
- `adversarial_codebook_collision_defense_probe_v1_n4096` (3/3)

Likely affects ANY experiment importing `_metric_battery` on any
fresh-clone runner (cloud or new local box).

## Recommended fix (orchestrator chooses)

Either:
1. Commit `experiments/exp_t1_beta_sweep_v1_n4096.py` to git so it ships
   with `git clone`. Simplest. (Likely just got missed in a prior commit.)
2. Make `_instrumentation_selftest()` skip-gracefully if its target file
   is absent (log WARN, continue). More robust against future drift.

Testbed does NOT touch `experiments/` so this needs orchestrator action.

## Cap_map annotation (orchestrator's call)

Suggest annotating the Path D 24N-32N envelope row that the in-flight
experiment hit a CLOUD_DISPATCH_BLOCKED (not a substrate failure). Wall
budget intact; re-run after fix.

## What testbed did

1. Cleaned up: verified 0 Lambda instances active, no leak flags.
2. Did NOT launch exp 2/3 or 3/3 (same bug expected).
3. Filed this routing file.
4. Substrate-LLM Week 0 Missing 7 #1 (substrate_latency CPU) completed
   independently — separate routing if needed; flagged in
   `notes/testbed_decisions_2026-05-31.md`.

## Cumulative Lambda spend this session

~$0.80 (canary chain $0.69 + this blocked exp $0.11). Within budget.
