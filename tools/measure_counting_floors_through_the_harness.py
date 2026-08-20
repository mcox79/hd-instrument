"""Measure BOTH counting floors through `f5_evaluation_harness`, and set the bar from the stronger.

**THE BAR MUST BE MEASURED WITH THE SAME INSTRUMENT THE CANDIDATE WILL BE.** Earlier floor numbers
came from a separate scorer, and when a lookup bug was fixed in one of them the bar moved twice.
Running both floors through the harness the F5 cell will use removes that whole class of mismatch.

**THE LOOKUP BUG, RECORDED BECAUSE IT MOVED EVERY NUMBER.** `docfreq`/`cooc` are keyed by
`content_lemmas` output, so a SURFACE lookup misses every inflected form -- `achievements` absent,
`achievement` present. Inflected words were silently dropped from the candidate slate, and any that
survived scored the unknown-word sentinel and outranked real candidates. **Fixing it moved
second-order counting from +10.9 pp to +28.3 pp and dropped its ORIGINAL-sentence hit rate from
42.6% to 12.5%, so the earlier "most of the floor's skill is a slot effect" reading was largely an
artifact of this bug.** Look up what the table is keyed by.
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
UNKNOWN = -1e9   # NOT 0.0: under higher-is-more-anomalous, 0.0 outranks every real (negative) score


def main():
    from f5_evaluation_harness import score_across_sets

    from hdlab.corpus_registry import CorpusRegistry
    from hdlab.reading_grounding_loop import content_lemmas, normalize_lemma

    held = set()
    for p in SETS:
        held |= {i["sentence_original"] for i in json.load(open(p, encoding="utf-8"))["items"]}
    sents = [s for s in CorpusRegistry().handles["simplewiki"].take(8000) if s not in held]
    print("LEAK CONTROL: %d corpus sentences after excluding EVERY set's item sentences" % len(sents))

    df, co, n = collections.Counter(), collections.defaultdict(collections.Counter), 0
    for s in sents:
        u = set(content_lemmas(s))
        n += 1
        df.update(u)
        for w in u:
            co[w].update(u)

    def lem(t):
        return normalize_lemma("".join(c for c in t.lower() if c.isalpha()))

    cache = {}

    def prof(w):
        v = cache.get(w)
        if v is None:
            pw = df[w] / n if df.get(w) else 0.0
            v = {}
            if pw > 0:
                for c, j in co[w].items():
                    if c == w:
                        continue
                    pc = df[c] / n
                    if pc > 0 and j > 0:
                        p = math.log((j / n) / (pw * pc))
                        if p > 0:
                            v[c] = p
            nrm = math.sqrt(sum(x * x for x in v.values())) or 1.0
            v = {k: x / nrm for k, x in v.items()}
            cache[w] = v
        return v

    def first_order(toks, i):
        w = lem(toks[i])
        if not df.get(w):
            return UNKNOWN
        pw, vals = df[w] / n, []
        for j, t in enumerate(toks):
            if j == i:
                continue
            c = lem(t)
            if not df.get(c):
                continue
            pj = co[w][c] / n
            vals.append(math.log(pj / (pw * (df[c] / n))) if pj > 0 else -8.0)
        return -float(np.mean(vals)) if vals else UNKNOWN

    def second_order(toks, i):
        vw = prof(lem(toks[i]))
        if not vw:
            return UNKNOWN
        out = []
        for j, t in enumerate(toks):
            if j == i:
                continue
            vc = prof(lem(t))
            if not vc:
                continue
            a, b = (vw, vc) if len(vw) < len(vc) else (vc, vw)
            out.append(sum(x * b.get(k, 0.0) for k, x in a.items()))
        return -float(np.mean(out)) if out else UNKNOWN

    print("\n===== FIRST-ORDER CO-OCCURRENCE =====")
    a = score_across_sets(first_order, SETS, name="FIRST_ORDER")
    print("\n===== SECOND-ORDER CO-OCCURRENCE =====")
    b = score_across_sets(second_order, SETS, name="SECOND_ORDER")
    ubs = [r["ci"][1] for r in a["per_set"]] + [r["ci"][1] for r in b["per_set"]]
    print("\n" + "=" * 78)
    print("THE BAR = max per-set CI UPPER bound across BOTH counting floors = %+.1f pp" % max(ubs))
    print("(gate on the floor's UPPER bound, never its point value -- standing rule)")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
