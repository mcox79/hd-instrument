"""What does OUR OWN representation score on this task with **ZERO LEARNING**?

**THIS IS A MANDATORY CONTROL, NOT AN EXPERIMENT.** Standing discipline: *build the
information-free version of your winning arm and score it.* A 10-sparse random arm once beat a real
one at rank 14.0 vs 18.0; an all-zero accumulator once scored median rank 1.0, a twenty-fold "win".
**Any F5 number has to be read against what the SAME representation scores having learned nothing** --
not against zero.

**THE ARM.** `context_vector` bundles hash-seeded bipolar codes for the content words near the
target. With no reading and no accumulation, a word's "profile" is just its OWN hash code. So the
detector is `-cos(symbol_vector(word), context_vector(rest of sentence))`: **how much does this
word's arbitrary random code resemble the arbitrary random codes of its neighbours.** There is no
information in it about English whatsoever.

**WHAT THE ANSWER MEANS.**
- **~0 pp** -- the representation is unbiased, and any F5 discrimination is genuinely earned.
- **MATERIALLY ABOVE 0** -- the geometry itself carries an artifact (length, frequency of the hash
  draw, bundle norm), and **that artifact would be inherited by every arm built on it, F5 included.**
  Finding that BEFORE the build is worth far more than finding it after.

*Uses `tools/f5_evaluation_harness.py`, so this arm is held to exactly the diagnostics and the
paired read-out an F5 candidate will be. If the harness refuses to score it, that is the answer.*
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import sys  # noqa: E402

import numpy as np  # noqa: E402

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for _p in (_REPO, os.path.join(_REPO, "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

SETS = [os.path.join(_REPO, "scratch", "set_%s.json" % s)
        for s in ("20260821", "31415926", "27182818", "16180339")]


def main():
    from f5_evaluation_harness import DiagnosticFailure, score_across_sets

    from hdlab.reading_grounding_loop import (
        CTX_D,
        content_words,
        context_vector,
        normalize_lemma,
        symbol_vector,
    )

    def detector(toks, i):
        """HIGHER = more anomalous. NO READING, NO ACCUMULATION -- the word's own hash code against
        a bundle of its neighbours' hash codes."""
        target = normalize_lemma("".join(c for c in toks[i].lower() if c.isalpha()))
        if not target:
            return -1e9
        rest = [w for j, w in enumerate(toks) if j != i]
        neigh = content_words(" ".join(rest))
        if not neigh:
            return -1e9
        ctx = context_vector(" ".join(neigh), d=CTX_D)
        v = symbol_vector(target, d=CTX_D)
        nv, nc = np.linalg.norm(v), np.linalg.norm(ctx)
        if nv <= 0 or nc <= 0:
            return -1e9
        return -float(np.dot(v, ctx) / (nv * nc))

    print("ARM: untrained substrate geometry -- hash codes only, nothing read, nothing accumulated.")
    print("EXPECTED: ~0 pp. Anything materially above 0 is an artifact of the GEOMETRY that every")
    print("arm built on it would inherit, F5 included.\n")
    try:
        out = score_across_sets(detector, SETS, name="UNTRAINED_GEOMETRY")
    except DiagnosticFailure as e:
        print("\nHARNESS REFUSED TO SCORE IT, and that is a legitimate answer:\n  %s" % e)
        return 0
    eff = out["effects"]
    print("\n" + "=" * 78)
    if max(abs(e) for e in eff) < 5.0:
        print("CLEAN: the untrained geometry carries no anomaly signal (|max| %.1f pp < 5.0)."
              % max(abs(e) for e in eff))
        print("Any F5 discrimination is therefore earned by LEARNING, not donated by the codebook.")
    else:
        print("*** ARTIFACT: the untrained geometry scores %+.1f pp with NOTHING LEARNED. ***"
              % max(eff, key=abs))
        print("Every arm built on this codebook inherits it. An F5 result must be read as a margin")
        print("over THIS, not over zero.")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
