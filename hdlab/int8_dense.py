"""INT8 dense workspace utilities per E v5 CG finding (2026-07-01, commit 716174a7).

Chain-grade result: at N=8192 in WM capacity-crack regime M∈{40k,80k}, INT8_DENSE
recall matches FP32 within 0.0015 at 0.25x memory. Cross-seed cv max 0.045.

Substrate design implication: use int8 dense workspaces when memory-bound in the
capacity-crack regime. FP32 offers no recall advantage.

References:
- Skunkworks CG atom: `bytes_per_fact_pareto_v5_int8_pareto_optimal_M_40k_80k_3seed_HP_CG_2026-07-01`
- Pre-reg: `preregs/2026-07-01_substrate_bytes_per_fact_pareto_v5_int8_specialization.md`
"""
from __future__ import annotations

from typing import Tuple

import torch


def quantize_int8_dense(W: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
    """Per-row max-scale quantize float32 (N, N) -> int8 (N, N) + scale (N, 1).

    Returns (W_int8, scale_per_row). Recover with dequantize_int8_dense.

    Storage: 1 byte per weight + 4 bytes per row → 0.25x FP32 memory.
    """
    if W.dtype != torch.float32:
        W = W.to(torch.float32)
    row_max = W.abs().max(dim=1, keepdim=True).values.clamp_min(1e-9)
    scale = row_max / 127.0
    W_int8 = torch.round(W / scale).clamp_(-127, 127).to(torch.int8)
    return W_int8, scale


def dequantize_int8_dense(W_int8: torch.Tensor, scale: torch.Tensor) -> torch.Tensor:
    """Reconstruct float32 (N, N) from int8 (N, N) + per-row scale (N, 1)."""
    return W_int8.to(torch.float32) * scale


def hebbian_accumulate_int8(
    keys: torch.Tensor,
    vals: torch.Tensor,
    n_dim: int,
    batch_size: int = 2000,
) -> Tuple[torch.Tensor, torch.Tensor]:
    """Hebbian outer-product Sum(vals_i outer keys_i / n_dim), then int8 quantize.

    Args:
        keys: (n_items, n_dim) float32 keys
        vals: (n_items, n_dim) float32 values
        n_dim: dimensionality
        batch_size: batch dim for accumulation to bound memory

    Returns (W_int8, scale_per_row). Chain-grade for M ∈ [40k, 80k] at N=8192.
    """
    if keys.shape != vals.shape:
        raise ValueError(f"keys {keys.shape} != vals {vals.shape}")
    device = keys.device
    Wf = torch.zeros(n_dim, n_dim, dtype=torch.float32, device=device)
    for b in range(0, keys.shape[0], batch_size):
        Wf.add_((vals[b:b + batch_size].T @ keys[b:b + batch_size]) / n_dim)
    return quantize_int8_dense(Wf)


def bytes_per_fact_int8_dense(n_dim: int, n_facts: int) -> int:
    """Compute bytes/fact for INT8 dense workspace: W_int8 + scale + per-fact index."""
    return int((n_dim * n_dim + n_dim * 4) / max(n_facts, 1))


__all__ = [
    "quantize_int8_dense",
    "dequantize_int8_dense",
    "hebbian_accumulate_int8",
    "bytes_per_fact_int8_dense",
]
