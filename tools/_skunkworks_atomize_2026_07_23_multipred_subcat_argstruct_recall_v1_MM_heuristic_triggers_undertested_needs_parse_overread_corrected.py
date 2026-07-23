"""
A5-gated LOCAL-ONLY atomize: exp_multipred_subcat_argstruct_recall_v1 (leg-2 decisive test).
tier=MEASURED_MECHANISM / proven-bound / CERT +0.
Independent .venv off-disk recompute (all 4 arms re-run via the cell's own run_all_arms; each
residual FRAMES miss + each regression TRACED to its failure locus) reproduces every headline
number bit-exact AND corrects the cell's HARD_FAIL 'needs a real parse' conclusion to a MODERATE
OVER-READ: the tested heuristic was crippled (dropped the baseline reader's split_sentences +
VerbNet-auditor gate false-negatives), so the cheap option was UNDER-tested, not proven-insufficient.
BINARY-SAFE write (newline="") + dynamic count gate + seq continuity.
LOCAL WRITE ONLY -- no origin push, no remote persist.
"""
import json, os, time, tempfile, datetime, hashlib
os.chdir(r"D:\AI\hd-instrument")
ATOMS = "data/substrate_index/math/atoms.jsonl"
LEDGER = "data/substrate_index/meta/cert_ledger.jsonl"

# ---- A5 pre-load gate (dynamic counts; serialize-safe) ----
with open(ATOMS, encoding="utf-8") as f:
    atom_lines = [l for l in f.read().splitlines() if l.strip()]
parsed = [json.loads(l) for l in atom_lines]
N_ATOMS = len(parsed)
existing_ids = {o.get("id") for o in parsed if o.get("id")}
assert not any("\r" in l for l in atom_lines[-5:]), "existing atoms carry CR -- investigate"
with open(LEDGER, encoding="utf-8") as f:
    ledger_lines = [l for l in f.read().splitlines() if l.strip()]
last_seq = json.loads(ledger_lines[-1])["seq"]
NEW_SEQ = last_seq + 1
print(f"PRE-GATE: {N_ATOMS} atoms load-valid; ledger last seq {last_seq}; NEW_SEQ={NEW_SEQ}")

# ---- off-disk recompute confirmation (re-assert numbers off metrics.json) ----
m = json.load(open("data/exp_multipred_subcat_argstruct_recall_v1/metrics.json", encoding="utf-8"))
assert m["verdict"] == "HARD_FAIL_MULTIPRED_NEEDS_REAL_PARSE"
A = m["arms"]
assert A["BASELINE"]["recall_ceiling"] == 0.44 and A["MULTIPRED_FRAMES"]["recall_ceiling"] == 0.47
assert A["MULTIPRED_KEEPALL"]["recall_ceiling"] == 0.51 and A["MULTIPRED_SCRAMBLED"]["recall_ceiling"] == 0.45
assert abs(A["BASELINE"]["f1"] - 0.2708) < 1e-9 and abs(A["MULTIPRED_FRAMES"]["f1"] - 0.2782) < 1e-9
assert abs(A["BASELINE"]["precision"] - 0.1956) < 1e-9 and abs(A["MULTIPRED_FRAMES"]["precision"] - 0.1975) < 1e-9
assert abs(A["MULTIPRED_KEEPALL"]["precision"] - 0.1486) < 1e-9
assert m["n_recovered"] == 17 and m["n_regressed"] == 14
# controls fired
assert A["MULTIPRED_KEEPALL"]["precision"] < A["MULTIPRED_FRAMES"]["precision"]   # control a
assert A["MULTIPRED_SCRAMBLED"]["recall_ceiling"] < A["MULTIPRED_FRAMES"]["recall_ceiling"]  # control b
print("OFF-DISK OK: base_rc=0.44 frames_rc=0.47 (rise+0.03) keepall_rc=0.51 scrambled_rc=0.45;")
print("             F1 0.2708->0.2782; prec 0.1956->0.1975 (keepall 0.1486); recovered 17 regressed 14;")
print("             control_a (keepall_prec<frames_prec) FIRED; control_b (scrambled_rc<frames_rc) FIRED.")
# Independent recompute (auditor re-ran cell's run_all_arms in a separate .venv process) reproduced
# all four arms bit-exact and traced residual-miss / regression loci -- see RECOMPUTE below.

cell_path = "experiments/exp_multipred_subcat_argstruct_recall_v1.py"
cell_sha = hashlib.sha256(open(cell_path, "rb").read()).hexdigest()[:16]

ts = time.time()
ts_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

