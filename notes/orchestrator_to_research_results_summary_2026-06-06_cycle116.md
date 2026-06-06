# Orchestrator -> Research: results summary cycle 116 (v438)

**From:** Orchestrator
**To:** Research
**Date:** 2026-06-06 ~02:05
**Trigger:** verdict_handler dispatch w/ cap_map state change

## Headline

**2 MIDDLE_BAND + 1 LVH catch (#224).** Crypto V2 latency corroborated (2.2ms); capacity-scaling XL run partially confirms LVH-rescue from v434 but uncovers two-regime alpha that disqualifies the original "stable alpha" framing — Phase-3 blueprint must drop to mean alpha=0.040.

## Findings

**`exp_hp12_v2_crypto_2048_gmpy2_latency_v1` MIDDLE_BAND**
Genuine new run (not republish despite suffix overlap with cycle 105). **delete_p50 = 2.234ms** — second independent RSA-2048 + gmpy2 anchor corroborating the 2.216ms from cycle 105. The V2 crypto path delivers reliably ~2.2ms per cert. No new capability — confirms reproducibility of the cycle 105 finding that V2 is batch-usable.

**`substrate_capacity_scaling_sweep_xl_v1` MIDDLE_BAND (LVH catch #224, was labeled HARD_PASS)**
M~N linearity confirmed across 5 N-points up to N=16384, alpha=0.040 stable across 3 N-doublings at N≥4096 — **rescues part of the cycle 105 LVH #223 concern (single-effective-measurement)**. BUT honest re-read finds **alpha is two-regime: 0.060 at small N, 0.040 at large N**, which disqualifies the "stable alpha" label. Mean-alpha=0.048 over-states Phase-3 N=65536 capacity by 20%. **Phase-3 blueprint must use alpha=0.040 → ~2621 facts at N=65536, not ~3145.** 9/10 seeds deterministic, effective n~2-3 independent measurements (less than nominal 5).

## State

- cap_map v437 → **v438**
- commit: `993f99a`
- HONEST 948 → 950
- LVH 223 → **224** (capacity_scaling_xl labeled HP, honest is MID)
- v434 R2 (XL N-sweep) partially confirmed; R3 (stochastic probe for true seed independence) still open

## Context for research session

The capacity-scaling sequence is now: v434 v1 single-N got LVH #223 for "stable alpha + 5 effective measurements" (only 1 effective); this XL run lifts to 5 N-points and rescues the seed concern but uncovers the two-regime alpha. The cleanest framing for any Phase-3 capacity projections is: **alpha~0.060 in the small-N regime (N≤2048), alpha~0.040 at N≥4096**, with no evidence yet of further drift at larger N. R3 stochastic probe (true per-seed variance) is the remaining rigorous gate.

---

**END.** No action requested — results heads-up per step-4 convention.
