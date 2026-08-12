"""
A5-gated atomization for landed VET of
exp_substrate_stage1_apply_exp3e_layer075_v3_clean_arc_closure_2026_07_03 (FULL).

Skunkworks landed-VET, off-disk recompute per Fix#28.

OFF-DISK RECOMPUTE (from metrics.json per_seed[]):
  seeds = [11, 17, 23]
  ARM_MAIN_V3_CLEAN:            per_seed=[0.71, 0.82, 0.68]  mean=0.7367  pop_sd=0.0602  sample_sd=0.0737
    -> cv(pop)=0.0817 (matches reported 0.082); cv(sample)=0.1001 (>=0.10 border FAIL if sample)
    -> 95% CI (t,df=2): [0.5535, 0.9198]  (WIDE at n=3)
  ARM_ORACLE_COMPOSITION_SANITY: [0.82, 0.83, 0.80] mean=0.8167  cv=0.019 (very stable)
  hp_full = 0.9 * ORACLE_mean = 0.7350
  MAIN vs hp_full margin = +0.0017 (0.7367 vs 0.7350 = ~1 correct query per 300 total)
  ARM_V3_STACKED_WITH_S1S2:     [0.50, 0.60, 0.42] mean=0.5067; drift vs Exp3D MAIN 0.511 = -0.0043 (TIGHT)
  ARM_EXP3_BASELINE_REPRODUCTION: [0.41, 0.52, 0.39] mean=0.44; drift vs 0.411 = +0.029 (in-band)
  ARM_STAGE3_V1_QUERY_ONLY_RESCORE: [0, 0.04, 0] mean=0.0133; drift vs 0.011 = +0.002 (in-band)
  ARM_STAGE3_V2_ITERATIVE_QUERY_AUG_ONLY: [0.04, 0.05, 0.04] mean=0.0433; drift vs 0.033 = +0.010 (in-band)
  ARM_RANDOM_CANDIDATES_CONTROL: [0, 0.06, 0.03] mean=0.03 (control clean vs random chance ~0.02)
  Seed 23 MAIN = 0.68 (was 0.633 in Exp 3D SMOKE; now clears >=0.60 gate by 0.08)
  cardinality_ok=True; arms_differ_ok=True; v3_fire_summary shows 100/100 slot fires all seeds, 0 fallback.

PRE-REGISTERED GATES ASSESSMENT (all 4 required for CG arc closure):
  Gate 1 (MAIN >= 0.9*ORACLE): PASS by +0.0017 -- WITHIN MEASUREMENT NOISE (1/300 queries)
  Gate 2 (cv < 0.10): PASS by pop-sd convention (0.082); FAIL by sample-sd (0.1001).
                     Cell used pop-sd, pre-reg accepted -- gate technically PASS on stated terms
                     but standard convention (sample sd, n-1) puts this AT the border.
  Gate 3 (all seeds >= 0.60): PASS with margin (min=0.68, +0.08 above bar; seed 23 which
                              had failed at 0.633 in Exp 3D SMOKE now clears)
  Gate 4 (V3_STACKED_S1S2 drift < 0.05 vs Exp3D 0.511): PASS with big margin (drift=0.004,
                              8% of allowed bound). This is CG-tight in isolation.

TIER JUDGMENT:
  Two components are CG-tight:
    (i)  V3_STACKED_S1S2 drift 0.004 vs Exp3D MAIN 0.511 -> S1+S2-subtract diagnosis
         VALIDATED at FULL scale (independent structural claim about pipeline design).
    (ii) All-seeds >= 0.60 with min=0.68 -> seed-23 tail cleared with margin.
  Two components are MARGINAL:
    (iii) MAIN vs hp_full = +0.0017 margin -- literally 1 correct query per 300; a single
          coin-flip of query difficulty in the 100q sample would flip PASS to FAIL.
    (iv)  cv is 0.082 (pop) / 0.1001 (sample); the CI on MAIN is [0.55, 0.92] at n=3.

  The Director-flagged concern is real: cell-author framed HARD_PASS_FULL_ARC_CLOSURE, but
  the aggregate claim rests on 2 marginal gates. Honest tier is MM_TENTATIVE_ARC_CLOSURE with
  explicit revival criterion (5-seed OR 300q) to tighten CI. However, ONE independent
  sub-claim IS CG-tight: the S1+S2-subtract diagnosis reproduction at FULL scale
  (V3_STACKED drift 0.004). Filing that as separate CG so it isn't lost in the marginal
  aggregate; filing the umbrella arc-closure claim as MM.

MECHANISM SOURCE-SIGNATURE (per Director rule [[feedback_mechanism_abstraction_lossy_cite_source_signature_2026-07-03]]):
  Do NOT abstract to "structural KG filtering". Cite exact predicate:
    HOP-1 FILTER: retrieve candidates C such that C = subject(e0, r1, ?) -- filter on
                  slot=SUBJECT with anchor=e0 for relation r1
    HOP-2 FILTER: retrieve candidates C such that C = subject(bridge_mid, r2, ?) -- filter on
                  slot=SUBJECT with anchor=bridge_mid (predicted via hop-1) for relation r2
    COMPOSITION: FHRR bind e0 * r1 -> mid, then mid * r2 -> answer, over uniform PPR pool
                 (alpha=0.15, iters=5, top_k=5) with union_max=30, hub_dampen 0.30 on top-3
                 empirical hubs by degree, MMR lambda=0.30, k_final=5, b_bridges=5,
                 w_query_anchor=1.0, w_aug=1.0, bridge_min_cooccur=2.

CROSS-ARC OVERLAP CHECK (per USER-locked rule 2026-07-01):
  substrate_query "v3 clean structural KG-slot filter arc closure hub-concept-bridge":
    top cosine 0.292 (wordnet/structure) -- below 0.30 threshold; no substantial overlap.
  DIRECT COMPOSITION: composes on Exp 3D SMOKE MM atoms
    T3/EXP...exp3d..._V3_STRUCTURAL_KG_SLOT_ISOLATES_BRIDGE_ROLE... (parent MM)
    T3/EXP...exp3d..._STAGE1_STAGE2_SUBTRACT_FROM_STRUCTURAL_V3_STACKED... (parent MM)
  This landing MOVES parent MM SMOKE claims toward FULL scale but does NOT clean-close the
  arc; scope-narrows to hub-concept-bridge on synthetic corpus at N=8192.

SCOPE ANNOTATION (explicit per Director task):
  CLOSES for: hub-concept-bridge scope, synthetic corpus (procedurally generated cities +
              relations), N=8192, 100q x 3 seeds, mechanism validated MARGINALLY at FULL
  DOES NOT CLOSE for: non-hub-bridge scope (still gated by data availability)
  DOES NOT CLOSE for: 170K-atom Director-KB scale (Exp 1 / Exp 2C revival criteria still open)

Two atoms filed:
  (a) math MM_TENTATIVE_ARC_CLOSURE_MARGINAL_GATES on Exp 3E FULL v3-clean arc closure
      (aggregate 4-gate PASS but 2 gates within measurement noise; needs 5-seed to CG)
  (b) math CG_HARD_PASS on the S1+S2-subtract-diagnosis reproduction sub-claim
      (V3_STACKED drift 0.004 at FULL is genuinely tight; this is a proven bound on
       pipeline design regardless of arc-closure aggregate)
"""
import json
import os
import time
import tempfile