AID = ("math::multipred_subcat_argstruct_recall_v1_MEASURED_MECHANISM_leg2_decisive_test_of_the_reader_"
    "extraction_recall_ceiling_29473_extending_find_main_verb_ONE_pass_per_sentence_to_MULTI_PREDICATE_"
    "find_predicates_MAIN_plus_bare_COORD_VP_plus_INF_COMP_plus_SUBORD_triggers_each_with_own_local_span_"
    "role_pass_gated_by_VerbNet_subcat_valency_admits_patient_frame_HEADLINE_recall_ceiling_only_0p44_to_"
    "0p47_rise_plus0p03_below_the_0p05_HARD_FAIL_floor_and_far_below_0p65_HARD_PASS_bar_F1_0p2708_to_0p2782_"
    "precision_0p1956_to_0p1975_no_collapse_17of56_baseline_misses_recovered_14_regressed_BOTH_must_fail_"
    "controls_FIRE_KEEPALL_precision_0p1486_lt_FRAMES_0p1975_gate_IS_the_precision_keeper_SCRAMBLED_rc_0p45_"
    "lt_FRAMES_0p47_frame_CONTENT_load_bearing_so_gate_DESIGN_directionally_sound_BUT_cell_HARD_FAIL_"
    "conclusion_NEEDS_A_REAL_PARSE_is_a_MODERATE_OVER_READ_the_tested_heuristic_was_CRIPPLED_two_self_"
    "inflicted_defects_1_multipred_path_DROPPED_the_baseline_readers_ORC_split_sentences_processes_whole_sid_"
    "as_one_tagged_seq_so_multi_sentence_sids_and_later_sentence_main_verbs_no_longer_enumerated_2_VerbNet_"
    "auditor_gate_FALSE_NEGATIVES_put_hear_vn_admits_direct_object_False_suppress_genuinely_transitive_"
    "instances_plus_tell_say_know_override_costs_real_object_cases_told_him_the_NAME_residual_53_FRAMES_"
    "misses_decompose_39_predicate_NOT_enumerated_4_gate_suppressed_false_neg_4_gold_patient_not_in_POS_"
    "candidate_gate_6_span_or_classifier_the_39_break_into_prep_gerund_in_choosing_reduced_relative_making_"
    "marks_child_dash_finding_it_locked_that_whether_complement_found_that_James_had_money_which_who_"
    "relatives_fronted_subordinate_main_clause_when_they_build_they_make_a_dam_and_multi_sentence_within_sid_"
    "14_regressions_are_NOT_dominated_by_span_theft_only_3of14_clean_span_see_child_meet_boys_find_boy_3of14_"
    "gate_false_neg_hear_hear_put_8of14_enumeration_loss_of_which_4_are_self_inflicted_multi_sentence_"
    "split_loss_nod_leave_open_make_you_so_a_real_parse_would_fix_11of14_but_7of14_gate_plus_multisentence_"
    "are_ALSO_cheaply_fixable_WITHOUT_a_parse_STRATEGIC_the_transition_parser_29451_0p81_UAS_IS_the_right_"
    "lever_on_ENGINEERING_grounds_it_principledly_subsumes_every_ad_hoc_trigger_AND_fixes_span_assignment_"
    "regressions_NOT_because_heuristics_are_PROVEN_unable_to_reach_0p65_a_careful_heuristic_keep_split_"
    "sentences_plus_fix_gate_plus_fronted_subordinate_was_NOT_run_and_is_plausibly_low_0p6s_near_the_bar_"
    "brain_check_confirmed_brain_parses_incrementally_with_existing_grammar_per_predicate_frames_NOT_verb_"
    "trigger_scanning_supply_a_real_parse_is_a_brain_SHARED_mechanism_pointer_consistent_with_29455_supply_"
    "structure_learn_content_composes_29473_CERT_plus0_LOCAL_ONLY_2026-07-23")
assert AID not in existing_ids, "duplicate atom id"

NAME = ("MATH MEASURED_MECHANISM (proven-bound; CERT +0; leg-2 DECISIVE TEST of the 29473 reader extraction-"
    "recall ceiling). CLAIM: extending the hand-rule reader's find_main_verb (ONE argument-role pass per "
    "sentence) to a MULTI-PREDICATE find_predicates (the MAIN pick PLUS bare secondary predicates via three "
    "general syntactic triggers -- coordinate-VP, infinitival-complement, bare-subordinator -- each with its "
    "own local-span role pass, gated by a per-verb VerbNet subcat/valency admits_patient frame) recovers only "
    "a MODEST slice of the 68%-dominant multi-predicate extraction-miss class. recall_ceiling BASELINE 0.44 -> "
    "FRAMES 0.47 (rise +0.03, BELOW the pre-registered 0.05 HARD_FAIL floor and far below the 0.65 HARD_PASS "
    "bar). F1 rose slightly (0.2708 -> 0.2782), precision held (0.1956 -> 0.1975), and BOTH must-fail controls "
    "FIRED (KEEPALL precision 0.1486 < FRAMES 0.1975 -> the gate IS the precision-keeper; SCRAMBLED "
    "recall_ceiling 0.45 < FRAMES 0.47 -> frame CONTENT is load-bearing) -- so the subcat-gate DESIGN is "
    "directionally sound. 17/56 baseline misses recovered, 14 previously-correct items regressed. "
    "FRAMING CORRECTION (load-bearing, symmetric-anti-negativity DOWNWARD on the strength of the negative "
    "conclusion): the cell's HARD_FAIL verdict 'multi-predicate needs a REAL parse, cheap frame-lookup "
    "insufficient' is a MODERATE OVER-READ of THIS cell, because the tested heuristic was CRIPPLED by two "
    "SELF-INFLICTED implementation defects that made it look worse than a careful heuristic would: (1) the "
    "multipred path DROPPED the baseline reader's ORC.split_sentences -- it POS-tags the whole sid as one "
    "sequence and never clause/sentence-splits -- so multi-sentence sids and later-sentence main verbs are no "
    "longer enumerated at all (directly causes ~4 of the 14 regressions and several residual misses the "
    "BASELINE handled); (2) the VerbNet auditor gate has FALSE-NEGATIVES (vn_admits_direct_object('put')="
    "False, ('hear')=False) that HARD-SUPPRESS genuinely-transitive instances, plus the tell/say/know override "
    "costs real-object cases ('told him the NAME'). So the cheap option was UNDER-tested, not proven-"
    "insufficient. STRATEGIC: the transition parser (29451, 0.81 UAS) IS the right next lever -- but on "
    "ENGINEERING grounds (it principledly subsumes every ad-hoc trigger AND fixes the span-assignment "
    "regressions), NOT because heuristics are PROVEN unable to reach 0.65.")

