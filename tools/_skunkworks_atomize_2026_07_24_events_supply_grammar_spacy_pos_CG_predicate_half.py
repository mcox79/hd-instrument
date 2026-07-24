"""A5-gated LOCAL-ONLY atomize: exp_read_events_supply_grammar_spacy_pos_litbank_v1.
tier=CHAIN_GRADE / chain-grade / CERT +1. Cell verdict HARD_PASS (supply-grammar validated).
CLAIM: SUPPLYING better grammar (spaCy en_core_web_sm POS) as fixed preprocessing cuts the events
NONVERB_PRED bottleneck that 29520 localized to upstream NLTK POS on 19c LitBank prose. ONE variable
= POS source; whole downstream who-did-what reader (parser W + role clf + subcat gate + selectional
argmax) held fixed and glass-box. L2 nonverb 160->70 (rel +0.5625 >> 0.25 floor); L1 pure-POS
confound-free (NO parser) 606->266 (rel +0.5611) AGREES -> genuine POS effect not parser artifact;
abs obviously-wrong-rate 0.130->0.099 (rel +0.236). HONEST SCOPE: fixes the PREDICATE half only;
agent-typing untouched (inanimate-agent 196->195, rel +0.005). spaCy own-errors reported (33 introduced
-ed/-ated participials + dialect contractions; net still -90 at L2 = eliminated ~123). Composes 29520.
Independent .venv re-run reproduces ALL raw counts BIT-FOR-BIT. BINARY-SAFE write, LOCAL ONLY, git-commit.
"""
import json, os, time, tempfile, datetime, hashlib

ATOMS = "data/substrate_index/math/atoms.jsonl"
LEDGER = "data/substrate_index/meta/cert_ledger.jsonl"

# ---- A5 pre-load gate ----
with open(ATOMS, encoding="utf-8") as f:
    atom_lines = [l for l in f.read().splitlines() if l.strip()]
parsed = [json.loads(l) for l in atom_lines]
assert len(parsed) == 29519, f"expected 29519 atoms pre-write, got {len(parsed)}"
existing_ids = {o.get("atom_id") for o in parsed if o.get("atom_id")}
assert not any("\r" in l for l in atom_lines[-5:]), "existing atoms carry CR -- investigate before write"
assert parsed[-1]["seq"] == 29521, f"expected last atom seq 29521, got {parsed[-1]['seq']}"

with open(LEDGER, encoding="utf-8") as f:
    ledger_lines = [l for l in f.read().splitlines() if l.strip()]
last_seq = json.loads(ledger_lines[-1])["seq"]
assert last_seq == 29521, f"expected ledger last seq 29521, got {last_seq}"
NEW_SEQ = 29522
print("PRE-GATE: 29519 atoms load-valid; ledger last seq 29521.")

# ---- off-disk recompute confirmation (re-assert raw counts + derived off metrics.json) ----
M = json.load(open("data/exp_read_events_supply_grammar_spacy_pos_litbank_v1/metrics.json", encoding="utf-8"))
g = M["gate"]; l1 = g["level1_pure_pos"]; l2 = g["level2_full_extractor"]; nk = l2["nltk"]; sp = l2["spacy"]
assert M["verdict"] == "HARD_PASS"
assert l1["nltk_n_nonverb"] == 606 and l1["spacy_n_nonverb"] == 266 and l1["nltk_n_pred"] == 6174 and l1["spacy_n_pred"] == 6034
assert nk["n_nonverb_pred"] == 160 and sp["n_nonverb_pred"] == 70
assert nk["n_events"] == 2601 and sp["n_events"] == 2640
assert nk["n_inanimate_agent"] == 196 and sp["n_inanimate_agent"] == 195
assert nk["n_obviously_wrong"] == 338 and sp["n_obviously_wrong"] == 262
assert g["spacy_own_error_modes"]["n_spacy_introduced_nonverb_preds"] == 33
pc = g["positive_control_vs_29520"]
assert pc["measured_nltk_nonverb"] == 160 and pc["measured_nltk_n_events"] == 2601
assert pc["nonverb_reproduced"] and pc["n_events_reproduced"]
# hand-recompute derived
assert round((606 - 266) / 606, 6) == round(l1["nonverb_rel_reduction"], 6)
assert round((160 - 70) / 160, 6) == round(l2["nonverb_rel_reduction"], 6) == 0.5625
assert round((338 / 2601 - 262 / 2640) / (338 / 2601), 6) == round(l2["obviously_wrong_rate_rel_reduction"], 6)
assert round((196 - 195) / 196, 6) == round(l2["inanimate_agent_rel_reduction"], 6)
# positive-control anchor cross-check against 29520's OWN metrics.json
M29520 = json.load(open("data/exp_read_events_fix_role_reader_litbank_v1/metrics.json", encoding="utf-8"))
rr = M29520["gate2_litbank"]["real_reader"]
assert rr["n_nonverb_pred"] == 160 and rr["n_events"] == 2601, "29520 anchor mismatch"
print("OFF-DISK OK: PC nltk 160/2601 == 29520 real_reader 160/2601; L2 160->70 rel 0.5625; "
      "L1 606->266 rel 0.5611; owr 0.130->0.099 rel 0.236; inan 196->195 rel 0.005; own-errors 33. "
      "Independent .venv re-run (separate) reproduced ALL raw counts bit-for-bit.")

