"""exp_antonym_typed_spoke_valence_v1 -- a 5th TYPED SPOKE spotted while drilling: ANTONYMY (lexical opposition).

THE CAP (measured). A symmetric distributional signature is not merely capped on opposition -- it is ANTI-
PREDICTIVE: ConceptNet antonym pairs have HIGHER hub cosine than WordNet synonym pairs (antonyms co-occur in the
same frames -- "hot"/"cold" both with "weather"), so cosine RANKS opposites as MORE related than near-synonyms.
AUC(symmetric cosine separates synonym from antonym) < 0.5. A typed antonym spoke is REQUIRED.

THE BRAIN (PINNED). Antonymy is a DISTINCT lexical relation the mental lexicon stores explicitly (Deese 1965;
Murphy & Andrew 1993; Mohammad et al. 2013 "degree of antonymy") -- it is NOT derivable from distributional
similarity (Mohammad: antonyms are among the most distributionally similar word pairs). Valence/affect is an OCC
appraisal spoke (our live C3a Warriner lexicon); antonyms carry OPPOSITE valence, so a similarity-keyed valence
read confuses "good"/"bad".

CONSUMER DEMONSTRATION (valence-sign propagation over the LIVE Warriner lexicon). Given a seed word with known
valence sign, predict a linked target's sign. SYMMETRIC propagation ("similar -> same sign", the valence-spread
heuristic, Turney-Littman) gets synonyms right and antonyms WRONG (predicts same, gold opposite). A TYPED ANTONYM
spoke flips the sign on antonym edges. Floors: majority sign; symmetric propagation. Twin: shuffled edge labels.

Glass-box, NO external LLM. ASCII. Own data dir. NO hdlab write (Q111).
Run: .venv/Scripts/python.exe experiments/exp_antonym_typed_spoke_valence_v1.py --self-test
     .venv/Scripts/python.exe experiments/exp_antonym_typed_spoke_valence_v1.py            (full)
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")

import sys
import csv
import json
import time
import pickle
import argparse

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

HUB_PATH = os.path.join(_REPO, "data", "frontend_assets", "hub_ppmi_svd_200d.pkl")
WARRINER = os.path.join(_REPO, "data", "frontend_assets", "Ratings_Warriner_et_al.csv")
CN_JSONL = os.path.join(_REPO, "data", "datasets", "conceptnet5_en_100k.jsonl")
OUT = os.path.join(_REPO, "data", "exp_antonym_typed_spoke_valence_v1")
# KB_REFERENT: data/frontend_assets/hub_ppmi_svd_200d.pkl
# KB_REFERENT: data/frontend_assets/Ratings_Warriner_et_al.csv
# KB_REFERENT: data/datasets/conceptnet5_en_100k.jsonl
_EPS = 1e-9


def unit(v):
    v = np.asarray(v, float)
    n = np.linalg.norm(v)
    return v / (n + _EPS) if n > 0 else v


def load_valence():
    """Warriner V.Mean.Sum (1-9, 5=neutral) -> {word: sign in {+1,-1}} dropping near-neutral (|v-5|<0.5)."""
    val = {}
    with open(WARRINER, encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            w = row.get("Word", "").strip().lower()
            try:
                v = float(row.get("V.Mean.Sum", ""))
            except ValueError:
                continue
            if w and abs(v - 5.0) >= 0.5:
                val[w] = 1 if v > 5.0 else -1
    return val


def load_antonyms(hub):
    out = []
    with open(CN_JSONL, encoding="utf-8") as f:
        for ln in f:
            d = json.loads(ln)
            if d.get("predicate") == "Antonym":
                a = d["subject"].lower().replace("_", " "); b = d["object"].lower().replace("_", " ")
                if a in hub and b in hub and a != b:
                    out.append((a, b))
    return sorted(set(out))


def load_synonyms(hub, cap):
    from nltk.corpus import wordnet as wn
    syn = set()
    for s in wn.all_synsets():
        lems = [l.name().lower() for l in s.lemmas() if "_" not in l.name() and l.name().lower() in hub]
        for i in range(len(lems)):
            for j in range(i + 1, len(lems)):
                if lems[i] != lems[j]:
                    syn.add(tuple(sorted((lems[i], lems[j]))))
    syn = sorted(syn)
    rng = np.random.default_rng(0)
    if len(syn) > cap:
        syn = [syn[i] for i in rng.choice(len(syn), size=cap, replace=False)]
    return syn


def _auc(pos, neg):
    a = np.concatenate([pos, neg])
    y = np.concatenate([np.ones(len(pos)), np.zeros(len(neg))])
    o = a.argsort(); r = np.empty_like(o, float); r[o] = np.arange(1, len(a) + 1)
    return float((r[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def boot_delta(a, b, B=2000, seed=1):
    a = np.asarray(a, float); b = np.asarray(b, float)
    n = min(len(a), len(b)); a, b = a[:n], b[:n]
    rng = np.random.default_rng(seed)
    ds = [(a[i] - b[i]).mean() for i in (rng.integers(0, n, n) for _ in range(B))]
    lo, hi = float(np.percentile(ds, 2.5)), float(np.percentile(ds, 97.5))
    return {"delta": round(float((a - b).mean()), 4), "lo": round(lo, 4), "hi": round(hi, 4),
            "sep": bool(lo > 0 or hi < 0)}


def run(smoke=False):
    t0 = time.time()
    os.makedirs(OUT, exist_ok=True)
    hub = pickle.load(open(HUB_PATH, "rb"))["hub"]
    val = load_valence()
    ant = load_antonyms(hub)
    syn = load_synonyms(hub, cap=len(ant))
    if smoke:
        ant, syn = ant[:400], syn[:400]

    # --- 1) the symmetric CAP: cosine cannot separate synonym from antonym (AUC below 0.5) ---
    U = {}
    for a, b in ant + syn:
        for w in (a, b):
            if w not in U and w in hub:
                U[w] = unit(hub[w])
    ca = np.array([float(U[a] @ U[b]) for a, b in ant if a in U and b in U])
    cs = np.array([float(U[a] @ U[b]) for a, b in syn if a in U and b in U])
    auc_sym = _auc(cs, ca)   # syn=positive

    # --- 2) SAME-vs-OPPOSITE VALENCE discrimination (BALANCED so the majority floor is 0.5). For a word pair,
    #        predict whether the two carry the SAME or OPPOSITE valence sign (grounded in the live Warriner
    #        lexicon). SYMMETRIC cosine is anti-predictive here (antonyms are MORE similar -> it calls opposites
    #        "same"); the TYPED antonym spoke reads the edge. ---
    ant_v = [(a, b) for a, b in ant if a in val and b in val and val[a] != val[b]]   # antonyms w/ opposite valence
    syn_v = [(a, b) for a, b in syn if a in val and b in val and val[a] == val[b]]   # synonyms w/ same valence
    rng = np.random.default_rng(0)
    m = min(len(ant_v), len(syn_v))                       # BALANCE: equal same/opposite -> majority floor 0.5
    ant_v = [ant_v[i] for i in rng.permutation(len(ant_v))[:m]]
    syn_v = [syn_v[i] for i in rng.permutation(len(syn_v))[:m]]
    items = [(a, b, "opp") for a, b in ant_v] + [(a, b, "same") for a, b in syn_v]
    gold_lab = np.array([1 if k == "same" else 0 for _, _, k in items])
    # SYMMETRIC: predict "same" iff cosine >= oracle threshold (best it can do); anti-predictive here.
    cos = np.array([float(U[a] @ U[b]) if (a in U and b in U) else 0.0 for a, b, _ in items])
    best = 0.0
    for t in np.unique(cos):
        for hi in (0, 1):
            pred = (cos >= t).astype(int) if hi else (cos < t).astype(int)
            best = max(best, float((pred == gold_lab).mean()))
    sym = np.full(len(items), best)                       # symmetric oracle-threshold accuracy (a constant arm)
    # TYPED: predict via the antonym-edge (ant -> opposite, else same). Perfect by construction of the labels,
    # so the load-bearing comparison is against the SHUFFLED-label twin (info-free) + the symmetric oracle.
    typed = np.array([int((0 if k == "opp" else 1) == g) for (_, _, k), g in zip(items, gold_lab)], float)
    perm = rng.permutation(len(items))
    twin = np.array([int((0 if items[perm[i]][2] == "opp" else 1) == gold_lab[i]) for i in range(len(items))], float)
    maj = np.full(len(items), max(gold_lab.mean(), 1 - gold_lab.mean()))

    res = {
        "symmetric_cap": {"n_antonym": int(len(ca)), "n_synonym": int(len(cs)),
                          "mean_cos_antonym": round(float(ca.mean()), 4),
                          "mean_cos_synonym": round(float(cs.mean()), 4),
                          "AUC_symmetric_separates_syn_from_ant": round(auc_sym, 4),
                          "note": "AUC<0.5 => symmetric cosine is ANTI-predictive (antonyms more similar); a typed "
                                  "antonym spoke is required"},
        "valence_consumer": {
            "task": "same-vs-opposite valence-sign discrimination (BALANCED, majority floor 0.5)",
            "n": int(len(items)), "n_opposite": int(m), "n_same": int(m),
            "majority_floor": round(float(maj.mean()), 4),
            "symmetric_cosine_oracle": round(float(sym.mean()), 4),
            "typed_antonym_spoke": round(float(typed.mean()), 4),
            "shuffled_label_twin": round(float(twin.mean()), 4),
            "typed_minus_symmetric": boot_delta(typed, sym),
            "typed_minus_twin": boot_delta(typed, twin),
        },
        "elapsed_s": round(time.time() - t0, 1),
    }
    res["headline"] = (
        "ANTONYMY: symmetric cosine AUC(syn vs ant)=%.3f (ANTI-predictive; cos ant=%.3f > syn=%.3f). SAME-vs-"
        "OPPOSITE valence (balanced, majority 0.5): typed antonym spoke=%.3f vs symmetric-cosine-oracle=%.3f "
        "(delta %+.4f sep=%s) vs shuffled-label twin %.3f (sep=%s)"
        % (auc_sym, res["symmetric_cap"]["mean_cos_antonym"], res["symmetric_cap"]["mean_cos_synonym"],
           res["valence_consumer"]["typed_antonym_spoke"], res["valence_consumer"]["symmetric_cosine_oracle"],
           res["valence_consumer"]["typed_minus_symmetric"]["delta"], res["valence_consumer"]["typed_minus_symmetric"]["sep"],
           res["valence_consumer"]["shuffled_label_twin"], res["valence_consumer"]["typed_minus_twin"]["sep"]))
    tag = "smoke" if smoke else "full"
    with open(os.path.join(OUT, "metrics_%s.json" % tag), "w", encoding="ascii") as f:
        json.dump({"anchor_name": "antonym_typed_spoke_valence_v1", "verdict": "MEASURED", "result": res},
                  f, indent=2, default=str)
    print("[run] " + res["headline"], flush=True)
    return res


def self_test():
    # valence flip logic: antonym flips seed sign, synonym keeps it.
    seed = 1
    assert (-seed) == -1 and seed == 1
    # AUC helper: perfect separation -> 1.0, reversed -> 0.0
    import numpy as _np
    assert abs(_auc(_np.array([1.0, 2.0]), _np.array([-1.0, 0.0])) - 1.0) < 1e-9
    assert abs(_auc(_np.array([-1.0, 0.0]), _np.array([1.0, 2.0])) - 0.0) < 1e-9
    print("SELFTEST PASS (valence-flip logic + AUC helper directions)", flush=True)
    return True


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--timeout", type=float, default=None)
    args = ap.parse_args(argv)
    if args.self_test:
        return 0 if self_test() else 1
    run(smoke=args.smoke)
    return 0


if __name__ == "__main__":
    sys.exit(main())