MATH_ATOMS = "d:/AI/hd-instrument/data/substrate_index/math/atoms.jsonl"
META_ATOMS = "d:/AI/hd-instrument/data/substrate_index/meta/atoms.jsonl"
CERT_LEDGER = "d:/AI/hd-instrument/data/substrate_index/meta/cert_ledger.jsonl"

TS = time.time()
TS_ISO = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(TS))
COMMIT = "01f41fc20"

# ============= ATOM (a): MM_TENTATIVE_ARC_CLOSURE_MARGINAL_GATES =============
atom_mm = {
    "id": (
        "math::T3/EXP_substrate_stage1_apply_exp3e_layer075_v3_clean_arc_closure_FULL_"
        "MM_TENTATIVE_ARC_CLOSURE_MARGINAL_GATES_N8192_100q_3seeds_11_17_23_MAIN_V3_CLEAN_"
        "mean_0p7367_seeds_0p71_0p82_0p68_pop_cv_0p082_sample_cv_0p1001_border_ORACLE_mean_"
        "0p8167_seeds_0p82_0p83_0p80_cv_0p019_hp_full_threshold_0p9_times_ORACLE_0p7350_MAIN_"
        "vs_hp_full_margin_plus_0p0017_ONE_QUERY_PER_300_WITHIN_MEASUREMENT_NOISE_all_seeds_"
        "ge_0p60_min_0p68_PASS_with_margin_seed_23_recovered_from_0p633_in_exp3d_smoke_to_0p68_"
        "at_FULL_V3_STACKED_S1S2_drift_neg_0p0043_vs_exp3d_MAIN_0p511_TIGHT_reproduces_S1_plus_"
        "S2_subtract_diagnosis_at_FULL_scale_ORACLE_drift_neg_0p0053_vs_smoke_0p822_within_0p10_"
        "EXP3_BASELINE_drift_plus_0p029_vs_0p411_within_0p10_STAGE3_V1_drift_plus_0p002_vs_0p011_"
        "within_STAGE3_V2_drift_plus_0p010_vs_0p033_flagged_V2_HF_DRIFT_within_RANDOM_control_0p03_"
        "clean_cardinality_ok_true_arms_differ_ok_true_v3_fire_100_of_100_all_seeds_0_fallback_"
        "run_mode_full_wall_s_154_gate_1_MAIN_ge_hp_full_PASS_measurement_noise_gate_2_cv_lt_0p10_"
        "PASS_pop_sd_convention_FAIL_sample_sd_convention_border_gate_3_all_seeds_ge_0p60_PASS_"
        "margin_gate_4_V3_STACKED_drift_lt_0p05_PASS_big_margin_aggregate_4_gate_PASS_on_stated_"
        "terms_but_2_gates_within_measurement_noise_hence_MM_not_CG_per_symmetric_anti_negativity_"
        "USER_2026_06_17_MECHANISM_SOURCE_SIGNATURE_hop1_filter_slot_SUBJECT_anchor_e0_relation_r1_"
        "hop2_filter_slot_SUBJECT_anchor_bridge_mid_predicted_from_hop1_relation_r2_composition_"
        "FHRR_bind_e0_r1_mid_bind_mid_r2_answer_over_uniform_PPR_alpha_0p15_iters_5_top_k_5_union_"
        "max_30_hub_dampen_0p30_deg_thresh_8_top3_empirical_hubs_MMR_lambda_0p30_k_final_5_b_"
        "bridges_5_w_query_anchor_1p0_w_aug_1p0_bridge_min_cooccur_2_SCOPE_hub_concept_bridge_"
        "synthetic_corpus_N8192_only_does_NOT_close_non_hub_bridge_scope_or_170K_Director_KB_scale_"
        "revival_criterion_5_seed_OR_300q_to_tighten_CI_sample_cv_below_0p10_with_margin_AND_MAIN_"
        "vs_hp_full_margin_ge_0p03_composes_on_exp3d_smoke_MM_parents_amends_toward_FULL_2026-07-03"
    ),
    "name": "EXP substrate_stage1_apply_exp3e_layer075_v3_clean_arc_closure FULL MM_TENTATIVE_ARC_CLOSURE_MARGINAL_GATES (aggregate 4-gate PASS but MAIN vs hp_full margin +0.0017 within noise; sample-cv 0.1001 at border)",
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record",
    "description": (
        "Experiment record: Exp 3E FULL scale-up of the v3-clean structural KG-slot filter pipeline "
        "for hub-concept-bridge scope on synthetic corpus at N=8192, 100 queries x 3 seeds (11/17/23). "
        "Reported HARD_PASS_FULL_ARC_CLOSURE_V3_CLEAN with all 4 pre-registered gates PASS. Off-disk "
        "recompute confirms per-arm numbers: MAIN_V3_CLEAN mean=0.7367 (seeds [0.71, 0.82, 0.68]); "
        "ORACLE mean=0.8167 (seeds [0.82, 0.83, 0.80]); hp_full threshold = 0.9*ORACLE = 0.7350; MAIN "
        "vs hp_full margin = +0.0017 (LITERALLY 1 correct query per 300 total = within measurement "
        "noise). cv on MAIN is 0.082 using population sd (matches cell report) but 0.1001 using "
        "sample sd (n-1, standard estimator) -- AT the pre-registered 0.10 border. 95%% CI on MAIN "
        "at n=3 (t-dist df=2) is [0.5535, 0.9198] -- very wide. min_seed=0.68 clears >=0.60 gate "
        "with 0.08 margin (seed 23 which failed Exp 3D SMOKE at 0.633 now clears at 0.68, real "
        "improvement). V3_STACKED_S1S2 drift vs Exp3D MAIN 0.511 = -0.0043 (TIGHT) -- this "
        "reproduces the S1+S2-subtract diagnosis at FULL scale with big margin (8%% of allowed 0.05 "
        "bound). Other reproductions all in-band: ORACLE drift -0.005, EXP3_BASE +0.029, S3V1 "
        "+0.002, S3V2 +0.010 (flagged as V2_HF_DRIFT but within 0.10), RANDOM control 0.03. "
        "cardinality_ok=True, arms_differ_ok=True, v3_fire 100/100 all seeds, 0 fallback. "
        "TIER JUDGMENT: honest downward correction from HARD_PASS to MM_TENTATIVE_ARC_CLOSURE_"
        "MARGINAL_GATES because two of four gates are WITHIN measurement noise: (i) MAIN vs "
        "hp_full margin of +0.0017 is smaller than sampling variance in a 100q sample -- a "
        "single lucky query flip on any seed swings PASS<->FAIL; (ii) sample-sd cv is 0.1001, "
        "literally at the 0.10 threshold border. The pre-reg used pop-sd convention (cv=0.082) "
        "and by that convention gates PASS -- but this is a definitional choice, not measurement "
        "robustness. Per symmetric anti-negativity discipline (USER 2026-06-17): honest downward "
        "correction has the same rigor as upward -- the arc-closure aggregate claim should not be "
        "framed as clean CG when 2/4 gates are marginal. MM tier reflects: mechanism DOES work at "
        "FULL scale (positive result), but the CI is wide and the closure claim needs tighter "
        "gates before CG promotion. Two sub-components ARE genuinely CG-tight and warrant "
        "separate atoms: (a) V3_STACKED_S1S2 drift 0.004 at FULL reproduces S1+S2-subtract "
        "diagnosis (filed as separate CG below), (b) all-seeds >=0.60 with min=0.68 -- seed 23 "
        "tail recovered from Exp 3D SMOKE failure. "
        "MECHANISM SOURCE SIGNATURE (do NOT abstract per Director rule 2026-07-03): "
        "HOP-1 FILTER predicate: candidate C such that C = subject(e0, r1, ?), i.e. slot=SUBJECT "
        "anchored on entity e0 filtered by relation r1. HOP-2 FILTER predicate: candidate C such "
        "that C = subject(bridge_mid, r2, ?), i.e. slot=SUBJECT anchored on bridge_mid (predicted "
        "from hop-1) filtered by relation r2. COMPOSITION: FHRR bind(e0, r1) -> mid, then "
        "bind(mid, r2) -> answer, ranked over uniform PPR pool with alpha=0.15, iters=5, "
        "top_k=5, union_max=30, hub_dampen_factor=0.30 on empirical top-3 hubs by degree "
        "(hub_deg_thresh=8), MMR lambda=0.30, k_final=5, b_bridges=5, w_query_anchor=1.0, "
        "w_aug=1.0, bridge_min_cooccur=2. "
        "SCOPE (explicit): CLOSES for hub-concept-bridge scope on synthetic procedurally-generated "
        "corpus at N=8192, 100q x 3 seeds, at FULL scale -- MARGINALLY. Does NOT close for non-hub-"
        "bridge scope (data availability gate). Does NOT close for 170K-atom Director-KB scale "
        "(Exp 1 and Exp 2C revival criteria still open). Does NOT extrapolate to real-content "
        "corpora (mechanism-analog-vs-task-analog USER-locked rule). "
        "REVIVAL / PROMOTION-TO-CG CRITERION: re-dispatch at 5 seeds OR 300 queries per seed to "
        "tighten CI such that (i) sample-sd cv < 0.09 with margin (not border) and (ii) MAIN vs "
        "hp_full margin >= 0.03 (well above noise). If both tighten, promote to CG_ARC_CLOSURE_"
        "FULL. If either widens on repeat, DEMOTE this MM. "
        "COMPOSITION: composes on Exp 3D SMOKE parent MM atoms (v3-structural-KG-slot isolates "
        "bridge role; S1+S2-subtract from structural v3-stacked). Amends parents toward FULL "
        "scale in the marginal-gates direction; does not supersede."
    ),
    "aliases": [],
    "metadata": {
        "record_class": "experiment_record",
        "term_class": "STRUCTURAL_KG_SLOT_FILTER_HUB_CONCEPT_BRIDGE_FULL_MARGINAL_ARC_CLOSURE",
        "cert_status": "measured_mechanism_tentative_arc_closure_marginal_gates",
        "cert_class": "MM_TENTATIVE_ARC_CLOSURE_MARGINAL_GATES",
        "cert_ts": TS_ISO,
        "verified_off_data": True,
        "atomized_by": "skunkworks_landed_VET_2026-07-03_exp3e_FULL_arc_closure",
        "commit": COMMIT,
        "landing_path": "data/exp_exp_substrate_stage1_apply_exp3e_layer075_v3_clean_arc_closure_2026_07_03/metrics.json",
        "run_mode": "full",
        "n_dim": 8192,
        "target_queries": 100,
        "n_seeds": 3,
        "seeds": [11, 17, 23],
        "per_arm_recompute": {
            "MAIN_V3_CLEAN":  {"seeds": [0.71, 0.82, 0.68], "mean": 0.7367, "pop_sd": 0.0602, "sample_sd": 0.0737, "cv_pop": 0.0817, "cv_sample": 0.1001, "min": 0.68, "max": 0.82, "ci95_t_df2": [0.5535, 0.9198]},
            "ORACLE":         {"seeds": [0.82, 0.83, 0.80], "mean": 0.8167, "cv_pop": 0.0187},
            "EXP3_BASELINE":  {"seeds": [0.41, 0.52, 0.39], "mean": 0.44},
            "STAGE3_V1":      {"seeds": [0.0, 0.04, 0.0], "mean": 0.0133},
            "STAGE3_V2":      {"seeds": [0.04, 0.05, 0.04], "mean": 0.0433},
            "V3_STACKED_S1S2":{"seeds": [0.50, 0.60, 0.42], "mean": 0.5067, "drift_vs_exp3d_MAIN_0p511": -0.0043},
            "RANDOM":         {"seeds": [0.0, 0.06, 0.03], "mean": 0.03},
        },
        "hp_full_threshold": 0.7350,
        "MAIN_vs_hp_full_margin": 0.0017,
        "gates_assessment": {
            "gate_1_MAIN_ge_hp_full": {"stated_result": "PASS", "auditor_note": "PASS by +0.0017, WITHIN measurement noise at n=100q, 3seed"},
            "gate_2_cv_lt_0p10":       {"stated_result": "PASS (pop-sd)", "auditor_note": "PASS pop-sd=0.082; FAIL/BORDER sample-sd=0.1001. Pre-reg used pop convention."},
            "gate_3_all_seeds_ge_0p60": {"stated_result": "PASS", "auditor_note": "PASS with margin, min=0.68 vs 0.60 bar; seed 23 recovered from Exp 3D SMOKE 0.633"},
            "gate_4_V3_STACKED_drift_lt_0p05": {"stated_result": "PASS", "auditor_note": "PASS big margin, drift 0.004 = 8% of bound; CG-tight in isolation"}
        },
        "arc_closure_scope": {
            "closes_for": "hub-concept-bridge scope on synthetic corpus, N=8192, 100q x 3seed at FULL scale (MARGINALLY)",
            "does_not_close_for": [
                "non-hub-bridge scope (data availability gate)",
                "170K-atom Director-KB scale (Exp 1 / Exp 2C revival criteria still open)",
                "real-content corpora (mechanism-analog-vs-task-analog rule)"
            ]
        },
        "revival_promotion_criterion": "re-dispatch at 5-seed OR 300q per seed such that sample-sd cv < 0.09 with margin AND MAIN vs hp_full margin >= 0.03",
        "mechanism_source_signature": {
            "hop1_filter": "candidate C: C = subject(e0, r1, ?), slot=SUBJECT anchored on e0 filtered by relation r1",
            "hop2_filter": "candidate C: C = subject(bridge_mid, r2, ?), slot=SUBJECT anchored on bridge_mid (predicted hop-1) filtered by r2",
            "composition": "FHRR bind(e0,r1)->mid, bind(mid,r2)->answer, over uniform PPR pool alpha=0.15 iters=5 top_k=5 union_max=30 hub_dampen 0.30 on top-3 hubs deg_thresh=8, MMR lambda=0.30, k_final=5, b_bridges=5, w_query_anchor=1.0, w_aug=1.0, bridge_min_cooccur=2"
        },
        "composes_on_atoms": [
            "T3/EXP_substrate_stage1_apply_exp3d_layer075_structural_kg_slot_filtering_SMOKE_MM_V3_STRUCTURAL_KG_SLOT_ISOLATES_BRIDGE_ROLE_...2026-07-03",
            "T3/EXP_substrate_stage1_apply_exp3d_layer075_structural_kg_slot_filtering_SMOKE_MM_STAGE1_STAGE2_SUBTRACT_FROM_STRUCTURAL_V3_STACKED_...2026-07-03"
        ],
        "cross_arc_overlap_cosine_max": 0.292,
        "cross_arc_overlap_note": "top match wordnet/structure at 0.292 below 0.30 threshold; direct composition on Exp 3D SMOKE parents",
        "director_over_claim_correction": (
            "Cell-author and Director spawn framed HARD_PASS_FULL_ARC_CLOSURE_V3_CLEAN. Skunkworks "
            "honest downward correction: MM_TENTATIVE_ARC_CLOSURE_MARGINAL_GATES because MAIN vs "
            "hp_full margin +0.0017 is within measurement noise (1 correct query per 300); sample-sd "
            "cv is 0.1001 at the 0.10 border. Aggregate 4-gate PASS holds on stated terms but the "
            "arc-closure framing needs tighter CI (5-seed or 300q) before CG promotion. Symmetric "
            "anti-negativity USER 2026-06-17: honest downward correction with same rigor as upward."
        )
    },
    "provenance": {"generator": "skunkworks_atomize_exp3e_FULL_arc_closure_2026_07_03", "ts": TS_ISO},
    "ts_added": TS_ISO,
    "ts_atomized": TS_ISO,
    "supersedes": [],
}

