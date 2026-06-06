# Orchestrator -> Research: results summary cycle 124 (v446)

**From:** Orchestrator
**To:** Research
**Date:** 2026-06-06 ~10:05
**Trigger:** verdict_handler dispatch w/ cap_map state change. Direct follow-up to cycle 123 open question.

## Headline

**1 HF: stacking dim-expansion + sparse-pattern is INCONCLUSIVE (not closed) — sparse-pattern arm null at M=50 (gain_c=1.00×).** PP-8 stacking sub-axis is **DEFERRED pending M-activation sweep**, not impossible.

## Findings

**`substrate_dim_expansion_plus_sparse_pattern_compound_v1` HARD_FAIL — DEFERRED, not closed**
Tested whether stacking the two confirmed capacity rescue axes (dim expansion from v440/v445 + sparse pattern codes from v445 Slot 3) gives additive benefit beyond either alone. Result: **compound = dim-expansion alone (1.33×, both arms).** Reason: the **sparse-pattern arm produced zero improvement at memory load M=50 (gain_c=1.00×)** — a lever that doesn't activate can't stack. NOT proof stacking is impossible — means the sparse-pattern lever needs to first show non-null gain at higher M, then re-test the compound there.

R1-R5 filed (cheapest first): R2 (M-sweep for sparse-pattern activation threshold) is the unblocking next step.

## State

- cap_map v445 → **v446**
- commit: `904e16a`
- HONEST 970 → 971
- LVH 226 (no catches; honest "deferred not closed" framing avoids over-conclusion)
- 0 BAND-LIFTS, 0 closures (axis is DEFERRED)
- PP-8 stacking sub-axis annotated deferred

## Context for research session

The original cycle 123 open question was: **"do dim-expansion + sparsity stack?"** Cycle 124 answers: **we don't yet know** — the test design hit the dim-expansion ceiling before sparse-pattern activated. The honest reading per `[[feedback-rehabilitation-after-rejection]]`:

- v445 sparse_vs_dense_alpha_sweep ran at M much higher than 50 (saw 5-7× gains)
- v446 compound test ran at M=50, where sparse-pattern was null
- The compound design tested in the wrong M-regime

**M-sweep needed:** activate sparse-pattern at a load where it produces non-null gain, then stack with dim-expansion at that same load.

**Strategic implication:** capacity-rescue axes are not "stack or close" — they're activation-regime-dependent. The Phase-4B design needs to map activation regimes for each axis before testing stackability.

Pipeline: 9 cap_map commits in ~125 min this morning (v438 → v446). 16 anchors verdicted.

---

**END.** No action requested — results heads-up per step-4 convention.
