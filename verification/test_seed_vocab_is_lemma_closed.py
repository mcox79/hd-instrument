"""SEED_VOCAB must be LEMMA-CLOSED, because `substrate.py` compares LEMMAS against it.

**THE INVARIANT.** `hdlab/substrate.py` line ~547 does:

    for lem in content_lemmas(sent):
        if lem in self._seed_set:
            continue                      # do not episodically encode a seed word

`content_lemmas` yields **LEMMAS**; `_seed_set` is built from **`SEED_VOCAB` as written**. So a
seed entry stored only in a surface form is INVISIBLE to that check, and the word gets episodically
encoded when the design says skip it.

**AUDITED 2026-08-21 AND THE SUBSTRATE IS CLEAN -- BUT BY A PROPERTY NOTHING ASSERTED.** 15 of the
107 entries are not their own lemma (`called`, `used`, `made`, `known`, `named`, `is`/`are`/`was`,
...), and **all 15 have their lemma ALSO present in the list**, so the comparison never misses.
Measured on 4,000 simplewiki sentences: 34,647 content lemmas, 4,038 correctly skipped as seeds,
**0 missed.**

**Verbs are NOT filtered out, so this is a live path, not a theoretical one:**
`"The house was called Rome"` -> `content_lemmas` gives `call, house, people, rome`. The check
survives only because `SEED_VOCAB` happens to hold BOTH `called` and `call`.

**SO THIS FILE EXISTS TO STOP THAT BEING AN ACCIDENT.** Adding one inflected seed word without its
lemma would silently change what gets episodically encoded, with no error and no visible symptom --
the failure class this repo keeps paying for. *Write the control into the code, not the caution into
the prose.*

*This audit was prompted by a surface-vs-lemma lookup bug found in the F5 floor scorers the same
day, where the same mistake WAS present and deflated every measured floor. The question "is this
bug class anywhere else?" is an enumeration, and this is its answer for `hdlab/`.*
"""
from __future__ import annotations

import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)


def test_seed_vocab_is_lemma_closed():
    from hdlab.reading_grounding_loop import normalize_lemma
    from hdlab.substrate import SEED_VOCAB

    seed = set(SEED_VOCAB)
    uncovered = [(w, normalize_lemma(w)) for w in SEED_VOCAB
                 if normalize_lemma(w) != w and normalize_lemma(w) not in seed]
    assert not uncovered, (
        "SEED_VOCAB is not lemma-closed: %d entr(y/ies) appear only in a surface form, so "
        "substrate.py's `lem in self._seed_set` check will MISS them and episodically encode a "
        "word the design says to skip. Add the lemma alongside the surface form. Offenders: %s"
        % (len(uncovered), uncovered))


def test_the_check_is_actually_reachable():
    """POSITIVE CONTROL: prove verbs survive content-word filtering, so the invariant above is
    protecting a LIVE path rather than an unreachable one. An invariant nobody can violate is not
    worth asserting, and a test that passes for that reason is worse than no test."""
    from hdlab.reading_grounding_loop import content_lemmas
    from hdlab.substrate import SEED_VOCAB

    lemmas = content_lemmas("The house was called Rome by the people")
    assert "call" in lemmas, (
        "expected the verb 'called' to survive as the lemma 'call'; got %s. If verbs are now "
        "filtered out, the lemma-closure invariant may no longer be load-bearing -- re-derive it "
        "rather than deleting this file." % lemmas)
    assert "called" in SEED_VOCAB and "call" in SEED_VOCAB, (
        "the worked example this test is built on has changed: SEED_VOCAB no longer holds both "
        "'called' and 'call'")


def test_negative_control_a_broken_list_is_caught():
    """The guard must FAIL on a list that violates the invariant, or it proves nothing."""
    from hdlab.reading_grounding_loop import normalize_lemma

    broken = ["house", "called"]          # 'call' deliberately absent
    seed = set(broken)
    uncovered = [(w, normalize_lemma(w)) for w in broken
                 if normalize_lemma(w) != w and normalize_lemma(w) not in seed]
    assert uncovered == [("called", "call")], (
        "the detector did not flag a deliberately lemma-open list; it cannot be trusted on the "
        "real one. got %s" % uncovered)


if __name__ == "__main__":
    test_seed_vocab_is_lemma_closed()
    test_the_check_is_actually_reachable()
    test_negative_control_a_broken_list_is_caught()
    print("PASS: SEED_VOCAB is lemma-closed, the check is on a live path (verbs survive), and the "
          "detector catches a deliberately broken list")
