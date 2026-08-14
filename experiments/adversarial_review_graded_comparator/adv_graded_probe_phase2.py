"""ADVERSARIAL phase 2. READ-ONLY, writes only to scratch/.

Q1 DIMENSION: is the LIVE (sign) arm's deficit a MAGNITUDE-DESTRUCTION effect, or just
   quantisation noise at d=256?  Score A_SSN and A_GGZ at d = 256/512/1024/2048/4096.
   If sign@d>256 catches graded@256, the bottleneck is code capacity, not the ratio-flattening.
Q2 IS THE GRADED ARM JUST BAG-OF-WORDS?  Score the EXACT (unprojected) count-cosine between the
   query's kept-word count vector and the anchor's summed profile count vector, plus the exact
   BINARY variants. If exact-count-BOW ~= A_GGZ, the HD/divisive-normalisation framing is a
   re-description of a term-count cosine.
Q3 FLOOR: why is the scrambled floor BELOW chance? random-donor derangements + sibling/frequency
   structure.
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import hashlib
import json
import sys
from collections import Counter, defaultdict

import numpy as np

REPO = "D:/AI/hd-instrument"
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import experiments.exp_context_conditioned_near_neighbour_v1 as PARENT
import experiments.exp_graded_divisive_comparator_v1 as G
from hdlab.reading_grounding_loop import CTX_D, normalize_lemma

OUT = {}
MAXI = 600
assets = PARENT.build_corpus_assets()
counts = assets["counts"]
profile_pool, eval_pool = PARENT.split_pools(assets["buckets"])
items, _ = PARENT.build_items(assets["pairs_strict"], eval_pool, MAXI)
n = len(items)
words_used = sorted({w for it in items for w in (it["target"], it["distractor"])})
wpos = {w: i for i, w in enumerate(words_used)}
nw = len(words_used)
donors = PARENT.assign_donors(items)

# ---- precompute the KEPT-WORD lists once (identical for both encoders, by construction) --------
prof_tokens = []          # list of (anchor_idx, [words])
for i, w in enumerate(words_used):
    drop = frozenset({w})
    for sent in profile_pool.get(w, ()):
        prof_tokens.append((i, G._kept_words(sent, drop)))
q_tokens = []
qs_tokens = []
for i, it in enumerate(items):
    drop = frozenset({normalize_lemma(it["target"]), normalize_lemma(it["distractor"]),
                      it["target"], it["distractor"]})
    q_tokens.append(G._kept_words(it["sentence"], drop))
    d = items[donors[i]]
    dd = drop | frozenset({normalize_lemma(d["target"]), normalize_lemma(d["distractor"]),
                           d["target"], d["distractor"]})
    qs_tokens.append(G._kept_words(d["sentence"], dd))
print("[prep] profile sentences=%d anchors=%d items=%d" % (len(prof_tokens), nw, n))

vocab = sorted({w for _i, ws in prof_tokens for w in ws} |
               {w for ws in q_tokens for w in ws} | {w for ws in qs_tokens for w in ws})
vpos = {w: i for i, w in enumerate(vocab)}
print("[prep] distinct content words = %d" % len(vocab))

prof_idx = [(i, np.array([vpos[w] for w in ws], dtype=np.int64)) for i, ws in prof_tokens]
q_idx = [np.array([vpos[w] for w in ws], dtype=np.int64) for ws in q_tokens]
qs_idx = [np.array([vpos[w] for w in ws], dtype=np.int64) for ws in qs_tokens]
ti = np.array([wpos[it["target"]] for it in items])
di = np.array([wpos[it["distractor"]] for it in items])


def cos_pair(Q, A, ti, di):
    """2AFC accuracy: cos(q_i, A[ti]) vs cos(q_i, A[di]); alphabetical tie-break as in the cell."""
    An = np.linalg.norm(A, axis=1)
    Qn = np.linalg.norm(Q, axis=1)
    st = np.einsum("ij,ij->i", Q, A[ti]) / np.maximum(An[ti] * Qn, 1e-12)
    sd = np.einsum("ij,ij->i", Q, A[di]) / np.maximum(An[di] * Qn, 1e-12)
    corr = st > sd
    tie = st == sd
    for k in np.flatnonzero(tie):
        corr[k] = items[k]["target"] < items[k]["distractor"]
    return float(corr.mean()), int(tie.sum()), corr


def word_matrix(d, seed_words):
    """the cell's own per-word bipolar draw, materialised as a (|vocab|, d) float32 matrix."""
    W = np.empty((len(seed_words), d), dtype=np.float32)
    for i, w in enumerate(seed_words):
        s = int.from_bytes(hashlib.sha256(w.encode("utf-8")).digest()[:8], "big") % (2 ** 32)
        W[i] = np.random.default_rng(s).choice([-1.0, 1.0], size=d)
    return W


