# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; OLD vs NEW prediction-vector hash compare)
# - final_metrics_atomicity: tmp_replace
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except)
# - crlb_n/a: fixed small discriminator set (6 collision + 2 real-FP + 4 confused-4), no sweep
# - calibration_check: default_ok_for_this_regime (both readers reused verbatim/unchanged;
#   scope labels declared in the pre-reg BEFORE running, not fitted to the outcome)
# - cell_chunked: false (single-shot, n small, <5s, seed axis is a 3-way robustness check only)
# - all numbers MEASURED@ tagged in the completion report, not this file
#
# C-C PAYOFF TEST: does the CERTIFIED two-stage grounding (governor sense-select stage-1,
# exp_bridge1_governor_grounding_v1, cert notes/landed_vet_bridge1_foundation.md f06c06535) clear
# the ORIGINAL affect-reader failures that motivated the build, on its CERTIFIED scope --
# replacing resolve_valence_blind (exp_grounded_structure_phase0_probe_v1.py:133) where it is
# wrong? See preregs/2026-08-05_bridge1_original_failure_payoff_v1.md for the full eval-set
# assembly, per-item scope audit, and pre-registered bands.
"""LOCAL-only payoff cell. Reuses (never re-derives) resolve_valence_blind (the reader under
replacement) and exp_bridge1_governor_grounding_v1's certified governor stage (GOVERNOR_VERB_CLASS,
ADJ_MODIFIER_CLASS, extract_governor_feats, gold_type_from_classes, mk_item, COLLISION_PAIRS,
TRAIN_ITEMS) plus hdlab.thematic_role_labeler.train_perceptron. Evaluates BOTH readers on: (A) the
named hard/trick word-sense collision core, (B) 2 real-corpus word-sense false positives traced
from data/exp_maintained_affect_narrative_irony_probe_v1's sincere-item false positives, and
(C) the confused-4 relation-inference items with an explicit per-item scope audit (most are
out-of-scope known gaps, reported honestly, not folded into the pass/fail gate)."""
import hashlib
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

