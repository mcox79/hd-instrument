"""Chunked M x N attention for large-M substrate scales.

Peak memory ~= chunk_size * N * dtype (not M * N).
Enables M=1M at N=8192 on 8GB VRAM by chunking over the M (keys/vals) axis.

Numerical strategy: online log-sum-exp (FlashAttention-style two-pass fused into
one streaming pass). Per chunk we track:
    m: running max of logits (Q,)
    l: running softmax denominator (Q,)
    o: running unnormalized numerator (Q, V)

When a new chunk contributes logits s (Q, chunk) and vals v (chunk, V):
    m_new = max(m, s.max(-1))
    scale = exp(m - m_new)
    l = l * scale + exp(s - m_new).sum(-1)
    o = o * scale + exp(s - m_new) @ v
Final readout = o / l.

Standard use:
    from hdlab.chunked_attention import chunked_attention_readout
    query_readout = chunked_attention_readout(query, keys, vals, chunk_size=1024, beta=13)

Dtype paths:
    - FP32 keys/vals -> FP32 accumulator (default)
    - FP16 keys/vals -> FP32 accumulator (accumulator promoted internally)
    - INT8 keys + per-row scale -> FP32 dequant (composes with hdlab.int8_dense)
"""
from __future__ import annotations

from typing import Optional, Tuple

import torch


def _cosine_similarity_chunk(
    query_normed: torch.Tensor,
    keys_chunk: torch.Tensor,
) -> torch.Tensor:
    """Cosine similarity between L2-normalized query and a raw keys chunk.

    Args:
        query_normed: (Q, N) L2-normalized queries (float32).
        keys_chunk: (chunk, N) keys (float32; caller handles dtype cast).

    Returns:
        (Q, chunk) cosine similarities in float32.
    """
    keys_norm = keys_chunk / keys_chunk.norm(dim=-1, keepdim=True).clamp_min(1e-9)
    return query_normed @ keys_norm.T


def chunked_attention_readout(
    query: torch.Tensor,
    keys: torch.Tensor,
    vals: torch.Tensor,
    chunk_size: int = 1024,
    beta: float = 13.0,
    key_scale: Optional[torch.Tensor] = None,
) -> torch.Tensor:
    """Dense-Hopfield READ-REPLACE style attention, chunked over the M axis.

    Numerically equivalent to:
        sims = cos_sim(query, keys)     # (Q, M)
        weights = softmax(beta * sims)  # (Q, M)
        readout = weights @ vals        # (Q, V)
    but with peak memory O(Q * chunk_size + chunk_size * N + Q * V) instead of
    O(Q * M).

    Args:
        query: (Q, N) tensor. Queries at dim N.
        keys: (M, N) tensor. Keys at dim N. Large M.
            Supported dtypes: float32, float16, int8.
        vals: (M, V) tensor. Value vectors at dim V. Cast to float32 accumulator.
        chunk_size: int. Rows of M to process per chunk.
            Peak mem for the sims block ~= Q * chunk_size * float32.
        beta: float. Softmax sharpness (Cell D v2 CG regime ~= 13).
        key_scale: Optional[(M, 1)] tensor. Per-row dequant scale for INT8 keys.
            Required when keys.dtype == torch.int8. See hdlab.int8_dense.

    Returns:
        readout: (Q, V) tensor in float32. Attention-weighted vals.

    Raises:
        ValueError: shape/dtype mismatch or missing key_scale for int8 keys.
    """
    if query.ndim != 2 or keys.ndim != 2 or vals.ndim != 2:
        raise ValueError(
            f"expected 2D tensors; got query {query.shape}, keys {keys.shape}, "
            f"vals {vals.shape}"
        )
    if keys.shape[0] != vals.shape[0]:
        raise ValueError(
            f"keys and vals must share M axis; got keys M={keys.shape[0]}, "
            f"vals M={vals.shape[0]}"
        )
    if keys.shape[1] != query.shape[1]:
        raise ValueError(
            f"keys N ({keys.shape[1]}) != query N ({query.shape[1]})"
        )
    if keys.dtype == torch.int8 and key_scale is None:
        raise ValueError("int8 keys require key_scale (M, 1) for dequant")
    if chunk_size <= 0:
        raise ValueError(f"chunk_size must be positive; got {chunk_size}")

    device = query.device
    Q, N = query.shape
    M = keys.shape[0]
    V = vals.shape[1]

    # Promote query to float32 accumulator and L2-normalize once (outside the loop).
    q32 = query.to(torch.float32)
    q_normed = q32 / q32.norm(dim=-1, keepdim=True).clamp_min(1e-9)

    # Online log-sum-exp state.
    m_state = torch.full((Q,), float("-inf"), device=device, dtype=torch.float32)
    l_state = torch.zeros((Q,), device=device, dtype=torch.float32)
    o_state = torch.zeros((Q, V), device=device, dtype=torch.float32)

    for start in range(0, M, chunk_size):
        end = min(start + chunk_size, M)
        k_chunk_raw = keys[start:end]

        # Dtype path: dequant to float32 for cosine.
        if k_chunk_raw.dtype == torch.int8:
            scale_chunk = key_scale[start:end]
            k_chunk = k_chunk_raw.to(torch.float32) * scale_chunk
        elif k_chunk_raw.dtype == torch.float16:
            k_chunk = k_chunk_raw.to(torch.float32)
        else:
            k_chunk = k_chunk_raw.to(torch.float32)

        v_chunk = vals[start:end].to(torch.float32)

        # Cosine similarities for this chunk: (Q, chunk).
        sims_chunk = _cosine_similarity_chunk(q_normed, k_chunk)
        logits_chunk = beta * sims_chunk  # (Q, chunk)

        # Online softmax update.
        chunk_max = logits_chunk.max(dim=-1).values  # (Q,)
        m_new = torch.maximum(m_state, chunk_max)  # (Q,)
        # Rescale existing state.
        scale = torch.exp(m_state - m_new)  # (Q,)
        # exp(logits - m_new): (Q, chunk)
        exp_logits = torch.exp(logits_chunk - m_new.unsqueeze(-1))

        l_state = l_state * scale + exp_logits.sum(dim=-1)
        o_state = o_state * scale.unsqueeze(-1) + exp_logits @ v_chunk
        m_state = m_new

        # Free the biggest transient block for the next iteration.
        del k_chunk, v_chunk, sims_chunk, logits_chunk, exp_logits

    readout = o_state / l_state.unsqueeze(-1).clamp_min(1e-30)
    return readout


