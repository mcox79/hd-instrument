"""RUNTIME VERIFICATION PART 2 -- what each static asset ACTUALLY contains, and what its
NEIGHBOURHOOD PURITY over OUR 5,491 anchors actually is. Nothing is trusted by name.

Also reproduces the defining statistic (0.46% of a word's top-20 store neighbours are its
synonyms) as a regression gate on the incumbent store before any asset is scored.
ASCII only. No LLM at any point: these are static tables read off disk.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import json
import sys
import time

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
os.environ.setdefault("GENSIM_DATA_DIR", os.path.join(_REPO, "data", "gensim_cache"))

import numpy as np  # noqa: E402

import experiments.exp_synonym_clumping_consolidation_v1 as SC  # noqa: E402

OUT = os.path.join(_REPO, "scratch", "foundation_purity")
os.makedirs(OUT, exist_ok=True)
GC = os.path.join(_REPO, "data", "gensim_cache")
R = {}

t0 = time.time()
D = SC.load_all()
anchors = D["anchors"]
syn = D["syn"]
print("[load_all] %.1fs n_anchors=%d" % (time.time() - t0, len(anchors)), flush=True)


def purity(S, k=20, sample=1500, seed=7):
    """frac of a word's top-k neighbours that are its WordNet synonyms (morphological variants
    already removed upstream), plus the frac of words with AT LEAST ONE synonym in the top k."""
    Sn = SC.l2n(S)
    idx, _v = SC.topm_neighbours(Sn, k)
    rs = np.random.default_rng(seed)
    live = np.flatnonzero(np.linalg.norm(Sn, axis=1) > 1e-6)
    sub = live if live.size <= sample else np.sort(rs.choice(live, sample, replace=False))
    hit = tot = anyh = nw = 0
    for i in sub:
        mm = syn.get(int(i))
        if mm is None or mm.size == 0:
            continue
        nw += 1
        ss = set(mm.tolist())
        h = sum(1 for j in idx[i].tolist() if j in ss)
        hit += h
        tot += k
        anyh += 1 if h else 0
    return {"k": k, "n_words_scored": nw,
            "PURITY_frac_of_topk_that_are_SYNONYMS": round(hit / max(tot, 1), 5),
            "frac_of_words_with_a_synonym_in_topk": round(anyh / max(nw, 1), 4)}


# ---------------------------------------------------------------- regression gate on the store
R["INCUMBENT_STORE_purity20"] = purity(D["mat"], 20)
R["INCUMBENT_STORE_purity1"] = purity(D["mat"], 1)
print("[regression] store purity20 =", R["INCUMBENT_STORE_purity20"], flush=True)


def load_kv(path, binary, limit=None):
    from gensim.models import KeyedVectors
    return KeyedVectors.load_word2vec_format(path, binary=binary, limit=limit)


ASSETS = [
    ("glove-wiki-gigaword-300", "glove-wiki-gigaword-300.gz", False, None),
    ("word2vec-google-news-300", "word2vec-google-news-300.gz", True, 600000),
    ("fasttext-wiki-news-subwords-300", "fasttext-wiki-news-subwords-300.gz", False, 600000),
]
R["assets"] = {}
for name, fn, binary, limit in ASSETS:
    p = os.path.join(GC, name, fn)
    t = time.time()
    try:
        kv = load_kv(p, binary, limit)
    except Exception as e:
        R["assets"][name] = {"LOAD_FAILED": repr(e)[:300]}
        print("[asset] %s LOAD FAILED %r" % (name, e), flush=True)
        continue
    dim = int(kv.vector_size)
    X = np.zeros((len(anchors), dim), dtype=np.float32)
    hitv = np.zeros(len(anchors), dtype=bool)
    for i, w in enumerate(anchors):
        for cand in (w, w.capitalize(), w.upper()):
            if cand in kv.key_to_index:
                X[i] = kv[cand]
                hitv[i] = True
                break
    ent = {"path": p, "load_s": round(time.time() - t, 1), "vocab": int(len(kv.key_to_index)),
           "dim": dim, "anchor_coverage": round(float(hitv.mean()), 4),
           "n_covered": int(hitv.sum()),
           "SANITY_cos_king_queen": None, "SANITY_cos_king_banana": None}
    try:
        ent["SANITY_cos_king_queen"] = round(float(kv.similarity("king", "queen")), 4)
        ent["SANITY_cos_king_banana"] = round(float(kv.similarity("king", "banana")), 4)
    except Exception:
        pass
    ent["purity20"] = purity(X, 20)
    ent["purity1"] = purity(X, 1)
    np.savez_compressed(os.path.join(OUT, "asset_%s.npz" % name.replace("-", "_")),
                        X=X, hit=hitv)
    R["assets"][name] = ent
    print("[asset] %s %s" % (name, json.dumps(ent)), flush=True)
    del kv, X

# ---------------------------------------------------------------- CSKG, by reading it
ck = os.path.join(_REPO, "data", "cskg_foundation_v1")
if os.path.isdir(ck):
    fs = sorted(os.listdir(ck))
    rec = None
    shard = [f for f in fs if f.startswith("edges_shard")]
    if shard:
        with open(os.path.join(ck, shard[0]), "r", encoding="utf-8") as fh:
            rec = json.loads(fh.readline())
    R["cskg_foundation_v1"] = {"files": fs[:12], "n_shards": len(shard), "first_record": rec}
    print("[cskg]", json.dumps(R["cskg_foundation_v1"])[:900], flush=True)

R["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
with open(os.path.join(OUT, "runtime_verify_part2.json"), "w", encoding="ascii") as fh:
    json.dump(R, fh, indent=1, default=str)
print("WROTE", os.path.join(OUT, "runtime_verify_part2.json"), flush=True)
