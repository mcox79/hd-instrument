# Pre-registration: reasoning_depth_mech_survival_farfold_extrapolation_v1

Cell: `experiments/exp_reasoning_depth_mech_survival_farfold_extrapolation_v1.py`
Anchor: `reasoning_depth_mech_survival_farfold_extrapolation_v1`
Author: hdi_exp_dev  Date: 2026-07-08  Target queue: remote_cpu_queue

## Prior-work check
`bash tools/substrate_query.sh "mechanistic survival law extrapolation reasoning depth transmission coefficient far out of range fold margin"` -> top hit `transmission_mechanism` cosine=0.3428 (WordNet synonym), NO substrate arc cell at cosine>0.30. Genuinely novel envelope-push; NOT a rediscovery.

## What / why
Envelope-push of the VET'd mechanistic reasoning-depth extrapolation (base cell `exp_reasoning_depth_mechanistic_survival_law_extrapolation_v1.py`, commit ae4dae37a, VET'd MEASURED_MECHANISM). The base VET found the mech-vs-nearest-lookup win (+17.5% aggregate) is FAR-FOLD-DRIVEN: on the NEAREST out-of-range fold (fill=0.4219) flat lookup BEATS mech (boundary depth is a good short-range guess), but mech wins on the 2 FAR folds (0.5010/0.5977) because flat lookup degrades with distance while the a-priori physics law does not. The physics edge = ROBUSTNESS across horizons.

HYPOTHESIS: if the win is far-fold-driven, then extending to EVEN FURTHER out-of-range folds (fill 0.6504/0.7207/0.7998, well beyond the landed 0.60 max) should INCREASE the mech-vs-lookup margin. A growing margin firms the extrapolation from modest-MM toward a stronger result AND is the honest test of whether the forward model genuinely generalizes or got lucky on 2 folds.

## Method (clean forward-split, no leakage)
- FIT the mech law {s, kappa} + all comparator laws (affine, quad, lookup, const) on LOW landed folds ONLY (fill <= OOR_SPLIT=0.3516; landed envelope max). No test-fold value touches any fit.
- Physics input coll0 = closed-form birthday-paradox collision (a-priori for unmeasured provisioning).
- TEST on ALL out-of-range folds: NEAR {0.4219, 0.5010, 0.5977} + FAR {0.6504, 0.7207, 0.7998}.
- FAR folds MEASURED via the VET'd keyslots generator (baseline arm; Gate D positive control, `eff_key_capacity(8,1)=2048` asserted). n_test 74/82/91 -> fill 0.6504/0.7207/0.7998 (THEORETICAL@ eff_fill = n_test*18/2048).
- Per-fold margin m(f) = lookup_err(f) - mech_err(f) (positive => mech beats lookup).
- 5 seeds [7,17,23,31,41], N=8192.

## Discriminator (task-primary)
The mech-vs-lookup per-fold MARGIN GROWS with extrapolation distance. NEAR/FAR split at fill 0.62.

## Pre-registered bands
- HARD_PASS: mean far-margin > mean near-margin (margin grows) AND mech beats lookup at EVERY far fold (per-fold margin > 0) AND monotone (spearman(fill, margin) > 0 over all OOR folds) AND both firing controls fire. => a-priori forward model genuinely generalizes further out-of-range.
- HARD_FAIL: margin does NOT grow (mean far-margin <= mean near-margin) OR mech ties/loses lookup at any far fold. => the +17.5% win was 2-fold luck (honest deflation); escalate to percolation-critical-fill regime-shift drill.
- MIDDLE_BAND: margin grows AND all far folds beat lookup but not strictly monotone OR a control did not fire. Partial firming, scope UPGRADED not resolved.
- GATE_FAIL_FAR_FOLDS_FLOORED: far telemetry degenerate (all far folds usable_depth < 1; dead telemetry cannot carry the test). MEASURED@ smoke: far_depths=[2.0,1.5,2.0] (2 seeds), NOT floored -> gate clears.

