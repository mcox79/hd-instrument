"""Skunkworks 2026-06-21 -- CPU MECHANISM-PROBE (de-risks the flagship's CORE CHAIN-GRADE CLAIM; NOT the cell). HEAT-SAFE.
Probe 1 proved decrowding SURVIVES sparse (the make-or-break). This probes the flagship's ACTUAL chain-grade CLAIM:
does proj-SPARSE store >=3x more facts than proj-DENSE at matched recall (a3f473dd Willshaw super-capacity advantage)?
Method: small d=64 so each arm's capacity CEILING appears at low M (heat-safe; M x M stays small). Sweep M, find each
arm's M_ceiling (where recall drops below 0.90). Capacity ratio = M_ceiling(proj_sparse) / M_ceiling(proj_dense).
Arms: proj_dense (Arm2 / CERT 591 default) | proj_sparse f=0.10,0.05 (Arm1 / flagship) | raw_sparse (Arm3).
GREEN if proj_sparse ceiling >= 3x proj_dense ceiling (the >=3x-M bar). READ-ONLY. ASCII. Hand to Exp-Dev.
"""
from __future__ import annotations
import numpy as np


def make_crowded_keys(M, d, rng, n_dom=6, dom_scale=5.0):
    dom = rng.standard_normal((n_dom, d)); coeff = rng.standard_normal((M, n_dom)) * dom_scale
    return coeff @ dom + rng.standard_normal((M, d))


def zca_whiten(K):
    Kc = K - K.mean(0, keepdims=True); cov = (Kc.T @ Kc) / Kc.shape[0]
    U, S, _ = np.linalg.svd(cov + 1e-6 * np.eye(cov.shape[0]))
    return Kc @ (U @ np.diag(1.0 / np.sqrt(S + 1e-6)) @ U.T)


def sparsify_topk(K, f):
    k = max(1, int(round(f * K.shape[1]))); out = np.zeros_like(K)
    idx = np.argpartition(-np.abs(K), k - 1, axis=1)[:, :k]
    rows = np.arange(K.shape[0])[:, None]; out[rows, idx] = np.sign(K[rows, idx]); return out


def norm(K):
    n = np.linalg.norm(K, axis=1, keepdims=True); n[n == 0] = 1.0; return K / n


def recall(K, rng, noise):
    Kn = norm(K); Q = norm(K + noise * rng.standard_normal(K.shape) * np.std(K))
    pred = np.argmax(Q @ Kn.T, axis=1)
    return float((pred == np.arange(K.shape[0])).mean())


def arm_recall(kind, M, d, f, seed, noise):
    rng = np.random.default_rng(seed); raw = make_crowded_keys(M, d, rng)
    if kind == 'proj_dense':
        K = zca_whiten(raw)
    elif kind == 'proj_sparse':
        K = sparsify_topk(zca_whiten(raw), f)
    elif kind == 'raw_sparse':
        K = sparsify_topk(raw, f)
    return recall(K, rng, noise)


def ceiling(kind, d, f, noise, Ms):
    # smallest M where mean recall (3 seeds) drops below 0.90 -> the capacity ceiling (interpolated as last-ok M)
    last_ok = 0
    for M in Ms:
        r = float(np.mean([arm_recall(kind, M, d, f, s, noise) for s in (1, 2, 3)]))
        if r >= 0.90:
            last_ok = M
        else:
            return last_ok, M, r
    return last_ok, None, None  # never dropped in range -> lower-bound


def main():
    d, noise = 64, 0.5
    Ms = [200, 400, 800, 1600, 3200, 6400]
    print("FLAGSHIP CAPACITY-CEILING PROBE (heat-safe d=64): does proj-SPARSE store >=3x more than proj-DENSE at recall>=0.90?")
    print(f"  d={d}, noise={noise}, 3 seeds, M-sweep {Ms}; ceiling = last M with recall>=0.90\n")
    cd = ceiling('proj_dense', d, None, noise, Ms)
    print(f"  proj_dense  (Arm2): ceiling ~ {cd[0]}" + (f" (drops to {cd[2]:.2f} at M={cd[1]})" if cd[1] else " (>= max, lower-bound)"))
    for f in (0.10, 0.05):
        cs = ceiling('proj_sparse', d, f, noise, Ms)
        cr = ceiling('raw_sparse', d, f, noise, Ms)
        ratio = (cs[0] / cd[0]) if cd[0] > 0 else float('inf')
        print(f"  proj_sparse f={f} (Arm1): ceiling ~ {cs[0]}" + (f" (drops to {cs[2]:.2f} at M={cs[1]})" if cs[1] else " (>= max, lower-bound)")
              + f"   | raw_sparse f={f} (Arm3): ceiling ~ {cr[0]}")
        verdict = (">=3x GREEN" if ratio >= 3.0 else f"{ratio:.1f}x (sparse adds capacity, <3x)" if ratio > 1.2
                   else f"{ratio:.1f}x NO capacity gain -> flagship -> MM")
        print(f"      capacity ratio proj_sparse/proj_dense = {ratio:.1f}x  -> {verdict}\n")
    print("Read: proj_sparse ceiling >> proj_dense ceiling = sparse stores MORE (Willshaw super-capacity over dense) = the")
    print("flagship's >=3x-M chain-grade claim. proj_sparse vs raw_sparse = projection's contribution to the sparse capacity.")
    print("NOTE: synthetic ZCA stand-in + small d; CPU mechanism-probe to inform the GPU build's M-sweep, NOT the cell.")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
