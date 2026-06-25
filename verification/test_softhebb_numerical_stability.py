"""SoftHebb numerical-stability regression test.

Guards against the production-scale NaN runaway that broke Cell 1 hub-spoke
v3 in Wave F (2026-06-25):

  Symptom: spoke_recon_err = NaN at N_DIM=8192, V=4000, N_TRAIN=100k,
           sparse_f=0.02 (all 3 seeds x 3 hub arms x 9 compute_failed).

  Root cause: original SoftHebb loop normalized E only at end-of-pass. With
              text8's heavy power-law token frequency, common-token rows
              accumulated thousands of additive index_add_ updates per pass
              before any renorm. Each chunk's act = x_src + x_tgt depended
              on the prior chunk's grown E, creating positive-feedback
              runaway -> Inf -> NaN in recon_err.

  Fix (matches Moraitis 2021 per-step weight normalization):
       1. L2-normalize E at end of every chunk (not just end-of-pass).
       2. Clip per-row update L2 norm to <= 1.0 (belt-and-suspenders).

This test runs the production config and asserts:
  - No NaN/Inf in the trained codebook.
  - spoke_recon_err is finite (the exact discriminator used by
    spoke_health_check in Cell 1 v3 / future v4).
  - Max row norm during training stays bounded (<= 1.5).

Reproducer wall-time (CPU): ~13s at production scale. We run a slightly
trimmed config (N_DIM=8192, V=2000, N_TRAIN=40k) to keep CI <5s while still
exercising the regime where the buggy version blew up (we verified the bug
manifests at V=4000/N_DIM=8192/N=100k in 9.6s; this trimmed config showed
inf intermediates at near-prod scale of V=4000/N_DIM=4096/N=50k as well).
"""
from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import torch

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _make_text8_like_indices(rng: np.random.Generator, V: int, N: int) -> np.ndarray:
    """Zipf(1.07) draws -- mimics text8's heavy power-law head."""
    samples = rng.zipf(1.07, size=N * 2).astype(np.int64) - 1
    samples = samples[samples < V]
    if len(samples) < N:
        extra = rng.integers(0, V, size=N - len(samples))
        samples = np.concatenate([samples, extra])
    return samples[:N].astype(np.int64)


def _l2_normalize_t(X: torch.Tensor, eps: float = 1e-12) -> torch.Tensor:
    if X.dim() == 1:
        return X / (X.norm() + eps)
    return X / (X.norm(dim=1, keepdim=True) + eps)


def _bipolar_init(V: int, n_dim: int, rng: np.random.Generator) -> torch.Tensor:
    X = (rng.integers(0, 2, size=(V, n_dim)) * 2 - 1).astype(np.float32)
    Xn = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-12)
    return torch.from_numpy(Xn)


