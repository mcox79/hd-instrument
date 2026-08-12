"""
A5-gated atomization: exp_srn_capacity_growth_v1 (commit e81b06fbb) -> TWO atoms (2026-07-18).
  ATOM 1 (HARD_FAIL): Elman-1993 capacity-GROWTH refuted -- not growth-specific (SHRINK>GROWTH 3/3, LOWCAP>=GROWTH).
  ATOM 2 (MEASURED_MECHANISM): the "compression improves category-AMI" positive DECOMPOSED via an independent
          logistic-POS probe + PCA control -- part clustering-geometry ARTIFACT, part GENUINE (SHRINK-schedule only).

Director HELD pending this VET. Independent off-disk recompute (.venv; Fix #28) done via a fresh seed-7 re-run
importing the REAL arm functions, plus a supervised LOGISTIC POS PROBE and a PCA-compression control the cell
never ran (the decisive dimensionality-artifact test the Director asked for).
LOCAL ONLY: store_head_at_write=unsynced_needs_orchestrator; NO origin push.
"""

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
MATH_ATOMS = ROOT / "data/substrate_index/math/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"
ATOMIZED_BY = "skunkworks_landed_vet_srn_capacity_growth_v1_HF_elman_plus_MM_compression_decomp_2026-07-18"
ATOMIZED_DATE = "2026-07-18"
ANCHOR = "srn_capacity_growth_v1"
CELL_COMMIT = "e81b06fbb"

_iso = datetime.now(timezone.utc).isoformat()
_ts = time.time()

XARC = ("substrate_query.sh 'effective dimension compression low-rank improves category clustering AMI POS "
        "abstraction' -> top hit cosine=0.3242 (notes/research_density_scale_theory_reconciliation_970k: "
        "'reduced effective dimension -> fewer ambient dims needed to preserve geometry' -- a KB-RETRIEVAL/hubness "
        "context, DIFFERENT task+mechanism from KMeans category-clustering geometry; conceptual neighbor, not a "
        "rediscovery). 'abstraction' concept atom 0.31, wordnet 0.31. No prior ARC EXPERIMENT cell runs the "
        "capacity-schedule x category-induction contrast. Genuinely novel as an experiment.")

# ============================================================================ ATOM 1: Elman HARD_FAIL
ATOM1_ID = ("math::HF_srn_capacity_growth_v1_ELMAN_1993_capacity_GROWTH_start_small_grow_effective_dim_does_NOT_"
            "improve_predictive_reader_category_induction_and_is_NOT_growth_specific_on_real_Brown_prose_fixed_"
            "budget_AMI_growth_0p196_vs_fixed_0p158_delta_plus0p037_3of3_seeds_BUT_SHRINK_0p271_BEATS_growth_"
            "growth_minus_shrink_minus0p075_3of3_seeds_AND_LOWCAP_0p204_gte_growth_3of3_so_ANY_low_effective_dim_"
            "schedule_matches_or_beats_the_growth_ramp_direction_cleanly_REVERSED_Elman_starting_small_via_"
            "embedding_dim_mask_NOT_supported_first_class_negative_byte_reproduce_EXACT_seed7_growth_0p1951_fixed_"
            "0p1587_shrink_0p2828_CE_ordering_fixed_3p30_best_shrink_5p04_worst_scope_tests_EMBEDDING_dim_proxy_"
            "NOT_Elman_recurrent_memory_window_k_fixed_at_5_all_arms_e81b06fbb_2026-07-18")

ATOM1_CLAIM = (
    "MATH HARD_FAIL (first-class negative). On real NLTK Brown prose (~100k tokens, V=900, 9 universal-POS gold "
    "cats), Elman-1993 CAPACITY-GROWTH -- 'start small, grow the learner's effective dimension during training' "
    "-- does NOT improve the order-sensitive predictive reader's POS-category induction in a GROWTH-SPECIFIC way, "
    "at fixed token/exposure budget. The capacity schedule is a per-epoch leading-dim mask over d=128 (GROWTH "
    "8->128, FIXED=128 parent baseline, SHRINK 128->8, LOWCAP=8). GROWTH (AMI 0.196) does beat FIXED (0.158) by "
    "+0.037 on 3/3 seeds, BUT the direction is cleanly REVERSED: SHRINK (0.271) BEATS GROWTH (growth-shrink = "
    "-0.075 on 3/3 seeds) and LOWCAP (0.204) >= GROWTH on 3/3 seeds. So ANY low-effective-dimension schedule "
    "matches or beats the growth ramp -- the benefit is a low-dimensional-representation effect, NOT Elman "
    "starting-small. CE ordering (next-word): FIXED 3.30 best -> GROWTH 3.74 -> LOWCAP 4.97 -> SHRINK 5.04 worst. "
    "SCOPE CAVEAT (load-bearing): this cell manipulates EMBEDDING effective-dimension (a dim mask), which is a "
    "PROXY, NOT Elman's actual recurrent MEMORY-WINDOW growth -- the context window k is FIXED at 5 across all "
    "arms and the architecture is a fixed-k position-bind bag with no recurrent hidden state, so it CANNOT test "
    "memory-horizon starting-small. The refutation is scoped to embedding-capacity-growth, and it CLOSES the "
    "localized 'grow-capacity' next-lever that the sibling curriculum-order cell had flagged.")

