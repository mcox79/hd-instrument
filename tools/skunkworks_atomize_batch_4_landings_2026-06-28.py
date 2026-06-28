"""
A5-gated batch atomize 2026-06-28: 4 cell-batches landed today.

Step 2: WM v3 GPU 3-seed HARD_PASS -> chain-grade phase characterization (+1 CERT)
Step 3: cortex_hippo M=8192 3-seed META_RULE_AF violation -> HARD_FAIL (0 CERT, proven negative)
Step 4: ultrametric 3-seed HARD_PASS phase coverage -> chain-grade phase characterization
        with HONEST-DOWNWARD framing (ULTRA dominated by KMEANS in 60-65% of phase space;
        wins in 35-42%) (+1 CERT)
Step 5: schema exemplar-bayes 3-seed MIDDLE_BAND -> phase characterization MM (0 CERT)

Plus 1 META atom amending META_RULE_AF with FULL vs DIRECT bit-exact equality discipline.

Per Director directives + Skunkworks independent off-data verify:

WM v3 (chain-grade, +1):
  - Cross-seed cliff bit-exact: 256*B for all B in {1,2,4,8,16}, all 3 seeds
  - Rail K=64 B=1 N=8192 = 1.0000 (>=0.95 target), all 3 seeds
  - cardinality_ok=True (288/288 units), arms_differ 96/96, all 3 seeds
  - substrate_only_ok=True (zero LLM at inference), all 3 seeds
  - n_pass>=20 hard band met all 3 seeds (20/22/20)

Cortex_hippo (HARD_FAIL, 0 CERT, proven negative):
  - ARM_FULL_HANDOFF.recall_cortex == ARM_DIRECT_CORTEX.recall_cortex BIT-EXACT all 3 seeds
    seed_7:  0.308837890625 == 0.308837890625
    seed_13: 0.3272705078125 == 0.3272705078125
    seed_19: 0.3233642578125 == 0.3233642578125
  - cortex_norm bit-exact too (45.47652816772461 / 45.280181884765625 / 45.346351623535156)
  - META_RULE_AF violation: cell does NOT demonstrate cortex-hippo handoff;
    W_hippo unused in FULL path; cell-author rationalization is invalid.

Ultrametric (chain-grade phase-characterization with downward caveat, +1):
  - 3-seed regime structure consistent (separable 30/31/31 = 50/52/52% of phase points;
    chain_failure 26/24/25 = 43/40/42%; ultra_advantage 25/21/22 = 42/35/37%;
    discriminating 55/49/50 = 92/82/83% of all phase points)
  - All 3 seeds n_ultra_advantage>=12 (>=20% threshold per pre-reg); Director rule
    "ultra_advantage > 20% not at threshold" SATISFIED with margin (35-42%)
  - HOWEVER: directional mean delta_uk_acc_mean is NEGATIVE all 3 seeds
    (-0.139 / -0.164 / -0.120) -- ULTRA DOMINATED BY KMEANS on average
  - Honest framing: phase-diagram CHARACTERIZED (chain-grade); ULTRA advantage
    is a sub-regime phenomenon (35-42%), not a headline "ULTRA wins"

Schema (MM, 0 CERT):
  - 3-seed lift_pts consistent (38/36/41 of 60)
  - 3-seed capacity_scaling_met=False (delta 0.000/0.010/0.005)
  - cliff_observable=False all 3 seeds; phase-diagram coverage but no decisive cliff

META atom: META_RULE_AF amendment -- FULL vs DIRECT bit-exact equality discipline.

A5 protocol per atom write:
  - PRE: count lines, integrity-check all JSON parses
  - Atomic write tmp -> os.replace
  - POST: count delta == 1, target line parses, integrity-check all lines, Store loads.
"""
import json
import os
import time
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
MATH_ATOMS = ROOT / "data/substrate_index/math/atoms.jsonl"
META_ATOMS = ROOT / "data/substrate_index/meta/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"

ATOMIZED_BY = "skunkworks_atomize_batch_4_landings_2026-06-28"
ATOMIZED_DATE = "2026-06-28"

# ============================================================
# STEP 2: WM K-cliff v3 GPU chunked -- chain-grade phase characterization +1
# ============================================================
WM_V3_SEEDS = [7, 13, 19]
WM_V3_DATA = {
    7:  {"n_pass": 20, "n_pass_at_full_N": 9,  "n_saturate": 5, "n_floor": 48, "n_probe_cliffs": 0, "rail": 1.0},
    13: {"n_pass": 22, "n_pass_at_full_N": 11, "n_saturate": 9, "n_floor": 47, "n_probe_cliffs": 0, "rail": 1.0},
    19: {"n_pass": 20, "n_pass_at_full_N": 9,  "n_saturate": 7, "n_floor": 43, "n_probe_cliffs": 0, "rail": 1.0},
}
WM_V3_CLIFF_PER_B = {"B=1": 256, "B=2": 512, "B=4": 1024, "B=8": 2048, "B=16": 4096}  # IDENTICAL across all 3 seeds

def wm_v3_per_seed_atom(seed: int) -> dict:
    d = WM_V3_DATA[seed]
    return {
        "id": f"T3/EXP_substrate_wm_multibank_K_cliff_phase_diagram_v3_GPU_chunked_seed_{seed}_HARD_PASS_K_cliff_256B_torch_cuda_n_pass_{d['n_pass']}_rail_K64B1N8192_1p0_2026-06-28",
        "name": f"WM multi-bank K-cliff v3 GPU chunked seed_{seed} HARD_PASS (K_cliff = 256*B; rail K=64 B=1 N=8192 = 1.0)",
        "corpus": "math",
        "tier": "T3",
        "kind": "experiment_record",
        "description": (
            f"Stage 1 working-memory K-cliff phase diagram v3 (GPU chunked) cell seed_{seed} of 3. "
            f"96 phase points (K x B x N = 8 K-values x 5 B-values x ~variable N) at torch.cuda. "
            f"OFF-DATA recompute (skunkworks .venv python): "
            f"n_pass={d['n_pass']} (>=20 PASS); n_pass_at_full_N={d['n_pass_at_full_N']} (>=6 PASS); "
            f"rail K=64 B=1 N=8192 observed={d['rail']} (>=0.95 PASS); "
            f"n_saturate={d['n_saturate']}; n_floor={d['n_floor']}; n_probe_cliffs={d['n_probe_cliffs']}; "
            f"arms_differ_count=96/96 (no arms identical); cardinality_ok=True (288/288); "
            f"substrate_only_ok=True. cliff_per_B identical across 3 seeds: K_cliff(B=1)=256, "
            f"K_cliff(B=2)=512, K_cliff(B=4)=1024, K_cliff(B=8)=2048, K_cliff(B=16)=4096. "
            f"Promotes at cross-seed AGG to chain-grade phase characterization "
            f"(math::T3/EXP_substrate_wm_multibank_K_cliff_phase_diagram_v3_GPU_chunked_CROSS_SEED_AGG)."
        ),
        "aliases": [
            f"wm_multibank_K_cliff_phase_diagram_v3_GPU_chunked_seed_{seed}_HARD_PASS_2026-06-28",
            f"wm_K_cliff_v3_GPU_seed_{seed}_torch_cuda_2026-06-28",
        ],
        "metadata": {
            "provenance_quality": "MEASURED",
            "cert_status": "middle_band",
            "cert_class": "mechanism_characterization",
            "verdict": "HARD_PASS",
            "verdict_subtype": "K_CLIFF_V3_PHASE_DIAGRAM_PROMOTES_AT_CROSS_SEED_AGG_TO_CHAIN_GRADE",
            "cell_commit": "unknown_GPU_chunked",
            "cell_path": f"experiments/exp_substrate_wm_multibank_K_cliff_phase_diagram_v3_GPU_chunked_seed_{seed}.py",
            "metrics_path": f"data/exp_substrate_wm_multibank_K_cliff_phase_diagram_v3_GPU_chunked_seed_{seed}/metrics.json",
            "atomized_by": ATOMIZED_BY,
            "atomized_date": ATOMIZED_DATE,
            "verified_off_data": True,
            "verified_off_data_evidence": (
                f"OFF-DATA recompute via .venv python on metrics.json detail: "
                f"n_pass={d['n_pass']}>=20, n_pass_at_full_N={d['n_pass_at_full_N']}>=6, rail={d['rail']}>=0.95, "
                f"arms_differ=96/96, cardinality_ok=True. K_cliff(B) = 256*B for B in {{1,2,4,8,16}} -- "
                f"identical pattern across all 3 seeds confirms by-construction-saturation NOT present "
                f"(probe_cliffs=0, no saturate-only points)."
            ),
            "n_seeds_run": 1,
            "n_seeds_planned_total": 3,
            "seed": seed,
            "regime": {
                "B_VALUES": [1, 2, 4, 8, 16],
                "K_cliff_per_B": WM_V3_CLIFF_PER_B,
                "rail_anchor": "K=64 B=1 N=8192 fullN",
                "backend": "torch.cuda",
                "n_phase_points": 96,
                "n_units_observed_per_seed": 288,
            },
            "per_seed_headlines": {
                "n_pass": d["n_pass"],
                "n_pass_at_full_N": d["n_pass_at_full_N"],
                "n_saturate": d["n_saturate"],
                "n_floor": d["n_floor"],
                "n_probe_cliffs": d["n_probe_cliffs"],
                "rail_K64_B1_N8192": d["rail"],
            },
            "gates_evaluated": {
                "n_pass_ge_20": True,
                "n_pass_at_full_N_ge_6": True,
                "rail_ge_0p95": True,
                "cardinality_ok": True,
                "arms_differ_96_of_96": True,
                "substrate_only_ok": True,
                "n_probe_cliffs_eq_0": True,
            },
            "cert_increment_delta": 0,
            "stage_1_coverage_status": "PARTIAL_TO_HIGH_AT_CROSS_SEED_AGG_K4096_multibank_phase_coverage",
            "discipline_tags": [
                "META_RULE_AC", "META_RULE_AE", "META_RULE_AF",
                "META_RULE_H", "META_RULE_J", "META_RULE_L",
                "Fix_28_per_arm_metrics_not_verdict_msg",
                "DISCRIMINATOR_MUST_SURVIVE_SCALE_USER_2026-06-26",
                "chunked_per_seed_architecture_USER_2026-06-28",
                "feedback_no_hallucinated_numbers_verify_on_disk_2026-06-27",
                "Fix_24_GPU_dispatch_must_actually_use_GPU",
            ],
            "supersedes": None,
            "ts_iso_atomized": ATOMIZED_DATE,
        },
    }


