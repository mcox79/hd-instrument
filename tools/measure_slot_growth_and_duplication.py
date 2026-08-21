"""Does the concept space grow without bound, and does it hold DUPLICATES? -- the owner's middle clause.

**OWNER, COMMENTARY 2026-08-21:** *"We'll still want a consolidation function so we're not
duplicating things, but we should never throw out useful information."*

**TWO OF THE THREE CLAUSES ARE ALREADY BUILT** -- the three-tier architecture is proven and
`prelim_tier`'s docstring opens with *"retain-forever"*. **The middle clause, consolidation, is the
one with no implementation.** *And I asserted last turn that retain-forever without dedup means
unbounded growth. That was an assertion. This measures it.*

**TWO QUESTIONS, AND THEY HAVE DIFFERENT ANSWERS:**

1. **Does slot COUNT grow without bound?** Plot distinct lemmas against sentences read. *Vocabulary
   growth is expected to be sublinear -- Heaps' law -- so "it grows" is NOT the finding. The finding
   is whether it SATURATES or keeps climbing at the scale we actually read at.*
2. **Do distinct slots hold the SAME CONTENT?** That is what "duplicating things" means
   operationally: two different lemmas whose accumulated profiles are near-identical. **If there are
   none, consolidation has nothing to consolidate and the owner's middle clause is already
   satisfied by accident.**

⚠️ **THE TRAP, AND IT IS THE ONE THIS PROJECT KEEPS FALLING INTO.** Near-identical profiles are
**expected** for genuinely synonymous or morphologically related words, and for RARE words whose
profiles are built from one or two contexts. **A rare-word pair at cos 0.99 is not a duplicate, it
is an undersampled pair.** So duplication is reported **stratified by frequency**, and the
comparison is against a **frequency-matched null**, never against zero.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import collections  # noqa: E402
import random  # noqa: E402
import sys  # noqa: E402

import numpy as np  # noqa: E402

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for _p in (_REPO, os.path.join(_REPO, "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

N_READ = int(os.environ.get("DIAG_N_READ", "8000"))


def main():
    from hdlab.corpus_registry import CorpusRegistry
    from hdlab.reading_grounding_loop import (
        CTX_D,
        ConceptSpace,
        content_lemmas,
        context_vector_masked,
    )

    sents = list(CorpusRegistry().handles["simplewiki"].take(N_READ))
    space = ConceptSpace(d=CTX_D)
    freq = collections.Counter()
    marks, growth = [], []
    k = 1
    while k <= len(sents):
        marks.append(k)
        k *= 2
    for i, s in enumerate(sents, 1):
        for lem in content_lemmas(s):
            space.observe(lem, context_vector_masked(s, lem, d=CTX_D))
            freq[lem] += 1
        if i in marks:
            growth.append((i, len(space.anchors())))

    print("=" * 78)
    print("1. SLOT GROWTH -- does the concept space saturate?")
    print("=" * 78)
    print("%10s %10s %12s" % ("sentences", "slots", "slots/sent"))
    for n, a in growth:
        print("%10d %10d %12.3f" % (n, a, a / n))
    if len(growth) >= 3:
        (n1, a1), (n2, a2) = growth[-3], growth[-1]
        import math
        beta = math.log(a2 / a1) / math.log(n2 / n1)
        print("\n  Heaps exponent over the last stretch: beta = %.3f" % beta)
        print("  (beta ~ 0.4-0.6 is ordinary vocabulary growth; beta -> 0 means SATURATING;")
        print("   beta ~ 1 would mean every sentence brings a brand-new concept.)")
        print("  -> %s" % ("SATURATING" if beta < 0.25 else
                           "still climbing, sublinear -- ORDINARY, not pathological"
                           if beta < 0.75 else "CLIMBING NEAR-LINEARLY -- pathological"))

    # ---- 2. duplication, stratified, against a frequency-matched null
    print("\n" + "=" * 78)
    print("2. DUPLICATION -- do DIFFERENT slots hold the SAME content?")
    print("=" * 78)
    anchors = space.anchors()
    bands = {"rare (1-2)": [], "mid (3-9)": [], "common (10+)": []}
    for a in anchors:
        f = freq[a]
        band = "rare (1-2)" if f <= 2 else "mid (3-9)" if f <= 9 else "common (10+)"
        bands[band].append(a)
    rng = random.Random(7)
    print("%-14s %7s %10s %10s %10s %12s" % ("band", "n", "med cos", "p95 cos", ">0.90", "null p95"))
    for band, terms in bands.items():
        if len(terms) < 40:
            print("%-14s %7d   (too few to sample)" % (band, len(terms)))
            continue
        sample = rng.sample(terms, min(300, len(terms)))
        V = []
        for t in sample:
            v = space.bundle(t).astype(np.float64)
            n = np.linalg.norm(v)
            V.append(v / n if n > 0 else v)
        V = np.stack(V)
        C = V @ V.T
        off = C[~np.eye(len(sample), dtype=bool)]
        # frequency-matched null: SHUFFLE each profile's components, destroying content
        # but preserving the magnitude spectrum that frequency induces.
        W = np.stack([rng.sample(list(v), len(v)) for v in V])
        W = W / (np.linalg.norm(W, axis=1, keepdims=True) + 1e-12)
        Cn = W @ W.T
        offn = Cn[~np.eye(len(sample), dtype=bool)]
        print("%-14s %7d %10.3f %10.3f %9.2f%% %12.3f"
              % (band, len(terms), float(np.median(off)), float(np.percentile(off, 95)),
                 100.0 * float((off > 0.90).mean()), float(np.percentile(offn, 95))))

    print("\n**READ THE `>0.90` COLUMN AGAINST `null p95`, NEVER AGAINST ZERO.** A rare-word pair at")
    print("cos 0.99 is an UNDERSAMPLED pair, not a duplicate -- which is why this is stratified.")
    print("If duplication sits at the null in every band, CONSOLIDATION HAS NOTHING TO CONSOLIDATE")
    print("and the owner's middle clause is already satisfied -- by accident, but satisfied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
