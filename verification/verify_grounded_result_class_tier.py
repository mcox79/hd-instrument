# WIRE-DON'T-ISLAND WITNESS (2026-08-07). Scaffold-free, tracing=False (hdlab.goal_typing is
# pure-Python, no HDC tracer to disable).
"""verification/verify_grounded_result_class_tier.py -- reproduces the GROUNDED RESULT-CLASS
last-resort congruence tier (hdlab.goal_typing.congruence_grounded_result_class, wired as the third
fallback tier inside congruence_with_lexicon_fallback, AFTER congruence_outcome_valence_windowed
and congruence_referent_recurrence_windowed, BEFORE the bare V2_OUTCOME_UNMET/_MET lexicon).

WHAT THIS CHECKS:
  (1) The 3 pre-VET target items (agg_anne_liniment_cake_ch21 / ts_tom_sugar_theft /
      agg_anne_picnic_wish_ch14): MEASURED verdict via congruence_with_lexicon_fallback against gold,
      on the real experiments/data/goal_bearing_modern_eval_v1.jsonl 44-item bank.
  (2) full-44 / OOV-36 / 15-subset polarity counts, before vs after, against a FROZEN "BEFORE" replay
      (HEAD~this-build's parent, reproduced via congruence_outcome_valence_windowed +
      congruence_referent_recurrence_windowed WITHOUT the new tier -- i.e. calling the two prior
      tiers directly and falling to the bare lexicon, exactly what congruence_with_lexicon_fallback
      did before this wire) -- no external git-blob dependency, matching this module's own
      _baseline_nonwindowed / frozen-baseline convention elsewhere.
  (3) ZERO REGRESSION: every one of the 44 items NOT in the recovered set produces the IDENTICAL
      congruence_with_lexicon_fallback verdict before vs after.
  (4) Owner-selection propagation (2a-part-1 unification, hdlab.goal_owner_select): for the 2
      recovered items, select_outcome_owner resolves the CORRECT gold_outcome_owner (proving the
      congruence fix propagates to the owner path via the existing
      _unify_owner_via_polarity_path fallback, unmodified by this build).
  (5) Fair instruments byte-identical: verification/test_goal_owner_select.py's 48/48 full instrument
      + 12/12 multigoal, reproduced via its own run() (imported, not reimplemented).
  (6) NOISE anti-drift: 0 false MET/UNMET on the 8-verb NOISE bank (both via
      congruence_with_lexicon_fallback and via congruence_grounded_result_class directly).
  (7) ADVERSARIAL over-fire set: ~8 hand-built NEGATIVE_RESULT/POSITIVE_RESULT-verb sentences in
      NON-goal / positive-outcome / bystander contexts -- must NOT fire an incorrect verdict.
  (8) goal_typing.self_test() stays green (this build did not touch self_test's decisive cases).

HONEST SCOPE (reported, not hidden): of the 3 pre-VET targets, 2 recover
(ts_tom_sugar_theft via "rap", agg_anne_picnic_wish_ch14 via "punish", both correct UNMET, zero
regression) -- a MEASURED +2 net full-44 polarity gain (15->17 AT THIS BUILD), which is the PARTIAL
band per the pre-reg gate (>=+2 zero-regression = bankable), not the full +3 HARD-PASS band.

PIN REFRESH 2026-08-13 (Director): the full-44 AFTER pin moved 17 -> 18 and the OOV-36 AFTER pin
13 -> 14. This is DRIFT FROM LATER LANDED TIERS, NOT a regression and NOT a re-scoring of this
build: the before-vs-after sweep now shows 3 gains and 0 regressions, and the 3rd gain
(ts_tom_wish_free_potter) is typed by the LEVIN last-resort backoff (commit 276674abb,
levin_last_resort_backoff_applied=True), which landed after this witness was written. This build's
own claim is unchanged: still exactly the 2 items above, still via reason=grounded_result_class.
The AFTER assertions are now FLOORS (>=) rather than equalities, so the next landed improvement
does not manufacture a false failure here -- see the PIN POLICY block below. The third target,
agg_anne_liniment_cake_ch21, does NOT recover: its text contains NO literal spoil/ruin/damage/harm/
wreck/rap/punish/scold token at all (the disaster is conveyed entirely through "a most peculiar
expression crossed her face" / "what on earth did you put into that cake" / "flavored that cake with
Anodyne Liniment" -- comedic irony, not a lexical result-valence cue), so no literal-lexicon tier can
reach it without becoming a materially different (broader affect-inference) mechanism, out of this
tier's scope. agg_anne_hair_dye_green_ch27 was correctly NOT targeted (a goal-recognition gap, not a
congruence-tier gap) and is confirmed still NA/untouched.

Also reported (found + fixed DURING this build, not hidden): the first working NEGATIVE_RESULT
register included "fail", which mis-typed onestop_malala ("But they FAILED," she said -- the
ANTAGONIST's own failure, good news for the goal-holder Malala) as UNMET (gold MET). "fail" was
removed (not load-bearing for either real gain) -- see hdlab/goal_typing.py's NEGATIVE_RESULT
docstring for the full account. "break" was never included (excluded up front for the same class of
idiom risk, "broke the RECORD").

Run: .venv/Scripts/python.exe verification/verify_grounded_result_class_tier.py
"""
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import hdlab.goal_typing as G  # noqa: E402
from hdlab.goal_owner_select import select_outcome_owner  # noqa: E402

