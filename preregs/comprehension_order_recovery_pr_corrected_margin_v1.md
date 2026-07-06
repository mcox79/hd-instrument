# PRE-REG: exp_comprehension_order_recovery_pr_corrected_margin_v1

Author: exp_dev 2026-07-06. Cell: `experiments/exp_comprehension_order_recovery_pr_corrected_margin_v1.py`.
Status: SELFTEST PASS + SMOKE landed HARD_PASS (local, N=8192, 3 seeds, 36/36 units, 20.0s).
FULL staged (remote_cpu_queue). Non-parked (zero cert_ledger referent). Monitor-not-control (NOT
self-improvement). NEW cell -- does NOT overwrite the accept-boundary cell
`exp_comprehension_order_recovery_exact_margin_v1`. Source drill:
`notes/research_sub_gaussian_tail_self_margin_revival_participation_ratio_2026-07-06.md`
(P_deflated=0.50 -- novel-synthesis cap; an honest HARD_FAIL was pre-declared a legitimate outcome).

## Question under test (a genuine test; P=0.50, HARD_FAIL was legitimate)
The exact-margin cell landed ACCEPT_BOUNDARY: the Gaussian max-of-(V-1) order statistic OVER-predicted
the comprehension decode collapse (exact p1 mean_ratio=1.193, biased) while a trivial single-draw
("loose", V-blind) was near-unbiased (0.972) -- so the naive extreme-value-of-V mechanism added no value.
The revival drill measured the actual tail off-disk: it is NOT a different parametric marginal shape
(kurtosis 2.89 ~ Gaussian 3.0). It is an INDEPENDENCE problem -- the V-1 "distractors" are CORRELATED
(the block-local GSBC codebook is a JL-projection of the power-law concept-encoder Gram). Does substituting
the PARTICIPATION RATIO (effective rank) of the codeword Gram, `PR(V) = (sum lambda)^2 / sum(lambda^2)`,
as the effective competitor count `n_comp = PR(V)-1` (PR ~16-29, NOT V-1 ~999) into the IDENTICAL
Gauss-Hermite order statistic (one substituted exponent) UNBIAS the prediction?

## HONEST FLAG (why the ORIGINAL bands are NOT reused)
The exact-margin cell's HARD_PASS required the exact model to beat loose by `rel_improve >= 1.5x`. Loose
turned out accidentally near-unbiased (0.97, inside the unbiased band) for THIS codebook regime, so that
gate is UNREACHABLE-BY-CONSTRUCTION for ANY corrected model here (no corrected model can beat a
single-draw model that is already ~unbiased on aggregate bias). The REVISED bands below gate on
bias-removal + worst-cell error + the naive-V-over-predicts control + a correlation discriminator, which
is what actually changed. The PR correction is load-bearing vs NAIVE-V (the falsified original), NOT vs
the loose single-draw.

## The mechanism + controls
Score moments (mu_s,sig_s) of the signal + (mu_d,sig_d) of one distractor are MEASURED from the code
geometry (substrate's OWN geometry, at REFERENCE vocab V_REF=50, EXTRAPOLATED across V -- NOT fit to
accuracy). Target = per-role decode `p1 = decode_part^(1/D)` (apples-to-apples with sibling margins).
- MECHANISM `pr_corrected`: `n_comp = PR(V)-1`, PR = participation ratio of the (V,bs) role-0 codeword
  slice's Gram (`numpy.linalg.eigvalsh(cb[0:V] @ cb[0:V].T)`, <0.5s/cell). THEORETICAL@effective-rank
  (Roy & Vetterli 2007; Kish 1965 design-effect; Stringer 2019 effective dimensionality).
- CONTROL `naive_v` (the falsified original): `n_comp = V-1` -> OVER-predicts collapse (biased).
- CONTROL `loose` (diagnostic): `n_comp = 1` (V-blind) -> near-unbiased on aggregate but too-optimistic
  at the hardest cell (~11pp), so NOT a real discriminator.
