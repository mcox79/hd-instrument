# PRE-REG: pfc_gate_waypoint_rescue_coarse2fine_verify_v1

**Author:** exp_dev (hdi_exp_dev sub-agent)
**Date:** 2026-07-05
**Cell:** `experiments/exp_pfc_gate_waypoint_rescue_coarse2fine_verify_v1.py`
**Parent (verbatim primitive reuse + baseline reproduce):** `experiments/exp_pfc_gate_autonomous_waypoint_discovery_v1.py`
**Drill / research spec:** `notes/research_autonomous_waypoint_deep_corner_compounding_error_rescue_2026-07-05.md`
**Scope (USER-LOCKED):** narrow glass-box sub-goal discovery + error-correction. Mechanism-analog,
NOT task-analog. NOT autonomous planning / self-improvement. Cerebellar forward-model brain-component
build (predict-then-verify-before-commit); the CONTROL-depth target
(`research_brain_component_rerank_thalamus_cerebellum_load_2026-07-05.md`) is a sibling consumer.

## Prior-work check (substrate-KB concept query, USER-locked pre-authoring)
`bash tools/substrate_query.sh "coarse-to-fine waypoint decomposition verify-gate compounding error
rescue sequential bisection"` -> top hit `Verify-OFF-DATA gate decomposition` cosine=0.3154 (a
skunkworks AUDIT-DISCIPLINE note about verifying against on-disk data, NOT a prior rescue mechanism);
2nd `D composition DIRECTIONAL finding` cosine=0.3125 (QA-vocab composition, unrelated). Char-trigram
encoder (MEDIOCRE) surface-matches on the words "verify"/"decomposition"/"composition"; NEITHER is a
prior implementation of coarse-to-fine + verify-gate waypoint rescue. **Verdict: genuinely NOVEL**
(this exact three-mechanism combination has never been run on this substrate); direct continuation of
the parent autonomous-waypoint HARD_FAIL, not a rediscovery.

## Hypothesis
The parent autonomous-waypoint cell HARD_FAILed at the deep corner (`op4_V1200_d8`: wp_bisect_open
recovery = -0.014 MEASURED@data/exp_pfc_gate_autonomous_waypoint_discovery_v1/metrics.json:per_regime.
op4_V1200_d8.recovery_ratio). The negative-drill diagnosed a Ross-Bagnell O(T^2) COMPOUNDING-ERROR
regime (CITED@Ross-Bagnell AISTATS 2010), proven by a matched-entropy dissociation (op4_d4 ent8 1-step
recovers 0.690 vs op2_d8 ent8 3-step recovers 0.073 despite slightly better per-hop signal). This cell
tests whether coarse-to-fine recursive bisection (a) + a verify-gate (b) + multi-gamma SR (c) recover
real autonomous-decomposition at the deepest corner, versus the failing sequential-bisection baseline.

## Arms (10; paired; share E, W_ops, M, M_long, R per (regime,seed))
`flat_gonogo`, `oracle_exec`, `hier_oracle`, `hier_shuffled`, `wp_bisect_open` (parent's FAILING
baseline = the bar), `wp_bisect_coarse2fine` (a+c), `wp_bisect_verify` (b), `wp_bisect_combo` (a+b+c),
`wp_random_state` (floor), `wp_index_midpoint` (structural guard). best_rescue = max mean over the
three rescue arms.

## FOCUS regime
`op4_V1200_d8` (entropy=16, chain_steps=3) at FULL -- the exact parent HARD_FAIL corner, for a clean
before/after paired comparison. focus = highest-entropy discriminating regime (oracle_exec>=0.90 AND
headroom_exec>=0.10 AND headroom_decomp>=0.10).

## Key discriminator
`delta_recovery = recovery_ratio(best_rescue) - recovery_ratio(wp_bisect_open)` at FOCUS. Paired
sign-test is best_rescue vs wp_bisect_open (the failing mechanism), NOT vs flat.

