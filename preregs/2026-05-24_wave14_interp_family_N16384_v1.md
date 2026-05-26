# Pre-registration: wave14_interp_family_N16384_v1 (Cap 12 ✅ E2 STRESS)

**Date**: 2026-05-24
**Wave**: 14 (cross-family AMP-error predictor N-scaling)
**Driver**: orchestrator silent_idle emergency refill post-v175 promotion
**Capability under stress**: Cap 12 (AMP-vs-VAMP inference routing infrastructure) at ✅
**Anchor role**: E2 — N-scaling envelope expansion (customer-scale regime)
**Script**: `experiments/exp_wave14_interp_family_N16384_v1.py`
**Queue**: `overnight_queue` (GPU; depth-needing N-scaling sweep per [[feedback-gpu-first-for-depth-probes]])
**ETA**: 60-120 min

## Hypothesis

After v175 ✅ promotion the AMP-error predictor sum|delta kappa_n| produced Spearman rho >= 0.700 across {iid-Gauss → SRHT, iid-Gauss → Hadamard, iid-Gauss → RM, iid-Gauss → Kerdock} interpolation families at N=1024. The customer-facing claim is "kappa_n divergence sum is a META-DIAGNOSTIC predictor of AMP-error across codebook families." Customer codebooks at production scale are N >> 1024 (typically N ∈ {4096, 16384, 65536}). Is the predictor still strong at N=16384, or was it an N=1024 finite-N artifact?

Concretely: for each family in {Kerdock, SRHT, Hadamard}, for each N in {1024, 4096, 16384}, run the 5-alpha × 5-seed sweep used in v174/v175. Compute Spearman rho(amp_rel_err_mean, bbmd_distance_mean) across the alpha grid. Track max VAMP rel-err. Then check the N=16384 row against the HARD bands below.

## Bands (HARD PASS / HARD FAIL / MIDDLE BAND)

Per [[feedback-envelope-expansion-fail-bands]], all three bands pre-registered verbatim before queue submission.

### HARD PASS — Cap 12 ✅ survives E2 STRESS

rho >= 0.50 at N=16384 for ALL 3 families (Kerdock, SRHT, Hadamard)
AND max VAMP rel-err < 0.20 across N=16384 cells.

Interpretation: AMP-error predictor survives N-scaling to customer-scale regimes; kappa_n divergence is a true customer-scale meta-tool, not a finite-N artifact.

### HARD FAIL — Cap 12 ✅ reverts to 🟢 with N-bound annotation

rho < 0.30 on ANY of {Kerdock, SRHT, Hadamard} at N=16384.

Interpretation: kappa_n divergence sum was an N=1024 finite-N effect on at least one family; predictor does not generalize to customer-scale. Cap 12 reverts to 🟢 with annotation "predictor holds up to ~N=4096; N=16384 fails on family X."

### MIDDLE BAND — Cap 12 ✅ stays with N-scaling annotation

rho in [0.30, 0.50) at N=16384 on one family (partial monotonicity retained but weakened),
OR max VAMP rel-err in [0.10, 0.20) at N=16384.

Interpretation: Cap 12 ✅ stands but cap_map annotates "predictor weakens at customer-scale on family X." Strategy may dispatch a follow-up cell-level diagnostic.

## Design

- Families: {kerdock, srht, hadamard}. (Per dispatch note: Paley already PERFECT_ISOMETRY kappa_n=0; RM is at-threshold borderline. The three families chosen are the load-bearing N-scaling stress.)
- N_grid: {1024, 4096, 16384}.
- M = N (square; M/N = 1.0).
- alpha_interp grid: {0.0, 0.25, 0.5, 0.75, 1.0} (matches v174/v175).
- 5 seeds per (family, N, alpha) cell.
- Total cell count: 3 families × 3 N values × 5 alpha = 45 cells, each with 5 seeds = 225 (family, N, alpha, seed) tuples.
- W_alpha = ((1-alpha) * G + alpha * W_struct) / sqrt(N), G iid N(0,1), W_struct un-normalized.
- Per (family, N, alpha, seed): SVD on W; eigenvalues = s^2; moments 1..6 → free cumulants kappa_1..kappa_6 via Voiculescu inversion; bbmd_distance = sum_{n=2..6} |kappa_n - M/N|; AMP-SE pred (scalar Bayati-Montanari); empirical AMP via run_amp loop; VAMP-SE closed (using singular spectrum); empirical VAMP via run_vamp loop; amp_rel_err, vamp_rel_err.
- Per (family, N, alpha) cell: mean across 5 seeds of bbmd_distance, amp_rel_err, vamp_rel_err.
- Per (family, N): Spearman rho(amp_rel_err_mean, bbmd_distance_mean) across 5 alpha cells; max VAMP rel-err across 5 alpha cells.
- Verdict from rho_per_family_N at N=16384 against the three bands above.

