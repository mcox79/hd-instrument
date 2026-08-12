"""
A5-gated atomize: HEADLINE LANDED-VET (AUDIT-ONLY, XHIGH) of glass_box_micro_loop_conceptnet_multihop_v1.
Extends the toy-regime glass-box reasoning micro-loop (commit ba552930a, CG) to REAL ingested ConceptNet
2-hop chains at NON-CEILING difficulty. Directly REMOVES the toy atom's locked caveat (1) ("accB=1.000 is
ceiling-saturation on an engineered clean regime, NOT multi-hop-reasoning-in-the-wild") -- this is the exact
"capacity-stress / non-ceiling" extension the toy atom's OWN revival criterion (1) called for.

CELL: experiments/exp_glass_box_micro_loop_conceptnet_multihop_v1.py (commit 200b66c3f -- N 4096->8192 fix)
METRICS: force-pulled from marsh@home:C:/dev/hd-instrument/data/exp_glass_box_micro_loop_conceptnet_multihop_v1/
  metrics.json (LOCAL copy was STALE = prior N=4096 INCONCLUSIVE run; verdict HARD_PASS on the N=8192 remote run;
  5 seeds 7/17/23/31/41, N=8192 V~580 n_trials=240/seed n_hard=n_easy=120 n_isa_edges=240 n_syn_edges=120
  frac_easy=0.5 tau_gate=0.11, real_graph=True, rel1=CN_SYNONYM rel2=IS_A; 5/5 units).

INDEPENDENT OFF-DISK RECOMPUTE (.venv python off per_seed[], this session -- all 14 aggregates matched EXACTLY):
  P1 NON-CEILING GENUINE (not saturation-vacuous): accB per seed [0.958,0.942,0.925,0.929,0.933] mean 0.9375
    (mean <0.95 passes; ONLY seed7 individually 0.958>0.95). accA_hard=0.000 all 5 seeds -> single-shot on the
    HARD multi-hop lands on noise (discriminator FIRES at the real 240-edge store). Derived from identities
    (accA=.5*easy+.5*hard, accA_hard=0): implied accA_easy~0.99, implied hard-subset accB ~0.85-0.917 vs
    oracle-hard 0.99 -> a REAL ~10-15pp headroom to ceiling on the hard subset. Non-ceiling is genuine.
  P2 GENUINE MULTI-HOP (not single-hop lookup): resolve_lift=accB-accA=0.44 (floor 0.25). ARM_ALWAYS_REQUERY
    ~0.4975 (= accA!) because forcing re-query BREAKS easy (mirror of accA: right on hard, wrong on easy) ->
    gate_route_margin=accB-accAlways=0.44 proves the GATE ROUTING carries B, not re-query alone. hop-2 uses the
    RETRIEVED bridge_hat (cleanup(bind(anchor,SYN))), NOT ground-truth -> real composition (hop1 output feeds
    hop2). Paired asymmetry n_b_only:n_a_only per seed [111:1,109:2,105:3,108:3,106:2] (vs toy 495:0) sign_p~2.5e-12.
  P3 GLASS-BOX AUDIT HOLDS ON REAL CHAINS: causal_edit_flip=1.0, causal_edit_tamper=1.0, tamper_detect=1.0,
    merkle_verify=1.0, deterministic_replay=1.0 all 5 seeds; n_causal_trials [111,109,105,108,106] (HARD+B-correct
    trials, substantial N). causal_hand_edit RE-RUNS cleanup(bind(E[edited_bridge],ISA),E) on the REAL-graph ISA
    bundle -> recomputed answer flips AND edited Merkle steps break the committed root. Genuinely recomputed.
  P4 TELEMETRY-SENSITIVE + NOT PINNED: ARM_B_SCRAMBLE (re-query with RANDOM bridge) COLLAPSES to baseline
    (accScr 0.488) -> scramble_gap=0.449 (floor 0.25) proves WM CONTENT resolves, metric reads the data.
    gate_separation=margin_easy-margin_hard=0.470-0.050=0.420 (floor 0.10) moves per seed. NO headline metric is
    analytically pinned (scramble arm demonstrates each CAN be ~0). cv on every headline metric 0.006-0.026
    (max 0.046 margin_hard) -- far inside CG bar. All 14 means reproduce EXACTLY from per_seed.
  P5 HONEST SCOPE: "real ConceptNet knowledge" = real GRAPH TOPOLOGY (real edges/hubs/branching/co-typed
    distractors from 188,852 loaded edges; 240-edge single-cue ISA store at 37% of the N=8192 top1 wall), with
    RANDOM bipolar codes decoupled from semantics. Certifies multi-hop RELATIONAL retrieval + self-audit routing
    over real graph STRUCTURE at non-ceiling; does NOT certify semantic-embedding reasoning or open-domain /
    arbitrary multi-hop planning (fixed 2-hop X-CN_SYNONYM->A-IS_A->B template, 2 relations, V~580 sampled subgraph).

WHY THIS IS NEW (not a rediscovery of the toy atom, July-1 INT8 pattern does NOT apply): the toy atom
  (ba552930a) accB=1.000 CEILING on an engineered near-lossless regime (M/N=20/4096, orthogonal codes) and
  EXPLICITLY locked caveat (1) "NOT multi-hop-reasoning-in-the-wild" + revival criterion (1) "capacity-stress /
  noisy-readout: does resolve_lift survive when accB is NOT at ceiling". THIS cell answers that criterion: YES.
  The real graph genuinely STRESSES the store -- PROVEN by the fact the prior N=4096 run BROKE the oracle
  positive control (0.825<0.85 INCONCLUSIVE_RETRIEVAL_BROKEN) exactly because the real 240-edge co-typed bundle
  sat at 74.6% of the wall. Doubling N to 8192 (37% of wall, SNR 5.84) reproduces retrieval clean AND the loop
  resolves at NON-CEILING accB=0.9375. Novel: real-graph generalization + non-ceiling, not the clean toy ceiling.

CROSS-ARC OVERLAP CHECK (substrate_query 'glass box multi-hop reasoning loop WM re-query gate self-audit
  merkle'): top cosine 0.333 (compliance/architecture NOTES: multi-hop pseudocode, PER-HOP-AUDIT anchor), NONE a
  landed cell at cosine>0.30. Direct parent = toy atom ba552930a (same MECHANISM); this extends+removes its
  ceiling caveat, does NOT supersede it. 0 pre-existing atoms for anchor 'conceptnet_multihop'.

TIER = CHAIN_GRADE. Every HARD_PASS gate cleared (resolve_lift 0.44>=0.25, accB 0.9375<=0.95 NON-CEILING,
  accA_hard 0.0<=0.15 discriminator fires, gate_route_margin 0.44>=0.15, gate_sep 0.42>=0.10, gate_routing 0.94
  >=0.85, scramble_gap 0.449>=0.25, oracle_bridge(hard-subset) 0.995>=0.85, hop1 1.0>=0.80, det/merkle/tamper 1.0,
  causal_flip 1.0>=0.80, sign_p 2.5e-12<0.05, arms_differ, cardinality 5/5). Genuine non-ceiling multi-hop
  relational reasoning over real ConceptNet graph structure with intact glass-box self-audit. Whole-cell
  HARD_PASS UPHELD at CHAIN_GRADE.
"""
from __future__ import annotations
import json, os, time
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
MATH_ATOMS = ROOT / "data/substrate_index/math/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"

