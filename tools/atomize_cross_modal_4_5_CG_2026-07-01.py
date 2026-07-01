"""
A5-gated atomize: Cross-modal 4/5 modality v1 3-seed CHAIN_GRADE
                  (6th CG of 2026-07-01)

INDEPENDENT OFF-DATA VERIFICATION (skunkworks 2026-07-01):

Cell commit: fa00da80 (per Director framing)
Pre-reg: preregs/2026-07-01_cross_modal_binding_4_5_modality_v1.md
Pulled remote via SSH (sync lag): data/session_local/skunkworks/remote_crossmodal_45_seed_{7,13,19}.json

Substrate-KB overlap check (per new 2026-07-01 discipline rule):
  Query 'cross_modal_binding_4_5_modality': cosine 0.47 top match = older
  note-chunks (Cross-modal binding concept in 2026-05-31 through 2026-06-10
  research drills); no prior Store atom for 4/5-modality extension.
  Composes with:
    - Cross-modal 3rd modality single-seed MM atom (commit 5ec1b83b earlier today)
    - Prior cross-modal visual+auditory CG (per Director framing)
  4/5-modality is the NEXT extension in the arc: 2-mod CG -> 3-mod MM -> 4/5-mod CG.

Off-data facts (all 3 seeds run_mode=full on torch.cuda GPU):
  Per-seed verdicts: HARD_PASS all 3 seeds
  Elapsed: 1.08-1.60s per seed (GPU speed for 27 phase points x 40 records/pt = 1080 records)
  Cardinality: expected_n=1080 observed_n=1080 all seeds
  n_phase_points_total: 27 all seeds
  Config: K in [10,100,1000] x N in [2048,4096,8192] x n_mod in [3,4,5] = 3x3x3 = 27 pts
  Arms: [BIND_NMOD, NO_BIND]
  V_MOD=2048

Cross-seed n_discriminating_points:
  seed_7:  n_disc=20/27; discriminating_fraction=0.7407
  seed_13: n_disc=21/27; discriminating_fraction=0.7778
  seed_19: n_disc=20/27; discriminating_fraction=0.7407
  Cross-seed mean n_disc=20.33; sd=0.577; cv=0.0284 (excellent stability)
  Cross-seed mean disc_frac=0.7531; sd=0.0214; cv=0.0284
  All 3 exceed disc_frac >= 0.50 HP threshold by 1.5x margin.

Positive control (n_mod=5, K=10, N=8192 anchor):
  recall = 1.000 all 3 seeds (cv=0.000)
  positive_control_met = True all 3 seeds
  positive_control_cv = 0.000 all seeds
  Above 0.7 floor by wide margin.

Cliff evidence at edge of parameter surface:
  cliff fired at K=1000/N=2048/nmod=5 -> 0.000 (mechanism discriminates at high load)
  Smoke evidence (per Director framing): disc_frac=0.80 (confirmed at FULL 0.74-0.78 cross-seed)

Other quality gates:
  all_saturated = False all seeds (NOT ceiling-trapped)
  near_identical_arms = False all seeds (arms genuinely distinct)

META_RULE_Q check:
  positive_control at n_mod=5 K=10 N=8192 is anchor at ceiling BY DESIGN (calibration
  point); the 27 phase point grid tests discrimination away from this anchor.
  disc_frac 0.74-0.78 (not 1.000); all_saturated=False; not trapped.

============================================================
TIER RULING: CHAIN_GRADE. cert_increment_delta = +1.
============================================================

  All 3 seeds HP per-cell; cross-seed cv=0.028 on primary discriminator (n_disc);
  positive control 1.000 all seeds; cardinality 1080/1080 all seeds; not saturated;
  arms not near-identical; substrate-KB check confirms no prior Store atom for
  4/5-mod extension.

  SIXTH CG of 2026-07-01 (after A_v2 c7feb0c4, E_v5 716174a7, Cell D v2 863e14b5,
  ANCHOR4 N=16384 5ec1b83b, capacity multi-bank alpha-K HIGH 6c6a271d).

  CROSS-MODAL ARC EXTENSION:
    prior CG: visual+auditory (2-mod)
    prior MM: 3rd modality (5ec1b83b single-seed 2026-07-01 morning)
    THIS CG: 4/5-modality (3-seed 2026-07-01 evening)
    Substantive Stage 3 compositional-understanding capability extension:
    substrate supports cross-modal binding across up to 5 modalities.

  Note: 3rd modality single-seed MM atom (5ec1b83b) does NOT auto-promote to MM_STANDARD
  because this new 4/5-mod cell tests DIFFERENT modality counts (n_mod in [3,4,5])
  vs the 3rd-mod cell (single 3rd modality only). The 3rd-mod atom expansion criterion
  was 3-seed replication of its OWN discriminator, not extension to 4/5. That's a
  separate future atomization.
"""
from __future__ import annotations
import json, os, time
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
MATH_ATOMS = ROOT / "data/substrate_index/math/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"

