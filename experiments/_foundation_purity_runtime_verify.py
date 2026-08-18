"""RUNTIME VERIFICATION for the foundation-purity build. Nothing is trusted by name or docstring.

Answers, by importing and observing rather than by grepping:
  1. what the cached store/query artifacts ACTUALLY contain (keys, shapes, dtypes)
  2. whether Q_exact is the word's OWN row (which decides whether instrument B's exact-key arm
     generalises natively to a store in a different vector space)
  3. what each static asset on disk ACTUALLY is, and its coverage of our 5,491 anchors
  4. whether the ruler and the floor battery behave on a planted answer
ASCII only. No LLM. Writes only to scratch/foundation_purity/.
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

import numpy as np  # noqa: E402

OUT = os.path.join(_REPO, "scratch", "foundation_purity")
os.makedirs(OUT, exist_ok=True)
CACHE = os.path.join(_REPO, "scratch", "sparse_code_real_task", "real_cache.npz")
AUX = os.path.join(_REPO, "scratch", "sparsify_right_object", "aux_v2.npz")

R = {}


def l2n(A):
    A = np.asarray(A, dtype=np.float32)
    return (A / np.maximum(np.linalg.norm(A, axis=-1, keepdims=True), 1e-12)).astype(np.float32)


# ---------------------------------------------------------------- 1. the cached artifacts
z = np.load(CACHE, allow_pickle=True)
a = np.load(AUX, allow_pickle=True)
R["real_cache_keys"] = {k: [list(np.shape(z[k])), str(np.asarray(z[k]).dtype)] for k in z.files}
R["aux_v2_keys"] = {k: [list(np.shape(a[k])), str(np.asarray(a[k]).dtype)] for k in a.files}

anchors = [str(x) for x in z["anchors"].tolist()]
pos = {w: i for i, w in enumerate(anchors)}
mat = np.asarray(z["mat"], dtype=np.float32)
keep = np.asarray(z["keep"], dtype=bool)
L_words = [str(x) for x in z["L_words"].tolist()]
rows = np.flatnonzero(keep)
items = np.array([pos[L_words[i]] for i in rows], dtype=np.int64)
Qe = np.asarray(z["Q_exact"], dtype=np.float32)
Qp = np.asarray(z["Q_part"], dtype=np.float32)

# ---------------------------------------------------------------- 2. IS Q_exact the own row?
Sn = l2n(mat)
Qen = l2n(Qe[rows])
same = np.array([float(np.dot(Sn[items[c]], Qen[c])) for c in range(min(500, items.size))])
R["Q_exact_IS_the_own_row"] = {
    "mean_cos_Qexact_to_own_store_row_first500": round(float(np.mean(same)), 6),
    "min": round(float(np.min(same)), 6),
    "frac_above_0.999": round(float(np.mean(same > 0.999)), 4),
    "WHY_IT_MATTERS": "if Q_exact IS the word's own row then instrument B's EXACT-KEY arm is "
                      "'rank all anchors by similarity to this word's own representation, gold = "
                      "its WordNet meaning set, itself excluded' -- which generalises NATIVELY to "
                      "a store in ANY vector space. If it is not, a foundation in a different "
                      "space cannot be scored on instrument B without a learned projection."}
Qpn = l2n(Qp[rows])
samep = np.array([float(np.dot(Sn[items[c]], Qpn[c])) for c in range(min(500, items.size))])
R["Q_part_vs_own_row"] = {"mean_cos_first500": round(float(np.mean(samep)), 6)}

# ---------------------------------------------------------------- 3. the static assets
R["assets"] = {}
try:
    import gensim  # noqa
    R["assets"]["gensim_version"] = gensim.__version__
except Exception as e:  # pragma: no cover
    R["assets"]["gensim_version"] = "IMPORT FAILED: %r" % (e,)

GC = os.path.join(_REPO, "data", "gensim_cache")
for name in sorted(os.listdir(GC)):
    p = os.path.join(GC, name)
    if os.path.isdir(p):
        R["assets"][name] = {"files": sorted(os.listdir(p)),
                             "bytes": {f: os.path.getsize(os.path.join(p, f))
                                       for f in os.listdir(p) if os.path.isfile(os.path.join(p, f))}}

# WordNet, by runtime
try:
    from nltk.corpus import wordnet as wn
    R["assets"]["wordnet"] = {"n_synsets_probe_dog": len(wn.synsets("dog")),
                              "lemma_names_dog_n_01": wn.synset("dog.n.01").lemma_names()}
except Exception as e:
    R["assets"]["wordnet"] = "FAILED: %r" % (e,)

# CSKG, by reading one line
cskg_dir = os.path.join(_REPO, "data", "cskg")
if os.path.isdir(cskg_dir):
    shards = sorted(f for f in os.listdir(cskg_dir) if f.startswith("edges_shard"))
    rec = None
    if shards:
        with open(os.path.join(cskg_dir, shards[0]), "r", encoding="utf-8") as fh:
            rec = json.loads(fh.readline())
    R["assets"]["cskg"] = {"n_shards": len(shards), "first_record": rec,
                           "total_bytes": sum(os.path.getsize(os.path.join(cskg_dir, f))
                                              for f in shards)}

# thematic graph, by loading it
import pickle  # noqa: E402
TH = os.path.join(_REPO, "data", "thematic_relations_v1", "thematic_edges_v1.pkl")
with open(TH, "rb") as fh:
    d = pickle.load(fh)
R["assets"]["thematic_relations_v1"] = {
    "type": type(d).__name__,
    "keys": sorted(list(d.keys()))[:20] if isinstance(d, dict) else None,
    "n_event": len(d.get("event", [])) if isinstance(d, dict) else None,
    "first_event_record": [str(x) for x in d["event"][0]] if isinstance(d, dict) and d.get("event")
    else None}

# ---------------------------------------------------------------- 4. the ruler + the floors
import tools.floor_battery as FB  # noqa: E402

rng = np.random.default_rng(0)
Sfake = l2n(rng.normal(size=(200, 32)).astype(np.float32))
Qfake = Sfake[np.arange(50)]
Sc = (Sfake @ Qfake.T).astype(np.float32)
elig = np.ones((200, 50), dtype=bool)
gold = np.zeros((200, 50), dtype=bool)
gold[np.arange(50), np.arange(50)] = True
h = FB.hit_at_1_both_tie_conventions(Sc, elig, gold)
R["floor_battery_planted_answer"] = {"hit_exp": round(float(np.mean(h["hit_exp"])), 6),
                                     "keys": sorted(h.keys())}
R["floor_battery_public_names"] = sorted(n for n in dir(FB) if not n.startswith("_"))

from experiments.exp_task_degeneracy_v1 import ruler_mode_gate  # noqa: E402

R["ruler_mode_gate"] = ruler_mode_gate()
R["argv_has_smoke"] = any("--smoke" == x for x in sys.argv)

R["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
with open(os.path.join(OUT, "runtime_verify_part1.json"), "w", encoding="ascii") as fh:
    json.dump(R, fh, indent=1, default=str)
print(json.dumps(R, indent=1, default=str)[:6000])
print("WROTE", os.path.join(OUT, "runtime_verify_part1.json"))
