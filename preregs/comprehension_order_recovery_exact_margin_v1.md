# PRE-REG: exp_comprehension_order_recovery_exact_margin_v1

Author: exp_dev 2026-07-06. Cell: `experiments/exp_comprehension_order_recovery_exact_margin_v1.py`.
Status: SELFTEST PASS + SMOKE landed HARD_FAIL/ACCEPT_BOUNDARY (local, N=8192, 3 seeds, 36/36 units).
FULL staged (remote_cpu_queue). Non-parked (zero cert_ledger referent). Monitor-not-control (NOT
self-improvement). Frontier map: `notes/research_capability_self_margin_frontier_map_2026-07-06.md`
(row 5, TOP buildable pick, P_deflated=0.40 -- NOT certain; an honest accept-boundary was pre-declared
a legitimate outcome).

## Question under test (a genuine test, NOT a foregone HARD_PASS)
Does the substrate predict its OWN comprehension order-recovery collapse boundary (the decode cliff
at D=8 x V in the landed comprehension-envelope cell) in closed form, via the SAME 64-pt Gauss-Hermite
extreme-value order statistic that CG'd RNS decode margin, FHRR bundle capacity, and reasoning depth?
Per the frontier map's P=0.40, the honest a-priori was uncertain -- and the decisive zero-new-trials
off-disk pre-check (below) landed on the NEGATIVE side. This cell formalizes + independently re-measures
that result as a first-class artifact.

## The target (what actually collapses)
MEASURED@data/exp_comprehension_envelope_superposition_vocab_v1/metrics.json:per_unit --
`order_content_perrole` stays >= 0.93 (barely cliffs); the real order-recovery COLLAPSE is in
`decode_part` / `superposition_survival`, which fall from ~1.0 (D<=6) to 0.30-0.87 at D=8 as V grows.
Per-role decode `p1 = decode_part^(1/D)` is the FUNDAMENTAL per-role order statistic (the deep cliff is
its D-fold product). Prediction is gated on `p1` (apples-to-apples with the sibling per-hop/per-slot
margins); `decode_part = p1^D` is reported as the compounding-amplification diagnostic.

## Extends / reuses
- Measurement machinery reused VERBATIM by IMPORT of `exp_comprehension_envelope_superposition_vocab_v1`
  (`base.run_unit`, `base._build_cbmax`, `base._active_cb`) at the SAME regime (N=8192, same GSBC pool,
  same D x V grid) -> Gate D positive-control-at-test-regime, no invocation/regime drift.
- Order-statistic template: `exp_rns_subblock_margin_exact_prefactor_v2` (HARD_PASS) +
  `exp_fhrr_bundle_capacity_exact_margin_v1` (HARD_PASS) + `exp_reasoning_depth_exact_order_statistic_self_margin_v1`
  (smoke HARD_PASS) -- 64-pt numpy Gauss-Hermite, no scipy.

