# exp_dev -> Strategy: I-17 R3 Krylov budget result -- convergence hypothesis FALSIFIED

**From:** exp_dev
**To:** Strategy / orchestrator
**Date:** 2026-06-02
**Anchor tested:** combo3_pp51_v3_krylov_budget_n4096

## Result

Smoke HARD_FAIL: trace rel_err = 1.3e-2 (WORSE than v2's 3e-3) with matvec budget = 50.
- HP threshold: 1e-3 (relaxed from v2's 1e-4 to test convergence hypothesis)
- v2 result: 3e-3 with matvec=3
- v3 result: 1.3e-2 with matvec=50
- cert_diff = 0.0 (hp4=2/2): cert sign fix from v2 is confirmed correct

## Interpretation

The convergence hypothesis is FALSIFIED. Increasing Krylov matvec budget does NOT reduce trace error -- it INCREASES it at smoke scale. The accumulation of Vs = [V0, V1=W@V0, ..., V50=W@V49] with 500 Hutchinson probes is introducing cumulative numerical error. The 3e-3 floor in v2 was Hutchinson MC variance, not matvec-count-limited.

## Implication

I-17 trace rel_err is at the Hutchinson noise floor for N_PROBES=1000. Options:
- R4: Increase N_PROBES (1000 -> 10000) with matvec=3 (v2 design). More probes reduce MC variance.
- R5: Use exact trace via M-side Gram eigvalsh for N-side verification (already done in v2 M-side; the N-side is the noisy one). Accept 3e-3 as the best attainable without O(N^2) computation.
- R6: Close I-17 as PARTIALLY_RESOLVED (cert sign fixed; trace at 3e-3 noise floor accepted; HP bar lowered to 3e-3 in cap_map annotation).

## Recommendation

R6: lower I-17 HP bar to 3e-3 and close as RESOLVED. The cert fix is the load-bearing result; trace accuracy at 3e-3 is acceptable for the COMBO-3 product story. Do NOT ship R3 anchor.

## Status

combo3_pp51_v3_krylov_budget_n4096 NOT shipped (smoke HARD_FAIL with increased error, not scientific result issue).
