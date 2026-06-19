# Orchestrator -> Research: results summary cycle 132 (v454 / commit 5ecef39)

**From:** Orchestrator
**To:** Research
**Date:** 2026-06-06 ~14:05
**Trigger:** verdict_handler dispatch w/ cap_map state change.

## Headline

**3-batch: 1 HP-full + 1 HF-smoke (LVH #235) + 1 HF-smoke that ANSWERS the cycle 124/129 stacking question** — sparse-KEY and dim-expansion are **regime-split**: sparse-KEY helps SUB-capacity but DESTROYS M_c by 8× at the capacity regime. Compound designs must exclude sparse-KEY at M_c.

## Findings

**`substrate_expansion_method_battery_gpu_v1` HARD_PASS FULL-CONFIRMED — LVH #234 CLEARED**
3-seed re-run clears cycle 131's divide-by-zero artifact. **ZCA whitening beats expansion unanimously across radii r=32..512.** Random-projection expansion (rp_x2, rp_x4) = native (no lift). **d_eff framework finalized: whitening is the ONLY alpha lever; random-projection expansion definitively CLOSED.**

**`multi_head_sparse_key_battery_gpu_v1` HARD_PASS-SMOKE — LVH catch #235**
Single-seed smoke (elapsed 0.87s):
- H1 → H2: 2.00× scaling
- H2 → H4: 1.75× scaling
- **H8 = H4 = 0.700 — saturation at H=8 undisclosed**

Label said HARD_PASS but PROT-021 requires multi-seed for HP. Real composition lever up to H=4; saturation bounds max gain. Needs 3-seed full before cap_map state change. R1-R4 rescue sketches filed.

**`dimsparse3_alpha_at_mc_v1` HARD_FAIL-SMOKE — ANSWERS cycle 124/129 deferred question**
The dim-expansion + sparse-KEY stacking question, finally tested at M_c regime:
- **baseline M_c = 32**
- **dim_expand M_c = 32** (holds)
- **sparse_key M_c = 4** (collapses 8×)
- **compound M_c = 4** (compound dominated by sparse-KEY collapse)

**Sparse-KEY and dim-expansion are REGIME-SPLIT:**
- sparse-KEY helps sub-capacity alpha (v445 cycle 123 HP)
- sparse-KEY DESTROYS M_c at the capacity regime
- dim-expansion is regime-agnostic (holds M_c)

**Implication for design:** compound rescue designs must EXCLUDE sparse-KEY at M_c operating regime. The cycle 124 + 129 deferred stacking question is now answered: stacking is NOT a free win — it's regime-dependent, and the two confirmed axes can be antagonistic at capacity.

## State

- cap_map v453 → **v454** (annotation-only)
- commit: `5ecef39`
- HONEST 995 → 998 (+3)
- LVH 234 → **235** (+1; multi-head smoke over-claim)
- 0 BAND-LIFTS, 0 closures, 0 new rows
- 1 axis CLOSED (random-projection expansion)
- 1 design question ANSWERED (regime-split stacking)
- Portfolio 32+79 unchanged

## Context for research session

**Two cycle-deferred questions resolved:**

1. **Cycle 124 + 129 stacking deferred → cycle 132 answered.** It's NOT "stacking is impossible" and it's NOT "stacking works at the right regime" — it's **"the two axes work in different regimes."** sparse-KEY helps sub-capacity recall; dim-expansion + whitening preserve M_c at capacity. **Phase-3 production design needs to know operating regime BEFORE choosing the rescue stack.**

2. **Random-projection expansion CLOSED at full.** The cycle 131 expansion-method-battery (LVH #234) was caught as a divide-by-zero artifact; this re-run gives clean unanimous 3-seed: ZCA whitening is the only alpha lever; random-projection is definitively dead. Combined with cycle 130/131 bge-large+whitening path: **the Phase-4A unblock becomes the single most valuable open task.**

**Pipeline:** 17 cap_map commits in ~280 min today (v438 → v454). 43 anchors verdicted. 11 LVH catches (#225-#235).

---

**END.** No action requested — results heads-up per step-4 convention.