## Bands (LOCKED before dispatch)
- **HARD_PASS** (rescue is real; worth folding into the capability):
  `recovery_ratio(best_rescue) >= 0.20` **AND** `delta_recovery >= 0.15` **AND** `lift_flat > 0.05`
  **AND** `lift_random > 0.10` **AND** `index_artifact_gap < 0.05` **AND** `anti_tautology_corr < 0.85`
  **AND** `degenerate_rate < 0.10` **AND** `sign_p(best_rescue vs open) < 0.05` **AND**
  `cv(best_rescue) < 0.15` (FULL only; loosened from parent 0.10 given more moving parts, documented)
  **AND** `oracle_exec >= 0.90` **AND** headroom gates.
- **HARD_FAIL** (deep corner is a genuine bound even after the standard fixes):
  `delta_recovery <= 0.05` -> honest ACCEPT-BOUND; remaining lever (DAgger oracle-in-loop) breaks the
  "autonomous, no-oracle" framing -> out of scope.
- **MIDDLE_BAND**: `0.05 < delta_recovery < 0.15` (real partial mitigation), OR `delta_recovery >= 0.15`
  but `recovery_ratio(best_rescue) < 0.20`, OR any honesty guard fails while margins pass.
- **INCONCLUSIVE**: no discriminating regime, OR `index_artifact_gap > 0.10` with `idx_sign_p < 0.05`
  (structural index-order leak).

At FOCUS: HP requires best_rescue accuracy >= flat + 0.20*headroom_decomp = 0.077 + 0.20*0.851 = 0.247
(THEORETICAL@ using parent MEASURED flat=0.077, hier_oracle=0.928). HARD_FAIL if best_rescue <= ~0.108.

## P (deflated, from the drill)
- P(any real lift over open at FOCUS, clears MIDDLE): raw ~0.70-0.75 -> **P_deflated ~0.50-0.55**.
- P(clears full HARD_PASS at the deepest corner): raw ~0.50-0.55 -> **P_deflated ~0.35** (novel-synthesis
  cap 0.50). A partial rescue or a clean "compounding-error is a real residual bound" are realistic +
  informative outcomes; the cell is designed to be interpretable either way.

## SCHEMA-VET gates (all satisfied)
```yaml
cardinality_ok: true                 # EXPECTED_N_UNITS = 10 arms * n_seeds * n_regimes (verdict counts)
final_metrics_atomicity: tmp_replace # os.replace on metrics.json
except_ordering: "SystemExit/KeyboardInterrupt raise BEFORE except Exception (no BaseException)"
crlb_n/a: "accuracy-closure discriminator; reachability by feasibility (parent hier_oracle=0.928 at
           op4_d8 proves the given-decomposition envelope; HP recovery>=0.20 sits inside it)"
baseline_in_band: "rescue baseline = wp_bisect_open (the failing mechanism), collapsed to ~flat at
                   FOCUS (0.066 vs 0.077); discriminator = rescue-vs-open; oracle rail + headroom gates"
discriminator_survives_scale: "smoke SHOWS lift at BLUNTER N=2048 reach (delta +0.086/+0.147, 2 seeds);
                               FULL N=8192 reach is SHARPER (reach_rank d8 0.29->0.445) -> lower bound"
hard_pass_strictly_above_floor: "recovery>=0.20 + delta>=0.15 (META_RULE_L)"
HP_SCOPE: "HP gates -> best_rescue vs wp_bisect_open at FOCUS; oracle_rail(>=0.90)->oracle_exec;
           recovery references hier_oracle; index guard -> wp_index vs wp_random"
calibration_check: "adaptive_with_discriminator_gate: verify-gate tau = 70th-pctl of R off-diagonal
                    (principled); retry_rate + fallback_rate logged; discriminator = delta-over-open"
per_unit_failure_class: "fatal-flag per-seed crash -> write_partial_key failure_class; no bare except"
arms_differ_verified: true           # AF: best_rescue vs open/flat/random + hier_oracle vs shuffled hash
arms_differ_exempted:
  - "[wp_bisect_coarse2fine == wp_bisect_open] at d4/1-interior-boundary regimes: coarse-to-fine with a
     single interior boundary IS structurally identical to open (no recursion). LEGITIMATE identity;
     the AF gate correctly marks such non-FOCUS regimes hp_ok=False (no rescue benefit at d4 anyway).
     At FOCUS op4_d8 (3 interior boundaries) the recursion is non-trivial -> arms differ."
cell_chunked: false                  # single cell, per-seed checkpoint via _seed_checkpoint (resumable)
start_marker_written: true
crash_diagnostic_present: true       # Exception -> CELL_CRASHED metrics + traceback (atomic)
heartbeat_present: true              # _heartbeat.jsonl per (seed,V,n_ops)
defensive_error_checking: passed_all_4_patterns
progress_logging: print_flush_true   # flush=True on all progress lines; FULL timeout_s >= 1800
run_mode_verification: "post-dispatch verify landed metrics.json run_mode==full/smoke, size, elapsed"
```

