"""THE LIVE MEANING BAG ENCODES SURFACE FORMS. IT ALREADY COMPUTES THE LEMMA AND THROWS IT AWAY.

`context_vector_masked` (hdlab/reading_grounding_loop.py:251) reads:

    words = [w for w in content_words(sentence) if normalize_lemma(w) != target_lemma]
    return context_vector(" ".join(words), d=d, graded=graded)

It calls `normalize_lemma` on EVERY token to decide what to MASK, then hands the SURFACE forms to
the encoder. So `cat` and `cats` in the surrounding context receive INDEPENDENT random codes
(measured: cos +0.0469), and two sentences about the same thing share nothing on that token.

WHY THIS IS THE RIGHT EXPERIMENT AND NOT THE FORM CHANNEL. The obvious repair is the VWFA-analog
form code wired on 2026-08-22 -- but that makes SPELLING-similar words similar, and the archive
already measured what spelling is worth on this benchmark: the ORTHOGRAPHIC floor scores rho 0.015
(d1024) / 0.0169 (d512) in `exp_meaning_asset_hardened_margins_v1`. Near zero. Orthography is not
the missing ingredient. LEXICAL IDENTITY is -- and lemmatisation is how the brain's word-recognition
path delivers it: surface form is normalised to a lexeme BEFORE semantics, which is exactly the
`content_words` -> `content_lemmas` distinction this module already draws and does not use here.

ONE VARIABLE. Same pairs, same corpus, same sentence budget, same bundling math, same masking rule.
The ONLY difference is whether the surviving tokens are encoded as they appeared or as their lemma.

PREDICTION, STATED BEFORE RUNNING SO IT CAN FAIL: lemmatising MERGES types, so each lemma's profile
is built from more evidence per code and the meaning rho RISES. It could equally FALL -- lemmatising
destroys the tense/number distinction the bag currently carries, and `normalize_lemma` has its own
error rate. A null is also a real outcome and would say the surface/lemma split costs us nothing.

FLOORS ARE RECOMPUTED ON THIS POPULATION, NEVER IMPORTED (measurement bar rule 2), and the paired
difference carries a bootstrap CI beside the null p95 (rule 5).
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
    content_words, context_vector, context_vector_masked, form_identity_vector, normalize_lemma,
    symbol_vector,
)

N_SENT = 41
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _spearman(a, b) -> float:
    """GUARDED. A CONSTANT score vector is the trap this repo documents: np.argsort of a constant
    array returns 0..n-1 IN INDEX ORDER, so a scorer carrying ZERO information gets a real-looking
    rho. Caught here on the first run of this script -- the frequency floor was the capped sentence
    count, identical (41) for every covered lemma, and it read -0.1335 against a null p95 of 0.0664.
    An information-free arm must score as nothing, not as a floor."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    if len(a) < 3:
        return float("nan")
    if len(np.unique(a)) < 3 or len(np.unique(b)) < 3:
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
        pi = hdr.index("POS") if "POS" in hdr else None
        for line in fh:
            p = line.rstrip("\r\n").split("\t")
            if len(p) > si:
                out.append((p[0].lower(), p[1].lower(), float(p[si]),
                            p[pi] if pi is not None and len(p) > pi else "?"))
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
    # UNCAPPED occurrence count -- `by` is capped at N_SENT so it CANNOT serve as a frequency
    # floor (every covered lemma would tie at 41). Counted separately for that reason.
    raw = collections.Counter()
    i = 0
    while any(i < len(p) for p in pools) and i < 40000:
        for pool in pools:
            if i < len(pool):
                for w in set(content_words(pool[i])):
                    lem = normalize_lemma(w)
                    if lem in vocab:
                        raw[lem] += 1
                        if len(by[lem]) < N_SENT:
                            by[lem].append(pool[i])
        i += 1
    return by, len(pools), raw


