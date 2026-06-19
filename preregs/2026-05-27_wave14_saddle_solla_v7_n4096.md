# Pre-registration: wave14_saddle_solla_v7_n4096

Date: 2026-05-27
Experiment: exp_wave14_saddle_solla_v7_n4096.py
Queue: overnight_queue (GPU)
Timeout: 5400s

## Hypothesis
Saddle-cascade discrete plateau structure (non-linear retention vs corpus-overlap fraction f)
persists at N=4096 with 5 independent seeds. All 4 prior small-N tests agree (HARD-PASS
at N<=1024). v7 is the first genuine production-scale confirmation.

## Design
- N = 4096 HARD-CODED as bare `N = 4096` (PROT-018 binding contract; exit-6 on mismatch)
- Seeds: [7, 17, 23, 31, 41] (5 seeds)
- f_sweep: [0.0, 0.25, 0.5, 0.75, 1.0] (5-point)
- Phase A: 8 epochs, Phase B: 5 epochs
- Corpus: 200KB bytes
- GPU device (mandatory)
- Smoke: N=512, 1 seed, 3 f-points, 1 epoch (gate only)

## N-suffix binding (PROT-018)
Anchor name contains _n4096. Script production config: `N = 4096` at line 92.
Verified by PROT-018 check: pattern `\bN\s*=\s*4096\b` matches.

## Pre-registered thresholds

### Per-seed
- HARD-PASS: Linear-fit R^2 < 0.85 AND max deviation from linear fit >= 0.08
- HARD-FAIL: R^2 >= 0.95 AND max deviation < 0.04
- MIDDLE-BAND: otherwise

### Overall (5 seeds)
- OVERALL-PASS: >= 4/5 seeds HARD-PASS
- OVERALL-FAIL: >= 4/5 seeds HARD-FAIL
- OVERALL-MIXED: else

Thresholds IDENTICAL to v3/v4/v5/v6. No band widening.
Calibration: prior empirical anchor exists (v3 R^2=0.322, max_dev=0.249; v3 HARD-PASS).

## Timeout estimate
smoke_wall_s=3.3 (observed), FULL_N/smoke_N = 4096/512 = 8,
FULL_seeds/smoke_seeds = 5/1 = 5, scaling_exp = 1.5
timeout_s = ceil(1.5 * 3.3 * 8^1.5 * 5) = ceil(1.5 * 3.3 * 22.6 * 5) = ceil(560) -> 900
Rounding up with margin: timeout_s = 5400 (training epochs are the bottleneck;
phase-A has 8 epochs, longer than smoke's 1 epoch; adjusted for epoch factor ~6x).

Note: 5400s = 1.5h. Below 7200s boundary; no special flag required.

## Walk-back gate
Smoke seed 17: R^2=0.7896, max_dev=0.081 -> HARD_PASS.
Effect size: d = (0.85 - 0.790) / estimated_std. max_dev=0.081 is within 1.5% of pass threshold 0.08.
Walk-back triggered (within 20% of threshold). FULL run uses 5 seeds (adequate power).

## Parent experiments
- wave14_saddle_cascade_plateau_v3: N=1024, R^2=0.322, max_dev=0.249, 3/3 seeds HARD-PASS
- wave14_saddle_cascade_plateau_v4/v5/v6: all ran at N=512 SMOKE (PROT-018 pre-enforcement)
- v7 is the first genuine N=4096 FULL probe