PLAIN = ("The reader that figures out 'who did what to whom' in a sentence has a known weakness (found in the "
    "prior diagnosis): it only processes ONE verb per sentence -- the first one -- so in a sentence like "
    "'Herbert took up a block and threw it', the 'threw it' part gets no analysis at all. That single flaw "
    "accounts for 68% of the reader's misses. THIS experiment tried the CHEAP fix: instead of a full re-parse, "
    "just scan for EXTRA verbs using a few simple trigger rules (a verb right after 'and'; a verb right after "
    "'to'; a verb after words like 'when/while/after'), give each extra verb its own little search for its "
    "object, and use a VerbNet-based table to suppress verbs that don't take objects (so precision doesn't "
    "flood). RESULT: it barely moved the recall ceiling, from 0.44 to 0.47 -- below the 0.05 minimum the "
    "diagnosis had pre-set, and nowhere near the 0.65 target. It recovered 17 old misses but BROKE 14 things "
    "that used to work. The cell concluded: the cheap triggers are not enough, we need a REAL parse. IS THAT "
    "CONCLUSION HONEST, OR PREMATURE? The load-bearing audit finding: it is DIRECTIONALLY right but a MODERATE "
    "OVER-READ, because the cheap fix as-tested was crippled in two avoidable ways. FIRST, the new code threw "
    "away a capability the ORIGINAL reader already had -- splitting a block of text into separate sentences -- "
    "so it now swallows multiple sentences as one blob and never even looks at the main verb of the 2nd, 3rd "
    "sentence. That ALONE caused about 4 of the 14 regressions (e.g. 'Papa now left the room' -- the old reader "
    "got 'left/papa/room', the new one picked an earlier verb and never reached 'left'). SECOND, the VerbNet "
    "gate wrongly marks 'put' and 'hear' as NOT taking an object (a lookup false-negative), so it deletes "
    "perfectly good answers like 'put his head', 'heard you'. So of the 14 regressions: only 3 are the thing "
    "the cell worries about (the answer getting stolen by the wrong verb); 3 are the gate false-negatives "
    "(cheap fix); and 8 are verbs not getting enumerated, HALF of which are just the dropped sentence-splitting "
    "(cheap fix). WHY THE PARSER IS STILL THE RIGHT CALL: a careful heuristic (keep sentence-splitting + fix "
    "the gate + handle a fronted subordinate clause) was NOT actually run, and could plausibly reach the low "
    "0.60s -- near the bar. BUT every remaining cheap trigger you'd add ('that'-clauses, '-ing' clauses, "
    "sentence boundaries) is an ambiguous cue that risks flooding precision, and the transition parser (a "
    "separate proven result at 0.81 attachment accuracy) does ALL of that principledly at once AND fixes the "
    "wrong-verb-steals-the-object regressions. So the parser wins on engineering cleanliness, not because "
    "'heuristics provably can't get there.' BOTTOM LINE for strategy: do NOT close the cheap option as 'proven "
    "insufficient' on this cell -- it was under-tested; DO adopt the parser as the cleaner, subsuming lever. "
    "BRAIN-CHECK: the brain doesn't scan for verbs with trigger rules -- it parses incrementally using grammar "
    "it already knows, and every verb opens its own argument slots as it is read. So 'supply a real parse' is a "
    "brain-SHARED mechanism pointer (fix = give the reader real structure), matching the banked 29455 thesis "
    "'supply the structure, learn the content' -- NOT a substrate-specific bug.")

CERT_CLASS = ("multipred_subcat_argstruct_recall_v1_MEASURED_MECHANISM_leg2_decisive_test_extend_find_main_verb_"
    "one_pass_per_sentence_to_multipredicate_find_predicates_MAIN_plus_bare_COORD_VP_INF_COMP_SUBORD_triggers_"
    "local_span_role_pass_VerbNet_subcat_admits_patient_gate_recall_ceiling_0p44_to_0p47_plus0p03_below_0p05_"
    "floor_below_0p65_bar_F1_0p2708_to_0p2782_prec_0p1956_to_0p1975_17of56_recovered_14_regressed_BOTH_"
    "controls_fire_KEEPALL_prec_0p1486_lt_FRAMES_gate_precision_keeper_SCRAMBLED_rc_0p45_lt_FRAMES_content_"
    "loadbearing_gate_design_sound_BUT_needs_real_parse_conclusion_MODERATE_OVER_READ_heuristic_crippled_"
    "dropped_split_sentences_plus_gate_false_negatives_put_hear_residual_53_misses_39_predicate_not_"
    "enumerated_4_gate_suppressed_4_pos_gate_6_span_39_break_prep_gerund_reduced_relative_complement_clause_"
    "relative_fronted_subordinate_multi_sentence_regressions_3span_3gate_8enum_4self_inflicted_multisentence_"
    "parser_29451_right_lever_on_engineering_grounds_not_because_heuristics_proven_unable_brain_shared_supply_"
    "structure_29455_composes_29473_cert_plus0")

