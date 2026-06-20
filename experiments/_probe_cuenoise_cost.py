"""DE-RISK probe 2 (LEVER 1.5 path-b): the SUBSTRATE-NATIVE over-sparsity cost = CUE-NOISE ROBUSTNESS.
Associative memory recalls from a CORRUPTED cue (that is its function). A too-sparse pattern (tiny k) has too few bits to
error-correct a flipped cue -> fragile. A too-dense pattern fails CAPACITY at fixed load. If a moderate-f SWEET-SPOT emerges
(survives cue-noise AND capacity) that neither a too-sparse nor too-dense fixed-f hits -> path (b) is a genuine selection
problem with a substrate-native cost. (Readout-noise was the WRONG axis: probe 1 showed sparser is MORE readout-robust.)
"""
import numpy as np

N = 4096
ALPHA_C_BY_F = {0.2: 0.2, 0.1: 0.4, 0.05: 1.0, 0.02: 3.0, 0.01: 6.0, 0.005: 6.0, 0.002: 6.0, 0.001: 6.0}
F_GRID = [0.1, 0.05, 0.02, 0.01, 0.005, 0.002, 0.001]


def _sparse_pat(M, n, f, g):
    k = max(1, int(f * n)); P = np.zeros((M, n), np.float32)
    for i in range(M):
        idx = g.choice(n, k, replace=False); P[i, idx] = g.integers(0, 2, k) * 2 - 1
    return P


def recall_cue(target_alpha, f, n, seed, flip):
    """Auto-assoc recall with a CUE-NOISE flip-fraction (flip of the active bits are sign-flipped in the query)."""
    g = np.random.default_rng(seed); M = max(2, int(target_alpha * n))
    P = _sparse_pat(M, n, f, g); diag = (P * P).sum(0); s = P.copy()
    if flip > 0:
        for i in range(M):
            nz = np.nonzero(P[i])[0]; fl = nz[g.random(len(nz)) < flip]; s[i, fl] *= -1
    correct = 0; CHUNK = 2048
    for a in range(0, M, CHUNK):
        b = min(a + CHUNK, M)
        rc = np.sign((s[a:b] @ P.T) @ P - s[a:b] * diag)
        for i in range(a, b):
            nz = np.nonzero(P[i])[0]
            if len(nz) and np.all(rc[i - a][nz] == P[i][nz]):
                correct += 1
    return correct / M


if __name__ == "__main__":
    print("N=%d  cue-noise robustness probe (capN = f fails capacity at this load)" % N)
    for flip in [0.0, 0.1, 0.2, 0.3]:
        print("\n=== cue-flip=%.1f of active bits ===" % flip)
        for ta in [0.5, 1.0, 2.0]:
            row = []
            for f in F_GRID:
                cap = "Y" if ta <= ALPHA_C_BY_F[f] else "N"
                r = np.mean([recall_cue(ta, f, N, sd, flip) for sd in [1, 2]])
                row.append("f%.3f(k%d,c%s):%.2f" % (f, int(f * N), cap, r))
            print("  alpha=%.1f: %s" % (ta, "  ".join(row)))
