"""A5-gated atomization of theta_gamma_v3_N16384_gpu 3-seed cross-seed decision.

Landing (verified off-disk by Skunkworks independent recompute):
  Per-seed verdicts on-disk: seed 7 MIDDLE_BAND / seeds 13,19 HARD_PASS
  Cross-seed tier: MEASURED_MECHANISM (auditor-tiered; cross-seed unanimity BROKEN)

Rationale:
  - PRIMARY discriminator (FHRR vs CYCLIC log2_delta >= 1.5) holds on 3/3 seeds by WIDE margin
    (3.32 / 4.32 / 4.32); mechanism scales to N=16384 for the main claim.
  - SECONDARY discriminator (nested_vs_flat32 >= 0.1) fails on seed 7 (delta=0.000) but holds on
    seeds 13/19 (delta=1.000). Root cause: FLAT_32 cliff at K=200 for seed 7 vs K=100 for seeds
    13/19 (codebook-draw seed dependence); NESTED cliff rock-solid at K=100 across ALL 3 seeds.
  - Pre-reg HP requires cv <= 0.10 AND nested_vs_flat32 >= 0.1 AND min_cross_arm >= 0.1; seed 7
    fails all 3 secondary gates cleanly.
  - Prior v2 CG at N=4096 had cliff cv=0.000 (PERFECT cross-seed) - v3 does NOT reproduce that
    discipline at N=16384 for FLAT_32 arm; NESTED cliff cv=0.000 stays clean.
  - Auditor tier = MM captures substantive positive finding while flagging seed-dependent
    variance on the secondary discriminator. NOT chain-grade lift over v2.

Discipline invariants (per hdi_skunkworks.md):
  - Atomic tmp-write + os.replace on atoms.jsonl AND cert_ledger.jsonl
  - Matching timestamps between atom + ledger entries
  - verified_off_data=True on ledger entries
  - Load-verify after write
"""
import json
import os
import time
import pathlib

REPO = pathlib.Path("d:/AI/hd-instrument")
MATH_ATOMS = REPO / "data/substrate_index/math/atoms.jsonl"
CERT_LEDGER = REPO / "data/substrate_index/meta/cert_ledger.jsonl"

TS_NOW = time.time()
DATE = "2026-07-01"
COMMIT = "37c0c049"

