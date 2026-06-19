"""
substrate.ghrr -- REC-4 implementation.

Generalized HRR (GHRR) block-diagonal binding for non-commutative composition.

Per Research WIKIDATA_INGEST_OPTIMIZATION REC-4:
  "GHRR block-diagonal binding (b=8 to b=64) for multi-hop.
   Non-commutative property preserves path order.
   No positional permute trick needed.
   Multi-hop chains compose cleanly.
   Aligns with substrate's PP-119 K-hop traversal."

Construction:
  Each FHRR vector v of dim N is reshaped into (N/b^2) blocks of (b x b) complex matrices.
  Binding A ⊗ B: blockwise matrix multiplication A[i] @ B[i] for each block i.

Why non-commutative:
  Matrix multiplication is non-commutative in general (AB != BA for generic 2x2+ matrices).
  This preserves order in multi-hop chains: knows ⊗ Alice ⊗ lives_in ⊗ Paris
  encodes a different vector than knows ⊗ lives_in ⊗ Alice ⊗ Paris.

Why associative:
  Matrix mult IS associative: (AB)C = A(BC). So multi-hop chains compose cleanly
  (i.e. unbinding from the right or left works without ambiguity).

Default block size b=2 (2x2 complex matrices per block; dim must be divisible by b^2=4).
"""
from __future__ import annotations
import math

import numpy as np

from substrate.core import DEFAULT_DIM


DEFAULT_BLOCK = 2  # b=2 -> 2x2 complex matrices per block


def _validate(v: np.ndarray, b: int) -> int:
    """Verify v is a valid GHRR vector at block size b. Returns the per-row dim."""
    if v.ndim == 1:
        dim = v.shape[0]
    elif v.ndim == 2:
        dim = v.shape[1]
    else:
        raise ValueError(f"v must be 1D or 2D; got shape {v.shape}")
    if dim % (b * b) != 0:
        raise ValueError(f"dim={dim} must be divisible by b*b={b * b}")
    return dim


def reshape_to_blocks(v: np.ndarray, b: int = DEFAULT_BLOCK) -> np.ndarray:
    """Reshape FHRR vector(s) to GHRR block form.

    Input shape: (dim,) or (N, dim)  with complex elements
    Output shape: (n_blocks, b, b) for 1D input, OR (N, n_blocks, b, b) for 2D.
    """
    dim = _validate(v, b)
    n_blocks = dim // (b * b)
    if v.ndim == 1:
        return v.reshape(n_blocks, b, b)
    return v.reshape(v.shape[0], n_blocks, b, b)


def flatten_from_blocks(blocks: np.ndarray) -> np.ndarray:
    """Inverse of reshape_to_blocks."""
    if blocks.ndim == 3:
        # (n_blocks, b, b)
        return blocks.reshape(-1)
    if blocks.ndim == 4:
        # (N, n_blocks, b, b)
        return blocks.reshape(blocks.shape[0], -1)
    raise ValueError(f"blocks must be 3D or 4D; got shape {blocks.shape}")


def ghrr_bind(a: np.ndarray, b_vec: np.ndarray, block_size: int = DEFAULT_BLOCK) -> np.ndarray:
    """GHRR BIND via blockwise matrix multiplication.

    a, b_vec: complex FHRR vectors of dim N. Result: complex vector of dim N.
    Non-commutative: ghrr_bind(a, b) != ghrr_bind(b, a) in general.
    Associative: ghrr_bind(ghrr_bind(a, b), c) == ghrr_bind(a, ghrr_bind(b, c)).
    """
    A = reshape_to_blocks(a, b=block_size)  # (n_blocks, b, b)
    B = reshape_to_blocks(b_vec, b=block_size)  # (n_blocks, b, b)
    # Matrix multiply per-block
    C = np.einsum("nij,njk->nik", A, B)
    return flatten_from_blocks(C).astype(a.dtype)


