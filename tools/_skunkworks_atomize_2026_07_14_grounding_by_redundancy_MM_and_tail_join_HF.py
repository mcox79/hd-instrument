"""
A5-gated atomize (AUDIT-ONLY, XHIGH): two VET-confirmed landed results, 2026-07-14.
Staged local ONLY -- needs_orchestrator_store_sync=True; NO origin push (no user-auth this turn).

ATOM 1 -- grounding-by-redundancy joint-corruption allometry v1  -> MEASURED_MECHANISM (math)
  CANONICAL FULL (run_mode=full, 5 seeds 7/13/19/23/29, n_dim=8192, HARD_PASS). Filed off the CANONICAL,
  NOT the smoke (canon != preview). Cross-law CONSENSUS over jointly-corrupted attributes CORRECTS
  (+0.301) and LOCALIZES (0.800 vs no-redundancy 0.431, chance 0.25) the inconsistent value, leak-free.
  This is the GENUINE ground-by-consistency that FIXES the earlier law-consistency COUPLING-ARTIFACT
  (predecessor atom, read from disk below) -- there BOTH target and predictor were the same source and
  the predictor was always clean; HERE attributes are jointly corrupted and consensus must localize.

ATOM 2 -- grounded ingest tail-join v1  -> HF_STRUCTURAL_BOUND (math, honest structural negative)
  Bulk NUMERIC-literal grounding (Wikidata quantity claims) via exact-ID join reaches only ~1.8% of the
  substrate's sparse tail (HARD_FAIL vs 5% floor / 15% pass bar). => don't build the numeric literal-fusion
  pipeline; redirect grounding content-type to TEXT/GLOSS.

INDEPENDENT OFF-DISK RECOMPUTE (.venv, this session -- NOT verdict_msg, Fix #28):
  ATOM1 (per_seed[] off metrics.json, 5/5 units, expected 20 units cardinality_ok):
    FULL corr_gain per seed [0.320,0.385,0.188,0.367,0.244] mean=0.301 cv=0.247 (noisy, ~0.25).
    FULL loc mean=0.800 (per seed 0.781..0.859, cv 0.054); NO_REDUNDANCY loc=0.431; chance=0.250.
    NO_REDUNDANCY corr_gain NEG 5/5 [-0.403,-0.502,-0.261,-0.764,-0.072]; SCRAMBLE NEG 5/5
      [-0.354,-0.644,-0.371,-0.365,-0.510]; WRONG_EXP NOT 5/5 neg [-0.106,-0.160,-0.037,+0.061,-0.032]
      -> agg -0.055, BEATEN by FULL but 4/5 not 5/5 (HONEST framing correction below).
    FULL-vs-MARGINAL loc margin agg +0.113 (per seed 0.062..0.203; THIN, min +0.062 -- request's +0.078
      was seed-7 specifically). FULL corr 0.301 vs RELATIONAL corr 0.122 (aggregate only; thin over a
      strong no-law baseline). PARTNER-CORRUPTED DIAGNOSTIC (report-only): FULL loc_partner_corr per seed
      [0.438,0.406,0.406,0.281,0.250] agg full_loc_pc=0.356 -> collapses toward chance 0.25 when the
      correlated sibling is ALSO corrupted (consensus polluted). Request cited ~0.375; on-disk is 0.356.
  ATOM2 (per_entity[] off metrics.json + provenance.json, 500 units cardinality_ok):
    join_hit_rate 9/500 = 0.0180 (HARD_FAIL vs 0.05 floor, 0.15 pass bar). Of 123 matched (found-QID)
    entities only 9 carry a quantity claim = 7.3%; 114 matched carry NONE; 377 missing.
    Suppressible-key misses (casing/hyphen/multiword/redirect heuristic) 240/377 = 63.7% (provenance
    states 62.6% -- consistent, minor heuristic diff). LOSSY-KEY FLOOR, not total reach; BUT numeric
    conclusion SURVIVES a perfect key: 7.3% qty-carry on a fully-resolved 500 caps absolute reach ~7.3%
    and realistically ~3-6% << 15%. scramble_control hit-rates [0,0,0] (fires); source_sha256_match=True
    (snapshot identity ok). CROSSWALK-REVIVAL CLOSED: no lemma->QID on any on-disk source; revival needs
    an acquired lemma->external-numeric-ID crosswalk.

CROSS-ARC OVERLAP CHECK (substrate_query, mandatory):
  ATOM1 'cross-attribute law consistency redundancy consensus grounding correction localization allometric'
    -> top cosine 0.3223 char-trigram token 'consistency' (wordnet); cross_modal_consistency_cpu_v1 note
    0.2998 (<0.30, different mechanism). NO prior arc CELL rediscovery at cosine>0.30. The intended relation
    is to the predecessor law-consistency COUPLING-ARTIFACT atom (compose/amend, disclosed) -- not a
    rediscovery. July-1 INT8-rediscovery pattern does NOT apply.
  ATOM2 'bulk numeric literal grounding wikidata quantity claim exact ID join sparse tail reach lexical'
    -> top cosine 0.293 'numerical quantity' (wordnet token). NONE at cosine>0.30. Clean.

TIERS: ATOM1 = MEASURED_MECHANISM (real, leak-free ground-by-consistency mechanism; but thin margins over
  strong no-law baselines, noisy correction gain cv~0.25, WRONG_EXP beaten-not-collapsed 4/5, and a
  DIAGNOSTIC where partner-corruption collapses localization to ~chance -> proven bound, not a CG win).
  ATOM2 = HF_STRUCTURAL_BOUND (genuine substantive negative: positive/scramble control fires 0/0/0,
  snapshot identity verified; not a test-design failure; structural non-numeric tail).
"""
from __future__ import annotations
import json, os, time
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
MATH_ATOMS = ROOT / "data/substrate_index/math/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"

ATOMIZED_BY = "skunkworks_atomize_2026_07_14_grounding_by_redundancy_MM_and_tail_join_HF"
TS = time.time()
TS_ISO = "2026-07-14T00:00:00Z"
SESSION = "2026-07-14_grounding_by_redundancy_MM_plus_tail_join_HF_landed_vet"
REPO_HEAD = "7ca96dede"  # repo HEAD at atomize (cell metrics carry no own commit; local full)

