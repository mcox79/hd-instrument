"""Does `np.sign()` on the QUERY destroy our forgetting exponent? -- the one-line sleep experiment.

**THE HYPOTHESIS, from the 2026-08-14 drill's own analysis (flagged there as analysis, not
literature).** Benna & Fusi's whole achievement is reaching `SNR ~ t^-1/2` with **BOUNDED**
variables; an **unbounded perfect integrator already gets the same exponent for free**. And
`ConceptSpace.observe` does `self._sums[lemma] += ctx_vec` -- **exactly that integrator**. If a
hard 1-bit quantiser is applied before use, a bounded-variance `t^-1/2` system becomes a saturating
one. **So our forgetting exponent may not be absent; it may be destroyed by the `sign()`.**

**DISK-VERIFIED 2026-08-21, and the drill is half stale:** anchors are now GRADED
(`GRADED_COMPARATOR` defaults ON since 2026-08-14), but **the QUERY at
`reading_grounding_loop.py:776` is `new_bundle = np.sign(new_raw_sum)`, UNCONDITIONAL.** Half the
quantiser was already removed. This measures the half that remains.

**THE MEASURAND IS THE SHAPE, NOT THE LEVEL.** `SNR(t)` of a specific stored trace as `t` new
content arrives, plotted log-log. **Naive/saturating -> CURVED. A `t^-1/2` system -> a STRAIGHT LINE
of slope -1/2.** *We are fitting a slope, not comparing scores.*

*** THE CONFOUND, AND THE FLOOR THAT EXPOSES IT ***
**A SYSTEM THAT LEARNS LESS FORGETS LESS.** Retention is trivially maximised by not learning, and
this project has twice been fooled by that exact shape (an all-zero accumulator scored median rank
1.0; 10-sparse noise beat a real arm). **So a FROZEN arm is included as a floor: it must show the
BEST retention and FAIL acquisition.** If it does not, the metric cannot expose the cheat and no
number from it means anything. **Acquisition is reported beside retention, always.**

⚠️ **THE TIME AXIS IS NOT THEIRS.** Benna-Fusi's `t` is *memories stored at this synapse*; ours is
*content ingested*. Stated because the fitted slope otherwise describes a different quantity.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import math  # noqa: E402
import sys  # noqa: E402

import numpy as np  # noqa: E402

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for _p in (_REPO, os.path.join(_REPO, "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from memory_guard import guard  # noqa: E402
_MEM = guard(limit_gb=2.0, label=os.path.basename(__file__))

N_A = int(os.environ.get("DIAG_N_A", "600"))        # sentences forming set A (the memory)
N_STREAM = int(os.environ.get("DIAG_N_STREAM", "7000"))
N_B = int(os.environ.get("DIAG_N_B", "600"))        # set B -- the ACQUISITION probe


def snr(profiles, memories, terms, quantise):
    """SNR of each stored trace against the spread over unrelated traces.

    signal_i = cos(profile_i, memory_i); noise = sd over cos(profile_j, memory_i), j != i.
    Returns mean (signal - mean_off) / sd_off. This is the literature's own definition shape."""
    P = []
    for t in terms:
        v = profiles.get(t)
        if v is None:
            return None
        v = np.sign(v) if quantise else v
        n = np.linalg.norm(v)
        P.append(v / n if n > 0 else v)
    P = np.stack(P)
    M = np.stack([memories[t] / (np.linalg.norm(memories[t]) or 1.0) for t in terms])
    C = P @ M.T                                  # C[i, j] = cos(profile_i, memory_j)
    sig = np.diag(C)
    off = C[~np.eye(len(terms), dtype=bool)]
    sd = float(off.std()) or 1e-12
    return float((sig.mean() - off.mean()) / sd)