# ============= ATOM (b): CG on S1+S2-SUBTRACT-DIAGNOSIS FULL-SCALE REPRODUCTION =============
atom_cg = {
    "id": (
        "math::T3/EXP_substrate_stage1_apply_exp3e_layer075_v3_clean_arc_closure_FULL_"
        "CG_HARD_PASS_SUBCLAIM_S1_PLUS_S2_SUBTRACT_DIAGNOSIS_REPRODUCES_AT_FULL_SCALE_V3_"
        "STACKED_S1S2_mean_0p5067_seeds_0p50_0p60_0p42_drift_neg_0p0043_vs_exp3d_smoke_"
        "MAIN_STACKED_0p511_TIGHT_8pct_of_allowed_0p05_bound_gap_vs_V3_ONLY_MAIN_CLEAN_0p7367_"
        "equals_0p2300_absolute_31pct_relative_degradation_at_FULL_N8192_matches_exp3d_smoke_"
        "gap_pattern_0p256_absolute_33pct_relative_STAGE1_hub_dampen_0p30_deg_thresh_8_plus_"
        "STAGE2_MMR_lambda_0p30_DEMOTE_hop2_facts_when_mid_is_hub_subject_eq_mid_pattern_the_"
        "S1_S2_layer_075_smoothing_stacked_on_top_of_v3_structural_KG_slot_filter_NET_NEGATIVES_"
        "the_pipeline_when_v3_available_optimal_pipeline_uniform_PPR_then_v3_structural_SKIP_"
        "S1_S2_proven_bound_on_STACKED_pipeline_design_at_FULL_scale_independent_of_arc_closure_"
        "aggregate_claim_marginal_or_not_this_sub_claim_is_CG_tight_composition_FHRR_bind_e0_r1_"
        "mid_bind_mid_r2_answer_over_uniform_PPR_alpha_0p15_iters_5_top_k_5_scope_hub_concept_"
        "bridge_synthetic_corpus_N8192_100q_3_seeds_11_17_23_composes_on_exp3d_smoke_MM_parent_"
        "S1_S2_SUBTRACT_pattern_promotes_to_CG_at_FULL_scale_supersedes_None_2026-07-03"
    ),
    "name": "EXP Exp 3E FULL CG_HARD_PASS sub-claim: S1+S2-subtract-diagnosis reproduces at FULL scale (V3_STACKED drift 0.004 vs Exp3D SMOKE 0.511; gap 0.23 absolute)",
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record",
    "description": (
        "Sub-claim record extracted from Exp 3E FULL landing metrics.json. This is the ONE component "
        "of the Exp 3E FULL aggregate that is genuinely CG-tight in isolation, worth filing "
        "separately so it isn't diluted by the marginal arc-closure aggregate. "
        "CLAIM: at FULL scale (N=8192, 100q x 3seed, hub-concept-bridge scope), stacking S1 (uniform "
        "PPR with hub_dampen=0.30 on empirical top-3 hubs, deg_thresh=8) and S2 (MMR lambda=0.30) "
        "layers ON TOP OF the v3 structural KG-slot filter DEMOTES accuracy from MAIN_V3_CLEAN mean "
        "0.7367 to V3_STACKED_S1S2 mean 0.5067 -- a gap of 0.230 absolute, 31%% relative. This "
        "matches the Exp 3D SMOKE pattern (V3_ONLY 0.767 vs V3_STACKED 0.511, gap 0.256 absolute, "
        "33%% relative) with drift on the V3_STACKED number of -0.0043 (i.e. 8%% of the allowed "
        "0.05 bound = TIGHT). Per-seed: STACKED [0.50, 0.60, 0.42] vs MAIN [0.71, 0.82, 0.68] -- "
        "monotone degradation per seed. IMPLICATION: optimal pipeline is uniform PPR -> v3 "
        "structural KG-slot filter, SKIPPING S1 hub-dampen and S2 MMR-diversification. The S1 "
        "layer demotes hop-2 candidates when the bridge (mid) is a hub (subject=mid pattern), "
        "which is exactly the case in hub-concept-bridge scope by design. S2 MMR further "
        "diversifies AWAY from the true bridge. Net: S1+S2 subtract mechanism when v3 available. "
        "This is a PROVEN BOUND on STACKED pipeline design at FULL scale, independent of whether "
        "the overall arc-closure aggregate is marginal or clean. "
        "SCOPE: hub-concept-bridge, synthetic corpus, N=8192, 100q x 3seed at FULL. Promotes the "
        "Exp 3D SMOKE parent MM claim (V3_STACKED gap at SMOKE) to CG at FULL scale for this "
        "specific sub-claim; does NOT promote the arc-closure aggregate. "
        "REFUTATION CRITERION: a modified S1 (hub_dampen != 0.30 or deg_thresh != 8) or S2 "
        "(MMR lambda != 0.30) that ELIMINATES the gap while preserving MAIN performance would "
        "carve scope to 'default S1+S2 config subtracts' vs a broader claim about hub-aware "
        "smoothing. Left as revival if arc rewarms."
    ),
    "aliases": [],
    "metadata": {
        "record_class": "experiment_record",
        "term_class": "S1_PLUS_S2_SUBTRACT_FROM_V3_STRUCTURAL_FULL_SCALE_PROVEN_BOUND",
        "cert_status": "chain_grade_hard_pass_sub_claim",
        "cert_class": "CG_HARD_PASS",
        "cert_ts": TS_ISO,
        "verified_off_data": True,
        "atomized_by": "skunkworks_landed_VET_2026-07-03_exp3e_FULL_arc_closure",
        "commit": COMMIT,
        "landing_path": "data/exp_exp_substrate_stage1_apply_exp3e_layer075_v3_clean_arc_closure_2026_07_03/metrics.json",
        "gap_at_FULL": {"MAIN_V3_CLEAN_mean": 0.7367, "V3_STACKED_S1S2_mean": 0.5067, "gap_absolute": 0.2300, "gap_relative_pct": 31.2},
        "drift_from_exp3d_smoke": {"exp3d_MAIN_STACKED": 0.511, "exp3e_V3_STACKED_S1S2": 0.5067, "drift": -0.0043, "pct_of_allowed_0p05_bound": 8.6},
        "per_seed_stacked": [0.50, 0.60, 0.42],
        "per_seed_main": [0.71, 0.82, 0.68],
        "monotone_degradation_per_seed": True,
        "composes_on_atoms": [
            "T3/EXP_substrate_stage1_apply_exp3d_layer075_structural_kg_slot_filtering_SMOKE_MM_STAGE1_STAGE2_SUBTRACT_FROM_STRUCTURAL_V3_STACKED_...2026-07-03"
        ],
        "promotes_parent_at_full_scale": True,
        "does_not_promote_arc_closure_aggregate": True,
        "scope": "hub-concept-bridge synthetic corpus N=8192 100q x 3seed FULL",
    },
    "provenance": {"generator": "skunkworks_atomize_exp3e_FULL_arc_closure_2026_07_03", "ts": TS_ISO},
    "ts_added": TS_ISO,
    "ts_atomized": TS_ISO,
    "supersedes": [],
}


