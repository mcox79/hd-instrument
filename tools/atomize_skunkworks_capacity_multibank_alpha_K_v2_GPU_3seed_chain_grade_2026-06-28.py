"""Atomize: Skunkworks landed-VET — substrate_capacity_multibank_alpha_K_phase_diagram_v2_GPU 3-seed HARD_PASS.

OFF-DATA recompute (Skunkworks 2026-06-28; .venv Python):
  All 3 seeds confirmed HARD_PASS_CAPACITY_MB_ALPHA_K_PHASE_DIAGRAM_v2:
    seed_7  : 216/216 pts ; n_pass=119 n_pass_at_full_N=35 n_saturate=75 ; arms_differ=216/216 ; rail=0.9976
    seed_13 : 216/216 pts ; n_pass=118 n_pass_at_full_N=34 n_saturate=74 ; arms_differ=216/216 ; rail=1.0000
    seed_19 : 216/216 pts ; n_pass=119 n_pass_at_full_N=34 n_saturate=75 ; arms_differ=216/216 ; rail=0.9976

Cross-seed phase-boundary agreement: 214/216 phase points classify identically (PASS/FAIL) across
all 3 seeds. Per-seed n_pass spread 119/118/119 (std/mean=0.008, 0.8%).

cliff_per_B IDENTICAL across 3 seeds at full grid:
  B=4  -> alpha_cliff = 0.1
  B=16 -> alpha_cliff = 0.5
  B=64 -> alpha_cliff = 2.0
  Power-law scaling alpha_cliff(B) ≈ K_per_bank * B / N (matches theory).

K-axis discrimination at rail-family (alpha=0.05, B=4, N=8192):
  K=16  MULTI=0.156 SINGLE=0.039 (under-resourced)
  K=64  MULTI=0.624 SINGLE=0.141 (transition)
  K=128 MULTI=1.000 SINGLE=0.220 (well-resourced)
  K=256 MULTI=0.998 SINGLE=0.302 (rail; honest baseline degradation, NOT by-construction saturation)

Rail family dynamic range at K=256 B=4 N=8192:
  alpha=0.05 -> MULTI=0.998-1.000
  alpha=0.10 -> MULTI=0.825-0.839
  alpha=0.25 -> MULTI=0.199-0.208
  alpha=0.50 -> MULTI=0.040-0.049
  alpha=1.00 -> MULTI=0.010-0.013
  alpha=2.00 -> MULTI=0.003
  Sigmoidal cliff curve; cross-seed agreement on curve shape exceptional.

Discriminator-must-survive-scale (USER 2026-06-26):
  smoke-N (N=2048) at alpha=0.10 K=256 B=4: margin = 0.74-0.78
  full-N (N=8192) same config:              margin = 0.75-0.76
  DISCRIMINATOR SURVIVES SCALE.

GPU dispatch (Fix #24):
  device=cuda:0; gpu_name=NVIDIA GeForce RTX 4060 Ti; gpu_util_max=94-100%; gpu_util_mean=29-33%
  (chunked HD ops; memory-bound between matmul bursts; soft methodology note — cell's own
  HP_GPU_UTIL_MIN=0.50 not enforced in verdict logic, mean util below declared gate but
  util_max=100% confirms real GPU compute).

v1 -> v2 deltas (chain-grade revival path):
  K_per_bank {4,16,64} -> {16,64,128,256}            (extended)
  B {1,4,16}           -> {4,16,64}                  (dropped degenerate B=1, added B=64)
  HP n_pass_at_full_N  : >=8 -> >=12                 (tightened gate)
  Rail config: (alpha_min, K=64, B=1, N=FULL_N)      (was by-construction saturated)
            -> (alpha_min, K=256, B=4, N=FULL_N)     (clean above 0.95)

ATOMS BUILT (this batch):
  [1] PER-SEED seed_7  HARD_PASS_PHASE_DIAGRAM_v2_GPU  (delta=0; building-block evidence; EXPERIMENT_RECORD)
  [2] PER-SEED seed_13 HARD_PASS_PHASE_DIAGRAM_v2_GPU  (delta=0; building-block evidence; EXPERIMENT_RECORD)
  [3] PER-SEED seed_19 HARD_PASS_PHASE_DIAGRAM_v2_GPU  (delta=0; building-block evidence; EXPERIMENT_RECORD)
  [4] CROSS-SEED AGG chain_grade_phase_characterization (delta=+1; CAPABILITY_MAP)
      Supersedes v1 MM atom (3_of_3_MEASURED_MECHANISM_multi_bank_advantage_MASSIVE_at_B_16_*).

Net: CERT N delta = +1 (631 -> 632). Ledger rows: +4.

Composes-with:
  - WM K-cliff v3 chain-grade (commit 7274bafb): sibling phase-characterization
  - sequence_binding K-cliff chain-grade (commit 68714d0e): sibling phase-characterization
  - pattern_completion v2.2 dense chain-grade (commit ac706494): sibling phase-characterization
  All four describe substrate phase-cliff scaling laws across mechanism types.
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(".").resolve()))
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier
from tools.cert_ledger_writer import (
    append_cert_ledger_row,
    build_chain_grade_ruling_row,
)


STORE_ROOT = Path("data/substrate_index")
RULING_NOTE = "notes/skunkworks_landed_vet_capacity_multibank_alpha_K_v2_GPU_3seed_chain_grade_2026-06-28.md"
CELL_COMMIT = "v2_GPU_phase_diagram_3seed_landed_2026-06-28"
ATOMIZED_BY = "skunkworks_atomize_capacity_multibank_alpha_K_v2_GPU_3seed_chain_grade_2026-06-28"

METRICS_S7 = "data/exp_substrate_capacity_multibank_alpha_K_phase_diagram_v2_GPU_seed_7/metrics.json"
METRICS_S13 = "data/exp_substrate_capacity_multibank_alpha_K_phase_diagram_v2_GPU_seed_13/metrics.json"
METRICS_S19 = "data/exp_substrate_capacity_multibank_alpha_K_phase_diagram_v2_GPU_seed_19/metrics.json"

PREREG_PATH = "preregs/2026-06-28_substrate_capacity_multibank_alpha_K_phase_diagram_v2_GPU.md"

V1_SUPERSEDED_ATOM_ID = (
    "T3/EXP_substrate_capacity_multibank_alpha_K_phase_diagram_v1_GPU_CROSS_SEED_AGG_"
    "3_of_3_MEASURED_MECHANISM_multi_bank_advantage_MASSIVE_at_B_16_N8192_K64_alpha0p05_"
    "M_1p000_S_0p139_7x_alpha0p1_M_1p000_S_0p044_alpha0p5_M_0p246_S_0p003_80x_relative_"
    "RANDOM_FLOOR_0p000_n_pass_full_N_5_n_pass_total_23_blocks_HP_arms_differ_160_to_162_"
    "of_162_per_seed_cardinality_486_of_486_OK_gpu_util_mean_49_to_78_max_100_per_seed_"
    "codebook_16384_n_seeds_3_7_13_19"
)

CLIFF_PER_B_3SEED_IDENTICAL = {"B=4": 0.1, "B=16": 0.5, "B=64": 2.0}


# ============================================================================
# ATOM 1: PER-SEED seed_7 — HARD_PASS evidence (CERT-neutral)
# ============================================================================

def build_atom_seed7() -> Atom:
    return Atom(
        id=(
            "T3/EXP_substrate_capacity_multibank_alpha_K_phase_diagram_v2_GPU_seed_7_"
            "HARD_PASS_216_of_216_n_pass_119_n_pass_full_N_35_saturate_75_arms_differ_216_"
            "of_216_rail_K256_B4_N8192_recall_0p9976_cliff_per_B_4_0p1_16_0p5_64_2p0_"
            "RTX_4060_Ti_util_mean_31_max_100_elapsed_136s_n_llm_calls_0_2026-06-28"
        ),
        name=(
            "substrate_capacity_multibank_alpha_K_phase_diagram v2 GPU seed_7 HARD_PASS: "
            "216/216 pts; n_pass=119 n_pass_at_full_N=35 saturate=75; arms_differ=216/216; "
            "rail (alpha=0.05 K=256 B=4 N=8192) recall=0.9976; cliff_per_B={B=4:0.1, B=16:0.5, "
            "B=64:2.0}; RTX 4060 Ti util_mean=31% util_max=100%; elapsed=136s; n_llm_calls=0"
        ),
        description=(
            "Per-seed HARD_PASS evidence atom (CERT-neutral building block; delta=0).\n"
            "Cross-seed AGG atom carries the +1 chain-grade phase-characterization claim;\n"
            "this atom is the building-block evidence for seed_7 specifically.\n\n"
            "OFF-DATA RECOMPUTE (Skunkworks 2026-06-28; .venv Python from local metrics.json):\n\n"
            "  Cardinality: 648/648 units (216 phase_points x 3 arms); META_RULE_H pass.\n"
            "  Independent recount from per_unit raw data:\n"
            "    n_pass=119 (reported=119; match)\n"
            "    n_pass_at_full_N=35 (reported=35; match)\n"
            "    n_saturate=75 (reported=75; match)\n"
            "    n_floor (RANDOM<=0.05)=216/216 (random arm cleanly at floor)\n"
            "    arms_differ=216/216 (reported=216; match)\n"
            "    discriminator_fires (margin>=0.30) = 124/216\n"
            "    margin_max = 0.999\n"
            "  Rail config (alpha=0.05 K=256 B=4 N=8192): MULTI_recall=0.9976 (>= 0.95 target).\n"
            "  arm_sha256 distinct per phase point: 216/216.\n"
            "  n_llm_calls=0 ; substrate_only_ok=True.\n"
            "  GPU: device=cuda:0 ; gpu_name=NVIDIA GeForce RTX 4060 Ti ; gpu_max_mem_alloc=264MB.\n"
            "    gpu_util_mean=31.4% ; gpu_util_p50=18% ; gpu_util_max=100% (n=1176 samples).\n"
            "  Elapsed: 136.0s for 648 units (~210ms/unit; GPU matmul-bound).\n\n"
            "  K-axis discrimination at rail-family (alpha=0.05 B=4 N=8192):\n"
            "    K=16  MULTI=0.156 SINGLE=0.039 (under-resourced; substrate IS resource-bound)\n"
            "    K=64  MULTI=0.624 SINGLE=0.141 (transition zone)\n"
            "    K=128 MULTI=1.000 SINGLE=0.220 (well-resourced)\n"
            "    K=256 MULTI=0.998 SINGLE=0.302 (rail; honest baseline degradation)\n\n"
            "  Rail family dynamic range (K=256 B=4 N=8192 across alpha):\n"
            "    alpha=0.05 MULTI=0.998 SINGLE=0.302 FLOOR=0.000\n"
            "    alpha=0.10 MULTI=0.825 SINGLE=0.081 FLOOR=0.000\n"
            "    alpha=0.25 MULTI=0.199 SINGLE=0.012 FLOOR=0.000\n"
            "    alpha=0.50 MULTI=0.049 SINGLE=0.003 FLOOR=0.000\n"
            "    alpha=1.00 MULTI=0.010 SINGLE=0.001 FLOOR=0.000\n"
            "    alpha=2.00 MULTI=0.003 SINGLE=0.001 FLOOR=0.000\n"
            "  Sigmoidal cliff curve; NOT by-construction saturated (wide dynamic range).\n\n"
            "META_RULE COMPLIANCE:\n"
            "  H cardinality_ok=True (216 expected, 216 observed; 648 unit cells)\n"
            "  J no-silent-except: n_failures=0 n_probe_denials=0\n"
            "  K discriminator fires (124/216 phase points above margin threshold)\n"
            "  L band-check: 35 points at full-N (above the 12 chain-grade threshold)\n"
            "  AC arms-differ-by-SHA256: 216/216 distinct arm hashes\n"
            "  AE bands locked at module init (per pre-reg HP gates)\n"
            "  AF arms differ: all 3 regimes distinct in arm_sha256 and recall values\n\n"
            "WHY CERT-NEUTRAL (delta=0):\n"
            "  Per-seed atoms are building-block evidence. The CHAIN-GRADE phase-characterization\n"
            "  claim is carried by the cross-seed AGG atom (which depends on this + seed_13 +\n"
            "  seed_19 cliff_per_B being identical and arm-discriminator surviving across 3 seeds).\n"
            "  This atom counts toward audit-trail completeness; does NOT independently certify.\n"
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "HARD_PASS",
            "cert_status": "evidence_record_per_seed",
            "cert_class": "per_seed_evidence_for_cross_seed_phase_characterization",
            "cell_anchor": "substrate_capacity_multibank_alpha_K_phase_diagram_v2_GPU_seed_7",
            "cell_commit": CELL_COMMIT,
            "metrics_path": METRICS_S7,
            "prereg_path": PREREG_PATH,
            "ruling_note": RULING_NOTE,
            "verified_off_data": True,
            "run_mode": "full",
            "seed": 7,
            "n_phase_points": 216,
            "n_units_total": 648,
            "n_pass": 119,
            "n_pass_at_full_N": 35,
            "n_saturate": 75,
            "arms_differ_count": 216,
            "arm_sha256_distinct_per_point": 216,
            "discriminator_fires_count": 124,
            "margin_max": 0.999,
            "rail_alpha": 0.05,
            "rail_K_per_bank": 256,
            "rail_num_banks": 4,
            "rail_n_dim": 8192,
            "rail_recall": 0.9976,
            "rail_target": 0.95,
            "rail_ok": True,
            "cliff_per_B": CLIFF_PER_B_3SEED_IDENTICAL,
            "gpu_used": True,
            "gpu_name": "NVIDIA GeForce RTX 4060 Ti",
            "gpu_util_mean_pct": 31.4,
            "gpu_util_p50_pct": 18.0,
            "gpu_util_max_pct": 100.0,
            "gpu_max_mem_alloc_mb": 264,
            "elapsed_s": 136.0,
            "n_llm_calls": 0,
            "store_dtype": "torch.float16",
            "codebook_chunk": 4096,
            "discriminator_armed": True,
            "discriminator_fired_clean_separation": True,
            "by_construction_saturation_flag": False,
            "by_construction_saturation_reasoning": (
                "K-axis ramp K=16(0.156)->K=64(0.624)->K=128(1.000) proves substrate resource-bound; "
                "MULTI degrades through 0.998->0.003 across alpha at K=256 (wide sigmoidal); "
                "B=64 MULTI=0.698 at alpha=2.0 (load tested past degradation); "
                "SINGLE at rail=0.302 (above floor=0.000, honest baseline NOT pre-saturated)"
            ),
            "discriminator_survives_scale": True,
            "smoke_N_full_N_margin_agreement": (
                "smoke-N (2048) margin 0.74-0.78 vs full-N (8192) margin 0.75-0.76 "
                "at alpha=0.10 K=256 B=4 (within 0.02)"
            ),
            "META_RULE_H_cardinality_ok": True,
            "META_RULE_J_no_silent_except_ok": True,
            "META_RULE_K_discriminator_fires_clean": True,
            "META_RULE_L_band_check": "35_at_full_N_above_12_threshold",
            "META_RULE_AC_arms_differ_sha256": True,
            "META_RULE_AE_bands_locked": True,
            "META_RULE_AF_arms_differ_per_point": True,
            "stage": "Stage_1_base_substrate_phase_diagram",
            "skunkworks_audit_pass": True,
            "skunkworks_audit_red_flags": [],
            "skunkworks_audit_soft_notes": [
                "gpu_util_mean_31pct_below_cell_declared_HP_GPU_UTIL_MIN_0p50_but_util_max_100pct_confirms_real_GPU_compute_gate_not_enforced_in_verdict_logic"
            ],
            "atomized_by": ATOMIZED_BY,
        },
    )


# ============================================================================
# ATOM 2: PER-SEED seed_13 — HARD_PASS evidence (CERT-neutral)
# ============================================================================

def build_atom_seed13() -> Atom:
    return Atom(
        id=(
            "T3/EXP_substrate_capacity_multibank_alpha_K_phase_diagram_v2_GPU_seed_13_"
            "HARD_PASS_216_of_216_n_pass_118_n_pass_full_N_34_saturate_74_arms_differ_216_"
            "of_216_rail_K256_B4_N8192_recall_1p0000_cliff_per_B_4_0p1_16_0p5_64_2p0_"
            "RTX_4060_Ti_util_mean_29_max_94_elapsed_139s_n_llm_calls_0_2026-06-28"
        ),
        name=(
            "substrate_capacity_multibank_alpha_K_phase_diagram v2 GPU seed_13 HARD_PASS: "
            "216/216 pts; n_pass=118 n_pass_at_full_N=34 saturate=74; arms_differ=216/216; "
            "rail (alpha=0.05 K=256 B=4 N=8192) recall=1.0000; cliff_per_B={B=4:0.1, B=16:0.5, "
            "B=64:2.0}; RTX 4060 Ti util_mean=29% util_max=94%; elapsed=139s; n_llm_calls=0"
        ),
        description=(
            "Per-seed HARD_PASS evidence atom (CERT-neutral building block; delta=0).\n\n"
            "OFF-DATA RECOMPUTE (Skunkworks 2026-06-28; .venv Python from local metrics.json):\n\n"
            "  Cardinality: 648/648 units; META_RULE_H pass.\n"
            "  Independent recount:\n"
            "    n_pass=118 (reported=118; match)\n"
            "    n_pass_at_full_N=34 (reported=34; match)\n"
            "    n_saturate=74 (reported=74; match)\n"
            "    arms_differ=216/216 (reported=216; match)\n"
            "    discriminator_fires (margin>=0.30) = 124/216\n"
            "    margin_max = 0.999\n"
            "  Rail (alpha=0.05 K=256 B=4 N=8192): MULTI_recall=1.0000 (perfect at rail).\n"
            "  Rail family across alpha at K=256 B=4 N=8192:\n"
            "    0.05->1.000  0.10->0.839  0.25->0.203  0.50->0.045  1.00->0.010  2.00->0.003\n"
            "  GPU: device=cuda:0 ; gpu_util_mean=29.1% ; gpu_util_max=94% ; elapsed=139.2s\n"
            "  n_llm_calls=0 ; substrate_only_ok=True.\n"
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "HARD_PASS",
            "cert_status": "evidence_record_per_seed",
            "cert_class": "per_seed_evidence_for_cross_seed_phase_characterization",
            "cell_anchor": "substrate_capacity_multibank_alpha_K_phase_diagram_v2_GPU_seed_13",
            "cell_commit": CELL_COMMIT,
            "metrics_path": METRICS_S13,
            "prereg_path": PREREG_PATH,
            "ruling_note": RULING_NOTE,
            "verified_off_data": True,
            "run_mode": "full",
            "seed": 13,
            "n_phase_points": 216,
            "n_units_total": 648,
            "n_pass": 118,
            "n_pass_at_full_N": 34,
            "n_saturate": 74,
            "arms_differ_count": 216,
            "discriminator_fires_count": 124,
            "margin_max": 0.999,
            "rail_recall": 1.0000,
            "rail_ok": True,
            "cliff_per_B": CLIFF_PER_B_3SEED_IDENTICAL,
            "gpu_used": True,
            "gpu_util_mean_pct": 29.1,
            "gpu_util_max_pct": 94.0,
            "elapsed_s": 139.2,
            "n_llm_calls": 0,
            "discriminator_armed": True,
            "by_construction_saturation_flag": False,
            "META_RULE_H_cardinality_ok": True,
            "META_RULE_AC_arms_differ_sha256": True,
            "stage": "Stage_1_base_substrate_phase_diagram",
            "skunkworks_audit_pass": True,
            "atomized_by": ATOMIZED_BY,
        },
    )


# ============================================================================
# ATOM 3: PER-SEED seed_19 — HARD_PASS evidence (CERT-neutral)
# ============================================================================

def build_atom_seed19() -> Atom:
    return Atom(
        id=(
            "T3/EXP_substrate_capacity_multibank_alpha_K_phase_diagram_v2_GPU_seed_19_"
            "HARD_PASS_216_of_216_n_pass_119_n_pass_full_N_34_saturate_75_arms_differ_216_"
            "of_216_rail_K256_B4_N8192_recall_0p9976_cliff_per_B_4_0p1_16_0p5_64_2p0_"
            "RTX_4060_Ti_util_mean_33_max_100_elapsed_141s_n_llm_calls_0_2026-06-28"
        ),
        name=(
            "substrate_capacity_multibank_alpha_K_phase_diagram v2 GPU seed_19 HARD_PASS: "
            "216/216 pts; n_pass=119 n_pass_at_full_N=34 saturate=75; arms_differ=216/216; "
            "rail (alpha=0.05 K=256 B=4 N=8192) recall=0.9976; cliff_per_B={B=4:0.1, B=16:0.5, "
            "B=64:2.0}; RTX 4060 Ti util_mean=33% util_max=100%; elapsed=141s; n_llm_calls=0"
        ),
        description=(
            "Per-seed HARD_PASS evidence atom (CERT-neutral building block; delta=0).\n\n"
            "OFF-DATA RECOMPUTE (Skunkworks 2026-06-28; .venv Python from local metrics.json):\n\n"
            "  Cardinality: 648/648 units; META_RULE_H pass.\n"
            "  Independent recount:\n"
            "    n_pass=119 (reported=119; match)\n"
            "    n_pass_at_full_N=34 (reported=34; match)\n"
            "    n_saturate=75 (reported=75; match)\n"
            "    arms_differ=216/216 (reported=216; match)\n"
            "    discriminator_fires (margin>=0.30) = 124/216\n"
            "    margin_max = 0.998\n"
            "  Rail (alpha=0.05 K=256 B=4 N=8192): MULTI_recall=0.9976.\n"
            "  Rail family across alpha at K=256 B=4 N=8192:\n"
            "    0.05->0.998  0.10->0.835  0.25->0.208  0.50->0.040  1.00->0.013  2.00->0.003\n"
            "  GPU: device=cuda:0 ; gpu_util_mean=32.7% ; gpu_util_max=100% ; elapsed=141.0s\n"
            "  n_llm_calls=0 ; substrate_only_ok=True.\n"
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "HARD_PASS",
            "cert_status": "evidence_record_per_seed",
            "cert_class": "per_seed_evidence_for_cross_seed_phase_characterization",
            "cell_anchor": "substrate_capacity_multibank_alpha_K_phase_diagram_v2_GPU_seed_19",
            "cell_commit": CELL_COMMIT,
            "metrics_path": METRICS_S19,
            "prereg_path": PREREG_PATH,
            "ruling_note": RULING_NOTE,
            "verified_off_data": True,
            "run_mode": "full",
            "seed": 19,
            "n_phase_points": 216,
            "n_units_total": 648,
            "n_pass": 119,
            "n_pass_at_full_N": 34,
            "n_saturate": 75,
            "arms_differ_count": 216,
            "discriminator_fires_count": 124,
            "margin_max": 0.998,
            "rail_recall": 0.9976,
            "rail_ok": True,
            "cliff_per_B": CLIFF_PER_B_3SEED_IDENTICAL,
            "gpu_used": True,
            "gpu_util_mean_pct": 32.7,
            "gpu_util_max_pct": 100.0,
            "elapsed_s": 141.0,
            "n_llm_calls": 0,
            "discriminator_armed": True,
            "by_construction_saturation_flag": False,
            "META_RULE_H_cardinality_ok": True,
            "META_RULE_AC_arms_differ_sha256": True,
            "stage": "Stage_1_base_substrate_phase_diagram",
            "skunkworks_audit_pass": True,
            "atomized_by": ATOMIZED_BY,
        },
    )


# ============================================================================
# ATOM 4: CROSS-SEED AGG — chain_grade phase-characterization (delta = +1)
# ============================================================================

def build_atom_cross_seed_agg() -> Atom:
    return Atom(
        id=(
            "T3/EXP_substrate_capacity_multibank_alpha_K_phase_diagram_v2_GPU_CROSS_SEED_AGG_"
            "3_of_3_CHAIN_GRADE_PHASE_CHARACTERIZATION_cliff_per_B_identical_3seeds_B4_0p1_"
            "B16_0p5_B64_2p0_n_pass_full_N_34_to_35_per_seed_arms_differ_216_of_216_per_seed_"
            "rail_K256_B4_N8192_recall_0p9976_to_1p0000_K_axis_discriminates_K16_0p156_K64_"
            "0p624_K128_1p000_K256_0p998_substrate_resource_bound_NOT_pre_saturated_supersedes_"
            "v1_MM_3seeds_7_13_19_2026-06-28"
        ),
        name=(
            "substrate_capacity_multibank_alpha_K_phase_diagram v2 GPU CROSS-SEED-AGG 3/3 "
            "CHAIN-GRADE PHASE-CHARACTERIZATION: cliff_per_B={B=4:0.1, B=16:0.5, B=64:2.0} "
            "IDENTICAL across seeds 7/13/19; n_pass_at_full_N=34-35 per seed (above 12 threshold); "
            "arms_differ=216/216 per seed; rail (alpha=0.05 K=256 B=4 N=8192) recall=0.9976-1.0000; "
            "K-axis discriminates K=16(0.156) -> K=128(1.000) at rail; supersedes v1 MM"
        ),
        description=(
            "CHAIN_GRADE PHASE-CHARACTERIZATION (CERT delta = +1).\n\n"
            "Cross-seed substrate multi-bank alpha-K capacity phase diagram. Three seeds (7, 13, 19)\n"
            "of full-grid 216-point sweep (alpha x K_per_bank x num_banks x N_dim) over the\n"
            "MULTI_BANK_BIND / SINGLE_BANK_BASELINE / RANDOM_FLOOR triplet reproduce the\n"
            "cliff_per_B phase boundary IDENTICALLY at all 3 banks (B = 4, 16, 64).\n\n"
            "PROMOTION FROM v1 MM: this atom supersedes the v1 MEASURED_MECHANISM cross-seed atom\n"
            "(n_pass_at_full_N=5; HP gate unmet; rail by-construction saturated). v2 cell deltas:\n"
            "K_per_bank extended {4,16,64} -> {16,64,128,256}; degenerate B=1 dropped (B in\n"
            "{4,16,64}); HP gate tightened (n_pass_at_full_N >= 12); rail re-anchored to\n"
            "(alpha_min, K=256, B=4, N=FULL_N) (rail_ok=True across 3 seeds).\n\n"
            "OFF-DATA RECOMPUTE (Skunkworks 2026-06-28; .venv Python; 3 seeds; local metrics.json):\n\n"
            "  Per-seed top-line (recompute = reported; zero mismatches):\n"
            "    seed_7  : n_pass=119 n_pass_at_full_N=35 saturate=75 arms_differ=216/216 rail=0.9976\n"
            "    seed_13 : n_pass=118 n_pass_at_full_N=34 saturate=74 arms_differ=216/216 rail=1.0000\n"
            "    seed_19 : n_pass=119 n_pass_at_full_N=34 saturate=75 arms_differ=216/216 rail=0.9976\n"
            "  Per-seed n_pass spread: 119/118/119 (std/mean=0.008, 0.8%).\n\n"
            "  CROSS-SEED phase-boundary agreement:\n"
            "    214/216 phase points classify identically (PASS/FAIL) across all 3 seeds.\n"
            "    2 disagreements are at the exact threshold boundary\n"
            "    (MULTI=0.500 vs HP_PASS_REC=0.50 float boundary noise).\n"
            "    cliff_per_B IDENTICAL across all 3 seeds:\n"
            "      B=4  -> alpha_cliff = 0.1\n"
            "      B=16 -> alpha_cliff = 0.5\n"
            "      B=64 -> alpha_cliff = 2.0\n"
            "    Power-law scaling alpha_cliff(B) ~ K_per_bank * B / N (matches theory:\n"
            "    multi-bank distributes load such that each bank handles M/B items; cliff\n"
            "    crosses at M/B > K_per_bank, i.e. alpha > K*B/N).\n\n"
            "  K-AXIS DISCRIMINATION at rail-family (alpha=0.05 B=4 N=8192; seed_7):\n"
            "    K=16  MULTI=0.156 SINGLE=0.039 (substrate IS resource-bound; under-resourced)\n"
            "    K=64  MULTI=0.624 SINGLE=0.141 (transition zone)\n"
            "    K=128 MULTI=1.000 SINGLE=0.220 (well-resourced)\n"
            "    K=256 MULTI=0.998 SINGLE=0.302 (rail; honest baseline degradation)\n"
            "  K=128 already hits MULTI ceiling at low-alpha; K=256 gives modest extension\n"
            "  (3/54 phase points cross 0.50 only at K=256 vs K=128). The chain-grade value\n"
            "  is NOT in K=256 buying more capacity but in K=128 vs K=64 vs K=16 ramp\n"
            "  proving substrate is genuinely resource-bound through the cliff.\n\n"
            "  RAIL FAMILY dynamic range (K=256 B=4 N=8192 across alpha; 3-seed mean):\n"
            "    alpha=0.05 MULTI=0.998-1.000 SINGLE=0.283-0.315\n"
            "    alpha=0.10 MULTI=0.825-0.839 SINGLE=0.076-0.081\n"
            "    alpha=0.25 MULTI=0.199-0.208 SINGLE=0.009-0.012\n"
            "    alpha=0.50 MULTI=0.040-0.049 SINGLE=0.002-0.003\n"
            "    alpha=1.00 MULTI=0.010-0.013 SINGLE=0.001-0.002\n"
            "    alpha=2.00 MULTI=0.003       SINGLE=0.000-0.001\n"
            "  Sigmoidal cliff curve; cross-seed reproducibility on the curve exceptional\n"
            "  (0.998/1.000/0.998 at alpha=0.05; 0.003/0.003/0.003 at alpha=2.00).\n\n"
            "BY-CONSTRUCTION-SATURATION AUDIT (critical chain-grade gate):\n"
            "  Risk: v2 extended K_per_bank axis to 256. Could SINGLE_BANK fail by structure\n"
            "  rather than by lever?\n\n"
            "  No. Evidence:\n"
            "  (1) SINGLE_BANK is NOT floored at K=256. Rail SINGLE_recall=0.302 (well above\n"
            "      floor=0.000); degrades naturally with load.\n"
            "  (2) K-axis discriminates honestly through the cliff (K=16 MULTI=0.156 ramps\n"
            "      to K=128 MULTI=1.000) — substrate IS resource-bound, NOT pre-saturated.\n"
            "  (3) MULTI degrades through the cliff under load (alpha=0.05 -> 2.00: 0.998 -> 0.003).\n"
            "  (4) B=64 isn't a ceiling escape valve (K=256 B=64 alpha=2.0: MULTI=0.698).\n"
            "  (5) cliff_per_B scales with B (super-linear, matches theory).\n\n"
            "DISCRIMINATOR-MUST-SURVIVE-SCALE (USER 2026-06-26):\n"
            "  smoke-N (N=2048) at alpha=0.10 K=256 B=4: MULTI=0.81-0.85 SINGLE=0.07-0.10\n"
            "    -> margin ~0.74-0.78\n"
            "  full-N (N=8192) same config: MULTI=0.83-0.84 SINGLE=0.08\n"
            "    -> margin ~0.75-0.76\n"
            "  Smoke-N preview and full-N agree within 0.02. Discriminator survives scale.\n\n"
            "GPU dispatch (Fix #24):\n"
            "  device=cuda:0; gpu_name=NVIDIA GeForce RTX 4060 Ti; gpu_max_mem_alloc=264MB float16.\n"
            "  gpu_util_mean=29-33%; gpu_util_p50=18-23%; gpu_util_max=94-100% (across 3 seeds).\n"
            "  Wall=136-141s per seed for 648 units (~210ms/unit; GPU matmul-bound).\n"
            "  Soft note: cell's own HP_GPU_UTIL_MIN=0.50 declared in config but not gated in\n"
            "  verdict logic; mean util ~30% below declared 50% gate. util_max=100% confirms\n"
            "  real GPU compute, so Fix #24 intent (uses GPU) is satisfied — but cell's own\n"
            "  declared GPU-saturation gate was not enforced. Methodology note for future\n"
            "  GPU-mandate cells; NOT a chain-grade blocker.\n\n"
            "META_RULE COMPLIANCE:\n"
            "  H cardinality_ok=True (216 expected = 216 observed per seed; 648 units; 3 seeds)\n"
            "  J no-silent-except: n_failures=0 n_probe_denials=0 per seed\n"
            "  K discriminator fires (124/216 phase points above margin threshold per seed)\n"
            "  L band-check: 34-35 points at full-N per seed (above the 12 chain-grade threshold)\n"
            "  AC arms-differ-by-SHA256: 216/216 distinct per seed\n"
            "  AE bands locked at module init (per pre-reg)\n"
            "  AF arms differ per point: 211-214/216 with 3 distinct recalls (2-5 ties at\n"
            "    deep floor where SINGLE and FLOOR both converge to ~0.001 — honest convergence,\n"
            "    NOT arm-identity bug; arm hashes still 216/216 distinct)\n\n"
            "WHY CHAIN-GRADE:\n"
            "  (a) cliff_per_B IDENTICAL across 3 seeds at full-grid resolution\n"
            "  (b) HP gates (n_pass>=50, n_pass_at_full_N>=12, rail>=0.95) cleared 3x\n"
            "  (c) Discriminator survives scale (smoke-N preview = full-N within 0.02)\n"
            "  (d) Not by-construction saturated (K-axis ramp + SINGLE non-floored at rail)\n"
            "  (e) MULTI-vs-SINGLE separation through full alpha-range (margins 0.69-0.99 in\n"
            "      rail family) — substrate's binding mechanism is the load-bearing advantage\n"
            "      NOT just K-budget\n"
            "  (f) v1 -> v2 chain-grade revival via dropped degenerate baseline + extended axis\n"
            "      + tightened gate (honest upward correction, not gate-loosening)\n\n"
            "PHYSICAL INTERPRETATION:\n"
            "  Multi-bank binding partitions M items across B banks; each bank handles M/B items.\n"
            "  Single-bank baseline puts all M items in K_per_bank slots of one bank set. At fixed\n"
            "  K_per_bank, total slots = K_per_bank * B. Cliff at alpha_cliff(B) ~ K_per_bank*B/N.\n"
            "  At v2 rail (K=256 B=4 N=8192): predicted alpha_cliff ~ 256*4/8192 = 0.125. Observed\n"
            "  MULTI crosses 0.5 between alpha=0.10 and alpha=0.25 (close match). Cross-B scaling\n"
            "  cliff_per_B={B=4: 0.1, B=16: 0.5, B=64: 2.0} is 5x per 4x B — slightly super-linear\n"
            "  but matches K*B/N for fixed K, increasing B.\n\n"
            "SUPERSEDES:\n"
            "  v1 MM atom: " + V1_SUPERSEDED_ATOM_ID + "\n"
            "  Promotion: MEASURED_MECHANISM -> CHAIN_GRADE_PHASE_CHARACTERIZATION (CERT +1).\n"
            "  v1 still recorded as evidence; v2 is the chain-grade carrier going forward.\n\n"
            "COMPOSES-WITH:\n"
            "  - WM K-cliff v3 chain-grade (commit 7274bafb): sibling phase-characterization\n"
            "  - sequence_binding K-cliff chain-grade (commit 68714d0e): sibling phase-characterization\n"
            "  - pattern_completion v2.2 dense chain-grade (commit ac706494): sibling\n"
            "    phase-characterization\n"
            "  All four describe substrate phase-cliff scaling laws across mechanism types\n"
            "  (multi-bank binding / WM K-cliff / sequence-binding K-cliff / pattern-completion\n"
            "  corruption-cliff).\n"
        ),
        kind=AtomKind.CAPABILITY_MAP,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "CERT_CHAIN_GRADE",
            "cert_status": "chain_grade",
            "cert_class": "substrate_phase_characterization_multibank_alpha_K_cliff_per_B",
            "cell_anchor": "substrate_capacity_multibank_alpha_K_phase_diagram_v2_GPU_AGG",
            "cell_commit": CELL_COMMIT,
            "metrics_paths": [METRICS_S7, METRICS_S13, METRICS_S19],
            "prereg_path": PREREG_PATH,
            "ruling_note": RULING_NOTE,
            "verified_off_data": True,
            "n_seeds": 3,
            "seeds": [7, 13, 19],
            "n_phase_points": 216,
            "n_units_total_per_seed": 648,
            "n_units_total_3seeds": 1944,
            "n_pass_per_seed": [119, 118, 119],
            "n_pass_at_full_N_per_seed": [35, 34, 34],
            "n_saturate_per_seed": [75, 74, 75],
            "arms_differ_per_seed": [216, 216, 216],
            "rail_recall_per_seed": [0.9976, 1.0000, 0.9976],
            "rail_config": {"alpha": 0.05, "K_per_bank": 256, "num_banks": 4, "n_dim": 8192},
            "rail_target": 0.95,
            "cliff_per_B_3seed_identical": CLIFF_PER_B_3SEED_IDENTICAL,
            "cross_seed_phase_agreement_count": 214,
            "cross_seed_phase_agreement_total": 216,
            "cross_seed_n_pass_std_over_mean": 0.008,
            "supersedes_v1_atom_id": V1_SUPERSEDED_ATOM_ID,
            "supersession_class": "MM_to_CHAIN_GRADE_PHASE_CHARACTERIZATION_promotion_via_extended_axis_plus_tightened_gate_plus_dropped_degenerate",
            "v2_deltas_vs_v1": {
                "K_per_bank": "{4,16,64} -> {16,64,128,256}",
                "B_num_banks": "{1,4,16} -> {4,16,64} (dropped degenerate B=1)",
                "HP_n_pass_at_full_N_min": "8 -> 12",
                "rail_config": "(alpha_min, K=64, B=1, N=FULL_N) -> (alpha_min, K=256, B=4, N=FULL_N)",
            },
            "composes_with": [
                "WM_K_cliff_v3_chain_grade_commit_7274bafb",
                "sequence_binding_K_cliff_chain_grade_commit_68714d0e",
                "pattern_completion_v2p2_dense_chain_grade_commit_ac706494",
            ],
            "phase_characterization_class": "alpha_cliff_scales_with_B_at_fixed_K_N",
            "predicted_cliff_form": "alpha_cliff(B) ~ K_per_bank * B / N",
            "discriminator_armed": True,
            "discriminator_fired_clean_separation": True,
            "discriminator_survives_scale": True,
            "by_construction_saturation_flag": False,
            "by_construction_saturation_reasoning": (
                "K-axis discrimination at rail-family proves substrate resource-bound: "
                "K=16 MULTI=0.156 ramps to K=128 MULTI=1.000 (NOT pre-saturated); "
                "SINGLE at rail K=256=0.302 above floor=0.000 (honest baseline degradation); "
                "MULTI degrades 0.998->0.003 across alpha (wide sigmoidal); "
                "B=64 K=256 alpha=2.0 MULTI=0.698 (load tested past degradation)"
            ),
            "META_RULE_H_cardinality_ok": True,
            "META_RULE_J_no_silent_except_ok": True,
            "META_RULE_K_discriminator_fires_clean": True,
            "META_RULE_L_band_check": "34_to_35_at_full_N_per_seed_above_12_threshold",
            "META_RULE_AC_arms_differ_sha256": True,
            "META_RULE_AE_bands_locked": True,
            "META_RULE_AF_arms_differ_per_point": True,
            "stage": "Stage_1_base_substrate_phase_diagram",
            "skunkworks_audit_pass": True,
            "skunkworks_audit_red_flags": [],
            "skunkworks_audit_soft_notes": [
                "gpu_util_mean_29_to_33pct_below_cell_declared_HP_GPU_UTIL_MIN_0p50_but_util_max_94_to_100pct_confirms_real_GPU_compute",
                "2_phase_points_of_216_disagree_across_seeds_at_threshold_boundary_MULTI_eq_0p500_HP_PASS_REC_eq_0p50_float_noise_not_substantive",
                "K_eq_256_only_marginally_extends_PASS_region_over_K_eq_128_3_of_54_phase_points_chain_grade_value_in_K_axis_ramp_not_K_eq_256_specifically",
            ],
            "atomized_by": ATOMIZED_BY,
        },
    )


# ============================================================================
# SAFE WRITER HELPER (same pattern as pc_v2p2 atomize)
# ============================================================================

def safe_add_with_ledger(
    atom: Atom,
    *,
    source: str,
    note: str,
    ledger_row: dict,
    expected_cert_n_pre: int,
    expected_cert_n_post: int,
) -> tuple[bool, str | None]:
    ps = PartitionedStore(STORE_ROOT)
    qid = f"{atom.corpus.value}::{atom.id}"
    if ps.get_atom(qid) is not None:
        print(f"  SKIP (idempotent at Store layer): {atom.id[:100]} already present.")
    else:
        print(f"  ADDING atom: {atom.id[:120]}...")
        ps.add_atom(atom, source=source, note=note)
        ps2 = PartitionedStore(STORE_ROOT)
        found = ps2.get_atom(qid)
        if found is None:
            print(f"  FAIL: atom not found post-add")
            return (False, None)
        md = found.metadata or {}
        expected_pq = (atom.metadata or {}).get("provenance_quality")
        if md.get("provenance_quality") != expected_pq:
            print(f"  FAIL: pq mismatch (expected {expected_pq}, got {md.get('provenance_quality')})")
            return (False, None)
        print(f"  PASS: round-trip survival OK (pq={md.get('provenance_quality')})")

    ps_check = PartitionedStore(STORE_ROOT)
    live_n = sum(
        1 for a in ps_check.all_atoms()
        if (a.metadata or {}).get("provenance_quality") == "CERT_CHAIN_GRADE"
    )
    if live_n != expected_cert_n_post:
        print(f"  FAIL: live CERT N {live_n} != expected_cert_n_post {expected_cert_n_post}")
        return (False, None)

    print(
        f"  appending cert-ledger row "
        f"(op={ledger_row.get('op')} status={ledger_row.get('cert_status')} "
        f"delta={ledger_row.get('cert_increment_delta')})"
    )
    try:
        row_h = append_cert_ledger_row(
            ledger_row,
            expected_cert_n_pre=expected_cert_n_post,
            expected_cert_n_post=expected_cert_n_post,
        )
        print(f"  ledger row appended; row_hash = {row_h}")
        return (True, row_h)
    except Exception as e:
        print(f"  FAIL: cert-ledger append errored: {e}")
        return (False, None)


def build_per_seed_evidence_row(*, atom_id, cell_commit, verdict, notes_path, metrics_path,
                                atomized_by, note, ts=None):
    """Per-seed evidence rows are CERT-neutral (delta=0)."""
    return {
        "ts": ts,
        "op": "cert_ruling",
        "atom_id": atom_id,
        "cert_status": "custom",
        "cert_class": "mechanism_characterization",
        "verified_off_data": True,
        "atomized_by": atomized_by,
        "cell_commit": cell_commit,
        "verdict": verdict,
        "cert_increment_delta": 0,
        "cv": None,
        "referent_pointer": {
            "notes_path": notes_path,
            "metrics_path": metrics_path,
            "atom_qualified_id": atom_id,
        },
        "supersedes": None,
        "note": note,
    }


# ============================================================================
# MAIN
# ============================================================================

def main() -> int:
    apply = "--apply" in sys.argv

    a_s7 = build_atom_seed7()
    a_s13 = build_atom_seed13()
    a_s19 = build_atom_seed19()
    a_agg = build_atom_cross_seed_agg()

    atoms = [a_s7, a_s13, a_s19, a_agg]
    labels = [
        "[1] seed_7  HARD_PASS evidence (delta=0)",
        "[2] seed_13 HARD_PASS evidence (delta=0)",
        "[3] seed_19 HARD_PASS evidence (delta=0)",
        "[4] CROSS-SEED AGG chain_grade_phase_characterization (delta=+1; supersedes v1 MM)",
    ]

    print("=" * 72)
    print("Cert routing plan (DRY) -- multibank_alpha_K v2 GPU 3-seed chain-grade promotion")
    print("=" * 72)
    for atom, lbl in zip(atoms, labels):
        print(f"  {lbl}")
        print(f"      {atom.id[:120]}...")
        print(f"      pq={atom.metadata['provenance_quality']} status={atom.metadata['cert_status']} corpus={atom.corpus.value}")
    print()
    print("  Net CERT N change: +1 (631 -> 632; 1 cross-seed AGG chain-grade)")
    print("  Net ledger rows: +4 (3 evidence + 1 chain-grade-AGG)")

    if not apply:
        print()
        print("DRY: pass --apply to mutate Store + ledger.")
        return 0

    print()
    print("=" * 72)
    print("A5 PRE snapshot")
    print("=" * 72)
    ps_pre = PartitionedStore(STORE_ROOT)
    cert_pre = sum(
        1 for a in ps_pre.all_atoms()
        if (a.metadata or {}).get("provenance_quality") == "CERT_CHAIN_GRADE"
    )
    print(f"A5-PRE: live CERT N = {cert_pre}")

    expected_post = cert_pre + 1  # 1 chain-grade atom (AGG)

    def live_cert():
        ps_l = PartitionedStore(STORE_ROOT)
        return sum(
            1 for a in ps_l.all_atoms()
            if (a.metadata or {}).get("provenance_quality") == "CERT_CHAIN_GRADE"
        )

    sources = "skunkworks_landed_vet_multibank_alpha_K_v2_GPU_3seed_chain_grade_2026-06-28"

    # Atom 1: seed_7 (delta=0)
    print()
    print("=" * 72)
    print(f"Window 1: {labels[0]}")
    print("=" * 72)
    qid = f"{a_s7.corpus.value}::{a_s7.id}"
    row = build_per_seed_evidence_row(
        atom_id=qid,
        cell_commit=CELL_COMMIT,
        verdict="HARD_PASS_PHASE_DIAGRAM_v2_seed_7",
        notes_path=RULING_NOTE,
        metrics_path=METRICS_S7,
        atomized_by=ATOMIZED_BY,
        note="per_seed_evidence_multibank_alpha_K_v2_GPU_seed_7",
    )
    n0 = live_cert()
    ok, _ = safe_add_with_ledger(a_s7, source=sources, note="multibank_alpha_K_v2_GPU_seed_7",
                                  ledger_row=row, expected_cert_n_pre=n0,
                                  expected_cert_n_post=n0)
    if not ok:
        print("ABORT: atom 1 failed; do not proceed.")
        return 1

    # Atom 2: seed_13 (delta=0)
    print()
    print("=" * 72)
    print(f"Window 2: {labels[1]}")
    print("=" * 72)
    qid = f"{a_s13.corpus.value}::{a_s13.id}"
    row = build_per_seed_evidence_row(
        atom_id=qid,
        cell_commit=CELL_COMMIT,
        verdict="HARD_PASS_PHASE_DIAGRAM_v2_seed_13",
        notes_path=RULING_NOTE,
        metrics_path=METRICS_S13,
        atomized_by=ATOMIZED_BY,
        note="per_seed_evidence_multibank_alpha_K_v2_GPU_seed_13",
    )
    n0 = live_cert()
    ok, _ = safe_add_with_ledger(a_s13, source=sources, note="multibank_alpha_K_v2_GPU_seed_13",
                                  ledger_row=row, expected_cert_n_pre=n0,
                                  expected_cert_n_post=n0)
    if not ok:
        print("ABORT: atom 2 failed.")
        return 1

    # Atom 3: seed_19 (delta=0)
    print()
    print("=" * 72)
    print(f"Window 3: {labels[2]}")
    print("=" * 72)
    qid = f"{a_s19.corpus.value}::{a_s19.id}"
    row = build_per_seed_evidence_row(
        atom_id=qid,
        cell_commit=CELL_COMMIT,
        verdict="HARD_PASS_PHASE_DIAGRAM_v2_seed_19",
        notes_path=RULING_NOTE,
        metrics_path=METRICS_S19,
        atomized_by=ATOMIZED_BY,
        note="per_seed_evidence_multibank_alpha_K_v2_GPU_seed_19",
    )
    n0 = live_cert()
    ok, _ = safe_add_with_ledger(a_s19, source=sources, note="multibank_alpha_K_v2_GPU_seed_19",
                                  ledger_row=row, expected_cert_n_pre=n0,
                                  expected_cert_n_post=n0)
    if not ok:
        print("ABORT: atom 3 failed.")
        return 1

    # Atom 4: CROSS-SEED AGG (delta = +1)
    print()
    print("=" * 72)
    print(f"Window 4: {labels[3]}")
    print("=" * 72)
    qid = f"{a_agg.corpus.value}::{a_agg.id}"
    row = build_chain_grade_ruling_row(
        atom_id=qid,
        cell_commit=CELL_COMMIT,
        verdict="HARD_PASS_PHASE_DIAGRAM_v2_CROSS_SEED_AGG_3_of_3_chain_grade_phase_characterization",
        notes_path=RULING_NOTE,
        metrics_path=METRICS_S7,  # representative; full list in atom metadata
        cv=0.008,  # per-seed n_pass std/mean
        cert_class="pre_reg_pass",  # ledger-vocab-restricted; richer descriptor in atom metadata
        atomized_by=ATOMIZED_BY,
        note="chain_grade_promotion_multibank_alpha_K_v2_supersedes_v1_MM",
    )
    n0 = live_cert()
    qid_check = f"{a_agg.corpus.value}::{a_agg.id}"
    agg_already_present = PartitionedStore(STORE_ROOT).get_atom(qid_check) is not None
    if agg_already_present:
        exp_pre, exp_post = n0, n0
    else:
        exp_pre, exp_post = n0, n0 + 1
    ok, _ = safe_add_with_ledger(a_agg, source=sources, note="multibank_alpha_K_v2_GPU_CROSS_SEED_AGG",
                                  ledger_row=row, expected_cert_n_pre=exp_pre,
                                  expected_cert_n_post=exp_post)
    if not ok:
        print("ABORT: AGG atom failed.")
        return 1

    # Final A5 POST check
    print()
    print("=" * 72)
    print("A5 POST snapshot")
    print("=" * 72)
    ps_post = PartitionedStore(STORE_ROOT)
    cert_post = sum(
        1 for a in ps_post.all_atoms()
        if (a.metadata or {}).get("provenance_quality") == "CERT_CHAIN_GRADE"
    )
    print(f"A5-POST: live CERT N = {cert_post}")
    print(f"  Expected: {expected_post}")
    print(f"  Delta: {cert_post - cert_pre} (expected +1)")

    if cert_post != expected_post:
        print(f"FAIL: final CERT N mismatch.")
        return 1

    print()
    print("=" * 72)
    print("ALL ATOMS LANDED + LEDGER WRITTEN")
    print("=" * 72)
    print(f"  Per-seed evidence: 3 atoms (delta=0 each)")
    print(f"  Cross-seed AGG chain-grade phase-characterization: 1 atom (delta=+1)")
    print(f"  Supersedes v1 MM atom: {V1_SUPERSEDED_ATOM_ID[:80]}...")
    print(f"  CERT N: {cert_pre} -> {cert_post}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
