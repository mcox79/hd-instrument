# WIRE-DON'T-ISLAND PROMOTION WITNESS (2026-08-08). Scaffold-free, tracing=False (no HDC tracing
# anywhere in this module -- the organ under test does not take a tracing flag).
"""verification/test_parse_goal_extraction.py -- reproduces the core validation numbers for
hdlab.parse_goal_extraction (parse-structure GOAL-referent extraction organ) directly off the
PROMOTED public functions (parse_extract_goal / find_desired_state_v2), not off any experiment cell
-- this organ was validated in a session scratchpad script and promoted straight to hdlab/; see
hdlab/parse_goal_extraction.py's module docstring for the full mechanism + validated-numbers writeup
this witness's checks are drawn from.

Four checks:
  (1) FRESH RECALL: parse_extract_goal recovers the goal NP on >=15/18 of a fresh bank of
      request/categorical/passive/coordination/relative-clause/pp-distractor phrasings (18-item
      bank, verbatim from the source validation script's FRESH_ITEMS) -- also asserts
      hdlab.goal_typing.find_desired_state fires on NONE of them, documenting the phrasing gap this
      organ closes (find_desired_state has no nominal-request-complement pass at all).
  (2) STRICT-ADD: find_desired_state_v2 is BYTE-IDENTICAL (full dict equality, not just the referent
      field) to find_desired_state on 6 existing desiderative-style sentences find_desired_state
      already resolves -- proves the composition never overrides the production organ, only fills
      the gap when it returns None.
  (3) SUBJECT_IS_REFERENT FIX: "Ruth longed to win the reading prize this year." (embedded verb
      'win' is in the ARRIVE_SUCCEED class) resolves to the SUBJECT ('ruth') under parse_extract_goal
      called STANDALONE, not the embedded verb's object ('prize'/'reading') -- the fix this
      promotion adds over a naive PASS-B lift (a naive lift regresses this exact case: disk-verified
      in the source script's own STRICT-ADD sanity run, parse='reading' vs find_desired_state='ruth'
      before the fix). Cross-checked against find_desired_state's own verdict on the same two
      sentences (which already gets this right via its own SUBJECT_IS_REFERENT_CLASSES branch) to
      confirm the target referent is real, not a fabricated gold label.
  (4) DETERMINISM: same input -> same output, twice, for both public functions.
"""
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.parse_goal_extraction import parse_extract_goal, find_desired_state_v2  # noqa: E402
from hdlab.goal_typing import find_desired_state  # noqa: E402


# ---------------------------------------------------------------------------
# (1) fresh 18-item bank: request_basic / ditransitive / passive / coordination / relative_clause /
# pp_distractor -- verbatim (type, sentence, gold) from the source scratchpad validation script's
# FRESH_ITEMS, disk-verified this promotion: parse_extract_goal=17/18, find_desired_state=0/18.
# ---------------------------------------------------------------------------
FRESH_ITEMS = [
    ("request_basic", "Maria asked for a window seat.", "seat"),
    ("request_basic", "The clerk reserved a table for four.", "table"),
    ("request_basic", "He ordered a large pizza.", "pizza"),
    ("request_basic", "She requested a refund.", "refund"),
    ("ditransitive", "They booked her an aisle seat.", "seat"),
    ("passive", "A window seat was requested for Maria.", "seat"),
    ("passive", "A refund was requested by the customer.", "refund"),
    ("passive", "A larger office was requested by the new hire.", "office"),
    ("passive", "A window seat was booked for the elderly passenger.", "seat"),
    ("passive", "Aisle seating was ordered for the entire group.", "seating"),
    ("coordination", "The manager booked a flight and reserved a car.", "flight"),
    ("coordination", "The team requested more time and a bigger budget.", "time"),
    ("coordination", "They ordered two coffees and a sandwich.", "coffees"),
    ("relative_clause", "The seat that Maria requested was near the window.", "seat"),
    ("pp_distractor", "The customer asked for a discount on the item.", "discount"),
    ("pp_distractor", "We reserved the entire venue for the wedding.", "venue"),
    ("pp_distractor", "The children asked for more cookies after dinner.", "cookies"),
    ("pp_distractor", "The committee requested additional funding for the project.", "funding"),
]


def check_fresh_recall_ge_15_of_18():
    assert len(FRESH_ITEMS) == 18
    n_correct = 0
    n_baseline_fires = 0
    misses = []
    for ptype, sentence, gold in FRESH_ITEMS:
        got = parse_extract_goal(sentence)
        referent = got["referent"] if got else None
        if referent == gold:
            n_correct += 1
        else:
            misses.append((ptype, sentence, gold, referent))
        if find_desired_state(sentence) is not None:
            n_baseline_fires += 1
    assert n_baseline_fires == 0, (
        f"expected find_desired_state to fire on NONE of these 18 (documents the phrasing gap this "
        f"organ closes), got {n_baseline_fires} firing")
    assert n_correct >= 15, (
        f"parse_extract_goal must recover >=15/18, got {n_correct}/18; misses={misses}")
    print(f"[CHECK fresh_recall] parse_extract_goal={n_correct}/18 (misses={[m[1] for m in misses]}); "
          f"find_desired_state baseline=0/18 (phrasing gap confirmed)")
    return {"n_correct": n_correct, "n_total": 18, "misses": misses}


# ---------------------------------------------------------------------------
# (2) STRICT-ADD sanity: find_desired_state_v2 byte-identical to find_desired_state whenever the
# baseline already fires -- verbatim SANITY_ITEMS from the source validation script (all 6
# disk-verified to already return non-None from find_desired_state).
# ---------------------------------------------------------------------------
STRICT_ADD_ITEMS = [
    "Jack wanted to fix the old fence before the storm came.",
    "Ruth longed to win the reading prize this year.",
    "Owen wanted to save the boat before the storm hit",
    "Owen wanted to sink the raft before dawn",
    "Tom tried to steal sugar under his aunt's nose.",
    "Beth hoped to win a place at the summer fair.",
]


