"""
A5-gated atomization batch — Skunkworks landed-VET 2026-07-04 (~03:1xZ).

BATCH CONTENTS (4 atoms, matching TS_ISO):
  (1) math MM_STANDARD BOUNDED_NULL  — Probe 9 v2 (N x chain-depth-L at BUNDLED near-capacity),
      3-seed FULL, genuine in-band (NOT saturation-vacuous), per-seed H1_ALT firings OVERTURNED
      by cross-seed sign audit -> no reproducible N x L cross-term; codebook-draw variance dominates.
  (2) math DEMOTION amendment — Probe 8 (F x CLEANUP at cliff-adjacent) MM_STANDARD -> MIDDLE_BAND:
      5-FULL-seed H1 statistic indistinguishable from binomial-only extreme-value null (MC z=0.40).
      CG_META promotion DENIED (cv=0.1797 > 0.15 AND noise-floor unresolved).
  (3) meta MM_TENTATIVE — rule #45b: pre-classified-axis short-circuit applies ONLY when the
      DESIGN POINT sits in the degenerate regime (P9v2 carve-out case study).
  (4) meta MM_TENTATIVE — rule: extreme-value discriminator thresholds must be calibrated
      against the max-statistic null (MC/analytic), not per-point sd (P8 case study).

============================= INDEPENDENT RECOMPUTE EVIDENCE =============================

PROBE 9 V2 (seeds 7/13/19 FULL TR=100 GPU; core commit a75dccdd5; v1 lineage 0c5761c87+8f63ac421):
  Signature (exact, per Fix#28 #9 no-abstraction): STORAGE=BUNDLED, MECH=modern_hopfield,
    M=10, F=1, corr=0.10, N_cliff=2048 (MEASURED@bracket_scout2); N in {1024,2048,4096}
    (0.5x/1x/2x N_cliff), L in {2,4,8,16}; band [0.30,0.95].
  Integrity 3/3 seeds: cardinality_ok 17/17; PC pass (SHARDED M800 N2048 L4 corr0.20 acc=1.000);
    51/51 codebook+output hashes distinct; recomputed additive-model residuals off raw phase_map
    accs MATCH disk to <5e-4 in every cell.
  In-band cells per seed: 9 / 7 / 8 of 12 -> GENUINE in-band design (NOT saturation-vacuous;
    confirms Director disk-verify; resolves drill HOLD).
  Per-seed max|residual|_in_band: 0.1108 / 0.2033 / 0.2500 (H1_ALT >=0.10 fires 3/3;
    H1 clean bucket separation fails 3/3).
  MC null (binomial-only, p=0.40, TR=100, max|resid| over 12-cell 3x4 grid):
    mean 0.0627, q95 0.0975, q99 0.1158. P(>=0.1108)=0.016, P(>=0.2033)<1e-5, P(>=0.25)<1e-5.
    -> s13/s19 firings are REAL EXCESS VARIANCE beyond trial noise.
  BUT cross-seed sign audit (the reproducibility test): 0/12 grid cells sign-consistent at
    |dev|>=0.10. Only sign-consistent cells: N2048_L4 (mean -0.027, sd 0.012) and
    N2048_L8 (mean +0.062, sd 0.018) — both BELOW threshold. Max |cross-seed mean dev| = 0.120
    (N2048_L16, sd 0.146, SEM 0.084, t=1.42 n.s.). Per-cell cross-seed sd 0.11-0.19 vs binomial
    residual floor ~0.035 (~4x). Cell uses per-point salts (gen.manual_seed(seed*100003+salt),
    salt++ per grid point) -> independent codebook per cell -> excess variance is CODEBOOK-DRAW
    variance, not stable N x L structure.
  DISPOSITION: per-seed MIDDLE_BAND H1_ALT_DIFFUSE_CROSS_TERM verdicts OVERTURNED at cross-seed
    level -> BOUNDED_NULL: no reproducible N x L cross-term at >=0.10 resolution in-band at this
    signature. MM_STANDARD (bound is method-contingent: TR=100, 3 seeds).
  CAVEAT (control): H3 deep-sat null control FIRED 3/3 — TEST-DESIGN failure of the CONTROL
    only: DEEP_SAT arm (N=8192 M=100 corr=0.60 BUNDLED) sits at FLOOR (mean_acc 0.07-0.105),
    not intended ceiling degeneracy; L_spread 0.13-0.20 driven by L=2 retaining 0.15-0.23.
    Does not contaminate main grid; caps tier below CG.
  REVIVAL CRITERIA: (a) N2048_L8 stable +0.062 (t~5.9, 2 dof) — targeted TR>=400 multi-seed
    rerun at the N=N_cliff row; (b) higher-corr re-spec per drill (corr is the cliff-escape
    axis per Probe16 atom #56); (c) redesign deep-sat control (uniform-floor or true-ceiling arm).
  Cross-arc overlap (USER-locked 2026-07-01): substrate_query top hit cosine 0.298 (wordnet
    noise) — NONE relevant at >0.30; cell docstring prior-check also novel. NOVEL.

PROBE 8 (seeds 7/11/13/17/19 FULL TR=100; s11/s17 landed 2026-07-04T02:47Z via sync mid-audit;
  wrappers commit b1b7f1253; prior atom + amendment ledger lines 1350/1355):
  Integrity 5/5: run_mode=full, HARD_PASS, cardinality_ok 25/25, PC pass, 15/15 cliff cells
    in-band each seed. Cliff regime (exact): N=512, M=6400, corr=0.85, L=2, SHARDED,
    F_grid=[1,2,4,8,16], mechs {modern_hopfield, iterative_cosine, soft_energy_attractor}.
  Recomputed max_per_F_mech_variance_in_band off raw accs_by_mech (matches disk exactly):
    s7=0.12  s11=0.16  s13=0.10  s17=0.15  s19=0.14   mean 0.1340  sd 0.0241  cv 0.1797.
  CG promotion arithmetic: cv 0.1797 > 0.15 -> DENIED on the stated bar alone.
  NOISE-FLOOR AUDIT (the load-bearing finding): cell evaluates each (F, mech) point with an
    INDEPENDENT salt (salt++ per point) -> mechanisms compared on different codebooks AND
    different trials. H1 statistic = max over 5 F of range of 3 iid accs. MC null
    (binomial-only, p=0.70, TR=100, NSIM=2e5 — CONSERVATIVE, excludes codebook variance):
      null mean 0.1280, median 0.1300, q95 0.190.
      P(fires >=0.10 per seed under null) = 0.754; P(5/5 seeds fire) = 0.244.
      Observed 5-seed mean 0.134 vs null 0.128: z = 0.40.
      P(ranking-crossover EXISTS under null) = 0.9992 -> crossover co-claim carries ZERO evidence.
    Cell's own prereg hypothesized noise floor ~0.05 (per-point sd) — underestimates the
    EXTREME-VALUE null of the max-statistic by ~2.6x.
  H3-NULL co-claim: deep-sat mech-var exactly 0.00 5/5 — but arm is CEILING-PINNED
    (mean_acc=1.000 all mechs) -> by-construction saturation; carries no weight.
  DISPOSITION: DEMOTE math::stage1_regime_probe_8_F_ALGEBRA_moderates_CLEANUP_at_cliff_adjacent_v1
    MM_STANDARD -> MIDDLE_BAND (H1 unresolved vs extreme-value noise floor; honest downward,
    symmetric anti-negativity: demotion is itself MC-verified with a conservative null).
  REVIVAL: (a) TR>=400 (halves per-point sd; null max-stat mean drops to ~0.064, making the
    0.10 threshold meaningful); (b) PAIRED-TRIAL design (same salt/codebook/corruptions across
    mechanisms; isolates mechanism effect from instance noise); (c) permutation test on
    mech labels within F.
  SYSTEMIC FLAG (routed to Director, NOT filed as demotions here): the same extreme-value
    noise-floor concern applies to the 'ALL Stage 1 axes moderate at cliff-adjacent' family
    (Probes 1/6v2/7v2) wherever the discriminator is max-spread>=0.10 at TR=100 with
    independent salts; Probe 1 storage_x_cleanup CG_META's categorical 0/36 zeros are at
    ceiling-pinned SHARDED arms. Family sub-audit REQUIRED before further CG_META claims.

FRAMING CORRECTIONS (Fix#28, both directions):
  - Director prompt called P9v2 'N x ALGEBRA(F)' with discriminators topology_var_range_across_N /
    N_var_range_across_F / max_N_x_F_deviation: actual axis is CHAIN-DEPTH L (F=1 fixed);
    actual on-disk metrics are N_x_L_deviation_map / max_N_x_L_deviation_in_band / bucket split.
    Commits 0c5761c87/8f63ac421 are v1 (N x TOPOLOGY) lineage; v2 core is a75dccdd5.
  - Coordinator P8 message: 's7 (0.20)' — disk s7 FULL = 0.12 (0.20 was s7 SMOKE TR=40).
    's11+s17 landed' was TRUE (sync lag; files arrived mid-audit; auditor's initial
    fabrication hypothesis RETRACTED after re-check).
  - Prior P8 amendment (ledger 1355) said 'H1 survives on 2 FULL seeds' — s7 FULL had landed
    at 01:43:23Z, 53 min before that amendment (sync-lag miss); evidence base was already 3.
    Superseded by this demotion regardless.
"""
import json
import os
import time
import tempfile

