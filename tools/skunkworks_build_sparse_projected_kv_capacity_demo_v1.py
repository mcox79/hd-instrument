"""Skunkworks 2026-06-21 -- BUILD + DEMONSTRATE the flagship capacity claim on CPU (capability-build, not a de-risk probe).
THE FLAGSHIP CHAIN-GRADE CLAIM: does whiten-before-topk sparse-projected-KV store >=3x more facts than dense-projected
at matched recall (>=0.80)? = the Willshaw super-capacity advantage of sparse storage, with the whiten-before-topk encode
that survives sparsification (validated 73ba2055). This is a WORKING CPU implementation that finds each arm's capacity
ceiling + the ratio -- hand to Exp-Dev as the CPU capacity-validation; the GPU run scales it to real Pythia-2.8b keys.

3 storage arms (all NN-argmax recall under query noise; capacity ceiling = max M with recall>=0.80):
  A dense_proj   : project keys (decrowd) -> store DENSE -> cosine-NN recall  (CERT 591 default; Arm2)
  B sparse_proj  : project -> WHITEN -> top-k (the redesigned flagship encode) -> store SPARSE k-of-N -> NN recall (Arm1)
  C raw_sparse   : top-k raw keys -> sparse -> NN recall  (Arm3; projection's contribution)
Realistic concentrated-energy keys (mimics a trained InfoNCE projection's shared-dim energy -- the case where naive
top-k collapses + whiten-before-topk is needed). HEAT-SAFE: d=96, M<=6000 (M x M <= 36M floats). ASCII.
"""
from __future__ import annotations
import numpy as np


def keys(M, d, rng, n_shared=8, shared=4.0):
    # concentrated-energy projected keys (realistic InfoNCE-like: a few shared high-energy dirs + individuating part)
    dirs = rng.standard_normal((n_shared, d))
    return (rng.standard_normal((M, n_shared)) * shared) @ dirs + rng.standard_normal((M, d))


def zca(K):
    Kc = K - K.mean(0, keepdims=True); cov = (Kc.T @ Kc) / Kc.shape[0]
    U, S, _ = np.linalg.svd(cov + 1e-6 * np.eye(cov.shape[0]))
    return Kc @ (U @ np.diag(1.0 / np.sqrt(S + 1e-6)) @ U.T)


def topk(K, f):
    k = max(1, int(round(f * K.shape[1]))); out = np.zeros_like(K)
    idx = np.argpartition(-np.abs(K), k - 1, axis=1)[:, :k]
    r = np.arange(K.shape[0])[:, None]; out[r, idx] = np.sign(K[r, idx]); return out


def nrm(K):
    n = np.linalg.norm(K, axis=1, keepdims=True); n[n == 0] = 1.0; return K / n


def recall(store, rng, noise):
    Sn = nrm(store); Q = nrm(store + noise * rng.standard_normal(store.shape) * np.std(store))
    return float((np.argmax(Q @ Sn.T, axis=1) == np.arange(store.shape[0])).mean())


def arm_store(kind, M, d, f, seed):
    rng = np.random.default_rng(seed); K = keys(M, d, rng)
    if kind == 'A_dense_proj':   return zca(K), rng
    if kind == 'B_sparse_proj':  return topk(zca(K), f), rng    # whiten-before-topk (the redesigned flagship encode)
    if kind == 'C_raw_sparse':   return topk(K, f), rng


def ceiling(kind, d, f, noise, Ms):
    last = 0
    for M in Ms:
        r = float(np.mean([recall(*arm_store(kind, M, d, f, s)[:1] + (np.random.default_rng(s+9),), noise) for s in (1, 2, 3)]))
        # (recall needs (store,rng,noise); rebuild cleanly below)
        rs = []
        for s in (1, 2, 3):
            store, _ = arm_store(kind, M, d, f, s)
            rs.append(recall(store, np.random.default_rng(s + 9), noise))
        r = float(np.mean(rs))
        if r >= 0.80: last = M
        else: return last, M, r
    return last, None, None


def main():
    d, noise, f = 96, 0.5, 0.05
    Ms = [250, 500, 1000, 2000, 4000, 6000]
    print("FLAGSHIP CAPACITY DEMO (CPU build): does whiten-before-topk sparse-projected-KV store >=3x more than dense-proj?")
    print(f"  d={d}, f={f} (k={int(f*d)}), query-noise={noise}, 3 seeds, M-sweep {Ms}; ceiling=max M w/ recall>=0.80\n")
    res = {}
    for kind in ('A_dense_proj', 'B_sparse_proj', 'C_raw_sparse'):
        c = ceiling(kind, d, f, noise, Ms)
        res[kind] = c[0]
        drop = f" (drops to {c[2]:.2f} at M={c[1]})" if c[1] else " (>= max M, lower-bound)"
        print(f"  {kind:16s} capacity ceiling ~ {c[0]}{drop}")
    a, b, cc = res['A_dense_proj'], res['B_sparse_proj'], res['C_raw_sparse']
    ratio_ba = (b / a) if a > 0 else float('inf')
    ratio_bc = (b / cc) if cc > 0 else float('inf')
    print(f"\n  CAPACITY RATIO  B(sparse_proj)/A(dense_proj) = {ratio_ba:.1f}x   |   B/C(raw_sparse) = {ratio_bc:.1f}x")
    verdict = (">=3x GREEN -- flagship capacity claim HOLDS on CPU (sparse super-capacity over dense-proj)" if ratio_ba >= 3.0
               else f"{ratio_ba:.1f}x -- sparse adds capacity but <3x (chain-grade bar not met at this scale)" if ratio_ba > 1.2
               else f"{ratio_ba:.1f}x -- NO capacity gain over dense-proj -> flagship -> MM")
    print(f"  VERDICT: {verdict}")
    print(f"  (B/C shows the PROJECTION's contribution to sparse capacity; B/A is the flagship's headline >=3x claim.)")
    print("\nNOTE: CPU capability-build w/ realistic concentrated-energy keys + whiten-before-topk encode (validated 73ba2055).")
    print("Hand to Exp-Dev: this is the CPU capacity-validation; the GPU run scales it to real Pythia-2.8b keys.")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
