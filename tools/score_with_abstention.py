"""Score a classifier that can ABSTAIN, with no call signature that returns a bare accuracy.

WHY THIS EXISTS -- A MEASURED FAILURE, 2026-08-22, MINE
-------------------------------------------------------
I reported that supplying a word "eliminates abstention entirely: 0/8, Fisher p = 0.0049". I had
counted the third outcome, AMBIGUOUS, as a WRONG COMMITMENT. Six of the seven places in this repo
that classify it -- INCLUDING THE MODULE THAT EMITS IT -- count it as an ABSTENTION. Under theirs
the same data reads 2/8 and p = 0.2404 -- not significant. THE NUMBER PASSED A POSITIVE CONTROL, A
PRE-REGISTRATION AND A POWER CALCULATION AND BROKE ON A DEFINITION I NEVER LOOKED UP.

This is standing discipline 13 -- REPORT TIE CONVENTIONS BOTH WAYS, NEVER SILENTLY PICK THE
FLATTERING ONE -- in a new costume: there the ambiguous case was a TIE in a ranking, here it is a
THIRD OUTCOME in a classification. The repo already escalated the ranking version into
`tools/rank_with_ties.py` after the prose rule was violated twice in one day. This is the same
escalation for the classification version.

THE ENUMERATED DISAGREEMENT IN THE REPO (grep `AMBIGUOUS` over the consumers of this organ)
-------------------------------------------------------------------------------------------
ABSTENTION (6):  hdlab/goal_typing.py:2053 `_LEVIN_ABSTAIN`, USED at :2200 and :2214 -- THE SOURCE
                   OF TRUTH, in the very module that emits "AMBIGUOUS" at :1979
                 hdlab/consequence_learning_loop.py:219,235 ("AMBIGUOUS -> abstain")
                 verification/verify_levin_lastresort_backoff.py:51
                 verification/verify_request_response_typing.py:200
                 experiments/exp_verbclass_backoff_coverage_v1.py:214
                 experiments/exp_verbclass_backoff_coverage_v2.py:73

TWO FALSE POSITIVES I CHECKED RATHER THAN COUNTED: hdlab/goal_achievement.py's 7 hits are all
SCRAMBLE-CONTROL assertion strings, and hdlab/coref.py:295 is the substring "UNAMBIGUOUS" in a
comment. Neither is a third-outcome scorer. An enumeration is only worth as much as the reading.

WRONG ANSWER (1): experiments/exp_consequence_learning_loop_oov_outcome_verb_valence_v1.py
                 -- BY OMISSION. Its `_score` does `ok = (pred == gold)` and never mentions
                 AMBIGUOUS, so an abstention silently lands in the error column.

THE DISSENTER IS THE CELL WHOSE NUMBER THE WHOLE LINE IS GRADED ON, AND IT DISSENTS BY ACCIDENT.
Measured today: no AMBIGUOUS occurs in its OOV-36 population, so its landed primary is NOT wrong.
It is one prediction away from being wrong, and it WOULD be wrong on the in-lexicon 8 (2 of 8).

THE RULE
--------
`score()` returns an `AbstentionScore`. There is no call signature that yields a bare float.
`both_conventions()` scores the same data both ways and sets `.agree` -- when it is False, NO
accuracy from that data may be quoted without naming the convention beside it.

Self-test: `python tools/score_with_abstention.py --self-test`
"""

from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")

import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
from dataclasses import dataclass

# The repo-majority convention, enumerated above. Kept as a named constant so a future change is
# a visible edit rather than a habit.
ABSTAIN_MAJORITY = (None, "NONE", "NA", "AMBIGUOUS")
ABSTAIN_NARROW = (None, "NONE")


@dataclass(frozen=True)
class AbstentionScore:
    """A score that carries its own convention. Deliberately has no bare-accuracy accessor."""
    n: int
    correct: int
    wrong: int
    abstained: int
    abstain_tokens: tuple
    label: str

    @property
    def accuracy_abstain_counts_wrong(self) -> float:
        """Accuracy over ALL items, abstentions scored as errors. The strict reading."""
        return self.correct / self.n if self.n else float("nan")

    @property
    def precision_when_committing(self) -> float:
        """Accuracy over COMMITTED items only. Undefined if it never commits."""
        committed = self.correct + self.wrong
        return self.correct / committed if committed else float("nan")

    @property
    def abstention_rate(self) -> float:
        return self.abstained / self.n if self.n else float("nan")

    def line(self) -> str:
        return (f"[{self.label}] n={self.n} correct={self.correct} wrong={self.wrong} "
                f"abstained={self.abstained} | acc(abstain=wrong)="
                f"{self.accuracy_abstain_counts_wrong:.4f} | precision_when_committing="
                f"{self.precision_when_committing:.4f} | abstention_rate="
                f"{self.abstention_rate:.4f} | abstains_on={list(self.abstain_tokens)}")


def score(preds, golds, abstain_tokens=ABSTAIN_MAJORITY, label="majority") -> AbstentionScore:
    """Score predictions against golds. Returns a result carrying its convention, never a float."""
    preds, golds = list(preds), list(golds)
    if len(preds) != len(golds):
        raise ValueError(f"length mismatch: {len(preds)} preds vs {len(golds)} golds")
    if not preds:
        raise ValueError("refusing to score an empty population")
    c = w = a = 0
    for p, g in zip(preds, golds):
        if p in abstain_tokens:
            a += 1
        elif p == g:
            c += 1
        else:
            w += 1
    return AbstentionScore(len(preds), c, w, a, tuple(abstain_tokens), label)


