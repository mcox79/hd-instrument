"""
A5-gated LOCAL-ONLY atomize: exp_learner_implicative_sign_supplied_generalization_v1.
tier=MEASURED_MECHANISM / proven-bound / CERT +1. The culmination of 29490's diagnosed
"supply the fact, compose the rule" next step: swap the one-hot VERB feature (29490, which
structurally blocked held-out-verb transfer) for the SUPPLIED Karttunen implicative SIGN
(gold-blind IMPLICATIVE_LEXICON) + negation. Leave-one-VERB-out over 9 verbs.

INDEPENDENT off-disk recompute (skunkworks pure-python arms off tools/build_negation_
factuality_gold.build_implicative_gold, NOT the author plugin code) reproduces every headline:
  n=114, 9 verbs; joint cells (pos,False)=25 (pos,True)=6[bother-only] (neg,False)=60 (neg,True)=23;
  gold==Karttunen table 0 mismatches (gold-blind).
  COVERED (n=108): additive/linear=0.6574, full-joint-lookup(sim)=1.000, symbolic-XNOR=1.000.
  UNCOVERED (n=6, bother (pos,True), gold NOT_REALIZED, cov=0): additive=0.000, symbolic-XNOR=1.000.
  ruleind hypothesis (bother-held-out fold) = {(sign=neg,neg=False)->NOT_REALIZED cov60 prec1.0;
    [] default->REALIZED} -> a CONJUNCTION-LOOKUP, NOT the XNOR formula; predicts REALIZED (WRONG)
    on the unseen (pos,True) cell. A symbolic XNOR fills it correctly (1.000).
Cell re-run reproduces verdict + acc_module_covered=1.000 margin_lin=0.343 margin_sim=0.000
scramble_delta=0.412 acc_module_uncovered=0.000 BOUND_CONFIRMED_ASSOCIATIVE_NOT_SYMBOLIC.
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
existing_ids = {(o.get("atom_id") or o.get("id")) for o in parsed}
assert not any("\r" in l for l in atom_lines[-5:]), "existing atoms carry CR -- investigate"
with open(LEDGER, encoding="utf-8") as f:
    ledger_lines = [l for l in f.read().splitlines() if l.strip()]
last_seq = json.loads(ledger_lines[-1])["seq"]
NEW_SEQ = last_seq + 1
STORE_HEAD = last_seq
print(f"PRE-GATE: {N_ATOMS} atoms load-valid; ledger last seq {last_seq}; NEW_SEQ={NEW_SEQ}")

# ---- off-disk recompute confirmation (re-assert numbers off metrics.json) ----
m = json.load(open("data/exp_learner_implicative_sign_supplied_generalization_v1/metrics.json", encoding="utf-8"))
assert m["verdict"] == "HARD_PASS_BEYOND_LINEAR_NOT_BEYOND_SIMILARITY"
assert m["positive_control"]["chosen_name"] == "ruleind" and m["positive_control"]["passed"] is True
assert abs(m["positive_control"]["compression_ratios"]["ruleind"] - 9.841308894082914) < 1e-9
assert m["module_chosen_name_per_fold"] == {"ruleind": 9}
assert m["n_covered_test"] == 108 and m["n_uncovered_test"] == 6
assert abs(m["acc_module_covered"] - 1.0) < 1e-9
assert abs(m["acc_linear_covered"] - 0.6574074074074074) < 1e-9
assert abs(m["margin_module_linear_covered"] - 0.34259259259259256) < 1e-9
assert abs(m["acc_simvote_covered"] - 1.0) < 1e-9
assert abs(m["margin_module_simvote_covered"] - 0.0) < 1e-12
assert abs(m["scramble_delta"] - 0.4122807017543859) < 1e-9
assert m["acc_module_uncovered"] == 0.0 and m["acc_simvote_uncovered"] == 0.0 and m["acc_linear_uncovered"] == 0.0
assert m["unseen_joint_cell_extrapolation"] == "BOUND_CONFIRMED_ASSOCIATIVE_NOT_SYMBOLIC"
assert m["is_similarity_near_chance_on_heldout"] is False
print("OFF-DISK OK: COVERED module=1.000 linear=0.6574 (+0.343) simvote=1.000 (+0.000) scramble_delta=0.412 "
      "| UNCOVERED all-arms 0.000 ASSOCIATIVE_NOT_SYMBOLIC | module auto-selects ruleind 9/9 | XOR ctrl ruleind 9.84x passed")

cell_path = "experiments/exp_learner_implicative_sign_supplied_generalization_v1.py"
cell_sha = hashlib.sha256(open(cell_path, "rb").read()).hexdigest()[:16]
CELL_COMMIT = "378f01c2b"

ts = time.time()
ts_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

AID = ("math::learner_implicative_sign_supplied_generalization_v1_MEASURED_MECHANISM_the_culmination_of_29490s_"
    "supply_the_fact_compose_the_rule_next_step_swap_the_one_hot_VERB_identity_feature_that_structurally_blocked_"
    "held_out_verb_transfer_for_the_SUPPLIED_Karttunen_implicative_SIGN_gold_blind_IMPLICATIVE_LEXICON_plus_"
    "negation_leave_one_VERB_out_over_9_verbs_TWO_poles_neither_over_read_POSITIVE_supplying_the_lexical_SIGN_"
    "fact_gives_cross_verb_overlap_that_UNBLOCKS_the_held_out_verb_transfer_one_hot_identity_29490_made_"
    "structurally_impossible_on_the_COVERED_subset_n108_module_1p000_vs_linear_0p6574_margin_plus0p343_matches_"
    "the_Minsky_Papert_XNOR_additive_ceiling_and_the_module_AUTO_SELECTS_ruleind_9of9_folds_data_driven_no_task_"
    "name_branch_XOR_positive_control_ruleind_9p8413_passed_and_sign_scramble_delta_0p412_gt_0p25_floor_the_"
    "supplied_sign_is_LOAD_BEARING_scramble_control_bug_fixed_pre_run_so_it_now_BITES_BOUND_the_current_learners_"
    "are_ASSOCIATIVE_not_SYMBOLIC_beyond_linear_but_NOT_beyond_similarity_simvote_TIES_module_at_1p000_margin_"
    "0p000_because_the_2_binary_feature_sign_neg_joint_space_is_fully_ENUMERABLE_4_cells_kNN_lookup_solves_any_"
    "POPULATED_cell_linear_cannot_do_XNOR_similarity_can_once_cells_populated_is_similarity_near_chance_FALSE_and_"
    "the_UNCOVERED_subset_n6_bother_negated_pos_True_gold_NOT_REALIZED_with_ZERO_training_exemplars_of_that_joint_"
    "cell_ANYWHERE_scores_0p000_in_ALL_3_arms_including_module_ruleind_because_ruleind_learned_sign_neg_False_"
    "arrow_NOT_REALIZED_plus_default_arrow_REALIZED_a_CONJUNCTION_LOOKUP_not_the_compact_XNOR_FORMULA_so_the_"
    "unseen_pos_True_cell_falls_to_the_REALIZED_default_WRONG_a_skunkworks_independent_symbolic_XNOR_arm_FILLS_"
    "the_unseen_cell_at_1p000_confirming_the_learners_need_ge1_exemplar_of_the_joint_cell_associative_not_a_"
    "symbolic_rule_that_extrapolates_NOT_brain_shared_a_human_given_Karttunens_rule_plus_the_supplied_sign_"
    "computes_the_entailment_for_the_unseen_combination_by_symbolic_rule_application_so_this_is_a_genuine_"
    "SUBSTRATE_bound_associative_lookup_not_symbolic_rule_application_DISTINCT_from_29490s_brain_SHARED_lexical_"
    "polarity_bound_the_INDICATED_FIX_is_the_north_star_a_compact_rule_program_induction_plugin_symbolic_"
    "regression_Bayesian_program_induction_XOR_primitive_learner_that_induces_the_XNOR_FORMULA_and_fills_unseen_"
    "feature_combinations_the_module_29487_architecture_hosts_it_29489_proved_plugin_extensibility_supply_the_"
    "fact_compose_the_rule_validated_at_the_verb_transfer_level_symbolic_generalization_is_the_next_lever_"
    "composes_29490_29485_29487_29489_CERT_plus1_LOCAL_ONLY_2026-07-23")
assert AID not in existing_ids, "duplicate atom id"

HEADLINE = (
    "learner_implicative_sign_supplied_generalization_v1 -> MEASURED_MECHANISM (CERT+1). Executes 29490's "
    "diagnosed 'supply the fact, compose the rule' next step: the feature is swapped from one-hot VERB identity "
    "(which had ZERO cross-verb overlap so nothing could transfer) to the SUPPLIED Karttunen implicative SIGN "
    "(gold-blind IMPLICATIVE_LEXICON) + negation. TWO poles, neither over-read. POSITIVE (verb-transfer win): "
    "supplying the SIGN fact gives cross-verb overlap that UNBLOCKS held-out-verb transfer -- on the COVERED "
    "subset (n=108) module=1.000 vs linear=0.657 (+0.343, matches the Minsky-Papert XNOR additive ceiling); the "
    "module AUTO-SELECTS ruleind 9/9 folds (data-driven, no task-name branch; XOR positive control ruleind 9.84x "
    "passed); sign-scramble delta=0.412 (>0.25 floor) so the supplied sign is LOAD-BEARING (scramble-control bug "
    "fixed pre-run so it now bites). BOUND (associative not symbolic): beyond-linear but NOT beyond-similarity -- "
    "simvote TIES module at 1.000 (margin 0.000) because the 2-binary-feature (sign,neg) joint space is fully "
    "ENUMERABLE (4 cells), so a kNN lookup solves any POPULATED cell (linear can't do XNOR; similarity can once "
    "cells are populated). The UNCOVERED subset (n=6, bother-negated (pos,True), ZERO joint-cell exemplars "
    "anywhere) scores 0.000 in ALL 3 arms incl. module/ruleind: ruleind learned {(sign=neg,neg=False)->"
    "NOT_REALIZED; default->REALIZED} -- a CONJUNCTION-LOOKUP, not the compact XNOR FORMULA -- so the unseen "
    "(pos,True) cell falls to the REALIZED default (WRONG). An independent symbolic-XNOR arm FILLS the unseen "
    "cell at 1.000. So the current learners are ASSOCIATIVE (need >=1 exemplar of the joint cell), not SYMBOLIC. "
    "NOT brain-shared: a human given Karttunen's rule + the supplied sign computes the unseen combination by "
    "symbolic rule application -- a genuine SUBSTRATE bound (associative-lookup, not symbolic-rule-application), "
    "distinct from 29490's brain-SHARED lexical-polarity bound. INDICATED FIX = the north-star compact-rule / "
    "program-induction plugin (symbolic regression / Bayesian program induction / XOR-primitive learner) that "
    "induces the XNOR formula and fills unseen feature-combinations; the module (29487) architecture hosts it, "
    "29489 proved plugin extensibility. 'Supply the fact, compose the rule' validated at the verb-transfer level; "
    "true symbolic generalization is the next lever.")

NOTE = (
    "MEASURED_MECHANISM CERT+1 (HARD_PASS_BEYOND_LINEAR_NOT_BEYOND_SIMILARITY; two poles). POSITIVE: the fix over "
    "29490 lands -- supplying the Karttunen SIGN (cross-verb overlap) UNBLOCKS held-out-verb transfer that "
    "one-hot verb identity made structurally impossible; COVERED (n=108) module=1.000 vs linear=0.657 (+0.343, "
    "the XNOR additive ceiling), module auto-selects ruleind 9/9 (XOR ctrl ruleind 9.84x passed), sign-scramble "
    "delta=0.412 confirms the supplied sign is load-bearing (control bug fixed pre-run so it now bites). BOUND: "
    "beyond-linear NOT beyond-similarity -- simvote ties at 1.000 because the (sign,neg) joint space is a fully "
    "enumerable 4-cell table (kNN solves any populated cell). UNCOVERED (n=6 bother-negated (pos,True), zero "
    "joint-cell exemplars) = 0.000 in ALL arms incl. ruleind, which learned a conjunction-lookup {(neg,False)->"
    "NOT_REALIZED; default->REALIZED}, NOT the XNOR formula -> defaults REALIZED (wrong) on the unseen cell; an "
    "independent symbolic XNOR fills it at 1.000. So learners are ASSOCIATIVE (need >=1 joint-cell exemplar), not "
    "SYMBOLIC; NOT brain-shared (a human applies Karttunen's rule to the unseen cell) -> a genuine substrate "
    "bound, distinct from 29490's brain-shared lexical bound. NEXT LEVER = north-star compact-rule/program-"
    "induction plugin (symbolic regression / Bayesian program induction / XOR-primitive) that induces the compact "
    "formula and fills unseen feature-combinations; module (29487) hosts it, 29489 proved extensibility. "
    "Composes/executes 29490; composes 29485/29487/29489.")

DECISION = (
    "landed_vet_atomize (STANDARD_LANDED_VET): the sign-supplied generalization test THROUGH the centralized "
    "Learner module -> MEASURED_MECHANISM, CERT +1 (proven-bound). A clean two-pole result: a real positive + a "
    "deep proven boundary, neither over-read. INDEPENDENT off-disk recompute (skunkworks pure-python arms off "
    "tools/build_negation_factuality_gold.build_implicative_gold raw UD-EWT mine, NOT the author plugin code) + "
    "cell re-run. DATA: n=114, 9 verbs; joint cells (pos,False)=25 (pos,True)=6[bother-ONLY] (neg,False)=60 "
    "(neg,True)=23; gold==Karttunen truth-table 0 mismatches (gold-blind, derived from IMPLICATIVE_LEXICON + the "
    "published rule, no ground-by-X-grade-by-X). "
    "(1) VERB-TRANSFER WIN REAL y: on the COVERED subset (n=108) my independent additive/linear arm reproduces "
    "0.6574 EXACTLY, my full-joint-lookup (=simvote) arm reproduces 1.000, module=1.000 -> margin_over_linear "
    "+0.343 (the exact Minsky-Papert XNOR additive ceiling: one shared neg-weight provably cannot fit two of the "
    "four cells). The +0.343 is enabled specifically because the SUPPLIED sign feature has cross-verb overlap "
    "(sign=pos shared by manage/bother/dare, sign=neg by 6 verbs) -- so a held-out verb's (sign,neg)->entailment "
    "IS reconstructable from OTHER verbs sharing its sign, which one-hot verb identity (29490) made impossible. "
    "Module AUTO-SELECTS ruleind 9/9 folds (module_chosen_name_per_fold={ruleind:9}); XOR positive control chose "
    "ruleind at compression 9.8413, passed=True -- the module chose data-drivenly, not the author. "
    "(2) SIGN-SCRAMBLE LOAD-BEARING y: scramble_delta=0.4122 (>0.25 floor). The control permutes verb<->sign but "
    "leaves gold_class as the TRUE entailment, so under a scrambled sign the (scrambled_sign,neg)->true_label map "
    "is INCONSISTENT and covered accuracy collapses 1.000->0.588. The cell docstring discloses an earlier "
    "VACUOUS version of this control (self-consistent recompute -> delta 0.0) that the author fixed pre-run; "
    "confirmed the fixed control now genuinely bites. "
    "(3) BEYOND-LINEAR NOT BEYOND-SIMILARITY (honest) y: simvote ties module at 1.000 (margin_sim=0.000) because "
    "with only 2 binary features the (sign,neg) joint space is a fully ENUMERABLE 4-cell table -- once every cell "
    "is populated by ANY verb, exact-match kNN == full-table lookup. is_similarity_near_chance_on_heldout=False. "
    "So 'beyond-linear not beyond-similarity' is the honest characterization: linear provably cannot fit the "
    "XNOR; similarity trivially can once the cells are populated. The module's covered win is realized as "
    "associative lookup, NOT as a productive rule. "
    "(4) THE DEEP BOUND -- ASSOCIATIVE NOT SYMBOLIC, GENUINE + NOT brain-shared y: the UNCOVERED subset (n=6, all "
    "bother (pos,True), gold NOT_REALIZED, cov=0 -- the (pos,True) cell has ZERO exemplars anywhere once bother "
    "is held out) scores 0.000 in ALL 3 arms incl. module/ruleind. Root cause verified off the actual learned "
    "hypothesis: in the bother-held-out fold ruleind (keyed on sign) learned {conjunct=[sign=neg,neg=False]->"
    "NOT_REALIZED cov60 prec1.0; conjunct=[] default->REALIZED cov43} -- a CONJUNCTION-LOOKUP that carves the "
    "seen NOT_REALIZED block and defaults everything else to REALIZED; it did NOT induce the compact XNOR FORMULA. "
    "Applied to the unseen (pos,True) it returns the REALIZED default -> WRONG (gold NOT_REALIZED). A skunkworks "
    "independent SYMBOLIC-XNOR arm (apply Karttunen's rule directly from sign+neg) FILLS the unseen cell at 1.000 "
    "-- proving the failure is specifically the absence of symbolic-rule application, not a lack of information. "
    "So the module's learners are ASSOCIATIVE (residual-table / conjunction-lookup / nearest-populated-cell; need "
    ">=1 exemplar of the joint cell) NOT SYMBOLIC (a symbolic XNOR fills an unseen cell with zero exemplars). "
    "BRAIN-CHECK: NOT brain-shared -- a human given Karttunen's rule explicitly + the supplied sign computes "
    "bother's negated entailment for the never-seen combination by symbolic rule application. This is a genuine "
    "SUBSTRATE bound (associative-lookup, not symbolic-rule-application), CATEGORICALLY DISTINCT from 29490's "
    "held-out-VERB bound which WAS brain-shared (implicative polarity is a stored lexical fact humans also can't "
    "derive from surface). Here the sign is supplied, so the only remaining gap is rule-application -- which "
    "humans do and the current learners do not. "
    "(5) IMPLICATION SOUND y: true symbolic extrapolation to unseen feature-combinations needs a learner that "
    "induces the COMPACT RULE/FORMULA (symbolic regression / Bayesian program induction / an XOR-primitive "
    "learner) -- the north-star plugin not yet built. So the indicated fix for the associative bound = add a "
    "symbolic/program-induction plugin to the module; the centralized Learner architecture (29487) is built to "
    "host new hypothesis classes and 29489 proved plugin extensibility (core zero-diff), so this is a "
    "recombination-adds-a-plugin path, not a rebuild. Ties to the banked north-star framing (model-selection over "
    "hypothesis spaces; the missing plugin = compact-rule induction). "
    "GRADE MEASURED_MECHANISM proven-bound CERT+1: the 'supply the fact, compose the rule' thesis is VALIDATED at "
    "the verb-transfer level (supplied sign unblocks cross-verb transfer, +0.343 over linear, module auto-selects, "
    "scramble load-bearing) AND the precise ceiling of the current grow-thrust learners is proven (associative "
    "conjunction-lookup, beyond-linear but enumerable-similarity-solvable, fails the unseen joint cell where a "
    "symbolic rule extrapolates). Composes 29490 (executes its diagnosed next step; NOT superseded -- amends with "
    "the sign-supplied result), 29485 (ruleind grow-thrust needs beyond-linear structure -- supplied here, and "
    "the covered win pays off but only associatively), 29487 (module data-driven auto-select re-confirmed on this "
    "task), 29489 (gam_plugin extensibility -- the architecture that can host the north-star compact-rule plugin). "
    "Cell committed 378f01c2b, sha256_16 " + cell_sha + ", by explicit path. LOCAL-ONLY, no push; needs "
    "orchestrator store sync.")

KEY_METRICS = {
    "n_items": 114, "n_verbs": 9, "n_sents_scanned": 16622, "n_raw_hits": 114,
    "joint_cells": "(pos,False)=25[manage,bother,dare] (pos,True)=6[bother-ONLY] (neg,False)=60 (neg,True)=23",
    "gold_vs_karttunen_mismatches": 0,
    "module_autoselect": "ruleind 9/9 folds (module_chosen_name_per_fold={ruleind:9}); data-driven, no task-name branch",
    "xor_positive_control": "ruleind compression 9.8413 (> gam 5.9839 > estimation 0.9756), passed=True",
    "covered_n108": "module=1.000 linear=0.6574 simvote=1.000; margin_lin=+0.343 margin_sim=+0.000",
    "covered_independent_reproduce": "skunkworks additive=0.6574 EXACT, full-joint-lookup(sim)=1.000, symbolic-XNOR=1.000",
    "margin_lin_is_xnor_ceiling": "+0.343 == Minsky-Papert additive ceiling (one shared neg-weight cannot fit 2 of 4 cells)",
    "scramble": "delta=0.4122 (>0.25 floor): covered 1.000 -> scrambled 0.588; supplied sign LOAD-BEARING (control bug fixed pre-run, now bites)",
    "beyond_linear_not_beyond_similarity": "simvote ties module 1.000 -- 2-binary-feature (sign,neg) joint space fully ENUMERABLE (4 cells), kNN==full-table lookup; is_similarity_near_chance=False",
    "uncovered_n6": "bother (pos,True), gold NOT_REALIZED, cov=0; ALL 3 arms 0.000 (module=simvote=linear=0.000)",
    "uncovered_root_cause": "ruleind(bother-fold) learned {[sign=neg,neg=False]->NOT_REALIZED cov60 prec1.0; []default->REALIZED cov43} = CONJUNCTION-LOOKUP not XNOR; unseen (pos,True) -> REALIZED default = WRONG",
    "uncovered_symbolic_fills": "skunkworks independent symbolic-XNOR arm = 1.000 on the same unseen cell -> failure is absence of rule-application, not missing information",
    "bound": "BOUND_CONFIRMED_ASSOCIATIVE_NOT_SYMBOLIC: learners need >=1 joint-cell exemplar (associative); a symbolic XNOR fills an unseen cell",
    "brain_check": "NOT brain-shared -- a human given Karttunen's rule + supplied sign applies it to the unseen (pos,True) cell (symbolic rule application); DISTINCT from 29490's brain-SHARED lexical-polarity bound",
    "indicated_fix": "north-star compact-rule/program-induction plugin (symbolic regression / Bayesian program induction / XOR-primitive) induces the XNOR formula + fills unseen combinations; module 29487 hosts it, 29489 proved extensibility",
    "fallback_specificity_caveat": "the exact 0.000 on the unseen cell is arm-fallback-specific (ruleind default=REALIZED, simvote kNN nearest-populated=REALIZED both point WRONG); an independent global-majority-fallback lookup coincidentally scores 1.000 here because NOT_REALIZED is the global majority AND the true label -- so '0.000' is not a hard invariant; the ROBUST claim is that NO current arm APPLIES the XNOR rule (all generalize associatively), which a symbolic learner does",
}

FRAMING_CORRECTION = (
    "Director framed a two-pole HARD_PASS (verb-transfer win + associative-not-symbolic bound, both easy to "
    "over-read); CONFIRM both, guard each direction (symmetric anti-negativity). UPWARD (don't under-read the "
    "positive): supplying the Karttunen SIGN genuinely UNBLOCKS held-out-verb transfer that one-hot identity "
    "(29490) made structurally impossible -- +0.343 over linear on covered held-out verbs is REAL, the module "
    "auto-selects ruleind data-drivenly (9/9, no task-name branch, XOR ctrl passed), and sign-scramble delta=0.412 "
    "confirms the supplied sign is load-bearing. 'Supply the fact, compose the rule' is validated at the "
    "verb-transfer level. DOWNWARD (don't over-read as symbolic rule recovery): the +0.343 win is realized as "
    "similarity/associative LOOKUP, NOT productive symbolic rule composition -- simvote ties module at 1.000 "
    "because the 4-cell (sign,neg) space is fully enumerable, and the module's own covered win is a ruleind "
    "CONJUNCTION-LOOKUP {(neg,False)->NOT_REALIZED; default->REALIZED}, the SAME associative mechanism that then "
    "FAILS the unseen (pos,True) cell (0.000, defaults REALIZED) where an independent symbolic XNOR fills it "
    "(1.000). So the current grow-thrust learners are ASSOCIATIVE (need >=1 joint-cell exemplar), not SYMBOLIC; "
    "this bound is NOT brain-shared (a human applies Karttunen's rule to the unseen cell) -> a genuine substrate "
    "ceiling, distinct from 29490's brain-shared lexical bound. Honest net tier = MEASURED_MECHANISM: a real "
    "verb-transfer positive + a proven associative-not-symbolic boundary, with the north-star compact-rule/"
    "program-induction plugin as the indicated (and architecturally-supported, per 29489) next lever for true "
    "symbolic generalization. PRECISION on the bound: the exact 0.000 uncovered score is arm-fallback-specific "
    "(a global-majority fallback would coincidentally hit this cell); the ROBUST, load-bearing claim is that NO "
    "current arm APPLIES the rule -- all generalize associatively -- which a symbolic learner does.")

CROSS_ARC = ("NONE substantive at cosine>0.30 (substrate_query 'implicative sign negation supplied feature held-out "
    "verb transfer associative symbolic rule' -> top hits char-trigram surface only: 'implicative' 0.3701 / "
    "'applicative' 0.3506 wordnet + gene-ontology terms, NO prior-arc EXPERIMENT cell above the concept-overlap "
    "threshold). This is the intended lineage successor to 29490 (executes its diagnosed sign-supplied next step), "
    "NOT a rediscovery; composes declared parents 29490/29485/29487/29489.")

atom = {
    "atom_id": AID,
    "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "cert_status": "proven-bound",
    "cert_class": "proven-bound",
    "anchor_name": "learner_implicative_sign_supplied_generalization_v1",
    "cell": cell_path,
    "cell_commit": CELL_COMMIT,
    "cell_content_sha256_16": cell_sha,
    "metrics_path": "data/exp_learner_implicative_sign_supplied_generalization_v1/metrics.json",
    "module_paths": ["hdlab/learner/core.py", "hdlab/learner/registry.py",
                     "hdlab/learner/plugins/ruleind_plugin.py", "hdlab/learner/plugins/gam_plugin.py",
                     "tools/build_negation_factuality_gold.py"],
    "verdict": "HARD_PASS_BEYOND_LINEAR_NOT_BEYOND_SIMILARITY_verb_transfer_win_plus_associative_not_symbolic_bound_MEASURED_MECHANISM",
    "grade": "MEASURED_MECHANISM",
    "auditor": "hdi_skunkworks",
    "verified_off_data": True,
    "cert_delta": 1,
    "net_cert_delta": 1,
    "composes_seq": [29490, 29485, 29487, 29489],
    "seq": NEW_SEQ,
    "store_head_at_write": STORE_HEAD,
    "headline": HEADLINE,
    "decision": DECISION,
    "note": NOTE,
    "key_metrics": KEY_METRICS,
    "cross_arc_overlap": CROSS_ARC,
    "framing_correction": FRAMING_CORRECTION,
    "ts_iso": ts_iso,
    "ts": "2026-07-23",
    "needs_orchestrator_store_sync": True,
    "local_write_only_no_origin_push_no_remote_persist": True,
    "op": "add",
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
assert v[-1]["atom_id"] == AID and v[-1]["tier"] == "MEASURED_MECHANISM" and v[-1]["cert_status"] == "proven-bound"
assert v[-1]["seq"] == NEW_SEQ
print(f"ATOMS OK: {N_ATOMS} -> {len(v)} atoms; new atom verified; no CRLF doubling.")

# ---- ledger entry ----
ledger = {
    "seq": NEW_SEQ, "op": "landed_vet_atomize", "corpus": "math", "tier": "MEASURED_MECHANISM",
    "cert_status": "proven-bound", "cert_class": "proven-bound",
    "atom_id": AID, "anchor_name": "learner_implicative_sign_supplied_generalization_v1",
    "cell": cell_path, "cell_commit": CELL_COMMIT, "cell_content_sha256_16": cell_sha,
    "auditor": "hdi_skunkworks", "verified_off_data": True,
    "cert_delta": 1, "net_cert_delta": 1, "composes_seq": [29490, 29485, 29487, 29489],
    "decision": DECISION, "note": NOTE,
    "framing_correction": FRAMING_CORRECTION, "cross_arc_overlap": CROSS_ARC,
    "ts_iso": ts_iso, "ts": "2026-07-23",
    "needs_orchestrator_store_sync": True, "local_write_only_no_origin_push_no_remote_persist": True,
    "store_head_at_write": STORE_HEAD,
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
assert vl[-1]["atom_id"] == AID and vl[-1]["ts"] == "2026-07-23" and vl[-1]["seq"] == NEW_SEQ
assert vl[-2]["seq"] == last_seq, "seq continuity broken"
print(f"LEDGER OK: {len(ledger_lines)} -> {len(vl)} entries; seq {last_seq} -> {NEW_SEQ}; no CRLF.")
print("SEQ:", NEW_SEQ, "| CELL_COMMIT:", CELL_COMMIT, "| cell_sha:", cell_sha)
print("ATOM_ID_TAIL:", AID[-80:])
print("DONE. LOCAL-ONLY; no origin push; no remote persist. needs_orchestrator_store_sync=True")
