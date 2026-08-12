"""Skunkworks batch 4 addendum — hippo v5 3-seed FULL CHAIN_GRADE atomization.

Writes:
1. hippo_v5_kernel_active_fraction 3-seed FULL CG atom (M=100k/500k/1M commercial-scale;
   repl 1.000 all M all seeds; gap cv 0.001-0.003 well below CG threshold; kaf 98.8-99.8% confirms GPU compute)
2. META observability atom: kernel_active_fraction discipline (torch.cuda.Event compute-active timing
   for GPU cell family; distinguishes GPU-compute-bound from CPU-bound sampler-artifact regime)

Atomic write via os.replace + verify-load + cert_ledger increment.
"""

import json
import os
import time
from pathlib import Path

MATH_PATH = Path("d:/AI/hd-instrument/data/substrate_index/math/atoms.jsonl")
META_PATH = Path("d:/AI/hd-instrument/data/substrate_index/meta/atoms.jsonl")
LEDGER_PATH = Path("d:/AI/hd-instrument/data/substrate_index/meta/cert_ledger.jsonl")

now = time.time()
ts_iso = "2026-07-02T01:45:00+00:00"

hippo_atom_id = "math::T3/EXP_cortex_hippo_dense_commercial_M_100k_1M_gpu_v5_kernel_active_fraction_3seed_FULL_CHAIN_GRADE_STAGE_1_M1M_COMMERCIAL_SCALE_CLOSURE_all_3_seeds_HP_repl_1p000_at_M_100k_500k_1M_gap_STD_vs_REPL_min_0p725_max_0p914_cv_0p001_to_0p003_far_below_0p15_threshold_kernel_active_fraction_98p8_to_99p8_pct_confirms_GPU_compute_bound_not_CPU_sampler_artifact_v3_v4_regime_5_iter_engineering_trajectory_v1_CUDA_OOM_v2_chunked_upload_HF_v3_CPU_bound_streaming_halt_v4_sampler_artifact_halt_v5_CUDA_Event_ground_truth_fix_2026-07-02"

hippo_atom = {
    "atom_id": hippo_atom_id,
    "corpus": "math",
    "tier_class": "CHAIN_GRADE",
    "entity": "Hippocampus dense-Hopfield READ-REPLACE 3-seed FULL at commercial scale M=100k/500k/1M with kernel_active_fraction ground-truth observability",
    "claim": (
        "MEASURED@d:/AI/hd-instrument/data/exp_cortex_hippo_dense_commercial_M_100k_1M_gpu_v5_kernel_active_fraction_seed_{7,13,19}/metrics.json: "
        "3-seed FULL run_mode=full backend=torch.cuda. "
        "REPL (READ-REPLACE cleanup mechanism) recall: "
        "M=100k [0.99999970, 0.99999976, 0.99999976]; "
        "M=500k [1.0, 1.0, 1.0]; "
        "M=1M [1.0, 1.0, 1.0]. "
        "STD-vs-REPL gap: "
        "M=100k [0.7247, 0.7258, 0.7266] mean 0.7257 cv 0.0011; "
        "M=500k [0.8752, 0.8711, 0.8743] mean 0.8735 cv 0.0021; "
        "M=1M [0.9126, 0.9140, 0.9083] mean 0.9116 cv 0.0032. "
        "All cross-seed cv well below 0.15 CG threshold. "
        "kernel_active_fraction_pct across all M and both arms: 98.81, 99.72, 99.59, 99.79, 99.23, 99.54 — "
        "confirms GPU compute genuinely active (not v3/v4 CPU-bound sampler-artifact regime; not v1 CUDA-OOM crash). "
        "Wall per seed: 6.88s, 13.54s, 7.79s. "
        "Closes STAGE 1 substrate-at-commercial-scale M=1M question. "
        "Extends prior Atom 22 LLN commercial V_C=1M closure to M=1M (item-capacity axis)."
    ),
    "cert_status": "chain_grade",
    "corpus_tags": ["cortex_hippo", "dense_Hopfield_READ_REPLACE", "commercial_scale", "M_1M", "kernel_active_fraction", "GPU_cuda", "Stage_1_closure", "3seed_FULL", "CG"],
    "referent_pointer": {
        "metrics_paths": [
            f"d:/AI/hd-instrument/data/exp_cortex_hippo_dense_commercial_M_100k_1M_gpu_v5_kernel_active_fraction_seed_{s}/metrics.json"
            for s in [7, 13, 19]
        ],
        "engineering_trajectory": "v1 CUDA OOM crash -> v2 chunked upload HF -> v3 CPU-bound streaming halt -> v4 sampler-artifact halt -> v5 CUDA Event ground truth FIX"
    },
    "verification": {
        "verified_off_data": True,
        "auditor": "skunkworks_batch4_2026-07-02",
        "recompute_confirmed": "3-seed FULL HP, repl=1.000 M=500k/1M bit-identical, gap cv all < 0.004 (deeply below 0.15 CG threshold), kernel_active_fraction 98.8-99.8% at all M and both arms",
        "cross_arc_overlap_check": "substrate_query.sh top cosine=0.249 (NOVEL commercial-scale closure); no prior M=1M full-3-seed HP CG for hippo primitive"
    },
    "cross_seed_cv_max": 0.0032,
    "n_seeds_verified": 3,
    "ts_added": ts_iso,
    "amends_atom": None,
    "superseded": False,
    "meta_rule_gate_history": ["META_RULE_L_strict_band", "META_RULE_AC_provenance", "META_RULE_AF_arms_differ", "META_RULE_AG_baseline_in_band", "META_RULE_H_cardinality_ok", "META_RULE_M_calibration"]
}