## Firing controls
- C1 (scramble-mech-law): permute collT<->depth pairing over full landscape, refit; fires iff true pairing beats scrambled (real MAE < scrambled p10 AND scrambled_mean - real > 0.3). MEASURED@ base cell full: real 0.731 vs scr_mean 4.896 -> fires robustly.
- C2 (scramble-curve): fires iff |spearman(fill,depth)| outside null p90 AND scrambling destroys signal by robust margin (|T_real| - null_mean > 0.20). HARDENED vs base cell's flaky single-scrambled-draw check (the null is itself built from scrambled draws, so ~10% of fresh draws exceed their own p90 by construction, giving a ~10% false-non-fire with zero discriminating value). MEASURED@ smoke: absT=0.978 outside p90=0.451 -> fires.

## Compute architecture
Class (b) sequential-CPU with justification: the cell IS the reuse of the VET'd keyslots generator (bit-identical CPU reference telemetry); each provisioning level is an independent numpy walk (~8.9s/gen MEASURED@ smoke). 30 gens (6 folds x 5 seeds) ~270s. Storage: no_composition (analysis/monitor cell scoring a closed-form law over generated telemetry). GPU batching N/A: generation reuses the exact VET'd CPU generator to preserve the positive-control identity; total wall < 10 min.

## SCHEMA-VET fields
- cardinality_ok: True (EXPECTED_OOR_FOLDS=6; verdict counts len(oor_fills), HARD_FAIL_CARDINALITY_BREACH otherwise)
- arms_differ_verified: True (MEASURED@ smoke; 5 prediction arms distinct)
- final_metrics_atomicity: tmp_replace
- except SystemExit: raise BEFORE except Exception (no BaseException / bare except) -- grep-gate CLEAN
- crlb_n/a: analysis cell; telemetry-gen reuses VET'd keyslots generator (own noise floor characterized); discriminator_reachability=True
- baseline_in_band: N/A (no accuracy baseline arm; discriminator = margin-growth over comparator laws). Far folds non-degenerate (not floored) MEASURED@ smoke.
- discriminator survives scale: option C preview -- smoke runs the FULL near+far fold structure at reduced seeds; primary discriminator (margin growth) fires (monotone spearman=1.000, far>near by 0.849, all far positive, nearest-fold reproduces VET negative margin -0.328). C1/C2 fire.
- effective_vs_nominal_parameter_audit: ALIGNED (fill is the swept axis; the generator + closed-form collT both experience the same fill; no partition routing)
- discriminating_fraction: 6/6 OOR folds land in the meaningful depth band (actual depths 2.0-3.0, above the 0-floor, below D_MAX censor); MEASURED@ smoke
- composition_edges: none (single generator -> closed-form law scorer; SHAPE_MATCH trivially)
- positive_control_arms: keyslots generator reproduces landed envelope (Gate D; eff_key_capacity assertion + n_test=48 reproduces landed fill=0.4219)
- functional_requirements: (1) generate valid far-fold telemetry -> VET'd keyslots baseline arm; (2) fit forward model on landed low folds -> mech_depth + fit_mech grid; (3) score margin growth -> margin_growth_analysis
- start_marker_written / crash_diagnostic_present: True; heartbeat_present: False (per-fold flush progress instead; run < 10 min)
- progress_logging: print_flush_true (per-fold [gen] lines, flush=True)
- calibration_check: default_ok_for_this_regime
- run_mode: no silent default; runner injects HDLAB_RUN_MODE=full (verify landed metrics run_mode==full post-dispatch)

## Smoke result (MEASURED@ data/exp_reasoning_depth_mech_survival_farfold_extrapolation_v1_smoke/metrics.json)
- self_test: HARD_PASS (nesting + margin-grows + all-far-beat + monotone + both controls, all assertions pass)
- smoke (2 seeds, real telemetry): HARD_PASS. margins=[-0.328, 0.187, 0.63, 0.815, 1.018, 1.203] for fills [0.42,0.50,0.60,0.65,0.72,0.80]; near_margin=0.163 far_margin=1.012 (far-near=0.849); monotone spearman=1.000; all far beat lookup; C1=True C2=True; far_depths=[2.0,1.5,2.0] NOT floored. Canonical verdict = 5-seed FULL on remote (per canon!=preview).