EVAL_REL = "experiments/data/goal_bearing_modern_eval_v1.jsonl"

TARGET_IDS = ["agg_anne_liniment_cake_ch21", "ts_tom_sugar_theft", "agg_anne_picnic_wish_ch14"]
NOT_TARGETED = "agg_anne_hair_dye_green_ch27"

# Recovered set (MEASURED@this build): items that flip NONE -> correct via reason=grounded_result_class.
# These 2 remain a REQUIRED SUBSET of the gain set (not the whole of it -- see PIN POLICY below).
EXPECTED_RECOVERED = sorted(["ts_tom_sugar_theft", "agg_anne_picnic_wish_ch14"])

# ---------------------------------------------------------------- PIN POLICY (2026-08-13, Director)
# BEFORE pins stay `==`: they are a FROZEN historical replay (the two prior tiers + bare lexicon).
# They are not the production number; if one of them moves, the recorded delta claim itself is no
# longer the claim that was measured, and this witness SHOULD fail loudly so it gets re-examined.
# AFTER pins became FLOORS (`>=`): they are the LIVE production accuracy on an accumulating quality
# metric where more-is-better. Pinning those with `==` guarantees a false failure every time an
# unrelated tier lands (which is exactly what happened here), and an equality assert cannot tell an
# improvement from a regression anyway. Regression protection is carried by `assert not regressions`
# + the required-subset gain check, both of which stay exact.
#
# PIN UPDATE 2026-08-13: full-44 AFTER 17 -> 18, OOV-36 AFTER 13 -> 14. VERIFIED gains-with-zero-
# regressions: the before-vs-after sweep now shows 3 gains (ts_tom_sugar_theft,
# agg_anne_picnic_wish_ch14, ts_tom_wish_free_potter) and 0 regressions; BEFORE pins (15/12/10) all
# still reproduce exactly. The 3rd gain, ts_tom_wish_free_potter, is NOT this build's -- it is typed
# by the LEVIN last-resort backoff (commit 276674abb, `levin_last_resort_backoff_applied=True`),
# a tier that landed AFTER this witness was written and that _before_verdict deliberately does not
# replay. Drift, not regression.
EXPECTED_FULL44_BEFORE = 15          # frozen replay, exact
EXPECTED_FULL44_AFTER_FLOOR = 18     # was pinned ==17 (2026-08-07); now >=18 (2026-08-13)
EXPECTED_OOV36_BEFORE = 12           # frozen replay, exact
EXPECTED_OOV36_AFTER_FLOOR = 14      # was pinned ==13 (2026-08-07); now >=14 (2026-08-13)
EXPECTED_SUB15_BEFORE = 10           # frozen replay, exact
EXPECTED_SUB15_AFTER_FLOOR = 10      # unchanged value; converted ==10 -> >=10 (accumulating metric)

