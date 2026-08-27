"""Witness for hdlab.incremental_parser (landed 2026-08-27, consolidation phase).

Self-contained construction proof of the incremental left-corner argument-structure builder (no corpus/predictor):
  [1] canonical SVO recovery: "the dog chased the cat" -> the verb's args = {subject, object}.
  [2] LEFT-CORNER bind: the subject is the NEAREST preceding nominal (a bottom-up projection from the buffer),
      not a distant one.
  [3] genuinely INCREMENTAL (Now-or-Never): a PREFIX parse's bindings are a SUBSET of the full-sentence parse --
      eager bindings do not retract as more words arrive (revision off).
  [4] BOUNDED good-enough: a verb's argument set is bounded (<=3: subj+obj+obj2) no matter how many nominals the
      sentence has -- the builder does NOT over-generate (the precision mechanism that beats the batch parser).
  [5] glass-box: incremental_build takes no gold/labels.
The QA-SRL win over the batch parser (+0.0352 F1 via precision) is the solver's verify_incremental_argstruct_builder.py.
"""
from __future__ import annotations

import inspect
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hdlab.incremental_parser import incremental_build  # noqa: E402


def _verb_idx(pos, k=1):
    """1-based index of the k-th VERB."""
    seen = 0
    for i, t in enumerate(pos):
        if t == "VERB":
            seen += 1
            if seen == k:
                return i + 1
    return -1


def main() -> int:
    # [1] canonical SVO: the(1) dog(2) chased(3) the(4) cat(5)  -> verb 3 gets {2 subj, 5 obj}
    toks = ["the", "dog", "chased", "the", "cat"]
    pos = ["DET", "NOUN", "VERB", "DET", "NOUN"]
    out = incremental_build(toks, pos, predictor=None)
    v = _verb_idx(pos)
    print(f"[1] SVO: verb@{v} args={sorted(out.get(v, set()))} (expect subject=2, object=5)")
    assert out.get(v) == {2, 5}, f"canonical SVO not recovered: {out}"

    # [2] LEFT-CORNER: the(1) man(2) dog(3) barked(4) -> subject is the NEAREST preceding nominal (3=dog), not 2
    toks2 = ["the", "man", "dog", "barked"]
    pos2 = ["DET", "NOUN", "NOUN", "VERB"]
    out2 = incremental_build(toks2, pos2, predictor=None)
    v2 = _verb_idx(pos2)
    print(f"[2] left-corner: verb@{v2} args={sorted(out2.get(v2, set()))} (expect nearest nominal 3=dog, not 2)")
    assert out2.get(v2) == {3}, f"subject must be the nearest preceding nominal (left-corner): {out2}"

    # [3] INCREMENTAL / prefix-consistency: a prefix parse's verb args are a SUBSET of the full parse (no retraction)
    full = incremental_build(toks, pos, predictor=None)
    ok_prefix = True
    for k in range(1, len(toks) + 1):
        pref = incremental_build(toks, pos, predictor=None, stop_at=k)
        for vv, args in pref.items():
            if not args.issubset(full.get(vv, set())):
                ok_prefix = False
    print(f"[3] incrementality: every prefix parse's bindings subset the full parse -> {ok_prefix}")
    assert ok_prefix, "[witness] a prefix binding was RETRACTED in the full parse (not genuinely incremental)"

    # [4] BOUNDED good-enough (Now-or-Never): many nominals, one verb -> args bounded <=3, NOT all nominals
    toks3 = ["the", "dog", "and", "the", "cat", "and", "the", "fox", "watched", "the", "mouse"]
    pos3 = ["DET", "NOUN", "CCONJ", "DET", "NOUN", "CCONJ", "DET", "NOUN", "VERB", "DET", "NOUN"]
    out3 = incremental_build(toks3, pos3, predictor=None)
    v3 = _verb_idx(pos3)
    n_nominals = sum(1 for t in pos3 if t == "NOUN")
    args3 = out3.get(v3, set())
    print(f"[4] bounded: verb@{v3} args={sorted(args3)} (|args|={len(args3)} <=3; sentence has {n_nominals} nominals)")
    assert len(args3) <= 3, f"the builder over-generated (|args|={len(args3)} > 3): not bounded good-enough"
    assert len(args3) < n_nominals, "a verb should NOT bind every nominal (precision over over-generation)"

    # [5] glass-box: no gold in the signature
    params = list(inspect.signature(incremental_build).parameters)
    assert "gold" not in params and "labels" not in params, params
    print(f"[5] glass-box PASS (no gold/labels in signature; args are indices, no external answer)")

    print("\nALL WITNESS ASSERTIONS PASSED -- the incremental left-corner builder recovers canonical argument")
    print("structure, binds the nearest preceding nominal (left-corner), is genuinely incremental (prefix parses")
    print("do not retract), and is bounded good-enough (<=3 args/verb, no over-generation).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