cell_sha16 = hashlib.sha256(open("experiments/exp_read_events_supply_grammar_spacy_pos_litbank_v1.py", "rb").read()).hexdigest()[:16]
metrics_sha16 = hashlib.sha256(open("data/exp_read_events_supply_grammar_spacy_pos_litbank_v1/metrics.json", "rb").read()).hexdigest()[:16]
assert cell_sha16 == "669b3cb70c7fd1da" and metrics_sha16 == "b0c2431a490e7729"

ts = time.time()
ts_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
ts_day = "2026-07-24"

AID = ("math::read_events_supply_grammar_spacy_pos_litbank_v1_CHAIN_GRADE_SUPPLY_GRAMMAR_spaCy_POS_CUTS_the_"
    "EVENTS_NONVERB_PRED_BOTTLENECK_29520_localized_to_UPSTREAM_NLTK_POS_on_19c_LitBank_prose_ONE_variable_POS_"
    "SOURCE_NLTK_PerceptronTagger_vs_spaCy_en_core_web_sm_SAME_D_ORC_tokenize_SAME_trained_parser_W_role_clf_"
    "subcat_gate_selectional_sel_fn_built_once_shared_both_arms_SAME_25_LitBank_books_spaCy_POS_eq_SUPPLIED_"
    "PREPROCESSING_fixed_input_NOT_black_box_LLM_reasoning_stays_glassbox_north_star_supply_grammar_L2_full_"
    "extractor_nonverb_pred_160_to_70_rel_plus0p5625_GG_25pct_HARD_PASS_floor_CLEAN_NEG_at_le0_reachable_"
    "discriminator_can_fail_POSITIVE_CONTROL_NLTK_arm_nonverb_160_n_events_2601_reproduces_29520_real_reader_"
    "EXACT_off_29520_own_metrics_json_L1_PURE_POS_CONFOUND_FREE_no_trained_parser_content_verb_indices_ext_pure_"
    "POS_nonverb_606_to_266_rel_plus0p5611_AGREES_with_L2_so_reduction_is_GENUINE_POS_effect_NOT_parser_artifact_"
    "CRUX_because_parser_W_and_clf_were_fit_on_NLTK_tagged_McGuffey_the_L2_spaCy_arm_runs_mildly_OOD_L1_is_the_"
    "clean_confound_free_evidence_and_L2_corroborates_including_the_shift_abs_obviously_wrong_rate_0p1300_338of"
    "2601_to_0p0992_262of2640_rel_plus0p2363_HONEST_SCOPE_supply_grammar_POS_fixes_the_PREDICATE_half_nonverb_"
    "pred_minus56pct_but_does_NOT_touch_the_AGENT_typing_half_inanimate_agent_196_to_195_rel_plus0p005_UNCHANGED_"
    "so_the_events_bottleneck_DECOMPOSES_into_predicate_POS_fixable_by_supply_plus_agent_typing_separate_residual_"
    "needs_entity_type_knowledge_the_NEXT_LEVER_spaCy_OWN_ERROR_MODES_no_free_lunch_spaCy_INTRODUCED_33_nonverb_"
    "preds_NLTK_did_not_participial_adjectives_ed_ated_read_VBN_VB_uninitiated_castellated_massy_plus_dialect_"
    "contractions_m_s_leastwise_but_net_still_LARGE_WIN_L2_eliminated_about_123_introduced_33_net_minus90_L1_net_"
    "minus340_GLASSBOX_spaCy_retags_red_VBD_to_JJ_london_VB_to_NNP_musgrove_russell_chancellor_to_NNP_apostrophe_"
    "s_VBZ_to_POS_mistagged_token_no_longer_emitted_as_predicate_verified_off_data_venv_rerun_reproduces_all_raw_"
    "counts_bit_for_bit_composes_29520_events_bottleneck_localization_cross_arc_NONE_gt_0p30_CERT_plus1_LOCAL_"
    "ONLY_2026-07-24")