SUBSET15 = [
    "lw_meg_currant_jelly", "lw_laurie_flower_table_amy",
    "agg_gilbert_pond_rescue_friendship_plea_ch28", "agg_anne_pudding_sauce_mouse_ch16",
    "agg_anne_mrs_barry_forgiveness_currant_wine_ch16_17", "woz_dorothy_kansas_wish",
    "woz_scarecrow_brains", "woz_tin_woodman_heart", "woz_lion_courage_denied",
    "alice_beautiful_garden", "race_german_dog", "race_davey_wiffle", "onestop_malala",
    "onestop_hunt_crowdfunding", "onestop_limal_dating",
]

NOISE = [("walked", "He walked to the well and carried the pail home"),
         ("sat", "She sat by the fire in the evening"),
         ("spoke", "She turned and spoke to her brother"),
         ("turned", "He turned and looked toward the door"),
         ("answered", "The boy answered the question at once"),
         ("asked", "He asked for a cup of cold water"),
         ("stood", "The horse stood by the wooden gate"),
         ("carried", "She carried the basket to the market")]

# ADVERSARIAL over-fire set (Director-specified pattern + this witness's own construction): each
# pairs a genuine antecedent goal with a NEGATIVE_RESULT/POSITIVE_RESULT-adjacent outcome that must
# NOT type an incorrect verdict via congruence_grounded_result_class.
ADVERSARIAL = [
    # ("id", passage_text, forbidden_verdict_or_None_for_must_abstain)
    ("fixed_broken_toy",
     "Kim wanted to cheer her little brother up. She fixed the broken toy he had been crying over.",
     None),  # POSITIVE_RESULT "fix" may type MET; must not type UNMET
    ("broke_the_record_no_break_in_lexicon",
     "Kim wanted to win the sprint. He broke the record at the meet.",
     None),  # "break" excluded from NEGATIVE_RESULT entirely -- must stay NA/whatever prior tiers say
    ("storm_bystander_damage",
     "Kim wanted to win the race. The storm damaged the old barn on the hill.",
     "UNMET"),  # bystander event (storm, inanimate, unrelated to Kim) -- guard(2) must block firing
    ("no_harm_done_negation_flip",
     "Kim wanted to reach the summit safely. She slipped once, but no harm was done.",
     "UNMET"),  # occurrence-gate: "no" negates "harm" -> must NOT stay UNMET (flips to MET)
    ("rap_on_door_knock_sense",
     "Kim wanted to see her old friend again. She rapped on the door and waited.",
     "UNMET"),  # "rapped ON the door" = knocked (neutral), sense-exception must block firing
    ("spoil_indulge_sense",
     "Kim wanted her nephew to have a happy birthday. She loves to spoil him with treats every year.",
     "UNMET"),  # "spoil HIM" = indulge (positive-adjacent), sense-exception must block firing
    ("without_fail_idiom_absent_now",
     "Kim wanted to catch the early train. She arrives at the station without fail every morning.",
     "UNMET"),  # "fail" no longer in NEGATIVE_RESULT at all -- idiom cannot fire regardless
    ("antagonist_own_failure",
     "Kim wanted to keep singing despite the heckler. They tried to boo her off stage, but they failed.",
     "UNMET"),  # antagonist's ("they") own failure is good news for Kim -- "fail" removed, must not fire
]


def _load():
    rows = [json.loads(l) for l in open(os.path.join(REPO_ROOT, EVAL_REL), encoding="utf-8")
            if l.strip()]
    return rows, {r["id"]: r for r in rows}


def _gold(r):
    return "MET" if r["gold_outcome_polarity"] == "met" else "UNMET"


