"""Skunkworks 2026-06-21 -- flagship capacity DEMO v3: FAITHFUL = a3f473dd's VERBATIM recall (copied from
experiments/exp_sparse_boundary_v2_cpu_v1.py lines 41-61, the cert-atom's actual mechanism -- NOT re-implemented).
v1 (cosine-NN) + v2 (hetero-KV) were both the WRONG store; a3f473dd is AUTO-ASSOCIATIVE k-of-N sparse-pattern recall
r=sign((s@P.T)@P - s*diag), FLIP=0.05. The flagship's NEW question: do whiten-before-topk patterns from REALISTIC
PROJECTED keys retain a3f473dd's super-capacity (alpha_c RISES as f decreases) vs RANDOM k-of-N (the proven control)?
HEAT-SAFE: N=1024 + LOADS capped at 3.0 (a3f473dd uses N=8192 = the HEAVY run that caused the sparse-onset runaway --
NOT run here). Small-N shows the DIRECTION; the full >=3x at scale rides the GPU cell. ASCII.
"""
from __future__ import annotations
import numpy as np

FLIP = 0.05
N = 1024
LOADS = [0.05, 0.1, 0.2, 0.4, 0.7, 1.0, 1.5, 2.0, 3.0]   # capped (heat-safe; a3f473dd's full goes to 6.0 at N=8192)


def random_kofn(M, n, f, g):                              # a3f473dd sparse_pat VERBATIM (the proven control)
    k = max(1, int(f * n)); P = np.zeros((M, n), np.float32)
    for i in range(M):
        idx = g.choice(n, k, replace=False); P[i, idx] = g.integers(0, 2, k) * 2 - 1
    return P


def whiten_topk_projected(M, n, f, g):                   # the FLAGSHIP encode: realistic projected keys -> whiten -> top-k -> k-of-N
    n_shared = 8
    dirs = g.standard_normal((n_shared, n))
    K = (g.standard_normal((M, n_shared)) * 4.0) @ dirs + g.standard_normal((M, n))   # concentrated-energy (InfoNCE-like)
    Kc = K - K.mean(0, keepdims=True); cov = (Kc.T @ Kc) / M
    U, S, _ = np.linalg.svd(cov + 1e-6 * np.eye(n)); Kw = Kc @ (U @ np.diag(1.0/np.sqrt(S+1e-6)) @ U.T)  # whiten
    k = max(1, int(f * n)); P = np.zeros((M, n), np.float32)
    idx = np.argpartition(-np.abs(Kw), k - 1, axis=1)[:, :k]; r = np.arange(M)[:, None]
    P[r, idx] = np.sign(Kw[r, idx])                       # top-k -> {-1,+1} k-of-N pattern
    return P


def recall(P, g):                                        # a3f473dd recall VERBATIM (lines 48-61)
    M, n = P.shape; diag = (P * P).sum(0); s = P.copy()
    for i in range(M):
        nz = np.nonzero(P[i])[0]; fl = nz[g.random(len(nz)) < FLIP]; s[i, fl] *= -1
    correct = 0; CHUNK = 2048
    for a in range(0, M, CHUNK):
        b = min(a + CHUNK, M)
        rc = np.sign((s[a:b] @ P.T) @ P - s[a:b] * diag)
        for i in range(a, b):
            nz = np.nonzero(P[i])[0]
            if np.all(rc[i - a][nz] == P[i][nz]): correct += 1
    return correct / M


def cap(patgen, f, seed):                                # a3f473dd cap loop VERBATIM (with custom pattern gen)
    g = np.random.default_rng(seed); c = 0.0
    for load in LOADS:
        M = max(2, int(load * N))
        if recall(patgen(M, N, f, np.random.default_rng(seed * 13 + M)), g) >= 0.95:
            c = load
        else:
            break
    return c


def main():
    fs = [0.5, 0.1, 0.05, 0.02]   # dense-ish -> sparse
    print("FLAGSHIP CAPACITY v3 (FAITHFUL a3f473dd recall, N=%d, heat-safe): does whiten-before-topk retain super-capacity?" % N)
    print("  alpha_c(f) = max LOAD at recall>=0.95; super-capacity = alpha_c RISES as f decreases. 2 seeds.\n")
    for label, patgen in (("random_kofn (a3f473dd control)", random_kofn), ("whiten_topk_projected (FLAGSHIP encode)", whiten_topk_projected)):
        acs = {}
        for f in fs:
            acs[f] = float(np.mean([cap(patgen, f, s) for s in (7, 17)]))
        rising = all(acs[fs[i]] >= acs[fs[i-1]] - 1e-9 for i in range(1, len(fs)))   # monotone rise as f decreases
        print(f"  {label:38s} alpha_c/f: " + " ".join(f"f{f}={acs[f]:.2f}" for f in fs) + f"   super-capacity(rises)? {rising}")
    print("\n  Read: if whiten_topk_projected shows alpha_c RISING as f decreases (like random_kofn control), the flagship")
    print("  encode RETAINS a3f473dd super-capacity -> capacity claim plausible (full >=3x at scale = GPU cell). If FLAT/")
    print("  falling, the projection's structure breaks super-capacity -> flagship capacity at-risk. N=1024 shows DIRECTION only.")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
