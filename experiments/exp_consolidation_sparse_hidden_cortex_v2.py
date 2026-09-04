"""CONSOLIDATION deepening (v2): is the "selective replay is zero-sum" negative a property of the BRAIN,
or of my over-simple SINGLE-LAYER LINEAR cortex? The real cortex has a SPARSE, nonlinear HIDDEN layer
(k-WTA / lateral inhibition; O'Reilly Leabra) that ALLOCATES different concepts to different, largely
NON-OVERLAPPING hidden subpopulations. That separability is exactly what could break the zero-sum:
replaying an at-risk concept then updates only ITS hidden units' output weights, sparing the others -- so
SELECTIVE replay could protect the at-risk WITHOUT collateral damage, becoming a real lever.

v1 (linear cortex) found: interleaving works, but selective/schema/3-factor replay never beat the uniform
twin (zero-sum under representational overlap; witnessed both directions). CRUCIAL CAVEAT v1 left open, and
the surprise cell too: both used a store where every concept shares ALL the weights (linear map, or a DENSE
tanh hidden). Neither tested a SPARSE k-WTA hidden cortex -- the brain's actual separability mechanism.

THIS CELL: a 2-layer cortex. key -(fixed random expansion W1)-> pre-hidden -(k-WTA, keep HID_KEEP)-> sparse
hidden h -(learned W2, delta rule)-> value. Expansion Dh >> Dv + k-WTA gives sparse conjunctive codes (each
concept lights up a small, mostly-distinct hidden set). Replay updates ONLY W2 columns for a concept's active
hidden units. THE QUESTION: does SELECTIVE (surprise-prioritized) replay now beat UNIFORM at a SCARCE budget,
where in the linear cortex it did not? Sweep HID_KEEP (hidden sparsity) and the replay budget.

DECISIVE: if selective beats uniform CI-separated in the sparse-hidden cortex (and NOT in a dense-hidden
control), the brain mechanism is SELECTIVE REPLAY + SPARSE CORTICAL CODING (deviation #4 is the enabler on
the WRITE too) -> the v1 negative was a linear-model artifact and the wiring recommendation changes. If
selective still ties uniform even with a sparse hidden layer, the zero-sum is deeper than architecture and
the v1 negative stands, now much stronger.

ASCII-only. float64. Deterministic seeds. Reuses v1._build_pairs (real simplewiki reading, era fixed).
"""
from __future__ import annotations

import os as _os
_os.environ.setdefault("OMP_NUM_THREADS", "1")
_os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
_os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import json
import random
import sys
import time
from typing import Dict, List, Optional, Tuple

import numpy as np

sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import exp_consolidation_real_reading_old_vs_new_v1 as v1  # noqa: E402

DATA_DIR = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "data",
                         "exp_consolidation_sparse_hidden_cortex_v2")
SEEDS = (20260826, 7, 101)
DH = 512             # hidden expansion (Dh >> Dv)
HID_KEEP = 0.05      # k-WTA: fraction of hidden units active per concept (sparse conjunctive code)
EPOCHS = 40
LR = 0.5


def _unit_rows(M):
    n = np.linalg.norm(M, axis=1, keepdims=True); n[n < 1e-12] = 1.0
    return M / n


def _hidden(Kin: np.ndarray, W1: np.ndarray, keep: float, dense: bool) -> np.ndarray:
    """pre-hidden = relu(W1 @ key); k-WTA keeps top-`keep` fraction per row (sparse conjunctive code).
    dense=True -> skip k-WTA (dense tanh-like control) to isolate SPARSITY as the causal variable."""
    P = Kin @ W1.T                                   # [n, Dh]
    if dense:
        return np.tanh(P)
    H = np.zeros_like(P)
    k = max(1, int(round(keep * P.shape[1])))
    P = np.maximum(P, 0.0)                            # relu (nonneg before competition)
    for i in range(P.shape[0]):
        idx = np.argpartition(P[i], P.shape[1] - k)[P.shape[1] - k:]
        H[i, idx] = P[i, idx]
    return _unit_rows(H)


def _ranks(W2: np.ndarray, H: np.ndarray, Ch: np.ndarray, tgt: np.ndarray, idxs, self_cb) -> np.ndarray:
    Yhat = _unit_rows(H[idxs] @ W2.T)
    S = Yhat @ Ch.T
    for r, i in enumerate(idxs):
        S[r, self_cb[i]] = -1e9
    order = np.argsort(-S, axis=1)
    return np.array([int(np.where(order[r] == tgt[i])[0][0]) for r, i in enumerate(idxs)])


