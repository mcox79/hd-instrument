"""A5-gated atomize: BATCH 2026-06-28 evening.

Landing 1 (PARIETAL MOVABLE-REBIND PHASE DIAGRAM v1 SMOKE):
  Verdict: HARD_PASS (smoke 4-corner). Cert class: mechanism_characterization.
  CERT delta = 0.
  CRITICAL CORRECTION TO LANDING NARRATIVE: User framing said "FULL 3-seed all HARD_PASS
  at 13:36-13:37 PDT". Verify-OFF-DATA shows:
    - data/exp_substrate_parietal_movable_rebind_phase_diagram_v1_seed_{7,13,19}/metrics.json
      ALL have run_mode="self_test", elapsed_s=0.0, no phase_map field; ts_iso 16:36-16:37Z = 12:36-12:37 EDT.
    - The actual seed metrics.json files are SELF-TESTS (1 point each, n_scenes=3 stub),
      NOT FULL 56-point phase sweeps.
  The ONLY landed real-data file is the SMOKE: data/exp_substrate_parietal_movable_rebind_phase_diagram_v1_seed_7_smoke/metrics.json
    - 4 corners, smoke HARD_PASS, n_sat=3, n_fail=1 (cliff at g=32,n=200,mf=0.5 -> 0.25),
      n_strong=3, AM clean, arms-distinct True.
  Pre-reg/cell drift noted:
    - Pre-reg said n_objs in {3, 8, 20, 50}; cell sweeps {8, 20, 50, 100, 200} (5 values, dropped n=3, added 100/200).
      Cell-author comment: "Extended based on empirical probe; cliff begins around n_obj=100 at N=1024;
      Plate analytic cap underestimates substrate capacity by ~2x" -- this is META_RULE_AN-pattern.
    - Pre-reg said smoke corners include move_freq=0.8; cell uses mf=0.5 across all 4 smoke corners.
    - Pre-reg said FULL = 4*4*4 = 64 points; cell filters n_obj <= n_pos -> 56 points (skips n=20/50/100/200 at g=4).
  Cliff localization (smoke evidence): substrate drops from 1.000 -> 0.250 between
    (g=16, n=20, mf=0.5) and (g=32, n=200, mf=0.5). Smoke does not bracket the cliff tightly.
  Chain-grade promotion REQUIRES: 3-seed FULL re-dispatch (56 points/seed) + cv check + cliff-bracket verification.
  Counts as: mechanism_characterization (cliff existence + saturation regime + arms-distinct confirmed at smoke).

Landing 2 (MULTIHOP PHASE DIAGRAM depth*V_C*N_chains SMOKE_v3):
  Verdict: SMOKE_GATE_FAIL. Cert class: mechanism_characterization (honest-negative; test-design driven).
  CERT delta = 0.
  Failure decomposition (verify-OFF-DATA recompute):
    Gate 1 cardinality_ok=True (4 corners observed)
    Gate 2 arm_discrim_fires=4/4 (all >0.20 sub-rand lift)
    Gate 3 saturation_observed=True (corner 3 at 1.000; corner 4 at 0.990)
    Gate 4 regime_fail_observed=False  -- FAILED (no corner < 0.10)
    Gate 5 arms_differ_all=True (4 distinct SHA-256 pairs)
    Gate 6 sat_corner_ok=False (corner 1 at 0.940 vs threshold >=0.95; 0.01 short -- rounding noise)
    Gate 7 cross_cell_ok=True (corner 2 at 0.820, in pre-reg [0.75,0.86] band -- reproduces v1 anchor 0.808)
    Gate 8 fail_corner_ok=False  -- FAILED (corner 4 hit 0.990 vs threshold <0.10)
    Gate 9 gpu_util_ok=False  -- FAILED (n_samples=0; mean=0.0; cuda avail True but no samples appended)
  Failure modes:
    (a) NOT cell-bug for substrate mechanism -- substrate over-performed prediction at fail-corner
        (oracle reduces effective V_C = V_C/N_PARTITIONS = 16000/20 = 800; top1_pred formula didn't account for this)
        TEST-DESIGN issue: the `top1_pred` cone-formula extrapolation is wrong at high V_C with partition-oracle.
    (b) GPU util sampling is broken: torch.cuda.utilization(0) wrapped in try/except Exception -> swallows
        any NVML/pynvml error and returns 0.0 without appending to _GPU_UTIL_SAMPLES.
        Silent-except violation per META_RULE_J (no silent except).
    (c) Sat corner 0.940 vs 0.95 threshold: stochastic noise at n_chains=50 (std ~0.034); not real failure.
  Root cause primary: (a) -- test-design: predictive model conflated nominal V_C with effective_V_C_after_partition.
  Substrate did its job; the bands the cell was tested against were wrong.
  Recommendation:
    - Cell-author to fix top1_pred formula: account for partition-routing reducing effective V_C
      (effective_V_C = V_C / N_PARTITIONS = 20 in current config; constant across V_C sweep!)
    - The cell should sweep N_PARTITIONS too, OR explicitly compute top1_pred from per-step floor at part_size.
    - Cell-author to FIX gpu_util sampling: remove silent except OR log exception to a separate counter.
    - Research to re-spec: with partition_size held constant at 800 (V_C=16000, N_PARTITIONS=20), this is
      effectively a V_C=200 task; the "16000" axis isn't testing what it claims.
    - Re-dispatch SMOKE_v4 after cell-fix + pre-reg band re-derivation.

A5 protocol:
  1. Read pre-write line counts; build 2 atoms + 2 ledger rows in memory
  2. Append parietal atom to math/atoms.jsonl via tmp -> os.replace
  3. Append multihop atom to math/atoms.jsonl via tmp -> os.replace
  4. Append both cert_ledger rows to meta/cert_ledger.jsonl
  5. Verify-load: +2 to math/atoms.jsonl, +2 to cert_ledger.jsonl; tail parses; round-trip IDs match

Anchors (load-bearing absolute paths):
  PARIETAL:
    - notes/skunkworks_batch_parietal_movable_HP_multihop_smoke_fail_2026-06-28.md
    - data/exp_substrate_parietal_movable_rebind_phase_diagram_v1_seed_7_smoke/metrics.json
    - data/exp_substrate_parietal_movable_rebind_phase_diagram_v1_seed_{7,13,19}/metrics.json  (self_test stubs ONLY)
    - preregs/2026-06-28_substrate_parietal_movable_rebind_phase_diagram_v1.md
    - experiments/exp_substrate_parietal_movable_rebind_phase_diagram_v1_seed_{7,13,19}.py
    - experiments/_parietal_phase_diagram_v1_base.py
  MULTIHOP:
    - data/exp_substrate_multihop_phase_diagram_depth_VC_NChains_v1_smoke_v3/metrics.json
    - preregs/2026-06-28_substrate_multihop_phase_diagram_depth_VC_NChains_v1.md
    - experiments/exp_substrate_multihop_phase_diagram_depth_VC_NChains_v1.py
"""