### §15 composition/sweep gates
```yaml
sweep_alignment_verdict: ALIGNED     # depth ladder op4 x {d4,d6,d8}; effective depth == nominal depth
discriminating_fraction: ">=0.30"    # FULL op4_d6 (chain_steps=2) + op4_d8 (chain_steps=3) + op2/op3_d8
                                     #   are the discriminating collapse regimes (open recovery ~0); d4
                                     #   is the alive/no-harm control (open recovers 0.69)
composition_edges: "discovery_fn -> _boundaries_to_hops -> run_hier_arm_wp; all SHAPE_MATCH (identical
                    wp_idx [n_chains,depth] interface for every wp_* arm, per parent design)"
positive_control_arms:
  - arm: wp_bisect_open  # re-run IN-CELL on identical seeds; M trained first at gamma=0.85 with the
                         # parent's exact sr_gen seed -> reproduces parent flat/hier_oracle/open by
                         # construction. cited_prior op4_V1200_d8 open recovery=-0.014, flat=0.077,
                         # hier_oracle=0.928, oracle_exec=0.934 MEASURED@parent metrics; tolerance 0.05.
                         # regime_extension_audit: SHAPE_MATCH (identical config/primitives/seeds).
functional_requirements:
  - "discover a sub-goal decomposition from trained SR without an oracle trajectory (parent primitive)"
  - "avoid compounding error over chained bisection steps -> coarse-to-fine recursion (NEW mechanism)"
  - "do not commit weak/unverified waypoints -> verify-gate threshold+fallback (NEW mechanism)"
  - "sharp long-range reach for the coarse pick -> multi-gamma SR M_long@0.95 (NEW mechanism)"
```

## Compute architecture
(a) batched-GPU. SR-TD (M@0.85 AND M_long@0.95), reach, coarse-to-fine + verify picks = batched
matmuls/argmax. Chains batched; within-chain hops sequential (genuine dependency). M+M_long+R once per
(V,n_ops) group. Storage: sharded. Extra vs parent: one 2nd SR train (M_long) per group. **FULL ->
overnight_queue (GPU).**

## Config
- selftest: N=256, tiny. smoke: N=2048, op4 x {d4,d6,d8}, V=300, 3 seeds, SR_STEPS=2500 (trained SR so
  the discriminator fires at blunter smoke reach). full: N=8192, 5 seeds, SR_STEPS=8000, regimes
  op4 x {d4,d6,d8} (V=1200) + op3_V1000_d8 + op2_V800_d8 (matched-entropy dissociation partner).
- EXPECTED_N_UNITS full = 10 * 5 * 5 = 250. Timeout FULL >= 4500s (parent FULL 405 units in 1789.5s on
  GPU; this = 250 units + one extra SR/group; ~1500-2500s expected).

## Smoke result (SR_STEPS=2500, N=2048; MEASURED off-disk)
See metrics @ `data/exp_pfc_gate_waypoint_rescue_coarse2fine_verify_v1_smoke/metrics.json`. 2-seed
_eval_regime preview: op4_d8 best_rescue(coarse2fine) beats open by delta +0.086 (seed7) / +0.147
(seed17); op4_d4 delta=0.000 (no harm; c2f==open at 1 interior boundary). Directional lift confirmed
at blunt smoke reach -> stage GPU FULL.