def _delta(W2, H, V, idxs, epochs, lr, rng):
    for _ in range(epochs):
        o = list(idxs); rng.shuffle(o)
        for i in o:
            W2 += lr * np.outer(V[i] - W2 @ H[i], H[i])
    return W2


def _surprise_ranks(W2, H, C, tgt, idxs, self_cb):
    r = _ranks(W2, H, C, tgt, idxs, self_cb)
    return r


def _phase2(arm, W0, H, V, C, tgt, old, new, epochs, lr, budget, alpha, seed, self_cb):
    rng = random.Random(seed ^ 0xC0FFEE)
    W2 = W0.copy()
    m = min(budget, len(old))
    for _ in range(epochs):
        if arm == "SEQUENTIAL":
            replay = []
        elif arm in ("INTERLEAVED", "RANDOM"):
            replay = [old[j] for j in rng.sample(range(len(old)), m)]
        elif arm == "SELECTIVE":
            r = _ranks(W2, H, C, tgt, old, self_cb)
            s = 1.0 - 1.0 / (r + 1.0)
            p = np.power(np.clip(s, 1e-6, None), alpha); p = p / p.sum()
            sel = np.random.default_rng(seed ^ (rng.randrange(1 << 30))).choice(len(old), size=m, replace=False, p=p)
            replay = [old[j] for j in sel]
        else:
            replay = []
        W2 = _delta(W2, H, V, new + replay, 1, lr, rng)
    return W2


ARMS = ("SEQUENTIAL", "INTERLEAVED", "SELECTIVE", "RANDOM")


def _run(seed, d, hid_keep, dense, budget_frac, epochs, lr, alpha, neurogen=False):
    K, names, avals = d["K"], d["names"], d["avals"]
    Dv = d["Dv"]
    cb_names = list(dict.fromkeys(list(names) + list(avals)))
    cb_pos = {c: i for i, c in enumerate(cb_names)}
    name_vec = {names[i]: K[i] for i in range(len(names))}
    assoc_vec = d.get("assoc_vec", {})
    C = np.zeros((len(cb_names), Dv))
    for i, c in enumerate(cb_names):
        C[i] = name_vec[c] if c in name_vec else assoc_vec[c]
    C = _unit_rows(C)
    tgt = np.array([cb_pos[avals[i]] for i in range(len(names))], dtype=np.int64)
    self_cb = np.array([cb_pos[names[i]] for i in range(len(names))], dtype=np.int64)
    V = C[tgt]

    # fixed random expansion; sparse hidden code for the training keys. Retrieval compares the predicted
    # VALUE (Dv, = W2 @ h(key)) against the codebook's VALUE vectors C (Dv) -- NOT against hidden codes.
    rng = np.random.default_rng(seed ^ 0x9a17)
    W1 = rng.standard_normal((DH, Dv)) / np.sqrt(Dv)
    H = _hidden(K, W1, hid_keep, dense)             # [N, Dh] sparse hidden for training concepts

    N = len(names)
    perm = np.random.default_rng(seed ^ 0x513).permutation(N)
    n_old = int(0.4 * N); n_new = int(0.4 * N)
    old = list(perm[:n_old]); new = list(perm[n_old:n_old + n_new]); held = list(perm[n_old + n_new:])
    budget = int(round(budget_frac * n_new))

    if neurogen:
        # DG adult neurogenesis: recruit a DISJOINT pool of fresh hidden units for NEW (and novel held-out)
        # memories, so OLD/NEW occupy separate granule-cell populations -> maximal pattern separation across
        # temporally-distinct memories. OLD uses units [0:half]; NEW + HELD use [half:].
        half = DH // 2
        M = np.zeros((N, DH))
        M[:, :half] = 1.0
        for i in new + held:
            M[i, :] = 0.0; M[i, half:] = 1.0
        H = _unit_rows(H * M)

    W_old = _delta(np.zeros((Dv, DH)), H, V, old, epochs, lr, random.Random(seed ^ 0xA11CE))
    out = {}
    for arm in ARMS:
        W2 = _phase2(arm, W_old, H, V, C, tgt, old, new, epochs, lr, budget, alpha, seed, self_cb)
        r_old = _ranks(W2, H, C, tgt, old, self_cb)
        r_new = _ranks(W2, H, C, tgt, new, self_cb)
        r_held = _ranks(W2, H, C, tgt, held, self_cb)   # GENERALISATION: concepts trained in NEITHER phase
        out[arm] = dict(ranks_old=r_old.tolist(), ranks_new=r_new.tolist(), ranks_held=r_held.tolist())
    return out


