"""
A5-gated LOCAL-ONLY atomize: exp_agreement_attractor_role_binding_cg_viability_v1 (commit 7662876c6).
tier=MEASURED_MECHANISM / proven-bound / CERT +0. A well-specified real-text NEGATIVE.
Independent .venv off-disk recompute (baselines reproduced BIT-EXACT by independent code;
substrate numbers reproduced by deterministic re-run). BINARY-SAFE write (newline="") to avoid
CRLF doubling. LOCAL WRITE ONLY -- no origin push, no remote persist. save_atoms single-banker.
"""
import json, os, time, tempfile, datetime

ATOMS = "data/substrate_index/math/atoms.jsonl"
LEDGER = "data/substrate_index/meta/cert_ledger.jsonl"

# ---- A5 pre-load gate ----
with open(ATOMS, encoding="utf-8") as f:
    atom_lines = [l for l in f.read().splitlines() if l.strip()]
parsed = [json.loads(l) for l in atom_lines]
assert len(parsed) == 29442, f"expected 29442 atoms pre-write, got {len(parsed)}"
existing_ids = {o.get("id") for o in parsed if o.get("id")}
print("PRE-GATE: 29442 atoms load-valid; last id ends ...", parsed[-1]["id"][-46:])

with open(LEDGER, encoding="utf-8") as f:
    ledger_lines = [l for l in f.read().splitlines() if l.strip()]
last_seq = json.loads(ledger_lines[-1])["seq"]
assert last_seq == 29442, f"expected ledger last seq 29442, got {last_seq}"
NEW_SEQ = 29443

# CRLF-doubling guard: ensure no source line already carries \r
assert not any("\r" in l for l in atom_lines[-5:]), "existing atoms carry CR -- investigate before write"

COMPOSE_29440 = ("math::learned_composition_glue_pun_selectional_generalization_v1_MEASURED_MECHANISM_"
    "held_out_verb_disjoint_selectional_generalization_REAL_0p843_beats_freq_0p000_lookup_0p571_random_"
    "0p500_scramble_0p243_uncovered_subset_0p852_sign_flip_real_beats_random_plus_0p343_BUT_REDUCES_TO_"
    "FIXED_WORDNET_HYPERNYM_SIMILARITY_KERNEL_a_parameter_free_similarity_vote_NO_replay_cycle_reproduces_"
    "the_learned_arm_predictions_EXACTLY_70of70_items_delta_plus_0p0000_1NN_0p871_ge_0p843_replay_cycle_is_"
    "a_Hebbian_outer_product_accumulator_equals_linear_kernel_readout_over_the_FIXED_KB_similarity_atomize_"
    "plus_sleep_adds_NOTHING_beyond_the_given_WordNet_tree_sign_flip_only_proves_KB_similarity_is_USED_not_"
    "that_a_rule_is_LEARNED_structured_lookup_in_disguise_same_fixed_structure_trap_as_29399_29437_with_a_KB_"
    "tree_instead_of_FHRR_algebra_NOT_chain_grade_curve_rise_0p029_fails_flat_high_from_6_verbs_consistent_"
    "with_signal_present_from_start_2_class_binary_majority_0p6")
COMPOSE_29441 = ("math::relational_vs_similarity_conflict_viability_probe_v1_MEASURED_MECHANISM_role_binding_"
    "EXPRESSES_filler_independent_relational_feature_beats_surface_similarity_kNN_0p545_and_linear_loop_0p492_"
    "at_chance_C_0p997_margin_plus0p452_wrongrole_mustfail_collapses_0p628_BUT_LEVER_IS_REPRESENTATION_NOT_"
    "LEARNER_knn_over_relational_features_arm_D_ties_0p998_scramble_binary_learning_cosmetic_CONSTRUCTION_"
    "FAVORABLE_SYNTHETIC_real_conflict_corpus_unbuildable_4of42_because_29440_rule_similarity_co_extensive_"
    "settling_DEGRADES_0p88_single_step_unbind_compare_quadratic_is_the_nonlinearity_existence_proof_of_"
    "representation_not_learning_NOT_chain_grade")

