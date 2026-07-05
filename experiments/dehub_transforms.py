"""dehub_transforms -- shared training-free content-embedding de-hubbing transforms.

Pure functions on a raw embedding matrix (NO label / scorer / target information
used). Each transform is applied to CONTENT features BEFORE any downstream
training (relation-scorer or RKD student), never as a post-hoc score rescore
(that lever is exp_schema_relation_hubness_debias_rescore_v1, already run, shown
partially phantom -- NOT repeated here).

Candidates (per notes/research_content_dehub_joint_lever_gen_encoder_2026-07-05.md
Section 1d, which measured Nk10-Gini reduction on both real content spaces):
  LOCAL_SCALING (PRIMARY)  -- Zelnik-Manor & Perona 2004 self-tuning local scale.
                              Realized here as an EXACT eigen-embedding of the
                              local-scaled affinity (kernel-PCA of the self-tuning
                              affinity), so the de-hubbed geometry becomes a unit-
                              normed feature matrix a bilinear scorer can train on
                              AND a Gram target an RKD student can match -- the
                              same math on any point set, no out-of-sample /
                              Nystrom step (fixed object codebook on the gen side;
                              per-batch on the encoder side). Feldbauer & Flexer
                              2019: nonlinear distance-distorting embeddings reduce
                              hubness even above intrinsic dimension.
  ZCA_WHITEN (SECONDARY)   -- full-covariance whitening (Su et al. 2021), a linear
                              feature transform fit on a reference set.
  ABTT (REFERENCE/weakest)  -- All-but-the-Top D (Mu & Viswanath 2018): subtract
                              mean + top-D PCs. Note: the ABTT paper makes NO
                              hubness claim; retained as the weakest-expected arm.

Mechanism check throughout: nk_gini (Gini of the k-occurrence distribution Nk).
A transform DE-HUBS iff nk_gini(transformed) < nk_gini(raw).

ASCII-only. No emojis. No em dashes. float64 internals; float32 out.
"""
from __future__ import annotations

from typing import Dict, Optional

import numpy as np

_EPS = 1e-9


def _unit_rows(X: np.ndarray, eps: float = _EPS) -> np.ndarray:
    """Row-wise L2 normalize (float64)."""
    Xr = np.ascontiguousarray(X, dtype=np.float64)
    nrm = np.linalg.norm(Xr, axis=1, keepdims=True) + eps
    return Xr / nrm


# ---------------------------------------------------------------------------
# Hubness measurement (Nk k-occurrence Gini)
# ---------------------------------------------------------------------------
def nk_occurrence(X: np.ndarray, k: int = 10) -> np.ndarray:
    """Object-side k-occurrence Nk: how many times each point appears inside
    another point's cosine top-k (self excluded). X:(n,d) -> (n,) int counts."""
    Xu = _unit_rows(X)
    n = Xu.shape[0]
    if n < 2:
        return np.zeros(n, dtype=np.float64)
    S = Xu @ Xu.T
    np.fill_diagonal(S, -np.inf)
    kk = int(min(k, n - 1))
    idx = np.argpartition(-S, kk - 1, axis=1)[:, :kk]
    nk = np.bincount(idx.reshape(-1), minlength=n).astype(np.float64)
    return nk


def gini(x: np.ndarray) -> float:
    """Gini coefficient of a non-negative distribution (0 = uniform)."""
    v = np.sort(np.asarray(x, dtype=np.float64))
    n = v.size
    if n == 0:
        return float("nan")
    s = v.sum()
    if s <= 0:
        return 0.0
    idx = np.arange(1, n + 1, dtype=np.float64)
    return float((2.0 * np.sum(idx * v)) / (n * s) - (n + 1.0) / n)


def nk_gini(X: np.ndarray, k: int = 10) -> float:
    """Gini of the Nk k-occurrence distribution -- the hubness scalar."""
    return gini(nk_occurrence(X, k))