import json
import os
import time
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
MATH_ATOMS = ROOT / "data/substrate_index/math/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"

ATOMIZED_BY = "skunkworks_atomize_batch_parietal_smoke_HP_multihop_smoke_fail_2026-06-28"
ATOMIZED_DATE = "2026-06-28"
CELL_COMMIT = "fade4410"

# ============================================================
# ATOM 1: PARIETAL MOVABLE-REBIND PHASE DIAGRAM SMOKE HARD_PASS
# ============================================================
parietal_atom = {
    "id": "T3/EXP_parietal_movable_rebind_phase_diagram_v1_SMOKE_HARD_PASS_cliff_g32_n200_mf05_FULL_NOT_RUN_2026-06-28",
    "name": (
        "Parietal MOVABLE-rebind phase diagram v1 SMOKE HARD_PASS (4-corner cliff observed at g=32 n_obj=200 mf=0.5 substrate=0.25; "
        "saturation observed at g=8/16 n_obj=8/20 mf=0.5; FULL 56-point 3-seed sweep NOT RUN -- per-seed metrics.json are self_test stubs only)"
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record",
    "description": (
        "Layer-1 phase-diagram MAP cell for parietal MOVABLE-rebind (HRR-bind + apply MOVE rebind + unbind cleanup). "
        "OFF-DATA recompute on data/exp_substrate_parietal_movable_rebind_phase_diagram_v1_seed_7_smoke/metrics.json: "
        "n_points=4, n_sat=3, n_fail=1, n_strong=3, META_AM_breaches=[], arms_distinct=True. SMOKE_HARD_PASS confirmed. "
        "Per-corner: (g=8,n=8,mf=0.5) sub=1.000 rand=0.000 static=0.000 -- saturate + STATIC fails confirming rebind discriminator. "
        "(g=16,n=20,mf=0.5) sub=1.000 rand=0.050 static=0.000 -- still saturated at higher load. "
        "(g=32,n=200,mf=0.5) sub=0.250 rand=0.000 static=0.000 -- CLIFF observed (far over-capacity). "
        "(g=4,n=8,mf=0.0) sub=1.000 rand=0.300 static=1.000 -- sanity baseline (no rebind; SUB=STATIC as expected). "
        "Cliff localization: substrate drops 1.000 -> 0.250 between (g=16,n=20,mf=0.5) and (g=32,n=200,mf=0.5); smoke does not bracket tightly. "
        "CRITICAL: the FULL 56-point 3-seed sweep DID NOT RUN. Per-seed metrics.json files at seed_7/13/19 contain run_mode='self_test', "
        "elapsed_s=0.0, no phase_map field (1-point selftest stubs only). Landing narrative claim of '3-seed all HARD_PASS at 13:36-13:37 PDT' "
        "is INCORRECT (Fix #28 / BIAS-Q violation; ts_iso says 16:36-16:37Z = 12:36-12:37 EDT). "
        "Pre-reg vs cell drift: pre-reg n_objs={3,8,20,50}, cell {8,20,50,100,200}; cell-author rationale: 'Plate analytic cap "
        "underestimates substrate by ~2x at N=1024' -- META_RULE_AN pattern. Pre-reg smoke corners include mf=0.8; cell uses mf=0.5 throughout. "
        "Cell filter n_obj<=n_pos drops FULL from 4*5*4=80 to 56 points. "
        "Promotion to chain-grade phase-characterization gates on: (a) 3-seed FULL (56 pts/seed) re-dispatch landing real phase_map data, "
        "(b) cross-seed cv<0.15 on cliff location, (c) cliff bracket verification (currently 1.000->0.250 jump is too wide). "
        "Counts as mechanism_characterization at smoke: cliff existence proven, saturation regime confirmed, arms-distinct, rebind discriminator (sub vs static) lift=1.000 at saturation."
    ),
    "aliases": [
        "parietal_movable_rebind_phase_diagram_v1_SMOKE_HARD_PASS_2026-06-28",
        "parietal_HRR_MOVE_rebind_cliff_smoke_g32_n200_mf05_2026-06-28",
    ],
    "metadata": {
        "provenance_quality": "MEASURED",
        "cert_status": "smoke_hard_pass_full_not_run",
        "cert_class": "mechanism_characterization",
        "verdict": "SMOKE_HARD_PASS",
        "verdict_subtype": "SMOKE_HP_4_CORNER_CLIFF_OBSERVED_FULL_56PT_3SEED_NOT_LANDED",
        "cell_commit": CELL_COMMIT,
        "cell_path": "experiments/exp_substrate_parietal_movable_rebind_phase_diagram_v1_seed_7.py",
        "engine_path": "experiments/_parietal_phase_diagram_v1_base.py",
        "prereg_path": "preregs/2026-06-28_substrate_parietal_movable_rebind_phase_diagram_v1.md",
        "metrics_path_smoke": "data/exp_substrate_parietal_movable_rebind_phase_diagram_v1_seed_7_smoke/metrics.json",
        "metrics_path_seed_7_selftest": "data/exp_substrate_parietal_movable_rebind_phase_diagram_v1_seed_7/metrics.json",
        "metrics_path_seed_13_selftest": "data/exp_substrate_parietal_movable_rebind_phase_diagram_v1_seed_13/metrics.json",
        "metrics_path_seed_19_selftest": "data/exp_substrate_parietal_movable_rebind_phase_diagram_v1_seed_19/metrics.json",
        "atomized_by": ATOMIZED_BY,
        "atomized_date": ATOMIZED_DATE,
        "verified_off_data": True,
        "verified_off_data_evidence": (
            "Python recompute on smoke metrics.json: n_sat=3 n_fail=1 n_strong=3 cardinality_ok=True arms_distinct=True; "
            "Per-seed FULL metrics inspection: ALL three (seed_7/13/19) have run_mode='self_test' elapsed_s=0.0 NO phase_map field; "
            "smoke phase_map per-corner re-verified."
        ),
        "regime": {
            "N_DIM": 1024,
            "n_half": 512,
            "encoder": "FHRR_complex_unit_modulus_multiscale_frady_kanerva",
            "k_scales": 4,
            "position_noise": 0.05,
            "n_scenes_per_point_smoke": 20,
            "n_scenes_per_point_full": 20,
            "arms": ["substrate_hrr", "random", "static_binding"],
        },
        "smoke_per_corner": [
            {"grid": 8, "n_obj": 8, "move_freq": 0.5, "n_pos": 64, "substrate": 1.0, "random": 0.0, "static": 0.0, "lift_static": 1.0},
            {"grid": 16, "n_obj": 20, "move_freq": 0.5, "n_pos": 256, "substrate": 1.0, "random": 0.05, "static": 0.0, "lift_static": 1.0},
            {"grid": 32, "n_obj": 200, "move_freq": 0.5, "n_pos": 1024, "substrate": 0.25, "random": 0.0, "static": 0.0, "lift_static": 0.25},
            {"grid": 4, "n_obj": 8, "move_freq": 0.0, "n_pos": 16, "substrate": 1.0, "random": 0.3, "static": 1.0, "lift_static": 0.0},
        ],
        "cliff_localization_smoke_only": {
            "saturate_to_cliff_jump": "1.000 -> 0.250 between (g=16,n=20,mf=0.5) and (g=32,n=200,mf=0.5)",
            "tightness": "WIDE_JUMP_NOT_BRACKETED",
            "promotion_blocker": "cliff bracket undetermined at smoke; needs FULL 56-pt sweep",
        },
        "full_run_status": {
            "expected_n_points_per_seed": 56,
            "expected_n_seeds": 3,
            "observed_seeds_with_full_phase_map": 0,
            "observed_seeds_with_selftest_stub": 3,
            "remediation": "re_dispatch_FULL_seed_7_13_19_to_remote_cpu_queue_without_self_test_flag",
        },
        "prereg_vs_cell_drift": {
            "n_objs_pre_reg": [3, 8, 20, 50],
            "n_objs_cell": [8, 20, 50, 100, 200],
            "cell_author_rationale": "Plate analytic cap underestimates substrate by ~2x at N_DIM=1024 (META_RULE_AN pattern); empirical probe shows cliff begins at n_obj=100",
            "smoke_corners_pre_reg": "include move_freq=0.8",
            "smoke_corners_cell": "all move_freq=0.5",
            "full_n_pre_reg": 64,
            "full_n_cell_after_n_obj_le_n_pos_filter": 56,
            "drift_severity": "MEDIUM (sweep ranges extended with rationale; smoke move_freq dropped without rationale; total points 64->56 filtered)",
        },
        "arms_distinct_sha256": True,
        "arms_hashes": {
            "substrate": "a76c5966972c7563b53b40da2845b4bdb73efde86a869b5b8cd444492ddfeda5",
            "random": "9bfe702cf30297dbdd1c56ae10551a4b71f54fb98c0634c60af5791f77997183",
            "static": "57ee4a85325755aff54a229ca2be48988450e4ec8724fc71275d1629701e4cc4",
        },
        "promotion_recommendation": (
            "WAIT for actual 3-seed FULL 56-pt phase sweep landings before chain-grade promotion. "
            "Cell-author re-dispatch instruction: queue seed_7/13/19 WITHOUT --self-test flag; verify run_mode='full' in landed metrics.json; "
            "verify phase_map has 56 entries per seed. Promotion gate: 3-seed cv<0.15 on cliff location AND cliff bracket narrowed (e.g., n_obj in {50, 100, 150, 200} at g=32)."
        ),
        "cert_increment_delta": 0,
        "discipline_tags": [
            "META_RULE_AC", "META_RULE_AE", "META_RULE_AF", "META_RULE_AG",
            "META_RULE_AM", "META_RULE_AN", "META_RULE_H",
            "DISCRIMINATOR_MUST_SURVIVE_SCALE_USER_2026-06-26",
            "Fix_28_per_arm_metrics_not_verdict_msg",
            "BIAS-Q_suspect_1p000_results",
            "feedback_no_hallucinated_numbers_verify_on_disk_2026-06-27",
            "feedback_metrics_path_disambiguation_selftest_smoke_full_2026-06-27",
        ],
        "next_actions": [
            "research_or_cell_author_re_dispatch_FULL_seed_7_13_19_to_remote_cpu_queue_no_self_test_flag",
            "verify_landed_metrics_run_mode_full_and_phase_map_n_56_per_seed",
            "post_3_seed_landing_re_VET_for_chain_grade_promotion_decision_with_cliff_bracket_check",
        ],
        "supersedes": None,
        "ts_iso_atomized": ATOMIZED_DATE,
    },
}

parietal_ledger = {
    "ts": time.time(),
    "op": "cert_ruling",
    "atom_id": f"math::{parietal_atom['id']}",
    "cert_status": "smoke_hard_pass_full_not_run",
    "cert_class": "mechanism_characterization",
    "verified_off_data": True,
    "atomized_by": ATOMIZED_BY,
    "cell_commit": CELL_COMMIT,
    "verdict": (
        "SMOKE_HARD_PASS_4corner_cliff_observed_g32_n200_mf05_sub_0p25_saturation_g8_g16_n8_n20_mf05_sub_1p0_arms_distinct_TRUE_lift_static_1p0_at_saturation_proving_rebind_discriminator_FULL_56pt_3seed_NOT_LANDED_seed_7_13_19_metrics_are_self_test_stubs_only_landing_framing_3_seed_FULL_HP_was_INCORRECT"
    ),
    "cert_increment_delta": 0,
    "cv": None,
    "referent_pointer": {
        "metrics_path_smoke": "data/exp_substrate_parietal_movable_rebind_phase_diagram_v1_seed_7_smoke/metrics.json",
        "metrics_path_seed_7_selftest": "data/exp_substrate_parietal_movable_rebind_phase_diagram_v1_seed_7/metrics.json",
        "metrics_path_seed_13_selftest": "data/exp_substrate_parietal_movable_rebind_phase_diagram_v1_seed_13/metrics.json",
        "metrics_path_seed_19_selftest": "data/exp_substrate_parietal_movable_rebind_phase_diagram_v1_seed_19/metrics.json",
        "prereg_path": "preregs/2026-06-28_substrate_parietal_movable_rebind_phase_diagram_v1.md",
        "cell_path": "experiments/exp_substrate_parietal_movable_rebind_phase_diagram_v1_seed_7.py",
        "atom_qualified_id": f"math::{parietal_atom['id']}",
    },
    "supersedes": None,
    "note": (
        "parietal_MOVABLE_rebind_v1_smoke_HARD_PASS_cliff_observed_g32_n200_mf05_substrate_0p25_FULL_3seed_NOT_LANDED_per_seed_metrics_are_self_test_stubs_re_dispatch_required_for_chain_grade_promotion"
    ),
}


# ============================================================
# ATOM 2: MULTIHOP PHASE DIAGRAM SMOKE_v3 SMOKE_GATE_FAIL
# ============================================================
multihop_atom = {
    "id": "T3/EXP_substrate_multihop_phase_diagram_depth_VC_NChains_v1_SMOKE_v3_GATE_FAIL_test_design_2026-06-28",
    "name": (
        "Multihop phase diagram (depth*V_C*N_chains) v1 smoke_v3 SMOKE_GATE_FAIL (substrate over-performed fail-corner prediction "
        "due to partition-oracle reducing effective V_C; test-design issue not substrate failure; gpu_util silent-except bug)"
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record",
    "description": (
        "Layer-1 phase-diagram MAP cell for multihop reasoning at depth*V_C*N_chains. Smoke_v3 landed at "
        "data/exp_substrate_multihop_phase_diagram_depth_VC_NChains_v1_smoke_v3/metrics.json. SMOKE_GATE_FAIL. "
        "OFF-DATA recompute confirms 3 of 9 gates failed: (Gate 4) regime_fail_observed=False; (Gate 8) fail_corner_ok=False; (Gate 9) gpu_util_ok=False. "
        "Per-corner: corner1 (d=5,V_C=200,N=50) top1_sub=0.940 saturated=False arms_differ=True; "
        "corner2 (d=15,V_C=200,N=200) top1_sub=0.820 arms_differ=True (reproduces v1 anchor 0.808 in pre-reg cross_cell band [0.75,0.86]); "
        "corner3 (d=5,V_C=16000,N=50) top1_sub=1.000 saturated=True arms_differ=True; "
        "corner4 (d=15,V_C=16000,N=200) top1_sub=0.990 saturated=True arms_differ=True. "
        "Pre-reg predicted corner4 top1_pred=0.0 (i.e., regime-fail null check), but substrate hit 0.99. "
        "ROOT CAUSE diagnosis (test-design issue, NOT substrate failure): the SUBSTRATE arm uses partition-routed oracle cleanup with "
        "N_PARTITIONS=20, reducing effective per-step search to V_C/N_PARTITIONS. At V_C=16000 this is part_size=800, NOT 16000. "
        "The cone-formula top1_pred extrapolation (anchored on v1 0.808 at V_C=200, scaled by V_C*N_chains ratio) implicitly assumed "
        "full-V_C search per step. With partition-oracle, the EFFECTIVE V_C is held nearly constant (~part_size=800 at V_C=16000), so "
        "substrate top1 stays high. The fail-corner is therefore not testing what the pre-reg claims; the 'fail at high V_C' regime "
        "doesn't exist in this cell as written. Secondary issue: gpu_util_n_samples=0 despite gpu_avail=True; sample_gpu_util() wraps "
        "torch.cuda.utilization(0) in try/except Exception which silently returns 0.0 and never appends to _GPU_UTIL_SAMPLES (META_RULE_J "
        "no-silent-except violation; NVML/pynvml not initialized typical cause). Tertiary: sat_corner top1=0.940 vs threshold 0.95 is "
        "stochastic noise (n_chains=50; binomial std ~0.034); 0.01 below threshold is within noise. "
        "FAILURE MODE CLASSIFICATION: (b) test-design issue -- substrate is healthy; the predictive bands were derived from a model that "
        "didn't account for partition-routing. Remediation: cell-author to either (i) sweep N_PARTITIONS holding part_size~constant, "
        "(ii) recompute top1_pred per-corner using effective V_C = V_C/N_PARTITIONS, OR (iii) drop the high-V_C regime-fail null since "
        "partition-oracle makes that regime not actually failing. Also fix gpu_util silent-except: log exceptions to a counter so the "
        "gate can distinguish 'sampled 0' from 'never sampled'. After cell-fix, re-dispatch smoke_v4 with corrected bands."
    ),
    "aliases": [
        "multihop_phase_diagram_depth_VC_NChains_v1_SMOKE_GATE_FAIL_test_design_2026-06-28",
        "multihop_phase_diagram_v1_smoke_v3_GATE_FAIL_partition_oracle_test_design_flaw_2026-06-28",
    ],
    "metadata": {
        "provenance_quality": "MEASURED",
        "cert_status": "smoke_gate_fail",
        "cert_class": "mechanism_characterization",
        "verdict": "SMOKE_GATE_FAIL",
        "verdict_subtype": "TEST_DESIGN_FAILURE_PARTITION_ORACLE_EFFECTIVE_V_C_NOT_NOMINAL_V_C_GPU_UTIL_SILENT_EXCEPT_BUG",
        "cell_commit": CELL_COMMIT,
        "cell_path": "experiments/exp_substrate_multihop_phase_diagram_depth_VC_NChains_v1.py",
        "prereg_path": "preregs/2026-06-28_substrate_multihop_phase_diagram_depth_VC_NChains_v1.md",
        "metrics_path": "data/exp_substrate_multihop_phase_diagram_depth_VC_NChains_v1_smoke_v3/metrics.json",
        "atomized_by": ATOMIZED_BY,
        "atomized_date": ATOMIZED_DATE,
        "verified_off_data": True,
        "verified_off_data_evidence": (
            "Python recompute on metrics.json per_seed[0]: cardinality_ok=True (4/4); arms_differ_all=True (4 SHA pairs distinct); "
            "arm_discrim_count=4; sat_corner top1=0.940 (<0.95 by 0.01); fail_corner top1=0.990 (>>0.10); "
            "gpu_util_n_samples=0 gpu_util_mean=0.0 despite gpu_avail=True name='NVIDIA GeForce RTX 4060 Ti'; "
            "cross_cell corner (15,200,200) top1=0.820 IN pre-reg [0.75,0.86] cross-cell rail (v1 anchor 0.808 reproduced)."
        ),
        "regime": {
            "N_DIM": 8192,
            "depths_smoke": [5, 15],
            "V_Cs_smoke": [200, 16000],
            "N_chains_smoke": [50, 200],
            "N_PARTITIONS": 20,
            "part_size_at_V_C_200": 10,
            "part_size_at_V_C_16000": 800,
            "max_W_depth": 15,
            "V_P": 10,
            "encoder": "SUBSTRATE_NATIVE_BIPOLAR",
            "arms": ["SUBSTRATE_partition_routed_oracle_cleanup", "RANDOM_uniform_pick_from_codebook"],
        },
        "smoke_per_corner": [
            {"corner_idx": 0, "depth": 5, "V_C": 200, "N_chains": 50, "top1_substrate": 0.940, "top1_random": 0.000, "top1_pred": 0.9824, "HP": 0.50, "HF": 0.25, "saturated": False, "arms_differ": True, "tier": "HARD_PASS"},
            {"corner_idx": 1, "depth": 15, "V_C": 200, "N_chains": 200, "top1_substrate": 0.820, "top1_random": 0.000, "top1_pred": 0.808, "HP": 0.50, "HF": 0.25, "saturated": False, "arms_differ": True, "tier": "HARD_PASS"},
            {"corner_idx": 2, "depth": 5, "V_C": 16000, "N_chains": 50, "top1_substrate": 1.000, "top1_random": 0.000, "top1_pred": 0.2414, "HP": 0.10, "HF": 0.05, "saturated": True, "arms_differ": True, "tier": "HARD_PASS"},
            {"corner_idx": 3, "depth": 15, "V_C": 16000, "N_chains": 200, "top1_substrate": 0.990, "top1_random": 0.000, "top1_pred": 0.0000, "HP": 0.05, "HF": 0.02, "saturated": True, "arms_differ": True, "tier": "HARD_PASS"},
        ],
        "gates_failed": {
            "regime_fail_observed": False,
            "sat_corner_ok": False,
            "fail_corner_ok": False,
            "gpu_util_ok": False,
        },
        "gates_passed": {
            "cardinality_ok": True,
            "arm_discrim_fires_ge_2": True,
            "arm_discrim_count": 4,
            "saturation_observed": True,
            "arms_differ_all": True,
            "cross_cell_rail_ok": True,
        },
        "failure_mode_classification": "b_test_design_issue_partition_oracle_effective_V_C_not_nominal",
        "primary_root_cause": (
            "top1_pred cone-formula extrapolation assumed full-V_C per-step search; substrate arm uses partition-routed oracle "
            "cleanup with N_PARTITIONS=20 holding part_size constant at ~800 (at V_C=16000); effective_V_C is ~part_size, NOT nominal V_C. "
            "Result: substrate top1 stays high across V_C sweep because the actual per-step problem isn't getting harder."
        ),
        "secondary_issues": [
            "gpu_util_n_samples=0 despite gpu_avail=True; sample_gpu_util try/except swallows NVML init errors silently (META_RULE_J violation)",
            "sat_corner top1=0.940 vs threshold 0.95 is stochastic noise (n_chains=50 binomial std ~0.034); not real failure",
        ],
        "is_substrate_failure": False,
        "is_cell_bug": False,
        "is_test_design_issue": True,
        "remediation_options": [
            "i_sweep_N_PARTITIONS_holding_part_size_constant_to_test_actual_per_step_difficulty_axis",
            "ii_recompute_top1_pred_per_corner_using_effective_V_C_eq_V_C_div_N_PARTITIONS_with_anchor_at_part_size_200",
            "iii_drop_high_V_C_regime_fail_null_since_partition_oracle_makes_that_regime_not_actually_failing",
            "iv_fix_gpu_util_silent_except_log_exceptions_to_counter_so_gate_distinguishes_sampled_0_from_never_sampled",
        ],
        "recommended_action": "research_re_spec_pre_reg_with_effective_V_C_bands_and_partition_size_axis_then_cell_author_re_dispatch_smoke_v4",
        "cert_increment_delta": 0,
        "discipline_tags": [
            "META_RULE_AC", "META_RULE_AE", "META_RULE_AF", "META_RULE_AG",
            "META_RULE_AH", "META_RULE_AN", "META_RULE_H", "META_RULE_J",
            "DISCRIMINATOR_MUST_SURVIVE_SCALE_USER_2026-06-26",
            "Fix_24_GPU_dispatch_must_actually_use_GPU",
            "Fix_28_per_arm_metrics_not_verdict_msg",
            "BIAS-Q_suspect_1p000_results",
            "BIAS-N_verify_referent_verdict_field",
            "feedback_compute_formulas_in_code_before_quoting_2026-06-27",
        ],
        "next_actions": [
            "research_re_spec_pre_reg_top1_pred_formula_uses_effective_V_C_eq_V_C_div_N_PARTITIONS",
            "cell_author_fix_sample_gpu_util_remove_silent_except",
            "cell_author_consider_sweeping_N_PARTITIONS_axis_instead_of_or_in_addition_to_V_C",
            "re_dispatch_smoke_v4_after_pre_reg_band_recompute_and_gpu_util_fix",
        ],
        "supersedes": None,
        "ts_iso_atomized": ATOMIZED_DATE,
    },
}

multihop_ledger = {
    "ts": time.time(),
    "op": "cert_ruling",
    "atom_id": f"math::{multihop_atom['id']}",
    "cert_status": "smoke_gate_fail",
    "cert_class": "mechanism_characterization",
    "verified_off_data": True,
    "atomized_by": ATOMIZED_BY,
    "cell_commit": CELL_COMMIT,
    "verdict": (
        "SMOKE_GATE_FAIL_3of9_gates_failed_regime_fail_observed_False_fail_corner_ok_False_gpu_util_ok_False_root_cause_test_design_partition_oracle_effective_V_C_not_nominal_V_C_substrate_top1_0p990_at_predicted_0p000_corner_NOT_substrate_failure_NOT_cell_bug_test_design_issue_cell_author_fix_gpu_util_silent_except_research_re_spec_pre_reg_bands_with_effective_V_C"
    ),
    "cert_increment_delta": 0,
    "cv": None,
    "referent_pointer": {
        "metrics_path": "data/exp_substrate_multihop_phase_diagram_depth_VC_NChains_v1_smoke_v3/metrics.json",
        "prereg_path": "preregs/2026-06-28_substrate_multihop_phase_diagram_depth_VC_NChains_v1.md",
        "cell_path": "experiments/exp_substrate_multihop_phase_diagram_depth_VC_NChains_v1.py",
        "atom_qualified_id": f"math::{multihop_atom['id']}",
    },
    "supersedes": None,
    "note": (
        "multihop_phase_diagram_v1_smoke_v3_SMOKE_GATE_FAIL_3_gate_fails_test_design_issue_partition_oracle_effective_V_C_makes_high_V_C_regime_not_fail_as_predicted_substrate_healthy_gpu_util_silent_except_secondary_bug_research_re_spec_then_smoke_v4_DO_NOT_promote_DO_NOT_close_multihop_phase_direction"
    ),
}


# ============================================================
# A5 WRITE PROTOCOL
# ============================================================
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
    os.replace(str(tmp_path), str(path))

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
    print(f"[A5] BATCH atomize START {ATOMIZED_BY} ts={time.time():.3f}")
    print(f"[A5] parietal atom_id = math::{parietal_atom['id'][:80]}...")
    print(f"[A5] multihop atom_id = math::{multihop_atom['id'][:80]}...")

    append_jsonl_a5(MATH_ATOMS, parietal_atom, "math/atoms.jsonl <- parietal")
    append_jsonl_a5(CERT_LEDGER, parietal_ledger, "meta/cert_ledger.jsonl <- parietal ruling")
    append_jsonl_a5(MATH_ATOMS, multihop_atom, "math/atoms.jsonl <- multihop")
    append_jsonl_a5(CERT_LEDGER, multihop_ledger, "meta/cert_ledger.jsonl <- multihop ruling")

    print(f"[A5] BATCH DONE OK; parietal CERT delta=0 (smoke_HP not chain-grade; FULL not run); multihop CERT delta=0 (test-design SMOKE_GATE_FAIL)")
    print(f"[A5] BATCH total CERT delta = +0")


if __name__ == "__main__":
    main()
