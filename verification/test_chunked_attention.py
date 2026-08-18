"""Chunked attention verification (numerical equivalence + peak-memory bound).

Motivation: M3 commercial deployment needs M=100k-1M memory items. Chunked
attention lets the substrate exercise commercial-M frontier scales on an 8GB
VRAM device by chunking over the M axis (peak_mem = chunk * N * dtype, not M*N).

Would-have-caught: if a future refactor breaks the online log-sum-exp
accumulation (e.g., forgets to rescale l_state/o_state when m_state updates),
T1/T3/T4 fail immediately; the bug regime is silent divergence from reference.

Tests:
    T1: chunked FP32 matches non-chunked reference for M=1024, N=1024
        (1e-4 relative).
    T2: analytical peak memory at M=100000, chunk=1024, N=8192 stays under
        200 MB; if CUDA is available, also verify empirically via
        torch.cuda.max_memory_allocated.
    T3: chunked FP16-keys + FP32-accum matches FP32 reference to 1e-3.
    T4: chunked INT8-keys + FP32-dequant matches FP32 reference to 1e-2
        (composes with hdlab.int8_dense).
"""
from __future__ import annotations

import gc

import pytest
import torch

from hdlab.chunked_attention import (
    chunked_attention_readout,
    estimate_peak_memory_bytes,
    reference_attention_readout,
)
from hdlab.int8_dense import quantize_int8_dense


def _make_case(M: int, N: int, V: int, Q: int, seed: int = 0):
    """Reproducible (query, keys, vals) triple with unit-scale gaussian entries."""
    g = torch.Generator().manual_seed(seed)
    query = torch.randn(Q, N, generator=g)
    keys = torch.randn(M, N, generator=g)
    vals = torch.randn(M, V, generator=g)
    return query, keys, vals


def _relative_error(a: torch.Tensor, b: torch.Tensor) -> float:
    return float((a - b).norm() / b.norm().clamp_min(1e-12))


def test_t1_chunked_matches_reference_fp32() -> None:
    """Chunked FP32 vs non-chunked reference, M=1024, N=1024, tol 1e-4."""
    M, N, V, Q = 1024, 1024, 64, 4
    query, keys, vals = _make_case(M, N, V, Q, seed=0)
    beta = 13.0
    ref = reference_attention_readout(query, keys, vals, beta=beta)
    for chunk_size in (128, 256, 1024):
        got = chunked_attention_readout(
            query, keys, vals, chunk_size=chunk_size, beta=beta
        )
        err = _relative_error(got, ref)
        assert err < 1e-4, (
            f"chunk_size={chunk_size}: relative err {err:.3e} exceeds 1e-4"
        )


def test_t2_peak_memory_bound() -> None:
    """Analytical (+ optional empirical CUDA) peak-mem bound at M=100000,
    chunk=1024, N=8192 under 200 MB.

    The bound is on the memory the chunked pass ADDS on top of input storage
    (matches the design contract: peak scales with chunk_size * N, not M * N).
    """
    M, N, V, Q = 100_000, 8192, 64, 1
    chunk = 1024
    analytical = estimate_peak_memory_bytes(Q=Q, N=N, V=V, chunk_size=chunk)
    assert analytical < 200 * 1024 * 1024, (
        f"analytical peak {analytical / 1024 / 1024:.1f} MB exceeds 200 MB"
    )

    # Empirical check: only when a CUDA device is present. Skip cleanly otherwise.
    if not torch.cuda.is_available():
        pytest.skip("CUDA unavailable; analytical bound already asserted")

    device = torch.device("cuda")
    # Build inputs on-device with FP16 keys (realistic 100k scale) and small V.
    g = torch.Generator(device=device).manual_seed(0)
    query = torch.randn(Q, N, generator=g, device=device)
    keys = torch.randn(M, N, generator=g, device=device).to(torch.float16)
    vals = torch.randn(M, V, generator=g, device=device)
    input_bytes = (
        query.element_size() * query.nelement()
        + keys.element_size() * keys.nelement()
        + vals.element_size() * vals.nelement()
    )

    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats(device)
    baseline = torch.cuda.memory_allocated(device)
    _ = chunked_attention_readout(query, keys, vals, chunk_size=chunk, beta=13.0)
    peak = torch.cuda.max_memory_allocated(device)
    added = peak - baseline
    # The chunked-pass overhead (excluding inputs already resident) must stay
    # well under 200 MB. Give 2x analytical headroom for PyTorch allocator
    # bookkeeping.
    limit = 200 * 1024 * 1024
    assert added < limit, (
        f"empirical added peak {added / 1024 / 1024:.1f} MB exceeds "
        f"{limit / 1024 / 1024:.1f} MB (input storage {input_bytes / 1024 / 1024:.1f} MB, "
        f"analytical {analytical / 1024 / 1024:.1f} MB)"
    )


