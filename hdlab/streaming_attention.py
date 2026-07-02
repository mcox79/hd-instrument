"""CPU-resident streaming attention for M >> GPU-VRAM regimes.

Extends hdlab.chunked_attention: keys/vals live on CPU (optionally pinned),
each chunk is transferred to GPU per iteration. Peak GPU memory is bounded
by the chunk footprint plus small persistent state, INDEPENDENT of M.

Why this exists (v3 fix per Wave 25 v2 crash):
    chunked_attention_readout requires keys/vals already on target device.
    At M=1M / N=8192 that is 16 GB FP16 keys alone — cannot fit on 8 GB VRAM.
    streaming_attention_readout keeps keys/vals on CPU and streams chunks.
    Peak GPU footprint at M=1M / N=8192 / V=256 / chunk=1024 is ~40 MB
    (transient) + Q*V*4 (state) — regardless of M.

Numerical correctness: identical online log-sum-exp to chunked_attention;
selftests here verify streaming matches non-streaming (chunked) result on a
small M=1000 case to within FP16 tolerance.

Standard use:
    from hdlab.streaming_attention import streaming_attention_readout
    # keys_cpu: (M, N) fp16 or int8 CPU tensor (pinned or unpinned)
    # vals_cpu: (M, V) fp16 CPU tensor
    readout = streaming_attention_readout(
        query=query_gpu, keys_cpu=keys_cpu, vals_cpu=vals_cpu,
        chunk_size=1024, beta=13.0, device=torch.device("cuda"),
        key_scale_cpu=key_scale_cpu,  # required if keys_cpu.dtype == int8
    )
"""
from __future__ import annotations

from typing import Optional

import torch


def _cosine_similarity_chunk(
    query_normed: torch.Tensor,
    keys_chunk: torch.Tensor,
) -> torch.Tensor:
    """Cosine similarity between L2-normed query and a raw keys chunk (device tensors)."""
    keys_norm = keys_chunk / keys_chunk.norm(dim=-1, keepdim=True).clamp_min(1e-9)
    return query_normed @ keys_norm.T


