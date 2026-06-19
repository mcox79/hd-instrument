"""Tests for experiments/_bit_precision.py helper.

Coverage:
- fp32 no-op (byte-exact)
- fp16 roundtrip max-abs-error < 1e-3 on random tensors
- int8 roundtrip max-abs-error < 1e-2 on random tensors
- int4/int2 sane bounded error
- int1 sign-preservation
- numpy backend basic
- precision_metadata bytes math
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
import pytest
import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "experiments"))

import _bit_precision as bp  # noqa: E402


def _rng_tensor(shape=(256, 256), seed=17):
    """Random tensor normalized to roughly [-1, 1] (substrate-W-like scale)."""
    g = torch.Generator().manual_seed(seed)
    raw = torch.randn(*shape, generator=g, dtype=torch.float32)
    # Normalize so max-abs is ~1.0, matching post-normalization W scale.
    return raw / raw.abs().max()


def test_fp32_is_noop_byte_exact():
    x = _rng_tensor()
    q, scale = bp.quantize(x, "fp32")
    assert scale == 1.0
    assert q is x  # no copy
    rt = bp.quantize_roundtrip(x, "fp32")
    assert rt is x
    assert torch.equal(rt, x)


def test_fp16_roundtrip_low_error():
    x = _rng_tensor()
    rt = bp.quantize_roundtrip(x, "fp16")
    err = (rt - x).abs().max().item()
    assert err < 1e-3, f"fp16 roundtrip max-abs-error too large: {err}"
    assert rt.dtype == torch.float32  # dequantized back to original dtype


def test_int8_roundtrip_bounded_error():
    x = _rng_tensor()
    rt = bp.quantize_roundtrip(x, "int8")
    err = (rt - x).abs().max().item()
    assert err < 1e-2, f"int8 roundtrip max-abs-error too large: {err}"


def test_int4_roundtrip_bounded_error():
    x = _rng_tensor()
    rt = bp.quantize_roundtrip(x, "int4")
    err = (rt - x).abs().max().item()
    # int4 has only 15 levels; expected error scale is ~max_abs/7 ~= 0.7
    max_abs = x.abs().max().item()
    assert err < max_abs, f"int4 roundtrip exceeded max_abs: err={err} max_abs={max_abs}"


def test_int2_roundtrip_bounded_error():
    x = _rng_tensor()
    rt = bp.quantize_roundtrip(x, "int2")
    err = (rt - x).abs().max().item()
    max_abs = x.abs().max().item()
    assert err <= max_abs + 1e-6, (
        f"int2 roundtrip exceeded max_abs: err={err} max_abs={max_abs}"
    )


def test_int1_sign_preservation():
    x = _rng_tensor()
    # Filter out exact zeros (extremely unlikely for randn but be safe).
    nz_mask = x != 0
    rt = bp.quantize_roundtrip(x, "int1")
    # Signs must match wherever x is non-zero.
    sign_x = torch.sign(x[nz_mask])
    sign_rt = torch.sign(rt[nz_mask])
    assert torch.equal(sign_x, sign_rt), "int1 must preserve sign"
    # All non-zero values should have identical magnitude (uniform scale).
    rt_nz = rt[nz_mask].abs()
    if rt_nz.numel() > 0:
        assert (rt_nz.max() - rt_nz.min()).item() < 1e-5, (
            "int1 magnitudes must be uniform"
        )


def test_numpy_backend_fp16_and_int8():
    rng = np.random.default_rng(17)
    raw = rng.standard_normal((128, 128)).astype(np.float32)
    x = raw / np.abs(raw).max()  # normalize to roughly [-1, 1]
    rt16 = bp.quantize_roundtrip(x, "fp16")
    err16 = np.abs(rt16 - x).max()
    assert err16 < 1e-3, f"numpy fp16 roundtrip max-abs-error too large: {err16}"
    rt8 = bp.quantize_roundtrip(x, "int8")
    err8 = np.abs(rt8 - x).max()
    assert err8 < 1e-2, f"numpy int8 roundtrip max-abs-error too large: {err8}"


def test_numpy_int1_sign():
    rng = np.random.default_rng(23)
    x = rng.standard_normal(1024).astype(np.float32)
    rt = bp.quantize_roundtrip(x, "int1")
    nz = x != 0
    assert np.array_equal(np.sign(x[nz]), np.sign(rt[nz]))


def test_precision_metadata_bytes():
    md = bp.precision_metadata(numel=8192 * 8192, precision="int4")
    assert md["precision_used"] == "int4"
    assert md["precision_baseline_bytes"] == 8192 * 8192 * 4
    assert md["precision_memory_bytes"] == int(round(8192 * 8192 * 0.5))
    assert md["precision_compression_ratio"] == 8.0
    assert md["precision_numel_W"] == 8192 * 8192


def test_precision_metadata_int1_is_32x_smaller_than_fp32():
    md = bp.precision_metadata(numel=4096 * 4096, precision="int1")
    # 32 bits -> 1 bit = 32x compression
    assert md["precision_compression_ratio"] == 32.0


def test_invalid_precision_raises():
    with pytest.raises(ValueError):
        bp.quantize(_rng_tensor(), "fp64")


def test_all_zero_tensor_safe():
    x = torch.zeros(64, 64, dtype=torch.float32)
    for p in ("fp32", "fp16", "int8", "int4", "int2", "int1"):
        rt = bp.quantize_roundtrip(x, p)
        assert rt.abs().max().item() < 1e-6, f"zero tensor not preserved at {p}"
