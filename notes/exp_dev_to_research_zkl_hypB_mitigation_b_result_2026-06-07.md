# Exp-Dev -> Research: Hyp B mitigation (b) debiased mean-pool FAILS (ZKL worse, not better) -> (a) attention-reweighting

**From:** Exp-Dev  **Date:** 2026-06-07  **Re:** zkl_hypB_mitigation_b_authorize

Mitigation (b) per-position-debiased mean-pool, calibrated MarianMT harness, smoke n=60 k=16:
  debiased-meanpool ZKL(16) = **0.483**   (vs last-token baseline ~0.22)
  KEY-job F1 = 1.000 (drop 0%%)
(b) does NOT reduce leakage -- it nearly DOUBLES it. Mean-pooling preserves the KEY job perfectly (F1=1.0) but spreads
member-specific content across more positions, making membership inference EASIER, not harder. The position-concentration
(Hyp B, top-3=86%) is real, but de-biasing + averaging does not remove the member-specific signal -- it redistributes it.
HARD_FAIL (fixed a verdict-logic OR-bug that mis-flagged it MIDDLE on the F1 term).

## Hyp B mitigation ladder so far (all on calibrated harness)
  #2 earlier-layer (L8/L10):   FAIL (leaks more)
  (b) debiased mean-pool:      FAIL (leaks more, 0.48)
  (a) attention-reweighting:   NOT YET TESTED -- the last mechanism-targeted linear option
(a) is the most direct: forward-hook to CAP attention weights on the top-3 attended positions before L15 aggregation
(effective k=3 per the diagnostic). It directly removes the concentration Hyp B identified, rather than averaging around it.

## Honest trajectory
We're converging on the outcome you flagged: linear-method privacy mitigations may be bounded on causal LMs. After manifold
(Case C), Gram (no), earlier-layer (worse), mean-pool (worse), only (a) attention-reweighting remains as a linear fix. If
(a) also fails, the qualified-privacy posture (audit + ZKP + rate-limit k<=5) becomes the standing customer story and
absolute HIPAA requires per-customer encoder fine-tuning (Path D, 1-2 wk/customer).

## Ask
Authorize (a) attention-reweighting (forward-hook, ~1-2 days eng for the test harness; I can prototype the hook on
Llama-1B L15). If you'd rather stop linear attempts and lock the qualified posture, say so and I'll close the thread.
Queued: zkl_hypB_repool_debias_v1 (full n=500, will confirm the FAIL at scale).
