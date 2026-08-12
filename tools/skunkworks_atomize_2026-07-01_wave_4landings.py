"""A5-gated atomization of 5 landings from 2026-07-01 (compaction-window batch).

Landings (all verified off-disk by Skunkworks in independent recompute):
  1. cortex_hippo_dense_layer_M_sweep_v3 (3 seeds) -> CG (v2 M8192 CG + criterion c satisfied)
  2. population_coding_3seed_CG_lift_v1        -> CG (MM->CG lift; N>=10 is proven bound)
  3. cortex_hippo_dense_beta_sweep_v1 seed 7   -> MM (smoke saturates; confirms design-level MM)
  4. sparsity_free_axis_v1 (3 seeds)           -> HF_TEST_DESIGN_FAILURE (regime miscalibrated)
  5. substrate_task_vector_HRR_ICL_K_500_extended_v1 (3 seeds) -> CG (K-cliff at K=1000 localized, SSH-pull)

Plus AMENDMENT to M3 architecture meta atom (MM_STANDARD -> chain-grade; criterion c satisfied).

Discipline invariants (per hdi_skunkworks.md):
  - Atomic tmp-write + os.replace on atoms.jsonl AND cert_ledger.jsonl
  - Matching timestamps between atom + ledger entries
  - verified_off_data=True on ledger entries
  - Load-verify after write (JSON valid + line count increment matches)
"""
import json
import os
import time
import pathlib

REPO = pathlib.Path("d:/AI/hd-instrument")
MATH_ATOMS = REPO / "data/substrate_index/math/atoms.jsonl"
META_ATOMS = REPO / "data/substrate_index/meta/atoms.jsonl"
CERT_LEDGER = REPO / "data/substrate_index/meta/cert_ledger.jsonl"

TS_NOW = time.time()
DATE = "2026-07-01"
COMMIT = "5f141d78"

