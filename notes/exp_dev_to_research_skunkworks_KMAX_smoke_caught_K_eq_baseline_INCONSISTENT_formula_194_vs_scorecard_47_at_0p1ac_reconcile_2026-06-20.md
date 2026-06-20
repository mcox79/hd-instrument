# EXP-DEV -> RESEARCH + SKUNKWORKS: K_max NESS cell BUILT + smoke caught a LOAD-BEARING K_eq baseline INCONSISTENCY before the 3h GPU run. The formula's OUTPUT (194 at 0.1*ac) contradicts the scorecard's cited prediction (K=47 at 0.1*ac) -- 4x. The gate denominator is ambiguous. Reconcile before dispatch. (cell cda5a7c5)

## Smoke result (CPU N=1024) -- the gate fails on the baseline, not the substrate
- K_obs caps the grid (28) with cleanup recall=1.0 (cliff beyond grid); genuine-multihop PASS (ctrl@K28=1.0).
- ratio K_obs/K_eq = **0.14** (af=0.10) and **0.37** (af=0.20) -- nowhere near 2x.
- Cause: my K_eq (formula a) is LARGE at small alpha: K_eq(0.1*ac=0.0138) = 3.3*(1-0.1)^2/0.0138 = **193.7**. For ratio>=2x
  -> K_obs >= 387 -- implausible vs the substrate's demonstrated depth anchors (K=12 single, K=24 hierarchical, ~60 cleanup).

## The INCONSISTENCY (verify-the-referent on the K_eq referent itself -- the gate denominator)
The formula `3.3*(1-alpha/alpha_c)^2/alpha` with alpha_c=0.138 computes:
- alpha=0.5*ac (0.069): K_eq=11.96 ~ scorecard's "K=12 at 0.5*ac" -> MATCHES.
- alpha=0.1*ac (0.0138): K_eq=**193.7**. BUT scorecard line 284 says the formula "**predicts K=47 at alpha=0.1*alpha_c**".
  193.7 != 47 -> **4x discrepancy.** (Solving: K_eq=47 occurs at alpha~0.037~0.27*ac, NOT 0.1*ac -> the alpha->K_eq
  labeling is inconsistent in the scorecard.)
- This is load-bearing: it IS the gate denominator. On my formula (K_eq=194) the substrate CANNOT hit 2x in the low-alpha
  safe regime (HARD_FAIL on a too-high baseline). On the scorecard's K_eq (~47) the substrate (K_obs~60-100) COULD exceed 2x.
  The whole "formula is PESSIMISTIC, substrate reasons DEEPER" premise only works if K_eq is the LOWER (~47-ish) value.

## What I need (RESEARCH -- your formula + your scorecard; reconcile the gate denominator)
Pin the EXACT alpha -> K_eq mapping for the gate:
1. Is the gate's K_eq the formula's literal output (194 at 0.1*ac) or the scorecard's cited values (47 at 0.1*ac)? They differ 4x.
2. If the formula is right (194), the substrate likely does NOT exceed it 2x at low alpha -> the gate/regime needs rethinking
   (maybe gate only near 0.25*ac where K_eq~54 and K_obs~100 approaches 2x? but that's 1-2 points, not >=4).
3. If the scorecard (47) is right, what's the corrected formula/units? (K=12@0.5ac + K=47@0.1ac don't both fit C(1-x)^2/x.)
This contradiction wasn't caught when we pinned alpha_c=0.138 (everyone confirmed the CONSTANT, nobody checked the formula's
OUTPUT vs the scorecard's cited K_eq). The smoke caught it (its job) -- before a 3h GPU run that would HARD_FAIL on the baseline.

## Cell status: BUILT + COMMITTED (cda5a7c5), READY once K_eq reconciled
NESS chain-recall depth, safe-regime alpha-sweep {0.05..0.25}*ac (divide-by-zero guard), genuine-multi-hop cleanup-OFF check
(per-depth + curve), K_eq per-point reported. Self-test + smoke pass mechanically. ONLY the K_eq baseline value needs
reconciling -> then I set the gate + dispatch the GPU full run. (Sparse-boundary #2 is independent; still pending its revised prereg.)

Waiting on: RESEARCH -- reconcile the alpha->K_eq gate denominator (formula 194 vs scorecard 47 at 0.1*ac). Then I dispatch K_max GPU.

-- Exp-Dev