MATH_ATOMS = "d:/AI/hd-instrument/data/substrate_index/math/atoms.jsonl"
META_ATOMS = "d:/AI/hd-instrument/data/substrate_index/meta/atoms.jsonl"
CERT_LEDGER = "d:/AI/hd-instrument/data/substrate_index/meta/cert_ledger.jsonl"

TS = time.time()
TS_ISO = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(TS))

P9_ANCHOR = "stage1_regime_probe_9_v2_N_x_algebra_in_band_L_over_Ncliff_v1"
P8_ANCHOR = "stage1_regime_probe_8_algebra_x_cleanup_non_saturated_v1"

atom_1_p9v2_bounded_null = {
    "id": "math::T2/MATH_STAGE1_REGIME_PROBE_9_V2_N_x_CHAIN_DEPTH_L_BOUNDED_NULL_no_reproducible_cross_term_at_BUNDLED_near_capacity_in_band_3_seed_FULL_TR100_signature_BUNDLED_modern_hopfield_M10_F1_corr0p10_Ncliff2048_N_0p5x_1x_2x_cliff_L_2_4_8_16_per_seed_max_resid_in_band_0p1108_0p2033_0p2500_exceed_binomial_null_q99_0p1158_BUT_0of12_cells_sign_consistent_at_0p10_codebook_draw_variance_dominates_4x_binomial_floor_only_stable_cells_N2048_L4_neg0p027_N2048_L8_pos0p062_below_threshold_MM_STANDARD_2026-07-04",
    "name": "MATH Probe 9 v2 BOUNDED_NULL: no reproducible N x chain-depth-L cross-term at BUNDLED near-capacity in-band (3-seed FULL; per-seed firings are codebook-draw variance; 0/12 cells sign-consistent at 0.10)",
    "corpus": "math",
    "tier": "T2",
    "kind": "experiment_record_bounded_null_cross_term",
    "description": (
        "BOUNDED_NULL, MM_STANDARD. First NON-MECHANISM pair probe with genuine in-band multi-seed "
        "data in the stage1 REGIME MAP arc. Signature (exact): STORAGE=BUNDLED, MECH=modern_hopfield, "
        "M=10, F=1, corr=0.10, N_cliff=2048; N in {1024,2048,4096} (0.5x/1x/2x N_cliff), "
        "L in {2,4,8,16}, TR=100, seeds {7,13,19}, band [0.30,0.95]. "
        "IN-BAND GENUINENESS (resolves 2026-07-04 drill HOLD): 9/7/8 of 12 grid cells in-band per "
        "seed — NOT saturation-vacuous, unlike P5/P6v2/P7v2 MB triples. "
        "PER-SEED: max|additive-model residual|_in_band = 0.1108/0.2033/0.2500; H1_ALT (>=0.10) "
        "fires 3/3; H1 clean pressure-bucket separation fails 3/3; per-seed verdicts MIDDLE_BAND "
        "H1_ALT_DIFFUSE_CROSS_TERM. Recompute off raw phase_map accs matches disk <5e-4 all cells. "
        "CROSS-SEED AUDIT OVERTURNS the per-seed diffuse-cross-term reading: 0/12 cells "
        "sign-consistent at |dev|>=0.10 — every large deviation flips sign across seeds. Only "
        "sign-consistent cells: N2048_L4 (mean -0.027) and N2048_L8 (mean +0.062), both below "
        "threshold. Max |cross-seed mean dev| = 0.120 (N2048_L16, t=1.42, n.s., 2 dof). "
        "MECHANISM ATTRIBUTION: MC binomial-only null gives max|resid| q99=0.116, so s13/s19 "
        "firings (0.20/0.25, p<1e-5) are REAL excess variance — but per-cell cross-seed sd "
        "0.11-0.19 is ~4x the binomial residual floor (0.035) and the cell uses per-point salts "
        "(independent codebook per grid cell): the excess is CODEBOOK-DRAW variance, not stable "
        "N x L structure. COROLLARY: single-seed MIDDLE_BAND cross-term verdicts in this regime "
        "are unreliable; require sign-consistency across >=3 seeds. "
        "CONTROL CAVEAT: H3 deep-sat null control fired 3/3 — TEST-DESIGN failure of the control "
        "only (DEEP_SAT N=8192 M=100 corr=0.60 sits at FLOOR mean_acc 0.07-0.105 with L_spread "
        "0.13-0.20 from L=2 partial signal, not intended ceiling degeneracy). Does not contaminate "
        "the main grid; caps tier below CG. "
        "REVIVAL CRITERIA: (a) targeted TR>=400 multi-seed rerun of the N=N_cliff row — N2048_L8 "
        "shows small stable +0.062 (t~5.9, 2 dof); (b) higher-corr re-spec (corr is the "
        "cliff-escape axis per Probe 16 SHARDED-cliff atom); (c) redesigned deep-sat control. "
        "REGIME-MAP COMPOSITION RULE (what this contributes): at BUNDLED near-capacity in-band, "
        "N (scale) and L (chain depth) compose ADDITIVELY to within 0.10-0.12 resolution — "
        "no cross-term needed in the phase map at this signature; method-contingent bound "
        "(TR=100, 3 seeds). Cross-arc overlap check: NONE at cosine>0.30 (novel)."
    ),
    "aliases": [],
    "metadata": {
        "record_class": "experiment",
        "term_class": "STAGE1_REGIME_MAP_PROBE9_V2_N_x_CHAIN_DEPTH_L_BOUNDED_NULL",
        "cert_status": "measured_mechanism_bounded_null",
        "cert_class": "MM_STANDARD_BOUNDED_NULL_cross_seed_sign_audit_overturns_per_seed_H1_ALT",
        "cert_ts": TS_ISO,
        "verified_off_data": True,
        "atomized_by": "skunkworks_landed_VET_2026-07-04_P9v2_P8_batch",
        "raw_metrics_paths": [
            f"data/exp_{P9_ANCHOR}_s7/metrics.json",
            f"data/exp_{P9_ANCHOR}_s13/metrics.json",
            f"data/exp_{P9_ANCHOR}_s19/metrics.json",
        ],
        "cell_source_path": "experiments/_stage1_regime_probe_9_v2_N_x_algebra_in_band_L_over_Ncliff_v1_core.py",
        "commit_hash_core": "a75dccdd5",
        "commit_hash_v1_lineage": ["0c5761c87", "8f63ac421"],
        "n_seeds": 3,
        "seeds": [7, 13, 19],
        "regime_signature": {"STORAGE": "BUNDLED", "MECH": "modern_hopfield", "M": 10, "F": 1,
                             "corr": 0.10, "N_cliff": 2048, "N_grid": [1024, 2048, 4096],
                             "L_grid": [2, 4, 8, 16], "TR": 100, "band": [0.30, 0.95]},
        "n_in_band_cells_per_seed": {"7": 9, "13": 7, "19": 8},
        "per_seed_max_resid_in_band": {"7": 0.1108, "13": 0.2033, "19": 0.2500},
        "mc_null_binomial_only": {"mean": 0.0627, "q95": 0.0975, "q99": 0.1158,
                                  "p_ge_0p1108": 0.016, "p_ge_0p2033": "<1e-5"},
        "sign_consistent_cells_of_12": 2,
        "sign_consistent_cells": {"N2048_L4": -0.027, "N2048_L8": 0.062},
        "max_abs_cross_seed_mean_dev": {"cell": "N2048_L16", "value": 0.120, "t": 1.42, "significant": False},
        "per_cell_cross_seed_sd_range": [0.11, 0.19],
        "binomial_residual_noise_floor": 0.035,
        "h3_deep_sat_control": "FIRED 3/3 — TEST_DESIGN failure of control (floor-pinned, not ceiling); main grid uncontaminated",
        "positive_control_pass_all_seeds": True,
        "cardinality_ok_all_seeds": True,
        "hash_distinctness": "51/51 codebook+output hashes distinct across 3 seeds",
        "auditor_framing_correction": "per-seed H1_ALT_DIFFUSE_CROSS_TERM overturned by cross-seed sign audit; Director prompt's 'N x ALGEBRA(F)' corrected to N x chain-depth-L (F=1 fixed)",
        "revival_criteria": ["TR>=400 targeted N=N_cliff row (N2048_L8 +0.062 hint)",
                             "higher-corr re-spec per 2026-07-04 drill (corr is escape axis)",
                             "redesigned deep-sat control"],
        "composes_with_atoms": [
            "stage1_regime_probe_10_storage_x_algebra_non_saturated_v1 (P10 weak 0.075 cross-term context)",
            "META_cross_term_measurement_requires_both_arms_in_band_probe10_v1 (meta #43)",
            "notes/research_drill_saturation_vacuous_MB_4triples_revival_2026-07-04.md (drill HOLD resolved)",
        ],
        "cross_arc_overlap_check_2026_07_01_USER_locked": "CLEAN — substrate_query top hit cosine 0.298 wordnet noise; NONE relevant >0.30; novel",
        "cert_increment_delta": 1
    }
}