def append_jsonl_atomic_verify(path, obj):
    tmpfd, tmp = tempfile.mkstemp(prefix=".skunkworks_atomize_", dir=os.path.dirname(path))
    os.close(tmpfd)
    try:
        with open(path, "r", encoding="utf-8") as f_in:
            existing = f_in.read()
        with open(tmp, "w", encoding="utf-8") as f_out:
            if existing and not existing.endswith("\n"):
                f_out.write(existing + "\n")
            else:
                f_out.write(existing)
            f_out.write(json.dumps(obj, ensure_ascii=False) + "\n")
        os.replace(tmp, path)
    except Exception:
        try: os.unlink(tmp)
        except Exception: pass
        raise
    # verify load
    with open(path, "r", encoding="utf-8") as f_check:
        lines = f_check.readlines()
    last = json.loads(lines[-1])
    assert last["id"] == obj["id"], f"verify-load failed: {last.get('id')} != {obj['id']}"
    return last["id"]


mm_id = append_jsonl_atomic_verify(MATH_ATOMS, atom_mm)
print(f"[a] MM atom filed: {mm_id[:120]}...")

cg_id = append_jsonl_atomic_verify(MATH_ATOMS, atom_cg)
print(f"[b] CG atom filed: {cg_id[:120]}...")

# ============= CERT LEDGER ENTRIES =============
def append_ledger(entry):
    tmpfd, tmp = tempfile.mkstemp(prefix=".skunkworks_ledger_", dir=os.path.dirname(CERT_LEDGER))
    os.close(tmpfd)
    try:
        with open(CERT_LEDGER, "r", encoding="utf-8") as f_in:
            existing = f_in.read()
        with open(tmp, "w", encoding="utf-8") as f_out:
            if existing and not existing.endswith("\n"):
                f_out.write(existing + "\n")
            else:
                f_out.write(existing)
            f_out.write(json.dumps(entry, ensure_ascii=False) + "\n")
        os.replace(tmp, CERT_LEDGER)
    except Exception:
        try: os.unlink(tmp)
        except Exception: pass
        raise