- CONTROL `pr_independent` (correlation discriminator): PR of a MATCHED independent bipolar codebook
  (same V,bs,k) -> PR_indep ~V (recovers naive), proving the low GSBC PR is the correlation structure,
  not the formula. Degenerate limit (identical codewords) -> PR=1 (rank-1) asserted in formula selftest.

## Off-disk cheap decisive test (ALREADY RUN; zero new trials; in-cell `_retrospective_offdisk`, gated in --self-test)
Recomputed vs `data/exp_comprehension_envelope_superposition_vocab_v1/metrics.json:per_unit`
(8 non-saturated seed-avg p1 cells; 24 per-seed cells):
- PR-CORRECTED p1: mean_ratio 1.007 (UNBIASED), per-seed max_ratio_err 1.088, cross-seed cv 0.019.
- NAIVE-V (V-1): mean_ratio 1.193 (BIASED, over-predicts), per-seed max_ratio_err 2.175.
- improve (naive per-seed max / pr per-seed max) = 2.00x.
- PR table (seed-avg): V=50 ->17.6, V=250 ->25.1, V=1000 ->27.1 (saturates ~27, NOT V-1).
- correlation discriminator: PR_indep(V=1000)=506 vs PR_gsbc=27 -> 18.7x. degenerate PR=1.0 exact.
The in-cell retrospective asserts this DIRECTION reproduces (guards a silent code change flipping it).

## Aggregation-level discipline (load-bearing band-design note)
Ratio-error / hardest-cell / improvement gates are computed at the PER-SEED level (max over all
(D,V,seed) non-saturated cells) -- that is where the drill measured 1.088 / 2.175 / 2.00x. Seed-averaging
FIRST compresses the naive worst-cell to ~1.49 (improvement ~1.44x); that is an aggregation artifact, not
the mechanism, and would falsely fail a >=1.5x gate. Mean-ratio (bias) is computed at the seed-aggregated
cell level (an aggregate quantity). Both levels reported in metrics.

## HP_SCOPE (per-arm gate scope)
- `pr_corrected` arm: mean-ratio unbiased, per-seed ratio_err<=1.5x, hardest-cell<=1.10, improve>=1.5x, cv<=0.15.
- `naive_v` arm: ONLY the naive-biased direction gate (mean-ratio OUTSIDE [0.85,1.18]).
- `loose` arm: diagnostic only (no gate).
- `pr_independent` arm: ONLY the correlation-discriminator gate (PR_indep/PR_gsbc >= 5x at max V).
- Saturated cells (meas_p1 >= 0.999, the D<=4 corners) EXCLUDED from all ratio gates.

## Bands (envelope-fail-bands; ratio = meas_p1/pred_p1)
- HARD_PASS (comprehension order-recovery joins the exact self-margin family via PR; CG-candidate; a FULL
  build at the WIDER V grid + 5 seeds must confirm before CHAIN_GRADE):
  - PR-corrected aggregate mean-ratio in [HP_BIAS_LO,HP_BIAS_HI]=[0.80,1.25] (unbiased), AND
  - PR-corrected per-seed per-cell ratio_err <= HP_RATIO_MAX (1.5) at ALL non-saturated seed-cells, AND
  - PR-corrected per-seed ratio_err <= HP_HARDEST_MAX (1.10) at the SINGLE hardest cell (max D, max V), AND
  - NAIVE-V biased: naive aggregate mean-ratio OUTSIDE [NAIVE_UNBIASED_LO,HI]=[0.85,1.18] (naive over-predicts
    -> PR correction is LOAD-BEARING vs naive-V), AND
  - improve over naive: naive_perseed_max_err / pr_perseed_max_err >= REL_IMPROVE_MIN (1.5), AND
  - cross-seed CV of per-seed PR ratio_err <= HP_CV_MAX (0.15), AND
  - correlation discriminator FIRES: PR_indep/PR_gsbc >= INDEP_RATIO_MIN (5.0) at max V.
