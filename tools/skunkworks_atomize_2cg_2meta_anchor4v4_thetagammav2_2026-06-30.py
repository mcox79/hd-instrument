#!/usr/bin/env python3
"""Skunkworks A5-gated atomize: 2 chain-grade + 2 META rules (2026-06-30 batch).

Atoms:
  1. math::T3/EXP_substrate_anchor4_encoder_family_v4_3seed_HP_CG_encoder_axis_actually_wired_bundled_memory_2026-06-30
     (CHAIN_GRADE; cert delta +1)
  2. math::T3/EXP_substrate_theta_gamma_v2_FHRR_all_complex_3seed_HP_CG_axes_I_plus_J_phase_diagram_2026-06-30
     (CHAIN_GRADE; cert delta +1)
  3. meta::RULE_director_spawn_prompts_file_sizes_and_slugs_off_disk_verification_META_RULE_AZ_2026-06-30
     (METHODOLOGY_RULE; cert delta 0)
  4. meta::RULE_remote_runner_double_exp_prefix_slug_bug_theta_gamma_v2_META_RULE_BA_2026-06-30
     (METHODOLOGY_RULE; cert delta 0)

A5 GATING:
  PRE: CERT N = 634, axiom = 206, cap_pres = 6/6
  POST after atom1: CERT N = 635
  POST after atom2: CERT N = 636
  POST after atom3: CERT N = 636
  POST after atom4: CERT N = 636

Director ACK: explicit (2026-06-30 message).
Verified off-disk: Skunkworks landed-VET report this conversation.

Usage:
  .venv/Scripts/python.exe tools/skunkworks_atomize_2cg_2meta_anchor4v4_thetagammav2_2026-06-30.py [--dry-run|--apply]
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier
from tools.cert_ledger_writer import (
    append_cert_ledger_row,
    build_chain_grade_ruling_row,
    _cert_count,
    _axiom_count,
    _cap_pres_ok,
)

STORE_ROOT = Path(__file__).resolve().parent.parent / "data" / "substrate_index"


def atom_anchor4_v4_chain_grade() -> Atom:
    return Atom(
        id=("T3/EXP_substrate_anchor4_encoder_family_v4_3seed_HP_CG_"
            "encoder_axis_actually_wired_bundled_memory_2026-06-30"),
        name=(
            "ANCHOR 4 v4 encoder_family 3-seed CHAIN_GRADE: 5/5 encoders "
            "distinct + chain-grade per Pareto-AUC; v3 bit-identical trap "
            "CLOSED via bundled-memory mechanism"
        ),
        description=(
            "CHAIN_GRADE landed-VET of cell substrate_anchor4_encoder_family_v4 "
            "over 3 seeds (7, 13, 19). Cell commit a17e13be by hdi_exp_dev "
            "a1be2051. Off-disk recompute by Skunkworks 2026-06-30 ~20:00 UTC. "
            "OFF-DATA RESULTS (independent recompute from metrics.fresh JSONs):\n"
            "  - 180/180 phase-diagram cells observed all 3 seeds "
            "(N_DIM x 3 / decay x 3 / load x 4 / encoders x 5 = 180 exact); "
            "cardinality_ok=True all seeds.\n"
            "  - 5/5 encoders chain-grade per Pareto-AUC: binary_bipolar, "
            "hrr_real, fhrr, sparse_bipolar, sparse_real. n_encoders_chain_grade=5.\n"
            "  - 10/10 arm pairs differ (mechanism_hash vs random_hash) all 3 "
            "seeds; per-encoder arms_differ_per_encoder all True.\n"
            "  - 9/10 metric-distinct seed_7; 8/10 seeds 13/19 "
            "(cross_encoder_metric_distinct |delta| values 0.04-0.40 range; "
            "min 0.0408 sparse_real vs hrr_real edge-case).\n"
            "  - 0% saturation: saturation_frac_total=0.0, n_saturated_cells_total=0.\n"
            "  - overall_dominance_rate=1.000 all 3 seeds; TD beats RD in all "
            "180 cells (mechanism unanimous). overall_rd_loss_rate=0.0.\n"
            "  - preflight_hashes SHA-256 distinct across 5 encoders within each "
            "seed AND distinct across 3 seeds within each encoder (15 distinct "
            "values; v3 bit-identical trap CLOSED).\n"
            "  - Cross-seed cv on top-level metrics: overall_dominance_rate "
            "cv=0.000; n_pairs_differ cv=0.000; n_pairs_metric_distinct cv=0.069; "
            "saturation_frac_total cv=0.000.\n"
            "  - Cross-seed cv on per-encoder mean td_minus_random_composite: "
            "binary=0.045, hrr=0.046, fhrr=0.034, sparse_bipolar=0.057, "
            "sparse_real=0.048 (all <= 0.058; well inside 0.10 bar).\n"
            "  - ws_retention=1.000 cells confined to FHRR + load=8.0 easy-corner "
            "(5-7 cells per seed); composite metric not saturated "
            "(saturated=False flag on every cell); regime-correct phase-diagram "
            "behavior, NOT META_RULE_Q violation.\n"
            "  - Positive control PASS all 3 seeds: binary_bipolar decay=180 "
            "load=8.0 N_DIM=4096 -> TD_DOMINATES (measured), "
            "recency_decode_acc=0.91 (target 0.7-0.999).\n"
            "  - elapsed_s = 4.24-4.32s per seed; sum(per-cell wall_s)=4.10-4.14s; "
            "internally consistent at ~23ms/cell across 180 numpy-vectorized "
            "phase-map cells. META_RULE_AV not triggered (run_mode=full, no "
            "_phase=selftest_done marker, work was actually done).\n"
            "PROMOTION TO CHAIN-GRADE: META_RULE_AX/AY/AW/Q all PASS. v3 "
            "dense-triplet bit-identical trap CLOSED via bundled-memory "
            "mechanism (index_add_ canonical HD capacity stressor introduced "
            "by cell-author beyond original spec). Encoder axis ACTUALLY wired "
            "into mechanism (pre-flight SHA-256 distinctness gate confirms; "
            "arms_differ_per_encoder confirms cross-encoder discrimination).\n"
            "REFERENT: data/exp_substrate_anchor4_encoder_family_v4_seed_{7,13,19}/"
            "metrics.fresh_2026-06-30.json (230KB each; remote-fetch mtime "
            "2026-06-30T19:43Z; slug per actual remote, NOT Director's cited "
            "'_phase_diagram_v4_' which composes with META_RULE_AZ)."
        ),
        kind=AtomKind.CHAIN_GRADE_PHASE_CHARACTERIZATION,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "CERT_CHAIN_GRADE",
            "cert_status": "chain_grade",
            "cert_class": "pre_reg_pass",
            "cert_increment_delta": 1,
            "verified_off_data": True,
            "atomized_by": "skunkworks_landed_VET_2026-06-30",
            "cell_commit": "a17e13be",
            "cell_author": "hdi_exp_dev_a1be2051",
            "anchor_name": "substrate_anchor4_encoder_family_phase_diagram_v4",
            "n_seeds_planned": 3,
            "n_seeds_run": 3,
            "seeds_landed": [7, 13, 19],
            "verdict": "HARD_PASS",
            "metrics_paths": [
                "data/exp_substrate_anchor4_encoder_family_v4_seed_7/metrics.fresh_2026-06-30.json",
                "data/exp_substrate_anchor4_encoder_family_v4_seed_13/metrics.fresh_2026-06-30.json",
                "data/exp_substrate_anchor4_encoder_family_v4_seed_19/metrics.fresh_2026-06-30.json",
            ],
            "discriminator": "Pareto_AUC_TD_dominates_RD_across_phase_diagram",
            "scope_observed": (
                "encoder_family x {binary_bipolar, hrr_real, fhrr, "
                "sparse_bipolar, sparse_real}, N_DIM x {2048,4096,8192}, "
                "decay_days x {30,60,180}, capacity_load_ratio x {8,12,16,24}, "
                "noise_sigma=0.1, R_BUCKETS=128, n_atoms=1500, n_days=365, "
                "bundled_memory=M_atoms_per_chunk"
            ),
            "scope_not_claimed": (
                "Does not characterize FHRR + load=8.0 easy-corner saturation as "
                "an intrinsic capability claim (regime-correct behavior of TD "
                "eviction policy at minimum capacity stress with strongest "
                "encoder; phase-diagram corner)."
            ),
            "cross_seed_stats": {
                "overall_dominance_rate_mean": 1.000,
                "overall_dominance_rate_cv": 0.000,
                "n_pairs_differ_mean": 10.0,
                "n_pairs_metric_distinct_mean": 8.333,
                "n_pairs_metric_distinct_cv": 0.069,
                "td_minus_random_composite_per_encoder_cv": {
                    "binary_bipolar": 0.045,
                    "hrr_real": 0.046,
                    "fhrr": 0.034,
                    "sparse_bipolar": 0.057,
                    "sparse_real": 0.048,
                },
            },
            "META_RULE_AX_per_arm_distinctness_strict_PASS": True,
            "META_RULE_AY_no_auto_demote_triggered": True,
            "META_RULE_AW_per_seed_config_distinct_PASS": True,
            "META_RULE_Q_no_suspect_1000_at_scale_PASS": True,
            "META_RULE_AV_not_selftest_run_mode_full_PASS": True,
            "v3_bit_identical_trap_closed": True,
            "bundled_memory_introduced_beyond_spec": True,
            "v3_encoder_axis_failure_class_resolved": True,
            "load_bearing_finding_1": (
                "Encoder axis (5 families) is now empirically wired into the "
                "mechanism: all 10 cross-encoder pairs distinct + all 5 "
                "encoders independently chain-grade per Pareto-AUC."
            ),
            "load_bearing_finding_2": (
                "Bundled memory via index_add_ is the canonical HD capacity "
                "stressor that resolves the v3 collapse-to-bit-identical "
                "failure mode; cell-author introduced beyond original spec."
            ),
            "ruling_note": (
                "11th CHAIN-GRADE promotion of session 2026-06-30 (CERT 634 -> 635)."
            ),
        },
    )


def atom_theta_gamma_v2_chain_grade() -> Atom:
    return Atom(
        id=("T3/EXP_substrate_theta_gamma_v2_FHRR_all_complex_3seed_HP_CG_"
            "axes_I_plus_J_phase_diagram_2026-06-30"),
        name=(
            "Theta-gamma v2 FHRR all-complex 3-seed CHAIN_GRADE: 5-arm cliff "
            "ordering identical cross-seed; first outer-axis CG on axes I "
            "(Sequence encoding) + J (Order binding)"
        ),
        description=(
            "CHAIN_GRADE landed-VET of cell substrate_theta_gamma_v2_FHRR_all_"
            "complex over 3 seeds (7, 13, 19). Cell commit 3faa827e by "
            "hdi_exp_dev af82e9d9. Off-disk recompute by Skunkworks 2026-06-30 "
            "~20:00 UTC.\n"
            "OFF-DATA RESULTS:\n"
            "  - 30/30 K-sweep cells observed all 3 seeds (5 arms x 6 K-values); "
            "cardinality_ok=True all seeds.\n"
            "  - 5-arm cliff ordering IDENTICAL across all 3 seeds: NO_POSITION=0, "
            "FHRR_FLAT_PHASE_8=0, FHRR_FLAT_PHASE_32=50, FHRR_NESTED_THETA_GAMMA=100, "
            "CYCLIC_SHIFT=200. cliff_log2_K_per_arm cv=0.000 (perfect "
            "cross-seed agreement on primary discriminator).\n"
            "  - max_fhrr_vs_cyclic_log2_delta=2.000 all 3 seeds (HP floor 0.3; "
            "6.7x margin).\n"
            "  - nested_vs_flat32_log2_delta=1.000 all 3 seeds (HP floor 0.1; "
            "10x margin; confirms theta-gamma nesting contributes beyond just "
            "FHRR phase representation).\n"
            "  - min_cross_arm_log2_delta=1.000 all 3 seeds; n_pairs_differ=10/10 "
            "all 3 seeds (all 5 arms distinct from all others).\n"
            "  - 15/15 per-arm raw-data signatures distinct across (arm x seed) "
            "via SHA-256 of (arm, K_SEQ, retrieval_acc, n_correct) tuples "
            "(no bit-identical recurrence; META_RULE_AX strict PASS).\n"
            "  - META_RULE_Q satisfied: 2/5 arms saturate at K=50 "
            "(CYCLIC_SHIFT + FHRR_NESTED_THETA_GAMMA at acc=1.0), but all "
            "5 arms collapse to acc=0.00-0.04 at K=2000 (the cliff is real, "
            "not a saturation artifact; mechanism produces expected cliff curve).\n"
            "  - no_position_acc_K50 = {0.02, 0.04, 0.0} (near-zero floor as "
            "expected for non-positional arm).\n"
            "  - elapsed_s = 18.26-21.30s per seed; cardinality + run_mode=full "
            "consistent (META_RULE_AV not triggered).\n"
            "  - Per-seed config_version distinct (seeds 7/13/19 explicit in "
            "config_version; META_RULE_AW seed-config-distinct PASS).\n"
            "  - Raw retrieval_acc cv at tail K (>500) reaches ~1.7 in absolute "
            "terms (relative variance over near-zero values; mean<0.05); "
            "discriminator metric (cliff_log2_K) is rock-solid at cv=0.000.\n"
            "PROMOTION TO CHAIN-GRADE: First outer-axis CG closure on both "
            "substrate axes I (Sequence encoding) AND J (Order binding) at "
            "chain-grade scale. Theta-gamma nesting demonstrated to contribute "
            "beyond just FHRR phase (NESTED outperforms FLAT_32 by 2x in cliff_K).\n"
            "REFERENT: data/exp_substrate_theta_gamma_v2_FHRR_all_complex_seed_"
            "{7,13,19}/metrics.fresh_2026-06-30.json (~11.6KB each; remote-fetch "
            "mtime 2026-06-30T19:25Z; remote slug had double 'exp_' prefix bug "
            "'exp_exp_substrate_theta_gamma_...' composes with META_RULE_BA)."
        ),
        kind=AtomKind.CHAIN_GRADE_PHASE_CHARACTERIZATION,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "CERT_CHAIN_GRADE",
            "cert_status": "chain_grade",
            "cert_class": "pre_reg_pass",
            "cert_increment_delta": 1,
            "verified_off_data": True,
            "atomized_by": "skunkworks_landed_VET_2026-06-30",
            "cell_commit": "3faa827e",
            "cell_author": "hdi_exp_dev_af82e9d9",
            "anchor_name": "substrate_theta_gamma_v2_FHRR_all_complex",
            "n_seeds_planned": 3,
            "n_seeds_run": 3,
            "seeds_landed": [7, 13, 19],
            "verdict": "HARD_PASS",
            "metrics_paths": [
                "data/exp_substrate_theta_gamma_v2_FHRR_all_complex_seed_7/metrics.fresh_2026-06-30.json",
                "data/exp_substrate_theta_gamma_v2_FHRR_all_complex_seed_13/metrics.fresh_2026-06-30.json",
                "data/exp_substrate_theta_gamma_v2_FHRR_all_complex_seed_19/metrics.fresh_2026-06-30.json",
            ],
            "discriminator": (
                "5-arm K-cliff phase diagram: NO_POSITION vs CYCLIC_SHIFT vs "
                "FHRR_FLAT_PHASE_8 vs FHRR_FLAT_PHASE_32 vs FHRR_NESTED_THETA_GAMMA; "
                "cliff_log2_K monotone-ordered + cross-arm-distinct"
            ),
            "scope_observed": (
                "arms x 5 (NO_POSITION, CYCLIC_SHIFT, FHRR_FLAT_PHASE_8, "
                "FHRR_FLAT_PHASE_32, FHRR_NESTED_THETA_GAMMA), "
                "K_SEQ x {50,100,200,500,1000,2000}, N_DIM=4096, "
                "ITEM_VOCAB=10000, POSITION_NESTED=64, NOISE_SIGMA=0.05"
            ),
            "scope_not_claimed": (
                "Does NOT claim K_SEQ > 2000 generalization (no measurements "
                "beyond K=2000); does NOT claim N_DIM != 4096 generalization "
                "(single-dim sweep). Closure scoped to axes I + J at "
                "N_DIM=4096, K_SEQ <= 2000."
            ),
            "cross_seed_stats": {
                "cliff_log2_K_cv_all_arms": 0.000,
                "max_fhrr_vs_cyclic_log2_delta_mean": 2.000,
                "nested_vs_flat32_log2_delta_mean": 1.000,
                "min_cross_arm_log2_delta_mean": 1.000,
                "n_pairs_differ_mean": 10.0,
            },
            "META_RULE_AX_per_arm_distinctness_strict_PASS": True,
            "META_RULE_Q_saturation_pattern_pre_reg_anticipated_PASS": True,
            "META_RULE_AW_per_seed_config_distinct_PASS": True,
            "META_RULE_AV_not_selftest_run_mode_full_PASS": True,
            "substrate_axes_closed": [
                "I_Sequence_encoding",
                "J_Order_binding",
            ],
            "first_outer_axis_CG_closure": True,
            "load_bearing_finding_1": (
                "Theta-gamma nesting contributes measurable capacity beyond "
                "flat FHRR phase: NESTED cliff_K=100 vs FLAT_32 cliff_K=50 "
                "(2x cliff lift; log2_delta=1.000)."
            ),
            "load_bearing_finding_2": (
                "CYCLIC_SHIFT achieves highest cliff_K=200; demonstrates "
                "positional binding via shift-permutation outperforms phase-"
                "based binding at the K_SEQ scales tested."
            ),
            "ruling_note": (
                "12th CHAIN-GRADE promotion of session 2026-06-30 (CERT 635 -> 636)."
            ),
        },
    )


def atom_meta_rule_az() -> Atom:
    return Atom(
        id=("RULE_director_spawn_prompts_file_sizes_and_slugs_off_disk_"
            "verification_META_RULE_AZ_2026-06-30"),
        name=(
            "META_RULE_AZ: Director spawn prompts citing file sizes / slugs / "
            "arm counts MUST verify off-disk before publishing"
        ),
        description=(
            "RULE (load-bearing):\n"
            "  Director spawn prompts that cite landed-cell artifact "
            "properties (file sizes in KB, anchor slugs, per-seed arm counts, "
            "verdict-msg snippets) MUST verify those properties off-disk "
            "before being published in a spawn prompt. The Skunkworks "
            "auditor receiving the prompt is NOT obligated to use cited "
            "values as ground truth and SHALL discover slugs/sizes off-disk "
            "before any atomization.\n"
            "WITNESS (caught 2026-06-30 ~19:50 UTC by Skunkworks):\n"
            "  - Director spawn prompt cited 'ANCHOR 4 v4 ~11KB metrics.json' "
            "and 'theta-gamma v2 ~230KB metrics.json'. OFF-DISK reality "
            "(remote SCP side-pull verified): ANCHOR 4 v4 is actually 230KB; "
            "theta-gamma v2 is actually ~11.6KB. Director SWAPPED the sizes.\n"
            "  - Director spawn prompt cited slug "
            "'exp_substrate_anchor4_encoder_family_phase_diagram_v4_seed_*'. "
            "OFF-DISK reality: actual remote slug is "
            "'exp_substrate_anchor4_encoder_family_v4_seed_*' (no "
            "'_phase_diagram_' token). Skunkworks had to discover slug "
            "manually via 'powershell ls | match' to find the cells.\n"
            "REMEDY (Director-side):\n"
            "  Before citing file sizes / slugs / arm counts in a spawn prompt, "
            "run a 1-line verification:\n"
            "    powershell -NoProfile -Command \"Get-ChildItem <data_root>/ "
            "-Directory | Where-Object {$_.Name -match '<pattern>'} | "
            "ForEach-Object {$mf = Join-Path $_.FullName 'metrics.json'; "
            "if (Test-Path $mf) {$fi = Get-Item $mf; Write-Output ('{0} "
            "size={1} mtime={2}' -f $_.Name, $fi.Length, "
            "$fi.LastWriteTimeUtc.ToString('s'))}}\"\n"
            "  Or programmatic: use os.path.getsize() + glob for slug "
            "discovery; cite the discovered values not assumed values.\n"
            "REMEDY (Skunkworks-side):\n"
            "  Default to off-disk discovery on every landed-VET. If slug or "
            "size in Director's prompt mismatches reality, flag the "
            "discrepancy in the VET report (do not silently use the "
            "Director-cited values). This catches both Director typos AND "
            "stale-spawn-prompt drift (cell renamed between dispatch and "
            "VET).\n"
            "COMPOSES WITH:\n"
            "  - META_RULE_I (verify-the-referent: discipline that demands "
            "verification at point of consumption, not point of authorship).\n"
            "  - feedback_director_framing_discipline_timezone_and_arm_"
            "counts_2026-06-30 (Director framing-discipline thread; this is "
            "a structural reinforcement).\n"
            "  - META_RULE_BA (remote runner double exp_ prefix bug; "
            "co-located cell discoverability issue that AZ catches when "
            "Director cites the 'expected' slug).\n"
            "LOAD-BEARING WHY:\n"
            "  Cited slugs/sizes serve as the auditor's address-of-truth + "
            "sanity-check at A5 PRE. If they're wrong, the auditor either "
            "(a) can't locate the artifacts (failure-CLOSED) or (b) silently "
            "uses Director-cited values and propagates framing errors "
            "downstream (failure-OPEN; the dangerous mode). The rule "
            "preempts (b)."
        ),
        kind=AtomKind.METHODOLOGY_RULE,
        tier=Tier.TIER_METHODOLOGY,
        corpus=Corpus.META,
        algebra=None,
        metadata={
            "provenance_quality": None,
            "cert_status": "discipline_meta",
            "cert_class": "discipline_meta",
            "cert_increment_delta": 0,
            "atomized_by": "skunkworks_landed_VET_2026-06-30",
            "meta_rule_id": "META_RULE_AZ",
            "rule_class": "director_spawn_prompt_off_disk_verification",
            "witnesses_count": 1,
            "first_witness_ts": "2026-06-30T19:50Z",
            "first_witness_anchor": (
                "anchor4_v4_slug_size_swap_director_spawn_prompt_2026-06-30"
            ),
            "composes_with": [
                "META_RULE_I_verify_the_referent",
                "META_RULE_BA_remote_runner_double_exp_prefix_slug_bug",
            ],
            "memory_references": [
                "feedback_director_framing_discipline_timezone_and_arm_counts_2026-06-30",
            ],
            "operational_rule": (
                "Director: verify off-disk before citing slugs/sizes in spawn "
                "prompts. Skunkworks: default to off-disk discovery; flag "
                "Director-cited values that mismatch reality."
            ),
            "confirmed_or_candidate": "CONFIRMED",
        },
    )


def atom_meta_rule_ba() -> Atom:
    return Atom(
        id=("RULE_remote_runner_double_exp_prefix_slug_bug_theta_gamma_v2_"
            "META_RULE_BA_2026-06-30"),
        name=(
            "META_RULE_BA: Remote runner produced double 'exp_' prefix slug "
            "for theta-gamma v2; audit slug-construction at queue_add + "
            "harness HDLAB_EXP_NAME"
        ),
        description=(
            "BUG FINDING (load-bearing infra-discipline):\n"
            "  Remote runner produced double 'exp_' prefix slug "
            "'exp_exp_substrate_theta_gamma_v2_FHRR_all_complex_seed_{7,13,19}' "
            "for theta-gamma v2 cells dispatched 2026-06-30 (commit "
            "3faa827e). Local exp_dev convention is single 'exp_' prefix; "
            "the runner OR queue_add slug-normalization introduced the second "
            "'exp_'.\n"
            "WITNESS (caught 2026-06-30 ~19:50 UTC by Skunkworks):\n"
            "  - Skunkworks SCP-discovered remote directory listing during "
            "landed-VET; expected slug "
            "'exp_substrate_theta_gamma_v2_FHRR_all_complex_seed_*' was "
            "absent. Actual remote slug 'exp_exp_substrate_theta_gamma_v2_"
            "FHRR_all_complex_seed_*' present with FULL-sized metrics.json "
            "(11.6KB each, mtime 19:25Z, verdict=HARD_PASS).\n"
            "  - Other cells dispatched same batch (ANCHOR 4 v4) did NOT "
            "exhibit double-prefix: 'exp_substrate_anchor4_encoder_family_v4_"
            "seed_*' was clean. So the bug is cell-specific (likely the "
            "harness HDLAB_EXP_NAME env-var passed by the cell already "
            "contained 'exp_' and queue_add prepended a second one) OR "
            "anchor-name-specific in queue_add slug construction.\n"
            "ROOT-CAUSE HYPOTHESES:\n"
            "  H1: Cell harness 'HDLAB_EXP_NAME' env-var construction "
            "(experiments/substrate_theta_gamma_v2_FHRR_all_complex.py or "
            "shared harness) prepends 'exp_' explicitly AND queue_add.sh "
            "also prepends 'exp_' without dedup; result is 'exp_exp_'. "
            "Audit point: queue_add.sh ~line 150 slug construction; cell "
            "harness HDLAB_EXP_NAME setup.\n"
            "  H2: queue_add.sh handles ANCHOR_NAME without 'exp_' prefix "
            "via 'exp_{ANCHOR_NAME}' template, but the theta-gamma cell "
            "harness passed ANCHOR_NAME already including 'exp_' prefix.\n"
            "REMEDY:\n"
            "  Audit tools/queue_add.sh slug construction (sub_dir handling "
            "at ~line 150) for idempotent prefix handling. Cell harnesses "
            "should pass ANCHOR_NAME WITHOUT 'exp_' prefix; queue_add adds "
            "it. Add 'exp_exp_' regression test to queue_add CI smoke.\n"
            "OPERATIONAL IMPACT:\n"
            "  - Affects discoverability: Director / Skunkworks searches for "
            "'exp_substrate_<anchor>' miss the cell.\n"
            "  - Affects sync currency: hd_metrics_sync may sync to wrong "
            "local path if it normalizes the prefix differently than the "
            "remote.\n"
            "  - Affects atom ID + metrics_path references: this atomization "
            "ROW uses the corrected slug (no double prefix) per anchor-of-"
            "record convention, but the runtime artifact remains at the "
            "double-prefix path until the bug fix lands.\n"
            "COMPOSES WITH:\n"
            "  - META_RULE_AZ (Director spawn-prompt off-disk verification; "
            "the BA bug is exactly the kind of slug-drift that AZ catches at "
            "the auditor end).\n"
            "  - Reference: tools/queue_add.sh slug-construction discipline "
            "(if/when audited)."
        ),
        kind=AtomKind.METHODOLOGY_RULE,
        tier=Tier.TIER_METHODOLOGY,
        corpus=Corpus.META,
        algebra=None,
        metadata={
            "provenance_quality": None,
            "cert_status": "discipline_meta",
            "cert_class": "discipline_meta",
            "cert_increment_delta": 0,
            "atomized_by": "skunkworks_landed_VET_2026-06-30",
            "meta_rule_id": "META_RULE_BA",
            "rule_class": "remote_runner_slug_construction_bug",
            "witnesses_count": 1,
            "first_witness_ts": "2026-06-30T19:50Z",
            "first_witness_anchor": (
                "theta_gamma_v2_FHRR_all_complex_exp_exp_prefix_remote_2026-06-30"
            ),
            "follow_up_audit": [
                "tools/queue_add.sh slug construction ~line 150",
                "cell harness HDLAB_EXP_NAME env-var handling "
                "(experiments/substrate_theta_gamma_v2_FHRR_all_complex.py)",
                "Add regression test for 'exp_exp_' double-prefix to queue_add CI",
            ],
            "operational_impact": [
                "discoverability_search_miss",
                "sync_currency_path_normalization",
                "atom_id_vs_runtime_artifact_path_divergence",
            ],
            "composes_with": [
                "META_RULE_AZ_director_spawn_prompts_off_disk_verification",
            ],
            "confirmed_or_candidate": "CONFIRMED",
        },
    )


def add_atom_safely(atom: Atom, source: str, note: str,
                    ledger_row: dict | None = None,
                    expected_cert_n_pre: int | None = None,
                    expected_cert_n_post: int | None = None) -> bool:
    """A5-gated atom add: PRE snapshot + add_atom + POST verify + (optional) ledger row.

    Mirrors add_audit_lesson_safely from atomize_audit_lesson_template_SAFE.py
    but extended for any AtomKind. Returns True on full success.
    """
    ps = PartitionedStore(STORE_ROOT)
    qid = f"{atom.corpus.value}::{atom.id}"

    # PRE
    pre_cert = _cert_count(ps)
    pre_ax = _axiom_count(ps)
    pre_cap = _cap_pres_ok()
    print(f"  A5-PRE: CERT={pre_cert} AXIOM={pre_ax} CAP_PRES={pre_cap}")
    assert pre_ax == 206, f"A5-PRE axiom drift: {pre_ax} != 206"
    assert pre_cap, "A5-PRE cap_pres FAIL"
    if expected_cert_n_pre is not None:
        assert pre_cert == expected_cert_n_pre, (
            f"A5-PRE CERT mismatch: live={pre_cert} expected={expected_cert_n_pre}"
        )

    # Idempotency
    if ps.get_atom(qid) is not None:
        print(f"  SKIP (idempotent): {atom.id} already present.")
        return True

    print(f"  ADDING: {atom.id[:80]}")
    print(f"    kind={atom.kind.value} tier={atom.tier.value} "
          f"corpus={atom.corpus.value} pq={(atom.metadata or {}).get('provenance_quality')}")
    ps.add_atom(atom, source=source, note=note)

    # Round-trip verify via fresh Store
    ps2 = PartitionedStore(STORE_ROOT)
    atoms = list(ps2.all_atoms())
    found = next((a for a in atoms if a.id == atom.id), None)
    if found is None:
        print(f"  FAIL: atom not found post-add")
        return False
    if found.tier != atom.tier:
        print(f"  FAIL: tier mismatch (expected {atom.tier}, got {found.tier})")
        return False
    if found.kind != atom.kind:
        print(f"  FAIL: kind mismatch (expected {atom.kind}, got {found.kind})")
        return False
    md = found.metadata or {}
    expected_pq = (atom.metadata or {}).get("provenance_quality")
    if md.get("provenance_quality") != expected_pq:
        print(f"  FAIL: pq mismatch (expected {expected_pq}, got {md.get('provenance_quality')})")
        return False
    print(f"  PASS: round-trip survival OK")

    # POST snapshot
    post_cert = _cert_count(ps2)
    post_ax = _axiom_count(ps2)
    post_cap = _cap_pres_ok()
    print(f"  A5-POST: CERT={post_cert} AXIOM={post_ax} CAP_PRES={post_cap}")
    assert post_ax == 206, f"A5-POST axiom drift: {post_ax} != 206"
    assert post_cap, "A5-POST cap_pres FAIL"
    if expected_cert_n_post is not None:
        assert post_cert == expected_cert_n_post, (
            f"A5-POST CERT mismatch: live={post_cert} expected={expected_cert_n_post} "
            f"(pre={pre_cert}, delta_observed={post_cert - pre_cert})"
        )

    # Cert-ledger append (Phase C)
    if ledger_row is not None:
        try:
            rh = append_cert_ledger_row(
                ledger_row,
                expected_cert_n_pre=None,  # already verified above
                expected_cert_n_post=None,  # already verified above
            )
            print(f"  PHASE-C: ledger row appended; row_hash={rh}")
        except Exception as e:
            print(f"  FAIL: cert-ledger append errored: {e}")
            return False

    return True


def main():
    apply = "--apply" in sys.argv
    print("=" * 80)
    print(f"Skunkworks atomize batch 2026-06-30: 2 CG + 2 META")
    print(f"Mode: {'APPLY (LIVE Store mutation)' if apply else 'DRY RUN (no mutations)'}")
    print("=" * 80)

    a1 = atom_anchor4_v4_chain_grade()
    a2 = atom_theta_gamma_v2_chain_grade()
    a3 = atom_meta_rule_az()
    a4 = atom_meta_rule_ba()

    print("\nAtoms to write (in order):")
    for i, a in enumerate([a1, a2, a3, a4], 1):
        delta = (a.metadata or {}).get('cert_increment_delta', 0)
        print(f"  {i}. {a.corpus.value}::{a.id[:80]} kind={a.kind.value} delta=+{delta}")

    if not apply:
        print("\nDRY RUN -- no mutations. Re-run with --apply to commit.")
        return 0

    # A5-pre overall snapshot
    ps = PartitionedStore(STORE_ROOT)
    pre_cert = _cert_count(ps)
    print(f"\nA5-PRE overall: CERT={pre_cert} (expected 634)")
    assert pre_cert == 634, f"PRE CERT mismatch: {pre_cert} != 634"

    # Atom 1: anchor4 v4 chain-grade (+1)
    print("\n--- Atom 1: ANCHOR 4 v4 CHAIN-GRADE ---")
    qid_a1 = f"math::{a1.id}"
    ledger_a1 = build_chain_grade_ruling_row(
        atom_id=qid_a1,
        cell_commit="a17e13be",
        verdict="HARD_PASS",
        notes_path=None,  # skunkworks landed-VET reply lives in conversation (Agent Teams HYBRID)
        metrics_path="data/exp_substrate_anchor4_encoder_family_v4_seed_7/metrics.fresh_2026-06-30.json",
        cv=0.069,  # n_pairs_metric_distinct cv (highest top-level metric cv)
        cert_class="pre_reg_pass",
        atomized_by="skunkworks_landed_VET_2026-06-30",
        note=(
            "11th CG promotion of 2026-06-30; 5/5 encoders chain-grade; v3 "
            "bit-identical trap CLOSED via bundled_memory mechanism"
        ),
    )
    ok = add_atom_safely(
        a1,
        source="skunkworks_landed_VET_anchor4_v4_3seed_2026-06-30",
        note="Chain-grade promotion; off-disk recompute Skunkworks 2026-06-30; Director ACK explicit.",
        ledger_row=ledger_a1,
        expected_cert_n_pre=634,
        expected_cert_n_post=635,
    )
    if not ok:
        print("ABORT: atom 1 failed")
        return 1

    # Atom 2: theta-gamma v2 chain-grade (+1)
    print("\n--- Atom 2: Theta-gamma v2 CHAIN-GRADE ---")
    qid_a2 = f"math::{a2.id}"
    ledger_a2 = build_chain_grade_ruling_row(
        atom_id=qid_a2,
        cell_commit="3faa827e",
        verdict="HARD_PASS",
        notes_path=None,
        metrics_path="data/exp_substrate_theta_gamma_v2_FHRR_all_complex_seed_7/metrics.fresh_2026-06-30.json",
        cv=0.000,  # cliff_log2_K cv (primary discriminator)
        cert_class="pre_reg_pass",
        atomized_by="skunkworks_landed_VET_2026-06-30",
        note=(
            "12th CG promotion of 2026-06-30; first outer-axis CG on axes "
            "I (Sequence encoding) + J (Order binding); cliff_log2_K cv=0.000"
        ),
    )
    ok = add_atom_safely(
        a2,
        source="skunkworks_landed_VET_theta_gamma_v2_3seed_2026-06-30",
        note="Chain-grade promotion; off-disk recompute Skunkworks 2026-06-30; Director ACK explicit.",
        ledger_row=ledger_a2,
        expected_cert_n_pre=635,
        expected_cert_n_post=636,
    )
    if not ok:
        print("ABORT: atom 2 failed")
        return 1

    # Atom 3: META_RULE_AZ (delta=0; no cert-ledger row since not a cert event)
    print("\n--- Atom 3: META_RULE_AZ (Director off-disk verification discipline) ---")
    ok = add_atom_safely(
        a3,
        source="skunkworks_atomize_META_RULE_AZ_director_off_disk_verify_2026-06-30",
        note="META rule; CERT-neutral; caught 2026-06-30 ~19:50 UTC by Skunkworks landed-VET.",
        ledger_row=None,  # no cert-ledger row for META rules (delta=0; discipline_meta)
        expected_cert_n_pre=636,
        expected_cert_n_post=636,
    )
    if not ok:
        print("ABORT: atom 3 failed")
        return 1

    # Atom 4: META_RULE_BA (delta=0)
    print("\n--- Atom 4: META_RULE_BA (remote runner double-exp_ prefix bug) ---")
    ok = add_atom_safely(
        a4,
        source="skunkworks_atomize_META_RULE_BA_remote_runner_double_exp_prefix_2026-06-30",
        note="META bug finding; CERT-neutral; follow-up audit on tools/queue_add.sh.",
        ledger_row=None,
        expected_cert_n_pre=636,
        expected_cert_n_post=636,
    )
    if not ok:
        print("ABORT: atom 4 failed")
        return 1

    # Final overall A5 verify
    ps_final = PartitionedStore(STORE_ROOT)
    final_cert = _cert_count(ps_final)
    final_ax = _axiom_count(ps_final)
    final_cap = _cap_pres_ok()
    print("\n" + "=" * 80)
    print(f"FINAL A5: CERT={final_cert} (expected 636) AXIOM={final_ax} CAP_PRES={final_cap}")
    print("=" * 80)
    assert final_cert == 636, f"FINAL CERT mismatch: {final_cert} != 636"
    assert final_ax == 206
    assert final_cap

    print("\nSUCCESS: 4 atoms written; CERT 634 -> 636 (+2); META rules AZ + BA atomized.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