# ---------------------------------------------------------------------------
# LOCAL_SCALING (primary) -- exact eigen-embedding of the self-tuning affinity
# ---------------------------------------------------------------------------
def local_scaling_affinity(X: np.ndarray, k: int = 10, eps: float = _EPS) -> np.ndarray:
    """Zelnik-Manor & Perona 2004 self-tuning affinity A[i,j] =
    exp(-d(i,j)^2 / (sigma_i sigma_j)), sigma_i = dist to i's k-th NN.
    Unit-row X -> d(i,j)^2 = 2 - 2 cos(i,j). Returns symmetric A:(n,n) in [0,1]."""
    Xu = _unit_rows(X, eps)
    n = Xu.shape[0]
    S = np.clip(Xu @ Xu.T, -1.0, 1.0)
    D2 = np.maximum(2.0 - 2.0 * S, 0.0)
    kk = int(min(k, n - 1)) if n > 1 else 1
    d2 = D2.copy()
    np.fill_diagonal(d2, np.inf)
    sig2 = np.partition(d2, kk - 1, axis=1)[:, kk - 1]      # k-th smallest sq-dist
    sigma = np.sqrt(np.maximum(sig2, eps))                   # (n,)
    denom = np.outer(sigma, sigma) + eps
    A = np.exp(-D2 / denom)
    np.fill_diagonal(A, 1.0)
    return 0.5 * (A + A.T)


def local_scaling_embedding(X: np.ndarray, k: int = 10, rank: Optional[int] = None,
                            eps: float = _EPS) -> np.ndarray:
    """Feature realization of LOCAL_SCALING: kernel-PCA of the symmetric-normalized
    self-tuning affinity. Returns a UNIT-NORMED (n, rank) feature matrix whose
    cosine geometry is the de-hubbed local-scaled geometry -- usable directly by a
    bilinear scorer (feature input) and as an RKD Gram target (Phi @ Phi.T is a
    cosine similarity in [-1,1], same range as the raw teacher Gram, so a fair
    RAW-vs-DEHUB comparison never changes the target SCALE, only its GEOMETRY)."""
    Xu = _unit_rows(X, eps)
    n = Xu.shape[0]
    if n < 3:
        return Xu.astype(np.float32)
    A = local_scaling_affinity(Xu, k, eps)
    deg = A.sum(axis=1)
    dinv = 1.0 / np.sqrt(deg + eps)
    M = (dinv[:, None] * A) * dinv[None, :]
    M = 0.5 * (M + M.T)
    w, U = np.linalg.eigh(M)                                 # ascending
    order = np.argsort(-w)
    w = w[order]
    U = U[:, order]
    r = int(rank) if rank is not None else min(n - 1, 128)
    r = max(1, min(r, n))
    wpos = np.maximum(w[:r], 0.0)
    Phi = U[:, :r] * np.sqrt(wpos)[None, :]
    return _unit_rows(Phi, eps).astype(np.float32)


# ---------------------------------------------------------------------------
# ZCA whitening (secondary) -- fit on a reference set, apply out-of-sample
# ---------------------------------------------------------------------------
def fit_zca(Xref: np.ndarray, eps: float = 1e-3) -> Dict[str, np.ndarray]:
    Xr = np.ascontiguousarray(Xref, dtype=np.float64)
    mu = Xr.mean(axis=0, keepdims=True)
    Xc = Xr - mu
    C = (Xc.T @ Xc) / max(1, Xc.shape[0])
    w, V = np.linalg.eigh(0.5 * (C + C.T))
    w = np.maximum(w, 0.0)
    W = (V * (1.0 / np.sqrt(w + eps))[None, :]) @ V.T
    return {"mu": mu, "W": W.astype(np.float64)}


def apply_zca(X: np.ndarray, fit: Dict[str, np.ndarray], eps: float = _EPS) -> np.ndarray:
    Xc = np.ascontiguousarray(X, dtype=np.float64) - fit["mu"]
    return _unit_rows(Xc @ fit["W"], eps).astype(np.float32)