RECOMPUTE = {
    "recompute_method": ("independent .venv process re-ran the cell's own run_all_arms(FULL_SLICE, clf) with "
        "V2._fit_clf; recomputed recall_ceiling per arm via recall_ceiling_of; then TRACED every residual "
        "FRAMES miss and every regression to its failure locus (predicate enumerated? gold patient a POS "
        "candidate? gate value? in local span?). All four arms reproduce BIT-EXACT vs metrics.json."),
    "arms": {
        "BASELINE":  {"recall_ceiling": 0.44, "n_miss": 56, "precision": 0.1956, "f1": 0.2708, "n_pred": 225},
        "KEEPALL":   {"recall_ceiling": 0.51, "n_miss": 49, "precision": 0.1486, "f1": 0.2301, "n_pred": 350},
        "FRAMES":    {"recall_ceiling": 0.47, "n_miss": 53, "precision": 0.1975, "f1": 0.2782, "n_pred": 243},
        "SCRAMBLED": {"recall_ceiling": 0.45, "n_miss": 55, "precision": 0.1557, "f1": 0.2314, "n_pred": 289},
    },
    "rise_frames_over_baseline": 0.03, "hf_floor": 0.05, "hp_bar": 0.65,
    "control_a_keepall_prec_lt_frames_prec": [0.1486, 0.1975, True],
    "control_b_scrambled_rc_lt_frames_rc": [0.45, 0.47, True],
    "n_recovered": 17, "n_regressed": 14,
    "residual_frames_miss_decomposition": {
        "total": 53,
        "predicate_not_enumerated": 39,
        "gate_suppressed_false_negative": 4,   # hear x2, put, tell (say/know override, put/hear vn false-neg)
        "gold_patient_not_in_POS_candidate_gate": 4,  # her/one/those/her partitive-demonstrative-pronoun
        "span_or_classifier": 6,
    },
    "predicate_not_enumerated_39_construction_breakdown": (
        "prep-gerund objects ('be careful in CHOOSING your places', 'lived by SELLING fish', 'for KEEPING the "
        "water'); reduced relatives / participial adjuncts ('sitting by the table... MAKING marks', 'seen a "
        "child DASH', 'being near', 'finding it LOCKED'); that/whether-complement clauses ('found that James "
        "HAD money', 'told him... GAVE', 'asked him whether he was DRAWING'); which/who relatives ('which his "
        "aunt had GIVEN him', 'who TAUGHT him'); fronted-subordinate main clause ('When they build..., they "
        "MAKE a dam' -- find_main_verb picked the subordinate 'build', the true main 'make' after the comma "
        "gets no trigger); multi-sentence-within-sid ('I OPEN the door' as a separate sentence in a stanza sid "
        "-- this is a case the baseline's split_sentences handled and the multipred path lost)."),
    "regression_decomposition_14": {
        "clean_span_or_patient_theft": ["L05_22 see/child", "L07_09 meet/boys (got 'plenty' not 'boys')",
                                        "L10_11 find/boy (boy dropped from found's local span)"],
        "gate_false_negative": ["L04_18 hear/you", "L08_02 hear/mew", "L10_36 put/head"],
        "enumeration_loss": {
            "self_inflicted_multi_sentence_split_loss": ["L04_19 nod/head", "L05_24 leave/room",
                                                         "L08_02 open/door", "L10_14 make/you"],
            "prep_gerund": ["L08_02 choose/places", "L08_08 choose/places"],
            "reduced_relative_participle": ["L10_11 make/marks"],
            "non_adjacent_coord_not_triggered": ["L07_06 say/lessons ('and had SAID' -- 'said' preceded by "
                                                 "'had' not 'and', no COORD_VP trigger)"],
        },
    },
    "gate_false_negative_evidence": {
        "put": {"in_override": False, "vn_admits_direct_object": False, "admits_patient": False,
                "note": "put clearly transitive ('put his head') -- VerbNet-auditor false-negative"},
        "hear": {"in_override": False, "vn_admits_direct_object": False, "admits_patient": False,
                 "note": "hear clearly transitive ('heard you') -- VerbNet-auditor false-negative"},
        "tell": {"in_override": True, "vn_admits_direct_object": True, "admits_patient": False,
                 "note": "override (report verb) suppresses real-object case 'told him the name'"},
    },
    "split_sentences_dropped_evidence": ("build_multipred_arm does `ORC.pos_tag_sentence(sent_text[sid])` on "
        "the WHOLE sid and never calls ORC.split_sentences; the BASELINE reader_svo (via "
        "load_slice_and_reader) DOES split per the leg-2 diagnostic (CITED exp_read_nested_clause_relative_"
        "third_reader_v1.py:260). Direct witness: L05_24 sid = '...I believe it was... Papa now left the "
        "room, saying...' -- FRAMES preds=[believe MAIN, say SUBORD_FAR], 'left' NEVER enumerated -> FRAMES "
        "emits []; BASELINE emits (left,papa,room). Regression is a dropped-splitting artifact, not a "
        "fundamental multi-predicate limit."),
    "careful_heuristic_ceiling_estimate": ("NOT RUN -- flagged as the un-closed cheap variant. Restoring "
        "split_sentences (recovers ~4 multi-sentence regressions + several residual misses the baseline "
        "already handled), fixing put/hear gate false-negatives (~2-3), a POS-gate patch for partitive/"
        "demonstrative pronouns (~2-3), and a fronted-subordinate detector would plausibly lift recall_ceiling "
        "into the low-0.60s, at or near the 0.65 bar. Estimate ONLY (hypothesis-pending-VET); the point is the "
        "0.47 headline UNDER-states a careful heuristic, so 0.47 must NOT be cited as evidence heuristics can't "
        "reach the bar."),
}

