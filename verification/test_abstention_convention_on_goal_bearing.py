"""The landed cell scores the third outcome as an ERROR. This fires the day that starts to matter.

WHAT THIS GUARDS (measured 2026-08-22, notes/THE_LANDED_CELL_SCORES_ABSTENTIONS_AS_ERRORS_BY_
OMISSION_SIX_PLACES_DISAGREE_2026-08-22.md)

`hdlab/goal_typing.py` emits three outcomes: MET, UNMET, and an abstention (`:1979 AMBIGUOUS`,
`:1984 NONE`, plus an `NA` family). SIX places classify the abstention as an abstention -- including
`_LEVIN_ABSTAIN` at `:2053`, defined and used INSIDE the emitting module, which is the source of
truth. ONE place classifies it as a WRONG ANSWER:
`experiments/exp_consequence_learning_loop_oov_outcome_verb_valence_v1.py`, whose `_score` does
`ok = (pred == gold)` and never mentions the token. That cell produces the landed number this whole
line is graded on, and it dissents BY OMISSION rather than by decision.

IT IS NOT WRONG TODAY, AND THAT IS LUCK, NOT DESIGN. Its OOV-36 population happens to return zero
AMBIGUOUS. The day it returns one, the landed accuracy silently counts an abstention as an error
and nothing anywhere says so. THIS TEST IS THAT SOMETHING.

FOUR CHECKS, AND THE LAST TWO ARE WHAT MAKE THE FIRST MEAN ANYTHING:
  1. the OOV-36 scored population contains NO abstention token that the cell would miscount
  2. tools/score_with_abstention agrees with hdlab.goal_typing._LEVIN_ABSTAIN (a constant parsed by
     another file is coupled to it, so a divergence must fail loudly rather than drift)
  3. POSITIVE CONTROL on the ORGAN: the in-lexicon 8 DOES contain AMBIGUOUS. Without this, check 1
     would pass vacuously if the loader broke or the organ stopped emitting -- "no X found"
     inherits every blindness of the thing that measures it; "X is present" does not.
  4. POSITIVE CONTROL on the GUARD ITSELF: the check MUST fail when pointed at that population,
     with an actionable message. A guard nobody has seen fire is a guard nobody has tested.
"""
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.goal_typing import congruence_with_lexicon_fallback, _LEVIN_ABSTAIN  # noqa: E402
from tools.score_with_abstention import ABSTAIN_MAJORITY, both_conventions  # noqa: E402

EVAL_REL = os.path.join("experiments", "data", "goal_bearing_modern_eval_v1.jsonl")

# The cell's own filter (experiments/exp_consequence_learning_loop_..._v1.py:126). Mirrored here
# rather than imported, because importing that cell drags in a corpus read.
_OOV = False


def _rows():
    with open(os.path.join(REPO_ROOT, EVAL_REL), "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def _predict(rows):
    return [congruence_with_lexicon_fallback(r["text"])[0] for r in rows]


def _golds(rows):
    return ["MET" if r["gold_outcome_polarity"] == "met" else "UNMET" for r in rows]


def test_constant_matches_the_source_of_truth():
    """A constant duplicated across files is an API. Diverge loudly, never silently."""
    ours = tuple(t for t in ABSTAIN_MAJORITY if t is not None)
    assert set(ours) == set(_LEVIN_ABSTAIN), (
        f"tools/score_with_abstention.ABSTAIN_MAJORITY={ours} has diverged from "
        f"hdlab.goal_typing._LEVIN_ABSTAIN={tuple(_LEVIN_ABSTAIN)}. Reconcile in one commit.")


def test_positive_control_the_organ_still_emits_ambiguous():
    """POSITIVE CONTROL for the test below. If this fails, that test proves nothing."""
    rows = [r for r in _rows() if r.get("outcome_in_lexicon") is True]
    assert rows, "the in-lexicon control items are gone -- the bank changed shape"
    preds = _predict(rows)
    assert "AMBIGUOUS" in preds, (
        f"the organ no longer emits AMBIGUOUS on the in-lexicon controls (got {sorted(set(preds))}). "
        f"Either the organ changed or the loader is broken -- until this passes, the OOV-36 "
        f"absence check below is VACUOUS and must not be read as reassurance.")


def assert_no_miscounted_abstention(rows):
    """The load-bearing check, extracted so a POSITIVE CONTROL can reach it.

    It lived inside the test below and sat BEHIND an `len(rows) == 36` shape assertion, so the
    first positive control I ran tripped the shape check and never exercised this at all -- the
    "a gate's THRESHOLD is not the only thing to check, check what it EXITS BEFORE" rule, caught
    on my own guard within a minute of writing it.
    """
    preds = _predict(rows)
    pair = both_conventions(preds, _golds(rows))
    miscounted = sorted({p for p in preds if p in ABSTAIN_MAJORITY and p not in (None, "NONE")})
    assert pair.agree, (
        f"THE LANDED PRIMARY IS NOW MISCOUNTING ABSTENTIONS AS ERRORS. The OOV-36 population has "
        f"started returning {miscounted}, and "
        f"experiments/exp_consequence_learning_loop_oov_outcome_verb_valence_v1.py:_score scores "
        f"them WRONG via `ok = (pred == gold)` while its own engine "
        f"(hdlab/consequence_learning_loop.py:235) abstains on them.\n"
        f"  under each convention:\n{pair.report()}\n"
        f"FIX: make that cell's _score abstain on {tuple(_LEVIN_ABSTAIN)}, then re-land it. Do NOT "
        f"silence this test -- the landed accuracy is wrong until the cell is fixed.")


def test_landed_population_carries_no_miscounted_abstention():
    """The landed cell counts an abstention as a wrong answer. Today none occurs. Fire when one does."""
    rows = [r for r in _rows() if r.get("outcome_in_lexicon") is _OOV]
    assert len(rows) == 36, f"expected the landed OOV-36 population, got {len(rows)}"
    assert_no_miscounted_abstention(rows)


def test_the_guard_can_actually_fire():
    """POSITIVE CONTROL, wired in rather than run by hand: the check MUST fail on a population
    that really does contain AMBIGUOUS. A guard nobody has seen fire is a guard nobody has tested."""
    inlex = [r for r in _rows() if r.get("outcome_in_lexicon") is True]
    try:
        assert_no_miscounted_abstention(inlex)
    except AssertionError as exc:
        msg = str(exc)
        assert "MISCOUNTING ABSTENTIONS" in msg and "FIX:" in msg, (
            f"the guard fired but its message is not actionable: {msg[:200]}")
        return
    raise AssertionError(
        "THE GUARD IS DECORATIVE: it did not fire on the in-lexicon controls, which are measured "
        "to return 2 AMBIGUOUS of 8. Either the organ changed or the check is broken.")


if __name__ == "__main__":
    test_constant_matches_the_source_of_truth()
    print("[CHECK constant] tools/score_with_abstention matches hdlab.goal_typing._LEVIN_ABSTAIN")
    test_positive_control_the_organ_still_emits_ambiguous()
    print("[CHECK positive_control] the organ still emits AMBIGUOUS on the in-lexicon controls")
    test_landed_population_carries_no_miscounted_abstention()
    print("[CHECK landed_population] OOV-36 carries no abstention the landed cell would miscount")
    test_the_guard_can_actually_fire()
    print("[ALL CHECKS PASS] the by-omission convention in the landed cell is LATENT, not active.")