def _ctx_lemma(sentence: str, target_lemma: str, d: int) -> np.ndarray:
    """The ONE-VARIABLE twin of context_vector_masked: identical masking, identical bundling,
    tokens handed over as LEMMAS instead of surfaces."""
    lems = [normalize_lemma(w) for w in content_words(sentence)]
    kept = [l for l in lems if l != target_lemma]
    return context_vector(" ".join(kept), d=d)


def _profiles(pairs, by, d, fn):
    prof = {}
    for lem in {w for a, b, _s, _p in pairs for w in (a, b)}:
        v = np.sum([fn(s, lem, d) for s in by[lem][:N_SENT]], axis=0)
        n = np.linalg.norm(v)
        prof[lem] = v / n if n else v
    return prof


def _trigrams(w: str):
    p = f"##{w}##"
    return {p[i:i + 3] for i in range(len(p) - 2)}


def main() -> int:
    gold = _gold()
    vocab = {w for a, b, _s, _p in gold for w in (a, b)}
    by, n_corp, raw_freq = _by_lemma(vocab)
    print(f"shelf: {n_corp} corpora", flush=True)
    covered = {k for k, v in by.items() if len(v) >= N_SENT}
    pairs = [(a, b, s, pos) for a, b, s, pos in gold if a in covered and b in covered]
    print(f"pairs scored (BOTH words have {N_SENT} sentences): {len(pairs)}", flush=True)
    if len(pairs) < 100:
        print("REFUSING: too few jointly-covered pairs to read anything.")
        return 2

    # HOW MUCH DOES THE INTERVENTION ACTUALLY CHANGE? A control excluding nothing is not a control.
    tot = chg = 0
    for lem in list(covered)[:200]:
        for s in by[lem][:5]:
            for w in content_words(s):
                tot += 1
                chg += int(w.lower() != normalize_lemma(w))
    print(f"tokens whose surface differs from its lemma: {chg:,}/{tot:,} = {chg/max(tot,1):.1%}",
          flush=True)

    human = np.array([s for _a, _b, s, _p in pairs], float)
    rs = np.random.default_rng(11)

    def band(scores):
        nulls = [_spearman(scores, human[rs.permutation(len(human))]) for _ in range(200)]
        nulls = np.array([x for x in nulls if np.isfinite(x)])
        return float(np.percentile(np.abs(nulls), 95))

    # ---- FLOORS, RECOMPUTED ON THIS POPULATION ------------------------------------------------
    orth = [len(_trigrams(a) & _trigrams(b)) / max(len(_trigrams(a) | _trigrams(b)), 1)
            for a, b, _s, _p in pairs]
    frq = [-abs(np.log1p(raw_freq[a]) - np.log1p(raw_freq[b])) for a, b, _s, _p in pairs]
    print("\n=== FLOORS on THIS population (never imported) ===")
    for nm, sc in (("ORTHOGRAPHIC trigram", orth), ("FREQUENCY (uncapped)", frq)):
        r = _spearman(sc, human)
        d_ = len(np.unique(np.asarray(sc, float)))
        if not np.isfinite(r):
            print(f"    {nm:24} DEGENERATE ({d_} distinct values) -- REFUSING to score")
        else:
            print(f"    {nm:24} rho = {r:+.4f}  |rho| = {abs(r):.4f}  "
                  f"null p95 = {band(sc):.4f}  ({d_} distinct)")

    # ---- THE TWO ARMS -------------------------------------------------------------------------
    print("\n=== ARMS: identical except how the surviving tokens are spelled ===")
    results = {}
    for d in (256, 1024):
        cos = {}
        for name, fn in (("SURFACE (live)", lambda s, l, dd: context_vector_masked(s, l, d=dd)),
                         ("LEMMA (twin)", _ctx_lemma)):
            prof = _profiles(pairs, by, d, fn)
            cos[name] = np.array([float(np.dot(prof[a], prof[b])) for a, b, _s, _p in pairs])
            r, p95 = _spearman(cos[name], human), band(cos[name])
            print(f"    d={d:4d}  {name:16} rho = {r:+.4f}   null p95 = {p95:.4f}", flush=True)
            results[(d, name)] = (r, p95)

        # paired bootstrap on the DIFFERENCE -- a width is not an effect
        a1, a2 = cos["SURFACE (live)"], cos["LEMMA (twin)"]
        bs = np.random.default_rng(5)
        diffs = []
        for _ in range(400):
            idx = bs.integers(0, len(human), len(human))
            diffs.append(_spearman(a2[idx], human[idx]) - _spearman(a1[idx], human[idx]))
        diffs = np.array([x for x in diffs if np.isfinite(x)])
        lo, hi = np.percentile(diffs, [2.5, 97.5])
        obs = results[(d, "LEMMA (twin)")][0] - results[(d, "SURFACE (live)")][0]
        sep = "SEPARATED from 0" if (lo > 0 or hi < 0) else "NOT separated from 0"
        print(f"    d={d:4d}  LEMMA - SURFACE = {obs:+.4f}  95% CI [{lo:+.4f}, {hi:+.4f}]  {sep}")

    # ---- THE FORM CODE, MEASURED RATHER THAN ARGUED --------------------------------------------
    # The lemma result above makes an ARGUMENT about the form channel: lemmatisation is the PERFECT
    # merge of inflectional variants, a form code is a PARTIAL one (cos 0.44-0.57) that additionally
    # manufactures similarity between unrelated lookalikes -- so lemma should upper-bound it. An
    # argument is not a measurement, and this is cheap, so the arm is run.
    # Ungraded on all three arms here so the ONLY variable is which code the tokens get.
    print("\n=== FORM CODE IN THE MEANING BAG (ungraded, one variable: the code) ===")

    def _bag(sentence, target_lemma, d, vec):
        acc = np.zeros(d)
        for w in content_words(sentence):
            if normalize_lemma(w) != target_lemma:
                acc += vec(w, d)
        out = np.sign(acc)
        out[out == 0] = 1.0
        return out

    d = 1024
    for name, vec in (("SURFACE hash", symbol_vector), ("FORM code", form_identity_vector)):
        prof = _profiles(pairs, by, d, lambda s, l, dd, _v=vec: _bag(s, l, dd, _v))
        sc = np.array([float(np.dot(prof[a], prof[b])) for a, b, _s, _p in pairs])
        print(f"    d={d}  {name:14} rho = {_spearman(sc, human):+.4f}   "
              f"null p95 = {band(sc):.4f}", flush=True)

    # ---- by word class, since the archive says nouns and verbs behave differently --------------
    print("\n=== by word class (d=256), because verbs and nouns are NOT the same story here ===")
    d = 256
    prof_s = _profiles(pairs, by, d, lambda s, l, dd: context_vector_masked(s, l, d=dd))
    prof_l = _profiles(pairs, by, d, _ctx_lemma)
    for pos in ("N", "V", "A"):
        sub = [(a, b, s) for a, b, s, p in pairs if p == pos]
        if len(sub) < 30:
            print(f"    POS {pos}: n={len(sub)} -- TOO FEW, not scored")
            continue
        h = np.array([s for _a, _b, s in sub], float)
        cs = [float(np.dot(prof_s[a], prof_s[b])) for a, b, _s in sub]
        cl = [float(np.dot(prof_l[a], prof_l[b])) for a, b, _s in sub]
        nl = [_spearman(cl, h[rs.permutation(len(h))]) for _ in range(200)]
        p95 = float(np.percentile(np.abs([x for x in nl if np.isfinite(x)]), 95))
        print(f"    POS {pos} n={len(sub):3d}   SURFACE {_spearman(cs, h):+.4f}   "
              f"LEMMA {_spearman(cl, h):+.4f}   null p95 {p95:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