## The two models
Per role r, decode at its (true) block: the true filler self-correlates at score ~k; the V-1
same-partition distractors compete; the L-1 co-superposed OTHER-partition fillers add noise. Score
moments (mu_s,sig_s) of the signal + (mu_d,sig_d) of one distractor are MEASURED from the code geometry
(the substrate's OWN geometry, at a REFERENCE vocab V_REF=50, then EXTRAPOLATED across V -- NOT fit to
the accuracy surface).
- EXACT (the CG'd extreme-value order statistic): `p1_exact(L,V) = E_{s~N(mu_s,sig_s)}[ Phi((s-mu_d)/sig_d)^(V-1) ]`
  (64-pt GH). THEORETICAL@order-statistic (Hajek ECE361 L8 / Proakis Ch.4; David & Nagaraja max-of-n CDF Phi(x)^n).
- LOOSE (retained control): `p1_loose(L,V) = E_s[ Phi((s-mu_d)/sig_d)^1 ]` -- signal vs ONE typical
  distractor, V-INDEPENDENT (ignores the extreme-value-of-V amplification).

## Off-disk cheap decisive test (ALREADY RUN; zero new trials; in-cell `_retrospective_offdisk`, gated in --self-test)
Recomputed vs `data/exp_comprehension_envelope_superposition_vocab_v1/metrics.json:per_unit` (8 non-saturated p1 cells):
- EXACT p1: mean_ratio 1.19, gm_ratio_err 1.18, max_ratio_err 1.47  (BIASED -- OVER-predicts collapse)
- LOOSE p1: mean_ratio 0.97, gm_ratio_err 1.03  (CLOSER, but V-blind)
- rel_improve = loose_gm / exact_gm = 0.87 (< 1.0 -> exact NOT tighter than loose)
- decode_part (p1^D) exact ratio-err: gm 3.5x, MAX ~22x  (D-fold compounding of the p1 over-prediction)
DIRECTION: the exact extreme-value order statistic OVER-predicts the comprehension decode cliff and
does NOT beat a trivial single-draw model. MECHANISM: sparse block-local GSBC distractor scores have a
LIGHT (sub-Gaussian) upper tail (measured signal margin (mu_s-mu_d)/sig_d ~ 3.5 at D=8; a Gaussian
max-of-1000 sits at ~3.24 -> Gaussian model predicts p1 ~ 0.62 vs MEASURED p1 = 0.91), so the Gaussian
order statistic over-counts the extreme value. Convergent with the encoder power-law accept-boundary
(GSBC-heterogeneity). The in-cell retrospective asserts this DIRECTION reproduces (guards against a
silent code change flipping it).

## HP_SCOPE (per-arm gate scope)
- EXACT arm: the ratio-error gates (ratio_err<=1.5x, mean-ratio unbiased, rel_improve>=1.5, cv<=0.15).
- LOOSE arm: ONLY the bias-direction gate (is loose biased?); never inherits the exact ratio gates.
- Saturated cells (meas_p1 >= 0.999, the D<=4 self-correlation corners) EXCLUDED from all ratio gates,
  exactly as RNS/FHRR exclude their saturated corners.

## Bands (envelope-fail-bands; aggregate over NON-SATURATED cells; ratio = meas_p1/pred_p1)
- HARD_PASS (H CONFIRMED -- comprehension joins the exact self-margin family, CG-candidate):
  - exact per-cell ratio_err <= HP_RATIO_MAX (1.5) at ALL non-saturated cells, AND
  - exact aggregate mean-ratio in [HP_BIAS_LO, HP_BIAS_HI] = [0.80, 1.25] (unbiased), AND
  - exact TIGHTER than loose: rel_improve (loose_gm/exact_gm) >= REL_IMPROVE_MIN (1.5), AND
  - loose biased (loose mean-ratio OUTSIDE [LOOSE_UNBIASED_LO,HI]=[0.85,1.18]), AND
  - cross-seed CV of per-seed exact ratio_err <= HP_CV_MAX (0.15).
- HARD_FAIL / ACCEPT_BOUNDARY (H REFUTED -- the off-disk-PREDICTED outcome; a LEGITIMATE,
  mechanistically-interpretable negative, reported as verdict HARD_FAIL with verdict_msg tagged
  ACCEPT_BOUNDARY + the mechanism string so downstream reads a scientific boundary, not a crash):
  - exact NOT tighter than loose: rel_improve < ACCEPT_REL_MAX (1.0) -- the extreme-value order
    statistic adds no value over a trivial single-draw model, OR
  - exact aggregate mean-ratio OUTSIDE [HF_BIAS_LO, HF_BIAS_HI] = [0.60, 1.70] (exact biased), OR
  - exact per-cell ratio_err > HF_RATIO_MAX (2.0) at ANY non-saturated cell.
- MIDDLE_BAND: exact tightens vs loose (1.0 <= rel_improve < 1.5) but misses a HARD_PASS sub-gate; OR
  insufficient non-saturated cells (< MIN_NONSAT: smoke>=3 / full>=6 -- decode surface saturated).

## SCHEMA-VET mandatory fields
- cardinality_ok (META_RULE_H): EXPECTED_N_UNITS = seeds x D_grid x V_grid. smoke 3x4x3=36; full 5x4x5=100.
  Verdict emits HARD_FAIL_CARDINALITY_BREACH if len(per_unit) != expected. Non-saturated floor MIN_NONSAT.
- arms_differ_verified (AF): true -- the EXACT prediction surface (n_comp=V-1) and LOOSE surface (n_comp=1)
  are hash-distinct per unit (verified in compute_verdict; HARD_FAIL_ARMS if identical). Formula selftest
  asserts p1_exact <= p1_loose pointwise for V>1.
- final_metrics_atomicity: tmp_replace (os.replace of metrics.json.tmp).
- except SystemExit: raise BEFORE except Exception (no BaseException / no bare except; grep-clean, verified).
- crlb / discriminator_reachability: prediction-match test; the gated quantity is a ratio (no Cramer-Rao
  noise floor). crlb_n_a: exact-vs-loose ratio tightness. discriminator_reachability: MEASURED off-disk
  (exact gm 1.18, loose gm 1.03, rel_improve 0.87) -- HP is reachable in PRINCIPLE by a light-tail-corrected
  model but the pre-registered Gaussian order statistic lands ACCEPT_BOUNDARY; BOTH outcomes pre-registered.
- baseline_in_band (AG): prediction-match, not a difficulty baseline. Saturated D<=4 cells EXCLUDED
  (declared). Loose arm = live CONTROL; exact arm = MECHANISM under test.
- calibration_check: default_ok_for_this_regime -- the exact formula is parameter-free given the
  geometry-measured moments; moments measured at V_REF and extrapolated, NOT fit to accuracy. 64-pt GH.
- sweep_alignment_verdict: ALIGNED -- each (D,V) cell's decode literally experiences V same-partition
  distractors + L=D/2 superposed fillers; the predictor consumes that cell's own (L,V) + measured moments.
- discriminating_fraction: >= 0.30 -- the decode cliff (non-saturated p1 cells) spans D=8 (all V) + D=6
  high-V; smoke MEASURED 5/36 cells non-saturated with p1 in (0.877, 0.997), populating the ratio.
- composition_edges: SHAPE_MATCH (single primitive: role-typed matched-filter decode -> per-role argmax;
  the prediction is a downstream closed form, not a composed primitive).
- positive_control_arms (Gate D): the measurement machinery IS the landed comprehension cell's, IMPORTED +
  reused VERBATIM (base.run_unit) at the SAME regime; the fresh measurement reproduces the landed decode
  surface (smoke D8V1000 decode_part 0.35-0.58 vs landed 0.30-0.55). regime_extension_audit: SHAPE_MATCH.
- functional_requirements: (1) recognize the occupied SET [base occupancy]; (2) recover role->block ORDER
  under superposition [base role-typed matched filter]; (3) decode each filler [base partition-restricted
  argmax]; (4) predict where (2)+(3) collapse as (D,V) grow [extreme-value order statistic]. Requirement
  (4) is the one under test; the finding is that (4) resists the parameter-free Gaussian order statistic.
- progress_logging: line_buffered_stdout + print(flush=True) on every progress line; heartbeat.jsonl each unit.
- start_marker_written / crash_diagnostic_present / heartbeat_present: true. cell_chunked: false (single
  metrics.json; per-seed loop is fast -- smoke 36 units in 20s; full ~2 min).
- defensive_error_checking: passed_all_4_patterns.
- run_mode: defaults to full (bare / runner HDLAB_RUN_MODE=full); --smoke / --self-test flip. Cell asserts
  written run_mode == mode (§16 RUN_MODE verification).

## Compute architecture
SEQUENTIAL-CPU (numpy matched-filter + block-argmax; the cell IS the substrate comprehension primitive
being re-measured -- bit-identical CPU reference exemption). Storage: no_storage / no_composition beyond
the base cell's superposition (synthetic clean GSBC partitions). The prediction arms are numpy Gauss-Hermite
quadrature (deterministic; no GPU, no scipy, no torch, no LLM). DEPENDENCY: the untracked GSBC pool npz
`data/gen_decoder_gsbc_fillers/gsbc_expand2x_pool_v1.npz` + the base cell file must be present on remote
(SCP the pool before FULL; queue_add does NOT ship it). NON-PARKED (synthetic GSBC data; no cert_ledger referent).

## SMOKE RESULT (local, N=8192, D {2,4,6,8} x V {50,250,1000}, seeds 7/13/19, 36/36 units, 20.2s)
HARD_FAIL / ACCEPT_BOUNDARY (as pre-registered). MEASURED@data/exp_comprehension_order_recovery_exact_margin_v1/metrics.json:extra:
- EXACT p1 mean_ratio=1.1928 (OVER-predicts), gm_err=1.1847, max_err=1.4497.
- LOOSE p1 mean_ratio=0.9721 (biased=False -- the trivial model is already ~unbiased on p1), gm_err=1.0292.
- rel_improve=0.8687 (< 1.0 -> exact NOT tighter than loose -> ACCEPT_BOUNDARY gate).
- decode_part(p1^D) compounding gm=2.54x, max=7.73x (fresh 3-seed; ~22x on the full landed surface).
- cross_seed_cv=0.1373; arms_differ=True; 5 non-saturated cells; cardinality 36/36.
- In-cell off-disk retrospective vs landed metrics: exact_mean_ratio 1.187, rel_improve 0.873,
  decode_part_max_err 21.84x -> ACCEPT_BOUNDARY_DIRECTION_CONFIRMED.

## FULL grid (staged; remote_cpu_queue -- SMOKE-only-local rule; exp_dev CANNOT push -> Orchestrator dispatches)
D {2,4,6,8} x V {50,125,250,500,1000}; seeds {7,13,19,23,29} (>= 5, CG multi-seed precedent);
EXPECTED_N_UNITS=100; run_mode=full. FULL adds the 2 intermediate V points + 2 seeds -> a first-class
independently-re-measured accept-boundary artifact + full-grid multi-seed cv. timeout: smoke 36 units =
20s on laptop; FULL 100 units + 5 codebook builds ~ 2-4 min; recommend --timeout 1800 (30 min, ample).
RECOMMENDATION (exp_dev): FULL is OPTIONAL -- the accept-boundary is decisively established both off-disk
(landed 60-row surface) AND by the fresh 3-seed smoke (rel_improve 0.87, cross_seed_cv 0.14). A 5-seed
FULL only re-confirms + upgrades to a first-class landed artifact at trivial CPU cost. Director's call.
