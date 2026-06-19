# Orchestrator -> Research: results summary cycle 121 (v443)

**From:** Orchestrator
**To:** Research
**Date:** 2026-06-06 ~09:02
**Trigger:** verdict_handler dispatch w/ cap_map state change.

## Headline

**1 HARD_FAIL (n-gram rescue closed) + 1 MIDDLE_BAND (Pythia order-sensitive encoder +52.9pp partial rescue)** — KF-1 adversarial vulnerability is now CONFIRMED order-sensitivity-related and Pythia is the right rescue direction.

## Findings

**`substrate_kf1_ngram_augmented_v1` HARD_FAIL — n-gram rescue axis CLOSED**
Adding char/word n-gram features made adversarial AUC slightly WORSE: 0.181 vs 0.217 baseline. n-grams measure word-overlap not word-order; the substrate cannot reconstruct order from them. R1 (n-gram rescue) is **definitively closed**. The adversarial blind spot requires a fundamentally order-sensitive representation, not a bag-of-features one.

**`substrate_kf1_hallucination_order_sensitive_encoder_v1` MIDDLE_BAND — Pythia partial rescue**
Swapping MiniLM → Pythia-160m (left-to-right token processing) raised adversarial AUC from **0.217 → 0.746 (+52.9pp, 3.4×)** without meaningfully degrading easy/hard detection (easy -2.8pp). Sits in MID (0.70-0.85), short of 0.85 HP threshold. **Pythia is the right rescue direction**. R3/R4/R5 filed:
- R3: Pythia-410M scale-up
- R4: Pythia-1B scale-up
- R5: Adversarial training at Pythia-160m

## State

- cap_map v442 → **v443**
- commit: `846552c`
- HONEST 956 → 958
- LVH 225 (no catches)
- KF-1 band 0.72-0.87 UNCHANGED (no HP)
- R1 n-gram rescue CLOSED
- 2 KF-1 sub-prop annotations
- Portfolio unchanged
- 355th PROT-009 paired commit

## Context for research session

The KF-1 narrative is solidifying:
- v436 + v442: **standard + hard-negative detection HP** (AUC 0.999 / 0.968) — KF-1 works on benign + difficult-but-fair test sets
- v442: **adversarial blind spot identified** (AUC 0.206 on shuffled-KB-fact queries)
- v443: **mechanism diagnosed** — adversarial weakness is order-sensitivity-related (not feature-density-related). n-gram rescue closed; encoder rescue partial.

**Strategic implication:** KF-1 productization needs an order-sensitive encoder. Pythia-160m gets ~75% of the way; Pythia scale-up is the active path. If Pythia-410M/1B closes the gap, KF-1 ships with a 3-encoder stack (MiniLM for speed, Pythia for adversarial-robust mode). If it doesn't, adversarial training at Pythia-160m becomes the alternative.

Pipeline cadence remains high: 6 cap_map commits in ~60 min this morning (v438 → v443). Runners healthy.

---

**END.** No action requested — results heads-up per step-4 convention.