ATOM1_RECOMPUTE = (
    "INDEP recompute (.venv, fresh seed-7 re-run importing the REAL arm_learner_capacity, NOT verdict_msg; Fix "
    "#28): BYTE-REPRODUCE EXACT to 4dp -- seed 7 ami_growth=0.1951 ami_fixed=0.1587 ami_shrink=0.2828 (all match "
    "metrics per_seed[0]); CE gr=3.7352 fx=3.2988 sh=5.0357 lc=4.9720 (match exact); delta_growth=+0.0364, "
    "growth_minus_shrink=-0.0877 (match). Across metrics 3 seeds: delta_growth +0.0364/+0.0270/+0.0486 (3/3 "
    ">0 but ALL < the muddy line because...) growth_minus_shrink -0.0877/-0.0862/-0.0517 (3/3 NEGATIVE, direction "
    "reversed), lowcap-growth +0.010/+0.010/+0.005 (3/3 LOWCAP>=GROWTH). FIXED arm reproduces PARENT "
    "exp_srn_predict_category_v1 ami_learner_pos_mean=0.1585 EXACT (provenance rail holds). PROVENANCE: parent "
    "metrics.json ami_learner_pos_mean=0.1585 == this cell ami_fixed_mean 0.1585. randcode AMI -0.0002 (metric "
    "fires). NOTE lowcap AMI is init-FRAGILE: my seed-7 reproduce gave 0.2172 vs metrics 0.2052 (the 3 fully-"
    "trained arms matched to 4dp; only LOWCAP -- which carries 120 frozen random-init noise dims -- shifted "
    "under KMeans n_init variation, itself evidence LOWCAP's AMI is noise-driven; see atom 2).")

ATOM1_SCOPE = (
    "REAL Brown prose toy (glass-box numpy/torch-cpu/sklearn, NO LLM). A first-class NEGATIVE / mechanism "
    "localization: capacity-GROWTH via embedding-dim schedule is refuted as growth-SPECIFIC. Do NOT over-read as "
    "refuting Elman-1993 wholesale: (a) the cell tests EMBEDDING effective-dim, not the recurrent MEMORY-WINDOW "
    "that was Elman's actual 'starting small' variable (k is fixed=5, no recurrent state) -- a genuine memory-"
    "horizon-growth test remains OPEN and would need a recurrent/growing-window architecture; (b) the cell lacks "
    "structured priors. The clean, defensible negative: on THIS substrate/task, a growth RAMP confers no benefit "
    "beyond what any low-effective-dim schedule (even constant LOWCAP) confers -- and that low-dim benefit is "
    "itself largely a clustering-geometry artifact (atom 2). BRAIN-CHECK (sound): the cell correctly flags it "
    "tests the wrong axis (embedding-dim not memory-window) and honestly scopes the refutation. Revival: test "
    "memory-window growth in a recurrent/growing-context architecture before claiming Elman refuted.")

ATOM1_METRICS = {
    "ami_growth_mean": 0.1958, "ami_fixed_mean": 0.1585, "ami_shrink_mean": 0.271, "ami_lowcap_mean": 0.2041,
    "ami_randomcode_mean": -0.0002,
    "delta_growth_mean": 0.0373, "growth_minus_shrink_mean": -0.0752, "delta_shrink_mean": 0.1125,
    "per_seed_delta_growth": [0.0364, 0.027, 0.0486],
    "per_seed_growth_minus_shrink": [-0.0877, -0.0862, -0.0517],
    "per_seed_lowcap_minus_growth": [0.0101, 0.0098, 0.0051],
    "ce_fixed": 3.30, "ce_growth": 3.74, "ce_lowcap": 4.97, "ce_shrink": 5.04,
    "parent_provenance_ami_fixed_eq_learner_pos": 0.1585,
    "seed7_reproduce_exact": {"ami_growth": 0.1951, "ami_fixed": 0.1587, "ami_shrink": 0.2828},
    "lowcap_ami_init_fragile": {"metrics": 0.2052, "reproduce_seed7": 0.2172},
    "hp_margin": 0.02, "cell_verdict": "HARD_FAIL", "auditor_tier": "HARD_FAIL (confirmed first-class negative)",
    "k_fixed_all_arms": 5,
}