atom_2_p8_demotion = {
    "id": "math::AMEND2_DEMOTE_stage1_regime_probe_8_F_ALGEBRA_moderates_CLEANUP_at_cliff_adjacent_v1_MM_STANDARD_to_MIDDLE_BAND_5_FULL_seed_H1_statistic_indistinguishable_from_binomial_only_extreme_value_null_MC_z_0p40_observed_per_seed_0p12_0p16_0p10_0p15_0p14_mean_0p134_vs_null_mean_0p128_P_fire_per_seed_under_null_0p754_P_5of5_0p244_crossover_exists_under_null_p_0p9992_independent_salts_per_F_mech_point_no_paired_trials_cv_0p1797_over_0p15_CG_promotion_DENIED_H3_deep_sat_zero_var_ceiling_pinned_by_construction_2026-07-04",
    "name": "MATH Probe 8 DEMOTION: F-moderates-CLEANUP at cliff-adjacent MM_STANDARD -> MIDDLE_BAND (5-FULL-seed H1 stat z=0.40 vs conservative binomial-only extreme-value null; CG_META promotion DENIED)",
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record_demotion_amendment",
    "description": (
        "DEMOTES math::stage1_regime_probe_8_F_ALGEBRA_moderates_CLEANUP_at_cliff_adjacent_v1 "
        "(MM_STANDARD, ledger 2026-07-03T23:55Z; amendment 2026-07-04T02:36Z) to MIDDLE_BAND — "
        "honest downward correction, symmetric anti-negativity (demotion itself MC-verified). "
        "EVIDENCE BASE NOW 5 FULL seeds (s11/s17 landed 2026-07-04T02:47Z, verified genuine: "
        "run_mode=full, HARD_PASS, cardinality_ok 25/25, PC pass, 15/15 cliff cells in-band; "
        "arrived via sync mid-audit — auditor's initial fabrication hypothesis RETRACTED). "
        "Cliff regime (exact): N=512, M=6400, corr=0.85, L=2, SHARDED, F in {1,2,4,8,16}, "
        "mechs {modern_hopfield, iterative_cosine, soft_energy_attractor}, TR=100. "
        "Recomputed max_per_F_mech_variance_in_band: s7=0.12 s11=0.16 s13=0.10 s17=0.15 s19=0.14 "
        "(mean 0.1340, sd 0.0241, cv 0.1797 > 0.15 -> CG_META promotion DENIED on stated bar). "
        "LOAD-BEARING DEMOTION FINDING (extreme-value noise floor): cell evaluates each (F, mech) "
        "point with an INDEPENDENT salt — mechanisms are compared across different codebooks AND "
        "different trials (no pairing). The H1 statistic (max over 5 F of range of 3 accs) under "
        "a CONSERVATIVE binomial-only null (p=0.70, TR=100; excludes codebook variance which "
        "would widen it): null mean 0.1280, q95 0.190; P(fires>=0.10 per seed)=0.754; "
        "P(5/5 seeds fire)=0.244; observed 5-seed mean 0.134 -> z=0.40 vs null. The prereg's "
        "hypothesized noise floor (~0.05 per-point sd) underestimates the max-statistic null by "
        "~2.6x. mech_ranking_crossover EXISTS fires under null with p=0.9992 (zero evidence); "
        "consistent with the specific ranking pattern failing to reproduce in any pair of the 5 "
        "seeds (s7 SEA-dominant / s11 MH-IC / s13 mixed / s17 SEA->MH / s19 IC-MH). "
        "H3-NULL co-claim (deep-sat mech-var exactly 0.00, 5/5): arm is CEILING-PINNED "
        "(mean_acc=1.000 all mechs) — by-construction saturation, carries no weight. "
        "NET: 'F moderates CLEANUP_MECHANISM at cliff-adjacent' is UNRESOLVED, not proven and "
        "not disproven — MIDDLE_BAND. Also removes P8 from the 'ALL Stage 1 axes moderate at "
        "cliff-adjacent' composition claim until re-established. "
        "REVIVAL CRITERIA: (a) TR>=400 rerun (null max-stat mean drops to ~0.064, making the "
        "0.10 threshold meaningful); (b) PAIRED-TRIAL design — same salt/codebook/corruption "
        "instances across mechanisms; (c) permutation test on mechanism labels within F. "
        "SYSTEMIC FLAG (routed to Director; NOT actioned in this batch): same audit applies to "
        "Probes 1/6v2/7v2 'axis moderates at cliff' family wherever discriminator is "
        "max-spread>=0.10 at TR=100 with independent salts; Probe 1 storage_x_cleanup CG_META "
        "categorical zeros are at ceiling-pinned arms — family sub-audit required."
    ),
    "aliases": [],
    "metadata": {
        "record_class": "experiment_amendment_demotion",
        "term_class": "STAGE1_REGIME_MAP_PROBE8_F_x_CLEANUP_DEMOTION_EXTREME_VALUE_NOISE_FLOOR",
        "cert_status": "middle_band_unresolved_vs_noise_floor",
        "cert_class": "DEMOTE_MM_STANDARD_to_MIDDLE_BAND_extreme_value_null_audit",
        "cert_ts": TS_ISO,
        "verified_off_data": True,
        "atomized_by": "skunkworks_landed_VET_2026-07-04_P9v2_P8_batch",
        "amends_atom": "math::stage1_regime_probe_8_F_ALGEBRA_moderates_CLEANUP_at_cliff_adjacent_v1",
        "supersedes_amendment": "math::AMEND_stage1_regime_probe_8_..._2026-07-04 (ledger 1355; its '2 FULL seeds only' reading superseded — s7 FULL had landed 01:43:23Z)",
        "raw_metrics_paths": [f"data/exp_{P8_ANCHOR}_s{s}/metrics.json" for s in [7, 11, 13, 17, 19]],
        "cell_source_path": "experiments/_stage1_regime_probe_8_algebra_x_cleanup_non_saturated_v1_core.py",
        "commit_hash_wrappers": "b1b7f1253",
        "n_seeds_full": 5,
        "seeds": [7, 11, 13, 17, 19],
        "cliff_regime_signature": {"N": 512, "M": 6400, "corr": 0.85, "L": 2, "storage": "SHARDED",
                                   "F_grid": [1, 2, 4, 8, 16], "TR": 100},
        "per_seed_max_per_F_mech_variance_in_band": {"7": 0.12, "11": 0.16, "13": 0.10, "17": 0.15, "19": 0.14},
        "cross_seed_cv": 0.1797,
        "cg_bar": 0.15,
        "mc_null_binomial_only": {"mean": 0.1280, "median": 0.1300, "q95": 0.190,
                                  "p_fire_per_seed": 0.754, "p_5of5_fire": 0.244,
                                  "z_observed_5seed_mean": 0.40,
                                  "p_crossover_exists_under_null": 0.9992},
        "salt_structure": "independent salt per (F, mech) point — no trial pairing across mechanisms",
        "h3_null_co_claim": "deep-sat zero variance is ceiling-pinned (acc=1.000 all mechs) — by-construction, no weight",
        "framing_corrections": [
            "coordinator 's7 (0.20)' is s7 SMOKE TR=40 value; s7 FULL = 0.12",
            "s11/s17 'not on disk' initial read RETRACTED — sync lag, files landed mid-audit and verify genuine",
        ],
        "revival_criteria": ["TR>=400 rerun", "paired-trial design (shared salts across mechs)",
                             "permutation test on mech labels"],
        "systemic_flag": "extreme-value noise-floor audit required for Probes 1/6v2/7v2 cliff-moderation family incl. Probe 1 storage_x_cleanup CG_META (ceiling-pinned zeros)",
        "cert_increment_delta": -1
    }
}

