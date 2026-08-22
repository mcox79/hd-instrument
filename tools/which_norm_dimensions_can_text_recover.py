"""WHICH NORM DIMENSIONS CAN A TEXT-DERIVED CHANNEL RECOVER -- AFFECT OR SENSORIMOTOR?

WHY THIS EXISTS. exp_verb_event_salient_channel_v1 (landed 2026-08-17) found that 3 AFFECT dims
(Warriner valence/arousal/dominance) beat all 12 sensorimotor+concreteness dims on SimVerb, and that
12+3 beats both width-matched controls. That is a SUPPLIED table -- it says the INFORMATION suffices,
never that a reading system could recover it.

I then wrote in my own note: "affect is plausibly HARDER to learn from text than sensorimotor
content, not easier." THAT IS AN ASSERTION AND THIS MEASURES IT. It may well be backwards: valence
is carried by lexical company (good/terrible/wonderful), whereas how a thing feels on the skin is
not something text describes often.

DESIGN -- parameter-free, and every dimension gets the IDENTICAL pairs, scorer and null, so the
CROSS-DIMENSION comparison is internally valid even though no single number is a capability claim.
  for each dim d:  rho_d = Spearman( text_similarity(w1,w2) , -|z_d(w1) - z_d(w2)| )
Two text channels, because ours is not the strongest text rival:
  OURS  masked context bundle, d=CTX_D              (what ships)
  IDF   co-occurrence counts * log(N/df)            (the recognised rival; beats us on meaning)

POSITIVE CONTROL: concreteness. It is the most robustly text-predictable of these dimensions in the
published literature. IF CONCRETENESS COMES OUT AT ITS NULL, THE HARNESS IS BROKEN AND NO OTHER
NUMBER HERE MAY BE READ -- that is reported, not worked around.

NULL: per dimension, shuffle the word->value map and recompute. Recomputed PER DIM because each
dimension has its own distribution, and importing one dim's null for another is the exact mistake
the measurement bar forbids.

CONFOUND REPORTED, NOT HIDDEN: log-frequency. A dim that merely tracks how common a word is would
score well for an uninteresting reason, so each dim's association with frequency is printed beside
its rho.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import collections
import csv
import math
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hdlab.reading_grounding_loop import (        # noqa: E402
    CTX_D, content_words, context_vector_masked, normalize_lemma,
)

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GT = os.path.join(REPO, "data", "grounding_testbed")
LANCASTER = os.path.join(GT, "Lancaster_sensorimotor_norms_for_39707_words.csv")
WARRINER = os.path.join(GT, "Ratings_Warriner_et_al.csv")
CONCRETE = os.path.join(GT, "Concreteness_ratings_Brysbaert_et_al_BRM.txt")

N_SENT = 41
N_PAIRS = 200_000
N_SHUF = 200
SEED = 7
MAX_VOCAB = 3000

SENSORIMOTOR = ["Auditory", "Gustatory", "Haptic", "Interoceptive", "Olfactory", "Visual",
                "Foot_leg", "Hand_arm", "Head", "Mouth", "Torso"]
AFFECT = ["Valence", "Arousal", "Dominance"]
CONTROL = ["Concreteness"]   # POSITIVE CONTROL: if this reads at its null, the harness is broken.


def _sentences() -> list[str]:
    """THE WHOLE SHELF, ROUND-ROBIN. An alphabetical cap on this call is the error that produced a
    withdrawn board question earlier tonight: it read 9 of 28 corpora and I called it the shelf."""
    from hdlab.corpus_registry import CorpusRegistry
    reg = CorpusRegistry()
    pools = []
    for name in reg.readable_names():
        h = reg.handles.get(name)
        if h is None:
            continue
        try:
            pools.append((name, list(h.pool())))
        except Exception as exc:
            print(f"  [{name}] pool() failed: {type(exc).__name__}: {exc}", flush=True)
    print(f"  corpora readable: {len(pools)}", flush=True)
    out: list[str] = []
    idx = 0
    while True:
        added = 0
        for _, pool in pools:
            if idx < len(pool):
                s = pool[idx]
                if 40 < len(s) < 400:
                    out.append(s)
                added += 1
        if added == 0:
            break
        idx += 1
    return out


def _load_norms() -> dict[str, dict[str, float]]:
    """Lancaster (11 sensorimotor + concreteness proxy) and Warriner (VAD), raw values."""
    vals: dict[str, dict[str, float]] = collections.defaultdict(dict)
    with open(LANCASTER, encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            w = (row.get("Word") or "").strip().lower()
            if not w:
                continue
            for dim in SENSORIMOTOR:
                v = row.get(f"{dim}.mean")
                if v not in (None, ""):
                    try:
                        vals[w][dim] = float(v)
                    except ValueError:
                        pass
    with open(WARRINER, encoding="utf-8-sig", newline="") as fh:
        rdr = csv.DictReader(fh)
        cols = {"Valence": "V.Mean.Sum", "Arousal": "A.Mean.Sum", "Dominance": "D.Mean.Sum"}
        for row in rdr:
            w = (row.get("Word") or "").strip().lower()
            if not w:
                continue
            for dim, col in cols.items():
                v = row.get(col)
                if v not in (None, ""):
                    try:
                        vals[w][dim] = float(v)
                    except ValueError:
                        pass
    # Brysbaert concreteness -- THE POSITIVE CONTROL. Tab-separated, CRLF.
    with open(CONCRETE, encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            w = (row.get("Word") or "").strip().lower()
            v = row.get("Conc.M")
            if w and v not in (None, ""):
                try:
                    vals[w]["Concreteness"] = float(v)
                except ValueError:
                    pass
    return vals


def _rank(a: np.ndarray) -> np.ndarray:
    """Average-rank transform, so Spearman == Pearson on ranks and ties are handled."""
    order = np.argsort(a, kind="mergesort")
    r = np.empty(len(a), dtype=np.float64)
    r[order] = np.arange(len(a), dtype=np.float64)
    # average ties
    s = a[order]
    i = 0
    while i < len(s):
        j = i
        while j + 1 < len(s) and s[j + 1] == s[i]:
            j += 1
        if j > i:
            r[order[i:j + 1]] = (i + j) / 2.0
        i = j + 1
    return r


def _pearson(x: np.ndarray, y: np.ndarray) -> float:
    xc = x - x.mean()
    yc = y - y.mean()
    d = math.sqrt(float(xc @ xc) * float(yc @ yc))
    return 0.0 if d == 0 else float(xc @ yc) / d


def main() -> int:
    print("reading the shelf ...", flush=True)
    sents = _sentences()
    print(f"corpus sentences: {len(sents)}", flush=True)
    if len(sents) < 50_000:
        print("REFUSING: shelf far smaller than the 286k this project reads -- not the population.")
        return 2

    norms = _load_norms()
    need = set(SENSORIMOTOR) | set(AFFECT) | set(CONTROL)
    normed = {w: v for w, v in norms.items() if need <= set(v)}
    print(f"words with ALL {len(need)} dims: {len(normed)}", flush=True)

    by_lemma: dict[str, list[str]] = collections.defaultdict(list)
    freq: collections.Counter = collections.Counter()
    for s in sents:
        ws = content_words(s)
        for w in ws:
            freq[normalize_lemma(w)] += 1
        for w in set(ws):
            lem = normalize_lemma(w)
            if len(lem) > 2 and len(by_lemma[lem]) < N_SENT:
                by_lemma[lem].append(s)

    vocab = sorted(l for l, ss in by_lemma.items() if len(ss) >= N_SENT and l in normed)
    print(f"VOCAB (>= {N_SENT} sentences AND all dims): {len(vocab)}", flush=True)
    if len(vocab) > MAX_VOCAB:
        # SEEDED subsample, and the drop is PRINTED -- a silent cap reads as full coverage.
        pre = len(vocab)
        vocab = sorted(np.random.default_rng(SEED).choice(vocab, size=MAX_VOCAB, replace=False).tolist())
        print(f"  CAPPED at {MAX_VOCAB} (dropped {pre - MAX_VOCAB} for memory; seeded, not the head of the list)", flush=True)
    if len(vocab) < 200:
        print("REFUSING: too few words carry both a profile and every dimension.")
        return 2

    # ---- OURS: masked context bundle, exactly what the live path accumulates ----
    print("building OURS profiles ...", flush=True)
    ours = np.zeros((len(vocab), CTX_D), dtype=np.float64)
    for i, lem in enumerate(vocab):
        acc = np.zeros(CTX_D, dtype=np.float64)
        for s in by_lemma[lem][:N_SENT]:
            acc += context_vector_masked(s, lem)
        ours[i] = acc
        if (i + 1) % 500 == 0:
            print(f"  {i + 1}/{len(vocab)}", flush=True)

    # ---- IDF: co-occurrence counts over the SAME sentences, weighted log(N/df) ----
    print("building IDF profiles ...", flush=True)
    ctx_index: dict[str, int] = {}
    rows: list[collections.Counter] = []
    for lem in vocab:
        c: collections.Counter = collections.Counter()
        for s in by_lemma[lem][:N_SENT]:
            for w in content_words(s):
                cw = normalize_lemma(w)
                if cw == lem:
                    continue
                if cw not in ctx_index:
                    ctx_index[cw] = len(ctx_index)
                c[ctx_index[cw]] += 1
        rows.append(c)
    df = np.zeros(len(ctx_index), dtype=np.float64)
    for c in rows:
        for k in c:
            df[k] += 1
    idfw = np.log(len(vocab) / np.maximum(df, 1.0))
    idf = np.zeros((len(vocab), len(ctx_index)), dtype=np.float32)
    for i, c in enumerate(rows):
        for k, v in c.items():
            idf[i, k] = v * idfw[k]
    print(f"  context vocabulary: {len(ctx_index)}", flush=True)

    def unit(m: np.ndarray) -> np.ndarray:
        n = np.linalg.norm(m, axis=1, keepdims=True)
        return m / np.maximum(n, 1e-12)

    ours_u = unit(ours)
    idf_u = unit(idf)   # stays float32: at 3k words x ~30k context terms, float64 is ~1 GB

    rng = np.random.default_rng(SEED)
    n = len(vocab)
    ia = rng.integers(0, n, size=N_PAIRS * 2)
    ib = rng.integers(0, n, size=N_PAIRS * 2)
    keep = ia != ib
    ia, ib = ia[keep][:N_PAIRS], ib[keep][:N_PAIRS]
    print(f"pairs scored: {len(ia)}", flush=True)

    sim_ours = np.einsum("ij,ij->i", ours_u[ia], ours_u[ib])
    sim_idf = np.einsum("ij,ij->i", idf_u[ia], idf_u[ib])
    r_ours = _rank(sim_ours)
    r_idf = _rank(sim_idf)

    logf = np.array([math.log10(max(freq[l], 1)) for l in vocab], dtype=np.float64)
    r_freq = _rank(-np.abs(logf[ia] - logf[ib]))

    dims = CONTROL + SENSORIMOTOR + AFFECT
    print()
    print(f"{'dimension':<16}{'OURS':>9}{'null95':>9}{'IDF':>9}{'null95':>9}{'freq':>9}  group")
    print("-" * 70)
    out = []
    for dim in dims:
        z = np.array([normed[l][dim] for l in vocab], dtype=np.float64)
        z = (z - z.mean()) / (z.std() + 1e-12)
        sim_d = -np.abs(z[ia] - z[ib])
        rd = _rank(sim_d)
        ro = _pearson(r_ours, rd)
        ri = _pearson(r_idf, rd)
        rf = _pearson(r_freq, rd)
        no, ni = [], []
        for _ in range(N_SHUF):
            zs = z[rng.permutation(n)]
            rs = _rank(-np.abs(zs[ia] - zs[ib]))
            no.append(abs(_pearson(r_ours, rs)))
            ni.append(abs(_pearson(r_idf, rs)))
        p95o = float(np.percentile(no, 95))
        p95i = float(np.percentile(ni, 95))
        grp = "AFFECT" if dim in AFFECT else ("**CONTROL**" if dim in CONTROL else "sensorimotor")
        print(f"{dim:<16}{ro:>9.4f}{p95o:>9.4f}{ri:>9.4f}{p95i:>9.4f}{rf:>9.4f}  {grp}")
        out.append((dim, ro, p95o, ri, p95i, grp))

    print()
    for label, arm_i, null_i in (("OURS", 1, 2), ("IDF", 3, 4)):
        aff = [r[arm_i] for r in out if r[5] == "AFFECT"]
        sen = [r[arm_i] for r in out if r[5] == "sensorimotor"]
        cl = [r[0] for r in out if r[arm_i] > r[null_i]]
        print(f"{label}: mean AFFECT {np.mean(aff):+.4f} | mean sensorimotor {np.mean(sen):+.4f} "
              f"| clears own null: {len(cl)}/{len(out)} {cl}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