# ============================================================================ ATOM 2: compression MM (decomposed)
ATOM2_ID = ("math::MM_srn_capacity_growth_v1_low_effective_dim_improves_category_AMI_is_PART_clustering_geometry_"
            "ARTIFACT_part_GENUINE_shrink_schedule_only_DECOMPOSED_via_independent_logistic_POS_probe_plus_PCA_"
            "control_raw_AMI_shrink_0p271_lowcap_0p204_growth_0p196_vs_fixed_0p158_BUT_supervised_5fold_probe_acc_"
            "fixed_0p644_growth_0p655_lowcap_0p655_shrink_0p708_so_LOWCAP_and_GROWTH_probe_ties_FIXED_their_AMI_"
            "edge_is_ARTIFACT_compressing_FIXED_rep_to_8_PCA_dims_ALONE_lifts_its_AMI_0p159_to_0p199_zero_retrain_"
            "only_SHRINK_genuinely_encodes_more_POS_probe_0p708_gt_0p644_plus6pt_2x_foldstd_but_SINGLE_SEED_probe_"
            "and_SCHEDULE_specific_train_full_then_compress_NOT_low_cap_per_se_costs_catastrophic_CE_5p04_vs_3p30_"
            "prediction_vs_abstraction_tradeoff_GENUINE_for_shrink_but_partly_mechanical_8dim_readout_bottleneck_"
            "e81b06fbb_2026-07-18")

ATOM2_CLAIM = (
    "MATH MEASURED_MECHANISM (proven-bound; a DECOMPOSITION that corrects an over-read while preserving a genuine "
    "kernel). The cell's side-observation 'low-effective-dimension / compression sharply improves POS-category "
    "AMI' (raw AMI SHRINK 0.271, LOWCAP 0.204, GROWTH 0.196 vs FIXED 0.158) is PART clustering-geometry ARTIFACT "
    "and PART genuine, and the two must be separated. DECISIVE CONTROLS (independent, off-disk, the cell never "
    "ran them): (1) a supervised 5-fold LOGISTIC-REGRESSION POS PROBE on the L2-normed representations -- which "
    "measures linear POS decodability regardless of dimensional spread -- gives probe-acc FIXED 0.644, GROWTH "
    "0.655, LOWCAP 0.655, SHRINK 0.708 (majority-class floor 0.499). So GROWTH and LOWCAP encode NO more POS "
    "information than FIXED (probe ties within fold-noise) even though their raw AMI is +0.04-0.05 higher -- that "
    "AMI edge is an ARTIFACT. (2) PCA control: compressing the FIXED representation alone to 8 PCA dims lifts its "
    "KMeans-AMI from 0.159 to 0.199 (+0.040) with ZERO retraining -- KMeans simply clusters better in low-d, so "
    "~0.04 of every low-d arm's apparent AMI advantage is clustering geometry, not information. (3) LOWCAP's raw "
    "AMI is additionally noise-fragile: it carries 120 frozen random-init dims and its AMI shifts 0.205->0.217 "
    "under KMeans-init variation (fully-trained arms are stable to 4dp). THE GENUINE KERNEL (SHRINK only): SHRINK "
    "linearly encodes MORE POS -- probe 0.708 >> FIXED 0.644 (+6.4pts, ~2x fold-std) AND its AMI margin (0.271 > "
    "FIXED-PCA8 0.199) exceeds the geometry bonus, replicated across 3 seeds. But this is (a) a SCHEDULE effect "
    "(train at full capacity, THEN progressively compress the active subspace), NOT 'low capacity is better' "
    "(pure LOWCAP is artifact); (b) probe evidence is SINGLE-SEED (seed 7); (c) it costs catastrophic next-word "
    "CE (5.04 vs FIXED 3.30). The PREDICTION-vs-ABSTRACTION tradeoff (FIXED best-CE/worst-AMI; SHRINK worst-CE/"
    "best-probe) is GENUINE (probe confirms SHRINK simultaneously has more POS-info AND worse CE, not a pure "
    "clustering artifact) but partly MECHANICAL: an 8-dim final active subspace suffices to separate 9 POS "
    "classes yet starves 900-way next-token prediction. Defensible claim: a FULL-then-SHRINK capacity SCHEDULE "
    "genuinely concentrates more linearly-decodable POS structure than fixed-full training, at a large "
    "prediction cost -- a narrow, single-seed-probe efficiency lever, NOT a broad 'compression improves "
    "abstraction' law.")