assert AID not in existing_ids, "duplicate atom id"

HEADLINE = ("SUPPLY-GRAMMAR VALIDATED (CHAIN_GRADE, CERT +1): supplying spaCy en_core_web_sm POS as fixed "
    "preprocessing cuts the events NONVERB_PRED noise that 29520 localized to upstream NLTK POS on real 19c "
    "LitBank prose. ONE variable = POS source (NLTK PerceptronTagger vs spaCy); the whole downstream who-did-what "
    "reader (parser W + role clf + subcat gate + selectional argmax) is held fixed and stays glass-box -- spaCy "
    "POS is SUPPLIED preprocessing (a fixed input), not a black-box LLM in the reasoning loop (north-star: humans "
    "read via already-known grammar). L2 full-extractor nonverb_pred 160->70 (rel +0.5625, >> 0.25 HARD_PASS "
    "floor; CLEAN_NEGATIVE at rel<=0 was reachable). POSITIVE CONTROL: the NLTK arm reproduces 29520's real "
    "reader EXACTLY (nonverb 160, n_events 2601 -- confirmed off 29520's own metrics.json). CRUX / confound-free: "
    "L1 pure-POS predicate selection (NO trained parser, content_verb_indices_ext is pure POS) gives nonverb "
    "606->266 (rel +0.5611) and AGREES with L2 -> the reduction is a GENUINE POS effect, not a parser artifact. "
    "This matters because parser W + clf were fit on NLTK-tagged McGuffey, so the L2 spaCy arm runs mildly OOD; "
    "L1 is the clean confound-free evidence and L2 corroborates including the shift. Absolute obviously-wrong "
    "rate 0.1300 (338/2601) -> 0.0992 (262/2640), rel +0.2363. HONEST SCOPE: supply-grammar-POS fixes the "
    "PREDICATE half (nonverb_pred -56%) but does NOT touch the AGENT-typing half (inanimate-agent 196->195, rel "
    "+0.005, essentially unchanged) -- the events bottleneck DECOMPOSES into predicate (POS-fixable-by-supply) + "
    "agent-typing (a separate residual needing entity-type knowledge = the next lever). NO FREE LUNCH: spaCy "
    "INTRODUCED 33 nonverb-preds NLTK did not (participial adjectives -ed/-ated read as VBN/VB: uninitiated / "
    "castellated / massy; dialect contractions m/s/leastwise) -- net is still a large win (L2 eliminated ~123, "
    "introduced 33, net -90; L1 net -340). Composes 29520 (events-bottleneck localization).")

key_metrics = {
    "l2_nonverb_pred_nltk": 160, "l2_nonverb_pred_spacy": 70, "l2_nonverb_rel_reduction": 0.5625,
    "l1_pure_pos_nonverb_nltk": 606, "l1_pure_pos_nonverb_spacy": 266, "l1_pure_pos_nonverb_rel": 0.5611,
    "l1_confound_free_no_parser": True,
    "obviously_wrong_rate_nltk": 0.12995, "obviously_wrong_rate_spacy": 0.09924, "owr_rel_reduction": 0.2363,
    "n_events_nltk": 2601, "n_events_spacy": 2640, "net_event_count_delta": 39,
    "inanimate_agent_nltk": 196, "inanimate_agent_spacy": 195, "inanimate_agent_rel_reduction": 0.0051,
    "positive_control_nltk_nonverb_160_reproduces_29520": True,
    "positive_control_nltk_n_events_2601_reproduces_29520": True,
    "spacy_introduced_own_nonverb_preds": 33, "l2_gross_eliminated_derived": 123, "l2_net_delta": -90,
    "hard_pass_floor_rel": 0.25, "clean_neg_rel": 0.0, "parser_uas_dev": M["parser_uas_dev"],
    "n_books": 25, "verdict": "HARD_PASS",
}

