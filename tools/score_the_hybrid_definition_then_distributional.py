"""Does using the DEFINITION when there is one, and the distributional profile otherwise, beat
either alone?

**THIS TURNS AN OPEN DESIGN DECISION INTO A MEASUREMENT.** Angle B's corrected note recorded three
fallbacks for the ~75% of words with no extracted definition, and said I had no evidence to choose:

1. no prediction for uncovered words (a scope admission),
2. **fall back to the distributional profile** -- contradicts the design's stated reason for the
   split, but the distributional arm measures **+16.3 pp** on this task, so it is not worthless,
3. widen definitional coverage first (unbounded work).

**OPTION 2 IS THE ONLY ONE THAT IS CHEAP TO TEST, AND IT IS DECIDABLE TODAY.** If the hybrid beats
the pure distributional arm, the fallback is justified by outcome rather than by preference. If it
does not, the definitional half adds nothing at the coverage it has, and the design should say so.

**THE PRE-COMMITTED READING, WRITTEN BEFORE THE RUN:**

| result | what it means |
|---|---|
| hybrid **>** distributional, CI-separated | the definitions carry signal the profiles do not -- fallback justified |
| hybrid ~ distributional | the definitions add nothing AT THIS COVERAGE. **Not "definitions are useless"** -- 24.6% coverage bounds how much they could add |
| hybrid **<** distributional | the definitions are actively worse where they fire, which would be a finding about the extractor |

*Paired against the distributional arm on the same items via `compare_detectors_paired`, because
overlapping marginal CIs are not a test of a difference -- the lesson from the substrate-vs-counting
comparison earlier today.*
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

from memory_guard import guard  # noqa: E402
_MEM = guard(limit_gb=2.0, label=os.path.basename(__file__))

SETS = [os.path.join(_REPO, "scratch", "set_%s.json" % s)
        for s in ("20260821", "31415926", "27182818", "16180339")]
N_READ = int(os.environ.get("DIAG_N_READ", "8000"))
UNKNOWN = -1e9


def main():
    from f5_evaluation_harness import compare_detectors_paired, score_across_sets

    from hdlab.corpus_registry import CorpusRegistry
    from hdlab.definitional_extraction import extract_from_sentences
    from hdlab.reading_grounding_loop import (
        CTX_D,
        ConceptSpace,
        content_lemmas,
        context_vector_masked,
        normalize_lemma,
    )

    held = set()
    for p in SETS:
        held |= {i["sentence_original"] for i in json.load(open(p, encoding="utf-8"))["items"]}
    raw = CorpusRegistry().handles["simplewiki"].take(N_READ)
    sents = [s for s in raw if s not in held]
    print("LEAK CONTROL: %d of %d read sentences excluded as item sentences (%d read)"
          % (len(raw) - len(sents), len(raw), len(sents)))

    # ---- the two ingredients, built from the SAME sentences so neither gets extra data
    by_term = extract_from_sentences(sents)
    defs = {}
    for term, ds in by_term.items():
        bag = collections.Counter()
        for d in ds:
            bag.update(getattr(d, "definiens_lemmas", []) or [])
        if bag:
            defs.setdefault(normalize_lemma(str(term).lower()), collections.Counter()).update(bag)

    space = ConceptSpace(d=CTX_D)
    for k, s in enumerate(sents):
        _MEM()
        for lem in content_lemmas(s):
            space.observe(lem, context_vector_masked(s, lem, d=CTX_D))
        if (k + 1) % 2500 == 0:
            print("  read %d/%d" % (k + 1, len(sents)), flush=True)
    print("INGREDIENTS: %d defined terms, %d accumulated anchors (SAME sentences for both)"
          % (len(defs), len(space.anchors())))

    def _lem(t):
        return normalize_lemma("".join(c for c in t.lower() if c.isalpha()))

    def distributional(toks, i):
        lem = _lem(toks[i])
        prof = space.bundle(lem) if lem else None
        if prof is None:
            return UNKNOWN
        ctx = context_vector_masked(" ".join(toks), lem, d=CTX_D)
        a, b = np.linalg.norm(prof), np.linalg.norm(ctx)
        if a <= 0 or b <= 0:
            return UNKNOWN
        return -float(np.dot(prof, ctx) / (a * b))

    def definitional(toks, i):
        w = _lem(toks[i])
        d = defs.get(w)
        if not d:
            return None                      # signals "no definition", NOT a score
        ctx = collections.Counter(content_lemmas(" ".join(toks)))
        ctx.pop(w, None)
        if not ctx:
            return None
        num = sum(d[k] * ctx[k] for k in set(d) & set(ctx))
        den = (math.sqrt(sum(v * v for v in d.values()))
               * math.sqrt(sum(v * v for v in ctx.values()))) or 1.0
        return -float(num / den)

    # **THE TWO SCALES ARE NOT COMPARABLE**, so the hybrid cannot just pick whichever number is
    # available -- a cosine over PPMI counts and a cosine over bundled bipolar codes have different
    # spreads, and mixing them per-word would make the RANKING depend on which route fired rather
    # than on how anomalous the word is. That is the same defect as the unknown-word sentinel of
    # 0.0 that once outranked every real score. So each route is z-scored WITHIN the sentence
    # before the choice is made, which puts both on a common per-item scale.
    def hybrid(toks, i):
        cand = [j for j in range(len(toks)) if _lem(toks[j])]
        dv = [definitional(toks, j) for j in cand]
        if definitional(toks, i) is None:
            return distributional(toks, i)
        have = [v for v in dv if v is not None]
        if len(have) < 2:
            return distributional(toks, i)
        mu, sd = float(np.mean(have)), float(np.std(have)) or 1.0
        return (definitional(toks, i) - mu) / sd

    print("\nARM: definition where available, distributional profile otherwise.")
    print("Reference: distributional alone +16.3 pp; counting +29.4 (bar +44.2).\n")
    hy = score_across_sets(hybrid, SETS, name="HYBRID")
    print("")
    di = score_across_sets(distributional, SETS, name="DISTRIBUTIONAL")
    print("\nPAIRED, same items -- overlapping marginal CIs are not a test of a difference:")
    compare_detectors_paired(hybrid, distributional, SETS, name_a="HYBRID", name_b="DISTRIB")
    print("\n" + "=" * 80)
    print("HYBRID        %s  median %+.1f" % (", ".join("%+.1f" % e for e in hy["effects"]),
                                              float(np.median(hy["effects"]))))
    print("DISTRIBUTIONAL %s  median %+.1f" % (", ".join("%+.1f" % e for e in di["effects"]),
                                               float(np.median(di["effects"]))))
    print("**Read against COVERAGE: definitions exist for only 24.6% of the words, so this bounds")
    print("how much they could possibly add -- a null here is 'nothing at THIS coverage'.**")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
