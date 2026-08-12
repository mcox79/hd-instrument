"""
A5-gated atom-write: ground-by-LAW consistency (allometry) landed-VET (2026-07-14).

Adversarial off-disk landed-VET (.venv, AUDIT-ONLY) of a WANTED-POSITIVE. CLAIMED HARD_PASS
(5 seeds): ground-by-LAW detects corrupted (AUC 0.999 vs no-law 0.717), corrects (+0.833 vs
-0.584), imputes cold tail (LAW +0.978 vs RELATIONAL -1.513, degree-invariant); must-fails
(wrong-exp, scramble) collapse. Proposed as the convergence's sparse-tail grounding bottleneck-fix.

INDEPENDENT RECOMPUTE (.venv, off data/exp_.../metrics.json per_seed + the real mammal dataset,
NOT verdict_msg; Fix #28):
  - Aggregates reproduce BIT-EXACT: law_auc 0.99922, rel_auc 0.71745, law_imp_cold 0.97792,
    wrong_imp 0.46643, scr_auc 0.51445 -- all match metrics.agg to 5 dp.
  - mass<->length pearson(log)=0.9928; data's ACTUAL OLS slope=2.80 (law assumes 3.0); fixed-3.0
    fit R2=0.9805 = the imputation info-ceiling. LAW cold impute R2=0.9779 (== ceiling), interior
    0.9764. RELATIONAL cold collapse reproduced -1.39 (metrics 5-seed avg -1.51).

DISPOSITION: DOWNGRADE the grounding-lever FRAMING, bank as MEASURED_MECHANISM (proven bound).
The cell is CORRECTLY SCORED vs its own pre-registered gates (every gate genuinely fires, controls
fire), but the CRUX -- flagged by exp_dev -- resolves against the "genuine grounding" reading:

  THE WIN IS A PREDICTOR-CLEAN, SAME-SOURCE-COUPLING ARTIFACT.
  (1) In BOTH detection/correction AND imputation ONLY the TARGET (mass) is corrupted/held-out;
      the PREDICTOR (length) is ALWAYS clean. Adversarial recompute: apply the cell's OWN corruption
      magnitude (shift 0.8-1.5 dex) to the PREDICTOR instead -> LAW cold R2 collapses 0.978 ->
      +-0.30 dex 0.337, +-0.60 dex -1.554 (BELOW the RELATIONAL floor -1.39 it was beating),
      +-1.00 dex -6.02. The lever holds ONLY while a highly-correlated sibling attribute is clean.
  (2) The HARD_PASS is carried ENTIRELY by the headline law mass_from_length (pearson-log 0.993,
      near-tautological geometric isometry; impute R2 0.978 AT the 0.98 ceiling). The gate uses
      law0 only. The two GENUINE (moderate-corr) allometric laws do NOT support the general claim:
      gestation_from_mass fit 0.47 -> impute 0.484 (BELOW the 0.50 bar); lifespan_from_mass fit
      0.43 -> impute 0.518 (barely). So "one law grounds MANY" is not demonstrated -- only the
      near-tautological pair clears.
  (3) "Degree-invariant" is TRUE but TRIVIAL/structural: the LAW arm is a GLOBAL closed-form
      regression that ignores the graph entirely, so cold (0.978) ~= interior (0.976) BY
      CONSTRUCTION, not an emergent grounding property. The genuinely-measured fact is the
      RELATIONAL cold-tail collapse (-1.39) -- a re-confirmation of the already-known sparse-tail
      connectivity bottleneck, not a new grounding capability.
  (4) "5-seed robust" is vacuous on the imputation axis: law_imp_cold is BIT-IDENTICAL
      (0.9779217198496859) across all 5 seeds -- imputation runs on true data with no per-seed
      randomness -> cv=0 trivially. Only detection AUC carries real seed variance (0.997-1.000).
  (5) Must-fails DO fire genuinely (scramble AUC 0.514, wrong-exp impute 0.466 << LAW 0.978) so it
      is NOT a pure regularizer -- BUT wrong-exp uses slope 1.0, far from the data's actual OLS 2.80;
      the must-fail proves "a correlated predictor with roughly-right scaling helps", NOT that THE
      specific allometric exponent value is load-bearing.

TIER: MEASURED_MECHANISM. The proven bound is REAL and reproduces exactly: cross-attribute
law-consistency = clean-anchor cross-attribute regression that detects/corrects/imputes a
corrupted-or-missing target ONLY in the predictor-clean regime, and only clears the bar for a
near-tautological attribute pair. It is a construction-proof of "redundant clean sibling attribute
+ known scaling = imputable value", NOT a genuine degree-invariant grounding lever for the
connectivity-limited sparse tail. cert_increment_delta=1 (proven boundary). Downgrades the
grounding-lever framing (symmetric anti-negativity). No new META (application of existing
disciplines: construction-proof-not-capability-win; verify-off-data; predictor-clean coupling).

Writes: 1 math atom (MEASURED_MECHANISM) + 1 cert_ledger row. needs_orchestrator_store_sync=True.
A5: read -> build -> tmp write + fsync -> os.replace -> re-read + verify count delta + tail ID match.
"""

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
MATH_ATOMS = ROOT / "data/substrate_index/math/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"
ATOMIZED_BY = "skunkworks_landed_vet_grounding_law_consistency_allometry_2026-07-14"
ATOMIZED_DATE = "2026-07-14"