CERT_CLASS = ("read_events_supply_grammar_spacy_pos_litbank_v1_CHAIN_GRADE_supply_spaCy_POS_cuts_events_nonverb_"
    "pred_bottleneck_29520_upstream_pos_l2_160_to_70_rel_plus0p5625_l1_pure_pos_confound_free_606_to_266_rel_"
    "plus0p5611_agrees_genuine_pos_not_parser_artifact_posctrl_nltk_160_2601_reproduces_29520_exact_owr_0p130_to_"
    "0p099_rel_plus0p236_predicate_half_fixed_agent_typing_untouched_196_to_195_decomposition_spacy_own_errors_33_"
    "net_minus90_composes_29520_cert_plus1_hard_pass")

atom = {
    "atom_id": AID,
    "seq": NEW_SEQ,
    "corpus": "math",
    "tier": "CHAIN_GRADE",
    "cert_status": "chain-grade",
    "cert_class": CERT_CLASS,
    "grade": "CG_SUPPLY_GRAMMAR_POS_CUTS_EVENTS_PREDICATE_BOTTLENECK",
    "verdict": "HARD_PASS",
    "anchor_name": "read_events_supply_grammar_spacy_pos_litbank_v1",
    "cell": "experiments/exp_read_events_supply_grammar_spacy_pos_litbank_v1.py",
    "cell_commit": f"sha256_{cell_sha16}_working_tree_UNTRACKED_at_HEAD_7924aa482",
    "cell_content_sha256_16": cell_sha16,
    "metrics_path": "data/exp_read_events_supply_grammar_spacy_pos_litbank_v1/metrics.json",
    "metrics_sha256_16": metrics_sha16,
    "headline": HEADLINE,
    "key_metrics": key_metrics,
    "auditor": "hdi_skunkworks",
    "verified_off_data": True,
    "composes_seq": [29520],
    "corrects_seq": [],
    "cert_delta": 1,
    "net_cert_delta": 1,
    "store_head_at_write": 29521,
    "cross_arc_overlap": ("substrate_query 'supply grammar spaCy POS tagging events predicate nonverb bottleneck' "
        "top cosine 0.2852 = generic concept 'bottleneck' node; 0.2324 'prescriptive_grammar'; 0.2236 'grammar' "
        "-- all WordNet/concept nodes, NONE a prior arc EXPERIMENT atom at cosine>0.30. Novel targeted extension "
        "of 29520 (which localized the bottleneck); this cell SUPPLIES the fix and validates it confound-free."),
    "honest_scope": ("Full run, 25 LitBank books, real 19c prose. ONE variable = POS source; downstream reader "
        "identical + glass-box. Metric = the 29520 proxy obviously-wrong / nonverb_pred COUNT (no LitBank event "
        "gold exists), same proxy as the localization it validates -- this is a NOISE-reduction / extraction-"
        "quality win on the predicate dimension, not a gold-accuracy F1. SCOPE OF THE WIN: predicate half only "
        "(nonverb_pred -56%); the AGENT-typing half is untouched (inanimate-agent 196->195). L2 spaCy arm is "
        "mildly OOD (parser W + clf fit on NLTK-tagged McGuffey); the confound-free evidence is L1 (pure POS, no "
        "parser) which agrees. spaCy has its OWN 33 introduced nonverb-preds (net still -90 at L2)."),
    "framing_correction": ("Director framing UPHELD at the proposed HARD_PASS / honest scope; banked CHAIN_GRADE "
        "(CERT +1) because this is a POSITIVE capability/validation win with a can-fail discriminator that fired "
        "well above floor (rel +0.5625 vs 0.25; CLEAN_NEGATIVE at rel<=0 reachable), independently reproduced "
        "bit-for-bit. TWO SHARPENINGS (neither overturns): (1) the load-bearing number is the L1 confound-free "
        "rel +0.5611 (NO parser) -- the L2 +0.5625 carries a mild train/test tag-shift because parser W + clf "
        "were fit on NLTK-tagged McGuffey; the two agreeing is exactly what makes the POS-attribution robust, so "
        "cite L1 as primary and L2 as corroboration, never L2 alone. (2) This is a SUPPLY-PREPROCESSING win, not "
        "a substrate-reasoning-mechanism win: swapping an off-the-shelf tagger is north-star-legitimate (supply "
        "grammar) but the durable capability claim is 'the predicate half of the events bottleneck is "
        "POS-fixable-by-supplied-grammar', with agent-typing named as the separate un-fixed residual. The metric "
        "is a noise-count proxy (no event gold), so this validates 29520's LOCALIZATION and demonstrates the "
        "lever works -- it does not by itself prove downstream who-did-what accuracy rose."),
    "local_write_only_no_origin_push_no_remote_persist": True,
    "needs_orchestrator_store_sync": True,
    "ts": ts, "ts_iso": ts_iso, "ts_day": ts_day,
}
json.loads(json.dumps(atom))