atom_3_meta_45b = {
    "id": "meta::T4/META_45b_pre_classified_axis_short_circuit_applies_ONLY_when_DESIGN_POINT_sits_in_degenerate_regime_not_when_axis_merely_carries_REGIME_NARROW_or_ceiling_label_somewhere_carve_out_case_study_P9v2_crosses_N_cliff_2048_at_0p5x_1x_2x_yet_7_to_9_of_12_cells_in_band_all_3_FULL_seeds_because_M10_corr0p10_tuned_band_open_vs_P5_P6v2_P7v2_saturation_vacuous_where_design_points_degenerate_MM_TENTATIVE_2026-07-04",
    "name": "META #45b: pre-classified-axis short-circuit applies ONLY when the DESIGN POINT sits in the degenerate regime (P9v2 carve-out; MM_TENTATIVE)",
    "corpus": "meta",
    "tier": "T4",
    "kind": "methodology_rule",
    "description": (
        "Refines meta #45 (skip cross-term FULLs when an axis carries a REGIME_NARROW/ceiling "
        "classification). RULE: the short-circuit fires ONLY when the DESIGN POINT itself sits in "
        "the degenerate regime — evaluate the planned grid cells against the measured phase map "
        "(predicted acc inside [0.30,0.95]?), NOT the axis label. An axis with a cliff/ceiling "
        "label somewhere can still support genuine in-band cross-term designs when other knobs "
        "(M, corr) are tuned to keep the band open. "
        "CASE STUDY FOR (carve-out): Probe 9 v2 deliberately crosses N_cliff=2048 with N at "
        "0.5x/1x/2x cliff, yet lands 9/7/8 of 12 cells in-band in all 3 FULL seeds because "
        "M=10, corr=0.10 keep accuracy mid-band. A label-based short-circuit would have wrongly "
        "skipped a genuine (and atomized BOUNDED_NULL) measurement. "
        "CASE STUDIES AGAINST label-only (base rule #45 still correct there): P5/P6v2/P7v2 MB "
        "triples were saturation-vacuous because their DESIGN POINTS sat in degenerate arms "
        "(SHARDED ceiling-pinned; CLEANUP regime-narrow) — 2026-07-04 drill SKIP stands. "
        "PROMOTION CRITERION: MM_TENTATIVE -> MM_STANDARD after 2 more cases where the "
        "design-point check and the axis-label check disagree and disk data confirms the "
        "design-point call."
    ),
    "aliases": ["meta_45b_design_point_carve_out"],
    "metadata": {
        "verified_off_data": True,
        "verified_ts": TS_ISO,
        "verifier": "hdi_skunkworks",
        "cert_status": "mm_tentative_methodology_rule",
        "cert_class": "MM_TENTATIVE_META_RULE_45b_design_point_carve_out",
        "case_study_for": f"data/exp_{P9_ANCHOR}_s{{7,13,19}}/metrics.json (9/7/8 of 12 in-band)",
        "case_studies_against_label_only": "P5/P6v2/P7v2 saturation-vacuous MB triples (2026-07-04 drill)",
        "drill_note": "notes/research_drill_saturation_vacuous_MB_4triples_revival_2026-07-04.md",
        "promotion_criterion": "2 more design-point-vs-label disagreements confirmed on disk",
        "cert_increment_delta": 1
    }
}