@dataclass(frozen=True)
class ConventionPair:
    majority: AbstentionScore
    narrow: AbstentionScore

    @property
    def agree(self) -> bool:
        """True iff the choice of convention cannot change any headline from this data."""
        return (self.majority.correct == self.narrow.correct
                and self.majority.wrong == self.narrow.wrong
                and self.majority.abstained == self.narrow.abstained)

    def report(self) -> str:
        out = [self.majority.line(), self.narrow.line()]
        if self.agree:
            out.append("[conventions] AGREE -- no AMBIGUOUS/NA in this population; "
                       "either reading gives the same numbers.")
        else:
            out.append("[conventions] DISAGREE -- NO ACCURACY OR ABSTENTION FIGURE FROM THIS "
                       "POPULATION MAY BE QUOTED WITHOUT NAMING THE CONVENTION BESIDE IT.")
        return "\n".join(out)


def both_conventions(preds, golds) -> ConventionPair:
    return ConventionPair(
        score(preds, golds, ABSTAIN_MAJORITY, "majority: AMBIGUOUS/NA abstain"),
        score(preds, golds, ABSTAIN_NARROW, "narrow:   only NONE abstains"),
    )


def self_test() -> int:
    # 1. THE REAL FAILURE. The in-lexicon 8, measured 2026-08-22 through the live organ:
    #    predictions MET 3 / UNMET 3 / AMBIGUOUS 2 against 4 MET / 4 UNMET, scoring 4 correct.
    preds = ["MET", "MET", "AMBIGUOUS", "UNMET", "AMBIGUOUS", "UNMET", "MET", "UNMET"]
    golds = ["UNMET", "MET", "UNMET", "UNMET", "MET", "UNMET", "MET", "MET"]
    pair = both_conventions(preds, golds)
    assert pair.majority.correct == 4 and pair.narrow.correct == 4, "correct count must not move"
    assert pair.majority.abstained == 2, f"majority abstained={pair.majority.abstained}, want 2"
    assert pair.narrow.abstained == 0, f"narrow abstained={pair.narrow.abstained}, want 0"
    assert not pair.agree, "the real failure MUST be flagged as a disagreement"
    print("[self-test] PASS reproduces the real 2026-08-22 failure: abstained 2 vs 0, flagged")

    # 2. THE HEADLINE THAT SURVIVED IT. Accuracy is identical either way -- the guard must not
    #    imply otherwise, or it would have flagged a claim that was actually robust.
    assert (pair.majority.accuracy_abstain_counts_wrong
            == pair.narrow.accuracy_abstain_counts_wrong == 0.5), "accuracy is convention-free here"
    print("[self-test] PASS accuracy 0.5000 is identical under both -- that claim was robust")

    # 3. NEGATIVE CONTROL. A population with no ambiguous outcome must NOT be flagged, or the
    #    guard cries wolf and gets ignored (the lesson rank_with_ties.py records).
    clean = both_conventions(["MET", "UNMET", "NONE", "MET"], ["MET", "MET", "UNMET", "MET"])
    assert clean.agree, "a population with no AMBIGUOUS/NA must NOT be flagged"
    assert clean.majority.abstained == 1 and clean.majority.correct == 2
    print("[self-test] PASS clean population is NOT flagged (no false alarm)")

    # 4. THE LANDED CELL'S OOV-36 POPULATION: UNMET 7 / NONE 20 / MET 9, no AMBIGUOUS. Its
    #    by-omission convention is therefore harmless TODAY -- assert exactly that, so if the
    #    population ever changes this test says so.
    oov = ["NONE"] * 20 + ["MET"] * 9 + ["UNMET"] * 7
    assert both_conventions(oov, ["MET"] * 36).agree, (
        "OOV-36 shape must contain no AMBIGUOUS -- if this fails, the landed primary is now "
        "scoring abstentions as errors and the cell must be fixed")
    print("[self-test] PASS landed OOV-36 shape is convention-free (its omission is latent, "
          "not active)")

    # 5. COUPLING TO THE SOURCE OF TRUTH. hdlab/goal_typing.py:2053 defines `_LEVIN_ABSTAIN` and
    #    USES it at :2200 and :2214 -- in the SAME module that emits "AMBIGUOUS" at :1979. That is
    #    the canonical set, so this guard must not quietly diverge from it. Imported here rather
    #    than at module level so callers do not pay for importing hdlab.
    from hdlab.goal_typing import _LEVIN_ABSTAIN  # noqa: E402
    canonical = tuple(t for t in ABSTAIN_MAJORITY if t is not None)
    assert set(canonical) == set(_LEVIN_ABSTAIN), (
        f"DIVERGED FROM THE SOURCE OF TRUTH: hdlab.goal_typing._LEVIN_ABSTAIN is "
        f"{_LEVIN_ABSTAIN}, this module's is {canonical}. Reconcile them in one commit -- "
        f"a doc parsed by code is coupled to it, and so is a constant.")
    print(f"[self-test] PASS matches hdlab.goal_typing._LEVIN_ABSTAIN {tuple(_LEVIN_ABSTAIN)} "
          f"(plus None for a missing prediction)")

    # 6. REFUSALS.
    for bad, why in (((["MET"], ["MET", "MET"]), "length mismatch"), (([], []), "empty")):
        try:
            score(*bad)
        except ValueError:
            print(f"[self-test] PASS refuses {why}")
        else:
            raise AssertionError(f"should have refused {why}")

    print("[self-test] RESULT: PASS")
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        raise SystemExit(self_test())
    print(__doc__)
    raise SystemExit(0)
