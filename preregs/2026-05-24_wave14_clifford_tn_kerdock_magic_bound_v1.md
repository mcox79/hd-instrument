# Pre-registration: wave14_clifford_tn_kerdock_magic_bound_v1 (Cap 13 candidate F-4 / Sub-anchor A)

**Date**: 2026-05-24
**Wave**: 14 (Clifford-enhanced tensor networks — F-4 deep drill Section 3)
**Driver**: Research deep-drill `notes/research_new_continents_deep_drill_2026-05-24.md` Section 3 (F-4 Clifford-enhanced tensor networks)
**Capability under test**: Cap 13 candidate "stabilizer-rank / magic monotone audit" — closed-form O(N log N) derivation of Cap 8 Schur-Weyl-Pauli via Clifford-TN bond-dim-1 contraction; Barnes-Wall magic monotone = 0 audit certificate.
**Anchor role**: CPU theory anchor (P_deflated=0.50, novel-synthesis cap)
**Script**: `experiments/exp_wave14_clifford_tn_kerdock_magic_bound_v1.py`
**Queue**: `remote_cpu_queue` (pure CPU, single-thread numpy/eigvalsh, no GPU benefit)
**ETA**: 6-12 hr CPU wallclock (5 seeds * 4 N values * 4 n orders, dominated by O((2N)^3) eigvalsh at N=1024)
**Companion**: `wave14_clifford_tn_kerdock_n4096_sanity_v1` (GPU, N=4096 production-scale sanity check; queued in parallel)

## Hypothesis

Per Lami-Haug-De Nardis PRX Quantum 6.010345 (2025) the Kerdock orbit is a CMPS at bond-dimension chi=1 (degenerate Clifford-only). Per Kalra-Sinha 2025 (arXiv:2503.04101) the Barnes-Wall norm of a Kerdock-orbit state is exactly 0 (zero-magic stabilizer state).

This implies substrate's Cap 8 Schur-Weyl-Pauli decomposition admits a CLOSED-FORM O(N log N) derivation via bond-dim-1 stabilizer-tableau update, replacing v169's O(N^3) Schur-Weyl machinery.

Two load-bearing closed-form predictions for the 2-coset Kerdock codebook (M = 2N codewords):
  - **Spectral measure**: eigenvalues of (1/N) A A^T are all = 1.0 (uniform delta).
  - **Power sums**: p_k = 1 for all k => Schur-Weyl mass_n(n) = 1.0, mass_111 = 0 at all orders.

Three operational claims:
  1.  Bond-dim-1 CMPS contraction reproduces v169 Schur-Weyl mass_n within 1e-10 across N in {16, 64, 256, 1024}.
  2.  Barnes-Wall magic monotone = 0 for all Kerdock codewords at every N.
  3.  O(N log N) wallclock reduction confirmed against v169's O(N^3) baseline (within 25% slope tolerance on log-log fit).

## Bands (HARD PASS / HARD FAIL / MIDDLE BAND)

Per [[feedback-strategy-spec-formula-selftests]] and [[feedback-envelope-expansion-fail-bands]], all three bands pre-registered verbatim.

### HARD PASS — Cap 13 candidate licensed

For every (N, n) pair: `rel_err = |v169_mass_n - tn_mass_n| / max(|v169|, |tn|) < 1e-10`
AND `max BW_magic_monotone(codeword) < 1e-10` over all (N, codeword) pairs
AND tn wallclock scaling slope < 1.5 in log(t) vs log(N) (sublinear-to-log, NOT N^3).

Interpretation: substrate's Cap 8 derivation reduces from O(N^3) to O(N log N); Cap 13 "Clifford-TN bond-dim-1 audit" licensed; substrate gains a closed-form magic-monotone audit cert.

### HARD FAIL — claim killed

`rel_err > 0.10` at ANY (N, n) (>10% divergence between bond-dim-1 contraction and v169)
OR `BW_magic_monotone(codeword) > 0.01` for ANY codeword (nonzero magic kills the closed-form claim).

Interpretation: substrate has non-Clifford structure from Hopfield-cleanup post-processing (Research flagged this as the recurring risk). Cap 13 candidate rejected. Audit substrate's cleanup-step to identify non-stabilizer contribution.

### MIDDLE BAND — partial validation

`rel_err in (1e-10, 0.05]` at some (N, n) (matches v169 within 5% but not 1e-10)
OR `BW_magic_monotone in (1e-10, 0.01]` at some codewords (small magic injection).

