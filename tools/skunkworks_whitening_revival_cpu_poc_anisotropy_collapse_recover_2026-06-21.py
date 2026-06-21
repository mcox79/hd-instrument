"""Skunkworks 2026-06-21 -- CPU PROOF-OF-CONCEPT for the WHITENING REVIVAL I routed (de-risk my own ruling before the fleet acts).
HYPOTHESIS (my re-VET): the M-indep superposition ARM1 collapses on REAL learned keys NOT because superposition fails, but
because pythia keys are ANISOTROPIC (large common-mode) -> the linear readout r = W.cue ~ common-mode * sum(all codes) swamps
the per-key signal -> chance. FIX = isotropize (mean-center / shrinkage-ZCA-whiten) the keys -> remove common-mode -> ARM1
should RECOVER (the isotropic random-core held 0.824). ARM2 softmax should hold throughout (normalize+contrast removes common-mode).

This PoC (synthetic, no GPU/model) tests all 4 legs:
  (A) ISOTROPIC keys (N(0,1), = random-core)            -> ARM1 should HOLD   (reproduce random-core)
  (B) ANISOTROPIC keys (strong common-mode mu added)    -> ARM1 should COLLAPSE to ~chance (reproduce the pythia learned-key result)
  (C) (B) + MEAN-CENTER (subtract mean key)             -> ARM1 should RECOVER
  (D) (B) + SHRINKAGE-ZCA-WHITEN (the flagship method)  -> ARM1 should RECOVER (>= mean-center)
  ARM2 softmax-attention reported for all -> expected HOLD throughout.
Mechanism reused VERBATIM from the dense-KV cells (ARM1 W=code[y].T@Ks O(d^2); ARM2 softmax beta=1/sqrt(d); C-codebook decode).
ASCII; numpy-only; deterministic per seed (no Date/random-global).
"""
from __future__ import annotations
import numpy as np

C = 256          # codebook (chance = 1/256 = 0.0039)
D = 768
BETA = 1.0 / np.sqrt(D)


def _norm(X):
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def _decode(R, codebook):
    return np.argmax(_norm(R) @ codebook.T, axis=1)


def arm1_arm2(K, y, codebook, sigma, seed):
    """K already in the desired geometry; scale to Ramsauer norm ~sqrt(d) (matches the cells). Returns (arm1_recall, arm2_recall)."""
    g = np.random.default_rng(seed * 911 + len(K))
    d = K.shape[1]
    Ks = _norm(K) * np.sqrt(d)                                  # Ramsauer scale (unit-dir x sqrt(d))
    M = len(Ks); qn = min(M, 2000)
    qidx = np.arange(M) if M <= qn else np.sort(g.choice(M, qn, replace=False))
    cue = Ks[qidx] + sigma * g.standard_normal((len(qidx), d)).astype(np.float32)
    ytrue = y[qidx]
    W = codebook[y].T @ Ks                                      # (d,d) M-indep superposition
    a1 = float((_decode(cue @ W.T, codebook) == ytrue).mean())
    logits = BETA * (cue @ Ks.T); logits -= logits.max(axis=1, keepdims=True)
    wts = np.exp(logits); wts /= wts.sum(axis=1, keepdims=True)
    a2 = float((_decode(wts @ codebook[y], codebook) == ytrue).mean())
    return round(a1, 4), round(a2, 4)


def shrinkage_zca(K, tau=0.05):
    """Flagship whiten-before-topk shrinkage-ZCA (rank-deficient-safe): floor eigenvalues at tau*max_eig (relative, not abs)."""
    Kc = K - K.mean(0, keepdims=True)
    cov = (Kc.T @ Kc) / len(Kc)
    w, V = np.linalg.eigh(cov)
    w = np.maximum(w, tau * w.max())                            # shrinkage floor (relative)
    Wz = V @ np.diag(1.0 / np.sqrt(w)) @ V.T
    return Kc @ Wz


