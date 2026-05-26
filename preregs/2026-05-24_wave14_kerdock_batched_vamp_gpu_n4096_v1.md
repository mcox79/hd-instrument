# wave14 Kerdock batched-VAMP recovery curve on GPU (substrate-native N=4096) v1

Date: 2026-05-24
Cap target: Cap 8 (VAMP universality envelope) and Cap 13 (Clifford-TN at substrate scale)
Type: GPU anchor (genuinely CUDA-bound: batched matmul + per-iter denoising on GPU)

## Question

At substrate-native N=4096 with the FULL 4-coset MM Kerdock measurement codebook
(M=16384, M/N=4), does the empirical batched-VAMP recovery curve over SNR sweep
trace the (R-transform-predicted) state-evolution fixed point with no batch-to-batch
variance blowup?  This is the production-scale empirical companion to the CPU
Cap 8 R-transform anchor.

## Why GPU

Each (seed, snr) cell runs `batch_size=2048` independent signals through 200 VAMP
iterations on the same (16384, 4096) Kerdock measurement matrix.  Each iteration
is two batched matmuls:
  - z_a = A @ x_hat_batch       shape (16384, 2048)  in (16384x4096)@(4096x2048)
  - r_b = A.T @ residual_batch  shape (4096, 2048)   in (4096x16384)@(16384x2048)

Per iteration: ~16384*4096*2048*2 = 2.75e11 mul-adds *2 directions = 5.5e11 FLOPs.
At 200 iter * 8 SNR cells * 5 seeds = 8000 iterations = 4.4e15 FLOPs total.

A 4060 Ti at sustained 8 TFLOPs (fp32) gives ~9 minutes of pure GPU matmul,
plus denoiser kernels and reduction ops — total wall-clock 30-90 min, all on GPU.
No numpy fallback: codebook, signals, iterates all live on cuda device.

## Method

1. Build 4-coset MM Kerdock codebook at N=4096 on GPU (M=16384, entries +/-1).
2. Normalize: A_norm = codebook / sqrt(N), so A_norm.T @ A_norm has unit-bulk spectrum.
3. For each (seed, snr) cell:
   a. Draw batch_size=2048 isotropic Gaussian signals x in R^N on GPU.
   b. Compute y = A_norm @ x + sigma * noise on GPU; signal-to-noise ratio fixed.
   c. Run VAMP for n_iter=200 with matched MMSE denoiser (Gaussian prior).
      Track per-iteration MSE averaged across the 2048-sample batch.
   d. Record final MSE, iter-to-converge, and per-sample MSE std (universality
      check: batch variance should shrink as 1/batch_size if SE applies).
4. Compare empirical batch-MSE-mean to the R-transform-predicted SE fixed point
   (computed CPU-side via the Kerdock spectrum from a one-time eigvalsh).

## Decision rule

Verdict labels (in `verdict` field):

- HARD_PASS_KERDOCK_VAMP_GPU_UNIVERSALITY: at every SNR cell, |emp_mse - se_mse| / se_mse < 0.05,
  AND batch_mse_std / sqrt(batch_size) < 0.10 * se_mse (universality variance bound holds).
  This licenses the R-transform / Cap 8 anchor at production scale.

- MIDDLE_BAND_KERDOCK_VAMP_PARTIAL: rel_err in [0.05, 0.20] on at least one cell,
  OR batch variance bound fails on at most 2 cells. Partial agreement; Cap 8
  envelope holds in bulk but production-scale finite-size effects detected.

- HARD_FAIL_KERDOCK_VAMP_GPU_DIVERGES: rel_err > 0.20 on at least one cell. Kerdock
  matrix breaks VAMP universality at substrate scale.

- HARD_FAIL_NO_RESULTS: every (seed, snr) cell crashed or returned NaN/inf.

## Hyperparams (full mode)

- N = 4096
- M = 16384 (full 4-coset MM Kerdock)
- batch_size = 2048
- snr_db_list = [-6, -3, 0, 3, 6, 9, 12, 15]   (8 cells)
- n_iter = 200
- n_seeds = 5
- device = cuda
- dtype = float32

## Hyperparams (smoke mode)

- N = 1024 (smallest valid Kerdock 4-coset N)
- M = 4096
- batch_size = 64
- snr_db_list = [0, 6]
- n_iter = 20
- n_seeds = 1
- device = cuda if available else cpu

## Self-tests (5)

1. Codebook entries +/-1 at N=1024 (4-coset MM).
2. A_norm column norms equal sqrt(M/N) at N=1024 with seed=0.
3. VAMP one-step matches direct MMSE update at iter=1 (zero-warm-start sanity).
4. R-transform SE fixed point at M/N=4, signal_var=1, snr=0 dB matches closed form
   (alpha=4 large-noise asymptote: mse -> signal_var / (1 + snr_lin*alpha)).
5. Verdict-function logic on 4 synthetic cell tables.

## Outputs

- `data/exp_wave14_kerdock_batched_vamp_gpu_n4096_v1/metrics.json`
- Required keys: `verdict`, `verdict_msg`, `elapsed_s`, `summary` (with per-cell stats),
  `config`, `all_results` (list of per-cell dicts).

## Expected wall-clock

30-90 min on RTX 4060 Ti. Timeout set to 10800 s (3 hr) for safety margin.

## Cap-map updates this anchor licenses (on HARD_PASS)

- Cap 8 (VAMP_UNIVERSALITY_KERDOCK): bumped from middle-band to HARD_PASS at
  substrate-native N=4096 with batch_size=2048 (was only verified at N<=2048).
- Cap 13 (CLIFFORD_TN_PRODUCTION_SCALE): independent GPU corroboration that the
  Kerdock 4-coset spectrum is well-conditioned at N=4096 (eigenvalues != 0 in
  the active subspace; VAMP wouldn't converge otherwise).