def check_strict_add_byte_identical():
    assert len(STRICT_ADD_ITEMS) == 6
    for s in STRICT_ADD_ITEMS:
        baseline = find_desired_state(s)
        assert baseline is not None, (
            f"STRICT-ADD sanity item must already resolve under find_desired_state: {s!r}")
        composed = find_desired_state_v2(s)
        assert composed == baseline, (
            f"find_desired_state_v2 must be byte-identical to find_desired_state when the baseline "
            f"fires: sentence={s!r} baseline={baseline!r} composed={composed!r}")
    print(f"[CHECK strict_add] find_desired_state_v2 byte-identical to find_desired_state on "
          f"{len(STRICT_ADD_ITEMS)}/{len(STRICT_ADD_ITEMS)} existing desiderative-goal sentences")
    return {"n_checked": len(STRICT_ADD_ITEMS)}


# ---------------------------------------------------------------------------
# (3) SUBJECT_IS_REFERENT fix: ARRIVE_SUCCEED-class embedded verb ('win') -> SUBJECT, not object,
# under parse_extract_goal called STANDALONE (not via the find_desired_state_v2 passthrough, which
# would mask a regression here since find_desired_state already resolves these two sentences).
# ---------------------------------------------------------------------------
def check_subject_is_referent_fix():
    sentence = "Ruth longed to win the reading prize this year."
    got = parse_extract_goal(sentence)
    assert got is not None, f"parse_extract_goal returned None for {sentence!r}"
    assert got["referent"] == "ruth", (
        f"expected SUBJECT 'ruth' (ARRIVE_SUCCEED-class embedded verb 'win'), got "
        f"{got['referent']!r} (construction={got.get('construction')!r}) -- this is exactly the "
        f"regression a naive object-only PASS-B lift produces (parse='reading', disk-verified this "
        f"promotion before the fix)")
    assert got["construction"] == "PURPOSE_INF_SUBJECT", (
        f"expected construction=PURPOSE_INF_SUBJECT, got {got.get('construction')!r}")

    sentence2 = "Beth hoped to win a place at the summer fair."
    got2 = parse_extract_goal(sentence2)
    assert got2 is not None, f"parse_extract_goal returned None for {sentence2!r}"
    assert got2["referent"] == "beth", (
        f"expected SUBJECT 'beth', got {got2['referent']!r} "
        f"(construction={got2.get('construction')!r})")
    assert got2["construction"] == "PURPOSE_INF_SUBJECT"

    # Cross-check: find_desired_state (baseline) independently agrees on the SAME referent for both
    # sentences via its own SUBJECT_IS_REFERENT_CLASSES branch -- confirms the target is a real gold
    # referent, not a label invented for this witness.
    b1, b2 = find_desired_state(sentence), find_desired_state(sentence2)
    assert b1 is not None and b1["referent"] == "ruth", f"baseline disagreement: {b1!r}"
    assert b2 is not None and b2["referent"] == "beth", f"baseline disagreement: {b2!r}"
    print("[CHECK subject_is_referent] parse_extract_goal('...longed to win...') -> referent='ruth' "
          "(subject, not object); parse_extract_goal('...hoped to win...') -> referent='beth'; both "
          "match find_desired_state's own SUBJECT_IS_REFERENT_CLASSES verdict")
    return {"ruth_referent": got["referent"], "beth_referent": got2["referent"]}


# ---------------------------------------------------------------------------
# (4) determinism: same input -> same output, twice, for both public functions.
# ---------------------------------------------------------------------------
def check_determinism():
    samples = [s for _t, s, _g in FRESH_ITEMS[:6]] + STRICT_ADD_ITEMS[:3] + \
        ["Ruth longed to win the reading prize this year."]
    for s in samples:
        a1 = parse_extract_goal(s)
        a2 = parse_extract_goal(s)
        assert a1 == a2, f"parse_extract_goal not deterministic on {s!r}: {a1!r} != {a2!r}"
        b1 = find_desired_state_v2(s)
        b2 = find_desired_state_v2(s)
        assert b1 == b2, f"find_desired_state_v2 not deterministic on {s!r}: {b1!r} != {b2!r}"
    print(f"[CHECK determinism] {len(samples)} sentences, parse_extract_goal + find_desired_state_v2 "
          f"both stable across repeated calls")
    return {"n_checked": len(samples)}


# ---------------------------------------------------------------------------
# pytest collection wrappers
# ---------------------------------------------------------------------------
def test_fresh_recall_ge_15_of_18():
    check_fresh_recall_ge_15_of_18()


def test_strict_add_byte_identical():
    check_strict_add_byte_identical()


def test_subject_is_referent_fix():
    check_subject_is_referent_fix()


def test_determinism():
    check_determinism()


def run():
    r1 = check_fresh_recall_ge_15_of_18()
    r2 = check_strict_add_byte_identical()
    r3 = check_subject_is_referent_fix()
    r4 = check_determinism()
    print("[ALL CHECKS PASS] hdlab/parse_goal_extraction reproduces >=15/18 fresh recall + "
          "STRICT-ADD byte-identical + SUBJECT_IS_REFERENT fix + determinism.")
    return {"fresh_recall": r1, "strict_add": r2, "subject_is_referent": r3, "determinism": r4}


if __name__ == "__main__":
    import json
    print(json.dumps(run(), indent=2, default=str))