def zca_whiten(X: np.ndarray, eps: float = 1e-3) -> np.ndarray:
    """Transductive convenience: fit ZCA on X and apply to X."""
    return apply_zca(X, fit_zca(X, eps))


# ---------------------------------------------------------------------------
# ABTT (reference / weakest-expected) -- All-but-the-Top D
# ---------------------------------------------------------------------------
def fit_abtt(Xref: np.ndarray, D: int = 1) -> Dict[str, np.ndarray]:
    Xr = np.ascontiguousarray(Xref, dtype=np.float64)
    mu = Xr.mean(axis=0, keepdims=True)
    Xc = Xr - mu
    _, _, Vt = np.linalg.svd(Xc, full_matrices=False)
    D = max(0, min(int(D), Vt.shape[0]))
    pcs = Vt[:D] if D > 0 else np.zeros((0, Xr.shape[1]), dtype=np.float64)
    return {"mu": mu, "pcs": pcs.astype(np.float64)}


def apply_abtt(X: np.ndarray, fit: Dict[str, np.ndarray], eps: float = _EPS) -> np.ndarray:
    Xc = np.ascontiguousarray(X, dtype=np.float64) - fit["mu"]
    pcs = fit["pcs"]
    if pcs.shape[0] > 0:
        Xc = Xc - (Xc @ pcs.T) @ pcs
    return _unit_rows(Xc, eps).astype(np.float32)


def abtt(X: np.ndarray, D: int = 1) -> np.ndarray:
    """Transductive convenience: fit ABTT on X and apply to X."""
    return apply_abtt(X, fit_abtt(X, D))


# ---------------------------------------------------------------------------
# Unified dispatch (used by both harnesses so the "same method" is literally the
# same code). Returns a de-hubbed UNIT-NORMED feature matrix of X.
# ---------------------------------------------------------------------------
def dehub_features(X: np.ndarray, method: str, k: int = 10,
                   rank: Optional[int] = None, zca_eps: float = 1e-3,
                   abtt_D: int = 1) -> np.ndarray:
    m = method.upper()
    if m in ("RAW", "CONTENT_RAW", "CE_BASELINE", "NONE"):
        return _unit_rows(X).astype(np.float32)
    if m in ("LOCAL_SCALING", "LOCALSCALING", "LS"):
        return local_scaling_embedding(X, k=k, rank=rank)
    if m in ("ZCA_WHITEN", "ZCA"):
        return zca_whiten(X, eps=zca_eps)
    if m == "ABTT":
        return abtt(X, D=abtt_D)
    raise ValueError(f"unknown dehub method {method!r}")


# ---------------------------------------------------------------------------
# Formula self-tests (import-cheap; construct a by-construction hub set and
# verify each transform's Nk-Gini behaviour + determinism).
# ---------------------------------------------------------------------------
def _make_hub_content(seed: int, n: int = 400, d: int = 48, n_hub: int = 6,
                      hub_pull: float = 0.75) -> np.ndarray:
    """Construct a content matrix with a small set of geometric hubs: most points
    are random unit vectors pulled toward one of n_hub central directions."""
    rng = np.random.RandomState(seed)
    hubs = rng.standard_normal((n_hub, d))
    hubs /= np.linalg.norm(hubs, axis=1, keepdims=True) + _EPS
    base = rng.standard_normal((n, d))
    base /= np.linalg.norm(base, axis=1, keepdims=True) + _EPS
    assign = rng.randint(0, n_hub, size=n)
    X = (1.0 - hub_pull) * base + hub_pull * hubs[assign]
    X[:n_hub] = hubs                          # plant the hubs themselves
    X /= np.linalg.norm(X, axis=1, keepdims=True) + _EPS
    return X.astype(np.float32)