# read predecessor coupling-artifact atom id from disk (ATOM1 fixes it) -- avoid transcription error
_pred_id = None
with open(MATH_ATOMS, "r", encoding="utf-8") as f:
    for ln in f:
        if not ln.strip():
            continue
        try:
            _a = json.loads(ln)
        except Exception:
            continue
        _i = _a.get("id", "")
        if _i.startswith("math::MEASURED_MECHANISM_ground_by_LAW_consistency_allometry_is_a_PREDICTOR_CLEAN"):
            _pred_id = _i
assert _pred_id is not None, "predecessor law-consistency coupling-artifact atom not found on disk"
PRED_COUPLING_ARTIFACT = _pred_id

# ---------------------------------------------------------------------------
# ATOM 1 -- grounding-by-redundancy MEASURED_MECHANISM
# ---------------------------------------------------------------------------
atom1 = {
    "id": (
        "math::MEASURED_MECHANISM_grounding_by_REDUNDANCY_joint_corruption_allometry_v1_CROSS_LAW_CONSENSUS_"
        "over_JOINTLY_corrupted_attributes_CORRECTS_and_LOCALIZES_the_inconsistent_value_LEAK_FREE_this_is_"
        "the_GENUINE_ground_by_consistency_that_FIXES_the_earlier_LAW_consistency_PREDICTOR_CLEAN_COUPLING_"
        "ARTIFACT_CANONICAL_FULL_5seed_7_13_19_23_29_n_dim8192_HARD_PASS_20units_FULL_corr_gain_plus0p301_"
        "per_seed_0p320_0p385_0p188_0p367_0p244_cv0p247_FULL_loc_0p800_vs_NO_REDUNDANCY_0p431_chance_0p250_"
        "det_auc_0p870_NO_REDUNDANCY_corr_NEG_5of5_SCRAMBLE_corr_NEG_5of5_WRONG_EXP_BEATEN_agg_neg0p055_but_"
        "only_4of5_neg_seed23_plus0p061_HONEST_not_a_clean_5of5_collapse_THIN_MARGINS_FULL_vs_MARGINAL_loc_"
        "plus0p113_min_seed_plus0p062_FULL_corr_0p301_vs_RELATIONAL_0p122_aggregate_only_DIAGNOSTIC_report_"
        "only_when_the_correlated_SIBLING_is_ALSO_corrupted_FULL_loc_partner_corr_collapses_to_full_loc_pc_"
        "0p356_toward_chance_0p250_consensus_polluted_leak_free_scramble_and_no_redundancy_mustfails_"
        "collapse_5of5_aggregates_reproduce_off_per_seed_venv_TIER_MEASURED_MECHANISM_proven_bound_real_"
        "ground_by_consistency_mechanism_but_thin_over_strong_no_law_baselines_noisy_gain_FIXES_predictor_"
        "clean_coupling_artifact_head_7ca96dede_2026-07-14"
    ),
    "name": (
        "MATH MEASURED_MECHANISM: grounding-by-REDUNDANCY -- cross-law CONSENSUS over JOINTLY-corrupted "
        "attributes CORRECTS (corr_gain +0.301) and LOCALIZES (loc 0.800 vs no-redundancy 0.431, chance "
        "0.250) the inconsistent value, LEAK-FREE, on the CANONICAL FULL (5 seeds 7/13/19/23/29, n_dim=8192, "
        "HARD_PASS, 20 units). This is the GENUINE ground-by-consistency that FIXES the earlier "
        "law-consistency PREDICTOR-CLEAN COUPLING-ARTIFACT. HONEST BOUNDS: thin margins over strong no-law "
        "baselines (FULL-vs-MARGINAL loc +0.113, min-seed +0.062; FULL-vs-RELATIONAL corr passes on "
        "aggregate only), correction gain noisy (cv 0.247), WRONG_EXP beaten-not-collapsed (agg -0.055, 4/5 "
        "seeds neg), and a report-only DIAGNOSTIC where partner-corruption of the correlated sibling "
        "collapses localization to ~chance (full_loc_pc 0.356). TIER = MEASURED_MECHANISM (proven bound)."
    ),
    "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "kind": "experiment_landed_vet",
    "cert_status": (
        "confirmed_measured_mechanism_grounding_by_redundancy_cross_law_consensus_over_jointly_corrupted_"
        "attributes_corrects_and_localizes_the_inconsistent_value_leak_free_genuine_ground_by_consistency_"
        "fixes_the_earlier_law_consistency_predictor_clean_coupling_artifact_but_thin_margins_over_strong_"
        "no_law_baselines_noisy_correction_gain_and_partner_corrupt_diagnostic_collapses_localization_to_"
        "chance_proven_bound_not_chain_grade_win"
    ),
    "cert_class": (
        "cross_attribute_multi_law_consensus_grounding_detection_correction_localization_over_jointly_"
        "corrupted_allometric_attributes_leak_free_with_no_redundancy_scramble_wrong_exp_marginal_"
        "relational_controls_and_a_partner_corrupted_report_only_diagnostic"
    ),
    "description": (
        "Independent adversarial off-disk landed-VET (.venv, AUDIT-ONLY). Recomputed all aggregates from "
        "metrics.json per_seed[] (NOT verdict_msg, Fix #28) on the CANONICAL FULL "
        "(exp_grounding_by_redundancy_joint_corruption_allometry_v1; run_mode=full; 5 seeds 7/13/19/23/29; "
        "n_dim=8192; expected 20 units, got 20, cardinality_ok; verdict HARD_PASS). Filed off the CANONICAL, "
        "NOT the smoke (canon != preview). THE MECHANISM: a fully-connected 4-node pairwise-power-law network "
        "(mass/length/lifespan/gestation) is used so that each attribute is over-determined by its siblings; "
        "when a target attribute is JOINTLY corrupted, cross-law CONSENSUS (agreement of the sibling-implied "
        "predictions) both DETECTS, CORRECTS, and LOCALIZES the inconsistent value. This is the GENUINE "
        "ground-by-consistency that FIXES the earlier law-consistency COUPLING-ARTIFACT (predecessor atom "
        "'ground_by_LAW_consistency_allometry_is_a_PREDICTOR_CLEAN_SAME_SOURCE_COUPLING_artifact'), where in "
        "BOTH detection/correction AND imputation ONLY the target was corrupted while the predictor was "
        "ALWAYS clean -- here attributes are JOINTLY corrupted and consensus must genuinely localize. "
        "VERIFIED off per_seed: FULL corr_gain per seed [0.320,0.385,0.188,0.367,0.244] mean=+0.301 cv=0.247; "
        "FULL loc per seed [0.781,0.859,0.766,0.844,0.750] mean=0.800 (cv 0.054); NO_REDUNDANCY loc=0.431; "
        "chance_loc=0.250; FULL det_auc=0.870. MUST-FAILS: NO_REDUNDANCY corr_gain NEG 5/5 "
        "[-0.403,-0.502,-0.261,-0.764,-0.072] and SCRAMBLE corr_gain NEG 5/5 [-0.354,-0.644,-0.371,-0.365,"
        "-0.510] collapse cleanly; WRONG_EXP corr_gain [-0.106,-0.160,-0.037,+0.061,-0.032] is BEATEN by FULL "
        "on aggregate (-0.055) but is NEG only 4/5 (seed 23 = +0.061) -- so the 'all must-fails collapse 5/5' "
        "framing OVERSTATES WRONG_EXP (honest correction: NO_REDUNDANCY+SCRAMBLE 5/5, WRONG_EXP beaten 4/5). "
        "HONEST BOUNDS (the load-bearing caveats): (1) THIN MARGINS over strong NO-LAW baselines -- "
        "FULL-vs-MARGINAL loc margin agg +0.113 but per-seed 0.062..0.203 (min +0.062; request's '+0.078' was "
        "seed-7 specifically); FULL corr 0.301 vs RELATIONAL corr 0.122 passes on the AGGREGATE only. (2) "
        "correction gain is NOISY (cv 0.247, ~0.25). (3) PARTNER-CORRUPTED DIAGNOSTIC (report-only, NOT a "
        "gate): when the correlated SIBLING is ALSO corrupted, FULL localization collapses -- loc_partner_corr "
        "per seed [0.438,0.406,0.406,0.281,0.250], agg full_loc_pc=0.356, toward chance 0.250 (consensus "
        "polluted). Request cited ~0.375; on-disk reproduces 0.356. LEAK-FREE (scramble + no-redundancy "
        "controls collapse). Aggregates reproduce off per_seed. TIER = MEASURED_MECHANISM: a REAL, leak-free "
        "ground-by-consistency mechanism (correctly fixes the predictor-clean coupling artifact) but a PROVEN "
        "BOUND, not a chain-grade capability win -- thin over strong no-law baselines, noisy gain, and it "
        "degrades to chance when the redundant sibling is co-corrupted."
    ),
    "provenance": {
        "cell": "experiments/exp_grounding_by_redundancy_joint_corruption_allometry_v1.py",
        "commit": REPO_HEAD,
        "commit_note": "cell metrics carry no own commit; repo HEAD at atomize (local canonical full)",
        "metrics_path": "data/exp_grounding_by_redundancy_joint_corruption_allometry_v1/metrics.json",
        "seeds": [7, 13, 19, 23, 29],
        "run_mode": "full",
        "n_dim": 8192,
        "expected_n_units": 20,
        "got_n_units": 20,
        "cardinality_ok": True,
        "whole_cell_verdict": "HARD_PASS",
        "audit_tier": "MEASURED_MECHANISM",
        "ts_iso": TS_ISO,
        "atomized_by": ATOMIZED_BY,
        "verified_off_data": True,
        "verified_off_data_note": (
            "Independent .venv recompute off per_seed[] (5/5, 20 units). FULL corr_gain "
            "[0.320,0.385,0.188,0.367,0.244] mean 0.301 cv 0.247; FULL loc [0.781,0.859,0.766,0.844,0.750] "
            "mean 0.800; NO_REDUNDANCY loc 0.431; chance 0.250; FULL det_auc 0.870. NO_REDUNDANCY corr NEG "
            "5/5; SCRAMBLE corr NEG 5/5; WRONG_EXP corr [-0.106,-0.160,-0.037,+0.061,-0.032] agg -0.055 "
            "beaten 4/5. FULL-vs-MARGINAL loc +0.113 (min-seed +0.062). FULL corr 0.301 vs RELATIONAL 0.122 "
            "aggregate. PARTNER-CORRUPT loc_partner_corr [0.438,0.406,0.406,0.281,0.250] agg full_loc_pc "
            "0.356. All reproduce off per_seed."
        ),
    },
    "verified_numbers": {
        "n_dim": 8192, "n_seeds": 5, "seeds": [7, 13, 19, 23, 29],
        "expected_n_units": 20, "got_n_units": 20, "cardinality_ok": True,
        "full_corr_gain_per_seed": [0.320, 0.385, 0.188, 0.367, 0.244],
        "full_corr_gain_mean": 0.3009498365414959, "full_corr_gain_cv": 0.247,
        "full_loc_per_seed": [0.781, 0.859, 0.766, 0.844, 0.750],
        "full_loc": 0.8, "full_loc_cv": 0.054,
        "no_redundancy_loc": 0.43125, "chance_loc": 0.25,
        "full_det_auc": 0.8697265625,
        "no_redundancy_corr_gain_per_seed": [-0.403, -0.502, -0.261, -0.764, -0.072],
        "no_redundancy_corr_neg_5of5": True,
        "scramble_corr_gain_per_seed": [-0.354, -0.644, -0.371, -0.365, -0.510],
        "scramble_corr_neg_5of5": True,
        "wrong_exp_corr_gain_per_seed": [-0.106, -0.160, -0.037, 0.061, -0.032],
        "wrong_exp_corr_agg": -0.054699948633232395,
        "wrong_exp_beaten_but_only_4of5_neg": True,
        "full_vs_marginal_loc_margin_agg": 0.1125, "full_vs_marginal_loc_margin_min_seed": 0.062,
        "full_corr_agg": 0.3009498365414959, "relational_corr_agg": 0.12247880958544684,
        "partner_corrupt_full_loc_pc": 0.35625,
        "partner_corrupt_full_loc_partner_corr_per_seed": [0.438, 0.406, 0.406, 0.281, 0.250],
        "mechanism_fires": True, "mustfail_collapses": True,
    },
    "honest_scope": (
        "MEASURED_MECHANISM proven bound: a REAL leak-free ground-by-consistency mechanism (cross-law "
        "consensus over jointly-corrupted attributes corrects + localizes; correctly fixes the earlier "
        "predictor-clean coupling artifact) -- but NOT a chain-grade capability win. Margins over the strong "
        "no-law baselines (MARGINAL, RELATIONAL) are THIN, the correction gain is noisy (cv 0.247), WRONG_EXP "
        "is beaten-not-collapsed (4/5 seeds neg), and localization degrades to ~chance (full_loc_pc 0.356) "
        "when the redundant sibling is co-corrupted. The mechanism is grounded ONLY while at least one "
        "redundant sibling stays clean."
    ),
    "framing_corrections_vs_cell_author_and_director": [
        "SYMMETRIC ANTI-NEGATIVITY (upward): this is a GENUINE mechanism, not another coupling artifact -- it "
        "correctly FIXES the predecessor law-consistency predictor-clean artifact by JOINTLY corrupting "
        "attributes so consensus must truly localize. Leak-free (scramble + no-redundancy collapse). Bank it "
        "as MEASURED_MECHANISM, do not deflate to a negative.",
        "HONEST DOWNWARD (must-fails): the 'all must-fails collapse 5/5' framing OVERSTATES WRONG_EXP. Off "
        "per_seed, NO_REDUNDANCY and SCRAMBLE corr_gain are NEG 5/5 (clean collapse), but WRONG_EXP corr_gain "
        "is NEG only 4/5 (seed 23 = +0.061); it is BEATEN by FULL on aggregate (-0.055) but not a clean 5/5 "
        "collapse. Encode as 'NO_REDUNDANCY+SCRAMBLE collapse 5/5; WRONG_EXP beaten 4/5'.",
        "HONEST DOWNWARD (margins): the FULL-vs-MARGINAL loc margin is +0.113 aggregate but the request's "
        "'+0.078' is seed-7 specifically; the per-seed range is 0.062..0.203, so the THIN-margin claim is "
        "correct and the true min-seed margin is +0.062. FULL-vs-RELATIONAL corr (0.301 vs 0.122) passes on "
        "the AGGREGATE only -- not a per-seed guarantee.",
        "PARTNER-CORRUPTED DIAGNOSTIC is REPORT-ONLY (not a scored gate) and on-disk reproduces full_loc_pc "
        "=0.356 (request cited ~0.375). Localization collapses toward chance 0.250 when the correlated "
        "sibling is ALSO corrupted -> the mechanism requires at least one clean redundant sibling; bake this "
        "boundary into any downstream framing.",
    ],
    "revival_or_extension_criterion": (
        "MM scope: cross-law consensus over jointly-corrupted allometric attributes on a fully-connected "
        "4-node pairwise-power-law network (mass/length/lifespan/gestation), 5 seeds, n_dim=8192. PROMOTION "
        "to CG would require: (1) the FULL-vs-MARGINAL / FULL-vs-RELATIONAL margins to widen and hold "
        "PER-SEED (not aggregate-only) on a network where NO near-tautological pair carries the result; (2) "
        "correction gain cv to tighten well below the current 0.247; (3) a WRONG_EXP-style must-fail to "
        "collapse cleanly 5/5. DEMOTION trigger: if a re-run shows the localization win depends on a single "
        "near-tautological sibling pair, or if the partner-corrupt collapse to chance also occurs under "
        "single-sibling corruption (which would mean consensus never had redundancy to exploit). EXTENSION "
        "(new cell, composes not supersedes): push to a SPARSE / partially-observed law network where not "
        "every attribute has a clean sibling -- the realistic grounding regime the dense 4-node network "
        "cannot answer."
    ),
    "composes": [PRED_COUPLING_ARTIFACT],
    "compose_note": (
        "AMENDS/FIXES the predecessor MEASURED_MECHANISM 'ground_by_LAW_consistency_allometry_is_a_"
        "PREDICTOR_CLEAN_SAME_SOURCE_COUPLING_artifact' (NOT superseded -- that atom's proven bound stands as "
        "'law-consistency with an always-clean predictor is a coupling artifact'). This cell closes that gap "
        "by JOINTLY corrupting the attributes so the predictor is no longer privileged; cross-law consensus "
        "then genuinely localizes the inconsistent value (leak-free). The predecessor documented WHY "
        "same-source predictor-clean coupling is not grounding; this atom documents the CONDITIONS under "
        "which redundancy DOES ground (at least one clean sibling) and the boundary where it fails "
        "(partner-corrupt -> chance)."
    ),
    "cross_arc_overlap_check": (
        "substrate_query 'cross-attribute law consistency redundancy consensus grounding correction "
        "localization allometric' -> top cosine 0.3223 char-trigram token 'consistency' (wordnet), "
        "cross_modal_consistency_cpu_v1 note 0.2998 (<0.30, different mechanism = cross-MODAL shared-value "
        "retrieval, not cross-ATTRIBUTE allometric law-consensus over corruption). NO prior arc CELL "
        "rediscovery at cosine>0.30. The genuine relation is the DISCLOSED compose/amend of the predecessor "
        "law-consistency coupling-artifact atom. July-1 INT8-rediscovery pattern does NOT apply."
    ),
    "anchor": "grounding_by_redundancy_joint_corruption_allometry_v1",
    "cell_commit": REPO_HEAD,
    "seeds": [7, 13, 19, 23, 29],
    "run_mode": "full",
    "cardinality_ok": True,
    "verified_off_data": True,
    "auditor": "hdi_skunkworks",
    "atomized_by": "hdi_skunkworks",
    "landed_VET_session": SESSION,
    "needs_orchestrator_store_sync": True,
    "ts": TS,
    "ts_iso": TS_ISO,
    "ts_added": TS_ISO,
    "aliases": [
        "grounding-by-redundancy: cross-law consensus over jointly-corrupted attributes corrects (+0.301) and localizes (0.800 vs no-redundancy 0.431, chance 0.25) the inconsistent value, leak-free -- MEASURED_MECHANISM",
        "the GENUINE ground-by-consistency that FIXES the earlier law-consistency PREDICTOR-CLEAN coupling artifact (joint corruption removes the privileged clean predictor)",
        "HONEST BOUNDS: thin over strong no-law baselines (FULL-vs-MARGINAL loc +0.113 min-seed +0.062), noisy gain cv 0.247, WRONG_EXP beaten-not-collapsed 4/5",
        "PARTNER-CORRUPT DIAGNOSTIC (report-only): FULL localization collapses to full_loc_pc 0.356 toward chance 0.25 when the correlated sibling is also corrupted -- needs >=1 clean redundant sibling",
        "grounding_by_redundancy_joint_corruption_allometry_v1 CANONICAL FULL 5-seed 7/13/19/23/29 n_dim=8192 HARD_PASS landed-VET MEASURED_MECHANISM",
    ],
    "added_atom_id": None,
}
atom1["added_atom_id"] = atom1["id"]