# ---- A5 atomic append (BINARY-SAFE: newline='' prevents Windows CRLF doubling) ----
new_line = json.dumps(atom, ensure_ascii=False)
assert "\r" not in new_line and "\n" not in new_line, "atom line contains embedded newline/CR"
new_atoms_text = "\n".join(atom_lines + [new_line]) + "\n"
d = os.path.dirname(os.path.abspath(ATOMS))
fd, tmp = tempfile.mkstemp(dir=d, suffix=".tmp"); os.close(fd)
with open(tmp, "w", encoding="utf-8", newline="") as f:
    f.write(new_atoms_text); f.flush(); os.fsync(f.fileno())
os.replace(tmp, ATOMS)

with open(ATOMS, "rb") as f:
    raw = f.read()
assert b"\r\n" not in raw, "CRLF doubling detected in atoms.jsonl after write"
with open(ATOMS, encoding="utf-8") as f:
    v = [json.loads(l) for l in f.read().splitlines() if l.strip()]
assert len(v) == 29520, f"post-write expected 29520, got {len(v)}"
assert v[-1]["atom_id"] == AID and v[-1]["tier"] == "CHAIN_GRADE" and v[-1]["cert_status"] == "chain-grade"
print(f"ATOMS OK: now {len(v)} atoms (was 29519); new atom seq {NEW_SEQ} verified; no CRLF doubling.")

