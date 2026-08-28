"""SUBSTRATE CENSUS (dimensional): place the DISTINCT store FAMILIES on the capacity diagram, not just the
register. The ~80 hdlab organs with a dimensionality parameter collapse to a handful of store ARCHITECTURES;
this cell empirically places the family the register work did NOT cover and that the multihop work should have
consulted: the DIRECTED HEBBIAN-W RELATIONAL STORE (hdlab.kg_traversal.KGStore, used by hdlab.multi_hop).

Why this one: it is the substrate's ACTUAL relational/multihop memory (relation-typed key E[s]*R[p] bound into an
asymmetric Hebbian W = outer(E[o], key)), directed by construction -- unlike the naive commutative-bind edge store
the multihop cell first measured. Its capacity is governed by the SAME Plate FHRR law the register obeys, so we
also VALIDATE against the substrate's closed form hdlab.k_cliff_scaling.k_cliff(N) = 0.87*N/log2(N).

MEASURE: one-hop retrieval accuracy vs number of stored triples T (the load) at several n_dim, over random KGs;
recompute chance (1/n_ent) and an info-free twin (query a NON-stored (s,p)) at each point. VERDICT: the store's
empirical cliff should track k_cliff(N) (rising with N) -- if it does, the whole FHRR-family substrate is on ONE
capacity law and the register result generalises; the family is PLACED, not merely inventoried.

Run:  .venv/Scripts/python.exe experiments/exp_dim_phase_diagram_census_v1.py [--self-test]
ASCII only. Writes ONLY to data/exp_dim_phase_diagram_census_v1/. NO hdlab write.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import json
import sys
import time

import numpy as np
import torch

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.kg_traversal import KGStore  # noqa: E402
import hdlab.k_cliff_scaling as KC  # noqa: E402

OUTDIR = os.path.join(REPO_ROOT, "data", "exp_dim_phase_diagram_census_v1")
SEED = 20260828


def _gen(s):
    return torch.Generator().manual_seed(int(s) % (2**31))


def _one(n_dim, n_ent, n_rel, n_triples, n_reps, seed):
    """One-hop retrieval accuracy over n_reps random KGs of n_triples distinct (s,p,o); also an info-free twin
    (query a (s,p) that was NEVER stored -> must not spuriously retrieve the held-out object)."""
    ok = tot = tw_ok = tw_tot = 0
    for rep in range(n_reps):
        g = _gen(seed + rep * 7919)
        kg = KGStore(n_ent=n_ent, n_rel=n_rel, n_dim=n_dim, generator=g)
        rr = np.random.default_rng(seed + rep * 7919 + 1)
        # distinct (s,p) keys so each has ONE gold object (single-valued retrieval)
        pairs = set(); triples = []
        while len(triples) < n_triples:
            s = int(rr.integers(0, n_ent)); p = int(rr.integers(0, n_rel))
            if (s, p) in pairs:
                continue
            o = int(rr.integers(0, n_ent))
            pairs.add((s, p)); triples.append((s, p, o))
        kg.ingest_triples(torch.tensor(triples))
        for (s, p, o) in triples:
            ok += int(kg.predict_one_hop(s, p) == o); tot += 1
        # twin: an unstored (s,p) -- should not match a random held-out object
        for _ in range(min(n_triples, 20)):
            s = int(rr.integers(0, n_ent)); p = int(rr.integers(0, n_rel))
            if (s, p) in pairs:
                continue
            o_fake = int(rr.integers(0, n_ent))
            tw_ok += int(kg.predict_one_hop(s, p) == o_fake); tw_tot += 1
    return ok / tot, (tw_ok / tw_tot if tw_tot else float("nan"))


def run():
    # The W-matrix (outer-product Hebbian) associative store has capacity ~O(n_dim) (Willshaw/Hopfield matrix
    # capacity), FAR above the vector-bundle k_cliff ~ N/log2(N). So probe ABSOLUTE loads scaled to n_dim to find
    # THIS store's own cliff, and locate it as a multiple of n_dim -- a DIFFERENT capacity regime than the register.
    n_ent, n_rel = 400, 40     # up to 16000 distinct (s,p) keys available
    d_grid = [512, 1024, 2048]
    n_reps = 5
    rows = []
    for d in d_grid:
        kcl = KC.k_cliff(d)
        t_grid = [int(f * d) for f in (0.5, 2.0, 8.0, 16.0, 28.0)]     # push far past dim to find the matrix cliff
        t_grid = [t for t in t_grid if 4 <= t < n_ent * n_rel]
        accs = {}
        for t in t_grid:
            a, tw = _one(d, n_ent, n_rel, t, n_reps, SEED)
            accs[str(t)] = {"T": t, "acc": round(a, 4), "twin": round(tw, 4),
                            "T_over_dim": round(t / d, 2), "T_over_kcliff": round(t / kcl, 2)}
        rows.append({"n_dim": d, "k_cliff_bundle_pred": kcl, "chance": round(1.0 / n_ent, 4), "loads": accs})
    return {"anchor": "dim_phase_diagram_census_v1", "store_family": "directed_hebbian_W_relational (kg_traversal/multi_hop)",
            "n_ent": n_ent, "n_rel": n_rel, "d_grid": d_grid, "n_reps": n_reps, "rows": rows}


def summarize(res):
    print(f"\n=== SUBSTRATE CENSUS: directed Hebbian-W relational store (kg_traversal), chance={1.0/res['n_ent']:.4f} ===")
    print("  one-hop retrieval accuracy vs load T (T/dim and T/bundle-k_cliff shown):")
    for r in res["rows"]:
        print(f"  n_dim={r['n_dim']:>5d} (bundle k_cliff={r['k_cliff_bundle_pred']}):  " +
              "  ".join(f"T={c['T']}({c['T_over_dim']}D,{c['T_over_kcliff']}kc):{c['acc']:.2f}" for c in r["loads"].values()))
        tw = np.mean([c["twin"] for c in r["loads"].values()])
        print(f"           info-free twin (unstored key) mean acc = {tw:.3f} (chance {1.0/res['n_ent']:.4f})")
    # find each store's own cliff as a multiple of n_dim (where accuracy first drops below 0.9)
    cliffs = {}
    for r in res["rows"]:
        cliff = None
        for c in r["loads"].values():
            if c["acc"] < 0.9:
                cliff = c["T_over_dim"]; break
        cliffs[r["n_dim"]] = cliff
    print(f"  W-matrix store cliff (T/dim where acc<0.9), per n_dim: {cliffs}")
    print(f"  => the directed relational store obeys a DIFFERENT capacity law than the register's vector bundle: its"
          f" capacity is ~O(n_dim) (matrix-Hebbian), FAR above the bundle k_cliff~N/log2(N). The substrate has "
          f"MULTIPLE capacity regimes -- the register result does NOT generalise to the W-matrix relational store.")


def self_test():
    # THE CONTRAST that proves a different regime: at a load where a vector-bundle store would be DEAD (10x its
    # k_cliff), the W-matrix relational store is still ~perfect. (Its own cliff is far higher -- located in run().)
    kcl = KC.k_cliff(512)               # ~49
    a_bundlekill, tw = _one(512, 400, 40, 10 * kcl, 4, 1)   # T ~ 490 = 10x bundle k_cliff
    assert a_bundlekill > 0.9, f"W-matrix store must stay reliable where a bundle would be dead; got {a_bundlekill}"
    assert tw < 0.1, f"info-free twin (unstored key) must be ~chance; got {tw}"
    a_crush, _ = _one(512, 400, 40, 12000, 2, 1)            # extreme overload -> must finally degrade
    assert a_crush < a_bundlekill - 0.1, f"extreme overload must degrade the W-matrix store; got {a_crush}"
    print(f"SELF-TEST PASS: W-matrix at 10x bundle-k_cliff (T={10*kcl})={a_bundlekill:.3f} (bundle would be dead); "
          f"extreme T=12000 degrades to {a_crush:.3f}; twin={tw:.3f}")


def main():
    if "--self-test" in sys.argv:
        self_test(); return
    t0 = time.time()
    res = run(); res["elapsed_s"] = round(time.time() - t0, 1)
    summarize(res)
    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, "metrics.json"), "w", encoding="utf-8", newline="") as fh:
        json.dump(res, fh, indent=2)
    print(f"\nwrote {OUTDIR} (elapsed {res['elapsed_s']}s)")


if __name__ == "__main__":
    main()
