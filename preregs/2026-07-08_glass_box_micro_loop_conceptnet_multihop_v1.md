# Pre-reg: glass_box_micro_loop_conceptnet_multihop_v1

Date: 2026-07-08
Author: exp_dev (Opus 4.8 1M, agent-spawn)
Cell: experiments/exp_glass_box_micro_loop_conceptnet_multihop_v1.py
Extends (CG certified): experiments/exp_glass_box_micro_loop_retrieve_gate_audit_requery_v1.py (commit ba552930a)

## Objective
Extend the CG-certified glass-box reasoning micro-loop (retrieve -> gate/self-audit -> WM-mediated re-query
-> commit, every hop Merkle-audited + hand-editable) from its clean engineered TOY regime (accB saturated at
~1.0 = ceiling) to REAL ingested ConceptNet knowledge. The loop answers genuine MULTI-HOP relational queries
over the real CN word-graph: resolve B given a real 2-hop chain X -CN_SYNONYM-> A -IS_A-> B (69,292 such
chains in data/substrate_index/concept/relations.jsonl -- 188,852 loaded edges, syn_src=58,855 isa_src=50,512).
The difficulty is GRADED by real graph structure so accB is NON-ceiling (< 0.95) -- this measures
generalization to ingested knowledge, not a repeat of the toy ceiling. Directly attacks the CG cert's scope
caveat ("mechanism works on a toy" != "multi-hop reasoning in the wild").

## Mechanism (reused certified parts; GPU cells NOT re-run)
- Merkle audit-replay TRANSCRIBED VERBATIM from exp_reasoning_chain_replay_v1 (HARD_PASS).
- attention-routing arbitration margin gate (exp_substrate_gen_lm_combinedgate_recency_content_v8, CHAIN_GRADE).
- BG Go/NoGo value-gate accept/re-query (exp_pfc_bg_composed_attention_value_gate_v1).
Brain grounding: notes/research_neural_reasoning_loop_mechanism_inventory_2026-07-08.md (PFC->hippocampal
retrieval-in-service-of-inference; WM active-slot re-binding; cortico-BG-thalamic Go/NoGo).

## Regime (weak-first, on REAL chains)
Mixed per-seed corpus the loop cannot tell apart a priori:
- EASY (50%): real 1-hop edge X -IS_A-> B; X is a DIRECT key in the global IS_A store -> single shot resolves.
- HARD (50%): real 2-hop chain X -CN_SYNONYM-> A -IS_A-> B; B is keyed by the BRIDGE A, and X has NO IS_A edge
  in the store (enforced: B not in isa[X] AND hard anchors excluded from ISA distractors), so a single shot
  from X lands on NOISE. Only WM-mediated re-query (retrieve A from the CN_SYNONYM store, re-bind into the
  IS_A store) resolves it.
Random bipolar codes are assigned to real node IDs (semantics DECOUPLED from store-codes per
reference_correlation_hurts_associative_store_capacity_decouple_from_retrieval_2026-07-08). Stores are GLOBAL
per-relation bundles of real sampled edges (real hubs / branching / co-typed distractors).

## Arms
ARM_A_SINGLE_SHOT (baseline; commit shot), ARM_B_WM_REQUERY (gated: margin>=tau => Go else WM re-query),
ARM_B_SCRAMBLE (gated but re-query with RANDOM bridge; telemetry control), ARM_ALWAYS_REQUERY (never accept
shot), ARM_ORACLE_BRIDGE (hand true bridge into ISA; hop-2 positive control on HARD subset).

## Contract / bands
HARD_PASS: resolve_lift(accB-accA) >= 0.25 AND gate_route_margin(accB-accALWAYS) >= 0.15 AND sign_p < 0.05
  AND accB <= 0.95 (NON-CEILING) AND accA_hard <= 0.15 (discriminator fires: single-shot fails multi-hop)
  AND gate_separation >= 0.10 AND gate_routing_acc >= 0.85 AND scramble_gap >= 0.25 AND oracle_bridge_acc
  >= 0.85 AND hop1_retrieve_acc >= 0.80 AND deterministic_replay == 1.0 AND merkle_verify == 1.0 AND
  tamper_detect == 1.0 AND causal_edit_flip >= 0.80 AND arms_differ.