# ---- ledger entry (matching ts; seq continuity 29521 -> 29522) ----
ledger = {
    "seq": NEW_SEQ, "op": "landed_vet_atomize", "corpus": "math", "tier": "CHAIN_GRADE",
    "cert_status": "chain-grade", "cert_class": CERT_CLASS, "verdict": "HARD_PASS",
    "grade": "CG_SUPPLY_GRAMMAR_POS_CUTS_EVENTS_PREDICATE_BOTTLENECK",
    "atom_id": AID, "anchor_name": "read_events_supply_grammar_spacy_pos_litbank_v1",
    "cell": "experiments/exp_read_events_supply_grammar_spacy_pos_litbank_v1.py",
    "cell_commit": f"sha256_{cell_sha16}_working_tree_UNTRACKED_at_HEAD_7924aa482",
    "cell_content_sha256_16": cell_sha16,
    "metrics_path": "data/exp_read_events_supply_grammar_spacy_pos_litbank_v1/metrics.json",
    "metrics_sha256_16": metrics_sha16,
    "key_metrics": key_metrics,
    "headline": HEADLINE,
    "note": ("AUDIT-ONLY independent off-disk recompute. VERIFIED: (1) POSITIVE CONTROL: NLTK arm nonverb=160, "
        "n_events=2601 reproduces 29520's real-reader EXACTLY -- cross-checked against 29520's OWN metrics.json "
        "(gate2_litbank.real_reader n_nonverb_pred 160, n_events 2601). (2) DISCRIMINATOR (all three recomputed "
        "off raw counts): L2 nonverb 160->70 rel +0.5625; L1 pure-POS 606->266 rel +0.5611; abs obviously-wrong "
        "rate 338/2601=0.12995 -> 262/2640=0.09924 rel +0.2363. (3) CRUX confound-free: L1 (predicate_level_counts "
        "-> content_verb_indices_ext) is pure POS with NO M.decode_clause / parser W (source-verified), and its "
        "+0.5611 AGREES with L2 +0.5625 -> genuine POS effect not a parser artifact; the OOD caveat (parser W+clf "
        "fit on NLTK-tagged McGuffey) is correctly handled by L1 being parser-free. (4) spaCy own-errors: 33 "
        "introduced nonverb-preds (participial -ed/-ated as VBN/VB + dialect contractions), reconciles L2 net -90 "
        "= eliminated ~123 minus introduced 33. (5) DECOMPOSITION: predicate half fixed (nonverb -56%), "
        "agent-typing untouched (inanimate 196->195 rel +0.005) -- honestly stated in cell notes. (6) GLASS-BOX "
        "spot-check off stored samples: red VBD->JJ (bleak S22), chancellor NN->NNP (S25), 's VBZ->POS (S54), "
        "musgrove/russell VBP->NNP, london VB->NNP (persuasion S3/S32/S33) -- each still_pred_in_spacy=False. "
        "(7) GLASS-BOX INVARIANT: make_spacy_tagger disables parser/ner/lemmatizer (tags only), same "
        "D.ORC.tokenize tokens -> spaCy POS is SUPPLIED preprocessing, reasoning loop unchanged/glass-box "
        "(north-star supply-grammar). INDEPENDENT .venv full re-run reproduced ALL raw counts (L1 606/266, L2 "
        "160/70/2601/2640/196/195/338/262, own-errors 33) BIT-FOR-BIT -- metrics not hand-edited, deterministic."),
    "framing_correction": atom["framing_correction"],
    "fairness_verdict": ("FAIR: ONE variable (POS source), same tokenization/parser/clf/gate/sel_fn shared both "
        "arms (built once), arms_differ_verified True; discriminator pre-registered can-fail (CLEAN_NEGATIVE at "
        "rel<=0 reachable, HARD_PASS strictly above at rel>=0.25 with a gap); positive control reproduces 29520 "
        "exactly. Conservative: L1 confound-free is the load-bearing number (L2 carries mild OOD tag-shift, and "
        "the two agreeing is the robustness); spaCy own-errors reported (no free lunch)."),
    "cross_arc_overlap": atom["cross_arc_overlap"],
    "composes_seq": [29520], "corrects_seq": [],
    "cert_delta": 1, "net_cert_delta": 1, "store_head_at_write": 29521,
    "auditor": "hdi_skunkworks", "verified_off_data": True,
    "decision": ("BANK as CHAIN_GRADE (chain-grade / CERT +1). SUPPLY-GRAMMAR VALIDATED: supplying spaCy POS as "
        "fixed preprocessing cuts the events NONVERB_PRED bottleneck 29520 localized to upstream NLTK POS. L2 "
        "160->70 (rel +0.5625 >> 0.25 floor); the confound-free L1 pure-POS (no parser) 606->266 (rel +0.5611) "
        "AGREES -> genuine POS effect not parser artifact; abs obviously-wrong rate 0.130->0.099 (rel +0.236). "
        "Positive control reproduces 29520 exactly. HONEST SCOPE: predicate half only (agent-typing 196->195 "
        "untouched = separate residual, the next lever); L2 spaCy arm mildly OOD, handled by parser-free L1; "
        "spaCy's own 33 introduced errors reported (net still -90). Composes 29520; validates its localization "
        "and demonstrates the supply-grammar lever works on the predicate dimension. Local-only; needs "
        "orchestrator store sync."),
    "local_write_only_no_origin_push_no_remote_persist": True,
    "needs_orchestrator_store_sync": True,
    "ts_iso": ts_iso, "ts": ts, "ts_day": ts_day,
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
assert b"\r\n" not in rawl, "CRLF doubling detected in cert_ledger.jsonl after write"
with open(LEDGER, encoding="utf-8") as f:
    vl = [json.loads(l) for l in f.read().splitlines() if l.strip()]
assert len(vl) == len(ledger_lines) + 1
assert vl[-1]["atom_id"] == AID and vl[-1]["ts"] == ts and vl[-1]["seq"] == NEW_SEQ
assert vl[-2]["seq"] == 29521, "seq continuity broken"
print(f"LEDGER OK: {len(ledger_lines)} -> {len(vl)} entries; seq 29521 -> {NEW_SEQ}; ts matches atom; no CRLF.")
print("ATOM_ID tail:", AID[-70:])
print("DONE. LOCAL-ONLY. needs_orchestrator_store_sync=True; no origin push; no remote persist.")
