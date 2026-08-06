"""Scaffold-free witness for the DID-IT-HAPPEN occurrence-gate + recurrence + window-widening build
(2026-08-06). tracing=False; hdlab organs + the in-repo eval JSONL only (no experiment-cell scaffold,
no corpora needed -- the eval carries each passage's text directly).

Pre-reg: preregs/2026-08-06_did_it_happen_occurrence_gate_v1.md
Design:  notes/research_did_it_happen_occurrence_gate_congruence_wiring_2026-08-06.md

MEASURED VERDICT (this witness reproduces it): Check 1 = HARD-FAIL, Check 4 = HARD-FAIL.
  - The occurrence-gate + recurrence channel + window-widening are all CORRECTLY BUILT (they fire on
    constructed inputs, see check_mechanism_fires) and are strict-ADD (zero regression across all 44
    eval items; goal_typing.self_test byte-identical), BUT they produce ZERO net-new-correct on the
    real-prose eval because every did-it-happen item is blocked by structural gaps DEEPER than the
    pre-reg's GAP-1 window framing:
      GAP-A: all 15 desired verbs are OOV of CLASS_REGISTRY (empty desired classes) -> the
             occurrence-gate has no class-related candidate to flip.
      GAP-B: a CONTROL-pattern OOV desired verb yields desired referent=None -> a recurrence "same"
             dies at referent_extraction_failed (onestop_limal: window reaches "found love" and
             recurrence fires, but referent=None kills it).
      GAP-C: a pre-verbal negator ("did not"/"never") occupies the SUBJECT slot that
             find_actual_state_candidates reads, poisoning the actual referent to "not"/"never" ->
             the occurrence-gate flip is discarded at referent_mismatch (the flip is computed,
             occurrence_gate_fired=True, but never reaches a linking referent).
      GAP-D: window-widening reaches a DISTRACTOR clause ("All the balls failed") or finds no
             class/recurrence candidate anywhere in the window (woz_dorothy: carry/take are OOV).
  - This is the pre-reg's anticipated "clean fail is honest + informative" outcome (P_deflated
    Check1=0.35, Check4=0.25). The mechanism is retained (dormant-but-correct substrate); the newly
    discovered blocker is GAP-B/GAP-C referent extraction, the natural next FORMALIZE target.

Run: .venv/Scripts/python.exe verification/witness_did_it_happen_occurrence_gate_v1.py
"""
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import hdlab.goal_typing as G

EVAL_REL = "experiments/data/goal_bearing_modern_eval_v1.jsonl"

SUBSET15 = [
    "lw_meg_currant_jelly", "lw_laurie_flower_table_amy",
    "agg_gilbert_pond_rescue_friendship_plea_ch28", "agg_anne_pudding_sauce_mouse_ch16",
    "agg_anne_mrs_barry_forgiveness_currant_wine_ch16_17", "woz_dorothy_kansas_wish",
    "woz_scarecrow_brains", "woz_tin_woodman_heart", "woz_lion_courage_denied",
    "alice_beautiful_garden", "race_german_dog", "race_davey_wiffle", "onestop_malala",
    "onestop_hunt_crowdfunding", "onestop_limal_dating",
]
GAP1_ITEMS = ["lw_laurie_flower_table_amy", "agg_anne_mrs_barry_forgiveness_currant_wine_ch16_17",
              "woz_dorothy_kansas_wish", "race_davey_wiffle", "onestop_limal_dating"]
NOISE = [("walked", "He walked to the well and carried the pail home"),
         ("sat", "She sat by the fire in the evening"),
         ("spoke", "She turned and spoke to her brother"),
         ("turned", "He turned and looked toward the door"),
         ("answered", "The boy answered the question at once"),
         ("asked", "He asked for a cup of cold water"),
         ("stood", "The horse stood by the wooden gate"),
         ("carried", "She carried the basket to the market")]


def _load():
    rows = [json.loads(l) for l in open(os.path.join(REPO_ROOT, EVAL_REL), encoding="utf-8")
            if l.strip()]
    return rows, {r["id"]: r for r in rows}


def _gold(r):
    return "MET" if r["gold_outcome_polarity"] == "met" else "UNMET"


def _windowed_fallback(txt):
    """congruence_with_lexicon_fallback contract but routed through the WINDOWED primary (Check 4)."""
    v, det = G.congruence_outcome_valence_windowed(txt)
    if v != "NA":
        return v, det
    sents = G._sentences(txt)
    return (G.lexicon_predict(sents[-1]) if sents else "NONE"), {"reason": "abstain_fallback_to_lexicon"}


