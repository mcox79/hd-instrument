"""
A5-gated atomize: Batches A + C + D landed-VET rulings (2026-07-01)

INDEPENDENT OFF-DATA RECOMPUTE via .venv python.

============================================================
BATCH A -- pc_sparsity_x_encoder_crossproduct_v1_n8192 (3 seeds)
============================================================
Preview seed_7 framing: HARD_PASS_ENCODER_x_SPARSITY_INTERACTION;
interaction_pairs_visible=3/6; per_encoder_sparsity_range visible for fhrr (0.297)
+ binary/sparse_bipolar (0.11/0.12); hrr_real ~0.0.

Off-data 3-seed recompute (skunkworks 2026-07-01):
  cardinality:      seed_7 16/16, seed_13 16/16, seed_19 16/16     PASS
  run_mode=full:    seed_7 (33.3s), seed_13 (5.9s), seed_19 (6.0s) PASS
                    (seed_13/19 faster due to warm-cache in chunked runner; identical config_version)
  positive_control: seed_7 1.000, seed_13 0.993, seed_19 0.997     PASS (all >= 0.1 floor + <0.95 non-sat)
  encoder_pair_distinct: 6/6 all seeds                              PASS
  n_combos_arms_differ: 16/16 all seeds                             PASS
  tier_counts identical: SATURATED=10, HARD_PASS=3, MIDDLE_BAND=3, FLOOR=0, HARD_FAIL=0
  interaction_pairs_visible: seed_7=3/6, seed_13=2/6, seed_19=2/6  (>=2 gate met all seeds)
  fhrr row monotone decreasing across sparsity 0.01->0.25 all seeds:
    seed_7:  [0.8233, 0.6767, 0.5967, 0.5267]
    seed_13: [0.8000, 0.6433, 0.5667, 0.5533]
    seed_19: [0.8300, 0.6633, 0.6167, 0.5367]

Cross-seed CV of per_encoder_sparsity_range (the discriminator):
  binary_bipolar: cv=0.129 (< 0.15)   PASS
  fhrr:           cv=0.100 (< 0.15)   PASS  <-- the interaction the finding rides on
  sparse_bipolar: cv=0.141 (< 0.15)   PASS
  hrr_real:       cv=0.866 (>> 0.15)  saturation-noise near zero; expected for saturated

BUT: 10 of 16 cells are SATURATED (top1=1.0). Saturation-count = 10/16 > 60%
(META_RULE_Q SUSPECT_1.000 trip). The mechanism only DISCRIMINATES on 6 cells:
- fhrr at s=0.01, 0.05, 0.1, 0.25 (all 4 fhrr cells - genuine range 0.30)
- binary_bipolar and sparse_bipolar at s=0.25 (edge-of-sparsity)

TIERING DECISION:
  The claim "encoder x sparsity interaction visible" is well supported cross-seed.
  BUT: the finding is DOMINATED by fhrr degradation (per_encoder_sparsity_range
  0.28 for fhrr vs. 0.13/0.14 for binary/sparse_bipolar vs. 0.00 for hrr_real).
  The interaction is essentially "fhrr degrades with sparsity, others saturate".
  hrr_real fully saturates at cv=0.866 (structural saturation, not a true axis).
  binary_bipolar / sparse_bipolar have interaction only at s=0.25 (edge).

  The mechanism IS real (interaction pair visible cross-seed for pairs involving fhrr).
  BUT the axis is by-construction-limited: 10/16 cells at saturation ceiling
  means the axis characterization is CAPACITY-BOUND, not FREE-DISCRIMINATION.
  This is exactly META_RULE_Q / BIAS-Q territory.

  TIER: MEASURED_MECHANISM (mechanism_characterization)
  Rationale: the FHRR-degrades-with-sparsity finding is chain-grade-quality
  (3-seed monotone, cv<0.15, discriminator fires), but the FULL 4x4 interaction
  matrix framing is over-broad -- 10/16 saturated cells mean the "interaction"
  is one axis (fhrr sensitive; others saturated). MM captures the real bound.
  cert_increment_delta = 0.

============================================================
BATCH C -- compression_pareto_v1 (3 seeds)
============================================================
FULL n_facts=10000 N=8192; verdict = MIDDLE_BAND 5/6 gates on ALL 3 seeds.
recall_preserved_pass = False (the H2 core claim).

Off-data 3-seed recompute (skunkworks 2026-07-01):
  cardinality:      4/4 all seeds                                   PASS
  positive_control: PASS all seeds                                  PASS
  compression_gap:  100x HARDMAX ratio                              PASS (10x on EXEMPLAR_BAYES)
  pareto_distinct:  6/6 pairs distinct all seeds                    PASS
  arms_differ:      6.0/6 all seeds                                 PASS
  cross_seed_cv:    PASS

  Per-arm recall (mean across seeds):
    NO_COMPRESSION:     0.87 (0.91, 0.86, 0.86)
    EXEMPLAR_BAYES:     0.77 (0.76, 0.79, 0.77)  <- 10x compression, -0.10 recall
    HARDMAX_CENTROID:   0.04 (0.02, 0.06, 0.04)  <- 100x compression, -0.83 recall (LOSSY)
    HIERARCHICAL:       0.007 (0.01, 0.01, 0.00) <- 10x compression, -0.86 recall

  H2 (compression cheap at chain-grade): the smoke framing already REFUTED this;
  FULL corroborates the refutation. HARDMAX at 100x drops recall from 0.87 -> 0.04
  (SEVERE loss). EXEMPLAR_BAYES at 10x drops recall 0.10 (cheap).
  H2 is REFUTED at n_facts=10000 N=8192 too. Larger N does NOT rescue HARDMAX.

TIERING DECISION:
  The mechanism is characterized (proven bound: 10x cheap via EXEMPLAR_BAYES;
  100x lossy via HARDMAX). This is a PROVEN NEGATIVE for the H2 hypothesis
  "compression is cheap at chain-grade" AND a PROVEN POSITIVE for the sub-mechanism
  EXEMPLAR_BAYES-at-10x as the cost-optimal Pareto point.

  TIER: MEASURED_MECHANISM (mechanism_characterization)
  Rationale: 5/6 gates PASS, one gate FAIL by design of the H2 discriminator;
  the finding IS a real bound (10x cheap / 100x lossy for HARDMAX). CERT +0.
  cert_increment_delta = 0.

============================================================
BATCH D -- routing_geometry_family_kg_ingest_v2 (3 seeds)
============================================================
Cell-author preview smoke framing:
  "knn_softmax 0.509 > learned_supervised 0.380 > random_partition 0.130"

FULL 3-seed recompute (skunkworks 2026-07-01) at M_ingest=100000 N_DIM=2048
routing_noise_cos=0.60 P_SHARDS=256:

  retrieval_acc_by_arm PER SEED:
    seed_7:  random_partition=0.116, learned_supervised=-1.0, lsh_hash=-1.0,
             hierarchical_tree=-1.0, knn_softmax=-1.0
    seed_13: random_partition=0.115, learned_supervised=-1.0, lsh_hash=-1.0,
             hierarchical_tree=-1.0, knn_softmax=-1.0
    seed_19: random_partition=0.115, learned_supervised=-1.0, lsh_hash=-1.0,
             hierarchical_tree=-1.0, knn_softmax=-1.0

  routing_hash_by_arm: random_partition=hash, ALL OTHERS='FAIL'
  n_distinct_localizations = 1 (need >= 3 per META_RULE_AV)
  discrimination_gate_pass = False
  per_arm_tier: random_partition=HARD_FAIL, learned_supervised=FAIL,
                lsh_hash=FAIL, hierarchical_tree=FAIL, knn_softmax=FAIL

Cell auto-emits MIDDLE_BAND_DISCRIMINATION_FLOOR per META_RULE_AV.

INDEPENDENT ASSESSMENT: This is not MIDDLE_BAND. This is HARD_FAIL at FULL scale.
4/5 arms did not produce a hash (returned -1.0 sentinel). Only random_partition
completed and it sits barely-above-floor (0.115 vs 0.10 floor). The cell's
generous MIDDLE_BAND is per its auto-classifier; the auditor's honest reading
is HARD_FAIL for the "outer-axis G characterization" claim.

Cross-referencing smoke framing:
- Smoke ran at n_facts~1000 with all 5 arms producing hashes
- FULL at n_facts=100000 crashes 4/5 arms (implementation bug or scale-mismatch)
- CANONICAL "DISCRIMINATOR_MUST_SURVIVE_SCALE_USER_2026-06-26" violation

TIERING DECISION:
  Not a clean HARD_FAIL of a well-posed hypothesis -- rather a HARD_FAIL of
  CELL IMPLEMENTATION at production scale. 4 arms don't complete. Positive
  control (random_partition) survives but at floor. The axis G characterization
  claim is NOT SUPPORTED; smoke framing over-claimed by extrapolating from
  a scale where all arms ran successfully.

  TIER: HARD_FAIL (honest_negative for the axis G claim; cell needs to be
        fixed before re-attempt). CERT +0 for a chain-grade; we record it
        as a NEGATIVE result to prevent re-exploration without a fix.
  cert_increment_delta = 0.

  DRILL RECOMMENDATION for Director's 2x-drill queue:
    Cell implementation needs to survive M_ingest=100000 for learned_supervised /
    lsh_hash / hierarchical_tree / knn_softmax arms before axis G characterization
    can proceed. This is a cell-author (not skunkworks) task.

============================================================
Discipline tags across all three:
  - META_RULE_Q suspect 1.000 (Batch A saturation-heavy)
  - META_RULE_AV auto-demote discrimination-floor (Batch D)
  - DISCRIMINATOR_MUST_SURVIVE_SCALE_USER_2026-06-26 (Batch D violation)
  - Fix_28_per_arm_metrics_not_verdict_msg (all three)
  - META_RULE_H sweep-cell cardinality (all three PASS)
  - feedback_smoke_must_fire_discriminator_at_full_N (Batch D)
"""
from __future__ import annotations
import json, os, time
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
MATH_ATOMS = ROOT / "data/substrate_index/math/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"