# ---- off-disk recompute confirmation (already done in VET; re-assert key numbers off metrics.json) ----
m = json.load(open("data/exp_agreement_attractor_role_binding_cg_viability_v1/metrics.json", encoding="utf-8"))
sm = m["summary_metrics"]
assert m["verdict"] == "MIDDLE_BAND_POSITIONAL_OR_COUNT_HEURISTIC"
assert abs(sm["stage1_oracle_read_test"] - 1.0) < 1e-9 and sm["stage1_pass"] is True
assert abs(sm["acc_substrate"] - 0.7913) < 1e-3 and abs(sm["acc_majority"] - 0.5795) < 1e-3
assert abs(sm["snf_substrate"] - 0.5803) < 1e-3 and abs(sm["snf_majority"] - 0.6269) < 1e-3
assert abs(sm["headtrack_delta"] - (-0.0466)) < 1e-3 and sm["headtrack_win"] is False
assert sm["structure_used"] is False and sm["conflict_win"] is True
assert abs(sm["snf_structshuffle"] - 0.6214) < 1e-3
assert m["N_DIM"] == 2048 and m["seeds"] == [7, 13, 19] and m["cardinality_ok"] is True
print("OFF-DISK OK: S1=1.0 sub=0.7913 maj=0.5795 | SNF sub=0.5803 maj=0.6269 ss=0.6214 "
      "delta=-0.0466 structure_used=False conflict_win=True")

ts = time.time()
ts_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

AID = ("math::agreement_attractor_role_binding_cg_viability_v1_MEASURED_MECHANISM_first_REAL_TEXT_"
    "compgen_probe_LINZEN2016_14761items_LINEAR_logistic_readout_over_HRR_unbind_role_slot_features_learns_"
    "an_interpretable_POSITIONAL_plus_function_word_heuristic_RS1_first_weight_plus5p25_FW_PREP_neg1p66_FW_"
    "CCONJ_neg0p63_beats_surface_baselines_AGGREGATE_sub0p791_vs_nearest0p427_below_chance_attractor_first0p"
    "748_majority0p580_and_CONFLICT_subset_sub0p837_vs_majority0p632_near0p000_conflict_win_True_BUT_FAILS_"
    "the_head_tracking_bar_on_held_out_SUBJECT_NOT_FIRST_SNF_subset_sub0p580_vs_majority0p627_delta_neg0p047_"
    "need_plus0p10_headtrack_win_False_AND_does_NOT_beat_counts_preserving_STRUCTURE_SHUFFLE_control_on_SNF_"
    "ss0p621_gt_sub0p580_structure_used_False_STAGE1_REPRESENTABILITY_1p000_all_3seeds_oracle_head_number_"
    "read_from_bound_superposition_given_oracle_subject_position_survives_crosstalk_at_N_DIM2048_so_CEILING_"
    "IS_THE_LINEAR_LEARNER_NOT_THE_REPRESENTATION_lexeme_free_encoding_disjoint_heldout_subject_lexemes_2064_"
    "train_1381_test_0_overlap_label_invariant_clean_14761of14761_baselines_reproduce_BIT_EXACT_independent_"
    "recompute_substrate_numbers_reproduce_deterministic_rerun_3seed_7_13_19_bin4_0p847_arms_differ_weights_"
    "nondeg_KEY_FRAMING_the_learner_was_a_LINEAR_logistic_readout_NOT_the_atomize_plus_sleep_nonlinear_"
    "consolidation_loop_so_this_RE_DERIVES_29440_linear_reduces_to_fixed_similarity_limit_ON_REAL_TEXT_and_"
    "adds_two_novel_things_real_Linzen_text_not_synthetic_and_representability_1p000_isolation_ceiling_is_"
    "LEARNER_but_does_NOT_refute_the_atomize_plus_sleep_LEAP_which_was_UNTESTED_here_real_leap_test_on_this_"
    "VALIDATED_testbed_STILL_PENDING_composes_29440_29441_NOT_chain_grade_CERT_plus0_LOCAL_ONLY_2026-07-22")

assert AID not in existing_ids, "duplicate atom id"

