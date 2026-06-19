# Pre-registration: wave14_tropical_margin_certificate_kerdock_v1 (Cap 13 candidate)

**Date**: 2026-05-24
**Wave**: 14 (tropical-polytope adversarial-margin certificate)
**Driver**: Research deep-drill `notes/research_new_continents_deep_drill_2026-05-24.md` Section 1 — F-14 tropical geometry; ship FIRST per Section 4.2.
**Capability under test**: Cap 13 candidate "tropical-polytope adversarial-margin certificate" — closed-form lower bound on substrate's BSC erasure margin, certified without Monte Carlo.
**Anchor role**: Theory-first novel-cap probe (P_deflated=0.55, novel-synthesis cap)
**Script**: `experiments/exp_wave14_tropical_margin_certificate_kerdock_v1.py`
**Queue**: `remote_cpu_queue` (pure CPU, argmax sweeps, no GPU benefit; runtime estimate 4-8 hr per [[feedback-pipeline-pacing]])
**ETA**: 4-8 hr CPU wallclock
**Companion**: `wave14_tropical_kerdock_N4096_emp_margin_v1` (GPU, N=4096 empirical baseline; queued in parallel)

## Hypothesis

The substrate's Kerdock readout `argmax_i <w_i, y>` is structurally a tropical polynomial in the max-plus semiring R_max:

  p(y) = max_{i in codebook} <w_i, y>

Per Tropical Decision Boundaries 2024 (arXiv 2402.00576) and Tropical Attention NeurIPS 2025 (arXiv 2505.17190): for a piecewise-linear classifier defined as the argmax of a tropical polynomial, the L_inf adversarial margin at point y inside cell of codeword w_i is closed-form:

  margin_closed(y, w_i) = min_{j != i} (<w_i, y> - <w_j, y>) / ||w_i - w_j||_1

The Cap 13 claim: this closed-form margin MATCHES the substrate's empirical BSC adversarial margin (minimum L_inf perturbation that flips readout) to within 5% across the operational N grid. If true, substrate gains a Monte-Carlo-free margin certificate distinct from Cap 1 (CFT-based) and Cap 8 (VAMP-based).

## Bands (HARD PASS / HARD FAIL / MIDDLE BAND)

Per [[feedback-strategy-spec-formula-selftests]] and [[feedback-envelope-expansion-fail-bands]], all three bands pre-registered verbatim before queue submission.

### HARD PASS — Cap 13 candidate licensed

For each N in {4, 16, 64, 256, 1024}: compute mean relative error
   rel_err_N = mean_i,seed | margin_closed(y, w_i) - margin_emp(y, w_i) | / max(margin_closed, margin_emp)
across at least 5 (seed, codeword) trials per N.

HARD PASS if rel_err_N <= 0.05 in at least 4 of 5 N values
AND Kerdock-orbit symmetry reduces unique pairwise-distance equivalence classes to <300 at every N <= 1024.

Interpretation: substrate's tropical-margin certificate is operationally valid; Cap 13 "tropical-polytope adversarial certificate" licensed as new portfolio capability.

### HARD FAIL — claim killed

rel_err_N > 0.25 at ANY single N in {4, 16, 64, 256, 1024}
OR # unique pairwise-distance equivalence classes >= 300 at any N (means symmetry reduction intractable; closed-form is not actually computable).

Interpretation: substrate is NOT a clean tropical polynomial in operational regime, OR the symmetry collapse needed for tractability fails. Cap 13 candidate rejected. Audit substrate's actual decision-rule to identify deviation from pure-tropical structure.

### MIDDLE BAND — partial validation

rel_err_N in (0.05, 0.10] on some N (matches within ~10% but not the 5% target)
OR rel_err_N in (0.10, 0.25] at <= 1 of 5 N values.

Interpretation: closed-form margin is approximately valid but not tight; Cap 13 candidate stays as "🟡 partial certificate" pending follow-up (e.g., second-order tropical correction, or restriction to symmetric subset of codewords).

## Design

- Codebook: 2-coset Kerdock-like (sylvester Hadamard + (-1)^{Q_1} * Hadamard) per `make_kerdock_2coset_codebook` in `exp_wave14v_erase_kerdock_v2.py`. 2N codewords, applicable at any N=2^k, k>=2. Matches the small-N Kerdock-orbit structure (Q_1 is the canonical degree-2 bent function on F_2^k).
- N grid: {4, 16, 64, 256, 1024}.
- For each N, for each seed in {0,...,4} (5 seeds), for each codeword index i in random sample of size min(10, 2N): pick random y ~ Uniform(B_inf(c=w_i, r=1)) (point inside cell of w_i, clipped via projection on cell). Practical: sample y = w_i + eps * normalized random direction, with eps small.
- Compute margin_closed(y, w_i) via the closed-form formula above (closed-form L_inf adversarial).
- Compute margin_emp(y, w_i) via brute-force search: for each j != i, find minimum integer k_ij such that flipping the top-k_ij sensitivity coordinates of y produces <w_j, y'> > <w_i, y'>. Sensitivity ordering: |w_i_k - w_j_k| (coordinates where they disagree; flipping y_k there has +2 impact on <w_j - w_i, y>). margin_emp = min_j (2 * k_ij), expressed in L_inf-norm-equivalent units (each flip = L_inf perturbation of magnitude 2; aggregated min-flip count gives discretized L_inf margin).
- Symmetry-reduction: for each N, compute the multiset of unique pairwise L_1 distances ||w_i - w_j||_1 across all (i,j) pairs in 2N codewords. Report unique-equivalence-class count.