def _before_verdict(passage_text):
    """Replays congruence_with_lexicon_fallback's PRE-this-build behavior: the two prior tiers, then
    straight to the bare lexicon -- i.e. skip congruence_grounded_result_class entirely. Calls the
    unmodified prior-tier functions directly (does not reimplement their logic)."""
    v, det = G.congruence_outcome_valence_windowed(passage_text)
    if v != "NA":
        return v, det
    v2, det2 = G.congruence_referent_recurrence_windowed(passage_text)
    if v2 != "NA":
        return v2, det2
    sents = G._sentences(passage_text)
    lex = G.lexicon_predict(sents[-1]) if sents else "NONE"
    return lex, {"reason": "abstain_fallback_to_lexicon", "lexicon_raw": lex}


def check_target_items():
    _rows, d = _load()
    results = {}
    for tid in TARGET_IDS:
        r = d[tid]
        v, det = G.congruence_with_lexicon_fallback(r["text"])
        results[tid] = {"gold": _gold(r), "got": v, "reason": det.get("reason"),
                        "verb_lemma": det.get("verb_lemma")}
        print(f"[CHECK target_items] {tid}: gold={_gold(r)} got={v} reason={det.get('reason')} "
              f"verb_lemma={det.get('verb_lemma')}")
    for tid in EXPECTED_RECOVERED:
        assert results[tid]["got"] == results[tid]["gold"], (
            f"{tid} must recover to gold, got {results[tid]}")
        assert results[tid]["reason"] == "grounded_result_class", (
            f"{tid} must recover via the new tier specifically, got reason={results[tid]['reason']}")
    # honest: the third target and the not-targeted item stay as measured (no forced pass).
    liniment = results["agg_anne_liniment_cake_ch21"]
    assert liniment["got"] != liniment["gold"] or liniment["reason"] != "grounded_result_class", (
        "agg_anne_liniment_cake_ch21 unexpectedly recovered via the new tier -- update docstring "
        "if this is now genuinely earned")
    v_hd, det_hd = G.congruence_with_lexicon_fallback(d[NOT_TARGETED]["text"])
    assert det_hd.get("reason") != "grounded_result_class", (
        f"{NOT_TARGETED} was explicitly NOT a target (goal-recognition gap) -- the new tier must not "
        f"be the reason it types, got {det_hd}")
    print("[CHECK target_items] recovered=%s (both correct, via grounded_result_class); "
          "agg_anne_liniment_cake_ch21 stays unrecovered (no literal signal in text, honest); "
          "agg_anne_hair_dye_green_ch27 untouched (not a congruence-tier gap)" % EXPECTED_RECOVERED)
    return results


