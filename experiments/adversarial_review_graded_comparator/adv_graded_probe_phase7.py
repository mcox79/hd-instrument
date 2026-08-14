"""ADVERSARIAL phase 7 -- the dimension test at the FULL n=4000 / 2377-anchor scale.
READ-ONLY; writes only to scratch/.
Validates the pipeline by reproducing the FULL run's A_SSN / A_GGZ at d=256, then asks whether the
LIVE (sign) comparator at d=1024 reaches the GRADED comparator at d=256.
Also re-computes the exact (unprojected) term-space ceiling at full scale.
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import hashlib
import json
import sys
from collections import Counter

import numpy as np

REPO = "D:/AI/hd-instrument"
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import experiments.exp_context_conditioned_near_neighbour_v1 as PARENT
import experiments.exp_graded_divisive_comparator_v1 as G
from hdlab.reading_grounding_loop import normalize_lemma

OUT = {}
assets = PARENT.build_corpus_assets()
profile_pool, eval_pool = PARENT.split_pools(assets["buckets"])
items, _ = PARENT.build_items(assets["pairs_strict"], eval_pool, 4000)
n = len(items)
words_used = sorted({w for it in items for w in (it["target"], it["distractor"])})
wpos = {w: i for i, w in enumerate(words_used)}
nw = len(words_used)
print("[prep] items=%d anchors=%d" % (n, nw), flush=True)

prof_tokens = []
for i, w in enumerate(words_used):
    drop = frozenset({w})
    for sent in profile_pool.get(w, ()):
        prof_tokens.append((i, G._kept_words(sent, drop)))
q_tokens = []
for it in items:
    drop = frozenset({normalize_lemma(it["target"]), normalize_lemma(it["distractor"]),
                      it["target"], it["distractor"]})
    q_tokens.append(G._kept_words(it["sentence"], drop))
vocab = sorted({w for _i, ws in prof_tokens for w in ws} | {w for ws in q_tokens for w in ws})
vpos = {w: i for i, w in enumerate(vocab)}
prof_idx = [(i, np.array([vpos[w] for w in ws], dtype=np.int64)) for i, ws in prof_tokens]
q_idx = [np.array([vpos[w] for w in ws], dtype=np.int64) for ws in q_tokens]
ti = np.array([wpos[it["target"]] for it in items])
di = np.array([wpos[it["distractor"]] for it in items])
print("[prep] profile sentences=%d vocab=%d" % (len(prof_idx), len(vocab)), flush=True)


def a2(Q, A):
    An = np.linalg.norm(A, axis=1); Qn = np.linalg.norm(Q, axis=1)
    st = np.einsum("ij,ij->i", Q, A[ti]) / np.maximum(An[ti] * Qn, 1e-12)
    sd = np.einsum("ij,ij->i", Q, A[di]) / np.maximum(An[di] * Qn, 1e-12)
    c = st > sd
    for k in np.flatnonzero(st == sd):
        c[k] = items[k]["target"] < items[k]["distractor"]
    return c


def sweep(d, salt=""):
    W = np.empty((len(vocab), d), dtype=np.float32)
    for i, w in enumerate(vocab):
        s = int.from_bytes(hashlib.sha256((salt + w).encode("utf-8")).digest()[:8], "big") % (2**32)
        W[i] = np.random.default_rng(s).choice([-1.0, 1.0], size=d)
    sumS = np.zeros((nw, d)); sumG = np.zeros((nw, d))
    qsG = np.zeros(d); qsG2 = np.zeros(d)
    for ai, idx in prof_idx:
        acc = W[idx].sum(axis=0).astype(np.float64)
        sg = np.sign(acc); sg[sg == 0] = 1.0
        sumS[ai] += sg; sumG[ai] += acc
        qsG += acc; qsG2 += acc * acc
    m = len(prof_idx)
    qmu = qsG / m
    qsd = np.sqrt(np.maximum(qsG2 / m - qmu ** 2, 0.0))
    QS = np.zeros((n, d)); QG = np.zeros((n, d))
    for i, idx in enumerate(q_idx):
        acc = W[idx].sum(axis=0).astype(np.float64)
        QG[i] = acc
        sg = np.sign(acc); sg[sg == 0] = 1.0
        QS[i] = sg
    live = a2(QS, np.sign(sumS))
    prim = a2((QG - qmu) / (qsd + 1e-9),
              (sumG - sumG.mean(axis=0)) / (sumG.std(axis=0) + 1e-9))
    gradN = a2(QG, sumG)
    del W
    return {"A_SSN": round(float(live.mean()), 6), "A_GGZ": round(float(prim.mean()), 6),
            "A_GGN": round(float(gradN.mean()), 6),
            "delta": round(float(prim.mean() - live.mean()), 6)}


OUT["full_scale_dimension"] = {}
for d in (256, 1024, 4096):
    r = sweep(d)
    OUT["full_scale_dimension"][d] = r
    print("[d=%d] %s" % (d, json.dumps(r)), flush=True)

# exact term-space ceiling at full scale
A_tf = [Counter() for _ in range(nw)]
for ai, ws in prof_tokens:
    A_tf[ai].update(ws)
A_bin = [Counter({w: 1 for w in c}) for c in A_tf]


def exact(anchor, qmode):
    hits = 0
    for i, ws in enumerate(q_tokens):
        qv = Counter(ws) if qmode == "count" else Counter({w: 1 for w in set(ws)})
        qn = np.sqrt(sum(v * v for v in qv.values()))
        sc = []
        for ai in (ti[i], di[i]):
            av = anchor[ai]
            dot = sum(qv[w] * av.get(w, 0) for w in qv)
            an = np.sqrt(sum(v * v for v in av.values()))
            sc.append(0.0 if an == 0 or qn == 0 else dot / (an * qn))
        hits += int(sc[0] > sc[1]) if sc[0] != sc[1] else int(
            items[i]["target"] < items[i]["distractor"])
    return round(hits / n, 6)


OUT["full_scale_exact"] = {"anchor_counts_query_counts": exact(A_tf, "count"),
                           "anchor_PRESENCE_query_PRESENCE": exact(A_bin, "binary")}
print("[exact]", json.dumps(OUT["full_scale_exact"]), flush=True)

with open(os.path.join(REPO, "scratch", "adv_graded_phase7_out.json"), "w") as f:
    json.dump(OUT, f, indent=2, default=float)
print("DONE")