ATOMIZED_BY = "skunkworks_atomize_2026_07_08_glass_box_micro_loop_conceptnet_multihop_v1_CHAIN_GRADE"
CELL_COMMIT = "200b66c3f"
TS = time.time()
TS_ISO = "2026-07-08T00:00:00Z"
SESSION = "2026-07-08_glass_box_micro_loop_conceptnet_multihop_v1_landed_vet_REAL_CONCEPTNET_NONCEILING_CG"

# direct parent: the toy-regime glass-box loop CG atom (extended + ceiling caveat removed, NOT superseded)
P_TOY = (
    "math::CHAIN_GRADE_glass_box_micro_loop_retrieve_gate_audit_requery_v1_GLASS_BOX_self_auditing_retrieve_gate_"
    "audit_requery_loop_composes_certified_attention_gate_value_gate_merkle_audit_gated_WM_mediated_requery_"
    "RESOLVES_weak_first_multihop_single_shot_CANNOT_resolve_lift_0p495_accB_1p000_vs_accA_0p505_ALL_5_seeds_7_17_"
    "23_31_41_paired_sign_495to0_pooled_99to0_perseed_controls_at_chance_accScramble_0p50_accAlways_0p50_scramble_"
    "gap_0p49to0p50_gate_route_margin_0p495_TELEMETRY_SENSITIVE_not_pinned_gate_separation_VARIES_perseed_0p7684to"
    "0p7897_spread_0p0213_margins_move_accScr_to_0p51_seed41_accAlways_to_0p505_seed23_31_CAUSAL_HAND_EDIT_holds_"
    "edit_logged_bridge_flips_downstream_recompute_AND_fires_merkle_tamper_causal_edit_flip_1p000_tamper_1p000_"
    "100of100_trials_perseed_positive_control_oracle_bridge_1p000_hop1_1p000_audit_rails_det_verify_1p000_CAVEAT_"
    "accB_1p000_is_CEILING_SATURATION_engineered_clean_regime_MoverN_20over4096_orthogonal_certifies_LOOP_"
    "MECHANISM_plus_glass_box_editability_NOT_multihop_reasoning_solved_in_wild_baseline_ARM_A_0p505_in_band_not_"
    "saturated_resolve_lift_identical_across_seeds_is_near_zero_hard_hit_rate_coincidence_NOT_pin_telemetry_moves_"
    "tamper_merkle_1p000_are_sha256_soundness_rails_not_discoveries_causal_flip_is_the_substantive_claim_composes_"
    "reasoning_chain_replay_merkle_rail_combinedgate_v8_arbitration_margin_pfc_bg_value_gate_cardinality_5of5_"
    "commit_ba552930a_2026-07-08"
)