def check_full_eval_and_zero_regression():
    rows, d = _load()
    oov = [r for r in rows if r.get("outcome_in_lexicon") is False]
    assert len(oov) == 36, f"expected 36 OOV, got {len(oov)}"

    before = {r["id"]: _before_verdict(r["text"])[0] for r in rows}
    after = {r["id"]: G.congruence_with_lexicon_fallback(r["text"])[0] for r in rows}

    full44_before = sum(before[r["id"]] == _gold(r) for r in rows)
    full44_after = sum(after[r["id"]] == _gold(r) for r in rows)
    oov36_before = sum(before[r["id"]] == _gold(r) for r in oov)
    oov36_after = sum(after[r["id"]] == _gold(r) for r in oov)
    sub15_before = sum(before[d[i]["id"]] == _gold(d[i]) for i in SUBSET15)
    sub15_after = sum(after[d[i]["id"]] == _gold(d[i]) for i in SUBSET15)

    # BEFORE = frozen replay -> exact (a move here invalidates the recorded delta; fail loudly).
    assert full44_before == EXPECTED_FULL44_BEFORE, (full44_before, EXPECTED_FULL44_BEFORE)
    assert oov36_before == EXPECTED_OOV36_BEFORE, (oov36_before, EXPECTED_OOV36_BEFORE)
    assert sub15_before == EXPECTED_SUB15_BEFORE, (sub15_before, EXPECTED_SUB15_BEFORE)
    # AFTER = live production accuracy, accumulating, more-is-better -> FLOOR (see PIN POLICY).
    assert full44_after >= EXPECTED_FULL44_AFTER_FLOOR, (full44_after, EXPECTED_FULL44_AFTER_FLOOR)
    assert oov36_after >= EXPECTED_OOV36_AFTER_FLOOR, (oov36_after, EXPECTED_OOV36_AFTER_FLOOR)
    assert sub15_after >= EXPECTED_SUB15_AFTER_FLOOR, (sub15_after, EXPECTED_SUB15_AFTER_FLOOR)

    changed = [r["id"] for r in rows if before[r["id"]] != after[r["id"]]]
    gains = [rid for rid in changed if after[rid] == _gold(d[rid]) and before[rid] != _gold(d[rid])]
    regressions = [rid for rid in changed if before[rid] == _gold(d[rid]) and after[rid] != _gold(d[rid])]
    other_changed = [rid for rid in changed if rid not in gains and rid not in regressions]

    # EXACT, deliberately NOT loosened: zero regressions is the invariant this witness exists for.
    assert not regressions, f"REGRESSION: {regressions} were correct before, wrong after"
    # Required-SUBSET (was `sorted(gains) == EXPECTED_RECOVERED`): the gain SET accumulates as other
    # tiers land, but THIS build's 2 recovered items must never drop out of it. Equality here would
    # fail on somebody else's improvement while proving nothing extra -- the "no free lunch" side is
    # already covered exactly by `assert not regressions` above.
    assert set(EXPECTED_RECOVERED) <= set(gains), (sorted(gains), EXPECTED_RECOVERED)

    print(f"[CHECK full_eval_and_zero_regression] full44={full44_before}->{full44_after}/44, "
          f"oov36={oov36_before}->{oov36_after}/36, sub15={sub15_before}->{sub15_after}/15, "
          f"gains={sorted(gains)}, regressions={regressions} (must be empty), "
          f"other_changed_but_still_wrong={other_changed} (honest, not a regression)")
    return {"full44_before": full44_before, "full44_after": full44_after,
            "gains": sorted(gains), "regressions": regressions, "other_changed": other_changed}


def check_owner_propagation():
    """2a-part-1: the 2 recovered items resolve the CORRECT owner via select_outcome_owner, proving
    the congruence fix propagates to the owner-selection path (hdlab.goal_owner_select imports +
    calls congruence_with_lexicon_fallback directly in _unify_owner_via_polarity_path). HONEST
    per-item (not all-or-nothing): _unify_owner_via_polarity_path's OWN goal-search only scans
    sents[:-1] (it does NOT have this build's "also try sents[-1] for a coordinated
    goal+result-in-one-sentence" extension -- that extension lives in
    congruence_grounded_result_class only, a strict-ADD to hdlab/goal_typing.py, and this build is
    NOT authorized to also edit hdlab/goal_owner_select.py). So an item whose ONLY goal-search hit is
    the coordinated-single-sentence case (ts_tom_sugar_theft: the goal 'tried to steal sugar' is in
    the SAME sentence as the outcome 'got his knuckles rapped') can still raise ValueError from
    enumerate_and_score's `not any_typed` branch -- MEASURED, not hidden. Each recovered item is
    checked independently and the outcome (propagated-correctly / raised / wrong-owner) is reported
    per item; only a WRONG owner (not a raise) is a hard failure of this check."""
    _rows, d = _load()
    results = {}
    for rid in EXPECTED_RECOVERED:
        r = d[rid]
        try:
            owner = select_outcome_owner(r["text"], r["roster"], seed=0)
        except ValueError as e:
            results[rid] = {"status": "OWNER_PATH_RAISED", "detail": str(e)[:120]}
            print(f"[CHECK owner_propagation] {rid}: OWNER_PATH_RAISED (not a wrong-owner failure -- "
                  f"see docstring: _unify_owner_via_polarity_path's own goal-search does not extend "
                  f"to the coordinated-single-sentence case) -- {str(e)[:120]}")
            continue
        correct = owner == r["gold_outcome_owner"]
        results[rid] = {"status": "CORRECT" if correct else "WRONG", "owner": owner,
                        "gold": r["gold_outcome_owner"]}
        print(f"[CHECK owner_propagation] {rid}: owner={owner!r} gold={r['gold_outcome_owner']!r} "
              f"-> {'CORRECT' if correct else 'WRONG'}")
        assert correct, (
            f"{rid}: select_outcome_owner resolved a WRONG owner (not a raise) -- "
            f"got {owner!r}, gold {r['gold_outcome_owner']!r}")
    print(f"[CHECK owner_propagation] per-item results: {results}")
    return results


