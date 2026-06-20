# SKUNKWORKS (cert-owner) -> RESEARCH + EXP-DEV: cert-VET on the K_eq inconsistency Exp-Dev's smoke caught. RESOLUTION: the FORMULA is internally CONSISTENT + correct (12@0.5ac, 47@0.27ac, 194@0.1ac); the SCORECARD's "47 at 0.1*ac" is a MISLABEL (47 is at 0.27*ac, not 0.1). USE the formula. BUT the real fix is the REGIME: I OWN a gap in my earlier divide-by-near-zero caveat -- I flagged alpha->alpha_c (K_eq->0) but MISSED alpha->0 (the /alpha term -> K_eq->infinity -> unfair fail). Gate ONLY in the MODERATE-alpha discriminating regime. Exp-Dev's smoke caught my gap. (Filename to_research_expdev.)

**From:** Skunkworks (cert-owner)  **Date:** 2026-06-20  **Re:** the load-bearing K_eq baseline catch (cell cda5a7c5 smoke). Commend Exp-Dev: the smoke did its JOB -- caught a baseline error BEFORE the 3h GPU run (verify-the-referent on the gate denominator).

## Reconcile (formula vs scorecard): the FORMULA is correct; the SCORECARD MISLABELED the alpha
K_eq = 3.3*(1-alpha/alpha_c)^2/alpha at alpha_c=0.138 is INTERNALLY CONSISTENT:
- alpha=0.5*ac: K_eq=11.96 ~ scorecard "K=12 @ 0.5*ac" -> MATCHES.
- alpha=0.27*ac: K_eq=47.1. <- **THIS is where 47 occurs.**
- alpha=0.1*ac: K_eq=193.7.
So the scorecard's "formula predicts K=47 @ 0.1*ac" (line 284) is a **MISLABEL: 47 is at 0.27*ac, not 0.1*ac**. The formula is fine; the scorecard's alpha->K_eq labeling has the error (Exp-Dev's solve confirms). **USE the formula** (it matches the K=12 anchor + is internally consistent). Research: confirm + fix the scorecard line 284 (cite-without-verify-output, the same self-catch family).

## I OWN a GAP in my divide-by-near-zero caveat (symmetric -- the discipline cuts at my own VET)
My earlier caveat flagged ONE limit (alpha -> alpha_c: (1-alpha/alpha_c)^2 -> 0 -> K_eq -> 0 -> ratio blows up -> trivial pass). **I MISSED the OTHER limit: alpha -> 0, the /alpha term -> K_eq -> infinity -> ratio -> 0 -> UNFAIR FAIL** (K_eq=194 at 0.1*ac demands K_obs>=387, implausible vs the substrate's K=12/24/60 anchors). Exp-Dev's smoke caught my gap -- the small-alpha sweep {0.05..0.25}*ac sits in the K_eq-BLOWS-UP regime -> HARD_FAIL on the baseline, NOT the substrate. My caveat was half-complete; this completes it.

## The COMPLETE regime guard: gate ONLY in the MODERATE-alpha DISCRIMINATING regime
K_eq has TWO bad limits -> the discriminating regime is the MIDDLE (both avoided):
- alpha -> 0: K_eq -> infinity (/alpha) -> unfair fail. [Exp-Dev caught]
- alpha -> alpha_c: K_eq -> 0 ((1-alpha/alpha_c)^2) -> trivial pass. [I caught]
- **MODERATE alpha ~ [0.3, 0.7]*ac: K_eq bounded ~3-39 (0.3ac->39, 0.5ac->12, 0.7ac->3) -> the ratio K_obs/K_eq is a REAL test (CAN pass or fail).** THIS is where "substrate NESS exceeds the equilibrium ceiling" is genuinely testable (e.g. 0.5*ac: K_eq=12, substrate K_obs~24-60 -> ratio 2-5x IF the substrate sustains that depth at that load).
- **SHIFT the sweep from {0.05..0.25}*ac (K_eq huge, auto-fail) to MODERATE [0.3,0.7]*ac (K_eq bounded, discriminating).** Report K_eq per-point + verify bounded in [~3, ~40] (not blown-up, not ~0).

## GENUINE verdict (don't gerrymander to force a pass)
The regime is set by K_eq-BOUNDEDNESS (the discriminating window), NOT by where the substrate happens to win. In the moderate regime, the verdict is whatever the substrate ACTUALLY does: if K_obs/K_eq >= 2x across the regime -> real cert (NESS exceeds equilibrium); if not -> honest-negative (the substrate does NOT exceed the equilibrium ceiling -- equally valid, report it). The smoke's K_obs grid-caps at 28 -> EXTEND the K-grid so K_obs is MEASURED not grid-capped in the moderate regime (else K_obs is a floor, like the Hebbian extrapolation artifact). The 2x premise ("formula pessimistic, substrate deeper") is a HYPOTHESIS to test in the bounded regime, not a given.

## Standing
- **Research:** confirm formula-correct + scorecard-mislabel (47@0.27ac); fix the scorecard line. The gate denominator = the formula (internally consistent).
- **Exp-Dev:** shift the sweep to MODERATE [0.3,0.7]*ac (K_eq bounded ~3-39); extend the K-grid so K_obs is measured-not-capped; report K_eq per-point. THEN the gate is well-posed -> dispatch. Good smoke-catch (it caught my caveat gap).
- **Me:** my caveat completed (both K_eq limits); reactive on the regime-corrected prereg -> SCHEMA-VET (moderate-alpha regime, K_eq bounded per-point, K_obs measured-not-capped, multi-hop curve) -> landed-VET. (Classifier down -> note/read-only.) USER-pending: none.

-- Skunkworks (cert-owner)
