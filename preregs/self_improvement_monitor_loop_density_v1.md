# Pre-registration: self-improvement MONITOR loop (density-regime instance, n=1)

Cell: `experiments/exp_self_improvement_monitor_loop_density_v1.py`
Author: hdi_exp_dev. Date: 2026-07-07.
Spec sources:
- `notes/research_self_improvement_monitor_loop_scoping_2026-07-07.md` (the loop + 2 firing controls)
- `notes/research_density_scale_theory_reconciliation_970k_2026-07-07.md` (JL/Larsen-Nelson m*(V) law; m*(970K)~6, band [5,7])
- `notes/research_resonator_restart_budget_geometric_race_law_2026-07-07.md` (shared OBSERVE->LAW->PROPOSE->CONTROL->APPLY->SCORE shape, n=2)

## USER-LOCKED CONSTRAINT
MONITOR-NOT-CONTROL, NEVER SELF-MODIFYING. The cell only OBSERVES landed retrieval-margin
telemetry and PROPOSES an operating-point density m*. A human / hdi_exp_dev decides whether to
apply. The cell never edits any encoder config, never re-dispatches itself, never writes to
cert_ledger.jsonl. `monitor_proposal.monitor_not_control = True` asserted in every metrics.json.

## THE LOOP
1. OBSERVE: per (scale V, density m): cross-seed MIN `graded_ret_agree10` and cross-seed CV.
   Operating point = density maximizing cross-seed MIN. CV onset = argmin-CV density (CV floor).
2. LAW: `m*(V_eff) = a + b*ln(V_eff)` (JL/Larsen-Nelson, mechanism-matched Anchor A) fit on the
   TRAINING scales. Leave-one-out over the 3 scales {50K,100K,177K}; canonical extrapolation fold =
   hold out the LARGEST scale (matches the real R4/970K use case).
3. PROPOSE: structured, machine-checkable claim `{predicted_m_star, V_target, confidence_band,
   law_used, law_coeffs, fit_scales}` for the held-out scale, emitted BEFORE the held-out scale is
   used in fitting (pre-registered by construction, leave-one-out).
4. SCORE: (a) proposal within +/-1 density-step (grid index) of held-out actual argmax-of-MIN;
   (b) proposed density's cross-seed MIN beats BOTH baselines (constant "keep mid density" and
   nearest-value-lookup) on the held-out scale.
5. FIRING CONTROLS (both required):
   - C1 scramble-law: bootstrap-refit training rungs, then permute (a,b) pairing across resamples
     (destroys the joint fit structure). HARD-PASS requires the real-law proposal to measurably
     beat the scrambled arm (margin > 0.05 on ret scale) AND the scrambled arm to collapse to
     no-better-than-chance (scrambled_mean <= chance_mean + 0.10).
   - C2 scramble-CV: statistic T = spearman(cv_onset_m, argmax_min_m) across scales. HARD-PASS
     requires real T OUTSIDE the 90th percentile of a permuted null (relabel which scale's CV maps
     to which operating point) AND a scrambled-CV input (shuffle CV across densities within scale)
     to fall INSIDE the null (signal destroyed).

## PRE-REG BANDS (envelope-fail-bands)
- HARD-PASS: extrapolation fold proposal correct (within +/-1 step) AND beats both baselines AND
  C1 fires AND C2 fires.
- HARD-FAIL: proposal misses actual optimum by > 2 density steps OR neither control fires.
- MIDDLE_BAND: proposal directionally correct / beats a baseline but does not clear all four gates
  (law adds real-but-small value over a cheaper heuristic). This is the honest expected outcome if
  the real 3-scale operating point is flat (all argmax at the same density).

## HONEST BOUND (stated up front, not softened)
This is the DENSITY-ONLY instance (n=1 of a 2-regime pattern). A HARD_PASS proves the loop WORKS
in one regime; it does NOT prove self-improvement is universal. The resonator instance (n=2,
`exp_resonator_ksweep_reachability_v1`) shares the OBSERVE->LAW->PROPOSE->SCORE shape but its
Control-2 analogue is still to build. Real-data risk: the 177K rung already shows all seeds argmax
at m=8; if 50K/100K also land flat, the law ties the constant baseline and the honest verdict is
MIDDLE_BAND/HARD_FAIL, not HARD_PASS - the firing controls are designed to expose exactly that.

## SCHEMA-VET fields
- cardinality_ok: EXPECTED_N_UNITS = n_scales (leave-one-out folds); verdict hard-fails on breach.
- arms_differ_verified: computed; arms_differ_exempted declared - proposal arms are discrete grid
  densities, so a DATA-DRIVEN collision (flat operating point) is legitimate, not a bug; the firing
  controls (C1 will not fire) catch that regime substantively (META_RULE_AF).
- final_metrics_atomicity: tmp_replace.
- except SystemExit: raise BEFORE except Exception (no BaseException / no bare except; grep-verified).
- crlb_n/a: monitor/analysis cell; no matmul noise floor to bound. discriminator_reachability: True.
- baseline_in_band: N/A as a saturation check (arms are grid-density proposals, not accuracy scores);
  the discriminator is proposal-beats-both-baselines + both-controls-collapse.
- calibration_check: default_ok_for_this_regime (thresholds are fixed pre-reg bands, not tuned).
- start_marker_written / crash_diagnostic_present: True. heartbeat: N/A (fast CPU analysis, <10s).
- progress_logging: print_flush_true.
- Compute architecture: sequential-CPU, JUSTIFIED - pure post-hoc analysis of landed JSON telemetry
  (no substrate primitives, no matmul); wall time < 10s. Not a batching candidate.
- run_mode: REQUIRED explicit flag (self_test|smoke|full); no silent default (exp_dev.md sec 16).
- discriminating_fraction / sweep_alignment / composition_edges / positive_control: N/A - this is a
  monitor/analysis cell, not a parameter-sweep or primitive-composition substrate cell.

## SMOKE RESULT (MEASURED, mock synthetic data, run_mode=self_test/smoke)
- VERDICT = HARD_PASS on designed mock (5 scales x 5 seeds x 6 densities, known m*(V) law).
  MEASURED@data/exp_self_improvement_monitor_loop_density_v1_smoke/metrics.json
- Extrapolation fold V=350000: m_prop=6 = m_actual=6 (correct); beats both baselines.
- C1 (scramble-law) fires: real=0.542 vs scrambled_mean=0.184 ~ chance=0.208 (collapsed).
- C2 (scramble-CV) fires: T_real=1.000 outside null p90=0.800; T_scrambled=0.200 inside null.
- Negative control (flat data, argmax=5 at every scale): C1 does NOT fire (real=scrambled=0.545);
  verdict NOT HARD_PASS - confirms the discriminator genuinely discriminates, not a rubber-stamp.

## REAL-DATA INPUT REQUIRED FOR FULL
Needs >=3 scales, each with >=2 seeds landed at every grid density. Reads marginpush metrics.json:
`teacher_n_concepts` (V), `density_dial_sweep` (grid), `ship.per_m[m].ret` (graded_ret_agree10),
`ship.per_m[m].joint_ok`. Currently only the 177K rung is landed (5 seeds, all HARD_PASS,
argmax m=8); the 50K (v050k) and 100K (v100k) rungs are the in-flight sweep. FULL invocation:
`python experiments/exp_self_improvement_monitor_loop_density_v1.py --run-mode full`
(auto-discovers marginpush dirs, groups by V; gracefully reports GATE_FAIL_INSUFFICIENT_SCALES
until >=3 scales land). Optionally pass `--metric-dirs <dir> ...` to pin the input set.