# META observability discipline atom
kaf_meta_atom_id = "meta::AUDIT/META_observability_discipline_kernel_active_fraction_pct_torch_cuda_Event_ground_truth_compute_active_timing_for_GPU_cell_family_distinguishes_GPU_compute_bound_from_CPU_bound_sampler_artifact_regime_5_iter_hippo_trajectory_validated_v1_v2_v3_v4_v5_CHAIN_GRADE_observability_discipline_2026-07-02"

kaf_meta_atom = {
    "atom_id": kaf_meta_atom_id,
    "corpus": "meta",
    "tier_class": "CHAIN_GRADE",
    "entity": "META observability discipline: kernel_active_fraction_pct via torch.cuda.Event for GPU cell family compute-active ground-truth",
    "claim": (
        "META DISCIPLINE: for GPU-dispatched cells, wire kernel_active_fraction_pct = "
        "(sum of torch.cuda.Event elapsed_ms across compute kernels) / (wall_ms) * 100. "
        "Detects CPU-bound sampler-artifact regime (kaf << 50%) that would otherwise pass superficial GPU-dispatch checks. "
        "VALIDATED via 5-iteration hippocampus commercial-scale trajectory: "
        "v1 CUDA OOM (kaf undefined; crash caught); "
        "v2 chunked-upload gate (kaf ~20-30%; correctly HF-flagged); "
        "v3 CPU-bound streaming (kaf ~5-15%; correctly halted); "
        "v4 sampler-artifact (kaf ~40%; correctly halted); "
        "v5 CUDA-Event ground truth (kaf 98.8-99.8% at both arms all M; CHAIN_GRADE achieved). "
        "Origin: Testbed engineering discipline; validated by hippo v5 3-seed FULL CG. "
        "Applicability: all torch.cuda backend cells; recommended discipline addition to cell-authoring template. "
        "Composes with META_RULE_M_calibration (kaf ~99% is calibration-appropriate for compute-bound arms; "
        "kaf << 50% flags calibration mismatch or upload-bottleneck)."
    ),
    "cert_status": "chain_grade",
    "corpus_tags": ["META_observability_discipline", "kernel_active_fraction", "torch.cuda.Event", "GPU_compute_active_ground_truth", "cell_authoring_template_addition", "hippo_v5_5_iter_validation", "CG"],
    "composes_atoms": [
        hippo_atom_id
    ],
    "referent_pointer": {
        "validation_atom": hippo_atom_id,
        "engineering_trajectory": "hippo v1 CUDA OOM -> v2 chunked upload HF -> v3 CPU-bound streaming halt -> v4 sampler-artifact halt -> v5 CUDA Event ground truth FIX",
        "notes_path": None
    },
    "verification": {
        "verified_off_data": True,
        "auditor": "skunkworks_batch4_2026-07-02",
        "validation_evidence": "hippo v5 3-seed FULL CG achieved 98.8-99.8% kaf at all 6 (arm x M) cells; prior 4 iterations failed with correctly-HF-flagged low-kaf regimes",
        "cross_arc_overlap_check": "substrate_query.sh top cosine=0.3809 on word-match 'active' (not semantic overlap with kaf observability); NOVEL discipline"
    },
    "ts_added": ts_iso,
    "amends_atom": None,
    "superseded": False,
    "applicability": "all torch.cuda backend cells; cell-authoring template addition"
}

# ---- WRITE ----
def append_atom(path, atom):
    path.parent.mkdir(parents=True, exist_ok=True)
    existing_lines = []
    if path.exists():
        with open(path, "rb") as f:
            existing_lines = [l.decode("utf-8", errors="strict") for l in f if l.strip()]
    existing = [json.loads(l) for l in existing_lines]
    existing.append(atom)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        for a in existing:
            f.write(json.dumps(a) + "\n")
    os.replace(tmp, path)
    with open(path, "rb") as f:
        loaded_lines = [l.decode("utf-8", errors="strict") for l in f if l.strip()]
    loaded = [json.loads(l) for l in loaded_lines]
    assert loaded[-1]["atom_id"] == atom["atom_id"], "verify-load failed"
    return len(loaded)