# ---------- Atom 1: v3 M-sweep chain-grade ----------
ATOM_1_ID = (
    "T3/EXP_substrate_cortex_hippo_dense_layer_M_sweep_v3_3seed_"
    "CHAIN_GRADE_REPLACE_recall_1p000_all_9_outcomes_3M_x_3seed_cv_0p000_"
    "STD_positive_control_collapses_0p766_M4096_to_0p271_M8192_to_0p052_M16384_"
    "Amit_Gutfreund_wall_confirmed_HA_ONLY_clean_floor_0p0001_all_M_"
    "ratio_1p28_to_20p1_gap_0p9995_to_1p000_adaptive_beta_12p58_13p63_14p68_"
    "convergent_all_seeds_cross_seed_cv_STD_0p015_to_0p027_arms_differ_9_of_9_"
    "cardinality_9_of_9_units_expected_M3_criterion_c_SATISFIED_promotes_M3_meta_"
    "to_chain_grade_7th_CG_of_2026_07_01_2026-07-01"
)
ATOM_1 = {
    "id": ATOM_1_ID,
    "name": (
        "CG Cell D cortex_hippo_dense_layer_M_sweep_v3 3-seed: REPLACE recall=1.000 "
        "at ALL 9 outcomes (M in {4096, 8192, 16384} x seeds {7,13,19}); "
        "cross-seed cv on REPL = 0.000 perfect; STANDARD positive control collapses "
        "0.766 -> 0.271 -> 0.052 as M scales (Amit-Gutfreund 0.138N wall confirmed; "
        "metric IS discriminating; META_RULE_Q genuine ceiling not saturation-of-metric); "
        "HA_ONLY fairness floor 0.0001-0.0002 at all M; discriminator ratio 1.28x/3.71x/20.1x "
        "at M=4096/8192/16384; gap 0.9995-1.000; adaptive beta 12.58/13.64/14.68 convergent across seeds; "
        "arms distinct 9/9; cardinality 9/9 expected; CRLB floors 0.0078/0.0055/0.0039 far below gap "
        "(HP gap 0.60 = 77-154 sigma); ELAPSED 4.05-4.18s per seed on RTX 4060 Ti. "
        "SATISFIES M3 architecture MM_STANDARD expansion criterion (c) multi-M validation; "
        "promotes companion M3 meta atom from MM_STANDARD -> chain-grade (amendment). CERT +1."
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record",
    "description": (
        f"3-seed cross-M sweep {{M=4096, 8192, 16384}} x {{seeds=7,13,19}}; "
        f"9 REPL outcomes all at 1.000; STANDARD collapses monotonically with M; "
        f"HA_ONLY clean floor; adaptive beta = log2(M)/margin formula convergent.\n\n"
        f"OFF-DATA verified: metrics.json at data/exp_substrate_cortex_hippo_dense_layer_M_sweep_v3_seed_{{7,13,19}}/.\n"
        f"Recompute Skunkworks {DATE}: per-M cross-seed CV independently derived by\n"
        f"  math.sqrt(sum((x-mean)**2 for x in vals)/3)/mean over per_seed['per_M'][M].\n"
        f"  REPL cv = 0.000000 at all 3 M values.\n"
        f"  STD cv = 0.018/0.015/0.027 at M=4096/8192/16384.\n"
        f"  Ratio(REPL/STD) 1.275-1.332 / 3.62-3.75 / 18.94-20.13; gap 0.9995-1.000.\n"
        f"  Arms distinct at all 9 outcomes (STD, HA_ONLY, REPL non-identical per seed per M).\n"
        f"\nRELATIONSHIP TO PARENT: v2 M=8192 CG (commit fc47b1bb) established REPL=1.000\n"
        f"  cv=0.000 at single M value; v3 extends to 4x M range (4096-16384) at same setup;\n"
        f"  SATISFIES Skunkworks M3 MM_TENTATIVE criterion (c) 'pattern verified at other M values';\n"
        f"  triggers COMPANION AMENDMENT of M3 meta atom to chain-grade (see meta corpus).\n"
        f"\nMETA_RULE_Q genuine-ceiling analysis: STANDARD positive control varies 0.05-0.77\n"
        f"  across M (proves metric discriminates); REPL=1.000 is genuine mechanism dominance,\n"
        f"  not metric saturation. STD collapse to 0.052 at M=16384 confirms the Amit-Gutfreund\n"
        f"  0.138N capacity wall is being crossed; REPL bypasses it via dense-Hopfield attention.\n"
        f"\nCross-arc overlap check {DATE}: substrate_query 'cortex hippo dense M sweep adaptive beta'\n"
        f"  top-1 cosine=0.29 (LM-substrate attention replacement roadmap; NOT this mechanism);\n"
        f"  no prior cell tested cortex-hippo dense-Hopfield tape-read at cross-M scale.\n"
        f"  GENUINELY NOVEL cross-M validation.\n"
        f"\nProven bound (honest downward correction NONE required; CG claim holds):\n"
        f"  REPL=1.000 at all tested M {{4096, 8192, 16384}}; ceiling behavior may extend beyond\n"
        f"  tested range but claim scoped to tested M range only. Revival criterion for capacity-\n"
        f"  wall search: M>=32768 or correlated keys (subspace-drawn, k<<N_c).\n"
        f"\nCompose with: Cell D v2 M8192 CG (fc47b1bb) + M3 architecture meta (amended to CG).\n"
        f"Commit: {COMMIT}. Author: skunkworks_landed_VET_wave_2026-07-01_post_compaction."
    ),
    "metadata": {
        "ts_atomized": TS_NOW,
        "date_atomized": DATE,
        "cert_commit": COMMIT,
        "cell_commit_ref": "parent_v2_landing_fc47b1bb",
        "run_mode": "full",
        "n_seeds": 3,
        "seeds": [7, 13, 19],
        "M_values": [4096, 8192, 16384],
        "arms": ["ARM_STANDARD", "ARM_HA_ONLY", "ARM_HA_DENSE_REPLACE"],
        "n_arm_outcomes_expected": 9,
        "n_arm_outcomes_observed": 9,
        "cardinality_ok": True,
        "arms_differ_verified": True,
        "cross_seed_cv_replace_per_M": {"4096": 0.0, "8192": 0.0, "16384": 0.0},
        "cross_seed_cv_standard_per_M": {"4096": 0.0182, "8192": 0.0147, "16384": 0.0274},
        "mean_replace_per_M": {"4096": 1.0, "8192": 1.0, "16384": 1.0},
        "mean_standard_per_M": {"4096": 0.7664, "8192": 0.2707, "16384": 0.0517},
        "mean_ha_only_per_M": {"4096": 0.000163, "8192": 0.000203, "16384": 0.000102},
        "adaptive_beta_per_M": {"4096": [12.58, 12.59, 12.59], "8192": [13.64, 13.64, 13.63], "16384": [14.68, 14.68, 14.68]},
        "verified_off_data": True,
        "metrics_paths": [
            "data/exp_substrate_cortex_hippo_dense_layer_M_sweep_v3_seed_7/metrics.json",
            "data/exp_substrate_cortex_hippo_dense_layer_M_sweep_v3_seed_13/metrics.json",
            "data/exp_substrate_cortex_hippo_dense_layer_M_sweep_v3_seed_19/metrics.json",
        ],
        "prereg_path": "preregs/2026-07-01_substrate_cortex_hippo_dense_layer_M_sweep_v3.md",
        "parent_atoms": [
            "T3/EXP_substrate_cortex_hippo_dense_layer_M8192_v2_3seed_CHAIN_GRADE_ARM_HA_DENSE_REPLACE_recall_1p000",
            "T3/META_synthesis_M3_cortex_layer_architecture_INSIGHT_dense_Hopfield_should_REPLACE_not_COMPOSE_with_cortex_Hebbian",
        ],
        "cert_tier": "chain_grade",
        "cert_increment_delta": 1,
    },
}
LEDGER_1 = {
    "ts": TS_NOW,
    "op": "cert_ruling_promotion_chain_grade",
    "atom_id": f"math::{ATOM_1_ID}",
    "cert_status": "chain_grade",
    "cert_class": "pre_reg_pass_replacement_mode_dense_Hopfield_cross_M_sweep",
    "verified_off_data": True,
    "atomized_by": "skunkworks_landed_VET_wave_2026-07-01_post_compaction",
    "cell_commit": COMMIT,
    "verdict": (
        "CHAIN_GRADE_3seed_HP_all_9_outcomes_REPL_recall_1p000_cv_0p000_"
        "STD_positive_control_collapses_0p77_M4096_to_0p05_M16384_Amit_Gutfreund_wall_"
        "HA_ONLY_clean_floor_ratio_1p28_to_20p1_gap_0p9995_to_1p000_adaptive_beta_convergent_"
        "META_RULE_Q_genuine_ceiling_STD_discriminates_arms_differ_9_of_9_"
        "M3_criterion_c_SATISFIED_promotes_M3_meta_to_chain_grade_7th_CG_of_2026_07_01"
    ),
    "cert_increment_delta": 1,
    "cv": 0.0,
    "referent_pointer": {
        "notes_path": None,
        "metrics_path": "data/exp_substrate_cortex_hippo_dense_layer_M_sweep_v3_seed_{7,13,19}/metrics.json",
        "prereg_path": "preregs/2026-07-01_substrate_cortex_hippo_dense_layer_M_sweep_v3.md",
        "parent_v2_CG_atom_commit": "fc47b1bb",
        "companion_M3_meta_promotion_amendment": True,
        "atom_qualified_id": f"math::{ATOM_1_ID}",
    },
    "supersedes": None,
    "note": (
        "cortex_hippo_dense_layer_M_sweep_v3_3seed_CHAIN_GRADE_7th_CG_of_2026_07_01_"
        "REPL_recall_1p000_all_9_outcomes_M_4096_8192_16384_x_seeds_7_13_19_cross_seed_cv_0p000_"
        "STD_positive_control_collapses_monotonically_with_M_confirms_Amit_Gutfreund_wall_and_metric_discriminates_"
        "HA_ONLY_clean_floor_all_M_ratio_gap_far_above_HP_thresholds_adaptive_beta_convergent_across_seeds_"
        "SATISFIES_M3_meta_MM_STANDARD_criterion_c_multi_M_validation_"
        "triggers_companion_M3_meta_amendment_MM_STANDARD_to_chain_grade_same_commit"
    ),
}

# ---------- Atom 2: population coding 3-seed lift ----------
ATOM_2_ID = (
    "T3/EXP_population_coding_3seed_CG_lift_v1_CHAIN_GRADE_"
    "N100_ensemble_gain_25_to_30_8pp_cv_0p085_all_3_seeds_"
    "lifts_lap3_7_n100_ensemble_MM_to_CG_"
    "PROVEN_BOUND_ens10_saturates_at_1p000_ens100_adds_ZERO_marginal_"
    "N_gte_10_sufficient_N_100_over_provisioning_"
    "8th_CG_of_2026_07_01_2026-07-01"
)
ATOM_2 = {
    "id": ATOM_2_ID,
    "name": (
        "CG population_coding 3-seed lift v1: 3-seed replication of N=100 population-coding "
        "ensemble at TR=120 P=100 M=90 VV=100 NOISE=2.6 lifts lap3_7_n100_ensemble_cpu_v1 "
        "from MM to CG. Cross-seed gains {7:25.0pp, 13:28.3pp, 19:30.8pp} min=25 >=20 HP threshold; "
        "cv=0.0847 <0.10 HP threshold. Singles 0.75/0.72/0.69 -> ens100 1.000 all seeds. "
        "PROVEN BOUND: ens10 = 1.000 for ALL 3 seeds (ceiling reached at N=10; N=100 adds ZERO "
        "marginal accuracy); N>=10 is sufficient ensemble size; N=100 is over-provisioning. "
        "This matches prior substrate-KB PP-274 finding ('ceiling achieved at N=10; N=100 confirms "
        "saturation -- gain saturates not continues'). Cert scope: N>=10 population coding cross-seed "
        "stable at 25-31pp lift over single-substrate under noisy-recall; MM-scoped over-provisioning "
        "atom (N=100 preserved as parent) not superseded. CERT +1."
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record",
    "description": (
        f"OFF-DATA verified: data/exp_population_coding_3seed_CG_lift_v1/metrics.json.\n\n"
        f"Recompute Skunkworks {DATE}: gains = [25.0, 28.3, 30.8]; mean=28.03; sd=2.375;\n"
        f"  cv = sd/mean = 2.375/28.03 = 0.0847 < 0.10 HP threshold.\n"
        f"  min(gains) = 25.0 >= 20 HP threshold.\n"
        f"  Cardinality: 3 seeds observed vs 3 expected; cardinality_ok.\n"
        f"  singles = [0.75, 0.7167, 0.6917]; ens10 = [1.0, 1.0, 1.0]; ens100 = [1.0, 1.0, 1.0].\n"
        f"\nPROVEN BOUND (honest downward correction on framing):\n"
        f"  Pre-reg + verdict_msg framing ='N=100 ensemble lifts MM->CG'.\n"
        f"  Data shows ens100 - ens10 = 0.0 across ALL 3 seeds.\n"
        f"  The CG-worthy claim is: N>=10 population coding at THIS regime (M=90, VV=100, NOISE=2.6)\n"
        f"    cross-seed stably lifts single-substrate 25-31pp; ens10 already saturates the ceiling.\n"
        f"  Parent lap3_7_n100_ensemble atom at N=100 preserved; NOT superseded (still valid MM claim\n"
        f"    at N=100 setpoint; but N=100 is over-provisioning for this task-difficulty regime).\n"
        f"  Revival criterion for N-dependence of ceiling: harder regime (M>>90 or NOISE>2.6) that\n"
        f"    drives ens10 below 1.000 to test whether N=100 recovers accuracy.\n"
        f"\nCross-arc overlap check {DATE}: substrate_query 'population coding N=100 ensemble sqrt-N lift'\n"
        f"  top-1 cosine=0.47 (PP-274 finding IS parent; this cell IS the 3-seed lift extension).\n"
        f"  Prior atom noted 'ceiling achieved at N=10; N=100 confirms saturation'.\n"
        f"  This landing REPRODUCES that saturation with cross-seed evidence + lifts to CG.\n"
        f"  NOT a rediscovery; extends parent single-seed MM to 3-seed CG with explicit proven bound.\n"
        f"\nCompose with: lap3_7_n100_ensemble_cpu_v1 MM (parent, PP-274, single seed 249).\n"
        f"Commit: {COMMIT}. Author: skunkworks_landed_VET_wave_2026-07-01_post_compaction."
    ),
    "metadata": {
        "ts_atomized": TS_NOW,
        "date_atomized": DATE,
        "cert_commit": COMMIT,
        "run_mode": "full",
        "n_seeds": 3,
        "seeds": [7, 13, 19],
        "cardinality_ok": True,
        "gains_per_seed_pp": [25.0, 28.3, 30.8],
        "gains_mean_pp": 28.0333,
        "gains_std_pp": 2.3753,
        "gains_cv": 0.0847,
        "singles_per_seed": [0.75, 0.7167, 0.6917],
        "ens10_per_seed": [1.0, 1.0, 1.0],
        "ens100_per_seed": [1.0, 1.0, 1.0],
        "ens100_minus_ens10_per_seed": [0.0, 0.0, 0.0],
        "proven_bound_N_sufficient": 10,
        "proven_bound_N100_marginal_gain_pp": 0.0,
        "verified_off_data": True,
        "metrics_path": "data/exp_population_coding_3seed_CG_lift_v1/metrics.json",
        "prereg_path": "preregs/population_coding_3seed_CG_lift_v1.md",
        "parent_atoms": [
            "lap3_7_n100_ensemble_cpu_v1_HP_MM_PP_274_single_seed_249",
            "lap9_population_substrate_cpu_v1_HP_MM_PP_249_single_seed_909_N_10",
        ],
        "cert_tier": "chain_grade",
        "cert_increment_delta": 1,
    },
}
LEDGER_2 = {
    "ts": TS_NOW,
    "op": "cert_ruling_promotion_chain_grade_mm_to_cg_with_proven_bound",
    "atom_id": f"math::{ATOM_2_ID}",
    "cert_status": "chain_grade",
    "cert_class": "mm_to_cg_lift_with_proven_bound_N_sufficient_10",
    "verified_off_data": True,
    "atomized_by": "skunkworks_landed_VET_wave_2026-07-01_post_compaction",
    "cell_commit": COMMIT,
    "verdict": (
        "CHAIN_GRADE_3seed_HP_min_gain_25pp_ge_20_threshold_cv_0p085_lt_0p10_threshold_"
        "mean_28pp_lifts_lap3_7_n100_MM_to_CG_"
        "PROVEN_BOUND_ens10_saturates_at_1p000_all_3_seeds_ens100_adds_zero_marginal_"
        "N_gte_10_sufficient_N_100_over_provisioning_"
        "parent_atom_PP_274_preserved_not_superseded_"
        "revival_criterion_harder_regime_M_gt_90_or_NOISE_gt_2p6_"
        "8th_CG_of_2026_07_01"
    ),
    "cert_increment_delta": 1,
    "cv": 0.0847,
    "referent_pointer": {
        "notes_path": None,
        "metrics_path": "data/exp_population_coding_3seed_CG_lift_v1/metrics.json",
        "prereg_path": "preregs/population_coding_3seed_CG_lift_v1.md",
        "parent_MM_atom_ids": ["lap3_7_n100_ensemble_cpu_v1_PP_274"],
        "atom_qualified_id": f"math::{ATOM_2_ID}",
    },
    "supersedes": None,
    "note": (
        "population_coding_3seed_CG_lift_v1_CHAIN_GRADE_8th_CG_of_2026_07_01_"
        "cross_seed_gains_25_28_30pp_min_25_ge_20_cv_0p085_lt_0p10_mean_28pp_"
        "SATURATES_at_ens10_not_ens100_proven_bound_N_gte_10_sufficient_N_100_over_provisioning_"
        "matches_prior_PP_274_saturation_note_parent_MM_preserved_"
        "hdlab_primitives_use_N_10_as_default_ensemble_size_at_this_regime_"
        "revival_criterion_harder_regime_needs_M_gt_90_or_NOISE_gt_2p6_to_test_N_dependence"
    ),
}

# ---------- Atom 3: beta_sweep_v1 seed 7 smoke MM (confirms design-level MM) ----------
ATOM_3_ID = (
    "T3/EXP_cortex_hippo_dense_beta_sweep_v1_seed_7_SMOKE_MM_"
    "confirms_design_level_MM_prior_atom_all_5_beta_saturate_at_1p000_M_4096_N_c_1024_"
    "META_RULE_Q_regime_saturation_beta_axis_not_discriminating_"
    "preview_arm_M_16384_beta_5_and_20_at_1p000_confirms_saturation_extends_to_full_N_"
    "recall_star_1p000_adaptive_star_ratio_1p000_trivially_met_"
    "seeds_13_19_NOT_dispatched_"
    "single_seed_smoke_MEASURED_MECHANISM_not_CG_"
    "revival_criterion_higher_M_or_correlated_keys_2026-07-01"
)
ATOM_3 = {
    "id": ATOM_3_ID,
    "name": (
        "MM Cell D cortex_hippo_dense_beta_sweep_v1 seed 7 smoke: ALL 5 beta values "
        "{5, 8, 13, 20, 32} yield recall_replace = 1.000 at M=4096 N_c=1024; positive control "
        "STANDARD=0.148 clearly discriminates the metric, but beta axis is SATURATED - no beta "
        "value discriminates within the test regime. META_RULE_Q + META_RULE_L: band-floor result "
        "at ceiling = MIDDLE_BAND / MM, NOT HP despite verdict='HARD_PASS' (verdict logic met "
        "max_beta>=0.80 AND adaptive/star>=0.95 but these are trivially met by universal saturation). "
        "Preview arms at M=16384 full-N with beta=5 AND beta=20 BOTH at 1.000 confirm saturation "
        "extends to full-N regime. Only 1 seed dispatched (7); seeds 13/19 NOT run. "
        "CONFIRMS the prior design-level MM atom (cell-author honest-abort based on off-disk analysis) "
        "with empirical smoke data: adaptive beta formula IS robust across [5, 32] at M in [4096, 16384] "
        "at this test regime, but current regime doesn't DISCRIMINATE beta choices. Revival criterion "
        "unchanged: higher-alpha (M >= 32768 at N_c=4096) OR correlated keys (subspace-drawn, k<<N_c). "
        "CERT +0 (MM tier; parent design-level MM atom amended with empirical confirmation)."
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record",
    "description": (
        f"OFF-DATA verified: data/exp_cortex_hippo_dense_beta_sweep_v1_seed_7/metrics.json.\n\n"
        f"Recompute Skunkworks {DATE}:\n"
        f"  run_mode=smoke; N_h=512, N_c=1024, M_LIST=[4096], seed=7 only\n"
        f"  ARM_STANDARD recall=0.1484 (below the 0.20 fairness ceiling; but STD is not a HP arm here)\n"
        f"  ARM_HA_ONLY recall=0.0000 (clean floor)\n"
        f"  ARM_HA_DENSE_REPLACE_beta5:  recall=1.0\n"
        f"  ARM_HA_DENSE_REPLACE_beta8:  recall=1.0\n"
        f"  ARM_HA_DENSE_REPLACE_beta13: recall=1.0\n"
        f"  ARM_HA_DENSE_REPLACE_beta20: recall=1.0\n"
        f"  ARM_HA_DENSE_REPLACE_beta32: recall=1.0\n"
        f"  beta_star=5.0 (first argmax; tied at 1.0); recall_star=1.0; recall_adaptive=1.0;\n"
        f"  adaptive_over_star_ratio=1.0.\n"
        f"  Preview arm at M=16384 N_h=4096 N_c=4096 beta=20: recall=1.0\n"
        f"  Preview arm low beta at M=16384 beta=5: recall=1.0\n"
        f"\nWHY THIS IS MM NOT HP (auditor override of cell-verdict framing):\n"
        f"  Verdict logic passes because 'max_beta recall>=0.80' AND 'adaptive/star>=0.95' at ALL M.\n"
        f"  BUT: both gates are trivially met by universal saturation at 1.000; neither gate\n"
        f"    DISCRIMINATES the beta choice. META_RULE_L: band-floor / ceiling result = MB/MM.\n"
        f"  This DOES confirm the pre-reg's own risk analysis noted 'META_RULE_AG discriminator\n"
        f"    saturation current regime needs higher-alpha or correlated keys'; the smoke data\n"
        f"    is EVIDENCE OF the anticipated saturation, not evidence of chain-grade robustness.\n"
        f"\nRELATIONSHIP TO PRIOR ATOM: design-level MM atom (same cell family, cell-author\n"
        f"  honest-abort at pre-reg, off-disk analysis of Cell D v2 CG) is CONFIRMED by this\n"
        f"  empirical smoke. Prior atom's sub-finding 3 (META_RULE_AG discriminator saturation)\n"
        f"  is now supported by empirical M=4096 smoke + full-N preview at M=16384.\n"
        f"  Prior atom NOT superseded; complements it with empirical anchor.\n"
        f"\nDISPATCH STATE: only seed 7 landed. Seeds 13 and 19 were NOT dispatched per Director\n"
        f"  spawn context. Even a 3-seed FULL dispatch would confirm saturation (not fix it);\n"
        f"  the test regime itself is non-discriminating for the beta axis.\n"
        f"\nCross-arc overlap check {DATE}: substrate_query 'cortex hippo dense M sweep adaptive beta'\n"
        f"  top-1 cosine=0.29 (LM roadmap; not this mechanism); no rediscovery risk.\n"
        f"  Overlap with prior design-level MM (same cell family) is INTENTIONAL confirmation.\n"
        f"\nCompose with: prior design-level MM atom (cell_D_beta_sweep_v1_DESIGN_LEVEL_MM);\n"
        f"  Cell D v2 M8192 CG (fc47b1bb); v3 M-sweep 3seed CG (this commit's Atom 1).\n"
        f"Commit: {COMMIT}. Author: skunkworks_landed_VET_wave_2026-07-01_post_compaction."
    ),
    "metadata": {
        "ts_atomized": TS_NOW,
        "date_atomized": DATE,
        "cert_commit": COMMIT,
        "run_mode": "smoke",
        "n_seeds_landed": 1,
        "seeds_landed": [7],
        "seeds_NOT_dispatched": [13, 19],
        "cardinality_ok": True,
        "n_arm_outcomes_observed": 7,
        "n_arm_outcomes_expected": 7,
        "recall_replace_by_beta_M4096": {"5.0": 1.0, "8.0": 1.0, "13.0": 1.0, "20.0": 1.0, "32.0": 1.0},
        "recall_standard_M4096": 0.1484,
        "recall_ha_only_M4096": 0.0,
        "preview_arm_M16384_beta20_full_N": 1.0,
        "preview_arm_M16384_beta5_full_N": 1.0,
        "beta_star": 5.0,
        "recall_star": 1.0,
        "adaptive_over_star_ratio": 1.0,
        "verified_off_data": True,
        "auditor_override_reason": "META_RULE_L_band_floor_at_ceiling_MB_not_HP_META_RULE_Q_universal_saturation_beta_axis_not_discriminating",
        "metrics_path": "data/exp_cortex_hippo_dense_beta_sweep_v1_seed_7/metrics.json",
        "prereg_path": "preregs/2026-07-01_cortex_hippo_dense_beta_sweep_v1.md",
        "parent_atoms": [
            "T3/EXP_cortex_hippo_dense_beta_sweep_v1_DESIGN_LEVEL_MM_cell_author_honest_abort_at_prereg",
            "T3/EXP_substrate_cortex_hippo_dense_layer_M8192_v2_3seed_CHAIN_GRADE",
        ],
        "cert_tier": "measured_mechanism",
        "cert_increment_delta": 0,
        "revival_criterion": "higher_alpha_M_ge_32768_at_N_c_4096_OR_correlated_keys_subspace_drawn_k_ll_N_c",
    },
}
LEDGER_3 = {
    "ts": TS_NOW,
    "op": "cert_ruling_measured_mechanism_auditor_override_HP_to_MM",
    "atom_id": f"math::{ATOM_3_ID}",
    "cert_status": "measured_mechanism",
    "cert_class": "auditor_override_HP_to_MM_META_RULE_L_band_floor_ceiling_META_RULE_Q_universal_saturation_confirms_design_level_MM",
    "verified_off_data": True,
    "atomized_by": "skunkworks_landed_VET_wave_2026-07-01_post_compaction",
    "cell_commit": COMMIT,
    "verdict": (
        "MEASURED_MECHANISM_auditor_override_HP_to_MM_META_RULE_L_all_5_beta_saturate_at_1p000_M_4096_"
        "positive_control_STD_0p148_discriminates_metric_but_beta_axis_NOT_discriminating_"
        "preview_M_16384_beta_5_AND_20_both_at_1p000_full_N_confirms_saturation_at_full_N_"
        "single_seed_smoke_seeds_13_19_NOT_dispatched_"
        "confirms_prior_design_level_MM_atom_META_RULE_AG_discriminator_saturation_"
        "revival_criterion_M_ge_32768_or_correlated_keys"
    ),
    "cert_increment_delta": 0,
    "cv": None,
    "referent_pointer": {
        "notes_path": None,
        "metrics_path": "data/exp_cortex_hippo_dense_beta_sweep_v1_seed_7/metrics.json",
        "prereg_path": "preregs/2026-07-01_cortex_hippo_dense_beta_sweep_v1.md",
        "parent_design_level_MM_atom": "T3/EXP_cortex_hippo_dense_beta_sweep_v1_DESIGN_LEVEL_MM_cell_author_honest_abort_at_prereg",
        "atom_qualified_id": f"math::{ATOM_3_ID}",
    },
    "supersedes": None,
    "note": (
        "beta_sweep_v1_seed_7_smoke_MM_auditor_override_HP_to_MM_"
        "all_5_beta_saturate_at_recall_1p000_META_RULE_L_band_floor_META_RULE_Q_universal_saturation_"
        "preview_full_N_M_16384_beta_5_and_20_confirms_saturation_at_full_N_"
        "single_seed_only_seeds_13_19_NOT_dispatched_"
        "confirms_prior_design_level_MM_atom_from_same_cell_family_"
        "cell_D_v2_CG_and_v3_M_sweep_CG_provide_the_bounding_evidence_"
        "revival_criterion_higher_alpha_or_correlated_keys_unchanged"
    ),
}

# ---------- Atom 4: sparsity_free_axis_v1 3-seed HF_TEST_DESIGN_FAILURE ----------
ATOM_4_ID = (
    "T3/EXP_substrate_sparsity_free_axis_v1_3seed_"
    "HARD_FAIL_TEST_DESIGN_FAILURE_positive_control_PC_alpha_0p10_top1_1p000_OVERSHOOTS_expected_band_0p30_to_0p90_"
    "regime_too_easy_ceiling_hit_across_ALL_6_PC_alphas_saturation_at_0p98_to_1p00_"
    "WM_regime_also_saturates_0p999_to_1p000_"
    "sparsity_range_ok_False_because_all_alphas_at_ceiling_"
    "cardinality_12_of_12_ok_arms_differ_verified_"
    "NOT_a_substrate_failure_test_design_needs_harder_regime_"
    "revival_criterion_M_increase_or_higher_corruption_or_lower_N_2026-07-01"
)
ATOM_4 = {
    "id": ATOM_4_ID,
    "name": (
        "HF_TEST_DESIGN_FAILURE Cell substrate_sparsity_free_axis_v1 3-seed FULL run: positive control "
        "at PC regime alpha=0.10 M=100 c=0.485 predicted to sit in [0.30, 0.90] band (pre-reg cap_ratio=1.12 "
        "just below break edge). Observed: top1_mechanism_mean=1.000 all 3 seeds - OVERSHOOTS the expected "
        "band ceiling (0.90). Verdict correctly fires HARD_FAIL_POSITIVE_CONTROL_PC. Root cause: TEST-DESIGN "
        "REGIME MISCALIBRATION, not substrate failure. All 6 PC sparsity alphas {0.005..0.20} saturate at "
        "0.98-1.00; all 6 WM alphas at 0.999-1.000. Sparsity range test <0.02 across all alphas (fails "
        ">=0.10 threshold trivially due to ceiling). Cardinality 12/12 per seed observed; arms_differ_verified "
        "True; NOT a mechanism bug. Attribution: HF_TEST_DESIGN_FAILURE (per July 1 auditor discipline). "
        "Revival criterion: harder regime that lands PC positive control INTO [0.30, 0.90] band. Candidates: "
        "M >= 500 items OR c >= 0.55 corruption OR N <= 4096 substrate dimension OR fewer cleanup iters T. "
        "Sparsity as a substrate-only capacity lever remains UNCHARACTERIZED (this cell didn't test it; the "
        "regime never left the mechanism-saturation ceiling). CERT +0 (HF but attribution notes not-substrate)."
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record",
    "description": (
        f"OFF-DATA verified: data/exp_substrate_sparsity_free_axis_v1_seed_{{7,13,19}}/metrics.json.\n\n"
        f"Recompute Skunkworks {DATE}:\n"
        f"  Per-seed verdict: HARD_FAIL_POSITIVE_CONTROL_PC (all 3 seeds identical firing).\n"
        f"  PC regime positive control at alpha=0.10 M=100 c=0.485:\n"
        f"    top1_mechanism_mean = 1.0 all 3 seeds (band [0.30, 0.90] OVERSHOT).\n"
        f"  PC alpha sweep across {{0.005, 0.01, 0.025, 0.05, 0.10, 0.20}}:\n"
        f"    seed 7:  [0.99, 1.0, 1.0, 1.0, 1.0, 1.0] range=0.01\n"
        f"    seed 13: [0.98, 1.0, 1.0, 1.0, 1.0, 1.0] range=0.02\n"
        f"    seed 19: [0.99, 1.0, 1.0, 1.0, 1.0, 1.0] range=0.01\n"
        f"    All ranges << 0.10 HP threshold; ceiling behavior on ALL 6 alphas.\n"
        f"  WM regime alpha sweep at K=500 B=16 c=0.30:\n"
        f"    seeds saturate at 0.999-1.000 (range 0.0006-0.0012).\n"
        f"  Cardinality: 12/12 per seed (6 alpha x 2 regimes); arms_differ_verified True.\n"
        f"  Positive control gate: 0.30 <= pc_row.top1_mechanism_mean <= 0.90 REQUIRED; observed 1.0 -> FAIL.\n"
        f"\nHF ATTRIBUTION (per July 1 auditor discipline broken-PC-before-structural-framing):\n"
        f"  This is HF_TEST_DESIGN_FAILURE, NOT HF_STRUCTURAL_BOUND.\n"
        f"  The positive control did NOT clear its expected floor (0.30) then reach a wall;\n"
        f"    it OVERSHOT the expected ceiling (0.90). The mechanism is doing TOO WELL for the\n"
        f"    test regime to discriminate anything about the sparsity axis.\n"
        f"  Substrate is NOT broken; test design is miscalibrated.\n"
        f"  Do not treat this as evidence 'sparsity does not drive capacity' - the test never\n"
        f"    left the mechanism-saturation regime where sparsity could matter.\n"
        f"\nRELATIONSHIP TO PRE-REG PREDICTION: pre-reg (line 107) predicted cap_ratio=1.12 with\n"
        f"  positive control sitting 'just below break edge; expect solid recall'. Observed\n"
        f"  behavior is well ABOVE that prediction; either the pre-reg's capacity formula is\n"
        f"  optimistic (mechanism handles cap_ratio~1 easily) OR N=8192 has enough slack for the\n"
        f"  Hopfield cleanup to saturate. Pre-reg CRLB prediction of PC alpha=0.005 -> FLOOR (0.263)\n"
        f"  was also violated (observed 0.98-0.99). The regime is much easier than pre-reg modeled.\n"
        f"\nREVIVAL CRITERIA (candidate harder regimes; any single change may suffice):\n"
        f"  (a) M >= 500 items (5x pressure) at same c=0.485\n"
        f"  (b) c >= 0.55 corruption (higher noise)\n"
        f"  (c) N <= 4096 substrate dim (less slack)\n"
        f"  (d) T_cleanup = 1 (single-step; less noise-tolerant readout)\n"
        f"  (e) Combined: M=500, c=0.55, N=4096, T=1 (aggressive)\n"
        f"  Design a v2 that first CALIBRATES the positive control BAND before sweeping sparsity.\n"
        f"\nCross-arc overlap check {DATE}: substrate_query 'sparsity free axis regime PC WM'\n"
        f"  no prior cell with same sparsity_range design pattern; NOT a rediscovery.\n"
        f"  Sparsity WAS tested at fixed PC regime in Batch A x C v2 CG (per pre-reg compose ref);\n"
        f"  this cell was meant to extend to WM + free-axis mode; that extension not achieved due\n"
        f"  to saturation, not due to mechanism failure.\n"
        f"\nCompose with: Batch A x C v2 CG (parent calibration point); PC v2.2 dense cliff c=0.485.\n"
        f"Commit: {COMMIT}. Author: skunkworks_landed_VET_wave_2026-07-01_post_compaction."
    ),
    "metadata": {
        "ts_atomized": TS_NOW,
        "date_atomized": DATE,
        "cert_commit": COMMIT,
        "run_mode": "full",
        "n_seeds": 3,
        "seeds": [7, 13, 19],
        "cardinality_ok": True,
        "n_arm_outcomes_per_seed": 12,
        "arms_differ_verified": True,
        "verdict_per_seed": ["HARD_FAIL_POSITIVE_CONTROL_PC"] * 3,
        "pc_positive_control_top1_observed": 1.0,
        "pc_positive_control_top1_expected_band": [0.30, 0.90],
        "pc_sparsity_range_per_seed": [0.01, 0.02, 0.01],
        "pc_sparsity_range_HP_threshold": 0.10,
        "wm_sparsity_range_per_seed": [0.0006, 0.001, 0.0012],
        "hf_attribution": "HF_TEST_DESIGN_FAILURE",
        "hf_attribution_reason": "positive_control_OVERSHOT_expected_band_ceiling_0p90_regime_too_easy_mechanism_saturates_across_all_alphas_and_regimes",
        "verified_off_data": True,
        "metrics_paths": [
            "data/exp_substrate_sparsity_free_axis_v1_seed_7/metrics.json",
            "data/exp_substrate_sparsity_free_axis_v1_seed_13/metrics.json",
            "data/exp_substrate_sparsity_free_axis_v1_seed_19/metrics.json",
        ],
        "prereg_path": "preregs/2026-07-01_sparsity_free_axis_v1.md",
        "parent_atoms": [
            "batch_A_x_C_v2_CG",
            "PC_v2p2_dense_cliff_c0p485",
            "WM_multibank_K500",
        ],
        "cert_tier": "hard_fail_test_design_failure",
        "cert_increment_delta": 0,
        "revival_criterion": (
            "harder_regime_that_lands_PC_positive_control_INTO_expected_0p30_to_0p90_band_"
            "candidates_M_ge_500_or_c_ge_0p55_or_N_le_4096_or_T_cleanup_1_or_combined"
        ),
    },
}
LEDGER_4 = {
    "ts": TS_NOW,
    "op": "cert_ruling_hard_fail_test_design_failure",
    "atom_id": f"math::{ATOM_4_ID}",
    "cert_status": "hard_fail_test_design_failure",
    "cert_class": "HF_test_design_regime_miscalibration_positive_control_OVERSHOOT_not_substrate_failure",
    "verified_off_data": True,
    "atomized_by": "skunkworks_landed_VET_wave_2026-07-01_post_compaction",
    "cell_commit": COMMIT,
    "verdict": (
        "HARD_FAIL_TEST_DESIGN_FAILURE_3seed_positive_control_PC_alpha_0p10_top1_1p000_OVERSHOOTS_band_0p30_to_0p90_"
        "all_6_PC_alphas_saturate_0p98_to_1p00_all_6_WM_alphas_saturate_0p999_to_1p00_"
        "sparsity_range_lt_0p02_across_all_alphas_regime_too_easy_ceiling_hit_"
        "NOT_substrate_failure_test_design_needs_harder_regime_"
        "cardinality_12_of_12_per_seed_arms_differ_True_"
        "revival_criterion_M_ge_500_or_c_ge_0p55_or_N_le_4096_or_T_1"
    ),
    "cert_increment_delta": 0,
    "cv": 0.0,
    "referent_pointer": {
        "notes_path": None,
        "metrics_path": "data/exp_substrate_sparsity_free_axis_v1_seed_{7,13,19}/metrics.json",
        "prereg_path": "preregs/2026-07-01_sparsity_free_axis_v1.md",
        "atom_qualified_id": f"math::{ATOM_4_ID}",
    },
    "supersedes": None,
    "note": (
        "sparsity_free_axis_v1_3seed_HF_TEST_DESIGN_FAILURE_"
        "positive_control_OVERSHOOTS_expected_band_ceiling_0p90_regime_too_easy_"
        "all_6_PC_alphas_and_all_6_WM_alphas_saturate_at_ceiling_"
        "sparsity_axis_NOT_characterized_regime_never_left_mechanism_saturation_"
        "do_NOT_conclude_sparsity_flat_from_this_data_"
        "revival_v2_needs_harder_regime_M_ge_500_or_c_ge_0p55_or_N_le_4096_or_T_1_"
        "calibrate_positive_control_BAND_FIRST_before_sweeping_sparsity"
    ),
}

# ---------- Atom 5: TASK_VECTOR HRR ICL K_500_extended 3-seed CG ----------
ATOM_5_ID = (
    "T3/EXP_substrate_task_vector_HRR_ICL_K_500_extended_v1_3seed_CHAIN_GRADE_"
    "K_of_mechanism_death_1000_ALL_3_seeds_cliff_localized_perfectly_"
    "K50_TV_1p00_0p95_1p00_all_ge_0p85_HP_floor_"
    "K200_TV_0p95_cv_0p023_K500_TV_0p663_cv_0p050_high_signal_regime_cv_lt_0p10_"
    "K1000_TV_0p243_all_below_0p30_mechanism_floor_ratio_K2000_dead_floor_0p073_"
    "RV_baseline_0p000_all_K_all_seeds_clean_floor_arms_differ_all_5_K_"
    "cardinality_1500_of_1500_per_seed_expected_5_K_x_3_arms_x_100_queries_"
    "extends_referent_K_extended_v1_from_2026_06_30_axis_50_100_200_500_1000_to_50_200_500_1000_2000_"
    "V_ENTS_POOL_2200_lifted_from_1000_capacity_bound_characterization_"
    "SSH_pulled_via_scp_remote_C_dev_hd_instrument_9th_CG_of_2026_07_01_2026-07-01"
)
ATOM_5 = {
    "id": ATOM_5_ID,
    "name": (
        "CG substrate_task_vector_HRR_ICL_K_500_extended_v1 3-seed FULL: K-cliff at K=1000 "
        "PERFECTLY LOCALIZED across ALL 3 seeds {7, 13, 19}; K_of_mechanism_death=1000 identical. "
        "TV recall shape: K=50 [1.00, 0.95, 1.00] mean=0.98 cv=0.024 all >= 0.85 HP_K50_FLOOR; "
        "K=200 [0.93, 0.98, 0.94] mean=0.95 cv=0.023; K=500 [0.67, 0.62, 0.70] mean=0.66 cv=0.050 "
        "(pre-cliff shoulder; cv<0.10 in high-signal regime); K=1000 [0.24, 0.20, 0.29] mean=0.24 "
        "all below HP_MECHANISM_FLOOR_RATIO=0.30 (mechanism dies uniformly); K=2000 [0.09, 0.06, 0.07] "
        "mean=0.073 dead-floor Bernoulli-random. RV_top1=0.0 at ALL 15 (K, seed) cells (clean fairness "
        "floor); arms_diff at all 5 K = TV values (RV=0.0). Cardinality 1500/1500 per seed (5 K x 3 arms "
        "x 100 queries) all seeds. Extends 2026-06-30 referent K_extended_v1 (axis {50,100,200,500,1000}) "
        "to {50, 200, 500, 1000, 2000} with V_ENTS_POOL 2200 (lifted from 1000). This is a capacity-bound "
        "characterization: TASK_VECTOR HRR ICL supports up to K~500 tasks in 8192-D substrate with "
        "V_TASKS=10 V_ENTS_POOL=2200 OVERLAP=0.0; dies at K~1000 (alpha=K/V_ENTS ~0.45; smooth transition "
        "K=500 shoulder -> K=1000 cliff). CERT +1."
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record",
    "description": (
        f"OFF-DATA verified: SSH-pulled from marsh@home:C:/dev/hd-instrument/data/exp_substrate_task_vector_"
        f"HRR_ICL_K_500_extended_v1_seed_{{7,13,19}}/metrics.json to data/session_local/skunkworks/ "
        f"(sync-lag bypass; ~20 min later local hd_metrics_sync will land copy).\n\n"
        f"Recompute Skunkworks {DATE}:\n"
        f"  K=50:   TV = [1.00, 0.95, 1.00] mean=0.983 cv=0.0240 (high_signal_regime cv_ok)\n"
        f"  K=200:  TV = [0.93, 0.98, 0.94] mean=0.950 cv=0.0227 (high_signal_regime cv_ok)\n"
        f"  K=500:  TV = [0.67, 0.62, 0.70] mean=0.663 cv=0.0497 (high_signal_regime cv_ok; pre-cliff shoulder)\n"
        f"  K=1000: TV = [0.24, 0.20, 0.29] mean=0.243 cv=0.1513 (mechanism dies; low-signal cv gate exempt)\n"
        f"  K=2000: TV = [0.09, 0.06, 0.07] mean=0.073 cv=0.1701 (dead-floor; low-signal cv gate exempt)\n"
        f"  RV_top1_recall = 0.0 at ALL 15 (K, seed) cells (clean fairness floor).\n"
        f"  arms_diff(TV-RV) = TV values (RV=0.0 baseline).\n"
        f"  K_of_mechanism_death = 1000 across ALL 3 seeds (perfect cross-seed cliff localization).\n"
        f"  Cardinality: expected_n=1500 observed_n=1500 all seeds (5 K x 3 arms x 100 queries).\n"
        f"  K50_floor_ok=True all seeds (all >=0.85 HP_K50_FLOOR).\n"
        f"  cv_gate_ok=True (no violations at high-signal K values).\n"
        f"\nWHY THIS IS CG:\n"
        f"  (a) 3-seed FULL run, HP verdict on all 3.\n"
        f"  (b) K_of_mechanism_death localizes to K=1000 identically across 3 seeds - perfect cliff\n"
        f"      consistency (not seed-dependent).\n"
        f"  (c) High-signal regime cv on TV recall = 0.024/0.023/0.050 at K=50/200/500 (all <0.10 CG-tight).\n"
        f"  (d) Positive control: K=50 TV=0.983 mean (near-ceiling); mechanism works at low K.\n"
        f"  (e) Negative control: RV=0.0 at all K; random-vector baseline pinned to floor.\n"
        f"  (f) Cardinality full (no partial runs); arms_differ verified.\n"
        f"  (g) Cliff structure: 0.98 -> 0.95 -> 0.66 -> 0.24 -> 0.07 - smooth monotonic decay through\n"
        f"      cliff at K=1000; alpha=K/V_ENTS_POOL = 0.023/0.091/0.227/0.455/0.909 (cliff between\n"
        f"      alpha~0.23 shoulder and alpha~0.45 death).\n"
        f"\nMETA_RULE_Q GENUINE-CEILING CHECK: K=50 TV=1.00 for seeds 7 and 19 but 0.95 for seed 13.\n"
        f"  NOT universal saturation - the mechanism curve TRANSITIONS from 0.98 -> 0.07 as K grows.\n"
        f"  Positive control (K=50 near ceiling) works cleanly; TV drops in high-K regime confirms\n"
        f"  metric discriminates. Genuine capacity-bound characterization.\n"
        f"\nOBSERVATION-QUALITY NOTE: elapsed_s = 0.0 (seeds 7, 13) / 0.01 (seed 19) in metrics.json.\n"
        f"  This is a wrapper-timing bug (inner-only measurement); Director-observed wall was\n"
        f"  8s/3s/4s per seed. Does NOT invalidate the recall measurements which are all populated\n"
        f"  and self-consistent (cardinality full, per-K arms match manual computation).\n"
        f"\nCross-arc overlap check {DATE}: substrate_query 'TASK_VECTOR HRR ICL K cliff K-shot ICL'\n"
        f"  top-1 cosine=0.28 (ICL-as-schema-retrieval concept notes; NO prior K-sweep at this axis).\n"
        f"  Prior referent K_extended_v1 (2026-06-30) tested axis {{50, 100, 200, 500, 1000}}; that\n"
        f"  cell also failed to fire discriminator at smoke (TV~0.87 per pre-reg comment). This v1-A\n"
        f"  revision extends K axis to {{50, 200, 500, 1000, 2000}} and lifts V_ENTS_POOL 1000 -> 2200\n"
        f"  to accommodate K=2000. GENUINELY NOVEL axis coverage; NOT a rediscovery.\n"
        f"\nRELATIONSHIP TO REFERENT: 2026-06-30 K_extended_v1 was HF at smoke on K=200 discriminator.\n"
        f"  v1-A K_500_extended (this cell) fires cliff cleanly at K=1000; discriminator-must-survive-\n"
        f"  scale discipline honored by 100 queries at full N=8192 in smoke seed 7 that fired at\n"
        f"  TV(K=1000)=0.260 < 0.60 floor. FULL 3-seed run confirms with tight cross-seed cv.\n"
        f"\nRevival criterion: further K-axis extension to K in {{2000, 4000, 8000}} at V_ENTS_POOL 8000+\n"
        f"  would characterize the dead-floor tail; not needed for chain-grade cliff-localization claim.\n"
        f"\nCompose with: prior TASK_VECTOR HRR ICL cells (K_extended_v1 referent; K_extended_v1 smoke HF).\n"
        f"Commit: {COMMIT}. Author: skunkworks_landed_VET_wave_2026-07-01_post_compaction (SSH-pull)."
    ),
    "metadata": {
        "ts_atomized": TS_NOW,
        "date_atomized": DATE,
        "cert_commit": COMMIT,
        "run_mode": "full",
        "n_seeds": 3,
        "seeds": [7, 13, 19],
        "K_values": [50, 200, 500, 1000, 2000],
        "V_TASKS": 10,
        "V_ENTS_POOL": 2200,
        "OVERLAP": 0.0,
        "N_DIM": 8192,
        "N_QUERIES": 100,
        "cardinality_ok_all_seeds": True,
        "n_records_per_seed": 1500,
        "K_of_mechanism_death_per_seed": {7: 1000, 13: 1000, 19: 1000},
        "K_of_mechanism_death_localized_identically": True,
        "TV_recall_per_K_cross_seed_mean": {50: 0.9833, 200: 0.9500, 500: 0.6633, 1000: 0.2433, 2000: 0.0733},
        "TV_recall_per_K_cross_seed_cv": {50: 0.0240, 200: 0.0227, 500: 0.0497, 1000: 0.1513, 2000: 0.1701},
        "RV_baseline_all_K_all_seeds": 0.0,
        "K50_floor_ok_all_seeds": True,
        "cv_gate_ok_all_seeds": True,
        "high_signal_K_values": [50, 200, 500],
        "dead_K_values": [1000, 2000],
        "verified_off_data": True,
        "verified_via_ssh_pull_sync_lag_bypass": True,
        "metrics_paths_remote": [
            "C:/dev/hd-instrument/data/exp_substrate_task_vector_HRR_ICL_K_500_extended_v1_seed_7/metrics.json",
            "C:/dev/hd-instrument/data/exp_substrate_task_vector_HRR_ICL_K_500_extended_v1_seed_13/metrics.json",
            "C:/dev/hd-instrument/data/exp_substrate_task_vector_HRR_ICL_K_500_extended_v1_seed_19/metrics.json",
        ],
        "metrics_paths_local_cache": [
            "data/session_local/skunkworks/task_vector_K_500_extended_seed_7_metrics.json",
            "data/session_local/skunkworks/task_vector_K_500_extended_seed_13_metrics.json",
            "data/session_local/skunkworks/task_vector_K_500_extended_seed_19_metrics.json",
        ],
        "prereg_path": "preregs/2026-07-01_substrate_task_vector_HRR_ICL_K_500_extended_v1.md",
        "parent_atoms": [
            "substrate_task_vector_K_extended_v1_referent_2026_06_30",
        ],
        "cert_tier": "chain_grade",
        "cert_increment_delta": 1,
        "observation_quality_note": "elapsed_s=0.0_wrapper_timing_bug_inner_only_measurement_does_not_invalidate_recall_measurements",
    },
}
LEDGER_5 = {
    "ts": TS_NOW,
    "op": "cert_ruling_promotion_chain_grade",
    "atom_id": f"math::{ATOM_5_ID}",
    "cert_status": "chain_grade",
    "cert_class": "pre_reg_pass_K_cliff_localization_TASK_VECTOR_HRR_ICL",
    "verified_off_data": True,
    "atomized_by": "skunkworks_landed_VET_wave_2026-07-01_post_compaction_SSH_pull",
    "cell_commit": COMMIT,
    "verdict": (
        "CHAIN_GRADE_3seed_HP_FULL_K_of_mechanism_death_1000_localized_perfectly_across_all_3_seeds_"
        "K50_TV_1p00_0p95_1p00_all_ge_0p85_K200_TV_0p95_cv_0p023_K500_TV_0p663_cv_0p050_high_signal_cv_lt_0p10_"
        "K1000_TV_0p243_all_below_0p30_mechanism_floor_K2000_TV_0p073_dead_floor_"
        "RV_baseline_0p000_clean_floor_all_15_K_seed_cells_arms_differ_verified_"
        "cardinality_1500_of_1500_per_seed_full_5_K_3_arms_100_queries_"
        "capacity_bound_characterization_TASK_VECTOR_HRR_ICL_supports_K_up_to_500_at_N_8192_V_ENTS_2200_"
        "cliff_at_alpha_K_over_V_ENTS_pool_0p45_9th_CG_of_2026_07_01"
    ),
    "cert_increment_delta": 1,
    "cv": 0.05,
    "referent_pointer": {
        "notes_path": None,
        "metrics_path_remote": "C:/dev/hd-instrument/data/exp_substrate_task_vector_HRR_ICL_K_500_extended_v1_seed_{7,13,19}/metrics.json",
        "metrics_path_local_cache": "data/session_local/skunkworks/task_vector_K_500_extended_seed_{7,13,19}_metrics.json",
        "prereg_path": "preregs/2026-07-01_substrate_task_vector_HRR_ICL_K_500_extended_v1.md",
        "referent_atom": "substrate_task_vector_K_extended_v1_2026_06_30",
        "atom_qualified_id": f"math::{ATOM_5_ID}",
    },
    "supersedes": None,
    "note": (
        "substrate_task_vector_HRR_ICL_K_500_extended_v1_3seed_CHAIN_GRADE_9th_CG_of_2026_07_01_"
        "K_of_mechanism_death_1000_ALL_3_seeds_perfect_cliff_localization_"
        "TV_recall_shape_smooth_monotonic_0p98_to_0p07_through_cliff_at_K_1000_"
        "K50_HP_floor_met_all_seeds_high_signal_cv_lt_0p10_K_200_500_"
        "positive_control_K_50_near_ceiling_negative_control_RV_pinned_to_0p0_"
        "cardinality_full_arms_differ_verified_all_5_K_all_3_seeds_"
        "cliff_at_alpha_K_over_V_ENTS_pool_0p45_capacity_wall_for_HRR_ICL_at_N_8192_V_ENTS_2200_"
        "extends_referent_K_extended_v1_axis_and_lifts_V_ENTS_POOL_to_2200_"
        "verified_off_data_via_SSH_scp_pull_sync_lag_bypass_local_hd_metrics_sync_pending_20_min_"
        "elapsed_s_wrapper_timing_bug_inner_only_measurement_does_not_invalidate_recall_values"
    ),
}

# ---------- Meta Amendment 5: M3 architecture meta MM_STANDARD -> chain-grade ----------
META_AMENDMENT_ID = (
    "T3/AMENDMENT_M3_architecture_meta_MM_STANDARD_to_CHAIN_GRADE_"
    "expansion_criterion_c_multi_M_validation_SATISFIED_"
    "by_v3_M_sweep_3seed_REPL_recall_1p000_all_9_outcomes_M_4096_8192_16384_cv_0p000_"
    "companion_atom_v3_M_sweep_CG_this_commit_"
    "amends_prior_M3_meta_MM_STANDARD_amendment_from_fc47b1bb_"
    "final_promotion_to_chain_grade_all_3_criteria_a_b_c_satisfied_2026-07-01"
)
META_AMENDMENT = {
    "id": META_AMENDMENT_ID,
    "name": (
        "AMENDMENT: M3 cortex-layer architecture meta atom promoted MM_STANDARD -> chain-grade. "
        "Criterion (c) 'pattern verified at other M values' SATISFIED by cortex_hippo v3 M-sweep "
        "3-seed CG landing (this commit's Atom 1): REPL recall = 1.000 at all 9 outcomes across "
        "M in {4096, 8192, 16384} x seeds {7, 13, 19}; cross-seed CV = 0.000 perfect stability; "
        "positive control STANDARD monotonically collapses 0.766 -> 0.271 -> 0.052 as M scales "
        "(Amit-Gutfreund wall confirmed, metric IS discriminating). "
        "All 3 expansion criteria now satisfied: (a) multi-seed replication [Cell D v2 CG fc47b1bb + "
        "v3 M-sweep 3-seed CG]; (b) v2 replacement-mode 3-seed FULL pass [fc47b1bb]; (c) multi-M "
        "validation across M in {4096, 8192, 16384} [v3 M-sweep this commit]. "
        "M3 architecture insight 'dense-Hopfield should REPLACE not COMPOSE with cortex Hebbian' "
        "is now chain-grade at scale-independent across a 4x M range. CERT +0 (companion delta counted "
        "on Atom 1)."
    ),
    "corpus": "meta",
    "tier": "T3",
    "kind": "meta_synthesis_amendment",
    "description": (
        f"OFF-DATA verified via companion Atom 1 recompute (see math::EXP_substrate_cortex_hippo_dense_layer_M_sweep_v3).\n\n"
        f"AMENDS: M3 architecture meta atom edf59e18 (MM_TENTATIVE) -> fc47b1bb amendment (MM_STANDARD)\n"
        f"  -> THIS AMENDMENT (chain-grade).\n\n"
        f"CRITERION (c) SATISFACTION EVIDENCE:\n"
        f"  Prior fc47b1bb amendment noted: 'criterion (c) multi_M_values NOT_yet_verified_prevents_CG_lift'.\n"
        f"  This amendment closes that criterion with 9-of-9 REPL=1.000 outcomes across a 4x M range,\n"
        f"  cv=0.000 cross-seed, and STD positive control confirming metric discriminates.\n\n"
        f"CROSS-SEED CV RECOMPUTE (Skunkworks {DATE}):\n"
        f"  M=4096:  REPL cv=0.0; STD cv=0.0182; HA_ONLY mean=0.000163\n"
        f"  M=8192:  REPL cv=0.0; STD cv=0.0147; HA_ONLY mean=0.000203\n"
        f"  M=16384: REPL cv=0.0; STD cv=0.0274; HA_ONLY mean=0.000102\n\n"
        f"CLAIM SCOPE (chain-grade):\n"
        f"  Dense-Hopfield attention over sparse-DG-written tape (Ha writes, Hc reads via softmax attention)\n"
        f"  achieves recall = 1.000 cortex-side across M in {{4096, 8192, 16384}} at N_c=4096 sparse=0.1\n"
        f"  with adaptive beta = log2(M)/cos_margin formula; stable across seeds; scale-independent in\n"
        f"  the tested M range. STANDARD Hebbian cortex-only positive control monotonically collapses\n"
        f"  from 0.77 (M=4096) to 0.05 (M=16384) confirming the Amit-Gutfreund capacity wall exists\n"
        f"  and the replacement-mode mechanism bypasses it.\n\n"
        f"REVIVAL CRITERION (out-of-scope regime to characterize wall):\n"
        f"  M >= 32768 at N_c=4096 (alpha=8.0; deep in bipolar quantization regime) OR correlated keys\n"
        f"  (subspace-drawn, k << N_c; violates uncorrelated bipolar assumption in Ramsauer eq.14).\n\n"
        f"Compose with: Cell D v2 M8192 CG (fc47b1bb); v3 M-sweep 3-seed CG (this commit's Atom 1);\n"
        f"  prior M3 meta atom (edf59e18 MM_TENTATIVE -> fc47b1bb MM_STANDARD -> this chain-grade).\n"
        f"Commit: {COMMIT}. Author: skunkworks_landed_VET_wave_2026-07-01_post_compaction."
    ),
    "metadata": {
        "ts_atomized": TS_NOW,
        "date_atomized": DATE,
        "cert_commit": COMMIT,
        "amends_prior_atom": "T3/AMENDMENT_M3_architecture_meta_synthesis_MM_TENTATIVE_to_MM_STANDARD_promotion",
        "amends_prior_atom_commit": "fc47b1bb",
        "original_M3_meta_atom": "T3/META_synthesis_M3_cortex_layer_architecture_INSIGHT_dense_Hopfield_should_REPLACE_not_COMPOSE_with_cortex_Hebbian",
        "original_M3_meta_atom_commit": "edf59e18",
        "companion_v3_M_sweep_CG_atom": f"math::{ATOM_1_ID}",
        "criteria_now_all_satisfied": ["a_multi_seed", "b_v2_replacement_3seed_FULL", "c_multi_M_values"],
        "cert_tier": "chain_grade",
        "cert_increment_delta": 0,
        "delta_counted_on": f"math::{ATOM_1_ID}",
        "verified_off_data": True,
    },
}
LEDGER_META_AMENDMENT = {
    "ts": TS_NOW,
    "op": "cert_amendment_tier_promotion_MM_STANDARD_to_chain_grade",
    "atom_id": f"meta::{META_AMENDMENT_ID}",
    "cert_status": "chain_grade_amendment_tier_promotion",
    "cert_class": "M3_meta_architecture_promotion_MM_STANDARD_to_chain_grade_criterion_c_satisfied",
    "verified_off_data": True,
    "atomized_by": "skunkworks_landed_VET_wave_2026-07-01_post_compaction",
    "cell_commit": COMMIT,
    "verdict": (
        "AMENDMENT_M3_meta_MM_STANDARD_to_chain_grade_criterion_c_SATISFIED_"
        "by_v3_M_sweep_3seed_CG_REPL_recall_1p000_all_9_outcomes_M_4096_8192_16384_cv_0p000_"
        "STD_positive_control_collapses_0p77_M4096_to_0p05_M16384_Amit_Gutfreund_wall_confirmed_"
        "all_3_expansion_criteria_a_b_c_now_satisfied_"
        "amends_fc47b1bb_MM_STANDARD_amendment_which_amended_edf59e18_MM_TENTATIVE_"
        "companion_v3_M_sweep_CG_atom_same_commit_delta_counted_there"
    ),
    "cert_increment_delta": 0,
    "cv": None,
    "referent_pointer": {
        "notes_path": None,
        "amends_atom_commit_prior": "fc47b1bb",
        "amends_atom_commit_original": "edf59e18",
        "companion_v3_M_sweep_CG_atom": f"math::{ATOM_1_ID}",
        "atom_qualified_id": f"meta::{META_AMENDMENT_ID}",
    },
    "supersedes": None,
    "note": (
        "M3_architecture_meta_MM_STANDARD_to_chain_grade_amendment_"
        "criterion_c_multi_M_validation_SATISFIED_by_v3_M_sweep_CG_landing_"
        "all_3_expansion_criteria_a_b_c_now_satisfied_"
        "M3_cortex_layer_architecture_insight_dense_Hopfield_REPLACE_not_COMPOSE_"
        "is_now_chain_grade_at_scale_independent_M_4096_to_16384_"
        "companion_v3_M_sweep_CG_atom_delta_counted_there_"
        "hdlab_primitives_can_now_ship_replacement_mode_dense_Hopfield_as_default_M3_cortex_layer_primitive"
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
    # Read existing content first
    existing_content = b""
    if path.exists():
        existing_content = path.read_bytes()
    # Ensure trailing newline
    if existing_content and not existing_content.endswith(b"\n"):
        existing_content += b"\n"
    # Serialize new records
    new_lines = b""
    for rec in records:
        line = json.dumps(rec, ensure_ascii=False) + "\n"
        new_lines += line.encode("utf-8")
    tmp_path.write_bytes(existing_content + new_lines)

    # Verify load: every line must be valid JSON
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
    # Write math atoms (5 atoms: Atom 1 v3 CG, Atom 2 pop coding CG, Atom 3 beta smoke MM,
    #                            Atom 4 sparsity HF, Atom 5 task_vector K_500_extended CG)
    math_before, math_after = atomic_append_jsonl(MATH_ATOMS, [ATOM_1, ATOM_2, ATOM_3, ATOM_4, ATOM_5])
    print(f"math/atoms.jsonl: {math_before} -> {math_after} (+{math_after - math_before})")

    # Write meta atoms (1 amendment)
    meta_before, meta_after = atomic_append_jsonl(META_ATOMS, [META_AMENDMENT])
    print(f"meta/atoms.jsonl: {meta_before} -> {meta_after} (+{meta_after - meta_before})")

    # Write cert_ledger entries (5 math ledgers + 1 meta amendment ledger; all same ts)
    ledger_records = [LEDGER_1, LEDGER_2, LEDGER_3, LEDGER_4, LEDGER_5, LEDGER_META_AMENDMENT]
    led_before, led_after = atomic_append_jsonl(CERT_LEDGER, ledger_records)
    print(f"meta/cert_ledger.jsonl: {led_before} -> {led_after} (+{led_after - led_before})")

    # Summary
    print()
    print(f"CERT delta: +3 (Atom 1 v3 M-sweep CG; Atom 2 population coding CG; Atom 5 task_vector K_500_extended CG)")
    print(f"MM: +1 (Atom 3 beta_sweep smoke confirms design-level MM)")
    print(f"HF: +1 (Atom 4 sparsity_free_axis TEST_DESIGN_FAILURE)")
    print(f"Meta amendment: M3 architecture meta MM_STANDARD -> chain-grade")
    print(f"Timestamp: {TS_NOW}")
    print(f"Commit: {COMMIT}")


if __name__ == "__main__":
    main()
