"""_gpu_cap.py -- torch/GPU helpers for capacity-sweep matmuls (so GPU cells actually use the GPU).

The capacity cells were doing the big matmuls (V^T K, keys @ W^T, V @ R) in numpy on CPU -> GPU sat at 0% while the
cell ran for hours. These helpers push the matmuls to CUDA -> 10-100x faster + real GPU utilization. numpy in / float out.
"""
import numpy as np
import torch

_DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def _values(M, n_val, sparse, alpha, g):
    if sparse:
        V = np.zeros((M, n_val), np.float32); kk = max(1, int(alpha * n_val))
        for i in range(M):
            idx = g.choice(n_val, kk, replace=False); V[i, idx] = g.integers(0, 2, kk) * 2 - 1
    else:
        V = (g.integers(0, 2, (M, n_val)) * 2 - 1).astype(np.float32)
    return V


def recall_unique_t(keys, n_val, seed, sparse=False, alpha=0.10, flip=0.0):
    """Unique-value hetero recall on GPU. keys (M,nk) float; optional key-flip (key-collision-aware) + sparse values."""
    g = np.random.default_rng(seed); M, nk = keys.shape
    V = _values(M, n_val, sparse, alpha, g)
    with torch.no_grad():
        K = torch.from_numpy(np.ascontiguousarray(keys, dtype=np.float32)).to(_DEV)
        Vt = torch.from_numpy(V).to(_DEV); Vt = Vt / (Vt.norm(dim=1, keepdim=True) + 1e-8)
        if flip > 0:
            m = torch.rand(M, nk, device=_DEV) < flip; Kq = K.clone(); Kq[m] *= -1.0
        else:
            Kq = K
        W = Vt.t() @ K                       # (n_val, nk)
        scores = (Kq @ W.t()) @ Vt.t()       # (M, M)
        pred = scores.argmax(dim=1)
        return float((pred == torch.arange(M, device=_DEV)).float().mean().item())


def m50_unique_t(keys_fn, n_val, loads, seed, sparse=False, alpha=0.10, flip=0.0):
    """M at which recall first drops below 0.5. keys_fn(M)-> (M,nk) float keys for that load."""
    prev = 2
    for load in loads:
        M = keys_fn.M_for(load)
        if M < 2:
            continue
        K = keys_fn(M)
        if recall_unique_t(K, n_val, seed * 7 + M, sparse, alpha, flip) < 0.5:
            return prev
        prev = M
    return prev


def hopfield_recall_t(P, flip, steps, seed):
    """W-free auto-assoc Hopfield exact-recovery on GPU. P (M,n) +/-1. W@s = P^T(P s) - M s, zero-diagonal."""
    g = np.random.default_rng(seed)
    with torch.no_grad():
        Pt = torch.from_numpy(np.ascontiguousarray(P, dtype=np.float32)).to(_DEV)
        M, n = Pt.shape
        S = Pt * torch.where(torch.rand(M, n, device=_DEV) < flip, -1.0, 1.0)
        for _ in range(steps):
            WS = (Pt.t() @ (Pt @ S.t())).t() - M * S
            S = torch.sign(WS); S[S == 0] = 1.0
        return float((S == Pt).all(dim=1).float().mean().item())


def hop_recall(keys, n_unused, seed, sparse=False, alpha=0.10, flip=0.05, steps=6):
    """Confirmed real-encoder capacity metric: sign-binarize keys -> auto-assoc Hopfield exact-recovery (GPU).
    Drop-in for recall_unique_t signature. (sparse arg ignored here; sparse-pattern variant handled per-cell.)"""
    P = np.sign(np.ascontiguousarray(keys, dtype=np.float32)); P[P == 0] = 1.0
    return hopfield_recall_t(P, flip, steps, int(seed))


def whiten_gpu(K):
    """ZCA whitening on GPU (torch SVD) -- eliminates the CPU SVD bottleneck at large D. numpy in/out."""
    with torch.no_grad():
        X = torch.from_numpy(np.ascontiguousarray(K, dtype=np.float32)).to(_DEV)
        X = X - X.mean(0)
        cov = (X.t() @ X) / max(X.shape[0], 1)
        U, S, _ = torch.linalg.svd(cov)
        Wd = X @ ((U / torch.sqrt(S + 1e-3)) @ U.t())
        Wd = Wd / (Wd.norm(dim=1, keepdim=True) + 1e-8)
        return Wd.cpu().numpy().astype(np.float32)


def expand_gpu(emb, D, seed):
    """Nonlinear random-feature lift phi(x)=sign(Rx) on GPU. numpy in/out."""
    d0 = emb.shape[1]
    if D == d0:
        return np.ascontiguousarray(emb, dtype=np.float32)
    with torch.no_grad():
        g = torch.Generator(device=_DEV).manual_seed(int(seed))
        R = torch.randn(d0, D, generator=g, device=_DEV, dtype=torch.float32) / (d0 ** 0.5)
        E = torch.from_numpy(np.ascontiguousarray(emb, dtype=np.float32)).to(_DEV)
        return torch.sign(E @ R).cpu().numpy().astype(np.float32)
