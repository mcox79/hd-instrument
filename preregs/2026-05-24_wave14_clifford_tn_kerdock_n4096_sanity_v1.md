# Pre-registration: wave14_clifford_tn_kerdock_n4096_sanity_v1 (Cap 13 candidate F-4 / Sub-anchor B)

**Date**: 2026-05-24
**Wave**: 14 (Clifford-enhanced tensor networks — F-4 deep drill Section 3; GPU sanity companion to Sub-anchor A)
**Driver**: Research deep-drill `notes/research_new_continents_deep_drill_2026-05-24.md` Section 3 (F-4 — GPU sanity component)
**Capability under test**: Cap 13 candidate "stabilizer-rank / magic monotone audit" at substrate-native scale.
**Anchor role**: GPU sanity at substrate-native N=4096 production scale.
**Script**: `experiments/exp_wave14_clifford_tn_kerdock_n4096_sanity_v1.py`
**Queue**: `overnight_queue` (GPU, eigvalsh on 16384x16384 Gram for full 4-coset MM Kerdock; CPU fallback available but slow)
**ETA**: 30-60 min GPU wallclock (5 seeds * 5 codeword indices = 25 measurements; each ~1-2 min for the Gram eigvalsh)
**Companion**: `wave14_clifford_tn_kerdock_magic_bound_v1` (CPU theory anchor at N in {16, 64, 256, 1024}; queued in parallel)

## Hypothesis

At substrate-native N=4096 with the FULL 4-coset MM Kerdock codebook (M=16384 codewords), the Clifford-TN bond-dim-1 closed-form prediction is:

  - **Spectral measure** of (1/N) A A^T: 2-point delta at {0, M/N} = {0, 4}.
    Multiplicities: 0 with mult (M-N)=3N=12288; 4 with mult N=4096.
  - **Power sums**: p_k = (N/M) * (M/N)^k = 4^(k-1) for k>=1.
  - **Schur-Weyl mass_n**: closed-form via Frobenius character formula on p_k = 4^(k-1).

The substrate-native check: at production scale (N=4096), the empirical Gram spectrum should match this 2-point measure within the Welch-bound cross-coset noise floor; the Schur-Weyl mass_n should match the closed-form prediction within 1%.

## Bands (HARD PASS / HARD FAIL / MIDDLE BAND)

### HARD PASS — Cap 13 candidate licensed at production scale

`rel_err_max < 0.01` between empirical and Clifford-TN closed-form mass_n at all (seed, codeword, n) tuples (1% agreement)
AND `eig_max_dev_2pt < 0.20` (each eigenvalue is within 0.20 of the nearest closed-form value in {0, M/N=4}; 5% of M/N)
AND `BW_magic_monotone_max < 1e-10` (Barnes-Wall norm exactly 0).

Interpretation: substrate-native Cap 8 derivation reduces from O(N^3) to O(N log N) at production scale; Cap 13 "Clifford-TN bond-dim-1 audit" licensed at N=4096.

### HARD FAIL — claim killed

`rel_err_max > 0.10` at ANY (seed, codeword, n) (>10% divergence)
OR `eig_max_dev_2pt > 2.0` (eigenvalue dispersion exceeds the 2-point prediction by >2 units; closed-form structure fails)
OR `BW_magic_monotone_max > 0.01` (nonzero magic content; Kerdock is NOT a pure stabilizer state at production scale).

Interpretation: substrate's 4-coset MM Kerdock at N=4096 has non-Clifford structure; closed-form O(N log N) derivation kill. Audit the Maiorana-McFarland construction for magic-injection mechanism.

### MIDDLE BAND — partial validation

`rel_err_max in (0.01, 0.05]` at some (seed, codeword, n)
OR `eig_max_dev_2pt in (0.20, 0.80]`
OR `BW_magic_monotone in (1e-10, 0.01]` at some codewords.

Interpretation: partial Clifford-orbit at production scale; the bond-dim-1 closed form is a useful approximation but not exact. Cap 13 stays 🔬 with annotation about the cross-coset Welch-bound noise floor or small magic content.

## Design