def run_at_d(d):
    W = word_matrix(d, vocab)
    sumS = np.zeros((nw, d), dtype=np.float64)
    sumG = np.zeros((nw, d), dtype=np.float64)
    qsS = np.zeros(d); qsS2 = np.zeros(d); qsG = np.zeros(d); qsG2 = np.zeros(d)
    for ai, idx in prof_idx:
        if idx.size == 0:
            continue
        acc = W[idx].sum(axis=0).astype(np.float64)
        sg = np.sign(acc)
        sg[sg == 0] = 1.0
        sumS[ai] += sg
        sumG[ai] += acc
        qsS += sg; qsS2 += sg * sg
        qsG += acc; qsG2 += acc * acc
    m = len(prof_idx)
    QMU = {"S": qsS / m, "G": qsG / m}
    QSD = {"S": np.sqrt(np.maximum(qsS2 / m - QMU["S"] ** 2, 0.0)),
           "G": np.sqrt(np.maximum(qsG2 / m - QMU["G"] ** 2, 0.0))}

    def enc(idxlist, mode):
        M = np.zeros((len(idxlist), d), dtype=np.float64)
        for i, idx in enumerate(idxlist):
            if idx.size == 0:
                continue
            acc = W[idx].sum(axis=0).astype(np.float64)
            if mode == "S":
                acc = np.sign(acc)
                acc[acc == 0] = 1.0
            M[i] = acc
        return M

    res = {}
    # LIVE arm: sign enc, sign agg (ternary), no norm
    A_SS = np.sign(sumS)
    QS_ = enc(q_idx, "S")
    res["A_SSN"] = cos_pair(QS_, A_SS, ti, di)[0]
    # PRIMARY: graded enc, graded agg, Z on both pools
    A_GG = sumG
    amu, asd = A_GG.mean(axis=0), A_GG.std(axis=0)
    A_GGZ = (A_GG - amu) / (asd + 1e-9)
    QG_ = enc(q_idx, "G")
    QGZ = (QG_ - QMU["G"]) / (QSD["G"] + 1e-9)
    res["A_GGZ"] = cos_pair(QGZ, A_GGZ, ti, di)[0]
    # graded, no normalisation (isolates the ENC/AGG change from the pool statistics)
    res["A_GGN"] = cos_pair(QG_, A_GG, ti, di)[0]
    # sign arm WITH the same Z pooling (isolates: does the pool normaliser rescue the sign code?)
    amuS, asdS = A_SS.mean(axis=0), A_SS.std(axis=0)
    res["A_SSZ"] = cos_pair((QS_ - QMU["S"]) / (QSD["S"] + 1e-9),
                            (A_SS - amuS) / (asdS + 1e-9), ti, di)[0]
    del W
    return res


OUT["Q1_dimension_sweep"] = {}
for d in (256, 512, 1024, 2048, 4096):
    r = run_at_d(d)
    OUT["Q1_dimension_sweep"][d] = {k: round(v, 6) for k, v in r.items()}
    print("[Q1] d=%5d %s" % (d, json.dumps(OUT["Q1_dimension_sweep"][d])), flush=True)

# ---------------- Q2: EXACT (unprojected) bag-of-words comparators -------------------------------
A_cnt = [Counter() for _ in range(nw)]
for ai, ws in prof_tokens:
    A_cnt[ai].update(ws)
A_df = [Counter() for _ in range(nw)]        # document frequency: sentences containing the word
for ai, ws in prof_tokens:
    A_df[ai].update(set(ws))


def exact_arm(anchor_counters, query_binary):
    hits = 0
    for i, ws in enumerate(q_tokens):
        qv = Counter(ws)
        if query_binary:
            qv = Counter(set(ws))
        qn = np.sqrt(sum(v * v for v in qv.values()))
        sc = []
        for ai in (ti[i], di[i]):
            av = anchor_counters[ai]
            dot = sum(qv[w] * av.get(w, 0) for w in qv)
            an = np.sqrt(sum(v * v for v in av.values()))
            sc.append(0.0 if an == 0 or qn == 0 else dot / (an * qn))
        if sc[0] == sc[1]:
            hits += int(items[i]["target"] < items[i]["distractor"])
        else:
            hits += int(sc[0] > sc[1])
    return round(hits / len(q_tokens), 6)


OUT["Q2_exact_bow"] = {
    "exact_count_cosine": exact_arm(A_cnt, False),
    "exact_count_anchor_binary_query": exact_arm(A_cnt, True),
    "exact_df_anchor_count_query": exact_arm(A_df, False),
    "exact_df_anchor_binary_query": exact_arm(A_df, True),
}
print("[Q2]", json.dumps(OUT["Q2_exact_bow"]), flush=True)