WM_V3_AGG_ATOM = {
    "id": "T3/EXP_substrate_wm_multibank_K_cliff_phase_diagram_v3_GPU_chunked_CROSS_SEED_AGG_3_of_3_HARD_PASS_K_cliff_256B_bit_exact_rail_1p0_chain_grade_phase_characterization_2026-06-28",
    "name": (
        "WM multi-bank K-cliff v3 GPU chunked CROSS-SEED 3-of-3 HARD_PASS -- "
        "chain-grade phase characterization (K_cliff = 256*B bit-exact across seeds; "
        "rail K=64 B=1 N=8192 = 1.0); +1 CERT"
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "capability_map",  # AtomKind.CAPABILITY_MAP (valid enum)
    "description": (
        "Stage 1 working-memory K-cliff phase diagram v3 (GPU torch.cuda chunked) cross-seed "
        "characterization (seeds 7, 13, 19; chunked-per-seed architecture). Each seed lands "
        "HARD_PASS independently on the same 96-phase-point sweep (K x B x N). "
        "OFF-DATA recompute confirms: "
        "n_pass=[20, 22, 20] all >= 20 hard band; n_pass_at_full_N=[9, 11, 9] all >= 6; "
        "rail K=64 B=1 N=8192 = [1.0, 1.0, 1.0] all >= 0.95; "
        "arms_differ_count = 96/96 every seed (no degenerate arms); "
        "cardinality_ok=True every seed (288/288 units); substrate_only_ok=True. "
        "PHASE STRUCTURE: K_cliff(B) = 256*B EXACTLY, bit-identical across all 3 seeds: "
        "K_cliff(B=1)=256, K_cliff(B=2)=512, K_cliff(B=4)=1024, K_cliff(B=8)=2048, K_cliff(B=16)=4096. "
        "This is a clean affine scaling law of K-cliff with bank-count B. "
        "CHAIN-GRADE PROMOTION rationale: "
        "(1) Discriminator fires 3/3 seeds at pre-registered band (n_pass>=20 hard, "
        "n_pass_at_full_N>=6 hard, rail>=0.95); "
        "(2) Cross-seed agreement BIT-EXACT on the headline phase structure (K_cliff per B); "
        "(3) substrate_only_ok=True asserts zero LLM at inference; "
        "(4) No by-construction-saturation (probe_cliffs=0 every seed); "
        "(5) GPU backend genuinely used (torch.cuda confirmed in per_seed.backend; gpu_mem_peak_mb tracked). "
        "Promotion to Stage 1 multi-bank WM K=4096 phase coverage HIGH "
        "(was PARTIAL per chain-grade portfolio: 'WM multi-bank K=4096'). "
        "STAGE 1 IMPLICATION: multi-bank working memory K-cliff is CHARACTERIZED at GPU scale; "
        "downstream WM-cell designs can rely on K_cap(B) ~ 256*B affine law at N=8192. "
        "M3 IMPLICATION: working-memory bank-count B trades linearly with K capacity (no superlinear "
        "regime found); this constrains downstream M3 attention-like compose to expect bounded "
        "K per bank with B chosen to match expected load."
    ),
    "aliases": [
        "wm_multibank_K_cliff_phase_diagram_v3_GPU_chunked_CROSS_SEED_AGG_3_of_3_HARD_PASS_2026-06-28",
        "wm_K_cliff_v3_chain_grade_phase_characterization_2026-06-28",
        "stage_1_multibank_WM_K_4096_phase_coverage_HIGH_2026-06-28",
    ],
    "metadata": {
        "provenance_quality": "MEASURED",
        "cert_status": "chain_grade",
        "cert_class": "phase_characterization",
        "verdict": "CROSS_SEED_3_OF_3_HARD_PASS_WM_K_CLIFF_V3_GPU_CHUNKED_CHAIN_GRADE_PHASE_CHARACTERIZATION",
        "verdict_subtype": "PHASE_CHARACTERIZATION_K_cliff_256B_AFFINE_LAW_BIT_EXACT_ACROSS_3_SEEDS_RAIL_1p0_GPU_torch_cuda_substrate_only",
        "atomized_by": ATOMIZED_BY,
        "atomized_date": ATOMIZED_DATE,
        "verified_off_data": True,
        "verified_off_data_evidence": (
            "OFF-DATA recompute via .venv python on all 3 sibling metrics.json detail: "
            "seed_7  n_pass=20 n_pass_at_full_N=9  rail=1.0 cliff_per_B={B=1:256,B=2:512,B=4:1024,B=8:2048,B=16:4096}; "
            "seed_13 n_pass=22 n_pass_at_full_N=11 rail=1.0 cliff_per_B={B=1:256,B=2:512,B=4:1024,B=8:2048,B=16:4096}; "
            "seed_19 n_pass=20 n_pass_at_full_N=9  rail=1.0 cliff_per_B={B=1:256,B=2:512,B=4:1024,B=8:2048,B=16:4096}. "
            "cliff_per_B BIT-IDENTICAL across all 3 seeds confirms a clean affine scaling law. "
            "arms_differ=96/96 all seeds; cardinality_ok=True all seeds; substrate_only_ok=True all seeds."
        ),
        "n_seeds_run": 3,
        "n_seeds_planned_total": 3,
        "seeds_landed": [7, 13, 19],
        "per_seed_atom_ids": {
            f"seed_{s}": f"math::T3/EXP_substrate_wm_multibank_K_cliff_phase_diagram_v3_GPU_chunked_seed_{s}_HARD_PASS_K_cliff_256B_torch_cuda_n_pass_{WM_V3_DATA[s]['n_pass']}_rail_K64B1N8192_1p0_2026-06-28"
            for s in WM_V3_SEEDS
        },
        "per_seed_metrics_paths": {
            f"seed_{s}": f"data/exp_substrate_wm_multibank_K_cliff_phase_diagram_v3_GPU_chunked_seed_{s}/metrics.json"
            for s in WM_V3_SEEDS
        },
        "regime": {
            "B_VALUES": [1, 2, 4, 8, 16],
            "rail_anchor": "K=64 B=1 N=8192",
            "K_cliff_law": "K_cliff(B) = 256 * B (bit-exact across all 3 seeds)",
            "backend": "torch.cuda",
            "n_phase_points_per_seed": 96,
            "n_units_observed_per_seed": 288,
            "n_units_aggregate": 864,
        },
        "cross_seed_stats": {
            "n_pass": [20, 22, 20],
            "n_pass_at_full_N": [9, 11, 9],
            "n_saturate": [5, 9, 7],
            "n_floor": [48, 47, 43],
            "n_probe_cliffs": [0, 0, 0],
            "rail_K64_B1_N8192": [1.0, 1.0, 1.0],
            "cliff_per_B_all_seeds_identical": True,
            "all_3_seeds_HARD_PASS": True,
            "all_3_seeds_cardinality_ok": True,
            "all_3_seeds_substrate_only_ok": True,
        },
        "promotion_gate_evaluation": {
            "gate_text": (
                "3/3 seeds HARD_PASS via pre-registered discriminators (n_pass>=20 hard, "
                "n_pass_at_full_N>=6, rail>=0.95); cliff_per_B bit-identical across seeds = clean "
                "affine scaling law characterization; no by-construction saturation (probe_cliffs=0); "
                "GPU torch.cuda genuinely engaged."
            ),
            "criteria_met": {
                "3_of_3_seeds_HARD_PASS": True,
                "cross_seed_cliff_pattern_bit_exact": True,
                "rail_saturates_pre_reg_band": True,
                "no_probe_cliff_phantoms": True,
                "GPU_torch_cuda_confirmed_in_per_seed_backend": True,
                "discriminator_survives_scale": True,
                "by_construction_saturation_gate_passed": True,
            },
            "tier_decision": "chain_grade_phase_characterization_at_AGG_CERT_plus_1",
            "tier_rationale": (
                "Phase-diagram CHARACTERIZED at GPU scale; cross-seed bit-exact agreement on "
                "the affine K_cliff(B) = 256*B law makes this a chain-grade phase characterization "
                "(not just MM). Per Director directive + cert-disposition framework, CERT +1 "
                "at the chain-grade tier for phase-characterization promotion of Stage 1 multi-bank "
                "WM K=4096 coverage PARTIAL -> HIGH."
            ),
        },
        "stage_1_coverage_status_promoted": "MULTI_BANK_WM_K_4096_PARTIAL_to_HIGH_2026-06-28",
        "M3_implication": (
            "Working-memory bank-count B trades linearly with K capacity (K_cap(B) ~ 256*B at N=8192). "
            "No superlinear regime found within tested B range. Downstream M3 attention-like cells "
            "should expect bounded K-per-bank, choosing B to match expected concurrent-item load."
        ),
        "cert_increment_delta": 1,
        "discipline_tags": [
            "META_RULE_AC", "META_RULE_AE", "META_RULE_AF",
            "META_RULE_H", "META_RULE_J", "META_RULE_L",
            "Fix_28_per_arm_metrics_not_verdict_msg",
            "DISCRIMINATOR_MUST_SURVIVE_SCALE_USER_2026-06-26",
            "chunked_per_seed_architecture_USER_2026-06-28",
            "feedback_no_hallucinated_numbers_verify_on_disk_2026-06-27",
            "Fix_24_GPU_dispatch_must_actually_use_GPU",
            "feedback_capability_dev_is_goal_cert_grade_is_instrument_USER_2026-06-19",
            "M3_milestone_glass_box_conversational",
        ],
        "supersedes": None,
        "ts_iso_atomized": ATOMIZED_DATE,
    },
}


# ============================================================
# STEP 3: cortex_hippo M=8192 3-seed HARD_FAIL (META_RULE_AF violation)
# ============================================================
CORTEX_HIPPO_DATA = {
    7:  {"FULL": 0.308837890625, "DIRECT": 0.308837890625, "NO_REPLAY": 0.0001220703125, "cortex_norm_full": 45.47652816772461, "cortex_norm_direct": 45.47652816772461},
    13: {"FULL": 0.3272705078125, "DIRECT": 0.3272705078125, "NO_REPLAY": 0.0001220703125, "cortex_norm_full": 45.280181884765625, "cortex_norm_direct": 45.280181884765625},
    19: {"FULL": 0.3233642578125, "DIRECT": 0.3233642578125, "NO_REPLAY": 0.0001220703125, "cortex_norm_full": 45.346351623535156, "cortex_norm_direct": 45.346351623535156},
}


def cortex_hippo_per_seed_atom(seed: int) -> dict:
    d = CORTEX_HIPPO_DATA[seed]
    return {
        "id": f"T3/EXP_substrate_cortex_hippo_handoff_chain_grade_M_8192_GPU_v1_seed_{seed}_HARD_FAIL_META_RULE_AF_FULL_eq_DIRECT_bit_exact_W_hippo_unused_in_FULL_path_2026-06-28",
        "name": f"Cortex-hippo handoff M=8192 GPU seed_{seed} HARD_FAIL (META_RULE_AF: FULL == DIRECT bit-exact)",
        "corpus": "math",
        "tier": "T3",
        "kind": "experiment_record",
        "description": (
            f"Stage 1 cortex-hippocampus handoff cell seed_{seed} of 3 (M=8192, N_h=4096, N_c=8192, "
            f"hippo_sparsity=0.1, N_replay=50, backend=torch.cuda). "
            f"Cell-author verdict_msg reads 'MIDDLE_BAND: transfer partial' BUT the per_seed arm "
            f"metrics reveal META_RULE_AF violation: ARM_FULL_HANDOFF.recall_cortex = "
            f"{d['FULL']} == ARM_DIRECT_CORTEX.recall_cortex = {d['DIRECT']} BIT-EXACT. "
            f"cortex_norm bit-exact too (FULL={d['cortex_norm_full']} == DIRECT={d['cortex_norm_direct']}). "
            f"NO_REPLAY arm = {d['NO_REPLAY']} (near zero as expected when hippo is bypassed). "
            f"This means the FULL handoff path produces IDENTICAL cortex state to the DIRECT path, "
            f"i.e. W_hippo (hippocampus weights) is unused / no-op in the FULL arm's code path. "
            f"The cell does NOT demonstrate cortex-hippo handoff -- it demonstrates that the cortex "
            f"update sums commutatively over replay items independent of hippo intermediate, which is "
            f"the SAME outcome as direct cortex write of the same item-codes. Cell-author "
            f"rationalization ('permutation-invariant sum') is post-hoc; pre-reg required a DIFFERENCE "
            f"between FULL and DIRECT. Honest negative: cell ruled HARD_FAIL by skunkworks "
            f"(over-rides cell-author MIDDLE_BAND framing which mis-read ratio_FULL_to_DIRECT=1.000 "
            f"as 'transfer' when it's actually 'identity = no handoff effect')."
        ),
        "aliases": [
            f"cortex_hippo_M_8192_GPU_seed_{seed}_META_RULE_AF_violation_HARD_FAIL_2026-06-28",
            f"cortex_hippo_handoff_seed_{seed}_FULL_eq_DIRECT_bit_exact_2026-06-28",
        ],
        "metadata": {
            "provenance_quality": "MEASURED",
            "cert_status": "hard_fail",
            "cert_class": "mechanism_test_design_failure",
            "verdict": "HARD_FAIL",
            "verdict_subtype": "META_RULE_AF_VIOLATION_FULL_HANDOFF_eq_DIRECT_CORTEX_BIT_EXACT_W_hippo_unused_in_FULL_path_cell_author_rationalization_is_post_hoc",
            "cell_path": f"experiments/exp_substrate_cortex_hippo_handoff_chain_grade_M_8192_GPU_v1_seed_{seed}.py",
            "metrics_path": f"data/exp_substrate_cortex_hippo_handoff_chain_grade_M_8192_GPU_v1_seed_{seed}/metrics.json",
            "atomized_by": ATOMIZED_BY,
            "atomized_date": ATOMIZED_DATE,
            "verified_off_data": True,
            "verified_off_data_evidence": (
                f"OFF-DATA recompute via .venv python on metrics.json per_seed[0].arms: "
                f"ARM_FULL_HANDOFF.recall_cortex = {d['FULL']}; "
                f"ARM_DIRECT_CORTEX.recall_cortex = {d['DIRECT']}; "
                f"ARM_NO_REPLAY.recall_cortex = {d['NO_REPLAY']}. "
                f"FULL == DIRECT bit-exact (same Python float repr). "
                f"cortex_norm: FULL={d['cortex_norm_full']} == DIRECT={d['cortex_norm_direct']} also bit-exact. "
                f"META_RULE_AF violation: pre-reg required FULL != DIRECT to demonstrate handoff effect; "
                f"observed FULL = DIRECT means cell-author code did not exercise the W_hippo path."
            ),
            "n_seeds_run": 1,
            "n_seeds_planned_total": 3,
            "seed": seed,
            "regime": {
                "M": 8192,
                "N_h": 4096,
                "N_c": 8192,
                "hippo_sparsity": 0.1,
                "N_replay": 50,
                "backend": "torch.cuda",
            },
            "per_seed_headlines": {
                "ARM_FULL_HANDOFF_recall_cortex": d["FULL"],
                "ARM_DIRECT_CORTEX_recall_cortex": d["DIRECT"],
                "ARM_NO_REPLAY_recall_cortex": d["NO_REPLAY"],
                "FULL_eq_DIRECT_bit_exact": True,
                "cortex_norm_FULL_eq_DIRECT_bit_exact": True,
            },
            "gates_evaluated": {
                "META_RULE_AF_arms_distinct": False,
                "FULL_strictly_greater_than_DIRECT": False,
                "ratio_FULL_to_DIRECT_eq_1": True,
                "alpha_simple_eq_1": True,
            },
            "cert_increment_delta": 0,
            "test_design_failure_summary": (
                "FULL arm code path does not exercise W_hippo; replays sum into cortex commutatively "
                "with no hippo-mediated retrieval gating. ARM_NO_REPLAY ~ 0 confirms cortex starts blank "
                "and is built solely by the replay loop -- but FULL replay produces the same cortex as "
                "DIRECT replay because the hippo W_h step is functionally a no-op for this setup."
            ),
            "recommended_redesign": [
                "Use noisy / sparsified / corrupted item cues at retrieval (not the original clean cue): "
                "DIRECT lookup will fail at corruption but FULL hippo path should denoise.",
                "Compare FULL vs DIRECT under PARTIAL cue or NEGATIVE cue regime (overlapping items).",
                "Atomic test: assert torch.allclose(cortex_FULL, cortex_DIRECT) is False at pre-reg time.",
                "Add a META_RULE_AF gate: bit-exact equality between FULL and any baseline arm is FATAL.",
            ],
            "discipline_tags": [
                "META_RULE_AF",
                "META_RULE_AF_AMENDED_FULL_eq_DIRECT_bit_exact_FATAL",
                "Fix_28_per_arm_metrics_not_verdict_msg",
                "honest_negative_HARD_FAIL_proven_bound",
                "discriminator_must_survive_scale_USER_2026-06-26",
                "feedback_no_hallucinated_numbers_verify_on_disk_2026-06-27",
                "chunked_per_seed_architecture_USER_2026-06-28",
            ],
            "supersedes": None,
            "ts_iso_atomized": ATOMIZED_DATE,
        },
    }


# Meta-amendment atom (meta partition) -- META_RULE_AF extension
CORTEX_HIPPO_META_AMENDMENT = {
    "id": "META_RULE_AF_AMENDMENT_FULL_vs_DIRECT_bit_exact_equality_FATAL_for_handoff_cells_2026-06-28",
    "name": "META_RULE_AF amendment: for FULL vs DIRECT vs NO_REPLAY arm-triples, bit-exact FULL == DIRECT is FATAL (no handoff demonstrated)",
    "corpus": "meta",
    "tier": "T1",
    "kind": "discipline_rule_amendment",
    "description": (
        "Amendment to META_RULE_AF (arms-must-differ): when cell pre-registers FULL vs DIRECT vs "
        "NO_REPLAY arm triples (transfer / handoff / replay-effect characterization cells), "
        "the auditor MUST check FULL == DIRECT bit-exact equality in addition to FULL == NO_REPLAY. "
        "Bit-exact FULL == DIRECT means the intermediate path (hippocampus / scratchpad / "
        "intermediate codebook) was NOT exercised; the cell does NOT demonstrate the handoff. "
        "This is FATAL (HARD_FAIL) even if the verdict-heuristic ratio_FULL_to_DIRECT == 1.0 "
        "is interpreted by the cell-author as 'PASS = transfer worked' -- ratio of 1.0 means "
        "the intermediate had no effect, NOT that the transfer succeeded. "
        "EXAMPLE TRIGGER: cortex_hippo_handoff_chain_grade_M_8192_GPU_v1 (3 seeds 2026-06-28). "
        "All 3 seeds showed ARM_FULL_HANDOFF.recall_cortex == ARM_DIRECT_CORTEX.recall_cortex "
        "bit-exact (0.308837890625 / 0.3272705078125 / 0.3233642578125). cortex_norm also bit-exact. "
        "Cell-author MIDDLE_BAND verdict was rationalized as 'transfer partial'; skunkworks "
        "over-ruled to HARD_FAIL per META_RULE_AF + this amendment. "
        "AUDITOR-CHECK ALGORITHM: "
        "  (1) Identify FULL / DIRECT / NO_REPLAY (or equivalent) arms in per_seed.arms[]. "
        "  (2) For numeric outcome metric M: if abs(M_FULL - M_DIRECT) < 1e-9 -> HARD_FAIL. "
        "  (3) Additionally check secondary metrics (norms, intermediate-state magnitudes); "
        "      bit-exact match on >= 2 metrics confirms intermediate is no-op. "
        "  (4) Override cell-author verdict if any of (2)/(3) trigger; rule HARD_FAIL with "
        "      cert_class = mechanism_test_design_failure."
    ),
    "aliases": [
        "META_RULE_AF_amend_FULL_eq_DIRECT_bit_exact_FATAL_2026-06-28",
        "META_RULE_AF_extension_handoff_cells_arm_triple_check_2026-06-28",
    ],
    "metadata": {
        "provenance_quality": "MEASURED",
        "cert_status": "discipline_rule",
        "cert_class": "discipline_rule_amendment",
        "verdict": "RULE_AMENDMENT_FROM_HARD_FAIL_CASE",
        "atomized_by": ATOMIZED_BY,
        "atomized_date": ATOMIZED_DATE,
        "supersedes": None,
        "amends": "META_RULE_AF",
        "trigger_case_atom_ids": [
            f"math::T3/EXP_substrate_cortex_hippo_handoff_chain_grade_M_8192_GPU_v1_seed_{s}_HARD_FAIL_META_RULE_AF_FULL_eq_DIRECT_bit_exact_W_hippo_unused_in_FULL_path_2026-06-28"
            for s in [7, 13, 19]
        ],
        "cert_increment_delta": 0,
        "discipline_tags": [
            "META_RULE_AF",
            "META_RULE_AF_AMENDED_FULL_eq_DIRECT_bit_exact_FATAL_2026-06-28",
            "Fix_28_per_arm_metrics_not_verdict_msg",
            "cert_owner_overrides_cell_author_verdict_when_arm_test_design_invalid",
        ],
        "ts_iso_atomized": ATOMIZED_DATE,
    },
}


# ============================================================
# STEP 4: ultrametric 3-seed chain-grade phase characterization with HONEST-DOWNWARD
# ============================================================
ULTRA_DATA = {
    7:  {"ultra_acc_mean": 0.595, "kmeans_acc_mean": 0.734, "random_acc_mean": 0.150, "delta_uk_mean": -0.139,
         "n_separable": 30, "n_chain_failure": 26, "n_ultra_advantage": 25, "n_discriminating": 55,
         "ultra_gap_mean": 0.105, "kmeans_gap_mean": 0.077, "n_points": 60},
    13: {"ultra_acc_mean": 0.598, "kmeans_acc_mean": 0.762, "random_acc_mean": 0.147, "delta_uk_mean": -0.164,
         "n_separable": 31, "n_chain_failure": 24, "n_ultra_advantage": 21, "n_discriminating": 49,
         "ultra_gap_mean": 0.106, "kmeans_gap_mean": 0.085, "n_points": 60},
    19: {"ultra_acc_mean": 0.595, "kmeans_acc_mean": 0.715, "random_acc_mean": 0.143, "delta_uk_mean": -0.120,
         "n_separable": 31, "n_chain_failure": 25, "n_ultra_advantage": 22, "n_discriminating": 50,
         "ultra_gap_mean": 0.106, "kmeans_gap_mean": 0.082, "n_points": 60},
}


def ultra_per_seed_atom(seed: int) -> dict:
    d = ULTRA_DATA[seed]
    return {
        "id": f"T3/EXP_substrate_ultrametric_clustering_phase_diagram_v1_seed_{seed}_HARD_PASS_phase_coverage_MID_to_HIGH_ULTRA_advantage_in_sub_regime_dominated_overall_by_KMEANS_2026-06-28",
        "name": (
            f"Ultrametric clustering phase diagram v1 seed_{seed} HARD_PASS (phase-coverage "
            f"MID->HIGH; ULTRA advantage in {d['n_ultra_advantage']}/60 of phase space but "
            f"DOMINATED by KMEANS on average delta_uk={d['delta_uk_mean']})"
        ),
        "corpus": "math",
        "tier": "T3",
        "kind": "experiment_record",
        "description": (
            f"Stage 2 ultrametric-clustering phase diagram v1 cell seed_{seed} of 3. 60 phase points "
            f"(N_CLUSTERS x CLUSTER_SIZE x N x TREE_DEPTH). "
            f"OFF-DATA recompute (skunkworks .venv python): "
            f"ultra_acc_mean={d['ultra_acc_mean']} kmeans_acc_mean={d['kmeans_acc_mean']} "
            f"random_acc_mean={d['random_acc_mean']} delta_uk_mean={d['delta_uk_mean']}. "
            f"n_separable(ULTRA>=0.95)={d['n_separable']}/60 (>=12 PASS); "
            f"n_chain_failure(d_uk<=-0.20)={d['n_chain_failure']}/60 (>=12 PASS); "
            f"n_ultra_advantage(d_uk>=0.10)={d['n_ultra_advantage']}/60 (>=12 PASS); "
            f"n_discriminating(|d_uk|>0.05)={d['n_discriminating']}/60 (>=30 PASS); "
            f"ultra_gap_mean={d['ultra_gap_mean']} kmeans_gap_mean={d['kmeans_gap_mean']}. "
            f"HONEST CHARACTERIZATION: phase diagram MID->HIGH coverage achieved (>=20% of grid in each "
            f"regime + >=50% discriminating overall). HOWEVER directional mean delta_uk is NEGATIVE "
            f"({d['delta_uk_mean']}) -- ULTRA is DOMINATED by KMEANS in {60 - d['n_ultra_advantage']}/60 "
            f"= {100*(60 - d['n_ultra_advantage'])/60:.1f}% of phase space; ULTRA wins in "
            f"{d['n_ultra_advantage']}/60 = {100*d['n_ultra_advantage']/60:.1f}%. Phase characterization "
            f"is real but headline 'ULTRA WINS' framing would be incorrect."
        ),
        "aliases": [
            f"ultrametric_clustering_phase_diagram_v1_seed_{seed}_HARD_PASS_2026-06-28",
            f"ultrametric_seed_{seed}_phase_coverage_with_directional_downward_caveat_2026-06-28",
        ],
        "metadata": {
            "provenance_quality": "MEASURED",
            "cert_status": "middle_band",
            "cert_class": "phase_characterization_with_directional_downward_caveat",
            "verdict": "HARD_PASS_phase_coverage_with_HONEST_DOWNWARD_directional_framing",
            "verdict_subtype": "PHASE_COVERAGE_MID_TO_HIGH_BUT_ULTRA_DOMINATED_BY_KMEANS_ON_AVERAGE_PROMOTES_AT_CROSS_SEED_AGG_TO_chain_grade_phase_characterization",
            "cell_path": f"experiments/exp_substrate_ultrametric_clustering_phase_diagram_v1_seed_{seed}.py",
            "metrics_path": f"data/exp_substrate_ultrametric_clustering_phase_diagram_v1_seed_{seed}/metrics.json",
            "atomized_by": ATOMIZED_BY,
            "atomized_date": ATOMIZED_DATE,
            "verified_off_data": True,
            "verified_off_data_evidence": (
                f"OFF-DATA recompute on metrics.json verdict_msg: ultra={d['ultra_acc_mean']} < kmeans={d['kmeans_acc_mean']} "
                f"(delta_uk={d['delta_uk_mean']}); n_separable={d['n_separable']}/60>=12 PASS; "
                f"n_chain_failure={d['n_chain_failure']}/60>=12 PASS; n_ultra_advantage={d['n_ultra_advantage']}/60>=12 PASS; "
                f"n_discriminating={d['n_discriminating']}/60>=30 PASS. Discriminator FIRES at pre-reg bands "
                f"but directional mean is downward."
            ),
            "n_seeds_run": 1,
            "n_seeds_planned_total": 3,
            "seed": seed,
            "regime": {
                "n_phase_points": 60,
                "TREE_DEPTH": "see metrics.json",
            },
            "per_seed_headlines": {
                "ultra_acc_mean": d["ultra_acc_mean"],
                "kmeans_acc_mean": d["kmeans_acc_mean"],
                "delta_uk_mean": d["delta_uk_mean"],
                "n_separable": d["n_separable"],
                "n_chain_failure": d["n_chain_failure"],
                "n_ultra_advantage": d["n_ultra_advantage"],
                "n_discriminating": d["n_discriminating"],
                "pct_phase_space_ultra_advantage": round(100 * d["n_ultra_advantage"] / 60, 1),
                "pct_phase_space_ultra_dominated": round(100 * (60 - d["n_ultra_advantage"]) / 60, 1),
            },
            "gates_evaluated": {
                "n_separable_ge_12": True,
                "n_chain_failure_ge_12": True,
                "n_ultra_advantage_ge_12": True,
                "n_discriminating_ge_30": True,
                "directional_mean_ULTRA_beats_KMEANS": False,
            },
            "cert_increment_delta": 0,
            "honest_downward_framing": (
                f"Phase-diagram coverage discriminator FIRES (all 4 phase-cardinality bands met). "
                f"HOWEVER directional mean delta_uk_acc_mean = {d['delta_uk_mean']} (negative) -- "
                f"on average ULTRA is BEATEN BY KMEANS. ULTRA wins only in {d['n_ultra_advantage']}/60 "
                f"= {100*d['n_ultra_advantage']/60:.1f}% of phase space (the 'hierarchical-advantage' regime); "
                f"the other ~{round(100*(60 - d['n_ultra_advantage'])/60)}% is either separable (KMEANS wins) or "
                f"chain-failure regime."
            ),
            "discipline_tags": [
                "META_RULE_AC", "META_RULE_AE", "META_RULE_J", "META_RULE_L",
                "Fix_28_per_arm_metrics_not_verdict_msg",
                "feedback_no_hallucinated_numbers_verify_on_disk_2026-06-27",
                "anti_inflation_bias_directional_mean_negative_does_not_become_ultra_wins_claim",
                "anti_negativity_bias_phase_coverage_still_chain_grade_eligible_at_AGG",
                "chunked_per_seed_architecture_USER_2026-06-28",
            ],
            "supersedes": None,
            "ts_iso_atomized": ATOMIZED_DATE,
        },
    }


ULTRA_AGG_ATOM = {
    "id": "T3/EXP_substrate_ultrametric_clustering_phase_diagram_v1_CROSS_SEED_AGG_3_of_3_HARD_PASS_chain_grade_phase_characterization_with_HONEST_DOWNWARD_ULTRA_dominated_by_KMEANS_60_pct_2026-06-28",
    "name": (
        "Ultrametric clustering phase-diagram v1 CROSS-SEED 3-of-3 HARD_PASS -- "
        "chain-grade phase characterization with HONEST-DOWNWARD: ULTRA wins in "
        "35-42% of phase space; DOMINATED by KMEANS on average. CERT +1 for "
        "phase-characterization promotion (Stage 2 coverage MID -> HIGH)"
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "capability_map",  # AtomKind.CAPABILITY_MAP
    "description": (
        "Stage 2 ultrametric-clustering phase diagram v1 cross-seed characterization (seeds 7, 13, 19). "
        "Each seed lands HARD_PASS at the discriminator bands. OFF-DATA recompute (skunkworks): "
        "all 4 phase-cardinality gates PASS for every seed (n_separable [30,31,31]>=12; "
        "n_chain_failure [26,24,25]>=12; n_ultra_advantage [25,21,22]>=12; n_discriminating [55,49,50]>=30). "
        "Cross-seed regime structure CONSISTENT: separable ~50-52%, chain_failure ~40-43%, "
        "ultra_advantage ~35-42%, discriminating ~82-92%. "
        "HONEST-DOWNWARD HEADLINE: ULTRA is DOMINATED by KMEANS on average across all 3 seeds: "
        "ultra_acc_mean [0.595, 0.598, 0.595] < kmeans_acc_mean [0.734, 0.762, 0.715]; "
        "delta_uk_acc_mean [-0.139, -0.164, -0.120] consistently negative. "
        "ULTRA wins only in the 'hierarchical-advantage' sub-regime (~35-42% of phase points). "
        "CHAIN-GRADE PROMOTION rationale: "
        "(1) Discriminator FIRES 3/3 seeds at pre-registered phase-cardinality bands; "
        "(2) Cross-seed regime structure stable (not seed-7 cherry-pick); "
        "(3) Director rule explicitly: 'if 3-seed agreement holds AND ultra_advantage > 20% (not at "
        "threshold), tier = chain_grade_phase_characterization'. Ultra_advantage 35-42% is well above "
        "20% threshold (12/60) with margin; "
        "(4) The CHARACTERIZATION is real (where ULTRA wins vs loses is now mapped); "
        "the HEADLINE is honest-downward ('ULTRA wins in a sub-regime; dominated overall'). "
        "Stage 2 ULTRAMETRIC clustering phase coverage MID -> HIGH per cert-disposition framework. "
        "M3 IMPLICATION: ultrametric clustering is NOT a default-superior primitive; pick KMEANS by "
        "default unless the regime is known to be 'hierarchical-advantage' (deep tree + specific N/cluster_size "
        "ratios in the ~35-42% sub-regime characterized here). Saves wasted compute on chain_failure "
        "regime (~40% of phase space where ULTRA HARMS performance)."
    ),
    "aliases": [
        "ultrametric_clustering_phase_diagram_v1_CROSS_SEED_AGG_3_of_3_HARD_PASS_chain_grade_phase_characterization_2026-06-28",
        "stage_2_ultrametric_phase_coverage_MID_to_HIGH_with_honest_downward_2026-06-28",
        "ULTRA_dominated_by_KMEANS_60_pct_phase_space_wins_in_35_to_42_pct_sub_regime_2026-06-28",
    ],
    "metadata": {
        "provenance_quality": "MEASURED",
        "cert_status": "chain_grade",
        "cert_class": "phase_characterization_with_honest_downward",
        "verdict": "CROSS_SEED_3_OF_3_HARD_PASS_ULTRAMETRIC_PHASE_DIAGRAM_chain_grade_with_HONEST_DOWNWARD_ULTRA_dominated_by_KMEANS",
        "verdict_subtype": "PHASE_CHARACTERIZATION_CHAIN_GRADE_AT_AGG_BUT_DIRECTIONAL_HEADLINE_DOWNWARD_ULTRA_wins_only_in_35_to_42_pct_sub_regime_anti_inflation_bias_load_bearing",
        "atomized_by": ATOMIZED_BY,
        "atomized_date": ATOMIZED_DATE,
        "verified_off_data": True,
        "verified_off_data_evidence": (
            "OFF-DATA recompute via .venv python on all 3 sibling metrics.json verdict_msg: "
            "seed_7  ultra=0.595 kmeans=0.734 delta_uk=-0.139 n_sep=30 n_chf=26 n_adv=25 n_disc=55; "
            "seed_13 ultra=0.598 kmeans=0.762 delta_uk=-0.164 n_sep=31 n_chf=24 n_adv=21 n_disc=49; "
            "seed_19 ultra=0.595 kmeans=0.715 delta_uk=-0.120 n_sep=31 n_chf=25 n_adv=22 n_disc=50. "
            "Cross-seed: all 4 phase-cardinality gates fire all 3 seeds; ultra_acc_mean stable at ~0.595-0.598; "
            "delta_uk_mean consistently negative ~-0.12 to -0.16; ultra_advantage cardinality 21-25/60 (35-42%) "
            "well above 20% pre-reg threshold but below KMEANS-wins regime (50-52% separable). "
            "Phase regime cardinality stable across seeds = not a seed-7 cherry-pick."
        ),
        "n_seeds_run": 3,
        "n_seeds_planned_total": 3,
        "seeds_landed": [7, 13, 19],
        "per_seed_atom_ids": {
            f"seed_{s}": f"math::T3/EXP_substrate_ultrametric_clustering_phase_diagram_v1_seed_{s}_HARD_PASS_phase_coverage_MID_to_HIGH_ULTRA_advantage_in_sub_regime_dominated_overall_by_KMEANS_2026-06-28"
            for s in [7, 13, 19]
        },
        "per_seed_metrics_paths": {
            f"seed_{s}": f"data/exp_substrate_ultrametric_clustering_phase_diagram_v1_seed_{s}/metrics.json"
            for s in [7, 13, 19]
        },
        "regime": {
            "n_phase_points_per_seed": 60,
        },
        "cross_seed_stats": {
            "ultra_acc_mean": [0.595, 0.598, 0.595],
            "kmeans_acc_mean": [0.734, 0.762, 0.715],
            "random_acc_mean": [0.150, 0.147, 0.143],
            "delta_uk_acc_mean": [-0.139, -0.164, -0.120],
            "n_separable_ge_0p95": [30, 31, 31],
            "n_chain_failure_dukle_minus_0p20": [26, 24, 25],
            "n_ultra_advantage_dukge_0p10": [25, 21, 22],
            "n_discriminating_abs_duk_gt_0p05": [55, 49, 50],
            "pct_phase_ultra_advantage": [41.7, 35.0, 36.7],
            "pct_phase_ultra_dominated_or_neutral": [58.3, 65.0, 63.3],
            "all_3_seeds_HARD_PASS_at_discriminator_bands": True,
            "directional_mean_ULTRA_beats_KMEANS": False,
            "regime_cardinality_stable_across_seeds_not_cherry_pick": True,
        },
        "promotion_gate_evaluation": {
            "gate_text": (
                "Per Director directive 2026-06-28: 'if 3-seed cross-seed agreement holds AND "
                "ultra_advantage > 20% (not at threshold), tier = chain_grade_phase_characterization +1; "
                "else MEASURED_MECHANISM.' Ultra_advantage cardinality 35-42% across 3 seeds is WELL "
                "above 20% threshold with margin; regime structure consistent across seeds."
            ),
            "criteria_met": {
                "3_of_3_seeds_HARD_PASS": True,
                "ultra_advantage_above_20_pct_with_margin": True,
                "regime_structure_consistent_across_seeds": True,
                "anti_inflation_caveat_directional_mean_downward_documented": True,
                "discriminator_bands_at_pre_reg": True,
            },
            "tier_decision": "chain_grade_phase_characterization_with_honest_downward_caveat_CERT_plus_1",
            "tier_rationale": (
                "Director rule explicitly authorizes chain-grade when ultra_advantage > 20%-with-margin "
                "AND 3-seed agreement holds. Both gates met. CERT +1 at phase-characterization tier. "
                "HONEST-DOWNWARD framing baked into atom: directional mean is negative; ULTRA is sub-regime "
                "win, not headline win. Anti-inflation discipline observed (we do NOT claim 'ULTRA "
                "beats KMEANS')."
            ),
        },
        "stage_2_coverage_status_promoted": "ULTRAMETRIC_CLUSTERING_PHASE_COVERAGE_MID_to_HIGH_2026-06-28",
        "composes_with": [
            "Stage 3 cortex schema chain-grade primitive (per Director rationale): "
            "ultrametric provides a phase-typed regime characterization that the schema primitive "
            "can route around (use KMEANS in separable; use ULTRA in hierarchical-advantage)."
        ],
        "M3_implication": (
            "Ultrametric clustering is a SUB-REGIME primitive (~35-42% of phase space). "
            "Default M3 cells should pick KMEANS unless regime is known to be hierarchical-advantage. "
            "This characterization saves ~58-65% of compute on regimes where ULTRA loses to or harms KMEANS."
        ),
        "cert_increment_delta": 1,
        "discipline_tags": [
            "META_RULE_AC", "META_RULE_AE", "META_RULE_J", "META_RULE_L",
            "Fix_28_per_arm_metrics_not_verdict_msg",
            "feedback_no_hallucinated_numbers_verify_on_disk_2026-06-27",
            "anti_inflation_bias_directional_mean_negative_documented",
            "anti_negativity_bias_phase_coverage_still_chain_grade_eligible_at_AGG",
            "chunked_per_seed_architecture_USER_2026-06-28",
            "feedback_capability_dev_is_goal_cert_grade_is_instrument_USER_2026-06-19",
        ],
        "supersedes": None,
        "ts_iso_atomized": ATOMIZED_DATE,
    },
}


# ============================================================
# STEP 5: schema exemplar-bayes 3-seed MIDDLE_BAND (phase fill, MM)
# ============================================================
SCHEMA_DATA = {
    7:  {"lift_pts": 38, "avg_bayes_minus_nn": 0.300, "capacity_scaling_delta": 0.000, "random_arm_pathology_pts": 0,
         "low_load_sat_met": True, "cliff_observable": False, "capacity_scaling_met": False, "n_combos": 60},
    13: {"lift_pts": 36, "avg_bayes_minus_nn": 0.306, "capacity_scaling_delta": 0.010, "random_arm_pathology_pts": 0,
         "low_load_sat_met": True, "cliff_observable": False, "capacity_scaling_met": False, "n_combos": 60},
    19: {"lift_pts": 41, "avg_bayes_minus_nn": 0.327, "capacity_scaling_delta": 0.005, "random_arm_pathology_pts": 1,
         "low_load_sat_met": True, "cliff_observable": False, "capacity_scaling_met": False, "n_combos": 60},
}


def schema_per_seed_atom(seed: int) -> dict:
    d = SCHEMA_DATA[seed]
    return {
        "id": f"T3/EXP_substrate_schema_exemplar_bayes_phase_diagram_v1_seed_{seed}_MIDDLE_BAND_lift_pts_{d['lift_pts']}_60_avg_bayes_minus_nn_{int(d['avg_bayes_minus_nn']*1000)}_capacity_scaling_unmet_2026-06-28",
        "name": (
            f"Schema exemplar-Bayes phase diagram v1 seed_{seed} MIDDLE_BAND "
            f"(lift_pts={d['lift_pts']}/60; capacity_scaling unmet delta={d['capacity_scaling_delta']})"
        ),
        "corpus": "math",
        "tier": "T3",
        "kind": "experiment_record",
        "description": (
            f"Stage 2 schema exemplar-Bayes phase diagram v1 cell seed_{seed} of 3. "
            f"60 phase points. OFF-DATA recompute (skunkworks .venv python): "
            f"lift_pts={d['lift_pts']}/60 (BAYES > NN); avg_bayes_minus_nn={d['avg_bayes_minus_nn']}; "
            f"low_load_saturate_met={d['low_load_sat_met']}; cliff_observable={d['cliff_observable']}; "
            f"capacity_scaling_met={d['capacity_scaling_met']} (delta={d['capacity_scaling_delta']}); "
            f"random_arm_pathology_pts={d['random_arm_pathology_pts']}; arms_identical=False; "
            f"regime_flip=False. MIDDLE_BAND ruling honest: BAYES does lift over NN on average "
            f"({d['avg_bayes_minus_nn']:.3f} pp) and across {d['lift_pts']}/60 phase points, but "
            f"capacity-scaling (the capacity-vs-N discriminator) does NOT meet pre-reg band -- the "
            f"mechanism doesn't cleanly scale. Cliff_observable=False means no decisive K-cliff in "
            f"the schema-Bayes regime. Phase characterization MM; no CERT delta."
        ),
        "aliases": [
            f"schema_exemplar_bayes_phase_diagram_v1_seed_{seed}_MIDDLE_BAND_2026-06-28",
        ],
        "metadata": {
            "provenance_quality": "MEASURED",
            "cert_status": "middle_band",
            "cert_class": "mechanism_characterization",
            "verdict": "MIDDLE_BAND",
            "verdict_subtype": "schema_bayes_lift_real_but_capacity_scaling_unmet_cliff_not_observable_phase_characterization_MM",
            "cell_path": f"experiments/exp_substrate_schema_exemplar_bayes_phase_diagram_v1_seed_{seed}.py",
            "metrics_path": f"data/exp_substrate_schema_exemplar_bayes_phase_diagram_v1_seed_{seed}/metrics.json",
            "atomized_by": ATOMIZED_BY,
            "atomized_date": ATOMIZED_DATE,
            "verified_off_data": True,
            "verified_off_data_evidence": (
                f"OFF-DATA recompute on metrics.json verdict_msg: "
                f"lift_pts={d['lift_pts']}/60; avg_bayes_minus_nn={d['avg_bayes_minus_nn']}; "
                f"capacity_scaling_met=False (delta={d['capacity_scaling_delta']}); "
                f"low_load_sat_met=True; cliff_observable=False; arms_identical=False; "
                f"random_arm_pathology_pts={d['random_arm_pathology_pts']}. MIDDLE_BAND verdict "
                f"confirmed."
            ),
            "n_seeds_run": 1,
            "n_seeds_planned_total": 3,
            "seed": seed,
            "regime": {"n_phase_points": 60},
            "per_seed_headlines": {
                "lift_pts_of_60": d["lift_pts"],
                "avg_bayes_minus_nn": d["avg_bayes_minus_nn"],
                "capacity_scaling_delta": d["capacity_scaling_delta"],
                "low_load_sat_met": d["low_load_sat_met"],
                "cliff_observable": d["cliff_observable"],
                "capacity_scaling_met": d["capacity_scaling_met"],
                "random_arm_pathology_pts": d["random_arm_pathology_pts"],
            },
            "cert_increment_delta": 0,
            "discipline_tags": [
                "META_RULE_AC", "META_RULE_AE", "META_RULE_J", "META_RULE_L",
                "Fix_28_per_arm_metrics_not_verdict_msg",
                "feedback_no_hallucinated_numbers_verify_on_disk_2026-06-27",
                "chunked_per_seed_architecture_USER_2026-06-28",
                "honest_MIDDLE_BAND_3_seed_consistent",
            ],
            "supersedes": None,
            "ts_iso_atomized": ATOMIZED_DATE,
        },
    }


SCHEMA_AGG_ATOM = {
    "id": "T3/EXP_substrate_schema_exemplar_bayes_phase_diagram_v1_CROSS_SEED_AGG_3_of_3_MIDDLE_BAND_phase_characterization_MM_lift_real_but_capacity_scaling_unmet_2026-06-28",
    "name": (
        "Schema exemplar-Bayes phase-diagram v1 CROSS-SEED 3-of-3 MIDDLE_BAND -- "
        "phase-characterization MM (BAYES lift real ~0.30 pp; capacity-scaling unmet); "
        "no CERT delta"
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "capability_map",  # phase characterization fits capability_map at AGG
    "description": (
        "Stage 2 schema exemplar-Bayes phase-diagram v1 cross-seed characterization (seeds 7, 13, 19). "
        "All 3 seeds land MIDDLE_BAND honestly: BAYES does lift over NN by 0.30-0.33 pp on average "
        "across 36-41/60 phase points; HOWEVER the capacity-scaling discriminator does not fire "
        "(delta 0.000 / 0.010 / 0.005, well below pre-reg band) and no K-cliff is observable. "
        "Cross-seed structure CONSISTENT (not seed-7 cherry-pick): lift_pts in tight range "
        "[36, 38, 41] of 60; avg_bayes_minus_nn [0.300, 0.306, 0.327]; arms_identical=False all seeds. "
        "MIDDLE_BAND outcome cross-seed = phase-characterization MM at AGG. No CERT delta. "
        "Future drill: if encoder track or higher-N regime un-saturates the low_load regime, "
        "the capacity-scaling cliff may become observable -- 3-seed MM here documents the "
        "non-saturated finding cleanly."
    ),
    "aliases": [
        "schema_exemplar_bayes_phase_diagram_v1_CROSS_SEED_AGG_3_of_3_MIDDLE_BAND_2026-06-28",
        "schema_bayes_phase_characterization_MM_capacity_scaling_unmet_2026-06-28",
    ],
    "metadata": {
        "provenance_quality": "MEASURED",
        "cert_status": "middle_band",
        "cert_class": "phase_characterization",
        "verdict": "CROSS_SEED_3_OF_3_MIDDLE_BAND_SCHEMA_BAYES_PHASE_CHARACTERIZATION_MM",
        "atomized_by": ATOMIZED_BY,
        "atomized_date": ATOMIZED_DATE,
        "verified_off_data": True,
        "verified_off_data_evidence": (
            "OFF-DATA on all 3 sibling metrics.json: "
            "seed_7  lift_pts=38/60 avg=0.300 cap_scaling_delta=0.000; "
            "seed_13 lift_pts=36/60 avg=0.306 cap_scaling_delta=0.010; "
            "seed_19 lift_pts=41/60 avg=0.327 cap_scaling_delta=0.005. "
            "All 3 cliff_observable=False; capacity_scaling_met=False. "
            "Cross-seed lift_pts in [36, 41] tight range; avg in [0.300, 0.327] tight range."
        ),
        "n_seeds_run": 3,
        "n_seeds_planned_total": 3,
        "seeds_landed": [7, 13, 19],
        "per_seed_atom_ids": {
            f"seed_{s}": f"math::T3/EXP_substrate_schema_exemplar_bayes_phase_diagram_v1_seed_{s}_MIDDLE_BAND_lift_pts_{SCHEMA_DATA[s]['lift_pts']}_60_avg_bayes_minus_nn_{int(SCHEMA_DATA[s]['avg_bayes_minus_nn']*1000)}_capacity_scaling_unmet_2026-06-28"
            for s in [7, 13, 19]
        },
        "cross_seed_stats": {
            "lift_pts_of_60": [38, 36, 41],
            "avg_bayes_minus_nn": [0.300, 0.306, 0.327],
            "capacity_scaling_delta": [0.000, 0.010, 0.005],
            "low_load_sat_met": [True, True, True],
            "cliff_observable": [False, False, False],
            "capacity_scaling_met": [False, False, False],
            "all_3_seeds_MIDDLE_BAND": True,
        },
        "cert_increment_delta": 0,
        "discipline_tags": [
            "META_RULE_AC", "META_RULE_AE", "META_RULE_J", "META_RULE_L",
            "Fix_28_per_arm_metrics_not_verdict_msg",
            "feedback_no_hallucinated_numbers_verify_on_disk_2026-06-27",
            "chunked_per_seed_architecture_USER_2026-06-28",
            "honest_MIDDLE_BAND_3_seed_consistent_phase_characterization_MM",
        ],
        "supersedes": None,
        "ts_iso_atomized": ATOMIZED_DATE,
    },
}


# ============================================================
# A5 plumbing
# ============================================================

def append_jsonl_a5(path: Path, new_row: dict, label: str):
    print(f"[A5] {label}: path={path}")
    assert path.exists(), f"target missing: {path}"
    with open(path, "r", encoding="utf-8") as f:
        pre_lines = f.read().splitlines()
    pre_count = len(pre_lines)
    for i, ln in enumerate(pre_lines):
        if not ln.strip():
            continue
        try:
            json.loads(ln)
        except Exception as e:
            raise RuntimeError(f"PRE integrity fail {label} line {i+1}: {e}")
    new_line = json.dumps(new_row, ensure_ascii=True)
    parsed_back = json.loads(new_line)
    if "id" in new_row:
        assert parsed_back.get("id") == new_row.get("id")
    if "atom_id" in new_row:
        assert parsed_back.get("atom_id") == new_row.get("atom_id")
    out_lines = pre_lines + [new_line]
    out_text = "\n".join(out_lines) + "\n"
    tmp = path.with_suffix(path.suffix + ".tmp_a5")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(out_text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(str(tmp), str(path))
    with open(path, "r", encoding="utf-8") as f:
        post_lines = f.read().splitlines()
    post_count = len(post_lines)
    assert post_count == pre_count + 1, f"count delta {pre_count}->{post_count}"
    for i, ln in enumerate(post_lines):
        if not ln.strip():
            continue
        try:
            json.loads(ln)
        except Exception as e:
            raise RuntimeError(f"POST integrity fail {label} line {i+1}: {e}")
    tail = json.loads(post_lines[-1])
    if "id" in new_row:
        assert tail["id"] == new_row["id"]
    if "atom_id" in new_row:
        assert tail["atom_id"] == new_row["atom_id"]
    print(f"[A5] {label}: OK pre={pre_count} post={post_count}")
    return post_count


def _ledger_row(idx: int, atom: dict, op: str, cert_status: str, cert_class: str, verdict: str, delta: int, note: str, metrics_path: str = None, cell_commit: str = None) -> dict:
    referent = {"atom_qualified_id": f"{atom['corpus']}::{atom['id']}"}
    if metrics_path:
        referent["metrics_path"] = metrics_path
    if cell_commit:
        referent["cell_commit"] = cell_commit
    return {
        "ts": time.time() + 0.001 * idx,
        "op": op,
        "atom_id": f"{atom['corpus']}::{atom['id']}",
        "cert_status": cert_status,
        "cert_class": cert_class,
        "verified_off_data": True,
        "atomized_by": ATOMIZED_BY,
        "cell_commit": cell_commit,
        "verdict": verdict,
        "cert_increment_delta": delta,
        "cv": None,
        "referent_pointer": referent,
        "supersedes": None,
        "note": note,
    }


def main():
    print("=" * 78)
    print(f"A5 BATCH ATOMIZE {ATOMIZED_BY}")
    print(f"target ATOM writes: 4 (Step 2 per-seed) + 1 (Step 2 AGG +1) + ")
    print(f"                    3 (Step 3 per-seed HF) + 1 (Step 3 META amendment) + ")
    print(f"                    3 (Step 4 per-seed) + 1 (Step 4 AGG +1) + ")
    print(f"                    3 (Step 5 per-seed MB) + 1 (Step 5 AGG MM)")
    print(f"Predicted CERT delta = +2 (Step 2 WM v3 AGG +1, Step 4 ultrametric AGG +1)")
    print("=" * 78)

    # Build atom lists
    wm_atoms = [wm_v3_per_seed_atom(s) for s in WM_V3_SEEDS] + [WM_V3_AGG_ATOM]
    cortex_per_seed = [cortex_hippo_per_seed_atom(s) for s in [7, 13, 19]]
    ultra_per_seed = [ultra_per_seed_atom(s) for s in [7, 13, 19]]
    schema_per_seed = [schema_per_seed_atom(s) for s in [7, 13, 19]]

    # Append all math atoms
    math_writes = [
        *[(a, f"wm_v3_seed_{s}") for s, a in zip(WM_V3_SEEDS, wm_atoms[:3])],
        (wm_atoms[3], "wm_v3_AGG_+1"),
        *[(a, f"cortex_hippo_seed_{s}_HF") for s, a in zip([7, 13, 19], cortex_per_seed)],
        *[(a, f"ultrametric_seed_{s}") for s, a in zip([7, 13, 19], ultra_per_seed)],
        (ULTRA_AGG_ATOM, "ultrametric_AGG_+1"),
        *[(a, f"schema_seed_{s}_MB") for s, a in zip([7, 13, 19], schema_per_seed)],
        (SCHEMA_AGG_ATOM, "schema_AGG_MM"),
    ]
    meta_writes = [
        (CORTEX_HIPPO_META_AMENDMENT, "META_RULE_AF_amendment"),
    ]

    for atom, label in math_writes:
        append_jsonl_a5(MATH_ATOMS, atom, f"math/atoms.jsonl ({label})")
    for atom, label in meta_writes:
        append_jsonl_a5(META_ATOMS, atom, f"meta/atoms.jsonl ({label})")

    # Now ledger rows
    ledger_rows = []
    idx = 0
    # WM v3
    for s, a in zip(WM_V3_SEEDS, wm_atoms[:3]):
        ledger_rows.append(_ledger_row(
            idx, a, "cert_ruling", "middle_band", "mechanism_characterization",
            f"WM_K_CLIFF_V3_GPU_seed_{s}_HARD_PASS_per_cell_promotes_at_AGG",
            0, f"wm_v3_seed_{s} HARD_PASS per-cell; CERT delta=0; promotes at AGG",
            metrics_path=a["metadata"]["metrics_path"],
            cell_commit=a["metadata"].get("cell_commit"),
        ))
        idx += 1
    ledger_rows.append(_ledger_row(
        idx, wm_atoms[3], "cert_ruling_promotion_phase_characterization",
        "chain_grade", "phase_characterization",
        "WM_K_CLIFF_V3_GPU_CROSS_SEED_3_of_3_HARD_PASS_chain_grade_phase_characterization_CERT_plus_1",
        1, "wm_v3 CROSS-SEED AGG chain-grade phase characterization; Stage 1 multi-bank WM K=4096 PARTIAL -> HIGH",
    )); idx += 1
    # Cortex-hippo HARD_FAIL (3 per-seed, no AGG -- this is a negative; 0 CERT)
    for s, a in zip([7, 13, 19], cortex_per_seed):
        ledger_rows.append(_ledger_row(
            idx, a, "cert_ruling", "hard_fail", "mechanism_test_design_failure",
            f"cortex_hippo_M_8192_seed_{s}_HARD_FAIL_META_RULE_AF_violation",
            0, f"cortex_hippo seed_{s} META_RULE_AF violation: FULL == DIRECT bit-exact; W_hippo unused",
            metrics_path=a["metadata"]["metrics_path"],
        ))
        idx += 1
    # Ultrametric
    for s, a in zip([7, 13, 19], ultra_per_seed):
        ledger_rows.append(_ledger_row(
            idx, a, "cert_ruling", "middle_band", "phase_characterization_with_directional_downward_caveat",
            f"ultrametric_seed_{s}_HARD_PASS_phase_coverage_with_downward_directional",
            0, f"ultrametric seed_{s} HARD_PASS at discriminator bands but directional mean delta_uk negative",
            metrics_path=a["metadata"]["metrics_path"],
        ))
        idx += 1
    ledger_rows.append(_ledger_row(
        idx, ULTRA_AGG_ATOM, "cert_ruling_promotion_phase_characterization",
        "chain_grade", "phase_characterization_with_honest_downward",
        "ULTRAMETRIC_CROSS_SEED_3_of_3_HARD_PASS_chain_grade_phase_characterization_with_honest_downward_CERT_plus_1",
        1, "ultrametric CROSS-SEED AGG chain-grade phase characterization; ULTRA wins 35-42% sub-regime, dominated 60%+ overall; Stage 2 phase coverage MID -> HIGH",
    )); idx += 1
    # Schema
    for s, a in zip([7, 13, 19], schema_per_seed):
        ledger_rows.append(_ledger_row(
            idx, a, "cert_ruling", "middle_band", "mechanism_characterization",
            f"schema_bayes_seed_{s}_MIDDLE_BAND_lift_real_capacity_scaling_unmet",
            0, f"schema_bayes seed_{s} MIDDLE_BAND honest: BAYES lifts but capacity-scaling discriminator fails",
            metrics_path=a["metadata"]["metrics_path"],
        ))
        idx += 1
    ledger_rows.append(_ledger_row(
        idx, SCHEMA_AGG_ATOM, "cert_ruling", "middle_band", "phase_characterization",
        "SCHEMA_BAYES_CROSS_SEED_3_of_3_MIDDLE_BAND_phase_characterization_MM",
        0, "schema_bayes CROSS-SEED AGG MM; honest cross-seed consistent MB; no CERT delta",
    )); idx += 1
    # META amendment
    ledger_rows.append(_ledger_row(
        idx, CORTEX_HIPPO_META_AMENDMENT, "discipline_rule_amendment",
        "discipline_rule", "discipline_rule_amendment",
        "META_RULE_AF_amendment_FULL_eq_DIRECT_bit_exact_FATAL",
        0, "META_RULE_AF amendment: bit-exact FULL == DIRECT is FATAL; triggered by cortex_hippo 3-seed HARD_FAIL",
    )); idx += 1

    for row in ledger_rows:
        append_jsonl_a5(CERT_LEDGER, row, f"meta/cert_ledger.jsonl ({row['atom_id'][:80]}...)")

    print()
    print("=" * 78)
    print("FINAL Store re-load test")
    print("=" * 78)
    from backend.substrate_index.partition import PartitionedStore
    S = PartitionedStore(Path("d:/AI/hd-instrument/data/substrate_index"))
    atoms = list(S.all_atoms())
    print(f"Store loads OK: {len(atoms)} atoms")
    print()
    print("CERT DELTA THIS BATCH: +2 (WM v3 AGG +1; ULTRAMETRIC AGG +1)")
    print("HARD_FAILs filed: 3 (cortex_hippo per-seed META_RULE_AF violation)")
    print("MIDDLE_BANDs filed: 6 (schema 3 per-seed + AGG; ultrametric 3 per-seed contextual)")
    print("META amendments: 1 (META_RULE_AF FULL=DIRECT bit-exact FATAL)")
    print("DONE")


if __name__ == "__main__":
    main()
