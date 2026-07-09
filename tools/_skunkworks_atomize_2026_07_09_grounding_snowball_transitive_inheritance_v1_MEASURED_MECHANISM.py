"""
A5-gated atomize: LANDED-VET (AUDIT-ONLY, HIGH) of grounding_snowball_transitive_inheritance_v1.
Transitive grounding-inheritance is REAL but SHALLOW (~1 hop). TIER = MEASURED_MECHANISM (proven boundary).

CELL: experiments/exp_grounding_snowball_transitive_inheritance_v1.py (commit 89a088469)
PREREG: preregs/2026-07-09_grounding_snowball_transitive_inheritance_v1.md
METRICS: data/exp_grounding_snowball_transitive_inheritance_v1/metrics.json
  run_mode=full, 5 seeds 7/13/17/23/29, n_nodes 12000 -> CN 2-core n=10577 E=34659 med_deg 3, 120 ground-seeds.
  cell verdict HARD_PASS (all prereg HARD_PASS bands cleared on aggregate).

INDEPENDENT OFF-DISK RECOMPUTE (.venv, aggregated per_seed[] all 5 seeds -- EVERY gate value reproduces EXACTLY):
  near_acc(d1)   mean=0.60727 pstd=0.01305 cv=0.0215  per-seed [0.585,0.6191,0.6017,0.6207,0.6099]
  far_acc(d4+)   mean=0.52520 pstd=0.01259 cv=0.0240  (far_bin=3, n=174 nodes)
  decay          mean=0.08206 pstd=0.01335 cv=0.1627  per-seed [0.0786,0.0991,0.0588,0.0859,0.088]
  shuf_near      mean=0.51081 pstd=0.01599 cv=0.0313  (control flat at chance, all bins ~0.49-0.51)
  genuine_margin mean=0.09646 pstd=0.02458 cv=0.2548  per-seed [0.0534,0.0966,0.0927,0.1143,0.1253]
  rel_auc        mean=0.86351 pstd=0.00218 cv=0.0025  (strong + tight)
  grounded_floor mean=0.54640 cv=0.0116 (in band [0.42,0.62], NOT leakage <0.70)
  stage1_gap     0.31711 (HP 0.30) ; cotrain_lift_near +0.00732 (null; smoke was -0.023)
  assort smooth=0.7102 shuf=0.0047 precond_ok=True ; selftest decay 0.1889 gm 0.1743 (fires STRONG)

  SHALLOWNESS -- the load-bearing audit finding (smooth-minus-shuffled MARGIN by graph distance):
    d1=0.0965  d2=0.0434  d3=0.0228  d4+=0.0318   -> genuine signal is essentially GONE by d2,
    at noise by d3+ (bins d3/d4+ margin within per-seed spread). "Transitive inheritance" is ~1 HOP.

FULL is WEAKER than smoke on every headline (symmetric anti-negativity note):
  near_acc 0.630->0.607 ; decay 0.146->0.082 ; genuine_margin 0.135->0.096. At FULL scale the effect is
  roughly HALF the smoke decay/margin. decay clears its own HP (0.08) by only +0.0006 -- razor-thin.

WHY MEASURED_MECHANISM (proven boundary), NOT CHAIN_GRADE:
  (i) SHALLOW: genuine margin collapses to ~chance by d2; the mechanism is a 1-hop neighbour effect, NOT deep
      transitive inheritance. decay barely clears HP.
  (ii) Headline discriminators FAIL the CG cv gate: decay cv=0.163 (>0.15 CG), genuine_margin cv=0.255
       (>0.20 even the MM gate -- reflects small effect size, but 1/5 seeds (seed7) individually dips BELOW HP
       on BOTH near_acc (0.585<0.60) AND genuine_margin (0.053<0.06); aggregate carried by the other 4).
  (iii) SYNTHETIC attribute: the grounded scalar is a graph-smooth field diffused over the real CN subgraph
        (honest stand-in per prereg, NOT real perceptual grounding). The certified mechanism is narrow:
        a graph-smooth attribute is readable off 1-hop neighbours of seeds via label-prop over relational codes.
  (iv) Co-training does NOT deepen propagation (cotrain_lift +0.007, null both directions vs smoke -0.023).

WHY NOT MB/HF (do NOT over-deflate):
  The effect is GENUINELY REAL and reproduces exactly: shuffled MUST-FAIL control flat at chance (0.511, all
  bins ~0.50); planted-signal selftest fires STRONG (decay 0.189, gm 0.174 -> discriminator telemetry-sensitive,
  not analytically pinned); aggregate decay monotone; ALL 5 seeds positive genuine_margin (min 0.053 > HF 0.03);
  rel_auc tight+strong. All prereg HARD_PASS bands cleared on aggregate. This is a clean positive with a real bound.

CROSS-ARC OVERLAP (USER-locked check): substrate_query "transitive grounding inheritance seed propagation graph
  distance decay relational encoder attribute label propagation" -> top hits are GENERIC 'propagation' nodes
  (wordnet/concept 'propagation' 0.4424, 'CN_propagation' 0.3477), an R-GCN/HAN drill note 0.3447, and a
  DIFFERENT-mechanism 'Confidence propagation' multi-hop prereg 0.3408. NONE substantively about transitive
  GROUNDING-inheritance. Genuinely novel mechanism, NOT a rediscovery (matches prereg's own scan). The July-1
  INT8-rediscovery failure mode does not apply.

TIER = MEASURED_MECHANISM (proven boundary): transitive grounding-inheritance over a native teacher-free relational
  encoder EXISTS but is SHALLOW (~1 hop), driven by relational structure itself (co-training does not deepen it),
  on a synthetic graph-smooth attribute. Counts toward CERT N as a proven boundary. Composes the CHAIN_GRADE
  teacher-free relational encoder (06e5a493d): Stage-1 rel_auc 0.864 is the encoder's neighbour-closeness positive
  control reproduced at this regime; the snowball adds the propagation layer on top.
"""
from __future__ import annotations
import json, os, time
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
MATH_ATOMS = ROOT / "data/substrate_index/math/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"

