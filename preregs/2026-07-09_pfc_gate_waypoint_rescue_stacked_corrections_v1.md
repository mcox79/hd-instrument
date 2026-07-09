# Pre-registration: pfc_gate_waypoint_rescue_stacked_corrections_v1

Date: 2026-07-09. Author: exp_dev. Anchor: `pfc_gate_waypoint_rescue_stacked_corrections_v1`.
Parent: `pfc_gate_waypoint_rescue_kb_grounded_check_v1` (verdict MIDDLE_BAND_FLATNESS_BELOW_50).
Driver: `notes/research_stacked_independent_corrections_push_compounding_frontier_2026-07-09.md`.

## Question
Does STACKING two informationally-INDEPENDENT correction channels (the landed KB-grounded gate =
channel A + a NEW cross-fit calibrated correctness-selector = channel B) as an OR-gate suppress the
compounding-reasoning-drift wall MULTIPLICATIVELY -- pushing the recovery frontier PAST where either
channel reaches alone (KB-alone landed recovery 0.2444 at op4_V1200_d8, decaying ~0.51x/hop)?

## Mechanism under test
- Channel A: KB-grounded gate (VERBATIM from parent; raw-graph reachability mask; zero shared params w/ M/R).
- Channel B (NEW): cross-fit calibrated selector. Features from raw graph ONLY (anchor/candidate out-degree
  + graded reach closeness anchor->cand and cand->goal). Logistic weights fit on train-fold A; Platt
  calibration fit on DISJOINT train-fold B (double-ML independence by construction). Accept iff calibrated
  P(correct) >= tau (tau = 70th-pctl of fold-B calibrated scores).
- STACKED (A OR B): mask R's balance-argmax to candidates KB-CONFIRMED *OR* SELECTOR-ACCEPTED; empty ->
  reset fresh re-anchored at START; still-empty -> open-argmax fallback. True waypoint skipped only when
  NEITHER channel confirms it -> P(skip)=miss_A*miss_B IFF the misses are independent.
- Self-derived (non-independent) MUST-FAIL control: wp_bisect_verify (re-checks R against a percentile of R).

## Arms (14; paired): flat_gonogo, oracle_exec, hier_oracle, hier_shuffled, wp_bisect_open,
wp_bisect_coarse2fine, wp_bisect_verify (KEY comparator), wp_bisect_combo, wp_replay_generate_select,
wp_kb_grounded_gate (channel A), wp_calibrated_selector_gate (channel B), wp_stacked_kb_plus_selector
(RESCUE), wp_random_state, wp_index_midpoint.

## FULL grid (5 regimes x 5 seeds [7,17,23,31,41]): op4_V1200_d4 (ent8, steps1, flatness ref),
op4_V1200_d6 (ent12, steps2), op4_V1200_d8 (ent16, steps3, FOCUS), op3_V1000_d8 (ent~12.7),
op2_V800_d8 (ent8, steps3, matched-entropy dissociation). N=8192.
EXPECTED_N_UNITS = 14 arms x 5 seeds x 5 regimes = 350. `cardinality_ok` gated.

## Mandatory screens (both reported first-class; #2 is the load-bearing NEW one)
1. `independence_corr` = corr(kb_confirm, m_error) AND `selector_independence_corr` = corr(selector_conf,
   m_error). Predict |corr| ~ 0 by construction (channels independent of M/R).
2. `failmask_corr` = corr(failure_mask_KB, failure_mask_SELECTOR) over per-chain correctness. THE new
   screen; the multiplicative claim is VOID if high (shared coverage density). Reported per regime + FOCUS.

## Bands (LOCKED before FULL; FOCUS = op4_V1200_d8)
HARD_PASS (multiplicative stacking; frontier genuinely pushed):
- recovery(stacked) >= 0.35 AND delta_recovery(vs verify) >= 0.15 AND stacked_over_kb >= 0.03 AND
- super_additive: gain(stacked) > gain(kb) + gain(sel)  [gain = recovery - recovery_verify] AND
- flatness_ratio >= 0.50 AND (flatness_ratio - flatness_kb) >= 0.10 AND
- |independence_corr| <= 0.15 AND |selector_independence_corr| <= 0.15 AND |failmask_corr| <= 0.20 AND
- kb non-vacuous AND selector non-vacuous AND lift_flat>0.05 AND lift_random>0.10 AND index_gap<0.05 AND
  anti_taut<0.85 AND degen<0.10 AND sign_p<0.05 AND cv<0.15 (FULL) AND oracle rail>=0.90 AND headroom gates
  AND max_entropy_hp_ok > 12.0 (frontier extends past KB-alone).