def check_step0_baseline():
    """Step 0: bare production organ (congruence_with_lexicon_fallback) -- full-36 + 15-subset."""
    rows, d = _load()
    oov = [r for r in rows if r.get("outcome_in_lexicon") is False]
    assert len(oov) == 36, f"expected 36 OOV, got {len(oov)}"
    full = sum(G.congruence_with_lexicon_fallback(r["text"])[0] == _gold(r) for r in oov)
    sub = sum(G.congruence_with_lexicon_fallback(d[i]["text"])[0] == _gold(d[i]) for i in SUBSET15)
    # all 6 currently-correct 15-subset items are LEXICON-FALLBACK (zero congruence-native), incl the
    # two the design note guessed were structural (woz_lion, alice) -- an honest Step-0 correction.
    native_correct = 0
    for i in SUBSET15:
        pred, det = G.congruence_with_lexicon_fallback(d[i]["text"])
        if pred == _gold(d[i]) and det.get("reason") != "abstain_fallback_to_lexicon":
            native_correct += 1
    assert full == 6, f"Step-0 full-36 must be 6 (empty-overlay floor), got {full}"
    assert sub == 6, f"Step-0 15-subset must be 6, got {sub}"
    assert native_correct == 0, f"Step-0 congruence-native-correct on subset must be 0, got {native_correct}"
    print(f"[CHECK step0] full-36=6/36=0.1667 | 15-subset=6/15=0.40 | congruence-native-correct=0 "
          f"(all 6 are lexicon-fallback luck)")
    return {"full36": full, "sub15": sub, "native_correct": native_correct}


def check_mechanism_fires():
    """The occurrence-gate, recurrence channel, and window-widening FIRE correctly on constructed
    inputs -- distinguishes 'correctly built, eval does not exercise it' from 'silently broken'."""
    # recurrence-only MET (OOV desired verb 'pitch' with an extractable ECM referent 'davey')
    v, det = G.congruence_decision(["The coach wanted Davey to pitch in the final"],
                                   "Davey pitched all afternoon")
    assert v == "MET" and G.RECURRENCE_SENTINEL in det["actual"]["classes"], (v, det)
    # occurrence-gate EXECUTES on a negated recurrence (flip); poisoned referent defeats the verdict
    v2, det2 = G.congruence_decision(["The coach wanted Davey to pitch in the final"],
                                     "Davey did not pitch at all")
    assert det2.get("occurrence_gate_fired") is True and det2["actual"]["referent"] == "not", (v2, det2)
    # window-widening steps back past a trailing reaction sentence to the true clause
    p = ("The coach wanted Davey to pitch in the final. Davey pitched all afternoon. "
         "Everyone cheered loudly.")
    assert G.congruence_outcome_valence_windowed(p)[0] == "MET" and \
        G.congruence_outcome_valence(p)[0] == "NA"
    # referent-poisoning demonstration (GAP-C): the occurrence-gate SHOULD flip save+"did not sink"
    # to MET (boat saved) but poisoned referent forces referent_mismatch(UNMET) -- documented defeat.
    vp, detp = G.congruence_decision(["Owen wanted to save the boat before the storm hit"],
                                     "The boat did not sink")
    assert detp.get("occurrence_gate_fired") is True and vp == "UNMET" and \
        detp["reason"] == "referent_mismatch", (vp, detp)
    print("[CHECK mechanism_fires] recurrence->MET; occurrence-gate flip EXECUTES (gate_fired=True); "
          "window steps back to true clause; GAP-C poisoning defeat reproduced (save+'did not sink' "
          "flips to same but referent='not' -> referent_mismatch)")
    return {"recurrence": v, "gate_fired": det2.get("occurrence_gate_fired")}


