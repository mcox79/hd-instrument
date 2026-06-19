# Pre-registration: wave14_interp_family_N8192_v1 (Cap 12 ✅ E2 follow-up after N16384 timeout)

**Date**: 2026-05-24
**Wave**: 14 (cross-family AMP-error predictor N-scaling)
**Driver**: substrate-honest follow-up after wave14_interp_family_N16384_v1 timed out (3h budget exceeded; no number produced)
**Capability under stress**: Cap 12 (AMP-vs-VAMP inference routing infrastructure) at ✅
**Anchor role**: E2 — N-scaling envelope expansion at the largest N tractable in budget
**Script**: `experiments/exp_wave14_interp_family_N8192_v1.py`
**Queue**: `overnight_queue` (GPU; depth-needing N-scaling sweep per [[feedback-gpu-first-for-depth-probes]])
**ETA**: 60-120 min

## Why N=8192 (not N=16384)

The original E2 N-stress was specified at N=16384 to hit the customer-scale regime. The first attempt (`wave14_interp_family_N16384_v1`) timed out at the 3h wall budget on the overnight runner; no verdict was produced. Per dispatch instruction: **"substrate-honest follow-up — better to test at the largest N we can complete in budget than to leave the N-envelope UNRESOLVED."** N=8192 is the next-down power of 2 from 16384 and reduces the dominant cost (SVD at N=16384 scales as O(N^3) ≈ 4× cheaper than N=16384, plus AMP/VAMP iter cost shrinks).

## Kerdock structural absence at N=8192

The 4-coset Kerdock builder requires `n_log2(N) % 2 == 0` (it uses GF(2^t) with t = n_log2/2). For N=8192, n_log2=13 is odd, so Kerdock is **structurally unbuildable at this N**. The script detects this and skips Kerdock@N=8192 (logged explicitly). The verdict logic correspondingly requires ≥2 of {SRHT, Hadamard} present at N=8192, not 3.