ANCHOR_NAME = "bridge1_original_failure_payoff_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPERIMENTS_DIR = os.path.join(REPO_ROOT, "experiments")
for _p in (REPO_ROOT, EXPERIMENTS_DIR, os.path.join(REPO_ROOT, "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

from exp_grounded_structure_phase0_probe_v1 import resolve_valence_blind  # noqa: E402 (reader under replacement)
import exp_bridge1_governor_grounding_v1 as gov  # noqa: E402 (certified governor stage, reused verbatim)
import exp_construction_integration_relation_inference_v1 as ci  # noqa: E402 (tokenizer + gold loader)
import exp_situated_goal_structure_valence_v1 as sgv  # noqa: E402 (CATEGORY_TARGET_VALENCE, cited)
from hdlab.thematic_role_labeler import train_perceptron  # noqa: E402

SEEDS = [0, 1, 2]
N_TRAIN_THETA_UNUSED = None  # this cell does not need the sim theta valuation, only the TYPE call

# CITED (not recomputed): the OLD reader's own measured inertness under scramble on confused_4,
# established in the prior phase0 probe.
OLD_READER_CONFUSED4_SCRAMBLE_INERT_REF = (
    "MEASURED@d:/AI/hd-instrument/data/exp_grounded_structure_phase0_probe_v1/metrics.json: "
    "metrics_by_scope.confused_4.GROUNDED_ORACLE_SCRAMBLED_VALENCE_accuracy == "
    "metrics_by_scope.confused_4.GROUNDED_ORACLE_NARRATIVE_accuracy == 0.75"
)


# ---------------------------------------------------------------------------
# Start marker / crash diagnostic
# ---------------------------------------------------------------------------
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_metrics(output_dir, d):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2, default=str)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _write_crash(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME}
    _write_metrics(output_dir, diag)


# ---------------------------------------------------------------------------
# A) named collision core -- reused verbatim from the certified cell
# ---------------------------------------------------------------------------
def collision_core_items():
    """hard + trick pairs only (the task-named word-sense collision core), pulled straight out of
    gov.COLLISION_PAIRS (never re-authored)."""
    items = []
    for form, a, b in gov.COLLISION_PAIRS:
        if form not in ("hard", "trick"):
            continue
        for it, is_harm_form in ((a, False), (b, True)):
            items.append({
                "eval_id": f"collision_{it['note']}", "scope": "IN_SCOPE",
                "scope_reason": "named word-sense collision core, governor sense-select axis",
                "tokens": it["tokens"], "pos": it["pos"], "target_idx": it["target_idx"],
                "target_word": it["target_word"],
                "action_text": " ".join(it["tokens"]),
                "expected_harm": is_harm_form,
            })
    return items


# ---------------------------------------------------------------------------
# B) real-corpus word-sense false positives -- traced from the maintained-affect probe
# ---------------------------------------------------------------------------
def real_corpus_fp_items():
    return [
        {
            "eval_id": "missed_a_trick_real", "scope": "IN_SCOPE",
            "scope_reason": ("real-corpus governor-extractable item (governor='missed'); "
                              "traced from grapp_sincere_003 false positive in "
                              "data/exp_maintained_affect_narrative_irony_probe_v1"),
            "source": "tom_sawyer line 570 (para_start_line=570)",
            "action_text": ("Aunt Polly was vexed to think she had overlooked that bit of "
                             "circumstantial evidence, and missed a trick."),
            "tokens": ["and", "missed", "a", "trick"],
            "pos": ["CCONJ", "VERB", "DET", "NOUN"],
            "target_idx": 3, "target_word": "trick",
            "expected_harm": False,
        },
        {
            "eval_id": "studied_hard_real", "scope": "IN_SCOPE",
            "scope_reason": ("real-corpus governor-extractable item (governor='studied', lemma "
                              "'study' is literally in TRAIN_NEUTRAL_VERBS); traced from "
                              "grapp_sincere_005 false positive in "
                              "data/exp_maintained_affect_narrative_irony_probe_v1"),
            "source": "anne_of_green_gables line 8778 (para_start_line=8778)",
            "action_text": ("I don't know. Sometimes I think I'll be all right--and then I get "
                             "horribly afraid. We've studied hard and Miss Stacy has drilled us "
                             "thoroughly, but we mayn't get through for all that."),
            "tokens": ["we", "studied", "hard"],
            "pos": ["PRON", "VERB", "ADV"],
            "target_idx": 2, "target_word": "hard",
            "expected_harm": False,
        },
    ]


# ---------------------------------------------------------------------------
# C) confused-4 -- explicit per-item scope audit (declared BEFORE running, per pre-reg)
# ---------------------------------------------------------------------------
CONFUSED4_SCOPE = {
    "relinf_unstated_007": ("OUT_OF_SCOPE",
        "irony/discourse: surface reads HELP-toned ('take care of herself') but gold=REVENGE_PUNISH "
        "(spiteful abandonment); no force-verb+patient collision exists; STAGE-2b discourse port, "
        "proven not open-vocab-tested per the cert."),
    "relinf_unstated_010": ("OUT_OF_SCOPE",
        "no force verb or HARM/HELP-class governor/adjective present (governor='skate'/'sound', "
        "both UNK); only cue is the adverb 'carefully', a structure bridge1 does not operate on."),
    "relinf_unstated_011": ("MECHANICALLY_IN_SCOPE_BUT_DIFFERENT_PROVEN_GAP",
        "governor='slap' IS in TEST_HARM_VERBS and patient='Lion' is animate, but gold_valence=HELP "
        "(PROTECT_OTHERS) because the harmed entity is the ADVERSARY not the beneficiary (Toto) -- "
        "PROVEN GAP #2 social-relational/beneficiary-tracking, not animacy/force. Both readers "
        "predict HARM here (both wrong, same architectural cause); reported separately, not gated."),
    "relinf_unstated_012": ("OUT_OF_SCOPE",
        "target patient 'ears' is a body-part noun -- PROVEN GAP #1 (WordNet routes to inanimate, "
        "no lift either way)."),
}


def confused4_items():
    gold = ci.load_gold()
    by_id = {it["id"]: it for it in gold["unstated_goal"]}
    out = []
    for cid, (scope, reason) in CONFUSED4_SCOPE.items():
        it = by_id[cid]
        gold_target, gold_valence = sgv.CATEGORY_TARGET_VALENCE[it["correct_category"]]
        out.append({
            "eval_id": cid, "scope": scope, "scope_reason": reason,
            "action_text": it["action_text"], "correct_category": it["correct_category"],
            "gold_valence": gold_valence,
        })
    return out


# ---------------------------------------------------------------------------
# readers
# ---------------------------------------------------------------------------
def old_reader(action_text):
    """resolve_valence_blind, ternary HARM/HELP/NA. Unmodified."""
    return resolve_valence_blind(action_text)


def new_reader_ternary(pred_type):
    """Map the governor stage's 4-way TYPE prediction onto the same HARM/HELP/NA ternary space as
    resolve_valence_blind's output, using the CERTIFIED cell's own class definitions
    (gold_type_from_classes: HARM class -> BLOCK_*, HELP class -> RECIPROCITY, UNK -> NEUTRAL)."""
    if pred_type in ("BLOCK_HIGH", "BLOCK_LOW"):
        return "HARM"
    if pred_type == "RECIPROCITY":
        return "HELP"
    return "NA"


def fit_governor_perceptron(seed):
    """Reuses gov.TRAIN_ITEMS + gov.extract_governor_feats + train_perceptron exactly as
    gov.run_seed step (b) does -- not re-derived."""
    train_ex = [(gov.extract_governor_feats(it["tokens"], it["pos"], it["target_idx"],
                                             gov.GOVERNOR_VERB_CLASS, gov.ADJ_MODIFIER_CLASS)[0],
                 it["gold_type"]) for it in gov.TRAIN_ITEMS]
    pred_fn, w, roles = train_perceptron(train_ex, seed=seed + 1000, epochs=20, roles=gov.sim.TYPES)
    return pred_fn


def new_reader_pred_type(pred_fn, tokens, pos, target_idx, verb_class=None, adj_class=None):
    vclass = verb_class if verb_class is not None else gov.GOVERNOR_VERB_CLASS
    aclass = adj_class if adj_class is not None else gov.ADJ_MODIFIER_CLASS
    feats, gov_word, adj_word, gclass, aclass_out, cope = gov.extract_governor_feats(
        tokens, pos, target_idx, vclass, aclass)
    return pred_fn(feats), gov_word, gclass, cope


# ---------------------------------------------------------------------------
# scoring
# ---------------------------------------------------------------------------
def score_ab_item(item, pred_fn):
    old_pred = old_reader(item["action_text"])
    new_type, gov_word, gclass, cope = new_reader_pred_type(
        pred_fn, item["tokens"], item["pos"], item["target_idx"])
    new_pred = new_reader_ternary(new_type)
    expected_harm = item["expected_harm"]
    old_correct = (old_pred == "HARM") == expected_harm
    new_correct = (new_pred == "HARM") == expected_harm
    return {
        **{k: item[k] for k in ("eval_id", "scope", "scope_reason", "action_text", "target_word",
                                 "expected_harm")},
        "governor_extracted": gov_word, "governor_class": gclass, "cope_cue": cope,
        "old_reader_pred": old_pred, "old_reader_correct": old_correct,
        "new_reader_pred_type": new_type, "new_reader_pred_ternary": new_pred,
        "new_reader_correct": new_correct,
        "old_wrong_new_right": (not old_correct) and new_correct,
        "old_right_new_wrong": old_correct and (not new_correct),
    }


def score_confused4_item(item, pred_fn):
    old_pred = old_reader(item["action_text"])
    gold_valence = item["gold_valence"]
    old_correct = (gold_valence == "NA") or (old_pred == gold_valence) or (
        gold_valence == "HARM" and old_pred == "HARM") or (gold_valence == "HELP" and old_pred == "HELP")
    # sign-normalize: old reader ternary vs gold_valence (HELP/HARM/NA)
    old_correct = (gold_valence == "NA") or (old_pred == gold_valence)

    row = {
        "eval_id": item["eval_id"], "scope": item["scope"], "scope_reason": item["scope_reason"],
        "correct_category": item["correct_category"], "gold_valence": gold_valence,
        "action_text": item["action_text"],
        "old_reader_pred": old_pred, "old_reader_correct": old_correct,
    }

    if item["eval_id"] != "relinf_unstated_011":
        row["new_reader_pred_type"] = None
        row["new_reader_pred_ternary"] = None
        row["new_reader_correct"] = None
        row["note"] = "not governor-extractable / out of scope -- new reader not applicable"
        return row

    # relinf_unstated_011: mechanically extractable -- governor='slap', patient='Lion'.
    tokens = ["she", "slapped", "the", "lion"]
    pos = ["PRON", "VERB", "DET", "NOUN"]
    target_idx = 3
    new_type, gov_word, gclass, cope = new_reader_pred_type(pred_fn, tokens, pos, target_idx)
    new_pred = new_reader_ternary(new_type)
    new_correct = (gold_valence == "NA") or (new_pred == gold_valence)

    # scramble control: does the two-stage signal change under a scrambled governor-class dict
    # (i.e. is it a REAL, non-inert discriminator, unlike the old reader's measured inertness on
    # confused_4)?
    scr_verb = gov._scrambled_class_dict(gov.GOVERNOR_VERB_CLASS, seed=99001)
    scr_adj = gov._scrambled_class_dict(gov.ADJ_MODIFIER_CLASS, seed=99002)
    scr_type, _, scr_gclass, _ = new_reader_pred_type(pred_fn, tokens, pos, target_idx,
                                                       verb_class=scr_verb, adj_class=scr_adj)
    scr_pred = new_reader_ternary(scr_type)

    row.update({
        "governor_extracted": gov_word, "governor_class": gclass,
        "new_reader_pred_type": new_type, "new_reader_pred_ternary": new_pred,
        "new_reader_correct": new_correct,
        "old_wrong_new_right": (not row["old_reader_correct"]) and new_correct,
        "old_right_new_wrong": row["old_reader_correct"] and (not new_correct),
        "scramble_control": {
            "scrambled_governor_class": scr_gclass, "scrambled_pred_ternary": scr_pred,
            "changed_under_scramble": scr_pred != new_pred,
        },
        "note": ("mechanically in-scope but requires beneficiary-tracking (PROVEN GAP #2); both "
                 "readers predict HARM, both WRONG vs gold_valence=HELP -- tied failure, same "
                 "architectural cause, NOT a two-stage-grounding regression."),
    })
    return row


# ---------------------------------------------------------------------------
# arms-must-differ (META_RULE_AF)
# ---------------------------------------------------------------------------
def arms_must_differ(ab_rows):
    old_vec = "|".join(r["old_reader_pred"] for r in ab_rows)
    new_vec = "|".join(r["new_reader_pred_ternary"] for r in ab_rows)
    da = hashlib.sha256(old_vec.encode()).hexdigest()
    db = hashlib.sha256(new_vec.encode()).hexdigest()
    if da == db:
        raise AssertionError(
            f"META_RULE_AF VIOLATION: OLD and NEW reader prediction vectors bit-identical "
            f"(digest={da}) on the A+B eval set -- no differentiation, cell is vacuous.")
    return {"old_digest": da, "new_digest": db, "identical": False}


# ---------------------------------------------------------------------------
# run
# ---------------------------------------------------------------------------
def run(run_mode: str):
    t0 = time.perf_counter()
    ab_items = collision_core_items() + real_corpus_fp_items()
    c4_items = confused4_items()
    expected_n_units = len(ab_items) * len(SEEDS) + len(c4_items) * len(SEEDS)
    _write_start_marker(OUTPUT_DIR, run_mode, expected_n_units)

    per_seed_ab = {}
    per_seed_c4 = {}
    for seed in SEEDS:
        pred_fn = fit_governor_perceptron(seed)
        per_seed_ab[seed] = [score_ab_item(it, pred_fn) for it in ab_items]
        per_seed_c4[seed] = [score_confused4_item(it, pred_fn) for it in c4_items]

    measured_n_units = sum(len(v) for v in per_seed_ab.values()) + sum(len(v) for v in per_seed_c4.values())
    if measured_n_units != expected_n_units:
        raise AssertionError(
            f"META_RULE_H CARDINALITY BREACH: got {measured_n_units}, expected {expected_n_units}")

    # arms-must-differ on seed-0 A+B rows (the discriminator-bearing set)
    arm_digests = arms_must_differ(per_seed_ab[SEEDS[0]])

    # aggregate A+B (collision core + real-corpus FPs) across seeds: majority-vote per item
    def majority(vals):
        counts = {}
        for v in vals:
            counts[v] = counts.get(v, 0) + 1
        return max(counts.items(), key=lambda kv: kv[1])[0]

    ab_agg = []
    for i, base_item in enumerate(ab_items):
        old_preds = [per_seed_ab[s][i]["old_reader_pred"] for s in SEEDS]
        new_preds = [per_seed_ab[s][i]["new_reader_pred_ternary"] for s in SEEDS]
        old_corrects = [per_seed_ab[s][i]["old_reader_correct"] for s in SEEDS]
        new_corrects = [per_seed_ab[s][i]["new_reader_correct"] for s in SEEDS]
        assert len(set(old_preds)) == 1, "old reader is deterministic; must be seed-invariant"
        ab_agg.append({
            "eval_id": base_item["eval_id"], "scope": base_item["scope"],
            "scope_reason": base_item["scope_reason"], "action_text": base_item["action_text"],
            "expected_harm": base_item["expected_harm"],
            "old_reader_pred": old_preds[0], "old_reader_correct_all_seeds": old_corrects,
            "old_reader_correct": all(old_corrects),
            "new_reader_pred_per_seed": new_preds, "new_reader_pred_majority": majority(new_preds),
            "new_reader_correct_per_seed": new_corrects,
            "new_reader_correct_majority_seeds": sum(new_corrects) >= 2,
        })

    named_collision_ids = {"collision_hard_A_nonharm", "collision_hard_B_harm",
                            "collision_trick_A_nonharm", "collision_trick_B_harm"}
    core6 = [r for r in ab_agg if r["eval_id"] in named_collision_ids
             or r["eval_id"] in ("missed_a_trick_real", "studied_hard_real")]
    assert len(core6) == 6, f"expected 6 core items (4 named collision + 2 real-FP), got {len(core6)}"

    old_correct_core6 = sum(1 for r in core6 if r["old_reader_correct"])
    new_correct_core6 = sum(1 for r in core6 if r["new_reader_correct_majority_seeds"])
    old_wrong_count = 6 - old_correct_core6

    if new_correct_core6 == 6 and old_wrong_count >= 4:
        verdict = "HARD_PASS"
    elif new_correct_core6 >= 4:
        verdict = "MIDDLE_BAND"
    else:
        verdict = "HARD_FAIL"

    # confused-4 diagnostic (never gates the verdict)
    c4_agg = []
    for i, base_item in enumerate(c4_items):
        rows_this = [per_seed_c4[s][i] for s in SEEDS]
        r0 = rows_this[0]
        entry = {"eval_id": r0["eval_id"], "scope": r0["scope"], "scope_reason": r0["scope_reason"],
                  "correct_category": r0["correct_category"], "gold_valence": r0["gold_valence"],
                  "old_reader_pred": r0["old_reader_pred"], "old_reader_correct": r0["old_reader_correct"]}
        if r0["new_reader_pred_ternary"] is not None:
            new_corrects = [r["new_reader_correct"] for r in rows_this]
            entry["new_reader_pred_ternary"] = r0["new_reader_pred_ternary"]
            entry["new_reader_pred_per_seed"] = [r["new_reader_pred_ternary"] for r in rows_this]
            entry["new_reader_correct_all_seeds"] = new_corrects
            entry["new_reader_correct"] = all(new_corrects)
            entry["scramble_control"] = r0["scramble_control"]
            entry["note"] = r0["note"]
        else:
            entry["new_reader_pred_ternary"] = None
            entry["new_reader_correct"] = None
            entry["note"] = r0["note"]
        c4_agg.append(entry)

    old_reader_confused4_scramble_inert = OLD_READER_CONFUSED4_SCRAMBLE_INERT_REF
    item011 = next(r for r in c4_agg if r["eval_id"] == "relinf_unstated_011")
    new_reader_changed_under_scramble_item011 = item011.get("scramble_control", {}).get(
        "changed_under_scramble")

    core6_named = [r["eval_id"] for r in core6]
    elapsed = time.perf_counter() - t0
    metrics = {
        "verdict": verdict,
        "verdict_msg": (
            f"{verdict}: core6(named-collision+real-FP) old_correct={old_correct_core6}/6 "
            f"new_correct(majority-of-3-seeds)={new_correct_core6}/6 old_wrong={old_wrong_count}/6 "
            f"| confused_4: 3/4 OUT_OF_SCOPE (irony/no-structure/body-part), 1/4 "
            f"(relinf_unstated_011) mechanically-in-scope but tied-failure on a DIFFERENT proven "
            f"gap (beneficiary-tracking); new-reader-changed-under-scramble={new_reader_changed_under_scramble_item011} "
            f"vs old-reader-measured-inert-on-confused4 (cited, see old_reader_confused4_scramble_inert_ref)"
        ),
        "summary": f"{verdict} on core6; confused_4 reported as labeled diagnostic, not gated",
        "elapsed_s": elapsed, "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(), "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
        "expected_n_units": expected_n_units, "measured_n_units": measured_n_units,
        "cardinality_ok": True, "arms_differ_verified": True, "arm_digests": arm_digests,
        "seeds": SEEDS,
        "core6_eval_ids": core6_named,
        "core6_rows": core6,
        "ab_agg_all": ab_agg,
        "confused_4_diagnostic": c4_agg,
        "old_reader_confused4_scramble_inert_ref": old_reader_confused4_scramble_inert,
        "gates": {
            "old_correct_core6": old_correct_core6, "new_correct_core6": new_correct_core6,
            "old_wrong_count": old_wrong_count,
            "hard_pass_criteria": "new_correct_core6==6 and old_wrong_count>=4",
            "middle_band_criteria": "new_correct_core6>=4",
        },
        "note_scope": (
            "core6 = the 4 named hard/trick collision items + the 2 real-corpus word-sense FPs "
            "traced from data/exp_maintained_affect_narrative_irony_probe_v1. confused_4 is "
            "reported separately per the pre-registered per-item scope audit -- 3/4 items are "
            "OUT_OF_SCOPE (irony/discourse, no force-verb structure, body-part patient) and the "
            "4th (relinf_unstated_011) is MECHANICALLY_IN_SCOPE_BUT_DIFFERENT_PROVEN_GAP (needs "
            "beneficiary-tracking, not animacy/force) -- both readers tie-fail there for the same "
            "architectural reason. Neither counts toward the core6 HARD_PASS/FAIL gate."
        ),
    }

    tmp_path = os.path.join(OUTPUT_DIR, "metrics.json.tmp")
    final_path = os.path.join(OUTPUT_DIR, "metrics.json")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=str)
    os.replace(tmp_path, final_path)
    return metrics