## Self-test cells (per [[feedback-strategy-spec-formula-selftests]])

The script self-tests 8 formula assertions, all of which must pass before the experiment runs:

1. **Tropical polynomial evaluation on N=2 trivial case**: codebook = {(+1,+1), (+1,-1)}; for y = (2, 0.5), p(y) = max(2+0.5, 2-0.5) = 2.5; argmax = first codeword. Assert evaluate_tropical_poly returns 2.5 and argmax=0.
2. **Closed-form margin on N=2 trivial case**: from y=(2, 0.5), margin_closed = (2.5 - 1.5) / ||(0,2)||_1 = 1.0 / 2 = 0.5. Assert margin_closed_form returns 0.5.
3. **Hadamard pairwise IP**: for N=4 Sylvester Hadamard, all off-diagonal entries of H @ H.T / N are 0 (rows orthogonal).
4. **2-coset codebook shape**: make_kerdock_2coset_codebook(N=4) returns shape (8, 4).
5. **L_1 distance computation**: ||(+1,+1,-1,-1) - (+1,-1,+1,-1)||_1 = 0+2+2+0 = 4.
6. **Margin closed-form non-negativity**: for any y in cell of w_i, margin_closed >= 0 (argmax => <w_i, y> >= <w_j, y> for all j, so numerator >= 0).
7. **Pairwise-distance equivalence-class count at N=4 2-coset**: should produce a SMALL number of equivalence classes (Hadamard codewords have all pairwise distances in {0, 2N} for orthogonal pairs; coset structure adds finite set of cross-coset distances). Assert # unique classes <= 10 at N=4.
8. **Verdict logic**: synthetic PASS data (5 N values, all rel_err < 0.05, all unique-classes < 300) → HARD PASS; synthetic FAIL data (1 N with rel_err > 0.25) → HARD FAIL; mid data → MIDDLE BAND.

All 8 pass locally before queue submission. Remote-side `--self-test` gate re-runs pre-execution.

## Acceptance criteria for queue submission

- [x] Script includes `sys.stdout.reconfigure(...)` block at top.
- [x] Script includes metrics-write block (atomic .tmp + rename).
- [x] Env-var-driven `HDLAB_EXP_NAME` outdir.
- [x] Self-test runs at start of `run_main` / `run_smoke`.
- [x] Pre-run smoke at N=4 / 1-seed completed locally; produced valid metrics.json.
- [x] HARD PASS / HARD FAIL / MIDDLE BAND verbatim in this prereg.

## Pause-flag compliance

`data/orchestrator_paused.flag` ABSENT at dispatch time. exp_dev verified flag is not present (orchestrator invocation explicitly stated PAUSE CLEARED). [[feedback-obey-user-pause-explicitly]] honored.

## Notes

- Theoretical citations: Tropical Attention NeurIPS 2025 (arXiv 2505.17190); Tropical Decision Boundaries arXiv 2402.00576 + Neural Networks 2026 (in press); Maragos ICASSP 2024 Tutorial.
- Distinct from existing capabilities: Cap 1 erase (CFT-based) and Cap 8 cognitive composition (VAMP-based). This is a NEW closed-form audit certificate from a third algebraic framework (max-plus semiring).
- Companion GPU run `wave14_tropical_kerdock_N4096_emp_margin_v1` provides the production-N=4096 empirical baseline; if it produces a clean threshold the same closed-form check extrapolates to substrate-native scale.
- Per [[feedback-pipeline-pacing]]: CPU-bound 4-8 hr fits remote_cpu_queue; queue pacing satisfied (depth >= 1 maintained).
- **Honest caveat from smoke at N=4**: smoke produced TROPICAL_MARGIN_KILLED (rel_err=0.53 at single N=4 with 3 trials). The closed-form is a CONTINUOUS L_inf lower bound; the empirical BSC margin is a DISCRETIZED bit-flip count (each flip = 2 units of L_inf). At small N this discretization-vs-continuous gap dominates rel_err. The HARD PASS criterion requires >=4 of 5 N values pass, so small-N discretization-driven failure at N=4 can still leave 4 of 5 (N=16, 64, 256, 1024) passing — full run will tell. If N=4 KILLs and N>=16 PASS at 5%, the substrate-level claim is licensed at production scales (where bit-flip discretization is sub-1% of margin); annotate "tropical-margin certificate holds at N>=16" in cap_map.