# ---------------- Q3: why is the scrambled floor below chance? ------------------------------------
# (a) random-donor derangements instead of the deterministic offset one
W256 = word_matrix(CTX_D, vocab)
sumG = np.zeros((nw, CTX_D)); sumS = np.zeros((nw, CTX_D))
qsG = np.zeros(CTX_D); qsG2 = np.zeros(CTX_D)
for ai, idx in prof_idx:
    acc = W256[idx].sum(axis=0).astype(np.float64)
    sg = np.sign(acc); sg[sg == 0] = 1.0
    sumG[ai] += acc; sumS[ai] += sg
    qsG += acc; qsG2 += acc * acc
mm = len(prof_idx)
qmuG = qsG / mm
qsdG = np.sqrt(np.maximum(qsG2 / mm - qmuG ** 2, 0.0))
A_GG = sumG
A_GGZ = (A_GG - A_GG.mean(axis=0)) / (A_GG.std(axis=0) + 1e-9)


def enc_graded(idxlist):
    M = np.zeros((len(idxlist), CTX_D))
    for i, idx in enumerate(idxlist):
        if idx.size:
            M[i] = W256[idx].sum(axis=0).astype(np.float64)
    return M


accs_rand = []
rng = np.random.default_rng(12345)
for rep in range(20):
    perm = rng.permutation(n)
    for i in range(n):           # make it a derangement w.r.t. candidate overlap
        j = perm[i]
        tries = 0
        while tries < 50 and (j == i or items[j]["target"] in (items[i]["target"], items[i]["distractor"])
                              or items[j]["distractor"] in (items[i]["target"], items[i]["distractor"])):
            j = (j + 1) % n
            tries += 1
        perm[i] = j
    idxl = []
    for i in range(n):
        d = items[perm[i]]
        drop = frozenset({normalize_lemma(items[i]["target"]), normalize_lemma(items[i]["distractor"]),
                          items[i]["target"], items[i]["distractor"],
                          normalize_lemma(d["target"]), normalize_lemma(d["distractor"]),
                          d["target"], d["distractor"]})
        ws = G._kept_words(d["sentence"], drop)
        idxl.append(np.array([vpos[w] for w in ws if w in vpos], dtype=np.int64))
    QG = enc_graded(idxl)
    QGZ = (QG - qmuG) / (qsdG + 1e-9)
    accs_rand.append(cos_pair(QGZ, A_GGZ, ti, di)[0])
OUT["Q3_random_donor_scram_GGZ"] = {"mean": float(np.mean(accs_rand)),
                                    "sd": float(np.std(accs_rand)),
                                    "min": float(np.min(accs_rand)),
                                    "max": float(np.max(accs_rand)),
                                    "n_reps": len(accs_rand)}
print("[Q3a]", json.dumps(OUT["Q3_random_donor_scram_GGZ"]), flush=True)

# (b) is the DISTRACTOR anchor systematically closer to an arbitrary sentence?
#     score every item's two anchors against 300 RANDOM PROFILE sentences of unrelated words.
rng2 = np.random.default_rng(999)
sel = rng2.choice(len(prof_idx), size=300, replace=False)
Qr = np.zeros((300, CTX_D))
for k, s in enumerate(sel):
    Qr[k] = W256[prof_idx[s][1]].sum(axis=0).astype(np.float64)
QrZ = (Qr - qmuG) / (qsdG + 1e-9)
An = np.linalg.norm(A_GGZ, axis=1)
Qn = np.linalg.norm(QrZ, axis=1)
S = (QrZ @ A_GGZ.T) / np.outer(Qn, An)          # (300, nw)
mean_attract = S.mean(axis=0)                    # how attractive each anchor is to random queries
OUT["Q3_generic_attractiveness"] = {
    "frac_items_distractor_more_attractive": float((mean_attract[di] > mean_attract[ti]).mean()),
    "mean_attract_targets": float(mean_attract[ti].mean()),
    "mean_attract_distractors": float(mean_attract[di].mean()),
    "corr_attract_with_corpus_freq": float(np.corrcoef(
        mean_attract, np.array([np.log(counts.get(w, 1) + 1) for w in words_used]))[0, 1]),
}
# (c) does corpus frequency of target vs distractor differ in the capped 600-item set?
ft = np.array([counts.get(it["target"], 0) for it in items], dtype=float)
fd = np.array([counts.get(it["distractor"], 0) for it in items], dtype=float)
OUT["Q3_freq_asymmetry"] = {"mean_log_freq_target": float(np.log(ft + 1).mean()),
                            "mean_log_freq_distractor": float(np.log(fd + 1).mean()),
                            "frac_target_more_frequent": float((ft > fd).mean())}
print("[Q3b]", json.dumps(OUT["Q3_generic_attractiveness"]),
      json.dumps(OUT["Q3_freq_asymmetry"]), flush=True)

with open(os.path.join(REPO, "scratch", "adv_graded_phase2_out.json"), "w") as f:
    json.dump(OUT, f, indent=2, default=float)
print("DONE")
