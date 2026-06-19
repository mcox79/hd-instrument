# Prereg: wave14_cap11_chi4_early_warning_anchor_v1

Date: 2026-05-24
Queue: overnight_queue (GPU — depth-needing per gpu-first-for-depth-probes feedback)
ETA: 45-60 min wallclock (8 alpha levels x 5 seeds x N=4096; 32 trajectory runs per cell + 5-trajectory permutation null)
Type: ANCHOR (Cap 11 chi_4 early-warning license; Composition C unlock)

## Purpose

Research drill 2026-05-24 (notes/research_cap11_chi4_early_warning_drill_2026-05-24.md) identified chi_4 as the right primary indicator of approach-to-capacity for Kerdock-Hopfield substrate (glassy-substrate algebra; literature SNR 5-10x). The drill also mandated parallel instrumentation of AC(1), Var, and tau_R (zero marginal cost) to inoculate against the seizure-literature methodological-noise risk.

This anchor tests whether chi_4 (and the three complementary indicators) detect approach to the Cap 10 capacity boundary alpha_c BEFORE retrieval-SNR collapses — i.e. whether Cap 11 can be licensed as early-warning observability for Cap 10.

## Substrate + design

- Substrate: Kerdock 4-coset Hebbian W at N=4096 (canonical wave14y_v3 codebook).
- alpha_c hypothesis: 0.14 from generic Hopfield (Amit-Gutfreund-Sompolinsky); substrate-specific recalibration permitted post-hoc if the retrieval knee disagrees.
- alpha grid: {0.014, 0.028, 0.056, 0.084, 0.112, 0.140, 0.168, 0.196} = {0.1, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4} x alpha_c. Ramps from 0.1 -> 1.4 of alpha_c per drill spec.
- 5 seeds.
- Per alpha cell: build Kerdock-Hebbian W, sample 32 perturbed-trajectory runs of T_steps=10, measure 4 indicators + retrieval accuracy on 100 probes.
- Permutation null at chi_4-peak alpha: re-sample codewords (independent draw), recompute chi_4; real-peak must be >= 1.5x the permutation median to pass.

## Indicators (all 4 measured in parallel, per Research mandate)