## Self-test cells (per [[feedback-strategy-spec-formula-selftests]])

The script self-tests 9 formula assertions, all of which must pass before the experiment runs:

1. bbmd_distance on Marchenko-Pastur reference (kappa_n = c) → 0.
2. bbmd_distance on deviating cumulants (kappa_n = c + 0.1n for n=1..5) → 1.5.
3. spearmanr on monotone increasing pair → 1.0.
4. compute_rho_per_family_N buckets correctly by (family, N) and computes rho.
5. compute_verdict on synthetic PASS data (all 3 families rho >= 0.50 at N=16384, VAMP < 0.20) → HARD PASS.
6. compute_verdict on synthetic FAIL data (one family rho < 0.30 at N=16384) → HARD FAIL.
7. compute_verdict on synthetic MIDDLE data (one family rho in [0.30, 0.50)) → INCONCLUSIVE.
8. compute_verdict with missing N=16384 cells → INCONCLUSIVE.
9. compute_verdict with VAMP blowup at one family → INCONCLUSIVE (not FAIL, since rho still >= 0.30).

All 9 pass locally before queue submission. Remote-side `--self-test` gate will re-run pre-execution.

## Kerdock t=7 N=16384 dependency

Per [[feedback-poll-closed-session-logs]] and dispatch note: the Kerdock builder (`make_kerdock_4coset_codebook` in `exp_wave14y_erase_kerdock_v3.py`) requires t=7 primitive polynomial for N=16384. PRIMITIVE_POLY entry for t=7 was patched in earlier this session (verified via `notes/exp_dev_to_queue_emergency_refill_batch_3_2026-05-23.md` line 54 — "Kerdock t=7 PATCH: applied locally to exp_wave14y_erase_kerdock_v3.py (PRIMITIVE_POLY entry for t=7 = 0b10000011), and SCP'd to remote BEFORE ship. Verified period-127 cycle and codebook construction at N=16384"). Local verification at N=1024 (t=5) and N=4096 (t=6) confirmed during smoke; N=16384 (t=7) deferred to remote runner.

## Acceptance criteria for queue submission

- [x] Script includes `sys.stdout.reconfigure(...)` block at top.
- [x] Script includes metrics-write block (atomic .tmp + rename).
- [x] Env-var-driven `HDLAB_EXP_NAME` outdir.
- [x] Self-test runs at start of `run_main` / `run_smoke`.
- [x] Pre-run smoke at N=64 / 1-seed / 2-family (srht + hadamard; kerdock at N=64 unsupported due to PRIMITIVE_POLY t=5 minimum) completed locally; produced valid metrics.json.
- [x] HARD PASS / HARD FAIL / MIDDLE BAND verbatim in this prereg.

## Pause-flag compliance

`data/orchestrator_paused.flag` ABSENT at dispatch time. exp_dev verified flag is not present before writing this prereg.

## Notes

- This is a CPU-feasible but compute-heavy N-scaling sweep (225 AMP + 225 VAMP runs at varying N). Routed to `overnight_queue` per [[feedback-gpu-first-for-depth-probes]] (depth probe; N >= 4096 matrix work; multi-cell sweep). Runtime estimate 60-120 min on GPU.
- The 3 families chosen are the load-bearing N-scaling stress: Kerdock (substrate-canonical), SRHT (Dudeja-Lu-Kini AMP-universal), Hadamard (deterministic, no randomization). Paley deferred (already PERFECT_ISOMETRY kappa_n=0 at v174 so adding a 5th family that's a degenerate boundary case would not contribute discriminative power; deferred for research thought per dispatch note).
- Failure at N=16384 on a family that PASSed at N=1024 is informative: identifies which family is finite-N artifact.