ATOMIZED_BY = "skunkworks_atomize_2026_07_09_grounding_snowball_transitive_inheritance_v1_MEASURED_MECHANISM"
CELL_COMMIT = "89a088469"
TS = time.time()
TS_ISO = "2026-07-09T00:00:00Z"
SESSION = "2026-07-09_grounding_snowball_transitive_inheritance_v1_landed_vet_SHALLOW_1HOP_MM"

P_ENCODER = (
    "math::CHAIN_GRADE_teacher_free_relational_encoder_cn_subgraph_v1_TEACHER_FREE_graph_neighbor_InfoNCE_plus_"
    "explicit_VICReg_repulsion_learns_structure_aligned_discriminative_concept_codes_with_NO_teacher_on_ConceptNet_"
    "2core_degge2_n10577_meddeg3_primary_Z_497p9_min453p2_5of5_seeds_cv0p073_lift_over_lexical_floor_min297sigma_"
    "repulsion_LOAD_BEARING_ablation_no_repulsion_CROWDS_offcos_to_0p99_5of5_offmargin_min0p987_no_dim_collapse_"
    "effrank_min254p5_of256_TELEMETRY_SENSITIVE_selftest_pert_drops_Z_to_15p8pct_CAVEAT_control_CROWDS_directional_"
    "uniformity_failure_NOT_rank_collapse_effrank_stays_253_lexical_floor_SUBSTANTIAL_Z149_lexical_leak_warning_true_"
    "LIFT_is_load_bearing_evidence_not_absolute_Z_scope_degge2_dense_subgraph_char_trigram_v1_features_deg1_tail_out_"
    "of_scope_teacher_free_code_verified_clean_BGE_eval_only_never_in_any_backward_commit_06e5a493d_2026-07-08"
)

ATOM_ID = (
    "math::MEASURED_MECHANISM_grounding_snowball_transitive_inheritance_v1_transitive_grounding_inheritance_over_the_"
    "native_teacher_free_relational_encoder_is_REAL_but_SHALLOW_apprx_1_HOP_FULL_5seed_7_13_17_23_29_CN_2core_n10577_"
    "E34659_meddeg3_120_ground_seeds_a_SYNTHETIC_graph_smooth_scalar_attached_to_120_seed_atoms_is_read_off_NON_seed_"
    "atoms_by_cosine_k7_label_propagation_over_the_UNGROUNDED_relational_codes_binned_by_graph_distance_to_nearest_"
    "seed_near_acc_d1_0p607_HP0p60_far_acc_d4plus_0p525_decay_0p082_HP0p08_monotone_aggregate_genuine_margin_smooth_"
    "minus_SHUFFLED_0p0965_HP0p06_shuffled_must_fail_control_FLAT_at_chance_0p511_all_bins_apprx0p50_STAGE1_hollow_"
    "skeleton_rel_auc_0p864_HP0p75_grounded_floor_0p546_in_band_NOT_leakage_gap_0p317_HP0p30_reproduces_EXACT_off_"
    "disk_all_5_seeds_PROVEN_BOUNDARY_NOT_CG_because_i_SHALLOW_the_smooth_minus_shuffled_MARGIN_by_distance_collapses_"
    "d1_0p0965_d2_0p0434_d3_0p0228_d4plus_0p0318_genuine_signal_essentially_GONE_by_d2_at_noise_by_d3_a_1_hop_"
    "neighbour_effect_NOT_deep_transitive_inheritance_decay_clears_own_HP_by_only_0p0006_razor_thin_ii_headline_"
    "discriminators_FAIL_CG_cv_gate_decay_cv_0p163_gt_0p15_genuine_margin_cv_0p255_gt_0p20_and_1_of_5_seeds_seed7_"
    "dips_BELOW_HP_on_BOTH_near_acc_0p585_and_genuine_margin_0p053_aggregate_carried_by_other_4_all_5_still_clear_HF_"
    "0p03_iii_SYNTHETIC_graph_smooth_attribute_honest_stand_in_NOT_real_perceptual_grounding_mechanism_certified_is_"
    "narrow_a_graph_smooth_attribute_readable_off_1_hop_neighbours_of_seeds_via_labelprop_over_relational_codes_iv_"
    "co_training_encoder_with_seed_only_attribute_MSE_does_NOT_deepen_propagation_cotrain_lift_near_plus0p007_null_"
    "FULL_is_WEAKER_than_smoke_near_0p630_to_0p607_decay_0p146_to_0p082_genuine_margin_0p135_to_0p096_apprx_half_at_"
    "scale_NOT_MB_HF_because_shuffled_control_flat_planted_signal_selftest_FIRES_strong_decay_0p189_gm_0p174_telemetry_"
    "sensitive_aggregate_decay_monotone_all_5_seeds_positive_margin_rel_auc_tight_SCOPE_synthetic_CN_2core_subgraph_"
    "not_real_grounding_certifies_1_hop_grounded_attribute_propagation_NOT_language_understanding_NOT_deep_transitivity_"
    "composes_CHAIN_GRADE_teacher_free_relational_encoder_stage1_rel_auc_is_its_neighbour_closeness_positive_control_"
    "reproduced_commit_89a088469_2026-07-09"
)

