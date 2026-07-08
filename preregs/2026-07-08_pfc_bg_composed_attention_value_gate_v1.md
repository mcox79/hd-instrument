# Pre-registration: pfc_bg_composed_attention_value_gate_v1

Date: 2026-07-08
Author: exp_dev (Opus 4.8 1M, agent-spawn)
Cell: experiments/exp_pfc_bg_composed_attention_value_gate_v1.py
Proposal: notes/research_value_based_action_selection_basal_ganglia_2026-07-08.md
Prior-work check (substrate-KB concept-query): top hit "B1. Basal ganglia action selection" cosine=0.4893
  (research-drill notes), generic; NO prior cell composes v8-attention into cfrpe Go/NoGo (research grep of
  exp_pfc_gate_* x combinedgate/contentgate lineage confirms the two gate families never wired). GENUINELY NOVEL.

## What
Compose two independently-certified brain-component gates, both reused UNCHANGED, only the goal SOURCE swapped
per arm:
- (A) v8 COMBINED attention-routing INPUT gate (exp_substrate_gen_lm_combinedgate_recency_content_v8_n8192_gpu,
  commit 4227e7e97, CHAIN_GRADE): softmax(content_rel/GATE_TAU + recency_bias) selects the right slot.
- (B) cfrpe Go/NoGo value OUTPUT gate (exp_pfc_gate_cfrpe_trained_v2, HARD_PASS; MEASURED V1200_d4
  gonogo=0.653 additive=0.053 oracle=0.962 closure=0.661): learned SR reach trained by the cfrpe RPE
  delta-rule feeds a WTA actor.
The v8 gate soft-pools a K-slot goal-cue window -> goal_hat -> fed as the goal into the unchanged cfrpe
Go/NoGo actor for a multi-hop navigation task. Task-correct requires BOTH: attention finds the right goal,
AND the value-gate selects the right actions given it. Empirical test of Chatham & Badre (2021): PFC/BG
input/output gating as one composable Go/NoGo primitive.

## Regime (pinned to the known-good spot; do NOT re-discover)
FULL: N=8192, V=1200 (N/V=6.83, cfrpe FAIR moderate), decision_depth=4, K in {4,6}, seeds {7,17,23,31,41},
  SR_STEPS=8000, SR_BATCH=256, rollout ~50*V, cue_q=0.25 (v8 headline; > arb boundary q*=0.15), GATE_TAU=0.05,
  RECENCY_GAP_TARGET=3.0. Requires CUDA (overnight_queue).
SMOKE: N=2048, V=300 (N/V=6.83 == FULL), K in {4,6}, seeds {7,17}, SR_STEPS=1500 (preview-strength so
  reach_rank~0.66 ~ FULL 0.69), cue_snr LOWER than FULL (harder cue) -> discriminator PREVIEW.

## Arms (6; paired -- share E/W_ops/M/chains/goal-windows per (seed,K); differ only by goal source + action)
ORACLE_GOAL_GONOGO (ceiling; Gate-D reproduce of cfrpe), V8_GATE_GONOGO (THE TEST), RAW_UNIFORM_GONOGO
(attention-blind control), V8_GATE_SCRAMBLED_GONOGO (telemetry guard), V8_GATE_ADDITIVE (value-actor-blind
control), ORACLE_ACTION (nav ceiling / closure rail). w_reach==0 null reduction verified in self-test ST-REDUCE.

## Discriminators (headline K=6)
att_lift = V8_GATE - RAW_UNIFORM ; composition_tax = ORACLE_GOAL - V8_GATE ; scramble_gap = V8_GATE - SCRAMBLED
closure = att_lift / (ORACLE_GOAL - RAW_UNIFORM) ; value_actor_lift = V8_GATE - V8_GATE_ADDITIVE

## Bands (PROSPECTIVE; locked at import)
- HARD_PASS: closure>=0.25 AND att_lift>=0.15 AND scramble_gap>=0.30 AND composition_tax<=0.20 AND
  oracle_action>=0.90 AND ORACLE_GOAL in [0.45,0.85] (cfrpe reproduce) AND reach_rank_test>0.30 AND arms differ.
- MIDDLE_BAND: att_lift>=0.15 but composition_tax>0.20 OR closure<0.25 OR scramble_gap in [0.15,0.30).
- HARD_FAIL_COMPOSITION_ADDS_NOTHING: att_lift<0.15 (the two proven gates do not combine).
- INCONCLUSIVE_TAUTOLOGICAL_METRIC: scramble_gap<0.15 (NOT telemetry-sensitive; NOT a clean negative).
- INCONCLUSIVE guards: nav_ceiling_broken (oracle_action<0.90); oracle_goal_mismatch (out of reproduce band);
  no_attention_pressure (RAW >= oracle_goal-0.05).

## SCHEMA-VET fields
- cardinality_ok: EXPECTED_N_UNITS = len(SEEDS)*len(K_GRID)*len(ARMS) = 5*2*6 = 60 (FULL). Verdict counts units;
  HARD_FAIL_CARDINALITY_BREACH_META_RULE_H otherwise.
- arms_differ_verified: true (META_RULE_AF; per-seed op-trace hashes of the 4 gonogo goal-source arms must
  differ; af_collision flag). Smoke: af_collision=False both K.
- final_metrics_atomicity: tmp_replace (os.replace on metrics.json + crash-diag).
- except-ordering: except SystemExit: raise BEFORE except Exception (no BaseException / bare except; grep-clean).
- crlb_n/a: accuracy-gap discriminator; no single closed-form noise floor. Reachability by feasibility --
  cfrpe MEASURED gonogo=0.653 & v8 COMBINED~1.0 at this regime; SMOKE (preview SR) MEASURED att_lift=0.200
  scramble_gap=0.325 composition_tax=0.008 closure=0.960, all strictly inside HARD_PASS.
