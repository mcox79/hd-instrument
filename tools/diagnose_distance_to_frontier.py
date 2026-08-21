"""Is a GRADED distance-to-the-frontier computable from what we already have? Measured, not assumed.

WHY. The owner asked for *"the ~distance from any new fact to the grounded foundation"*. The organ
we built answers YES/NO instead: `is_gap` agrees with plain anchor membership on 237 of 240 probes,
and its `margin` is pinned at exactly 1.0 for every known word. **There is no gradation to rank by.**

WHY NOT JUST USE VECTOR SIMILARITY. An UNREAD word has no learned vector -- `symbol_vector()` is a
hash-seeded random draw, so its similarity to any anchor is noise. **Distance for a word we have not
read cannot come from the word's own representation. It has to come from the company it keeps.**

THE CANDIDATE MEASURE, which is `MEMORY.md`'s own relational-bridge idea made concrete:

    grounded_neighbour_fraction(w) = |{c in co-occurring(w) : c is anchored}| / |co-occurring(w)|

**NEAR the frontier = most of the words it appears alongside are already understood** -> reading it
now would land. **FAR = it sits among other unknowns** -> reading it now is wasted. *That is the ZPD
ordering, and it needs nothing we do not already have.*

WHAT WOULD KILL IT, checked here rather than after a build:
  * the distribution is DEGENERATE (one or two values) -> no ordering, same failure as `margin`;
  * it is identical to plain co-occurrence COUNT -> a counter wearing a new name;
  * known and unknown words are indistinguishable on it -> it measures nothing.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")

import collections  # noqa: E402
import csv  # noqa: E402
import statistics as S  # noqa: E402
import sys  # noqa: E402

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

N_SENT = int(os.environ.get("DIAG_N_SENT", "6000"))


def main():
    from hdlab.corpus_registry import CorpusRegistry
    from hdlab import foundation_persistence as fp
    from hdlab.reading_grounding_loop import content_lemmas

    st = fp.load_foundation("data/foundation/reading_grounding_v1")
    anchors = set(st.space.anchors())
    print("anchors in foundation: %d" % len(anchors))

    reg = CorpusRegistry()
    h = reg.handles.get("simplewiki")
    sents = list(h.take(N_SENT))
    cooc = collections.defaultdict(set)
    for s in sents:
        ls = set(content_lemmas(s))
        for w in ls:
            cooc[w] |= (ls - {w})
    print("lemmas with co-occurrence context: %d (from %d sentences)" % (len(cooc), len(sents)))

    def gnf(w):
        ns = cooc.get(w) or set()
        if len(ns) < 3:
            return None
        return sum(1 for c in ns if c in anchors) / len(ns)

    rows = list(csv.DictReader(open(
        "data/corpora/base_vocabulary/cleaned/base_vocabulary_ordered.csv", encoding="utf-8")))
    vocab = [r["word"] for r in rows[:6000] if r["word"].isalpha() and len(r["word"]) > 2]
    known = [w for w in vocab if w in anchors]
    unknown = [w for w in vocab if w not in anchors]

    kv = [x for x in (gnf(w) for w in known) if x is not None]
    uv = [x for x in (gnf(w) for w in unknown) if x is not None]
    if len(uv) < 30:
        print("too few scorable unknown words (%d) -- UNDERPOWERED" % len(uv))
        return 1

    print("\n" + "=" * 76)
    print("IS IT GRADED? (the failure that killed `margin` was ONE distinct value)")
    print("=" * 76)
    for nm, v in (("KNOWN words", kv), ("UNKNOWN words", uv)):
        print("  %-14s n=%-5d distinct=%-5d min %.3f  p25 %.3f  med %.3f  p75 %.3f  max %.3f"
              % (nm, len(v), len(set(round(x, 4) for x in v)), min(v),
                 sorted(v)[len(v) // 4], S.median(v), sorted(v)[3 * len(v) // 4], max(v)))

    print("\n" + "=" * 76)
    print("DOES IT ORDER THE UNKNOWNS? -- the whole point: which to read FIRST")
    print("=" * 76)
    scored = sorted(((gnf(w), w) for w in unknown if gnf(w) is not None), reverse=True)
    print("  NEAREST the frontier (read these first):")
    for sc, w in scored[:8]:
        print("      %.3f  %s" % (sc, w))
    print("  FARTHEST (not ready):")
    for sc, w in scored[-8:]:
        print("      %.3f  %s" % (sc, w))

    # IS IT JUST A COUNT? the control that matters -- a counter wearing a new name
    cnt = [len(cooc[w]) for _, w in scored]
    frac = [s_ for s_, _ in scored]
    n = len(frac)
    mc, mf = sum(cnt) / n, sum(frac) / n
    num = sum((cnt[i] - mc) * (frac[i] - mf) for i in range(n))
    den = (sum((c - mc) ** 2 for c in cnt) ** 0.5) * (sum((f - mf) ** 2 for f in frac) ** 0.5)
    print("\n  CONTROL -- correlation with plain neighbour COUNT: r = %.3f" % (num / den if den else 0.0))
    print("  (near +/-1 would mean this is co-occurrence count in disguise)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
