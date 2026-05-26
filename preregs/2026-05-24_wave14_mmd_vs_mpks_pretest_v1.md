# Prereg: wave14_mmd_vs_mpks_pretest_v1

**Date**: 2026-05-24
**Vertex**: MMD_VS_MPKS_PRETEST_PASS / KILLED / INCONCLUSIVE
**Capability target**: Cap 12 ✅ — **alternative-score audit** (does MMD or Wasserstein out-perform MP-KS as the routing non-conformity score?)
**Queue**: `remote_cpu_queue` (~2h CPU)
**Script**: `experiments/exp_wave14_mmd_vs_mpks_pretest_v1.py`

## Background

Research probe #3 identified MMD-with-RBF-kernel and Sliced-Wasserstein as candidates that may strictly out-perform MP-KS for the Cap 12 pre-test. If true, this either:
- (a) tightens the v175 Cap-12 ✅ predictor from ρ=0.700 (MP-KS) to ρ ≥ 0.75 (MMD/Wasserstein) — claim-strengthening, OR
- (b) reveals v175's ρ=0.700 was a test-power artifact (the underlying AMP-error signal is stronger than KS captures).

This is a META-tool audit: it interrogates Cap 12's own design.

## Hypothesis

At least one of {MMD-RBF, Sliced-Wasserstein-1D} produces a Spearman ρ vs AMP-error that exceeds MP-KS by >5% (ρ_alt ≥ 0.75 vs ρ_KS ≈ 0.70) AND achieves routing accuracy ≥ 4/5 at its best threshold (matching or exceeding MP-KS's v175 ✅ baseline).

## Design

- N=1024, M/N=1.0, 5 codebooks × 5 seeds (matches Cap 12 v175 baseline).
- Per (codebook, seed):
  1. Build W; SVD → empirical eigenvalues.
  2. Compute MP-KS score (Cap 12 baseline; via mp_ks_stat).
  3. Compute MMD-RBF score between empirical eigenvalues and an MP reference sample (Gaussian kernel, σ via median heuristic).
  4. Compute Sliced-Wasserstein 1D between empirical eigenvalues and MP reference sample.
  5. Run AMP → empirical AMP-rel-err vs AMP-SE prediction.
- Per codebook (mean across 5 seeds): record ks_mean, mmd_mean, w1_mean, amp_rel_err_mean, empirical_label.
- Across 5 codebook cells: compute Spearman ρ(amp_rel_err, score) for each of {KS, MMD, W1}; compute best-threshold routing accuracy for each.

## Reference distribution

MP reference samples are the empirical eigenvalues of a fresh iid Gaussian (M_ref, N_ref) matrix at the same aspect ratio c = M/N, with N_ref = max(n_samples, 1024). Avoids the 1/x singularity at the lower MP support edge that destroys naive inverse-CDF samplers near c=1.

## HARD PASS (MMD or Wasserstein strictly better than MP-KS by > 5%)

- **ρ_MMD ≥ 0.75 OR ρ_W1 ≥ 0.75** (strictly better than MP-KS ρ ≈ 0.70 by >5%)
- **AND** the winning score's best-threshold routing accuracy **≥ 0.80** (matches or exceeds MP-KS's 4/5 v175 baseline)

## HARD FAIL (MMD/Wasserstein add nothing)

- **ρ_MMD AND ρ_W1 both ≤ 0.70** (no improvement over MP-KS)
- **AND** their best-threshold routing accuracies ≤ MP-KS's

## MIDDLE BAND

- ρ improvement < 5% (marginal; not worth swapping) — Cap 12 stays on MP-KS

## Formula self-tests (12/12 pass)

1. `sample_mp_reference` returns samples in MP support, mean ≈ 1
2. `mmd_rbf` identity (same distribution → small MMD)
3. `mmd_rbf` shift distinction (shifted distribution → larger MMD)
4. `sliced_wasserstein_1d` identity (small W1)
5. `sliced_wasserstein_1d` shift → exact shift magnitude (W1(x, x+2) = 2)
6. `empirical_truth_from_amp_rel` boundary cases
7. `best_routing_accuracy` on perfectly-separable scores → 1.0
8. `best_routing_accuracy` on inseparable scores → < 1.0
9. Compute_verdict PASS (MMD strictly better)
10. Compute_verdict HARD FAIL (alternatives anti-monotone)
11. Compute_verdict MIDDLE BAND (ρ < 0.75 but neither anti-monotone)
12. Compute_verdict INCONCLUSIVE on missing codebooks

## Acceptance for queue submission

- [x] Script includes `sys.stdout.reconfigure` block
- [x] Script includes atomic metrics-write block
- [x] Script includes env-var-driven `HDLAB_EXP_NAME` outdir
- [x] Self-test runs at start of `run_main`
- [x] Pre-run smoke at N=64 / 1 seed / 2 codebooks (iid + SRHT) completed locally; produced valid metrics.json (INCONCLUSIVE via "missing codebooks" branch — expected for smoke scale). MP reference sampler verified: mean=1.0037, support [0, 3.94].
- [x] HARD PASS / HARD FAIL / MIDDLE BAND verbatim in this prereg

## Pause-flag compliance

`data/orchestrator_paused.flag` ABSENT at dispatch time. exp_dev verified flag is not present before writing this prereg.

## Honest framing

This is a META-tool audit, not substrate-physics novelty. PASS gives Strategy a license to swap or augment Cap 12's score in the next revision (MMD or W1 becomes the new pre-test default; MP-KS becomes a fallback). FAIL hardens v175 ✅ by showing MP-KS is at least as good as the alternatives — a defensive falsification of more-sophisticated scores being secretly better.

## ETA note

~2h is dominated by 5 codebooks × 5 seeds × SVD(N=1024) + AMP loop (~300 iter) + 3 score computations (KS is O(N log N), MMD is O(N^2) on the 1024-point eigenvalue arrays, W1 is O(N log N)). Per-cell cost ~50s, total ~21 minutes for the SVD/AMP loop + MMD O(N^2 = 10^6) Gaussian-kernel matrix * 5*5 = 25 evaluations at ~5s each = ~2 min. Total walltime budget includes 2x margin for warm-up + I/O.