ATOM2_RECOMPUTE = (
    "INDEP recompute (.venv, fresh seed-7 re-run importing REAL arm functions + eval; Fix #28): (A) AMI byte-"
    "reproduce EXACT growth 0.1951 / fixed 0.1587 / shrink 0.2828 (lowcap 0.2172 vs metrics 0.2052 -- KMeans-init "
    "fragility on the 120-frozen-noise-dim arm). (B) LOGISTIC POS PROBE (5-fold StratifiedKFold, C=1.0, L2-normed "
    "reps, n=893 gold words, 9 cats, majority floor 0.4994): probe_acc growth 0.6552+-0.029, fixed 0.6440+-0.038, "
    "lowcap 0.6551+-0.017, shrink 0.7077+-0.022. SHRINK is the ONLY arm clearly above FIXED (+0.064, ~2x combined "
    "fold-std); GROWTH/LOWCAP within noise of FIXED. (C) trained-vs-frozen dim count (|E - identical-init|>1e-6 "
    "per col): growth/fixed/SHRINK all train 128/128 dims (SHRINK trains all dims EARLY at full-cap then masks -- "
    "so its win is NOT a frozen-noise artifact), LOWCAP trains only 8/128 (120 frozen random). (D) trained-dim-"
    "subspace KMeans == full for the 3 fully-trained arms (128 dims), lowcap-on-8-trained-dims AMI 0.215. (E) PCA "
    "control -- FIXED rep KMeans after PCA compress: PCA8 0.1995, PCA16 0.1915, PCA32 0.1864 vs full-128 0.1587 "
    "(compression ALONE recovers +0.04 AMI, no retrain). sklearn 1.9.0.")

ATOM2_SCOPE = (
    "REAL Brown prose toy, glass-box, NO LLM; SINGLE SEED for the probe/PCA controls (seed 7) -- the AMI margins "
    "replicate across 3 seeds but the probe/PCA decomposition does NOT yet. This is a MECHANISM DECOMPOSITION, "
    "not a capability. Load-bearing bounds: (a) the raw-AMI framing 'compression improves category-abstraction' "
    "OVER-READS -- for LOWCAP and GROWTH the AMI gain over FIXED is a KMeans-in-high-d clustering-geometry "
    "artifact (probe-info-content ties FIXED); only SHRINK carries genuine extra POS info. (b) even SHRINK's "
    "genuine part is a train-full-THEN-compress SCHEDULE effect (NOT low-capacity-per-se) and is single-seed on "
    "the decisive probe. (c) the prediction/abstraction tradeoff is genuine but partly mechanical (8-dim "
    "bottleneck starves 900-way prediction while sufficing for 9-way POS). Do NOT bank as a general efficiency "
    "law. Revival to CG: replicate the logistic-probe SHRINK>FIXED gap across >=3 seeds AND show it survives a "
    "compression-geometry-matched control (e.g. probe FIXED at matched effective rank), then characterize why "
    "full-then-shrink concentrates POS info (does early full-cap training find the structure the late "
    "compression then distills?).")

ATOM2_METRICS = {
    "ami_raw": {"fixed": 0.1585, "growth": 0.1958, "shrink": 0.271, "lowcap": 0.2041},
    "logistic_probe_acc_5fold_seed7": {"fixed": 0.6440, "growth": 0.6552, "lowcap": 0.6551, "shrink": 0.7077,
                                       "majority_floor": 0.4994, "std_fixed": 0.038, "std_shrink": 0.022},
    "pca_control_fixed_kmeans_ami": {"full128": 0.1587, "pca8": 0.1995, "pca16": 0.1915, "pca32": 0.1864},
    "trained_dims": {"growth": 128, "fixed": 128, "shrink": 128, "lowcap": 8},
    "lowcap_ami_init_fragility": {"metrics": 0.2052, "reproduce": 0.2172},
    "ce": {"fixed": 3.30, "growth": 3.74, "lowcap": 4.97, "shrink": 5.04},
    "genuine_component": "SHRINK_only_probe_0p708_vs_fixed_0p644_plus6p4pt_single_seed",
    "artifact_component": "LOWCAP_and_GROWTH_AMI_edge_is_clustering_geometry_probe_ties_fixed_PCA8_recovers_0p04",
    "cell_verdict": "HARD_FAIL", "auditor_tier": "MEASURED_MECHANISM (decomposed; genuine SHRINK kernel + artifact)",
}

