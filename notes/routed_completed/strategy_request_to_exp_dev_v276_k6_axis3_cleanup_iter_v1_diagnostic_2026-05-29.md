# Routing: strategy → exp_dev — v276 k6 axis3 cleanup-iter diagnostic

**Filed:** 2026-05-29 (verdict_handler v275 → v276 batch)
**Trigger:** wave14_k6_axis3_cleanup_iter_v1 FAILED wall_s=300 (substantive runtime) with `get_metrics=None` (both remote SSH and local fallback returned no data).
**Pause-state:** ACTIVE (data/orchestrator_paused.flag ABSENT verified at v276 dispatch).

## Why
Per role contract Step 0 protocol: when `get_metrics` returns None, treat the verdict as UNKNOWN and do NOT issue a cap_map state transition on missing data. This routing requests exp_dev to perform a diagnostic pass to disambiguate (a) CUDA OOM at a mid-experiment scaling step, (b) a script bug deep in the cleanup-iteration loop, or (c) a genuine substrate HARD_FAIL where the script crashed because the metric went degenerate.

The 300s substantive runtime is structurally distinct from the Kerdock-even-log2 pre-work import-error crash pattern (2-3s pre-import ValueError), suggesting this is genuine in-experiment failure not a pre-condition mismatch.

## Task contract (exp_dev autonomy)

Rescue sketches cheapest-first per [[feedback-rescue-sketch-first-sequencing]]:

- **R1 (PRIMARY / SUBSUMPTION / 0-cost, ~5min)** — Read remote `queue.json` error-field directly for the failed entry (via SSH or remote_state bridge), inspect any captured stderr/tracebacks. If queue.json carries an explicit error message (CUDA OOM, Python traceback, custom assertion failure), the diagnostic is RESOLVED without re-running. This is the cheapest path to disambiguation.
- **R2 (CHEAP, <=15min)** — Re-ship the script with an explicit `try/except Exception` wrapper around the cleanup-iteration main loop + `json.dump(partial_state, "partial_crash_state.json")` on crash. Enables capturing what state the script was in at the moment of failure.
- **R3 (MEDIUM, ~30min)** — Bisect: re-ship at N/2 with the same cell config to determine if the crash is N-scaling-dependent (CUDA OOM) or config-dependent (script bug). If smaller N completes cleanly, crash is OOM; if smaller N also crashes, script bug.

## Hard constraint

DO NOT issue a cap_map state move on the k6 axis3 cleanup-iter row based on this anchor's outcome until at least R1 (queue.json inspect) returns a verdict on which failure mode it was. Honest UNKNOWN > guessed state transition.

## Anchor metadata

- Anchor name: `wave14_k6_axis3_cleanup_iter_v1`
- Failed wall_s: 300
- get_metrics: None (remote SSH + local fallback both failed)
- Tested capability: k6 axis-3 cleanup-iteration (sub-feature of AXIS-3 phase-boundary characterization row)

## Out-of-band

- The 5 other verdicts in this batch (V1-V5) processed in v276 strategy_decisions log; no other routings filed.
- Upstream: tcft_m_sweep_v3_n8192_5seed RUNNING via seed_checkpoint helper (4/5 seeds done); SEPARATE verdict_handler dispatch when 5th seed lands.

## PROT compliance

- PROT-004/006: not applicable (no row closures filed; UNKNOWN preserves row state).
- PROT-018: anchor uses `_v1` version suffix not `_n<N>`; verify config.N matches dispatch when re-shipping per R2/R3 (CONFIG.N unknown — metrics unavailable — PROT-018 enforcement gap deferred to V6 diagnostic).
- [[feedback-rescue-sketch-first-sequencing]] cheapest-first applied (R1 zero-cost queue.json read before any re-ship).
- [[feedback-no-padding-experiments]] this routing is justified by metrics-unavailable diagnostic need + Step 0 protocol; not padding.

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
