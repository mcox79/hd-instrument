# Pre-registration: wave14_cap8_vamp_iterates_rm_1_m_v1

**Date:** 2026-05-24
**Queue:** `remote_cpu_queue`
**Script:** `experiments/exp_wave14_cap8_vamp_iterates_rm_1_m_v1.py`
**ETA:** ~10-15 min CPU
**Anchor type:** DATA GENERATION (not a hypothesis test)

## Purpose

Generate VAMP iterate trajectories for the RM(1, m) codebook at the Cap 8
protocol shape so that the downstream audit-trail v5 can compute a non-fallback
Spearman rho on RM(1, m) and disambiguate v4's reported 0.40.

Per-family iterate-status output from v4 showed RM(1, m) silently fell back to
spectrum-only mode because v3/v4's `measure_codebook_audit_trail_v2` gates
iterate-loading on `name in ("srht", "hadamard")`. v4's rho=0.40 may therefore
be an artifact of shorter (spectrum-only) fingerprint vectors rather than a
genuine property of the RM(1, m) family.

## Configuration

- `N = 4096`
- `n_seeds = 5` (seed values: 13, 1013, 2013, 3013, 4013 -- matches v1c)
- `alpha_grid = {0.5, 0.75, 1.0}` (M/N ratios; matches v1c)
- `codebooks = ["rm_1_m"]`
- `signal_var = 1.0`, `sigma_noise = 0.1`, `n_iter = 300`
- Expected files: 1 codebook x 3 alphas x 5 seeds = **15 iterate-trace JSON files**

## Outputs

- `data/exp_wave14_cap8_vamp_iterates_rm_1_m_v1/iterates/rm_1_m/alpha_{0p50,0p75,1p00}/seed_{0013,1013,2013,3013,4013}.json`
- `data/exp_wave14_cap8_vamp_iterates_rm_1_m_v1/metrics.json`

Per-cell file contains the full `run_vamp_with_iterates` trace: `mse_per_iter`,
`x_hat_norms`, `x_hat_2_norms`, `onsager_term_norm`, `gamma_1`, `gamma_2`,
`n_iter_actual`, plus the closed-form `vamp_se_pred`.

## Verdict bands

This is data generation; there are NO hard-pass/hard-fail signal thresholds.
Verdicts are file-count based:

- **CAP8_RM_ITERATES_GENERATED** (success): all 15 files written with
  `n_iter_actual >= 3` each. Downstream v5 unblocked.
- **CAP8_RM_ITERATES_PARTIAL**: 5-14 files written. v5 will check file-existence
  per cell; rho on RM(1, m) computable on a subset.
- **CAP8_RM_ITERATES_FAILED**: <5 files. Data gap not filled; v5 will fall back
  to spectrum-only on RM(1, m), defeating the purpose of this anchor.

## Self-tests (run before main)

1. `_alpha_label` produces filesystem-safe directory names.
2. `build_rm_1_m` works at N=4096 with M in {2048, 4096}; entries are bipolar
   normalised to magnitude 1/sqrt(N).
3. `build_rm_1_m` row uniqueness check at N=64, M=8 (RM(1, m) has 2N=128
   distinct codewords; subsampling 8 must give 8 unique sign-rows).
4. VAMP iid-Gaussian sanity: final MSE within 20% of closed-form AMP-SE
   prediction (per Rangan-Schniter-Fletcher 2017 equivalence at iid).
5. iterate-trace JSON round-trip.
6. `compute_verdict` branches: synthetic-missing-files manifest produces a
   non-GENERATED verdict.

## Smoke

`N=64`, 1 seed, alpha=1.0, RM(1, m) only -> 1 iterate-trace file.
Smoke output: `data/exp_wave14_cap8_vamp_iterates_rm_1_m_v1_smoke/`.
Smoke result (2026-05-24): **PASS**, verdict=CAP8_RM_ITERATES_GENERATED, 1 file written.

## Blockers / risks

- RM(1, m) codebook construction at N=4096 requires `torch` (used internally
  for `sylvester_hadamard`). Self-test 2 confirms it builds at N=4096 on the
  desktop; remote CPU runner should have the same env.
- Bipolar RM(1, m) codebook with `M=4096` of `2N=8192` codewords subsamples
  fine. No degeneracy expected.

## Downstream

The v5 audit-trail pipeline (Anchor 2) depends on these traces being present
in the `rm_1_m/alpha_1p00/seed_{0013,...,4013}.json` layout. v5's multi-root
loader searches both v1c and rm_1_m_v1 roots.