atom = {
    "id": ATOM_ID,
    "name": (
        "MEASURED_MECHANISM (proven boundary): transitive grounding-inheritance over the native teacher-free "
        "relational encoder is REAL but SHALLOW (~1 hop). FULL, 5 seeds 7/13/17/23/29, CN 2-core n=10577 E=34659 "
        "med_deg 3, 120 ground-seeds. A SYNTHETIC graph-smooth scalar attached to 120 seed atoms is read off NON-seed "
        "atoms by cosine k=7 label-propagation over the UNGROUNDED relational codes, binned by graph distance to "
        "nearest seed: near_acc(d1)=0.607 (HP 0.60), far_acc(d4+)=0.525, decay=0.082 (HP 0.08) monotone (aggregate), "
        "genuine_margin (smooth - SHUFFLED)=0.0965 (HP 0.06); the SHUFFLED must-fail control is FLAT at chance (0.511, "
        "all bins ~0.50). Stage-1 hollow-skeleton: rel_auc=0.864 (HP 0.75), grounded_floor=0.546 (in band, NOT "
        "leakage), gap=0.317 (HP 0.30). Reproduces EXACTLY off-disk across all 5 seeds. BOUNDARY (why MM not CG): "
        "(i) SHALLOW -- the smooth-minus-shuffled MARGIN by distance collapses d1=0.0965, d2=0.0434, d3=0.0228, "
        "d4+=0.0318: genuine signal is essentially GONE by d2, at noise by d3, i.e. a 1-hop neighbour effect, NOT "
        "deep transitive inheritance; decay clears its own HP by only +0.0006 (razor-thin). (ii) Headline "
        "discriminators FAIL the CG cv gate: decay cv=0.163 (>0.15), genuine_margin cv=0.255 (>0.20), and 1/5 seeds "
        "(seed7) dips BELOW HP on BOTH near_acc (0.585) and genuine_margin (0.053) -- aggregate carried by the other "
        "4 (all 5 still clear HF 0.03). (iii) SYNTHETIC graph-smooth attribute (honest stand-in, NOT real perceptual "
        "grounding); the certified mechanism is narrow: a graph-smooth attribute is readable off 1-hop neighbours of "
        "seeds via label-prop over relational codes. (iv) Co-training the encoder with a seed-only attribute-MSE loss "
        "does NOT deepen propagation (cotrain_lift +0.007, null). FULL is WEAKER than smoke on every headline "
        "(near 0.630->0.607, decay 0.146->0.082, genuine_margin 0.135->0.096; ~half at scale). NOT MB/HF: the "
        "shuffled control is flat, the planted-signal selftest FIRES strong (decay 0.189, gm 0.174 -> telemetry-"
        "sensitive), aggregate decay is monotone, all 5 seeds have positive margin, rel_auc is tight. SCOPE: synthetic "
        "CN 2-core subgraph, NOT real grounding; certifies 1-hop grounded-attribute propagation, NOT language "
        "understanding and NOT deep transitivity."
    ),
    "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "kind": "experiment_landed_vet",
    "cert_status": (
        "mm_grounding_snowball_transitive_inheritance_v1_transitive_grounding_inheritance_over_native_teacher_free_"
        "relational_encoder_REAL_but_SHALLOW_1_hop_near_acc_d1_0p607_far_d4plus_0p525_decay_0p082_monotone_genuine_"
        "margin_vs_shuffled_0p0965_shuffled_control_flat_at_chance_0p511_stage1_rel_auc_0p864_grounded_floor_0p546_in_"
        "band_gap_0p317_5seed_full_reproduces_exact_off_disk_PROVEN_BOUNDARY_shallow_margin_by_distance_collapses_"
        "d1_0p0965_d2_0p0434_d3_0p0228_d4_0p0318_gone_by_d2_1_hop_not_deep_decay_cv_0p163_genuine_margin_cv_0p255_"
        "seed7_below_HP_on_both_synthetic_graph_smooth_attribute_not_real_grounding_cotrain_does_not_deepen_plus0p007_"
        "full_weaker_than_smoke_half_at_scale"
    ),
    "cert_class": (
        "single_hop_dominant_label_propagation_of_a_synthetic_graph_smooth_scalar_attribute_from_a_seed_set_over_the_"
        "ungrounded_relational_codes_of_a_teacher_free_conceptnet_2core_encoder_read_by_cosine_k7_nearest_grounded_"
        "seeds_binned_by_graph_distance_where_the_load_bearing_signal_is_the_distance_decay_of_ordering_accuracy_for_a_"
        "graph_smooth_attribute_vs_a_shuffled_empirical_null_measured_5seed_full_n10577_120_ground_seeds_the_genuine_"
        "smooth_minus_shuffled_margin_decays_to_chance_within_1_hop_synthetic_attribute_not_real_perceptual_grounding_"
        "deep_transitivity_and_real_grounding_untested"
    ),
    "description": (
        "LANDED-VET (AUDIT-ONLY, HIGH) of exp_grounding_snowball_transitive_inheritance_v1 (commit 89a088469; prereg "
        "2026-07-09; run_mode=full; 5 seeds 7/13/17/23/29; n_nodes 12000 -> CN 2-core n=10577 E=34659 med_deg 3; 120 "
        "ground-seeds; cell verdict HARD_PASS). Verified off-disk by independent .venv recompute -- aggregated "
        "per_seed[] over all 5 seeds; EVERY prereg gate value reproduces EXACTLY. "
        "RECOMPUTED (mean 5 seeds; pstd/cv): near_acc(d1)=0.60727 cv=0.0215 [0.585,0.6191,0.6017,0.6207,0.6099]; "
        "far_acc(d4+)=0.52520 cv=0.0240 (far_bin=3, n=174 nodes); decay=0.08206 cv=0.1627 "
        "[0.0786,0.0991,0.0588,0.0859,0.088]; shuf_near=0.51081 cv=0.0313 (control flat, all bins ~0.49-0.51); "
        "genuine_margin=0.09646 cv=0.2548 [0.0534,0.0966,0.0927,0.1143,0.1253]; rel_auc=0.86351 cv=0.0025; "
        "grounded_floor=0.54640 (in [0.42,0.62], NOT leakage <0.70); stage1_gap=0.31711 (HP 0.30); "
        "cotrain_lift_near=+0.00732 (null; smoke was -0.023); assort smooth=0.7102 shuf=0.0047 precond_ok=True; "
        "selftest decay 0.1889 gm 0.1743 (fires STRONG). "
        "MECHANISM: attach a synthetic graph-smooth scalar (diffused over the real CN 2-core subgraph, honest "
        "stand-in per prereg) to 120 seed atoms; read it off NON-seed atoms via cosine k=7 label-propagation over the "
        "UNGROUNDED relational codes (the Gunther transitive-inheritance kernel), binned by graph distance to nearest "
        "seed; the shuffled-attribute arm (graph-smoothness destroyed) is the must-fail control isolating genuine "
        "propagation from encoder/readout artifact. "
        "FIVE ADVERSARIAL CHECKS (all off per_seed[], not verdict_msg): "
        "(P1) SHUFFLED MUST-FAIL CONTROL FIRES: shuffled arm flat at chance (near 0.511, all bins ~0.49-0.51), while "
        "smooth decays -- graph-smoothness is load-bearing. (P2) SELFTEST TELEMETRY-SENSITIVE: planted graph-smooth "
        "codes give decay 0.189, gm 0.174 (far bin drops to 0.499); perturbing the attribute moves the metric -- not "
        "analytically pinned. (P3) SHALLOWNESS (the load-bearing bound): smooth-minus-shuffled MARGIN by distance = "
        "d1 0.0965, d2 0.0434, d3 0.0228, d4+ 0.0318 -- genuine signal essentially GONE by d2, at noise by d3+; the "
        "'transitive inheritance' is a 1-hop neighbour effect. decay=0.0821 clears its own HP (0.08) by only +0.0006. "
        "(P4) TELEMETRY + CARDINALITY + PER-SEED: 5/5 seeds complete (seed_failures=[]), cardinality_ok; rel_auc tight "
        "(cv 0.0025) reproduces the encoder's neighbour-closeness (positive control); but decay cv=0.163 (>0.15 CG) "
        "and genuine_margin cv=0.255 (>0.20 MM), and seed7 dips BELOW HP on BOTH near_acc (0.585<0.60) and "
        "genuine_margin (0.053<0.06) -- aggregate carried by the other 4 (all 5 still clear HF 0.03). 'monotone=True' "
        "is on the aggregate mean-by-bin; 3/5 individual seeds show a small non-monotonic uptick at the far bin d3 "
        "(n=174, noisy) -- does not invalidate the aggregate verdict but scopes it. (P5) HONEST SCOPE: the grounded "
        "scalar is SYNTHETIC (graph-smooth field, not a measured perceptual attribute); certifies 1-hop grounded-"
        "attribute PROPAGATION over relational structure, NOT language understanding, NOT real grounding, NOT deep "
        "transitivity. FULL is WEAKER than smoke on every headline (near 0.630->0.607, decay 0.146->0.082, "
        "genuine_margin 0.135->0.096; ~half the smoke decay/margin at scale). "
        "CROSS-ARC OVERLAP (USER-locked): substrate_query 'transitive grounding inheritance seed propagation graph "
        "distance decay relational encoder attribute label propagation' -> top hits are GENERIC 'propagation' nodes "
        "(wordnet/concept 'propagation' 0.4424, 'CN_propagation' 0.3477), an R-GCN/HAN drill note 0.3447, and a "
        "DIFFERENT-mechanism 'Confidence propagation' multi-hop prereg 0.3408; NONE substantively about transitive "
        "GROUNDING-inheritance. Genuinely novel mechanism, NOT a rediscovery (matches prereg's own scan). "
        "TIER = MEASURED_MECHANISM (proven boundary): the mechanism is real, reproduces exactly, discriminator fires "
        "non-vacuously (shuffled flat + selftest strong) -- but it is SHALLOW (~1 hop; margin gone by d2), the "
        "headline discriminators fail the CG cv gate, the attribute is synthetic, and co-training does not deepen it. "
        "Symmetric anti-negativity: NOT deflated to MB/HF (control flat, selftest fires, aggregate decay monotone, "
        "5/5 seeds positive margin clearing HF, rel_auc tight, all prereg HP bands cleared on aggregate); NOT inflated "
        "to a deep-transitive-grounding CG (shallow, synthetic, marginal decay, high cv, co-train null). Counts toward "
        "CERT N as a proven boundary. Composes the CHAIN_GRADE teacher-free relational encoder (06e5a493d): Stage-1 "
        "rel_auc 0.864 is that encoder's neighbour-closeness positive control reproduced at this regime; the snowball "
        "adds the grounding-propagation layer on top. commit 89a088469 2026-07-09."
    ),
    "provenance": {
        "cell": "experiments/exp_grounding_snowball_transitive_inheritance_v1.py",
        "commit": CELL_COMMIT,
        "metrics_path": "data/exp_grounding_snowball_transitive_inheritance_v1/metrics.json",
        "prereg": "preregs/2026-07-09_grounding_snowball_transitive_inheritance_v1.md",
        "seeds": [7, 13, 17, 23, 29],
        "run_mode": "full",
        "whole_cell_verdict": "HARD_PASS",
        "whole_cell_verdict_msg": "HARD_PASS | STAGE1_HARD_PASS | STAGE2_HARD_PASS",
        "audit_tier": "MEASURED_MECHANISM",
        "ts_iso": TS_ISO,
        "atomized_by": ATOMIZED_BY,
        "verified_off_data": True,
        "verified_off_data_note": (
            "Independent .venv recompute aggregated per_seed[] over all 5 seeds: EVERY prereg gate reproduces EXACTLY. "
            "near_acc(d1)=0.60727 (cv 0.0215), far_acc(d4+)=0.52520, decay=0.08206 (cv 0.1627), shuf_near=0.51081, "
            "genuine_margin=0.09646 (cv 0.2548), rel_auc=0.86351 (cv 0.0025), grounded_floor=0.54640, gap=0.31711, "
            "cotrain_lift=+0.00732. Smooth-minus-shuffled margin by distance: d1=0.0965 d2=0.0434 d3=0.0228 "
            "d4+=0.0318 (signal gone by d2). seed7 below HP on near_acc (0.585) and genuine_margin (0.053); all 5 "
            "seeds clear HF 0.03. seed_failures=[] (5/5 complete). Selftest decay 0.1889 gm 0.1743 (fires). "
            "FULL weaker than smoke: near 0.630->0.607, decay 0.146->0.082, gm 0.135->0.096."
        ),
    },
    "verified_numbers": {
        "run_mode": "full", "n_seeds": 5, "seeds": [7, 13, 17, 23, 29], "seed_failures_count": 0,
        "cn_subgraph_n": 10577, "cn_subgraph_E": 34659, "median_degree": 3.0, "n_ground_seeds": 120,
        "stage1_rel_auc_mean": 0.86351, "stage1_rel_auc_cv": 0.0025,
        "stage1_grounded_floor_mean": 0.54640, "stage1_gap": 0.31711,
        "leakage_flag": False, "baseline_in_band": True,
        "near_acc_d1_mean": 0.60727, "near_acc_cv": 0.0215,
        "far_acc_d4plus_mean": 0.52520, "far_bin_index": 3, "far_bin_n_nodes": 174,
        "decay_mean": 0.08206, "decay_cv": 0.1627, "monotone_aggregate": True,
        "shuffled_near_mean": 0.51081, "genuine_margin_mean": 0.09646, "genuine_margin_cv": 0.2548,
        "margin_by_distance": {"d1": 0.0965, "d2": 0.0434, "d3": 0.0228, "d4plus": 0.0318},
        "per_seed_near_acc": [0.585, 0.6191, 0.6017, 0.6207, 0.6099],
        "per_seed_genuine_margin": [0.0534, 0.0966, 0.0927, 0.1143, 0.1253],
        "per_seed_decay": [0.0786, 0.0991, 0.0588, 0.0859, 0.088],
        "seed7_below_HP_near_acc": True, "seed7_below_HP_genuine_margin": True, "all_seeds_clear_HF": True,
        "cotrain_lift_near": 0.00732, "cotrain_deepens_propagation": False,
        "assort_smooth": 0.7102, "assort_shuffled": 0.0047, "precondition_ok": True,
        "selftest_decay": 0.1889, "selftest_genuine_margin": 0.1743, "discriminator_fires_at_scale": True,
        "smoke_near_acc": 0.630, "smoke_decay": 0.146, "smoke_genuine_margin": 0.135,
        "full_weaker_than_smoke": True,
        "bands_HP": {"near_acc": 0.60, "decay": 0.08, "genuine_margin": 0.06, "rel_auc": 0.75, "gap": 0.30},
        "bands_HF": {"near_acc": 0.55, "decay": 0.03, "genuine_margin": 0.03},
        "cardinality_ok": True, "arms_differ_verified": True, "all_headline_reproduce_exact": True,
    },
    "can_fail_discriminator_verdict": (
        "FIRES + telemetry-sensitive on the primary contrast, but the depth/CG bar is NOT reached. (1) The shuffled "
        "MUST-FAIL control (same codes, same seeds, graph-smoothness destroyed) stays FLAT at chance (near 0.511, all "
        "bins ~0.49-0.51) while the smooth arm decays -- the HARD_FAIL 'shuffled ~ smooth => leakage/artifact' branch "
        "was reachable (genuine_margin HF=0.03) and did not fire (margin 0.0965). (2) The planted-signal selftest "
        "fires STRONG (decay 0.189, gm 0.174; far bin drops to 0.499) and perturbing the attribute moves the metric "
        "-> not analytically pinned. (3) BUT the discriminator only fires at 1 HOP: the smooth-minus-shuffled margin "
        "collapses to 0.043 by d2 and ~0.02-0.03 (noise) by d3+, decay clears its own HP by only +0.0006, and the "
        "headline discriminators fail the CG cv gate (decay cv 0.163, genuine_margin cv 0.255) with 1/5 seeds below "
        "HP on two metrics -- so the cell CAN and DOES fire the 1-hop grounded-propagation contrast, but CANNOT fire "
        "a DEEP-transitive-inheritance claim at this regime. Precisely why this is a PROVEN BOUNDARY (MM), not a "
        "HARD_PASS-to-CG."
    ),
    "framing_corrections_vs_cell_author_and_director": [
        "CONFIRM Director's pass-through framing: transitive grounding-inheritance is REAL but SHALLOW (~1 hop), "
        "driven by relational structure (co-training does not deepen it, cotrain_lift +0.007), shuffled control flat, "
        "attribute is a synthetic graph-smooth stand-in. Independent recompute confirms every gate.",
        "ADD (symmetric anti-negativity / Fix #28): FULL is WEAKER than smoke on EVERY headline -- near_acc "
        "0.630->0.607, decay 0.146->0.082, genuine_margin 0.135->0.096, i.e. roughly HALF the smoke decay/margin at "
        "scale. decay=0.0821 clears its own HP (0.08) by only +0.0006 (razor-thin). The shallowness is MORE "
        "pronounced at FULL than the smoke implied: the smooth-minus-shuffled margin is already 0.043 by d2 and at "
        "noise (0.02-0.03) by d3+. Do not carry the smoke numbers as the canonical headline.",
        "SCOPE the 'monotone' claim: monotone=True is on the AGGREGATE mean-by-bin; 3/5 individual seeds (13/17/29) "
        "show a small non-monotonic uptick at the far bin d3 (n=174 nodes, noisy). The aggregate verdict holds, but "
        "'monotone decay' is an aggregate property, not a per-seed one.",
        "SCOPE the per-seed spread: 1/5 seeds (seed7) individually dips BELOW HP on BOTH near_acc (0.585<0.60) AND "
        "genuine_margin (0.053<0.06); the aggregate HARD_PASS is carried by the other 4 seeds. All 5 still clear the "
        "HF floors (near 0.55, margin 0.03). This is why the headline discriminators fail the CG cv gate (decay cv "
        "0.163, genuine_margin cv 0.255) and the tier is MM not CG.",
        "SYMMETRIC anti-negativity the OTHER way: do NOT deflate this to MB/HF. The effect is genuinely real -- the "
        "shuffled must-fail control is flat at chance, the planted-signal selftest fires strong (decay 0.189), the "
        "aggregate decay is monotone, all 5 seeds have positive genuine_margin clearing HF, rel_auc is tight and "
        "strong, and all prereg HARD_PASS bands cleared on aggregate. It is a clean positive with a real 1-hop bound.",
        "HONESTY on the attribute (load-bearing, per prereg): the grounded scalar is a SYNTHETIC graph-smooth field "
        "diffused over the real CN 2-core subgraph -- an honest stand-in for a measured non-symbolic attribute, NOT "
        "real perceptual grounding and NOT 'teaching the substrate English'. The certified mechanism is narrow: a "
        "graph-smooth attribute is readable off 1-hop neighbours of grounded seeds via label-prop over relational "
        "codes. Frame any downstream use as 1-hop grounded-attribute propagation, never as grounding/comprehension.",
    ],
    "revival_or_extension_criterion": (
        "MM scope: certifies that a SYNTHETIC graph-smooth attribute attached to a 120-atom seed set is readable off "
        "1-hop NON-seed neighbours (near_acc d1 0.607, genuine_margin 0.0965 vs shuffled) via k=7 cosine label-prop "
        "over the ungrounded teacher-free relational codes, decaying to ~chance within 1 hop, 5 seeds, CN 2-core "
        "n=10577. PROMOTE-toward-CG / EXTENSIONS (each a NEW cell, composes NOT supersedes): (1) DEEPEN THE SNOWBALL "
        "-- a mechanism (iterative propagation, higher-order kernels, or a structurally richer attribute) that keeps "
        "the smooth-minus-shuffled margin above noise at d2-d3 (currently 0.043 / 0.023); the current mechanism is "
        "1-hop. (2) REAL (non-synthetic) node attribute keyed to ConceptNet -- test whether a MEASURED attribute "
        "(size/weight/magnitude) propagates the same way; the synthetic graph-smooth field is the honest stand-in "
        "the current cert is scoped to. (3) TIGHTEN THE MARGIN cv -- a regime/readout where genuine_margin cv < 0.15 "
        "and no seed dips below HP (currently seed7 does, cv 0.255). (4) PREDICTION C (deferred): causal/index "
        "diagnostic -- perturbing the grounded feature must move the representation >= 2x a matched relation-only "
        "perturbation. DEMOTION trigger: a re-run where the shuffled control is NOT flat (near_acc_shuffled > 0.55, "
        "leakage), or the smooth arm does not exceed chance at d1 (near_acc < 0.55), or genuine_margin < 0.03 "
        "(discriminator goes inert)."
    ),
    "composes": [P_ENCODER],
    "compose_note": (
        "Composes the CHAIN_GRADE teacher-free relational encoder cn_subgraph_v1 (commit 06e5a493d): this cell REUSES "
        "that encoder pipeline (load_cn_subgraph, char_trigram_features, ProjHead, info_nce, vicreg_repulsion) and "
        "adds only the grounding/attribute/propagation layer. The Stage-1 relational-AUC probe (rel_auc 0.864, cv "
        "0.0025) is the encoder's neighbour-closeness POSITIVE CONTROL reproduced at this regime (consistent with the "
        "encoder cert's structure-aligned codes). The snowball MM is thus a propagation layer ON TOP of the certified "
        "encoder: grounding attached to a seed set inherits transitively for ~1 hop through the encoder's relational "
        "web. Brain-grounding: transitive grounding-inheritance (Gunther et al. 2018) + ATL graded-hub gradient -- "
        "meaning attached to a few anchors spreading to relationally-close neighbours, decaying with distance."
    ),
    "cross_arc_overlap_check": (
        "substrate_query 'transitive grounding inheritance seed propagation graph distance decay relational encoder "
        "attribute label propagation' -> top hits GENERIC 'propagation' nodes: wordnet/concept 'propagation' 0.4424, "
        "'CN_propagation' 0.3477, wordnet gloss 0.3486; an R-GCN/HAN relational-message-passing drill note 0.3447; a "
        "DIFFERENT-mechanism 'Confidence propagation' mixed-confidence multi-hop prereg 0.3408. NONE substantively "
        "about transitive GROUNDING-inheritance (they are about the word 'propagation', GNN message passing, or "
        "confidence over reasoning chains). Genuinely novel mechanism, NOT a rediscovery -- matches the prereg's own "
        "scan (top 0.3135 Locative_relation::Distance FrameNet frame, nothing substantive). The July-1 INT8-"
        "rediscovery failure mode does not apply."
    ),
    "anchor": "grounding_snowball_transitive_inheritance_v1",
    "cell_commit": CELL_COMMIT,
    "seeds": [7, 13, 17, 23, 29],
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
        "transitive grounding-inheritance over the native teacher-free relational encoder is REAL but SHALLOW (~1 hop); MEASURED_MECHANISM proven boundary",
        "a synthetic graph-smooth scalar on 120 seed atoms is read off 1-hop non-seed neighbours via k=7 label-prop over ungrounded relational codes: near_acc(d1)=0.607 genuine_margin=0.0965 vs shuffled-flat control",
        "the snowball is 1-hop: smooth-minus-shuffled margin collapses d1=0.0965 d2=0.0434 d3=0.0228 d4+=0.0318, gone by d2; decay=0.082 barely clears HP 0.08",
        "BOUNDARY: headline discriminators fail CG cv gate (decay cv 0.163, genuine_margin cv 0.255); seed7 dips below HP on both near_acc (0.585) and genuine_margin (0.053); attribute synthetic; co-training does not deepen (cotrain_lift +0.007)",
        "FULL is weaker than smoke: near 0.630->0.607, decay 0.146->0.082, genuine_margin 0.135->0.096 (~half at scale)",
        "NOT MB/HF: shuffled control flat at chance, planted-signal selftest fires strong (decay 0.189), aggregate decay monotone, 5/5 seeds positive margin clearing HF, rel_auc tight 0.864",
        "SCOPE: synthetic CN 2-core subgraph, not real grounding; certifies 1-hop grounded-attribute propagation NOT language understanding NOT deep transitivity; composes the CHAIN_GRADE teacher-free encoder (06e5a493d) whose neighbour-closeness is the Stage-1 positive control",
        "grounding_snowball_transitive_inheritance_v1 landed-VET MEASURED_MECHANISM",
    ],
    "added_atom_id": None,
}
atom["added_atom_id"] = atom["id"]

