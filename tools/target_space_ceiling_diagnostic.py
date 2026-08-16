"""CEILING DIAGNOSTIC for candidate TARGET SPACES. NOT A CELL. NO FLOORS. NOT A VERDICT.

Question: with the word's OWN hand-rated code (no graph, no bridging -- the K1 condition),
how much SimLex signal can each candidate target space hold AT ALL, overall and per POS?

This measures the ROOF of each space. It says nothing about whether any arm clears a floor.
Numbers here may NOT be quoted as an experimental result; they exist to decide which spaces
are worth putting into a can-fail cell.
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
N_BOOT = 2000

# ---------- SimLex ----------
pairs = []
with io.open(SIMLEX, "r", encoding="utf-8") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        pairs.append(
            (r["word1"].strip().lower(), r["word2"].strip().lower(),
             r["POS"].strip(), float(r["SimLex999"]))
        )

# ---------- raw tables ----------
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
LSD = [c.replace(".mean", ".SD") for c in L11]
LDER = ["Max_strength.perceptual", "Minkowski3.perceptual", "Exclusivity.perceptual",
        "Dominant.perceptual", "Max_strength.action", "Minkowski3.action",
        "Exclusivity.action"]
VAD = ["V.Mean.Sum", "A.Mean.Sum", "D.Mean.Sum"]


def f(v):
    try:
        return float(v)
    except Exception:
        return None


def build(spec):
    """spec: list of (source, column). returns {word: np.array}"""
    src = {"L": lanc, "C": conc, "W": warr}
    vocab = None
    for s, _c in spec:
        v = set(src[s])
        vocab = v if vocab is None else (vocab & v)
    out = {}
    for w in vocab:
        vals = []
        ok = True
        for s, c in spec:
            x = f(src[s][w].get(c))
            if x is None:
                ok = False
                break
            vals.append(x)
        if ok:
            out[w] = np.array(vals, dtype=np.float64)
    return out


SPACES = {
    "S1_CURRENT_12DIM_lanc11_plus_conc": [("L", c) for c in L11] + [("C", "Conc.M")],
    "S2_lanc11_only": [("L", c) for c in L11],
    "S3_VAD_ONLY_3dim": [("W", c) for c in VAD],
    "S4_12DIM_plus_VAD_15dim": [("L", c) for c in L11] + [("C", "Conc.M")] + [("W", c) for c in VAD],
    "S5_12DIM_plus_lancSD_23dim": [("L", c) for c in L11] + [("C", "Conc.M")] + [("L", c) for c in LSD],
    "S6_12DIM_plus_derived_18dim": [("L", c) for c in L11] + [("C", "Conc.M")]
                                    + [("L", c) for c in LDER if c != "Dominant.perceptual"],
    "S7_EVERYTHING_lanc_all_plus_conc_plus_VAD": [("L", c) for c in L11 + LSD]
                                    + [("L", c) for c in LDER if c != "Dominant.perceptual"]
                                    + [("C", "Conc.M")] + [("W", c) for c in VAD],
    "S8_CONC_ONLY_1dim": [("C", "Conc.M")],
}


def score(tbl, zscore):
    """returns per-POS and overall rho + bootstrap CI on covered pairs"""
    words = sorted(tbl)
    M = np.stack([tbl[w] for w in words])
    if zscore:
        mu = M.mean(0)
        sd = M.std(0)
        sd[sd == 0] = 1.0
        M = (M - mu) / sd
    nrm = np.linalg.norm(M, axis=1, keepdims=True)
    nrm[nrm == 0] = 1.0
    M = M / nrm
    idx = {w: i for i, w in enumerate(words)}

    res = {}
    for pos_filter in ["ALL", "N", "V", "A"]:
        sims, gold = [], []
        for w1, w2, pos, g in pairs:
            if pos_filter != "ALL" and pos != pos_filter:
                continue
            if w1 in idx and w2 in idx:
                sims.append(float(M[idx[w1]] @ M[idx[w2]]))
                gold.append(g)
        n = len(sims)
        if n < 10:
            res[pos_filter] = {"n": n, "rho": None}
            continue
        sims = np.array(sims)
        gold = np.array(gold)
        rho = float(spearmanr(sims, gold).statistic)
        boots = np.empty(N_BOOT)
        for b in range(N_BOOT):
            s = RNG.integers(0, n, n)
            boots[b] = spearmanr(sims[s], gold[s]).statistic
        lo, hi = np.percentile(boots, [2.5, 97.5])
        res[pos_filter] = {"n": n, "rho": round(rho, 4),
                           "ci95": [round(float(lo), 4), round(float(hi), 4)]}
    return res


out = {
    "WHAT_THIS_IS": "CEILING DIAGNOSTIC. Word's OWN hand-rated code, plain cosine, Spearman vs SimLex-999 gold. NO FLOORS, NO NULL ARM, NOT A CELL, NOT A VERDICT.",
    "n_boot": N_BOOT,
    "seed": 20260816,
    "spaces": {},
}
for name, spec in SPACES.items():
    tbl = build(spec)
    out["spaces"][name] = {
        "n_dim": len(spec),
        "vocab": len(tbl),
        "RAW_concat": score(tbl, zscore=False),
        "ZSCORED_per_dim": score(tbl, zscore=True),
    }
    print("done", name, flush=True)

print(json.dumps(out, indent=2))
with io.open(REPO + "/data/_target_space_ceiling_diagnostic.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh, indent=2)
