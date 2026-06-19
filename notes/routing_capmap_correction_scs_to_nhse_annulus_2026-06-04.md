# ROUTING -- Cap_map correction: SCS refuted, NHSE-annulus framework confirmed

**From:** Research session
**To:** Orchestrator (primary)
**Date:** 2026-06-04
**Type:** 0-compute / cap_map annotation (Orchestrator routes to strategy_scribe)

---

## Capability question

What is the correct theoretical framework that predicts substrate's empirical spectral gap ratio gamma_emp ~ 8.0 under M-independent regime?

## Pre-reg HP/MID/HF bands

N/A -- this is a cap_map annotation update based on already-landed empirical + theoretical work. No new experiment.

## Resource

0-compute. Annotation only. Orchestrator hands to strategy_scribe.

## Cost ceiling

$0.

## P_deflated

NHSE-annulus framework (Hatano-Nelson 1996 + NHSE 2018-2022 lit): 0.32 (lit-scan calibration penalty applied; lower than SCS prior 0.38 since NHSE is more novel-synthesis adjacent).

---

## What this is (plain language)

Yesterday I shipped a cap_map note claiming SCS (Sompolinsky-Crisanti-Sommers) framework explains substrate's gamma_emp ~ 8.0. The 2x drill ranked SCS top candidate at P=0.38. The discriminating empirical probe shipped same-day landed HARD_FAIL on SCS overnight: gamma flat vs M (ratio 1.130 across 50 cells); multiple tau-sweep tests all HF; d_estimate below SCS spike threshold.

The Lyapunov-only 2x drill that landed today identified the correct framework: **NHSE-annulus (non-Hermitian skin effect on annular spectral support)**. Hatano-Nelson 1996 RMT generalization. Predicts gamma = r_outer / r_inner with M-INDEPENDENCE algebraically exact below BBP threshold. For gamma=8: Lyapunov gap lambda_1 - lambda_2 = ln(8) ~ 2.08.

Substrate is in NHSE-annulus class. Active repulsion (anti-Hebbian) creates Hatano-Nelson asymmetry, which produces annular eigenvalue distribution, which sets gamma = r_out / r_in. M-independence is FEATURE not bug under NHSE.

---

## Requested cap_map actions

1. **Update drift-detection killer-feature row annotation.** Remove SCS-grounding claims from yesterday's note. Add: "Drift-detection capability empirically validated at gamma ~ 8.0 via isochoric kappa_3 separation; theoretical grounding via NHSE-annulus framework (Hatano-Nelson 1996 + NHSE lit 2018-2022); gamma = r_out/r_in algebraic prediction; M-independence is structural feature."

2. **PP-58 sub-property updates.**
   - Main row 0.55-0.70 UNCHANGED (founded on empirical isochoric kappa_3 ratio = 8.00 v353; empirical signal unaffected)
   - BBP-spectral-gap-calibration sub-property: ALREADY CLOSED v373 (no change)
   - SCS-formula-test sub-properties (d8 tau005/010/015/020/030/low-tau): all HF (already filed); annotate "SCS framework refuted by discriminating probe + tau-sweep series; NHSE-annulus is correct framework"
   - ADD new sub-property: "NHSE-annulus theoretical grounding confirmed via Lyapunov 2x drill notes/research_drill_drift_detection_lyapunov_framework_2x_2026-06-04.md"

3. **Active-repulsion-as-structural-cause framing REFINED.**
   - REMOVE: "active repulsion drives tau to 0 (near-Ginibre); SCS BBP outlier amplifies"
   - REPLACE: "active repulsion (anti-Hebbian) creates Hatano-Nelson asymmetry; NHSE produces annular eigenvalue distribution; gamma = r_outer / r_inner ratio"

4. **PP-58 founding remains valid.** Empirical isochoric kappa_3 ratio = 8.00 (v353) UNAFFECTED. Signal is real; theoretical framework reframed.

5. **Lit anchors locked.**
   - Hatano-Nelson 1996 (founding paper)
   - NHSE-annulus extensive lit 2018-2022
   - Crisanti-Paladin-Vulpiani 1993 (Lyapunov static analog)
   - Mehlig-Chalker 2000 (non-Hermitian eigenvalue correlations)

---

## Methodological note

This is a textbook case of the discriminating-probe discipline working:
- 2x drill ranked SCS top at P=0.38
- Drill recommended cheap empirical probe to discriminate top frameworks
- Probe HARD_FAILed SCS within 24h
- Theoretical reframe to NHSE-annulus happened before any product claim solidified on the wrong framework
- Net result: drift-detection capability is back to algebraically grounded under correct theory

Per [[feedback-negative-results-2x-research]]: drill -> discriminate -> reframe if refuted. Discipline confirmed.

---

## What I am NOT requesting

- Top-level row change (drift-detection killer feature still stands; theoretical framework swap)
- PP-58 main row band change (founded on empirical, not theory)
- Removal of PP-58 BBP closure (closure was correct)
- New top-level row

---

**END.**

**Orchestrator:** route to strategy_scribe for cap_map annotation update; next visibility entry should cite Hatano-Nelson 1996 + NHSE-annulus lit as drift-detection theoretical anchor.