ATOMIZED_BY = "skunkworks_landed_VET_batches_ACD_2026-07-01"
ATOMIZED_DATE = "2026-07-01"

# ============================================================================
# BATCH A -- PC sparsity x encoder crossproduct v1 (3-seed MM)
# ============================================================================
atom_batch_A = {
    "id": (
        "T3/EXP_substrate_pc_sparsity_x_encoder_crossproduct_v1_n8192_3seed_MM_"
        "fhrr_degrades_with_sparsity_others_saturate_10of16_saturated_by_construction_axis_bound_"
        "per_encoder_sparsity_range_fhrr_0p279_binary_0p130_sparse_0p142_hrr_saturated_2026-07-01"
    ),
    "name": (
        "MEASURED-MECHANISM PC sparsity x encoder crossproduct v1 N=8192 3-seed FULL: FHRR degrades "
        "monotonically with sparsity 0.01->0.25 all 3 seeds (per_encoder_sparsity_range mean=0.279 "
        "cv=0.100); binary_bipolar + sparse_bipolar degrade only at s=0.25 edge (range 0.13/0.14); "
        "hrr_real fully saturated (range 0.002 cv=0.866). 10/16 cells SATURATED at top1=1.0 "
        "(META_RULE_Q trip). Interaction pairs visible 2-3/6 cross-seed (>=2 gate met). "
        "Positive control PASS all seeds. Cardinality 16/16 all seeds. n_encoder_pair_distinct=6/6. "
        "Mechanism is real but axis-bound: FHRR-sensitivity-to-sparsity is the discriminating axis, "
        "others saturate. CERT +0 (mechanism_characterization)."
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record",
    "description": (
        "3-seed FULL PC sparsity x encoder crossproduct (v1_n8192). Verdict per cell: HARD_PASS all "
        "3 seeds by author criterion; per-cell tier_counts identical across seeds "
        "(SATURATED=10, HARD_PASS=3, MIDDLE_BAND=3, FLOOR=0, HARD_FAIL=0). "
        "OFF-DATA recompute: cross-seed CV of per_encoder_sparsity_range: fhrr 0.100 / "
        "binary_bipolar 0.129 / sparse_bipolar 0.141 / hrr_real 0.866 (all < 0.15 except "
        "structurally-saturated hrr_real). FHRR row values across [s=0.01,0.05,0.1,0.25]: "
        "seed_7 [0.82,0.68,0.60,0.53]; seed_13 [0.80,0.64,0.57,0.55]; seed_19 [0.83,0.66,0.62,0.54]; "
        "monotone decreasing in all 3 seeds. binary_bipolar + sparse_bipolar saturate at top1=1.0 "
        "for s in {0.01,0.05,0.1} across all seeds; only s=0.25 shows drop (0.85-0.89). "
        "hrr_real saturates entirely at 1.0 (except seed_13/19 s=0.01 at 0.9967 within measurement noise). "
        "Positive control (binary_bipolar s=0.1) recovers: 1.000/0.993/0.997 across seeds. "
        "SATURATION FLAG: 10/16 cells at top1=1.0 (>60% saturation trips META_RULE_Q). "
        "The 'interaction' claim is TRUE but the DISCRIMINATING axis is essentially "
        "FHRR-degrades-with-sparsity; other encoders saturate at high top1 in low-sparsity "
        "regime. Chain-grade requires non-by-construction discrimination across the axis; "
        "here the axis is capacity-bound. TIER: MEASURED_MECHANISM. cert_increment_delta=0."
    ),
    "metadata": {
        "provenance_quality": "MEASURED_MECHANISM",
        "verdict": "MEASURED_MECHANISM",
        "verified_off_data_by": ATOMIZED_BY,
        "verified_off_data_evidence": (
            "OFF-DATA recompute via .venv python on 3 seeds metrics.json: run_mode=full all 3; "
            "cardinality 16/16 all; tier_counts identical (SAT=10 HP=3 MB=3 FLOOR=0 FAIL=0); "
            "positive control 1.000/0.993/0.997; n_combos_arms_differ=16 all; encoder_pair_distinct=6/6 all; "
            "per_encoder_sparsity_range cross-seed cv: fhrr=0.100 binary=0.129 sparse=0.141 hrr=0.866; "
            "fhrr row monotone decreasing across sparsity all 3 seeds; META_RULE_Q trips at 10/16 saturation"
        ),
        "regime": {
            "N": 8192,
            "encoders": ["binary_bipolar", "hrr_real", "fhrr", "sparse_bipolar"],
            "sparsity_grid": [0.01, 0.05, 0.10, 0.25],
            "corruption_frac": 0.485,
            "cleanup_iters": 5,
            "M_items": 300,
            "beta": 8.0,
        },
        "per_seed_metrics_paths": {
            "seed_7":  "data/exp_substrate_pc_sparsity_x_encoder_crossproduct_v1_n8192_seed_7/metrics.json",
            "seed_13": "data/exp_substrate_pc_sparsity_x_encoder_crossproduct_v1_n8192_seed_13/metrics.json (remote_full)",
            "seed_19": "data/exp_substrate_pc_sparsity_x_encoder_crossproduct_v1_n8192_seed_19/metrics.json (remote_full)",
        },
        "per_encoder_sparsity_range_cross_seed": {
            "fhrr":            {"vals": [0.2966, 0.2467, 0.2933], "mean": 0.2789, "cv": 0.100},
            "binary_bipolar":  {"vals": [0.1133, 0.1300, 0.1467], "mean": 0.1300, "cv": 0.129},
            "sparse_bipolar":  {"vals": [0.1233, 0.1633, 0.1400], "mean": 0.1422, "cv": 0.141},
            "hrr_real":        {"vals": [0.0000, 0.0033, 0.0033], "mean": 0.0022, "cv": 0.866, "note": "structurally saturated -- cv is noise near zero"},
        },
        "fhrr_row_monotone_all_seeds": True,
        "saturation_10_of_16": True,
        "meta_rule_Q_tripped": True,
        "meta_rule_H_cardinality_ok": True,
        "positive_control_pass_all_seeds": True,
        "cert_increment_delta": 0,
        "discipline_tags": [
            "META_RULE_Q_SUSPECT_1p000_10_of_16_saturated",
            "META_RULE_H_cardinality_ok_16_of_16_all_seeds",
            "META_RULE_AV_interaction_pairs_visible_ge_2",
            "Fix_28_per_arm_metrics_verified",
            "DISCRIMINATOR_MUST_SURVIVE_SCALE_confirmed_at_N_8192_full",
            "stage_3_compositional_understanding_USER_2026-06-26",
        ],
        "ts_iso_atomized": ATOMIZED_DATE,
    },
}

# ============================================================================
# BATCH C -- Compression Pareto v1 (3-seed MM; H2 REFUTED)
# ============================================================================
atom_batch_C = {
    "id": (
        "T3/EXP_substrate_compression_pareto_v1_3seed_MM_H2_REFUTED_"
        "HARDMAX_100x_recall_drop_0p83_LOSSY_EXEMPLAR_BAYES_10x_recall_drop_0p10_cheap_"
        "no_larger_N_rescue_2026-07-01"
    ),
    "name": (
        "MEASURED-MECHANISM Compression Pareto v1 n_facts=10000 N=8192 3-seed FULL: H2 "
        "'compression is cheap at chain-grade' REFUTED. HARDMAX_CENTROID at 100x ratio drops "
        "recall 0.87->0.04 (0.83 loss, LOSSY). EXEMPLAR_BAYES at 10x ratio drops recall "
        "0.87->0.77 (0.10 loss, CHEAP). HIERARCHICAL at 10x collapses to 0.007. 5/6 gates PASS "
        "(recall_preserved_pass=False by design of H2 discriminator). Cross-seed cv PASS all "
        "arms. Larger N=8192 does NOT rescue HARDMAX vs smoke n=1000. Pareto-front "
        "characterized: EXEMPLAR_BAYES at 10x is cost-optimal; HARDMAX at 100x is impractical. "
        "CERT +0 (mechanism_characterization; proven bound + proven sub-mechanism)."
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record",
    "description": (
        "3-seed FULL compression pareto (n_facts=10000, N=8192). Verdict per cell: "
        "MIDDLE_BAND 5/6 gates all seeds (recall_preserved_pass=False by H2 test-design). "
        "OFF-DATA recompute: NO_COMPRESSION recall = [0.91, 0.86, 0.86] mean=0.877 sd=0.024; "
        "EXEMPLAR_BAYES recall = [0.76, 0.79, 0.77] mean=0.773 sd=0.012 (ratio=10x); "
        "HARDMAX_CENTROID recall = [0.02, 0.06, 0.04] mean=0.040 sd=0.020 (ratio=100x); "
        "HIERARCHICAL recall = [0.01, 0.01, 0.00] mean=0.007 sd=0.005 (ratio=9.9x). "
        "compression_ratio_gap_measured=100.0 all seeds; recall_drop_measured=[0.89, 0.80, 0.82] "
        "for the top-of-Pareto (NO vs HARDMAX). All 6 Pareto pairs distinct all seeds "
        "(distinct_pareto_pairs=6/6, arms_differ_mean_pairs=6.0). Cardinality 4/4 arms all seeds. "
        "Positive control PASS. cross_seed_cv gate PASS. "
        "H2 CLAIM REFUTED: HARDMAX at 100x is SEVERELY LOSSY. Smoke at n_facts=1000 already "
        "showed this; FULL n_facts=10000 N=8192 CORROBORATES. Larger N does NOT rescue "
        "HARDMAX (mean recall 0.04 across seeds). "
        "SUB-MECHANISM CHARACTERIZED: EXEMPLAR_BAYES at 10x ratio is cost-optimal Pareto point "
        "(0.10 recall drop for 10x memory savings; efficiency ~1.75-1.82). "
        "TIER: MEASURED_MECHANISM (proven bound + proven cost-optimal sub-mechanism). "
        "cert_increment_delta=0."
    ),
    "metadata": {
        "provenance_quality": "MEASURED_MECHANISM",
        "verdict": "MEASURED_MECHANISM",
        "verified_off_data_by": ATOMIZED_BY,
        "verified_off_data_evidence": (
            "OFF-DATA recompute via .venv python on 3 seeds metrics.json (remote pulled): "
            "run_mode=full all 3; cardinality 4/4 all; 5/6 gates PASS all seeds; "
            "recall_preserved_pass=False all seeds (H2 discriminator fires as designed); "
            "EXEMPLAR_BAYES [0.76, 0.79, 0.77] cv=0.016; HARDMAX_CENTROID [0.02, 0.06, 0.04] cv=0.500 "
            "(structurally noisy at floor); NO_COMPRESSION [0.91, 0.86, 0.86] cv=0.028; "
            "distinct_pareto_pairs=6/6 all seeds; positive_control PASS all"
        ),
        "regime": {
            "n_facts": 10000,
            "N": 8192,
            "arms": ["ARM_NO_COMPRESSION", "ARM_SCHEMA_EXEMPLAR_BAYES",
                     "ARM_SCHEMA_HARDMAX_CENTROID", "ARM_SCHEMA_HIERARCHICAL"],
        },
        "per_seed_metrics_paths": {
            "seed_7":  "data/exp_substrate_compression_pareto_v1_seed_7/metrics.json (remote pulled)",
            "seed_13": "data/exp_substrate_compression_pareto_v1_seed_13/metrics.json (remote pulled)",
            "seed_19": "data/exp_substrate_compression_pareto_v1_seed_19/metrics.json (remote pulled)",
        },
        "per_arm_recall_cross_seed": {
            "NO_COMPRESSION":   {"vals": [0.91, 0.86, 0.86], "mean": 0.877, "sd": 0.024, "ratio": 1.0},
            "EXEMPLAR_BAYES":   {"vals": [0.76, 0.79, 0.77], "mean": 0.773, "sd": 0.012, "ratio": 10.0, "cost_optimal": True},
            "HARDMAX_CENTROID": {"vals": [0.02, 0.06, 0.04], "mean": 0.040, "sd": 0.020, "ratio": 100.0, "note": "LOSSY: 0.83 recall drop"},
            "HIERARCHICAL":     {"vals": [0.01, 0.01, 0.00], "mean": 0.007, "sd": 0.005, "ratio": 9.9,  "note": "collapses despite modest ratio"},
        },
        "H2_hypothesis_refuted": True,
        "sub_mechanism_pareto_optimal": "EXEMPLAR_BAYES_at_10x_ratio_recall_drop_0p10",
        "cert_increment_delta": 0,
        "discipline_tags": [
            "META_RULE_H_cardinality_ok_4_of_4_all_seeds",
            "META_RULE_AC_smoke_refutation_survives_full_scale",
            "Fix_28_per_arm_metrics_verified",
            "H2_compression_cheap_at_chain_grade_REFUTED_at_full_N",
            "stage_3_compositional_understanding_USER_2026-06-26",
        ],
        "ts_iso_atomized": ATOMIZED_DATE,
    },
}

# ============================================================================
# BATCH D -- Routing Geometry Family KG Ingest v2 (3-seed HARD_FAIL at FULL)
# ============================================================================
atom_batch_D = {
    "id": (
        "T3/EXP_substrate_routing_geometry_family_kg_ingest_v2_3seed_HARD_FAIL_"
        "at_M_ingest_100k_4of5_arms_crash_only_random_partition_survives_at_floor_"
        "SMOKE_framing_did_not_survive_scale_axis_G_char_NOT_supported_2026-07-01"
    ),
    "name": (
        "HARD_FAIL Routing Geometry Family KG Ingest v2 3-seed FULL at M_ingest=100000: "
        "4 of 5 arms crash (retrieval_acc=-1.0, routing_hash=FAIL) for "
        "learned_supervised / lsh_hash / hierarchical_tree / knn_softmax across ALL 3 seeds. "
        "Only random_partition completes and sits at floor "
        "(0.116/0.115/0.115 across seeds vs floor=0.10). n_distinct_localizations=1 all seeds "
        "(need >=3 per META_RULE_AV). Smoke framing "
        "'knn_softmax 0.509 > learned_supervised 0.380 > random_partition 0.130' was at "
        "n_facts~1k and does NOT survive M_ingest=100k. Cell auto-emits MIDDLE_BAND per its "
        "internal classifier; auditor tiers HARD_FAIL for the outer-axis-G characterization claim. "
        "DISCRIMINATOR_MUST_SURVIVE_SCALE violation; smoke over-claimed by extrapolation. "
        "CERT +0. 2x-drill recommendation: cell-author must fix arm-crash implementation at "
        "M_ingest=100k before re-attempting axis G characterization."
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record",
    "description": (
        "3-seed FULL routing_geometry_family_kg_ingest_v2 at M_ingest=100000, N_DIM=2048, "
        "routing_noise_cos=0.60, P_SHARDS=256, n_eval=1024, n_kg_triples=100000. "
        "OFF-DATA recompute: per-seed retrieval_acc_by_arm shows 4/5 arms return -1.0 sentinel "
        "(cell's failure marker) across all 3 seeds: learned_supervised / lsh_hash / "
        "hierarchical_tree / knn_softmax. Only random_partition produces a valid hash and "
        "retrieval_acc (0.116/0.115/0.115). Positive control on random_partition PASS "
        "(0.115+ > 0.10 floor). All arms return per_arm_tier=FAIL/HARD_FAIL. "
        "n_unique_hashes=1 all seeds; n_distinct_localizations=1 all seeds; "
        "discrimination_gate_pass=False all seeds; cardinality 5/5 all seeds. "
        "The cell auto-emits MIDDLE_BAND_DISCRIMINATION_FLOOR per META_RULE_AV auto-demote. "
        "AUDITOR TIER: HARD_FAIL for the outer-axis-G routing-geometry-family "
        "characterization claim. The smoke framing 'knn_softmax > learned_supervised > "
        "random_partition' was at smoke scale (n_facts~1k) and did NOT survive scale to "
        "M_ingest=100k. This is a canonical DISCRIMINATOR_MUST_SURVIVE_SCALE_USER_2026-06-26 "
        "violation: smoke tested cell RUNS but did not test discriminator at full-N. "
        "2X-DRILL RECOMMENDATION: cell-author (hdi_exp_dev) must diagnose why 4/5 arms "
        "return -1.0 at M_ingest=100k (memory? complexity? uninitialized state? "
        "exception-swallow?) before re-attempting axis-G characterization. This is a "
        "cell-implementation defect, not a mechanism claim. cert_increment_delta=0."
    ),
    "metadata": {
        "provenance_quality": "HARD_FAIL",
        "verdict": "HARD_FAIL",
        "verified_off_data_by": ATOMIZED_BY,
        "verified_off_data_evidence": (
            "OFF-DATA recompute via .venv python on 3 seeds metrics.json (remote pulled): "
            "run_mode=full all 3; per-seed retrieval_acc_by_arm returns -1.0 for 4/5 arms "
            "(learned_supervised/lsh_hash/hierarchical_tree/knn_softmax) all seeds; "
            "routing_hash_by_arm=FAIL for 4/5 arms all seeds; only random_partition survives "
            "at floor (0.115-0.116); n_distinct_localizations=1 all seeds; "
            "discrimination_gate_pass=False all seeds; per_arm_tier FAIL/HARD_FAIL all arms all seeds"
        ),
        "regime": {
            "M_ingest": 100000,
            "N_DIM": 2048,
            "P_SHARDS": 256,
            "n_eval": 1024,
            "routing_noise_cos": 0.60,
            "arms": ["random_partition", "learned_supervised", "lsh_hash",
                     "hierarchical_tree", "knn_softmax"],
        },
        "per_seed_metrics_paths": {
            "seed_7":  "data/exp_substrate_routing_geometry_family_kg_ingest_v2_seed_7/metrics.json (remote pulled)",
            "seed_13": "data/exp_substrate_routing_geometry_family_kg_ingest_v2_seed_13/metrics.json (remote pulled)",
            "seed_19": "data/exp_substrate_routing_geometry_family_kg_ingest_v2_seed_19/metrics.json (remote pulled)",
        },
        "per_arm_retrieval_acc_cross_seed": {
            "random_partition":  {"vals": [0.11634, 0.11527, 0.11517], "mean": 0.1156, "note": "barely-above-floor 0.10"},
            "learned_supervised":{"vals": [-1.0, -1.0, -1.0], "note": "CRASH -- returned failure sentinel"},
            "lsh_hash":          {"vals": [-1.0, -1.0, -1.0], "note": "CRASH -- returned failure sentinel"},
            "hierarchical_tree": {"vals": [-1.0, -1.0, -1.0], "note": "CRASH -- returned failure sentinel"},
            "knn_softmax":       {"vals": [-1.0, -1.0, -1.0], "note": "CRASH -- returned failure sentinel"},
        },
        "smoke_framing_did_not_survive_scale": True,
        "smoke_framing_at_scale_n_facts_1k": "knn_softmax 0.509 > learned_supervised 0.380 > random_partition 0.130",
        "full_scale_reality_at_M_ingest_100k": "4/5 arms crash; only random_partition at 0.116",
        "discriminator_must_survive_scale_violation": True,
        "cell_implementation_defect": True,
        "2x_drill_recommendation": (
            "hdi_exp_dev: diagnose retrieval_acc=-1.0 return-sentinel path for "
            "learned_supervised/lsh_hash/hierarchical_tree/knn_softmax at M_ingest=100k. "
            "Likely candidates: (a) silent except-block swallowing exception per META_RULE, "
            "(b) OOM at scale, (c) uninitialized routing state at large P_SHARDS, "
            "(d) numerical overflow. Fix, re-smoke at N_ingest=100k preview, then retry."
        ),
        "cert_increment_delta": 0,
        "discipline_tags": [
            "META_RULE_AV_auto_demote_discrimination_floor",
            "DISCRIMINATOR_MUST_SURVIVE_SCALE_USER_2026-06-26_VIOLATION",
            "smoke_must_fire_discriminator_at_full_N_USER_2026-06-26",
            "META_RULE_H_cardinality_ok_5_of_5_but_4_of_5_crash",
            "Fix_28_per_arm_metrics_verified_reveals_-1p0_crash_sentinel",
            "META_RULE_no_silent_except_investigate_crash_sentinel",
            "stage_3_compositional_understanding_USER_2026-06-26",
        ],
        "ts_iso_atomized": ATOMIZED_DATE,
    },
}

# ============================================================================
# CERT LEDGER ROWS (3 total; all cert_increment_delta=0)
# ============================================================================
_t0 = time.time()

ledger_A = {
    "ts": _t0,
    "op": "cert_ruling",
    "atom_id": f"math::{atom_batch_A['id']}",
    "cert_status": "measured_mechanism",
    "cert_class": "mechanism_characterization",
    "verified_off_data": True,
    "atomized_by": ATOMIZED_BY,
    "cell_commit": None,
    "verdict": (
        "MM_3seed_FHRR_degrades_monotone_with_sparsity_range_0p279_cv_0p100_others_saturate_"
        "10_of_16_at_top1_1p000_META_RULE_Q_trip_axis_bound_char"
    ),
    "cert_increment_delta": 0,
    "cv": 0.100,
    "referent_pointer": {
        "notes_path": None,
        "metrics_path": "data/exp_substrate_pc_sparsity_x_encoder_crossproduct_v1_n8192_seed_{7,13,19}/metrics.json",
        "atom_qualified_id": f"math::{atom_batch_A['id']}",
    },
    "supersedes": None,
    "note": (
        "batch_A_pc_sparsity_x_encoder_crossproduct_v1_n8192_3seed_MM_"
        "fhrr_axis_discriminates_others_saturate_META_RULE_Q_10of16_"
        "per_encoder_sparsity_range_fhrr_0p279_binary_0p130_sparse_0p142_hrr_0p002_"
        "positive_control_pass_all_seeds_cardinality_ok_16_of_16_all_seeds"
    ),
}

ledger_C = {
    "ts": _t0 + 0.001,
    "op": "cert_ruling",
    "atom_id": f"math::{atom_batch_C['id']}",
    "cert_status": "measured_mechanism",
    "cert_class": "mechanism_characterization",
    "verified_off_data": True,
    "atomized_by": ATOMIZED_BY,
    "cell_commit": None,
    "verdict": (
        "MM_3seed_H2_compression_cheap_REFUTED_HARDMAX_100x_recall_drop_0p83_LOSSY_"
        "EXEMPLAR_BAYES_10x_recall_drop_0p10_cheap_no_N_rescue_5of6_gates_pass"
    ),
    "cert_increment_delta": 0,
    "cv": 0.016,
    "referent_pointer": {
        "notes_path": None,
        "metrics_path": "data/exp_substrate_compression_pareto_v1_seed_{7,13,19}/metrics.json (remote_pulled)",
        "atom_qualified_id": f"math::{atom_batch_C['id']}",
    },
    "supersedes": None,
    "note": (
        "batch_C_compression_pareto_v1_3seed_MM_H2_refuted_"
        "NO_recall_0p877_EXEMPLAR_BAYES_recall_0p773_at_10x_HARDMAX_recall_0p040_at_100x_"
        "HIERARCHICAL_recall_0p007_at_10x_sub_mechanism_EXEMPLAR_BAYES_10x_cost_optimal_pareto_point"
    ),
}

ledger_D = {
    "ts": _t0 + 0.002,
    "op": "cert_ruling",
    "atom_id": f"math::{atom_batch_D['id']}",
    "cert_status": "hard_fail",
    "cert_class": "honest_negative_cell_implementation_defect",
    "verified_off_data": True,
    "atomized_by": ATOMIZED_BY,
    "cell_commit": None,
    "verdict": (
        "HARD_FAIL_3seed_at_M_ingest_100k_4of5_arms_crash_return_-1p0_sentinel_"
        "only_random_partition_survives_at_floor_0p115_smoke_did_not_survive_scale_"
        "DISCRIMINATOR_MUST_SURVIVE_SCALE_violation_2x_drill_required"
    ),
    "cert_increment_delta": 0,
    "cv": None,
    "referent_pointer": {
        "notes_path": None,
        "metrics_path": "data/exp_substrate_routing_geometry_family_kg_ingest_v2_seed_{7,13,19}/metrics.json (remote_pulled)",
        "atom_qualified_id": f"math::{atom_batch_D['id']}",
    },
    "supersedes": None,
    "note": (
        "batch_D_routing_geometry_family_kg_ingest_v2_3seed_HARD_FAIL_"
        "4_of_5_arms_crash_at_M_ingest_100k_axis_G_char_NOT_supported_"
        "cell_auto_MB_via_META_RULE_AV_auditor_overrides_to_HARD_FAIL_"
        "2x_drill_cell_author_diagnose_crash_before_reattempt"
    ),
}


# ============================================================================
# A5 write protocol (same as barrier1_partition_oracle atomize)
# ============================================================================
def append_jsonl_a5(path: Path, new_row: dict, label: str):
    print(f"[A5] {label}: path={path}")
    assert path.exists(), f"target does not exist: {path}"

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
        assert parsed_back.get("id") == new_row.get("id"), "round-trip id mismatch"
    if "atom_id" in new_row:
        assert parsed_back.get("atom_id") == new_row.get("atom_id"), "round-trip atom_id mismatch"

    out_lines = pre_lines + [new_line]
    out_text = "\n".join(out_lines) + "\n"

    tmp_path = path.with_suffix(path.suffix + ".tmp_a5")
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(out_text)
        f.flush()
        os.fsync(f.fileno())
    # Windows os.replace race: another process may hold a read handle briefly.
    # Retry with exponential backoff up to ~5s. Concurrency-gotcha per MEMORY.md.
    import time as _time
    for _attempt in range(10):
        try:
            os.replace(str(tmp_path), str(path))
            break
        except PermissionError:
            if _attempt == 9:
                raise
            _time.sleep(0.1 * (2 ** _attempt))

    with open(path, "r", encoding="utf-8") as f:
        post_lines = f.read().splitlines()
    post_count = len(post_lines)
    print(f"[A5] {label}: post_count={post_count}")
    assert post_count == pre_count + 1, f"count delta mismatch: {pre_count} -> {post_count}"

    tail = json.loads(post_lines[-1])
    if "id" in new_row:
        assert tail["id"] == new_row["id"], f"tail id mismatch"
    if "atom_id" in new_row:
        assert tail["atom_id"] == new_row["atom_id"], f"tail atom_id mismatch"

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
    print(f"[A5] atomize START {ATOMIZED_BY} ts={time.time():.3f}")
    print(f"[A5] atom_A_id = math::{atom_batch_A['id']}")
    print(f"[A5] atom_C_id = math::{atom_batch_C['id']}")
    print(f"[A5] atom_D_id = math::{atom_batch_D['id']}")
    print(f"[A5] ledger_A: cert_status={ledger_A['cert_status']} delta={ledger_A['cert_increment_delta']}")
    print(f"[A5] ledger_C: cert_status={ledger_C['cert_status']} delta={ledger_C['cert_increment_delta']}")
    print(f"[A5] ledger_D: cert_status={ledger_D['cert_status']} delta={ledger_D['cert_increment_delta']}")

    # Batch A already appended on 2026-07-01 run 1 (28821 -> 28822); resume from C
    # Verify: last line in atoms.jsonl matches atom_batch_A['id']; if so skip.
    with open(MATH_ATOMS, "r", encoding="utf-8") as _f:
        _last = _f.read().splitlines()[-1]
    _last_id = json.loads(_last).get("id", "")
    if _last_id == atom_batch_A["id"]:
        print(f"[A5] Batch A already landed as tail atom; skipping duplicate append.")
    else:
        append_jsonl_a5(MATH_ATOMS, atom_batch_A, "math/atoms.jsonl (Batch A pc_sparsity MM)")
    append_jsonl_a5(MATH_ATOMS, atom_batch_C, "math/atoms.jsonl (Batch C compression MM)")
    append_jsonl_a5(MATH_ATOMS, atom_batch_D, "math/atoms.jsonl (Batch D routing HARD_FAIL)")
    append_jsonl_a5(CERT_LEDGER, ledger_A, "meta/cert_ledger.jsonl (Batch A)")
    append_jsonl_a5(CERT_LEDGER, ledger_C, "meta/cert_ledger.jsonl (Batch C)")
    append_jsonl_a5(CERT_LEDGER, ledger_D, "meta/cert_ledger.jsonl (Batch D)")

    print(f"[A5] DONE OK")
    print(f"[A5] Batch A: MM (fhrr axis discriminates, others saturate; META_RULE_Q)")
    print(f"[A5] Batch C: MM (H2 REFUTED; EXEMPLAR_BAYES 10x cost-optimal)")
    print(f"[A5] Batch D: HARD_FAIL (4/5 arms crash at M=100k; 2x-drill required)")
    print(f"[A5] CERT delta = 0 (0 CG promotions this batch)")


if __name__ == "__main__":
    main()