# ---------------------------------------------------------------------------
# ATOM 2 -- exact-ID numeric join go/no-go HF_STRUCTURAL_BOUND
# ---------------------------------------------------------------------------
atom2 = {
    "id": (
        "math::HF_STRUCTURAL_BOUND_grounded_ingest_tail_join_v1_bulk_NUMERIC_literal_grounding_wikidata_"
        "quantity_claims_via_EXACT_ID_join_reaches_only_1p8pct_9of500_of_the_substrates_sparse_tail_HARD_"
        "FAIL_vs_5pct_floor_15pct_pass_bar_the_tail_is_NON_NUMERIC_verb_phrase_lemmas_abstract_relations_"
        "WN_synsets_taxonomic_leaves_of_123_matched_QID_entities_only_9_carry_any_quantity_claim_7p3pct_114_"
        "carry_none_377_missing_1p8pct_is_a_LOSSY_KEY_FLOOR_62p6pct_of_misses_casing_hyphen_redirect_"
        "suppressible_NOT_total_reach_BUT_numeric_conclusion_SURVIVES_perfect_key_7p3pct_qty_carry_caps_"
        "absolute_reach_and_realistically_3to6pct_much_less_than_15pct_scramble_control_0_0_0_fires_source_"
        "sha256_match_True_snapshot_identity_ok_CROSSWALK_REVIVAL_CLOSED_no_lemma_to_QID_on_any_on_disk_"
        "source_DO_NOT_build_numeric_literal_fusion_pipeline_redirect_grounding_content_type_to_TEXT_GLOSS_"
        "wordnet_wiktionary_revival_criterion_acquire_lemma_to_external_numeric_ID_crosswalk_head_7ca96dede_"
        "2026-07-14"
    ),
    "name": (
        "MATH HF_STRUCTURAL_BOUND: bulk NUMERIC-literal grounding (Wikidata quantity claims) via exact-ID "
        "join reaches only ~1.8% (9/500) of the substrate's sparse tail (HARD_FAIL vs 5% floor / 15% pass "
        "bar). The tail is NON-NUMERIC (verb-phrase lemmas, abstract relations, WN synsets, taxonomic "
        "leaves): of 123 matched-QID entities only 9 (7.3%) carry any quantity claim. => DO NOT build the "
        "numeric literal-fusion pipeline; redirect grounding content-type to TEXT/GLOSS (WordNet/Wiktionary). "
        "HONEST BOUND: 1.8% is a LOSSY-KEY floor (62.6% of misses casing/hyphen/redirect-suppressible), NOT "
        "total reach -- but the numeric conclusion SURVIVES a perfect key (7.3% qty-carry caps absolute reach "
        "~3-6% << 15%). Crosswalk-revival path CLOSED (no lemma->QID on any on-disk source)."
    ),
    "corpus": "math",
    "tier": "HF_STRUCTURAL_BOUND",
    "kind": "experiment_landed_vet",
    "cert_status": (
        "confirmed_hard_fail_structural_bound_bulk_numeric_literal_grounding_via_exact_id_join_reaches_only_"
        "1p8pct_of_sparse_tail_the_tail_is_non_numeric_of_matched_entities_only_7p3pct_carry_quantity_claims_"
        "lossy_key_floor_not_total_reach_but_numeric_conclusion_survives_perfect_key_3to6pct_much_less_than_"
        "15pct_do_not_build_numeric_literal_fusion_pipeline_redirect_to_text_gloss_crosswalk_revival_closed"
    ),
    "cert_class": (
        "grounded_ingest_bulk_numeric_literal_fusion_reach_go_no_go_wikidata_quantity_claim_exact_enwiki_"
        "sitelink_id_join_over_sparse_support1_lexical_tail_with_scramble_control_and_snapshot_identity_hash_"
        "structural_negative_non_numeric_tail"
    ),
    "description": (
        "Independent adversarial off-disk landed-VET (.venv, AUDIT-ONLY) of "
        "exp_grounded_ingest_tail_join_v1 (run_mode=full; verdict HARD_FAIL; 500 units cardinality_ok). "
        "Recomputed off per_entity[] in metrics.json + provenance.json (NOT verdict_msg, Fix #28). GO/NO-GO "
        "QUESTION: can bulk MEASURED-NUMERIC sources (Wikidata quantity claims, e.g. P2067 mass / P1082 "
        "population / P2046 area) ground the substrate's sparse tail via an EXACT enwiki-sitelink-title -> "
        "QID join (NO fuzzy search)? ANSWER: NO. join_hit_rate = 9/500 = 1.80% (HARD_FAIL vs 5% floor; 15% "
        "pass bar). Of 123 matched-QID entities only 9 carry any quantity-typed claim (7.3%); 114 matched "
        "carry NONE; 377 miss the exact join entirely. The tail is dominated by NON-NUMERIC entities "
        "(verb-phrase lemmas, abstract relations, WN synsets, rare taxonomic leaves, proper nouns) with no "
        "measured-data analog. HONEST BOUND (the load-bearing caveat): 1.8% is a LOSSY-KEY FLOOR, not total "
        "reach -- 240/377 = 63.7% of misses are casing/hyphen/multiword/redirect-suppressible (provenance "
        "states 62.6%, consistent), so a smarter key would recover more MATCHES. BUT the NUMERIC conclusion "
        "SURVIVES a perfect key: only 7.3% of matched entities carry any quantity claim, so even resolving "
        "every one of the 500 caps absolute numeric reach at ~7.3% and realistically lands ~3-6% -- still << "
        "the 15% pass bar. CONTROLS: scramble_control hit-rates [0.0, 0.0, 0.0] over 3 repeats (a scrambled "
        "title yields ZERO spurious quantity hits -> the join is not matching noise; the negative is "
        "SUBSTANTIVE, not a broken query); source_graph_sha256 matches expected (snapshot_identity_check_ok "
        "= True) so the sampled population is the pinned substrate. CROSSWALK-REVIVAL PATH IS CLOSED: there "
        "is no lemma->QID crosswalk on any on-disk source, so the miss cannot be closed from local data. "
        "IMPLICATION: DO NOT build the numeric literal-fusion pipeline (Phase 1-3) on this basis; the next "
        "grounding channel is GLOSS/DEFINITION TEXT (WordNet/Wiktionary), NOT numeric literals. TIER = "
        "HF_STRUCTURAL_BOUND -- a genuine substantive structural negative (positive/scramble control fires, "
        "snapshot identity verified, HARD_FAIL is about the TAIL's content-type not a test-design failure), "
        "with an explicit revival criterion."
    ),
    "provenance": {
        "cell": "experiments/exp_grounded_ingest_tail_join_v1.py",
        "commit": REPO_HEAD,
        "commit_note": "cell metrics/provenance carry no own commit; repo HEAD at atomize",
        "metrics_path": "data/exp_grounded_ingest_tail_join_v1/metrics.json",
        "provenance_path": "data/exp_grounded_ingest_tail_join_v1/provenance.json",
        "run_mode": "full",
        "expected_n_units": 500,
        "n_units_measured": 500,
        "cardinality_ok": True,
        "whole_cell_verdict": "HARD_FAIL",
        "audit_tier": "HF_STRUCTURAL_BOUND",
        "ts_iso": TS_ISO,
        "atomized_by": ATOMIZED_BY,
        "verified_off_data": True,
        "verified_off_data_note": (
            "Independent .venv recompute off per_entity[] + provenance.json (500 units). n_hit=9 -> hit_rate "
            "0.0180; matched-QID(found)=123, of which quantity-carrying=9 (7.3%), no-quantity=114; missing="
            "377; suppressible-key misses (casing/hyphen/multiword/redirect heuristic) 240/377=63.7% "
            "(provenance states 62.6%). Perfect-key ceiling: 7.3% qty-carry -> ~3-6% absolute reach << 15%. "
            "scramble_control control_hit_rates [0.0,0.0,0.0] (3 repeats). source_graph_sha256_match True "
            "(snapshot_identity_check_ok). All reproduce off per_entity."
        ),
    },
    "verified_numbers": {
        "sample_size": 500, "n_hit": 9, "join_hit_rate": 0.018,
        "hard_fail_hit_rate": 0.05, "hard_pass_hit_rate": 0.15,
        "n_matched_qid_found": 123, "n_matched_carry_quantity": 9,
        "frac_matched_carry_quantity": 0.0732, "n_matched_no_quantity": 114,
        "n_missing": 377,
        "suppressible_key_misses": 240, "suppressible_key_miss_frac_recompute": 0.637,
        "suppressible_key_miss_frac_provenance": 0.626,
        "perfect_key_absolute_reach_ceiling": 0.0732, "perfect_key_realistic_reach": "0.03_to_0.06",
        "scramble_control_hit_rates": [0.0, 0.0, 0.0],
        "source_graph_sha256_match": True, "snapshot_identity_check_ok": True,
        "prefix_composition_in_sample": {"CN": 476, "WN": 21, "FN": 3},
        "excluded_nonlexical_tail_count": 400,
    },
    "honest_scope": (
        "HF_STRUCTURAL_BOUND: the negative is about CONTENT-TYPE, not query quality. 1.8% is a LOSSY-KEY "
        "floor (62.6% of misses key-suppressible) so it UNDER-states MATCH reach -- but the NUMERIC reach "
        "conclusion is robust because only 7.3% of matched entities carry any quantity claim, capping "
        "perfect-key numeric reach at ~3-6% << 15%. Scope is the exact-enwiki-sitelink join over the "
        "support<=1 lexical (CN/WN/FN) tail of the pinned snapshot; scramble control fires and the snapshot "
        "hash matches, so this is a substantive structural bound, not a test-design failure."
    ),
    "framing_corrections_vs_cell_author_and_director": [
        "The HARD_FAIL is GENUINE and SUBSTANTIVE, not a test-design failure: the scramble control returns "
        "0/0/0 quantity hits (the join is not matching noise) and the source snapshot hash matches expected "
        "(snapshot_identity_check_ok=True). Positive/negative controls clear before the negative is banked "
        "(auditor discipline: HF must not be a broken test).",
        "HONEST BOUND (do not over-claim the 1.8%): 1.8% is a LOSSY-KEY FLOOR, not total reach -- 63.7% of "
        "misses (provenance 62.6%) are casing/hyphen/multiword/redirect-suppressible, so a better key raises "
        "MATCH rate. The load-bearing point is that the NUMERIC conclusion survives anyway: 7.3% of matched "
        "entities carry any quantity claim, so a perfect key still caps numeric reach at ~3-6% << 15%.",
        "SCOPE the negative precisely: this closes NUMERIC-LITERAL grounding via exact-ID join over the "
        "support<=1 lexical tail. It does NOT close TEXT/GLOSS grounding (the recommended next channel) and "
        "does NOT close numeric grounding for HIGH-support head entities (out of this sample's scope; the "
        "sample is deliberately support<=1 tail).",
        "REVIVAL is gated on an EXTERNAL artifact: the crosswalk-revival path is CLOSED on-disk (no "
        "lemma->QID mapping on any local source). Revival criterion = 'acquire a lemma->external-numeric-ID "
        "crosswalk'; absent that, numeric literal-fusion stays a proven structural non-starter for this tail.",
    ],
    "revival_or_extension_criterion": (
        "REVIVAL criterion (HF_STRUCTURAL_BOUND): acquire a lemma->external-numeric-ID crosswalk (e.g. a "
        "lemma->QID or lemma->measured-attribute mapping not present on any on-disk source). Even WITH a "
        "perfect exact-key, numeric reach is capped ~3-6% (7.3% qty-carry among matches), so a revival must "
        "ALSO show that the crosswalk reaches entities that actually CARRY quantity claims -- not merely more "
        "QIDs. DO NOT re-run the numeric literal-fusion probe on this tail without such a crosswalk. "
        "REDIRECT (the actionable output): grounding content-type -> TEXT/GLOSS (WordNet gloss / Wiktionary "
        "definition) which the NON-NUMERIC lemma/synset/verb-phrase tail DOES have; that is the next "
        "grounding channel to test."
    ),
    "composes": [],
    "compose_note": (
        "Novel go/no-go structural bound; no parent atom superseded. Relates thematically to the grounding "
        "arc (grounding-by-redundancy MM this same session, and the substrate-has-zero-grounded-data "
        "finding) by supplying the DATA-SOURCE constraint: the sparse tail's content-type is non-numeric, so "
        "the grounding CONTENT channel must be TEXT/GLOSS not numeric literals. Uses the Wikidata action-API "
        "join method previously ratified (substrate_ratify_wikidata_action_api_v1) as its exact-ID join "
        "mechanism."
    ),
    "cross_arc_overlap_check": (
        "substrate_query 'bulk numeric literal grounding wikidata quantity claim exact ID join sparse tail "
        "reach lexical' -> top cosine 0.293 char-trigram token 'numerical quantity' (wordnet/atoms), 0.2549 "
        "CN_numerical_quantity. NONE at cosine>0.30; no prior arc CELL rediscovery. Clean; consistent with "
        "SUBSTRATE-KNOWS-NOTHING. July-1 INT8-rediscovery pattern does NOT apply."
    ),
    "anchor": "grounded_ingest_tail_join_v1",
    "cell_commit": REPO_HEAD,
    "run_mode": "full",
    "cardinality_ok": True,
    "verified_off_data": True,
    "auditor": "hdi_skunkworks",
    "atomized_by": "hdi_skunkworks",
    "landed_VET_session": SESSION,
    "needs_orchestrator_store_sync": True,
    "ts": TS,
    "ts_iso": TS_ISO,
    "ts_added": TS_ISO,
    "aliases": [
        "bulk numeric-literal grounding (Wikidata quantity claims) via exact-ID join reaches only ~1.8% (9/500) of the sparse tail -- HARD_FAIL vs 5% floor / 15% pass bar; the tail is NON-NUMERIC",
        "of 123 matched-QID entities only 9 (7.3%) carry any quantity claim -> perfect key still caps numeric reach ~3-6% << 15%",
        "1.8% is a LOSSY-KEY floor (62.6% of misses casing/hyphen/redirect-suppressible) NOT total reach -- but numeric conclusion survives",
        "DO NOT build the numeric literal-fusion pipeline; redirect grounding content-type to TEXT/GLOSS (WordNet/Wiktionary). Crosswalk-revival CLOSED on-disk",
        "grounded_ingest_tail_join_v1 exact-ID numeric join go/no-go landed-VET HF_STRUCTURAL_BOUND; revival = acquire lemma->external-numeric-ID crosswalk",
    ],
    "added_atom_id": None,
}
atom2["added_atom_id"] = atom2["id"]

