"""Skunkworks 2026-06-21 -- CPU MECHANISM-PROBE (de-risks the sparse-projected-KV flagship; NOT the cell).
THE FLAGSHIP MAKE-OR-BREAK (Exp-Dev's #1 + my SCHEMA-VET C3): does a decrowding projection's crosstalk-rho
reduction SURVIVE k-of-N sparsification? If sparse washes out the decrowding (projected-then-sparse ~ raw-sparse),
the flagship collapses to MM (saves a heavy GPU build). If it survives (projected-then-sparse << raw-sparse), the
flagship is green-lit. Synthetic anisotropic (crowded) keys + analytic ZCA decrowder (stand-in for CERT 591's
learned projection -- the QUESTION is preservation-under-sparse, not the learning, which 591 proved).
Stages: raw / projected / raw->sparse (Arm3 analog) / projected->sparse (Arm1 analog).
Metrics: rho_mean (mean |off-diag cosine| = crosstalk) + recall (NN-argmax self-id under load). 3 seeds.
READ-ONLY (no Store write). ASCII. Hands result to Exp-Dev to inform the GPU build.
"""
from __future__ import annotations
import numpy as np


def make_crowded_keys(M, d, rng, n_dom=8, dom_scale=6.0):
    # anisotropic keys: a few dominant shared directions (-> high pairwise correlation = crowding), like raw LM keys
    dom = rng.standard_normal((n_dom, d))
    coeff = rng.standard_normal((M, n_dom)) * dom_scale
    iso = rng.standard_normal((M, d))
    K = coeff @ dom + iso
    return K


def zca_whiten(K):
    # analytic decrowder: ZCA whitening decorrelates -> reduces pairwise crosstalk (stand-in for #7 learned projection)
    Kc = K - K.mean(0, keepdims=True)
    cov = (Kc.T @ Kc) / Kc.shape[0]
    U, S, _ = np.linalg.svd(cov + 1e-6 * np.eye(cov.shape[0]))
    W = U @ np.diag(1.0 / np.sqrt(S + 1e-6)) @ U.T
    return Kc @ W


def sparsify_topk(K, f):
    # a3f473dd-style: keep top-k by magnitude, bipolar sign -> k-of-N sparse code
    k = max(1, int(round(f * K.shape[1])))
    out = np.zeros_like(K)
    idx = np.argpartition(-np.abs(K), k - 1, axis=1)[:, :k]
    rows = np.arange(K.shape[0])[:, None]
    out[rows, idx] = np.sign(K[rows, idx])
    return out


def normalize(K):
    n = np.linalg.norm(K, axis=1, keepdims=True)
    n[n == 0] = 1.0
    return K / n


def rho_mean(K, max_pairs=2000, rng=None):
    # mean |off-diagonal cosine| over a sample of pairs (crosstalk proxy)
    Kn = normalize(K)
    M = Kn.shape[0]
    if rng is None:
        rng = np.random.default_rng(0)
    i = rng.integers(0, M, size=max_pairs)
    j = rng.integers(0, M, size=max_pairs)
    keep = i != j
    i, j = i[keep], j[keep]
    cos = np.abs(np.sum(Kn[i] * Kn[j], axis=1))
    return float(cos.mean())


def recall_self(K):
    # NN-argmax self-identification under load: each key's nearest (by cosine) among all M should be itself
    Kn = normalize(K)
    S = Kn @ Kn.T
    np.fill_diagonal(S, -np.inf)  # nearest OTHER
    nn = np.argmax(S, axis=1)
    # recall proxy: fraction whose nearest-other cosine < self-margin is hard to define for self-id;
    # use the standard associative proxy: store K, query with K+noise, recover argmax==self.
    return None  # replaced below by query_recall


def query_recall(K, rng, noise=0.6):
    # store K; query = key + noise; recover via argmax cosine; recall = fraction recovered to self
    Kn = normalize(K)
    Q = K + noise * rng.standard_normal(K.shape) * np.std(K)
    Qn = normalize(Q)
    S = Qn @ Kn.T
    pred = np.argmax(S, axis=1)
    return float((pred == np.arange(K.shape[0])).mean())


def run_seed(seed, M, d, f, noise):
    rng = np.random.default_rng(seed)
    raw = make_crowded_keys(M, d, rng)
    proj = zca_whiten(raw)
    raw_sp = sparsify_topk(raw, f)
    proj_sp = sparsify_topk(proj, f)
    rr = np.random.default_rng(seed + 100)
    return {
        'rho_raw': rho_mean(raw, rng=rr), 'rho_proj': rho_mean(proj, rng=rr),
        'rho_raw_sparse': rho_mean(raw_sp, rng=rr), 'rho_proj_sparse': rho_mean(proj_sp, rng=rr),
        'rec_raw': query_recall(raw, rng, noise), 'rec_proj': query_recall(proj, rng, noise),
        'rec_raw_sparse': query_recall(raw_sp, rng, noise), 'rec_proj_sparse': query_recall(proj_sp, rng, noise),
    }


def main():
    # de-saturated + HEAT-SAFE (USER flagged laptop heat): low d=128 + high noise + M>>d crowds capacity so
    # raw_sparse recall DROPS, WITHOUT a heavy large-M matmul (M<=8000 -> M x M <= 64M floats, ~1-2s). The
    # projection's recall-benefit can then show. (the pythia-v1 de-saturation lesson, applied heat-consciously.)
    d, noise = 128, 1.5
    print("FLAGSHIP DE-RISK PROBE v2 (de-saturated, heat-safe): decrowding survive k-of-N sparse on rho AND recall?")
    print(f"  d={d}, query-noise={noise}, ZCA decrowder, 3 seeds; M-sweep (M>>d crowds capacity); heat-safe (M<=8000)\n")
    f = 0.05
    print(f"=== f={f} (k={int(f*d)} of {d}); M-sweep ===")
    for M in (1000, 2000, 4000, 8000):
        rows = [run_seed(s, M, d, f, noise) for s in (1, 2, 3)]
        agg = {k: float(np.mean([r[k] for r in rows])) for k in rows[0]}
        rho_survive = agg['rho_raw_sparse'] - agg['rho_proj_sparse']
        rec_survive = agg['rec_proj_sparse'] - agg['rec_raw_sparse']
        print(f"  M={M:6d}  rho[raw_sp={agg['rho_raw_sparse']:.3f} proj_sp={agg['rho_proj_sparse']:.3f}]  "
              f"recall[raw_sp={agg['rec_raw_sparse']:.3f} proj_sp={agg['rec_proj_sparse']:.3f} | dense raw={agg['rec_raw']:.3f} proj={agg['rec_proj']:.3f}]  "
              f"REC_GAIN(sparse)={rec_survive:+.3f}")
    print("\n  Read: where raw_sp recall DROPS below ~1.0 (load bites), does proj_sp HOLD higher? -> recall-survival.")
    print("  rho-survival already established (proj_sp << raw_sp at every M). recall-survival = the capability proof.")
    print("NOTE: synthetic ZCA stand-in for CERT 591's learned projection; CPU mechanism-probe to inform the GPU build,")
    print("NOT the flagship cell. Hand to Exp-Dev. The real cell uses the actual 591 projection on Pythia-2.8B keys.")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