ledger = {
    "ts": TS, "ts_iso": TS_ISO, "op": "add", "atom_id": atom["id"], "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "disposition": "measured_mechanism_proven_boundary_grounding_snowball_transitive_inheritance_v1_transitive_grounding_inheritance_is_real_but_shallow_1_hop",
    "cert_status": atom["cert_status"],
    "cert_class": atom["cert_class"],
    "cert_increment_delta": {"CG": 0, "MM": 1, "HF": 0},
    "cert_delta": {"CG": 0, "MM": 1, "HF": 0},
    "cert_delta_note": (
        "MM +1 (proven boundary): transitive grounding-inheritance over the native teacher-free relational encoder is "
        "REAL but SHALLOW (~1 hop). FULL, 5 seeds 7/13/17/23/29, CN 2-core n=10577 E=34659 med_deg 3, 120 ground-"
        "seeds. A synthetic graph-smooth scalar on 120 seed atoms is read off NON-seed atoms via k=7 cosine label-"
        "prop over the ungrounded relational codes, binned by graph distance: near_acc(d1)=0.607 (HP 0.60), "
        "far_acc(d4+)=0.525, decay=0.082 (HP 0.08) monotone (aggregate), genuine_margin (smooth-SHUFFLED)=0.0965 "
        "(HP 0.06); shuffled must-fail control FLAT at chance (0.511). Stage-1: rel_auc=0.864 (HP 0.75), "
        "grounded_floor=0.546 (in band, NOT leakage), gap=0.317 (HP 0.30). Verified off-disk by independent .venv "
        "recompute -- every gate reproduces EXACTLY across all 5 seeds. WHY MM NOT CG: (i) SHALLOW -- smooth-minus-"
        "shuffled margin by distance collapses d1=0.0965, d2=0.0434, d3=0.0228, d4+=0.0318 (gone by d2, noise by "
        "d3+); a 1-hop neighbour effect, NOT deep transitivity; decay clears own HP by only +0.0006. (ii) Headline "
        "discriminators fail CG cv gate: decay cv=0.163, genuine_margin cv=0.255; seed7 dips BELOW HP on BOTH "
        "near_acc (0.585) and genuine_margin (0.053), aggregate carried by other 4 (all 5 clear HF). (iii) SYNTHETIC "
        "graph-smooth attribute (honest stand-in, NOT real perceptual grounding). (iv) Co-training does NOT deepen "
        "(cotrain_lift +0.007, null). FRAMING (symmetric anti-negativity): FULL is WEAKER than smoke on every "
        "headline (near 0.630->0.607, decay 0.146->0.082, gm 0.135->0.096; ~half at scale); do not carry smoke as "
        "canonical. 'monotone' is aggregate-only (3/5 seeds show a minor d3 uptick, n=174). NOT deflated to MB/HF "
        "(control flat, selftest fires strong decay 0.189, aggregate decay monotone, 5/5 positive margin clearing "
        "HF, rel_auc tight, all prereg HP bands cleared on aggregate); NOT inflated to deep-transitive CG. SCOPE: "
        "synthetic CN 2-core subgraph, NOT real grounding; certifies 1-hop grounded-attribute propagation, NOT "
        "language understanding, NOT deep transitivity. Cross-arc: genuinely novel (top substrate_query hits generic "
        "'propagation' + a different-mechanism confidence-propagation prereg; NONE substantive), not a rediscovery. "
        "Composes the CHAIN_GRADE teacher-free relational encoder (06e5a493d) whose neighbour-closeness is the "
        "Stage-1 rel_auc positive control. Needs orchestrator Store-sync (skunkworks atoms do not auto-persist)."
    ),
    "verified_off_data": True,
    "verification": "recomputed_near_far_decay_shuffled_genuine_margin_rel_auc_grounded_floor_gap_cotrain_per_seed_all_5seed_exact_match + margin_by_distance_decomposition_shows_signal_gone_by_d2_1hop + shuffled_control_flat_at_chance + selftest_planted_signal_fires_strong + seed7_below_HP_on_near_acc_and_genuine_margin + full_weaker_than_smoke_half_at_scale + cross_arc_substrate_query_no_substantive_overlap_novel",
    "anchor": "grounding_snowball_transitive_inheritance_v1",
    "cell_commit": CELL_COMMIT,
    "auditor": "hdi_skunkworks", "atomized_by": "hdi_skunkworks",
    "landed_VET_session": SESSION,
    "composes": [P_ENCODER],
    "needs_orchestrator_store_sync": True,
    "raw_metrics_paths": ["data/exp_grounding_snowball_transitive_inheritance_v1/metrics.json"],
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
    append_jsonl_a5(MATH_ATOMS, atom, "math/atoms (grounding snowball transitive inheritance v1 SHALLOW 1-hop MEASURED_MECHANISM)")
    append_jsonl_a5(CERT_LEDGER, ledger, "cert_ledger (MM +1)")
    print(f"[A5] DONE OK -> grounding snowball transitive inheritance v1 SHALLOW 1-hop MEASURED_MECHANISM (MM +1)")


if __name__ == "__main__":
    main()