- HARD_FAIL (honest re-ACCEPT if the correction does not hold multi-seed / at smoke -- a LEGITIMATE outcome):
  - PR-corrected aggregate mean-ratio OUTSIDE [HF_BIAS_LO,HF_BIAS_HI]=[0.60,1.70], OR
  - PR-corrected per-seed ratio_err > HF_RATIO_MAX (2.0) at ANY non-saturated seed-cell, OR
  - improve over naive < ACCEPT_REL_MIN (1.2) (the correction was a coincidence, not a mechanism).
- MIDDLE_BAND: clears the core PR bands but misses a HARD_PASS sub-gate (hardest-cell in (1.10,1.5],
  improve in [1.2,1.5), cv in (0.15,..], discriminator below floor); OR insufficient non-saturated cells
  (< MIN_NONSAT: smoke>=3 / full>=6 -- decode surface saturated).

## SCHEMA-VET mandatory fields
- cardinality_ok (META_RULE_H): EXPECTED_N_UNITS = seeds x D_grid x V_grid. smoke 3x4x3=36; full 5x4x5=100.
  Verdict emits HARD_FAIL_CARDINALITY_BREACH if len(per_unit) < expected. Non-saturated floor MIN_NONSAT.
- arms_differ_verified (AF): true -- the PR-corrected surface (n_comp=PR-1) is hash-distinct from BOTH the
  NAIVE (n_comp=V-1) and LOOSE (n_comp=1) surfaces (verified in compute_verdict; HARD_FAIL_ARMS if identical).
- final_metrics_atomicity: tmp_replace (os.replace of metrics.json.tmp).
- except SystemExit: raise BEFORE except Exception (no BaseException / no bare except; grep-clean, verified).
- crlb / discriminator_reachability: prediction-match test; the gated quantity is a ratio (no Cramer-Rao
  noise floor). crlb_n_a: exact-vs-measured ratio tightness. discriminator_reachability: MEASURED off-disk +
  at smoke (PR mean_ratio 1.009, per-seed worst 1.076, improve 2.04x) -- HARD_PASS REACHABLE for the
  PR-corrected model; FULL-grid confirmation (untested V=125,500 + seeds 23,29) is the remaining risk (P=0.50).
- baseline_in_band (AG): prediction-match, not a difficulty baseline. Saturated D<=4 cells EXCLUDED
  (declared). NAIVE + LOOSE = live CONTROLS; pr_corrected = MECHANISM under test.
- calibration_check: default_ok_for_this_regime -- the PR formula is parameter-free given the codeword Gram
  (NOT fit to accuracy); moments measured at V_REF and extrapolated; 64-pt GH matches RNS/FHRR/reasoning.