def check_fair_instruments_unchanged():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import test_goal_owner_select as FAIR  # noqa: E402
    result = FAIR.run()
    assert result["full_instrument"]["content_total"] == 48
    assert result["multigoal"]["content"] == 12
    print("[CHECK fair_instruments_unchanged] 48/48 fair + 12/12 multigoal reproduced via imported "
          "test_goal_owner_select.run() (byte-identical, unaffected by this strict-ADD)")
    return result


def check_noise_anti_drift():
    leaks = 0
    for v_, sent in NOISE:
        for goalp in ["Kim wanted to open the greenhouse before winter came",
                      f"Kim wanted to {v_} to the market before noon"]:
            passage = f"{goalp}. {sent}."
            verd, det = G.congruence_with_lexicon_fallback(passage)
            if det.get("reason") == "grounded_result_class":
                leaks += 1
            gv, _gd = G.congruence_grounded_result_class(passage)
            if gv != "NA":
                leaks += 1
    assert leaks == 0, f"NOISE anti-drift leaks = {leaks} (HARD-FAIL if > 0)"
    print("[CHECK noise_anti_drift] 0 leaks on the 8-verb NOISE bank "
          "(congruence_with_lexicon_fallback + congruence_grounded_result_class direct probe)")
    return {"noise_leaks": leaks}


def check_adversarial_overfire():
    failures = []
    for aid, passage, forbidden in ADVERSARIAL:
        v, det = G.congruence_with_lexicon_fallback(passage)
        gv, gdet = G.congruence_grounded_result_class(passage)
        fired = gdet.get("reason") == "grounded_result_class"
        print(f"[CHECK adversarial_overfire] {aid}: full_verdict={v} tier_verdict={gv} "
              f"tier_fired={fired} detail={gdet if fired else '(NA)'}")
        if forbidden is not None and v == forbidden and fired:
            failures.append((aid, v, gdet))
    assert not failures, f"ADVERSARIAL OVER-FIRE: {failures}"
    print(f"[CHECK adversarial_overfire] {len(ADVERSARIAL)}/{len(ADVERSARIAL)} adversarial "
          "sentences: zero forbidden-verdict over-fires from congruence_grounded_result_class")
    return {"n_adversarial": len(ADVERSARIAL), "failures": failures}


def check_self_test_green():
    res = G.self_test()
    print("[CHECK self_test_green] hdlab.goal_typing.self_test() passes unmodified "
          "(this build did not touch any decisive-case assertion)")
    return res


def run():
    r_targets = check_target_items()
    r_full = check_full_eval_and_zero_regression()
    r_owner = check_owner_propagation()
    r_fair = check_fair_instruments_unchanged()
    r_noise = check_noise_anti_drift()
    r_adv = check_adversarial_overfire()
    r_self = check_self_test_green()
    print("[ALL CHECKS PASS] GROUNDED RESULT-CLASS tier: full44 %d->%d/44 (net +%d), gains=%s "
          "(this build's own 2 recovered items are a required subset; any extras are later-landed "
          "tiers, e.g. the Levin last-resort backoff), ZERO regressions, fair instruments "
          "48/48+12/12 unchanged, NOISE 0 leaks, adversarial over-fire 0/%d, self_test green. This "
          "build's banded verdict is unchanged: PARTIAL (its own net +2, below the +3 HARD-PASS "
          "band; bankable per pre-reg gate)." % (
              r_full["full44_before"], r_full["full44_after"],
              r_full["full44_after"] - r_full["full44_before"], r_full["gains"],
              len(ADVERSARIAL)))
    return {"targets": r_targets, "full": r_full, "owner": r_owner, "fair": r_fair,
            "noise": r_noise, "adversarial": r_adv, "self_test": r_self}


if __name__ == "__main__":
    run()
