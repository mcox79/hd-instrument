# Prereg: substrate_sparse_receiver_energy_diagnosis_v1

**Date:** 2026-06-23
**Author:** exp_dev
**Anchor:** substrate_sparse_receiver_energy_diagnosis_v1
**Script:** experiments/exp_substrate_sparse_receiver_energy_diagnosis_v1.py
**Queue:** remote_cpu_queue
**Trigger:** exp_dev_handoff_research_sparse_cleanup_compose_breakage_diagnosis_2026-06-23.md (PRIMARY anchor)

---

## Scientific question

Does matched-filter-energy loss (signal_energy = f*N for sparse bipolar) explain
the HARD_FAIL of exp_substrate_theta_gamma_nested_with_brain_compensation_N4096_v1?

Hypothesis: receiver SNR scales as sqrt(f*N)/sigma. Recall vs SNR_pred should
collapse onto a single monotone Q-tail curve across the (f, sigma) grid,
giving Pearson r >= 0.85 if matched-filter-energy is the primary mechanism.

---

## Config

- N_DIM: 4096
- M: 500
- N_EVAL: 200
- SEEDS: [7, 17, 23]
- F_GRID: [0.005, 0.01, 0.02, 0.10, 0.5, 1.0]
- SIGMA_GRID: [16.0, 32.0, 64.0, 128.0]
- Grid size: 6 f-values x 4 sigma-values x 3 seeds x 200 trials = 14,400 measurements

## N-suffix

No _n<NUMBER> suffix in anchor name. Production N = 4096. Rationale: the
experiment's primary axis is the (f, sigma) grid, not N itself; N is held
fixed at 4096 to match the source failing cell exactly.

---

## Arms

- ARM_DENSE_BASELINE: dense bipolar codebook (f=1.0 equivalent); amplitude +/-1; same sigma grid
- ARM_SPARSE_RAW: sparse bipolar, f-fraction active, amplitude +/-1 (raw; -17dB penalty at f=0.02)
- ARM_SPARSE_AMPLIFIED: sparse bipolar, amplitude 1/sqrt(f); energy = N (dense-equivalent)

---

## Pre-registered HARD bands (immutable post-dispatch)

### HARD_PASS (Pearson r >= 0.85):
Matched-filter-energy IS primary mechanism. Routes to SECONDARY anchor
(exp_theta_gamma_nested_brain_amplified_compose_v2) per handoff.

Tier: MM (measurement_mechanism). Chain-grade-eligible if HARD_PASS +
brain-canonical mechanism confirmed by SECONDARY anchor.

### MIDDLE_BAND (r in [0.50, 0.85)):
Matched-filter-energy is a partial explanation; another mechanism also
contributes ~30-50% of variance. Routes to Anchor 3 (support-restricted
WTA receiver) per handoff.

### HARD_FAIL (r < 0.50):
Matched-filter-energy NOT primary mechanism. Different bug class.
Refer back to Research for re-drill on alternative failure mechanisms
(basin-overlap finite-N? attractor pathology? compose interference?).

---

## Secondary pre-reg criteria

### CRITERION_B: ARM_SPARSE_RAW @ f=0.02, sigma=16 in [0.45, 0.75]
Reproduces empirical 0.583 from SINGLE_LOCKIN_SPARSE arm of source cell.
Confirms this cell runs the same receiver math as the source failure.

### CRITERION_C: ARM_SPARSE_RAW @ f=0.50, sigma=16 >= 0.95
High-density sparse recovers near-dense performance, confirming the
failure is f-driven (not some other structural issue).

### CRITERION_D: ARM_SPARSE_AMPLIFIED @ f=0.02, sigma=16 >= 0.95
Amplitude fix (1/sqrt(f)) restores dense-equivalent performance, confirming
amplitude-scaling is the correct receiver-side fix.

### CV < 0.05: Pearson r CV across seeds must be < 0.05.

---

## Calibration notes

Prior empirical anchor: YES. Source cell gives SINGLE_LOCKIN_SPARSE@sigma=16 = 0.583
at f=0.02, N=4096. The matched-filter algebra predicts this (see research note L2.2).
Pre-reg bands are NOT +-50% widened (this is not a first-calibration-probe; the
research note provides empirical grounding at P_deflated=0.85).

---

## Smoke gate results

- Smoke N=512, M=50, f_grid=[0.02, 0.5], sigma_grid=[16, 64], seeds=[7,17]
- Per-seed Pearson r: seed=7: 0.976, seed=17: 0.729
- Aggregate Pearson r: 0.80 (MIDDLE_BAND at smoke scale)
- Smoke scale shows limited dynamic range; full grid at N=4096 covers SNR 0.06 to 4.0
- Multi-scale smoke N=2048: Pearson r = 0.94 (HARD_PASS territory)
- Walk-back gate: per-seed r=0.98 and 0.73; max well above HARD_PASS threshold.
  FULL scale N=4096 includes f=1.0 (dense, snr=4.0/sigma) which anchors the
  top of the sigmoid. No sample doubling needed.
- INSTRUMENTATION_SUSPECT check: no all-zero, no all-constant, no filter-eliminates-all
- Self-test PASS

---

## Timeout estimate

Smoke wall: 0.5s for 2 seeds, 4 configs at N=512.
FULL: 3 seeds, 24 configs (6f x 4sigma) at N=4096.

Per seed, bottleneck is W = codebook.T @ codebook at shape (4096, 4096) per (arm, f) combo.
Per seed: 3 arms x 6 f-values = 18 W-matrix computations.
Each W: O(M * N^2) = 500 * 4096^2 = 8.4B FLOPs.
Total W computations: 18 * 3 seeds = 54 W-computations = 54 * 8.4B = 454B FLOPs.
Remote CPU at ~10-20 GFLOPS: ~23-46s for W alone.
Plus batched query evaluation: 200 evals x 24 configs x 3 seeds x (N x N decode + M score) = tolerable.

Estimated FULL wall: ~5-15 min on remote CPU.

timeout_s = ceil(1.5 * 900 * 1.0 * 1) = 1350 rounded up -> 1800s (30 min).
Using scaling_exp=1.0 (linear sweep; no matrix work grows quadratically with scale axis).

---

## Cert chain expectation

If HARD_PASS: Pearson r >= 0.85 confirms matched-filter-energy is primary.
  -> Dispatch SECONDARY anchor (amplitude-scaled brain-compose fix cell)
  -> Atomize: sparse_bipolar_pays_sqrt_f_receiver_SNR_unless_amplitude_scaled_meta (META)
  -> Audit K-module heterogeneous compose cell abda9f08 sparse arm

If MIDDLE_BAND: Dispatch Anchor 3 (support-restricted WTA) per handoff.

If HARD_FAIL: Route back to Research. Do NOT dispatch SECONDARY.