COMPOSES1 = [
    "CLOSES the localized 'grow-capacity' next-lever flagged by the sibling MM atom math::MM_srn_curriculum_"
    "order_v1 (curriculum-order MIDDLE_BAND, whose brain-check localized Elman-1993 to CAPACITY-GROWTH not input-"
    "order and named this as the next lever). This cell tests that lever and returns a first-class NEGATIVE -- "
    "the curriculum arc's Elman thread is now closed on BOTH halves (order = MB near-null; capacity-growth = HF).",
    "provenance-composes with parent math::MM_MEASURED_MECHANISM_srn_predict_category_v1 (the reused predictive "
    "reader, commit 9d8afcbd1): FIXED arm reproduces parent ami_learner_pos 0.1585 EXACT.",
    "credit: Elman (1990/1993) 'starting small' / capacity-growth (the refuted hypothesis, mechanism analog); "
    "Rohde-Plaut (1999) adequate-fixed-capacity null (consistent-with).",
]
COMPOSES2 = [
    "SUBORDINATE-to / corrects the over-read of atom 1's incidental observation that low-effective-dim helps "
    "AMI: atom 1 establishes the Elman-growth negative; THIS atom decomposes WHY the low-dim arms score higher "
    "on AMI (clustering geometry + a narrow genuine SHRINK-schedule kernel).",
    "conceptual neighbor (NOT duplicate): notes/research_density_scale_theory_reconciliation_970k (cosine 0.32) "
    "on effective-dimension vs ambient-dimension in KB RETRIEVAL/hubness -- different task/mechanism; this is "
    "KMeans category-clustering geometry, an independent instance of 'lower effective dim can flatter a distance-"
    "based metric without more information'.",
    "METHOD-composes with the auditor discipline that a clustering-metric win must be checked with a dimension-"
    "agnostic supervised probe before crediting it as an information gain (dimensionality-artifact control).",
]


def build_atom(aid, claim, recompute, scope, metrics, tier, cert_status, cert_class, composes,
               over_reads, revival, genuine_pos):
    return {
        "id": aid, "name": claim, "corpus": "math", "tier": tier, "kind": "experiment_landed_vet",
        "cert_status": cert_status, "cert_class": cert_class,
        "description": (claim + "\n\nRECOMPUTE (off-disk .venv, Fix #28): " + recompute
                        + "\n\nHONEST SCOPE: " + scope),
        "aliases": [], "ts_iso": _iso, "ts": _ts,
        "metadata": {
            "provenance_quality": "byte_reproduce_exact_seed7_plus_independent_logistic_probe_and_pca_control_off_disk",
            "anchor": ANCHOR, "cell_commit": CELL_COMMIT, "supersedes": None,
            "store_head_at_write": "unsynced_needs_orchestrator",
            "metrics_path": "data/exp_srn_capacity_growth_v1/metrics.json",
            "verified_off_data": recompute, "honest_scope": scope, "metrics": metrics,
            "over_reads_corrected": over_reads,
            "genuine_positives_symmetric_anti_negativity": genuine_pos,
            "revival_criteria": revival,
            "cross_arc_overlap_check": XARC,
            "cites": [
                "Fix_28_verify_off_data_not_verdict_msg",
                "symmetric_anti_negativity_verify_both_directions_USER",
                "cited_number_must_reproduce_from_cell",
                "verify_the_referent_atom_ids_mechanism_metric_regime",
                "dimensionality_artifact_clustering_metric_check_with_supervised_probe",
                "feedback_strategic_reads_run_ahead_of_evidence_caveat_interpretation_not_just_verdicts",
                "HF_test_design_vs_structural_bound_attribution",
            ],
            "composes_with": composes,
            "atomized_by": ATOMIZED_BY, "atomized_date": ATOMIZED_DATE,
            "needs_orchestrator_store_sync": True,
            "local_write_only_no_origin_push_no_remote_persist": True,
        },
    }


