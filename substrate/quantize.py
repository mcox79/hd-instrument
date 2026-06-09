"""
substrate.quantize -- REC-5 implementation.

1-bit quantization of FHRR phasor vectors after bundle normalization.

Per Research WIKIDATA_INGEST_OPTIMIZATION REC-5:
  "1-bit quantization (PP-200 pattern) after bundle normalization.
   <2% retrieval accuracy loss at N>=4096 (per literature).
   16x memory savings vs float32. Compounds with REC-1 (Q-codes as atomic) for
   total storage compression."

Strategy:
  Each complex64 element (8 bytes) -> 2-bit sign-of-real + sign-of-imaginary
  = 4 elements per byte = 16x memory reduction.

  Stored as packed uint8 arrays.

  Reconstruction back to phasor is approximate:
    bit 0 (sign real)  -> real ~ +/- 1/sqrt(2)
    bit 1 (sign imag)  -> imag ~ +/- 1/sqrt(2)

  This preserves the angular quadrant of each phasor (loses sub-quadrant precision
  but maintains rotational symmetry of FHRR binding).
"""
from __future__ import annotations
import numpy as np


def quantize_1bit(vecs: np.ndarray) -> np.ndarray:
    """Quantize complex phasor vectors to 1-bit sign per real/imag component.

    Input shape: (N, dim) complex64 (unit-magnitude phasors expected).
    Output shape: (N, dim_packed) uint8 where dim_packed = ceil(dim*2 / 8) = dim/4.

    Each output byte packs the (sign_real, sign_imag) of 4 consecutive elements:
      byte = (real0 >= 0) << 7 | (imag0 >= 0) << 6 | (real1 >= 0) << 5 | ...
    """
    if vecs.ndim == 1:
        vecs = vecs[None, :]
    n, dim = vecs.shape
    if dim % 4 != 0:
        raise ValueError(f"dim must be a multiple of 4; got {dim}")

    # Stack sign bits: real positive -> 1, real negative -> 0
    sign_r = (vecs.real >= 0).astype(np.uint8)
    sign_i = (vecs.imag >= 0).astype(np.uint8)

    # Interleave: [r0, i0, r1, i1, ...] per row
    interleaved = np.empty((n, dim * 2), dtype=np.uint8)
    interleaved[:, 0::2] = sign_r
    interleaved[:, 1::2] = sign_i

    # Pack into bytes - 8 bits per byte, MSB first
    packed = np.packbits(interleaved, axis=1, bitorder="big")
    return packed


def dequantize_1bit(packed: np.ndarray, dim: int) -> np.ndarray:
    """Reconstruct complex64 phasors from 1-bit-per-real/imag packed bytes.

    Input shape: (N, dim/4) uint8
    Output shape: (N, dim) complex64 with elements in {+/-1/sqrt(2) +/- 1/sqrt(2)*i}.
    """
    if packed.ndim == 1:
        packed = packed[None, :]
    n = packed.shape[0]
    if dim % 4 != 0:
        raise ValueError(f"dim must be a multiple of 4; got {dim}")

    interleaved = np.unpackbits(packed, axis=1, bitorder="big")[:, : dim * 2]
    sign_r = interleaved[:, 0::2].astype(np.float32) * 2 - 1   # 0->-1, 1->+1
    sign_i = interleaved[:, 1::2].astype(np.float32) * 2 - 1
    scale = 1.0 / np.sqrt(2.0)
    return (sign_r * scale + 1j * sign_i * scale).astype(np.complex64)


def storage_bytes(vecs: np.ndarray, quantized: bool = False) -> int:
    """Return the storage size in bytes for these vectors."""
    if quantized:
        if vecs.dtype != np.uint8:
            raise ValueError("quantized arrays must be uint8")
        return vecs.size
    return vecs.size * vecs.itemsize


def compression_ratio(original: np.ndarray, packed: np.ndarray) -> float:
    """How much smaller the packed array is vs the original."""
    return storage_bytes(original) / storage_bytes(packed, quantized=True)


def cosine_recovery(original: np.ndarray, packed: np.ndarray, dim: int) -> float:
    """Average cosine between each original vector and its dequantized reconstruction."""
    reconstructed = dequantize_1bit(packed, dim)
    cosines = []
    for orig, recon in zip(original, reconstructed):
        c = float(np.real(np.vdot(orig, recon))) / (np.linalg.norm(orig) * np.linalg.norm(recon) + 1e-9)
        cosines.append(c)
    return float(np.mean(cosines))


# ============================================================
# Self-test
# ============================================================

def _self_test():
    from substrate.core import cphasor

    dim = 8192
    n = 100
    rng = np.random.default_rng(42)
    vecs = cphasor(n, dim=dim, rng=rng)
    assert vecs.shape == (n, dim)
    assert vecs.dtype == np.complex64

    # Quantize
    packed = quantize_1bit(vecs)
    assert packed.dtype == np.uint8
    assert packed.shape == (n, dim // 4), packed.shape

    # Compression ratio: complex64 = 8 bytes/element -> uint8 = 1 byte per 4 elements -> 32x
    ratio = compression_ratio(vecs, packed)
    assert ratio == 32.0, f"expected 32x compression got {ratio}x"

    # Reconstruction is approximate but should preserve quadrant
    avg_cos = cosine_recovery(vecs, packed, dim=dim)
    # 1-bit quant of uniformly distributed phasors should give ~2/pi ~ 0.637 expected cosine
    # (E[sign(X)*X] / 1 for X = exp(i*theta))
    # Empirically lit reports ~0.6-0.7 for FHRR; we check it's well above random
    assert avg_cos > 0.5, f"reconstruction cosine should be > 0.5; got {avg_cos}"

    # Determinism
    packed2 = quantize_1bit(vecs)
    assert np.array_equal(packed, packed2), "quantize_1bit should be deterministic"

    # Memory check
    orig_bytes = storage_bytes(vecs)
    packed_bytes = storage_bytes(packed, quantized=True)
    print(f"[substrate.quantize] self-test PASS "
          f"({n} vecs at dim={dim}: {orig_bytes / 1024:.0f} KB -> {packed_bytes / 1024:.0f} KB "
          f"({ratio:.0f}x compression); avg cosine recovery {avg_cos:.3f}; "
          f"angular-quadrant preserved)")


if __name__ == "__main__":
    _self_test()
