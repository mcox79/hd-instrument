"""Bipolar encoder for ICL demonstrations and queries.

Mirrors the encoder used by `testbed.curriculum.policies.SubstrateCurriculumPolicy`:

  1. Build a hashed character-bigram count vector v of length hash_dim=4096.
  2. Apply a FIXED Rademacher random projection R (hash_dim -> N), seeded by
     proj_seed.
  3. xi = sign(R^T v)  in  {-1, +1}^N.

This encoder is deterministic given (text, N, proj_seed).  R is cached by
proj_seed so repeated `encode_text_bipolar` calls do not re-allocate.

ASCII-only per feedback_ascii_only_in_scripts.
"""
from __future__ import annotations

from typing import Dict, Tuple

import numpy as np


_HASH_DIM = 4096  # bigram-hash bucket count (must match curriculum-policy default)

# proj cache: (hash_dim, N, proj_seed) -> R(hash_dim, N) Rademacher matrix
_PROJ_CACHE: Dict[Tuple[int, int, int], np.ndarray] = {}


def _get_projection(N: int, proj_seed: int, hash_dim: int = _HASH_DIM) -> np.ndarray:
    """Fetch (or build & cache) the fixed Rademacher projection R."""
    key = (int(hash_dim), int(N), int(proj_seed))
    R = _PROJ_CACHE.get(key)
    if R is None:
        rng = np.random.default_rng(int(proj_seed))
        R = rng.choice([-1, 1], size=(hash_dim, N)).astype(np.float32)
        _PROJ_CACHE[key] = R
    return R


def encode_text_bipolar(text: str, N: int, proj_seed: int = 1729,
                        hash_dim: int = _HASH_DIM) -> np.ndarray:
    """Encode `text` to bipolar (N,) float32 in {-1, +1}.

    Args:
        text:      Input string.
        N:         Output dimensionality.
        proj_seed: Seed for the fixed Rademacher projection matrix.
        hash_dim:  Bigram-hash bucket count (default 4096).
    """
    R = _get_projection(N, proj_seed, hash_dim=hash_dim)
    v = np.zeros(hash_dim, dtype=np.float32)
    if not isinstance(text, str):
        text = str(text)
    if len(text) >= 2:
        b = text.encode("utf-8", errors="replace")
        for i in range(len(b) - 1):
            bucket = (b[i] * 256 + b[i + 1]) % hash_dim
            v[bucket] += 1.0
    elif len(text) == 1:
        b0 = ord(text[0]) & 0xFF
        v[(b0 * 256 + b0) % hash_dim] += 1.0
    # else len(text)==0 -> zero vector -> sign(0)=+1 everywhere (matches default)
    z = v @ R   # (N,)
    xi = np.where(z >= 0.0, 1.0, -1.0).astype(np.float32)
    return xi


def encode_pair_bipolar(input_text: str, output_text: str, N: int,
                        proj_seed: int = 1729, sep: str = " -> ") -> np.ndarray:
    """Encode an (input, output) demonstration pair as a single bipolar vector.

    Concatenates as `input_text + sep + output_text` and encodes via
    encode_text_bipolar.  This is what we write into the substrate W: each
    demo's (in, out) becomes one bipolar pattern, and the query encodes only
    the input -- so cos(W xi_in, xi_in) implicitly retrieves the joint state.
    """
    return encode_text_bipolar(input_text + sep + output_text, N=N, proj_seed=proj_seed)


# -----------------------------------------------------------------------------
# Self-test
# -----------------------------------------------------------------------------
def _selftest() -> None:
    """PROT-022: determinism, shape, bipolarity, projection caching."""
    print("[selftest] testbed.icl.encoder")

    # T1: shape + dtype + bipolarity
    xi = encode_text_bipolar("hello world", N=1024, proj_seed=1729)
    assert xi.shape == (1024,), f"shape: {xi.shape}"
    assert xi.dtype == np.float32, f"dtype: {xi.dtype}"
    uniq = set(xi.tolist())
    assert uniq.issubset({-1.0, 1.0}), f"non-bipolar: {uniq}"
    print(f"  T1 PASS: shape={xi.shape}, dtype={xi.dtype}, bipolar")

    # T2: determinism (same text, same seed -> identical)
    xi2 = encode_text_bipolar("hello world", N=1024, proj_seed=1729)
    assert np.array_equal(xi, xi2), "non-deterministic encoding"
    print("  T2 PASS: deterministic re-encode")

    # T3: different text -> different encoding (high prob)
    xi3 = encode_text_bipolar("goodbye world", N=1024, proj_seed=1729)
    overlap = float(np.mean(xi == xi3))
    assert overlap < 0.9, f"different texts too similar: overlap={overlap}"
    print(f"  T3 PASS: different texts diverge (overlap={overlap:.3f})")

    # T4: different proj_seed -> different encoding (high prob)
    xi4 = encode_text_bipolar("hello world", N=1024, proj_seed=4242)
    overlap2 = float(np.mean(xi == xi4))
    assert overlap2 < 0.9, f"diff proj_seed gave same enc: {overlap2}"
    print(f"  T4 PASS: different proj_seed diverges (overlap={overlap2:.3f})")

    # T5: encode_pair_bipolar combines input + output
    xi_pair_a = encode_pair_bipolar("king", "queen", N=1024, proj_seed=1729)
    xi_pair_b = encode_pair_bipolar("king", "duke", N=1024, proj_seed=1729)
    assert not np.array_equal(xi_pair_a, xi_pair_b), "pair encoding ignored output"
    print("  T5 PASS: pair encoding sensitive to output text")

    # T6: empty string handled gracefully
    xi_empty = encode_text_bipolar("", N=64, proj_seed=1729)
    assert xi_empty.shape == (64,) and set(xi_empty.tolist()).issubset({-1.0, 1.0})
    print("  T6 PASS: empty string -> bipolar (degenerate but well-formed)")

    # T7: projection caching (cache hit returns same object)
    _ = encode_text_bipolar("foo", N=1024, proj_seed=999)
    R1 = _get_projection(1024, 999)
    R2 = _get_projection(1024, 999)
    assert R1 is R2, "projection cache returned different objects"
    print("  T7 PASS: projection caching active")

    print("[selftest] testbed.icl.encoder ALL PASS")


_selftest()


if __name__ == "__main__":
    _selftest()