atom1 = build_atom(
    ATOM1_ID, ATOM1_CLAIM, ATOM1_RECOMPUTE, ATOM1_SCOPE, ATOM1_METRICS, "HARD_FAIL",
    ("confirmed_hard_fail_elman1993_capacity_growth_via_embedding_dim_mask_not_growth_specific_shrink_beats_"
     "growth_3of3_lowcap_gte_growth_3of3_any_low_effective_dim_schedule_matches_or_beats_growth_ramp_scoped_to_"
     "embedding_dim_not_recurrent_memory_window_k_fixed_5_byte_reproduce_exact_parent_provenance_holds_first_"
     "class_negative"),
    ("elman_capacity_growth_start_small_grow_effective_dim_does_not_improve_predictive_reader_pos_category_"
     "induction_growth_specifically_at_fixed_budget_low_effective_dim_is_the_incidental_lever_not_growth_"
     "direction_reversed_hard_fail_negative_scoped_embedding_dim_proxy_not_memory_window"),
    COMPOSES1,
    ["cell verdict HARD_FAIL is CONFIRMED (not deflated) -- but guard the interpretation: this refutes "
     "capacity-GROWTH via an EMBEDDING-DIM schedule, NOT Elman's recurrent MEMORY-WINDOW starting-small (k fixed "
     "at 5, no recurrent state). 'Elman refuted' would over-read; 'embedding-capacity-growth confers no growth-"
     "specific benefit on this substrate' is the defensible claim.",
     "the delta_growth +0.037 (GROWTH>FIXED 3/3) is NOT a positive for growth -- it is the SAME low-effective-dim "
     "clustering-geometry effect that LOWCAP and SHRINK show even more strongly (see atom 2); growth spends early "
     "epochs at low d_eff so it inherits a slice of the artifact."],
    ["test a genuine MEMORY-WINDOW growth (growing recurrent context horizon) in a recurrent/growing-k "
     "architecture before concluding Elman starting-small is refuted -- this cell cannot address that axis.",
     "add structured priors; the cell is a bare position-bind bag."],
    ("HONEST NEGATIVE done RIGHT: (a) byte-reproduces EXACT off-disk; (b) FIXED reproduces the parent AMI 0.1585 "
     "exactly (provenance rail); (c) can-fail-both-ways design with HARD_PASS + HARD_FAIL pre-defined; (d) the "
     "direction control (SHRINK) and knob-bites control (LOWCAP) are BOTH present and BOTH fire, which is exactly "
     "what turns 'growth beats fixed' into a clean 'not growth-specific' negative; (e) the brain-check honestly "
     "scopes the refutation to the wrong-axis proxy."))

atom2 = build_atom(
    ATOM2_ID, ATOM2_CLAIM, ATOM2_RECOMPUTE, ATOM2_SCOPE, ATOM2_METRICS, "MEASURED_MECHANISM",
    ("confirmed_measured_mechanism_low_effective_dim_improves_category_ami_is_part_clustering_geometry_artifact_"
     "lowcap_and_growth_probe_tie_fixed_pca8_recovers_0p04_part_genuine_shrink_schedule_only_probe_0p708_vs_"
     "0p644_single_seed_prediction_abstraction_tradeoff_genuine_but_partly_mechanical_8dim_bottleneck"),
    ("compression_low_effective_dimension_category_ami_improvement_decomposed_clustering_geometry_artifact_vs_"
     "genuine_shrink_schedule_pos_info_gain_via_logistic_probe_and_pca_control_narrow_single_seed_efficiency_"
     "lever_not_general_law_measured_mechanism"),
    COMPOSES2,
    ["Director's inclination that 'compression/low-effective-dim improves category-abstraction' is a GENUINE "
     "efficiency lever is PARTLY corrected: for LOWCAP and GROWTH the AMI gain over FIXED is a clustering-"
     "geometry ARTIFACT (dimension-agnostic logistic probe ties FIXED; compressing FIXED alone to PCA8 recovers "
     "+0.04 AMI with no retraining). The general framing 'low-effective-dim improves abstraction' over-reads.",
     "the cell's own verdict_msg framing 'a shrink/compress schedule is better' is TRUE only in the narrow, "
     "probe-confirmed, single-seed SHRINK sense -- and even there it is a train-full-THEN-compress SCHEDULE, not "
     "low-capacity-per-se, at a catastrophic CE cost. 'better' must specify FOR WHAT (POS clustering yes; next-"
     "word prediction no)."],
    ["replicate the logistic-probe SHRINK>FIXED POS gap across >=3 seeds (currently single-seed) AND show it "
     "survives a compression-geometry-matched control before promoting MM->CG.",
     "characterize the mechanism: does early full-capacity training find POS structure that late compression "
     "distills into a lower-rank, more-clusterable code? (a real, brain-adjacent 'expand-then-compress' idea "
     "worth a targeted follow-up).",
     "if the 3-seed probe replication FAILS, the whole positive collapses to the clustering-geometry artifact "
     "and only atom 1 (the Elman HF) stands."],
    ("GENUINE kernel preserved symmetrically (NOT dismissed): SHRINK's logistic-probe POS accuracy 0.708 clearly "
     "exceeds FIXED 0.644 (+6.4pts, ~2x fold-std), its AMI margin exceeds the PCA-geometry bonus, and it "
     "replicates across 3 seeds on AMI -- a real, dimension-agnostic signal that a full-then-shrink schedule "
     "concentrates more linearly-decodable POS structure. The prediction/abstraction tension is genuine (probe "
     "confirms more POS-info WITH worse CE simultaneously). This is a real, if narrow, finding worth a follow-up "
     "-- not a pure artifact."))