def ghrr_unbind_right(c: np.ndarray, b_vec: np.ndarray, block_size: int = DEFAULT_BLOCK) -> np.ndarray:
    """Right-unbind: given c = ghrr_bind(a, b), recover ~a using inverse of b.

    For unitary blocks (FHRR phasors typically yield blocks of small numeric magnitude),
    we approximate B^(-1) as conjugate-transpose (Hermitian adjoint), which is correct
    only for unitary blocks. For non-unitary blocks we use the explicit pseudoinverse.
    """
    C = reshape_to_blocks(c, b=block_size)
    B = reshape_to_blocks(b_vec, b=block_size)
    # B^(-1) ~ conj-transpose for unitary blocks
    # For numerical robustness: explicit inverse with damping
    B_inv = np.linalg.pinv(B)  # (n_blocks, b, b)
    A = np.einsum("nij,njk->nik", C, B_inv)
    return flatten_from_blocks(A).astype(c.dtype)


def ghrr_compose_chain(*vecs: np.ndarray, block_size: int = DEFAULT_BLOCK) -> np.ndarray:
    """Compose a multi-hop chain v1 ⊗ v2 ⊗ ... ⊗ vk via left-fold ghrr_bind.

    Useful for K-hop traversal: ghrr_compose_chain(rel_1, ent_2, rel_2, ent_3, ...).
    """
    if len(vecs) == 0:
        raise ValueError("need at least one vector")
    result = vecs[0]
    for v in vecs[1:]:
        result = ghrr_bind(result, v, block_size=block_size)
    return result


def ghrr_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity for GHRR-encoded vectors (same formula as FHRR; the
    structure difference is only in the bind operation, not the similarity metric)."""
    return float(np.real(np.vdot(b, a))) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9)


# ============================================================
# Self-test
# ============================================================

def _self_test():
    from substrate.core import cphasor

    dim = 8192
    b = DEFAULT_BLOCK
    rng = np.random.default_rng(7)
    A = cphasor(1, dim=dim, rng=rng)[0]
    B = cphasor(1, dim=dim, rng=rng)[0]
    C = cphasor(1, dim=dim, rng=rng)[0]

    # Bind
    AB = ghrr_bind(A, B, block_size=b)
    BA = ghrr_bind(B, A, block_size=b)

    # Non-commutativity: A⊗B != B⊗A
    cos_AB_BA = ghrr_similarity(AB, BA)
    assert abs(cos_AB_BA) < 0.5, f"AB and BA should differ; got cosine {cos_AB_BA}"

    # Associativity: (AB)C == A(BC)
    ABC_left = ghrr_bind(AB, C, block_size=b)
    BC = ghrr_bind(B, C, block_size=b)
    ABC_right = ghrr_bind(A, BC, block_size=b)
    cos_assoc = ghrr_similarity(ABC_left, ABC_right)
    assert cos_assoc > 0.99, f"GHRR should be associative; got cosine {cos_assoc}"

    # Right-unbind recovers A: ghrr_unbind_right(AB, B) ~ A
    A_recovered = ghrr_unbind_right(AB, B, block_size=b)
    cos_recovery = ghrr_similarity(A, A_recovered)
    assert cos_recovery > 0.9, f"unbind should recover A; got cosine {cos_recovery}"

    # K-hop chain composition
    chain = ghrr_compose_chain(A, B, C, block_size=b)
    chain_explicit = ghrr_bind(ghrr_bind(A, B, block_size=b), C, block_size=b)
    assert np.allclose(chain, chain_explicit), "chain compose should equal explicit left-fold"

    print(f"[substrate.ghrr] self-test PASS "
          f"(b={b}; non-commutative cos AB vs BA = {cos_AB_BA:+.3f}; "
          f"associative cos = {cos_assoc:.3f}; right-unbind recovery cos = {cos_recovery:.3f}; "
          f"K-hop chain ok)")


if __name__ == "__main__":
    _self_test()
