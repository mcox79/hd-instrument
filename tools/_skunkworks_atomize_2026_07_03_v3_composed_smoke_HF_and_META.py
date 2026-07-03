"""
A5-gated atomization for landed VET of exp_substrate_composed_encoder_v3_smoke_2026_07_03.
Session 2026-07-03. Skunkworks landed-VET, off-disk recompute per Fix#28.

LANDING SUMMARY (per-arm off metrics.json, N=100, n_dim=2048, 3 seeds 11/17/23):
  ARM_V3_COMPOSED_EQUAL_ALPHA r@5 mean = 0.3333  (per-seed: 0.34/0.33/0.33)
  ARM_VWFA_ALONE r@5 mean            = 0.2400   (per-seed: 0.23/0.25/0.24)
  ARM_PPMI_ALONE r@5 mean            = 0.3400   (per-seed: 0.34/0.34/0.34, bit-flat)
  ARM_V1_CONCEPT_ENCODER r@5 mean    = 0.1600   (HP3 exact match to prior)
  ARM_CHAR_TRIGRAM r@5 mean          = 0.2800   (HP4 exact match to prior)
  cardinality_ok=15/15, arms_differ_verified=True, hp6_vwfa_identity_ok, hp6_ppmi_identity_ok

VERDICT: HARD_FAIL. v3=0.3333 < max(VWFA=0.240, PPMI=0.340) = 0.340 by 0.007.
  Per-seed differences v3-PPMI = [0.00, -0.01, -0.01] -- systematic direction (2/3 strictly below,
  1/3 equal). PPMI is bit-identical 0.34 across all seeds; v3 sits at or below.
  0.333 is above naive-average (0.24+0.34)/2 = 0.29 but below best-single (0.34):
  composition does SOMETHING useful (better than naive avg) but strictly hurts vs best single spoke.
  NOT razor-thin noise: 1 query = 0.01 at N=100, but per-seed direction is consistent.

CROSS-ARC OVERLAP CHECK (2026-07-01 discipline): the "PPMI beats char-trigram by +0.06 at r@5"
finding IS THE SAME NUMBER as V2-A precedent (exp_substrate_concept_encoder_v2_A_ppmi_svd_sparse
smoke 2026-07-03: v2a_r5=0.34 vs ct_r5=0.28 = +0.06). V2-A FULL landed as MIDDLE_BAND with
v2a_r5=0.272 vs ct_r5=0.260 = +0.012 (discriminator shrank at scale).
=> Cell-author's "first-ever mechanism win on WordNet" framing is INCORRECT. PPMI-alone at
   smoke is a REDISCOVERY of V2-A, not a novel finding. Not filing PPMI-alone as new CG.

Two atoms filed:
  (a) HF_CG on v3 equal-alpha composition (SUPERVISED WordNet lexicon N=100 smoke asymmetric-strength scope)
  (b) META MM on COMPOSITION_AT_EQUAL_ALPHA_DILUTES_ASYMMETRIC_STRENGTH_STREAMS (mechanism characterization)
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
COMMIT = "114a0f3cf"

# ============= ATOM (a): HF on v3 equal-alpha composition =============
atom_hf = {
    "id": "math::T3/EXP_substrate_composed_encoder_v3_smoke_2026_07_03_HARD_FAIL_HF1_COMPOSITION_HURTS_v3_equal_alpha_r5_0p3333_below_max_spoke_PPMI_r5_0p3400_by_0p007_VWFA_r5_0p2400_ARM_PPMI_ALONE_r5_0p3400_bit_identical_across_3_seeds_ARM_V3_COMPOSED_r5_0p3333_per_seed_0p34_0p33_0p33_ARM_VWFA_ALONE_r5_0p2400_ARM_V1_CONCEPT_ENCODER_r5_0p1600_HP3_exact_ARM_CHAR_TRIGRAM_r5_0p2800_HP4_exact_composition_sits_above_naive_avg_0p29_below_best_single_0p34_composition_does_something_but_strictly_hurts_best_spoke_scope_SUPERVISED_WordNet_lexicon_N_100_smoke_single_word_queries_equal_alpha_weighting_only_NOT_a_claim_composition_impossible_scope_extension_criterion_adaptive_alpha_or_learned_weights_HF_genuine_not_razor_thin_per_seed_direction_consistent_2_of_3_below_1_of_3_equal_PPMI_arm_reproduces_V2A_precedent_smoke_r5_0p34_which_landed_MIDDLE_BAND_at_FULL_0p272_predicting_same_discriminator_narrowing_at_scale_2026-07-03",
    "name": "EXP substrate_composed_encoder_v3 smoke HARD_FAIL (equal-alpha composition strictly hurts vs best spoke on asymmetric-strength streams; SUPERVISED WordNet N=100 smoke scope)",
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record",
    "description": (
        "Experiment record: exp_substrate_composed_encoder_v3_smoke_2026_07_03. Cell tests brain-analog "
        "VWFA + PPMI score-level late-combine (equal-alpha=0.5) against single-spoke baselines on WordNet "
        "synonym-retrieval (N=100 lexicon atoms, single-word queries, 3 seeds 11/17/23, n_dim=2048). "
        "HARD_FAIL per prereg HF1: v3_r5=0.3333 < max(VWFA=0.240, PPMI=0.340) = 0.340 by delta=-0.007. "
        "Per-seed v3-PPMI diffs = [0.00, -0.01, -0.01]: systematic direction, 2/3 seeds strictly below, "
        "1/3 equal. PPMI is bit-flat 0.34 across all seeds. v3=0.333 sits above naive-mean-of-spokes "
        "(0.24+0.34)/2=0.29 but below best-single 0.34: composition IS doing structured work (rescues "
        "from naive average) but strictly hurts vs best individual spoke. Auditor concurs HF classification "
        "is genuine, NOT razor-thin noise despite delta=0.007 < 1_query_res=0.01 at N=100 (per-seed "
        "direction is consistent). Baseline reproductions exact per HP3/HP4: v1=0.160 (HP3), "
        "char-trigram=0.280 (HP4). All meta_rules touched: AF_arms_differ, AG_baseline_in_band, "
        "AH_atomic_final_metrics, K_discriminator_fires, L_strict_above_floor, M_calibration_default_ok, "
        "H_cardinality_ok, run_mode_verification_16. Cardinality 15/15, arms_differ_verified. "
        "SCOPE: SUPERVISED WordNet lexicon N=100 smoke, single-word queries, equal-alpha weighting. "
        "NOT a claim that 'composition doesn't work' -- adaptive-alpha (fit_weights_grid_2spoke exists) "
        "NOT tested; multi-token queries (Wikipedia) NOT tested. Revival criterion: adaptive-alpha v3 "
        "variant that dynamically down-weights weaker spoke, OR multi-token-query regime where VWFA "
        "position-binding has actual phrase-position signal. USER-LOCKED framing: substrate knows almost "
        "nothing; this HF characterizes a specific composition-weighting failure on supervised regime, "
        "NOT a general capability finding."
    ),
    "aliases": [],
    "metadata": {
        "record_class": "experiment_record",
        "term_class": "PROCESS_KNOWLEDGE_NON_MATH",
        "metric_type": "recall_at_5_wordnet_synonym_retrieval",
        "experiment_path": "experiments/exp_substrate_composed_encoder_v3_smoke_2026-07-03.py",
        "prereg_path": "preregs/2026-07-03_substrate_composed_encoder_v3_smoke.md",
        "metrics_paths": ["data/exp_substrate_composed_encoder_v3_smoke_2026_07_03_smoke/metrics.json"],
        "cell_sha": COMMIT,
        "remote_run_id": None,
        "verdict": "HARD_FAIL_HF1_COMPOSITION_HURTS",
        "run_mode": "smoke",
        "provenance_quality": "CG_HONEST_NEGATIVE",
        "relevance_tier": "HIGH",
        "era": "STAGE_2_CONCEPT_ENCODER_ARC_2026-07-02",
        "cert_status": "chain_grade_honest_negative",
        "cert_class": "equal_alpha_composition_strictly_hurts_best_spoke_on_asymmetric_strength_streams_supervised_wordnet_scope",
        "verified_off_data": True,
        "atomized_by": "skunkworks_landed_VET_2026-07-03_v3_composed_smoke",
        "cert_ts": TS_ISO,
        "n_seeds": 3,
        "seeds": [11, 17, 23],
        "n_dim": 2048,
        "N_atoms": 100,
        "run_mode": "smoke",
        "cardinality_ok": True,
        "arms_differ_verified": True,
        "arm_r5_means": {
            "v3_composed_equal_alpha": 0.3333,
            "vwfa_alone": 0.2400,
            "ppmi_alone": 0.3400,
            "v1_concept_encoder_cosine": 0.1600,
            "char_trigram_unsup_reference": 0.2800
        },
        "per_seed_v3_r5": [0.34, 0.33, 0.33],
        "per_seed_ppmi_r5": [0.34, 0.34, 0.34],
        "per_seed_vwfa_r5": [0.23, 0.25, 0.24],
        "hf_delta_v3_minus_max_spoke": -0.0067,
        "naive_avg_of_spokes_r5": 0.29,
        "composition_rescues_from_naive_avg_but_hurts_best_single": True,
        "hp3_v1_exact_reproduction": True,
        "hp4_trigram_exact_reproduction": True,
        "hp6_vwfa_identity_ok_all_seeds": True,
        "hp6_ppmi_identity_ok_all_seeds": True,
        "razor_thin_check": "delta=0.007 < 1_query_res=0.01 at N=100 BUT per-seed direction consistent (2/3 strictly below, 1/3 equal); PPMI bit-flat 0.34 all seeds; v3 varies 0.33-0.34. HF is genuine.",
        "auditor_framing_correction_vs_cell_author": (
            "Cell-author framed ARM_PPMI_ALONE=0.340 as 'first-ever substrate-native mechanism to beat "
            "char-trigram bag on WordNet-synonym retrieval'. Auditor OFF-DATA cross-check: this reproduces "
            "V2-A precedent exp_substrate_concept_encoder_v2_A_ppmi_svd_sparse_2026_07_03 smoke r5=0.34 vs "
            "ct=0.28 = +0.06 IDENTICALLY. V2-A FULL landed as MIDDLE_BAND at r5=0.272 vs ct=0.260 = +0.012. "
            "PPMI-alone is NOT a novel mechanism win; it is a rediscovery of V2-A smoke result. Not filing "
            "a fresh CG for PPMI-alone. Cell-author scope-tightness on HF verdict was correct; framing "
            "of PPMI as new was over-claim."
        ),
        "supersedes": None,
        "composes_with": [
            "V2A_ppmi_svd_sparse_smoke_HARD_PASS_2026-07-03_r5_0p34",
            "V2A_ppmi_svd_sparse_FULL_MIDDLE_BAND_2026-07-03_r5_0p272_delta_0p012",
            "brain_analog_VWFA_position_binding_5x_drill_2026-07-02"
        ],
        "cites": [
            "Fix_28_verify_per_arm_not_verdict_msg",
            "USER_locked_substrate_knows_almost_nothing_2026-07-02",
            "cross_arc_overlap_check_pre_atomization_2026-07-01"
        ],
        "revival_criterion": "adaptive-alpha v3 variant (fit_weights_grid_2spoke) that dynamically down-weights weaker spoke, OR multi-token-query regime (Wikipedia titles/body) where VWFA position-binding may have phrase-position signal",
        "cert_increment_delta": 1
    }
}

# ============= ATOM (b): META rule COMPOSITION_AT_EQUAL_ALPHA_DILUTES_ASYMMETRIC_STRENGTH_STREAMS =============
atom_meta = {
    "id": "meta::T2/META_COMPOSITION_AT_EQUAL_ALPHA_DILUTES_ASYMMETRIC_STRENGTH_STREAMS_MM_TENTATIVE_when_two_spokes_have_asymmetric_individual_strength_gap_ge_0p10_at_the_task_regime_equal_alpha_score_level_late_combine_produces_composition_score_above_naive_arithmetic_mean_of_spokes_but_strictly_below_best_single_spoke_witnessed_at_v3_composed_encoder_smoke_2026_07_03_VWFA_r5_0p24_PPMI_r5_0p34_gap_0p10_equal_alpha_composition_r5_0p333_naive_avg_0p29_best_single_0p34_composition_rescues_from_naive_by_0p043_but_hurts_best_by_0p007_mechanism_class_ensemble_dilution_at_equal_weighting_on_asymmetric_learners_standard_ensembling_lemma_but_first_evidenced_in_substrate_score_level_bind_scope_wordnet_supervised_single_word_query_regime_at_n_dim_2048_expansion_criterion_witness_at_different_regime_e_g_multi_token_query_wikipedia_and_confirm_adaptive_alpha_recovers_best_or_better_promote_to_CG_META_if_holds_across_2_more_regimes_2026-07-03",
    "name": "META COMPOSITION_AT_EQUAL_ALPHA_DILUTES_ASYMMETRIC_STRENGTH_STREAMS (MM_TENTATIVE): equal-alpha score-level late-combine of asymmetric-strength spokes sits above naive-mean but strictly below best-single",
    "corpus": "meta",
    "tier": "T2",
    "kind": "methodology_rule_mechanism_characterization",
    "description": (
        "META rule characterization (MM_TENTATIVE tier, single-cell witness): when two spokes have "
        "asymmetric individual strength (per-arm-alone metric gap >= 0.10 at the task regime), equal-alpha "
        "score-level late-combine produces a composition score ABOVE the naive arithmetic mean of the "
        "spokes but STRICTLY BELOW the best single spoke. First witness: v3_composed_encoder smoke "
        "2026-07-03 on WordNet synonym retrieval r@5: VWFA_alone=0.24, PPMI_alone=0.34, gap=0.10; "
        "equal-alpha composition=0.333, naive_avg=0.29, best_single=0.34. Composition rescues from "
        "naive by +0.043 but hurts best by -0.007. Mechanism class: this is a standard ensembling "
        "lemma (weak-learner ensembles hurt strong-learner performance when mixed at equal weight), "
        "but first empirically evidenced in substrate score-level late-combine of HRR-scale bind. "
        "SCOPE: WordNet-supervised single-word-query regime at n_dim=2048; witnessed in one cell. "
        "NOT a general claim across all task regimes or all HRR-bind topologies. Expansion criterion "
        "to CG_META: witness at 2 more independent regimes (multi-token Wikipedia queries; different "
        "gap magnitude) AND confirm adaptive-alpha (fit_weights_grid_2spoke) recovers best-single or "
        "better on same regime -- would establish the rule holds AND the fix works. Absent expansion, "
        "MM tier because single-cell mechanism-class characterization is not yet cross-regime. "
        "Directly informs Director's next step: adaptive-alpha v3 variant."
    ),
    "aliases": [],
    "metadata": {
        "record_class": "methodology_rule",
        "term_class": "COMPOSITION_ENSEMBLING_LEMMA",
        "cert_status": "measured_mechanism_tentative_synthesis",
        "cert_class": "MM_TENTATIVE_SYNTHESIS_single_cell_witness",
        "cert_ts": TS_ISO,
        "verified_off_data": True,
        "atomized_by": "skunkworks_landed_VET_2026-07-03_v3_composed_smoke_META",
        "witness_cells": [
            {
                "cell_id": "exp_substrate_composed_encoder_v3_smoke_2026_07_03",
                "task_regime": "wordnet_synonym_retrieval_single_word_queries_n_dim_2048_N_100_smoke",
                "spokes": {"VWFA_alone": 0.24, "PPMI_alone": 0.34, "gap": 0.10},
                "composition_equal_alpha": 0.333,
                "naive_avg_of_spokes": 0.29,
                "best_single_spoke": 0.34,
                "composition_rescues_from_naive_by": 0.043,
                "composition_hurts_best_by": -0.007
            }
        ],
        "gap_threshold_for_asymmetry": 0.10,
        "mechanism_class": "ensemble_dilution_at_equal_weighting_on_asymmetric_learners_score_level_late_combine_HRR_scale_bind",
        "standard_lemma_novelty": "standard ensembling lemma (equal-weight mixing of asymmetric learners hurts best); FIRST empirically evidenced in substrate score-level late-combine bind, not a new theoretical framing but load-bearing for future spoke-fusion design",
        "expansion_criterion_to_CG_META": (
            "witness at >=2 more independent regimes (e.g., multi-token Wikipedia queries; different "
            "gap magnitudes) AND confirm adaptive-alpha (fit_weights_grid_2spoke) recovers best-single "
            "or better on the same regime, establishing rule holds AND fix works"
        ),
        "cites": [
            "witness_atom_v3_composed_encoder_smoke_HF_2026-07-03",
            "brain_analog_VWFA_position_binding_5x_drill_2026-07-02",
            "V2A_ppmi_svd_sparse_smoke_HP_and_FULL_MB_precedent_2026-07-03"
        ],
        "cert_increment_delta": 1
    }
}


def a5_append(path, atom):
    """Atomic append: tmp write + fsync + replace-append via read-write."""
    d = os.path.dirname(path)
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_atomize_", suffix=".jsonl")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            # copy existing
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
    # verify-load
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


def ledger_append(atom, ledger_path=CERT_LEDGER):
    entry = {
        "ts": TS,
        "ts_iso": TS_ISO,
        "atom_id": atom["id"],
        "corpus": atom["corpus"],
        "cert_status": atom["metadata"].get("cert_status"),
        "cert_class": atom["metadata"].get("cert_class"),
        "cert_increment_delta": atom["metadata"].get("cert_increment_delta", 0),
        "verified_off_data": atom["metadata"].get("verified_off_data", False),
        "cell_sha": atom["metadata"].get("cell_sha"),
        "atomized_by": atom["metadata"].get("atomized_by"),
        "landed_VET_session": "2026-07-03_v3_composed_smoke_HF_plus_META",
    }
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
    print(f"[atomize] ts_iso={TS_ISO} commit={COMMIT}")
    n_math = a5_append(MATH_ATOMS, atom_hf)
    print(f"[atomize] math atoms.jsonl now has {n_math} lines; appended HF atom id[:80]={atom_hf['id'][:80]}...")
    n_meta = a5_append(META_ATOMS, atom_meta)
    print(f"[atomize] meta atoms.jsonl now has {n_meta} lines; appended META atom id[:80]={atom_meta['id'][:80]}...")
    ledger_append(atom_hf)
    ledger_append(atom_meta)
    print(f"[atomize] cert_ledger.jsonl updated with 2 entries (HF + META).")
    print(f"[atomize] DONE. CERT delta: +1 CG_HONEST_NEGATIVE (math) +1 MM_TENTATIVE_SYNTHESIS (meta).")
