"""ADVERSARIAL phase 6. READ-ONLY, writes only to scratch/.
U1 WORD-IDENTITY LEAK: is the target's own code recoverable from the GRADED query when it is not
   from the SIGN query? (both candidates are masked, but the leak controls are morphological)
U2 SIGN-ARM FAIRNESS: the live ENC quantiser maps sign-zero to +1 (a constant component shared by
   every query), while the live AGG quantiser leaves zeros (ternary). Do those two conventions --
   which are NOT the magnitude hypothesis -- cost the LIVE arm anything?
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import json
import sys
import numpy as np

REPO = "D:/AI/hd-instrument"
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import experiments.exp_context_conditioned_near_neighbour_v1 as PARENT
import experiments.exp_graded_divisive_comparator_v1 as G
from hdlab.reading_grounding_loop import CTX_D, normalize_lemma

OUT = {}
assets = PARENT.build_corpus_assets()
profile_pool, eval_pool = PARENT.split_pools(assets["buckets"])
items, _ = PARENT.build_items(assets["pairs_strict"], eval_pool, 600)
n = len(items)
words_used = sorted({w for it in items for w in (it["target"], it["distractor"])})
wpos = {w: i for i, w in enumerate(words_used)}
nw = len(words_used)
ti = np.array([wpos[it["target"]] for it in items])
di = np.array([wpos[it["distractor"]] for it in items])

# ---- U1: does the query vector correlate with the CANDIDATE'S OWN word code? --------------------
def leak(fn):
    hits = 0
    mt, md = [], []
    for it in items:
        drop = frozenset({normalize_lemma(it["target"]), normalize_lemma(it["distractor"]),
                          it["target"], it["distractor"]})
        q = fn(it["sentence"], drop)
        qn = np.linalg.norm(q) + 1e-12
        vt = G._word_vec(it["target"], CTX_D)
        vd = G._word_vec(it["distractor"], CTX_D)
        ct = float(q @ vt) / (qn * np.linalg.norm(vt))
        cd = float(q @ vd) / (qn * np.linalg.norm(vd))
        mt.append(ct); md.append(cd)
        hits += int(ct > cd)
    return {"acc_pick_higher_cos_to_own_word_code": round(hits / n, 6),
            "mean_cos_target": round(float(np.mean(mt)), 6),
            "mean_cos_distractor": round(float(np.mean(md)), 6)}


OUT["U1_word_identity_leak"] = {"graded_query": leak(G._graded), "signed_query": leak(G._signed)}
print("[U1]", json.dumps(OUT["U1_word_identity_leak"]), flush=True)

# ---- U2: zero-convention variants for the LIVE arm ----------------------------------------------
sum_S = np.zeros((nw, CTX_D))
sum_G = np.zeros((nw, CTX_D))
for i, w in enumerate(words_used):
    drop = frozenset({w})
    for sent in profile_pool.get(w, ()):
        sum_S[i] += G._signed(sent, drop)
        sum_G[i] += G._graded(sent, drop)
A_tern = np.sign(sum_S)                     # LIVE anchor code (ternary, hdlab's convention)
A_bip = np.sign(sum_S); A_bip[A_bip == 0] = 1.0     # bipolar anchors (the other live convention)

Q_bip = np.zeros((n, CTX_D))                # LIVE query code (sign-zero -> +1)
Q_tern = np.zeros((n, CTX_D))               # ternary query (sign-zero left at 0)
Q_grad = np.zeros((n, CTX_D))
for i, it in enumerate(items):
    drop = frozenset({normalize_lemma(it["target"]), normalize_lemma(it["distractor"]),
                      it["target"], it["distractor"]})
    acc = G._graded(it["sentence"], drop)
    Q_grad[i] = acc
    s = np.sign(acc)
    Q_tern[i] = s
    s2 = s.copy(); s2[s2 == 0] = 1.0
    Q_bip[i] = s2


def acc(Q, A):
    An = np.linalg.norm(A, axis=1); Qn = np.linalg.norm(Q, axis=1)
    st = np.einsum("ij,ij->i", Q, A[ti]) / np.maximum(An[ti] * Qn, 1e-12)
    sd = np.einsum("ij,ij->i", Q, A[di]) / np.maximum(An[di] * Qn, 1e-12)
    c = st > sd
    for k in np.flatnonzero(st == sd):
        c[k] = items[k]["target"] < items[k]["distractor"]
    return round(float(c.mean()), 6)


OUT["U2_zero_convention"] = {
    "LIVE as shipped (bipolar query x ternary anchor)": acc(Q_bip, A_tern),
    "ternary query x ternary anchor": acc(Q_tern, A_tern),
    "bipolar query x bipolar anchor": acc(Q_bip, A_bip),
    "ternary query x bipolar anchor": acc(Q_tern, A_bip),
    "frac_zero_dims_in_sign_query": float((Q_tern == 0).mean()),
    "frac_zero_dims_in_ternary_anchor": float((A_tern == 0).mean()),
    "graded query x ternary anchor (ENC change only, no norm)": acc(Q_grad, A_tern),
    "graded query x graded anchor (no norm)": acc(Q_grad, sum_G),
}
print("[U2]", json.dumps(OUT["U2_zero_convention"], indent=1), flush=True)

with open(os.path.join(REPO, "scratch", "adv_graded_phase6_out.json"), "w") as f:
    json.dump(OUT, f, indent=2, default=float)
print("DONE")
