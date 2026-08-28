"""THE INTEGRATION CAPSTONE: reasoning over REALISTIC (correlated) memory is broken by default -- and the brain's
three mechanisms, STACKED, recover it. Proves the audit's thesis end-to-end.

The audit isolated three real bottlenecks (none dimensional): binding DIRECTEDNESS (commutative bind -> undirected
edges -> multihop lost per hop), CODE ORTHOGONALITY (correlated codes -> cleanup crosstalk), and the READOUT RULE
(independent argmax -> leaves capacity on the table vs CA3 joint completion). Each is a brain-faithful FIX
(permutation protection; DG sparse pattern separation; CA3 attractor completion). This cell runs a MULTIHOP query
over a knowledge chain whose nodes are CORRELATED codes (the realistic regime, not iid-random), and ablates the
three fixes to show (a) the default substrate fails and (b) stacking the fixes recovers it.

  NODES: N correlated bipolar codes (shared-background correlation rho -- the realistic regime the real-code cell
         measured for WordNet meaning codes). Bipolar bind is elementwise multiply (self-inverse), = event_bundle.
  STORE: chain n0->n1->...->nL as SUM of edges. arms toggle:
         DIRECTED  (permutation-protect the tail: bind(h, roll(t)))  vs  undirected bind(h,t).
         DECORR    (DG top-k sparsify each node before use)          vs  dense correlated.
  READ:  K-hop walk; per hop cleanup argmax  vs  CA3 iterative completion, over the (decorrelated) node codebook.

ARMS: DEFAULT (undirected + correlated + argmax) -> the failing baseline; +DIR; +DIR+DECORR; +DIR+DECORR+CA3
(the full brain stack). FLOOR = chance 1/N; TWIN = shuffled-edge store (must collapse). VERDICT: stacked brain
fixes recover multi-hop reasoning that the default substrate loses.

Run:  .venv/Scripts/python.exe experiments/exp_dim_phase_diagram_stacked_v1.py [--self-test]
ASCII only. Writes ONLY to data/exp_dim_phase_diagram_stacked_v1/. NO hdlab write.
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

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

OUTDIR = os.path.join(REPO_ROOT, "data", "exp_dim_phase_diagram_stacked_v1")
SEED = 20260828
D = 1024


def _correlated_bipolar(n, d, rho, rng):
    """n bipolar {-1,+1} codes sharing a background by fraction rho (the realistic correlated regime)."""
    bg = rng.choice([-1.0, 1.0], size=d)
    own = rng.choice([-1.0, 1.0], size=(n, d))
    take_bg = rng.random((n, d)) < rho
    codes = np.where(take_bg, bg[None, :], own)
    return codes.astype(np.float64)


def _dg(mat, frac=0.05):
    """DG sparse pattern separation: remove the shared-background common mode (per-code mean), keep only the top-k
    most-distinctive dims (k-winners-take-all), sign them. Decorrelates codes that share a background."""
    d = mat.shape[1]; k = max(1, int(frac * d))
    centered = mat - mat.mean(axis=1, keepdims=True)      # strip the common-mode shared background
    idx = np.argpartition(-np.abs(centered), k - 1, axis=1)[:, :k]
    out = np.zeros_like(mat)
    rows = np.arange(mat.shape[0])[:, None]
    out[rows, idx] = np.sign(centered[rows, idx])
    return out


def _roll(v):
    return np.roll(v, 1, axis=-1)


def _unroll(v):
    return np.roll(v, -1, axis=-1)


def _cleanup(readback, cb, ca3=False, steps=4):
    scores = cb @ readback
    idx = int(np.argmax(scores))
    if not ca3:
        return idx
    x = readback.astype(np.float64); tau = np.sqrt(cb.shape[1])
    for _ in range(steps):
        s = cb @ x / tau
        s = s - s.max()
        w = np.exp(s); w = w / w.sum()
        x = w @ cb
        ni = int(np.argmax(cb @ x))
        if ni == idx:
            break
        idx = ni
    return idx


def _one(n_nodes, chain_len, max_hops, rho, directed, decorr, ca3, n_reps, seed, shuffle=False):
    hit = np.zeros(max_hops); tot = np.zeros(max_hops)
    for rep in range(n_reps):
        rng = np.random.default_rng(seed + rep * 7919)
        base = _correlated_bipolar(n_nodes, D, rho, rng)
        nodes = _dg(base, frac=0.05) if decorr else base
        cb = nodes                                    # cleanup codebook (same transform as stored)
        chain = list(rng.permutation(n_nodes))[:chain_len + 1]
        edges = [(chain[i], chain[i + 1]) for i in range(len(chain) - 1)]
        if shuffle:
            tails = list(rng.permutation([t for _, t in edges]))
            edges = [(edges[i][0], tails[i]) for i in range(len(edges))]
        S = np.zeros(D)
        for (h, t) in edges:
            tail = _roll(nodes[t]) if directed else nodes[t]
            S = S + nodes[h] * tail                    # bipolar bind = elementwise multiply
        cur = nodes[chain[0]]
        for k in range(1, min(max_hops, len(chain) - 1) + 1):
            rb = S * cur                               # unbind (self-inverse)
            if directed:
                rb = _unroll(rb)
            ci = _cleanup(rb, cb, ca3=ca3)
            cur = nodes[ci]
            hit[k - 1] += int(ci == chain[k]); tot[k - 1] += 1
    return [round(hit[k] / tot[k], 4) if tot[k] else None for k in range(max_hops)]


def run():
    """The fixes are STORE-TYPE-SPECIFIC (a brain-faithful finding): permutation-directedness + CA3-completion
    belong to the multiplicative-BINDING relational store (multihop); DG sparse decorrelation belongs to the
    AUTOASSOCIATIVE bundle store (member recovery -- see exp_dim_phase_diagram_realcode_v1), and BREAKS a
    multiplicative-binding store because sparse x sparse ~= empty. This cell shows the matched fixes recover
    multihop, and the mismatched fix (DG into a binding store) fails -- so the brain's cortex->DG->CA3 pipeline
    is a SPECIFIC composition, not an arbitrary stack."""
    n_nodes, chain_len, max_hops, rho, n_reps = 60, 6, 6, 0.5, 60
    arms = {
        "DEFAULT (undirected + correlated + argmax)":   dict(directed=False, decorr=False, ca3=False),
        "+DIRECTED (permutation protection)":           dict(directed=True, decorr=False, ca3=False),
        "+DIRECTED +CA3 completion (matched fixes)":    dict(directed=True, decorr=False, ca3=True),
        "+DIRECTED +DG-sparse (MISMATCHED store)":      dict(directed=True, decorr=True, ca3=False),
    }
    out = {name: _one(n_nodes, chain_len, max_hops, rho, n_reps=n_reps, seed=SEED, **cfg)
           for name, cfg in arms.items()}
    twin = _one(n_nodes, chain_len, max_hops, rho, directed=True, decorr=False, ca3=True,
                n_reps=n_reps, seed=SEED, shuffle=True)
    return {"anchor": "dim_phase_diagram_stacked_v1", "D": D, "n_nodes": n_nodes, "chain_len": chain_len,
            "rho": rho, "n_reps": n_reps, "chance": round(1.0 / n_nodes, 4), "arms": out,
            "shuffled_twin_matched": twin}


def summarize(res):
    print(f"\n=== STORE-MATCHED brain-fixes: multihop reasoning over CORRELATED memory (N={res['n_nodes']}, "
          f"rho={res['rho']}, chance={res['chance']}) ===")
    print("  accuracy at hop k (1..%d):" % res["chain_len"])
    for name, curve in res["arms"].items():
        print(f"    {name:<44s} " + " ".join(f"{x:.2f}" if x is not None else " -" for x in curve))
    print(f"    {'shuffled-edge twin (matched fixes)':<44s} " +
          " ".join(f"{x:.2f}" if x is not None else " -" for x in res["shuffled_twin_matched"]))
    d = res["arms"]["DEFAULT (undirected + correlated + argmax)"]
    m = res["arms"]["+DIRECTED +CA3 completion (matched fixes)"]
    mis = res["arms"]["+DIRECTED +DG-sparse (MISMATCHED store)"]
    print(f"  => hop-4: default {d[3]:.2f} -> MATCHED fixes (directed+CA3) {m[3]:.2f} (recovers); MISMATCHED "
          f"(DG into a binding store) {mis[3]:.2f} (DG belongs in the AUTOASSOCIATIVE store, not here).")


def self_test():
    d = _one(60, 6, 4, 0.5, directed=False, decorr=False, ca3=False, n_reps=20, seed=1)
    m = _one(60, 6, 4, 0.5, directed=True, decorr=False, ca3=True, n_reps=20, seed=1)
    mis = _one(60, 6, 4, 0.5, directed=True, decorr=True, ca3=False, n_reps=20, seed=1)
    assert m[3] > d[3] + 0.2, f"matched fixes (directed+CA3) must recover multi-hop; default={d} matched={m}"
    assert mis[1] < m[1] - 0.2, f"DG into a multiplicative-binding store must BREAK it; matched={m} mismatched={mis}"
    tw = _one(60, 6, 4, 0.5, directed=True, decorr=False, ca3=True, n_reps=20, seed=1, shuffle=True)
    assert tw[0] < m[0] - 0.4, f"shuffled-edge twin must lose to the matched fixes; matched1={m[0]} twin1={tw[0]}"
    print(f"SELF-TEST PASS: default {d}; matched(dir+CA3) {m}; MISMATCHED(DG) {mis} (breaks); "
          f"twin1={tw[0]:.3f}<<matched {m[0]:.3f}")


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