def reference_attention_readout(
    query: torch.Tensor,
    keys: torch.Tensor,
    vals: torch.Tensor,
    beta: float = 13.0,
    key_scale: Optional[torch.Tensor] = None,
) -> torch.Tensor:
    """Non-chunked reference for verification. NOT for production; O(Q*M) memory.

    Args mirror chunked_attention_readout. Returns (Q, V) float32.
    """
    if keys.dtype == torch.int8:
        if key_scale is None:
            raise ValueError("int8 keys require key_scale for reference impl")
        k = keys.to(torch.float32) * key_scale
    else:
        k = keys.to(torch.float32)
    v = vals.to(torch.float32)
    q32 = query.to(torch.float32)
    q_normed = q32 / q32.norm(dim=-1, keepdim=True).clamp_min(1e-9)
    k_normed = k / k.norm(dim=-1, keepdim=True).clamp_min(1e-9)
    sims = q_normed @ k_normed.T  # (Q, M)
    logits = beta * sims
    weights = torch.softmax(logits, dim=-1)
    return weights @ v


def estimate_peak_memory_bytes(
    Q: int,
    N: int,
    V: int,
    chunk_size: int,
    key_dtype_bytes: int = 4,
    val_dtype_bytes: int = 4,
    accum_dtype_bytes: int = 4,
) -> int:
    """Analytical peak memory (bytes) for the chunked pass, excluding query/state.

    Dominant transient blocks per step:
        k_chunk: chunk_size * N * accum_dtype_bytes
        v_chunk: chunk_size * V * accum_dtype_bytes
        sims_chunk / logits_chunk / exp_logits: 3 * Q * chunk_size * 4
    Plus persistent:
        o_state: Q * V * 4
        l_state, m_state: 2 * Q * 4

    NOT counted: input keys/vals (caller owns those); this bound is what the
    chunked pass ADDS on top of the storage.
    """
    del key_dtype_bytes, val_dtype_bytes  # transient bufs use accum dtype
    per_chunk = chunk_size * N * accum_dtype_bytes  # k_chunk
    per_chunk += chunk_size * V * accum_dtype_bytes  # v_chunk
    per_chunk += 3 * Q * chunk_size * 4  # sims + logits + exp_logits
    persistent = Q * V * 4 + 2 * Q * 4
    return per_chunk + persistent


__all__ = [
    "chunked_attention_readout",
    "reference_attention_readout",
    "estimate_peak_memory_bytes",
]