def _boot(vals, rng, iters=2000):
    if vals.size == 0:
        return (float("nan"),) * 3
    idx = rng.integers(0, vals.size, size=(iters, vals.size))
    b = vals[idx].mean(axis=1)
    return float(vals.mean()), float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--n_read", type=int, default=6000)
    ap.add_argument("--n_concepts", type=int, default=320)
    ap.add_argument("--code_dim", type=int, default=48)
    ap.add_argument("--hid_keep", type=str, default="0.05")   # comma list to sweep hidden sparsity
    ap.add_argument("--budget_frac", type=float, default=0.25)  # SCARCE budget (fraction of |new| of |old|)
    ap.add_argument("--epochs", type=int, default=EPOCHS)
    ap.add_argument("--alpha", type=float, default=2.0)
    ap.add_argument("--dense_control", action="store_true")   # also run a DENSE-hidden control
    ap.add_argument("--neurogenesis", action="store_true")    # DG neurogenesis: fresh hidden pool for NEW
    args = ap.parse_args()

    v1.CODE_DIM = args.code_dim
    v1.SPARSE_KEEP = 1.0
    v1.N_CONCEPTS = 120 if args.smoke else args.n_concepts
    seeds = (20260826,) if args.smoke else SEEDS
    n_read = 2500 if args.smoke else args.n_read
    keeps = [float(x) for x in args.hid_keep.split(",")]
    modes = [("sparse", False)] + ([("dense", True)] if args.dense_control else [])

    t0 = time.time()
    per_seed = {sd: v1._build_pairs(sd, n_read, 1000) for sd in seeds}
    brng = np.random.default_rng(4242)
    results = {}
    print(f"SPARSE-HIDDEN CORTEX: Dh={DH} budget_frac={args.budget_frac} keeps={keeps} "
          f"dense_control={args.dense_control}")
    for mode, dense in modes:
        for keep in keeps:
            rows = [_run(sd, per_seed[sd], keep, dense, args.budget_frac, args.epochs, LR, args.alpha,
                         neurogen=args.neurogenesis)
                    for sd in seeds if per_seed[sd] is not None]
            agg = {}
            for arm in ARMS:
                ro = np.concatenate([np.array(r[arm]["ranks_old"]) for r in rows])
                rn = np.concatenate([np.array(r[arm]["ranks_new"]) for r in rows])
                rh = np.concatenate([np.array(r[arm]["ranks_held"]) for r in rows])
                mo, loo, hio = _boot((ro == 0).astype(float), brng)
                mn, _, _ = _boot((rn == 0).astype(float), brng)
                mh, lhh, hhh = _boot((rh == 0).astype(float), brng)
                agg[arm] = dict(old=mo, old_lo=loo, old_hi=hio, new=mn, bal=min(mo, mn),
                                gen=mh, gen_lo=lhh, gen_hi=hhh)
            key = f"{mode}_keep{keep}"
            results[key] = agg
            itl, sel = agg["INTERLEAVED"], agg["SELECTIVE"]
            sep_old = sel["old_lo"] > itl["old_hi"]
            print(f"\n  [{key}] ({time.time()-t0:.0f}s)")
            print(f"    OLD: SEQ={agg['SEQUENTIAL']['old']:.3f} UNIFORM={itl['old']:.3f}[{itl['old_lo']:.3f},{itl['old_hi']:.3f}] "
                  f"SELECTIVE={sel['old']:.3f}[{sel['old_lo']:.3f},{sel['old_hi']:.3f}]")
            print(f"    BALANCED(min): UNIFORM={itl['bal']:.3f} SELECTIVE={sel['bal']:.3f}")
            print(f"    GENERALISATION (held-out, trained in NEITHER phase): UNIFORM={itl['gen']:.3f}[{itl['gen_lo']:.3f},{itl['gen_hi']:.3f}]  (retention-vs-generalisation tradeoff)")
            print(f"    -> SELECTIVE beats UNIFORM on OLD CI-sep? {sep_old}  on BAL? {sel['bal']>itl['bal']}")

    out_dir = DATA_DIR + ("_neurogen" if args.neurogenesis else "")
    _os.makedirs(out_dir, exist_ok=True)
    tmp = _os.path.join(out_dir, "metrics.json.tmp")
    with open(tmp, "w") as f:
        json.dump(dict(run_mode="smoke" if args.smoke else "full", anchor_name="consolidation_sparse_hidden_cortex_v2",
                       seeds=list(seeds), dh=DH, budget_frac=args.budget_frac, keeps=keeps,
                       dense_control=args.dense_control, results=results, elapsed_s=time.time()-t0), f)
    _os.replace(tmp, _os.path.join(out_dir, "metrics.json"))
    print(f"\n[done {time.time()-t0:.0f}s -> {out_dir}/metrics.json]")


if __name__ == "__main__":
    main()