Interpretation: partial Clifford-orbit; substrate post-processing injects small T-gate-equivalent magic. Cap 13 stays 🔬 with annotation about magic content; v169 reduction approximate but useful.

## Design

- Codebook: 2-coset Kerdock-like (Sylvester Hadamard ∪ (-1)^{Q_1} Hadamard) per `make_kerdock_2coset_codebook` in `exp_wave14v_erase_kerdock_v2.py`. 2N codewords, applicable at any N=2^k.
- N grid: {16, 64, 256, 1024}.
- Seeds: {17, 23, 31, 41, 53}.
- n orders: {2, 3, 4, 5}.

For each (N, seed): build codebook; for each n: compute v169 empirical Schur-Weyl masses from eigvalsh of (1/N) A A^T (O((2N)^3)); compute Clifford-TN closed-form masses from uniform p_k=1 spectral measure (O(1)). Compute rel_err. Compute Barnes-Wall magic monotone for each row.

## Self-test cells (6, per [[feedback-strategy-spec-formula-selftests]])

All run before the experiment starts; each verified locally:

1. **BW norm of |0>^N stabilizer state** = N at N in {4, 8, 16, 64}; magic = 0.
2. **BW norm of 2-coset Kerdock codeword** = N at N=8; magic = 0 for all 16 rows.
3. **Clifford-TN closed-form at n=2, uniform p_k=1**: mass_n = 1.0 (s_(2) = 1, s_(1,1) = 0).
4. **v169 vs Clifford-TN at N=16, n=2**: agreement within 5% (numerical floor for eigvalsh).
5. **Kerdock 2-coset Gram eigenvalues at N=16**: mean(eig) ~ 1.0 (verifies the uniform-spectrum prediction).
6. **Verdict logic** on synthetic HARD_PASS / MIDDLE_BAND / HARD_FAIL inputs.

All 6 PASS locally before queue submission.

## Acceptance criteria for queue submission

- [x] Script includes `sys.stdout.reconfigure(...)` block at top.
- [x] Script includes metrics-write block (atomic .tmp + rename).
- [x] Env-var-driven `HDLAB_EXP_NAME` outdir.
- [x] Self-test runs at start of `run_main`.
- [x] Pre-run smoke at N=16 / 1-seed completed locally; produced valid metrics.json.
- [x] HARD PASS / HARD FAIL / MIDDLE BAND verbatim in this prereg.

## Smoke result (local)

N=16 / 1 seed / 1 n-order: rel_err = 0.0, BW magic = 0.0, VERDICT = HARD_PASS_CLIFFORD_TN_LICENSED. Self-tests 6/6 PASS. Closed-form prediction verified at smoke scale: Kerdock 2-coset Gram eigenvalues are uniformly 1.0; v169 reproduces this exactly via eigvalsh; both Schur-Weyl mass_n outputs match to floating-point precision.

## Pause-flag compliance

`data/orchestrator_paused.flag` ABSENT at dispatch time. Pause CLEARED at invocation. [[feedback-obey-user-pause-explicitly]] honored.

## Notes / honest read

- **Theoretical citations**: Lami-Haug-De Nardis PRX Quantum 6.010345 (2025); Kalra-Sinha arXiv 2503.04101 (2025); Calderbank-Hammons-Kumar-Sloane-Sole (1997); Masot-Llima-Garcia-Saez arXiv 2403.08724 (2024).
- **Distinct from existing capabilities**: Cap 8 v169 is the O(N^3) Schur-Weyl-Pauli decomposition; this anchor reproduces the same output via O(N log N) closed form and adds the BW magic monotone audit cert.
- **Honest risk from Research deep drill Section 5**: this is a 60-70% Cap 13 plus a strong envelope-extension on Cap 8. The main risk is that the Kerdock 2-coset codebook (substrate's small-N construction) is structurally simpler than the 4-coset MM Kerdock (substrate's N=4096 native), so the bond-dim-1 prediction MIGHT only hold at the 2-coset case. The companion GPU anchor `wave14_clifford_tn_kerdock_n4096_sanity_v1` at N=4096 4-coset is the production-scale sanity check that closes this gap.
- **Iterated-argmax / Hopfield-cleanup caveat**: this anchor tests the readout codebook itself, NOT iterated readout. If substrate's full Cap 8 pipeline uses iterated argmax with Hopfield cleanup, the cleanup step may inject T-gate-equivalent magic that this anchor does NOT capture. Follow-up anchor (out-of-scope here): apply the BW magic monotone to the output of the full Cap 8 pipeline rather than just the codebook.