- Codebook: 4-coset MM Kerdock per `make_kerdock_4coset_codebook` in `exp_wave14y_erase_kerdock_v3.py`. M = 4N codewords, N = 2^(2t) for t in {5, 6, 7}.
- N = 4096 (t=6, substrate-native).
- Seeds: {17, 23, 31, 41, 53} (5 seeds).
- Codeword indices: {0, 100, 500, 1000, 2000} (5 codewords spanning all 4 cosets).
- n orders: {2, 3, 4, 5}.
- Total measurements: 5 seeds × 5 codewords × 4 n orders = 100 (5×5=25 codebook builds; for each, 4 Schur-mass computations).

For each (N, seed): build codebook; for each codeword: compute Barnes-Wall magic monotone; for each n: compute v169 empirical Schur-Weyl mass via GPU-accelerated eigvalsh on (1/N) A A^T (16384x16384 matrix); compute Clifford-TN 4-coset closed-form mass from p_k = 4^(k-1); compute rel_err.

## Self-test cells (5)

1. **4-coset Kerdock codebook entries +/-1 at N=1024** with shape (4096, 1024).
2. **Gram spectrum near 1.0 at N=1024**: mean(eig) ~ 1.0 (verifies the closed-form mean = M/N * (N/M) = 1.0 holds empirically).
3. **BW magic monotone = 0 for +/-1 vectors** at N in {64, 256, 1024}.
4. **Clifford-TN 4-coset closed-form consistency**: at M/N=4, mass_n(n=2) = 1.0, mass_n(n=3) = 0.6818 (verified analytically from p_k=4^(k-1)).
5. **Verdict logic** on synthetic HARD_PASS / MIDDLE_BAND / HARD_FAIL inputs.

All 5 PASS locally.

## Acceptance criteria for queue submission

- [x] Script includes `sys.stdout.reconfigure(...)` block at top.
- [x] Script includes metrics-write block (atomic .tmp + rename).
- [x] Env-var-driven `HDLAB_EXP_NAME` outdir.
- [x] Self-test runs at start of `run_main`.
- [x] Pre-run smoke at N=1024 / 1 seed / 1 codeword completed locally; produced valid metrics.json.
- [x] HARD PASS / HARD FAIL / MIDDLE BAND verbatim in this prereg.

## Smoke result (local)

N=1024 / 1 seed / 1 codeword (CPU): rel_err = 0.0, eig_dev_from_2pt = 1.0e-4 (eigenvalues are exactly at {0, 4} up to numerical noise), BW magic = 0.0, VERDICT = HARD_PASS_CLIFFORD_TN_N4096_LICENSED. Self-tests 5/5 PASS. The 4-coset Gram spectrum at N=1024 is verified to be a clean 2-point delta at {0, M/N=4} with closed-form Schur masses matching v169 exactly.

## Pause-flag compliance

`data/orchestrator_paused.flag` ABSENT at dispatch time. [[feedback-obey-user-pause-explicitly]] honored.

## Notes / honest read

- **Theoretical citations**: Lami-Haug-De Nardis PRX Quantum 6.010345 (2025); Kalra-Sinha arXiv 2503.04101 (2025).
- **Production-scale check**: this anchor is the substrate-native (N=4096, full 4-coset MM Kerdock) sanity for the bond-dim-1 closed form derived in Sub-anchor A. If both anchors HARD_PASS, the Clifford-TN closed-form O(N log N) reduction of Cap 8 is verified end-to-end from small-N theory to production scale.
- **Risk**: the 4-coset MM Kerdock has cross-coset Welch-bound inner products of magnitude 1/sqrt(N) per pair, which at N=4096 gives 1/64 = 1.6% noise floor. The closed-form 2-point prediction may have ~1-2% eigenvalue dispersion AT EACH eigenvalue, which is well within the MIDDLE_BAND threshold (0.80 in lambda units of M/N=4) but worth tracking.
- **Resource use**: addresses user-flagged "GPU is idle" — this anchor explicitly targets GPU for the production-scale eigvalsh on the 16384x16384 Gram. Smoke ran on CPU (sub-second at N=1024); full run at N=4096 needs GPU memory budget ~1 GB for the float32 Gram.