def formula_selftests(verbose: bool = True) -> Dict[str, float]:
    # 1. gini sanity: uniform -> ~0; one-hot -> ~1 - 1/n.
    g_uniform = gini(np.ones(100))
    g_spike = gini(np.array([0.0] * 99 + [100.0]))
    assert abs(g_uniform) < 1e-9, f"gini(uniform)={g_uniform} != 0"
    assert g_spike > 0.98, f"gini(spike)={g_spike} not near 1"

    # 2a. anisotropy set (single dominant common direction -- the case ABTT D=1
    #     is designed for): ALL THREE transforms must REDUCE Nk-Gini.
    Xa = _make_hub_content(seed=0, n_hub=1, hub_pull=0.55)
    ga_raw = nk_gini(Xa, k=10)
    ga_ls = nk_gini(local_scaling_embedding(Xa, k=10), k=10)
    ga_zca = nk_gini(zca_whiten(Xa), k=10)
    ga_abtt = nk_gini(abtt(Xa, D=1), k=10)
    assert ga_ls < ga_raw - 1e-6, f"LS did not de-hub (aniso): {ga_ls:.4f} !< {ga_raw:.4f}"
    assert ga_zca < ga_raw - 1e-6, f"ZCA did not de-hub (aniso): {ga_zca:.4f} !< {ga_raw:.4f}"
    assert ga_abtt < ga_raw - 1e-6, f"ABTT did not de-hub (aniso): {ga_abtt:.4f} !< {ga_raw:.4f}"

    # 2b. harder multi-hub set (6 competing hub directions): LOCAL_SCALING (the
    #     PRIMARY, nonlinear distance-distorting method) must still de-hub. ABTT
    #     (linear top-D removal) is NOT asserted here -- consistent with the note:
    #     the ABTT source paper makes no hubness claim and it is the weakest arm.
    X = _make_hub_content(seed=0)
    g_raw = nk_gini(X, k=10)
    g_ls = nk_gini(local_scaling_embedding(X, k=10), k=10)
    g_zca = nk_gini(zca_whiten(X), k=10)
    g_abtt = nk_gini(abtt(X, D=1), k=10)
    assert g_ls < g_raw - 1e-6, f"LOCAL_SCALING did not de-hub: {g_ls:.4f} !< {g_raw:.4f}"

    # 3. the direct self-tuning affinity also de-hubs (reproduces the note's
    #    similarity-space Nk-Gini reduction as a positive control on the method).
    A = local_scaling_affinity(X, k=10)
    np.fill_diagonal(A, -np.inf)
    kk = 10
    idx = np.argpartition(-A, kk - 1, axis=1)[:, :kk]
    nk_aff = np.bincount(idx.reshape(-1), minlength=X.shape[0]).astype(np.float64)
    g_aff = gini(nk_aff)
    assert g_aff < g_raw - 1e-6, f"affinity did not de-hub: {g_aff:.4f} !< {g_raw:.4f}"

    # 4. determinism (same input -> byte-identical output).
    e1 = local_scaling_embedding(X, k=10)
    e2 = local_scaling_embedding(X, k=10)
    assert e1.tobytes() == e2.tobytes(), "local_scaling_embedding non-deterministic"

    # 5. embedding is unit-normed and rank-bounded.
    e = local_scaling_embedding(X, k=10, rank=32)
    assert e.shape[1] == 32, f"rank not honoured: {e.shape}"
    nrm = np.linalg.norm(e, axis=1)
    assert np.allclose(nrm, 1.0, atol=1e-4), "embedding rows not unit-normed"

    # 6. dispatch RAW is identity-up-to-normalization.
    r = dehub_features(X, "RAW")
    assert np.allclose(np.linalg.norm(r, axis=1), 1.0, atol=1e-4)

    out = {"g_raw": g_raw, "g_local_scaling": g_ls, "g_zca": g_zca,
           "g_abtt": g_abtt, "g_affinity": g_aff}
    if verbose:
        print("[dehub_transforms selftest] "
              + " ".join(f"{kk2}={vv:.4f}" for kk2, vv in out.items())
              + " PASS", flush=True)
    return out


if __name__ == "__main__":
    formula_selftests()
