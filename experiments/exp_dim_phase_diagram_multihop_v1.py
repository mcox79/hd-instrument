"""THE MULTIHOP / REASONING capacity cliff -- the dimension the single-shot storage diagram does NOT capture.

Storing a fact is one bind+bundle; REASONING over facts is a CHAIN of retrievals, and crosstalk COMPOUNDS per
hop (each retrieval is noisy, and an error at hop k dooms every later hop). This is the capacity axis behind
multihop QA / transitive inference -- and it is NOT the same as the storage cliff (a store can hold 1000 facts
cleanly yet fail a 4-hop chain).

SETUP (brain-relevant): a successor graph of N nodes with a chain n0->n1->...->nL is stored as ONE associative
bundle  S = SUM_i bind(node_i, node_{i+1})  (L superposed edges = the bundle load). A K-hop query from n0 walks
the chain: cur=n0; repeat K times cur = cleanup(unbind(S, cur)); correct iff cur == n_K. This is exactly the
substrate's event->event CausalLinkRegister chain (hdlab.situation_model_accumulate.CausalLinkRegister), measured
here as a clean phase diagram.

READOUTS compared per hop:
  * ARGMAX      -- single-shot nearest-codeword (the organ's current cleanup).
  * CA3/ITER    -- iterative attractor completion per hop (Treves & Rolls; the brain's recurrent settle).
Swept over K (hops), D (dimension), L (chain length = bundle load). FLOOR = chance 1/N; TWIN = shuffled-edge
store (info-free -> must collapse). CAN-FAIL: if depth falls off a cliff that D does NOT push, multihop is
capacity-bound (a real limit to report); if D or the better readout pushes it, that is the lever.

Run:  .venv/Scripts/python.exe experiments/exp_dim_phase_diagram_multihop_v1.py [--self-test]
ASCII only. Writes ONLY to data/exp_dim_phase_diagram_multihop_v1/. NO hdlab write.
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

from hdlab import binding  # noqa: E402
from hdlab.situation_model_accumulate import unit_phase_vec  # noqa: E402

OUTDIR = os.path.join(REPO_ROOT, "data", "exp_dim_phase_diagram_multihop_v1")
SEED = 20260828


def _gen(s):
    return torch.Generator().manual_seed(int(s) % (2**31))


def _argmax(readback, node_mat):
    return int(torch.argmax(torch.real(torch.conj(node_mat) @ readback)))


def _iter_complete(readback, node_mat, steps=4, temp=None):
    """CA3-style iterative attractor completion: softmax-weighted pull toward the node codebook, repeated.
    Returns the final argmax index. temp defaults to sqrt(d) scaling (cosine attractor)."""
    d = readback.shape[0]
    x = readback
    tau = temp if temp is not None else float(np.sqrt(d))
    idx = _argmax(x, node_mat)
    for _ in range(steps):
        sims = torch.real(torch.conj(node_mat) @ x) / tau          # [N]
        w = torch.softmax(sims, dim=0).to(node_mat.dtype)          # attractor weights
        x = (w @ node_mat)                                          # pulled toward basin
        ni = int(torch.argmax(torch.real(torch.conj(node_mat) @ x)))
        if ni == idx:
            break
        idx = ni
    return idx


def _roll(v):        # permutation protection (unitary; breaks bind's commutativity -> DIRECTED edge)
    return torch.roll(v, 1)


def _unroll(v):
    return torch.roll(v, -1)


def _one(d, n_nodes, chain_len, max_hops, n_reps, seed, readout="argmax", shuffle=False, directed=True):
    """Per-hop accuracy up to max_hops, averaged over n_reps random chains. Returns acc[k] for k=1..max_hops.

    directed=True: store edge as bind(head, roll(tail)) -- permutation protection makes the edge DIRECTED
    (FHRR bind is commutative, so bind(head,tail) is UNDIRECTED and a chain is 50/50 lost per hop). Hop:
    inverse-roll the readback before cleanup. directed=False reproduces the naive undirected store (the
    can-fail control that shows symmetric binding breaks directed reasoning)."""
    hit = np.zeros(max_hops); tot = np.zeros(max_hops)
    for rep in range(n_reps):
        g = _gen(seed + rep * 7919)
        nodes = [unit_phase_vec(d, g) for _ in range(n_nodes)]
        node_mat = torch.stack(nodes, dim=0)
        rr = np.random.default_rng(seed + rep * 7919 + 1)
        chain = list(rr.permutation(n_nodes))[:chain_len + 1]
        edges = [(chain[i], chain[i + 1]) for i in range(len(chain) - 1)]
        store_edges = edges
        if shuffle:                                                 # info-free twin: random head->tail pairing
            tails = list(rr.permutation([t for _, t in edges]))
            store_edges = [(edges[i][0], tails[i]) for i in range(len(edges))]

        def _edge(h, t):
            return binding.bind(nodes[h], _roll(nodes[t]) if directed else nodes[t])
        S = _edge(*store_edges[0])
        for e in store_edges[1:]:
            S = S + _edge(*e)
        cur = nodes[chain[0]]
        for k in range(1, min(max_hops, len(chain) - 1) + 1):
            rb = binding.unbind(S, cur)
            if directed:
                rb = _unroll(rb)
            ci = _iter_complete(rb, node_mat) if readout == "iter" else _argmax(rb, node_mat)
            cur = node_mat[ci]
            hit[k - 1] += int(ci == chain[k]); tot[k - 1] += 1
    return [round(hit[k] / tot[k], 4) if tot[k] else None for k in range(max_hops)]


def run():
    n_nodes = 60
    chain_len = 8                # 8 edges stored; ask up to 8 hops
    max_hops = 8
    n_reps = 60
    d_grid = [256, 512, 1024, 2048, 4096]
    chance = 1.0 / n_nodes
    curves = {}
    for d in d_grid:
        curves[d] = {"argmax": _one(d, n_nodes, chain_len, max_hops, n_reps, SEED, "argmax"),
                     "iter": _one(d, n_nodes, chain_len, max_hops, n_reps, SEED, "iter")}
    twin = _one(1024, n_nodes, chain_len, max_hops, n_reps, SEED, "argmax", shuffle=True)
    undirected = _one(1024, n_nodes, chain_len, max_hops, n_reps, SEED, "argmax", directed=False)  # symmetric-bind control
    # load axis: at fixed D=1024, vary chain length (bundle load) and read the 4-hop accuracy
    load_rows = []
    for L in [4, 8, 16, 32, 64]:
        c = _one(1024, n_nodes if n_nodes > L else L + 2, L, min(L, 8), max(n_reps // 2, 30), SEED + 5, "argmax")
        ci = _one(1024, n_nodes if n_nodes > L else L + 2, L, min(L, 8), max(n_reps // 2, 30), SEED + 5, "iter")
        load_rows.append({"chain_len": L, "hop4_argmax": c[3] if len(c) > 3 else None,
                          "hop4_iter": ci[3] if len(ci) > 3 else None})
    return {"anchor": "dim_phase_diagram_multihop_v1", "n_nodes": n_nodes, "chain_len": chain_len,
            "max_hops": max_hops, "n_reps": n_reps, "chance": round(chance, 4), "d_grid": d_grid,
            "curves": curves, "shuffled_twin_D1024": twin, "undirected_naive_bind_D1024": undirected,
            "load_sweep_D1024": load_rows}


def summarize(res):
    print(f"\n=== MULTIHOP reasoning cliff (successor-chain retrieval; N={res['n_nodes']} nodes, "
          f"chain={res['chain_len']} edges, chance={res['chance']}) ===")
    print("  accuracy at hop k (1..8), per D, ARGMAX readout:")
    print("     D  " + "  ".join(f"h{k}" for k in range(1, res["max_hops"] + 1)))
    for d in res["d_grid"]:
        print(f"  {d:>5d} " + "  ".join(f"{x:.2f}" if x is not None else "  -" for x in res["curves"][d]["argmax"]))
    print("  accuracy at hop k, CA3/ITER completion readout:")
    for d in res["d_grid"]:
        print(f"  {d:>5d} " + "  ".join(f"{x:.2f}" if x is not None else "  -" for x in res["curves"][d]["iter"]))
    print(f"  shuffled-edge twin (D=1024, argmax): {res['shuffled_twin_D1024']}  (info-free -> ~chance)")
    print(f"  UNDIRECTED naive-bind control (D=1024): {res['undirected_naive_bind_D1024']}  "
          f"(symmetric FHRR bind -> chain 50/50 lost per hop -> collapses vs directed)")
    print("  load axis (D=1024): 4-hop accuracy vs chain length (bundle load):")
    for r in res["load_sweep_D1024"]:
        print(f"    chain_len={r['chain_len']:>3d}  hop4 argmax={r['hop4_argmax']}  iter={r['hop4_iter']}")


def self_test():
    # DIRECTED (permutation-protected) chain at generous D: multi-hop stays reliable. UNDIRECTED (naive
    # symmetric bind) collapses by hop 2 (predecessor/successor ambiguity). shuffled twin ~chance.
    c = _one(2048, 40, 6, 4, 20, 1, "argmax", directed=True)
    assert c[0] > 0.9 and c[1] > 0.7, f"directed multi-hop at generous D must hold >=2 hops; got {c}"
    u = _one(2048, 40, 6, 4, 20, 1, "argmax", directed=False)
    assert u[1] < c[1] - 0.2, f"undirected naive-bind must collapse by hop 2 vs directed; directed={c} undirected={u}"
    tw = _one(1024, 40, 8, 4, 15, 1, "argmax", shuffle=True)
    assert tw[0] < 0.15, f"shuffled-edge twin must be ~chance (1/40=0.025); got {tw[0]}"
    print(f"SELF-TEST PASS: directed hops {c}; undirected hops {u} (collapses); shuffled twin 1-hop={tw[0]:.3f}")


def main():
    if "--self-test" in sys.argv:
        self_test(); return
    t0 = time.time()
    res = run()
    res["elapsed_s"] = round(time.time() - t0, 1)
    summarize(res)
    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, "metrics.json"), "w", encoding="utf-8", newline="") as fh:
        json.dump(res, fh, indent=2)
    print(f"\nwrote {OUTDIR} (elapsed {res['elapsed_s']}s)")


if __name__ == "__main__":
    main()