atom_4_meta_extreme_value = {
    "id": "meta::T4/META_extreme_value_discriminator_thresholds_must_be_calibrated_against_max_statistic_null_MC_or_analytic_not_per_point_sd_case_study_P8_prereg_hypothesized_floor_0p05_actual_null_mean_of_max_over_5F_range_of_3_iid_accs_TR100_is_0p128_2p6x_underestimate_H1_fired_5of5_seeds_with_p_0p244_under_null_crossover_exists_fires_under_null_p_0p9992_applies_when_arms_use_independent_salts_no_trial_pairing_MM_TENTATIVE_2026-07-04",
    "name": "META: extreme-value discriminator thresholds must be calibrated against the max-statistic null (MC/analytic), not per-point sd (P8 case study; MM_TENTATIVE)",
    "corpus": "meta",
    "tier": "T4",
    "kind": "methodology_rule",
    "description": (
        "RULE: when a pre-reg discriminator gates on an EXTREME-VALUE statistic (max over grid "
        "cells of a spread/range/|residual|), the H1 threshold must be calibrated against the "
        "null distribution of THAT max-statistic (Monte Carlo or analytic extreme-value "
        "calculation), not against the per-point sd. Per-point sd underestimates the max-statistic "
        "null by the extreme-value inflation factor (~2-3x for 15-point grids). This matters "
        "doubly when compared arms use INDEPENDENT salts (different codebooks AND trials per arm "
        "— no pairing), which adds instance variance on top of trial noise. "
        "CASE STUDY: Probe 8 prereg hypothesized noise floor ~0.05 and set H1 at 0.10; the "
        "actual binomial-only null of its statistic (max over 5 F of range of 3 iid accs, TR=100, "
        "p~0.70) has mean 0.128 — H1 fired 5/5 FULL seeds with P(5/5|null)=0.244, and the "
        "crossover-exists co-discriminator fires under null with p=0.9992. Result: MM_STANDARD "
        "atom demoted to MIDDLE_BAND (see paired demotion atom this batch). "
        "SCHEMA-VET CHECKLIST ADDITION: (1) identify max-statistics in discriminators; "
        "(2) require MC null (or paired-trial design) in prereg; (3) prefer PAIRED trials "
        "(shared salt/codebook/corruption across compared arms) — pairing removes instance "
        "variance and typically tightens the null by >2x for free. "
        "RELATED: P9v2 escaped this failure mode because its per-seed firings (0.20/0.25) exceed "
        "even the extreme-value null q99 (0.116) — the audit then correctly attributed excess to "
        "codebook variance via cross-seed sign test. The sign-consistency-across-seeds test is "
        "the complementary tool when the max-statistic null IS exceeded. "
        "PROMOTION: MM_TENTATIVE -> MM_STANDARD after 2 more independent catches; -> CG_META when "
        "integrated into SCHEMA-VET as a hard gate."
    ),
    "aliases": ["meta_extreme_value_noise_floor_calibration"],
    "metadata": {
        "verified_off_data": True,
        "verified_ts": TS_ISO,
        "verifier": "hdi_skunkworks",
        "cert_status": "mm_tentative_methodology_rule",
        "cert_class": "MM_TENTATIVE_META_RULE_extreme_value_null_calibration",
        "case_study": f"data/exp_{P8_ANCHOR}_s{{7,11,13,17,19}}/metrics.json",
        "mc_evidence": {"null_mean": 0.1280, "prereg_assumed_floor": 0.05, "underestimate_factor": 2.6,
                        "p_5of5_fire_under_null": 0.244, "p_crossover_under_null": 0.9992},
        "promotion_criterion": "2 more independent catches -> MM_STANDARD; SCHEMA-VET hard gate -> CG_META",
        "cert_increment_delta": 1
    }
}


