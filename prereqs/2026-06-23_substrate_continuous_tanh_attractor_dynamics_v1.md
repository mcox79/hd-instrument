# Prereg: substrate_continuous_tanh_attractor_dynamics_v1

**Filed: 2026-06-23 (pre-run)**
**Anchor:** substrate_continuous_tanh_attractor_dynamics_v1
**Script:** experiments/exp_substrate_continuous_tanh_attractor_dynamics_v1.py
**Queue:** remote_cpu_queue (pure numpy, no torch)
**Author:** exp_dev (Skunkworks META recommendation)

---

## Hypothesis

Multi-iter cleanup HARD_FAILed in v1 because sign(W@x) binarizes all state to {-1,+1}
in 1 iteration -- ALL multi-iter arms become bit-identical. The fix: replace sign() with
tanh(beta * state), preserving continuous graded activation across iterations.

Brain-existence-proof: CA3 uses graded continuous activation (firing rates in [0, max]),
NOT bipolar binarization. The substrate's sign() update is a coarse approximation that
destroys the graded signal needed for multi-iteration attractor convergence.

This cell is ORTHOGONAL to the cue-clamped re-injection fix (a340a5a51b818ed33 in flight).

---

## Configuration

- N_DIM = 4096 (FULL; smoke runs at N_DIM=512)
- SEEDS = [7, 17, 23]
- N_TRAIN = 100_000
- N_HELD = 20_000
- VOCAB_CAP = 4000
- SPARSITY_F = 0.05
- AMPLITUDE_SCALE = 1/sqrt(0.05) ~= 4.472
- N_ITER_CLEANUP = 3 (fixed; no converge mode to avoid oscillation in continuous case)

## Arms (6 total)

1. ARM_BASELINE_NO_CLEANUP -- no cleanup iterations; reproduces no-cleanup baseline
2. ARM_SIGN_HOPFIELD_3ITER -- bipolar sign, 3 iters; reproduces v1 HARD_FAIL
3. ARM_TANH_BETA_0p5 -- tanh with beta=0.5 (soft, near-linear)
4. ARM_TANH_BETA_1p0 -- tanh with beta=1.0 (unity gain, brain-like)
5. ARM_TANH_BETA_2p0 -- tanh with beta=2.0 (mid gain)
6. ARM_TANH_BETA_5p0 -- tanh with beta=5.0 (high gain, approaches sign())

---

## Pre-registered bands (HARD before run; do NOT adjust ex-post)

- **HARD_PASS:** any ARM_TANH_BETA beats ARM_BASELINE_NO_CLEANUP by >= +0.05 bits BPC
- **CHAIN_GRADE_BONUS:** lift >= +0.15 bits AND absolute BPC beats cf-RPE chain-grade 7.1052
- **MIDDLE_BAND:** lift +0.02 to +0.05 bits
- **HARD_FAIL:** all ARM_TANH_BETA <= ARM_BASELINE_NO_CLEANUP across all beta (lift < 0.02)
- **SANITY_RAIL:** ARM_BASELINE_NO_CLEANUP must reproduce 7.2268 +/- 0.05 (N_DIM=4096 may
  deviate from v1 N_DIM=8192; note in verdict if delta > tolerance)
- **CV_MAX:** cv < 0.05 per arm across 3 seeds

## N-suffix (PROT-018)

No _nN suffix in anchor name. Production N_DIM = 4096 (stated in script + here).

---

## Calibration probe note

Prior empirical anchors exist from v1 (ARM_BASELINE_NO_CLEANUP bpc=7.2268 at N=8192).
This is NOT a first-measurement probe. Thresholds set from known substrate behavior.
N_DIM=4096 (vs v1 N_DIM=8192) may shift baseline slightly -- sanity rail captures this.

---

## Timeout estimate

smoke_wall_s = 1.0s (N_DIM=512, 1 seed, 6 arms)
FULL_N / smoke_N = 4096 / 512 = 8
FULL_seeds / smoke_seeds = 3 / 1 = 3
scaling_exp = 2.0 (W matrix [N_DIM x N_DIM] is matrix-multiply dominant)

timeout_s = ceil(1.5 * 1.0 * 8^2.0 * 3) = ceil(1.5 * 64 * 3) = ceil(288) = 300s

However: at N=4096 the W matrix is 4096x4096 float32 = 64MB; the outer-product accumulation
for N_TRAIN=100k tokens is the bottleneck. Empirically v1 at N=8192 N_TRAIN=100k took ~40-60
min per seed; at N=4096 expect ~10-15 min per seed. 3 seeds + 6 arms = ~45 min wall time.

Using empirical estimate: timeout_s = ceil(1.5 * 900 * 3) = 4050 -> **timeout_s = 4500**

(900s = 15 min per seed estimate, rounded up; 1.5x safety factor; 3 seeds)

This is under the 7200s flag threshold and well under the 14400s block threshold.

---

## Smoke result (BELOW_REGIME -- expected)

Smoke at N_DIM=512: HARD_FAIL (lift=-0.04 to -0.10). This is the BELOW_REGIME artifact:
- At V=300/N_TRAIN=2000, baseline already beats unigram by ~0.02 bits; cleanup arms hurt.
- Raw_bpc at T1_L1 DOES differ across arms (7.72 baseline vs 7.68-7.69 tanh arms) --
  mechanism is physically running; logits are non-identical.
- Calibrated BPC collapses to same value because lam=0.7 dominates at this tiny scale.
- The Skunkworks note (TARGET 1) explicitly states: N=512 is far below the regime where
  multi-iter cleanup would matter.

Multi-scale smoke at N_DIM=2048 (x4): same pattern, lift=-0.10. Still below regime.

This is the same "below-regime smoke" documented by Skunkworks for the v1 cell.
The FULL run at N=4096 is the load-bearing test. Dispatching FULL.

NOT triggering INSTRUMENTATION_SUSPECT: logits provably non-identical across arms,
self-test passes diff_beta_range check, BPC is finite and in plausible range.

---

## Dependency check

- experiments/_seed_checkpoint.py: EXISTS
- data/text8_cache/text8.txt: EXISTS (used by all substrate LM cells)
- No other upstream dependencies

---

## What this does NOT show

- Whether tanh dynamics help with different encoders (char-trigram specific)
- Whether effect persists at N_DIM=8192 (run at N_DIM=4096)
- Whether the optimal beta generalizes beyond word-bigram BPC metric
- Results for the ORTHOGONAL cue-clamped re-injection fix (separate cell)