NAME = ("MATH MEASURED_MECHANISM (proven-bound; first REAL-TEXT compgen probe, well-specified NEGATIVE). "
    "CLAIM: on the Linzen/Dupoux/Goldberg 2016 subject-verb agreement corpus (14,761 real Wikipedia items, "
    "attractor bins 0-4), a fixed HRR role/position-binding encoding + a LINEAR logistic readout over "
    "unbind-derived role-slot number features learns an INTERPRETABLE positional+function-word heuristic "
    "(first-noun/rank-from-start weight +5.25, FW_PREP -1.66, FW_CCONJ -0.63). It beats surface baselines in "
    "aggregate (substrate 0.791 vs nearest 0.427 (below chance -- nearest IS the attractor here) / first "
    "0.748 / majority 0.580) and on the conflict subset (0.837 vs majority 0.632; conflict_win=True), BUT "
    "FAILS the genuine head-tracking bar on the held-out subject-not-first (SNF) subset (0.580 vs majority "
    "0.627; delta -0.047, need +0.10; headtrack_win=False) and does NOT beat the counts-preserving "
    "STRUCTURE-SHUFFLE control on SNF (ss 0.621 > sub 0.580; structure_used=False). Stage-1 representability "
    "= 1.000 (all 3 seeds): given the oracle subject position, the head number is recoverable from the bound "
    "superposition through crosstalk at N_DIM=2048 -- so the CEILING IS THE LINEAR LEARNER, NOT THE "
    "REPRESENTATION. Lexeme-free encoding, disjoint held-out subject lexemes (0 overlap). KEY FRAMING "
    "(auditor correction): the learner tested was a LINEAR logistic readout, NOT the atomize+sleep nonlinear "
    "consolidation loop -- so this RE-DERIVES atom 29440's linear->fixed-similarity limit ON REAL TEXT (adding "
    "two novel things: real Linzen text not synthetic, and representability=1.000 isolation) but does NOT "
    "refute the atomize+sleep LEAP, which was NOT tested here. The real leap-test on this validated testbed "
    "is STILL PENDING.")

PLAIN = ("This is the program's first compositional-generalization shot on REAL text: can the substrate learn, "
    "from labeled real-Wikipedia sentences, that subject-verb agreement number belongs on the syntactic-HEAD "
    "noun (the subject) rather than the nearest noun (an 'attractor'), without being handed a parse? The "
    "corpus (Linzen 2016, 14,761 items) is built so the nearest-noun heuristic is actively WRONG (nearest is "
    "the attractor). The substrate holds each sentence's noun-number map in one bound HRR superposition and a "
    "simple LINEAR logistic classifier reads role-slots from it and tries to learn the right weighting, "
    "generalizing to held-out sentences whose subject-words it never saw in training. RESULT: it learns a "
    "readable rule -- mostly 'trust the first noun', plus small function-word corrections ('a noun right after "
    "a preposition is probably NOT the subject'). That rule beats the surface baselines overall and on the "
    "conflict cases where the nearest noun disagrees with the answer. But it FAILS the honest test: on the "
    "subset where the subject is NOT the first noun, it drops to 0.580 and cannot beat even the majority-class "
    "guess (0.627), and it does no better than a control that keeps the noun COUNTS but destroys the "
    "position/function-word STRUCTURE -- so it is riding position and counts, not tracking the head. Crucially, "
    "Stage-1 proves the encoding is FAIR: given the true subject position, the number reads out of the "
    "superposition perfectly (1.000), so the failure is the LEARNER's, not a rigged representation. AUDITOR "
    "FRAMING CORRECTION: the learner here was a LINEAR readout, which is exactly the path atom 29440 already "
    "proved collapses to a fixed-similarity vote -- so this negative RE-DERIVES that linear limit on REAL "
    "text (the genuinely new parts are: it is real Linzen text, not synthetic, and the representability=1.000 "
    "gate cleanly pins the ceiling on the learner). It does NOT test, and therefore does NOT refute, the "
    "USER's actual LEAP hypothesis -- the NONLINEAR atomize+sleep consolidation loop. The real leap-test on "
    "this now-validated real-text testbed is STILL PENDING, not closed.")

