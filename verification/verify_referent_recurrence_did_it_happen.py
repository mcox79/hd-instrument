"""Scaffold-free witness for the 2026-08-07 A3 REFERENT-EXTRACTION FIX + REFERENT-RECURRENCE
did-it-happen CHANNEL build. tracing=False (hdlab.goal_typing is pure-Python, no tracer to disable);
hdlab organs + the in-repo eval JSONL only -- no experiment-cell scaffold, no corpora needed.

Pre-reg lineage: preregs/2026-08-06_did_it_happen_occurrence_gate_v1.md (the channel this build
extends) + notes/coverage_wall_decomposition_2b_ceiling_and_referent_did_it_happen_2026-08-06.md (the
plan this build executes -- "A3: fix referent extraction... needed first" + "detector: referent-
recurrence... woz_tin_woodman heart, onestop_hunt money").

BUILD SUMMARY.
Part A (referent-extraction repair, hdlab.goal_typing.find_desired_state + helpers):
  - TRANSFER_CLASS ditransitive-theme fix: an ECM "want HIM to GIVE me a heart" now extracts the
    THEME being transferred ("heart") instead of the ECM subject ("him") for a small closed
    transfer-of-possession verb class (give/hand/bring/send/offer/grant/...).
  - ECM-COPULA fix: a copular-predicate antecedent ("my greatest WISH now ... IS to get back to
    Kansas") is no longer misread as a true ECM embedding (which grabbed the copula "is" itself as
    the referent); falls through to the embedded verb's own complement with a PP-aware object scan
    ("get BACK TO Kansas" -> "kansas", not "back").
  - INVALID-ECM-REFERENT guard: a dropped numeric token ("decided IN [2013] to see") can strand a
    bare preposition as the "referent" (onestop_carle_madeinfrance: was "in") -- now falls through to
    the embedded verb's complement (honestly None here, no object NP present).
  - _QUOTE_BOUNDARY: _object_referent_after now also stops at quotative-attribution verbs (reused
    from hdlab.coreference_resolver._SPEECH_VERBS) so a dialogue-final object NP doesn't run on into
    "...," said X (this is what makes "heart"/"brains"/"courage" extract cleanly from the three
    parallel Oz "give me X" scenes instead of grabbing the speaker's name).
  - _PREVERBAL_AUX finite-clause guard + _DEICTIC_NON_NOMINAL guard: two referent-recurrence-specific
    REGRESSIONS found and fixed during this build's own regression sweep (see HONESTY below) --
    a modal/copula inside an object scan marks a separate finite clause (not part of the object NP),
    and a bare deictic adverb ("here"/"there"/"now"/...) is never a real NP head.

Part B (hdlab.goal_typing.congruence_referent_recurrence_windowed, NEW, wired into
congruence_with_lexicon_fallback as a fallback tier BETWEEN the verb-class windowed primary and the
bare lexicon): sibling of the goal-verb-recurrence channel, keyed on the goal's TARGET REFERENT
(noun) instead of its verb. If the goal's (corrected) referent recurs -- literal, shared-feature
(hdlab.lexical_similarity), or a small SUPPLY noun-concept register (MONEY_CLASS) -- in one of the
trailing 2 sentences in a non-negated clause (occurrence-gate re-read via _is_negator, same
primitive the verb-side gate uses) -> MET; negated -> UNMET. Isolated new code path: does NOT modify
find_actual_state_candidates / congruence_decision / _referent_links, so the existing verb-class
Pass-1 + occurrence-gate + verb-recurrence machinery (7058d026b / 842e5840c) is untouched.

MEASURED (this witness reproduces all of it; "BEFORE" = commit 842e5840c HEAD, reproduced via a
frozen id-set below rather than a dynamic git-blob import, matching this module's own
_baseline_nonwindowed convention elsewhere):
  - full-44 eval: 11/44 -> 15/44 (net +4)
  - OOV-36 subset: 8/36 -> 12/36 (net +4)
  - 15-item did-it-happen-primary subset: 7/15 -> 10/15 (net +3)
  - Recovered (all NONE/abstain -> correct, zero luck): woz_tin_woodman_heart, woz_scarecrow_brains
    (15-subset only; already lexicon-correct at full-44 level, now earned not luck),
    woz_lion_courage_granted, woz_dorothy_kansas_wish, onestop_hunt_crowdfunding.
  - ZERO regressions (exhaustively verified against HEAD 842e5840c across all 44 items).
  - cert 220 passed / 3 skipped (verification/run_certification.py, includes
    test_goal_owner_select.py::test_full_fair_instrument_48_of_48 -- backward-compat unaffected).
  - NOISE anti-drift: 0 leaks (8 light-verb sentences, both the existing congruence_decision probe
    and a direct congruence_referent_recurrence_windowed probe).
  - numeric-threshold guard: race_chen_situps / onestop_carle_madeinfrance remain non-MET.
  - goal_typing.self_test() green (byte-identical decisive-case assertions).

PIN REFRESH 2026-08-13 (Director). The three aggregate pins above were LIVE production counts pinned
with `==`, so they went stale the moment later tiers landed. Measured today: full-44 15 -> 18,
OOV-36 12 -> 14, 15-subset 10 -> 10. VERIFIED as gains-with-zero-regressions, NOT a regression and
NOT a re-scoring of this build: all 11 MUST_STAY_CORRECT items are still correct (11/11), and the
referent-recurrence-ATTRIBUTED gain set is still exactly the same 4 items this build earned. The
extra correct items come from tiers that landed after this witness (grounded result-class 2026-08-07;
Levin last-resort backoff 276674abb). The three aggregates are now FLOORS (>=) so the next landed
improvement cannot manufacture a false failure; the two things that are genuinely exact -- the
MUST_STAY_CORRECT sweep and the reason-filtered gain set -- stay `==`. See PIN POLICY below.

HONESTY (regressions found + fixed during THIS build, not hidden): the first working version of the
referent-recurrence channel (TRANSFER_CLASS + _QUOTE_BOUNDARY alone, no _PREVERBAL_AUX/
_DEICTIC_NON_NOMINAL guards) introduced 2 real regressions on items previously correct via lexicon-
fallback luck: agg_anne_pudding_sauce_mouse_ch16 (a vocative "Diana" mis-extracted as the referent by
_object_referent_after running past a pronoun object through a modal/copula comparative clause into a
trailing vocative address) and ts_potter_failed_escape (a bare deictic "here" mis-extracted and then
falsely recurring). Both are FIXED by two small, general (not eval-tuned) guards documented above,
verified by re-running the full 44-item regression sweep to ZERO. Reported here per the discipline
that a HARD-FAIL must be reported, not silently patched away without a trace -- this witness's own
history is that trace.

Run: .venv/Scripts/python.exe verification/verify_referent_recurrence_did_it_happen.py
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
# Frozen "BEFORE" reference (commit 842e5840c HEAD, this build's parent) -- reproduced as an explicit
# id-set (not a dynamic git-blob import) so this witness has no external-process dependency, matching
# _baseline_nonwindowed's own frozen-baseline convention in the sibling did-it-happen witness.
GAINS_EXPECTED = sorted(["woz_tin_woodman_heart", "woz_dorothy_kansas_wish",
                          "woz_lion_courage_granted", "onestop_hunt_crowdfunding"])

# ---------------------------------------------------------------- PIN POLICY (2026-08-13, Director)
# The full-44 / OOV-36 / 15-subset numbers below are LIVE production accuracy counts read straight
# off congruence_with_lexicon_fallback -- they ACCUMULATE as later tiers land, and more is better.
# Pinned with `==` they are guaranteed to go stale on every improvement, and an equality assert
# cannot tell an improvement from a regression. They are now FLOORS (`>=`).
# NOT converted (deliberately): the MUST_STAY_CORRECT sweep below stays an EXACT per-item equality --
# it is a frozen zero-regression invariant, and a floor there would hide exactly what it exists to
# catch. check_gate_items' per-item verdict+reason equality likewise stays exact.
#
# PIN UPDATE 2026-08-13: full-44 15 -> 18, OOV-36 12 -> 14, 15-subset 10 -> 10 (unchanged value,
# still converted to a floor). VERIFIED gains-with-zero-regressions: all 11 MUST_STAY_CORRECT items
# still correct (11/11), and the referent-recurrence gain set is still EXACTLY GAINS_EXPECTED (this
# build's own 4 items, unchanged). The +3 on full-44 / +2 on OOV-36 come from tiers that landed
# AFTER this witness (grounded result-class, 2026-08-07; Levin last-resort backoff, 276674abb), not
# from any re-scoring of this build. Drift, not regression.
EXPECTED_FULL44_FLOOR = 18   # was pinned ==15 (2026-08-07); now >=18 (2026-08-13)
EXPECTED_OOV36_FLOOR = 14    # was pinned ==12 (2026-08-07); now >=14 (2026-08-13)
EXPECTED_SUB15_FLOOR = 10    # unchanged value; converted ==10 -> >=10 (accumulating metric)
MUST_STAY_CORRECT = ["agg_anne_pudding_sauce_mouse_ch16", "agg_gilbert_pond_rescue_friendship_plea_ch28",
                      "alice_beautiful_garden", "lw_aunt_march_opposition", "lw_jo_story_prize",
                      "onestop_limal_dating", "race_german_dog", "race_tim_rescue",
                      "ts_potter_failed_escape", "woz_lion_courage_denied", "woz_scarecrow_brains"]
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


def check_referent_extraction_repairs():
    """Part A: the named referent-extraction fixes reproduce directly (not just via the eval)."""
    d1 = G.find_desired_state('"And I want him to give me a heart," said the Tin Woodman')
    assert d1 is not None and d1["referent"] == "heart" and d1["pattern"] == "ECM", d1
    d2 = G.find_desired_state('"My greatest wish now," Dorothy added, "is to get back to Kansas')
    assert d2 is not None and d2["referent"] == "kansas" and d2["pattern"] == "ECM_COPULA", d2
    d3 = G.find_desired_state(
        "Carle decided in 2013 to see if it was possible to live using only French-made products "
        "for ten months")
    assert d3 is not None and d3["referent"] is None, (
        f"invalid-ECM-referent guard must discard the stranded preposition 'in', got {d3}")
    # regression guards: the two self_test ECM decisive cases must be untouched.
    d4 = G.find_desired_state("Owen wanted his sister to win the race before the whistle blew")
    assert d4["referent"] == "sister" and d4["pattern"] == "ECM", d4
    d5 = G.find_desired_state("Grace wanted the ferry to sink so the insurers would pay out")
    assert d5["referent"] == "ferry" and d5["pattern"] == "ECM", d5
    print("[CHECK referent_extraction_repairs] heart/kansas/None(carle) extract correctly; "
          "sister/ferry ECM regression guards untouched")
    return {"heart": d1["referent"], "kansas": d2["referent"], "carle_referent": d3["referent"]}


def check_regression_guards_fixed():
    """The two regressions found+fixed DURING this build (see witness docstring HONESTY section) stay
    fixed: the vocative-address mis-extraction and the deictic-adverb mis-extraction."""
    d_diana = G.find_desired_state(
        '"I meant to cover it just as much as could be, Diana, but I forgot all about covering '
        "the pudding sauce")
    assert d_diana["referent"] != "diana", (
        f"FINITE-CLAUSE GUARD regression: referent must not be the vocative 'diana', got {d_diana}")
    d_here = G.find_desired_state("What did you want to come here for")
    assert d_here["referent"] is None, (
        f"DEICTIC guard regression: referent must not be the bare adverb 'here', got {d_here}")
    print("[CHECK regression_guards_fixed] vocative 'diana' and deictic 'here' no longer mis-extracted")
    return {"diana_referent": d_diana["referent"], "here_referent": d_here["referent"]}


def check_gate_items():
    """HARD-PASS gate 'at minimum': woz_tin_woodman_heart AND onestop_hunt_crowdfunding both flip to
    correct via the referent_recurrence reason (earned, not lexicon-fallback luck)."""
    _rows, d = _load()
    for i in ("woz_tin_woodman_heart", "onestop_hunt_crowdfunding"):
        v, det = G.congruence_with_lexicon_fallback(d[i]["text"])
        assert v == _gold(d[i]) and det.get("reason") == "referent_recurrence", (i, v, det)
    print("[CHECK gate_items] woz_tin_woodman_heart + onestop_hunt_crowdfunding both MET via "
          "referent_recurrence (gate 'at minimum' satisfied)")
    return True


def check_full_eval_and_zero_regression():
    """full-44 / OOV-36 / 15-subset counts + the exact recovered-id set + zero regression on the
    frozen MUST_STAY_CORRECT set (measured against HEAD 842e5840c, this build's parent)."""
    rows, d = _load()
    oov = [r for r in rows if r.get("outcome_in_lexicon") is False]
    assert len(oov) == 36, f"expected 36 OOV, got {len(oov)}"

    full44 = sum(G.congruence_with_lexicon_fallback(r["text"])[0] == _gold(r) for r in rows)
    oov36 = sum(G.congruence_with_lexicon_fallback(r["text"])[0] == _gold(r) for r in oov)
    sub15 = sum(G.congruence_with_lexicon_fallback(d[i]["text"])[0] == _gold(d[i]) for i in SUBSET15)

    # FLOORS (accumulating live production accuracy; see PIN POLICY). Pre-build reference: 11/8/7.
    assert full44 >= EXPECTED_FULL44_FLOOR, (
        f"full-44 must be >= {EXPECTED_FULL44_FLOOR} (11 pre-build, 15 at this build), got {full44}")
    assert oov36 >= EXPECTED_OOV36_FLOOR, (
        f"OOV-36 must be >= {EXPECTED_OOV36_FLOOR} (8 pre-build, 12 at this build), got {oov36}")
    assert sub15 >= EXPECTED_SUB15_FLOOR, (
        f"15-subset must be >= {EXPECTED_SUB15_FLOOR} (7 pre-build), got {sub15}")

    gains = []
    for r in rows:
        v, det = G.congruence_with_lexicon_fallback(r["text"])
        if v == _gold(r) and r["id"] not in MUST_STAY_CORRECT and det.get("reason") == "referent_recurrence":
            gains.append(r["id"])
    # EXACT, deliberately NOT loosened: this set is filtered to reason=="referent_recurrence", i.e. it
    # is THIS build's own attribution, not a global accuracy count. It does not accumulate when other
    # tiers land, so equality is the right assertion -- an extra member here would mean this tier
    # started firing somewhere new and must be re-VETted, and a missing member is a real loss.
    assert sorted(gains) == GAINS_EXPECTED, (sorted(gains), GAINS_EXPECTED)

    # EXACT, deliberately NOT loosened: frozen zero-regression invariant (11/11).
    for i in MUST_STAY_CORRECT:
        v, _det = G.congruence_with_lexicon_fallback(d[i]["text"])
        assert v == _gold(d[i]), f"REGRESSION: {i} was correct pre-build, now {v} (gold {_gold(d[i])})"

    print(f"[CHECK full_eval_and_zero_regression] full44={full44}/44 (floor "
          f"{EXPECTED_FULL44_FLOOR}; 11 pre-build, 15 at this build), oov36={oov36}/36 (floor "
          f"{EXPECTED_OOV36_FLOOR}; 8 pre-build, 12 at this build), sub15={sub15}/15 (floor "
          f"{EXPECTED_SUB15_FLOOR}; 7 pre-build); referent_recurrence-attributed gains="
          f"{sorted(gains)} (exact); all {len(MUST_STAY_CORRECT)} "
          f"previously-correct items still correct (zero regression)")
    return {"full44": full44, "oov36": oov36, "sub15": sub15, "gains": sorted(gains)}


def check_noise_and_numeric_guard():
    """NOISE anti-drift (0 leaks, both the existing congruence_decision probe AND a direct
    referent-recurrence-tier probe) + numeric-threshold no-false-MET."""
    _rows, d = _load()
    leaks = 0
    for v_, sent in NOISE:
        for goalp in ["Kim wanted to open the greenhouse before winter came",
                      f"Kim wanted to {v_} to the market before noon"]:
            verd, det = G.congruence_decision([goalp], sent)
            if det.get("reason") in ("same_class_same_referent", "opposed_class_same_referent",
                                     "referent_mismatch") and verd in ("MET", "UNMET"):
                leaks += 1
            rv, _rd = G.congruence_referent_recurrence_windowed(f"{goalp}. {sent}.")
            if rv != "NA":
                leaks += 1
    assert leaks == 0, f"NOISE anti-drift leaks = {leaks} (HARD-FAIL if > 0)"
    for i in ("race_chen_situps", "onestop_carle_madeinfrance"):
        v, _det = G.congruence_with_lexicon_fallback(d[i]["text"])
        assert v != "MET", f"numeric-threshold guard: {i} must never be MET, got {v}"
    print("[CHECK noise_and_numeric_guard] NOISE leaks=0 (congruence_decision + referent_recurrence "
          "probes both clean); race_chen_situps/onestop_carle_madeinfrance stay non-MET")
    return {"noise_leaks": leaks}


def check_strict_add_and_self_test():
    """goal_typing.self_test() passes; the referent-recurrence channel is a pure additive fallback
    (never consulted when the verb-class windowed primary already resolves)."""
    G.self_test()
    theme_mismatch, theme_detail = G.congruence_decision(
        ["Owen wanted to open the greenhouse before winter came"], "The gardener reached the market")
    assert theme_mismatch == "NA" and theme_detail["reason"] == "verb_class_unrelated"
    print("[CHECK strict_add_and_self_test] goal_typing.self_test() green; primary-vs-fallback "
          "ordering intact")
    return True


def run():
    r_extract = check_referent_extraction_repairs()
    r_guards = check_regression_guards_fixed()
    r_gate = check_gate_items()
    r_full = check_full_eval_and_zero_regression()
    r_noise = check_noise_and_numeric_guard()
    r_self = check_strict_add_and_self_test()
    print("[ALL CHECKS PASS] A3 referent-extraction repair + referent-recurrence did-it-happen "
          "channel: THIS BUILD's measured claim unchanged (full44 11->15 (+4), oov36 8->12 (+4), "
          "15-subset 7->10 (+3)); LIVE today (floors, later tiers included) full44="
          f"{r_full['full44']} oov36={r_full['oov36']} sub15={r_full['sub15']}; "
          f"referent_recurrence-attributed gains={r_full['gains']} (exact); "
          "gate items (woz_tin_woodman_heart + onestop_hunt_crowdfunding) both "
          "PASS; ZERO regressions on 11 previously-correct items; cert 220/3 (run separately, see "
          "docstring); NOISE 0 leaks; numeric-threshold guards hold; self_test green.")
    return {"extraction": r_extract, "guards": r_guards, "gate": r_gate, "full": r_full,
            "noise": r_noise, "self_test": r_self}


if __name__ == "__main__":
    run()
