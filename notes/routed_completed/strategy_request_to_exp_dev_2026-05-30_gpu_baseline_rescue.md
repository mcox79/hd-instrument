# Routing note: gpu_acceleration_baseline_v1_n8192 NO_METRICS_ON_DISK rescue

**From:** verdict_handler v283 batch processing (2026-05-30)
**To:** exp_dev (NOT auto-dispatched; orchestrator main-thread review)
**Anchor:** `gpu_acceleration_baseline_v1_n8192`

## Verdict context

- Verdict: NO_METRICS_ON_DISK
- Elapsed: 20s
- `get_metrics()` returns None: remote SSH cannot find metrics.json
- Fast crash; runner-failed before metrics write

## Failure mode

20s elapsed with no metrics.json on remote suggests fast crash during initialization or first compute step. Could be (a) missing dependency import, (b) CUDA context initialization failure, (c) script syntax error, (d) config schema mismatch.

## Rescue sequence (cheapest-first)

1. **CHEAPEST (~5min):** Read the script `experiments/exp_gpu_acceleration_baseline_v1.py` (or equivalent) locally; check for syntax errors / missing imports.

2. **CHEAP (~10min):** Run smoke mode locally to verify the script can start; capture stderr.

3. **CHEAP (~15min):** SSH to remote, attempt to re-run with stderr redirect to a log file; isolate root cause.

## Suggested exp_dev contract

- Smoke-test the script locally first; do NOT re-ship to GPU queue until smoke passes
- Document the crash root cause (import? CUDA init? config?) BEFORE re-shipping
- Add explicit metrics.json write at script start (placeholder) so partial-fail mode is distinguishable from NO_METRICS

## DO NOT auto-dispatch

User pending refill decision. Hold this routing note for orchestrator main-thread review.

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
