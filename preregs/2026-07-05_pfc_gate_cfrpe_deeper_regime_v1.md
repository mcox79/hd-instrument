# Pre-reg: pfc_gate_cfrpe_deeper_regime_v1

Author: exp_dev (Opus 4.8 1M, agent-spawn) 2026-07-05
Cell: `experiments/exp_pfc_gate_cfrpe_deeper_regime_v1.py`
Anchor: `pfc_gate_cfrpe_deeper_regime_v1`  (smoke: `_smoke`)

## Question
v2 FULL proved the cf-RPE-trained Go/NoGo control gate at a FAIR depth-4 regime
(closure=0.661, gonogo_lift=0.600) but the SAME gate DEGRADES to gonogo=0.075
(closure=0.073) at depth-6. Does a LONGER-HORIZON successor-representation (SR) restore
control at depth-6, and WHY does it degrade?

MEASURED@data/exp_pfc_gate_cfrpe_trained_v2/metrics.json (N=8192, n_ops=4):
- reach_rank_test (mechanism signal; chance=1/n_ops=0.25): d4=0.686-0.690, d5=0.564-0.615,
  d6=0.509 -> reach signal erodes ~26% d4->d6.
- additive baseline FLOORS at d5/d6 (all additive <= 0.016) -> NO fair d6 regime exists at
  n_ops=4 (structural compounding: chain_acc = per_hop^depth; per_hop_additive ~0.48).

## Mechanism hypothesis (TESTED, not assumed)
SR transport M trained by TD(0) with discount gamma sets horizon ~ 1/(1-gamma).
reach(cand;goal)=cos(E[cand]@M, E[goal]); the goal sits gamma^(depth-1) deep in the SR
bundle. gamma=0.85 (v2 value) -> horizon 6.7 steps -> at depth-6 the goal is near/past the
horizon and reach starves. THEORETICAL@geometric-SR-horizon: goal 5 hops out weighted
0.85^5=0.44 vs 0.95^5=0.77. FIX = longer-horizon SR (higher gamma).
CITED@notes/research_drill_natural_analog_hippocampal_DEEPER_3x_2026-06-07.md:chunk019
(hippocampal multi-scale SR: dorsal=short gamma / small fields; ventral=long gamma / large
fields; Stachenfeld-2017). Prior-work check: substrate-KB concept query top hit cosine=0.271
(< 0.30) -> NO prior arc CELL; genuinely novel. The cited hippocampal note grounds the fix.