def main():
    from hdlab.corpus_registry import CorpusRegistry
    from hdlab.reading_grounding_loop import (
        CTX_D,
        ConceptSpace,
        content_lemmas,
        context_vector_masked,
    )

    reg = CorpusRegistry()
    h = reg.handles["simplewiki"]
    setA = list(h.take(N_A))
    stream = list(h.take(N_STREAM))
    setB = list(h.take(N_B))
    print("SET A %d sentences | STREAM %d | SET B %d (acquisition probe)"
          % (len(setA), len(stream), len(setB)))

    space = ConceptSpace(d=CTX_D)
    memories = {}
    for s in setA:
        for lem in content_lemmas(s):
            v = context_vector_masked(s, lem, d=CTX_D)
            space.observe(lem, v)
            if lem not in memories:
                memories[lem] = v.astype(np.float64).copy()   # THE trace we will track
    terms = [t for t in memories if space.bundle(t) is not None]
    terms = sorted(terms)[:400]
    print("tracking %d stored traces" % len(terms))

    frozen = {t: space.bundle(t).copy() for t in terms}       # the CHEAT arm: stops here

    checkpoints = [1]
    while checkpoints[-1] * 2 <= len(stream):
        checkpoints.append(checkpoints[-1] * 2)
    rows, seen = [], 0
    for k, s in enumerate(stream):
        _MEM()
        for lem in content_lemmas(s):
            space.observe(lem, context_vector_masked(s, lem, d=CTX_D))
        seen += 1
        if seen in checkpoints:
            live = {t: space.bundle(t) for t in terms}
            rows.append((seen,
                         snr(live, memories, terms, quantise=False),
                         snr(live, memories, terms, quantise=True),
                         snr(frozen, memories, terms, quantise=False)))
    print("\n%8s %12s %12s %12s" % ("t", "GRADED", "SIGN()", "FROZEN"))
    print("-" * 48)
    for t, g, q, f in rows:
        print("%8d %12.4f %12.4f %12.4f" % (t, g, q, f))

    def slope(xs, ys):
        xs = np.log([x for x, y in zip(xs, ys) if y and y > 0])
        ys = np.log([y for y in ys if y and y > 0])
        if len(xs) < 3:
            return None, None
        A = np.vstack([xs, np.ones(len(xs))]).T
        m, c = np.linalg.lstsq(A, ys, rcond=None)[0]
        resid = ys - (m * xs + c)
        return float(m), float(np.sqrt((resid ** 2).mean()))

    T = [r[0] for r in rows]
    print("\n%-10s %10s %10s   (log-log fit; a t^-1/2 system reads -0.50)" % ("arm", "slope", "rms"))
    for name, idx in (("GRADED", 1), ("SIGN()", 2), ("FROZEN", 3)):
        m, r = slope(T, [x[idx] for x in rows])
        print("  %-8s %10s %10s" % (name, "%.3f" % m if m is not None else "n/a",
                                    "%.4f" % r if r is not None else "n/a"))

    # ---- ACQUISITION: does the arm still LEARN? The frozen arm must FAIL this.
    newlem = set()
    for s in setB:
        newlem |= set(content_lemmas(s))
    fresh = sorted(x for x in newlem if x not in memories)[:200]
    for s in setB:
        for lem in content_lemmas(s):
            space.observe(lem, context_vector_masked(s, lem, d=CTX_D))
    learned = sum(1 for t in fresh if space.bundle(t) is not None
                  and float(np.linalg.norm(space.bundle(t))) > 0)
    print("\nACQUISITION on %d words unseen at t=0:" % len(fresh))
    print("  LIVE arms  : %d of %d acquired (%.0f%%)" % (learned, len(fresh),
                                                         100.0 * learned / max(1, len(fresh))))
    print("  FROZEN arm : 0 of %d acquired (0%%) -- BY CONSTRUCTION, it stopped accumulating" % len(fresh))
    print("\n*** READ RETENTION AND ACQUISITION TOGETHER. ***")
    print("If FROZEN shows the best retention and zero acquisition, the metric CAN expose the")
    print("learn-less-forget-less cheat -- which is what makes the other two columns readable.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