CERT_CLASS = ("agreement_attractor_role_binding_cg_viability_v1_MEASURED_MECHANISM_first_real_text_compgen_"
    "linzen2016_LINEAR_logistic_readout_over_hrr_unbind_role_slots_learns_positional_plus_fnword_heuristic_"
    "rs1_plus5p25_fw_prep_neg1p66_beats_surface_agg_sub0p791_near0p427_first0p748_maj0p580_conflict_sub0p837_"
    "maj0p632_win_but_FAILS_headtrack_SNF_sub0p580_maj0p627_delta_neg0p047_win_False_structure_used_False_"
    "ss0p621_stage1_representability_1p000_ceiling_is_LINEAR_LEARNER_not_representation_lexeme_free_disjoint_"
    "heldout_baselines_bit_exact_3seed_re_derives_29440_linear_similarity_limit_on_real_text_adds_realtext_"
    "plus_representability_isolation_does_NOT_test_or_refute_atomize_sleep_leap_still_pending_NOT_chain_grade")

atom = {
    "id": AID,
    "name": NAME,
    "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "kind": "experiment_landed_vet",
    "cert_status": "proven-bound",
    "cert_class": CERT_CLASS,
    "plain_language": PLAIN,
    "importance": ("MEDIUM (well-specified real-text NEGATIVE; localizes the ceiling to the LINEAR learner). "
        "VALUE: (1) validates a real-text agreement-attraction testbed with a fairness-confirmed "
        "(representability=1.000) encoding, on which future leap-tests can run; (2) proves that on real "
        "text a LINEAR readout over HRR role-slots learns only a positional+function-word heuristic, NOT "
        "head-tracking -- a real-text extension of atom 29440's linear->fixed-similarity limit. LIMIT of "
        "value: it does NOT test the atomize+sleep nonlinear loop, so it neither advances nor refutes the "
        "LEAP; it must not be propagated as 'the leap testbed refuted the leap'. +0 CERT (non-win)."),
    "description": NAME,
    "aliases": [
        "first real-text compgen probe (Linzen 2016 agreement-attraction): LINEAR readout -> MIDDLE (MM)",
        "learns positional+fnword heuristic (RS1 +5.25, FW_PREP -1.66); fails head-tracking on SNF (0.580 vs maj 0.627)",
        "structure_used=False (ss 0.621 > sub 0.580 on SNF): rides position/counts, not role structure",
        "Stage-1 representability=1.000 -> ceiling is the LINEAR LEARNER, not the representation",
        "re-derives 29440 linear->fixed-similarity limit ON REAL TEXT; atomize+sleep LEAP still UNTESTED / pending",
    ],
    "ts_iso": ts_iso,
    "ts": ts,
    "serves_capability": ("real_text_compositional_generalization_agreement_attraction_head_tracking_is_NOT_"
        "acquired_by_a_LINEAR_readout_over_hrr_role_slots_ceiling_is_the_linear_learner_representation_is_fair_"
        "representability_1p000_atomize_sleep_nonlinear_leap_test_on_this_validated_testbed_still_pending"),
    "metadata": {
        "provenance_quality": ("independent_venv_offdisk_recompute: substrate_INDEPENDENT baselines "
            "reproduced BIT-EXACT by independent auditor code off the committed cache "
            "(agreement_probe_cache_v1.json.gz, 14761 linzen) for all 3 seeds -- first/nearest/bag/majority "
            "AGG and SNF and CONFLICT subsets all match metrics.json to 4dp; label invariant nums[subj_pos]==label "
            "verified 14761/14761; disjoint held-out subject lexeme pools verified (train 2064 / test 1381 / "
            "overlap 0). Substrate-DEPENDENT numbers (stage1=1.0, substrate SNF 0.5803, structshuffle 0.6214, "
            "headtrack_delta -0.0466) reproduced by DETERMINISTIC re-run of the cell off the same committed "
            "cache (bit-exact to 4dp). Learner identity confirmed by source inspection: only learners are "
            "train_readout (logistic-regression GD) + knn_predict (arm-D); NO replay_cycle/glass_box_loop/"
            "consolidation/atomize/sleep machinery present."),
        "anchor": "exp_agreement_attractor_role_binding_cg_viability_v1",
        "cell_commit": "7662876c6",
        "supersedes": None,
        "amends_atom_ids": None,
        "store_head_at_write": "unsynced_needs_orchestrator",
        "metrics_path": "data/exp_agreement_attractor_role_binding_cg_viability_v1/metrics.json",
        "verified_off_data": ("INDEP recompute (.venv Scripts/python; Fix #28, verify OFF DATA not verdict_msg). "
            "Baselines recomputed with INDEPENDENT auditor code off the cache reproduce BIT-EXACT: seed7 AGG "
            "first=0.7473 near=0.4270 bag=0.4990 maj=0.5802; SNF first=0.4138 near=0.5522 bag=0.4892 maj=0.6261; "
            "CONF near=0.0000 maj=0.6323 bag=0.3220 (seeds 13/19 likewise). Substrate path reproduced by "
            "deterministic re-run: stage1_oracle_read_test=1.0 (train 0.9998-1.0) all seeds; acc_substrate=0.7913; "
            "snf_substrate=0.5803 vs snf_majority=0.6269 (delta -0.0466, headtrack_win=False); "
            "snf_structshuffle=0.6214 > snf_substrate (structure_used=False); conflict_substrate=0.8368 vs "
            "conflict_majority=0.6319 (conflict_win=True); bin4=0.8475; arms_differ=True; weights_nondeg=True; "
            "learned weights RS1_first ~+5.1-5.25 (dominant), FW_PREP ~-1.4 to -1.66, FW_CCONJ ~-0.5 to -0.84. "
            "N_DIM=2048, seeds 7/13/19, train_cap=test_cap=6000."),
        "honest_scope": ("Full run (3 seeds), real Linzen 2016 corpus (14,761 items) read from the small committed "
            "cache. The learner is a LINEAR logistic readout over unbind-derived role-slot features (NOT the "
            "atomize+sleep nonlinear consolidation loop). Nonce (Gulordava) transfer arm DEFERRED (POS-tagger "
            "unavailable, 0 taggable prefixes) -- immaterial because the encoding is lexeme-free by construction. "
            "This is a NEGATIVE (MIDDLE_BAND per the cell's pre-registered bands): a well-specified real-text "
            "negative, NOT 'the substrate cannot'."),
        "metrics": {
            "stage1_oracle_read_test": 1.0, "stage1_pass": True,
            "acc_substrate": 0.7913, "acc_nearest": 0.4271, "acc_first": 0.7478, "acc_majority": 0.5795,
            "acc_bagcount": 0.5002, "acc_structshuffle": 0.5869, "acc_clean_ablation": 0.8124,
            "acc_knn_relational_D": 0.7856,
            "conflict_substrate": 0.8368, "conflict_majority": 0.6319, "conflict_nearest": 0.0,
            "snf_substrate": 0.5803, "snf_first": 0.4149, "snf_majority": 0.6269, "snf_bagcount": 0.4905,
            "snf_structshuffle": 0.6214, "snf_base_strongest": 0.6269,
            "headtrack_delta": -0.0466, "headtrack_win": False, "conflict_win": True, "structure_used": False,
            "bin4_substrate_acc": 0.8475,
            "learned_weights_seed7": {"RS1_first": 5.254, "RV1_nearest": 0.049, "FW_PREP": -1.66,
                                       "FW_CCONJ": -0.626, "FW_DET": 1.237, "FW_REL": 0.498, "FW_START": 0.242},
            "n_train": 6000, "n_test": 6000, "seeds": [7, 13, 19], "N_DIM": 2048,
            "corpus": "Linzen_Dupoux_Goldberg_2016", "n_corpus_items": 14761,
            "heldout_subject_lexemes_train": 2064, "heldout_subject_lexemes_test": 1381, "lexeme_overlap": 0,
        },
        "over_reads_corrected": [
            ("DO NOT read this as 'the atomize+sleep LEAP testbed refuted the leap'. The Stage-2 learner tested "
             "was a LINEAR logistic readout (train_readout), NOT the NONLINEAR atomize+sleep consolidation loop. "
             "Per atom 29440 a linear learner over given features provably collapses to a fixed-similarity vote, "
             "so this NEGATIVE largely RE-DERIVES the known linear limit -- now ON REAL TEXT. The actual "
             "atomize+sleep leap-test on this validated testbed is STILL PENDING, not refuted."),
            ("DO NOT read Stage-1 representability=1.000 as a positive capability result. It is a FAIRNESS gate: "
             "given the ORACLE subject position, the head number is recoverable from the bound superposition "
             "through crosstalk. It uses position (a fair taught scaffold), not the label, and its whole purpose "
             "is to prove the Stage-2 failure is the LEARNER's, not a rigged-unrepresentable encoding."),
            ("DO NOT read the aggregate/conflict-subset wins (0.791; conflict 0.837 vs maj 0.632) as head-tracking. "
             "They are delivered by a POSITIONAL heuristic (first-noun weight +5.25) plus a small function-word "
             "correction; on the subject-not-first subset the positional weighting is wrong and the learner cannot "
             "beat majority (0.580 vs 0.627) or the counts-preserving structure-shuffle control (0.621)."),
            ("DO NOT frame this as 'the substrate cannot do agreement head-tracking'. It is 'THIS mechanism (fixed "
             "role-binding + LINEAR readout) under THESE conditions did not acquire head-tracking here' -- a "
             "well-specified negative pointing at a needed structure-induction / nonlinear-learner capability."),
        ],
        "genuine_positives_symmetric_anti_negativity": (
            "GENUINE, credited (symmetric anti-negativity): (1) The TESTBED is now VALIDATED and FAIR -- real "
            "Linzen 2016 text (not synthetic), a representability-confirmed encoding (Stage-1=1.000 pins the "
            "ceiling on the learner not the representation), disjoint held-out subject lexemes (0 overlap, lexical "
            "memorization architecturally excluded), a label-clean corpus (14761/14761), and 5 real baselines that "
            "reproduce BIT-EXACT under independent recompute. (2) The discriminator genuinely CAN-FAIL and FIRED "
            "(headtrack_delta -0.047 < +0.10; structure_used=False) -- this is a design-gate-passing can-fail cell, "
            "not a saturated or construction-forced one. (3) The learned rule is glass-box INSPECTABLE and "
            "self-consistent across 3 seeds (RS1_first +5.1-5.25 dominant, FW_PREP -1.4 to -1.66), an honest, "
            "readable characterization of exactly what the linear learner acquired."),
        "revival_criteria": [
            ("THE PENDING LEAP-TEST: run the NONLINEAR atomize+sleep consolidation loop (per-case atoms + sleep "
             "consolidation to a general rule) as the Stage-2 learner on THIS SAME validated testbed. A PASS "
             "(head-tracking on the SNF subset beating majority and the structure-shuffle control by the "
             "pre-registered margins, 3 seeds) would be a genuine chain-grade candidate; a FAIL would extend the "
             "linear-limit conclusion to the nonlinear loop and is the decisive close."),
            ("A learner that beats the SNF head-tracking bar (delta >= +0.10 over max(first,majority,bagcount)) AND "
             "the counts-preserving structure-shuffle control (>= +0.10 on SNF) AND holds >= 0.55 at 4 attractors, "
             "3 seeds, on this corpus -> GREEN-LIGHT-PENDING-VET (still not a self-declared CG)."),
        ],
        "cross_arc_overlap_check": (
            "substrate_query 'subject verb agreement attractor head number learn real text linear readout' -> top "
            "cosine 0.2949 (real number / CN_number_agreement 0.288) < 0.30 threshold; the cell's own prereg check "
            "found only GENERIC CG notes at ~0.36-0.40 (SCAN/skill-composition), NONE on agreement-attraction. "
            "CONFIRMED GENUINELY NOVEL in the arc as the FIRST real-text agreement-attraction probe. At the "
            "mechanism level it is a targeted REAL-TEXT extension of atom 29440's LINEAR->fixed-similarity limit "
            "(not a duplicate) and COMPOSES 29440 + 29441; no full rediscovery."),
        "cites": [
            "Fix_28_verify_off_data_not_verdict_msg",
            "symmetric_anti_negativity_verify_both_directions_USER",
            "cited_number_must_reproduce_from_cell",
            "verify_the_referent_atom_ids_mechanism_metric_regime",
            "synthetic_toy_corpus_outcomes_can_be_construction_determined_real_questions_need_real_data",
            "every_negative_check_how_the_brain_does_it_proactively_USER",
            "Linzen_Dupoux_Goldberg_2016_agreement_attraction",
            "Gulordava_2018_colorless_green_nonce",
            "Wagers_Lau_Phillips_2009_cue_based_retrieval_agreement_attraction",
        ],
        "composes_with": [
            ("COMPOSES (does NOT supersede) 29440 learned_composition_glue_pun_selectional_generalization_v1: that "
             "atom proved a LINEAR atomize+sleep learner reduces to a fixed-similarity/1NN kernel over the given "
             "features (adds nothing beyond the KB tree). THIS atom is the REAL-TEXT witness of the same linear "
             "limit: a linear readout over HRR role-slots on real Linzen agreement text learns only a positional/"
             "count heuristic, not head-tracking. Key: it therefore does NOT test the atomize+sleep leap either."),
            ("COMPOSES (does NOT supersede) 29441 relational_vs_similarity_conflict_viability_probe_v1: that atom "
             "found role-binding EXPRESSES a beyond-similarity relational feature but the LEVER was "
             "REPRESENTATION-not-LEARNER (kNN-over-relational-features ties; linear loop at chance). THIS atom is "
             "consistent and complementary on REAL text: Stage-1 representability=1.000 (representation is fine) "
             "while the LINEAR learner fails to acquire head-tracking (learner is the ceiling)."),
        ],
        "strategic_implication": (
            "The real-text agreement-attraction testbed is now VALIDATED and FAIR (representability=1.000). A "
            "LINEAR readout over HRR role-slots learns a positional+function-word heuristic, not head-tracking -- "
            "extending atom 29440's linear->fixed-similarity limit to REAL TEXT. This does NOT refute the USER's "
            "atomize+sleep LEAP hypothesis (a NONLINEAR consolidation loop), which was NOT tested here. The "
            "GENUINE-CG bar and the real leap-test remain OPEN and now have a validated real-text, "
            "rule-conflicts-with-surface-similarity testbed to run on -- exactly the deep-picture CG target."),
        "atomized_by": "hdi_skunkworks",
        "atomized_date": "2026-07-22",
        "needs_orchestrator_store_sync": True,
        "local_write_only_no_origin_push_no_remote_persist": True,
    },
}
json.loads(json.dumps(atom))

