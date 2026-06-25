"""Skunkworks 2026-06-25 -- 5-cell smoke-to-full VET batch tier-rulings.

Tier rulings (verify-off-data + Q-discipline override):
  Cell 1 (partition_routing_10M_full_v2)    CHAIN_GRADE @ M=100k + bound M=1M  (delta +1)
  Cell 2 (refuse_gate_nonlinear_readout)    MEASURED_MECHANISM (saturation)    (delta 0)
  Cell 3 (distill_verify_operator_eq)        HONEST_NEGATIVE (cv outside rail)  (delta 0)
  Cell 4 (permutation_binding_multiocc)      CHAIN_GRADE (real seed variance)   (delta +1)
  Cell 5 (b_delta_readout_lever_transfer)    MEASURED_MECHANISM (NL ceiling)    (delta 0)

Source notes/skunkworks_tier_ruling_4cell_smoke_to_full_VET_batch_2026-06-25.md

DISCIPLINES:
  - Verify-off-data INDEPENDENT recompute on per_seed for all 5 cells
  - Q-discipline override of cell HARD_PASS for Cells 1/2/5 (saturation pattern)
  - Fix #28: read per-arm metrics directly; caught Director framing errors
    (Cell 3 1-NAMED-not-6; Cell 5 stale 2026-06-18 magnitudes)
  - A5 PRE/POST snapshot; round-trip pq verification
  - Idempotency: skip atoms already in Store
  - Path-scoped commits
  - ASCII only

CERT N delta expected: +2 (Cells 1 + 4 chain-grade).
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path("D:/AI/hd-instrument").resolve()))
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier
from tools.cert_ledger_writer import (
    append_cert_ledger_row,
    build_chain_grade_ruling_row,
    build_honest_negative_row,
    build_measured_mechanism_row,
)


STORE_ROOT = Path("D:/AI/hd-instrument/data/substrate_index")
ATOMIZED_BY = "skunkworks_atomize_4cell_VET_batch_2026-06-25"

NOTES_PATH = "notes/skunkworks_tier_ruling_4cell_smoke_to_full_VET_batch_2026-06-25.md"

# Commit hashes from `git log --oneline -1 -- <metrics_path>` at VET time:
#   Cells 2-5 (CPU local landing batch): ee03871c
#   Cell 1 (GPU late landing, will be path-scoped committed by skunkworks): set CELL1_COMMIT
CELL_2_5_COMMIT = "ee03871c"
CELL1_COMMIT = "523047b6"  # path-scoped commit of Cell 1 metrics.json by skunkworks


# ============================================================================
# CELL 1: chain-grade @ M=100k + tiered bound at M=1M (Q-discipline scope-bound)
# ============================================================================

def build_cell_1_partition_routing_10M_chain_grade() -> Atom:
    return Atom(
        id=(
            "T3/EXP_substrate_partition_routing_10M_full_v2_chain_grade_M_100k_"
            "partition_size_2000_inherits_cell_B_dense_KV_envelope_with_bound_M_1M"
        ),
        name=(
            "Partition-routing M=1M v2 -- CERT_CHAIN_GRADE @ M=100k with proven "
            "bound at M=1M (routed recall@10 M=100k=0.9697 cv=0.0442 / M=1M=0.95 "
            "cv=0.0114; partition_size=2000 each within Cell B dense KV chain-"
            "grade envelope <=10k; routing_acc=1.0 saturation regime-bounded; "
            "flat baseline strictly degrades 0.90->0.51 confirming partition "
            "routing does real work; substrate-product KG extends to 1M-class)"
        ),
        description=(
            "Partition-routing primitive composes VSA L1 routing with per-"
            "partition dense KV cleanup. M=10k/100k/1M N=1024 partition_size=2000 "
            "3 seeds [11, 13, 19]. Cell self-verdict HARD_PASS_PARTIAL_AT_M_1M "
            "(+ chain-grade @ M=100k per cell's own band ladder). Cert-owner "
            "ruling: CERT_CHAIN_GRADE at M=100k operating point with proven "
            "bound at M=1M; saturated routing_acc=1.0 regime-caveated.\n\n"
            "PER-N (3 seeds [11, 13, 19], independently recomputed off "
            "per_seed.routed_per_N):\n"
            "  M=10000:  routed=0.9167 cv=0.1286  per-seed=[0.75, 1.0, 1.0]\n"
            "  M=100000: routed=0.9697 cv=0.0442  per-seed=[0.9091, 1.0, 1.0]\n"
            "  M=1000000: routed=0.9500 cv=0.0114 per-seed=[0.945, 0.94, 0.965]\n"
            "  routing_acc per_N = 1.0 cv=0.0 across ALL (seed, N) cells\n"
            "  flat_per_N degrades strictly: 0.90 -> 0.7305 -> 0.5139\n\n"
            "BAND PLACEMENT (cell pre-reg bands):\n"
            "  HARD_PASS_M100K_ROUTED: 0.85; measured 0.9697 (PASS +14%)\n"
            "  HARD_PASS_M100K_CV: 0.05; measured 0.0442 (PASS within rail)\n"
            "  HARD_PASS_M100K_ROUTE_ACC: 0.95; measured 1.0 (PASS but saturated)\n"
            "  HARD_PASS_M1M_ROUTED: 0.50 stretch; measured 0.95 (PASS +90%)\n"
            "  HARD_FAIL_M100K_ROUTED: 0.50; measured 0.9697 (clear)\n"
            "  Q_SUSPECT_SATURATION: 0.995; routing_acc=1.0 triggers Q-flag\n\n"
            "Q-DISCIPLINE / SCOPE BOUND:\n"
            "  routing_acc=1.0 across all 9 (seed, N) cells IS at metric "
            "ceiling. The routing-decision step (which partition does query "
            "belong to) is near-trivial here because partition centroids are "
            "well-separated by construction (target_cos=0.133, cat_cos=0.7). "
            "routed_recall@10 is sub-saturation at multiple operating points "
            "(seed 11 at M=10k = 0.75; seed 11 at M=100k = 0.9091; all 3 "
            "seeds at M=1M in [0.94, 0.965] range). This is the substantive "
            "metric and shows honest seed variance.\n"
            "  Mechanism doing real work: flat baseline strictly degrades "
            "0.90 (M=10k) -> 0.73 (M=100k) -> 0.51 (M=1M). At M=1M routed "
            "beats flat by +0.44. NOT by-construction-saturation.\n\n"
            "ENVELOPE (load-bearing):\n"
            "  partition_size = 2000 (well below Cell B M=10k cliff at M=50k)\n"
            "  P_max = 500 partitions at M=1M\n"
            "  per-partition cleanup inherits Cell B chain-grade envelope "
            "(dense KV at M<=10k d=768 sigma=0.10 isotropic random-bipolar)\n"
            "  target_cos=0.133 / cat_cos=0.7 (partition centroid separation)\n"
            "  N=1024 (substrate width for routing layer)\n"
            "  device: NVIDIA RTX 4060 Ti; elapsed_s=1.55 (fast at M=1M)\n"
            "  Zero LLM forward calls at inference (verified per per_seed)\n\n"
            "COMPOSITION (inheritance from Cell B):\n"
            "  Cell 1 + Cell B compositionally VALID. Cell 1 partitions "
            "M=1M into 500 partitions of size 2000 each, well within Cell B "
            "chain-grade envelope (M<=10k cliff at M=50k). If Cell B atom "
            "demotes or partition_size>2000 used, Cell 1 atom inherits "
            "demote. Cell B + Cell 1 jointly map KG operating envelope: "
            "dense @ <=10k per partition, route @ 1M total.\n\n"
            "TIER RULING JUSTIFICATION:\n"
            "  CHAIN_GRADE at M=100k operating point: primary HARD_PASS band "
            "0.85 cleared with +14% margin; cv=0.044 within rail 0.05; real "
            "seed variance (seed 11 sub-ceiling 0.9091). This is genuine "
            "chain-grade evidence.\n"
            "  Proven bound at M=1M: above stretch HP 0.50 by 0.45; ALL "
            "seeds sub-ceiling (0.94, 0.94, 0.965). Not chain-grade because "
            "routing_acc saturation prevents extension claim without measuring "
            "where the routing mechanism itself starts to degrade.\n"
            "  Tiered single atom: chain-grade at M=100k with proven extension "
            "M=1M (analogous to Cell B tiering @ M=10k chain-grade + cliff "
            "@ M=50k proven bound).\n\n"
            "STRATEGIC ROLE: substrate-product KG positioning extends from "
            "Cell B 10k-class dense to 1M-class via partition routing. "
            "Architectural primitive that scales is partition routing + per-"
            "partition dense cleanup, not dense KV alone. Plus one chain-"
            "grade definitive in substrate-product KG envelope."
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "CERT_CHAIN_GRADE",
            "cert_status": "chain_grade",
            "cert_class": "pre_reg_pass",
            "verdict": (
                "HARD_PASS_PARTIAL_AT_M_1M_skunkworks_chain_grade_at_M_100k_"
                "with_proven_bound_at_M_1M_3seeds_11_13_19_partition_size_2000_"
                "P_max_500_routed_M_10k_0p9167_cv_0p1286_M_100k_0p9697_cv_0p0442_"
                "M_1M_0p95_cv_0p0114_routing_acc_1p0_saturated_regime_bounded_"
                "flat_baseline_strictly_decreasing_0p90_0p7305_0p5139_partition_"
                "routing_doing_real_work_inherits_Cell_B_dense_KV_envelope_at_"
                "partition_size_2000_substrate_product_KG_extends_to_1M_class_"
                "tiered_atom_chain_grade_at_M_100k_plus_proven_bound_at_M_1M"
            ),
            "cell_commit": CELL1_COMMIT,
            "metrics_path": (
                "data/exp_substrate_partition_routing_10M_full_v2/metrics.json"
            ),
            "notes_path": NOTES_PATH,
            "verified_off_data": (
                "Cert-owner read aggregate.routed_per_N_mean + routed_per_N_cv "
                "+ routed_per_N_per_seed + routing_acc_per_N_mean + "
                "flat_per_N_mean directly off metrics.json for 3 seeds. "
                "routed_per_N_mean M=10k=0.9167 cv=0.1286 per-seed [0.75, 1.0, "
                "1.0]; M=100k=0.9697 cv=0.0442 per-seed [0.9091, 1.0, 1.0]; "
                "M=1M=0.95 cv=0.0114 per-seed [0.945, 0.94, 0.965]. ALL seeds "
                "at M=1M sub-ceiling -- honest variance. routing_acc=1.0 "
                "across 9 (seed, N) cells = Q-suspect saturation; cell band "
                "Q_SUSPECT_SATURATION=0.995 fires. flat_per_N strictly degrades "
                "0.9 -> 0.7305 -> 0.5139; flat_strictly_decreasing=True verified. "
                "At M=1M routed-flat gap = 0.95-0.5139 = 0.436. Compositional "
                "validity: partition_size=2000 within Cell B chain-grade dense "
                "KV envelope <=10k cliff at 50k. P_max=500 at M=1M. "
                "target_cos=0.133 cat_cos=0.7 = partition centroid separation "
                "explains routing_acc ceiling honestly. elapsed_s=1.55 on "
                "RTX 4060 Ti."
            ),
            "honest_scope": (
                "Chain-grade at partition_size=2000 routing layer N=1024 with "
                "per-partition cleanup inheriting Cell B dense KV envelope. "
                "DOES show routed_recall@10 0.97 at M=100k with cv=0.044 + "
                "0.95 at M=1M with cv=0.011 -- substrate-product KG extends "
                "to 1M-class. DOES show flat baseline strictly degrades, "
                "confirming partition routing does real work. DOES NOT test "
                "partition_size > 2000 (extension would require new Cell B "
                "envelope). DOES NOT measure where routing mechanism itself "
                "starts to degrade (routing_acc=1.0 ceiling). DOES NOT test "
                "anisotropic partition encoders. DOES NOT test online "
                "(continual) partition reassignment."
            ),
            "n_seeds": 3,
            "seeds": [11, 13, 19],
            "N": 1024,
            "partition_size": 2000,
            "P_max": 500,
            "M_grid": [10000, 100000, 1000000],
            "target_cos": 0.133,
            "cat_cos": 0.7,
            "chain_grade_operating_point": {
                "M": 100000,
                "routed_recall_at_10_mean": 0.9697,
                "routed_recall_at_10_cv": 0.0442,
                "routing_acc": 1.0,
                "flat_baseline": 0.7305,
            },
            "proven_bound_extension": {
                "M": 1000000,
                "routed_recall_at_10_mean": 0.95,
                "routed_recall_at_10_cv": 0.0114,
                "routing_acc": 1.0,
                "flat_baseline": 0.5139,
                "interpretation": (
                    "Above stretch HP 0.50 by 0.45; routing_acc saturation "
                    "prevents chain-grade extension claim without measuring "
                    "routing mechanism degradation point"
                ),
            },
            "Q_discipline_check": {
                "routing_acc_at_1p0_ALL_cells": True,
                "Q_SUSPECT_SATURATION_threshold": 0.995,
                "Q_SUSPECT_routing_acc_FIRES": True,
                "BUT_routed_recall_genuine_variance": True,
                "by_construction_saturation_overall": False,
            },
            "pre_reg_bands": {
                "HP_M100K_ROUTED": ">=0.85 (PASS 0.97; +14% margin)",
                "HP_M100K_CV": "<=0.05 (PASS 0.044)",
                "HP_M100K_ROUTE_ACC": ">=0.95 (PASS 1.0 but saturated)",
                "HP_M1M_ROUTED": ">=0.50 stretch (PASS 0.95)",
                "HARD_FAIL_M100K_ROUTED": ">=0.50 (PASS far above)",
            },
            "envelope_inherits_from": (
                "T3/EXP_substrate_KG_capacity_sweep_d768_sigma01_chain_grade_"
                "at_M_10k_proven_cliff_M_50k (Cell B 2026-06-25)"
            ),
            "envelope_caveat": (
                "Chain-grade ONLY at partition_size=2000 (well below Cell B "
                "M=50k cliff). If partition_size > Cell B envelope ceiling, "
                "this Cell 1 atom inherits demote."
            ),
            "strategic_role": (
                "Substrate-product KG positioning extends from 10k-class dense "
                "(Cell B) to 1M-class via partition routing. Plus one chain-"
                "grade definitive to substrate-product KG envelope. Cell B + "
                "Cell 1 jointly map KG operating envelope."
            ),
            "device": "cuda_RTX_4060_Ti",
            "elapsed_s": 1.55,
            "gpu_available": True,
            "zero_llm_calls_at_inference": True,
            "composes_with": [
                "T3/EXP_substrate_KG_capacity_sweep_d768_sigma01_chain_grade_"
                "at_M_10k_proven_cliff_M_50k",
            ],
            "cites": [
                "Fix_28_verify_per_arm_metrics_per_seed_direct_recompute",
                "Q_discipline_routing_acc_saturation_routed_recall_real_variance",
                "Cell_B_envelope_inheritance_partition_size_within_dense_KV_chain_grade",
                "Director_routed_batch_2026-06-25_tier_ruling_5cell",
            ],
            "atomized_by": ATOMIZED_BY,
            "atomized_date": "2026-06-25",
            "era": "comprehensive_program_phase3_glassbox",
        },
    )


# ============================================================================
# CELL 2: measured_mechanism (saturation suspect; synthetic regime too easy)
# ============================================================================

def build_cell_2_refuse_gate_nonlinear_readout_v2_full_MM() -> Atom:
    return Atom(
        id=(
            "T3/EXP_substrate_refuse_gate_nonlinear_readout_v2_full_"
            "measured_mechanism_synthetic_regime_saturation_42pct_ops_saturate"
        ),
        name=(
            "Refuse-gate nonlinear-readout v2 full -- MEASURED_MECHANISM "
            "(concentration gate gap_refuse=1.000 at (beta=10..40, c=0.15..0.95) "
            "across 3 seeds; BUT 42% of 270 (seed, beta, c) cells saturate "
            ">=0.95 + accept_drop=0.0 EVERYWHERE; synthetic absent regime too "
            "discriminating; real-bge held-out is the unanswered chain-grade "
            "question; envelope bounded to synthetic noise=0.10 paraphrase regime)"
        ),
        description=(
            "Nonlinear-readout concentration gate (sigmoid(beta*(maxw-c))) on "
            "spread_report present vs absent. 3 seeds [11, 13, 19], 5 betas x "
            "18 c-thresholds = 90 ops per seed; n=256 alpha=1.0 paraphrase-"
            "noise=0.10 synthetic absent regime. Cell self-verdict HARD_PASS_"
            "CHAIN_GRADE. Cert-owner ruling: MEASURED_MECHANISM (saturation "
            "regime override).\n\n"
            "PER-SEED BEST (independently recomputed):\n"
            "  seed=11 best beta=10.0 c=0.15 gap_refuse=1.0 accept_drop=0.0\n"
            "  seed=13 best beta=10.0 c=0.15 gap_refuse=1.0 accept_drop=0.0\n"
            "  seed=19 best beta=10.0 c=0.15 gap_refuse=1.0 accept_drop=0.0\n"
            "(aggregate.best_chain_grade keys '40.0_0.95' but per-seed best "
            "is '10.0_0.15'; both saturate at 1.0; tiebreak picks differently.)\n\n"
            "SATURATION DENSITY (verified off-data):\n"
            "  113 of 270 (seed, beta, c) cells have gap_refuse >= 0.95 = 41.85%\n"
            "  accept_drop = 0.0 in EVERY one of 270 cells (present never drops)\n\n"
            "DISCRIMINATING SPREAD (mechanism IS real on opposite end):\n"
            "  beta=160_0.1: gap=0.0 / 0.0 / 0.0 (high-beta over-concentration)\n"
            "  beta=80_0.95: gap=0.82 / 0.88 / 0.92 (medium-beta near-saturation)\n"
            "  beta=40_0.1:  gap=0.017 / 0.017 / 0.0 (low-c too lax)\n"
            "  Rich (beta,c) curve exists; cell IS measuring a real bound.\n\n"
            "Q-DISCIPLINE OVERRIDE (saturation regime too easy):\n"
            "  42% of operating points saturate + accept_drop=0.0 universally "
            "= synthetic absent regime is structurally too easy. Real "
            "absent embeddings (real-bge held-out) have distribution overlap "
            "with present (this is the gap real refuse-gates must close), and "
            "this cell's spread_report.absent uses an over-clean synthetic "
            "(maxw_med 0.058 at beta=10 vs present 0.978 = 17x gap).\n"
            "  Cell measures a REAL primitive bound at this regime; chain-grade "
            "requires real-distribution evidence (real-bge held-out at typical "
            "<5x absent/present gap).\n\n"
            "ENVELOPE (load-bearing):\n"
            "  synthetic absent regime: paraphrase-noise=0.10 alpha=1.0 n=256\n"
            "  V_concentration: beta in {10, 20, 40, 80, 160} x c in 0.05-grid\n"
            "  Chain-grade operating point in synthetic regime: beta in [10, 40]\n"
            "  bands: HP gap_refuse=0.95 cv=0.05; HARD_FAIL gap=0.8\n\n"
            "STRATEGIC ROLE: refuse-gate primitive count unchanged by this VET. "
            "Substrate refuse-gate-tier portfolio:\n"
            "  3 chain-grade: audit-relation, graph-health, CSP\n"
            "  1 MM (this cell): nonlinear-readout pending real-bge held-out\n"
            "  Nonlinear-readout-concentration-gate is a real bound primitive; "
            "to chain-grade it requires real-bge held-out evidence at typical "
            "absent/present cosine gap (~0.5).\n\n"
            "REVIVAL PATH: v3 real-bge held-out absent (e.g. negative-pair "
            "harvest from BEIR or wiki random); HP gap_refuse target dropped "
            "to >=0.70 for genuinely harder distribution; broader (beta, c) "
            "grid only after real-bge baseline established.\n\n"
            "TIER: MEASURED_MECHANISM; delta=0; bound proven at synthetic "
            "regime (concentration-gate is a real primitive); chain-grade "
            "requires real-distribution evidence."
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "MEASURED_MECHANISM",
            "cert_status": "measured_mechanism",
            "cert_class": "mechanism_characterization",
            "verdict": (
                "MEASURED_MECHANISM_skunkworks_saturation_override_3seeds_11_13_19_"
                "synthetic_absent_regime_paraphrase_noise_0p10_42pct_270_ops_"
                "saturate_at_0p95_accept_drop_0p0_EVERY_cell_present_never_drops_"
                "rich_beta_c_curve_at_high_beta_low_c_mechanism_is_real_bound_"
                "but_chain_grade_requires_real_bge_held_out_at_typical_5x_"
                "absent_present_gap_substrate_refuse_gate_count_unchanged_"
                "3_chain_grade_plus_1_MM_revival_v3_real_bge_held_out"
            ),
            "cell_commit": CELL_2_5_COMMIT,
            "metrics_path": (
                "data/exp_substrate_refuse_gate_nonlinear_readout_v2_full/metrics.json"
            ),
            "notes_path": NOTES_PATH,
            "verified_off_data": (
                "Cert-owner read per_seed.per_op + spread_report directly. "
                "All 3 seeds best (beta=10.0, c=0.15) gap_refuse=1.0 "
                "accept_drop=0.0 score=1.0. aggregate.best_chain_grade keys "
                "'40.0_0.95' with gap=1.0 ALL seeds verified per_op[40.0_0.95]. "
                "Saturation density: 113 of 270 (seed x beta x c) cells have "
                "gap_refuse >= 0.95 = 41.85% verified by enumerating per_op. "
                "accept_drop=0.0 in ALL 270 cells verified by enumeration. "
                "Discriminating spread present: beta=160_0.1 gap=0 across all "
                "seeds; beta=80_0.95 gap in [0.82, 0.92]. spread_report "
                "shows absent_spreads=True at beta<=80 and False at beta=160 "
                "(over-concentration). present_maxw_med saturates 1.0 at "
                "beta>=40; absent_maxw_med 0.058 at beta=10 vs 0.92 at beta=160."
            ),
            "honest_scope": (
                "MM in synthetic absent regime (paraphrase-noise=0.10 alpha=1.0 "
                "n=256 3 seeds). DOES show concentration-gate sigmoid(beta*"
                "(maxw-c)) is a real bound primitive (rich (beta, c) curve "
                "with discrimination at high-beta low-c). DOES NOT chain-grade "
                "at this regime because synthetic absent is too easy (42% ops "
                "saturate + accept_drop=0 universally). DOES NOT test real-bge "
                "held-out distribution. DOES NOT test BEIR negative-pair harvest. "
                "DOES NOT test composition with other refuse-gate primitives."
            ),
            "n_seeds": 3,
            "seeds": [11, 13, 19],
            "alpha": 1.0,
            "n": 256,
            "n_operating_points": 90,
            "n_total_ops_3_seeds": 270,
            "n_saturated_ops": 113,
            "saturated_fraction": 0.4185,
            "accept_drop_universal_zero": True,
            "best_chain_grade_op": {
                "beta": 40.0,
                "c": 0.95,
                "gap_refuse_mean": 1.0,
                "gap_refuse_cv": 0.0,
                "accept_drop": 0.0,
            },
            "per_seed_best": {
                "beta": 10.0,
                "c": 0.15,
                "gap_refuse": 1.0,
                "accept_drop": 0.0,
            },
            "discriminating_spread_check": {
                "beta_160_c_0.1_gap_per_seed_all_zero": True,
                "beta_80_c_0.95_gap_range": [0.82, 0.92],
                "absent_spreads_True_at_beta_le_80": True,
                "mechanism_real_at_high_beta_low_c": True,
            },
            "Q_discipline_check": {
                "saturation_density_pct": 41.85,
                "saturation_density_threshold": 30.0,
                "Q_FIRES_saturation_too_dense": True,
                "accept_drop_zero_universal": True,
                "synthetic_regime_too_easy": True,
                "real_bge_held_out_required_for_chain_grade": True,
            },
            "pre_reg_bands": {
                "HP_GAP_REFUSE": ">=0.95 (PASS 1.0 saturated)",
                "HP_ACCEPT_DROP": "<=0.05 (PASS 0.0 trivially)",
                "HP_CV": "<=0.05 (PASS 0.0 saturated)",
                "HARD_FAIL_GAP": "<0.8 (clear; not failing)",
            },
            "envelope_caveat": (
                "MM ONLY at synthetic absent regime paraphrase-noise=0.10 "
                "n=256. Chain-grade requires real-bge held-out at typical 5x "
                "absent/present cosine gap."
            ),
            "strategic_role": (
                "Refuse-gate primitive count UNCHANGED: 3 chain-grade + 1 MM. "
                "Nonlinear-readout-concentration-gate is a real bound primitive "
                "at synthetic regime; revival via v3 real-bge held-out."
            ),
            "elapsed_s": 0.09,
            "run_mode": "full",
            "cites": [
                "Fix_28_verify_per_arm_metrics_per_seed_direct_recompute",
                "Q_discipline_saturation_density_override",
                "Refuse_gate_primitive_count_unchanged_3_chain_grade_plus_1_MM",
                "Director_routed_batch_2026-06-25_tier_ruling_5cell",
            ],
            "atomized_by": ATOMIZED_BY,
            "atomized_date": "2026-06-25",
            "era": "comprehensive_program_phase3_glassbox",
        },
    )


# ============================================================================
# CELL 3: honest_negative (cv outside rail; 1 NAMED total not 6; methodology weak)
# ============================================================================

def build_cell_3_distill_verify_operator_equivalence_v2_full_HN() -> Atom:
    return Atom(
        id=(
            "T3/EXP_substrate_distill_verify_operator_equivalence_v2_full_"
            "honest_negative_cv_outside_rail_corpus_1_NAMED_named_axis_untestable"
        ),
        name=(
            "Distill-verify operator equivalence v2 full -- HONEST_NEGATIVE "
            "(held distill 0.7778 below HP 0.80 + cv 0.20 ABOVE rail 0.07; "
            "ONLY 1 NAMED operator across 20 groups -- Director-claimed 6 "
            "NAMED falsified off-data; named-discriminator axis structurally "
            "untestable at this corpus; non-disjoint held-out folds)"
        ),
        description=(
            "Provable-operator-equivalence distillation held-out test. 3-fold "
            "cv across 3 seeds [11, 13, 19] over 20 duplicate-operator groups "
            "(14 training + 6 held-out per seed). Cell self-verdict MIDDLE_BAND_"
            "PARTIAL. Cert-owner ruling: HONEST_NEGATIVE (below HP + cv outside "
            "rail + corpus structurally too small for named-axis test).\n\n"
            "PER-SEED (independently recomputed):\n"
            "  seed=11 held_distill=0.6667 (4 of 6 PROVABLY_EQUIVALENT)\n"
            "  seed=13 held_distill=1.0000 (6 of 6 PROVABLY_EQUIVALENT)\n"
            "  seed=19 held_distill=0.6667 (4 of 6 PROVABLY_EQUIVALENT)\n"
            "  mean=0.7778 cv=0.2020\n\n"
            "BAND PLACEMENT (cell pre-reg bands):\n"
            "  HP_DISTILL: >=0.80; measured 0.7778 (MISS by 0.022; in MIDDLE)\n"
            "  HP_CV: <=0.07; measured 0.20 (MISS by 2.9x outside)\n"
            "  HARD_FAIL: <0.60; measured 0.7778 (PASS not failing)\n"
            "  MIDDLE_BAND: [0.60, 0.80); 0.7778 in middle band\n\n"
            "CRITICAL DIRECTOR FRAMING CORRECTION (verified off-data):\n"
            "  Director task referenced 'all 6 NAMED in 14-group training fold "
            "across 20 total dup-groups' -- FALSIFIED. Verified per-seed:\n"
            "    seed=11 named_in_training=1 named_in_held_out=0\n"
            "    seed=13 named_in_training=1 named_in_held_out=0\n"
            "    seed=19 named_in_training=1 named_in_held_out=0\n"
            "  Substrate has ONLY 1 NAMED operator across the entire 20-group "
            "corpus. All 3 seeds land that 1 NAMED in training fold (random "
            "chance 0.7^3=0.343; not pathological but corpus is too small to "
            "test named-axis at all).\n"
            "  named_held_distill_ratio=0.0 with cv=Infinity is mathematically "
            "trivial 0/0=NaN->inf; NOT meaningful signal.\n\n"
            "FOLD-DISJOINTNESS CHECK (methodology weakness):\n"
            "  fold_overlap_pairs: [[0,1,2,6,6], [0,2,2,6,6], [1,2,1,6,6]]\n"
            "  seeds 0&1 share 2 held-out groups; 0&2 share 2; 1&2 share 1\n"
            "  3-fold CV with overlap = reduced effective sample size; another "
            "factor in cv inflation\n\n"
            "Q-DISCIPLINE / TIER OVERRIDE:\n"
            "  Cell self-verdict MIDDLE_BAND_PARTIAL is the right band placement "
            "for the held-distill metric (0.7778 in [0.60, 0.80)) but BOTH:\n"
            "    (a) below HP 0.80 (chain-grade miss)\n"
            "    (b) cv 0.20 above HP rail 0.07 by 2.9x\n"
            "  triggers ledger cert_status='honest_negative' (proven bound "
            "that current methodology does NOT chain-grade) NOT just MIDDLE_BAND "
            "(which would leave it ambiguously open).\n\n"
            "REVIVAL PATH (v3 design requirements):\n"
            "  (a) NAMED corpus expansion 1 -> >=6 (so named-stratified split "
            "is feasible at all)\n"
            "  (b) disjoint folds enforcement (rotate, not shuffle)\n"
            "  (c) optionally relax cv-rail given small-corpus regime\n"
            "  (d) cap_int integration-check: prover-tier composition (T3+T2 "
            "vs T1 vs NA) appears in raw data; consider per-tier cv-rail\n\n"
            "STRATEGIC ROLE: substrate META-reasoning primitive (distill+"
            "verify operator equivalence) characterized as below-HP at current "
            "corpus AND named-axis is structurally untestable. This is an "
            "informative negative on substrate-product META-reasoning frontier; "
            "revival requires corpus expansion + methodology refresh.\n\n"
            "TIER: HONEST_NEGATIVE pre_reg_miss_proven_bound; delta=0."
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "HARD_FAIL",
            "cert_status": "honest_negative",
            "cert_class": "pre_reg_miss_proven_bound",
            "verdict": (
                "HONEST_NEGATIVE_skunkworks_below_HP_plus_cv_outside_rail_"
                "3seeds_11_13_19_held_distill_per_seed_0p6667_1p0_0p6667_"
                "mean_0p7778_below_HP_0p80_cv_0p20_above_rail_0p07_2p9x_"
                "DIRECTOR_FRAMING_CORRECTION_named_in_training_only_1_per_seed_"
                "named_in_held_out_0_per_seed_corpus_1_NAMED_TOTAL_across_20_"
                "groups_not_6_named_axis_structurally_untestable_fold_overlap_"
                "pairs_seeds_share_1_to_2_held_groups_methodology_weakness_"
                "revival_v3_needs_NAMED_corpus_expansion_to_6_plus_disjoint_folds"
            ),
            "cell_commit": CELL_2_5_COMMIT,
            "metrics_path": (
                "data/exp_substrate_distill_verify_operator_equivalence_v2_full/"
                "metrics.json"
            ),
            "notes_path": NOTES_PATH,
            "verified_off_data": (
                "Cert-owner read per_seed.held_distill_ratio + held_out_results "
                "+ named_in_training/held_out + n_total_groups + "
                "fold_overlap_pairs directly off metrics.json. Per-seed "
                "held_distill_ratio [0.6667, 1.0, 0.6667] mean 0.7778 cv 0.2020. "
                "named_in_training=1 for ALL 3 seeds; named_in_held_out=0 for "
                "ALL 3 seeds. n_total_groups=20 verified. Union of all held + "
                "training group names across seeds = 20 unique. The 1 NAMED "
                "operator across the whole corpus lands in training fold every "
                "time (random chance 0.7^3=0.343). named_held_distill_ratio=0 "
                "with cv=inf is mathematically trivial 0/0 NaN; not meaningful. "
                "fold_overlap_pairs [[0,1,2,6,6], [0,2,2,6,6], [1,2,1,6,6]] = "
                "seeds 0&1 overlap 2 held, 0&2 overlap 2, 1&2 overlap 1 = "
                "non-disjoint methodology. Held-out results include verdicts "
                "across PROVABLY_EQUIVALENT, UNDECIDABLE_BY_PROVER, NOT_EQUIVALENT "
                "categories; per-seed seeds: seed=11 4 of 6 held provable, "
                "seed=13 6 of 6, seed=19 4 of 6. any_not_equiv=False (no held "
                "fold flagged a NOT_EQUIVALENT)."
            ),
            "honest_scope": (
                "Honest-negative on held-distillation chain-grade at current "
                "20-group corpus with 1 NAMED total. DOES show distillation "
                "verifier flags 4 of 6 (or 6 of 6) PROVABLY_EQUIVALENT across "
                "held folds. DOES show no NOT_EQUIVALENT misfires in held "
                "(any_not_equiv=False). DOES NOT chain-grade at HP 0.80 + "
                "cv 0.07 simultaneously. DOES NOT permit named-axis test "
                "(corpus too small). DOES NOT enforce disjoint folds. DOES NOT "
                "test cap_int integration with prover-tier composition."
            ),
            "n_seeds": 3,
            "seeds": [11, 13, 19],
            "n_total_groups": 20,
            "n_held_out_per_seed": 6,
            "n_training_per_seed": 14,
            "n_named_total_in_corpus": 1,
            "n_named_in_training_per_seed": [1, 1, 1],
            "n_named_in_held_out_per_seed": [0, 0, 0],
            "held_distill_per_seed": [0.6667, 1.0, 0.6667],
            "held_distill_mean": 0.7778,
            "held_distill_cv": 0.2020,
            "fold_overlap_pairs_seeds_share_held": [
                [0, 1, 2],  # seeds 0&1 share 2 held groups
                [0, 2, 2],  # seeds 0&2 share 2 held groups
                [1, 2, 1],  # seeds 1&2 share 1 held group
            ],
            "named_axis_untestable_reason": (
                "Only 1 NAMED operator across 20-group corpus; cannot stratify "
                "named vs non-named in 3-fold CV"
            ),
            "director_framing_error_corrected": (
                "Director task claimed 'all 6 NAMED in 14-group training fold "
                "across 20 total dup-groups'; off-data shows only 1 NAMED total. "
                "Corpus has been reduced from earlier v1 reference to 20 groups; "
                "NAMED count is 1 not 6."
            ),
            "Q_discipline_check": {
                "cv_outside_rail_factor": 2.9,
                "mean_below_HP_band": True,
                "tier_HN_not_MIDDLE": True,
                "named_axis_untestable_corpus_too_small": True,
                "non_disjoint_folds_methodology_weakness": True,
            },
            "pre_reg_bands": {
                "HP_DISTILL": ">=0.80 (MISS 0.7778)",
                "HP_CV": "<=0.07 (MISS 0.20)",
                "HARD_FAIL": "<0.60 (PASS not failing 0.7778)",
                "MIDDLE_BAND": "[0.60, 0.80); 0.7778 in middle",
            },
            "revival_path_requirements": {
                "named_corpus_expansion": "1 -> >=6 NAMED operators",
                "disjoint_folds_methodology": "rotate not shuffle",
                "consider_relaxed_cv_rail_small_corpus": True,
                "cap_int_per_tier_cv_rail": True,
            },
            "strategic_role": (
                "Substrate META-reasoning primitive characterized as below-HP "
                "at current corpus; named-axis structurally untestable. "
                "Informative negative on META-reasoning frontier; revival "
                "requires corpus expansion + methodology refresh."
            ),
            "elapsed_s": 0.27,
            "run_mode": "full",
            "cites": [
                "Fix_28_verify_per_arm_metrics_per_seed_direct_recompute",
                "verify_the_referent_director_NAMED_count_falsified_off_data",
                "symmetric_anti_negativity_honest_below_HP_ruled_HN_not_MIDDLE",
                "Director_routed_batch_2026-06-25_tier_ruling_5cell",
            ],
            "atomized_by": ATOMIZED_BY,
            "atomized_date": "2026-06-25",
            "era": "comprehensive_program_phase3_glassbox",
        },
    )


# ============================================================================
# CELL 4: chain-grade (HRR primitive upgrade; FHRR baseline real seed variance)
# ============================================================================

def build_cell_4_permutation_binding_multiocc_v2_full_chain_grade() -> Atom:
    return Atom(
        id=(
            "T3/EXP_substrate_permutation_binding_multiocc_v2_full_chain_grade_"
            "HRR_primitive_upgrade_cyclic_shift_cleanup_rescues_FHRR_collision"
        ),
        name=(
            "Permutation-indexed binding multi-occ v2 full -- CERT_CHAIN_GRADE "
            "(perm 1.0000 vs FHRR 0.0629 across 3 seeds; FHRR baseline cv=0.117 "
            "with per-seed [0.053, 0.064, 0.071] honestly near chance 1/20=0.05; "
            "lift=0.9371 cv=0.0078; cyclic-shift cleanup rescues FHRR same-role "
            "collision failure mode; HRR-tier substrate primitive count +1)"
        ),
        description=(
            "Permutation-indexed binding rescues FHRR same-role multi-occurrence "
            "collision via cyclic-shift cleanup. 3 seeds [11, 13, 19] n_subset="
            "450 each N=512 d=512. Cell self-verdict HARD_PASS_CHAIN_GRADE. "
            "Cert-owner ruling: CERT_CHAIN_GRADE (real-discriminator-gap not "
            "by-construction-saturation).\n\n"
            "PER-SEED (independently recomputed):\n"
            "  seed=11 fhrr=0.0533 perm=1.0 lift=0.9467 n_subset=450\n"
            "  seed=13 fhrr=0.0644 perm=1.0 lift=0.9356 n_subset=450\n"
            "  seed=19 fhrr=0.0711 perm=1.0 lift=0.9289 n_subset=450\n"
            "  perm=1.0 ALL seeds; FHRR cv=0.1166 (recomputed; substantial); "
            "lift cv=0.0078 (real seed variance).\n\n"
            "BAND PLACEMENT (cell pre-reg bands):\n"
            "  HP_PERM: >=0.95; measured 1.0 (PASS at ceiling)\n"
            "  HP_FHRR_MAX: <=0.10; measured 0.0629 (PASS; FHRR honestly fails)\n"
            "  HP_LIFT: >=0.85; measured 0.9371 (PASS +10% margin)\n"
            "  HP_CV: <=0.05; lift cv=0.0078 (PASS clear)\n"
            "  HARD_FAIL_PERM: <0.70; measured 1.0 (clear)\n\n"
            "Q-DISCIPLINE / DISCRIMINATOR GAP CHECK:\n"
            "  perm=1.0 looks like by-construction-saturation at first glance.\n"
            "  BUT: FHRR baseline cv=0.1166 with per-seed [0.053, 0.064, 0.071] "
            "shows REAL seed variance at the chance-floor level (1/20=0.05 "
            "for random pick among 20 multi-occ candidates). FHRR HONESTLY "
            "FAILS at the baseline regime; perm-indexed honestly SUCCEEDS.\n"
            "  Discriminator gap: 1.0000 - 0.0629 = 0.9371 absolute = 93.7% "
            "swing from baseline-floor to mechanism-ceiling. NOT by-"
            "construction-saturation; the FHRR baseline IS the same family "
            "at the same N=512 d=512 same n_subset, and it FAILS. The "
            "mechanism (cyclic-shift cleanup) is doing 93.7% of the work.\n\n"
            "MECHANISM:\n"
            "  FHRR multi-occurrence collision: same role-key bound to "
            "multiple value-vectors creates additive interference. Cleanup "
            "via standard FHRR returns the centroid of all bound vectors, "
            "which is near-orthogonal to any individual value (1/20 = chance "
            "pick).\n"
            "  Permutation-indexed binding: i-th occurrence uses permutation "
            "pi^i applied to role-key, so pi^0 K, pi^1 K, pi^2 K are mutually "
            "near-orthogonal; cleanup via inverse-permutation per occurrence "
            "index returns the correct value-vector cleanly. Same envelope "
            "(N, d, encoder) as FHRR; different binding primitive.\n\n"
            "ENVELOPE (load-bearing):\n"
            "  N = 512 (HRR width)\n"
            "  n_subset = 450 per seed (binding capacity test)\n"
            "  multi-occurrence regime: same role-key bound to >=2 values\n"
            "  cleanup: cyclic-shift inverse-permutation per occurrence index\n"
            "  Zero LLM forward calls at inference\n\n"
            "STRATEGIC ROLE: substrate basis HRR-tier extends by 1 chain-"
            "grade primitive. Substrate now has 2 HRR-family mechanisms: "
            "standard FHRR + permutation-indexed binding. The latter is the "
            "multi-occurrence-robust variant; composes anywhere FHRR fails "
            "to same-role collision.\n\n"
            "COMPOSITION: composes with Stage 2 mechanisms (FREQ_ROUTED_"
            "DEEPER + MULTIPLICATIVE_LEVER) -- whenever a binding primitive "
            "must support multi-occurrence, permutation-indexed variant "
            "should replace standard FHRR. Could extend Stage 2 envelope "
            "(integration test pending).\n\n"
            "TIER: CERT_CHAIN_GRADE; delta=+1; HRR primitive upgrade."
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "CERT_CHAIN_GRADE",
            "cert_status": "chain_grade",
            "cert_class": "pre_reg_pass",
            "verdict": (
                "HARD_PASS_CHAIN_GRADE_skunkworks_HRR_primitive_upgrade_3seeds_"
                "11_13_19_n_subset_450_each_N_512_perm_acc_1p0_ALL_FHRR_per_seed_"
                "0p0533_0p0644_0p0711_cv_0p1166_real_seed_variance_at_chance_"
                "floor_lift_mean_0p9371_cv_0p0078_real_seed_variance_discriminator_"
                "gap_93p7pct_NOT_by_construction_saturation_FHRR_baseline_HONESTLY_"
                "FAILS_at_same_envelope_perm_cyclic_shift_cleanup_rescues_same_"
                "role_collision_substrate_HRR_tier_extends_by_1_primitive_"
                "composes_with_Stage_2_FREQ_ROUTED_DEEPER_MULTIPLICATIVE_LEVER"
            ),
            "cell_commit": CELL_2_5_COMMIT,
            "metrics_path": (
                "data/exp_substrate_permutation_binding_multiocc_v2_full/metrics.json"
            ),
            "notes_path": NOTES_PATH,
            "verified_off_data": (
                "Cert-owner read aggregate.perm_per_seed + fhrr_per_seed + "
                "lift_per_seed directly. perm_per_seed=[1.0, 1.0, 1.0] cv=0. "
                "fhrr_per_seed=[0.0533, 0.0644, 0.0711] mean 0.0629 stdev "
                "0.0073 recomputed cv 0.1166 (cell-reported cv=0 is for "
                "aggregate.fhrr_acc_mean which is a different stat; per-seed "
                "FHRR cv is 0.1166). lift_per_seed=[0.9467, 0.9356, 0.9289] "
                "mean 0.9371 cv 0.0078. Discriminator gap 1.0-0.0629=0.9371. "
                "n_subset=450 per seed verified all 3. N=512 verified. "
                "FHRR baseline near chance floor 1/20=0.05 (multi-occ candidate "
                "pool typical 20). Real seed variance in FHRR baseline + lift "
                "confirms mechanism is NOT by-construction-saturation."
            ),
            "honest_scope": (
                "Chain-grade for permutation-indexed binding multi-occurrence "
                "rescue at N=512 d=512 n_subset=450 3 seeds. DOES show perm-"
                "indexed binding achieves 100% multi-occ recall while FHRR "
                "achieves chance-floor (0.063). DOES show FHRR baseline has "
                "honest seed variance (cv=0.12) at floor. DOES NOT test at "
                "larger N (capacity scaling not measured). DOES NOT compose "
                "with non-FHRR encoders. DOES NOT test n_subset > 450 "
                "(capacity cliff not measured). DOES NOT test with structured "
                "(non-random) value-vectors."
            ),
            "n_seeds": 3,
            "seeds": [11, 13, 19],
            "N": 512,
            "d": 512,
            "n_subset_per_seed": 450,
            "perm_acc_mean": 1.0,
            "perm_acc_cv": 0.0,
            "fhrr_acc_mean": 0.0629,
            "fhrr_acc_cv_recomputed": 0.1166,
            "fhrr_per_seed": [0.0533, 0.0644, 0.0711],
            "lift_mean": 0.9371,
            "lift_cv": 0.0078,
            "lift_per_seed": [0.9467, 0.9356, 0.9289],
            "discriminator_gap_absolute": 0.9371,
            "Q_discipline_check": {
                "perm_at_ceiling": True,
                "FHRR_baseline_real_seed_variance": True,
                "FHRR_cv_recomputed": 0.1166,
                "by_construction_saturation": False,
                "real_discriminator_gap": True,
            },
            "pre_reg_bands": {
                "HP_PERM": ">=0.95 (PASS 1.0)",
                "HP_FHRR_MAX": "<=0.10 (PASS 0.063)",
                "HP_LIFT": ">=0.85 (PASS 0.9371 +10% margin)",
                "HP_CV": "<=0.05 (PASS lift cv=0.0078)",
                "HARD_FAIL_PERM": "<0.70 (clear; 1.0)",
            },
            "mechanism_summary": (
                "Cyclic-shift inverse-permutation per occurrence index "
                "rescues FHRR same-role multi-occurrence collision. Same "
                "envelope (N, d, encoder) as FHRR; different binding primitive."
            ),
            "strategic_role": (
                "Substrate basis HRR-tier extends by 1 chain-grade primitive. "
                "Substrate now has 2 HRR-family mechanisms: standard FHRR + "
                "permutation-indexed binding. Composes anywhere FHRR fails "
                "to same-role collision."
            ),
            "elapsed_s": 1.22,
            "run_mode": "full",
            "zero_llm_calls_at_inference": True,
            "composes_with_potential": [
                "Stage_2_FREQ_ROUTED_DEEPER",
                "Stage_2_MULTIPLICATIVE_LEVER",
            ],
            "cites": [
                "Fix_28_verify_per_arm_metrics_per_seed_direct_recompute",
                "Q_discipline_FHRR_baseline_real_seed_variance_proves_not_BCS",
                "HRR_primitive_upgrade_substrate_basis_extends",
                "Director_routed_batch_2026-06-25_tier_ruling_5cell",
            ],
            "atomized_by": ATOMIZED_BY,
            "atomized_date": "2026-06-25",
            "era": "comprehensive_program_phase3_glassbox",
        },
    )


# ============================================================================
# CELL 5: measured_mechanism (NL never cliffs; extension=1.0 = saturated metric)
# ============================================================================

def build_cell_5_b_delta_readout_lever_transfer_v2_full_MM() -> Atom:
    return Atom(
        id=(
            "T3/EXP_substrate_b_delta_readout_lever_transfer_v2_full_"
            "measured_mechanism_NL_never_cliffs_extension_saturated_metric"
        ),
        name=(
            "b_delta readout lever transfer v2 full -- MEASURED_MECHANISM "
            "(nonlinear-readout STAYS at 1.0 across M=64..1024 BOTH tasks; "
            "linear cliffs M=256->512 bipolar / M=128->256 continuous proves "
            "mechanism real; extension=1.0 is saturated metric (lin_high=0 + "
            "nl_high=1) NOT measure of finite extension; UPPER bound of NL "
            "capacity NOT measured)"
        ),
        description=(
            "Nonlinear-readout lever transfer test for capacity extension on "
            "TWO value-types (bipolar + continuous; both uniform keys). 3 "
            "seeds [11, 13, 19] N=1024 M_grid=[64, 128, 256, 512, 1024] "
            "beta=40 tuned both tasks. Cell self-verdict HARD_PASS_CHAIN_GRADE. "
            "Cert-owner ruling: MEASURED_MECHANISM (saturation-metric override; "
            "NL capacity upper bound unmeasured).\n\n"
            "PER-SEED PER-TASK PER-M (independently recomputed all 3 seeds):\n"
            "  Bipolar:    lin=[1.0, 1.0, 1.0, 0.0~0.002, 0.0] at M=[64..1024]\n"
            "              nl=[1.0, 1.0, 1.0, 1.0, 1.0] (NL stays 1.0)\n"
            "  Continuous: lin=[1.0, 1.0, ~0.20, 0.0, 0.0] at M=[64..1024]\n"
            "              nl=[1.0, 1.0, 1.0, 1.0, 1.0] (NL stays 1.0)\n"
            "  extension_bipolar = 1.0 ALL seeds\n"
            "  extension_continuous = 1.0 ALL seeds\n"
            "  all_cliff_bipolar = True; all_cliff_continuous = True\n\n"
            "BAND PLACEMENT (cell pre-reg bands):\n"
            "  HP_LIFT_BOTH: >=0.4; measured 1.0/1.0 (PASS saturated)\n"
            "  HP_CV: <=0.07; measured 0.0 (PASS saturated)\n"
            "  HARD_FAIL_LIFT_BOTH: <0.20 (clear; not failing)\n\n"
            "Q-DISCIPLINE / EXTENSION METRIC OVERRIDE:\n"
            "  extension formula = (nl_high - lin_high) / (lin_low - lin_high)\n"
            "  measured = (1.0 - 0.0) / (1.0 - 0.0) = 1.0\n"
            "  nl_high = 1.0 means nonlinear NEVER cliffs in M sweep [64, 1024]\n"
            "  extension = 1.0 is the MAX-POSSIBLE value of this metric given "
            "lin cliffed (1->0) AND nl didn't (1 at high M); does NOT mean "
            "nonlinear has infinite capacity; means we never measured nl cliff.\n"
            "  Linear baseline IS real (cleanly cliffs M=256->512 bipolar, "
            "M=128->256 continuous; bipolar M=512 lin=0.0~0.002 then M=1024 "
            "lin=0.0; continuous M=256 lin~0.20 then M=512 lin=0).\n"
            "  The bound: nonlinear holds at M=1024 with N=1024 (effective "
            "ratio M/N=1.0 with linear cliffing at M/N=0.5 bipolar, M/N=0.25 "
            "continuous). At least 8x lift in bipolar (linear capacity ~128 "
            "vs nonlinear at-least 1024). 4x lift in continuous (linear ~256 "
            "vs nonlinear at-least 1024).\n"
            "  UPPER bound: NL capacity > 1024 patterns at N=1024 -- "
            "MAGNITUDE NOT MEASURED.\n\n"
            "DIRECTOR FRAMING CORRECTION (confirmed by exp_dev pre-VET):\n"
            "  Director task headline '+53pp clustered @M256, +100pp uniform "
            "@M64' was STALE 2026-06-18 metrics. The 2026-06-25 v2 inherits "
            "the corrected mechanism (bipolar/continuous, BOTH uniform keys, "
            "noise model fixed). The OLD framing's specific magnitudes do NOT "
            "transfer. The v2 mechanism IS the corrected one; old strategic-"
            "significance numerics should be discarded.\n\n"
            "ENVELOPE (load-bearing):\n"
            "  N = 1024 (substrate width)\n"
            "  M tested in {64, 128, 256, 512, 1024} (max M = N)\n"
            "  beta = 40 tuned both tasks\n"
            "  noise = 0.15 (sqrt-N normalized)\n"
            "  bipolar AND continuous value-types both tested with uniform keys\n"
            "  metrics_source = measured_torch_cpu\n\n"
            "STRATEGIC ROLE: nonlinear-readout-capacity-lever is a real "
            "primitive bound; chain-grade requires M >> N to find nl cliff. "
            "MM is honest characterization of the lever at M<=N regime.\n\n"
            "REVIVAL PATH (v3 design):\n"
            "  Sweep M up to N*4 or N*8 (4096..8192 at N=1024) to find "
            "nonlinear cliff; only then can a genuine finite-extension "
            "chain-grade claim be made.\n\n"
            "TIER: MEASURED_MECHANISM; delta=0; nonlinear-readout-capacity-"
            "lever proven bound at M<=N; upper bound unmeasured."
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "MEASURED_MECHANISM",
            "cert_status": "measured_mechanism",
            "cert_class": "mechanism_characterization",
            "verdict": (
                "MEASURED_MECHANISM_skunkworks_NL_never_cliffs_saturation_metric_"
                "override_3seeds_11_13_19_N_1024_M_grid_64_128_256_512_1024_"
                "beta_40_bipolar_lin_cliffs_M_256_to_512_nl_stays_1p0_continuous_"
                "lin_cliffs_M_128_to_256_nl_stays_1p0_extension_1p0_BOTH_tasks_"
                "is_max_possible_metric_value_given_lin_cliffed_nl_did_not_NOT_"
                "infinite_capacity_just_unmeasured_upper_bound_at_least_8x_lift_"
                "bipolar_4x_lift_continuous_chain_grade_requires_M_much_larger_"
                "than_N_director_stale_2026_06_18_magnitudes_corrected_inherited_"
                "v1_mechanism_substrate_capacity_lever_primitive_real_bound"
            ),
            "cell_commit": CELL_2_5_COMMIT,
            "metrics_path": (
                "data/exp_substrate_b_delta_readout_lever_transfer_v2_full/"
                "metrics.json"
            ),
            "notes_path": NOTES_PATH,
            "verified_off_data": (
                "Cert-owner read per_seed.grid + capacity_bipolar + "
                "capacity_continuous directly for all 3 seeds. Bipolar grid "
                "(all seeds identical or near-identical): lin at M=[64..1024] = "
                "[1.0, 1.0, 1.0, 0.0~0.002, 0.0]; nl at M=[64..1024] = "
                "[1.0, 1.0, 1.0, 1.0, 1.0]. Continuous grid (all seeds): "
                "lin at M=[64..1024] = [1.0, 1.0, ~0.20, 0.0, 0.0]; nl = "
                "[1.0, 1.0, 1.0, 1.0, 1.0]. capacity_bipolar.extension = 1.0 "
                "all seeds via formula (nl_high - lin_high) / (lin_low - "
                "lin_high) = (1-0)/(1-0) = 1.0 (saturated metric). Linear "
                "cliffs cleanly verified at bipolar M=512 lin=0.0~0.002 and "
                "M=1024 lin=0; continuous M=256 lin~0.20 and M=512 lin=0. "
                "Nonlinear at 1.0 throughout proven by per-seed grid read. "
                "beta_tuned=40 both tasks all seeds. metrics_source="
                "measured_torch_cpu. noise=0.15."
            ),
            "honest_scope": (
                "MM in M<=N regime at N=1024 beta=40 noise=0.15 3 seeds. "
                "DOES show nonlinear-readout HOLDS at 1.0 through M=1024 "
                "while linear cliffs at M=256 (bipolar) and M=128 (continuous). "
                "DOES show >= 8x lift in bipolar and >= 4x lift in continuous "
                "(linear capacity vs nonlinear at-least-N). DOES NOT measure "
                "nonlinear cliff (would require M >> N). DOES NOT chain-grade "
                "the finite-extension magnitude claim. DOES NOT test other "
                "noise levels. DOES NOT test other key-types (already tests "
                "uniform-keys BOTH bipolar and continuous values)."
            ),
            "n_seeds": 3,
            "seeds": [11, 13, 19],
            "N": 1024,
            "M_grid": [64, 128, 256, 512, 1024],
            "beta_tuned": 40.0,
            "noise": 0.15,
            "tasks": ["bipolar", "continuous"],
            "extension_bipolar_per_seed": [1.0, 1.0, 1.0],
            "extension_continuous_per_seed": [1.0, 1.0, 1.0],
            "linear_cliff_bipolar_M": 512,
            "linear_cliff_continuous_M": 256,
            "nonlinear_holds_through_M": 1024,
            "lift_bipolar_at_least": 8,
            "lift_continuous_at_least": 4,
            "Q_discipline_check": {
                "extension_at_metric_ceiling_1p0": True,
                "nl_never_cliffs_in_sweep": True,
                "extension_inflates_via_saturation_lin_high_0_nl_high_1": True,
                "upper_bound_NL_capacity_unmeasured": True,
                "by_construction_saturation_partial": True,
            },
            "pre_reg_bands": {
                "HP_LIFT_BOTH": ">=0.4 (PASS 1.0 saturated)",
                "HP_CV": "<=0.07 (PASS 0.0 saturated)",
                "HARD_FAIL_LIFT_BOTH": "<0.20 (clear)",
            },
            "director_framing_error_corrected": (
                "Director task headline '+53pp clustered @M256, +100pp uniform "
                "@M64' was STALE 2026-06-18 metrics. The 2026-06-25 v2 inherits "
                "corrected mechanism (bipolar/continuous BOTH uniform keys); "
                "old specific magnitudes do not transfer."
            ),
            "revival_path_requirements": {
                "M_sweep_extension": "M up to N*4 or N*8 (4096..8192 at N=1024)",
                "find_nonlinear_cliff": "for genuine finite-extension chain-grade",
                "consider_other_noise_levels": "robustness of NL ceiling",
            },
            "strategic_role": (
                "Substrate nonlinear-readout-capacity-lever primitive: real "
                "bound at M<=N (>=8x bipolar lift, >=4x continuous lift). "
                "Chain-grade requires M >> N to find NL cliff."
            ),
            "elapsed_s": 3.48,
            "run_mode": "full",
            "metrics_source": "measured_torch_cpu",
            "cites": [
                "Fix_28_verify_per_arm_metrics_per_seed_direct_recompute",
                "Q_discipline_extension_metric_saturation_override",
                "verify_the_referent_director_stale_magnitudes_corrected",
                "Director_routed_batch_2026-06-25_tier_ruling_5cell",
            ],
            "atomized_by": ATOMIZED_BY,
            "atomized_date": "2026-06-25",
            "era": "comprehensive_program_phase3_glassbox",
        },
    )


# ============================================================================
# safe_add_with_ledger helper -- mirrors prior tier-ruling tool pattern
# ============================================================================

def safe_add_with_ledger(
    atom: Atom,
    *,
    source: str,
    note: str,
    notes_path: str,
    metrics_path: str,
    verdict_text: str,
    atom_id_full: str,
    cell_commit: str,
    cert_status: str,
):
    ps = PartitionedStore(STORE_ROOT)
    qid = f"{atom.corpus.value}::{atom.id}"
    if ps.get_atom(qid) is not None:
        print(f"  SKIP (idempotent): {atom.id} already present.")
    else:
        print(f"  ADDING atom: {atom.id}")
        ps.add_atom(atom, source=source, note=note)
        ps2 = PartitionedStore(STORE_ROOT)
        atoms = list(ps2.all_atoms())
        found = next((a for a in atoms if a.id == atom.id), None)
        if found is None:
            print("  FAIL: atom not found post-add")
            return (False, None)
        md = found.metadata or {}
        expected_pq = (atom.metadata or {}).get("provenance_quality")
        if md.get("provenance_quality") != expected_pq:
            print(f"  FAIL: pq mismatch (expected {expected_pq}, got {md.get('provenance_quality')})")
            return (False, None)
        print(f"  PASS: round-trip OK (pq={expected_pq})")

    ps_live = PartitionedStore(STORE_ROOT)
    live_cert = sum(
        1 for a in ps_live.all_atoms()
        if (a.metadata or {}).get("provenance_quality") == "CERT_CHAIN_GRADE"
    )

    if cert_status == "chain_grade":
        row = build_chain_grade_ruling_row(
            atom_id=atom_id_full,
            cell_commit=cell_commit,
            verdict=verdict_text,
            notes_path=notes_path,
            metrics_path=metrics_path,
            atomized_by=ATOMIZED_BY,
            note=note,
        )
        expected_pre = live_cert
        expected_post = live_cert
    elif cert_status == "honest_negative":
        row = build_honest_negative_row(
            atom_id=atom_id_full,
            cell_commit=cell_commit,
            verdict=verdict_text,
            notes_path=notes_path,
            metrics_path=metrics_path,
            atomized_by=ATOMIZED_BY,
            note=note,
        )
        expected_pre = live_cert
        expected_post = live_cert
    elif cert_status == "measured_mechanism":
        row = build_measured_mechanism_row(
            atom_id=atom_id_full,
            cell_commit=cell_commit,
            verdict=verdict_text,
            notes_path=notes_path,
            metrics_path=metrics_path,
            atomized_by=ATOMIZED_BY,
            note=note,
        )
        expected_pre = live_cert
        expected_post = live_cert
    else:
        print(f"  FAIL: unknown cert_status {cert_status!r}")
        return (False, None)

    print(
        f"  appending cert-ledger row (op={row['op']} status={row['cert_status']} "
        f"delta={row['cert_increment_delta']})"
    )
    try:
        h = append_cert_ledger_row(
            row,
            expected_cert_n_pre=expected_pre,
            expected_cert_n_post=expected_post,
        )
        print(f"  row_hash={h}")
        return (True, h)
    except Exception as e:
        print(f"  FAIL: ledger append errored: {e}")
        return (False, None)


# ============================================================================
# Main plan
# ============================================================================

# (builder, notes_path, metrics_path, verdict_text, cell_commit, ledger_note, cert_status)
ATOM_PLAN = [
    (
        build_cell_1_partition_routing_10M_chain_grade,
        NOTES_PATH,
        "data/exp_substrate_partition_routing_10M_full_v2/metrics.json",
        (
            "HARD_PASS_PARTIAL_AT_M_1M_skunkworks_chain_grade_at_M_100k_"
            "with_proven_bound_at_M_1M_partition_size_2000_inherits_cell_B_"
            "dense_KV_envelope_routing_acc_1p0_saturated_routed_recall_real_"
            "variance_substrate_product_KG_extends_to_1M_class_tiered_atom"
        ),
        CELL1_COMMIT,
        (
            "chain_grade_partition_routing_10M_full_v2_M_100k_routed_0p9697_"
            "cv_0p0442_M_1M_routed_0p95_cv_0p0114_partition_size_2000_inherits_"
            "Cell_B_dense_KV_envelope_routing_acc_1p0_saturated_routed_recall_"
            "real_seed_variance_flat_strictly_degrades_0p9_0p7305_0p5139_"
            "substrate_product_KG_extends_to_1M_class_via_partition_routing"
        ),
        "chain_grade",
    ),
    (
        build_cell_2_refuse_gate_nonlinear_readout_v2_full_MM,
        NOTES_PATH,
        "data/exp_substrate_refuse_gate_nonlinear_readout_v2_full/metrics.json",
        (
            "MEASURED_MECHANISM_skunkworks_saturation_override_synthetic_"
            "absent_regime_42pct_270_ops_saturate_accept_drop_zero_universal_"
            "real_bge_held_out_required_for_chain_grade_refuse_gate_count_"
            "unchanged_3_chain_grade_plus_1_MM"
        ),
        CELL_2_5_COMMIT,
        (
            "measured_mechanism_refuse_gate_nonlinear_readout_v2_full_3seeds_"
            "11_13_19_synthetic_paraphrase_noise_0p10_42pct_ops_saturate_at_"
            "gap_refuse_0p95_accept_drop_0p0_every_cell_rich_beta_c_curve_"
            "mechanism_real_chain_grade_requires_real_bge_held_out_refuse_"
            "gate_count_unchanged"
        ),
        "measured_mechanism",
    ),
    (
        build_cell_3_distill_verify_operator_equivalence_v2_full_HN,
        NOTES_PATH,
        (
            "data/exp_substrate_distill_verify_operator_equivalence_v2_full/"
            "metrics.json"
        ),
        (
            "MIDDLE_BAND_PARTIAL_skunkworks_honest_negative_below_HP_plus_cv_"
            "outside_rail_DIRECTOR_FRAMING_CORRECTION_1_NAMED_total_not_6_named_"
            "axis_structurally_untestable_revival_v3_NAMED_corpus_expansion"
        ),
        CELL_2_5_COMMIT,
        (
            "honest_negative_distill_verify_operator_equivalence_v2_full_"
            "3seeds_11_13_19_held_distill_per_seed_0p6667_1p0_0p6667_mean_"
            "0p7778_below_HP_0p80_cv_0p20_above_rail_0p07_2p9x_corpus_1_NAMED_"
            "TOTAL_not_6_director_framing_corrected_named_axis_untestable_"
            "fold_overlap_seeds_share_1_to_2_held_groups_methodology_weakness_"
            "revival_v3_NAMED_corpus_expansion_to_6_disjoint_folds"
        ),
        "honest_negative",
    ),
    (
        build_cell_4_permutation_binding_multiocc_v2_full_chain_grade,
        NOTES_PATH,
        (
            "data/exp_substrate_permutation_binding_multiocc_v2_full/metrics.json"
        ),
        (
            "HARD_PASS_CHAIN_GRADE_skunkworks_HRR_primitive_upgrade_FHRR_"
            "baseline_real_seed_variance_proves_not_BCS_discriminator_gap_"
            "93p7pct_cyclic_shift_cleanup_rescues_same_role_collision_substrate_"
            "HRR_tier_extends_by_1_primitive_composes_with_Stage_2"
        ),
        CELL_2_5_COMMIT,
        (
            "chain_grade_permutation_binding_multiocc_v2_full_3seeds_11_13_19_"
            "n_subset_450_N_512_perm_1p0_FHRR_0p0629_real_seed_variance_per_"
            "seed_0p0533_0p0644_0p0711_FHRR_cv_0p1166_lift_0p9371_cv_0p0078_"
            "discriminator_gap_93p7pct_NOT_by_construction_saturation_HRR_"
            "primitive_upgrade_composes_with_Stage_2_FREQ_ROUTED_DEEPER_"
            "MULTIPLICATIVE_LEVER"
        ),
        "chain_grade",
    ),
    (
        build_cell_5_b_delta_readout_lever_transfer_v2_full_MM,
        NOTES_PATH,
        (
            "data/exp_substrate_b_delta_readout_lever_transfer_v2_full/"
            "metrics.json"
        ),
        (
            "MEASURED_MECHANISM_skunkworks_NL_never_cliffs_extension_metric_"
            "saturation_override_director_stale_2026_06_18_magnitudes_corrected_"
            "NL_capacity_upper_bound_unmeasured_at_least_8x_bipolar_4x_continuous"
        ),
        CELL_2_5_COMMIT,
        (
            "measured_mechanism_b_delta_readout_lever_transfer_v2_full_3seeds_"
            "11_13_19_N_1024_M_grid_64_to_1024_beta_40_bipolar_lin_cliffs_M_"
            "256_to_512_continuous_lin_cliffs_M_128_to_256_NL_stays_1p0_through_"
            "M_1024_extension_1p0_BOTH_tasks_is_max_possible_metric_value_not_"
            "infinite_capacity_NL_upper_bound_unmeasured_at_least_8x_bipolar_"
            "4x_continuous_director_stale_magnitudes_corrected_revival_v3_M_4N_8N"
        ),
        "measured_mechanism",
    ),
]


def main() -> int:
    if "--apply" not in sys.argv:
        print("DRY: pass --apply to mutate Store + ledger.")
        print(f"Plan: {len(ATOM_PLAN)} atomizations "
              f"(2 chain-grade + 2 measured_mechanism + 1 honest_negative)")
        for i, item in enumerate(ATOM_PLAN, 1):
            builder, _, _, _, _, _, cert_status = item
            a = builder()
            delta = "+1" if cert_status == "chain_grade" else "+0"
            print(f"  {i}. {a.corpus.value}::{a.id}  "
                  f"pq={a.metadata['provenance_quality']}  delta={delta}")
        return 0

    if CELL1_COMMIT == "PENDING_CELL1_METRICS_COMMIT":
        print("ABORT: CELL1_COMMIT placeholder still in tool source.")
        print("Update CELL1_COMMIT after path-scoped commit of Cell 1 metrics.json")
        return 2

    ps = PartitionedStore(STORE_ROOT)
    atoms_pre = list(ps.all_atoms())
    n_atoms_pre = len(atoms_pre)
    cert_pre = sum(
        1 for a in atoms_pre
        if (a.metadata or {}).get("provenance_quality") == "CERT_CHAIN_GRADE"
    )
    print(f"A5-PRE: n_atoms={n_atoms_pre} CERT N={cert_pre}")
    expected_delta_atoms = len(ATOM_PLAN)
    expected_delta_cert = sum(
        1 for item in ATOM_PLAN if item[6] == "chain_grade"
    )
    print(f"Expected delta: atoms +{expected_delta_atoms}; CERT +{expected_delta_cert}")
    print()

    row_hashes = []
    for i, item in enumerate(ATOM_PLAN, 1):
        builder, notes_path, metrics_path, verdict_text, cell_commit, ledger_note, cert_status = item
        atom = builder()
        atom_id_full = f"{atom.corpus.value}::{atom.id}"
        delta = "+1" if cert_status == "chain_grade" else "+0"
        print(f"=== {i}/{len(ATOM_PLAN)}: {atom_id_full}")
        print(f"   pq={atom.metadata['provenance_quality']} cert_status={cert_status} delta={delta}")
        ok, h = safe_add_with_ledger(
            atom,
            source=ATOMIZED_BY,
            note=ledger_note,
            notes_path=notes_path,
            metrics_path=metrics_path,
            verdict_text=verdict_text,
            atom_id_full=atom_id_full,
            cell_commit=cell_commit,
            cert_status=cert_status,
        )
        if not ok:
            print(f"ABORT at item {i}")
            return 1
        row_hashes.append((atom.id, h))
        print()

    ps_post = PartitionedStore(STORE_ROOT)
    atoms_post = list(ps_post.all_atoms())
    n_atoms_post = len(atoms_post)
    cert_post = sum(
        1 for a in atoms_post
        if (a.metadata or {}).get("provenance_quality") == "CERT_CHAIN_GRADE"
    )
    print("=" * 72)
    print(f"A5-POST: n_atoms={n_atoms_post} (delta +{n_atoms_post - n_atoms_pre}, expected +{expected_delta_atoms})")
    print(f"         CERT N={cert_post} (delta +{cert_post - cert_pre}, expected +{expected_delta_cert})")
    print("=" * 72)
    print("Row hashes:")
    for aid, h in row_hashes:
        print(f"  {h}  {aid}")

    if (n_atoms_post - n_atoms_pre) != expected_delta_atoms:
        print("WARNING: atom count drift")
        return 1
    if (cert_post - cert_pre) != expected_delta_cert:
        print("WARNING: CERT count drift")
        return 1
    print("A5 invariants PRESERVED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