append_ledger({
    "ts": TS_ISO,
    "atom_id": atom_mm["id"],
    "atom_ref": "math::exp3e_FULL_arc_closure_MM_TENTATIVE_MARGINAL_GATES",
    "cert_class": "MM_TENTATIVE_ARC_CLOSURE_MARGINAL_GATES",
    "verified_off_data": True,
    "commit": COMMIT,
    "atomized_by": "skunkworks",
    "landing_path": "data/exp_exp_substrate_stage1_apply_exp3e_layer075_v3_clean_arc_closure_2026_07_03/metrics.json",
    "note": "Honest downward from HARD_PASS: MAIN vs hp_full margin +0.0017 within noise; sample-cv 0.1001 at 0.10 border. Two sub-gates CG-tight, aggregate MM. Revival: 5-seed or 300q."
})
append_ledger({
    "ts": TS_ISO,
    "atom_id": atom_cg["id"],
    "atom_ref": "math::exp3e_FULL_S1S2_subtract_diagnosis_CG_HARD_PASS_subclaim",
    "cert_class": "CG_HARD_PASS",
    "verified_off_data": True,
    "commit": COMMIT,
    "atomized_by": "skunkworks",
    "landing_path": "data/exp_exp_substrate_stage1_apply_exp3e_layer075_v3_clean_arc_closure_2026_07_03/metrics.json",
    "note": "V3_STACKED drift 0.004 vs Exp3D SMOKE 0.511 = 8% of allowed bound. Gap 0.23 absolute per-seed monotone. Promotes S1+S2-subtract parent to CG at FULL for this sub-claim."
})

print(f"[ledger] two entries appended to {CERT_LEDGER}")
print("\n=== SESSION TALLY (disk-audit) ===")
import subprocess
print(subprocess.check_output(["grep", "-c", "2026-07-03", MATH_ATOMS], text=True).strip(), "math atoms today")
print(subprocess.check_output(["grep", "-c", "2026-07-03", META_ATOMS], text=True).strip(), "meta atoms today")
