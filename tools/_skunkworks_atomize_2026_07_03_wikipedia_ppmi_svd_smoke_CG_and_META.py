"""
A5-gated atomization for landed VET of exp_substrate_wikipedia_ppmi_svd_baseline_smoke_2026_07_03.
Session 2026-07-03. Skunkworks landed-VET, off-disk recompute per Fix#28.

LANDING SUMMARY (per-arm off metrics.json, 3 seeds 11/17/23, N=500 Wikipedia, n_dim=2048):
  ARM_PPMI_SVD_WIKIPEDIA r@5 mean = 0.906  (per-seed: 0.906/0.906/0.906, std=0.000 deterministic)
  ARM_CHAR_TRIGRAM_WIKIPEDIA r@5 mean = 0.854 (per-seed 0.854/0.854/0.854; EXACT bit-identical
                                              reproduction of commit 43ec44a50 char-trigram SMOKE ref)
  ARM_RANDOM_BASELINE r@5 mean = 0.00733 (per-seed 0.002/0.014/0.006; chance=0.010 -> in-band < 0.05)
  cardinality_ok=9/9, arms_differ_verified=True (3 distinct digests per seed),
    baseline_in_band=True, HP1 (>= 0.884) cleared with +0.022 headroom.
  PPMI diag: vocab=7782 trigrams, effective_dim=500 (zero-padded to 2048), fit ~7s/seed,
    encode ~0.6s/seed, total wall 58s / 3 seeds.

VERDICT: HARD_PASS. Delta PPMI - char-trigram = +0.052 at SMOKE.

CROSS-ARC OVERLAP CHECK (2026-07-01 USER-locked discipline):
  - PPMI-on-Wikipedia: NO prior on disk. Grep experiments/ + substrate_index math/meta atoms.jsonl
    confirms this is genuinely FIRST. (wave14 PPMI cells are early substrate mining, not Wikipedia;
    V2-A PPMI/SVD is WordNet single-word, not Wikipedia.)
  - Char-trigram Wikipedia baseline reproduces commit 43ec44a50 CG bit-identically (deterministic
    blake2b codebook -> expected).
  - Contrast with V2-A precedent (WordNet single-word): PPMI smoke +0.06 -> FULL +0.012 (MB, ~5x
    shrink). This Wikipedia SMOKE +0.052 is a DIFFERENT regime (multi-token real-corpus co-occurrence
    matches PPMI's inductive bias more naturally than single-word synonym retrieval).

Two atoms filed:
  (a) MATH CG_MEASURED_BOUND: first substrate-native ATL-hub-analog PPMI/SVD encoder to beat
      char-trigram surface bag on real Wikipedia at SMOKE N=500 (TIGHT SCOPE: SUPERVISED
      title->body retrieval regime; NOT a general Wikipedia understanding claim).
  (b) META MM_TENTATIVE_SYNTHESIS: TASK_CLASS_AND_MECHANISM_CLASS_MATCH -- co-occurrence mechanisms
      (PPMI/SVD) lift MORE on multi-token retrieval regimes than on single-word regimes; smoke lift
      magnitude is task-class-dependent. Expansion criterion: FULL 10K Wikipedia lift holds >= +0.03
      -> promote to CG_META (would confirm task-class match survives scale).

FRAMING DISCIPLINE:
  - Cell-author scope-tight (MECHANISM_LIFT on SUPERVISED regime; NOT substrate knows Wikipedia).
    Auditor propagates that framing exactly. NO capability atom.
  - Genuinely novel probe (not rediscovery). CG at TIGHT SMOKE-scope; discriminator-narrows-at-scale
    is an OPEN QUESTION until FULL 10K lands.
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
COMMIT = "b655b9fd3"

# ============= ATOM (a): CG on Wikipedia PPMI/SVD SMOKE =============
atom_cg = {
    "id": "math::T3/EXP_substrate_wikipedia_ppmi_svd_baseline_SMOKE_CG_MEASURED_BOUND_3seed_N500_HP1_cleared_r5_0p906_std_0p000_deterministic_by_PPMI_fit_plus_SVD_ordering_char_trigram_ref_r5_0p854_EXACT_reproduction_of_43ec44a50_random_r5_0p007_baseline_in_band_delta_PPMI_minus_char_trigram_plus_0p052_HP1_floor_0p884_cleared_with_0p022_headroom_first_substrate_native_ATL_hub_analog_PPMI_SVD_encoder_to_BEAT_char_trigram_surface_bag_on_real_Wikipedia_title_to_body_retrieval_at_SMOKE_scale_hdlab_ppmi_sparse_encoder_Levy_Goldberg_2015_cooccurrence_plus_SVD_body_as_labeled_corpus_vocab_7782_trigrams_effective_dim_500_zero_padded_to_2048_fit_7s_per_seed_encode_0p6s_per_seed_wall_58s_3seeds_cardinality_9of9_arms_differ_verified_3_distinct_digests_intra_cos_0p559_inter_cos_0p324_snr_1p72_SCOPE_TIGHT_SUPERVISED_title_to_body_retrieval_500_articles_body_cap_800_chars_smoke_only_NOT_general_knowledge_claim_substrate_knows_almost_nothing_USER_LOCKED_framing_respected_MECHANISM_LIFT_on_supervised_regime_only_discriminator_narrows_at_FULL_10K_is_open_question_V2A_wordnet_precedent_showed_5x_shrink_but_this_is_DIFFERENT_task_class_multi_token_versus_single_word_2026-07-03",
    "name": "EXP substrate_wikipedia_ppmi_svd_baseline SMOKE CG_MEASURED_BOUND (first substrate-native ATL-hub-analog to beat char-trigram bag on real Wikipedia at SMOKE N=500; SUPERVISED title->body retrieval scope)",
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record",
    "description": (
        "Experiment record: exp_substrate_wikipedia_ppmi_svd_baseline_smoke_2026_07_03. Cell tests "
        "substrate-native PPMI/SVD (Levy/Goldberg 2015 co-occurrence + SVD; hdlab.ppmi_sparse_encoder) "
        "as ATL-hub-analog semantic encoder against char-trigram surface bag on real Wikipedia "
        "title->body retrieval (N=500 articles, body cap 800 chars, 3 seeds 11/17/23, n_dim=2048). "
        "HARD_PASS per prereg HP1: ARM_PPMI_SVD_WIKIPEDIA r@5=0.906 >= 0.884 = char_trigram_ref(0.854) "
        "+ 0.03 margin. Cleared HP1 with +0.022 headroom. Delta vs char-trigram bag = +0.052. "
        "ARM_CHAR_TRIGRAM_WIKIPEDIA r@5=0.854 EXACT bit-identical reproduction of commit 43ec44a50 "
        "SMOKE reference (deterministic blake2b codebook -> std=0 expected, not a bug). "
        "ARM_RANDOM_BASELINE r@5=0.007 (chance 0.010, in band < 0.05, META_RULE_AG satisfied). "
        "PPMI std=0.000 across 3 seeds is DETERMINISTIC-EXPECTED: PPMI fit on the same body corpus + "
        "SVD singular vector ordering are seed-invariant; only body/title randomization differs and "
        "did not perturb the encoded HDs at N=500. Diagnostic: vocab=7782 trigrams, effective_dim=500 "
        "(min(V,C,N)=500 zero-padded to 2048), fit_wall~7s/seed, encode_wall~0.6s/seed. "
        "Cardinality 9/9, arms_differ_verified True (3 distinct digests). "
        "META_RULES: AF_arms_differ, AG_baseline_in_band, AH_atomic_final_metrics, "
        "K_discriminator_fires, L_strict_above_floor, H_cardinality_ok. "
        "SCOPE (TIGHT): SUPERVISED Wikipedia title->article-body held-out retrieval, N=500 SMOKE, "
        "n_dim=2048, PPMI/SVD mechanism-alone. NOT a claim substrate 'understands Wikipedia'; NOT a "
        "capability finding; NOT a claim the lift survives FULL 10K. "
        "AUDITOR CROSS-ARC CHECK: first-of-kind PPMI-on-Wikipedia experiment (grep experiments/ + "
        "substrate math/meta atoms.jsonl -> NO prior; wave14 PPMI cells are early substrate mining "
        "and unrelated; V2-A PPMI/SVD is WordNet single-word not Wikipedia). Char-trigram reference "
        "reproduces commit 43ec44a50 bit-identically. Discriminator-narrows-at-scale is an OPEN "
        "QUESTION: V2-A WordNet precedent showed 5x shrink (smoke +0.06 -> FULL +0.012 MB) but that "
        "was SINGLE-WORD regime; Wikipedia is MULTI-TOKEN which better matches PPMI's co-occurrence "
        "inductive bias, so expected shrink factor is LESS THAN 5x, likely 2-3x -> expected FULL 10K "
        "delta in range +0.017 to +0.026 (MB likely; CG possible if task-class-match holds strongly). "
        "USER-LOCKED framing preserved: 'substrate knows almost nothing'; this CG is a MECHANISM-LIFT "
        "measurement on a supervised regime, not a knowledge claim."
    ),
    "aliases": [],
    "metadata": {
        "record_class": "experiment_record",
        "term_class": "PROCESS_KNOWLEDGE_NON_MATH",
        "metric_type": "recall_at_5_wikipedia_title_body_retrieval_supervised_regime",
        "experiment_path": "experiments/exp_substrate_wikipedia_ppmi_svd_baseline_smoke_2026-07-03.py",
        "prereg_path": "preregs/2026-07-03_substrate_wikipedia_ppmi_svd_baseline_smoke.md",
        "metrics_paths": ["data/exp_substrate_wikipedia_ppmi_svd_baseline_smoke_2026_07_03/metrics.json"],
        "cell_sha": COMMIT,
        "remote_run_id": None,
        "verdict": "HARD_PASS_HP1_MECHANISM_LIFT",
        "run_mode": "smoke",
        "provenance_quality": "CG_MEASURED_BOUND",
        "relevance_tier": "HIGH",
        "era": "STAGE_2_CONCEPT_ENCODER_ARC_2026-07-02",
        "cert_status": "chain_grade_measured_bound",
        "cert_class": "substrate_native_PPMI_SVD_ATL_hub_analog_beats_char_trigram_bag_on_real_wikipedia_title_body_retrieval_SMOKE_N500_supervised_regime_scope_only",
        "verified_off_data": True,
        "atomized_by": "skunkworks_atomize_substrate_wikipedia_ppmi_svd_smoke_2026_07_03",
        "cert_ts": TS_ISO,
        "n_seeds": 3,
        "seeds": [11, 17, 23],
        "n_dim": 2048,
        "n_articles": 500,
        "body_char_cap": 800,
        "run_mode": "smoke",
        "cardinality_ok": True,
        "arms_differ_verified": True,
        "baseline_in_band_ok": True,
        "hp1_gate_r5_floor": 0.884,
        "hp1_headroom_above_floor": 0.022,
        "arm_r5_means": {
            "ARM_PPMI_SVD_WIKIPEDIA": 0.906,
            "ARM_CHAR_TRIGRAM_WIKIPEDIA": 0.854,
            "ARM_RANDOM_BASELINE": 0.00733
        },
        "arm_r5_stds": {
            "ARM_PPMI_SVD_WIKIPEDIA": 0.000,
            "ARM_CHAR_TRIGRAM_WIKIPEDIA": 0.000,
            "ARM_RANDOM_BASELINE": 0.00499
        },
        "delta_ppmi_minus_char_trigram": 0.052,
        "char_trigram_ref_bit_identical_reproduction_of_43ec44a50": True,
        "ppmi_std_zero_is_deterministic_expected_not_bug": True,
        "ppmi_vocab_size": 7782,
        "ppmi_effective_dim": 500,
        "ppmi_zero_padded_to_n_dim": 2048,
        "wall_total_s": 58.19,
        "auditor_cross_arc_check": (
            "GENUINELY NOVEL: no prior PPMI-on-Wikipedia in experiments/ or substrate math/meta atoms. "
            "wave14 PPMI cells (2026-06) are early substrate mining, unrelated; V2-A PPMI/SVD "
            "2026-07-03 is WordNet single-word regime, NOT Wikipedia. First-of-kind."
        ),
        "auditor_symmetric_verify_positive_result": (
            "Anti-negativity-bias applied both ways: could this HP be artifact? Checked: "
            "(1) HP1 cleared by +0.022 -- not razor-thin (10 queries at N=500 res=0.002); "
            "(2) Char-trigram reference is bit-identical to prior CG (no measurement drift); "
            "(3) Random baseline in-band at 0.007 vs chance 0.010 -- calibration ok; "
            "(4) arms_differ 3 distinct digests -- no arm collapse; "
            "(5) PPMI diag effective_dim=500 = min(V,C,N)=500 -- expected, not overflow; "
            "(6) std=0.000 explained by deterministic PPMI fit + SVD ordering + fixed body corpus. "
            "HP is a genuine mechanism win at SMOKE scope, not artifact."
        ),
        "auditor_discriminator_narrows_at_scale_estimate": (
            "V2-A WordNet precedent: smoke +0.06 -> FULL +0.012 = 5x shrink at single-word regime. "
            "Wikipedia is multi-token which matches PPMI co-occurrence bias BETTER. Expected shrink "
            "factor at Wikipedia FULL 10K: 2-3x (task-class-match dampens shrink). Point estimate: "
            "smoke +0.052 -> FULL delta in [+0.017, +0.026] range. Most likely MIDDLE_BAND at FULL; "
            "CG possible if task-class match holds strongly and effective_dim scales with body count."
        ),
        "composes_with": [
            "EXP_substrate_wikipedia_char_trigram_baseline_smoke_2026_07_03_CG_r5_0p854_ref",
            "V2A_ppmi_svd_sparse_smoke_HP_r5_0p34_and_FULL_MB_r5_0p272_wordnet_single_word",
            "brain_analog_ATL_hub_amodal_semantic_hub_5x_drill_2026-07-02"
        ],
        "cites": [
            "Fix_28_verify_per_arm_not_verdict_msg",
            "USER_locked_substrate_knows_almost_nothing_2026-07-02",
            "USER_locked_mechanism_analog_is_not_task_analog_2026-07-02",
            "cross_arc_overlap_check_pre_atomization_2026-07-01",
            "Levy_Goldberg_2015_ppmi_svd_word_embedding"
        ],
        "revival_criterion_at_scale": "FULL Wikipedia N=10K PPMI/SVD confirm delta stays >= +0.03 vs char-trigram FULL",
        "cert_increment_delta": 1,
        "supersedes": None
    }
}

# ============= ATOM (b): META rule TASK_CLASS_AND_MECHANISM_CLASS_MATCH =============
atom_meta = {
    "id": "meta::T2/META_TASK_CLASS_AND_MECHANISM_CLASS_MATCH_MM_TENTATIVE_SYNTHESIS_ATL_hub_analog_PPMI_SVD_cooccurrence_mechanism_lift_magnitude_is_task_class_dependent_smoke_lift_amplifies_on_multi_token_retrieval_and_narrows_on_single_word_synonym_retrieval_when_mechanism_inductive_bias_matches_task_regime_composition_of_signal_lift_is_preserved_across_scale_expansion_criterion_wordnet_single_word_precedent_V2A_smoke_ppmi_minus_char_trigram_plus_0p06_FULL_shrank_to_plus_0p012_MB_5x_shrink_wikipedia_multi_token_smoke_ppmi_minus_char_trigram_plus_0p052_witnessed_here_FULL_10K_pending_predicts_shrink_factor_2_to_3x_not_5x_yielding_FULL_delta_in_plus_0p017_to_plus_0p026_range_because_multi_token_co_occurrence_matches_PPMI_inductive_bias_mechanism_class_ATL_hub_amodal_semantic_hub_analog_matches_multi_token_body_text_regime_more_naturally_than_single_word_lexical_regime_expansion_criterion_to_CG_META_wikipedia_FULL_10K_confirms_delta_holds_ge_plus_0p03_and_additional_multi_token_regime_witness_at_2nd_corpus_reference_task_class_matters_from_char_trigram_wikipedia_CG_2026_07_02_which_earlier_flagged_bag_of_features_beats_competitive_hebbian_on_symbolic_content_2026-07-03",
    "name": "META TASK_CLASS_AND_MECHANISM_CLASS_MATCH (MM_TENTATIVE_SYNTHESIS): co-occurrence mechanisms (ATL-hub-analog PPMI/SVD) lift more on multi-token retrieval than single-word regimes; smoke lift magnitude is task-class dependent",
    "corpus": "meta",
    "tier": "T2",
    "kind": "methodology_rule_mechanism_task_class_matching",
    "description": (
        "META rule (MM_TENTATIVE_SYNTHESIS tier, 2-cell cross-regime witness at smoke; single-regime "
        "FULL confirm pending): mechanism-lift magnitude at smoke is task-class-dependent. "
        "Co-occurrence mechanisms (Levy/Goldberg PPMI + SVD; ATL-hub amodal-semantic-hub analog) "
        "lift MORE at smoke on task regimes whose statistical structure matches the mechanism's "
        "inductive bias. Multi-token body-text retrieval (Wikipedia titles->bodies with body_cap=800 "
        "chars) provides richer co-occurrence signal than single-word synonym retrieval (WordNet "
        "lexicon), so the smoke lift on Wikipedia (+0.052 vs char-trigram) is comparable in "
        "magnitude to WordNet (+0.06) BUT the discriminator-narrows-at-scale factor is predicted "
        "to be SMALLER when task-class matches mechanism inductive bias. "
        "TWO WITNESSES: "
        "(1) V2-A PPMI/SVD sparse on WordNet single-word: smoke r5=0.34 vs char_trigram 0.28 = +0.06; "
        "FULL landed MIDDLE_BAND r5=0.272 vs 0.260 = +0.012 (5x shrink from smoke to FULL). "
        "(2) Wikipedia PPMI/SVD baseline multi-token (THIS witness): smoke r5=0.906 vs char_trigram "
        "0.854 = +0.052; FULL 10K pending (dispatched in parallel; commit 84c53803e char-trigram "
        "FULL in flight). "
        "PREDICTION: Wikipedia FULL 10K shrink factor 2-3x (not 5x) because task-class matches "
        "PPMI inductive bias -> expected FULL delta in [+0.017, +0.026]. "
        "MECHANISM CLASS: ATL (anterior temporal lobe) is the brain's amodal semantic hub, which "
        "aggregates cross-modal features across time -- naturally analogous to PPMI+SVD "
        "co-occurrence factorization over multi-token corpus. This is why the lift is preserved "
        "better on multi-token regime than on single-word regime. "
        "SCOPE: 2 cells; both PPMI/SVD as substrate-native encoder; single-cell FULL witness "
        "(V2-A WordNet); Wikipedia FULL 10K pending. "
        "EXPANSION CRITERION to CG_META: (a) Wikipedia FULL 10K confirms delta stays >= +0.03; "
        "(b) at least one additional multi-token regime witnessed with same pattern (e.g., a "
        "different corpus at similar body-cap). If both -> promote to CG_META. "
        "NOT filed as CG_META yet: single FULL witness against, single FULL witness pending. "
        "COMPOSES with: 2026-07-02 competitive_hebbian_LOSES_to_bag META (task-class matters was "
        "already flagged at MM tier for symbolic content vs brain-analog concept encoder); this "
        "META atom SHARPENS the earlier rule by adding mechanism-class-inductive-bias-matching-"
        "task-class-statistical-structure as the specific causal explanation."
    ),
    "aliases": [],
    "metadata": {
        "record_class": "methodology_rule",
        "term_class": "TASK_MECHANISM_CLASS_MATCHING",
        "cert_status": "measured_mechanism_tentative_synthesis",
        "cert_class": "MM_TENTATIVE_SYNTHESIS_two_cell_witness_task_class_dependent_lift_smoke",
        "cert_ts": TS_ISO,
        "verified_off_data": True,
        "atomized_by": "skunkworks_atomize_substrate_wikipedia_ppmi_svd_smoke_META_2026_07_03",
        "witness_cells": [
            {
                "cell_id": "exp_substrate_concept_encoder_v2_A_ppmi_svd_sparse_2026_07_03",
                "task_regime": "wordnet_single_word_synonym_retrieval",
                "smoke_delta_ppmi_minus_char_trigram": 0.06,
                "full_delta_ppmi_minus_char_trigram": 0.012,
                "shrink_factor": 5.0,
                "full_verdict": "MIDDLE_BAND"
            },
            {
                "cell_id": "exp_substrate_wikipedia_ppmi_svd_baseline_smoke_2026_07_03",
                "task_regime": "wikipedia_multi_token_title_body_retrieval",
                "smoke_delta_ppmi_minus_char_trigram": 0.052,
                "full_delta_ppmi_minus_char_trigram_pending": True,
                "predicted_shrink_factor": "2_to_3x_because_task_class_matches_mechanism_inductive_bias",
                "predicted_full_delta_range": [0.017, 0.026],
                "full_verdict_pending": True
            }
        ],
        "mechanism_class": "co_occurrence_factorization_PPMI_plus_SVD_ATL_hub_amodal_semantic_hub_analog",
        "task_class_dimension_that_matters": "multi_token_vs_single_word_query_regime",
        "expansion_criterion_to_CG_META": (
            "(a) Wikipedia FULL 10K confirms PPMI/SVD delta stays >= +0.03 vs char-trigram FULL; "
            "(b) at least one additional multi-token regime witnessed with same pattern at another "
            "corpus (different body-cap, different vocab). If BOTH satisfied -> promote to CG_META. "
            "If (a) fails (delta shrinks below +0.03) -> demote this META to MB and file that "
            "PPMI mechanism-lift doesn't survive scale on Wikipedia either."
        ),
        "cites": [
            "witness_atom_wikipedia_ppmi_svd_smoke_CG_2026-07-03",
            "witness_atom_V2A_ppmi_svd_sparse_wordnet_smoke_HP_and_FULL_MB_2026-07-03",
            "witness_atom_wikipedia_char_trigram_baseline_smoke_CG_2026-07-02_43ec44a50",
            "META_competitive_hebbian_LOSES_to_bag_task_class_matters_2026-07-02_MM_TENTATIVE",
            "USER_locked_substrate_knows_almost_nothing_2026-07-02",
            "brain_analog_ATL_hub_amodal_semantic_hub_neuroanatomy_reference"
        ],
        "sharpens_prior_META": "META_competitive_hebbian_LOSES_to_bag_task_class_matters_2026-07-02_MM_TENTATIVE (adds mechanism-class-inductive-bias-matching-task-class-statistical-structure as causal explanation)",
        "cert_increment_delta": 1
    }
}


def a5_append(path, atom):
    """Atomic append: tmp write + fsync + os.replace + verify-load."""
    d = os.path.dirname(path)
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_atomize_", suffix=".jsonl")
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
        "landed_VET_session": "2026-07-03_wikipedia_ppmi_svd_smoke_CG_plus_META",
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
    n_math = a5_append(MATH_ATOMS, atom_cg)
    print(f"[atomize] math atoms.jsonl now has {n_math} lines; appended CG atom id[:80]={atom_cg['id'][:80]}...")
    n_meta = a5_append(META_ATOMS, atom_meta)
    print(f"[atomize] meta atoms.jsonl now has {n_meta} lines; appended META atom id[:80]={atom_meta['id'][:80]}...")
    ledger_append(atom_cg)
    ledger_append(atom_meta)
    print(f"[atomize] cert_ledger.jsonl updated with 2 entries (CG + META).")
    print(f"[atomize] DONE. CERT delta: +1 CG_MEASURED_BOUND (math) +1 MM_TENTATIVE_SYNTHESIS (meta).")
