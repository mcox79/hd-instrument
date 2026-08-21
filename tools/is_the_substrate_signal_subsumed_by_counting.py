"""Is the substrate's anomaly signal SUBSUMED by counting, or does it contribute something of its own?

**THE QUESTION THE DAY LEAVES OPEN, AND IT IS DECISION-RELEVANT.** The substrate scores **+16.3 pp**
and counting scores **+29.4 pp**, and the paired test says we are measurably behind. **But "behind"
and "subsumed" are different findings with opposite consequences:**

| | what it means |
|---|---|
| **SUBSUMED** -- the substrate succeeds only where counting already does | we are a **lossy counter**. Building on this representation adds nothing counting does not already have |
| **NOT SUBSUMED** -- there are items only the substrate gets | there is an **independent contribution** to build on, even though the total is smaller |

*This project has run exactly this analysis before and got both answers: the cortical route came back
SUBSUMED (its unique contribution below what independence predicts, at every k), the sensorimotor
spoke came back NOT SUBSUMED (~independent of counting). So the method is established and both
outcomes are live.*

**THE MEASUREMENT.** Per item, on identical sentences and slots, record whether each arm put the
anomalous word first (pessimistic convention, ties against). Then compare the observed overlap with
what **independence** predicts from the two marginal rates. **Reporting only "the substrate has N
unique wins" would be meaningless** -- two arms of any quality have some disagreement by chance.

*** ⚠️ THE DISCRIMINATOR WAS MIS-SPECIFIED IN V1 OF THIS FILE, AND THE PROJECT HAD ALREADY SAID SO. ***
V1 read "substrate-unique BELOW what independence predicts -> SUBSUMED". **The 2026-08-19 spoke
diagnostic had already caught exactly that error, in its own words:** *"I wrote 'materially ABOVE
independence -> complementary; AT OR BELOW -> subsumed', which lumps AT independence together with
BELOW independence. **Those mean OPPOSITE things for buildability.** ... The correct discriminator is
the UNION GAIN."* **Two arms that succeed on DIFFERENT items at chance-overlap rates is precisely the
case where combining pays** -- that is not subsumption, it is complementarity.

**SO THE PRIMARY NUMBER IS `UNION / COUNTING`**, with the ratio reported beside it as secondary.
Reference points from that same diagnostic, on the same discriminator:

| route | ratio | **union gain** | verdict then |
|---|---|---|---|
| cortical read | 0.55 | **1.1x** | SUBSUMED |
| sensorimotor spoke | 0.94 | **2.2x** | a real second channel |

*I built this tool without running the prior-work read on my own project's answer to the same
question. That read is `tools/organ_map_cite.py`'s sibling discipline and it exists because of
exactly this.*
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
    sents = [s for s in CorpusRegistry().handles["simplewiki"].take(N_READ) if s not in held]
    print("LEAK CONTROL: %d sentences read after excluding every item sentence" % len(sents))

    space = ConceptSpace(d=CTX_D)
    df, co, nd = collections.Counter(), collections.defaultdict(collections.Counter), 0
    for k, s in enumerate(sents):
        lems = content_lemmas(s)
        u = set(lems)
        nd += 1
        df.update(u)
        for w in u:
            co[w].update(u)
        for lem in lems:
            space.observe(lem, context_vector_masked(s, lem, d=CTX_D))
        if (k + 1) % 2500 == 0:
            print("  read %d/%d" % (k + 1, len(sents)), flush=True)

    def _lem(t):
        return normalize_lemma(_word(t))

    cache = {}

    def prof2(w):
        v = cache.get(w)
        if v is None:
            pw = df[w] / nd if df.get(w) else 0.0
            v = {}
            if pw > 0:
                for c, j in co[w].items():
                    if c == w:
                        continue
                    pc = df[c] / nd
                    if pc > 0 and j > 0:
                        p = math.log((j / nd) / (pw * pc))
                        if p > 0:
                            v[c] = p
            n = math.sqrt(sum(x * x for x in v.values())) or 1.0
            v = {kk: x / n for kk, x in v.items()}
            cache[w] = v
        return v

    def counting(toks, i):
        vw = prof2(_lem(toks[i]))
        if not vw:
            return UNKNOWN
        out = []
        for j, t in enumerate(toks):
            if j == i:
                continue
            vc = prof2(_lem(t))
            if not vc:
                continue
            a, b = (vw, vc) if len(vw) < len(vc) else (vc, vw)
            out.append(sum(x * b.get(kk, 0.0) for kk, x in a.items()))
        return -float(np.mean(out)) if out else UNKNOWN

    def substrate(toks, i):
        lem = _lem(toks[i])
        prof = space.bundle(lem) if lem else None
        if prof is None:
            return UNKNOWN
        ctx = context_vector_masked(" ".join(toks), lem, d=CTX_D)
        a, b = np.linalg.norm(prof), np.linalg.norm(ctx)
        return UNKNOWN if a <= 0 or b <= 0 else -float(np.dot(prof, ctx) / (a * b))

    def hits(det, field):
        out = []
        for it in items_all:
            toks = it[field].split()
            cand = sorted({j for j, t in enumerate(toks) if _word(t) in _content}
                          | {it["anomaly_token_index"]})
            if len(cand) < 3:
                out.append(None)
                continue
            sc = [float(det(toks, j)) for j in cand]
            r = rank_with_ties(sc, cand.index(it["anomaly_token_index"]))
            out.append(int(r.pessimistic == 1))
        return out

    sa, ca = hits(substrate, "sentence_anomalous"), hits(counting, "sentence_anomalous")
    keep = [i for i in range(len(items_all)) if sa[i] is not None and ca[i] is not None]
    S = [sa[i] for i in keep]
    C = [ca[i] for i in keep]
    n = len(keep)
    both = sum(1 for a, b in zip(S, C) if a and b)
    s_only = sum(1 for a, b in zip(S, C) if a and not b)
    c_only = sum(1 for a, b in zip(S, C) if b and not a)
    neither = n - both - s_only - c_only
    ps, pc = sum(S) / n, sum(C) / n
    exp_both = ps * pc * n
    exp_s_only = ps * (1 - pc) * n

    print("\n" + "=" * 82)
    print("ON THE ANOMALOUS SENTENCES -- did each arm put the planted word FIRST? (n=%d)" % n)
    print("=" * 82)
    print("  substrate hit rate %.3f   counting hit rate %.3f" % (ps, pc))
    print()
    print("                     observed   if INDEPENDENT")
    print("  both arms hit      %8d   %13.1f" % (both, exp_both))
    print("  SUBSTRATE ONLY     %8d   %13.1f   <- the contribution in question" % (s_only, exp_s_only))
    print("  counting only      %8d   %13.1f" % (c_only, pc * (1 - ps) * n))
    print("  neither            %8d   %13.1f" % (neither, (1 - ps) * (1 - pc) * n))

    rng = random.Random(41)
    pairs = list(zip(S, C))
    boot = []
    for _ in range(20000):
        smp = [pairs[rng.randrange(n)] for _ in range(n)]
        a = sum(1 for x, y in smp if x and not y) / n
        p1 = sum(x for x, _ in smp) / n
        p2 = sum(y for _, y in smp) / n
        boot.append(a - p1 * (1 - p2))
    obs = s_only / n - ps * (1 - pc)
    lo, hi = float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))
    print("\n  substrate-unique rate MINUS what independence predicts: %+0.4f, 95%% CI [%+0.4f, %+0.4f]"
          % (obs, lo, hi))
    print("\n" + "=" * 82)
    union = (both + s_only + c_only) / n
    gain = union / pc if pc else float("nan")
    print("")
    print("  *** PRIMARY DISCRIMINATOR -- UNION GAIN (the ratio above is SECONDARY) ***")
    print("     union hit rate %.4f / counting %.4f = **%.2fx**" % (union, pc, gain))
    print("     reference, same discriminator, 2026-08-19: cortical read 1.1x = SUBSUMED;")
    print("     sensorimotor spoke 2.2x = a real second channel.")
    if gain < 1.15:
        print("  -> SUBSUMED by union gain: combining buys almost nothing over counting alone.")
    elif gain < 1.6:
        print("  -> PARTIAL: combining buys something real but far less than a genuine second")
        print("     channel. Between the cortical route and the spoke, nearer the cortical end.")
    else:
        print("  -> COMPLEMENTARY: combining buys a large gain -> a real second channel.")
    print("")
    if hi < 0:
        print("RATIO (secondary): substrate-unique wins are FEWER than independence predicts,")
        print("  so the two arms are positively correlated -- one signal read twice, not two")
        print("  sources. **But read the UNION GAIN above for the buildability question.**")
    elif lo > 0:
        print("NOT SUBSUMED: the substrate wins items counting misses, MORE often than independence")
        print("   predicts -> there is an independent contribution to build on, despite the smaller total.")
    else:
        print("UNRESOLVED at n=%d. **Not 'independent' and not 'subsumed'** -- the CI includes what" % n)
        print("   independence predicts, so this evidence does not separate the two readings.")
    print("=" * 82)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