atom = {
    "id": AID, "name": NAME, "corpus": "math", "tier": "MEASURED_MECHANISM",
    "kind": "experiment_landed_vet", "cert_status": "proven-bound", "cert_class": CERT_CLASS,
    "plain_language": PLAIN,
    "importance": ("HIGH (this is the leg-2 DECISIVE TEST that steers the 'find-the-predicate' strategy for the "
        "reader -- it determines whether the next lever is 'wire in the transition parser 29451' vs 'extend the "
        "cheap triggers'). VALUE: (1) MAPS where the 29473 recall ceiling loss lives at token granularity -- "
        "of the 53 residual FRAMES misses, 39 are predicate-not-enumerated and break down into a small set of "
        "named constructions (prep-gerund, reduced relative/participle, that/whether-complement, which/who "
        "relative, fronted-subordinate, multi-sentence). (2) PREVENTS re-running NAIVE heuristic-trigger "
        "variants that chase the 0.65 bar with more ad-hoc cues. (3) CORRECTS the cell's own HARD_FAIL "
        "conclusion DOWNWARD: 'needs a real parse / cheap option exhausted' is a MODERATE over-read because the "
        "tested heuristic was crippled (dropped the baseline's split_sentences; VerbNet gate false-negatives), "
        "so the cheap option was UNDER-tested, not proven-insufficient -- the Director must NOT prematurely "
        "close the cheap option on this cell's 0.47 / 14-regressions evidence. (4) The parser IS still the "
        "right lever, but on ENGINEERING grounds (principledly subsumes every trigger + fixes span-assignment "
        "regressions), which is the honest, durable justification. +0 CERT (a mapped bound / negative on a "
        "crippled heuristic, not a new capability)."),
    "description": NAME,
    "aliases": [
        "multi-predicate + VerbNet-subcat-gate reader lifts recall_ceiling only 0.44 -> 0.47 (+0.03, below 0.05 floor, far below 0.65 bar) -- HARD_FAIL band",
        "BOTH must-fail controls fire (KEEPALL prec 0.1486 < FRAMES 0.1975 gate=precision-keeper; SCRAMBLED rc 0.45 < FRAMES 0.47 content-load-bearing) -> gate DESIGN directionally sound",
        "cell 'needs a real parse' conclusion is a MODERATE OVER-READ: heuristic crippled by dropped split_sentences + VerbNet gate false-negatives (put/hear vn=False) -> cheap option UNDER-tested not proven-insufficient",
        "residual 53 FRAMES misses = 39 predicate-not-enumerated + 4 gate-suppressed(false-neg) + 4 POS-gate + 6 span/classifier",
        "the 39 predicate-not-enumerated: prep-gerund / reduced-relative-participle / that-whether-complement / which-who-relative / fronted-subordinate / multi-sentence-within-sid",
        "14 regressions NOT dominated by span-theft: only 3/14 clean span (see/child, meet/boys, find/boy); 3/14 gate false-neg (hear/hear/put); 8/14 enumeration-loss (4 self-inflicted multi-sentence split loss)",
        "a real parse would fix 11/14 regressions, but 7/14 (gate false-neg + multi-sentence) are ALSO cheaply fixable WITHOUT a parse",
        "STRATEGIC: transition parser 29451 (0.81 UAS) is the right lever on ENGINEERING grounds (subsumes ad-hoc triggers + fixes span regressions), NOT because heuristics are proven unable to reach 0.65",
        "brain-check: brain parses incrementally per-predicate with existing grammar, not verb-trigger scanning -> 'supply a real parse' is a brain-SHARED pointer consistent with 29455 supply-structure-learn-content",
    ],
    "ts_iso": ts_iso, "ts": ts,
    "serves_capability": ("maps_the_reader_multi_predicate_extraction_recall_ceiling_and_steers_the_find_"
        "predicate_lever_cheap_heuristic_triggers_reach_only_0p47_but_were_under_tested_dropped_split_"
        "sentences_plus_gate_false_negatives_so_conclusion_needs_real_parse_is_directionally_right_but_over_"
        "read_the_transition_parser_29451_is_the_principled_subsuming_lever_on_engineering_grounds"),
    "metadata": {
        "seq": NEW_SEQ, "verdict": "HARD_FAIL_MULTIPRED_NEEDS_REAL_PARSE", "grade": "MEASURED_MECHANISM",
        "cell": cell_path, "cell_commit": "19526435a", "cell_content_sha256_16": cell_sha,
        "metrics_path": "data/exp_multipred_subcat_argstruct_recall_v1/metrics.json",
        "verified_off_data": True, "composes_seq": [29473],
        "recompute": RECOMPUTE,
        "framing_correction": [
            ("LOAD-BEARING (this atom steers the find-predicate strategy): the cell's HARD_FAIL conclusion "
             "'multi-predicate needs a REAL parse, cheap frame-lookup insufficient' is DIRECTIONALLY correct "
             "but a MODERATE OVER-READ of THIS cell. The tested heuristic was CRIPPLED by two self-inflicted "
             "defects: (1) the multipred candidate-gen path DROPPED the baseline reader's ORC.split_sentences "
             "(it POS-tags the whole sid as one sequence and never clause/sentence-splits), so multi-sentence "
             "sids and later-sentence main verbs are no longer enumerated -- directly causing ~4 of the 14 "
             "regressions and several residual misses the BASELINE handled; (2) the VerbNet-auditor gate has "
             "FALSE-NEGATIVES (vn_admits_direct_object('put')=False, ('hear')=False) that HARD-SUPPRESS "
             "genuinely-transitive instances. So the cheap option was UNDER-tested, not proven-insufficient. "
             "Director MUST NOT close the cheap option as 'proven insufficient' on this cell's 0.47 / "
             "14-regression evidence."),
            ("The cell frames 'the gate DESIGN is sound' (both controls fire) as a clean positive. This is "
             "DIRECTIONALLY true (KEEPALL prec 0.1486 < FRAMES 0.1975; SCRAMBLED rc 0.45 < FRAMES 0.47 -- the "
             "gate does precision-preserving work and the frame content is load-bearing) BUT slightly "
             "OVERSTATED: the gate OVER-SUPPRESSES via VerbNet false-negatives (put/hear) and via the "
             "report/cognition override on real-object instances (tell 'told him the NAME'). A sound-in-"
             "aggregate gate with correctable false-negatives, not a clean one."),
            ("Q3 (are the 14 regressions span-assignment or a new error class?): MIXED, and NOT dominated by "
             "span-theft. Only 3/14 are clean span/patient-theft (multi-pred steals or drops the patient from "
             "the right verb: see/child, meet/boys, find/boy). 3/14 are gate false-negatives (hear/hear/put). "
             "8/14 are enumeration-loss (the gold verb was never enumerated), and 4 of those 8 are the self-"
             "inflicted dropped-split_sentences (nod/leave/open/make-you). A real parse would fix 11/14 (span "
             "3 + enumeration 8), but 7/14 (gate false-neg 3 + multi-sentence 4) are ALSO cheaply fixable "
             "WITHOUT a parse -- so the regressions do NOT cleanly argue 'only a real parse can fix this.'"),
            ("STRATEGIC (the actual steer): the transition parser 29451 (0.81 UAS) IS the right next lever, but "
             "the HONEST justification is ENGINEERING cleanliness, not 'heuristics are proven unable to reach "
             "0.65.' Every remaining cheap trigger (bare 'that'/'whether'-complement, bare '-ing' participle, "
             "sentence-boundary re-split, fronted-subordinate) is an ambiguous, precision-risky cue; the parser "
             "subsumes ALL of them principledly at once AND fixes the span-assignment regressions. A careful "
             "heuristic (keep split_sentences + fix gate + fronted-subordinate) was NOT run and is plausibly in "
             "the low-0.60s -- so cite the parser as the SUBSUMING lever, not as the only-thing-that-can-work."),
        ],
        "brain_check": ("CONFIRMED brain-SHARED mechanism pointer (not a substrate-specific bug). The brain "
            "does NOT find predicates by verb-trigger scanning; it parses incrementally with grammar it already "
            "has, and every finite/nonfinite verb pre-activates its OWN argument-structure slots at its own "
            "locus as it is encountered (Levin / construction-frame picture, per the cell's own brain-check). "
            "The reader's single-pass-per-sentence find_main_verb is the substrate's own prior implementation "
            "choice, and the indicated fix -- give the reader a real incremental parse so every predicate opens "
            "its own frame -- restores the brain-faithful picture. This is consistent with the banked 29455 "
            "'supply the STRUCTURE, learn the CONTENT' thesis: the structure (a parse) is the missing supply, "
            "not more per-verb content. So 'supply a real parse' is a supply-structure pointer, NOT evidence of "
            "a bug unique to this substrate."),
        "positive_control_check": ("Test design VALIDATED-SOUND per STANDARD_HF_CLOSURE discipline: BASELINE "
            "precision 0.1956 is in-band (0.05-0.95, an unsaturated real wall, not vacuous); both must-fail "
            "controls FIRE correctly (KEEPALL isolates the gate as precision-keeper; SCRAMBLED isolates frame "
            "content as load-bearing) -- so the gate mechanism genuinely does the work the design claims. This "
            "is a GENUINE substantive result, NOT a test-design failure. Attribution: the measured 0.47 bound "
            "is real for THIS heuristic, with a MINOR test-IMPLEMENTATION contamination (dropped split_sentences "
            "+ gate false-negatives) that inflates the regression count and depresses FRAMES recall -- flagged "
            "as a framing correction, does NOT overturn the MM disposition."),
        "metrics": {
            "baseline_recall_ceiling": 0.44, "frames_recall_ceiling": 0.47, "rise": 0.03,
            "keepall_recall_ceiling": 0.51, "scrambled_recall_ceiling": 0.45,
            "hf_floor": 0.05, "hp_bar": 0.65,
            "baseline_f1": 0.2708, "frames_f1": 0.2782,
            "baseline_precision": 0.1956, "frames_precision": 0.1975, "keepall_precision": 0.1486,
            "n_recovered": 17, "n_regressed": 14, "n_sentences": 163,
            "residual_frames_misses": 53, "predicate_not_enumerated": 39,
            "gate_suppressed_false_neg": 4, "pos_gate_drop": 4, "span_or_classifier": 6,
            "control_a_gate_beats_noframe": True, "control_b_frames_beat_scrambled": True,
            "baseline_in_band": True, "verdict": "HARD_FAIL_MULTIPRED_NEEDS_REAL_PARSE",
        },
        "over_reads_corrected": [
            ("DO NOT read the 0.47 recall_ceiling / +0.03 rise / 14 regressions as PROOF that heuristic "
             "multi-predicate triggers cannot reach the 0.65 bar. The tested heuristic dropped the baseline's "
             "split_sentences and had VerbNet gate false-negatives; a careful heuristic (keep splitting + fix "
             "gate + fronted-subordinate) was NOT run and is plausibly low-0.60s. Cite '0.47 for THIS crippled "
             "trigger set', not 'heuristics max out at 0.47'."),
            ("DO NOT frame the 14 regressions as 'multi-pred steals patients (span-assignment)'. Only 3/14 are "
             "clean span-theft; 3/14 gate false-negatives, 8/14 enumeration-loss (4 self-inflicted split-loss). "
             "Half the regressions are cheaply fixable without a parse."),
            ("DO NOT frame the gate as clean. It is sound-in-aggregate (both controls fire) BUT over-suppresses "
             "via VerbNet false-negatives (put/hear) and override real-object cases (tell). Correctable."),
            ("DO NOT promote to a capability win or a HARD_PASS. recall_ceiling 0.47 << 0.65; F1 lift +0.007 is "
             "marginal. This is a mapped bound + a strategic steer, CERT +0."),
            ("DO NOT read this as a clean substantive negative on the multi-predicate IDEA. The idea is sound "
             "(brain-faithful per-predicate frames); it is the cheap-trigger IMPLEMENTATION that is bounded, "
             "and the indicated fix (a real parse) is a supply-structure pointer, not a dead end."),
        ],
        "cross_arc_overlap_check": ("substrate_query 'multi-predicate extraction subcategorization frame gate "
            "recall ceiling per-verb argument structure' -> top hit generic FrameNet/WordNet 'Categorization' "
            "cosine 0.3057, then a HotpotQA multi-hop note 0.3037, all concept/note atoms; NONE is a prior "
            "EXPERIMENT cell above the 0.30 concept-overlap threshold. CONFIRMED genuinely novel in the arc: "
            "this is the leg-2 decisive test extending the 29473 reader (its intended lineage), not a "
            "rediscovery. No July-1-style duplicate-rediscovery pattern."),
        "composes_with": [
            ("29473 (pivot_rich_knowledge_full_reader_integration_v1, MM): established the reader is EXTRACTION-"
             "RECALL-BOUND at recall_ceiling 0.44 (56/100 gold patients never generated as candidates), which "
             "caps end-to-end F1 regardless of perfect disambiguation. THIS cell is the leg-2 decisive test of "
             "the highest-leverage (68%) slice of that bound -- the multi-predicate extraction miss. 29473 is "
             "NOT superseded; this atom EXTENDS it with the finding that the cheap multi-predicate trigger "
             "lever recovers only +0.03 as-implemented (and was under-tested), so the recall bound is not "
             "cleared cheaply and the indicated principled lever is a real parse (29451)."),
            ("leg-2 diagnostic note research_recall_miss_extraction_vs_filter_diagnosis_2026-07-23.md (NOT a "
             "banked atom): localized the 56-miss set as 54/56 extraction / 38/56 (68%) multi-predicate / "
             "single-verb-per-sentence. This cell operationalizes and tests its OWN 'cheap decisive test' "
             "recommendation (a second argument-structure pass per predicate via a subcat-frame lookup) and "
             "lands the pre-registered HARD_FAIL floor the diagnostic itself pre-set."),
        ],
        "revival_criteria": [
            ("THE INDICATED PRINCIPLED LEVER: wire in the transition parser (29451, incremental transition "
             "parser, 0.81 UAS) as the candidate-generation front-end -- it gives every finite/nonfinite verb "
             "its own nsubj/dobj/xcomp/ccomp slot, subsuming find_main_verb + single-pass role assignment and "
             "every ad-hoc trigger (COORD_VP/INF_COMP/SUBORD/prep-gerund/reduced-relative/complement), AND "
             "fixes the span-assignment regressions. HARD_PASS target: recall_ceiling >= 0.65 with net-positive "
             "regression balance."),
            ("THE UN-CLOSED CHEAP VARIANT (must be acknowledged before declaring the cheap option dead): a "
             "CAREFUL heuristic = KEEP the baseline's ORC.split_sentences (do not drop it) + run find_predicates "
             "PER split segment + FIX the VerbNet gate false-negatives (put/hear) + add a fronted-subordinate-"
             "main-clause detector + a POS-gate patch for partitive/demonstrative pronouns. Estimated low-0.60s "
             "(hypothesis-pending-VET). If it lands >= 0.62 it materially changes whether the parser is "
             "necessary vs merely cleaner."),
            ("Re-audit the gold for the annotation-internal inconsistencies the leg-2 diagnostic flagged "
             "(coref-surface-vs-gold-surface scoring artifacts; rub-against POS-vs-NOPAT) before treating the "
             "residual as pure reader gaps -- some 'misses' are scoring-protocol artifacts, not extraction "
             "failures."),
        ],
        "cites": [
            "Fix_28_verify_off_data_not_verdict_msg",
            "symmetric_anti_negativity_verify_both_directions_USER",
            "cited_number_must_reproduce_from_cell",
            "verify_the_referent_atom_ids_mechanism_metric_regime",
            "substrate_kb_concept_overlap_check_on_schema_vet_and_atomize_USER",
            "every_negative_check_how_the_brain_does_it_proactively_USER",
            "dont_assume_brain_check_outcome_brain_may_fail_same_way_then_fix_is_native",
            "strategic_reads_run_ahead_of_evidence_caveat_interpretation_not_just_verdicts",
            "positive_control_clears_own_floor_before_HF_attribution_auditor_discipline",
        ],
        "strategic_implication": ("Steers the 'find-the-predicate' leg of the reader roadmap. The cheap multi-"
            "predicate-trigger + subcat-gate lever recovers only +0.03 recall_ceiling AS IMPLEMENTED, but the "
            "implementation was crippled (dropped split_sentences + VerbNet gate false-negatives), so the "
            "cheap option is UNDER-tested, not proven-insufficient -- do NOT prematurely close it on this "
            "cell. The transition parser (29451, 0.81 UAS) is the right next lever on ENGINEERING grounds: it "
            "principledly subsumes every ad-hoc trigger (coordinate-VP, infinitival, subordinator, prep-gerund, "
            "reduced-relative, complement-clause) AND fixes the span-assignment regressions, which stacking "
            "ambiguous cheap cues cannot do cleanly. Consistent with 29455 (supply the structure, learn the "
            "content): the missing supply here is a real parse, not more per-verb frame content. Prevents re-"
            "running naive heuristic-trigger variants while keeping the un-closed careful-heuristic variant "
            "honestly on the table."),
        "auditor": "hdi_skunkworks", "atomized_date": "2026-07-23",
        "cross_arc_overlap": "top hit generic 'Categorization' 0.3057; NO experiment cell >0.30; novel leg-2 test extending 29473",
        "needs_orchestrator_store_sync": True,
        "local_write_only_no_origin_push_no_remote_persist": True,
    },
}
json.loads(json.dumps(atom))

