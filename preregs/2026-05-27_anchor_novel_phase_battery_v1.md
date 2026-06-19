# Pre-registration: anchor_novel_phase_battery_v1

**Date:** 2026-05-27
**Script:** experiments/exp_anchor_novel_phase_battery_v1.py
**Queue:** overnight_queue (GPU)
**ETA:** ~3-4h (N=4096 C1/C2 N-sweep is bottleneck)

## Hypothesis

Substrate is most likely in the "gated multistable AM / lR-phase" documented class (P=0.48) rather than genuinely novel (P=0.22) or a finite-N artifact (P=0.30). This 6-cell battery is the decisive class-identification test.

Source: notes/research_novel_phase_class_methodology_2026-05-27.md Finding 7.
Handoff: notes/exp_dev_handoff_novel_phase_class_battery_2026-05-27.md

## Design

- N sweep: {512, 1024, 2048, 4096} for cells C1 (q_EA) + C2 (plateau heights)
- Default N: 2048 for cells C3 (spectral gap), C4 (hysteresis area), C5 (disorder op), C6 (free energy wells)
- 5 seeds per cell
- 3-class BSC fixture (G1/G2/G3 clean/medium/low overlap)

## Pre-registered outcomes

### C1: q_EA(N) scaling
- DOCUMENTED: q_EA monotone, converges to q_EA* in [0.6, 0.9]
- NOVEL: q_EA non-monotone OR slope > 0.05/decade
- FINITE-N: q_EA < 0.1 at N=4096

### C2: Plateau height N-scaling
- DOCUMENTED: max drift < 0.02 across N sweep; inter-plateau gap > 0.05 at all N
- NOVEL: drift > 0.02
- FINITE-N: inter-plateau gap < 0.05 at N=4096 (plateaus collapse)

### C3: Goldstone mode absence (spectral gap)
- DOCUMENTED/NOVEL: spectral_gap_frac > 0.05 (no soft mode)
- FINITE-N: spectral_gap_frac < 0.05 (soft mode appears)

### C4: Hysteresis area stability
- DOCUMENTED: CV < 0.10 across seeds (first-order intrinsic)
- NOVEL: CV > 0.10 or anomalous pattern
- MIDDLE: area < 1e-4 (too small to interpret)

### C5: Non-local disorder operator
- DOCUMENTED: disorder_op_value in [0.05, 0.40]
- FINITE-N: < 0.02 (trivial)
- NOVEL: outside [0.05, 0.40]

### C6: Free-energy 3-well structure
- DOCUMENTED: >= 3 wells, gap_ratio in [0.30, 0.65]
- NOVEL: 3 wells with gap_ratio outside [0.30, 0.65]
- FINITE-N: < 2 wells

## Joint decision rules
- DOCUMENTED-BUT-UNTESTED: >= 5/6 cells match documented column
- NOVEL (declare SKAH-M): >= 4/6 novel AND >= 1 anomaly in C1/C2/C3
- FINITE-N-ARTIFACT: >= 4/6 finite-N
- MIDDLE-BAND: mixed

## Calibrated priors (no empirical anchor for most cells; bands set per calibration-probe policy)
- P(DOCUMENTED) = 0.48 [modal]
- P(NOVEL) = 0.22 [deflated per lit-scan penalty]
- P(FINITE-N) = 0.30
