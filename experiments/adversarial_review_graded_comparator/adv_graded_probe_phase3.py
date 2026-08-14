"""ADVERSARIAL phase 3. READ-ONLY, writes only to scratch/.

R1 ITEM-SUBSET ROBUSTNESS: the smoke keeps the ALPHABETICALLY-FIRST 600 of 8636 candidate items
   (build_items sorts by item_id then truncates). Does the delta survive on a different 600-item
   slice, and on a random 600?
R2 DONOR MECHANISM for the below-chance floor: is the donor sentence more often a DISTRACTOR-
   context than a TARGET-context under the deterministic offset derangement?
R3 The band question: bootstrap of (delta - 0.05).
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
all_items, diag = PARENT.build_items(assets["pairs_strict"], eval_pool, None)
print("[items] total available = %d" % len(all_items))


def evaluate(items, tag):
    n = len(items)
    words_used = sorted({w for it in items for w in (it["target"], it["distractor"])})
    wpos = {w: i for i, w in enumerate(words_used)}
    nw = len(words_used)
    sum_S = np.zeros((nw, CTX_D)); sum_G = np.zeros((nw, CTX_D))
    qs_S = np.zeros(CTX_D); qs_S2 = np.zeros(CTX_D)
    qs_G = np.zeros(CTX_D); qs_G2 = np.zeros(CTX_D)
    npr = 0
    for i, w in enumerate(words_used):
        drop = frozenset({w})
        for sent in profile_pool.get(w, ()):
            vs = G._signed(sent, drop); vg = G._graded(sent, drop)
            sum_S[i] += vs; sum_G[i] += vg
            qs_S += vs; qs_S2 += vs * vs
            qs_G += vg; qs_G2 += vg * vg
            npr += 1
    m = max(1, npr)
    QMU = {"S": qs_S / m, "G": qs_G / m}
    QSD = {"S": np.sqrt(np.maximum(qs_S2 / m - QMU["S"] ** 2, 0.0)),
           "G": np.sqrt(np.maximum(qs_G2 / m - QMU["G"] ** 2, 0.0))}
    donors = PARENT.assign_donors(items)
    Q = {}; QS = {}
    for enc, fn in (("S", G._signed), ("G", G._graded)):
        real = np.zeros((n, CTX_D)); scram = np.zeros((n, CTX_D))
        for i, it in enumerate(items):
            drop = frozenset({normalize_lemma(it["target"]), normalize_lemma(it["distractor"]),
                              it["target"], it["distractor"]})
            real[i] = fn(it["sentence"], drop)
            d = items[donors[i]]
            dd = drop | frozenset({normalize_lemma(d["target"]), normalize_lemma(d["distractor"]),
                                   d["target"], d["distractor"]})
            scram[i] = fn(d["sentence"], dd)
        Q[enc] = real; QS[enc] = scram
    ti = np.array([wpos[it["target"]] for it in items])
    di = np.array([wpos[it["distractor"]] for it in items])

    def acc(enc, agg, nm, scram=False):
        A0 = {("S", "S"): np.stack([G._sign_anchor(sum_S[i]) for i in range(nw)]),
              ("G", "G"): sum_G}[(enc, agg)]
        A = G._normalise(A0, A0.mean(axis=0), A0.std(axis=0), nm)
        Qa = G._normalise(QS[enc] if scram else Q[enc], QMU[enc], QSD[enc], nm)
        An = np.linalg.norm(A, axis=1); Qn = np.linalg.norm(Qa, axis=1)
        st = np.einsum("ij,ij->i", Qa, A[ti]) / np.maximum(An[ti] * Qn, 1e-12)
        sd = np.einsum("ij,ij->i", Qa, A[di]) / np.maximum(An[di] * Qn, 1e-12)
        c = st > sd
        for k in np.flatnonzero(st == sd):
            c[k] = items[k]["target"] < items[k]["distractor"]
        return c

    live = acc("S", "S", "N"); prim = acc("G", "G", "Z")
    scl = acc("S", "S", "N", scram=True); scp = acc("G", "G", "Z", scram=True)
    # donor-context diagnostic
    buckets = assets["buckets"]
    in_t = in_d = 0
    for i, it in enumerate(items):
        ds = items[donors[i]]["sentence"]
        if ds in buckets.get(it["target"], ()):
            in_t += 1
        if ds in buckets.get(it["distractor"], ()):
            in_d += 1
    res = {"n": n, "n_anchors": nw,
           "LIVE_A_SSN": round(float(live.mean()), 6),
           "PRIMARY_A_GGZ": round(float(prim.mean()), 6),
           "delta": round(float(prim.mean() - live.mean()), 6),
           "SCRAM_LIVE": round(float(scl.mean()), 6),
           "SCRAM_PRIMARY": round(float(scp.mean()), 6),
           "donor_sentence_in_target_bucket": in_t,
           "donor_sentence_in_distractor_bucket": in_d}
    print("[%s] %s" % (tag, json.dumps(res)), flush=True)
    return res, live, prim


OUT["R1_smoke_slice_0_600"], live0, prim0 = evaluate(all_items[:600], "slice[0:600] (THE SMOKE)")
OUT["R1_slice_2000_2600"], _, _ = evaluate(all_items[2000:2600], "slice[2000:2600]")
OUT["R1_slice_5000_5600"], _, _ = evaluate(all_items[5000:5600], "slice[5000:5600]")
rng = np.random.default_rng(4242)
pick = np.sort(rng.choice(len(all_items), size=600, replace=False))
OUT["R1_random_600"], _, _ = evaluate([all_items[i] for i in pick], "random600")

# R3 -- paired bootstrap of the delta against the +0.05 BAND (not against zero)
d = prim0.astype(float) - live0.astype(float)
rng = np.random.default_rng(20260813)
n = len(d)
boot = np.array([d[rng.integers(0, n, n)].mean() for _ in range(20000)])
OUT["R3_band_test"] = {"delta": float(d.mean()),
                       "ci95": [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))],
                       "frac_boot_above_0": float((boot > 0).mean()),
                       "frac_boot_above_0.05_band": float((boot > 0.05).mean()),
                       "frac_boot_above_0.0525_strict_margin": float((boot > 0.0525).mean())}
print("[R3]", json.dumps(OUT["R3_band_test"]))

with open(os.path.join(REPO, "scratch", "adv_graded_phase3_out.json"), "w") as f:
    json.dump(OUT, f, indent=2, default=float)
print("DONE")
