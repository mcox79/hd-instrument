"""Skunkworks 2026-06-21 -- CORRECTED flagship sparse-encode probe (after Exp-Dev's RED FLAG: my prior ZCA probe gave a
FALSE GREEN because ZCA SPREADS energy -- top-k-friendly -- while the real InfoNCE projection CONCENTRATES energy in
shared dims, so top-k-magnitude picks the SAME dims for all keys -> collapse). This probe (1) REPLICATES the collapse on
CONCENTRATED-energy keys (matching the real failure), then (2) tests fix-hypotheses for the sparse-ENCODE:
  A) top-k-magnitude (the naive flagship -> should COLLAPSE)
  B) whiten-THEN-top-k (my accidental fix: decorrelate to SPREAD energy before sparsify)
  C) random-fixed-position per key (Exp-Dev option 1a: diverse supports by construction)
Metric: rho_mean (mean |off-diag cosine| of the sparse codes; LOWER=more decrowded=diverse supports). If a fix gives
rho(fix-sparse) << rho(topk-sparse) ~ rho(raw-sparse-on-concentrated), it preserves diversity. HEAT-SAFE. Hand to Exp-Dev.
"""
from __future__ import annotations
import numpy as np


def concentrated_keys(M, d, rng, n_shared=6, shared_energy=8.0):
    # mimic InfoNCE+key-uniformity: keys align along a few SHARED high-energy directions (energy concentrated)
    shared_dirs = rng.standard_normal((n_shared, d))
    shared = (rng.standard_normal((M, n_shared)) * shared_energy) @ shared_dirs
    indiv = rng.standard_normal((M, d))  # low-energy individuating part
    return shared + indiv


def zca(K):
    Kc = K - K.mean(0, keepdims=True); cov = (Kc.T @ Kc) / Kc.shape[0]
    U, S, _ = np.linalg.svd(cov + 1e-6 * np.eye(cov.shape[0]))
    return Kc @ (U @ np.diag(1.0 / np.sqrt(S + 1e-6)) @ U.T)


def topk(K, f):
    k = max(1, int(round(f * K.shape[1]))); out = np.zeros_like(K)
    idx = np.argpartition(-np.abs(K), k - 1, axis=1)[:, :k]
    r = np.arange(K.shape[0])[:, None]; out[r, idx] = np.sign(K[r, idx]); return out


def random_pos(K, f, rng):
    # each key sparsifies at a RANDOM fixed support (diverse by construction); keep sign at those positions
    k = max(1, int(round(f * K.shape[1]))); out = np.zeros_like(K)
    for i in range(K.shape[0]):
        idx = rng.choice(K.shape[1], size=k, replace=False)
        out[i, idx] = np.sign(K[i, idx]) + (K[i, idx] == 0)  # avoid zero-sign
    return out


def norm(K):
    n = np.linalg.norm(K, axis=1, keepdims=True); n[n == 0] = 1.0; return K / n


def rho(K, rng, pairs=3000):
    Kn = norm(K); M = Kn.shape[0]
    i = rng.integers(0, M, pairs); j = rng.integers(0, M, pairs); keep = i != j
    return float(np.abs(np.sum(Kn[i[keep]] * Kn[j[keep]], axis=1)).mean())


def support_overlap(K, rng, pairs=3000):
    # mean fraction of shared active positions between key-pairs (1.0 = identical supports = collapse)
    A = (K != 0); M = K.shape[0]
    i = rng.integers(0, M, pairs); j = rng.integers(0, M, pairs); keep = i != j
    ai, aj = A[i[keep]], A[j[keep]]
    inter = np.sum(ai & aj, axis=1); uni = np.sum(ai | aj, axis=1); uni[uni == 0] = 1
    return float(np.mean(inter / uni))  # Jaccard


def main():
    M, d = 2000, 256
    print("SPARSE-ENCODE FIX PROBE (corrects my false-GREEN; replicate collapse + test fixes). HEAT-SAFE.")
    print(f"  M={M} CONCENTRATED-energy keys (mimics InfoNCE shared-dim concentration), d={d}, 3 seeds\n")
    for f in (0.05, 0.10):
        agg = {}
        for s in (1, 2, 3):
            rng = np.random.default_rng(s); rr = np.random.default_rng(s + 50)
            K = concentrated_keys(M, d, rng)  # the energy-concentrated "projected" keys (mimics InfoNCE)
            variants = {
                'A_concproj_topk(naive flagship)': topk(K, f),
                'B_whiten_then_topk(FIX?)': topk(zca(K), f),
                'C_random_pos(FIX?)': random_pos(K, f, rng),
            }
            for name, sp in variants.items():
                agg.setdefault(name, {'rho': [], 'ov': []})
                agg[name]['rho'].append(rho(sp, rr)); agg[name]['ov'].append(support_overlap(sp, rr))
        print(f"=== f={f} (rho=crosstalk LOWER=better; support_overlap=Jaccard, 1.0=identical-supports=collapse) ===")
        for name in agg:
            rh = float(np.mean(agg[name]['rho'])); ov = float(np.mean(agg[name]['ov']))
            print(f"  {name:34s} rho={rh:.3f}  support_overlap={ov:.3f}")
        print()
    print("Read: A (concentrated-proj -> top-k) should show HIGH rho + HIGH support_overlap = the COLLAPSE Exp-Dev found.")
    print("If B (whiten-then-topk) and/or C (random-pos) show LOW rho + LOW overlap -> a viable sparse-encode FIX.")
    return 0


def concentrate_proj(K, rng):
    return K


if __name__ == '__main__':
    raise SystemExit(main())