atom = {
    "id": (
        "math::CHAIN_GRADE_glass_box_micro_loop_conceptnet_multihop_v1_REAL_CONCEPTNET_2HOP_NON_CEILING_the_"
        "certified_glass_box_retrieve_gate_audit_requery_loop_GENERALIZES_from_the_toy_ceiling_to_REAL_ingested_"
        "ConceptNet_2hop_chains_X_CN_SYNONYM_A_IS_A_B_gated_WM_mediated_requery_RESOLVES_what_single_shot_CANNOT_"
        "resolve_lift_0p440_accB_0p9375_NON_CEILING_vs_accA_0p4975_accA_hard_0p000_discriminator_FIRES_at_real_"
        "240edge_ISA_store_gate_route_margin_0p440_beats_always_requery_which_breaks_easy_paired_nb_only_105to111_"
        "vs_na_only_1to3_perseed_sign_p_2e12_scramble_collapses_to_baseline_scramble_gap_0p449_gate_sep_0p420_"
        "TELEMETRY_SENSITIVE_causal_hand_edit_flips_downstream_recompute_on_REAL_chains_AND_fires_merkle_tamper_"
        "causal_flip_1p000_n_causal_105to111_perseed_positive_control_oracle_bridge_hard_subset_0p995_hop1_1p000_"
        "audit_rails_det_merkle_tamper_1p000_all_5_seeds_7_17_23_31_41_cardinality_5of5_cv_under_0p05_REMOVES_toy_"
        "atom_caveat1_ceiling_saturation_answers_its_revival_criterion1_capacity_stress_nonceiling_SCOPE_real_"
        "graph_TOPOLOGY_random_codes_decoupled_from_semantics_NOT_semantic_embedding_reasoning_NOT_open_domain_"
        "fixed_2hop_2relation_V580_sampled_subgraph_composes_toy_loop_commit_200b66c3f_2026-07-08"
    ),
    "name": (
        "REAL-CONCEPTNET NON-CEILING glass-box multi-hop reasoning loop: the certified retrieve->gate(self-audit)"
        "->WM-mediated re-query->commit loop GENERALIZES from the engineered toy ceiling to REAL ingested "
        "ConceptNet 2-hop chains (X-CN_SYNONYM->A-IS_A->B). The gated WM re-query RESOLVES what a single shot "
        "CANNOT at NON-CEILING difficulty (resolve_lift=0.440, accB=0.9375 <=0.95 vs accA=0.4975, accA_hard=0.000 "
        "-> single-shot fails the multi-hop at the real 240-edge store), BEATS always-requery by routing "
        "(gate_route_margin=0.440; always-requery breaks easy), scramble collapses to baseline (scramble_gap="
        "0.449, telemetry-sensitive), and the causal HAND-EDIT flips the downstream recompute on REAL chains AND "
        "fires Merkle tamper (causal_flip=1.000, n_causal 105-111/seed). oracle-hard 0.995, hop1=1.000, "
        "det/merkle/tamper=1.000, all 5 seeds, cv<0.05. REMOVES the toy atom's ceiling caveat; answers its own "
        "revival criterion (capacity-stress/non-ceiling). SCOPE: real graph TOPOLOGY with random codes "
        "(not semantic-embedding reasoning, not open-domain; fixed 2-hop/2-relation, V~580). CHAIN_GRADE."
    ),
    "corpus": "math",
    "tier": "CHAIN_GRADE",
    "kind": "experiment_landed_vet",
    "cert_status": (
        "cg_glass_box_reasoning_loop_generalizes_to_real_conceptnet_2hop_chains_nonceiling_gated_wm_requery_"
        "resolves_what_single_shot_cannot_accB_0p9375_resolve_lift_0p440_accA_hard_0p000_gate_routing_load_"
        "bearing_scramble_collapses_telemetry_sensitive_causal_hand_edit_flips_downstream_on_real_chains_fires_"
        "merkle_tamper_5seed_robust_real_graph_topology_random_codes_removes_toy_ceiling_caveat"
    ),
    "cert_class": (
        "composed_retrieve_then_margin_self_audit_gate_go_nogo_then_wm_mediated_requery_bind_retrieved_bridge_hat_"
        "into_hop2_ISA_store_then_commit_every_hop_merkle_chained_over_a_mixed_easy_hard_corpus_of_REAL_conceptnet_"
        "2hop_chains_where_single_shot_resolves_easy_only_and_gated_loop_resolves_both_at_NON_CEILING_difficulty_"
        "graded_by_real_graph_structure_with_scramble_and_always_requery_controls_and_a_monitor_not_control_causal_"
        "hand_edit_of_the_logged_bridge_that_flips_the_downstream_recompute_and_breaks_the_committed_root_real_"
        "graph_topology_random_bipolar_codes_decoupled_from_semantics"
    ),
    "description": (
        "HEADLINE LANDED-VET (AUDIT-ONLY, XHIGH) of exp_glass_box_micro_loop_conceptnet_multihop_v1 (commit "
        "200b66c3f; run_mode=full; 5 seeds 7/17/23/31/41; N=8192 V~580 n_trials=240/seed n_hard=n_easy=120 "
        "n_isa_edges=240 n_syn_edges=120 frac_easy=0.5 tau_gate=0.11 real_graph=True rel1=CN_SYNONYM rel2=IS_A; "
        "5/5 units; verdict HARD_PASS). NOTE: the LOCAL metrics.json was STALE (= prior N=4096 run, verdict "
        "INCONCLUSIVE_RETRIEVAL_BROKEN); the reported N=8192 HARD_PASS was force-pulled from the remote runner "
        "(marsh@home) and VERIFIED off that data (Fix#28 filesystem-verify -- the headline was NOT in the local "
        "file). Extends the CG toy-regime glass-box loop (ba552930a) to REAL ingested ConceptNet 2-hop chains. "
        "THE LOOP (mechanism reused verbatim): hop-1 retrieves a CN_SYNONYM bridge A into WM (cleanup(bind(anchor,"
        "SYN))); the single-shot cleanup MARGIN into the IS_A store is the self-audit why-signal; a BG Go/NoGo "
        "value-gate commits the shot if margin>=tau=0.11 else re-queries by binding the RETRIEVED bridge_hat into "
        "the IS_A store; every hop is Merkle-chained. THE REAL-GRAPH REGIME (falsifiable, non-tautological): mixed "
        "per-seed corpus half EASY (real 1-hop X-IS_A->B, X is a direct IS_A key -> single shot resolves) half "
        "HARD (real 2-hop X-CN_SYNONYM->A-IS_A->B, X has NO IS_A edge -> single shot lands on noise; only WM "
        "re-query resolves). Codes are RANDOM bipolar over real node ids (semantics DECOUPLED from store-codes). "
        "ADVERSARIAL AUDIT (5 probes, all verified off per_seed[] NOT verdict_msg): (P1) NON-CEILING GENUINE not "
        "saturation-vacuous -- accB per seed [0.958,0.942,0.925,0.929,0.933] mean 0.9375 (<=0.95; only seed7 "
        "individually 0.958>0.95); accA_hard=0.000 all 5 seeds (single-shot on the multi-hop FAILS at the real "
        "240-edge store -> discriminator fires); implied hard-subset accB ~0.85-0.92 vs oracle-hard 0.99 -> a real "
        "~10-15pp headroom, NOT at ceiling. (P2) GENUINE MULTI-HOP not single-hop lookup -- resolve_lift=accB-accA"
        "=0.440 (floor 0.25); ARM_ALWAYS_REQUERY~0.4975 (mirror of accA: right on hard, wrong on easy) so "
        "gate_route_margin=accB-accAlways=0.440 proves the GATE ROUTING carries B not re-query alone; hop-2 uses "
        "the RETRIEVED bridge_hat not ground-truth (real composition, hop1 output feeds hop2); paired asymmetry "
        "n_b_only:n_a_only per seed [111:1,109:2,105:3,108:3,106:2], sign_p~2.5e-12. (P3) GLASS-BOX AUDIT HOLDS ON "
        "REAL CHAINS -- causal_edit_flip/causal_edit_tamper/tamper_detect/merkle_verify/deterministic_replay all "
        "[1.0 x5]; n_causal_trials [111,109,105,108,106] (HARD+B-correct trials); causal_hand_edit RE-RUNS "
        "cleanup(bind(E[edited_bridge],ISA),E) on the REAL-graph ISA bundle -> recomputed answer flips AND edited "
        "Merkle steps break the committed root. (P4) TELEMETRY-SENSITIVE + NOT PINNED -- ARM_B_SCRAMBLE (re-query "
        "with RANDOM bridge) COLLAPSES to baseline (accScr 0.488) -> scramble_gap=0.449 (floor 0.25): WM CONTENT "
        "resolves; gate_separation=margin_easy-margin_hard=0.470-0.050=0.420 (floor 0.10) moves per seed; NO "
        "headline metric is analytically pinned (scramble arm shows each CAN be ~0); cv on every headline 0.006-"
        "0.026 (max 0.046 margin_hard); all 14 means reproduce EXACTLY from per_seed. (P5) HONEST SCOPE -- 'real "
        "ConceptNet knowledge' = real GRAPH TOPOLOGY (real edges/hubs/branching/co-typed distractors from 188,852 "
        "loaded edges; the 240-edge single-cue ISA store sits at 37% of the N=8192 top1 wall) with RANDOM codes "
        "decoupled from semantics; certifies multi-hop RELATIONAL retrieval + self-audit routing over real graph "
        "STRUCTURE at non-ceiling, NOT semantic-embedding reasoning and NOT open-domain / arbitrary multi-hop "
        "planning (fixed 2-hop X-CN_SYNONYM->A-IS_A->B template, 2 relations, V~580 sampled subgraph). HARNESS: "
        "cardinality 5/5; oracle_bridge_acc (hard-subset, code line 715 np.mean(oracle_correct_hard)) 0.995>=0.85 "
        "positive control; hop1=1.000; 4 core arm_digests distinct each seed (ARM_ORACLE==ARM_ALWAYS exempted, "
        "coincide iff hop1==1.0 MEASURED). NON-CEILING CONFIRMED VIA THE N=4096 CONTRAST: the prior N=4096 run "
        "BROKE the oracle positive control (0.825<0.85 INCONCLUSIVE) precisely because the real 240-edge co-typed "
        "bundle sat at 74.6% of the wall -> PROOF the real graph genuinely stresses the store (unlike the toy's "
        "near-lossless M/N=20/4096). The N->8192 capacity fix (37% of wall, SNR 5.84) reproduces retrieval clean "
        "AND the loop resolves at NON-CEILING accB=0.9375. TIER = CHAIN_GRADE: every HARD_PASS gate cleared, all "
        "5 probes hold off-disk, discriminators telemetry-sensitive, glass-box audit intact on real chains, "
        "genuine real-graph generalization. REMOVES toy atom (ba552930a) caveat (1) and ANSWERS its revival "
        "criterion (1) (capacity-stress / non-ceiling). Composes the toy loop at the mechanism level (NOT "
        "superseded; cell NOT re-run). commit 200b66c3f 2026-07-08."
    ),
    "provenance": {
        "cell": "experiments/exp_glass_box_micro_loop_conceptnet_multihop_v1.py",
        "commit": CELL_COMMIT,
        "metrics_path": "data/exp_glass_box_micro_loop_conceptnet_multihop_v1/metrics.json",
        "metrics_source_note": (
            "LOCAL metrics.json was STALE (prior N=4096 INCONCLUSIVE_RETRIEVAL_BROKEN run). The N=8192 HARD_PASS "
            "run was force-pulled via scp from marsh@home:C:/dev/hd-instrument/... and cached at "
            "data/session_local/skunkworks/remote_conceptnet_multihop_v1_metrics.json; VET recompute ran off the "
            "pulled data. config_version confirms N=8192 real_graph=True."
        ),
        "prereg": "preregs/2026-07-08_glass_box_micro_loop_conceptnet_multihop_v1.md",
        "seeds": [7, 17, 23, 31, 41],
        "run_mode": "full",
        "whole_cell_verdict": "HARD_PASS",
        "audit_tier": "CHAIN_GRADE",
        "ts_iso": TS_ISO,
        "atomized_by": ATOMIZED_BY,
        "verified_off_data": True,
        "verified_off_data_note": (
            "Independent .venv recompute off per_seed[] (5/5 units) of the force-pulled N=8192 remote metrics. "
            "All 14 aggregates matched EXACTLY: accB [0.9583,0.9417,0.925,0.9292,0.9333] mean 0.9375 cv 0.0126; "
            "accA [0.5,0.4958,0.5,0.4917,0.5] mean 0.4975; accA_hard [0,0,0,0,0]; accAlways mean 0.4975; accScr "
            "mean 0.4883; accOracle(hard) [1,0.9917,0.9917,0.9917,1] mean 0.995; resolve_lift [0.4583,0.4458,"
            "0.425,0.4375,0.4333] mean 0.44 min 0.425; gate_route_margin mean 0.44 min 0.4292; scramble_gap mean "
            "0.449 min 0.4375; gate_separation mean 0.42 cv 0.0224; gate_routing_acc mean 0.94; hop1 1.0; "
            "margin_easy 0.470 margin_hard 0.050; causal_flip/tamper/merkle/det [1.0 x5]; n_causal [111,109,105,"
            "108,106]; n_b_only:n_a_only [111:1,109:2,105:3,108:3,106:2]; sign_p 2.53e-12. cv on every headline "
            "0.006-0.026 (max 0.046 margin_hard). oracle discrepancy resolved: code line 715 accOracle is "
            "hard-subset-only (np.mean(oracle_correct_hard)) vs accs['ARM_ORACLE_BRIDGE'] over all 240 -- both "
            "legit, not fabrication."
        ),
    },
    "verified_numbers": {
        "N": 8192, "V_range": [576, 584], "n_trials": 240, "n_hard": 120, "n_easy": 120,
        "n_isa_edges": 240, "n_syn_edges": 120, "frac_easy": 0.5, "tau_gate": 0.11, "real_graph": True,
        "rel1": "CN_SYNONYM", "rel2": "IS_A",
        "accB_per_seed": [0.9583333333333334, 0.9416666666666667, 0.925, 0.9291666666666667, 0.9333333333333333],
        "accB_mean": 0.9375, "accB_nonceiling_floor": 0.95, "accB_cv": 0.0126,
        "accB_seed7_over_0p95": True, "accB_mean_margin_below_0p95": 0.0125,
        "accA_per_seed": [0.5, 0.49583333333333335, 0.5, 0.49166666666666664, 0.5], "accA_mean": 0.4975,
        "accA_hard_per_seed": [0.0, 0.0, 0.0, 0.0, 0.0], "accA_hard_discriminator_floor": 0.15,
        "accAlways_mean": 0.4975, "accScramble_mean": 0.4883333333333334,
        "accOracle_hard_per_seed": [1.0, 0.9916666666666667, 0.9916666666666667, 0.9916666666666667, 1.0],
        "accOracle_hard_mean": 0.995, "accOracle_floor": 0.85,
        "resolve_lift_per_seed": [0.4583333333333334, 0.4458333333333333, 0.425, 0.4375, 0.4333333333333333],
        "resolve_lift_mean": 0.44, "resolve_lift_min": 0.425, "resolve_lift_floor": 0.25,
        "gate_route_margin_mean": 0.44, "gate_route_margin_min": 0.4292, "gate_route_margin_floor": 0.15,
        "scramble_gap_mean": 0.4492, "scramble_gap_min": 0.4375, "scramble_gap_floor": 0.25,
        "gate_separation_per_seed": [0.4289, 0.4022, 0.4225, 0.4203, 0.4263], "gate_separation_mean": 0.42003,
        "gate_separation_floor": 0.10, "gate_separation_cv": 0.0224,
        "gate_routing_acc_mean": 0.94, "gate_routing_floor": 0.85,
        "hop1_retrieve_acc": 1.0, "margin_easy_mean": 0.47047, "margin_hard_mean": 0.05044,
        "implied_accA_easy": 0.99, "implied_hard_subset_accB_range": [0.85, 0.917],
        "oracle_hard_headroom_pp": "10-15",
        "causal_edit_flip_per_seed": [1.0, 1.0, 1.0, 1.0, 1.0],
        "causal_edit_tamper_per_seed": [1.0, 1.0, 1.0, 1.0, 1.0],
        "tamper_detect_per_seed": [1.0, 1.0, 1.0, 1.0, 1.0],
        "merkle_verify": 1.0, "deterministic_replay": 1.0,
        "n_causal_trials_per_seed": [111, 109, 105, 108, 106],
        "n_b_only_per_seed": [111, 109, 105, 108, 106], "n_a_only_per_seed": [1, 2, 3, 3, 2],
        "sign_p": 2.526696448975139e-12, "sign_p_note": "same binom helper obs+1e-12 quirk as toy: CONSERVATIVE, still <<0.05",
        "cardinality_units": 5, "cardinality_expected": 5, "arm_digests_distinct_per_seed": 4,
        "all_14_means_reproduce_exactly": True, "max_headline_cv": 0.046,
        "n4096_prior_run_oracle_broke_at": 0.825, "n4096_wall_occupancy_pct": 74.6, "n8192_wall_occupancy_pct": 37.3,
    },
    "can_fail_discriminator_verdict": (
        "FIRES against REAL can-fail alternatives and is TELEMETRY-SENSITIVE (verified by seed perturbation + the "
        "N=4096 contrast, not just by low cv). (1) ARM_B_SCRAMBLE (gated but re-queries with a RANDOM bridge) "
        "could have replicated the gain if the benefit were merely 'a free second try'; it COLLAPSES to baseline "
        "(accScr 0.488, scramble_gap 0.449) -> the WM CONTENT (retrieved CN_SYNONYM bridge) is what resolves. "
        "(2) ARM_ALWAYS_REQUERY (never accept the shot) BREAKS easy trials (accAlways ~0.4975 == accA, the mirror) "
        "-> the GATE ROUTING is load-bearing, not the re-query alone (gate_route_margin 0.44). (3) accA_hard=0.000 "
        "-- single-shot CANNOT solve the multi-hop at the real 240-edge store (X has no IS_A edge -> noise); the "
        "INCONCLUSIVE_DISCRIMINATOR_DEAD branch (accA_hard>0.15) was reachable and did NOT fire. (4) The whole "
        "regime is NON-CEILING (accB 0.9375, hard-subset ~0.88 vs oracle-hard 0.99) so this is NOT saturation-"
        "vacuous; the SATURATION_TOO_EASY branch (accB>0.95) was reachable (seed7 individually 0.958) and the mean "
        "cleared it. (5) The N=4096 prior run BROKE the oracle positive control (0.825<0.85) -> the "
        "INCONCLUSIVE_RETRIEVAL_BROKEN failure branch is genuinely reachable and the real graph DOES stress the "
        "store; the N=8192 fix reproduces retrieval AND the loop. (6) causal_edit_flip could have coincided "
        "(recomputed answer == original) but flips on all n_causal 105-111/seed HARD+correct trials. Audit rails "
        "(tamper/merkle) are SHA256 near-certainties (soundness, not the discriminator)."
    ),
    "framing_corrections_vs_cell_author_and_director": [
        "HARD_PASS (cell verdict) UPHELD at CHAIN_GRADE off independent recompute of the FORCE-PULLED remote "
        "N=8192 metrics. All 5 adversarial probes hold off per_seed[]. Symmetric anti-negativity: do NOT deflate "
        "a genuine 5-seed-robust non-ceiling real-graph multi-hop reasoning result with an intact glass-box audit.",
        "FIX#28 / STALE-DATA CATCH (load-bearing): the LOCAL data/exp_.../metrics.json was the PRIOR N=4096 run "
        "(verdict INCONCLUSIVE_RETRIEVAL_BROKEN, accB=0.697, oracle=0.825) -- NOT the reported N=8192 HARD_PASS. "
        "The headline was verified ONLY after force-pulling the remote runner's metrics.json (config_version "
        "N=8192). Anyone re-VETing this from the local file alone would have wrongly concluded the cell failed. "
        "Verify OFF the actual landed data, and confirm the config_version N matches the claim.",
        "CITE CORRECTION (Director): the toy-loop origin was cited as 'db3e72699'; that hash is NOT present in the "
        "substrate. The actual toy-regime glass-box loop CG atom is cell commit ba552930a (anchor "
        "glass_box_micro_loop_retrieve_gate_audit_requery_v1). This atom composes/extends THAT atom.",
        "SCOPE QUALIFIER IS LOAD-BEARING (bake into any downstream framing; consistent with SUBSTRATE-KNOWS-"
        "NOTHING): 'real ConceptNet knowledge' means the real GRAPH TOPOLOGY (which nodes connect via CN_SYNONYM "
        "and IS_A -- real hubs, branching, co-typed distractors), NOT real semantic meaning. Codes are RANDOM "
        "bipolar assigned to node ids, DECOUPLED from semantics (per correlation-hurts-capacity). This certifies "
        "multi-hop RELATIONAL retrieval + self-audit routing over real graph STRUCTURE at non-ceiling; it does "
        "NOT certify semantic-embedding reasoning, and NOT open-domain / arbitrary multi-hop planning (the chain "
        "is a FIXED 2-hop X-CN_SYNONYM->A-IS_A->B template, 2 relations, V~580 sampled subgraph, 240-edge store). "
        "Still a genuine step up from the toy: the real graph PROVABLY stresses the store (the N=4096 oracle break).",
        "NON-CEILING margin is THIN and rests on the RIGHT evidence: accB mean 0.9375 is only 1.25pp below the "
        "0.95 non-ceiling floor and seed7 individually is 0.958 (>0.95). The non-ceiling CLAIM is therefore "
        "anchored NOT on the exact accB level but on (a) accA_hard=0.000 (the discriminator fires) and (b) the "
        "hard-subset headroom (implied accB~0.88 vs oracle-hard 0.99, ~10-15pp) -- both robust. If a re-run's "
        "accB mean ticks above 0.95 it becomes SATURATION_TOO_EASY (raise store capacity), NOT a stronger result.",
        "hop-1 retrieval is ITSELF saturated (hop1=1.000 exactly; the 120-edge SYN store is well inside the "
        "wall). The non-ceiling difficulty lives entirely in hop-2 + gate routing, not hop-1. The composition is "
        "still genuine (the RETRIEVED bridge_hat, not ground-truth, feeds hop-2), but do not frame hop-1 as stressed.",
    ],
    "revival_or_extension_criterion": (
        "CG scope LOCKED to: the composed retrieve->gate(margin self-audit)->WM-mediated re-query->commit loop "
        "with per-hop Merkle audit + causal hand-edit, on REAL ConceptNet 2-hop chains (X-CN_SYNONYM->A-IS_A->B) "
        "at N=8192, V~580, 240-edge ISA store / 120-edge SYN store, frac_easy=0.5, tau_gate=0.11, RANDOM bipolar "
        "codes decoupled from semantics, 5 seeds. EXTENSIONS (each a NEW cell, composes NOT supersedes): "
        "(1) DEEPER CHAINS -- >2 hops (3-4 hop chains); does the WM re-bind compose without a global chain bundle. "
        "(2) SEMANTIC (not random) CODES -- assign correlated/embedding-derived codes to nodes; does resolve_lift "
        "survive when store-codes carry semantic correlation (correlation-hurts-capacity predicts store pressure). "
        "(3) LARGER VOCAB / FULL-GRAPH single store -- push V and the ISA store toward the wall (the N=4096 break "
        "shows the boundary is real); at what store occupancy does the loop stop resolving. (4) MORE RELATIONS / "
        "arbitrary relation ordering (not fixed CN_SYNONYM->IS_A) -- open-ended relation planning. (5) LEARNED "
        "tau_gate adapted per-context. DEMOTION trigger: if a re-run shows accB rises >0.95 (saturation -- the "
        "non-ceiling claim would need a harder regime), OR the oracle positive control re-breaks (retrieval "
        "untrustworthy), OR resolve_lift drops below 0.10, OR scramble stops firing (scramble_gap<0.10), OR "
        "causal_edit_flip drops below 0.80."
    ),
    "composes": [P_TOY],
    "compose_note": (
        "This cell reuses the ENTIRE certified glass-box loop mechanism from the toy atom (ba552930a) VERBATIM "
        "(retrieve->margin-gate->WM re-query->commit + Merkle audit + causal hand-edit) and changes ONLY the "
        "regime: the engineered near-lossless corpus (V=256, M=20, orthogonal codes, accB=1.0 ceiling) is "
        "replaced by REAL sampled ConceptNet subgraphs (V~580, 240-edge co-typed ISA store, real hubs/branching, "
        "random bipolar codes) at NON-CEILING difficulty (accB=0.9375). The NOVEL contribution is the "
        "GENERALIZATION CLAIM: the loop mechanism + glass-box audit survive the transition from clean toy to real "
        "graph AND the resolve_lift survives when accB is NOT at ceiling -- which is EXACTLY the toy atom's own "
        "revival criterion (1) ('capacity-stress / noisy-readout: does resolve_lift survive when accB is not at "
        "ceiling'). The toy atom is NOT superseded (it certifies the mechanism at the clean regime); this atom "
        "amends the field with the real-graph non-ceiling result and REMOVES the toy atom's caveat (1) scope "
        "limitation. Transitively composes (via the toy atom) the reasoning_chain_replay Merkle rail, "
        "combinedgate_v8 arbitration margin, and pfc_bg Go/NoGo value-gate. Brain-grounding "
        "(research_neural_reasoning_loop_mechanism_inventory_2026-07-08): PFC->hippocampal retrieval-in-service-"
        "of-inference, WM active-slot re-binding, cortico-BG-thalamic Go/NoGo."
    ),
    "cross_arc_overlap_check": (
        "substrate_query 'glass box multi-hop reasoning loop WM re-query gate self-audit merkle' -> top cosine "
        "0.333 (compliance/architecture NOTES: 'Section 3 Multi-hop reasoning loop pseudocode' 0.333, "
        "'PER-HOP-AUDIT' anchor 0.328) -- surface char-trigram / design-note hits, NONE a landed cell at "
        "cosine>0.30. 0 pre-existing atoms for anchor 'conceptnet_multihop'. The DIRECT parent is the toy-regime "
        "glass-box loop atom ba552930a (SAME mechanism); this is its pre-registered real-graph / non-ceiling "
        "EXTENSION, which the toy atom's revival criterion (1) explicitly called for -- so it is NOT a "
        "rediscovery (the July-1 INT8-rediscovery pattern does NOT apply: the toy CANNOT distinguish saturation "
        "from genuine reasoning; this cell does, at non-ceiling on a real graph). Genuine NEW capability claim: "
        "real-graph generalization + non-ceiling multi-hop relational reasoning with intact glass-box audit."
    ),
    "anchor": "glass_box_micro_loop_conceptnet_multihop_v1",
    "cell_commit": CELL_COMMIT,
    "seeds": [7, 17, 23, 31, 41],
    "run_mode": "full",
    "cardinality_ok": True,
    "arms_differ_verified": True,
    "verified_off_data": True,
    "auditor": "hdi_skunkworks",
    "atomized_by": "hdi_skunkworks",
    "landed_VET_session": SESSION,
    "needs_orchestrator_store_sync": True,
    "ts": TS,
    "ts_iso": TS_ISO,
    "ts_added": TS_ISO,
    "aliases": [
        "real-ConceptNet non-ceiling glass-box multi-hop reasoning loop -- gated WM re-query resolves real 2-hop chains a single shot cannot; CHAIN_GRADE",
        "resolve_lift=0.440 accB=0.9375 (NON-CEILING) vs accA=0.4975, accA_hard=0.000 (single-shot fails multi-hop at real 240-edge store); all 5 seeds",
        "gate routing load-bearing: always-requery breaks easy (accAlways=accA=0.4975); scramble collapses to baseline (scramble_gap=0.449, telemetry-sensitive)",
        "causal hand-edit on REAL chains: edit logged bridge -> downstream recompute flips AND Merkle tamper fires (causal_flip=1.0, n_causal 105-111/seed)",
        "REMOVES toy atom ceiling caveat; answers its revival criterion (capacity-stress/non-ceiling); N=4096 oracle break proves the real graph stresses the store",
        "SCOPE: real graph TOPOLOGY + random codes decoupled from semantics -- NOT semantic-embedding reasoning, NOT open-domain (fixed 2-hop/2-relation V~580)",
        "glass_box_micro_loop_conceptnet_multihop_v1 landed-VET CHAIN_GRADE",
    ],
    "added_atom_id": None,
}
atom["added_atom_id"] = atom["id"]