def test_t3_fp16_keys_fp32_accum() -> None:
    """FP16 keys + FP32 accumulator matches FP32 reference to 1e-3."""
    M, N, V, Q = 2048, 512, 32, 4
    query, keys, vals = _make_case(M, N, V, Q, seed=1)
    beta = 13.0
    ref = reference_attention_readout(query, keys, vals, beta=beta)
    keys_fp16 = keys.to(torch.float16)
    got = chunked_attention_readout(
        query, keys_fp16, vals, chunk_size=256, beta=beta
    )
    err = _relative_error(got, ref)
    assert err < 1e-3, f"FP16-keys relative err {err:.3e} exceeds 1e-3"


def test_t4_int8_keys_fp32_dequant() -> None:
    """INT8 keys + FP32 dequant matches FP32 reference to 1e-2.

    Uses hdlab.int8_dense.quantize_int8_dense for the per-row scale contract.
    Verifies the compose path (chunked_attention over INT8 storage).
    """
    M, N, V, Q = 2048, 512, 32, 4
    query, keys, vals = _make_case(M, N, V, Q, seed=2)
    beta = 13.0
    ref = reference_attention_readout(query, keys, vals, beta=beta)
    keys_int8, key_scale = quantize_int8_dense(keys)
    got = chunked_attention_readout(
        query,
        keys_int8,
        vals,
        chunk_size=256,
        beta=beta,
        key_scale=key_scale,
    )
    err = _relative_error(got, ref)
    assert err < 1e-2, f"INT8-keys relative err {err:.3e} exceeds 1e-2"


def test_t5_error_paths() -> None:
    """Shape / dtype guards trigger ValueError."""
    query, keys, vals = _make_case(64, 32, 8, 2, seed=3)
    # Missing key_scale for int8 keys.
    keys_int8, _ = quantize_int8_dense(keys)
    with pytest.raises(ValueError, match="int8 keys require key_scale"):
        chunked_attention_readout(query, keys_int8, vals, chunk_size=16, beta=13.0)
    # Mismatched M.
    with pytest.raises(ValueError, match="keys and vals must share M axis"):
        chunked_attention_readout(query, keys, vals[:32], chunk_size=16, beta=13.0)
    # Mismatched N.
    with pytest.raises(ValueError, match=r"keys N .* != query N"):
        chunked_attention_readout(query, keys[:, :16], vals, chunk_size=16, beta=13.0)
    # Bad chunk_size.
    with pytest.raises(ValueError, match="chunk_size must be positive"):
        chunked_attention_readout(query, keys, vals, chunk_size=0, beta=13.0)


if __name__ == "__main__":
    test_t1_chunked_matches_reference_fp32()
    try:
        test_t2_peak_memory_bound()
        t2_note = "T2 peak-mem bound"
    except pytest.skip.Exception as e:  # type: ignore[attr-defined]
        t2_note = f"T2 peak-mem bound (empirical SKIPPED: {e}; analytical OK)"
    test_t3_fp16_keys_fp32_accum()
    test_t4_int8_keys_fp32_dequant()
    test_t5_error_paths()
    gc.collect()
    print(
        "[verification/test_chunked_attention] PASS: "
        f"T1 chunked==ref FP32 + {t2_note} + T3 FP16-keys + "
        "T4 INT8-keys + T5 error paths"
    )
