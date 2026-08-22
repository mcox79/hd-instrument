"""NON-FORK WITNESS: hdlab/quality_proxy.py must agree ITEM-FOR-ITEM with the cell it was promoted from.

`hdlab.quality_proxy` carries a promoted copy of `cooccurs_v4` from
`experiments/exp_foundation_validation_harness_v4_proximity_v1.py`. A copy can drift from its source
silently, and the p = 0.0038 validation belongs to the CELL's version -- so if the two ever disagree,
the promoted module is no longer the thing that was validated.

This is the same pattern `exp_graded_divisive_comparator_v1` used to justify its own promotion:
assert byte-level agreement against the live implementation rather than trusting that a copy stayed
faithful.

Scaffold-free: imports both real modules and compares on the REAL corpus.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                "experiments"))

from hdlab import quality_proxy                                     # noqa: E402


def _cell():
    import exp_foundation_validation_harness_v4_proximity_v1 as v4  # noqa: E402
    return v4


def test_constants_match_the_validated_cell():
    """The p = 0.0038 validation was measured at exactly these values."""
    v4 = _cell()
    assert quality_proxy.PROXIMITY_WINDOW == v4.PROXIMITY_WINDOW, "proximity window drifted"
    assert quality_proxy.MIN_STEM_COVERAGE == v4.MIN_STEM_COVERAGE, "coverage threshold drifted"


def test_tokenisation_is_identical():
    v4 = _cell()
    for s in ("The cat sat on the mat.", "Don't split isn't wrongly, please.",
              "Numbers 123 and punctuation -- gone."):
        assert quality_proxy.sentence_tokens(s) == v4._sentence_tokens(s), f"tokenisation differs on {s!r}"


def test_agrees_item_for_item_on_the_real_corpus():
    """THE witness. Same facts, same corpus, both implementations."""
    import json
    v4 = _cell()
    from exp_foundation_validation_harness_v1 import load_corpus_sentences, CORPUS_SOURCES_FULL

    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    rows_path = os.path.join(repo, "data", "exp_grounding_quality_readout_v1", "_joined_verdicts.json")
    if not os.path.exists(rows_path):
        raise AssertionError(f"validation rows missing: {rows_path}")
    rows = json.load(open(rows_path, encoding="utf-8"))

    sents = load_corpus_sentences(CORPUS_SOURCES_FULL)
    toks = quality_proxy.tokenize_corpus(sents)

    n_true = 0
    for r in rows:
        mine = quality_proxy.is_meaningful_fact(r["subj"], r["obj"], toks)
        theirs = bool(v4.cooccurs_v4(r["subj"], r["obj"], toks))
        assert mine == theirs, f"disagreement on ({r['subj']}, {r['obj']}): {mine} vs {theirs}"
        n_true += int(mine)

    # POSITIVE CONTROL: agreement is worthless if both always say False. The validated run had
    # 32 of 100 passing (GOOD 13/22 + NOISE 19/78); assert the comparison was non-degenerate.
    assert n_true > 10, (f"only {n_true}/100 passed -- both implementations may be broken "
                         f"(the validated run had 32)")


def _run() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"  PASS  {t.__name__}")
        except AssertionError as exc:
            failed += 1
            print(f"  FAIL  {t.__name__}: {exc}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(_run())
