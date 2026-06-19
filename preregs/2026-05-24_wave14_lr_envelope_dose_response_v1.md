# Prereg — wave14_lr_envelope_dose_response_v1

## Hypothesis

The substrate-novel finding from `wave14_online_W_lr_envelope_duration_v1`
(E4 long-tail Robbins-Monro tau=40 dominates E1 baseline tau=10 at fixed
integral sum=10.0) is a real dose-response, not noise: retention accuracy
will rise monotonically (or peak at intermediate tau) as we sweep
tau in {10, 20, 40, 80, 160} with fixed integral.

If retention is flat in tau, the original E4 win was sampling noise and the
substrate is actually envelope-insensitive at fixed integral.

## Pre-registered bands

- **HARD PASS — MONOTONIC** (`LR_DOSE_MONOTONIC`):
  - Retention rises monotonically across all 4 adjacent (tau_k -> tau_{k+1}) pairs.
  - Argmax at tau=160 (endpoint).
  - Substrate prefers longer tails; longest tail wins.

- **HARD PASS — PEAKED** (`LR_DOSE_PEAKED`):
  - Argmax at an interior tau in {20, 40, 80}.
  - Peak retention exceeds both endpoints by >= 0.03.
  - Substrate has an OPTIMAL tail length; longer is not always better.

- **HARD FAIL** (`LR_DOSE_FLAT`):
  - max - min retention across 5 tau values < 0.03.
  - Substrate is envelope-insensitive at fixed integral; original E4 win was noise.

- **MIDDLE BAND** (`LR_DOSE_INCONCLUSIVE`):
  - Non-monotone but no clean peak (e.g., bimodal, oscillating).

## Design

- N = 4096 bipolar substrate (Cap 5 v153/v159 reference operating point).
- n_writes = 50, snap_threshold = 1.0.
- 5 tau values: {10, 20, 40, 80, 160}. All envelopes Robbins-Monro c/(1+t/tau)
  scaled so discrete sum_t lr(t) = 10.0 (within +/- 5%).
- 3 noise levels p_flip in {0.20, 0.30, 0.40}.
- 3 seeds per cell.
- Total cells: 5 * 3 * 3 = 45. ETA ~30-45 min CPU.

Cell metric: mean retention accuracy across the n_writes step trajectory
(uses `min` over the trajectory to capture worst-case retention as in the
parent experiment). Mean over 3 seeds per (tau, p) cell.

## Citations

- Parent: `wave14_online_W_lr_envelope_duration_v1` (substrate E4 win, 2026-05-24).
- Gong et al. 2026 Science DOI 10.1126/science.aeb0813: dopamine duration mechanism.
- Per [[feedback-2x-means-depth]]: 2x drill on substrate-novel finding.

## Routing

- Queue: `remote_cpu_queue`.
- Timeout: 3600 s.
- Pure-CPU torch (no CUDA).