# ---------------------------------------------------------------------------
# Ledger rows
# ---------------------------------------------------------------------------
ledger1 = {
    "ts": TS, "ts_iso": TS_ISO, "op": "cert_ruling", "atom_id": atom1["id"], "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "cert_status": atom1["cert_status"],
    "cert_class": atom1["cert_class"],
    "anchor": "grounding_by_redundancy_joint_corruption_allometry_v1",
    "cell_commit": REPO_HEAD,
    "store_head_at_write": "unsynced_needs_orchestrator",
    "verified_off_data": (
        "Independent .venv recompute off per_seed[] (5/5, 20 units) on the CANONICAL FULL. FULL corr_gain "
        "[0.320,0.385,0.188,0.367,0.244] mean 0.301 cv 0.247; FULL loc 0.800 vs NO_REDUNDANCY 0.431 chance "
        "0.250; det_auc 0.870. NO_REDUNDANCY+SCRAMBLE corr NEG 5/5; WRONG_EXP agg -0.055 neg 4/5. "
        "FULL-vs-MARGINAL loc +0.113 (min-seed +0.062). PARTNER-CORRUPT full_loc_pc 0.356 -> chance."
    ),
    "auditor": "hdi_skunkworks", "atomized_by": "hdi_skunkworks",
    "verdict": "HARD_PASS_upheld_as_MEASURED_MECHANISM",
    "cert_increment_delta": {"CG": 0, "MM": 1, "HF": 0},
    "cv": 0.247,
    "decision": "bank_MEASURED_MECHANISM_genuine_ground_by_consistency_that_fixes_the_predictor_clean_coupling_artifact_proven_bound",
    "framing_correction_vs_director": (
        "'all must-fails collapse 5/5' overstates WRONG_EXP -- off per_seed NO_REDUNDANCY+SCRAMBLE collapse "
        "5/5 but WRONG_EXP is beaten agg -0.055 and neg only 4/5 (seed 23 +0.061). FULL-vs-MARGINAL loc is "
        "+0.113 agg (request's +0.078 = seed-7); min-seed +0.062, thin confirmed. Partner-corrupt diagnostic "
        "reproduces full_loc_pc 0.356 (request cited ~0.375), report-only, collapses toward chance."
    ),
    "caveat": (
        "MEASURED_MECHANISM proven bound: real leak-free ground-by-consistency but thin over strong no-law "
        "baselines, noisy gain (cv 0.247), WRONG_EXP beaten-not-collapsed, and localization -> ~chance when "
        "the correlated sibling is co-corrupted (needs >=1 clean redundant sibling)."
    ),
    "answer_to_crux": (
        "YES redundancy grounds by consistency when >=1 sibling stays clean, and it correctly FIXES the "
        "earlier predictor-clean coupling artifact -- but it is a proven bound (MM), not a CG capability win."
    ),
    "net_cert_delta": {"CG": 0, "MM": 1, "HF": 0},
    "cross_arc_overlap_check": (
        "top cosine 0.3223 lexical token 'consistency'; cross_modal_consistency note 0.2998 (<0.30, diff "
        "mechanism). No prior arc CELL rediscovery >0.30. Genuine amend of predecessor coupling-artifact atom."
    ),
    "composes": [PRED_COUPLING_ARTIFACT],
    "needs_orchestrator_store_sync": True,
    "referent_pointer": "data/exp_grounding_by_redundancy_joint_corruption_allometry_v1/metrics.json",
    "landed_VET_session": SESSION,
}