ledger = {
    "ts": TS, "ts_iso": TS_ISO, "op": "add", "atom_id": atom["id"], "corpus": "math",
    "tier": "CHAIN_GRADE",
    "disposition": "chain_grade_new_capability_real_conceptnet_nonceiling_glass_box_multihop_reasoning_loop",
    "cert_status": atom["cert_status"],
    "cert_class": atom["cert_class"],
    "cert_increment_delta": {"CG": 1, "MM": 0, "HF": 0},
    "cert_delta": {"CG": 1, "MM": 0, "HF": 0},
    "cert_delta_note": (
        "CG +1: the certified glass-box reasoning micro-loop GENERALIZES from the engineered toy ceiling "
        "(ba552930a, accB=1.0) to REAL ingested ConceptNet 2-hop chains (X-CN_SYNONYM->A-IS_A->B) at NON-CEILING "
        "difficulty. HEADLINE ADVERSARIAL landed-VET, verified off-disk by independent .venv recompute off "
        "per_seed[] of the FORCE-PULLED remote N=8192 metrics (LOCAL metrics.json was the STALE N=4096 "
        "INCONCLUSIVE run -- Fix#28). All 5 probes hold across 5 seeds 7/17/23/31/41: (P1) non-ceiling genuine -- "
        "accB mean 0.9375 (<=0.95), accA_hard=0.000 (single-shot fails multi-hop), hard-subset accB~0.88 vs "
        "oracle-hard 0.99 (~10-15pp headroom); (P2) genuine multi-hop -- resolve_lift 0.44, gate routing "
        "load-bearing (always-requery breaks easy, accAlways=accA=0.4975), retrieved-bridge composition, paired "
        "105-111:1-3/seed sign_p 2.5e-12; (P3) glass-box audit intact on real chains -- causal_flip/tamper/merkle/"
        "det 1.0, n_causal 105-111/seed; (P4) telemetry-sensitive -- scramble collapses (scramble_gap 0.449), "
        "gate_sep 0.42 moves, all 14 means reproduce exactly, cv<0.05; (P5) honest scope -- real graph TOPOLOGY + "
        "random codes decoupled from semantics, NOT semantic-embedding reasoning, NOT open-domain (fixed "
        "2-hop/2-relation V~580 240-edge store). oracle_bridge(hard-subset) 0.995, hop1 1.0, cardinality 5/5. The "
        "N=4096 prior run BROKE the oracle (0.825<0.85) -> the real graph genuinely stresses the store (unlike the "
        "toy near-lossless regime); the N->8192 capacity fix reproduces retrieval AND the loop. REMOVES toy atom "
        "caveat (1) 'ceiling-saturation NOT in the wild' and ANSWERS its revival criterion (1) (capacity-stress / "
        "non-ceiling). Whole-cell HARD_PASS UPHELD at CHAIN_GRADE. Composes the toy loop atom at the mechanism "
        "level (NOT superseded; cell NOT re-run). Needs orchestrator Store-sync (skunkworks atoms do not "
        "auto-persist). Director cite note: toy origin 'db3e72699' not in substrate; actual toy atom = ba552930a."
    ),
    "verified_off_data": True,
    "anchor": "glass_box_micro_loop_conceptnet_multihop_v1",
    "cell_commit": CELL_COMMIT,
    "auditor": "hdi_skunkworks", "atomized_by": "hdi_skunkworks",
    "landed_VET_session": SESSION,
    "composes": [P_TOY],
    "needs_orchestrator_store_sync": True,
    "raw_metrics_paths": ["data/exp_glass_box_micro_loop_conceptnet_multihop_v1/metrics.json"],
}