ANCHOR = "grounding_law_consistency_allometry_v1"
METRICS = "data/exp_grounding_law_consistency_allometry_v1/metrics.json"
CELL = "experiments/exp_grounding_law_consistency_allometry_v1.py"
CELL_COMMIT = "UNKNOWN_local_full_no_commit_captured"
STORE_HEAD_AT_WRITE = "unsynced_needs_orchestrator"

atom = {
    "id": ("math::MEASURED_MECHANISM_ground_by_LAW_consistency_allometry_is_a_PREDICTOR_CLEAN_SAME_SOURCE_COUPLING_"
           "artifact_NOT_a_genuine_degree_invariant_grounding_lever_for_the_sparse_tail_cell_CORRECTLY_SCORED_HARD_PASS_"
           "vs_own_gates_and_all_aggregates_reproduce_BIT_EXACT_law_auc_0p999_law_imp_cold_0p978_scr_auc_0p514_off_disk_"
           "BUT_in_BOTH_detection_correction_AND_imputation_ONLY_the_TARGET_mass_is_corrupted_or_heldout_the_PREDICTOR_"
           "length_is_ALWAYS_clean_adversarial_recompute_applying_the_cells_OWN_corruption_magnitude_0p8_to_1p5_dex_to_"
           "the_PREDICTOR_collapses_LAW_cold_R2_from_0p978_to_neg1p55_BELOW_the_RELATIONAL_floor_neg1p39_it_was_beating_"
           "AND_the_HARD_PASS_is_carried_ENTIRELY_by_the_headline_mass_from_length_pearson_log_0p993_near_tautological_"
           "isometry_impute_at_the_0p98_ceiling_while_the_two_GENUINE_moderate_corr_allometric_laws_gestation_0p484_"
           "BELOW_the_0p50_bar_lifespan_0p518_barely_do_NOT_support_the_general_claim_and_degree_invariance_is_STRUCTURAL_"
           "the_LAW_arm_is_a_GLOBAL_regression_that_ignores_the_graph_so_cold_0p978_equals_interior_0p976_by_construction_"
           "not_emergent_and_5seed_robustness_is_VACUOUS_on_imputation_law_imp_cold_bit_identical_all_5_seeds_cv_0_uses_"
           "true_data_no_randomness_mustfails_DO_fire_scramble_0p514_wrongexp_0p466_so_not_a_pure_regularizer_but_wrong_"
           "exp_slope_1p0_is_far_from_the_data_OLS_2p80_so_it_proves_a_correlated_predictor_with_roughly_right_scaling_"
           "helps_NOT_the_specific_exponent_value_5seed_7_13_19_23_29_FULL_mammal_taxonomy_64sp_2026-07-14"),
    "name": ("MATH MEASURED_MECHANISM (DOWNGRADE the grounding-lever framing; bank as proven bound): ground-by-LAW "
             "consistency on mammal allometry is a PREDICTOR-CLEAN, SAME-SOURCE-COUPLING artifact, NOT a genuine "
             "degree-invariant grounding lever for the connectivity-limited sparse tail. The cell is CORRECTLY SCORED "
             "HARD_PASS vs its own pre-registered gates and every aggregate reproduces BIT-EXACT off-disk (law_auc "
             "0.99922, law_imp_cold 0.97792, rel_auc 0.71745, wrong_imp 0.46643, scr_auc 0.51445). BUT the crux "
             "(flagged by exp_dev) resolves against 'genuine grounding': (1) in BOTH detection/correction AND "
             "imputation only the TARGET (mass) is corrupted/held-out; the PREDICTOR (length) is ALWAYS clean -- "
             "adversarial recompute applying the cell's OWN corruption magnitude (0.8-1.5 dex) to the PREDICTOR "
             "collapses LAW cold R2 from 0.978 to -1.55 (BELOW the RELATIONAL floor -1.39 it beat). (2) The HARD_PASS "
             "is carried ENTIRELY by the headline law mass_from_length (pearson-log 0.993, near-tautological geometric "
             "isometry, impute R2 0.978 AT the 0.98 fit-ceiling); the gate uses law0 only. The two GENUINE moderate-"
             "correlation allometric laws do NOT support the general claim (gestation impute 0.484 BELOW the 0.50 bar; "
             "lifespan 0.518 barely). (3) 'Degree-invariant' is TRUE but STRUCTURAL/trivial -- the LAW arm is a global "
             "closed-form regression that ignores the graph, so cold 0.978 == interior 0.976 by construction, not an "
             "emergent property; the genuinely-measured fact is the RELATIONAL cold-tail collapse (-1.39), a re-"
             "confirmation of the known sparse-tail bottleneck. (4) '5-seed robust' is VACUOUS on imputation: "
             "law_imp_cold is BIT-IDENTICAL (0.9779217198496859) across all 5 seeds (true data, no per-seed randomness, "
             "cv=0); only detection AUC carries real variance (0.997-1.000). (5) Must-fails DO fire (scramble AUC 0.514, "
             "wrong-exp impute 0.466) so NOT a pure regularizer -- but wrong-exp slope 1.0 is far from the data's actual "
             "OLS 2.80, so it proves 'a correlated predictor with roughly-right scaling helps', not THE specific "
             "allometric exponent. PROVEN BOUND: cross-attribute law-consistency = clean-anchor cross-attribute "
             "regression, useful only in the predictor-clean regime and only for near-tautological pairs. 5 seeds "
             "[7,13,19,23,29] FULL mammal taxonomy 64 species."),
    "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "kind": "experiment_landed_vet",
    "cert_status": ("confirmed_measured_mechanism_ground_by_law_consistency_is_predictor_clean_same_source_coupling_"
                    "artifact_correctly_scored_hard_pass_reproduces_bit_exact_controls_fire_but_win_holds_only_while_"
                    "predictor_clean_carried_by_near_tautological_mass_length_pair_degree_invariance_structural_not_"
                    "emergent_not_a_grounding_lever_for_the_sparse_tail_downgrade_framing_bank_proven_bound"),
    "cert_class": ("cross_attribute_law_consistency_grounding_detection_correction_imputation_allometric_scaling_law_"
                   "predictor_clean_coupling_regime_degree_invariant_by_global_regression_construction"),
    "description": (
        "Independent adversarial off-disk landed-VET (.venv). Recomputed aggregates from metrics.json per_seed AND "
        "reimplemented the fit / LOO-intercept / imputation / RELATIONAL LOO from scratch against the REAL mammal "
        "dataset (load_mammals), NOT from verdict_msg (Fix #28).\n\n"
        "AGGREGATES REPRODUCE BIT-EXACT: law_auc 0.99922, rel_auc 0.71745, law_imp_cold 0.97792, wrong_imp_cold "
        "0.46643, scr_auc 0.51445 -- all identical to metrics.agg to 5 dp. cardinality_ok (15 units = 5 seeds x 3 "
        "laws). Data integrity clean.\n\n"
        "NEAR-TAUTOLOGY CONFIRMED: mass<->length pearson(log10)=0.9928. The data's ACTUAL free OLS slope is 2.80 "
        "(R2 0.9856); the 'law' assumes 3.0 (fixed-3.0 median-intercept fit R2 0.9805 = the imputation info-ceiling). "
        "LAW cold-tail impute R2 reproduces 0.9779 (== ceiling), interior 0.9764. RELATIONAL cold collapse reproduces "
        "-1.39 (metrics 5-seed avg -1.51); RELATIONAL interior 0.685.\n\n"
        "THE CRUX (exp_dev flag: genuine grounding vs same-source coupling) -- RESOLVED as COUPLING ARTIFACT. Read of "
        "the corruption + imputation protocol: in task (a) detection/correction, corrupt_logvals corrupts logy (the "
        "TARGET, mass) only, and law_resid(logx_true, slope) uses the CLEAN predictor length. In task (b) imputation, "
        "imp_pred[LAW] = slope*logx_true + b_loo_true uses CLEAN true length; only the target mass is held out. So the "
        "PREDICTOR is clean in EVERY arm. ADVERSARIAL RECOMPUTE: apply the cell's OWN corruption magnitude (shift "
        "0.8-1.5 dex, sign random) to the PREDICTOR (length) for cold-tail entities, then impute -> LAW cold R2 "
        "collapses: +-0.30 dex -> 0.337, +-0.60 dex -> -1.554 (BELOW the RELATIONAL floor -1.39 it was beating), "
        "+-1.00 dex -> -6.02. The lever holds ONLY while a highly-correlated sibling attribute stays clean; the moment "
        "the predictor carries the same noise as the target, the win inverts to a below-relational loss. This is a "
        "predictor-clean (same-source-coupling) tautology, not robust grounding.\n\n"
        "GENERALITY FAILS: the HARD_PASS gate uses HEADLINE_LAW=mass_from_length only. That is the near-tautological "
        "pair (r 0.993). The two GENUINE moderate-correlation allometric laws do NOT clear the general claim: "
        "gestation_from_mass fit R2 0.47 -> cold impute 0.4845 (BELOW the 0.50 HP bar); lifespan_from_mass fit R2 0.43 "
        "-> cold impute 0.5181 (barely). So 'one law grounds many values' is NOT demonstrated -- only the near-"
        "tautological attribute pair produces the headline number.\n\n"
        "DEGREE-INVARIANCE IS STRUCTURAL, NOT EMERGENT: the LAW arm is a global closed-form regression (fixed slope + "
        "LOO-median intercept) that structurally ignores taxonomic degree, so cold (0.978) ~= interior (0.976) BY "
        "CONSTRUCTION. The only genuinely-measured empirical fact is the RELATIONAL cold-tail collapse (-1.39), which "
        "re-confirms the already-established connectivity-limited sparse-tail bottleneck, not a new grounding lever.\n\n"
        "ROBUSTNESS CLAIM VACUOUS ON IMPUTATION: law_imp_cold is BIT-IDENTICAL (0.9779217198496859) in every one of the "
        "5 seeds -- imputation runs on true data with no per-seed randomness, so cv=0 is trivial, not evidence of "
        "robustness. Only detection AUC carries genuine seed variance (per-seed 0.9974/1.0/0.9987/1.0/1.0, tight).\n\n"
        "MUST-FAILS FIRE (genuine, not a pure regularizer): scramble detection AUC 0.514 (~chance), scramble corr "
        "-2.74, scramble impute -2.07; wrong-exp impute 0.466 << LAW 0.978. So a shuffled predictor / degraded law "
        "does NOT help -- the entity-pairing is load-bearing. CAVEAT: wrong-exp uses slope 1.0, far from the data's "
        "actual OLS slope 2.80, and fixed-3.0 (0.9805) barely beats free-fit (0.9856) -- so the exact exponent is NOT "
        "finely load-bearing; the must-fail proves 'a correlated predictor with roughly-right scaling helps', not "
        "'THE specific allometric exponent value is the grounding'.\n\n"
        "TIER: MEASURED_MECHANISM (proven bound). The bound is REAL and reproduces exactly: cross-attribute law-"
        "consistency detects/corrects/imputes a corrupted-or-missing TARGET attribute better than no-law baselines and "
        "is degree-invariant -- but ONLY in the predictor-clean regime, and the HARD_PASS-clearing magnitude requires a "
        "near-tautological (r~0.99) attribute pair. It is a construction-proof of 'redundant clean sibling attribute + "
        "known scaling = imputable value', NOT a genuine degree-invariant grounding lever for the sparse tail. "
        "cert_increment_delta=1 (proven boundary). This DOWNGRADES the director/cell 'grounding bottleneck-fix' framing "
        "(symmetric anti-negativity). REVIVAL: (a) corrupt ALL attributes jointly (predictor + target) and test whether "
        "cross-law CONSISTENCY over a redundant multi-law system can still localize which value is wrong -- that would "
        "be genuine grounding-by-redundancy, untested here; (b) find/ingest genuinely moderate-correlation laws where "
        "the sibling is not near-tautological and show a real sparse-tail lift; (c) test the case where the predictor "
        "itself is a sparse-tail (missing) attribute (the actual bottleneck), not a clean interior anchor."
    ),
    "aliases": [
        "ground-by-law consistency allometry is a predictor-clean same-source-coupling artifact not genuine grounding",
        "adversarial predictor-corruption collapses LAW cold R2 0.978 to -1.55 below relational floor at cells own corruption magnitude",
        "HARD_PASS carried entirely by near-tautological mass-length pair r0.993 two genuine allometric laws fail the bar",
        "degree-invariance is structural global regression ignores graph cold equals interior by construction not emergent",
        "5-seed imputation robustness vacuous bit-identical every seed cv0 true data no randomness must-fails fire but exponent not finely load-bearing",
    ],
    "metadata": {
        "provenance_quality": "MEASURED_MECHANISM_DOWNGRADE_grounding_lever_framing_cell_correctly_scored_aggregates_reproduce_bit_exact_but_predictor_clean_coupling_artifact",
        "cert_status": "confirmed_measured_mechanism_predictor_clean_coupling_not_grounding_lever_downgrade_framing",
        "cert_class": "cross_attribute_law_consistency_predictor_clean_coupling_degree_invariant_by_global_regression",
        "verdict_cell": "HARD_PASS",
        "verdict_scored_correctly_vs_own_gates": True,
        "grounding_lever_framing": "DOWNGRADED_predictor_clean_same_source_coupling_artifact_not_a_sparse_tail_grounding_fix",
        "skunkworks_adjudication": "DOWNGRADE_framing_bank_MEASURED_MECHANISM_proven_bound_win_holds_only_predictor_clean_and_near_tautological_pair",
        "anchor": ANCHOR,
        "cell_commit": CELL_COMMIT,
        "store_head_at_write": STORE_HEAD_AT_WRITE,
        "metrics_path": METRICS,
        "cell_path": CELL,
        "verified_off_data": (
            "Aggregates reproduce BIT-EXACT off per_seed (.venv): law_auc 0.99922, rel_auc 0.71745, law_imp_cold "
            "0.97792, wrong_imp 0.46643, scr_auc 0.51445. Reimplemented fit/LOO/impute/relational from scratch vs "
            "real load_mammals: pearson(log mass,length)=0.9928, OLS slope 2.80, fixed-3.0 fit R2 0.9805, LAW cold "
            "impute 0.9779, RELATIONAL cold -1.39. ADVERSARIAL predictor-corruption (cell's own 0.8-1.5 dex on "
            "length): LAW cold R2 0.337 / -1.554 / -6.021 at +-0.30/0.60/1.00 dex -> collapses below relational floor. "
            "law_imp_cold bit-identical (0.9779217198496859) all 5 seeds. Cross-arc overlap check (substrate_query "
            "'ground by law consistency degree invariant imputation sparse tail allometry'): top hits research NOTES "
            "at cosine<=0.268 (attribution self-consistency note, engram sparse-allocation note), NO prior certified "
            "experiment atom at cosine>0.30; BUT the cert_ledger mammal-taxonomy grounding arc (grounding CARRIES "
            "leakfree heldout RELATION placement MM 0.618 but 68pct entity-prior; concreteness degree-invariant "
            "grounding MM tail-survives-but-HIGH-washes) is the DIRECTLY related lineage -- same over-framing pattern "
            "(grounded channel wins but decomposes / is scoped), consistent with MM not CG."
        ),
        "honest_scope": (
            "CONFIRMS a REAL, reproduced, control-clean proven bound: cross-attribute law-consistency detects/corrects/"
            "imputes a corrupted-or-missing TARGET attribute over no-law baselines and is degree-invariant -- but ONLY "
            "when the PREDICTOR attribute is clean, and the HARD_PASS magnitude requires a near-tautological (r~0.99) "
            "attribute pair (mass<->length geometric isometry). NOT a genuine degree-invariant grounding lever for the "
            "connectivity-limited sparse tail: the win inverts to below-relational loss when the predictor carries "
            "equal noise, the two genuine moderate-correlation allometric laws fail the bar, and degree-invariance is "
            "a structural property of a global regression, not emergent grounding."
        ),
        "n_seeds": 5, "seeds": [7, 13, 19, 23, 29],
        "run_mode": "full", "expected_n_units": 15, "n_units": 15, "cardinality_ok": True,
        "corpus": "mammal_taxonomy_64species_18order_41family_5clade",
        "metrics": {
            "law_auc": 0.99922, "best_nolaw_auc": 0.71745, "rel_auc": 0.71745, "marg_auc": 0.58490,
            "wrong_auc": 0.72630, "scr_auc": 0.51445,
            "law_corr": 0.83287, "best_nolaw_corr": -0.58401, "wrong_corr": -0.65132, "scr_corr": -2.73728,
            "law_imp_cold": 0.97792, "rel_imp_cold": -1.51321, "mean_imp_cold": -0.39319, "rand_imp_cold": -0.96346,
            "wrong_imp_cold": 0.46643, "scr_imp_cold": -2.06774,
            "law_imp_interior": 0.97643, "rel_imp_interior": 0.68585,
            "l1_fit_r2_fixed_slope_3p0": 0.98053,
            "pearson_log_mass_length": 0.9928, "ols_free_slope": 2.80, "ols_free_r2": 0.9856,
            "hp_law_imp_r2_bar": 0.50, "hp_law_auc_bar": 0.85,
        },
        "per_law_cold_imputation_vs_0p50_bar": {
            "mass_from_length": {"law_imp_cold": 0.9779, "fit_r2": 0.9805, "pearson_log": 0.993, "clears_bar": True, "headline_gate_uses_this": True},
            "gestation_from_mass": {"law_imp_cold": 0.4845, "fit_r2": 0.4686, "clears_bar": False},
            "lifespan_from_mass": {"law_imp_cold": 0.5181, "fit_r2": 0.4307, "clears_bar": "barely"},
        },
        "adversarial_predictor_corruption_probe": {
            "protocol": "apply cell's own corruption magnitude (shift 0.8-1.5 dex, sign random) to PREDICTOR (length) on cold-tail entities, then LAW-impute mass",
            "law_cold_r2_at_shift": {"clean_baseline": 0.9779, "0p30_dex": 0.3371, "0p60_dex": -1.5541, "1p00_dex": -6.0208},
            "relational_cold_floor_it_beat": -1.39,
            "conclusion": "at the cell's OWN corruption magnitude on the predictor, LAW collapses BELOW the relational floor -> predictor-clean coupling artifact",
        },
        "predictor_always_clean_in_all_arms": True,
        "hard_pass_carried_entirely_by_near_tautological_mass_length_pair": True,
        "degree_invariance_is_structural_global_regression_not_emergent": True,
        "five_seed_imputation_robustness_vacuous_bit_identical_cv0_true_data_no_randomness": True,
        "must_fails_fire_but_exponent_value_not_finely_load_bearing_slope1p0_vs_data_ols_2p80": True,
        "aggregates_reproduce_bit_exact_off_disk": True,
        "controls_clean_scramble_collapses_positive_control_law_auc_fires": True,
        "revival_criteria": [
            "corrupt_ALL_attributes_jointly_predictor_plus_target_and_test_whether_cross_law_redundancy_can_still_localize_the_wrong_value_genuine_grounding_by_redundancy_untested",
            "find_or_ingest_genuinely_moderate_correlation_laws_non_tautological_sibling_and_show_real_sparse_tail_lift",
            "test_case_where_the_predictor_itself_is_a_sparse_tail_missing_attribute_the_actual_bottleneck_not_a_clean_interior_anchor",
        ],
        "composes_with": [
            "MEASURED_MECHANISM_grounding_CARRIES_leakfree_heldout_RELATION_placement_mammal_taxonomy_0p618_but_68pct_entity_prior (same arena, same over-framing-then-decompose pattern)",
            "MEASURED_MECHANISM_first_FAIR_positive_grounding_concreteness_degree_invariant_tail_survives_but_HIGH_washes_MM_not_CG (degree-invariant grounding scoped to MM)",
            "project_grounding_needs_active_intervention_exogenous_referent_3source (a baked-in law is borrowed external info, not internal bootstrapping -- cell docstring concurs)",
            "feedback_construction_proof_is_not_a_capability_win_ask_could_it_fail_informatively (imputation R2 = the correlation is fully implied by design)",
        ],
        "cites": [
            "Fix_28_verify_off_data_not_verdict_msg",
            "symmetric_anti_negativity_verify_both_directions_USER",
            "feedback_construction_proof_is_not_a_capability_win_ask_could_it_fail_informatively",
            "feedback_mechanism_analog_is_not_task_analog_supervised_synthetic_corpus_is_supervised_regime",
            "reference_correlation_hurts_associative_store_capacity_decouple_from_retrieval",
            "substrate_kb_concept_overlap_check_on_schema_vet_USER_locked_2026-07-01",
        ],
        "atomized_by": ATOMIZED_BY,
        "atomized_date": ATOMIZED_DATE,
        "needs_orchestrator_store_sync": True,
    },
}

