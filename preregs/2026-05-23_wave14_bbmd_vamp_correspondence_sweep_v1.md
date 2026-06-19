# Prereg — wave14_bbmd_vamp_correspondence_sweep_v1

**Date**: 2026-05-23 (late session)
**Owner**: exp_dev (BBMD anchor 1 of 2)
**Source**: research note `notes/research_promising_direction_2026-05-23.md` (BBMD regime proposal). Cap-12 promotion is conditional on BOTH anchors landing positive.

## Hypothesis

Bulk-Bounded Moment-Divergent (BBMD) regime claim: scalar-Onsager AMP's
state-evolution error scales **monotonically** with the empirical kappa_n
divergence integral `sum_{n=2..6} | kappa_n - kappa_n^MP |` (the BBMD-distance
scalar). VAMP's state-evolution error stays bounded across the regime axis.

To test this, interpolate the measurement matrix:

  `W_alpha = (1 - alpha) * G + alpha * W_kerdock,  alpha in {0, 0.25, 0.5, 0.75, 1.0}`

where `G` is iid `N(0, 1)` and `W_kerdock` is M rows of the substrate's 4-coset
Kerdock codebook. The Kerdock realization (subsample seed) is held fixed across
alphas for each top-level seed, so only `alpha` varies.

## Setup

- N = 4096, M = N (M/N = 1.0).
- alpha_interp grid: {0, 0.25, 0.5, 0.75, 1.0} (5 cells).
- 10 seeds per alpha (Kerdock row subsample + iid Gaussian both seeded).
- Signal prior: matched Gaussian, signal_var = 1.0.
- Noise: Gaussian, sigma_noise = 0.1 (sigma_sq = 0.01).
- VAMP iteration: 300 max iters or 5-iter MSE plateau (1e-10).
- AMP iteration: 300 max iters with matched Gaussian denoiser.
- kappa_n profile: spectral moments m_1..m_6 of `eig(W^T W / N)` -> NCP-Mobius
  inversion (reuse `exp_wave14_kappa_n_profile_v1` machinery).
- BBMD-distance: `sum_{n=2..6} | kappa_n_empirical - alpha_ratio |` where
  alpha_ratio = M/N is the MP reference value.

## Output metrics (per cell)

- `bbmd_distance_mean`: mean over seeds of `sum |delta_kappa_n|`.
- `amp_rel_err_mean`: mean over seeds of `|AMP-SE-pred - emp-AMP| / max(*, eps)`.
- `vamp_rel_err_mean`: mean over seeds of `|VAMP-SE-pred - emp-VAMP| / max(*, eps)`.
- `kappa_mean`: per-n cumulant averaged over seeds.

## Aggregate metrics

- `spearman_rho`: Spearman rank correlation of cell-level (BBMD-distance, AMP-rel-err)
  across the 5 alpha cells.
- `max_vamp_rel_err`: max over cells of `vamp_rel_err_mean`.

## Verdicts

**HARD PASS — `BBMD_VAMP_CORRESPONDENCE_PASS`** (Anchor 1 lands positive):
- `spearman_rho(AMP-error, sum|delta_kappa_n|) > 0.8` across the alpha sweep, AND
- `vamp_rel_err < 0.05` at EVERY alpha (including alpha=1 / pure Kerdock).

**HARD FAIL — `BBMD_VAMP_CORRESPONDENCE_KILLED`** (BBMD as a regime axis is killed):
- `spearman_rho < 0.4` (no monotonic relationship), OR
- `vamp_rel_err > 0.10` at any alpha (VAMP doesn't actually tame Kerdock; the
  v168 finding was an artifact).

**INCONCLUSIVE — `BBMD_VAMP_CORRESPONDENCE_INCONCLUSIVE`**: anything in between.

## Pre-commit

- Verdict thresholds and the Spearman-rho variable are FROZEN here.
- Spearman rho is computed over cell-level means (5 data points). With 5
  points the threshold rho > 0.8 corresponds to a near-monotonic relationship.
- If `bbmd_distance` is degenerate (all equal across alphas, unlikely),
  verdict defaults to INCONCLUSIVE.

## Downstream

- PASS + Anchor-2 PASS -> propose Cap-12 (BBMD-VAMP) to Strategy.
- PASS + Anchor-2 FAIL -> narrowed Cap-12 framed as Kerdock-internal.
- KILLED -> BBMD as a regime axis is wrong; substrate-product story degrades to
  "VAMP works on substrate" only.

## Queue

- Queue: `remote_cpu_queue` (interpolation + SE solving; numpy-bound, no GPU).
- Timeout: 5400 s.
- ETA: 30-60 min wallclock.

## Citations

- Zhong-Wang-Fan 2020/2024 (arXiv:2008.11892) — free-cumulant Onsager corrections
  in RI-AMP.
- Rangan-Schniter-Fletcher 2017 (arXiv:1610.03082) — VAMP.
- Bayati-Montanari 2011 — scalar AMP-SE (the truncation-at-kappa_1 baseline).
