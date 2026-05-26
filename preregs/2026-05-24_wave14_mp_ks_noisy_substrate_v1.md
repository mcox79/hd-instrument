# Pre-registration: wave14_mp_ks_noisy_substrate_v1 (Cap 12 ✅ E1 STRESS)

**Date**: 2026-05-24
**Wave**: 14 (MP-KS pre-flight diagnostic)
**Driver**: orchestrator silent_idle emergency refill post-v175 promotion
**Capability under stress**: Cap 12 (AMP-vs-VAMP inference routing infrastructure) at ✅
**Anchor role**: E1 — noisy-substrate envelope expansion (real customer conditions)
**Script**: `experiments/exp_wave14_mp_ks_noisy_substrate_v1.py`
**Queue**: `remote_cpu_queue`
**ETA**: 30-45 min (5 codebooks × 5 seeds × N=1024 × 3 tau values)

## Hypothesis

After v175 ✅ promotion the MP-KS pre-test pipeline routes 5/5 codebooks correctly at tau=0.20 (clean-codebook regime). The customer-facing claim is "MP-KS pre-flight diagnoses customer matrices in production." Production matrices are not clean — they have entry-level noise. The standard depolarization noise model is per-entry sign flip with probability eta. At eta=0.10 (10% bit flip), does MP-KS still route correctly?

Concretely: build each of the 5 codebooks at N=1024, inject sign-flip noise with eta=0.10 entry-wise, then compute MP-KS once on the noisy matrix, run AMP + VAMP once on (W_noisy, y) to establish the empirical truth label, and check at each tau in {0.15, 0.20, 0.25} whether route_from_ks(ks_noisy, tau) matches the empirical truth label.

## Bands (HARD PASS / HARD FAIL / MIDDLE BAND)

Per [[feedback-envelope-expansion-fail-bands]], all three bands pre-registered verbatim before queue submission.

### HARD PASS — Cap 12 ✅ survives E1 STRESS

>=4/5 codebooks routed correctly at EACH of tau in {0.15, 0.20, 0.25} under eta=0.10 noise.

Interpretation: MP-KS pre-flight is robust to real-world depolarization noise; the v175 ✅ promotion holds under noisy-substrate envelope expansion.

### HARD FAIL — Cap 12 ✅ reverts to 🟢 with clean-only annotation

0/5 routed correctly at ANY tau value under eta=0.10 noise.

Interpretation: Infrastructure FRAGILE to noise; the customer-facing claim collapses for noisy substrates. Cap 12 reverts to 🟢 (clean-codebook regime only).

### MIDDLE BAND — Cap 12 ✅ stays with noise-sensitivity annotation

1-3/5 correct at one or two tau values; partial robustness.

Interpretation: Cap 12 ✅ stands but cap_map annotates "robust to noise at tau=X, marginal at tau=Y." Strategy may dispatch a follow-up to identify the robust tau choice.

## Design

- N=1024, M/N=1.0, M=1024 (square; matches v174/v175 baseline).
- Codebooks (same 5 as v175): iid_gauss, srht, hadamard, rm_1_m, kerdock.
- Per codebook: 5 seeds (matches v175 statistical depth).
- For each seed:
  1. Build clean W (M × N) via codebook builder.
  2. Apply per-entry sign-flip noise with probability eta=0.10:
     mask = rng.random(W.shape) < eta; signs = where(mask, -1, +1); W_noisy = W * signs.
  3. Compute SVD of W_noisy.
  4. Compute MP-KS statistic on noisy eigenvalues.
  5. Build noisy signal y = W_noisy @ x_true + observation_noise (sigma=0.1).
  6. Run AMP and VAMP loops on (W_noisy, y) for n_iter=300 each.
  7. amp_rel = |amp_emp - amp_se_pred| / max; same for vamp_rel.
  8. Empirical truth label: AMP_OK if amp_rel < 0.10 else VAMP_REQUIRED.
- Aggregate ks across seeds; aggregate amp_rel and vamp_rel; pick empirical label from amp_rel_mean.
- For each tau in {0.15, 0.20, 0.25}: route_from_ks(ks_mean, tau); compare to empirical label; per_tau_correct.
- Verdict from per_tau_correct against the three bands above.

## Self-test cells (per [[feedback-strategy-spec-formula-selftests]])

The script self-tests 9 formula assertions, all of which must pass before the experiment runs:

1. `apply_signflip_noise(W, eta=0)` returns W unchanged.
2. `apply_signflip_noise(W, eta=1)` returns -W.
3. `apply_signflip_noise(W_big, eta=0.10)` flip fraction in (0.07, 0.13).
4. `route_from_ks(ks, tau)` boundary cases (<=tau → AMP_OK).
5. `empirical_truth_from_errs` boundary cases.
6. compute_verdict on a synthetic 5/5/5 dataset → HARD PASS.
7. compute_verdict on a synthetic 0/0/0 dataset → HARD FAIL.
8. compute_verdict on a synthetic 3/5/5 dataset → MIDDLE BAND.
9. compute_verdict on a 3-codebook (missing) dataset → INCONCLUSIVE.

All 9 pass locally before queue submission. Remote-side `--self-test` gate will re-run pre-execution.

## Acceptance criteria for queue submission

- [x] Script includes `sys.stdout.reconfigure(...)` block at top.
- [x] Script includes metrics-write block (`write_metrics` with atomic .tmp + rename).
- [x] Script includes env-var-driven `HDLAB_EXP_NAME` outdir.
- [x] Self-test runs at start of `run_main` (and `run_smoke`).
- [x] Pre-run smoke at N=64 / 1-seed / 2-codebook completed locally; produced valid metrics.json.
- [x] HARD PASS / HARD FAIL / MIDDLE BAND verbatim in this prereg.

## Pause-flag compliance

`data/orchestrator_paused.flag` ABSENT at dispatch time. exp_dev verified flag is not present before writing this prereg.

## Notes

- Noise seed offset by 50_000 from codebook seed for stable, reproducible noisy realizations.
- The noise is applied to BOTH the matrix that MP-KS sees and the matrix AMP/VAMP see (this is the customer-facing setting: operator observes only the noisy matrix; the routing must work given that observation).
- For bipolar codebooks (Hadamard, RM, Kerdock) a sign flip is a canonical depolarization. For Gaussian / SRHT entries it's a symmetric distortion that preserves the marginal magnitude distribution but disrupts joint sign structure — a meaningful nontrivial perturbation for both regimes.