SATURATION_TOO_EASY: accB > 0.95 (regime not graded hard enough; raise store capacity M; NOT a HARD_PASS).
MIDDLE_BAND: resolve_lift in [0.10,0.25) OR gate_separation in [0.05,0.10) OR causal_edit_flip in [0.50,0.80)
  OR gate_route_margin in [0.05,0.15).
HARD_FAIL: resolve_lift < 0.10 (loop no better than single-shot on real chains) OR tamper_detect < 1.0 OR
  deterministic_replay < 1.0 (audit breaks on real data).
INCONCLUSIVE_TAUTOLOGICAL_METRIC: scramble_gap < 0.10 OR gate_separation < 0.05.
INCONCLUSIVE_RETRIEVAL_BROKEN: oracle_bridge_acc < 0.85 OR hop1_retrieve_acc < 0.80 (substrate retrieval did
  not reproduce at the real-graph regime -> downstream untrustworthy).
INCONCLUSIVE_DISCRIMINATOR_DEAD: accA_hard > 0.15 (single-shot solves the multi-hop -> not a real 2-hop test).

## SMOKE RESULT (MEASURED@data/exp_glass_box_micro_loop_conceptnet_multihop_v1_smoke/metrics.json; 3 seeds [7,17,23], N=4096, M_SYN=100, M_ISA=150)
verdict = HARD_PASS. accA=0.487 accB=0.883 (NON-CEILING) accAlways=0.546 accScr=0.450 accOracle=0.975
accA_hard=0.000 (discriminator fires) | resolve_lift=0.396 route_margin=0.337 scramble_gap=0.433
gate_sep=0.344 routing=0.888 hop1=1.000 | det=1.000 verify=1.000 tamper=1.000 causal_flip=1.000 sign_p=0.0000.
Per-seed accB consistent [0.875, 0.887].

## Config (smoke == full on N and store capacity; discriminator-survives-scale option A)
- N_DIM = 4096 (smoke == full)
- M_SYN = 100, M_ISA = 150 (ABSOLUTE store capacities, smoke == full -> identical per-hop difficulty)
- TAU_GATE = 0.11 (single fixed value derived from measured margin physics; NOT tuned per-seed)
- FRAC_EASY = 0.5
- smoke: N_HARD=N_EASY=40, seeds [7,17,23]; full: N_HARD=N_EASY=120, seeds [7,17,23,31,41]
- EXPECTED_N_UNITS = len(SEEDS)

## SCHEMA-VET fields
- cardinality_ok: true (EXPECTED_N_UNITS = len(SEEDS); verdict counts completed seeds; HARD_FAIL_CARDINALITY on shortfall)
- arms_differ_verified: true (SHA256 of per-arm committed-answer streams; 4 core arms distinct MEASURED@smoke)
- arms_differ_exempted: [[ARM_ALWAYS_REQUERY, ARM_ORACLE_BRIDGE]] (coincide iff hop1==1.0; measured property)
- final_metrics_atomicity: tmp_replace (os.replace on metrics.json)
- except-ordering: except SystemExit: raise before except Exception (no BaseException); grep-verified clean
- crlb_n/a: "accuracy-gap discriminator; no single closed-form noise floor." Reachability by bundle-SNR:
  top1 reliable while M < N/(2 ln V); at N=4096, V~452, 2 ln V ~ 12.2 -> M<~336; M_ISA=150 well inside ->
  oracle_bridge ~0.975 MEASURED (retrieval reproduces AND leaves headroom); accB = hop1 x hop2 -> non-ceiling.
