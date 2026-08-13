"""verification/verify_lemma_verb_no_nonword_stems.py (2026-08-13)

WITNESS for the never-emit-a-non-word invariant on `hdlab.thematic_role_labeler.lemma_verb`.

Invariant asserted: for a DICTIONARY input, `lemma_verb` returns either a known English word or
the surface form unchanged -- never a truncation artifact (`status`->`statu`, `analysis`->
`analysi`, `arteries`->`arteri`).

Three blocks:
  (A) NEGATIVE cases: the -us/-is/-ous/-es family the unguarded suffix stripper corrupted. Each
      must come back UNCHANGED.
  (B) POSITIVE control: genuine verb inflections must still lemmatise. A rule that simply
      returned its input would pass (A) and fail (B).
  (C) DICTIONARY sweep: over the full Lancaster u Brysbaert u WordNet surface-form universe,
      no output may be a non-word.

`check(fn)` is factored out so the SAME assertions can be run against the pre-fix function to
demonstrate failing-before. Scaffold-free: imports the production symbol, no tracing.

Run: .venv/Scripts/python.exe verification/verify_lemma_verb_no_nonword_stems.py
"""
from __future__ import annotations

import csv
import os
import sys
from typing import Callable, List, Set

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_LANCASTER = os.path.join(REPO, "data", "grounding_testbed",
                          "Lancaster_sensorimotor_norms_for_39707_words.csv")
_BRYSBAERT = os.path.join(REPO, "data", "grounding_testbed",
                          "Concreteness_ratings_Brysbaert_et_al_BRM.txt")

# (A) must be returned UNCHANGED -- these are dictionary words, not inflections.
UNCHANGED_CASES = [
    "status", "igneous", "staphylococcus", "species", "analysis", "indigenous",
    "gas", "bus", "lens", "virus", "axis", "basis",
]
# (A2) real inflections whose OLD output was a non-word; the correct lemma is a real word.
INFLECTION_CASES = [
    ("billionaires", "billionaire"),
    ("tortures", "torture"),
]
# (B) positive control: genuine verb lemmatisation must survive the fix.
VERB_CASES = [
    ("runs", "run"), ("attaches", "attach"), ("breaks", "break"), ("converted", "convert"),
    ("building", "build"), ("took", "take"), ("cried", "cry"), ("arteries", "artery"),
]


def _dictionary() -> Set[str]:
    """Lancaster u Brysbaert u WordNet surface forms (the forensics universe)."""
    d: Set[str] = set()
    if os.path.exists(_LANCASTER):
        with open(_LANCASTER, "r", encoding="utf-8", newline="") as fh:
            for row in csv.DictReader(fh):
                w = (row.get("Word") or "").strip().lower()
                if w:
                    d.add(w)
    if os.path.exists(_BRYSBAERT):
        with open(_BRYSBAERT, "r", encoding="utf-8", newline="") as fh:
            for i, line in enumerate(fh):
                if i == 0:
                    continue
                parts = line.split("\t")
                if parts and parts[0].strip():
                    d.add(parts[0].strip().lower())
    try:
        from nltk.corpus import wordnet as wn
        for name in wn.all_lemma_names():
            if "_" not in name:
                d.add(name.lower())
    except Exception:  # noqa: BLE001 - degraded mode, norms alone still exercise the sweep
        pass
    return d


def check(fn: Callable[[str], str], sweep: bool = True) -> List[str]:
    """Return a list of failure strings; empty list == invariant holds."""
    from hdlab.thematic_role_labeler import is_known_word

    fails: List[str] = []

    for w in UNCHANGED_CASES:
        got = fn(w)
        if got != w:
            fails.append("A unchanged: {} -> {} (expected {})".format(w, got, w))

    for surf, want in INFLECTION_CASES:
        got = fn(surf)
        if got != want:
            fails.append("A2 inflection: {} -> {} (expected {})".format(surf, got, want))

    for surf, want in VERB_CASES:
        got = fn(surf)
        if got != want:
            fails.append("B positive-control: {} -> {} (expected {})".format(surf, got, want))

    if sweep:
        dictionary = _dictionary()
        bad = []
        for w in sorted(dictionary):
            if not w.isalpha():
                continue
            out = fn(w)
            if out == w:
                continue
            if not (out in dictionary or is_known_word(out)):
                bad.append((w, out))
        if bad:
            sample = ", ".join("{}->{}".format(a, b) for a, b in bad[:15])
            fails.append("C dictionary sweep: {} of {} forms produced a NON-WORD; e.g. {}".format(
                len(bad), len(dictionary), sample))
    return fails


def main() -> int:
    from hdlab.thematic_role_labeler import lemma_verb
    fails = check(lemma_verb)
    if fails:
        print("[witness] FAIL: lemma_verb non-word stems ({} failures)".format(len(fails)))
        for f in fails:
            print("   " + f)
        return 1
    print("[witness] PASS: verify_lemma_verb_no_nonword_stems "
          "(no non-word output over dictionary; verb inflections still lemmatise)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
