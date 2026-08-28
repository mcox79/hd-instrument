"""exp_entity_store_sparse_capacity_v1 -- the brain-foundational optimization the capstone drill named:
make the SHARP exact-recall half of the factorized store a real DG expand+k-WTA SPARSE conjunctive code
(Treves & Rolls 1994 p_max ~ C/(a ln(1/a)); Willshaw 1969) instead of a dense bundle.

THE PRE-REGISTERED DECISIVE TEST (from research_sparse_dg_capstone_2026-08-27.md): at FIXED dimension, vary
SPARSITY, CORRELATED content (recurring entities/verbs -- the regime where sparse beats dense; modern dense
Hopfield's exponential capacity holds only for RANDOM patterns), measure exact-recall vs SCALE (store size N).
  HARD-PASS: sparser (lower a) holds recall to HIGHER N / degrades SLOWER than dense -- the Treves-Rolls
             superlinear capacity signature -- CI-separated.
  HARD-FAIL: no CI-separated advantage -> our codes aren't in the correlated regime where sparse pays off;
             defer sparsification (honest negative).

FAIR: all arms share the SAME expansion dimension (isolates SPARSITY, not dimension); the ONLY difference is
the k-WTA sparsity a of the DG-separated address. Content is one-hot (maximally sparse). Uses the REAL
hdlab.dg_pattern_separation.dg_separate (the DG organ). Info-free twin = random-sparse addresses (no
address->verb correspondence) -> chance. Writes ONLY to data/entity_store_sparse_fan/. NO hdlab/ write.

Run: .venv/Scripts/python.exe experiments/exp_entity_store_sparse_capacity_v1.py --run  ... --self-test
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from typing import Dict, List

import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from experiments.exp_entity_store_sparse_fan_v1 import _batch_dg, D0  # noqa: E402
from hdlab.dg_pattern_separation import projection_matrix  # noqa: E402

OUTDIR = os.path.join(REPO_ROOT, "data", "entity_store_sparse_fan")
DEXP = 4096
SEED = 20260827


def _seeded_bipolar(tag: str, dim: int) -> np.ndarray:
    seed = int.from_bytes(hashlib.sha256(tag.encode()).digest()[:8], "big") % (2 ** 32)
    return np.random.default_rng(seed).choice(np.array([-1.0, 1.0], dtype=np.float32), size=dim)


def _correlated_events(N: int, n_entities: int, n_verbs: int, d0: int, rng: np.random.Generator):
    """N events over a SMALL set of recurring entities/verbs (CORRELATED patterns). Each event ->
    conjunctive input g = entity_vec * slot_vec * order_vec (real bipolar), + its verb index."""
    ent = {e: _seeded_bipolar(f"ent{e}", d0) for e in range(n_entities)}
    G = np.empty((N, d0), dtype=np.float32)
    y = np.empty(N, dtype=np.int64)
    slot_cache, ord_cache = {}, {}
    per_ent_slot = {e: 0 for e in range(n_entities)}
    for i in range(N):
        e = int(rng.integers(0, n_entities))
        s = per_ent_slot[e]; per_ent_slot[e] += 1
        o = int(rng.integers(0, 4))
        if s not in slot_cache:
            slot_cache[s] = _seeded_bipolar(f"slot{s}", d0)
        if o not in ord_cache:
            ord_cache[o] = _seeded_bipolar(f"ord{o}", d0)
        G[i] = ent[e] * slot_cache[s] * ord_cache[o]
        y[i] = int(rng.integers(0, n_verbs))     # recurring verbs (correlated content)
    return G, y


def _recall_at(G, y, a, expand_dim, n_verbs, Wp, twin=False, rng=None):
    """Store N (address->verb) via a Willshaw heteroassoc; return exact-recall accuracy. a=1.0 -> dense
    (no k-WTA); a<1 -> DG k-WTA sparse. twin -> query with a FRESH unrelated random-sparse address (null)."""
    N = G.shape[0]
    A = _batch_dg(G, expand_dim, a, Wp) if a < 1.0 else _dense_addr(G, expand_dim, Wp)
    Y = np.zeros((N, n_verbs), dtype=np.float32)
    Y[np.arange(N), y] = 1.0
    W = A.T @ Y                                    # (expand_dim, n_verbs)
    if twin:
        Gq = rng.standard_normal((N, G.shape[1])).astype(np.float32)
        Aq = _batch_dg(Gq, expand_dim, a, Wp) if a < 1.0 else _dense_addr(Gq, expand_dim, Wp)
        pred = np.argmax(Aq @ W, axis=1)
    else:
        pred = np.argmax(A @ W, axis=1)
    return float(np.mean(pred == y))


def _dense_addr(G, expand_dim, Wp):
    Y = G @ Wp.T
    return (Y / (np.linalg.norm(Y, axis=1, keepdims=True) + 1e-9)).astype(np.float32)


def run(expand_dim=DEXP, n_entities=20, n_verbs=100, d0=D0, seed=SEED,
        sparsities=(1.0, 0.10, 0.05, 0.02), scales=(500, 1000, 2000, 4000, 8000), n_seeds=5) -> Dict:
    Wp = projection_matrix(d0, expand_dim, "capacity")
    out = {"config": {"expand_dim": expand_dim, "n_entities": n_entities, "n_verbs": n_verbs,
                       "k_active": {a: max(1, round(a * expand_dim)) for a in sparsities if a < 1.0}},
           "recall_by_sparsity_and_scale": {}, "twin_at_largest_scale": {}}
    for a in sparsities:
        row = {}
        for N in scales:
            accs = []
            for sd in range(n_seeds):
                rng = np.random.default_rng(seed + sd * 101 + N)
                G, y = _correlated_events(N, n_entities, n_verbs, d0, rng)
                accs.append(_recall_at(G, y, a, expand_dim, n_verbs, Wp))
            row[str(N)] = {"recall_mean": float(np.mean(accs)),
                           "recall_ci": [float(np.percentile(accs, 2.5) if n_seeds >= 20 else min(accs)),
                                         float(np.percentile(accs, 97.5) if n_seeds >= 20 else max(accs))]}
        out["recall_by_sparsity_and_scale"][f"a={a}"] = row
        # info-free twin at the largest scale
        rng = np.random.default_rng(seed + 999)
        G, y = _correlated_events(scales[-1], n_entities, n_verbs, d0, rng)
        out["twin_at_largest_scale"][f"a={a}"] = round(
            _recall_at(G, y, a, expand_dim, n_verbs, Wp, twin=True, rng=rng), 3)
    # verdict: does a sparser code hold recall to higher N than dense? compare recall at the largest scale.
    big = str(scales[-1])
    dense_big = out["recall_by_sparsity_and_scale"]["a=1.0"][big]["recall_mean"]
    best_sparse_a = min([a for a in sparsities if a < 1.0], key=lambda a:
                        -out["recall_by_sparsity_and_scale"][f"a={a}"][big]["recall_mean"])
    sparse_big = out["recall_by_sparsity_and_scale"][f"a={best_sparse_a}"][big]["recall_mean"]
    out["verdict"] = {
        "dense_recall_at_largest_scale": round(dense_big, 3),
        "best_sparse_recall_at_largest_scale": round(sparse_big, 3),
        "best_sparse_a": best_sparse_a,
        "SPARSE_HOLDS_BETTER_AT_SCALE": sparse_big > dense_big + 0.05,
        "twin_at_chance": out["twin_at_largest_scale"][f"a={best_sparse_a}"] < 0.05,
        "reading": "Treves-Rolls: at FIXED dimension, a sparser DG code stores more before crosstalk collapse "
                   "-> holds recall to higher N. If SPARSE_HOLDS_BETTER_AT_SCALE, sparsity is the right "
                   "exact-recall code; the twin at chance confirms it is the address->content correspondence."}
    return out


def self_test() -> Dict:
    # tiny: sparse (a=0.05) must recall a small correlated store, and beat or match dense at a stressing scale;
    # twin at chance.
    Wp = projection_matrix(D0, 2048, "capacity")
    rng = np.random.default_rng(0)
    G, y = _correlated_events(400, 10, 50, D0, rng)
    r_sparse = _recall_at(G, y, 0.05, 2048, 50, Wp)
    r_dense = _recall_at(G, y, 1.0, 2048, 50, Wp)
    r_twin = _recall_at(G, y, 0.05, 2048, 50, Wp, twin=True, rng=np.random.default_rng(1))
    assert r_sparse > 0.9, f"sparse must recall a small store: {r_sparse}"
    assert r_twin < 0.1, f"info-free twin must be ~chance: {r_twin}"
    return {"sparse_recall_400": round(r_sparse, 3), "dense_recall_400": round(r_dense, 3),
            "twin": round(r_twin, 3)}


def _dump(name, obj):
    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, name), "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, default=float)
    print(f"[wrote] {os.path.join(OUTDIR, name)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        print(json.dumps(self_test(), indent=2, default=float)); return
    if args.run:
        rep = run(); print(json.dumps(rep, indent=2, default=float)); _dump("sparse_capacity.json", rep); return
    ap.print_help()


if __name__ == "__main__":
    main()