ts = time.time()
_iso = datetime.now(timezone.utc).isoformat()
atom["ts_iso"] = _iso
atom["ts"] = ts

ledger = {
    "op": "cert_ruling",
    "ts_iso": _iso,
    "ts": ts,
    "atom_id": atom["id"],
    "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "cert_status": atom["cert_status"],
    "cert_class": atom["cert_class"],
    "anchor": ANCHOR,
    "cell_commit": CELL_COMMIT,
    "store_head_at_write": STORE_HEAD_AT_WRITE,
    "verified_off_data": True,
    "auditor": "hdi_skunkworks",
    "atomized_by": ATOMIZED_BY,
    "verdict": ("HARD_PASS_scored_correctly_vs_own_gates_aggregates_reproduce_bit_exact_but_grounding_lever_framing_"
                "DOWNGRADED_to_MEASURED_MECHANISM_predictor_clean_same_source_coupling_artifact_win_inverts_below_"
                "relational_floor_when_predictor_carries_equal_noise_carried_by_near_tautological_mass_length_pair"),
    "cert_increment_delta": 1,
    "cv": {"law_imp_cold_crossseed_cv_VACUOUS_bit_identical": 0.0, "det_auc_crossseed_genuine": 0.001,
           "aggregates_reproduce_bit_exact": True},
    "decision": (
        "DOWNGRADE the grounding-lever framing; bank MEASURED_MECHANISM (proven bound). The cell is CORRECTLY SCORED "
        "HARD_PASS vs its own pre-registered gates and every aggregate reproduces BIT-EXACT off-disk (law_auc 0.99922, "
        "law_imp_cold 0.97792, scr_auc 0.51445); controls fire (scramble collapses, positive control law_auc fires). "
        "BUT the crux resolves against 'genuine grounding': in BOTH detection/correction AND imputation only the TARGET "
        "(mass) is corrupted/held-out; the PREDICTOR (length) is ALWAYS clean. Adversarial recompute applying the "
        "cell's OWN corruption magnitude (0.8-1.5 dex) to the predictor collapses LAW cold R2 from 0.978 to -1.55 "
        "(below the relational floor -1.39 it beat). The HARD_PASS is carried entirely by the headline near-"
        "tautological mass<->length pair (pearson-log 0.993); the two genuine moderate-correlation allometric laws "
        "fail the bar (gestation 0.484<0.50; lifespan 0.518 barely). Degree-invariance is structural (global "
        "regression ignores graph, cold==interior by construction). 5-seed imputation robustness is vacuous (bit-"
        "identical, cv=0). Must-fails fire but wrong-exp slope 1.0 vs data OLS 2.80 -> proves 'correlated predictor "
        "with roughly-right scaling helps', not the specific exponent."
    ),
    "framing_correction_vs_director": (
        "CLAIMED 'HARD_PASS ground-by-LAW: LAW_AUC 0.999, impute cold LAW +0.978 vs REL -1.513 degree-invariant, the "
        "convergence's proposed sparse-tail grounding bottleneck-fix' -- the NUMBERS are all real and reproduce bit-"
        "exact, but the STRATEGIC framing is over-stated on five axes: (1) it is a PREDICTOR-CLEAN result -- both "
        "detection and imputation keep the predictor (length) clean and corrupt only the target (mass); at the cell's "
        "own corruption magnitude on the PREDICTOR the LAW inverts to -1.55, BELOW the relational floor. (2) The win "
        "is carried entirely by the near-tautological mass<->length pair (r 0.993, impute at the 0.98 ceiling); the "
        "two GENUINE allometric laws do NOT clear the bar, so 'one law grounds many' is not shown. (3) 'Degree-"
        "invariant' is structural/trivial (global regression), not emergent grounding; the only new measured fact is "
        "the relational cold collapse, a re-confirmation of the known sparse-tail bottleneck. (4) '5-seed robust' is "
        "vacuous on imputation (bit-identical across seeds). (5) Must-fails fire but the specific exponent is not "
        "finely load-bearing (slope 1.0 vs data OLS 2.80). ANSWER TO CRUX: SAME-SOURCE-COUPLING artifact (predictor-"
        "clean tautology), NOT a genuine degree-invariant grounding lever -- so as the convergence's proposed sparse-"
        "tail bottleneck-fix it is NOT supported by this cell."
    ),
    "caveat": ("MEASURED_MECHANISM proven bound is real and reproduces exactly; +1 as a proven boundary, NOT as the "
               "claimed grounding capability win. Not a DEMOTE (fresh landing, no prior chain-grade disproven)."),
    "answer_to_crux": (
        "SAME-SOURCE-COUPLING ARTIFACT (predictor-clean tautology). Ground-by-law is NOT a genuine degree-invariant "
        "grounding lever for the connectivity-limited sparse tail: it is a clean-anchor cross-attribute regression "
        "that wins only because a 0.993-correlated predictor (length) is held clean, only clears the HARD_PASS bar for "
        "the near-tautological mass<->length pair, and inverts to below-relational-floor loss (-1.55) the moment the "
        "predictor carries the same noise the target does. Its degree-invariance is a structural property of a global "
        "regression, not emergent grounding. It is a construction-proof of 'redundant clean sibling attribute + known "
        "scaling = imputable value', banked as a proven bound (MEASURED_MECHANISM), not the proposed bottleneck-fix."
    ),
    "net_cert_delta": "+1 (proven BOUND: cross-attribute law-consistency = clean-anchor predictor-clean regression on near-tautological pairs; NOT a sparse-tail grounding capability win).",
    "cross_arc_overlap_check": ("substrate_query top hits research NOTES cosine<=0.268 (no prior cert experiment atom at "
                                ">0.30); but cert_ledger mammal-taxonomy grounding arc (relation-placement MM 0.618/68pct-"
                                "prior; concreteness degree-invariant MM tail-survives-HIGH-washes) is the directly-related "
                                "lineage -- same win-but-decompose/scope pattern, MM consistent."),
    "needs_orchestrator_store_sync": True,
    "referent_pointer": {"metrics_path": METRICS, "cell_path": CELL, "atom_qualified_id": atom["id"]},
}


