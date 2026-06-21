"""Skunkworks 2026-06-21 -- flagship capacity DEMO v2 (FAITHFUL a3f473dd associative store; fixes v1's wrong readout).
v1 was flawed: used cosine-NN-over-keys (NOT the a3f473dd store) + a saturated sweep -> meaningless 1.0x. Caught it.
v2 uses the FAITHFUL readout: KV associative store W = sum_i v_i k_i^T ; recall = sign(W @ k_q) bit-accuracy vs v_i
(the a3f473dd raw-sign readout). Capacity ceiling = max M where mean fact-recall (bit-acc>=0.90) >= 0.80. Sparse keys
(k-of-N) -> LESS crosstalk in W -> Willshaw SUPER-capacity vs dense. THE CLAIM: B(sparse_proj)/A(dense_proj) >= 3x.

3 arms (keys d-dim; values bipolar d-dim; query = key + noise):
  A dense_proj  : project (whiten) keys, store dense
  B sparse_proj : project -> whiten -> top-k (redesigned flagship encode), store k-of-N sparse
  C raw_sparse  : top-k raw keys
HEAT-SAFE: store W is d x d; recall is O(M*d^2) (NO M x M). d=128, M up to 20000 fine (~seconds). ASCII.
"""
from __future__ import annotations
import numpy as np


def keys(M, d, rng, n_shared=8, shared=4.0):
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


def encode(kind, M, d, f, rng):
    K = keys(M, d, rng)
    if kind == 'A_dense_proj':  return zca(K)
    if kind == 'B_sparse_proj': return topk(zca(K), f)
    if kind == 'C_raw_sparse':  return topk(K, f)


def fact_recall(kind, M, d, f, seed, noise):
    rng = np.random.default_rng(seed)
    Kk = encode(kind, M, d, f, rng)
    # normalize keys so the store is scale-comparable across arms
    Kn = Kk / (np.linalg.norm(Kk, axis=1, keepdims=True) + 1e-9)
    V = np.sign(rng.standard_normal((M, d)))            # bipolar values
    W = V.T @ Kn                                         # KV store W = sum_i v_i k_i^T  (d x d)
    Q = Kn + noise * rng.standard_normal(Kn.shape) / np.sqrt(d)   # noisy key query
    Qn = Q / (np.linalg.norm(Q, axis=1, keepdims=True) + 1e-9)
    rec = np.sign(Qn @ W.T)                              # sign(W @ k_q) per fact  (M x d)
    bitacc = (rec == V).mean(axis=1)                    # per-fact bit-accuracy vs true value
    return float((bitacc >= 0.90).mean())              # fraction of facts recalled (bit-acc>=0.90)


def ceiling(kind, d, f, noise, Ms):
    last = 0
    for M in Ms:
        r = float(np.mean([fact_recall(kind, M, d, f, s, noise) for s in (1, 2, 3)]))
        if r >= 0.80: last = M
        else: return last, M, r
    return last, None, None


def main():
    d, noise, f = 128, 0.3, 0.05
    Ms = [200, 500, 1000, 2000, 5000, 10000, 20000]
    print("FLAGSHIP CAPACITY DEMO v2 (FAITHFUL a3f473dd store): sparse-proj vs dense-proj capacity ceiling.")
    print(f"  d={d}, f={f} (k={int(f*d)}), noise={noise}, store W=sum v_i k_i^T, recall=sign(W k_q) bit-acc>=0.90, 3 seeds")
    print(f"  M-sweep {Ms}; ceiling = max M with fact-recall>=0.80\n")
    res = {}
    for kind in ('A_dense_proj', 'B_sparse_proj', 'C_raw_sparse'):
        c = ceiling(kind, d, f, noise, Ms)
        res[kind] = c[0]
        drop = f" (drops to {c[2]:.2f} at M={c[1]})" if c[1] else " (>= max M -- raise sweep)"
        print(f"  {kind:16s} ceiling ~ {c[0]}{drop}")
    a, b, cc = res['A_dense_proj'], res['B_sparse_proj'], res['C_raw_sparse']
    rba = (b / a) if a > 0 else float('inf'); rbc = (b / cc) if cc > 0 else float('inf')
    print(f"\n  CAPACITY RATIO  B(sparse_proj)/A(dense_proj) = {rba:.1f}x  |  B/C(raw_sparse) = {rbc:.1f}x")
    if a == 0 or b == 0 or (res['A_dense_proj'] == Ms[-1]):
        print("  INCONCLUSIVE: an arm didn't reach its ceiling in-sweep -- raise M (regime too easy). Not a real ratio.")
    else:
        v = (">=3x GREEN: flagship super-capacity claim HOLDS on CPU" if rba >= 3.0
             else f"{rba:.1f}x: sparse adds capacity, <3x bar" if rba > 1.2 else f"{rba:.1f}x: no gain -> MM")
        print(f"  VERDICT: {v}")
    print("\nNOTE: faithful a3f473dd KV store (W=sum v k^T, sign-readout) + whiten-before-topk encode; CPU build to inform")
    print("the GPU flagship. v1 (cosine-NN, saturated) was caught + fixed. Hand to Exp-Dev.")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
