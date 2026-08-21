"""What does the substrate score on this task **AS IT ACTUALLY RUNS** -- trained, not untrained?

**THE DECISIVE MEASUREMENT FOR THE F5 DECISION, AND NOTHING HAS DONE IT.** Two reference points now
exist: the untrained codebook scores **0 pp** (it donates nothing) and counting scores up to
**+44.2 pp**. **The substrate's own learned representation has never been placed between them.**

- **If it scores ~0** -- the learned profiles carry no anomaly signal at all, and F5 would have to
  supply the entire capability rather than read one out of what is already there.
- **If it scores well above 0** -- this is the first positive signal from our side on this task, and
  it tells us what F5 would be building ON rather than replacing.

**THE ARM IS THE SUBSTRATE'S OWN COMPARISON, NOT A NEW MECHANISM.** `ConceptSpace.observe` is fed
exactly what the reading loop feeds it -- the RAW `context_vector_masked` per occurrence, matching
the accumulation line in the source (adding a UNIT vector instead made a practice arm 1/44th of a
real read and produced a zero-width CI). The detector then compares a word's accumulated profile
against its sentence context, which is the same cosine `canonicalize` decides on.

**LEAK CONTROL IS MANDATORY AND IS PRINTED.** The items were drawn from this corpus, so every item
sentence is excluded from the reading pass; without it a word's profile would contain the very
sentence it is about to be scored in.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import json  # noqa: E402
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


def main():
    from f5_evaluation_harness import (DiagnosticFailure, compare_detectors_paired,
                                       score_across_sets)

    from hdlab.corpus_registry import CorpusRegistry
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
    print("LEAK CONTROL: %d of %d read sentences excluded because they ARE item sentences (%d read)"
          % (len(raw) - len(sents), len(raw), len(sents)))
    if len(raw) == len(sents):
        print("  !! the exclusion removed NOTHING -- a broken control, not a clean one")

    space = ConceptSpace(d=CTX_D)
    for k, s in enumerate(sents):
        for lem in content_lemmas(s):
            # ADD WHAT THE SYSTEM ADDS: the RAW masked context vector, exactly as the reading loop
            # accumulates it. Normalising here would make each read 1/44th of a real one.
            space.observe(lem, context_vector_masked(s, lem, d=CTX_D))
        if (k + 1) % 2000 == 0:
            print("  read %d/%d, %d anchors" % (k + 1, len(sents), len(space.anchors())), flush=True)
    anchors = space.anchors()
    norms = [float(np.linalg.norm(space.bundle(a))) for a in anchors[:2000]]
    print("TRAINED: %d anchors, mean profile norm %.1f (a norm near 0 would mean nothing accumulated)"
          % (len(anchors), float(np.mean(norms)) if norms else 0.0))

    def detector(toks, i):
        """HIGHER = more anomalous: NEGATIVE cosine between the word's ACCUMULATED profile and the
        context vector of the sentence it is sitting in. This is the substrate's own comparison."""
        lem = normalize_lemma("".join(c for c in toks[i].lower() if c.isalpha()))
        prof = space.bundle(lem) if lem else None
        if prof is None:
            return -1e9
        ctx = context_vector_masked(" ".join(toks), lem, d=CTX_D)
        np_, nc = np.linalg.norm(prof), np.linalg.norm(ctx)
        if np_ <= 0 or nc <= 0:
            return -1e9
        return -float(np.dot(prof, ctx) / (np_ * nc))

    print("\nARM: the substrate's LEARNED profiles. Reference points: untrained codebook 0 pp,")
    print("counting up to +44.2 pp.\n")
    try:
        out = score_across_sets(detector, SETS, name="TRAINED_SUBSTRATE")
    except DiagnosticFailure as e:
        print("\nHARNESS REFUSED TO SCORE IT, and that is a legitimate answer:\n  %s" % e)
        return 0
    eff = out["effects"]
    print("\n" + "=" * 78)
    print("SUBSTRATE (trained): %s  median %+.1f pp" % (
        ", ".join("%+.1f" % e for e in eff), float(np.median(eff))))
    print("  vs untrained codebook 0 pp   vs counting up to +44.2 pp")
    print("**A margin over the UNTRAINED arm is what learning bought; a margin over COUNTING is what")
    print("the substrate is worth. They are different questions and both are reported.**")
    print("=" * 78)

    # ---- THE PAIRED TEST, which is the only thing that can say "behind" rather than "not ahead"
    import collections as _c
    import math as _m
    df, co, nd = _c.Counter(), _c.defaultdict(_c.Counter), 0
    for s in sents:
        _MEM()
        u = set(content_lemmas(s)); nd += 1; df.update(u)
        for w in u:
            co[w].update(u)
    _pc = {}

    def prof2(w):
        v = _pc.get(w)
        if v is None:
            pw = df[w] / nd if df.get(w) else 0.0
            v = {}
            if pw > 0:
                for c, j in co[w].items():
                    if c == w:
                        continue
                    pc_ = df[c] / nd
                    if pc_ > 0 and j > 0:
                        p = _m.log((j / nd) / (pw * pc_))
                        if p > 0:
                            v[c] = p
            nrm = _m.sqrt(sum(x * x for x in v.values())) or 1.0
            v = {k: x / nrm for k, x in v.items()}
            _pc[w] = v
        return v

    def counting(toks, i):
        """SECOND-ORDER counting, the strongest floor -- same corpus, same leak control."""
        vw = prof2(normalize_lemma("".join(c for c in toks[i].lower() if c.isalpha())))
        if not vw:
            return -1e9
        out = []
        for j, t in enumerate(toks):
            if j == i:
                continue
            vc = prof2(normalize_lemma("".join(c for c in t.lower() if c.isalpha())))
            if not vc:
                continue
            a, b = (vw, vc) if len(vw) < len(vc) else (vc, vw)
            out.append(sum(x * b.get(k, 0.0) for k, x in a.items()))
        return -float(np.mean(out)) if out else -1e9

    print("")
    print("PAIRED SUBSTRATE vs SECOND-ORDER COUNTING -- same items, same slots, same corpus.")
    print("Two overlapping CIs from separate runs are NOT a test of a difference; this is.")
    compare_detectors_paired(detector, counting, SETS,
                             name_a="SUBSTRATE", name_b="COUNTING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