def write_atomic_append(path, new_lines):
    if not path.exists():
        return (0, 0, False, "path does not exist: %s" % path)
    with open(path, "rb") as f:
        cur_bytes = f.read()
    cur_text = cur_bytes.decode("utf-8")
    pre_count = cur_text.count("\n")
    if cur_bytes and not cur_bytes.endswith(b"\n"):
        cur_bytes = cur_bytes + b"\n"
    parts = [cur_bytes]
    for line in new_lines:
        s = json.dumps(line, ensure_ascii=True)
        if "\n" in s:
            return (pre_count, pre_count, False, "JSON contains newline; not jsonl-safe")
        parts.append((s + "\n").encode("utf-8"))
    new_bytes = b"".join(parts)
    tmp_path = path.with_suffix(path.suffix + ".tmp_a5")
    with open(tmp_path, "wb") as f:
        f.write(new_bytes); f.flush(); os.fsync(f.fileno())
    os.replace(tmp_path, path)
    with open(path, "rb") as f:
        verify_text = f.read().decode("utf-8")
    post_count = verify_text.count("\n")
    expected_post = pre_count + len(new_lines)
    if post_count != expected_post:
        return (pre_count, post_count, False, "line count mismatch: expected %d got %d" % (expected_post, post_count))
    tail = verify_text.rstrip("\n").split("\n")[-len(new_lines):]
    for i, tl in enumerate(tail):
        try:
            parsed = json.loads(tl)
        except Exception as e:
            return (pre_count, post_count, False, "tail-line %d JSON round-trip fail: %s" % (i, e))
        for key in ("id", "atom_id"):
            if key in new_lines[i] and parsed.get(key) != new_lines[i][key]:
                return (pre_count, post_count, False, "tail-line %d %s mismatch" % (i, key))
    return (pre_count, post_count, True, "OK")