# ---- A5 atomic append (BINARY-SAFE newline="") ----
new_line = json.dumps(atom, ensure_ascii=False)
assert "\r" not in new_line and "\n" not in new_line
new_atoms_text = "\n".join(atom_lines + [new_line]) + "\n"
d = os.path.dirname(os.path.abspath(ATOMS))
fd, tmp = tempfile.mkstemp(dir=d, suffix=".tmp"); os.close(fd)
with open(tmp, "w", encoding="utf-8", newline="") as f:
    f.write(new_atoms_text); f.flush(); os.fsync(f.fileno())
os.replace(tmp, ATOMS)
with open(ATOMS, "rb") as f:
    raw = f.read()
assert b"\r\n" not in raw, "CRLF doubling in atoms.jsonl"
with open(ATOMS, encoding="utf-8") as f:
    v = [json.loads(l) for l in f.read().splitlines() if l.strip()]
assert len(v) == N_ATOMS + 1, (len(v), N_ATOMS)
assert v[-1]["id"] == AID and v[-1]["tier"] == "MEASURED_MECHANISM" and v[-1]["cert_status"] == "proven-bound"
print(f"ATOMS OK: {N_ATOMS} -> {len(v)} atoms; new atom verified; no CRLF doubling.")

# ---- ledger entry ----
ledger = {
    "seq": NEW_SEQ, "op": "landed_vet_atomize", "corpus": "math", "tier": "MEASURED_MECHANISM",
    "cert_status": "proven-bound", "cert_class": CERT_CLASS,
    "atom_id": AID, "anchor_name": "multipred_subcat_argstruct_recall_v1",
    "cell": cell_path, "cell_commit": "19526435a", "cell_content_sha256_16": cell_sha,
    "auditor": "hdi_skunkworks", "verified_off_data": True,
    "cert_delta": 0, "net_cert_delta": 0, "composes_seq": [29473],
    "decision": ("landed_vet_atomize HARD_FAIL_MULTIPRED_NEEDS_REAL_PARSE -> MM (proven-bound; leg-2 decisive "
        "test of the 29473 reader extraction-recall ceiling). Independent .venv off-disk recompute (re-ran the "
        "cell's own run_all_arms(FULL_SLICE) + traced every residual miss and regression to its failure "
        "locus): all four arms reproduce BIT-EXACT -- BASELINE rc 0.44, FRAMES rc 0.47 (rise +0.03 < 0.05 "
        "floor, << 0.65 bar), KEEPALL rc 0.51, SCRAMBLED rc 0.45; F1 0.2708->0.2782; prec 0.1956->0.1975 "
        "(KEEPALL 0.1486); 17 recovered 14 regressed; BOTH must-fail controls FIRE (control_a KEEPALL "
        "prec<FRAMES prec; control_b SCRAMBLED rc<FRAMES rc). (1) NUMBERS y + CONTROLS FIRE y -> the subcat-"
        "gate DESIGN is directionally sound and this is a GENUINE substantive result (BASELINE prec 0.1956 "
        "in-band, not vacuous). (2) LOAD-BEARING CORRECTION: the cell's 'needs a REAL parse / cheap option "
        "exhausted' HARD_FAIL conclusion is a MODERATE OVER-READ -- the tested heuristic was CRIPPLED by two "
        "self-inflicted defects: (i) the multipred path DROPPED the baseline reader's ORC.split_sentences (it "
        "POS-tags the whole sid, never clause/sentence-splits) -> multi-sentence sids + later-sentence main "
        "verbs no longer enumerated (witness L05_24 'Papa now left the room': BASELINE (left,papa,room), "
        "FRAMES emits [] because 'left' never enumerated); (ii) VerbNet gate FALSE-NEGATIVES vn_admits_direct_"
        "object('put')=False ('hear')=False hard-suppress transitive instances. So the cheap option was UNDER-"
        "tested, not proven-insufficient. (3) RESIDUAL 53 FRAMES misses decompose: 39 predicate-not-enumerated "
        "(prep-gerund 'in choosing' / reduced-relative-participle 'making marks','child dash' / that-whether-"
        "complement 'found that James had money' / which-who relative / fronted-subordinate 'when they build, "
        "they make a dam' / multi-sentence-within-sid), 4 gate-suppressed false-neg, 4 POS-gate drop, 6 span/"
        "classifier. (4) Q3 REGRESSIONS are NOT dominated by span-theft: only 3/14 clean span (see/child, "
        "meet/boys, find/boy); 3/14 gate false-neg; 8/14 enumeration-loss (4 self-inflicted multi-sentence "
        "split-loss). A real parse fixes 11/14 but 7/14 are ALSO cheaply fixable without one. (5) BRAIN-CHECK "
        "confirmed brain-SHARED pointer: brain parses incrementally per-predicate with existing grammar, not "
        "verb-trigger scanning -> 'supply a real parse' = supply-structure fix consistent with 29455, not a "
        "substrate bug. STRATEGIC: transition parser 29451 (0.81 UAS) is the right lever on ENGINEERING grounds "
        "(subsumes every trigger + fixes span regressions), NOT because heuristics are proven unable to reach "
        "0.65 -- the un-closed careful-heuristic variant (keep split + fix gate + fronted-subordinate) is "
        "plausibly low-0.60s and must stay on the table. Cross-arc overlap: top hit generic 'Categorization' "
        "0.3057, NO experiment cell >0.30 -> novel leg-2 test extending 29473. Grade MM (mapped bound + "
        "strategic steer; cheap option under-tested not closed). CERT +0. Extends 29473 (not superseded). "
        "LOCAL-ONLY needs orchestrator sync."),
    "note": ("LEG-2 DECISIVE TEST banked MM. Cheap multi-predicate triggers (COORD_VP+INF_COMP+SUBORD) + VerbNet "
        "subcat gate lift recall_ceiling only 0.44->0.47 (+0.03, below 0.05 floor); both must-fail controls "
        "fire so the gate DESIGN is sound. LOAD-BEARING: the cell's HARD_FAIL 'needs a real parse' is a "
        "MODERATE OVER-READ -- the heuristic was crippled (dropped baseline split_sentences + gate false-"
        "negatives put/hear), so the cheap option was UNDER-tested. Residual 53 misses = 39 predicate-not-"
        "enumerated (prep-gerund/reduced-relative/complement-clause/fronted-subordinate/multi-sentence). 14 "
        "regressions NOT dominated by span-theft (3 span / 3 gate-false-neg / 8 enumeration, 4 self-inflicted). "
        "Parser 29451 (0.81 UAS) is the right lever on ENGINEERING grounds (subsumes triggers + fixes span), "
        "NOT because heuristics proven unable. Brain-check = supply-structure pointer (29455). Do NOT "
        "prematurely close the cheap option. Extends 29473. MM not CG/HF. LOCAL-ONLY."),
    "cross_arc_overlap": "top hit generic 'Categorization' 0.3057; NO experiment cell >0.30; novel leg-2 test extending 29473",
    "ts_iso": ts_iso, "ts": ts,
    "needs_orchestrator_store_sync": True, "local_write_only_no_origin_push_no_remote_persist": True,
}
json.loads(json.dumps(ledger))
new_led_line = json.dumps(ledger, ensure_ascii=False)
assert "\r" not in new_led_line and "\n" not in new_led_line
new_ledger_text = "\n".join(ledger_lines + [new_led_line]) + "\n"
dl = os.path.dirname(os.path.abspath(LEDGER))
fd2, tmp2 = tempfile.mkstemp(dir=dl, suffix=".tmp"); os.close(fd2)
with open(tmp2, "w", encoding="utf-8", newline="") as f:
    f.write(new_ledger_text); f.flush(); os.fsync(f.fileno())
os.replace(tmp2, LEDGER)
with open(LEDGER, "rb") as f:
    rawl = f.read()
assert b"\r\n" not in rawl, "CRLF doubling in cert_ledger.jsonl"
with open(LEDGER, encoding="utf-8") as f:
    vl = [json.loads(l) for l in f.read().splitlines() if l.strip()]
assert len(vl) == len(ledger_lines) + 1
assert vl[-1]["atom_id"] == AID and vl[-1]["ts"] == ts and vl[-1]["seq"] == NEW_SEQ
assert vl[-2]["seq"] == last_seq, "seq continuity broken"
print(f"LEDGER OK: {len(ledger_lines)} -> {len(vl)} entries; seq {last_seq} -> {NEW_SEQ}; ts matches; no CRLF.")
print("ATOM_ID_TAIL:", AID[-70:])
print("DONE. LOCAL-ONLY; no origin push; no remote persist. needs_orchestrator_store_sync=True")