# ---- A5 atomic append (BINARY-SAFE: newline="" prevents Windows CRLF doubling) ----
new_line = json.dumps(atom, ensure_ascii=False)
assert "\r" not in new_line and "\n" not in new_line, "atom line contains embedded newline/CR"
new_atoms_text = "\n".join(atom_lines + [new_line]) + "\n"
d = os.path.dirname(os.path.abspath(ATOMS))
fd, tmp = tempfile.mkstemp(dir=d, suffix=".tmp")
os.close(fd)
with open(tmp, "w", encoding="utf-8", newline="") as f:
    f.write(new_atoms_text); f.flush(); os.fsync(f.fileno())
os.replace(tmp, ATOMS)

# ---- verify-load + CRLF-doubling guard ----
with open(ATOMS, "rb") as f:
    raw = f.read()
assert b"\r\n" not in raw, "CRLF doubling detected in atoms.jsonl after write"
with open(ATOMS, encoding="utf-8") as f:
    v = [json.loads(l) for l in f.read().splitlines() if l.strip()]
assert len(v) == 29443, f"post-write expected 29443, got {len(v)}"
assert v[-1]["id"] == AID and v[-1]["tier"] == "MEASURED_MECHANISM" and v[-1]["cert_status"] == "proven-bound"
print(f"ATOMS OK: now {len(v)} atoms (was 29442); new atom #29443 verified; no CRLF doubling.")

