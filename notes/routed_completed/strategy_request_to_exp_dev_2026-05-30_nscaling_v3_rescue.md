# Strategy -> exp_dev routing -- 2026-05-30 -- n_scaling_modern_hopfield v3 rescue (F4 v2 still broken)

## Status

NOT-AUTO-DISPATCHED. Filed for orchestrator main-thread review and user next-batch decision.

## Background

`n_scaling_modern_hopfield_rescue_v2_n16384` was shipped in F-batch at commit ad30514 with intent to fix v1 instrumentation failure (no completed seeds at N=16384) via reduced M-sweep + OOM-graceful instrumentation. v2 STILL FAILS: 21s wall, no completed seeds, per_M empty in all 3 seeds. The v1->v2 fix did NOT reach the actual failure mode.

Per [[feedback-rehabilitation-after-rejection]] this is NOT a substrate-capability closure -- the test does not run. The substrate-at-N=16384 capability claim remains untested.

## Strategic context

Modern-Hopfield N=16384 scaling test is on the substrate-physics framework cap_map ledger. Its OPERATIONAL value is moderate (we have N=4096 and N=8192 evidence elsewhere), but the instrumentation failure suggests a substrate-construction or memory issue at N=16384 that could affect FUTURE N=16384 tests of OTHER mechanisms (BID v6, TCFT broad-envelope at N=16384, etc.).

Cheaply isolating the failure mode is more valuable than re-running the same failing test.

## Task

v3 design: SHRINK the test to isolate the failure.

1. **Phase 1 -- isolated substrate construction probe** (cheapest, ~15min CPU):
   - Run `substrate.build(N=16384)` in isolation (no seed loop, no M sweep).
   - Measure memory before/after construction.
   - Log explicit exit code / exception.
   - Determine: does construction itself OOM/crash?

2. **Phase 2 -- single-M N=16384 test** (cheap, ~30min CPU):
   - If Phase 1 succeeds: run ONE M=4096 cell at N=16384 with explicit memory tracking at each step.
   - 1 seed only.
   - Identifies whether failure is at seed-loop entry, retrieval, or scoring.

3. **Phase 3 -- iterate to FULL** (only if Phase 1+2 succeed):
   - Add M sweep back at single-seed.
   - Then 3-seed at reduced M-sweep.

## Why

[[feedback-rehabilitation-after-rejection]]: instrumentation-only failure is not capability closure; cheap isolation tests cost <30min CPU and salvage the question.

## Contract

- Pre-reg per [[feedback-envelope-expansion-fail-bands]]: phase-1 HP threshold = "substrate constructs without OOM"; phase-2 HP threshold = "at least 1 cell returns valid metrics".
- Self-tests on any helper formulas per [[feedback-strategy-spec-formula-selftests]].
- Per-experiment `--timeout` per [[feedback-per-experiment-timeout-required]] (small budgets: Phase 1 <300s, Phase 2 <600s).
- ASCII-only print/verdict_msg per [[feedback-ascii-only-in-scripts]].
- Background dispatch only per [[feedback-no-blocking-runs]].

## Autonomy

Exp_dev decides:
- Phase 1 / 2 / 3 scope per cycle (recommended: ship Phase 1 + 2 together in one anchor; defer Phase 3 to follow-up if phases pass).
- Queue choice (CPU laptop for Phase 1/2 cheap; GPU for Phase 3 FULL).
- Whether memory tracking instrumentation lives in script or via external profile.

## NOT auto-shipping

Per user explicit no-refill directive on F-batch context. Orchestrator surfaces to user.

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