- discriminator_reachability: true (HARD_PASS gates reachable AND met at smoke).
- baseline_in_band: true (ARM_A baseline accA=0.487 MEASURED, strictly inside (0.05, 0.95)).
- discriminator_survives_scale: option A (smoke N == full N == 4096; smoke M == full M; only n_trials/seeds differ).
- HP_SCOPE: resolve_lift/gate_route_margin/gate_separation/gate_routing_acc/scramble_gap/accB_non_ceiling/
  accA_hard_discriminator/causal_edit_flip/sign_p apply to ARM_B vs {ARM_A, ARM_ALWAYS, ARM_B_SCRAMBLE}.
  ARM_ORACLE_BRIDGE carries only the oracle_bridge_acc >= 0.85 retrieval-ceiling rail (positive control).
- calibration_check: default_ok_for_this_regime -- TAU_GATE=0.11 derived a-priori from measured marginA
  physics (hard mean~0.06 p90~0.12; easy median~0.39) as a SINGLE fixed value, not tuned per-seed; verified
  telemetry-sensitive by gate_separation=0.344 and scramble_gap=0.433 MEASURED.
- cell_chunked: false (multi-seed within one cell; fast ~40s full; per-seed None-guard on corpus shortage).
- start_marker_written: true
- crash_diagnostic_present: true (Exception -> CELL_CRASHED metrics.json + traceback)
- heartbeat_present: true (_heartbeat.jsonl per seed)
- defensive_error_checking: passed_all_4_patterns
- progress_logging: print_flush_true (line-buffered stdout + flush=True per progress line; timeout well under 1800s)

## §15 test-design gates
- sweep_alignment_verdict: ALIGNED (no parameter sweep; single fixed regime. M_SYN/M_ISA/N are held constant
  smoke==full so per-hop difficulty is identical.)
- discriminating_fraction: n/a (no sweep axis). accB=0.883 lands in the graded-difficulty band [<=0.95, >accA]
  by construction+measurement; accA_hard=0.000 confirms the HARD subset is genuinely 2-hop.
- composition_edges:
  - from: hop1_cleanup (CN_SYNONYM store unbind)  to: hop2_requery (IS_A store bind of WM bridge)
    A_natural_output_shape: node-id + bipolar code E[bridge_hat] (N-dim)
    B_natural_input_shape: bipolar code bound into IS_A store (N-dim)
    verdict: SHAPE_MATCH (both are N-dim bipolar codes over the shared codebook E)
- positive_control_arms:
  - arm: ARM_ORACLE_BRIDGE (hop-2 retrieval given the TRUE bridge)
    primitive: bipolar bundle single-key unbind + cleanup
    cited_prior: base cell exp_glass_box_micro_loop_retrieve_gate_audit_requery_v1 (oracle_bridge >= 0.90 synthetic)
    test_regime: {N: 4096, M_ISA: 150, V ~452, codes: random bipolar over REAL node ids}
    tolerance: retrieval reproduces if oracle_bridge_acc >= 0.85; MEASURED@smoke = 0.975 (reproduces).
    regime_extension_audit: SHAPE_DRIFT (synthetic disjoint pairs -> real global co-typed bundle) documented;
      risk absorbed by the oracle_bridge >= 0.85 gate (INCONCLUSIVE_RETRIEVAL_BROKEN if it fails).
  - hop1_retrieve_acc >= 0.80 is the hop-1 retrieval positive control (MEASURED@smoke = 1.000).
- functional_requirements:
  1. Retrieve the CN_SYNONYM bridge A from X (WM active-slot) -> hop1_cleanup (bundle unbind + cleanup).
  2. Detect single-shot failure to decide re-query -> arbitration-margin gate (v8 content-relevance margin).
  3. Decide commit-vs-requery -> BG Go/NoGo value-gate (margin >= TAU_GATE).
  4. Compose hop-2 from the WM bridge -> re-bind bridge into IS_A store + cleanup.
  5. Log + audit every hop, hand-editable -> Merkle chain (reasoning_chain_replay helpers).
  6. Prove the log is causally load-bearing -> causal hand-edit re-runs downstream recompute + fires tamper.

## Dispatch
Target queue: remote_cpu_queue (FULL CPU; local_cpu_queue is SMOKE-ONLY per USER-lock 2026-07-01).
Timeout: 900s (full ~40s measured-extrapolated from 6s smoke; generous margin; well under 1800s).
Pause-gated: FULL dispatch deferred while pause_state ACTIVE.
