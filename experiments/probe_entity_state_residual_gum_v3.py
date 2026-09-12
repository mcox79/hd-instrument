"""PROBE v3 (strategy, pri-1): the FOREGROUND constraint. The brain's situation model keeps only a few entities in focus
(Centering Cf / Glenberg availability / working-memory capacity); the event expectation decides among the in-focus
candidates, and only when the prior is undecided (precision-weighting: the PRIOR's sharpness gates the semantic cue).
Measures: (a) the in-focus ceiling -- how often the gold entity is within the grammar prior's top-k; (b) rerank by each
knowledge read restricted to the top-k prior candidates, with a prior-margin gate, tau swept, scramble control, paired CI.
"""
from __future__ import annotations

import os
import sys
import random

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import experiments.probe_entity_state_residual_gum_v1 as P1
import experiments.probe_entity_state_residual_gum_v2 as P2

SEED = 20260912


def main(predicted_parse=False):
    items = P2.collect_with_sentences(predicted_parse)
    n = len(items)
    obj, bg, G, roles = P2.load_selectional()
    from hdlab import generalized_event_knowledge as GEK
    import hdlab.typed_selectional_preference as TSP
    import math
    st = GEK._store(); tsp = TSP.get(); proj = GEK.GEKProjector()

    ALPHA = 1.0
    def r4(it, h):
        V = it["V"]
        if V is None or V not in obj:
            return None
        d = obj[V]; N = sum(d.values()); c = d.get(h, 0.0)
        pb = (bg.get(h, 0.0) + 0.5) / (G + 0.5 * len(bg))
        if c > 0:
            return math.log(((c + ALPHA * pb) / (N + ALPHA)) / pb)
        a = tsp.score(V, h)
        return 0.0 if a is None else math.log((ALPHA * pb * (1.0 + 4.0 * max(0.0, a))) / (N + ALPHA) / pb)

    def r5(it, h):
        if not it["sent_lemmas"]:
            return None
        s = proj.score(it["sent_lemmas"], [h]); return float(s) if s is not None else None

    def r1(it, h):
        V = it["V"]; return float(any(v == V and pat for v, rc, pat in it["events"][h])) if V else 0.0

    def r2(it, h):
        V = it["V"]
        if V is None or V not in st["wid"]:
            return None
        vals = [GEK._ppmi(st, st["wid"][v], st["wid"][V]) for v, _, _ in it["events"][h] if v in st["wid"]]
        return float(np.mean(vals)) if vals else None

    READS = [("R1 same-predicate", r1), ("R2 history->V", r2), ("R4 selectional", r4), ("R5 GEK content", r5)]
    pre = []
    for it in items:
        sc = P1.a5_scores(it)
        order = sorted(sc, key=sc.get, reverse=True)
        pre.append((sc, order))
    base_vec = np.array([int(it["cluster_of"][o[0]] == it["gold"]) for it, (_, o) in zip(items, pre)])
    print(f"items={n} A5={base_vec.mean():.4f}")
    for k in (1, 2, 3, 4, 5, 8):
        inside = sum(1 for it, (_, o) in zip(items, pre) if any(it["cluster_of"][h] == it["gold"] for h in o[:k]))
        print(f"  in-focus ceiling: gold within prior top-{k}: {inside}/{n} = {inside/n:.4f}")
    margins = np.array([(sc[o[0]] - sc[o[1]]) if len(o) > 1 else 9.9 for sc, o in pre])
    print(f"  prior top-2 margin: median {np.median(margins):.3f}; quartiles {np.percentile(margins,25):.3f}/{np.percentile(margins,75):.3f}; "
          f"A5 acc when margin<0.5: {base_vec[margins<0.5].mean():.3f} (n={int((margins<0.5).sum())}); margin>=0.5: {base_vec[margins>=0.5].mean():.3f}")
    rng = random.Random(SEED); rng2 = np.random.default_rng(SEED)

    def run(fn, k, tau, gate, scramble=False):
        out = []
        for it, (sc, o) in zip(items, pre):
            focus = o[:k]
            if len(o) < 2 or (gate is not None and (sc[o[0]] - sc[o[1]]) >= gate):
                pick = o[0]
            else:
                vals = [fn(it, h) for h in focus]
                if scramble:
                    rng.shuffle(vals)
                tot = {h: sc[h] + tau * (v if v is not None else 0.0) for h, v in zip(focus, vals)}
                pick = max(tot, key=tot.get)
            out.append(int(it["cluster_of"][pick] == it["gold"]))
        return np.array(out)

    def ci(vec):
        d = vec - base_vec
        boots = np.array([d[rng2.integers(0, n, n)].mean() for _ in range(2000)])
        return d.mean(), np.percentile(boots, 2.5), np.percentile(boots, 97.5)

    for name, fn in READS:
        print(f"\n{name}")
        for k in (2, 3, 4):
            for gate in (None, 1.0, 0.5):
                row = []
                for tau in (0.5, 1.0, 2.0):
                    v = run(fn, k, tau, gate); s = run(fn, k, tau, gate, scramble=True)
                    dm, lo, hi = ci(v)
                    flag = "*" if lo > 0 else ("-" if hi < 0 else " ")
                    row.append(f"tau={tau}: {v.mean():.4f}{flag} (scr {s.mean():.4f}) d={dm:+.4f}[{lo:+.3f},{hi:+.3f}]")
                print(f"  top-{k} gate={gate}: " + " | ".join(row))


if __name__ == "__main__":
    main(predicted_parse="--predicted" in sys.argv)
