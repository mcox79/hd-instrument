"""SUPPLIED human ratings vs what the substrate LEARNED, on identical pairs with one scorer.

WHY THIS EXISTS. The archive records our 12-dimension sensorimotor asset at rho 0.2701 on SimLex and
our live concept encoding at 0.1048 -- but those are DIFFERENT CELLS ON DIFFERENT PAIR SETS, and this
project's standing bar says no number crosses populations or scorers. So the ~2.7x gap between them
has never actually been measured; it has only been inferred by putting two numbers side by side that
are not entitled to be compared. This scores both on the SAME pairs, the SAME way, at once.

TWO CONSTRAINTS TAKEN FROM `hdlab/sensorimotor_spoke.py`'s OWN DOCSTRING, which
`tools/symbol_corrections.py` surfaced before this was written:

  1. **THIS IS SUPPLY, NOT LEARNING.** Its words: *"The Lancaster norms are HUMAN RATINGS... the
     substrate does not GROW this spoke, it is handed one. That is SUPPLY, not learning, and no
     result from this organ may be reported as the substrate having learned perceptual structure."*
     **So a win here is a statement about a HANDED-OVER ASSET beating a LEARNED one, which is a
     reason to use it and NOT evidence that the substrate understands anything.**
  2. **SWEEP THE METRIC, DO NOT ADOPT ONE.** Euclidean separates synonyms from siblings by 1.348
     pooled SDs against cosine's 0.511, but on concrete-versus-abstract pairs cosine wins by 22.8 to
     3.2. The organ exposes both deliberately, and its docstring records that the self-test which
     first asserted one was better FAILED. Both are reported here.

It calls the organ rather than loading the norms again -- a second loader would be islanding, and the
z-scoring in `grounded_similarity` is the part that is already right.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import collections
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hdlab.reading_grounding_loop import (        # noqa: E402
    content_words, context_vector_masked, normalize_lemma,
)
from hdlab import sensorimotor_spoke as spoke     # noqa: E402

N_SENT = 41
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _spearman(a, b) -> float:
    a, b = np.asarray(a, float), np.asarray(b, float)
    if len(a) < 3:
        return float("nan")
    ra = np.argsort(np.argsort(a)).astype(float)
    rb = np.argsort(np.argsort(b)).astype(float)
    ra -= ra.mean()
    rb -= rb.mean()
    den = np.sqrt((ra ** 2).sum() * (rb ** 2).sum())
    return float((ra * rb).sum() / den) if den else float("nan")


def _gold():
    out = []
    with open(os.path.join(REPO, "data/encoder_eval_benchmarks/simlex999.txt"),
              encoding="utf-8") as fh:
        hdr = fh.readline().rstrip("\r\n").split("\t")
        si = hdr.index("SimLex999")
        for line in fh:
            p = line.rstrip("\r\n").split("\t")
            if len(p) > si:
                out.append((p[0].lower(), p[1].lower(), float(p[si])))
    return out


def _by_lemma(vocab):
    from hdlab.corpus_registry import CorpusRegistry
    reg = CorpusRegistry()
    pools = []
    for name in reg.readable_names():
        h = reg.handles.get(name)
        if h is None:
            continue
        try:
            pool = [s for s in h.pool() if 40 < len(s) < 400]
        except Exception:
            continue
        if pool:
            pools.append(pool)
    by = collections.defaultdict(list)
    i = 0
    while any(i < len(p) for p in pools) and i < 40000:
        for pool in pools:
            if i < len(pool):
                for w in set(content_words(pool[i])):
                    lem = normalize_lemma(w)
                    if lem in vocab and len(by[lem]) < N_SENT:
                        by[lem].append(pool[i])
        i += 1
    return by, len(pools)


def main() -> int:
    gold = _gold()
    vocab = {w for a, b, _ in gold for w in (a, b)}
    by, n_corp = _by_lemma(vocab)
    print(f"shelf: {n_corp} corpora", flush=True)
    covered = {k for k, v in by.items() if len(v) >= N_SENT}

    # THE SAME-PAIRS RULE IS THE POINT OF THIS SCRIPT: a pair is scored only if BOTH arms can score
    # it. Otherwise the comparison is two different populations wearing one table, which is exactly
    # the fault this exists to fix.
    pairs = [(a, b, s) for a, b, s in gold
             if a in covered and b in covered
             and spoke.has_profile(a) and spoke.has_profile(b)]
    print(f"pairs covered by the CORPUS: "
          f"{len([1 for a, b, _ in gold if a in covered and b in covered])}")
    print(f"pairs covered by BOTH corpus AND norms (what is scored): {len(pairs)}", flush=True)
    if len(pairs) < 100:
        print("REFUSING: too few jointly-covered pairs.")
        return 2

    human = np.array([s for _a, _b, s in pairs], float)
    rs = np.random.default_rng(11)

    def band(scores):
        nulls = [_spearman(scores, human[rs.permutation(len(human))]) for _ in range(200)]
        nulls = np.array([x for x in nulls if np.isfinite(x)])
        return float(np.percentile(np.abs(nulls), 95))

    rows = []
    for d in (256, 1024):
        prof = {}
        for lem in {w for a, b, _ in pairs for w in (a, b)}:
            v = np.sum([context_vector_masked(s, lem, d=d) for s in by[lem][:N_SENT]], axis=0)
            n = np.linalg.norm(v)
            prof[lem] = v / n if n else v
        cos = [float(np.dot(prof[a], prof[b])) for a, b, _s in pairs]
        rows.append((f"LEARNED  masked context d={d}", cos))

    # SUPPLIED arm, BOTH metrics, because the organ's docstring says to sweep and not to adopt.
    P = {w: spoke.profile(w) for w in {x for a, b, _ in pairs for x in (a, b)}}
    sup_cos, sup_euc = [], []
    for a, b, _s in pairs:
        pa, pb = P[a], P[b]
        na, nb = np.linalg.norm(pa), np.linalg.norm(pb)
        sup_cos.append(float(np.dot(pa, pb) / (na * nb)) if na and nb else 0.0)
        sup_euc.append(-float(np.linalg.norm(pa - pb)))       # negated: distance -> similarity
    rows.append(("SUPPLIED norms12  cosine", sup_cos))
    rows.append(("SUPPLIED norms12  euclid (negated)", sup_euc))

    print("")
    print(f"{'arm':38} {'rho vs human':>13} {'null p95':>10}   (n={len(pairs)}, 200 shuffles)")
    got = {}
    for name, sc in rows:
        r, p95 = _spearman(sc, human), band(sc)
        got[name] = r
        mark = "" if r > p95 else "   <-- INSIDE THE NULL BAND"
        print(f"{name:38} {r:>13.4f} {p95:>10.4f}{mark}", flush=True)

    best_sup = max(got["SUPPLIED norms12  cosine"], got["SUPPLIED norms12  euclid (negated)"])
    learned = got["LEARNED  masked context d=1024"]
    print("")
    print(f"BEST SUPPLIED {best_sup:+.4f}  vs  LEARNED(d=1024) {learned:+.4f}  "
          f"=> supplied is {best_sup / learned:.2f}x the learned arm" if learned else "")
    print("READ AS: a HANDED-OVER asset beating a LEARNED one. Per the organ's own docstring this is")
    print("SUPPLY, not learning, and may NOT be reported as the substrate having learned perceptual")
    print("structure. It is a reason to USE the asset, not evidence of understanding.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
