# Prereg: wave14_kappa_gold_full_e3_v1

**Date**: 2026-05-24
**Vertex**: KAPPA_GOLD_FULL_E3_PASS / KILLED / INCONCLUSIVE
**Capability target**: Cap 12 ✅ — **E3 5th-family stress gate** (Gold sequences, GF(2^10)-trace family)
**Queue**: `remote_cpu_queue` (~30-45 min CPU)
**Script**: `experiments/exp_wave14_kappa_gold_full_e3_v1.py`

## Background

Cap 12 (AMP-vs-VAMP routing) was promoted to ✅ at v175 on the 5-codebook basis {iid_gauss, SRHT, Hadamard, RM(1,m), Kerdock}. E1 (noisy substrate) and E2 (N-scaling) ship/run. E3 adds a 5TH-family stress test using GOLD sequences — a separate algebraic family that shares Kerdock's GF(2^m)-trace machinery but uses distinct combinatorics (3-valued cross-correlation, no 4-coset of Reed-Muller).

The Gold quickprobe earlier this session returned BBMD_CANDIDATE (κ_n diverges from MP, but spectrum stays bulk-bounded — see `data/exp_wave14_kappa_gold_quickprobe_v1/metrics.json` or the routing note that introduced Gold).

## Hypothesis

The Cap 12 predictor — Spearman ρ between AMP rel-err and sum |Δκ_n| across an iid-Gauss → structured interpolation family — generalizes to the Gold-sequence family at the relaxed 5th-family threshold (ρ ≥ 0.50, max VAMP < 0.15). The thresholds are RELAXED vs Hadamard/SRHT primary-gate (ρ ≥ 0.70) because:
1. E3 is a 5th-family hardening, not the primary gate.
2. Gold uses GF(2^10) trace algebra distinct from Sylvester (SRHT/Hadamard) or 4-coset RM (Kerdock); some predictor degradation is expected.
3. Gold quickprobe at α=1 (pure-Gold) already showed BBMD_CANDIDATE (κ_n nontrivial → the predictor has signal to work with).

## Design

- m=10, N_eff=1023 (Gold family natural length), padded to N=1024 by appending a single zero column. The padded column contributes nothing to the spectrum (creates one extra zero eigenvalue); we account for this in BBMD by computing κ_n on the full N=1024 SVD.
- α grid {0.0, 0.25, 0.5, 0.75, 1.0}; 5 α cells.
- **10 seeds per cell** (matches v175 base resolution; Research drill spec).
- W_α = ((1-α) · G + α · W_gold_unnorm) / sqrt(N), where G is iid N(0,1) and W_gold_unnorm is M rows row-subsampled from the (N_eff+2, N_eff) Gold family (entries in {+1,-1}, plus a zero-padding column).
- Per (α, seed): SVD; κ profile k_2..k_6 (free-cumulant inversion); BBMD distance d = Σ_{n=2..6} |κ_n - M/N|; AMP-SE prediction; empirical AMP; VAMP-SE closed-form; empirical VAMP; AMP/VAMP rel-errs.
- Cell mean = mean across 10 seeds.
- Final: Spearman ρ(amp_rel_err_mean, bbmd_distance_mean) across 5 cells; max(vamp_rel_err_mean) across 5 cells.

## HARD PASS (E3 5th-family gate satisfied)

- **Spearman ρ ≥ 0.50 across 5 α cells**
- **AND max VAMP rel-err < 0.15**

## HARD FAIL (E3 breaks the predictor)

- **Spearman ρ < 0.30**
- **OR max VAMP rel-err > 0.30**

## MIDDLE BAND

- **ρ ∈ [0.30, 0.50) OR VAMP rel-err ∈ [0.15, 0.30)** — predictor weakens but doesn't collapse; Cap 12 ✅ holds with Gold-family middle-band annotation.

## Formula self-tests (9/9 pass)

1. `bbmd_distance` on MP-reference (κ = c) → 0
2. `bbmd_distance` on monotonically-deviating κ → exact sum
3. `spearmanr` on monotone pair → 1.0
4. Compute_verdict PASS (monotone amp_rel, low max VAMP)
5. Compute_verdict KILLED via low rho (anti-monotone amp_rel)
6. Compute_verdict KILLED via VAMP blowup
7. Compute_verdict MIDDLE BAND (rho ~ 0.4)
8. Compute_verdict MIDDLE BAND (VAMP ∈ [0.15, 0.30))
9. Too-few cells INCONCLUSIVE

## Acceptance for queue submission

- [x] Script includes `sys.stdout.reconfigure` block
- [x] Script includes atomic metrics-write block
- [x] Script includes env-var-driven `HDLAB_EXP_NAME` outdir
- [x] Self-test runs at start of `run_main`
- [x] Pre-run smoke at N=64 / 1 seed / m=6 / α ∈ {0, 0.5, 1.0} completed locally; produced valid metrics.json (KILLED via small-N VAMP blowup — expected for N=64 sub-capacity, matches v174/v175 smoke pattern)
- [x] HARD PASS / HARD FAIL / MIDDLE BAND verbatim in this prereg

## Pause-flag compliance

`data/orchestrator_paused.flag` ABSENT at dispatch time. exp_dev verified flag is not present before writing this prereg.

## Honest framing

PASS hardens Cap 12 ✅ with a 5th independent algebraic family beyond the 4 already validated (iid_gauss, SRHT, Hadamard, RM(1,m), Kerdock). FAIL marks Gold-family codebooks as outside the AMP-vs-VAMP routing envelope; Cap 12 retains its 5-codebook ✅ status with a Gold-family-excluded annotation in cap_map.
