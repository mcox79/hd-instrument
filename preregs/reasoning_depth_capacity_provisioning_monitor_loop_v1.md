# Pre-reg: reasoning_depth_capacity_provisioning_monitor_loop_v1

Date: 2026-07-07. Author: hdi_exp_dev. Regime: self-improvement MONITOR loop (revival of density HARD_FAIL).

## Purpose
Revive the self-improvement monitor loop on the REASONING-DEPTH capacity-provisioning regime. The
density instance (`exp_self_improvement_monitor_loop_density_v1`) HARD_FAILed as a VERIFIED honest
null: the density m*(V) landscape is genuinely flat (argmax_min_m=8 to 1e-15 across 3.5x V), so
neither firing control COULD fire. Per the 2x-revival drill
(`notes/research_self_improvement_regime_ranking_revival_2026-07-07.md`, rank-1 candidate), the
reasoning-depth capacity-provisioning law is genuinely NON-FLAT (p^D survival: max usable reasoning
depth as a function of provisioning/capacity), so the loop's proposal SHOULD beat baselines and both
controls SHOULD fire -- the demonstration density could not give.

## Compute architecture
Class (b) sequential-CPU, justified: post-hoc analysis of landed JSON telemetry, no matmul, no
storage, no composition. Wall time <10s (measured 3.86s). Zero new GPU/queue cost. Reuses the
validated loop machinery from `exp_self_improvement_monitor_loop_density_v1.py` (commit 31d78eff9).

## Data (verified off-disk BEFORE build)
- `data/exp_reasoning_depth_keyslots_sharding_v1/metrics.json` (273KB, landed 2026-07-05).
  `per_seed[*].units[*].arm_results[arm]` -> {eff_fill, eff_key_capacity, usable_depth,
  collision_frac_emp, predicted_usable_depth}. 5 seeds x 6 op-points x 5 real arms.
- eff_fill = 18 * n_test / eff_key_capacity (identity verified on disk) is the single provisioning
  coordinate (captures both load n_test and capacity).
- `control` arm (scrambled reasoning) usable_depth=0 across all 30 points -> independent on-disk
  confirmation of the C1 premise (surfaced, not a loop rung).

## The loop
- OBSERVE per (N,arm,n_test) rung -> group by provisioning level (eff_fill); pool cross-seed usable
  depths. 8 uncensored levels (fill in [0.0703, 0.3516]); fill=0.0527 censored at D_MAX=18.
- LAW: survival law linearized `usable_depth = a + b*phi(fill)`, phi(fill)=ln(FLOOR)/ln(1-fill),
  FLOOR=0.5. b = self-heal factor (naive occupancy-binary law is the b=1 special case).
  MEASURED in-sample fit: depth = 1.875 + 1.757*phi (b=1.76), MAE=0.82.
- PROPOSE: leave-one-provisioning-level-out; propose max usable depth at the held-out level.
- SCORE: |pred-actual| <= TOL=2 depth-steps AND law err beats BOTH constant + nearest-fill-lookup.
- C1 scramble-law: permute (fill,depth) training labels + refit -> proposal collapses to chance.
- C2 scramble-curve: Spearman(fill,depth) outside permuted null; scrambled-depth curve inside null.

## Pre-flight verification (MEASURED@data/exp_reasoning_depth_keyslots_sharding_v1/metrics.json)
- LOO law MAE=1.20 vs constant=4.70 vs nearest-lookup=1.65 -> law beats BOTH.
- Spearman(fill,depth) = -0.983 (strong monotone early-warning; C2 will fire on scramble).
- self-heal b~1.77 (substrate reasons ~1.77x deeper than naive occupancy-binary bound; matches the
  note's ~2.02x naive-vs-exact differential).

## Honest bands (envelope-fail)
- HARD-PASS: aggregate law MAE <= TOL AND law beats BOTH baselines AND C1 fires on >=50% folds AND
  C2 fires. (The non-trivial self-improvement demonstration density could not show.)
- MIDDLE_BAND: proposal correct + beats constant, but ties nearest-lookup OR a control silent.
- HARD-FAIL: law no better than baselines (flat, density-null analogue) OR neither control fires.
  Would be a DEEPER honest bound (substrate landscapes flat across the board).

## Schema-vet
cardinality_ok (EXPECTED_N_UNITS = 8 uncensored levels); arms_differ_verified; final_metrics_atomicity
= tmp_replace; except SystemExit: raise before except Exception (no BaseException / bare except);
crlb n/a (monitor cell, no matmul noise floor); discriminator_reachability True; start_marker +
crash_diagnostic present; progress_logging print_flush_true; calibration_check default_ok. SMOKE=FULL:
self_test runs the SAME loop code on designed mock with a known law (asserts machinery + both controls
fire -> HARD_PASS); full runs the identical code on real landed data.

## Result (MEASURED@data/exp_reasoning_depth_capacity_provisioning_monitor_loop_v1/metrics.json)
VERDICT = HARD_PASS. law MAE=1.20 (beats const 4.70 AND lookup 1.65); frac_correct=0.75; C1 fires
0.88 of folds; C2 fires (|T|=0.976 > null p90=0.619); self_heal b=1.77. Substrate own-scramble
control = 0.0 depth (30 pts). Extrapolation-fold proposal: fill=0.3516 -> depth 5.26 (actual 3.40,
band [3.26,7.26]).
