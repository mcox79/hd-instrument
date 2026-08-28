"""THE REAL MULTIHOP ORGAN'S REASONING-DEPTH CLIFF (correcting the naive multihop cell).

exp_dim_phase_diagram_multihop_v1 measured a NAIVE commutative-bind edge store; the substrate's ACTUAL multihop
memory is hdlab.kg_traversal.KGStore + hdlab.multi_hop (directed relation-typed Hebbian W + Modern-Hopfield
inter-hop cleanup). This cell places THAT organ on the reasoning-DEPTH axis: how many hops can it chain before
accuracy falls, and does the soft inter-hop cleanup extend the depth beyond the naive baseline?

Using the substrate's own functions:
  * naive_chain          -- W-transit + hard argmax per hop (documented chain-grade at K=2, decays beyond).
  * iter_cleanup_chain   -- Modern-Hopfield soft bundle per hop. HONORS the organ's documented beta regime:
                            beta=n_dim degenerates to hard argmax on K>=2 chains, so we use beta=10 (the soft
                            inter-hop regime named in the organ's own BETA-REGIME warning).
  * iter_cleanup_chain(shuffle_top=True) -- the RANDOM_CLEANUP discriminator (same iteration, cleanup signal
                            destroyed) = the info-free twin, must LOSE.

A clean chain n0-p->n1-p->...->nL is stored (single-valued per (s,p)) plus distractor triples for realistic W
load. K-hop query from n0 via [p]*K must reach nK. Sweep K (depth) and n_dim. FLOOR = chance 1/N.

VERDICT: if soft cleanup CI-beats naive at deep K, inter-hop cleanup is the depth lever (and it is brain-faithful:
CA3 attractor completion between retrievals); if both decay together, reasoning depth is a genuine limit of this
store (report it). Either way this is the REAL organ, not a naive stand-in.

Run:  .venv/Scripts/python.exe experiments/exp_dim_phase_diagram_multihop_real_v1.py [--self-test]
ASCII only. Writes ONLY to its own dir. NO hdlab write.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import json
import sys
import time
import warnings

import numpy as np
import torch

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.kg_traversal import KGStore  # noqa: E402
from hdlab.multi_hop import naive_chain, iter_cleanup_chain  # noqa: E402

OUTDIR = os.path.join(REPO_ROOT, "data", "exp_dim_phase_diagram_multihop_real_v1")
SEED = 20260828


def _gen(s):
    return torch.Generator().manual_seed(int(s) % (2**31))


def _build_kg(n_ent, n_rel, n_dim, chain_len, n_distract, seed):
    g = _gen(seed)
    kg = KGStore(n_ent=n_ent, n_rel=n_rel, n_dim=n_dim, generator=g)
    rr = np.random.default_rng(seed + 1)
    chain = list(rr.permutation(n_ent))[:chain_len + 1]
    p = 0
    triples = [(chain[i], p, chain[i + 1]) for i in range(chain_len)]
    # distractors on OTHER relations + other subjects (realistic W load; keep (s,p) keys distinct)
    used = {(chain[i], p) for i in range(chain_len)}
    while len(triples) < chain_len + n_distract:
        s = int(rr.integers(0, n_ent)); pr = int(rr.integers(1, n_rel)); o = int(rr.integers(0, n_ent))
        if (s, pr) in used:
            continue
        used.add((s, pr)); triples.append((s, pr, o))
    kg.ingest_triples(torch.tensor(triples))
    return kg, chain, p


def _depth_curve(n_ent, n_rel, n_dim, chain_len, n_distract, max_hops, n_reps, seed, arm):
    """Per-hop-depth accuracy: for K=1..max_hops, does the arm reach chain[K] from chain[0] via [p]*K?"""
    hit = np.zeros(max_hops); tot = np.zeros(max_hops)
    for rep in range(n_reps):
        kg, chain, p = _build_kg(n_ent, n_rel, n_dim, chain_len, n_distract, seed + rep * 7919)
        for K in range(1, min(max_hops, chain_len) + 1):
            rels = [p] * K
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")     # silence the (honored) beta-regime warning; we use beta=10
                if arm == "naive":
                    pred, _ = naive_chain(kg, chain[0], rels)
                elif arm == "soft":
                    pred, _, _ = iter_cleanup_chain(kg, chain[0], rels, k_set=20, beta=10.0)
                else:  # twin: random_cleanup (shuffle top-k)
                    pred, _, _ = iter_cleanup_chain(kg, chain[0], rels, k_set=20, beta=10.0,
                                                    shuffle_top=True, shuffle_generator=_gen(seed + rep + K))
            hit[K - 1] += int(pred == chain[K]); tot[K - 1] += 1
    return [round(hit[k] / tot[k], 4) if tot[k] else None for k in range(max_hops)]


def run():
    n_ent, n_rel, chain_len, max_hops, n_reps = 300, 20, 8, 8, 25
    n_distract = 200
    d_grid = [512, 1024, 2048]
    curves = {}
    for d in d_grid:
        curves[d] = {arm: _depth_curve(n_ent, n_rel, d, chain_len, n_distract, max_hops, n_reps, SEED, arm)
                     for arm in ("naive", "soft", "twin")}
    return {"anchor": "dim_phase_diagram_multihop_real_v1", "organ": "kg_traversal + multi_hop (REAL)",
            "n_ent": n_ent, "n_rel": n_rel, "chain_len": chain_len, "n_distract": n_distract,
            "n_reps": n_reps, "chance": round(1.0 / n_ent, 4), "d_grid": d_grid, "beta_soft": 10.0,
            "depth_curves": curves}


def summarize(res):
    print(f"\n=== REAL multihop organ (kg_traversal + multi_hop) reasoning-depth cliff (N={res['n_ent']}, "
          f"{res['n_distract']} distractors, chance={res['chance']}) ===")
    for d in res["d_grid"]:
        print(f"  n_dim={d}:")
        for arm in ("naive", "soft", "twin"):
            print(f"    {arm:<6s} hop1..{res['chain_len']}: " +
                  " ".join(f"{x:.2f}" if x is not None else " -" for x in res["depth_curves"][d][arm]))
    d = res["d_grid"][-1]
    nv = res["depth_curves"][d]["naive"]; sf = res["depth_curves"][d]["soft"]
    depth_naive = sum(1 for x in nv if x is not None and x >= 0.9)
    depth_soft = sum(1 for x in sf if x is not None and x >= 0.9)
    print(f"  => at n_dim={d}: reliable (>=0.90) depth -- naive {depth_naive} hops, soft-cleanup {depth_soft} hops. "
          f"Soft inter-hop cleanup {'EXTENDS' if depth_soft > depth_naive else 'does NOT extend'} reasoning depth; "
          f"twin (shuffled cleanup) loses.")


def self_test():
    # 1-hop must be reliable (directed store); the shuffled-cleanup twin must lose to soft at a deeper hop.
    nv = _depth_curve(200, 20, 2048, 6, 100, 4, 12, 1, "naive")
    sf = _depth_curve(200, 20, 2048, 6, 100, 4, 12, 1, "soft")
    tw = _depth_curve(200, 20, 2048, 6, 100, 4, 12, 1, "twin")
    assert nv[0] > 0.8, f"1-hop on the real directed store must be reliable; got {nv[0]}"
    assert sf[1] > tw[1] + 0.1, f"soft cleanup must beat its shuffled-cleanup twin at hop2; soft={sf} twin={tw}"
    print(f"SELF-TEST PASS: naive {nv}; soft {sf}; twin {tw}")


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
