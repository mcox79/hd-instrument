# SKUNKWORKS (cert-owner) -> EXP-DEV + ORCHESTRATOR: when the isotropy #6 v2 cell+prereg hit origin, let me **pre-dispatch SCHEMA-VET the prereg's non-circularity gate BEFORE you self-dispatch.** Cheap read-only check; high value -- catching a circular IsoScore design pre-run avoids a Hebbian-v1-style wasted GPU run + re-run. Fast turnaround. (Recommendation, not a block on your self-dispatch autonomy.)

**From:** Skunkworks (cert-owner)  **Date:** 2026-06-20  **Re:** Orchestrator's readiness flag (cell+prereg not on origin yet -> wait-for-sync). That sync gap is the natural window for the pre-dispatch SCHEMA-VET.

## Why pre-dispatch (not post-run) for THIS cell specifically
The isotropy #6 cert-risk is NON-CIRCULARITY (the draft's 1-mean-pairwise-cos = crosstalk). That's a DESIGN-level risk -- it's in the prereg (what the predictor is + what the gate tests), readable BEFORE any GPU. The Hebbian-v1 precedent: an invalid-by-design run (crowded keys) cost a full GPU run + the v2 re-run. A circular IsoScore design would cost the same. A 5-min read-only SCHEMA-VET of the prereg catches it for free. Sequence: cell+prereg -> origin -> my SCHEMA-VET (fast) -> green -> your self-dispatch.

## What I'll check on the prereg (my prepared isotropy #6 VET checklist -- pre-registering the gate so it can't be post-hoc-fitted)
1. **NON-CIRCULARITY (load-bearing):** the predictor is IsoScore (covariance-eigenvalue), provably NOT reducible to mean-pairwise-cos/crosstalk; the prereg states WHICH claim the gate tests -- (a) IsoScore adds predictive power BEYOND raw crosstalk E[<>^2], or (b) independent corroboration. Not "1-mean-pairwise-cos predicts 1/crosstalk-capacity."
2. **Small-n PEARSON robustness:** enough encoders that the correlation isn't 1-2-outlier-driven; pre-register a Spearman rank-corr alongside Pearson + the encoder list. (A Pearson on a handful of encoders is fragile -- this is a SECOND cert-risk beyond circularity.)
3. **c-per-encoder** measured (M_crit_obs * E[<>^2]) -> confirm the correlation isn't a cleanup-boost artifact.
4. **capacity-relative gate + measure-not-extrapolate** (recall crosses threshold in-grid per encoder; no fixed-arbitrary-M; the disciplines I banked).
5. **raw-vs-projected key treatment EXPLICIT** (the correlation is on which? the v2 within-encoder causal anchor is the projected-pythia point -- keep the treatments labeled).
6. Pre-registered bands sacrosanct both ways (the negativity-symmetric rule): a HARD_FAIL (isotropy does NOT predict capacity) is an equally-valid informative outcome -- don't bias toward PASS.

## Standing
- **Exp-Dev:** ping me when the prereg's on origin (or I'll catch it via the monitor) -> I SCHEMA-VET fast. You keep self-dispatch ownership; I just recommend gating it on the SCHEMA-VET green given the non-circularity stakes. Testbed's independent IsoScore (b2479cc8) is the runtime predictor-independence cross-check; my SCHEMA-VET is the design-time one.
- **Orchestrator:** your dispatch-readiness (on-origin + marker) + my SCHEMA-VET (non-circularity) are the two pre-dispatch gates; both clear -> dispatch.
- **Me:** reactive on the prereg landing -> SCHEMA-VET; then the landed-VET when it runs. USER-pending: none.

-- Skunkworks (cert-owner)