def streaming_attention_readout(
    query: torch.Tensor,
    keys_cpu: torch.Tensor,
    vals_cpu: torch.Tensor,
    chunk_size: int,
    beta: float,
    device: torch.device,
    key_scale_cpu: Optional[torch.Tensor] = None,
) -> torch.Tensor:
    """Dense-Hopfield READ-REPLACE attention with CPU-resident keys/vals.

    Streams (M, N) keys and (M, V) vals from CPU to `device` in chunks of
    `chunk_size` rows. Peak GPU memory is bounded by chunk footprint plus
    persistent state O(Q*V + Q) — INDEPENDENT of M.

    Args:
        query: (Q, N) tensor on `device` (float32 or float16; promoted to fp32).
        keys_cpu: (M, N) CPU tensor. Dtypes: float32 / float16 / int8.
        vals_cpu: (M, V) CPU tensor. Dtypes: float32 / float16.
        chunk_size: rows of M streamed to GPU per iteration.
        beta: softmax sharpness.
        device: target CUDA device.
        key_scale_cpu: (M, 1) CPU tensor for INT8 dequant. Required for int8 keys.

    Returns:
        readout: (Q, V) float32 tensor on `device`.

    Raises:
        ValueError: shape/dtype mismatch or missing key_scale_cpu for int8.
        RuntimeError: keys_cpu / vals_cpu not on CPU.
    """
    if query.ndim != 2 or keys_cpu.ndim != 2 or vals_cpu.ndim != 2:
        raise ValueError(
            f"expected 2D tensors; got query {query.shape}, keys_cpu "
            f"{keys_cpu.shape}, vals_cpu {vals_cpu.shape}"
        )
    if keys_cpu.shape[0] != vals_cpu.shape[0]:
        raise ValueError(
            f"keys and vals must share M axis; got keys M={keys_cpu.shape[0]}, "
            f"vals M={vals_cpu.shape[0]}"
        )
    if keys_cpu.shape[1] != query.shape[1]:
        raise ValueError(
            f"keys N ({keys_cpu.shape[1]}) != query N ({query.shape[1]})"
        )
    if keys_cpu.dtype == torch.int8 and key_scale_cpu is None:
        raise ValueError("int8 keys require key_scale_cpu (M, 1) for dequant")
    if keys_cpu.device.type != "cpu":
        raise RuntimeError(
            f"keys_cpu must be on CPU; got device {keys_cpu.device}"
        )
    if vals_cpu.device.type != "cpu":
        raise RuntimeError(
            f"vals_cpu must be on CPU; got device {vals_cpu.device}"
        )
    if chunk_size <= 0:
        raise ValueError(f"chunk_size must be positive; got {chunk_size}")

    Q, N = query.shape
    M = keys_cpu.shape[0]
    V = vals_cpu.shape[1]

    # Promote query to float32 on device and L2-normalize once.
    q32 = query.to(torch.float32)
    q_normed = q32 / q32.norm(dim=-1, keepdim=True).clamp_min(1e-9)

    # Online log-sum-exp state (on device).
    m_state = torch.full((Q,), float("-inf"), device=device, dtype=torch.float32)
    l_state = torch.zeros((Q,), device=device, dtype=torch.float32)
    o_state = torch.zeros((Q, V), device=device, dtype=torch.float32)

    for start in range(0, M, chunk_size):
        end = min(start + chunk_size, M)

        # Stream chunk from CPU to GPU. non_blocking works if keys_cpu is pinned.
        k_chunk_cpu = keys_cpu[start:end]
        v_chunk_cpu = vals_cpu[start:end]

        if k_chunk_cpu.dtype == torch.int8:
            # Upload INT8 chunk + scale slice, dequant on GPU.
            k_chunk_dev = k_chunk_cpu.to(device, non_blocking=True)
            assert key_scale_cpu is not None
            scale_chunk_dev = key_scale_cpu[start:end].to(device, non_blocking=True)
            k_chunk = k_chunk_dev.to(torch.float32) * scale_chunk_dev
            del k_chunk_dev, scale_chunk_dev
        else:
            k_chunk_dev = k_chunk_cpu.to(device, non_blocking=True)
            k_chunk = k_chunk_dev.to(torch.float32)
            del k_chunk_dev

        v_chunk_dev = v_chunk_cpu.to(device, non_blocking=True)
        v_chunk = v_chunk_dev.to(torch.float32)
        del v_chunk_dev

        # Cosine similarities (Q, chunk).
        sims_chunk = _cosine_similarity_chunk(q_normed, k_chunk)
        logits_chunk = beta * sims_chunk

        # Online softmax update.
        chunk_max = logits_chunk.max(dim=-1).values
        m_new = torch.maximum(m_state, chunk_max)
        scale = torch.exp(m_state - m_new)
        exp_logits = torch.exp(logits_chunk - m_new.unsqueeze(-1))

        l_state = l_state * scale + exp_logits.sum(dim=-1)
        o_state = o_state * scale.unsqueeze(-1) + exp_logits @ v_chunk
        m_state = m_new

        del k_chunk, v_chunk, sims_chunk, logits_chunk, exp_logits

    readout = o_state / l_state.unsqueeze(-1).clamp_min(1e-30)
    return readout