ATOMIZED_BY = "skunkworks_landed_VET_cross_modal_4_5_modality_CG_2026-07-01"
ATOMIZED_DATE = "2026-07-01"

atom_crossmodal_45_CG = {
    "id": (
        "T3/EXP_cross_modal_binding_4_5_modality_v1_3seed_CHAIN_GRADE_"
        "n_disc_20_21_20_of_27_cv_0p028_disc_frac_0p74_0p78_0p74_all_ge_0p50_HP_threshold_1p5x_margin_"
        "positive_control_n_mod_5_K_10_N_8192_recall_1p000_cv_0p000_all_seeds_met_True_"
        "saturated_False_near_identical_arms_False_cardinality_1080_of_1080_all_seeds_"
        "arms_BIND_NMOD_vs_NO_BIND_V_MOD_2048_K_10_100_1000_N_2048_4096_8192_n_mod_3_4_5_"
        "extends_cross_modal_visual_auditory_2mod_CG_and_3rd_modality_MM_5ec1b83b_"
        "6th_CG_of_2026_07_01_2026-07-01"
    ),
    "name": (
        "CHAIN-GRADE Cross-modal binding 4/5-modality v1 3-seed FULL: substrate supports "
        "cross-modal binding across n_mod in [3,4,5] with disc_frac 0.74-0.78 cross-seed "
        "(cv=0.028; all above 0.50 HP threshold by 1.5x margin). Positive control (n_mod=5, "
        "K=10, N=8192) recall=1.000 cv=0.000 all 3 seeds. saturated=False, near_identical_arms="
        "False, cardinality 1080/1080 all seeds. GPU torch.cuda backend. Extends cross-modal "
        "arc: 2-mod CG -> 3-mod MM (5ec1b83b) -> 4/5-mod CG. Load-bearing Stage 3 compositional-"
        "understanding capability extension. CERT +1. SIXTH CG of 2026-07-01."
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record",
    "description": (
        "3-seed FULL cross-modal binding 4/5-modality v1. Cell commit fa00da80; pre-reg "
        "2026-07-01_cross_modal_binding_4_5_modality_v1.md. Pulled remote via SSH (sync lag) "
        "at data/session_local/skunkworks/remote_crossmodal_45_seed_{7,13,19}.json.\n"
        "\n"
        "SUBSTRATE-KB OVERLAP CHECK (per new 2026-07-01 discipline): cosine 0.47 top match = "
        "older note-chunks on cross-modal binding concept (2026-05-31 through 2026-06-10 research "
        "drills); no prior Store atom for 4/5-modality extension. Composes with cross-modal 3rd "
        "modality single-seed MM atom (5ec1b83b 2026-07-01 morning) and prior cross-modal visual+"
        "auditory CG (per Director framing).\n"
        "\n"
        "OFF-DATA verification (all 3 seeds):\n"
        "  run_mode=full; backend=torch.cuda; verdict=HARD_PASS all 3 seeds\n"
        "  elapsed 1.08-1.60s (GPU speed for 27 phase points x 40 records/pt = 1080 records)\n"
        "  cardinality: expected_n=1080 observed_n=1080 all seeds; PASS\n"
        "  n_phase_points_total=27 all seeds (K:3 x N:3 x n_mod:3 = 27 grid)\n"
        "  Config: K in [10,100,1000] x N in [2048,4096,8192] x n_mod in [3,4,5]\n"
        "  Arms: [BIND_NMOD, NO_BIND]; V_MOD=2048\n"
        "\n"
        "PER-SEED DISCRIMINATOR METRICS:\n"
        "  seed_7:  n_disc=20/27  disc_frac=0.7407  pos_ctrl_recall=1.000  saturated=False\n"
        "  seed_13: n_disc=21/27  disc_frac=0.7778  pos_ctrl_recall=1.000  saturated=False\n"
        "  seed_19: n_disc=20/27  disc_frac=0.7407  pos_ctrl_recall=1.000  saturated=False\n"
        "\n"
        "CROSS-SEED CV:\n"
        "  n_disc = [20, 21, 20]; mean=20.33; sd=0.577; cv=0.0284\n"
        "  disc_frac = [0.7407, 0.7778, 0.7407]; mean=0.7531; sd=0.0214; cv=0.0284\n"
        "  positive_control_recall = [1.000, 1.000, 1.000]; cv=0.000\n"
        "  positive_control_cv = [0.000, 0.000, 0.000]; cv=0.000\n"
        "  All primary discriminator cv << 0.10 CG threshold.\n"
        "\n"
        "POSITIVE CONTROL (n_mod=5, K=10, N=8192 anchor point):\n"
        "  recall = 1.000 all 3 seeds; cv = 0.000\n"
        "  positive_control_met = True all 3 seeds\n"
        "  Above 0.7 floor with wide margin.\n"
        "\n"
        "CLIFF EVIDENCE (mechanism discriminates at high load; from smoke and confirmed by\n"
        "phase surface characterization):\n"
        "  cliff fired at K=1000/N=2048/nmod=5 -> 0.000 (BIND_NMOD collapses; discriminator active)\n"
        "\n"
        "OTHER QUALITY GATES:\n"
        "  all_saturated = False all seeds (NOT ceiling-trapped)\n"
        "  near_identical_arms = False all seeds (arms genuinely distinct)\n"
        "\n"
        "META_RULE_Q CHECK: positive_control at n_mod=5 K=10 N=8192 is anchor at ceiling BY DESIGN\n"
        "(calibration point); 27 phase-point grid tests discrimination AWAY from this anchor.\n"
        "disc_frac 0.74-0.78 (not 1.000); all_saturated=False. NOT trapped.\n"
        "\n"
        "CROSS-MODAL ARC EXTENSION:\n"
        "  Prior CG: visual+auditory (2-modality)\n"
        "  Prior MM: 3rd modality single-seed (commit 5ec1b83b 2026-07-01 morning)\n"
        "  THIS CG: 4/5-modality 3-seed (evening) -- substrate supports cross-modal binding\n"
        "  across n_mod in [3,4,5] at CG-quality.\n"
        "  Load-bearing Stage 3 compositional-understanding capability extension.\n"
        "\n"
        "TIER: CHAIN_GRADE. cert_increment_delta = +1. SIXTH CG of 2026-07-01.\n"
        "\n"
        "SUBSTRATE DESIGN IMPLICATION (chain-grade):\n"
        "  Substrate supports cross-modal binding across up to 5 modalities at N in [2048,4096,\n"
        "  8192] with K in [10,100,1000]. 74-78% of phase-point grid shows discrimination lift\n"
        "  >=0.30 over NO_BIND baseline. Anchor point (n_mod=5, K=10, N=8192) at ceiling\n"
        "  confirms mechanism works at boundary. hdlab/ primitives can bind up to 5 modalities.\n"
        "\n"
        "NOTE ON 3RD-MOD MM ATOM (5ec1b83b): does NOT auto-promote via this CG because 3rd-mod\n"
        "cell tested single 3rd-modality only (K in [10,50,100,500,1000] x N in [2048,4096,8192]\n"
        "with 3 mechanisms HRR_bind3/sum_then_query/position_key_bind3); THIS 4/5-mod cell tests\n"
        "different config (K in [10,100,1000] x N in [2048,4096,8192] x n_mod in [3,4,5]). The\n"
        "3rd-mod MM expansion criterion was 3-seed replication of ITS OWN discriminator on the\n"
        "3-mechanism/45-point grid. Separate future dispatch would promote 3rd-mod to CG."
    ),
    "metadata": {
        "provenance_quality": "CERT_CHAIN_GRADE",
        "verdict": "HARD_PASS",
        "verified_off_data_by": ATOMIZED_BY,
        "verified_off_data_evidence": (
            "OFF-DATA recompute via .venv python on 3 seeds metrics.json (SSH pulled from remote): "
            "all 3 seeds run_mode=full torch.cuda GPU; verdict=HARD_PASS; cardinality 1080/1080 "
            "all seeds; n_disc=[20,21,20]/27 cross-seed cv=0.028; disc_frac=[0.7407,0.7778,0.7407] "
            "cv=0.028; positive_control_recall=1.000 cv=0.000 all seeds; saturated=False; "
            "near_identical_arms=False; substrate-KB check confirms no prior Store atom for "
            "4/5-mod extension"
        ),
        "regime": {
            "K_values": [10, 100, 1000],
            "N_values": [2048, 4096, 8192],
            "n_mod_values": [3, 4, 5],
            "arms": ["BIND_NMOD", "NO_BIND"],
            "V_MOD": 2048,
            "n_phase_points_total": 27,
            "expected_n_records": 1080,
            "backend": "torch.cuda",
        },
        "per_seed_metrics_paths": {
            "seed_7":  "data/exp_cross_modal_binding_4_5_modality_v1_seed_7/metrics.json (SSH pulled)",
            "seed_13": "data/exp_cross_modal_binding_4_5_modality_v1_seed_13/metrics.json (SSH pulled)",
            "seed_19": "data/exp_cross_modal_binding_4_5_modality_v1_seed_19/metrics.json (SSH pulled)",
        },
        "prereg_path": "preregs/2026-07-01_cross_modal_binding_4_5_modality_v1.md",
        "cell_commit": "fa00da80",
        "per_seed_discriminator_metrics": {
            "seed_7":  {"n_disc": 20, "disc_frac": 0.7407, "pos_ctrl_recall": 1.000, "saturated": False},
            "seed_13": {"n_disc": 21, "disc_frac": 0.7778, "pos_ctrl_recall": 1.000, "saturated": False},
            "seed_19": {"n_disc": 20, "disc_frac": 0.7407, "pos_ctrl_recall": 1.000, "saturated": False},
        },
        "cross_seed_cv": {
            "n_disc":                {"vals": [20, 21, 20], "mean": 20.33, "sd": 0.577, "cv": 0.0284},
            "disc_frac":             {"vals": [0.7407, 0.7778, 0.7407], "mean": 0.7531, "sd": 0.0214, "cv": 0.0284},
            "positive_control_recall": {"vals": [1.000, 1.000, 1.000], "cv": 0.000},
            "positive_control_cv":   {"vals": [0.000, 0.000, 0.000], "cv": 0.000},
        },
        "discriminator_gates_all_pass": {
            "disc_frac_ge_0p50_all_seeds": True,
            "positive_control_recall_ge_0p7": True,
            "positive_control_cv_le_0p1": True,
            "saturated_False_all_seeds": True,
            "near_identical_arms_False_all_seeds": True,
            "cardinality_ok_all_seeds": True,
        },
        "cliff_evidence_at_K_1000_N_2048_nmod_5_recall_0p000": True,
        "META_RULE_Q_not_trapped_positive_control_at_ceiling_by_design_grid_discriminates": True,
        "cert_increment_delta": 1,
        "cg_promotion_note": (
            "SIXTH CG of 2026-07-01 (after A_v2 c7feb0c4, E_v5 716174a7, Cell D v2 863e14b5, "
            "ANCHOR4 N=16384 5ec1b83b, capacity multi-bank alpha-K HIGH 6c6a271d)"
        ),
        "cross_modal_arc_extension": {
            "prior_CG_visual_auditory_2_modality": True,
            "prior_MM_3rd_modality_commit": "5ec1b83b_2026-07-01_morning",
            "this_CG_4_5_modality_3_seed_2026-07-01_evening": True,
            "substrate_supports_cross_modal_binding_up_to_5_modalities_at_CG_quality": True,
            "stage_3_compositional_understanding_capability_extension": True,
        },
        "note_on_3rd_mod_MM_atom_5ec1b83b_does_NOT_auto_promote": (
            "3rd-mod cell tested single 3rd-modality only with 3-mechanism/45-point grid; "
            "THIS 4/5-mod cell tests different config (n_mod in [3,4,5] x K in [10,100,1000] "
            "x N in [2048,4096,8192] = 27-point grid). 3rd-mod MM expansion criterion was "
            "3-seed replication of ITS OWN discriminator on 45-point grid; separate future "
            "dispatch would promote 3rd-mod to CG."
        ),
        "substrate_design_implication_chain_grade": (
            "Substrate supports cross-modal binding across up to 5 modalities at N in [2048,"
            "4096,8192] with K in [10,100,1000]. 74-78% of phase-point grid shows discrimination "
            "lift >=0.30 over NO_BIND baseline. hdlab/ primitives can bind up to 5 modalities."
        ),
        "discipline_tags": [
            "META_RULE_Q_not_trapped_positive_control_at_ceiling_by_design_grid_discriminates",
            "META_RULE_H_cardinality_ok_1080_of_1080_all_seeds",
            "META_RULE_AV_disc_frac_gate_fire_cross_seed_ge_0p50_by_1p5x_margin",
            "META_RULE_AH_positive_control_recall_1p000_cv_0p000_saturated_False_near_identical_False",
            "6th_CG_promotion_of_2026_07_01",
            "cross_modal_arc_extension_2mod_CG_to_3mod_MM_to_4_5_mod_CG",
            "stage_3_compositional_understanding_capability_extension",
            "substrate_KB_check_first_confirms_no_prior_Store_atom_for_4_5_mod_extension",
            "results_to_application_hdlab_primitives_up_to_5_modality_binding",
            "stage_3_compositional_understanding_USER_2026-06-26",
        ],
        "ts_iso_atomized": ATOMIZED_DATE,
    },
}

# ============================================================================
# CERT LEDGER ROW
# ============================================================================
_t0 = time.time()

ledger_crossmodal_45_CG = {
    "ts": _t0,
    "op": "cert_ruling_promotion_chain_grade",
    "atom_id": f"math::{atom_crossmodal_45_CG['id']}",
    "cert_status": "chain_grade",
    "cert_class": "pre_reg_pass_cross_modal_binding_4_5_modality_extension",
    "verified_off_data": True,
    "atomized_by": ATOMIZED_BY,
    "cell_commit": "fa00da80",
    "verdict": (
        "CHAIN_GRADE_3seed_HP_cross_modal_4_5_modality_n_disc_20_21_20_of_27_cv_0p028_"
        "disc_frac_0p7407_0p7778_0p7407_all_ge_0p50_HP_threshold_1p5x_margin_"
        "positive_control_n_mod_5_K_10_N_8192_recall_1p000_cv_0p000_all_seeds_met_True_"
        "saturated_False_near_identical_arms_False_cardinality_1080_of_1080_all_seeds_"
        "GPU_torch_cuda_backend_arms_BIND_NMOD_vs_NO_BIND_V_MOD_2048_"
        "cliff_at_K_1000_N_2048_nmod_5_recall_0p000_mechanism_discriminates_at_high_load_"
        "extends_cross_modal_visual_auditory_2mod_CG_and_3rd_modality_MM_5ec1b83b_"
        "6th_CG_of_2026_07_01_stage_3_capability_extension"
    ),
    "cert_increment_delta": 1,
    "cv": 0.0284,
    "referent_pointer": {
        "notes_path": None,
        "metrics_path": "data/exp_cross_modal_binding_4_5_modality_v1_seed_{7,13,19}/metrics.json (SSH pulled)",
        "prereg_path": "preregs/2026-07-01_cross_modal_binding_4_5_modality_v1.md",
        "cell_commit": "fa00da80",
        "prior_3rd_mod_MM_atom_commit": "5ec1b83b_2026-07-01_morning",
        "atom_qualified_id": f"math::{atom_crossmodal_45_CG['id']}",
    },
    "supersedes": None,  # extends arc; does not supersede
    "note": (
        "cross_modal_binding_4_5_modality_v1_3seed_CHAIN_GRADE_6th_CG_of_2026_07_01_"
        "n_disc_20_21_20_of_27_cross_seed_cv_0p028_disc_frac_0p7407_0p7778_0p7407_all_ge_0p50_HP_1p5x_margin_"
        "positive_control_n_mod_5_K_10_N_8192_recall_1p000_cv_0p000_all_seeds_met_True_above_0p7_floor_"
        "saturated_False_near_identical_arms_False_all_seeds_"
        "cardinality_1080_of_1080_all_seeds_27_phase_point_grid_K_10_100_1000_N_2048_4096_8192_n_mod_3_4_5_"
        "arms_BIND_NMOD_vs_NO_BIND_V_MOD_2048_GPU_torch_cuda_backend_elapsed_1_to_2_s_per_seed_"
        "cliff_evidence_at_K_1000_N_2048_nmod_5_recall_0p000_mechanism_discriminates_at_high_load_"
        "META_RULE_Q_not_trapped_positive_control_at_ceiling_by_design_grid_discriminates_"
        "extends_cross_modal_arc_2mod_visual_auditory_CG_prior_to_3rd_modality_MM_5ec1b83b_to_4_5_mod_CG_"
        "stage_3_compositional_understanding_capability_extension_substrate_supports_up_to_5_modalities_"
        "substrate_KB_check_first_confirms_no_prior_Store_atom_only_older_note_chunks_cosine_0p47_"
        "3rd_mod_MM_atom_5ec1b83b_does_NOT_auto_promote_because_different_config_3_mechanism_45_point_grid_"
        "hdlab_primitives_can_bind_up_to_5_modalities_at_CG_quality"
    ),
}


# ============================================================================
# A5 write protocol
# ============================================================================
def append_jsonl_a5(path: Path, new_row: dict, label: str):
    print(f"[A5] {label}: path={path}")
    assert path.exists()

    with open(path, "r", encoding="utf-8") as f:
        pre_lines = f.read().splitlines()
    pre_count = len(pre_lines)
    print(f"[A5] {label}: pre_count={pre_count}")

    for i, ln in enumerate(pre_lines):
        if not ln.strip(): continue
        try: json.loads(ln)
        except Exception as e: raise RuntimeError(f"PRE integrity fail line {i+1}: {e}")

    new_line = json.dumps(new_row, ensure_ascii=True)
    parsed_back = json.loads(new_line)
    if "id" in new_row: assert parsed_back.get("id") == new_row.get("id")
    if "atom_id" in new_row: assert parsed_back.get("atom_id") == new_row.get("atom_id")

    out_text = "\n".join(pre_lines + [new_line]) + "\n"
    tmp_path = path.with_suffix(path.suffix + ".tmp_a5")
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(out_text); f.flush(); os.fsync(f.fileno())
    import time as _time
    for _attempt in range(10):
        try: os.replace(str(tmp_path), str(path)); break
        except PermissionError:
            if _attempt == 9: raise
            _time.sleep(0.1 * (2 ** _attempt))

    with open(path, "r", encoding="utf-8") as f:
        post_lines = f.read().splitlines()
    post_count = len(post_lines)
    print(f"[A5] {label}: post_count={post_count}")
    assert post_count == pre_count + 1

    tail = json.loads(post_lines[-1])
    if "id" in new_row: assert tail["id"] == new_row["id"]
    if "atom_id" in new_row: assert tail["atom_id"] == new_row["atom_id"]

    for i, ln in enumerate(post_lines):
        if not ln.strip(): continue
        try: json.loads(ln)
        except Exception as e: raise RuntimeError(f"POST integrity fail line {i+1}: {e}")

    print(f"[A5] {label}: OK")
    return post_count


def main():
    print(f"[A5] atomize START {ATOMIZED_BY} ts={time.time():.3f}")
    append_jsonl_a5(MATH_ATOMS, atom_crossmodal_45_CG,        "math/atoms (cross-modal 4/5 modality 3-seed CHAIN_GRADE)")
    append_jsonl_a5(CERT_LEDGER, ledger_crossmodal_45_CG,     "cert_ledger (cross-modal 4/5 CG +1; 6th CG of 2026-07-01)")
    print(f"[A5] DONE OK")
    print(f"[A5] Cross-modal 4/5 modality 3-seed: CHAIN_GRADE +1 (6th CG of 2026-07-01)")
    print(f"[A5] Cross-modal arc: 2-mod CG -> 3-mod MM -> 4/5-mod CG (Stage 3 capability extension)")
    print(f"[A5] CERT delta = +1")


if __name__ == "__main__":
    main()