## Design (controlled horizon comparison)
Train SR M at multiple gammas on the SAME rollout transitions (identical minibatch draws ->
only gamma differs). Two swept axes:
- gamma (SR horizon): BASELINE 0.85 (v2) vs DEEPER 0.95, 0.99 (the fix).
- n_ops (branching / FAIRNESS lever, analogous to v2's V lever): 2 vs 4. Lower branching
  raises per-hop additive so the compounded baseline lands in band at d6 -> a FAIR d6 regime
  where the closure contract can render. n_ops=4 reproduces the v2 d6 floor (Gate-D control).

## Arms (paired; share E, W_ops, and the SAME test chains per (regime,seed))
v1_no_goal | additive_baseline (SR-indep) | cfrpe_control_identity (identity-reach foil) |
oracle (ceiling) | gonogo_g0.85 (BASELINE-SR) | gonogo_g0.95 | gonogo_g0.99 (DEEPER-SR fix).

## Discriminators (per regime, per gamma)
headroom = oracle - additive; closure[g] = (gonogo[g]-additive)/headroom;
gonogo_lift[g] = gonogo[g]-additive; dynamics_lift[g] = gonogo[g]-control_identity;
reach_rank[g] (chance 1/n_ops); horizon_attributable = closure[deep]-closure[baseline].

## PASS / FAIL bands (envelope-fail-bands; META_RULE_L strict floor)
- HARD_PASS: EXISTS a FAIR d6 regime (0.05<additive<0.95) where a DEEPER-SR (gamma>0.85)
  has closure>=0.25 AND gonogo_lift>0.05 AND reach_tcos_corr<0.85 AND dynamics_lift>0.05 AND
  sign_p<0.05 AND reach_rank>1/n_ops+0.05 AND oracle>=0.90 AND cv<0.10 (FULL only) AND no
  af_collision. => control extends past depth-4 (not a shallow-only device).
  HONESTY GUARD: `horizon_is_the_lever` = (horizon_attributable>0.05). If HARD_PASS fires but
  the deeper-horizon fix did NOT beat baseline-SR at that regime, verdict_msg is marked
  `[EXTENDS_VIA_BRANCHING_..._NOT_the_lever]` so it cannot be misread as "horizon fix proven".
- HARD_FAIL_FIX_CANT_EXTEND_PAST_D4: fair d6 regime(s) exist AND at ALL of them EVERY gamma
  (baseline AND deeper) has gonogo_lift<=0.05 (control genuinely shallow-depth -- honest bound).
- MIDDLE_BAND_*: fair d6 helps (some gamma gonogo_lift>0.05) but no deeper-SR clears the full
  HP bar (below 0.25 OR cv>=0.10 OR not dynamics-attributable OR baseline-gamma-only extends).
- INCONCLUSIVE_NO_FAIR_REGIME: no d6 regime lands additive in band (REGIME-MISS, not
  structural) -- reach_rank mechanism signal still reported.
Reported regardless: reach_rank d4-vs-d6 for baseline-SR AND deeper-SR per (V,n_ops) group.

## SCHEMA-VET fields
- cardinality_ok: EXPECTED_N_UNITS = n_arms(7) * n_seeds(5) * n_regimes(6) = 210 (FULL).
- arms_differ_verified: gonogo[g] vs additive op-trace hash per seed; exempt when best_wr==0.
- final_metrics_atomicity: tmp_replace (os.replace).
- except SystemExit: raise BEFORE except Exception (no BaseException). Grep-gate: PASS.
- baseline_in_band (META_RULE_AG): per-regime 0.05<additive<0.95; n_ops=2 d6 is the fair
  candidate. MEASURED@smoke op2_V300_d6 additive=0.118 (FAIR); op4_V300_d6 additive=0.007
  (floored/unfair, reproduces v2). Fairness lever CONFIRMED at smoke.
- calibration_check: adaptive_with_discriminator_gate (adaptive cf-RPE LR + reach_rank gate).
- crlb_n/a: accuracy-closure has no single closed-form noise floor; reachability by feasibility
  (v2 measured closure=0.66 at fair d4; reach_rank>chance at d6).
- effective_vs_nominal (Gate A): n_ops directly sets reach_rank chance; gamma directly
  parametrizes train_sr_transport. sweep_alignment_verdict: ALIGNED.
- positive_control (Gate D): n_ops=4 V1200 d4 reproduces v2 fair-d4 (cited gonogo~0.653,
  closure~0.66, reach_rank~0.69); n_ops=4 V1200 d6 reproduces v2 d6 floor. tolerance 0.10.
- discriminating_fraction (Gate B): design intentionally spans floored (op4_d6, diagnosis) and
  in-band (op2, gonogo~0.3-0.5) regimes; discriminating regimes >= 0.30 of grid.
- functional_requirements: (1) per-hop op-selection toward a distant goal -> SR reach value;
  (2) extend credit horizon to depth-6 -> higher gamma (the fix); (3) fair measurability ->
  branching lever. All mapped to existing/parametrized primitives.
- defensive_error_checking: passed_all_4 (start_marker, crash_diagnostic, heartbeat, chunked
  via resumable_seeds per-seed partial + fatal-flag).
- progress_logging: print_flush_true (line-buffered + flush per line + per (seed,V,n_ops,gamma)
  print; per-seed heartbeat). FULL timeout_s >= 1800.

## Compute architecture
(a) batched-GPU. SR-TD training (per gamma), operator application, cleanup, reach = batched
matmuls on cuda-if-available. Chains batched; within-chain hops sequential (genuine
dependency). Storage: sharded (each op its own W; M a learned value operator). No bundled store.
FULL strongly prefers overnight_queue (GPU) -- 45 SR trains at N=8192.

## Discriminator-survives-scale (option C)
Smoke holds N/V == FULL per (V,n_ops) AND IDENTICAL decision depths {4,6} -> per-hop cleanup
difficulty AND depth-dependence match FULL. Smoke is a discriminator PREVIEW at matched N/V +
matched depth. Caveat: at N=2048 the reach signal is cleanup-noise limited (reach_rank ~0.40-0.45
at n_ops=4 vs 0.69 at N=8192); the gamma (horizon) effect may be MASKED by cleanup noise at
smoke scale and only resolve at N=8192 -- which is exactly what FULL measures.

## SMOKE RESULT (MEASURED@data/exp_pfc_gate_cfrpe_deeper_regime_v1_smoke/metrics.json)
N=2048, 3 seeds, gammas {0.85,0.95}, regimes {op4_V300_d4, op4_V300_d6, op2_V300_d6}, 136s wall
(<180s gate), cardinality 54/54. verdict=HARD_PASS
[EXTENDS_VIA_BRANCHING_horizon_attributable=-0.008_NOT_the_lever].
- FAIR d6 exists: op2_V300_d6 additive=0.118 (in band); op4_V300_d6 additive=0.007 (floored).
- Gate discriminates: gonogo=0.382 vs additive=0.118, sign_p=1.4e-8, reach_tcos_corr=-0.104,
  dynamics_lift=0.264, closure=0.306, oracle=0.979.
- MECHANISM signal (op4_V300): baseline-SR reach_rank d4=0.455 -> d6=0.403 (degradation=0.052,
  reproduces v2 direction); deeper-SR (g0.95) reach_rank d6=0.411 (deep-base@d6=+0.008 -- tiny
  positive at N=2048).
- HONEST READ: at N=2048 the branching lever, NOT the horizon fix, extends control
  (horizon_is_the_lever=False). FULL (N=8192 sharper reach + gamma to 0.99) is required to
  measure whether the horizon effect is real at scale. cv=0.143 at smoke (n_test=48) -> FULL
  n_test=240 should shrink it; FULL enforces cv<0.10 (risk: MIDDLE_BAND_CV_TOO_HIGH if it
  persists). This is designed uncertainty, honestly surfaced -- NOT an over-claim.

## FULL config (staged; do NOT self-dispatch)
N=8192, seeds [7,17,23,31,41], gammas [0.85,0.95,0.99], regimes {op4_V1200_d4, op4_V1200_d6,
op2_V800_d4, op2_V800_d6, op2_V1200_d4, op2_V1200_d6}, SR_STEPS=8000, SR_BATCH=256,
n_train=300 n_test=240, rollout_per_V=50. EXPECTED_N_UNITS=210.
Recommended queue: overnight_queue (GPU). Recommended --timeout: 10800s (3h; expected ~80-100min;
per-seed checkpoint/resume protects partials on timeout-kill).