# ============================================================================ ledger rows
def ledger_row(atom, verdict, decision, framing, net_delta):
    return {
        "op": "cert_ruling", "corpus": "math", "tier": atom["tier"], "cert_status": atom["cert_status"],
        "anchor": ANCHOR, "cell_commit": CELL_COMMIT, "supersedes_commit": None,
        "store_head_at_write": "unsynced_needs_orchestrator", "verified_off_data": True,
        "auditor": "hdi_skunkworks", "atomized_by": ATOMIZED_BY,
        "verdict": verdict, "cert_increment_delta": 1, "decision": decision,
        "framing_correction_vs_director": framing, "cross_arc_overlap_check": XARC,
        "net_cert_delta": net_delta, "supersedes": None,
        "needs_orchestrator_store_sync": True, "local_write_only_no_origin_push_no_remote_persist": True,
        "ts_iso": _iso, "ts": _ts, "atom_id": atom["id"],
    }

ledger1 = ledger_row(
    atom1,
    ("HARD_FAIL_CONFIRMED_elman1993_capacity_growth_not_growth_specific_shrink_0p271_beats_growth_0p196_3of3_"
     "lowcap_0p204_gte_growth_3of3_scoped_embedding_dim_not_memory_window_byte_reproduce_exact_parent_provenance"),
    ("HARD_FAIL confirmed (NOT deflated -- symmetric: a clean negative gets the same rigor as a positive). "
     "Numbers reproduce EXACT off-disk (growth 0.196, fixed 0.158, shrink 0.271; growth-shrink -0.075 on 3/3; "
     "lowcap>=growth 3/3). Direction cleanly reversed -> capacity-GROWTH is not growth-specific; any low-"
     "effective-dim schedule matches/beats the ramp. First-class negative that CLOSES the sibling curriculum "
     "cell's 'grow-capacity' next-lever. Scoped honestly to embedding-dim (not Elman's memory-window; k fixed "
     "5). Counts toward CERT as a proven negative."),
    ("Director LED this deflated and called it a clean HARD_FAIL for Elman capacity-growth -- I CONFIRM (no "
     "correction needed on the negative itself). One sharpening: the +0.037 GROWTH>FIXED is NOT a residual "
     "positive for growth; it is the same low-dim clustering-geometry artifact (atom 2), so the negative is even "
     "cleaner than 'growth helps a little but not more than shrink'. And scope the refutation to embedding-dim, "
     "not Elman's memory-window (untested here)."),
    "+1 HARD_FAIL (proven first-class negative: embedding-capacity-GROWTH is not a growth-specific lever on this substrate; memory-window growth OPEN).")

ledger2 = ledger_row(
    atom2,
    ("MEASURED_MECHANISM_compression_category_ami_win_decomposed_part_clustering_geometry_artifact_lowcap_growth_"
     "probe_tie_fixed_pca8_recovers_0p04_part_genuine_shrink_schedule_probe_0p708_vs_0p644_single_seed_tradeoff_"
     "genuine_partly_mechanical"),
    ("MM (proven-bound decomposition). The decisive dimensionality-artifact control the Director asked for: a "
     "supervised logistic POS probe (dim-agnostic) shows LOWCAP/GROWTH encode NO more POS than FIXED (0.655/"
     "0.655 vs 0.644) despite +0.04-0.05 higher AMI -> that AMI edge is clustering geometry (PCA8-compressing "
     "FIXED alone recovers +0.04). Only SHRINK genuinely encodes more POS (probe 0.708 >> 0.644, +6pt ~2x fold-"
     "std, 3-seed AMI margin) -- but single-seed probe, schedule-specific (full-then-compress), catastrophic CE "
     "cost. Prediction/abstraction tradeoff genuine but partly mechanical. Counts toward CERT as a decomposed "
     "mechanism boundary; genuine kernel preserved with a 3-seed-probe revival gate."),
    ("Director wrote: 'I'm inclined to LIKE the compression-positive (SHRINK 0.271 vs FIXED 0.159) but I've over-"
     "read 6 positives -- audit the dimensionality artifact HARDEST.' RESULT (symmetric): the raw-AMI framing "
     "'compression improves abstraction' is PARTLY an artifact -- LOWCAP and GROWTH are clustering-geometry (probe "
     "ties FIXED), so ~half the headline collapses. BUT the Director's instinct is NOT fully wrong: SHRINK "
     "carries a GENUINE, probe-confirmed POS-info gain (0.708 vs 0.644). Net: DEFLATE the general 'compression "
     "helps' claim to a narrow, single-seed, full-then-shrink SCHEDULE lever. The Director's over-read-caution "
     "was well-placed; the probe caught exactly the artifact they worried about, and also rescued a real kernel."),
    "+1 MM (decomposed mechanism boundary: low-effective-dim AMI gain is part clustering-geometry artifact [LOWCAP/GROWTH] + part genuine full-then-shrink SCHEDULE POS-info gain [SHRINK, single-seed probe]; general efficiency law NOT supported, narrow lever OPEN pending 3-seed probe replication).")