- discriminator_reachability: true (smoke preview lands HARD_PASS both K).
- baseline_in_band (META_RULE_AG): control is RAW_UNIFORM (must be handicapped: RAW < oracle_goal-0.05);
  ORACLE_ACTION rails >=0.90; ORACLE_GOAL in reproduce band. All enforced as guards; smoke: nav_rail=0.967,
  att_pressure=True, oracle_repro=True.
- discriminator survives scale (META_RULE_K / SCALE rule, option B+C): smoke holds N/V==FULL (6.83) so per-hop
  cleanup difficulty matches; cue_snr LOWER at smoke (harder cue); SR trained to reach_rank~FULL so att_lift
  previews the FULL headroom (NOT the under-trained-SR floor). Analytical: att_lift = closure*(ORACLE_GOAL-RAW);
  ORACLE_GOAL grows toward cfrpe MEASURED 0.653 at FULL V=1200 while RAW (blurred K-superposition goal,
  goal_cos~0.41 scale-invariant) stays flat -> headroom (and att_lift) expand at FULL.
- HP strictly above floor (META_RULE_L): all gates strict.
- HP_SCOPE: HP gates apply to V8_GATE_GONOGO vs {RAW_UNIFORM, ORACLE_GOAL, SCRAMBLED}; ORACLE_ACTION carries
  only the >=0.90 nav rail; ORACLE_GOAL carries only the reproduce band.
- calibration_check: default_ok_for_this_regime -- GATE_TAU=0.05, RECENCY_GAP_TARGET=3.0 (v8 a-priori, logit
  units, NOT tuned per-q). cfrpe alpha/w_reach TUNED on TRAIN with the ORACLE goal then FROZEN across arms ->
  actor unchanged; only goal source varies.
- §15 gates:
  A effective_vs_nominal: swept axis = K (goal-window size); effective K per gate = K; ALIGNED.
  B bracket_includes_discriminating_band: smoke MEASURED V8_GATE=0.700, RAW=0.500, ORACLE_GOAL=0.708 -- all in
    [0.30,0.70] discriminating band (not saturated / not floored); discriminating_fraction=1.0.
  C signal_shape_compatibility: edge v8_gate(pooled slot code, (B,N) unit vector) -> cfrpe actor goal_E
    ((B,N) unit vector). SHAPE_MATCH (both are N-dim unit-norm node-space codes; verified ST-READOUT +
    goal_cos telemetry).
  D reproduce_prior_chain_grade: ORACLE_GOAL_GONOGO reproduces cfrpe v2 gonogo (cited 0.653; reproduce band
    [0.45,0.85]; smoke MEASURED 0.708) AT TEST REGIME; ST-V8 reproduces v8 arbitration (recency argmax=K-1,
    goal_cos V8>>RAW/SCR) AT TEST REGIME. regime_extension_audit: synthetic->synthetic (both parents synthetic);
    SHAPE_MATCH.
  E functional_requirements: (1) find the right goal from a noisy K-slot window -> v8 combined gate;
    (2) select actions toward that goal over multi-hop -> cfrpe Go/NoGo reach actor. Both mapped to existing CG.
- defensive_error_checking: passed_all_4_patterns (start_marker, crash_diagnostic CELL_CRASHED+traceback,
  heartbeat _heartbeat.jsonl, per-seed fatal-flag). cell_chunked: false (single-V per seed; SR trained once).
- progress_logging: print_flush_true (line-buffered + flush=True per progress line + per-seed/K heartbeat).
- run_mode_verification: FULL landing must show run_mode=full (post-dispatch check by orchestrator).

## Numbers (tagged)
- cfrpe V1200_d4 gonogo=0.653 additive=0.053 oracle=0.962 closure=0.661
  MEASURED@data/exp_pfc_gate_cfrpe_trained_v2/metrics.json:per_regime.V1200_d4
- v8 COMBINED headline top1~1.0 (3/3 seeds) CITED@notes/research_value_based_action_selection_basal_ganglia_2026-07-08.md
- SMOKE (preview SR) att_lift=0.200 scramble_gap=0.325 composition_tax=0.008 closure=0.960 ORACLE_GOAL=0.708
  reach_rank=0.658 MEASURED@data/exp_pfc_bg_composed_attention_value_gate_v1_smoke/metrics.json
- arb boundary q* = GATE_TAU*RECENCY_GAP_TARGET = 0.15 THEORETICAL@ v8 biased-competition boundary
- FULL HARD_PASS P_deflated=0.38 HYPOTHESIZED@notes/research_value_based_action_selection_basal_ganglia_2026-07-08.md

## Compute architecture
(a) batched-GPU. SR-TD training, operator application, cleanup, reach, v8 gate pooling are batched matmuls on
cuda. SR trained ONCE per seed (single V) -> cheaper than cfrpe v2. Chains batched; within-chain hops sequential
(genuine dependency). Storage: sharded (each op its own W; M is a learned value operator; goal-cue is a
single-hop attention read, no composition store). FULL requires cuda -> overnight_queue.

## Dispatch
FULL -> overnight_queue (GPU): N=8192 codebook cleanup over V=1200 per hop/op/arm + SR 8000 steps at N=8192,
5 seeds; matmul-heavy, GPU-batching-mandatory. Timeout 5400s (generous; flush logging keeps it diagnosable).