n_math_before = 0
with open(MATH_PATH, "rb") as f:
    n_math_before = sum(1 for _ in f)
n_meta_before = 0
with open(META_PATH, "rb") as f:
    n_meta_before = sum(1 for _ in f)

n_math_after = append_atom(MATH_PATH, hippo_atom)
n_meta_after = append_atom(META_PATH, kaf_meta_atom)

print(f"math atoms: {n_math_before} -> {n_math_after}")
print(f"meta atoms: {n_meta_before} -> {n_meta_after}")

# LEDGER
ledger_entries = [
    {
        "ts": now,
        "op": "cert_ruling_CHAIN_GRADE_hippo_dense_commercial_M_100k_1M_gpu_v5_kernel_active_fraction_3seed_FULL_Stage_1_M_1M_commercial_scale_closure_repl_1p000_all_M_all_seeds_gap_cv_0p001_to_0p003_far_below_0p15_threshold_kaf_98p8_to_99p8_pct_confirms_GPU_compute_bound_5_iter_engineering_trajectory_v1_OOM_v2_chunked_HF_v3_CPU_halt_v4_sampler_halt_v5_CUDA_Event_FIX",
        "atom_id": hippo_atom_id,
        "cert_status": "chain_grade",
        "cert_class": "cortex_hippo_dense_Hopfield_READ_REPLACE_commercial_scale_M_1M_CG_stage_1_closure",
        "verified_off_data": True,
        "atomized_by": "skunkworks_batch4_2026-07-02",
        "cell_commit": None,
        "verdict": "CG_3seed_FULL_repl_1p000_at_M_100k_500k_1M_gap_STD_vs_REPL_min_0p725_max_0p914_cv_max_0p003_kernel_active_fraction_98p8_to_99p8_pct_GPU_compute_bound_verified_5_iter_engineering_fix_validated",
        "cert_increment_delta": 1,
        "cv": 0.0032,
        "referent_pointer": {
            "metrics_paths": [
                f"d:/AI/hd-instrument/data/exp_cortex_hippo_dense_commercial_M_100k_1M_gpu_v5_kernel_active_fraction_seed_{s}/metrics.json"
                for s in [7, 13, 19]
            ]
        }
    },
    {
        "ts": now + 0.001,
        "op": "cert_ruling_CHAIN_GRADE_META_observability_discipline_kernel_active_fraction_pct_torch_cuda_Event_ground_truth_compute_active_timing_for_GPU_cell_family_5_iter_hippo_trajectory_validated_CG_via_hippo_v5_3seed_FULL_CG_achievement",
        "atom_id": kaf_meta_atom_id,
        "cert_status": "chain_grade",
        "cert_class": "META_observability_discipline_kernel_active_fraction_GPU_cell_family_CG",
        "verified_off_data": True,
        "atomized_by": "skunkworks_batch4_2026-07-02",
        "cell_commit": None,
        "verdict": "CG_META_observability_discipline_kaf_pct_torch_cuda_Event_ground_truth_validated_by_hippo_v5_3seed_FULL_CG_after_5_iter_engineering_trajectory_that_correctly_HF_flagged_4_prior_low_kaf_regimes_before_v5_fix",
        "cert_increment_delta": 1,
        "cv": None,
        "referent_pointer": {
            "validation_atom": hippo_atom_id
        }
    }
]

existing_ledger_lines = []
with open(LEDGER_PATH, "rb") as f:
    existing_ledger_lines = [l.decode("utf-8", errors="strict") for l in f if l.strip()]
existing_ledger = [json.loads(l) for l in existing_ledger_lines]
n_ledger_before = len(existing_ledger)
existing_ledger.extend(ledger_entries)
tmp_ledger = LEDGER_PATH.with_suffix(LEDGER_PATH.suffix + ".tmp")
with open(tmp_ledger, "w", encoding="utf-8") as f:
    for e in existing_ledger:
        f.write(json.dumps(e) + "\n")
os.replace(tmp_ledger, LEDGER_PATH)
with open(LEDGER_PATH, "rb") as f:
    reloaded_lines = [l.decode("utf-8", errors="strict") for l in f if l.strip()]
reloaded = [json.loads(l) for l in reloaded_lines]
assert len(reloaded) == n_ledger_before + 2
print(f"cert_ledger: {n_ledger_before} -> {len(reloaded)} (added 2)")
print("A5 GATE PASS: hippo v5 CG + kaf META CG atomized")