# ---------- Atom 9: theta_gamma v3 N=16384 3-seed MEASURED_MECHANISM ----------
ATOM_9_ID = (
    "T3/EXP_substrate_theta_gamma_v3_N16384_gpu_3seed_MEASURED_MECHANISM_"
    "cross_seed_unanimity_BROKEN_2_of_3_HP_seeds_13_19_seed_7_MIDDLE_BAND_"
    "PRIMARY_discriminator_FHRR_vs_CYCLIC_log2_delta_3p32_seed7_4p32_seed13_4p32_seed19_all_ge_1p5_HP_by_wide_margin_"
    "SECONDARY_discriminator_nested_vs_flat32_log2_delta_0p000_seed7_1p000_seed13_1p000_seed19_HP_gate_0p1_"
    "FAILS_on_seed7_FLAT_32_cliff_shifts_from_K_100_to_K_200_codebook_draw_seed_dependence_"
    "NESTED_cliff_rock_solid_K_100_across_ALL_3_seeds_cv_0p000_NO_seed_dependence_on_MAIN_mechanism_"
    "CYCLIC_SHIFT_cliff_rock_solid_K_1000_across_ALL_3_seeds_cv_0p000_positive_control_stable_"
    "FLAT_32_cliff_cv_0p079_across_seeds_secondary_arm_variance_source_"
    "pairs_differ_10_of_10_all_seeds_cardinality_35_of_35_per_seed_"
    "prior_v2_CG_at_N_4096_had_cliff_cv_0p000_PERFECT_cross_seed_this_v3_does_NOT_reproduce_at_N_16384_"
    "auditor_MM_tier_captures_substantive_positive_finding_mechanism_scales_to_N_16384_for_primary_claim_"
    "flags_seed_dependent_variance_on_secondary_discriminator_NOT_chain_grade_lift_over_v2_"
    "revival_criterion_run_more_seeds_or_investigate_FLAT_32_seed_dependent_codebook_at_N_16384_2026-07-01"
)
ATOM_9 = {
    "id": ATOM_9_ID,
    "name": (
        "MM theta_gamma_v3_N16384_gpu 3-seed FULL: cross-seed unanimity BROKEN (2/3 HP + 1/3 "
        "MIDDLE_BAND). PRIMARY discriminator (FHRR-vs-CYCLIC log2_delta >= 1.5) holds on ALL 3 seeds "
        "by wide margin (seed 7: 3.32; seeds 13/19: 4.32); mechanism DOES scale to N=16384 for the "
        "main sequence-encoding claim. SECONDARY discriminator (nested_vs_flat32 >= 0.1) FAILS on "
        "seed 7 (delta=0.000) but holds on seeds 13/19 (delta=1.000). Root cause: FLAT_32 cliff "
        "shifts from K=100 (seeds 13/19; log2=5.6439) to K=200 (seed 7; log2=6.6439) - codebook-draw "
        "seed-dependence in the FLAT_32 arm. NESTED cliff is ROCK-SOLID at K=100 across ALL 3 seeds "
        "(cliff cv=0.000; no seed-dependence on the MAIN mechanism arm). CYCLIC_SHIFT positive control "
        "cliff at K=1000 across ALL 3 seeds (cv=0.000; positive-control-stable). FLAT_32 cliff cv "
        "across seeds = 0.079 - the variance-source arm. All 3 seeds pass pairs_differ=10/10 and "
        "cardinality 35/35. Prior v2 CG at N=4096 had cliff_cv=0.000 across all arms (perfect cross-"
        "seed reproducibility); v3 at N=16384 does NOT reproduce that discipline for FLAT_32. Auditor "
        "MM tier captures substantive positive finding (mechanism scales to N=16384 for primary claim) "
        "while flagging seed-dependent variance on secondary discriminator; NOT chain-grade lift over "
        "v2's perfect reproducibility. Revival criterion: run more seeds (5-10) OR investigate FLAT_32 "
        "codebook seed-dependence at N=16384 regime edge. CERT +0 (MM tier)."
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record",
    "description": (
        f"OFF-DATA verified: data/exp_substrate_theta_gamma_v3_N16384_gpu_seed_{{7,13,19}}/metrics.json.\n\n"
        f"Recompute Skunkworks {DATE}:\n"
        f"\n"
        f"=== Per-seed verdicts (cell-emitted) ===\n"
        f"  seed 7:  MIDDLE_BAND (nested_vs_flat32=0.000 fails 0.1 HP gate)\n"
        f"  seed 13: HARD_PASS  (all HP gates cleared)\n"
        f"  seed 19: HARD_PASS  (all HP gates cleared)\n"
        f"\n"
        f"=== Per-seed key discriminators ===\n"
        f"  seed 7:  fhrr_vs_cyclic=3.32 (HP OK) | nested_vs_flat32=0.000 (HP FAIL) | min_cross_arm=0.000 (HP FAIL) | pairs=10/10\n"
        f"  seed 13: fhrr_vs_cyclic=4.32 (HP OK) | nested_vs_flat32=1.000 (HP OK)   | min_cross_arm=1.000 (HP OK)   | pairs=10/10\n"
        f"  seed 19: fhrr_vs_cyclic=4.32 (HP OK) | nested_vs_flat32=1.000 (HP OK)   | min_cross_arm=1.000 (HP OK)   | pairs=10/10\n"
        f"\n"
        f"=== Cliff log2_K per arm cross-seed ===\n"
        f"  NO_POSITION:              [-1.0, -1.0, -1.0] (chance baseline; no cliff)\n"
        f"  CYCLIC_SHIFT:             [9.9658, 9.9658, 9.9658] cv=0.000 (perfect; positive control)\n"
        f"  FHRR_FLAT_PHASE_8:        [-1.0, -1.0, -1.0] (mechanism fails at N=16384)\n"
        f"  FHRR_FLAT_PHASE_32:       [6.6439, 5.6439, 5.6439] cv=0.0789 (SEED 7 ANOMALY; K=200 vs K=100)\n"
        f"  FHRR_NESTED_THETA_GAMMA:  [6.6439, 6.6439, 6.6439] cv=0.000 (perfect; MAIN mechanism)\n"
        f"\n"
        f"=== Cross-seed accuracy variance at key K points ===\n"
        f"  NESTED @ K=50:   [1.000, 1.000, 1.000] max_dev=0.000 (saturated ceiling; all 3 seeds)\n"
        f"  NESTED @ K=100:  [0.720, 0.720, 0.720] max_dev=0.000 (identical across seeds)\n"
        f"  NESTED @ K=200:  [0.300, 0.380, 0.280] max_dev=0.060 (cliff-edge variance normal)\n"
        f"  FLAT_32 @ K=100: [0.500, 0.300, 0.280] max_dev=0.140 (SEED 7 ANOMALY: keeps arm alive)\n"
        f"  CYCLIC @ K=1000: [0.640, 0.620, 0.660] max_dev=0.020 (positive control tight)\n"
        f"\n"
        f"=== HP gate analysis (pre-reg locked at module init) ===\n"
        f"  cardinality_ok:              3/3 seeds OK (35/35 per seed)\n"
        f"  n_pairs_differ >= 9 of 10:   3/3 seeds OK (10/10 all seeds)\n"
        f"  max_fhrr_vs_cyclic >= 1.5:   3/3 seeds OK (3.32/4.32/4.32)\n"
        f"  nested_vs_flat32 >= 0.1:     2/3 seeds OK (seed 7 = 0.000 FAIL)\n"
        f"  min_cross_arm >= 0.1:        2/3 seeds OK (seed 7 = 0.000 FAIL)\n"
        f"  NO_POSITION K=50 < 0.999:    3/3 seeds OK (all 0.000)\n"
        f"  META_RULE_Q < 3 arms sat:    3/3 seeds OK (2 arms saturate: CYCLIC + NESTED)\n"
        f"  n_llm_calls = 0:             3/3 seeds OK\n"
        f"  cross-seed cv <= 0.10:       primary arms OK; FLAT_32 cv=0.079 within tolerance\n"
        f"\n"
        f"=== Wall time per seed ===\n"
        f"  seed 7: 275.58s (5.5x longer than other seeds - possible GPU thermal or\n"
        f"    memory-fragmentation event; not correlated with mechanism failure directly)\n"
        f"  seed 13: 50.44s (normal)\n"
        f"  seed 19: 70.79s (normal)\n"
        f"  Cross-cell timing outlier for seed 7 is NOT the driver of MIDDLE_BAND verdict;\n"
        f"    verdict is driven by measurement content (FLAT_32 cliff position), not by timing.\n"
        f"\n"
        f"CROSS-SEED TIER JUDGMENT (auditor):\n"
        f"  Cross-seed unanimity is BROKEN: 2/3 HP + 1/3 MIDDLE_BAND.\n"
        f"  \n"
        f"  CASE FOR CG:\n"
        f"    (a) PRIMARY discriminator holds by WIDE margin on all 3 seeds (fhrr_vs_cyclic >= 3.32)\n"
        f"    (b) Core mechanism (NESTED sequence encoding) is ROCK-SOLID (cliff cv=0.000)\n"
        f"    (c) CYCLIC positive control rock-solid (cliff cv=0.000; matches v2 discipline)\n"
        f"    (d) 33% cross-seed borderline is EXPECTED variance at N=16384 regime edge\n"
        f"  \n"
        f"  CASE FOR MM (WHICH AUDITOR ADOPTS):\n"
        f"    (a) Prior v2 CG at N=4096 had cliff cv=0.000 (PERFECT reproducibility across ALL arms).\n"
        f"        v3 at N=16384 does NOT reproduce that discipline for FLAT_32 arm.\n"
        f"    (b) Pre-reg HP conditions are LOCKED and require ALL gates to hold; seed 7 fails\n"
        f"        nested_vs_flat32 and min_cross_arm HP gates. Cell verdict correctly emits\n"
        f"        MIDDLE_BAND. Cannot hand-wave a pre-reg locked gate.\n"
        f"    (c) Auditor discipline: cross-seed 2/3 HP is NOT chain-grade when prior parent CG had\n"
        f"        3/3 HP at cv=0.000. Bar is not lowered.\n"
        f"    (d) The MM captures the substantive positive finding: MAIN mechanism (NESTED sequence\n"
        f"        encoding + FHRR-vs-CYCLIC discriminator) scales cleanly to N=16384; SECONDARY\n"
        f"        discriminator (nesting-advantage vs FLAT_32) has seed-dependent behavior at scale.\n"
        f"  \n"
        f"  AUDITOR DECISION: MM tier. This is honest scoping of what IS chain-grade (the primary\n"
        f"    mechanism claim) vs what needs more evidence (nesting-advantage at N=16384).\n"
        f"\n"
        f"REVIVAL CRITERION:\n"
        f"  (a) Run additional seeds (5-10 total) to characterize the FLAT_32 seed-dependent cliff\n"
        f"      position distribution; if 2/10 seeds anomalous is consistent, this is a bounded\n"
        f"      seed-variance phenomenon and MM stands; if only 1/3 was anomalous by chance,\n"
        f"      re-tier to CG possible.\n"
        f"  (b) Investigate FLAT_32 codebook draw at N=16384: does the 32-position basis in complex64\n"
        f"      have a small combinatorial regime (~8000 draws)? Different seeds may hit different\n"
        f"      basis-position phase alignments causing K=100 vs K=200 cliff shifts.\n"
        f"  (c) Extend K-sweep resolution around K=100-200 (add K=125, 150, 175) to characterize\n"
        f"      the FLAT_32 cliff structure at higher resolution; may reveal smooth transition\n"
        f"      that discretization K=100/200 misses.\n"
        f"\n"
        f"CROSS-ARC OVERLAP CHECK {DATE}: substrate_query 'theta gamma nested position basis FHRR\n"
        f"  sequence encoding N_DIM scaling' top-1 cosine=0.32 (positional encoding concept notes /\n"
        f"  theta_gamma primitive discussion notes; NO prior N-sweep atoms at cosine >= 0.40).\n"
        f"  Prior v2 CG at N=4096 (2026-06-30; 12th CG of that day) is DIRECT parent (found via\n"
        f"  grep cert_ledger). v3 is 4x N regime extension; genuinely novel N-scale test.\n"
        f"  NOT a rediscovery.\n"
        f"\n"
        f"COMPOSES WITH:\n"
        f"  - v2 CG at N=4096 (12th CG of 2026-06-30; cliff cv=0.000 all arms): parent atom.\n"
        f"  - Not superseded; v2 remains valid at N=4096 setpoint.\n"
        f"  - v3 extends REGIME (N=16384) with partial reproduction (primary discriminator holds;\n"
        f"    secondary discriminator has seed-dependent behavior).\n"
        f"\n"
        f"Commit: {COMMIT}. Author: skunkworks_landed_VET_wave_2026-07-01_theta_gamma_v3_cross_seed."
    ),
    "metadata": {
        "ts_atomized": TS_NOW,
        "date_atomized": DATE,
        "cert_commit": COMMIT,
        "run_mode": "full",
        "n_seeds": 3,
        "seeds": [7, 13, 19],
        "N_DIM": 16384,
        "ITEM_VOCAB_SIZE": 10000,
        "NOISE_SIGMA": 0.05,
        "K_SEQ_sweep": [50, 100, 200, 500, 1000, 2000, 5000],
        "arms": ["NO_POSITION", "CYCLIC_SHIFT", "FHRR_FLAT_PHASE_8", "FHRR_FLAT_PHASE_32", "FHRR_NESTED_THETA_GAMMA"],
        "cardinality_ok_per_seed": True,
        "n_units_expected_per_seed": 35,
        "n_units_observed_per_seed": 35,
        "verdict_per_seed": {"7": "MIDDLE_BAND", "13": "HARD_PASS", "19": "HARD_PASS"},
        "cross_seed_HP_count": 2,
        "cross_seed_MB_count": 1,
        "cross_seed_unanimity": False,
        "primary_discriminator_HP_all_seeds": True,
        "secondary_discriminator_HP_seeds_13_19_only": True,
        "max_fhrr_vs_cyclic_log2_delta_per_seed": {"7": 3.3219, "13": 4.3219, "19": 4.3219},
        "nested_vs_flat32_log2_delta_per_seed": {"7": 0.0, "13": 1.0, "19": 1.0},
        "min_cross_arm_log2_delta_per_seed": {"7": 0.0, "13": 1.0, "19": 1.0},
        "n_pairs_differ_per_seed": {"7": 10, "13": 10, "19": 10},
        "cliff_log2_K_per_arm_per_seed": {
            "NO_POSITION": [-1.0, -1.0, -1.0],
            "CYCLIC_SHIFT": [9.9658, 9.9658, 9.9658],
            "FHRR_FLAT_PHASE_8": [-1.0, -1.0, -1.0],
            "FHRR_FLAT_PHASE_32": [6.6439, 5.6439, 5.6439],
            "FHRR_NESTED_THETA_GAMMA": [6.6439, 6.6439, 6.6439],
        },
        "cliff_cv_across_seeds_per_arm": {
            "NO_POSITION": None,
            "CYCLIC_SHIFT": 0.0,
            "FHRR_FLAT_PHASE_8": None,
            "FHRR_FLAT_PHASE_32": 0.0789,
            "FHRR_NESTED_THETA_GAMMA": 0.0,
        },
        "variance_source_arm": "FHRR_FLAT_PHASE_32",
        "variance_source_seed": 7,
        "variance_source_signature": "FLAT_32_cliff_K_shifts_from_100_to_200_for_seed_7_codebook_draw_seed_dependence_NESTED_cliff_unchanged",
        "positive_control_stable": True,
        "positive_control_CYCLIC_SHIFT_cliff_cv": 0.0,
        "no_position_saturates_K50_per_seed": {"7": False, "13": False, "19": False},
        "arms_saturating_at_K50_per_seed": {"7": 2, "13": 2, "19": 2},
        "meta_rule_Q_regime_not_too_easy_all_seeds": True,
        "elapsed_s_per_seed": {"7": 275.58, "13": 50.44, "19": 70.79},
        "seed_7_wall_5x_outlier": True,
        "seed_7_wall_outlier_correlation_with_verdict": "NOT_causal_verdict_driven_by_measurement_content_not_timing",
        "n_llm_calls_per_seed": {"7": 0, "13": 0, "19": 0},
        "verified_off_data": True,
        "metrics_paths": [
            "data/exp_substrate_theta_gamma_v3_N16384_gpu_seed_7/metrics.json",
            "data/exp_substrate_theta_gamma_v3_N16384_gpu_seed_13/metrics.json",
            "data/exp_substrate_theta_gamma_v3_N16384_gpu_seed_19/metrics.json",
        ],
        "prereg_path": "preregs/2026-07-01_theta_gamma_v3_N16384_gpu.md",
        "parent_atoms": [
            "T3/EXP_substrate_theta_gamma_v2_FHRR_all_complex_3seed_HP_CG_axes_I_plus_J_phase_diagram_2026-06-30",
        ],
        "prior_v2_CG_cliff_cv": 0.0,
        "prior_v2_CG_N_DIM": 4096,
        "v3_N_DIM_extension_factor": 4.0,
        "cert_tier": "measured_mechanism",
        "cert_increment_delta": 0,
        "revival_criterion": (
            "run_additional_seeds_5_to_10_total_to_characterize_FLAT_32_seed_dependent_cliff_distribution_"
            "OR_investigate_FLAT_32_codebook_seed_dependence_at_N_16384_"
            "OR_extend_K_sweep_resolution_K_125_150_175_to_characterize_smooth_transition_FLAT_32_cliff"
        ),
    },
}
LEDGER_9 = {
    "ts": TS_NOW,
    "op": "cert_ruling_measured_mechanism_cross_seed_unanimity_broken",
    "atom_id": f"math::{ATOM_9_ID}",
    "cert_status": "measured_mechanism",
    "cert_class": "auditor_MM_tier_cross_seed_unanimity_broken_2_of_3_HP_primary_discriminator_holds_secondary_discriminator_seed_dependent",
    "verified_off_data": True,
    "atomized_by": "skunkworks_landed_VET_wave_2026-07-01_theta_gamma_v3_cross_seed",
    "cell_commit": COMMIT,
    "verdict": (
        "MEASURED_MECHANISM_cross_seed_unanimity_BROKEN_2_of_3_HP_seeds_13_19_seed_7_MIDDLE_BAND_"
        "PRIMARY_discriminator_FHRR_vs_CYCLIC_log2_delta_3p32_seed7_4p32_seed13_4p32_seed19_all_HP_wide_margin_"
        "SECONDARY_discriminator_nested_vs_flat32_log2_delta_0p000_seed7_1p000_seed13_1p000_seed19_HP_gate_0p1_"
        "seed_7_fails_secondary_gate_FLAT_32_cliff_shifts_K_100_to_K_200_codebook_draw_seed_dependence_"
        "NESTED_cliff_rock_solid_K_100_all_3_seeds_cv_0p000_MAIN_mechanism_stable_"
        "CYCLIC_positive_control_cliff_K_1000_cv_0p000_stable_"
        "FLAT_32_cliff_cv_0p079_variance_source_"
        "pairs_differ_10_of_10_all_seeds_cardinality_35_of_35_per_seed_"
        "prior_v2_CG_N_4096_had_cliff_cv_0p000_v3_does_NOT_reproduce_that_discipline_at_N_16384_"
        "auditor_MM_tier_captures_substantive_positive_finding_mechanism_scales_N_16384_primary_claim_"
        "flags_seed_dependent_variance_secondary_discriminator_NOT_chain_grade_lift_over_v2"
    ),
    "cert_increment_delta": 0,
    "cv": 0.0789,
    "referent_pointer": {
        "notes_path": None,
        "metrics_path": "data/exp_substrate_theta_gamma_v3_N16384_gpu_seed_{7,13,19}/metrics.json",
        "prereg_path": "preregs/2026-07-01_theta_gamma_v3_N16384_gpu.md",
        "parent_v2_CG_atom_at_N_4096": "T3/EXP_substrate_theta_gamma_v2_FHRR_all_complex_3seed_HP_CG_axes_I_plus_J_phase_diagram_2026-06-30",
        "atom_qualified_id": f"math::{ATOM_9_ID}",
    },
    "supersedes": None,
    "note": (
        "theta_gamma_v3_N16384_gpu_3seed_MEASURED_MECHANISM_cross_seed_unanimity_broken_"
        "2_of_3_HP_seeds_13_19_seed_7_MIDDLE_BAND_"
        "primary_discriminator_FHRR_vs_CYCLIC_log2_delta_at_or_above_3p32_all_3_seeds_HP_wide_margin_"
        "secondary_discriminator_nested_vs_flat32_fails_on_seed_7_delta_0p000_"
        "FLAT_32_cliff_shifts_K_100_to_K_200_for_seed_7_codebook_draw_seed_dependence_"
        "NESTED_MAIN_mechanism_cliff_K_100_cv_0p000_across_all_3_seeds_rock_solid_"
        "CYCLIC_positive_control_cliff_K_1000_cv_0p000_stable_across_seeds_"
        "prior_v2_CG_N_4096_had_cliff_cv_0p000_v3_does_NOT_reproduce_perfect_reproducibility_at_N_16384_"
        "auditor_discipline_cross_seed_2_of_3_HP_is_NOT_chain_grade_when_parent_had_3_of_3_HP_at_cv_0p000_"
        "bar_not_lowered_MM_captures_substantive_positive_finding_"
        "revival_criterion_run_5_to_10_seeds_or_investigate_FLAT_32_codebook_seed_dependence_at_N_16384_"
        "or_extend_K_sweep_resolution_K_125_150_175_around_FLAT_32_cliff_"
        "v2_parent_atom_preserved_not_superseded_valid_at_N_4096_setpoint"
    ),
}

# ---------- Atomic write ----------
def atomic_append_jsonl(path: pathlib.Path, records: list[dict]) -> tuple[int, int]:
    """Atomic tmp-write + os.replace + verify-load. Returns (lines_before, lines_after)."""
    lines_before = 0
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            lines_before = sum(1 for _ in f)

    tmp_path = path.with_suffix(path.suffix + ".tmp")
    existing_content = b""
    if path.exists():
        existing_content = path.read_bytes()
    if existing_content and not existing_content.endswith(b"\n"):
        existing_content += b"\n"
    new_lines = b""
    for rec in records:
        line = json.dumps(rec, ensure_ascii=False) + "\n"
        new_lines += line.encode("utf-8")
    tmp_path.write_bytes(existing_content + new_lines)

    with tmp_path.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            try:
                json.loads(line)
            except json.JSONDecodeError as e:
                raise RuntimeError(f"Corrupt JSON at line {i+1} in {tmp_path}: {e}")

    os.replace(tmp_path, path)

    lines_after = 0
    with path.open("r", encoding="utf-8") as f:
        lines_after = sum(1 for _ in f)

    return lines_before, lines_after


def main():
    math_before, math_after = atomic_append_jsonl(MATH_ATOMS, [ATOM_9])
    print(f"math/atoms.jsonl: {math_before} -> {math_after} (+{math_after - math_before})")

    ledger_records = [LEDGER_9]
    led_before, led_after = atomic_append_jsonl(CERT_LEDGER, ledger_records)
    print(f"meta/cert_ledger.jsonl: {led_before} -> {led_after} (+{led_after - led_before})")

    print()
    print(f"CERT delta: +0 (Atom 9 theta_gamma v3 MEASURED_MECHANISM; cross-seed unanimity broken)")
    print(f"Session-cumulative today: CG=+6, MM=+2, HF=+1, meta_amendment=+1")
    print(f"  Wave 1 CG: Atom 1 (M-sweep v3), Atom 2 (population coding), Atom 5 (task_vector K500)")
    print(f"  Wave 2 CG: Atom 6 (multihop depth 40), Atom 7 (refuse-gate V_REL)")
    print(f"  Wave 3 CG: Atom 8 (N-sweep amended-scope)")
    print(f"  Wave 4 MM: Atom 9 (theta_gamma v3 N=16384 cross-seed unanimity broken)")
    print(f"Timestamp: {TS_NOW}")
    print(f"Commit: {COMMIT}")


if __name__ == "__main__":
    main()
