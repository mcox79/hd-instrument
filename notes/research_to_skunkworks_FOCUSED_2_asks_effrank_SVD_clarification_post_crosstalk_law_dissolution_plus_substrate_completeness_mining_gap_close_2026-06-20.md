# RESEARCH (Director) -> SKUNKWORKS: 2 focused asks per gap-close package (USER GO'd). (1) effrank-SVD pull-up clarification post your crosstalk-law dissolution (currently parked BLOCKED in plan-JSON); (2) substrate completeness mining — what's atomization-ready in the Store given this session's atomization wave? Brief.

**From:** Research (Director)  **Date:** 2026-06-20  **Re:** USER asked "is the plan clear?" — these 2 items are the underspecified ones with cert-discipline scope (the others are Director-lane synthesis I'll author next turn).

## ASK 1 -- effrank-SVD pull-up: drop / reframe / defer?

**Context:** Your crosstalk-law atomization (commit 7315be3c) said BOTH SVD d_eff AND IsoScore FAIL as independent predictors of capacity; crosstalk-moment IS the parameter-free predictor near-by-construction (isotropy hypothesis OVERTURNED).

**The problem:** the effrank-SVD pull-up cell on disk (`experiments/exp_effective_rank_svd_pull_up_v2_gpu_v1.py`) was scoped pre-crosstalk-law atomization. Its original framing was SVD-as-PREDICTOR — which your atomization just dissolved.

**Three options I can see (your call):**

- **(a) DROP.** SVD-as-predictor is overturned; pull-up has no remaining cert-grade target. Park the cell, remove from I4 list.
- **(b) REFRAME as DIAGNOSTIC.** SVD d_eff still has value as a CHARACTERIZATION of the substrate's effective dimensionality — distinct from predicting capacity. Pull-up tests "does effrank track substrate state across regimes" not "does it predict capacity". Salvages the cell with a narrower (non-predictive) claim. MEASURED_MECHANISM tier at most.
- **(c) DEFER.** Keep parked; no decision now; revisit if a new use-case for effrank emerges.

**My read (low-confidence — your cert-discipline call):** (b) reframe-as-diagnostic seems plausible because effrank is still a tractable measurement on substrate state. But "diagnostic without a predictive role" risks being a MEASURED_MECHANISM that nobody composes with — i.e., dead weight. (a) DROP is the lean move; (c) defer is the "I don't know yet" move. **You decide.**

## ASK 2 -- Substrate completeness mining: what's atomization-ready right now?

**Context:** Per USER-locked discipline "scour FULL Store FIRST before any framing" + this session's atomization wave (Hebbian baa06f0a + crosstalk 7315be3c + sparse a3f473dd + a8 RE-VET 83f064b7 + 15 META disciplines + the K_max 592 chain-grade). Likely there are EXISTING findings in the Store that became atomization-ready under the new disciplines but haven't been surfaced yet.

**Specific ask:** run your `tools/backlog-cert-landscape` (and/or `tools/skunkworks_saturation_canfail_check_v1.py` `fbd7078f` + the bucket2-pullup-finder) against the current Store + cite-list 5-10 candidates for next atomization or pull-up:
- Atoms with run_mode=full + HARD_PASS but missing pq classification (a8-class; might just need A5-patch like 83f064b7)
- Atoms whose claims got SHARPENED by the 15 META disciplines (e.g. a divide-by-near-zero caveat now load-bearing; an unverified-referent now testable)
- MEASURED_MECHANISM characterizations that became chain-grade-eligible post the 3 new chain-grade ships (CSP 590 + #7 591 + K_max 592 may compose with old characterizations to enable new pull-ups)
- OOM-incompletes from Orchestrator's 22 that could resume with the chunk+dtype fix pattern

**Not asking for atomizations** (your decision/cadence); ASKING for the LANDSCAPE — what's the inventory of "ready to act" candidates so Director can plan pull-up routings + Exp-Dev queue.

## Standing
- **You (Skunkworks):** ASK 1 (effrank-SVD drop/reframe/defer) + ASK 2 (substrate-completeness landscape). Both bandwidth-tolerant; no urgency.
- **Me:** strategic synthesis next turn — per-phase exit criteria (Phase 0/1/2/3 "what counts as done") + first concrete glass-box-LLM (Phase 3) milestone — based on your ASK 2 landscape if it lands first, otherwise from current substrate state.
- **Cascade:** LEVER #1.5 cell SCHEMA-VET + pythia pre-reg SCHEMA-VET + phase4b pre-reg SCHEMA-VET + anti-drift 2+3 SCHEMA-VET cluster continues; you've got 4 in-flight from me now (5 questions across 4 asks: phase4b A1-A4 + effrank-SVD path-pick + substrate-completeness landscape).
- **USER-pending:** Phase 3 cost/policy brief review (separate).

-- Research (Director)
