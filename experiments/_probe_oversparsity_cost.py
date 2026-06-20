"""DE-RISK probe (LEVER 1.5 path-b): does a GENUINE over-sparsity precision/SNR cost emerge?
Auto-assoc sparse recall WITH a finite readout-noise floor (substrate cannot read scores with infinite precision).
If too-sparse f FAILS under noise (small margin) while moderate f survives, AND too-dense f fails capacity (M>alpha_c*n),
then there is a REAL sweet-spot (emergent, not modeled) -> path (b) is a genuine selection problem. data-decides.
"""
import numpy as np

N = 4096
FLIP = 0.0                                            # query = clean stored pattern (isolate the precision floor, not cue noise)
ALPHA_C_BY_F = {1.0: 0.02, 0.5: 0.05, 0.2: 0.2, 0.1: 0.4, 0.05: 1.0, 0.02: 3.0, 0.01: 6.0, 0.005: 6.0, 0.002: 6.0, 0.001: 6.0}
F_GRID = [0.1, 0.05, 0.02, 0.01, 0.005, 0.002, 0.001]


def _sparse_pat(M, n, f, g):
    k = max(1, int(f * n)); P = np.zeros((M, n), np.float32)
    for i in range(M):
        idx = g.choice(n, k, replace=False); P[i, idx] = g.integers(0, 2, k) * 2 - 1
    return P


def recall_noisy(target_alpha, f, n, seed, noise_frac):
    """Auto-assoc recall; add Gaussian readout noise of std = noise_frac * RMS(raw active-bit scores) BEFORE sign()."""
    g = np.random.default_rng(seed); M = max(2, int(target_alpha * n))
    P = _sparse_pat(M, n, f, g); diag = (P * P).sum(0); s = P.copy()
    if FLIP > 0:
        for i in range(M):
            nz = np.nonzero(P[i])[0]; fl = nz[g.random(len(nz)) < FLIP]; s[i, fl] *= -1
    correct = 0; CHUNK = 2048
    # calibrate noise to the RMS of the raw scores on active bits (a finite-precision readout floor)
    raw0 = (s[:min(M, 512)] @ P.T) @ P - s[:min(M, 512)] * diag
    rms = float(np.sqrt(np.mean(raw0 ** 2))) + 1e-9
    for a in range(0, M, CHUNK):
        b = min(a + CHUNK, M)
        raw = (s[a:b] @ P.T) @ P - s[a:b] * diag
        if noise_frac > 0:
            raw = raw + g.standard_normal(raw.shape).astype(np.float32) * (noise_frac * rms)
        rc = np.sign(raw)
        for i in range(a, b):
            nz = np.nonzero(P[i])[0]
            if len(nz) and np.all(rc[i - a][nz] == P[i][nz]):
                correct += 1
    return correct / M


if __name__ == "__main__":
    print("N=%d  (capacity: f fails when target_alpha > alpha_c(f))" % N)
    for noise_frac in [0.0, 0.5, 1.0]:
        print("\n=== readout noise_frac=%.1f (x RMS score) ===" % noise_frac)
        for ta in [0.5, 1.0]:
            row = []
            for f in F_GRID:
                cap_ok = ta <= ALPHA_C_BY_F[f]
                r = np.mean([recall_noisy(ta, f, N, sd, noise_frac) for sd in [1, 2]])
                k = int(f * N)
                row.append("f=%.3f(k=%d,cap%s):%.2f" % (f, k, "Y" if cap_ok else "N", r))
            print("  load alpha=%.1f: %s" % (ta, "  ".join(row)))