1. **chi_4** = N_eff * Var_runs(C(t)) where C(t) = (1/N) <s(t), s_target> across runs. Berthier-Biroli-Bouchaud canonical 4-point connected susceptibility.
2. **AC(1)** = lag-1 autocorrelation of the mean-trajectory overlap m(t). Scheffer 2009 / Dakos critical-slowing-down indicator.
3. **Var** = variance of m(t). Dakos et al. CSD indicator.
4. **tau_R** = relaxation time from a small read-perturbation (perturb N//50 bits, count argmax iterations to fixed point). Power-grid damping-ratio analog.

## HARD PASS (chi_4 licensed as Cap 10 early-warning)

- chi_4 SNR (peak / baseline) >= 3.0; baseline = median of lowest-30% alpha cells across seeds.
- AND lead-time K >= 0.05 * alpha_c. K = alpha_at_retrieval_knee - alpha_at_chi4_peak (per-seed and median). Retrieval knee = smallest alpha at which mean overlap drops below 0.5 * plateau.
- AND permutation_null_passed = True (real chi_4 peak >= 1.5x median of 5 permutation re-samples).
- AND >= 3 of 5 seeds satisfy lead-time >= 0.05 * alpha_c.

Verdict: CAP11_CHI4_EARLY_WARNING_LICENSED. Substrate-product claim: "Cap 11 chi_4 predicts approach to Cap 10 capacity boundary at lead-time >= 5% of alpha_c, with peak-to-baseline SNR >= 3." Unlocks Composition C (Cap 12 + Cap 11 + Cap 1 = "adaptive routing under continual operation with predictive observability").

## HARD FAIL (chi_4 dead as early-warning)

- chi_4 SNR < 1.5 OR seeds_with_negative_lead >= 3 (i.e. on >= 3 of 5 seeds, chi_4 spikes AT or AFTER the retrieval knee).

Verdict: CAP11_CHI4_FAIL. Cap 11 chi_4 not predictive; substrate-product claim narrows to "Cap 11 detects retrieval failure post-hoc but does not provide early-warning lead-time."

## MIDDLE BAND

- chi_4 SNR in [1.5, 3), OR
- partial lead-time (some seeds positive, some <= 0; not >= 3 negative-lead seeds), OR
- permutation null failed but SNR >= 3 and lead positive.

Verdict: CAP11_CHI4_MIDDLE_BAND. Triggers combined-indicator anchor v2: report AC(1) + Var + tau_R SNRs and lead-times alongside chi_4. If any complementary indicator hard-passes its own SNR+lead criteria, propose combined-indicator anchor v2 weighting the four indicators. If none do, downgrade Cap 11 to passive monitor (no early-warning license).

Per Research drill's bonus mandate: AC(1), Var, tau_R SNRs are ALWAYS reported alongside chi_4, regardless of verdict. Inter-indicator agreement is itself diagnostic.

## Self-tests (executed before main run)

Verdict self-test (7 cases): PASS, FAIL via SNR, FAIL via 3+ neg-lead seeds, MIDDLE via SNR, MIDDLE via lead, MIDDLE via perm-null, INCONCLUSIVE.

Indicator formula self-tests (per strategy-spec-formula-selftests feedback):
1. chi_4 white-noise: E[chi_4] = n_runs * sigma^2; n_runs=1000, sigma=1 -> ~1000, tolerance (700, 1300).
2. AC(1) white-noise: ~0, tolerance |AC| < 0.1.
3. AC(1) AR(1) rho=0.7: ~0.7, tolerance (0.6, 0.8).
4. Var white-noise sigma=1: ~1, tolerance (0.9, 1.1).
5. tau_R zero-perturbation on identity W: returns >= 1.

All five formula self-tests pass; verdict self-test passes 7/7.

## Smoke (PASS — local CPU, N=1024, 1 seed, 4 alpha cells, ~25s)

```
seed=0 alpha=0.0500 M=51  chi4=0.000  AC1=0.000  Var=0.00000  tau_R=2  retrieval=1.000
seed=0 alpha=0.1000 M=102 chi4=0.002  AC1=0.000  Var=0.00000  tau_R=2  retrieval=0.999
seed=0 alpha=0.1400 M=143 chi4=0.021  AC1=0.058  Var=0.00000  tau_R=3  retrieval=0.997
seed=0 alpha=0.1800 M=184 chi4=0.063  AC1=0.612  Var=0.00001  tau_R=30 retrieval=0.843
VERDICT: CAP11_CHI4_MIDDLE_BAND (smoke; single-seed N=1024 is insufficient for production verdict)
```

Smoke confirms (a) pipeline runs end-to-end, (b) all four indicators compute and rise monotonically with alpha, (c) retrieval knee is detected at alpha=0.18 (> alpha_c=0.14, as expected), (d) AC(1) and tau_R show the classic critical-slowing-down signature near the boundary (AC(1) 0->0.612, tau_R 2->30), (e) metrics.json written, oracle assertion passed.

## Open questions / risks

- **alpha_c value:** 0.14 is the generic Hopfield value (Amit-Gutfreund-Sompolinsky). Kerdock structure may shift the substrate-specific alpha_c. If the production retrieval knee lands at substantially different alpha than 0.14, lead-time fractions need post-hoc recalibration with the empirical alpha_c. The alpha grid (0.014 -> 0.196) covers 0.1x -> 1.4x of nominal alpha_c, which should bracket any reasonable empirical knee.
- **Sharp-transition risk (per drill):** Kerdock structure may suppress crosstalk so thoroughly that chi_4 stays flat until catastrophic collapse, yielding high SNR but zero lead-time. This is exactly what the lead-time gate detects.
- **Permutation null choice:** independent codeword re-sampling at the same M, NOT write-order shuffling, because Kerdock-Hebbian W is order-symmetric (W = T^T T). The independent re-sample tests specificity to a particular sample of codewords vs the general high-load regime; an order-shuffle would be a no-op.
- **Sensitivity to T_steps=10, n_runs=32:** glass literature uses 100s of trajectories; we use 32 here to keep wall-time in budget. If MIDDLE BAND returns due to noisy chi_4, v2 would scale n_runs to 64-128.

## Self-tests pass log

```
$ python experiments/exp_wave14_cap11_chi4_early_warning_anchor_v1.py --self-test
verdict self-test passed (7/7 cases)
indicator formula self-tests passed (chi4 + AC(1) + Var + tau_R)
```
