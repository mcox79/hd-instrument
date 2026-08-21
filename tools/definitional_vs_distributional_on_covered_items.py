"""On the items where BOTH words HAVE a definition, is the definitional route better or worse?

**THE ONE MEASUREMENT THAT SEPARATES TWO EXPLANATIONS THE HYBRID RUN COULD NOT.** That run found
`HYBRID - DISTRIBUTIONAL = -0.107 per item, CI [-0.144, -0.069]` -- substituting a definition where
one exists made things worse. **But the hybrid z-scores the definitional route within each sentence
to put two differently-scaled cosines on a common footing, and THAT Z-SCORE IS MY INVENTION**,
sitting exactly where the damage would show.

| reading | consequence |
|---|---|
| the definitions genuinely predict context worse | a finding about the EXTRACTOR; Angle B's filter is wrong |
| my per-sentence z-score mixes scales badly | a finding about MY GLUE; the question stays open |

**SO: NO MIXING AND NO Z-SCORE HERE.** Each arm is scored alone, on the SAME restricted item set --
those where **both** the correct word and the intruder have an extracted definition -- so nothing of
mine sits between the two arms and the comparison is like-for-like.

⚠️ **n IS SMALL BY CONSTRUCTION (~48 items).** That is not a flaw in the design, it is the coverage
(24.6% of words have a definition) meeting a paired requirement. **A null here means UNRESOLVED at
this n, never "the two are equal"** -- the distinction this project has paid for repeatedly.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import collections  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import random  # noqa: E402
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
    from f5_evaluation_harness import _content, _word
    from rank_with_ties import rank_with_ties

    from hdlab.corpus_registry import CorpusRegistry
    from hdlab.definitional_extraction import extract_from_sentences
    from hdlab.reading_grounding_loop import (
        CTX_D,
        ConceptSpace,
        content_lemmas,
        context_vector_masked,
        normalize_lemma,
    )

    items_all, held = [], set()
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
        bag = collections.Counter()
        for d in ds:
            bag.update(getattr(d, "definiens_lemmas", []) or [])
        if bag:
            defs.setdefault(normalize_lemma(str(term).lower()), collections.Counter()).update(bag)
    space = ConceptSpace(d=CTX_D)
    for k, s in enumerate(sents):
        for lem in content_lemmas(s):
            space.observe(lem, context_vector_masked(s, lem, d=CTX_D))
        if (k + 1) % 2500 == 0:
            print("  read %d/%d" % (k + 1, len(sents)), flush=True)

    def _lem(t):
        return normalize_lemma(_word(t))

    def distributional(toks, i):
        lem = _lem(toks[i])
        prof = space.bundle(lem) if lem else None
        if prof is None:
            return UNKNOWN
        ctx = context_vector_masked(" ".join(toks), lem, d=CTX_D)
        a, b = np.linalg.norm(prof), np.linalg.norm(ctx)
        return UNKNOWN if a <= 0 or b <= 0 else -float(np.dot(prof, ctx) / (a * b))

    def definitional(toks, i):
        w = _lem(toks[i])
        d = defs.get(w)
        if not d:
            return UNKNOWN
        ctx = collections.Counter(content_lemmas(" ".join(toks)))
        ctx.pop(w, None)
        if not ctx:
            return UNKNOWN
        num = sum(d[k] * ctx[k] for k in set(d) & set(ctx))
        den = (math.sqrt(sum(v * v for v in d.values()))
               * math.sqrt(sum(v * v for v in ctx.values()))) or 1.0
        return -float(num / den)

    covered = [it for it in items_all
               if normalize_lemma(it["target"]) in defs and normalize_lemma(it["intruder"]) in defs]
    print("\nCOVERED ITEMS (both words have a definition): %d of %d (%.1f%%)"
          % (len(covered), len(items_all), 100.0 * len(covered) / len(items_all)))
    if len(covered) < 20:
        print("fewer than 20 -- refusing to score")
        return 1

    def disc(det):
        """paired (anom hit@1) - (orig hit@1), per item, on the covered set."""
        per = []
        for it in covered:
            row = {}
            for field in ("sentence_anomalous", "sentence_original"):
                toks = it[field].split()
                cand = sorted({j for j, t in enumerate(toks) if _word(t) in _content}
                              | {it["anomaly_token_index"]})
                if len(cand) < 3:
                    row = None
                    break
                sc = [float(det(toks, j)) for j in cand]
                r = rank_with_ties(sc, cand.index(it["anomaly_token_index"]))
                row[field] = int(r.pessimistic == 1)
            if row:
                per.append(row["sentence_anomalous"] - row["sentence_original"])
        return per

    dfn, dst = disc(definitional), disc(distributional)
    n = min(len(dfn), len(dst))
    dfn, dst = dfn[:n], dst[:n]
    rng = random.Random(31)

    def ci(v):
        b = [float(np.mean([v[rng.randrange(len(v))] for _ in v])) for _ in range(20000)]
        return float(np.mean(v)), float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))

    print("\n" + "=" * 82)
    print("SCORED ALONE ON THE SAME %d ITEMS -- no mixing, no z-score" % n)
    print("=" * 82)
    for name, v in (("DEFINITIONAL", dfn), ("DISTRIBUTIONAL", dst)):
        m, lo, hi = ci(v)
        print("  %-15s discrimination %+0.3f per item, 95%% CI [%+0.3f, %+0.3f]" % (name, m, lo, hi))
    pair = [a - b for a, b in zip(dfn, dst)]
    m, lo, hi = ci(pair)
    print("\n  PAIRED  DEFINITIONAL - DISTRIBUTIONAL = %+0.3f per item, 95%% CI [%+0.3f, %+0.3f]"
          % (m, lo, hi))
    print("\n" + "=" * 82)
    if lo > 0 or hi < 0:
        who = "DEFINITIONAL is WORSE" if m < 0 else "DEFINITIONAL is BETTER"
        print("SEPARATED: %s on the items where both routes fire." % who)
        print("-> The hybrid's loss is attributable to the DEFINITIONS, not only to my z-score glue.")
    else:
        print("NOT SEPARATED at n=%d. **This is UNRESOLVED, not 'the two are equal'.**" % n)
        print("-> The hybrid's loss CANNOT be attributed to the definitions from this evidence, and")
        print("   my per-sentence z-score remains a live explanation for it. Both stay open.")
    print("=" * 82)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
