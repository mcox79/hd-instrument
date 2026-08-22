"""THE FIRST BUILDABLE ARM OF THE NIGHT: if co-occurrence is being read as similarity, SUBTRACT it.

THE CHAIN THIS TESTS (each link already measured, notes/THE_SIGNAL_FOR_OPPOSITION_IS_IN_THE_TEXT_...):
antonyms CO-OCCUR (cond. "X and/or Y" 0.0782 vs 0.0022 random) -> context_vector_masked builds
SECOND-ORDER profiles, so sharing a sentence enriches both profiles -> antonyms become our CLOSEST
relation (cos 0.2062 > synonyms 0.1727) -> verb similarity reads 0.0000. If that chain is right, then
penalising co-occurrence should RAISE verb correlation. This is the first thing tonight worth
BUILDING rather than measuring, and it is still only a SCORER change, not a new encoder.

THE BAR IS NOT A SHUFFLE. It is idf-counting at 0.0689 on these exact pairs, which is the rival that
already beats us. Clearing a null here would mean nothing.

FOUR THINGS THAT CAN KILL IT, ALL RUN:
  A REPRODUCTION GATE   OURS alone must come back near 0.0000 on this population. If it does not, the
                        setup is not the one those numbers came from and NOTHING may be compared.
  B COOC ALONE          if co-occurrence by itself scores well, the "fix" is just counting again --
                        which is the project's standing negative, not a discovery.
  D RANDOM PENALTY      subtract a magnitude-matched RANDOM term. If that helps as much, the effect is
                        "any penalty helps", not opposition. THIS IS THE ONE THAT MATTERS MOST.
  HELD-OUT              lambda chosen on one half, scored on the other, 2,000 splits. An in-sample
                        swept maximum is a fitted number -- that error was made twice tonight already,
                        and 200 resamples was too few to place a bound near zero.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import collections
import math
import re
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hdlab.reading_grounding_loop import (        # noqa: E402
    content_words, context_vector_masked, normalize_lemma,
)
from which_norm_dimensions_can_text_recover import _pearson, _rank, _sentences   # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIMVERB = os.path.join(REPO, "data", "encoder_eval_benchmarks", "simverb3500.txt")
N_SENT = 41
D = 1024                      # matches the d the 0.0000 / 0.0689 verb numbers were computed at
LAMBDAS = [0.0, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0, 1.5]
N_SPLIT = 2000


def main() -> int:
    pairs = []
    with open(SIMVERB, encoding="utf-8") as fh:
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) >= 5:
                pairs.append((p[0].strip().lower(), p[1].strip().lower(), float(p[3]), p[4].strip()))

    sents = _sentences()
    wanted = {w for a, b, _, _ in pairs for w in (a, b)}
    where: dict[str, set] = collections.defaultdict(set)
    by_lemma: dict[str, list[str]] = collections.defaultdict(list)
    low: list[str] = []
    for i, s in enumerate(sents):
        lems = {normalize_lemma(w) for w in content_words(s)}
        for w in lems & wanted:
            where[w].add(i)
            if len(by_lemma[w]) < N_SENT:
                by_lemma[w].append(s)
        low.append(s.lower() if (lems & wanted) else "")

    vocab = sorted(w for w in wanted if len(by_lemma[w]) >= N_SENT)
    idx = {w: i for i, w in enumerate(vocab)}
    print(f"verbs with >= {N_SENT} sentences: {len(vocab)}", flush=True)

    # ---- OURS: masked-context bundle, and IDF: the rival, both over the SAME 41 sentences ----
    P = np.zeros((len(vocab), D), dtype=np.float64)
    ctx: dict[str, int] = {}
    rows = []
    for i, w in enumerate(vocab):
        acc = np.zeros(D, dtype=np.float64)
        c: collections.Counter = collections.Counter()
        for s in by_lemma[w][:N_SENT]:
            acc += context_vector_masked(s, w, d=D)
            for t in content_words(s):
                t = normalize_lemma(t)
                if t != w:
                    c[ctx.setdefault(t, len(ctx))] += 1
        P[i] = acc
        rows.append(c)
    df = np.zeros(len(ctx))
    for c in rows:
        for k in c:
            df[k] += 1
    idfw = np.log(len(vocab) / np.maximum(df, 1.0))
    IDF = np.zeros((len(vocab), len(ctx)), dtype=np.float32)
    for i, c in enumerate(rows):
        for k, v in c.items():
            IDF[i, k] = v * idfw[k]

    def unit(m):
        return (m / np.maximum(np.linalg.norm(m, axis=1, keepdims=True), 1e-12)).astype(np.float32)
    Pu, Iu = unit(P), unit(IDF)

    gold, ours, idfs, cooc = [], [], [], []
    for a, b, g, _rel in pairs:
        if a not in idx or b not in idx or a == b:
            continue
        ia, ib = idx[a], idx[b]
        sa, sb = where[a], where[b]
        both = sa & sb
        pat = re.compile(rf"\b{re.escape(a)}\w*\s+(?:and|or)\s+{re.escape(b)}\w*\b|"
                         rf"\b{re.escape(b)}\w*\s+(?:and|or)\s+{re.escape(a)}\w*\b")
        coord = sum(1 for i in both if pat.search(low[i]))
        # co-occurrence strength, frequency-normalised the way the v3 note settled on
        c_rate = coord / len(both) if both else 0.0
        lift = len(both) / max(len(sa) * len(sb) / len(sents), 1e-9)
        gold.append(g)
        ours.append(float(Pu[ia] @ Pu[ib]))
        idfs.append(float(Iu[ia] @ Iu[ib]))
        cooc.append(math.log1p(max(lift, 0.0)) + 3.0 * c_rate)

    gold = np.array(gold); ours = np.array(ours); idfs = np.array(idfs); cooc = np.array(cooc)
    n = len(gold)
    rg = _rank(gold)
    z = lambda v: (v - v.mean()) / (v.std() + 1e-12)          # noqa: E731
    zo, zc = z(ours), z(cooc)
    print(f"pairs scored: {n}", flush=True)

    r_ours = _pearson(_rank(ours), rg)
    r_idf = _pearson(_rank(idfs), rg)
    r_cooc = _pearson(_rank(cooc), rg)
    print(f"\n[A REPRODUCTION GATE] OURS alone rho {r_ours:+.4f}  (expected ~0.0000)")
    if abs(r_ours) > 0.05:
        print("  REFUSING: this is not the population the 0.0000 came from; nothing may be compared.")
        return 2
    print(f"[THE BAR]             idf-counting rho {r_idf:+.4f}  (expected ~0.0689)")
    print(f"[B COOC ALONE]        co-occurrence term rho {r_cooc:+.4f}")

    print(f"\n{'lambda':>8}{'OURS - L*COOC':>16}{'OURS - L*RANDOM':>18}")
    print("-" * 44)
    rng = np.random.default_rng(7)
    zr = z(rng.permutation(cooc))          # magnitude-matched RANDOM penalty
    best_l, best_r = 0.0, -9
    for L in LAMBDAS:
        rc = _pearson(_rank(zo - L * zc), rg)
        rr = _pearson(_rank(zo - L * zr), rg)
        print(f"{L:>8.2f}{rc:>16.4f}{rr:>18.4f}")
        if rc > best_r:
            best_r, best_l = rc, L

    # ---- HELD-OUT: choose lambda on one half, score on the other ----
    gains = []
    for s_ in range(N_SPLIT):
        r2 = np.random.default_rng(1000 + s_)
        perm = r2.permutation(n)
        h1, h2 = perm[: n // 2], perm[n // 2:]
        bl, br = 0.0, -9
        for L in LAMBDAS:
            v = _pearson(_rank(zo[h1] - L * zc[h1]), _rank(gold[h1]))
            if v > br:
                br, bl = v, L
        gains.append(_pearson(_rank(zo[h2] - bl * zc[h2]), _rank(gold[h2]))
                     - _pearson(_rank(zo[h2]), _rank(gold[h2])))
    g = np.array(gains)
    lo, hi = np.percentile(g, [2.5, 97.5])
    print(f"\n[IN-SAMPLE BEST]  lambda {best_l} -> rho {best_r:+.4f}  (gain {best_r-r_ours:+.4f})")
    print(f"[HELD-OUT GAIN]   {g.mean():+.4f}  95% CI [{lo:+.4f}, {hi:+.4f}]  ({N_SPLIT} splits)")
    print(f"[EXCLUDES ZERO]   {'YES' if lo > 0 else 'NO'}")
    print(f"[VS THE BAR]      best in-sample {best_r:+.4f} vs idf-counting {r_idf:+.4f} -> "
          f"{'CLEARS' if best_r > r_idf else 'DOES NOT CLEAR'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