def check1_occurrence_gate_and_recurrence():
    """Check 1 (production sents[-1] path): net-new-correct on the 15-subset + eval-wide no-regression
    + NOISE anti-drift + numeric-threshold no-false-MET."""
    _rows, d = _load()
    # baseline re-run (bare organ is what production is; Check 1 changes are strict-ADD inside it, so
    # to measure the *delta* we compare production-now against the Step-0 numbers just proven == 6/6).
    sub_now = sum(G.congruence_with_lexicon_fallback(d[i]["text"])[0] == _gold(d[i]) for i in SUBSET15)
    net_new = sub_now - 6
    # NOISE anti-drift: 0 spurious congruence-native MET/UNMET
    leaks = 0
    for v, sent in NOISE:
        for goalp in ["Kim wanted to open the greenhouse before winter came",
                      f"Kim wanted to {v} to the market before noon"]:
            verd, det = G.congruence_decision([goalp], sent)
            if det.get("reason") in ("same_class_same_referent", "opposed_class_same_referent",
                                     "referent_mismatch") and verd in ("MET", "UNMET"):
                leaks += 1
    # light/copula recurrence blocked
    for lv, past in [("be", "was"), ("do", "did"), ("have", "had"), ("say", "said"), ("get", "got")]:
        assert not any(G.RECURRENCE_SENTINEL in c["classes"]
                       for c in G.find_actual_state_candidates(f"He {past} the thing", lv))
    # numeric-threshold: must NOT be flipped to a false MET
    for i in ["race_chen_situps", "onestop_carle_madeinfrance"]:
        assert G.congruence_with_lexicon_fallback(d[i]["text"])[0] != "MET", i
    assert net_new == 0, f"MEASURED Check-1 net-new-correct on 15-subset = {net_new} (HARD-FAIL: 0)"
    assert leaks == 0, f"NOISE anti-drift leaks = {leaks} (HARD-FAIL if > 0)"
    print(f"[CHECK check1] MEASURED net-new-correct=0/15 -> HARD-FAIL bar hit (pre-reg: net==0 is "
          f"HARD-FAIL); NOISE leaks=0; light-verb recurrence blocked; numeric-threshold no false MET")
    return {"net_new": net_new, "noise_leaks": leaks}


def check4_window_widening():
    """Check 4 (windowed path): GAP-1 items recovered + FULL-44 non-regression."""
    rows, d = _load()
    recovered = []
    for i in GAP1_ITEMS:
        w = _windowed_fallback(d[i]["text"])[0]
        if w == _gold(d[i]):
            recovered.append(i)
    # FULL-44 non-regression: windowed primary must not change any verdict vs the production sents[-1]
    # path (measured: 0 changes -- window-widening reaches earlier clauses but the reached clauses hit
    # GAP-B/C/D so no verdict actually moves either way).
    changed = []
    for r in rows:
        base_pred = G.congruence_with_lexicon_fallback(r["text"])[0]
        win_pred = _windowed_fallback(r["text"])[0]
        if win_pred != base_pred:
            changed.append((r["id"], base_pred, win_pred))
    assert len(recovered) < 2, f"MEASURED GAP-1 recovered = {recovered} (pre-reg HARD-FAIL: < 2)"
    assert not changed, f"window-widening regressed/changed verdicts eval-wide: {changed}"
    print(f"[CHECK check4] MEASURED GAP-1 recovered={len(recovered)}/5 -> HARD-FAIL (pre-reg: <2 is "
          f"HARD-FAIL); FULL-44 verdict changes={len(changed)} (zero regression)")
    return {"recovered": recovered, "eval_wide_changes": changed}


def check_strict_add():
    """goal_typing.self_test passes (all decisive cases byte-identical) AND legacy find_actual_state_
    candidates (no desired_verb_lemma) never produces a RECURRENCE_SENTINEL."""
    G.self_test()
    assert not any(G.RECURRENCE_SENTINEL in c["classes"]
                   for c in G.find_actual_state_candidates("Davey pitched all afternoon"))
    print("[CHECK strict_add] goal_typing.self_test passes; legacy candidate scan has no recurrence")
    return True


def run():
    r0 = check_step0_baseline()
    rm = check_mechanism_fires()
    r1 = check1_occurrence_gate_and_recurrence()
    r4 = check4_window_widening()
    rs = check_strict_add()
    print("[ALL CHECKS PASS] did-it-happen occurrence-gate: mechanism CORRECTLY BUILT + strict-ADD "
          "(zero regression, self_test byte-identical), but MEASURED VERDICT = Check1 HARD-FAIL "
          "(net-new=0) + Check4 HARD-FAIL (GAP-1 recovered=0/5), blocked by referent-extraction "
          "gaps (GAP-A/B/C/D) deeper than the pre-reg's window framing. Honest informative fail.")
    return {"step0": r0, "mechanism": rm, "check1": r1, "check4": r4, "strict_add": rs}


if __name__ == "__main__":
    run()
