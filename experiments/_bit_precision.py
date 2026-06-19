"""Bit-precision quantization helper for substrate W matrices.

Supported precisions:
  fp32   -- 32-bit float (default; trivial no-op cast for backwards compat)
  fp16   -- 16-bit float (trivial dtype cast)
  int8   -- 8-bit signed integer (symmetric per-tensor quantization)
  int4   -- 4-bit signed integer (symmetric per-tensor quantization)
  int2   -- 2-bit signed integer (symmetric per-tensor quantization)
  int1   -- 1-bit (binary; sign only)

INT1 is binary: stored as the sign of each element. Magnitude is uniform
(scale = max-abs). All quantizers are symmetric per-tensor: scale = max(abs(x))
mapped to int_max for the precision.

Returns are dequantized tensors in the original (or requested) float dtype,
so downstream code is dtype-agnostic. The point is to simulate the precision
loss the substrate would incur at deployment without touching dtypes downstream.

Memory accounting (per element):
  fp32 = 4 bytes, fp16 = 2 bytes, int8 = 1 byte,
  int4 = 0.5 bytes, int2 = 0.25 bytes, int1 = 0.125 bytes.
"""
from __future__ import annotations

from typing import Tuple, Union

VALID_PRECISIONS = ("fp32", "fp16", "int8", "int4", "int2", "int1")

# Bits-per-element for each precision (float arithmetic OK; used for byte math).
BITS_PER_ELEM = {
    "fp32": 32.0,
    "fp16": 16.0,
    "int8": 8.0,
    "int4": 4.0,
    "int2": 2.0,
    "int1": 1.0,
}


def precision_bytes_per_elem(precision: str) -> float:
    """Return bytes per element for the given precision label."""
    if precision not in BITS_PER_ELEM:
        raise ValueError(f"Unknown precision: {precision}")
    return BITS_PER_ELEM[precision] / 8.0


def tensor_memory_bytes(numel: int, precision: str) -> int:
    """Total bytes needed to hold `numel` elements at `precision`."""
    return int(round(numel * precision_bytes_per_elem(precision)))


def _int_range_for(precision: str) -> int:
    """Symmetric int range half-width (e.g. int8 -> 127)."""
    if precision == "int8":
        return 127
    if precision == "int4":
        return 7
    if precision == "int2":
        return 1
    if precision == "int1":
        return 1
    raise ValueError(f"Not an integer precision: {precision}")


def _detect_backend(x):
    """Detect whether tensor x is torch or numpy."""
    cls_module = type(x).__module__
    if cls_module.startswith("torch"):
        return "torch"
    if cls_module.startswith("numpy"):
        return "numpy"
    raise TypeError(f"Unsupported tensor backend: {cls_module}")


def quantize(x, precision: str) -> Tuple:
    """Quantize tensor x to the requested precision. Returns (quantized, scale).

    For fp32/fp16: scale=1.0, quantized is a dtype-cast view.
    For intN: symmetric per-tensor quantization; quantized is integer-rounded
    values in float container; scale is max(abs(x)) / int_max.

    Backwards compat: fp32 returns x unchanged (no copy, scale=1.0).
    """
    if precision not in VALID_PRECISIONS:
        raise ValueError(f"precision must be one of {VALID_PRECISIONS}; got {precision}")

    backend = _detect_backend(x)

    if precision == "fp32":
        # No-op: keep dtype identical for byte-exact backward compat.
        return x, 1.0

    if backend == "torch":
        import torch
        if precision == "fp16":
            return x.to(torch.float16), 1.0
        # Integer precisions: symmetric per-tensor quantization.
        int_max = _int_range_for(precision)
        max_abs = float(x.abs().max().item())
        if max_abs == 0.0:
            scale = 1.0
            q = torch.zeros_like(x)
            return q, scale
        scale = max_abs / int_max
        q = torch.round(x / scale).clamp(-int_max, int_max)
        if precision == "int1":
            q = torch.sign(x)
        return q, scale

    if backend == "numpy":
        import numpy as np
        if precision == "fp16":
            return x.astype(np.float16), 1.0
        int_max = _int_range_for(precision)
        max_abs = float(np.abs(x).max())
        if max_abs == 0.0:
            scale = 1.0
            q = np.zeros_like(x)
            return q, scale
        scale = max_abs / int_max
        q = np.clip(np.round(x / scale), -int_max, int_max)
        if precision == "int1":
            q = np.sign(x)
        return q, scale

    raise TypeError(f"Unsupported backend: {backend}")


def dequantize(q, scale: float, dtype=None):
    """Dequantize q back to a float tensor in the requested dtype.

    For fp32 (scale=1.0 and q is already fp32): returns q unchanged.
    For fp16: cast back to dtype (default float32).
    For intN: multiply by scale and cast to dtype.
    """
    backend = _detect_backend(q)

    if backend == "torch":
        import torch
        target = dtype if dtype is not None else torch.float32
        out = q.to(target)
        if scale != 1.0:
            out = out * scale
        return out

    if backend == "numpy":
        import numpy as np
        target = dtype if dtype is not None else np.float32
        out = q.astype(target)
        if scale != 1.0:
            out = out * scale
        return out

    raise TypeError(f"Unsupported backend: {backend}")


def quantize_roundtrip(x, precision: str):
    """Convenience: quantize then dequantize. Returns float tensor in original dtype.

    For fp32: returns x unchanged (no-op, byte-exact).
    For other precisions: returns dequantized tensor with precision loss baked in.
    Use this to simulate substrate-at-INTN behavior while keeping downstream code
    dtype-agnostic.
    """
    if precision == "fp32":
        return x
    backend = _detect_backend(x)
    if backend == "torch":
        original_dtype = x.dtype
    else:
        original_dtype = x.dtype
    q, scale = quantize(x, precision)
    return dequantize(q, scale, dtype=original_dtype)


def precision_metadata(numel: int, precision: str) -> dict:
    """Build the metrics-json subdict for precision accounting."""
    baseline = tensor_memory_bytes(numel, "fp32")
    used = tensor_memory_bytes(numel, precision)
    ratio = baseline / max(1, used)
    return {
        "precision_used": precision,
        "precision_memory_bytes": used,
        "precision_baseline_bytes": baseline,
        "precision_compression_ratio": round(ratio, 4),
        "precision_numel_W": numel,
    }