def main():
    print("=== A5 atom-write: ground-by-LAW consistency allometry MEASURED_MECHANISM (2026-07-14) ===")
    print("ts_iso =", _iso)
    print()
    print("Writing 1 atom to math/atoms.jsonl ...")
    pre, post, ok, err = write_atomic_append(MATH_ATOMS, [atom])
    print("  pre=%d post=%d ok=%s err=%s" % (pre, post, ok, err))
    if not ok or post - pre != 1:
        print("ABORT: math atoms write failed"); sys.exit(1)

    print("Writing 1 row to meta/cert_ledger.jsonl ...")
    pre, post, ok, err = write_atomic_append(CERT_LEDGER, [ledger])
    print("  pre=%d post=%d ok=%s err=%s" % (pre, post, ok, err))
    if not ok or post - pre != 1:
        print("ABORT: cert_ledger write failed"); sys.exit(1)

    print()
    print("=== A5 WRITE COMPLETE ===")
    for p in (MATH_ATOMS, CERT_LEDGER):
        with open(p, "rb") as f:
            n = f.read().count(b"\n")
        print("  %s: %d lines" % (p.name, n))
    print()
    print("CERT N delta: +1 MEASURED_MECHANISM (proven bound; grounding-lever framing DOWNGRADED). No new META.")
    print("needs_orchestrator_store_sync = True")
    print("atom_id =", atom["id"][:90], "...")


if __name__ == "__main__":
    main()
