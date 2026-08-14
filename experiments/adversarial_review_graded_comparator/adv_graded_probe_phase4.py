"""ADVERSARIAL phase 4. READ-ONLY, writes only to scratch/.

S1 EXACT TERM-SPACE MAGNITUDE ABLATION: cosine between query and anchor in the true term space,
   with magnitude present vs FULLY DESTROYED on each side (binary presence sets). If destroying
   counts exactly costs ~nothing, then "per-component magnitude destruction" cannot be the cause
   of the live comparator's deficit -- the deficit must be random-projection interference.
S2 DIMENSION SWEEP, 3 INDEPENDENT PROJECTION DRAWS per d (salted word seeds), so the d-trend is
   not one lucky/unlucky draw.
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
items, _ = PARENT.build_items(assets["pairs_strict"], eval_pool, 600)
n = len(items)
words_used = sorted({w for it in items for w in (it["target"], it["distractor"])})
wpos = {w: i for i, w in enumerate(words_used)}
nw = len(words_used)
donors = PARENT.assign_donors(items)

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
ti = np.array([wpos[it["target"]] for it in items])
di = np.array([wpos[it["distractor"]] for it in items])
vocab = sorted({w for _i, ws in prof_tokens for w in ws} | {w for ws in q_tokens for w in ws})
vpos = {w: i for i, w in enumerate(vocab)}
print("[prep] prof=%d vocab=%d" % (len(prof_tokens), len(vocab)))

# ---------------- S1: exact term-space, magnitude on/off on each side ---------------------------
A_tf = [Counter() for _ in range(nw)]        # total term counts over the 70 profile sentences
A_df = [Counter() for _ in range(nw)]        # sentence (document) frequency
for ai, ws in prof_tokens:
    A_tf[ai].update(ws)
    A_df[ai].update(set(ws))
A_bin = [Counter({w: 1 for w in c}) for c in A_tf]   # PRESENCE ONLY -- magnitude fully destroyed


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


OUT["S1_exact_term_space"] = {
    "anchor_tf_query_count  (magnitude BOTH sides)": exact(A_tf, "count"),
    "anchor_tf_query_binary (magnitude anchor only)": exact(A_tf, "binary"),
    "anchor_df_query_count": exact(A_df, "count"),
    "anchor_binary_query_count (magnitude query only)": exact(A_bin, "count"),
    "anchor_binary_query_binary (magnitude FULLY DESTROYED)": exact(A_bin, "binary"),
    "mean_distinct_words_per_anchor": float(np.mean([len(c) for c in A_tf])),
    "mean_tokens_per_anchor": float(np.mean([sum(c.values()) for c in A_tf])),
}
print("[S1]", json.dumps(OUT["S1_exact_term_space"], indent=1), flush=True)

# ---------------- S2: dimension sweep with 3 independent projection draws ------------------------
prof_idx = [(i, np.array([vpos[w] for w in ws], dtype=np.int64)) for i, ws in prof_tokens]
q_idx = [np.array([vpos[w] for w in ws], dtype=np.int64) for ws in q_tokens]


def sweep(d, salt):
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
    A_SS = np.sign(sumS)
    A_GGZ = (sumG - sumG.mean(axis=0)) / (sumG.std(axis=0) + 1e-9)
    QGZ = (QG - qmu) / (qsd + 1e-9)

    def acc2(Q, A):
        An = np.linalg.norm(A, axis=1); Qn = np.linalg.norm(Q, axis=1)
        st = np.einsum("ij,ij->i", Q, A[ti]) / np.maximum(An[ti] * Qn, 1e-12)
        sd = np.einsum("ij,ij->i", Q, A[di]) / np.maximum(An[di] * Qn, 1e-12)
        c = st > sd
        for k in np.flatnonzero(st == sd):
            c[k] = items[k]["target"] < items[k]["distractor"]
        return c
    live = acc2(QS, A_SS); prim = acc2(QGZ, A_GGZ)
    del W
    return float(live.mean()), float(prim.mean())


OUT["S2_dimension_replicates"] = {}
for d in (256, 1024, 4096):
    rows = []
    for salt in ("", "salt1|", "salt2|"):
        l, p = sweep(d, salt)
        rows.append({"salt": salt or "CELL_EXACT", "live": round(l, 6), "primary": round(p, 6),
                     "delta": round(p - l, 6)})
        print("[S2] d=%5d salt=%-10s live=%.4f primary=%.4f delta=%+.4f"
              % (d, salt or "CELL", l, p, p - l), flush=True)
    OUT["S2_dimension_replicates"][d] = {
        "runs": rows,
        "mean_live": round(float(np.mean([r["live"] for r in rows])), 6),
        "mean_primary": round(float(np.mean([r["primary"] for r in rows])), 6),
        "mean_delta": round(float(np.mean([r["delta"] for r in rows])), 6)}

with open(os.path.join(REPO, "scratch", "adv_graded_phase4_out.json"), "w") as f:
    json.dump(OUT, f, indent=2, default=float)
print("DONE")