def make_keys(kind, M, d, seed):
    g = np.random.default_rng(seed)
    iso = g.standard_normal((M, d)).astype(np.float32)
    if kind == "isotropic":
        return iso
    # anisotropic: add a large common-mode mu (a dominant shared direction) -> cone / high mean cosine
    mu = g.standard_normal((1, d)).astype(np.float32)
    mu = mu / np.linalg.norm(mu) * np.sqrt(d) * 3.0            # common-mode ~3x the per-key signal norm
    return iso + mu


def mean_cos(K):
    Kn = _norm(K); S = Kn @ Kn.T
    iu = np.triu_indices(len(Kn), 1)
    return float(S[iu].mean())


def main():
    SEEDS = [0, 1, 2]; MS = [3000, 10000]; SIGMA = 0.1
    print(f"WHITENING-REVIVAL CPU PoC  C={C} d={D} chance={1/C:.4f}  seeds={SEEDS}  M={MS}  sigma={SIGMA}")
    print(f"{'cond':<26}{'M':>7}{'ARM1':>9}{'ARM2':>9}{'mean_cos':>10}")
    agg = {}
    for M in MS:
        rows = {"A_isotropic": [], "B_anisotropic": [], "C_meancenter": [], "D_shrinkZCA": []}
        for seed in SEEDS:
            g = np.random.default_rng(1000 + seed)
            y = g.integers(0, C, M)
            cb = _norm(g.standard_normal((C, D)).astype(np.float32))
            Kiso = make_keys("isotropic", M, D, seed)
            Kani = make_keys("anisotropic", M, D, seed)
            Kmc = Kani - Kani.mean(0, keepdims=True)
            Kzca = shrinkage_zca(Kani)
            rows["A_isotropic"].append((*arm1_arm2(Kiso, y, cb, SIGMA, seed), mean_cos(Kiso)))
            rows["B_anisotropic"].append((*arm1_arm2(Kani, y, cb, SIGMA, seed), mean_cos(Kani)))
            rows["C_meancenter"].append((*arm1_arm2(Kmc, y, cb, SIGMA, seed), mean_cos(Kmc)))
            rows["D_shrinkZCA"].append((*arm1_arm2(Kzca, y, cb, SIGMA, seed), mean_cos(Kzca)))
        for cond, vals in rows.items():
            a1 = float(np.median([v[0] for v in vals])); a2 = float(np.median([v[1] for v in vals])); mc = float(np.median([v[2] for v in vals]))
            agg[(cond, M)] = (a1, a2, mc)
            print(f"{cond:<26}{M:>7}{a1:>9.4f}{a2:>9.4f}{mc:>10.4f}")
    print("\nVERDICT (the whitening-revival hypothesis):")
    okB = agg[("B_anisotropic", 10000)][0] < 0.10
    okA = agg[("A_isotropic", 10000)][0] >= 0.50
    recC = agg[("C_meancenter", 10000)][0]; recD = agg[("D_shrinkZCA", 10000)][0]
    okrec = max(recC, recD) >= 0.50
    print(f"  (A) isotropic ARM1 holds @10k:        {agg[('A_isotropic',10000)][0]:.3f}  -> {'YES' if okA else 'NO'} (reproduce random-core)")
    print(f"  (B) anisotropic ARM1 collapses @10k:  {agg[('B_anisotropic',10000)][0]:.3f}  -> {'YES (~chance)' if okB else 'NO'} (reproduce pythia learned-key)")
    print(f"  (C) mean-center recovers @10k:        {recC:.3f}")
    print(f"  (D) shrinkage-ZCA recovers @10k:      {recD:.3f}")
    print(f"  REVIVAL MECHANISM CONFIRMED: {okA and okB and okrec}  (isotropic holds + anisotropic collapses + whitening recovers ARM1)")
    print(f"  -> if CONFIRMED: the GPU whitening-revival on REAL pythia keys is well-motivated (isotropize -> ARM1 should recover).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