ledger2 = {
    "ts": TS, "ts_iso": TS_ISO, "op": "cert_ruling", "atom_id": atom2["id"], "corpus": "math",
    "tier": "HF_STRUCTURAL_BOUND",
    "cert_status": atom2["cert_status"],
    "cert_class": atom2["cert_class"],
    "anchor": "grounded_ingest_tail_join_v1",
    "cell_commit": REPO_HEAD,
    "store_head_at_write": "unsynced_needs_orchestrator",
    "verified_off_data": (
        "Independent .venv recompute off per_entity[] + provenance.json (500 units). n_hit=9 hit_rate 0.0180 "
        "(HARD_FAIL vs 0.05 floor / 0.15 bar). matched-QID 123, quantity-carrying 9 (7.3%), no-quantity 114, "
        "missing 377. Suppressible-key misses 240/377=63.7% (provenance 62.6%). Perfect-key numeric reach "
        "ceiling ~3-6% << 15%. scramble_control [0,0,0] fires; source_sha256_match True."
    ),
    "auditor": "hdi_skunkworks", "atomized_by": "hdi_skunkworks",
    "verdict": "HARD_FAIL_confirmed_structural_bound",
    "cert_increment_delta": {"CG": 0, "MM": 0, "HF": 1},
    "cv": None,
    "decision": "bank_HF_STRUCTURAL_BOUND_do_not_build_numeric_literal_fusion_pipeline_redirect_grounding_to_text_gloss",
    "framing_correction_vs_director": (
        "1.8% is a LOSSY-KEY FLOOR (63.7% of misses key-suppressible, provenance 62.6%), NOT total reach -- "
        "but numeric conclusion SURVIVES perfect key because only 7.3% of matched entities carry any quantity "
        "claim, capping reach ~3-6% << 15%. HF is SUBSTANTIVE: scramble control 0/0/0 fires and snapshot hash "
        "matches, so not a test-design failure."
    ),
    "caveat": (
        "Scope = exact-enwiki-sitelink numeric-literal join over support<=1 lexical (CN/WN/FN) tail of the "
        "pinned snapshot. Does NOT close TEXT/GLOSS grounding or head-entity numeric grounding. Crosswalk-"
        "revival CLOSED on-disk (no lemma->QID)."
    ),
    "answer_to_crux": (
        "NO -- bulk numeric-literal grounding cannot reach the sparse tail; the tail is non-numeric (7.3% "
        "qty-carry among matches). Redirect grounding content-type to TEXT/GLOSS."
    ),
    "net_cert_delta": {"CG": 0, "MM": 0, "HF": 1},
    "cross_arc_overlap_check": (
        "top cosine 0.293 lexical token 'numerical quantity'; NONE >0.30; no prior arc cell rediscovery. Clean."
    ),
    "composes": [],
    "needs_orchestrator_store_sync": True,
    "referent_pointer": "data/exp_grounded_ingest_tail_join_v1/metrics.json",
    "landed_VET_session": SESSION,
}