HARD_FAIL (any):
- delta_recovery(vs verify) <= 0.05 (even stacked can't beat the self-derived control) -> BOUND_REAL, OR
- |failmask_corr| > 0.50 (channels' failures strongly correlated) -> FAILURE_MASKS_CORRELATED, OR
- stacked_over_kb <= 0.03 (no material lift over KB-alone) -> STACKING_REDUNDANT, OR
- |independence_corr| > 0.40 -> KB_SIGNAL_NOT_INDEPENDENT, OR
- |selector_independence_corr| > 0.40 -> SELECTOR_NOT_INDEPENDENT, OR
- flatness_ratio < 0.20 -> ACCELERATING_COLLAPSE.
=> the wall is single-channel-fundamental / data-coverage-limited; redirect to KB-density fix (informative).

MIDDLE_BAND: partial failmask corr (0.20, 0.50]; additive-but-not-superadditive; selector vacuous; partial
independence; or any HP gate sub-threshold while others pass.

## SCHEMA-VET fields
- `cardinality_ok`: true (EXPECTED_N_UNITS=350 gated).
- `crlb_n/a`: "accuracy-closure discriminator; feasibility by hier_oracle envelope (given-decomposition
  ceiling ~0.84-0.91) -- recovery>=0.35 sits inside; verify collapse to ~flat is the measured bar."
- `baseline_in_band`: KEY baseline = wp_bisect_verify; collapses to ~flat at FOCUS (SMOKE recov_verify=-0.045,
  well below oracle rail 0.917 -> discriminator fires, NOT saturation-vacuous).
- `discriminator survives scale`: SMOKE (N=2048/V=300) is BLUNTER than FULL (N=8192/V=1200); KB reachability
  is exact/N-independent so any positive kb-minus-verify at smoke is a LOWER bound on FULL. SMOKE fired the
  discriminator (verify collapsed; screens populated non-vacuously; failmask_corr=0.49 measured).
- `arms_differ_verified`: true (SMOKE: stacked trace != verify/open/kb/flat/random; stacked==selector at the
  deep corner is a REAL dilutive OR-gate property, not a wiring bug -- flagged, not AF-exempted).
- `final_metrics_atomicity`: tmp_replace (os.replace).
- `except SystemExit: raise` before `except Exception` (no BaseException); grep-gate clean.
- `cell_chunked`: false (multi-seed within cell w/ per-seed checkpoint/resume via _seed_checkpoint).
- `start_marker_written` / `crash_diagnostic_present` / `heartbeat_present`: true.
- `defensive_error_checking`: passed_all_4_patterns.
- `calibration_check`: adaptive_with_discriminator_gate (KB = exact reachability, no tunable thresh;
  verify tau = 70th-pctl of R; selector tau = 70th-pctl of fold-B calibrated scores; discriminators =
  delta-vs-verify + super-additivity + failmask_corr + flatness, not tuned-for-PASS).
- `effective_vs_nominal_parameter_audit`: entropy = log2(n_ops)*dd swept via (n_ops, dd); ALIGNED.
- `bracket_includes_discriminating_band`: verify collapses to ~flat at d6/d8; oracle in [0.84,0.98];
  discriminating (0.20-0.70) band covered by kb/sel/stacked at d6/d8. discriminating_fraction >= 0.30.
- `composition_edges`: selector features -> logistic (SHAPE_MATCH); KB/selector masks -> R-balance argmax
  (SHAPE_MATCH); no SHAPE_MISMATCH_no_adapter.
- `positive_control_arms`: wp_bisect_open/verify/flat/hier_oracle reproduce the parent by construction
  (same E/M/R/seeds); wp_kb_grounded_gate reuses the parent's verbatim discovery (channel-A reproducer).
- `functional_requirements`: (1) validate a waypoint independently of M/R -> KB reachability + cross-fit
  selector; (2) combine two validators without shared failure -> OR-gate + failmask screen.

## Compute architecture: (a) batched-GPU. SR/M/M_long/M_rev/R_* built once per (V,n_ops) group; reach_cum
boolean powers; selector logistic GD; masked bisection = batched gathers/argmax on cuda-if-available.
Storage: sharded. FULL strongly prefers overnight_queue (GPU).
progress_logging: print_flush_true (flush=True on every progress line; per-(seed,V,n_ops) heartbeat;
FULL timeout_s >= 1800).

## HYPOTHESIZED vs MEASURED
- KB-alone recovery 0.2444 at op4_V1200_d8: MEASURED@data/exp_pfc_gate_waypoint_rescue_kb_grounded_check_v1/metrics.json
- SMOKE FOCUS (op4_V300_d8, 3 seeds): recov_verify=-0.045, recov_kb=-0.045, recov_sel=-0.022, recov_stk=-0.022,
  failmask_corr=0.486, indep_corr=-0.004, sel_indep=0.061:
  MEASURED@data/exp_pfc_gate_waypoint_rescue_stacked_corrections_v1_smoke/metrics.json
- P(full HARD_PASS): ~0.10-0.20 HYPOTHESIZED@this prereg (research deflated estimate; SMOKE leans toward the
  pre-registered informative-negative: OR-gate dilutive + failure masks correlated).
