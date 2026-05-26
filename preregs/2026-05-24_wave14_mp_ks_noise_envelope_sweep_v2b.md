# Prereg: wave14_mp_ks_noise_envelope_sweep_v2b

Date: 2026-05-24
Queue: remote_cpu_queue
ETA: 45-60 min CPU (5 codebooks * 5 eta * 20 seeds = 500 cells; ~4x v1's 150)
Type: HYPOTHESIS TEST (Cap 12 noise envelope width)

## Purpose

E1' v1 swept eta in {0, 0.01, 0.025, 0.05, 0.075, 0.10} at 5 seeds and
landed in MIDDLE BAND. verdict_handler pre-registered this higher-stats
follow-up: finer grid in the apparently-critical region with ~4x more
seeds.

## What's new vs v1

- **Finer eta grid in the critical band.** eta in {0.01, 0.02, 0.03, 0.04, 0.05}.
  Dropped the eta=0 baseline (v174 already confirmed clean routing 4-5/5).
  Dropped eta=0.075, 0.10 because v1 already showed catastrophic failure
  there.
- **20 seeds per cell** (4x v1).
- Same protocol otherwise: 5 codebooks * N=1024 * M/N=1.0 * tau=0.20 *
  n_iter=300 VAMP.

## HARD PASS (Cap 12 noise envelope extends to eta <= 0.05)

- `per_eta_correct_codebooks >= 4` (out of 5) at EVERY eta in
  {0.01, 0.02, 0.03, 0.04, 0.05}
- AND average ks_mean across codebooks is monotonically non-decreasing
  in eta (tolerance: 1.0 stddev within-codebook spread)

Substrate-product claim: "Cap 12 tolerates noise up to eta = 5% before
degrading."

## HARD FAIL (Cap 12 noise envelope is NARROW)

- `per_eta_correct_codebooks <= 3` at eta=0.02 (envelope < 2%; routing
  starts breaking on minimal noise)

Substrate-product claim narrows to: "Cap 12 routes correctly only for
noise eta < 1-2%; the v175 ✅ promotion holds only for near-clean
conditions."

## MIDDLE BAND

- Monotonic decay but no clean eta_critical resolved between PASS and
  FAIL. v3 follow-up (more seeds) needed to pin eta_critical to
  +/- 0.005.

## Self-tests (executed before main run)

1. ETA_GRID_V2 monotonicity + required pillar etas (0.02, 0.05) present.
2. `route_from_ks` at tau=0.20 gives expected labels.
3. `identify_eta_critical` returns the smallest sub-threshold eta or
   ">max" sentinel.
4. Synthetic PASS branch: monotonic ks increasing in eta, all 5 codebooks
   routed correctly at every eta -> VERDICT_V2_PASS.
5. Synthetic FAIL branch: all 5 wrong at eta=0.02 -> VERDICT_V2_KILLED.
6. Synthetic MIDDLE branch: 4/5 correct at eta=0.02 but 0/5 at eta=0.04 ->
   VERDICT_V2_INCONCLUSIVE.
7. Missing-cells INCONCLUSIVE branch.
8. `check_monotonic_ks_in_eta` clean monotonic returns True.
9. `check_monotonic_ks_in_eta` strong downtick returns False (tol=0.05).

## Smoke (PASS)

```
N=64, 1 seed, 2 codebooks * 2 eta = 4 cells
VERDICT: MP_KS_NOISE_ENVELOPE_SWEEP_V2_INCONCLUSIVE (need 25 cells)
Self-tests: 9/9 PASS.
```

## Open questions / risks

- 20 seeds per cell may still be insufficient to discriminate
  per_eta_correct=4/5 vs 3/5 in the very narrow critical region (eta
  in {0.02, 0.03}). If MIDDLE BAND returns again, v3 should jump to
  50 seeds or use a different routing-confidence metric (CI on
  per-codebook routing rather than just count).
- Noise model is per-entry sign-flip (depolarization channel for
  bipolar codebooks); other noise models (additive Gaussian, sub-
  Gaussian) would map to different eta_critical and are NOT tested here.