def append_jsonl_a5(path: Path, new_row: dict, label: str) -> int:
    pre_lines = []
    if path.exists():
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
        assert parsed_back.get("id") == new_row.get("id")
    if "atom_id" in new_row:
        assert parsed_back.get("atom_id") == new_row.get("atom_id")
    out_text = "\n".join(pre_lines + [new_line]) + "\n"
    tmp_path = path.with_suffix(path.suffix + ".tmp_a5")
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(out_text)
        f.flush()
        os.fsync(f.fileno())
    for _attempt in range(10):
        try:
            os.replace(str(tmp_path), str(path))
            break
        except PermissionError:
            if _attempt == 9:
                raise
            time.sleep(0.1 * (2 ** _attempt))
    with open(path, "r", encoding="utf-8") as f:
        post_lines = f.read().splitlines()
    post_count = len(post_lines)
    print(f"[A5] {label}: post_count={post_count}")
    assert post_count == pre_count + 1
    tail = json.loads(post_lines[-1])
    if "id" in new_row:
        assert tail["id"] == new_row["id"]
    if "atom_id" in new_row:
        assert tail["atom_id"] == new_row["atom_id"]
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
    print(f"[A5] atomize START {ATOMIZED_BY} ts={TS:.3f}")
    print(f"[A5] predecessor coupling-artifact atom (ATOM1 composes/amends): {PRED_COUPLING_ARTIFACT[:90]}...")
    append_jsonl_a5(MATH_ATOMS, atom1, "math/atoms (ATOM1 grounding-by-redundancy MEASURED_MECHANISM)")
    append_jsonl_a5(MATH_ATOMS, atom2, "math/atoms (ATOM2 tail-join HF_STRUCTURAL_BOUND)")
    append_jsonl_a5(CERT_LEDGER, ledger1, "cert_ledger (ATOM1 MM +1)")
    append_jsonl_a5(CERT_LEDGER, ledger2, "cert_ledger (ATOM2 HF +1)")
    print("[A5] DONE OK -> ATOM1 MEASURED_MECHANISM (MM +1), ATOM2 HF_STRUCTURAL_BOUND (HF +1)")
    print("[A5] needs_orchestrator_store_sync=True on all 4 rows; NO origin push this turn")
    print(f"[A5] ATOM1_ID={atom1['id']}")
    print(f"[A5] ATOM2_ID={atom2['id']}")


if __name__ == "__main__":
    main()