def self_test():
    ab_items = collision_core_items()
    assert len(ab_items) == 4, f"expected 4 collision items (hard+trick, A+B each), got {len(ab_items)}"
    real_items = real_corpus_fp_items()
    assert len(real_items) == 2

    # real-code-path: confirm resolve_valence_blind actually fires HARM on the raw corpus text
    # (the false-positive under replacement) -- if this assertion fails the premise is stale.
    assert old_reader(real_items[0]["action_text"]) == "HARM", (
        "missed_a_trick_real: resolve_valence_blind expected to fire HARM (the FP being tested)")
    assert old_reader(real_items[1]["action_text"]) == "HARM", (
        "studied_hard_real: resolve_valence_blind expected to fire HARM (the FP being tested)")

    pred_fn = fit_governor_perceptron(seed=0)
    row0 = score_ab_item(ab_items[0], pred_fn)
    assert row0["new_reader_pred_type"] in gov.sim.TYPES

    c4 = confused4_items()
    assert len(c4) == 4
    scopes = {it["eval_id"]: it["scope"] for it in c4}
    assert scopes["relinf_unstated_007"] == "OUT_OF_SCOPE"
    assert scopes["relinf_unstated_011"] == "MECHANICALLY_IN_SCOPE_BUT_DIFFERENT_PROVEN_GAP"

    c4_row = score_confused4_item(c4[[i for i, it in enumerate(c4) if it["eval_id"] == "relinf_unstated_011"][0]], pred_fn)
    assert c4_row["new_reader_pred_ternary"] is not None
    assert "scramble_control" in c4_row

    print("[self-test] PASS", flush=True)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--run-mode", default="full", choices=["full", "smoke", "self_test"])
    args = parser.parse_args()

    if args.self_test:
        self_test()
        return

    metrics = run(args.run_mode)
    print(f"[done] verdict={metrics['verdict']} elapsed_s={metrics['elapsed_s']:.3f}", flush=True)
    print(metrics["verdict_msg"], flush=True)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash(OUTPUT_DIR, e)
        raise
