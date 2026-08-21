"""Raising the dimension improved IDENTIFICATION. Does it buy MEANING? Decides whether D1 is worth it.

WHY THIS EXISTS. On 2026-08-21 a floored sweep showed word IDENTIFICATION rising monotonically with
the context-vector dimension -- `d=1024` minus `d=256` is `+0.0622`, CI `[+0.0443, +0.0797]`, with the
scramble floor recomputed at every `d` and flat at chance. That is the evidence for `notes/PLAN.md`
D1, "raise the live path from 256 to 1024".

**BUT THE SAME NIGHT ESTABLISHED THAT IDENTIFICATION IS LARGELY A LOOKUP** -- the target word alone
scores 0.9687 where the word plus its whole sentence scores 0.6423. A lever that improves a lookup is
not obviously a lever that improves understanding, and D1 is expensive: it rewrites every persisted
store. So the question that actually decides it is whether dimension buys MEANING.

**AND THIS IS A RECORDED GAP, NOT A NEW IDEA.** `ORGAN_MAP` states that `P_LIVE_CONCEPT` -- our live
concept encoding, rho 0.1048 on SimLex with a CI crossing zero -- **was ONLY EVER RUN AT d=256**, and
says in terms: *"NO CAPACITY CLAIM IS AVAILABLE HERE."* This fills exactly that.

WHY THE CORPUS CONFOUND DOES NOT APPLY HERE. Earlier tonight a source-identity confound wrecked an
identification measurement, and the fix was a source-balanced sample that left only 111 usable pairs.
**That confound is irrelevant to THIS comparison**, because every `d` is scored on the SAME pairs
from the SAME corpora -- the confound is constant across the arms being compared and cancels. So this
can use all pairs whose words are covered, which is far better powered.

CONTROLS, both mandatory:
  * SHUFFLED gold at every `d` -- the human ratings permuted. Must sit at zero at every dimension. If
    it rises with `d`, the metric inflates and the real curve means nothing.
  * The pairing is by construction: identical pairs, identical corpora, only `d` changes.
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

N_SENT = 41
DIMS = (128, 256, 512, 1024, 2048)
GOLD = "data/encoder_eval_benchmarks/simlex999.txt"


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


def _gold_pairs() -> list[tuple]:
    """SimLex-999. TAB separated, score in the `SimLex999` column -- read the HEADER, do not guess.

    A plain `.split()` here returns the part-of-speech tag and every row raises, which produced a
    silent 'zero pairs' earlier tonight and would have read as 'the benchmark is absent'.
    """
    out = []
    with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), GOLD),
              encoding="utf-8") as fh:
        hdr = fh.readline().rstrip("\r\n").split("\t")
        si = hdr.index("SimLex999")
        for line in fh:
            p = line.rstrip("\r\n").split("\t")
            if len(p) > si:
                out.append((p[0].lower(), p[1].lower(), float(p[si])))
    return out


def _corpus_by_lemma(vocab: set) -> dict:
    """Sentences per lemma, ROUND-ROBIN across every readable corpus.

    Round-robin, not the first N alphabetically: that cap took 9 of 28 corpora earlier tonight -- all
    novels and readers, no textbooks -- and produced a claim I had to withdraw within the hour.
    """
    from hdlab.corpus_registry import CorpusRegistry
    reg = CorpusRegistry()
    pools = []
    for name in reg.readable_names():
        h = reg.handles.get(name)
        if h is None:
            continue
        try:
            pool = [s for s in h.pool() if 40 < len(s) < 400]
        except Exception as exc:
            print(f"  [{name}] pool() failed: {type(exc).__name__}: {exc}", flush=True)
            continue
        if pool:
            pools.append(pool)
    print(f"shelf: {len(pools)} corpora", flush=True)
    by = collections.defaultdict(list)
    i = 0
    while any(i < len(p) for p in pools):
        for pool in pools:
            if i < len(pool):
                s = pool[i]
                for w in set(content_words(s)):
                    lem = normalize_lemma(w)
                    if lem in vocab and len(by[lem]) < N_SENT:
                        by[lem].append(s)
        i += 1
        if i > 40000:
            break
    return by


def main() -> int:
    import hdlab.reading_grounding_loop as rgl
    print(f"CONFIG: GRADED_COMPARATOR={rgl.GRADED_COMPARATOR}", flush=True)
    gold = _gold_pairs()
    vocab = {w for a, b, _ in gold for w in (a, b)}
    print(f"SimLex pairs {len(gold)}, vocab {len(vocab)}", flush=True)
    by = _corpus_by_lemma(vocab)
    covered = {k for k, v in by.items() if len(v) >= N_SENT}
    pairs = [(a, b, s) for a, b, s in gold if a in covered and b in covered]
    print(f"lemmas covered at >={N_SENT} sentences: {len(covered)}")
    print(f"PAIRS SCORED (identical at every d): {len(pairs)}", flush=True)
    if len(pairs) < 100:
        print("REFUSING: too few pairs to read a correlation.")
        return 2

    rs = np.random.default_rng(5)
    human = [s for _a, _b, s in pairs]

    # THE NULL IS A BAND FROM MANY SHUFFLES, NOT ONE PERMUTATION.
    # The first version of this shuffled the gold ONCE and reused that single permutation at every
    # d. It read 0.0568 to 0.0846 -- comparable to the real signal -- and appeared to RISE with d.
    # That was one unlucky draw inherited by all five arms, not a property of the representation. A
    # single shuffle is a sample; a null is a DISTRIBUTION, and the bar here requires the null's p95
    # beside every margin.
    N_SHUF = 200

    print("")
    print(f"{'d':>6}  {'rho vs human':>13}  {'null p95':>10}  {'null mean':>10}   "
          f"(n={len(pairs)} pairs, {N_SHUF} shuffles)")
    per_d = {}
    for d in DIMS:
        prof = {}
        for lem in covered:
            v = np.sum([context_vector_masked(s, lem, d=d) for s in by[lem][:N_SENT]], axis=0)
            n = np.linalg.norm(v)
            prof[lem] = v / n if n else v
        cos = [float(np.dot(prof[a], prof[b])) for a, b, _s in pairs]
        per_d[d] = cos
        hv = np.array(human, float)
        nulls = []
        for _ in range(N_SHUF):
            nulls.append(_spearman(cos, hv[rs.permutation(len(hv))]))
        nulls = np.array([x for x in nulls if np.isfinite(x)])
        real = _spearman(cos, human)
        p95 = float(np.percentile(np.abs(nulls), 95))
        flag = "" if real > p95 else "   <-- INSIDE THE NULL BAND"
        print(f"{d:>6}  {real:>13.4f}  {p95:>10.4f}  {nulls.mean():>10.4f}{flag}", flush=True)

    # THE DECISION PAIR, WITH AN INTERVAL. Bootstrap over PAIRS, resampling the SAME indices for
    # both arms so the comparison stays paired -- the two arms differ only in d.
    a256, a1024 = np.array(per_d[256]), np.array(per_d[1024])
    h = np.array(human, float)
    boot = []
    for _ in range(2000):
        idx = rs.integers(0, len(h), len(h))
        boot.append(_spearman(a1024[idx], h[idx]) - _spearman(a256[idx], h[idx]))
    boot = np.array([x for x in boot if np.isfinite(x)])
    lo, hi = np.percentile(boot, [2.5, 97.5])
    diff = _spearman(a1024, h) - _spearman(a256, h)
    print("")
    print(f"d=1024 MINUS d=256 on MEANING: {diff:+.4f}  95% CI [{lo:+.4f}, {hi:+.4f}]  "
          f"half-width {(hi - lo) / 2:.4f}")
    print(f"CI EXCLUDES ZERO: {bool(lo > 0 or hi < 0)}")
    print("")
    print("READ: identification gained +0.0622 CI [+0.0443,+0.0797] from the same change. If this")
    print("interval spans zero, dimension buys the LOOKUP and not the understanding, and D1's cost")
    print("(it rewrites every persisted store) is being paid for the wrong half.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