def append_jsonl_a5(path: Path, new_row: dict, label: str) -> int:
    pre_lines = []
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            pre_lines = f.read().splitlines()
    pre_count = len(pre_lines)
    print(f"[A5] {label}: pre_count={pre_count}")
    for i, ln in enumerate(pre_lines):
        if not ln.strip():
            continue
        try:
            json.loads(ln)
        except Exception as e:
            raise RuntimeError(f"PRE integrity fail line {i+1}: {e}")
    new_line = json.dumps(new_row, ensure_ascii=True)
    parsed_back = json.loads(new_line)
    if "id" in new_row:
        assert parsed_back.get("id") == new_row.get("id")
    if "atom_id" in new_row:
        assert parsed_back.get("atom_id") == new_row.get("atom_id")
    out_text = "\n".join(pre_lines + [new_line]) + "\n"
    tmp_path = path.with_suffix(path.suffix + ".tmp_a5")
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(out_text)
        f.flush()
        os.fsync(f.fileno())
    for _attempt in range(10):
        try:
            os.replace(str(tmp_path), str(path))
            break
        except PermissionError:
            if _attempt == 9:
                raise
            time.sleep(0.1 * (2 ** _attempt))
    with open(path, "r", encoding="utf-8") as f:
        post_lines = f.read().splitlines()
    post_count = len(post_lines)
    print(f"[A5] {label}: post_count={post_count}")
    assert post_count == pre_count + 1
    tail = json.loads(post_lines[-1])
    if "id" in new_row:
        assert tail["id"] == new_row["id"]
    if "atom_id" in new_row:
        assert tail["atom_id"] == new_row["atom_id"]
    for i, ln in enumerate(post_lines):
        if not ln.strip():
            continue
        try:
            json.loads(ln)
        except Exception as e:
            raise RuntimeError(f"POST integrity fail line {i+1}: {e}")
    print(f"[A5] {label}: OK")
    return post_count


def main():
    print(f"[A5] atomize START {ATOMIZED_BY} ts={TS:.3f}")
    append_jsonl_a5(MATH_ATOMS, atom, "math/atoms (REAL-CONCEPTNET non-ceiling glass-box loop CHAIN_GRADE)")
    append_jsonl_a5(CERT_LEDGER, ledger, "cert_ledger (CG +1)")
    print(f"[A5] DONE OK -> REAL-CONCEPTNET non-ceiling glass-box multi-hop reasoning loop CHAIN_GRADE (CG +1)")


if __name__ == "__main__":
    main()