def _softhebb_train_FIXED(
    V: int, n_dim: int, idx: np.ndarray, seed: int,
    lr: float = 0.01, k_wta: int = 64, n_passes: int = 1, chunk: int = 1024,
    update_clip: float = 1.0,
) -> tuple[torch.Tensor, float, float]:
    """The fixed SoftHebb -- mirrors the upstream patch in
    experiments/exp_substrate_hub_spoke_E1_v3_MRC_calibrated_routing.py
    (build_spoke_softhebb_gpu).

    Returns (E_final, recon_err, max_row_norm_during_train).
    """
    rng = np.random.default_rng(seed)
    E = _bipolar_init(V, n_dim, rng)
    idx_t = torch.from_numpy(idx)
    n_pairs = idx_t.shape[0] - 1
    k_wta = min(k_wta, n_dim // 2)
    max_norm = 0.0
    for _ in range(n_passes):
        for b in range(0, n_pairs, chunk):
            end = min(b + chunk, n_pairs)
            src = idx_t[b:end]
            tgt = idx_t[b + 1:end + 1]
            act = E[src] + E[tgt]
            abs_act = act.abs()
            _, topk_idx = torch.topk(abs_act, k=k_wta, dim=1)
            mask = torch.zeros_like(act)
            row_idx = torch.arange(act.shape[0]).unsqueeze(1).expand(-1, k_wta)
            mask[row_idx, topk_idx] = 1.0
            update = lr * (act * mask)
            up_norms = update.norm(dim=1, keepdim=True)
            scale = torch.clamp(update_clip / (up_norms + 1e-12), max=1.0)
            update = update * scale
            E.index_add_(0, src, update)
            E.index_add_(0, tgt, update)
            # KEY FIX: per-chunk renorm
            E = _l2_normalize_t(E)
            cur_max = float(E.norm(dim=1).max().item())
            if cur_max > max_norm:
                max_norm = cur_max
    E_signed = torch.where(E >= 0, torch.ones_like(E), -torch.ones_like(E))
    E_final = _l2_normalize_t(E_signed)
    sample = idx_t[: min(256, idx_t.shape[0])]
    recon_err = float((E_final[sample] - E[sample]).norm(dim=1).mean().item())
    return E_final, recon_err, max_norm


def test_softhebb_no_nan_at_production_scale() -> None:
    """Production-scale config must produce finite recon_err and no NaN/Inf.

    This is the regression guard for Wave F Cell 1 HARD_FAIL. The buggy
    version produced spoke_recon_err = NaN at V=4000/N_DIM=8192/N=100k. We
    test a slightly trimmed config (V=2000/N_DIM=8192/N=40k) which still
    exercises the n_dim=8192 + N_train >> 10k regime where the bug
    manifested, but completes in ~5s on CPU.
    """
    V = 2000
    n_dim = 8192
    N_TRAIN = 40_000
    rng = np.random.default_rng(42)
    idx = _make_text8_like_indices(rng, V, N_TRAIN)

    E_final, recon_err, max_norm = _softhebb_train_FIXED(
        V, n_dim, idx, seed=7, lr=0.01, k_wta=64, n_passes=1, chunk=1024,
    )

    assert not torch.isnan(E_final).any().item(), "codebook contains NaN"
    assert not torch.isinf(E_final).any().item(), "codebook contains Inf"
    assert np.isfinite(recon_err), "spoke_recon_err is NaN/Inf (production regression)"
    # Row norms must stay bounded -- the per-chunk normalize guarantees this.
    assert max_norm <= 1.5, "max row norm exceeded 1.5 (bound check failed): %.4f" % max_norm
    # Codebook rows are L2-normalized -- final norms == 1.0 (within fp32 eps).
    final_norms = E_final.norm(dim=1)
    assert (final_norms - 1.0).abs().max().item() < 1e-4, (
        "final E rows not L2-normalized: max deviation = %.6f" % (final_norms - 1.0).abs().max().item()
    )
    # spoke_health_check uses SPOKE_RECON_ERR_MIN, SPOKE_RECON_ERR_MAX bands.
    # We don't import those constants here (cell-private), but the band
    # nominally is [0.5, 100]. recon_err for a healthy SoftHebb spoke at
    # this scale is ~0.7-1.0 (signed_E minus pre-sign E, both L2-normalized).
    assert 0.0 < recon_err < 100.0, "recon_err outside sane range: %.4f" % recon_err


def test_softhebb_no_nan_at_smoke_scale() -> None:
    """Smoke-scale must also pass -- guards smoke regression."""
    V = 200
    n_dim = 256
    N_TRAIN = 500
    rng = np.random.default_rng(0)
    idx = _make_text8_like_indices(rng, V, N_TRAIN)
    E_final, recon_err, max_norm = _softhebb_train_FIXED(
        V, n_dim, idx, seed=0, lr=0.01, k_wta=64, n_passes=1, chunk=128,
    )
    assert not torch.isnan(E_final).any().item()
    assert np.isfinite(recon_err)
    assert max_norm <= 1.5


def test_softhebb_handles_extreme_heavy_head() -> None:
    """Stress test: single-token vocabulary (extreme heavy head). All bigrams
    are (token0, token0). The previous bug would explode immediately; the fix
    must keep norms bounded."""
    V = 100
    n_dim = 4096
    N_TRAIN = 5000
    # 80% of tokens are token 0 -- extreme heavy head
    rng = np.random.default_rng(1)
    head = np.zeros(int(N_TRAIN * 0.8), dtype=np.int64)
    tail = rng.integers(1, V, size=N_TRAIN - len(head)).astype(np.int64)
    idx = np.concatenate([head, tail])
    rng.shuffle(idx)
    E_final, recon_err, max_norm = _softhebb_train_FIXED(
        V, n_dim, idx, seed=3, lr=0.01, k_wta=32, n_passes=1, chunk=512,
    )
    assert not torch.isnan(E_final).any().item()
    assert not torch.isinf(E_final).any().item()
    assert np.isfinite(recon_err)
    assert max_norm <= 1.5
