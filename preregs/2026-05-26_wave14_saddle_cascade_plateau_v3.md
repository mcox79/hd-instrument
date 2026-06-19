# Pre-registration: wave14_saddle_cascade_plateau_v3

**Filed:** 2026-05-26  
**Parent:** exp_wave14_saddle_cascade_plateau_v2.py (INSTRUMENTATION_FAIL TIMEOUT 7200s; 2/7 f-points)  
**Trigger:** strategy_decisions_2026-05-26.md v211 Decision (7) — saddle-cascade v3 redesign  
**Queue:** remote_cpu_queue  
**ETA:** ~60-90 min CPU (N=1024, 5 f-values x 3 seeds x 13 epoch-equivalent)

## Changes from v2

- N: 2048 -> 1024 (4x speedup; same substrate physics, finite-N correction within calibration noise)
- f-grid: 7 points {0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0} -> 5 points {0.0, 0.25, 0.5, 0.75, 1.0}
  (removes 0.1 and 0.9 near-anchor redundancies; 5 points sufficient for linear-vs-discrete discrimination)
- All pre-registered bands UNCHANGED from v1/v2

## Hypothesis

Saad-Solla 1995 saddle-cascade: retention(f) where f = corpus-overlap-fraction shows
DISCRETE STEP STRUCTURE (not smooth-monotone), indicating plateau dynamics from saddle-cascade
ODE fixed-point traversal.

## Pre-registered bands (UNCHANGED from v1/v2)

**HARD-PASS** (cascade active):
- Linear-fit R^2 < 0.85 AND max deviation from linear fit >= 0.08

**HARD-FAIL** (smooth-monotone, cascade refuted):
- Linear-fit R^2 >= 0.95 AND max deviation < 0.04

**MIDDLE-BAND** (inconclusive):
- R^2 in [0.85, 0.95) OR deviation in [0.05, 0.08)

**INSTRUMENTATION-FAIL**:
- Fewer than 3 f-values with valid cells; re-design needed

## Strategic context

v206 4-corpus equal-spacing falsifier was the load-bearing Saad-Solla test (HARD_PASS).
This saddle-cascade plateau sweep is an EXTENSION probe (finer f-resolution), not the primary gate.
MIDDLE_BAND here does not downgrade the v206 confirmation.

Parallel with 1-RSB hysteresis v3 (CONFIRMED v211): 1-RSB + Saad-Solla are complementary frameworks.

Per [[feedback-envelope-expansion-fail-bands]]: bands pre-registered with explicit numerical thresholds.