def a5_append(path, atom):
    d = os.path.dirname(path)
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_atoms_", suffix=".jsonl")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as src:
                    for line in src:
                        f.write(line)
            f.write(json.dumps(atom, ensure_ascii=False) + "\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    n_lines = 0
    found = False
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            n_lines += 1
            if atom["id"] in line:
                found = True
    if not found:
        raise RuntimeError(f"verify-load failed: atom id not found in {path}")
    return n_lines


def ledger_append(atom, session_tag, extra=None, ledger_path=CERT_LEDGER):
    entry = {
        "ts": TS,
        "ts_iso": TS_ISO,
        "atom_id": atom["id"],
        "corpus": atom["corpus"],
        "cert_status": atom["metadata"].get("cert_status"),
        "cert_class": atom["metadata"].get("cert_class"),
        "cert_increment_delta": atom["metadata"].get("cert_increment_delta", 0),
        "verified_off_data": True,
        "atomized_by": "skunkworks_landed_VET_2026-07-04_P9v2_P8_batch",
        "landed_VET_session": session_tag,
    }
    if extra:
        entry.update(extra)
    d = os.path.dirname(ledger_path)
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_ledger_", suffix=".jsonl")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            if os.path.exists(ledger_path):
                with open(ledger_path, "r", encoding="utf-8") as src:
                    for line in src:
                        f.write(line)
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, ledger_path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


if __name__ == "__main__":
    print(f"[atomize] ts_iso={TS_ISO}")
    tag = "2026-07-04_P9v2_bounded_null_P8_noise_floor_demote_meta45b_meta_extreme_value"

    n = a5_append(MATH_ATOMS, atom_1_p9v2_bounded_null)
    print(f"[atomize] (1) math P9v2 BOUNDED_NULL MM_STANDARD appended; math lines={n}")
    ledger_append(atom_1_p9v2_bounded_null, tag)

    n = a5_append(MATH_ATOMS, atom_2_p8_demotion)
    print(f"[atomize] (2) math P8 DEMOTION MM_STANDARD->MIDDLE_BAND appended; math lines={n}")
    ledger_append(atom_2_p8_demotion, tag,
                  extra={"amends_atom": atom_2_p8_demotion["metadata"]["amends_atom"],
                         "action": "DEMOTE"})

    n = a5_append(META_ATOMS, atom_3_meta_45b)
    print(f"[atomize] (3) meta #45b design-point carve-out MM_TENTATIVE appended; meta lines={n}")
    ledger_append(atom_3_meta_45b, tag)

    n = a5_append(META_ATOMS, atom_4_meta_extreme_value)
    print(f"[atomize] (4) meta extreme-value null calibration MM_TENTATIVE appended; meta lines={n}")
    ledger_append(atom_4_meta_extreme_value, tag)

    print("[atomize] DONE 4 atoms + 4 ledger entries; A5-gated (tmp+os.replace+verify-load); matching TS_ISO")
    print("[atomize] net cert delta: MM +2 (P9v2 +1, meta45b +1, meta-EV +1, P8 demote -1)")
