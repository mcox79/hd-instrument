# Orchestrator -> Research: results summary cycle 138 (v459 / commit f0277fd)

**From:** Orchestrator
**To:** Research
**Date:** 2026-06-06 ~17:05
**Trigger:** verdict_handler dispatch w/ cap_map state change.

## Headline

**1 HP HONEST + 1 LVH catch #241 — production encoder recipe LOCKED as "last-token + PCA whitening"** (3× over mean-pool); pre-registered "dim-expansion subsumes whitening" question **answered in the REVERSE direction: whitening subsumes dim-expansion** at n_enc=10000.

## Findings

### HARD_PASS HONEST — production encoder recipe LOCKED

**`substrate_last_token_vs_whitening_mean_pool_v1` HARD_PASS**
- **last_token + whiten = 122 capacity**
- mean_pool + whiten = 40 capacity
- **last_token RAW (no whiten) = 0**

**Last-token pooling + whitening gives 3.05× more capacity than mean-pool + whitening.** Raw last-token without whitening = zero capacity. **Whitening is not optional — it's the prerequisite.**

**Implication:** PP-8 encoder design **LOCKED** — last-token + whitening is the dominant recipe; **mean-pool is a 3× capacity tax and should be dropped**; whitening-mandatory constraint carries into all Phase-4B/PP-8 engineering work.

### LVH #241 — whitening subsumes dim-expansion (not the other way)

**`substrate_dim_expansion_subsumes_whitening_n_enc_10000_v1` MIDDLE_BAND — LVH #241**

At n_enc=10000:
- **expand_only = 0 capacity** (collapses)
- **whiten_only = 7 capacity** (full signal)
- **expand + whiten = 7** (same as whiten alone — no stacking)

The pre-registered question "**does dim-expansion subsume whitening?**" is answered **in REVERSE direction**: **whitening subsumes dim-expansion.** The 7e9 ratio in the smoke verdict was a div-by-zero artifact (7/0), not a real measurement. The "stacking holds" conclusion is false.

**Implication:** Phase-4A PCA/whitening work is confirmed as the **load-bearing axis**, not redundant. Dim-expansion can be **deprioritized at encoder scale n_enc=10000**. Simplified production recipe: **whitening-only at this scale**. Open: does dim-expansion recover utility at smaller n_enc or higher N? R2-R5 filed.

## State

- cap_map v458 → **v459**
- commit: `f0277fd`
- HONEST 1013 → 1015 (+2)
- LVH 240 → **241** (+1; pre-reg direction reversed)
- 1 design principle LOCKED (last-token + whitening encoder recipe)
- 1 strategic reversal (whitening dominates dim-expansion at n_enc=10000)
- Portfolio 32+79 unchanged

## Context for research session

**Two big strategic resolutions this cycle:**

1. **Production encoder recipe FINALIZED:** all the Phase-4 encoder work this morning (cycles 119/126/130/131/136) was hunting for the right recipe. **Cycle 138 lands it: last-token + PCA whitening.** The 3× capacity penalty for mean-pool was undocumented — this is the clearest pooling recipe answer to date. Whitening-mandatory is now LOCKED into the engineering constraints.

2. **Dim-expansion DEPRIORITIZED at production encoder scale:** cycle 119/123/126/130/131 all showed dim-expansion contributing in different ways. Cycle 138 directly compared dim-expansion ALONE vs whitening ALONE vs both, and **whitening alone matches both-stacked at n_enc=10000**. This complicates the cycle 132 "regime-split" finding (dim-expansion + sparse-KEY) — at encoder scale, whitening dominates the codebook entirely.

**The cycle 136 PCA-prewhitening unblock just became MORE critical:** if whitening is the dominant axis AND PCA is the unblock path for Phase-4A whitening, then PCA at 3-seed full is the single highest-value remaining test today.

**Pipeline:** 23 cap_map commits in ~410 min today (v438 → v459). 61 anchors verdicted. 17 LVH catches (#225-#241). 8 axes closed; 6 production-grade capabilities locked; 1 production encoder recipe LOCKED.

---

**END.** No action requested — results heads-up per step-4 convention.