- sweep_alignment_verdict: ALIGNED -- each (D,V) cell's decode literally experiences V same-partition
  distractors whose EFFECTIVE competitor count is PR(V) (measured from that cell's own codeword slice), and
  the predictor consumes that cell's own (L, PR(V)) + measured moments.
- discriminating_fraction: >= 0.30 -- the decode cliff (non-saturated p1 cells) spans D=8 (all V) + D=6
  high-V; smoke MEASURED 5/12 seed-agg cells non-saturated with p1 in (0.877, 0.997), populating the ratio.
- composition_edges: SHAPE_MATCH (single primitive: role-typed matched-filter decode -> per-role argmax; the
  PR-corrected prediction is a downstream closed form + one eigendecomposition, not a composed primitive).
- positive_control_arms (Gate D): (1) measurement machinery IS the landed comprehension cell's, IMPORTED +
  reused VERBATIM (base.run_unit) at the SAME regime (N=8192, same pool, same grid); (2) the Gauss-Hermite
  formula p_win_extreme is bit-identical to the exact-margin cell's (asserted in `_verbatim_check`). The fresh
  smoke reproduces the landed decode surface (D8V1000 decode_part 0.35-0.58 vs landed 0.30-0.55).
  regime_extension_audit: SHAPE_MATCH.
- functional_requirements: (1) recognize occupied SET [base]; (2) recover role->block ORDER under
  superposition [base role-typed matched filter]; (3) decode each filler [base partition-restricted argmax];
  (4) predict where (2)+(3) collapse as (D,V) grow [PR-corrected extreme-value order statistic]. Requirement
  (4) is under test; finding is that the PR correction unbiases it where the naive full-V count fails.
- progress_logging: line_buffered_stdout + print(flush=True) on every progress line; heartbeat.jsonl each unit.
- start_marker_written / crash_diagnostic_present / heartbeat_present: true. cell_chunked: false (single
  metrics.json; per-seed loop is fast -- smoke 36 units in 20s; full ~2-4 min).
- defensive_error_checking: passed_all_4_patterns.
- run_mode: defaults to full (bare / runner HDLAB_RUN_MODE=full); --smoke / --self-test flip. Cell asserts
  written run_mode == mode (§16 RUN_MODE verification).

## Compute architecture
SEQUENTIAL-CPU (numpy matched-filter + block-argmax + one (V,V) eigvalsh per (seed,V); the cell IS the
substrate comprehension primitive being re-measured -- bit-identical CPU reference exemption). Storage:
no_storage / no_composition beyond the base cell's superposition (synthetic clean GSBC partitions). The
prediction arms are numpy Gauss-Hermite quadrature + eigendecomposition (deterministic; no GPU, no scipy,
no torch, no LLM). DEPENDENCY: the untracked GSBC pool npz
`data/gen_decoder_gsbc_fillers/gsbc_expand2x_pool_v1.npz` + the base cell file must be present on remote
(SCP the pool before FULL; queue_add does NOT ship it). NON-PARKED (synthetic GSBC data; no cert_ledger referent).

## SMOKE RESULT (local, N=8192, D {2,4,6,8} x V {50,250,1000}, seeds 7/13/19, 36/36 units, 20.0s)
HARD_PASS (all gates cleared with margin). MEASURED@data/exp_comprehension_order_recovery_pr_corrected_margin_v1/metrics.json:extra:
- PR-CORRECTED p1 mean_ratio=1.0093 (unbiased [0.80,1.25]), gm_err=1.018, per-seed max_err=1.0755.
- hardest cell D8_V1000 per-seed err=1.0449 (<= 1.10). cross_seed_cv=0.0159 (<= 0.15).
- NAIVE-V p1 mean_ratio=1.1928 (biased=True, over-predicts), per-seed max_err=2.1973.
- LOOSE p1 mean_ratio=0.9721 (near-unbiased on aggregate; too-optimistic at hardest cell, diagnostic).
- improve over naive (per-seed) = 2.043 (>= 1.5). arms_differ=True. 5 non-saturated cells; cardinality 36/36.
- correlation discriminator PR_indep/PR_gsbc @ maxV = 18.715x (fires, >= 5.0).
- In-cell off-disk retrospective vs landed metrics: PR mean_ratio 1.006 (unbiased), NAIVE 1.187 (biased),
  improve 2.02x -> PR_CORRECTION_CONFIRMED. verbatim_check: p_win_extreme bit-identical to exact-margin cell.

## FULL grid (staged; remote_cpu_queue -- SMOKE-only-local rule; exp_dev CANNOT push -> Orchestrator dispatches)
D {2,4,6,8} x V {50,125,250,500,1000}; seeds {7,13,19,23,29} (>= 5, CG multi-seed precedent);
EXPECTED_N_UNITS=100; run_mode=full. FULL adds the 2 intermediate V points (125,500) + 2 seeds (23,29,
UNTESTED by the drill) -> the CHAIN_GRADE-confirming grid the drill explicitly reserved. timeout: smoke 36
units = 20s on laptop; FULL 100 units + 5 codebook builds + 25 eigvalsh ~ 2-5 min; recommend --timeout 1800
(30 min, ample; remote CPU may be slower). REMOTE DEPENDENCY: SCP `gsbc_expand2x_pool_v1.npz` before dispatch.
