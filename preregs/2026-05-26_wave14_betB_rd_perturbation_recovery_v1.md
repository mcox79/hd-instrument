# Pre-registration: wave14_betB_rd_perturbation_recovery_v1

**Filed:** 2026-05-26  
**Trigger:** research_reaction_diffusion_substrate_2026-05-26.md (P=0.32 deflated; Drill Q5 operationalized)  
**Queue:** remote_cpu_queue  
**ETA:** ~30-45 min CPU (N=1024, 3 seeds, Phase-A 8 epochs + Phase-B 5 epochs + 3 perturb + 8 recovery)

## Strategic context

RD-terrace theory (Giletti-Rossi, Polacik 2017-2023 propagating-terrace theory) and Saad-Solla
saddle-cascade make OPPOSITE predictions about perturbation response:
- RD-terrace: plateau states are dynamical attractors with restoring force; after controlled
  perturbation pushing retention from 0.74 -> lower, additional Phase-B WITH replay should
  recover exponentially toward 0.74.
- Saddle-cascade: plateau states are saddle points; perturbation leads to monotone drift to
  next plateau, no recovery toward 0.74 specifically.

This is a SHARP falsifier that can disambiguate the two frameworks at CPU cost only.
Parent research note confirms complementarity is possible (P=0.55); this experiment
distinguishes between frameworks directly.

## Hypothesis

HARD-PASS would confirm RD-terrace as COMPLEMENTARY framework to Saad-Solla (v208 annotation).
HARD-FAIL would confirm saddle-cascade is the sole framework and RD mapping does not apply.

## Pre-registered bands

**HARD-PASS** (RD-terrace confirmed; plateau is dynamical attractor):
- Exponential fit R^2 > 0.70 AND lambda > 0 AND |R_inf - 0.74| < 0.05

**HARD-FAIL** (RD-terrace refuted; saddle-cascade correct):
- Fit R^2 < 0.30 AND final_retention < 0.65 (monotone drift)

**MIDDLE-BAND** (inconclusive):
- R^2 in [0.30, 0.70] OR lambda <= 0 OR |R_inf - 0.74| in [0.05, 0.15]

**INSTRUMENTATION-FAIL**:
- delta_mean < 0.05 (perturbation failed to reach target class)

## Framework implications

HARD-PASS: RD-terrace framework CONFIRMED as complementary to Saad-Solla.
  - Cap_map: annotate RD-terrace as third theoretical home (P=0.32 -> P>0.45 post-pass).
  - Implication: REPLAY mechanism operates as perturbation-recovery in RD framework
    (H-A consolidation = restoring force toward G1_SAME attractor).
  
HARD-FAIL: Saddle-cascade is the sole dynamical framework. RD-terrace is a mathematical
  analog but NOT a predictive model for substrate dynamics.
  - No cap_map row-state change; annotation-only closure of RD avenue.

Per [[feedback-envelope-expansion-fail-bands]]: bands pre-registered.
Per [[feedback-dont-dismiss-adjacent-methods]]: dispatched per research note adjacency.
Per [[feedback-lit-scan-calibration-penalty]]: P=0.32 reflects calibration penalty.