Kerdock at N ∈ {1024, 4096} IS evaluated in this run (rows in the rho_per_family_N table) as the N-scaling anchor for the Kerdock family. The Kerdock customer-regime claim is therefore tested at N=4096 only (one N step above v174's N=1024).

## Hypothesis

After v175 ✅ promotion the AMP-error predictor sum|delta kappa_n| produced Spearman rho >= 0.700 across {iid-Gauss → SRHT, iid-Gauss → Hadamard, iid-Gauss → RM, iid-Gauss → Kerdock} interpolation families at N=1024. Does the predictor hold at N=8192 for SRHT and Hadamard (the non-Kerdock families)?

## Bands (HARD PASS / HARD FAIL / MIDDLE BAND)

Per [[feedback-envelope-expansion-fail-bands]], all three bands pre-registered verbatim before queue submission.

### HARD PASS — Cap 12 ✅ survives E2 STRESS at N=8192

rho >= 0.50 at N=8192 for BOTH present families (SRHT AND Hadamard)
AND max VAMP rel-err < 0.20 across N=8192 cells.

Interpretation: AMP-error predictor survives N-scaling to N=8192 (just one step below the original customer-scale target N=16384); kappa_n divergence is a customer-scale meta-tool on at least 2 of 3 families. Cap 12 ✅ holds with annotation "predictor verified to N=8192 on SRHT/Hadamard; Kerdock verified to N=4096."

### HARD FAIL — Cap 12 ✅ reverts to 🟢 with N-bound annotation

rho < 0.30 on EITHER SRHT or Hadamard at N=8192.

Interpretation: kappa_n divergence sum was an N=1024 finite-N effect on at least one non-Kerdock family; predictor does not generalize to N=8192. Cap 12 reverts to 🟢 with annotation "predictor holds up to ~N=4096; N=8192 fails on family X."

### MIDDLE BAND — Cap 12 ✅ stays with N-scaling annotation

rho in [0.30, 0.50) at N=8192 on one of the present families,
OR max VAMP rel-err in [0.20, 0.30) at N=8192,
OR Kerdock structurally absent and only ONE of {SRHT, Hadamard} present.

Interpretation: Cap 12 ✅ stands but cap_map annotates "predictor weakens at N=8192 on family X."

### TIMEOUT (NOT a FAIL)

If the runner exceeds the timeout budget below before producing metrics.json, the verdict is TIMEOUT (informational; same status as the N16384 attempt). The N-envelope remains UNRESOLVED at N=8192; Cap 12 ✅ stays with verified-to-N=4096 annotation. Strategy may dispatch a further-reduced N=6144 (or stick at N=4096) follow-up.

## COMPUTE BUDGET

- **Expected runtime**: 60-120 min on overnight_queue GPU (RTX-class).
- **Dominant cost**: SVD on W of shape (M, N) = (8192, 8192) at 5 seeds × 5 alpha × 2 families (SRHT + Hadamard at N=8192) = 50 SVDs; plus the N=1024 and N=4096 rows for all 3 families = 75 more SVDs; total 125 SVDs at varying N.
- **Wall-time check**: SVD at N=8192 on RTX-class GPU is ~30s/call → 50 × 30s ≈ 25 min for the N=8192 row alone; plus N=1024/4096 rows ≈ 15 min; plus AMP+VAMP loops (n_iter=300 across all 125 cells) ≈ 30-60 min.
- **Hard timeout to set on queue**: 9000s (150 min) — gives ~30 min headroom beyond the upper estimate.
- **If exceeded**: treat as TIMEOUT, NOT as HARD FAIL. The N-envelope claim is unresolved; substrate-honest annotation in cap_map is "Cap 12 predictor verified to N=4096 (Kerdock) and to N=8192 only if E2 completed within budget."

## Design

- Families: {kerdock, srht, hadamard}.
- N_grid: {1024, 4096, 8192}. Note: Kerdock is automatically SKIPPED at N=8192 (n_log2=13 odd) — logged explicitly; verdict logic compensates.
- M = N (square; M/N = 1.0).
- alpha_interp grid: {0.0, 0.25, 0.5, 0.75, 1.0} (matches v174/v175).
- 5 seeds per (family, N, alpha) cell.
- Total cells executed: 2 × 5 alpha × 5 seeds (SRHT+Hadamard at N=8192) + 3 × 5 × 5 × 2 (all 3 families at N=1024, N=4096) = 50 + 150 = 200 (family, N, alpha, seed) tuples. (Kerdock@N=8192 = 25 tuples skipped.)
- W_alpha = ((1-alpha) * G + alpha * W_struct) / sqrt(N), G iid N(0,1), W_struct un-normalized.
- Per (family, N, alpha, seed): SVD on W; eigenvalues = s^2; moments 1..6 → free cumulants κ_1..κ_6 via Voiculescu inversion; bbmd_distance = sum_{n=2..6} |κ_n - M/N|; AMP-SE pred; empirical AMP via run_amp; VAMP-SE closed (singular spectrum); empirical VAMP via run_vamp; amp_rel_err, vamp_rel_err.
- Per (family, N, alpha) cell: mean across 5 seeds of bbmd_distance, amp_rel_err, vamp_rel_err.
- Per (family, N): Spearman rho(amp_rel_err_mean, bbmd_distance_mean) across 5 alpha cells; max VAMP rel-err.
- Verdict from rho_per_family_N at N=8192 against the bands above.

## Self-test cells (per [[feedback-strategy-spec-formula-selftests]])

9 formula assertions, all of which must pass before the experiment runs:

1. bbmd_distance on Marchenko-Pastur reference (κ_n = c) → 0.
2. bbmd_distance on deviating cumulants (κ_n = c + 0.1n for n=1..5) → 1.5.
3. spearmanr on monotone increasing pair → 1.0.
4. compute_rho_per_family_N buckets correctly by (family, N) and computes rho.
5. compute_verdict on synthetic PASS data (SRHT + Hadamard at N=8192 both rho >= 0.50, VAMP < 0.20) → HARD PASS.
6. compute_verdict on synthetic FAIL data (Hadamard@N=8192 rho < 0.30) → HARD FAIL.
7. compute_verdict on synthetic MIDDLE data (Hadamard@N=8192 rho in [0.30, 0.50)) → INCONCLUSIVE.
8. compute_verdict with missing N=8192 cells → INCONCLUSIVE.
9. compute_verdict with VAMP blowup on SRHT@N=8192 → INCONCLUSIVE (not FAIL).

All 9 pass locally before queue submission. Remote-side `--self-test` gate will re-run pre-execution.

## Acceptance criteria for queue submission

- [x] Script includes `sys.stdout.reconfigure(...)` block at top.
- [x] Script includes metrics-write block (atomic .tmp + rename).
- [x] Env-var-driven `HDLAB_EXP_NAME` outdir.
- [x] Self-test runs at start of `run_main` / `run_smoke`.
- [x] Pre-run smoke at N=64 / 1-seed / 2-family (SRHT + Hadamard; Kerdock at N=64 unsupported) completed locally; produced valid metrics.json with expected INCONCLUSIVE (small-N).
- [x] HARD PASS / HARD FAIL / MIDDLE BAND / TIMEOUT bands verbatim above.
- [x] COMPUTE BUDGET section explicit (expected 60-120 min; queue timeout 9000s; TIMEOUT outcome treated as informational not FAIL).

## Pause-flag compliance

`data/orchestrator_paused.flag` ABSENT at dispatch time. exp_dev verified flag is not present before writing this prereg.

## Notes

- This is the substrate-honest E2 follow-up: better to verify the predictor at N=8192 (one step below the customer-target N=16384) than to leave the N-envelope unresolved after the N16384 timeout.
- The Kerdock@N=8192 structural skip means this run does NOT close out Kerdock@N>4096. A separate Kerdock-specific N=16384 run (compute-budgeted appropriately for Kerdock-only, which can take t=7 primitive poly) would close that gap if needed.
- TIMEOUT outcome is informational, not a HARD FAIL — Cap 12 ✅ retains its existing N=4096 annotation until a within-budget run resolves the N=8192 row.
