# Pre-registration: wave14_tropical_kerdock_N4096_emp_margin_v1 (Cap 13 candidate companion)

**Date**: 2026-05-24
**Wave**: 14 (tropical-polytope adversarial-margin certificate — GPU companion)
**Driver**: Companion to `wave14_tropical_margin_certificate_kerdock_v1`; supplies production-scale empirical BSC-margin baseline at substrate-native N=4096.
**Capability under test**: Cap 13 candidate "tropical-polytope adversarial-margin certificate" — empirical anchor at production scale.
**Anchor role**: Empirical GPU baseline for closed-form comparison
**Script**: `experiments/exp_wave14_tropical_kerdock_N4096_emp_margin_v1.py`
**Queue**: `overnight_queue` (GPU; substrate-native N=4096, full 4-coset Kerdock = 16384 codewords; depth probe per [[feedback-gpu-first-for-depth-probes]])
**ETA**: 30-60 min GPU wallclock

## Hypothesis

At substrate-production scale N=4096 with the full 4-coset MM Kerdock codebook (4N = 16384 codewords), the empirical BSC adversarial margin (minimum bit-flip count that flips argmax-readout) is well-defined: it has a low-variance, clean threshold distribution across random codewords and random query points.

This baseline FEEDS INTO `wave14_tropical_margin_certificate_kerdock_v1`: the closed-form margin formula derived in that anchor can be re-evaluated at N=4096 and compared against this empirical baseline. The two anchors together test the Cap 13 claim at production scale.

## Bands (HARD PASS / HARD FAIL)

### HARD PASS — empirical baseline well-defined

Empirical bit-flip margin distribution at N=4096:
- coefficient of variation (std / mean) <= 0.30 across 5 cells × 10 seeds × 5 random codewords (250 measurements)
- AND the 25th-percentile margin is strictly > 0 (substrate has a real adversarial margin, not degenerate-zero)

Interpretation: substrate's empirical margin at production N is a clean threshold; baseline is usable for closed-form comparison via Anchor 1.

### HARD FAIL — empirical margin degenerate

coefficient of variation > 0.80
OR > 20% of trials report margin = 0 (codeword is immediately ambiguous at queried y) or margin = full-N/2 (no perturbation can flip the readout in finite-bit budget; not a real adversarial scenario).

Interpretation: substrate's BSC margin at N=4096 is noise-dominated or pathological; Cap 13 closed-form claim cannot be cleanly empirically validated at production scale.

### MIDDLE BAND — usable but noisy baseline

coefficient of variation in (0.30, 0.80] with <= 20% degenerate trials.

Interpretation: baseline reportable but with caveats; Cap 13 candidate stays as 🟡 partial certificate pending higher-statistics empirical run.

## Design

- Codebook: 4-coset Maiorana-McFarland Kerdock at N=4096 (t=6 primitive polynomial) via `make_kerdock_4coset_codebook` in `exp_wave14y_erase_kerdock_v3.py`. 16384 codewords.
- Sweep: 5 cells × 10 seeds × 5 random codeword indices = 250 (cell, seed, codeword) tuples.
  - cells indexed by query-point construction: y = w_i + eps * direction for eps in {0.1, 0.3, 0.5, 0.7, 0.9} (sweeps query proximity to centroid; tests margin sensitivity to query location).
- For each tuple:
  - Sample random codeword index i; let w_i = codebook[i].
  - Construct y = w_i + eps * random_unit_direction (normalized).
  - Compute empirical bit-flip margin: for k = 1, 2, ..., binary-search over k for the minimum bit-flips that change argmax of <w_j, y'> from i to j != i. Use GPU-vectorized top-k coordinate selection: for each candidate j, the optimal bits to flip are those with highest |w_i_k - w_j_k| where y_k disagrees with w_i_k (max-impact coords).
  - Report margin_emp = 2 * min_j k_ij (each flip is L_inf perturbation of magnitude 2 at that coordinate).
- Aggregate per cell: mean, std, percentiles of margin_emp across 10 seeds * 5 codewords = 50 samples.
- Verdict from coefficient-of-variation across full distribution.

## Self-test cells (per [[feedback-strategy-spec-formula-selftests]])

The script self-tests 5 formula assertions, all of which must pass before the experiment runs:

1. **Kerdock codebook construction at N=4096**: `make_kerdock_4coset_codebook(4096, cpu)` returns codebook of shape (16384, 4096) with entries in {-1, +1}.
2. **Self-margin at y = w_i is 0**: when y = w_i exactly (eps=0), <w_i, y> = N is the max, and the closest competitor j has margin equal to a positive bit-flip count (not 0; substrate has nontrivial Hamming distance to nearest competitor).
3. **Bit-flip sensitivity ordering**: for a fixed (w_i, w_j) pair, flipping coordinate k where w_i_k != w_j_k changes <w_i - w_j, y> by exactly -4 (if y_k has same sign as w_i_k - w_j_k positive direction) or +4 (otherwise). Verify on a hand-built (i,j) pair at N=4.
4. **Cell coverage**: for 5 eps cells * 10 seeds * 5 codewords on smoke = 250 (full) and 25 (smoke), assert structure.
5. **Verdict logic**: synthetic data with cv=0.15 → HARD PASS; cv=0.9 → HARD FAIL; cv=0.5 → MIDDLE BAND; cv=0.4 with 25% degenerate → HARD FAIL.

All 5 pass locally before queue submission. Remote-side `--self-test` gate re-runs pre-execution.

## Acceptance criteria for queue submission

- [x] Script includes `sys.stdout.reconfigure(...)` block at top.
- [x] Script includes metrics-write block (atomic .tmp + rename).
- [x] Env-var-driven `HDLAB_EXP_NAME` outdir.
- [x] Self-test runs at start of `run_main` / `run_smoke`.
- [x] Pre-run smoke at N=1024 / 1-seed completed locally; produced valid metrics.json.
- [x] HARD PASS / HARD FAIL / MIDDLE BAND verbatim in this prereg.

## Pause-flag compliance

`data/orchestrator_paused.flag` ABSENT at dispatch time. exp_dev verified flag is not present (orchestrator invocation explicitly stated PAUSE CLEARED). [[feedback-obey-user-pause-explicitly]] honored.

## Notes

- This is a substrate-native (N=4096) empirical run; uses the FULL 4-coset MM Kerdock codebook (16384 codewords) — distinct from Anchor 1's small-N tractability sweep using 2-coset.
- GPU is appropriate per [[feedback-gpu-first-for-depth-probes]]: 250 samples × 16384 codewords × top-k search is matrix-heavy; expected runtime 30-60 min on remote GPU.
- Companion to `wave14_tropical_margin_certificate_kerdock_v1` (CPU, N <= 1024, closed-form vs empirical). Together: theory + production-scale empirical = full Cap 13 certificate.