def write_atomic_append(path, new_lines):
    if not path.exists():
        return (0, 0, False, "path does not exist: %s" % path)
    with open(path, "rb") as f:
        cur_bytes = f.read()
    cur_text = cur_bytes.decode("utf-8")
    pre_count = cur_text.count("\n")
    if cur_bytes and not cur_bytes.endswith(b"\n"):
        cur_bytes = cur_bytes + b"\n"
    parts = [cur_bytes]
    for line in new_lines:
        s = json.dumps(line, ensure_ascii=True)
        if "\n" in s:
            return (pre_count, pre_count, False, "JSON contains newline; not jsonl-safe")
        parts.append((s + "\n").encode("utf-8"))
    new_bytes = b"".join(parts)
    tmp_path = path.with_suffix(path.suffix + ".tmp_a5")
    with open(tmp_path, "wb") as f:
        f.write(new_bytes); f.flush(); os.fsync(f.fileno())
    os.replace(tmp_path, path)
    with open(path, "rb") as f:
        verify_text = f.read().decode("utf-8")
    post_count = verify_text.count("\n")
    expected_post = pre_count + len(new_lines)
    if post_count != expected_post:
        return (pre_count, post_count, False, "line count mismatch: expected %d got %d" % (expected_post, post_count))
    tail = verify_text.rstrip("\n").split("\n")[-len(new_lines):]
    for i, tl in enumerate(tail):
        try:
            parsed = json.loads(tl)
        except Exception as e:
            return (pre_count, post_count, False, "tail-line %d JSON round-trip fail: %s" % (i, e))
        for key in ("id", "atom_id"):
            if key in new_lines[i] and parsed.get(key) != new_lines[i][key]:
                return (pre_count, post_count, False, "tail-line %d %s mismatch" % (i, key))
    return (pre_count, post_count, True, "OK")


def main():
    print("=== A5 atom-write: srn_capacity_growth_v1 -> HF (Elman) + MM (compression decomp) (2026-07-18) ===")
    print("ts_iso =", _iso)
    for a in (atom1, atom2):
        assert a["id"].isascii(), "non-ascii atom id"
    assert ledger1["atom_id"] == atom1["id"] and ledger2["atom_id"] == atom2["id"], "atom_id/id mismatch"
    assert atom1["id"] != atom2["id"], "atom ids collide"

    existing = set()
    with open(MATH_ATOMS, "rb") as f:
        for line in f:
            try:
                existing.add(json.loads(line).get("id"))
            except Exception:
                pass
    for a in (atom1, atom2):
        if a["id"] in existing:
            print("ABORT: id already in store:", a["id"]); sys.exit(1)
    print("id-uniqueness OK (2 new, not pre-existing)")

    print("Writing 2 atoms to math/atoms.jsonl ...")
    pre, post, ok, err = write_atomic_append(MATH_ATOMS, [atom1, atom2])
    print("  pre=%d post=%d ok=%s err=%s" % (pre, post, ok, err))
    if not ok or post - pre != 2:
        print("ABORT: math atoms write failed"); sys.exit(1)

    print("Writing 2 rows to meta/cert_ledger.jsonl ...")
    pre, post, ok, err = write_atomic_append(CERT_LEDGER, [ledger1, ledger2])
    print("  pre=%d post=%d ok=%s err=%s" % (pre, post, ok, err))
    if not ok or post - pre != 2:
        print("ABORT: cert_ledger write failed"); sys.exit(1)

    n_ok = 0
    present = set()
    with open(MATH_ATOMS, "rb") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            json.loads(line); n_ok += 1
    with open(MATH_ATOMS, "rb") as f:
        for line in f:
            try:
                present.add(json.loads(line).get("id"))
            except Exception:
                pass
    assert atom1["id"] in present and atom2["id"] in present, "post-write integrity: new id missing"
    print("integrity: math/atoms.jsonl fully parses (%d lines), both new ids present." % n_ok)
    print()
    print("=== A5 WRITE COMPLETE (LOCAL ONLY; needs_orchestrator_store_sync=True) ===")
    print("ATOM1 (HF):", atom1["id"][:90], "...")
    print("ATOM2 (MM):", atom2["id"][:90], "...")


if __name__ == "__main__":
    main()