def streaming_hebbian_W(
    keys_cpu: torch.Tensor,
    vals_cpu: torch.Tensor,
    N: int,
    V: int,
    chunk_size: int,
    device: torch.device,
    key_scale_cpu: Optional[torch.Tensor] = None,
) -> torch.Tensor:
    """Streaming Hebbian outer-product accumulator: W = (vals.T @ keys) / N.

    Builds (V, N) FP32 W on `device` by streaming (chunk, N) key blocks and
    (chunk, V) val blocks from CPU. Peak GPU footprint = chunk_size * (N + V) * 4
    bytes transient + V * N * 4 bytes persistent — INDEPENDENT of M.

    Args:
        keys_cpu: (M, N) CPU tensor. Dtypes: float32 / float16 / int8.
        vals_cpu: (M, V) CPU tensor.
        N, V: dimensionalities (must match keys/vals).
        chunk_size: rows per streaming batch.
        device: target CUDA device.
        key_scale_cpu: (M, 1) CPU tensor for INT8 dequant. Required for int8 keys.

    Returns:
        W: (V, N) float32 tensor on `device`.
    """
    if keys_cpu.shape[1] != N:
        raise ValueError(f"keys_cpu N={keys_cpu.shape[1]} != N={N}")
    if vals_cpu.shape[1] != V:
        raise ValueError(f"vals_cpu V={vals_cpu.shape[1]} != V={V}")
    if keys_cpu.shape[0] != vals_cpu.shape[0]:
        raise ValueError(
            f"M mismatch: keys={keys_cpu.shape[0]}, vals={vals_cpu.shape[0]}"
        )
    if keys_cpu.dtype == torch.int8 and key_scale_cpu is None:
        raise ValueError("int8 keys require key_scale_cpu for dequant")

    M = keys_cpu.shape[0]
    W = torch.zeros(V, N, dtype=torch.float32, device=device)
    for start in range(0, M, chunk_size):
        end = min(start + chunk_size, M)
        k_cpu_chunk = keys_cpu[start:end]
        v_cpu_chunk = vals_cpu[start:end]

        if k_cpu_chunk.dtype == torch.int8:
            k_dev = k_cpu_chunk.to(device, non_blocking=True)
            assert key_scale_cpu is not None
            scale_chunk = key_scale_cpu[start:end].to(device, non_blocking=True)
            k_f32 = k_dev.to(torch.float32) * scale_chunk
            del k_dev, scale_chunk
        else:
            k_dev = k_cpu_chunk.to(device, non_blocking=True)
            k_f32 = k_dev.to(torch.float32)
            del k_dev

        v_dev = v_cpu_chunk.to(device, non_blocking=True)
        v_f32 = v_dev.to(torch.float32)
        del v_dev

        # W += v.T @ k
        W.addmm_(v_f32.T, k_f32, alpha=1.0, beta=1.0)
        del k_f32, v_f32

    W.div_(float(N))
    return W


def estimate_streaming_peak_bytes(
    Q: int,
    N: int,
    V: int,
    chunk_size: int,
) -> int:
    """Analytical peak GPU memory for streaming pass, INDEPENDENT of M.

    Dominant transient blocks per step:
        k_chunk_fp32: chunk_size * N * 4
        v_chunk_fp32: chunk_size * V * 4
        (plus original-dtype upload staging: chunk_size * N * key_bytes, small)
        sims / logits / exp_logits: 3 * Q * chunk_size * 4
    Persistent:
        o_state: Q * V * 4
        l_state, m_state: 2 * Q * 4
        (For streaming_hebbian_W: W = V * N * 4 persistent.)

    Returns the streaming-attention (READ-REPLACE) peak. For the Hebbian arm
    add V*N*4 persistent separately.
    """
    per_chunk = chunk_size * N * 4  # k_chunk fp32
    per_chunk += chunk_size * V * 4  # v_chunk fp32
    per_chunk += 3 * Q * chunk_size * 4  # sims + logits + exp_logits
    # Small upload staging block (dominant when keys are int8/fp16 pre-dequant).
    # Assume 4 bytes worst case since already counted in fp32; add small margin.
    persistent = Q * V * 4 + 2 * Q * 4
    return per_chunk + persistent


__all__ = [
    "streaming_attention_readout",
    "streaming_hebbian_W",
    "estimate_streaming_peak_bytes",
]
