"""PAIRED ceiling comparison on an IDENTICAL stratum. NOT A CELL. NO FLOORS. NOT A VERDICT.

The unpaired table compared spaces on different pair counts (999 vs 977), which is the
cross-population error this project keeps catching. This recomputes every space on the
SINGLE stratum where ALL spaces are defined, and bootstraps the DIFFERENCE with the
SAME resample index for both arms.
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import csv
import io
import json

import numpy as np
from scipy.stats import spearmanr

REPO = "D:/AI/hd-instrument"
GT = REPO + "/data/grounding_testbed"
SIMLEX = REPO + "/data/encoder_eval_benchmarks/simlex999.txt"
RNG = np.random.default_rng(20260816)
N_BOOT = 4000

pairs = []
with io.open(SIMLEX, "r", encoding="utf-8") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        pairs.append((r["word1"].strip().lower(), r["word2"].strip().lower(),
                      r["POS"].strip(), float(r["SimLex999"])))


def read_tbl(path, key="Word", delim=None):
    with io.open(path, "r", encoding="utf-8", errors="replace") as f:
        first = f.readline()
    if delim is None:
        delim = "\t" if first.count("\t") > first.count(",") else ","
    d = {}
    with io.open(path, "r", encoding="utf-8", errors="replace") as f:
        for r in csv.DictReader(f, delimiter=delim):
            w = (r.get(key) or "").strip().lower()
            if w:
                d[w] = r
    return d


lanc = read_tbl(GT + "/Lancaster_sensorimotor_norms_for_39707_words.csv")
conc = read_tbl(GT + "/Concreteness_ratings_Brysbaert_et_al_BRM.txt")
warr = read_tbl(GT + "/Ratings_Warriner_et_al.csv")

L11 = ["Auditory.mean", "Gustatory.mean", "Haptic.mean", "Interoceptive.mean",
       "Olfactory.mean", "Visual.mean", "Foot_leg.mean", "Hand_arm.mean",
       "Head.mean", "Mouth.mean", "Torso.mean"]
VAD = ["V.Mean.Sum", "A.Mean.Sum", "D.Mean.Sum"]
SRC = {"L": lanc, "C": conc, "W": warr}

SPACES = {
    "S1_CURRENT_12": [("L", c) for c in L11] + [("C", "Conc.M")],
    "S3_VAD_ONLY_3": [("W", c) for c in VAD],
    "S4_15_PLUS_VAD": [("L", c) for c in L11] + [("C", "Conc.M")] + [("W", c) for c in VAD],
    "S9_VALENCE_ONLY_1": [("W", "V.Mean.Sum")],
    "S10_AROUSAL_DOM_2": [("W", "A.Mean.Sum"), ("W", "D.Mean.Sum")],
}


def f(v):
    try:
        return float(v)
    except Exception:
        return None


def vec(w, spec):
    vals = []
    for s, c in spec:
        r = SRC[s].get(w)
        if r is None:
            return None
        x = f(r.get(c))
        if x is None:
            return None
        vals.append(x)
    return np.array(vals, dtype=np.float64)


# COMMON STRATUM: pairs where BOTH endpoints are defined in EVERY space
common = []
for w1, w2, pos, g in pairs:
    ok = all(vec(w1, sp) is not None and vec(w2, sp) is not None for sp in SPACES.values())
    if ok:
        common.append((w1, w2, pos, g))

words = sorted({w for p in common for w in p[:2]})


def sims_for(spec, zscore):
    M = np.stack([vec(w, spec) for w in words])
    if zscore:
        mu, sd = M.mean(0), M.std(0)
        sd[sd == 0] = 1.0
        M = (M - mu) / sd
    n = np.linalg.norm(M, axis=1, keepdims=True)
    n[n == 0] = 1.0
    M = M / n
    idx = {w: i for i, w in enumerate(words)}
    return np.array([float(M[idx[a]] @ M[idx[b]]) for a, b, _, _ in common])


out = {
    "WHAT_THIS_IS": "PAIRED CEILING DIAGNOSTIC on an identical stratum. Own hand-rated code, plain cosine, Spearman vs SimLex gold. NO FLOORS. NOT A CELL. NOT A VERDICT.",
    "common_stratum_pairs": len(common),
    "common_stratum_words": len(words),
    "per_pos_n": {},
    "n_boot": N_BOOT,
    "results": {},
}
from collections import Counter
out["per_pos_n"] = dict(Counter(p[2] for p in common))

gold = np.array([g for _, _, _, g in common])
pos_arr = np.array([p for _, _, p, _ in common])

for zscore in [False, True]:
    mode = "ZSCORED" if zscore else "RAW"
    S = {k: sims_for(sp, zscore) for k, sp in SPACES.items()}
    res = {}
    for pos in ["ALL", "N", "V", "A"]:
        m = np.ones(len(common), bool) if pos == "ALL" else (pos_arr == pos)
        n = int(m.sum())
        g = gold[m]
        point = {k: float(spearmanr(S[k][m], g).statistic) for k in S}
        # shared bootstrap index => paired
        boots = {k: np.empty(N_BOOT) for k in S}
        for b in range(N_BOOT):
            ix = RNG.integers(0, n, n)
            gg = g[ix]
            for k in S:
                boots[k][b] = spearmanr(S[k][m][ix], gg).statistic
        entry = {"n": n}
        for k in S:
            lo, hi = np.percentile(boots[k], [2.5, 97.5])
            entry[k] = {"rho": round(point[k], 4),
                        "ci95": [round(float(lo), 4), round(float(hi), 4)]}
        # paired deltas vs current space
        for k in S:
            if k == "S1_CURRENT_12":
                continue
            d = boots[k] - boots["S1_CURRENT_12"]
            lo, hi = np.percentile(d, [2.5, 97.5])
            entry["DELTA_" + k + "_minus_S1"] = {
                "point": round(point[k] - point["S1_CURRENT_12"], 4),
                "ci95": [round(float(lo), 4), round(float(hi), 4)],
                "CI_EXCLUDES_ZERO": bool(lo > 0 or hi < 0),
            }
        res[pos] = entry
    out["results"][mode] = res

print(json.dumps(out, indent=2))
with io.open(REPO + "/data/_target_space_paired_diagnostic.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh, indent=2)
