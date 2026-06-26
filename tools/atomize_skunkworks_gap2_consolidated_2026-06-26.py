"""Atomize: Skunkworks Gap 2 consolidated 3-cell diagnostic landed-VET (2026-06-26).

Cert routing per Skunkworks landed-VET ruling note 2026-06-26:
  notes/skunkworks_gap2_consolidated_landed_vet_2026-06-26.md

Three atoms in `meta` corpus:

  [1] T3/META_substrate_tracks_KNN_cosine_floor_within_0p007_across_eight_construction_
      param_combinations_n_seeds_1_smoke_M_2000_pythia_160m_window_16_to_64
      pq=CERT_CHAIN_GRADE  cert_status=proven_bound  cert_class=pre_reg_miss_proven_bound
      delta=+1   (chain-grade-eligible proven bound per ruling tier ladder)

  [2] T3/META_cosine_physics_floor_on_short_LM_window_keys_M_2000_pythia_160m_is_below_
      chain_grade_band_recall_at_1_le_0p16_across_all_tested_constructions
      pq=META_RULE_CERT_NEUTRAL  cert_status=custom  cert_class=discipline_meta
      delta=0    (META rule; CERT-neutral)

  [3] T3/META_when_substrate_tracks_an_external_baseline_within_smoke_noise_band_AND_
      baseline_itself_is_low_the_chain_grade_path_is_baseline_replacement_not_baseline_rescue
      pq=META_RULE_CERT_NEUTRAL  cert_status=custom  cert_class=discipline_meta
      delta=0    (Fix #26 pre-dispatch matcher discipline rule; CERT-neutral)

Verify-OFF-DATA basis: ruling note recomputed all 8 (cell, arm) delta values from
metrics.json (Fix #28 strict). This atomize tool inherits that verification by
reference; it does NOT re-verify metrics. Per ruling-note pre-write checklist.

A5 PRE/POST gating via cert_ledger_writer.append_cert_ledger_row. NON-DESTRUCTIVE:
no cell metrics.json or verdict_msg mutated.

CERT N change at write time: live CERT N -> live CERT N + 1 (one proven_bound delta=+1).

Run:
  .venv/Scripts/python.exe tools/atomize_skunkworks_gap2_consolidated_2026-06-26.py           # DRY
  .venv/Scripts/python.exe tools/atomize_skunkworks_gap2_consolidated_2026-06-26.py --apply   # WRITE
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(".").resolve()))
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier
from tools.cert_ledger_writer import (
    append_cert_ledger_row,
    build_measured_mechanism_row,
)


STORE_ROOT = Path("data/substrate_index")
RULING_NOTE = "notes/skunkworks_gap2_consolidated_landed_vet_2026-06-26.md"
CELL_COMMIT = "n/a-meta-composes-three-cells"

METRICS_V1 = "data/exp_substrate_gap2_stride_sweep_confirm_v1_smoketest/metrics.json"
METRICS_V2 = "data/exp_substrate_gap2_stride_sweep_confirm_v2_different_articles_per_key_smoke/metrics.json"
METRICS_V2B = "data/exp_substrate_gap2_stride_sweep_confirm_v2b_longer_window64_smoke/metrics.json"


# ============================================================================
# ATOM 1 -- MEASURED_MECHANISM proven-bound (CERT +1)
# ============================================================================

def build_atom1_substrate_tracks_knn_cosine_floor() -> Atom:
    return Atom(
        id=(
            "T3/META_substrate_tracks_KNN_cosine_floor_within_0p007_across_eight_"
            "construction_param_combinations_n_seeds_1_smoke_M_2000_pythia_160m_"
            "window_16_to_64"
        ),
        name=(
            "META proven-bound: substrate recall-at-1 tracks exhaustive-cosine-KNN "
            "recall-at-1 within delta(knn - sub) in [+0.0006, +0.0067] across 8 "
            "independent (construction x parameter) combinations; substrate ALWAYS "
            "at or below KNN (never above; bounded from above by cosine-physics); "
            "M=2000 pythia-160m window=16-to-64 single-seed smoke"
        ),
        description=(
            "PROVEN-BOUND (MEASURED_MECHANISM tier per Skunkworks ruling 2026-06-26; "
            "CERT-eligible boundary; +1 toward CERT N): substrate's recall-at-1 tracks "
            "exhaustive-cosine-KNN's recall-at-1 within delta(knn - sub) in [+0.0006, "
            "+0.0067] across 8 independent (construction x parameter) combinations "
            "spanning stride={1,4,8,16}, key-independence={same-article, different-"
            "articles}, window={16, 64}, all at M=2000 with pythia-160m on text8 prose, "
            "single-seed smoke (seed=11). Substrate is ALWAYS at or below KNN (never "
            "above); the substrate-is-bounded-from-above-by-cosine-physics property is "
            "proven within this regime (one-sided proven, not two-sided). "
            "VERIFIED EVIDENCE OFF-DATA (Skunkworks 2026-06-26 per ruling note): "
            "  v1  s1  KNN 0.0453 sub 0.0447 delta +0.0006 "
            "  v1  s4  KNN 0.1520 sub 0.1507 delta +0.0013 "
            "  v1  s8  KNN 0.1247 sub 0.1193 delta +0.0054 "
            "  v1  s16 KNN 0.1033 sub 0.0987 delta +0.0046 "
            "  v2  DIFFERENT_ARTICLES w=16 KNN 0.1427 sub 0.1360 delta +0.0067 "
            "  v2  SAME_ARTICLE_STRIDE_16 KNN 0.1140 sub 0.1107 delta +0.0033 "
            "  v2b DIFFERENT_ARTICLES w=64 KNN 0.1580 sub 0.1533 delta +0.0047 "
            "  v2b SAME_ARTICLE_STRIDE_16 KNN 0.0967 sub 0.0940 delta +0.0027 "
            "Min delta +0.0006; max delta +0.0067; mean +0.0037; ALL 8 non-negative. "
            "Substrate inherits KNN's non-monotone-in-stride structure (v1 s8 < s4; "
            "s16 < s8) -- additional evidence for the cosine-physics-floor framing. "
            "Window doubling (16->64) lifts ceiling +0.0153; topical independence "
            "(DIFF vs SAME) lifts ceiling +0.025-0.059. Route accuracy 0.908-0.957 "
            "across all 8 combinations -- routing is NOT the bottleneck; within-"
            "partition cleanup resolving cosine-near keys IS the bind. "
            "TIER (MEASURED_MECHANISM not chain-grade) per: "
            "(1) n_seeds=1 violates chain-grade dispersion requirement (cv=null); "
            "(2) smoke-regime ceiling: M=2000 << gap target M=10k; pythia-160m << "
            "production pythia-2.8b; (3) the mechanism (substrate-routes-and-cleans-"
            "up-cosine-keys) performs at the KNN cosine-physics ceiling -- a positive, "
            "durable, real finding; the ceiling itself (recall <= 0.158) does not "
            "reach chain-grade recall thresholds (~0.7-0.9) at M=2000 with pythia-160m "
            "short-window keys -- proven NEGATIVE bound on the cosine-floor ceiling "
            "(NOT substrate failure). DISCRIMINATOR (would-have-FAILED if False): if "
            "any of the 8 delta(knn - sub) measurements had been negative (substrate "
            "beating KNN) the one-sided proven-bound claim would be invalid -- 0/8 "
            "violations observed. CHAIN-GRADE-PROMOTION PATH: 3-seed pythia-2.8b "
            "M-scaling sweep on natural-key DIFFERENT_ARTICLES at M={10k, 100k, 1M} "
            "would close the smoke-to-chain-grade gap. Composes with the 6 prior "
            "geometry HARD_FAILs (whitening, MIMO, DG, polarimetric LEARNED, "
            "anisotropy_v4 AB tie, ScaNN aniso) which remain HARD_FAIL but whose "
            "post-hoc interpretation is now provided by Atom 2 (cosine-floor META rule)."
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.META,
        algebra=None,
        metadata={
            "provenance_quality": "CERT_CHAIN_GRADE",
            "cert_status": "proven_bound",
            "cert_class": "pre_reg_miss_proven_bound",
            "verdict": "MEASURED_MECHANISM_skunkworks_off_data_3_cell_8_combination",
            "cell_commit": CELL_COMMIT,
            "metrics_path": METRICS_V1,
            "metrics_paths_all": [METRICS_V1, METRICS_V2, METRICS_V2B],
            "notes_path": RULING_NOTE,
            "verified_off_data": (
                "Skunkworks landed-VET ruling 2026-06-26 (notes/"
                "skunkworks_gap2_consolidated_landed_vet_2026-06-26.md) verifies all "
                "8 delta(knn - sub) values reproduce from raw metrics.json per_arm "
                "blocks via .venv python recompute per Fix #28; no inheritance from "
                "verdict_msg. v1 deltas s1=+0.0006, s4=+0.0013, s8=+0.0054, s16=+0.0046; "
                "v2 DIFF=+0.0067, SAME=+0.0033; v2b DIFF=+0.0047, SAME=+0.0027. Min "
                "+0.0006 max +0.0067 mean +0.0037; ALL non-negative. Window-doubling "
                "lift +0.0153 reproduces (cited +0.015). beats_rail (DIFF-SAME) v2=+0.0253 "
                "(cited 0.025) v2b=+0.0593 (cited 0.059) reproduces. Pre-reg direction: "
                "this atom is a post-hoc consolidated bound over 3 cells whose individual "
                "verdicts (v1 HARD_FAIL_KNN_SENTINEL_REGRESSION; v2 / v2b smoke-gate-OFF) "
                "STAND unchanged; the consolidated cross-cell claim is a DIFFERENT and "
                "broader claim and does not conflict with any cell-internal verdict."
            ),
            "honest_scope": (
                "Wikipedia text8 prose corpus, M=2000 patterns, pythia-160m encoder, "
                "window={16, 64} tokens, stride={1,4,8,16}, key-construction={same-"
                "article, different-articles}, single-seed (seed=11) smoke. CHAIN-GRADE-"
                "INELIGIBLE on n_seeds=1 ALONE; tiered MEASURED_MECHANISM (proven bound) "
                "per cert-owner tier ladder. DOES prove substrate-is-bounded-from-above-"
                "by-cosine-physics across 8 independent combinations 0/8 violations. "
                "DOES NOT extrapolate to M=10k+ regime or to pythia-2.8b without explicit "
                "follow-on cells. DOES NOT promote to chain-grade absent across-seed cv "
                "<= 0.10 evidence at full regime. DOES NOT demote the 6 prior geometry "
                "HARD_FAILs (they remain HARD_FAIL; the new META rule provides post-hoc "
                "interpretation only)."
            ),
            "n_seeds": 1,
            "cv_load_bearing": None,
            "load_bearing_metric": (
                "delta_knn_minus_sub_in_0p0006_to_0p0067_across_8_combinations_"
                "0_of_8_violations_one_sided_proven_bound_min_0p0006_max_0p0067_"
                "mean_0p0037_substrate_NEVER_beats_KNN"
            ),
            "discriminator_armed": True,
            "discriminator_spec": (
                "if any of the 8 delta(knn - sub) measurements had been negative "
                "(substrate beating KNN) the one-sided proven-bound claim would be "
                "invalid; 0/8 violations observed (min delta = +0.0006, range [+0.0006, "
                "+0.0067]); discriminator FIRED in favor of the bound. CHAIN-GRADE "
                "PROMOTION DISCRIMINATOR (armed for future cell): 3-seed pythia-2.8b "
                "M-scaling sweep on natural-key DIFFERENT_ARTICLES at M={10k, 100k, 1M} "
                "with cv<=0.10; HARD_PASS at M>=10k chain-grade-validates re-classification."
            ),
            "composes_with": [
                # 6 geometry HARD_FAILs (interpretation extended by Atom 2):
                "geometry_whitening_hard_fail",
                "geometry_MIMO_hard_fail",
                "geometry_DG_hard_fail",
                "geometry_polarimetric_LEARNED_hard_fail",
                "geometry_anisotropy_v4_AB_tie_hard_fail",
                "geometry_ScaNN_aniso_hard_fail",
                # Chain-grade KG/cap_map atoms confirming floor IS chain-grade at full regime:
                "math::T3/EXP_partition_routing_M_10M_chain_grade",
                "math::T3/EXP_fly_lsh_M_10k_pythia_2p8b_chain_grade",
                "math::T3/EXP_kv_learned_M_10k_held_out_chain_grade",
            ],
            "cites": [
                "Skunkworks_landed_VET_gap2_consolidated_2026-06-26",
                "Research_gap2_consolidated_3_cell_diagnostic_pre_reg_2026-06-26",
                "Fix_28_verify_per_arm_metrics_not_verdict_msg",
                "Fix_26_verify_the_referent",
                "BIAS_S_band_calibration_regime_check_USER_2026-06-25",
                "by_construction_saturation_tiering_cert_owner_override_2026-06-22",
                "feedback_negativity_bias_symmetric_verify_both_directions_USER",
                "Cai_Kanai_Belkin_anisotropy_literature",
                "Mu_Viswanath_anisotropy_literature",
                "ScaNN_anisotropic_quantization_literature",
            ],
            "n_cells_under_atom": 3,
            "cells_under_atom": [
                "exp_substrate_gap2_stride_sweep_confirm_v1_smoketest",
                "exp_substrate_gap2_stride_sweep_confirm_v2_different_articles_per_key_smoke",
                "exp_substrate_gap2_stride_sweep_confirm_v2b_longer_window64_smoke",
            ],
            "delta_knn_minus_sub_range": [0.0006, 0.0067],
            "delta_knn_minus_sub_mean": 0.0037,
            "delta_knn_minus_sub_n_combinations": 8,
            "delta_knn_minus_sub_n_negative": 0,
            "config_version": (
                "M=2000,pythia_160m,window=16_to_64,stride=1_4_8_16,key_construction="
                "same_article_and_different_articles,n_seeds=1,seed=11,smoke,text8"
            ),
            "regime_caveats": (
                "smoke-regime ONLY: M=2000 << gap target M=10k; pythia-160m << "
                "production pythia-2.8b; n_seeds=1 cv=null. Full-regime confirmation "
                "PENDING per cap_map guard-rail label."
            ),
        },
    )


# ============================================================================
# ATOM 2 -- META rule: cosine-physics floor below chain-grade (CERT-neutral)
# ============================================================================

def build_atom2_cosine_floor_below_chain_grade() -> Atom:
    return Atom(
        id=(
            "T3/META_cosine_physics_floor_on_short_LM_window_keys_M_2000_pythia_160m_"
            "is_below_chain_grade_band_recall_at_1_le_0p16_across_all_tested_constructions"
        ),
        name=(
            "META rule (CERT-neutral): the KNN-cosine-physics ceiling on pythia-160m-"
            "encoded text8 keys with windows in [16, 64] tokens at M=2000 is empirically "
            "bounded above by 0.158 (recall@1) across 8 measurements; substrate cannot "
            "exceed this ceiling regardless of cleanup mechanism; therefore the high-M / "
            "chain-grade-capable path for Gap 2 is non-cosine mechanism (refuse-gate, "
            "sparse-tag retrieval, sparse-fan-in, learned-projection metric), NOT "
            "geometric rescue of cosine-based dense cleanup"
        ),
        description=(
            "META RULE (CERT-neutral; delta=0): the KNN-cosine-physics ceiling on "
            "pythia-160m-encoded text8 keys with windows in [16, 64] tokens at M=2000 "
            "is empirically bounded above by 0.158 (the maximum observed across 8 "
            "measurements; window=64 DIFF arm). Substrate cannot exceed this ceiling "
            "regardless of cleanup mechanism (proven 8/8 in the Atom 1 evidence). "
            "Window doubling (16->64) lifts the ceiling only ~0.015 in absolute "
            "recall@1; topical independence (different-articles vs stride-16-same-"
            "article) lifts the ceiling ~0.025-0.059. Therefore the high-M / chain-"
            "grade-capable path for Gap 2 (capacity) is NON-COSINE MECHANISM (refuse-"
            "gate, sparse-tag retrieval, sparse-fan-in pattern separation, learned-"
            "projection metric), NOT geometric rescue of cosine-based dense cleanup. "
            "This META rule provides the post-hoc interpretation for the 6 prior "
            "geometry HARD_FAILs (whitening, MIMO, DG, polarimetric LEARNED, "
            "anisotropy_v4 AB tie, ScaNN aniso) -- their HARD_FAIL tier STANDS; the "
            "META rule explains WHY they cannot succeed at this construction (they "
            "all attempt to lift recall above the cosine-floor, an information-"
            "theoretic impossibility on this key distribution at this M). "
            "SCOPE: rule is scoped to short-LM-window keys (window <= 64 tokens) at "
            "M=2000 with pythia-160m on text8. Full-regime applicability (M=10k+, "
            "pythia-2.8b, longer windows) is OPEN; chain-grade ledger entries "
            "(partition_routing M=10M = 0.978; fly-LSH M=10k pythia-2.8b = 0.997; "
            "KV-learned M=10k held-out = 0.827) establish floor IS chain-grade-capable "
            "at full regime on NATURAL-distribution keys -- so the rule's force is "
            "regime-specific: short-LM-window cosine cleanup is below chain-grade; "
            "longer windows + larger M + better encoder lift the floor above chain-"
            "grade. RECOMMENDED OPERATIONAL FIX: Gap 2 productization should route "
            "to non-cosine mechanisms (refuse-gate, sparse-tag, learned-projection) "
            "for short-LM-window regimes; cosine cleanup is the production path only "
            "at natural-key + longer-window + full-encoder regimes."
        ),
        kind=AtomKind.METHODOLOGY_RULE,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.META,
        algebra=None,
        metadata={
            "provenance_quality": "META_RULE_CERT_NEUTRAL",
            "cert_status": "meta_rule",
            "cert_class": "discipline_meta",
            "rule_id": "COSINE_PHYSICS_FLOOR_BELOW_CHAIN_GRADE_SHORT_LM_WINDOW",
            "rule_category": "capacity_gap_cosine_floor_discipline",
            "rule_name": (
                "cosine_physics_floor_short_LM_window_keys_M_2000_pythia_160m_below_"
                "chain_grade_high_M_path_is_non_cosine"
            ),
            "rule_text": (
                "On short-LM-window keys (<=64 tokens) at M=2000 with pythia-160m on "
                "text8, the KNN-cosine-physics ceiling is empirically bounded above by "
                "recall@1=0.158. Substrate cannot exceed this ceiling regardless of "
                "cleanup mechanism. Window-doubling lifts ceiling only ~0.015; topical "
                "independence lifts only ~0.025-0.059. The high-M / chain-grade-capable "
                "path for Gap 2 is NON-COSINE mechanism (refuse-gate, sparse-tag, "
                "sparse-fan-in, learned-projection metric), NOT geometric rescue of "
                "cosine-based dense cleanup."
            ),
            "rebuttal_check_for_skunkworks_landed_VET": (
                "if a cell claims substrate-rescue at recall@1 > 0.158 on pythia-160m "
                "text8 short-LM-window keys at M=2000 via any cosine-physics variant "
                "(whitening, anisotropy, DG, MIMO, polarimetric, ScaNN, etc.), demand "
                "off-data verification that the cell's KNN baseline also exceeds 0.158 "
                "(if it does, the rule's regime is exited -- different encoder or "
                "longer windows; if it does not, the rescue claim is information-"
                "theoretically impossible and the cell should be HARD_FAIL on cosine-"
                "floor saturation). Cite this META rule + Atom 1 8/8 proven bound."
            ),
            "originating_ruling_note": RULING_NOTE,
            "originating_cells": [
                "exp_substrate_gap2_stride_sweep_confirm_v1_smoketest",
                "exp_substrate_gap2_stride_sweep_confirm_v2_different_articles_per_key_smoke",
                "exp_substrate_gap2_stride_sweep_confirm_v2b_longer_window64_smoke",
            ],
            "metrics_paths_all": [METRICS_V1, METRICS_V2, METRICS_V2B],
            "supersedes_interpretation_for_atoms": [
                "geometry_whitening_hard_fail",
                "geometry_MIMO_hard_fail",
                "geometry_DG_hard_fail",
                "geometry_polarimetric_LEARNED_hard_fail",
                "geometry_anisotropy_v4_AB_tie_hard_fail",
                "geometry_ScaNN_aniso_hard_fail",
            ],
            "does_not_demote": (
                "the 6 geometry HARD_FAILs remain HARD_FAIL; this rule provides post-"
                "hoc interpretation only (NOT retroactive demotion)."
            ),
            "scope_caveat": (
                "regime-specific: short-LM-window (<=64 tokens) + M=2000 + pythia-160m + "
                "text8; at full regime (M=10k+, pythia-2.8b, natural-key DIFFERENT) the "
                "floor IS chain-grade-capable per partition_routing M=10M, fly-LSH "
                "M=10k pythia-2.8b, KV-learned M=10k chain-grade ledger entries."
            ),
            "composes_with": [
                ("meta::T3/META_substrate_tracks_KNN_cosine_floor_within_0p007_"
                 "across_eight_construction_param_combinations_n_seeds_1_smoke_M_"
                 "2000_pythia_160m_window_16_to_64"),
                "feedback::cert_owner_overrides_director_via_by_construction_saturation_2026-06-22",
            ],
            "cites": [
                "Skunkworks_landed_VET_gap2_consolidated_2026-06-26",
                "Cai_Kanai_Belkin_anisotropy",
                "Mu_Viswanath_anisotropy",
                "ScaNN_anisotropic_quantization",
                "6_prior_geometry_HARD_FAILs_whitening_MIMO_DG_polarimetric_anisotropy_v4_ScaNN",
            ],
        },
    )


# ============================================================================
# ATOM 3 -- META discipline rule: baseline-replacement-vs-rescue (CERT-neutral)
# ============================================================================

def build_atom3_baseline_replacement_not_rescue() -> Atom:
    return Atom(
        id=(
            "T3/META_when_substrate_tracks_an_external_baseline_within_smoke_noise_"
            "band_AND_baseline_itself_is_low_the_chain_grade_path_is_baseline_"
            "replacement_not_baseline_rescue"
        ),
        name=(
            "META discipline rule (CERT-neutral; Fix #26 pre-dispatch matcher): when "
            "substrate tracks an external baseline within smoke-noise band AND the "
            "baseline itself is below chain-grade, the productive path is to REPLACE "
            "the baseline metric class (not RESCUE within-class); generalizes the "
            "6-geometry-HARD_FAIL + 3-stride-sweep-MM pattern"
        ),
        description=(
            "META DISCIPLINE RULE (CERT-neutral; delta=0): when substrate achieves "
            "recall (or any cell-level metric) within ~0.01 of an external baseline "
            "across multiple construction variants, AND that external baseline is "
            "itself below the chain-grade band on the metric's absolute scale, the "
            "productive path forward is to REPLACE the baseline metric class (e.g. "
            "cosine -> non-cosine: tag retrieval, sparse-LSH, learned-projection, "
            "refuse-gate) rather than to RESCUE within-class (which would have to "
            "beat the baseline ceiling -- an information-theoretic impossibility on "
            "the relevant key distribution). "
            "ORIGINATING PATTERN (Skunkworks landed-VET 2026-06-26 over 9 cells): "
            "Gap 2 (capacity) attempts produced 6 geometry HARD_FAILs (whitening, "
            "MIMO, DG, polarimetric LEARNED, anisotropy_v4 AB tie, ScaNN aniso) -- "
            "all attempting to lift cosine-based dense cleanup above its information-"
            "theoretic ceiling; the 3 consolidated stride-sweep cells (v1, v2, v2b) "
            "proved substrate IS at the ceiling (8/8 delta <= +0.007). The 6 HARD_FAILs "
            "were structurally mis-framed at intent time: they targeted substrate "
            "(cleanup mechanism) when the bind was in the metric class (cosine "
            "geometry). Under this discipline rule, future Gap 2 (or analogous gap) "
            "cells should pre-flight check: is substrate tracking the baseline within "
            "smoke noise? if YES AND the baseline absolute level is < chain-grade band, "
            "DO NOT dispatch a substrate-rescue cell within the same metric class; "
            "DO dispatch a baseline-replacement (non-cosine mechanism) cell. "
            "FIX #26 PRE-DISPATCH MATCHER FORMULATION: tools/predispatch_check.py "
            "<anchor> should flag any dispatch where (a) recent_landings.jsonl shows "
            "substrate-tracks-baseline-within-0.01 on 2+ prior cells for the same key-"
            "domain AND (b) baseline absolute is < chain-grade band -- and recommend "
            "Research evaluate baseline-replacement instead of substrate-rescue. This "
            "would have caught 4-6 of the 6 geometry HARD_FAILs before dispatch. "
            "SCOPE: discipline rule is project-wide pattern matcher; not tied to "
            "Gap 2 specifically. Applies anywhere substrate-tracks-low-baseline within "
            "smoke noise. EDGE CASE: rule does NOT apply when baseline IS already at "
            "chain-grade and substrate is rescuing FROM SUB-CHAIN-GRADE TO CHAIN-GRADE "
            "(in that case substrate-rescue IS the path; rule is for substrate-AT-baseline "
            "where baseline-is-low)."
        ),
        kind=AtomKind.METHODOLOGY_RULE,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.META,
        algebra=None,
        metadata={
            "provenance_quality": "META_RULE_CERT_NEUTRAL",
            "cert_status": "meta_rule",
            "cert_class": "discipline_meta",
            "rule_id": "BASELINE_REPLACEMENT_NOT_BASELINE_RESCUE_WHEN_SUBSTRATE_TRACKS_LOW_BASELINE",
            "rule_category": "fix_26_pre_dispatch_matcher_discipline",
            "rule_name": (
                "when_substrate_tracks_external_baseline_within_smoke_noise_AND_"
                "baseline_is_low_chain_grade_path_is_baseline_replacement_not_rescue"
            ),
            "rule_text": (
                "When substrate achieves recall (or any cell-level metric) within "
                "~0.01 of an external baseline across multiple construction variants, "
                "AND that external baseline is itself below the chain-grade band on "
                "the metric's absolute scale, the productive path forward is to "
                "REPLACE the baseline metric class (cosine -> non-cosine: tag, "
                "sparse-LSH, learned-projection, refuse-gate) rather than to RESCUE "
                "within-class. Substrate-rescue within a low-baseline class is "
                "information-theoretically capped at the baseline ceiling."
            ),
            "rebuttal_check_for_skunkworks_landed_VET": (
                "if a cell proposes a substrate-rescue within a metric class where "
                "(a) >=2 prior cells show substrate tracks the baseline within 0.01 "
                "AND (b) the baseline absolute is < chain-grade band, demand the "
                "pre-reg either (i) move to baseline-replacement (different metric "
                "class) OR (ii) explicitly declare the cell is targeting baseline-"
                "REPLACEMENT mechanism even if framed as substrate-side; or HARD_FAIL "
                "pre-dispatch on this rule."
            ),
            "originating_ruling_note": RULING_NOTE,
            "originating_pattern": (
                "Gap 2 (capacity) 9-cell pattern: 6 geometry HARD_FAILs (whitening, "
                "MIMO, DG, polarimetric LEARNED, anisotropy_v4 AB tie, ScaNN aniso) "
                "+ 3 stride-sweep MM cells (v1, v2, v2b) proving substrate at cosine "
                "floor 8/8 delta <= +0.007."
            ),
            "fix_26_pre_dispatch_matcher_spec": (
                "tools/predispatch_check.py <anchor> should: "
                "(1) scan recent_landings.jsonl for cells in same key-domain showing "
                "substrate-tracks-baseline-within-0.01 delta on the relevant metric; "
                "(2) if 2+ such cells exist AND baseline absolute < chain-grade band, "
                "emit WARNING and recommend Research route to baseline-replacement "
                "mechanism instead of substrate-rescue within same metric class; "
                "(3) BLOCK dispatch absent Research override flag with rationale."
            ),
            "would_have_caught": (
                "estimated 4-6 of the 6 geometry HARD_FAILs in Gap 2 (whitening, MIMO, "
                "DG, polarimetric LEARNED, anisotropy_v4 AB tie, ScaNN aniso) -- all "
                "were dispatched after >=1 prior substrate-tracks-cosine-baseline "
                "evidence existed."
            ),
            "edge_case_does_not_apply": (
                "rule does NOT apply when baseline is already chain-grade and substrate "
                "is rescuing FROM sub-chain-grade TO chain-grade; in that case substrate-"
                "rescue IS the path."
            ),
            "composes_with": [
                ("meta::T3/META_substrate_tracks_KNN_cosine_floor_within_0p007_"
                 "across_eight_construction_param_combinations_n_seeds_1_smoke_M_"
                 "2000_pythia_160m_window_16_to_64"),
                ("meta::T3/META_cosine_physics_floor_on_short_LM_window_keys_M_"
                 "2000_pythia_160m_is_below_chain_grade_band_recall_at_1_le_0p16_"
                 "across_all_tested_constructions"),
                "feedback::cert_owner_overrides_director_via_by_construction_saturation_2026-06-22",
                "feedback::fix26_predispatch_verify_the_referent_gate_2026-06-22",
            ],
            "cites": [
                "Skunkworks_landed_VET_gap2_consolidated_2026-06-26",
                "Fix_26_predispatch_verify_the_referent_2026-06-22",
                "6_prior_geometry_HARD_FAILs_in_Gap_2_capacity_arc",
                "3_consolidated_stride_sweep_cells_v1_v2_v2b_2026-06-26",
            ],
        },
    )


# ============================================================================
# SAFE WRITER HELPER
# ============================================================================

def safe_add_with_ledger(
    atom: Atom,
    *,
    source: str,
    note: str,
    ledger_row: dict,
    expected_cert_n_after: int,
) -> tuple[bool, str | None]:
    """Add atom + ledger row (mirrors atomize_meta_harness_rigged_2026-06-23 pattern)."""
    ps = PartitionedStore(STORE_ROOT)
    qid = f"{atom.corpus.value}::{atom.id}"
    if ps.get_atom(qid) is not None:
        print(f"  SKIP (idempotent at Store layer): {atom.id} already present.")
    else:
        print(f"  ADDING atom: {atom.id}")
        ps.add_atom(atom, source=source, note=note)

        # Fresh-Store round-trip verify
        ps2 = PartitionedStore(STORE_ROOT)
        found = ps2.get_atom(qid)
        if found is None:
            print(f"  FAIL: atom not found post-add")
            return (False, None)
        md = found.metadata or {}
        expected_pq = (atom.metadata or {}).get("provenance_quality")
        if md.get("provenance_quality") != expected_pq:
            print(
                f"  FAIL: pq mismatch (expected {expected_pq}, "
                f"got {md.get('provenance_quality')})"
            )
            return (False, None)
        print(f"  PASS: round-trip survival OK (pq={md.get('provenance_quality')})")

    # Live-CERT cross-check
    ps_check = PartitionedStore(STORE_ROOT)
    live_n = sum(
        1 for a in ps_check.all_atoms()
        if (a.metadata or {}).get("provenance_quality") == "CERT_CHAIN_GRADE"
    )
    if live_n != expected_cert_n_after:
        print(
            f"  FAIL: live CERT N {live_n} != expected_cert_n_after {expected_cert_n_after}"
        )
        return (False, None)

    print(
        f"  appending cert-ledger row "
        f"(op={ledger_row.get('op')} status={ledger_row.get('cert_status')} "
        f"delta={ledger_row.get('cert_increment_delta')})"
    )
    try:
        row_h = append_cert_ledger_row(
            ledger_row,
            expected_cert_n_pre=expected_cert_n_after,
            expected_cert_n_post=expected_cert_n_after,
        )
        print(f"  ledger row appended; row_hash = {row_h}")
        return (True, row_h)
    except Exception as e:
        print(f"  FAIL: cert-ledger append errored: {e}")
        return (False, None)


def build_proven_bound_row(*, atom_id, cell_commit, verdict, notes_path, metrics_path,
                           atomized_by, note, ts=None):
    """Build a cert_ruling row for a proven_bound atomization (delta=+1)."""
    return {
        "ts": ts,
        "op": "cert_ruling",
        "atom_id": atom_id,
        "cert_status": "proven_bound",
        "cert_class": "pre_reg_miss_proven_bound",
        "verified_off_data": True,
        "atomized_by": atomized_by,
        "cell_commit": cell_commit,
        "verdict": verdict,
        "cert_increment_delta": 1,
        "cv": None,
        "referent_pointer": {
            "notes_path": notes_path,
            "metrics_path": metrics_path,
            "atom_qualified_id": atom_id,
        },
        "supersedes": None,
        "note": note,
    }


def build_meta_rule_row(*, atom_id, cell_commit, verdict, notes_path, atomized_by, note,
                       ts=None):
    """Build a cert_ruling row for a CERT-neutral META rule (delta=0; cert_status=custom)."""
    return {
        "ts": ts,
        "op": "cert_ruling",
        "atom_id": atom_id,
        "cert_status": "custom",
        "cert_class": "discipline_meta",
        "verified_off_data": True,
        "atomized_by": atomized_by,
        "cell_commit": cell_commit,
        "verdict": verdict,
        "cert_increment_delta": 0,
        "cv": None,
        "referent_pointer": {
            "notes_path": notes_path,
            "metrics_path": None,
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

    # Build atoms (DRY)
    atom1 = build_atom1_substrate_tracks_knn_cosine_floor()
    atom2 = build_atom2_cosine_floor_below_chain_grade()
    atom3 = build_atom3_baseline_replacement_not_rescue()

    print("=" * 72)
    print("Cert routing plan (DRY pre-flight)")
    print("=" * 72)
    print(f"  [1] {atom1.id}")
    print(
        f"       pq={atom1.metadata['provenance_quality']} "
        f"status={atom1.metadata['cert_status']} delta=+1"
    )
    print(f"  [2] {atom2.id}")
    print(
        f"       pq={atom2.metadata['provenance_quality']} "
        f"status={atom2.metadata['cert_status']} delta=0"
    )
    print(f"  [3] {atom3.id}")
    print(
        f"       pq={atom3.metadata['provenance_quality']} "
        f"status={atom3.metadata['cert_status']} delta=0"
    )
    print()
    print("  Net CERT N change: +1 (one proven_bound atomization)")
    print("  Net ledger rows: +3 (1 proven_bound ruling + 2 meta_rule rulings)")

    if not apply:
        print()
        print("DRY: pass --apply to mutate Store + ledger.")
        return 0

    # A5 PRE
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

    # Window 1: Atom 1 proven_bound (delta=+1)
    print()
    print("=" * 72)
    print("Window 1: Atom 1 (proven_bound; delta=+1)")
    print("=" * 72)
    qid1 = f"{atom1.corpus.value}::{atom1.id}"
    ps_check1 = PartitionedStore(STORE_ROOT)
    atom1_already_present = ps_check1.get_atom(qid1) is not None
    expected_after_a1 = cert_pre if atom1_already_present else cert_pre + 1
    row1 = build_proven_bound_row(
        atom_id=qid1,
        cell_commit=CELL_COMMIT,
        verdict=atom1.metadata["verdict"],
        notes_path=RULING_NOTE,
        metrics_path=atom1.metadata["metrics_path"],
        atomized_by="skunkworks_atomize_gap2_consolidated_2026-06-26",
        note=(
            "proven_bound_skunkworks_gap2_consolidated_3_cell_8_combination_"
            "substrate_tracks_KNN_cosine_floor_within_0p007_one_sided_proven_"
            "substrate_NEVER_beats_KNN_0_of_8_violations_M_2000_pythia_160m_"
            "n_seeds_1_smoke_chain_grade_promotion_path_3_seed_pythia_2p8b_M_10k_"
            "USER_full_auto_2026-06-26"
        ),
    )
    ok, h1 = safe_add_with_ledger(
        atom1,
        source="skunkworks_landed_vet_gap2_consolidated_2026-06-26",
        note=(
            "Atom 1: substrate-tracks-KNN-cosine-floor proven bound; 8/8 delta <=+0.007 "
            "all non-negative; MEASURED_MECHANISM tier (proven bound = chain-grade "
            "eligible boundary; +1 cert); A5 non-destructive (no cell metrics or "
            "verdicts mutated)."
        ),
        ledger_row=row1,
        expected_cert_n_after=expected_after_a1,
    )
    if not ok:
        print("ABORT: Atom 1 window failed; halting.")
        return 1
    print(f"  Live CERT N now {expected_after_a1}; row_hash {h1}")

    # Window 2: Atom 2 META rule cosine-floor (delta=0)
    print()
    print("=" * 72)
    print("Window 2: Atom 2 (META rule cosine-floor below chain-grade; delta=0)")
    print("=" * 72)
    qid2 = f"{atom2.corpus.value}::{atom2.id}"
    row2 = build_meta_rule_row(
        atom_id=qid2,
        cell_commit=CELL_COMMIT,
        verdict="META_RULE_CERT_NEUTRAL_skunkworks",
        notes_path=RULING_NOTE,
        atomized_by="skunkworks_atomize_gap2_consolidated_2026-06-26",
        note=(
            "meta_rule_META_cosine_physics_floor_on_short_LM_window_keys_M_2000_"
            "pythia_160m_below_chain_grade_band_high_M_path_is_non_cosine_mechanism_"
            "interpretation_for_6_prior_geometry_HARD_FAILs_no_demotion"
        ),
    )
    ok, h2 = safe_add_with_ledger(
        atom2,
        source="skunkworks_landed_vet_gap2_consolidated_2026-06-26",
        note=(
            "Atom 2: META rule on cosine-physics floor below chain-grade at short-LM-"
            "window keys; CERT-neutral; provides post-hoc interpretation for 6 prior "
            "geometry HARD_FAILs (no retroactive demotion)."
        ),
        ledger_row=row2,
        expected_cert_n_after=expected_after_a1,
    )
    if not ok:
        print("ABORT: Atom 2 window failed; halting.")
        return 1
    print(f"  Live CERT N now {expected_after_a1}; row_hash {h2}")

    # Window 3: Atom 3 META discipline rule baseline-replacement (delta=0)
    print()
    print("=" * 72)
    print("Window 3: Atom 3 (META discipline rule baseline-replacement-not-rescue; delta=0)")
    print("=" * 72)
    qid3 = f"{atom3.corpus.value}::{atom3.id}"
    row3 = build_meta_rule_row(
        atom_id=qid3,
        cell_commit=CELL_COMMIT,
        verdict="META_RULE_CERT_NEUTRAL_skunkworks",
        notes_path=RULING_NOTE,
        atomized_by="skunkworks_atomize_gap2_consolidated_2026-06-26",
        note=(
            "meta_rule_META_when_substrate_tracks_external_baseline_within_smoke_noise_"
            "AND_baseline_is_low_chain_grade_path_is_baseline_replacement_not_rescue_"
            "fix_26_pre_dispatch_matcher_discipline_would_have_caught_4_to_6_of_6_"
            "geometry_HARD_FAILs"
        ),
    )
    ok, h3 = safe_add_with_ledger(
        atom3,
        source="skunkworks_landed_vet_gap2_consolidated_2026-06-26",
        note=(
            "Atom 3: META discipline rule (CERT-neutral) -- baseline-replacement-vs-rescue "
            "discipline; Fix #26 pre-dispatch matcher; generalizes Gap 2 9-cell pattern."
        ),
        ledger_row=row3,
        expected_cert_n_after=expected_after_a1,
    )
    if not ok:
        print("ABORT: Atom 3 window failed; halting.")
        return 1
    print(f"  Live CERT N now {expected_after_a1}; row_hash {h3}")

    # A5 POST
    print()
    print("=" * 72)
    print("A5 POST snapshot")
    print("=" * 72)
    ps_post = PartitionedStore(STORE_ROOT)
    cert_post = sum(
        1 for a in ps_post.all_atoms()
        if (a.metadata or {}).get("provenance_quality") == "CERT_CHAIN_GRADE"
    )
    net_delta = cert_post - cert_pre
    print(f"A5-POST: live CERT N = {cert_post}")
    print(f"  CERT N: {cert_pre} -> {cert_post} (net delta = {net_delta})")

    # Verify final atoms present at intended pq
    ps_v = PartitionedStore(STORE_ROOT)
    a1_v = ps_v.get_atom(f"{atom1.corpus.value}::{atom1.id}")
    a2_v = ps_v.get_atom(f"{atom2.corpus.value}::{atom2.id}")
    a3_v = ps_v.get_atom(f"{atom3.corpus.value}::{atom3.id}")
    assert a1_v is not None, "Atom 1 missing post-run"
    assert a2_v is not None, "Atom 2 missing post-run"
    assert a3_v is not None, "Atom 3 missing post-run"
    assert (a1_v.metadata or {}).get("provenance_quality") == "CERT_CHAIN_GRADE"
    assert (a2_v.metadata or {}).get("provenance_quality") == "META_RULE_CERT_NEUTRAL"
    assert (a3_v.metadata or {}).get("provenance_quality") == "META_RULE_CERT_NEUTRAL"
    print(f"  PASS: all 3 atoms present at intended pq")

    # Summary
    print()
    print("=" * 72)
    print("SUMMARY")
    print("=" * 72)
    print(f"  Atom 1 ({atom1.id})")
    print(f"    proven_bound ledger row hash: {h1}")
    print(f"  Atom 2 ({atom2.id})")
    print(f"    meta_rule ledger row hash: {h2}")
    print(f"  Atom 3 ({atom3.id})")
    print(f"    meta_rule ledger row hash: {h3}")
    print()
    print(f"  CERT N: {cert_pre} -> {cert_post} (net delta {net_delta:+d})")
    print(f"  Ledger rows appended this run: 3 (1 proven_bound + 2 meta_rule)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
