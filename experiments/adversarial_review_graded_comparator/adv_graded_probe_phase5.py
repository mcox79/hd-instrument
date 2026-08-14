"""ADVERSARIAL phase 5. READ-ONLY, writes only to scratch/.
T1 PROJECTION-DRAW VARIANCE at the cell's own d=256: 8 independent draws of the word code.
   The item bootstrap holds the projection FIXED, so this variance component is invisible to it.
T2 HELD-OUT CLAIM: is any scored eval sentence also a PROFILE sentence of either candidate?
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import hashlib
import json
import sys
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

# ---- T2 held-out overlap -----------------------------------------------------------------------
prof_sets = {w: set(profile_pool.get(w, ())) for w in words_used}
in_target_profile = sum(1 for it in items if it["sentence"] in prof_sets[it["target"]])
in_distr_profile = sum(1 for it in items if it["sentence"] in prof_sets[it["distractor"]])
in_any_profile = sum(1 for it in items
                     if any(it["sentence"] in prof_sets[w] for w in (it["target"],
                                                                     it["distractor"])))
all_prof = set()
for w in words_used:
    all_prof |= prof_sets[w]
in_some_other_profile = sum(1 for it in items if it["sentence"] in all_prof)
OUT["T2_heldout"] = {"items": n,
                     "eval_sentence_in_TARGET_profile": in_target_profile,
                     "eval_sentence_in_DISTRACTOR_profile": in_distr_profile,
                     "eval_sentence_in_either_candidate_profile": in_any_profile,
                     "eval_sentence_in_ANY_anchor_word_profile": in_some_other_profile}
print("[T2]", json.dumps(OUT["T2_heldout"]), flush=True)

# ---- T1 projection variance ---------------------------------------------------------------------
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
d = 256


def draw(salt):
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

    def a2(Q, A):
        An = np.linalg.norm(A, axis=1); Qn = np.linalg.norm(Q, axis=1)
        st = np.einsum("ij,ij->i", Q, A[ti]) / np.maximum(An[ti] * Qn, 1e-12)
        sd = np.einsum("ij,ij->i", Q, A[di]) / np.maximum(An[di] * Qn, 1e-12)
        c = st > sd
        for k in np.flatnonzero(st == sd):
            c[k] = items[k]["target"] < items[k]["distractor"]
        return float(c.mean())
    return a2(QS, A_SS), a2(QGZ, A_GGZ)


rows = []
for salt in ("", "p1|", "p2|", "p3|", "p4|", "p5|", "p6|", "p7|"):
    l, p = draw(salt)
    rows.append({"salt": salt or "CELL_EXACT", "live": round(l, 6), "primary": round(p, 6),
                 "delta": round(p - l, 6)})
    print("[T1] salt=%-10s live=%.4f primary=%.4f delta=%+.4f" % (salt or "CELL", l, p, p - l),
          flush=True)
dd = np.array([r["delta"] for r in rows])
OUT["T1_projection_variance_d256"] = {
    "runs": rows, "mean_delta": float(dd.mean()), "sd_delta": float(dd.std(ddof=1)),
    "min": float(dd.min()), "max": float(dd.max()),
    "cell_draw_delta": rows[0]["delta"],
    "cell_draw_rank_of_8": int((dd > rows[0]["delta"]).sum()) + 1,
    "n_draws_below_0.0525_strict_margin": int((dd < 0.0525).sum()),
    "n_draws_below_0.05_band": int((dd < 0.05).sum()),
    "mean_live": float(np.mean([r["live"] for r in rows])),
    "mean_primary": float(np.mean([r["primary"] for r in rows]))}
print("[T1]", json.dumps(OUT["T1_projection_variance_d256"]["mean_delta"]),
      OUT["T1_projection_variance_d256"]["sd_delta"])

with open(os.path.join(REPO, "scratch", "adv_graded_phase5_out.json"), "w") as f:
    json.dump(OUT, f, indent=2, default=float)
print("DONE")
