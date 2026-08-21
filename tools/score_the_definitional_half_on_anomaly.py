"""Do the DEFINITIONAL meanings carry more anomaly signal than the distributional ones?

**THIS TESTS THE LOAD-BEARING CLAIM I HAVE REPEATED ALL SESSION AND NEVER TESTED ON A TASK.**
Angle B's design says: *bind only the definitional half*, because hand-scoring puts it at **32%
MEANINGFUL** against **4%** for the distributional half. **That is a RUBRIC comparison. It has never
been checked against an outcome.** A quality rubric and a task are different things, and this
project's standing rule is that a statistic the mechanism optimises may DIAGNOSE but never DECIDE.

**THE ARM.** A word's profile is built from **the words of its own extracted DEFINITION**
(`definiens_lemmas`), not from accumulated context. The detector then asks how well those definition
words fit the sentence the word is sitting in -- *the banked meaning used as the prediction*, which
is exactly what Angle B proposes.

**COVERAGE IS THE CONFOUND AND IS MEASURED FIRST.** Definitional extraction only fires on sentences
carrying a definitional pattern, so most words have no definition at all. A word with no definition
scores the unknown sentinel and can never be flagged -- **which biases the arm DOWNWARD for reasons
that have nothing to do with meaning quality.** So coverage is printed before any score, and if it
is too low the honest answer is *"cannot be tested at this coverage"*, not *"the definitional half
is worse"*. **That distinction is the whole point of running coverage first.**

*Compare against: untrained codebook ~0 pp, trained distributional substrate +16.3 pp, second-order
counting +29.4 pp (bar +44.2). Same harness, same items, same leak control.*
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import collections  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import sys  # noqa: E402

import numpy as np  # noqa: E402

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for _p in (_REPO, os.path.join(_REPO, "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

SETS = [os.path.join(_REPO, "scratch", "set_%s.json" % s)
        for s in ("20260821", "31415926", "27182818", "16180339")]
N_READ = int(os.environ.get("DIAG_N_READ", "8000"))
UNKNOWN = -1e9


def main():
    from f5_evaluation_harness import DiagnosticFailure, score_across_sets

    from hdlab.corpus_registry import CorpusRegistry
    from hdlab.definitional_extraction import extract_from_sentences
    from hdlab.reading_grounding_loop import content_lemmas, normalize_lemma

    held = set()
    items_all = []
    for p in SETS:
        it = json.load(open(p, encoding="utf-8"))["items"]
        items_all += it
        held |= {i["sentence_original"] for i in it}
    raw = CorpusRegistry().handles["simplewiki"].take(N_READ)
    sents = [s for s in raw if s not in held]
    print("LEAK CONTROL: %d of %d read sentences excluded as item sentences (%d read)"
          % (len(raw) - len(sents), len(raw), len(sents)))

    by_term = extract_from_sentences(sents)
    defs = {}
    for term, ds in by_term.items():
        lem = normalize_lemma(str(term).lower())
        bag = collections.Counter()
        for d in ds:
            bag.update(getattr(d, "definiens_lemmas", []) or [])
        if bag:
            defs.setdefault(lem, collections.Counter()).update(bag)
    print("DEFINITIONS: %d terms extracted from %d sentences, %d with non-empty definiens lemmas"
          % (len(by_term), len(sents), len(defs)))

    # ---- COVERAGE FIRST. A low-coverage arm scores badly for reasons unrelated to meaning quality.
    tgt = [normalize_lemma(i["target"]) for i in items_all]
    intr = [normalize_lemma(i["intruder"]) for i in items_all]
    have_t = sum(1 for w in tgt if w in defs)
    have_i = sum(1 for w in intr if w in defs)
    both = sum(1 for a, b in zip(tgt, intr) if a in defs and b in defs)
    n = len(items_all)
    print("\n" + "=" * 80)
    print("COVERAGE -- READ THIS BEFORE ANY SCORE")
    print("=" * 80)
    print("  items                                    %d" % n)
    print("  the CORRECT word has a definition        %d  (%.1f%%)" % (have_t, 100.0 * have_t / n))
    print("  the INTRUDER has a definition            %d  (%.1f%%)" % (have_i, 100.0 * have_i / n))
    print("  BOTH have one (the scorable items)       %d  (%.1f%%)" % (both, 100.0 * both / n))
    if both < 0.20 * n:
        print("\n  *** COVERAGE IS TOO LOW TO TEST THE CLAIM. ***")
        print("  Fewer than one item in five has a definition for both words, so the arm would score")
        print("  the unknown sentinel on most items and could never flag them. A low number here")
        print("  would measure COVERAGE, not meaning quality, and reporting it as 'the definitional")
        print("  half is worse' would be exactly the confound this section exists to prevent.")
        print("  HONEST VERDICT: NOT TESTABLE at this coverage -- not a negative result.")
        print("\n  *AND THAT IS ITSELF THE ANSWER TO ANGLE B's 'BIND ONLY THE DEFINITIONAL HALF':*")
        print("  *a half that covers this little cannot supply the prediction for most words, so the")
        print("  design needs a fallback for uncovered terms rather than a clean split.*")
        return 0

    def prof(w):
        return defs.get(w)

    def detector(toks, i):
        """HIGHER = more anomalous: NEGATIVE overlap between the word's DEFINITION words and the
        content words of the sentence it sits in."""
        w = normalize_lemma("".join(c for c in toks[i].lower() if c.isalpha()))
        d = prof(w)
        if not d:
            return UNKNOWN
        ctx = collections.Counter(content_lemmas(" ".join(toks)))
        ctx.pop(w, None)
        if not ctx:
            return UNKNOWN
        num = sum(d[k] * ctx[k] for k in set(d) & set(ctx))
        den = math.sqrt(sum(v * v for v in d.values())) * math.sqrt(
            sum(v * v for v in ctx.values())) or 1.0
        return -float(num / den)

    print("\nARM: definition words vs sentence context. Reference: untrained ~0, distributional")
    print("substrate +16.3, second-order counting +29.4 (bar +44.2).\n")
    try:
        out = score_across_sets(detector, SETS, name="DEFINITIONAL_HALF")
    except DiagnosticFailure as e:
        print("\nHARNESS REFUSED TO SCORE IT, and that is a legitimate answer:\n  %s" % e)
        return 0
    print("\nDEFINITIONAL: %s  median %+.1f pp"
          % (", ".join("%+.1f" % e for e in out["effects"]), float(np.median(out["effects"]))))
    print("**Read this against COVERAGE above, not on its own.**")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