# ---- ledger entry (matching ts; seq continuity 29442 -> 29443) ----
ledger = {
    "seq": NEW_SEQ,
    "op": "landed_vet_atomize",
    "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "cert_status": "proven-bound",
    "cert_class": CERT_CLASS,
    "anchor": "exp_agreement_attractor_role_binding_cg_viability_v1",
    "run_anchor": "agreement_attractor_role_binding_cg_viability_v1",
    "cell_commit": "7662876c6",
    "supersedes_commit": None,
    "supersedes_atom_id": None,
    "amends_atom_id": None,
    "composes": [COMPOSE_29440, COMPOSE_29441],
    "store_head_at_write": "unsynced_needs_orchestrator",
    "verified_off_data": True,
    "auditor": "hdi_skunkworks",
    "atomized_by": AID,
    "atom_id": AID,
    "decision": ("MEASURED_MECHANISM / proven-bound. First REAL-TEXT compgen probe (Linzen 2016, 14,761 items). "
        "A fixed HRR role/position-binding encoding + a LINEAR logistic readout learns an interpretable "
        "positional+function-word heuristic (RS1_first +5.25, FW_PREP -1.66) that beats surface baselines in "
        "aggregate (0.791 vs nearest 0.427 / majority 0.580) and on the conflict subset (0.837 vs maj 0.632; "
        "conflict_win=True) but FAILS head-tracking on the held-out subject-not-first subset (0.580 vs maj 0.627; "
        "delta -0.047; headtrack_win=False) and does not beat the counts-preserving structure-shuffle control "
        "there (0.621; structure_used=False). Stage-1 representability=1.000 (all seeds) pins the ceiling on the "
        "LINEAR LEARNER, not the representation. VET: baselines reproduce BIT-EXACT under independent auditor "
        "recompute off the cache; substrate numbers reproduce under deterministic re-run; label invariant clean "
        "(14761/14761); disjoint held-out subject lexemes (0 overlap); learner confirmed LINEAR by source "
        "inspection (no atomize+sleep/replay loop). KEY FRAMING CORRECTION: the learner was LINEAR, so this "
        "RE-DERIVES atom 29440's linear->fixed-similarity limit ON REAL TEXT (novel: real text + "
        "representability=1.000 isolation) and does NOT test or refute the USER's atomize+sleep LEAP -- the real "
        "leap-test on this validated testbed is STILL PENDING. COMPOSES (does NOT supersede) 29440 + 29441. "
        "CERT +0 (non-win). Local-only; needs orchestrator store sync."),
    "cert_delta": "+0 (MEASURED_MECHANISM proven-bound / well-specified real-text negative; not chain-grade)",
    "net_cert_delta": "+0",
    "ts_iso": ts_iso,
    "ts": ts,
    "needs_orchestrator_store_sync": True,
    "local_write_only_no_origin_push_no_remote_persist": True,
}
json.loads(json.dumps(ledger))
new_led_line = json.dumps(ledger, ensure_ascii=False)
assert "\r" not in new_led_line and "\n" not in new_led_line
new_ledger_text = "\n".join(ledger_lines + [new_led_line]) + "\n"
dl = os.path.dirname(os.path.abspath(LEDGER))
fd2, tmp2 = tempfile.mkstemp(dir=dl, suffix=".tmp")
os.close(fd2)
with open(tmp2, "w", encoding="utf-8", newline="") as f:
    f.write(new_ledger_text); f.flush(); os.fsync(f.fileno())
os.replace(tmp2, LEDGER)

with open(LEDGER, "rb") as f:
    rawl = f.read()
assert b"\r\n" not in rawl, "CRLF doubling detected in cert_ledger.jsonl after write"
with open(LEDGER, encoding="utf-8") as f:
    vl = [json.loads(l) for l in f.read().splitlines() if l.strip()]
assert len(vl) == len(ledger_lines) + 1
assert vl[-1]["atom_id"] == AID and vl[-1]["ts"] == ts and vl[-1]["seq"] == NEW_SEQ
assert vl[-2]["seq"] == 29442, "seq continuity broken"
print(f"LEDGER OK: {len(ledger_lines)} -> {len(vl)} entries; seq 29442 -> {NEW_SEQ}; ts matches atom; no CRLF.")
print("ATOM_ID:", AID)
print("DONE. LOCAL-ONLY. needs_orchestrator_store_sync=True; no origin push; no remote persist.")
