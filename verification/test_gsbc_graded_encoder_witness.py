"""Scaffold-free witness: GSBC graded-code encoder (density m) mechanism + registry.

Reproduces the certified DENSITY-DIAL retrieval gain from the arc
experiments/exp_encoder_gsbc_gradedcode_marginpush_v1* WITHOUT any training
scaffold or substrate state: on a clean synthetic dense codebook with planted
neighborhood structure, the graded top-m block code with the SHIP density m=5
recovers strictly more of the dense top-10 neighborhood than the coarser m=3
(which sits at/below the 0.30 ingest bar) and the near-sign m=1 (which collapses).
The density-lift discriminator FIRES: m5 > m3 > m1 every seed, and m5 clears the
0.30 bar where m3 does not robustly clear it.

Runs with tracing off (no active TraceBus). Uses passed-in numpy Generators.
Clean synthetic data only (no substrate KB state), per smoke/witness discipline.

ASCII-only. No emojis. No em dashes.
"""

from __future__ import annotations

import numpy as np

from hdlab.char_trigram_encoder import CharTrigramEncoder
from hdlab.gsbc_graded_encoder import (
    DEFAULT_BLK_L,
    DEFAULT_KB,
    DEFAULT_M,
    GsbcGradedEncoder,
    graded_block_code,
)
from hdlab.kb_encoder_registry import (
    CAPABILITIES,
    DEFAULT_ENCODER,
    resolve_kb_encoder,
)

N_DIM = DEFAULT_KB * DEFAULT_BLK_L  # 4096
_JITTER = 1.6                        # calibrated discriminating regime (documented)
_N_CLUSTERS = 60
_PER_CLUSTER = 14
_SEEDS = (7, 13, 19, 23, 29)
_INGEST_BAR = 0.30                   # the arc ingest bar the ship density must clear


def _codebook(gen: np.random.Generator) -> np.ndarray:
    """Synthetic dense codebook [N, N_DIM] with planted cluster neighborhoods."""
    centers = gen.standard_normal((_N_CLUSTERS, N_DIM)).astype(np.float32)
    X = np.repeat(centers, _PER_CLUSTER, axis=0)
    X = X + _JITTER * gen.standard_normal(X.shape).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def _top10(M: np.ndarray) -> np.ndarray:
    """Self-masked top-10 neighbor indices per row of [N, D] (by cosine/dot)."""
    S = M @ M.T
    np.fill_diagonal(S, -2.0)
    return np.argpartition(-S, 10, axis=1)[:, :10]


def _ret_agree10(dense: np.ndarray, codes: np.ndarray) -> float:
    """Mean top-10 overlap between dense-neighborhood and code-neighborhood."""
    cn = codes / (np.linalg.norm(codes, axis=1, keepdims=True) + 1e-8)
    td, tc = _top10(dense), _top10(cn)
    return float(np.mean([len(set(td[i]) & set(tc[i])) / 10.0
                          for i in range(dense.shape[0])]))


# ---------------------------------------------------------------------------
# Mechanism correctness (graded top-m block code: positive, unit-L1, m nonzeros).
# ---------------------------------------------------------------------------

def test_graded_block_code_shape_positive_unit_l1_and_sparsity():
    gen = np.random.default_rng(7)
    z = gen.standard_normal((32, N_DIM)).astype(np.float32)
    for m in (1, 3, 5, 8):
        code = graded_block_code(z, DEFAULT_KB, DEFAULT_BLK_L, m)
        assert code.shape == (32, N_DIM)
        assert np.all(code >= 0.0), f"m={m} graded survivors must be non-negative"
        blocks = code.reshape(32, DEFAULT_KB, DEFAULT_BLK_L)
        # exactly m nonzeros per block (ties are measure-zero for Gaussian input)
        nnz = (blocks > 0.0).sum(axis=-1)
        assert np.all(nnz == m), f"m={m}: per-block nnz {nnz.min()}..{nnz.max()} != {m}"
        # each block unit-L1
        l1 = blocks.sum(axis=-1)
        assert np.allclose(l1, 1.0, atol=1e-5), f"m={m}: block L1 not 1.0"


def test_encoder_default_is_ship_density_m5():
    enc = GsbcGradedEncoder(n_dim=N_DIM)
    assert enc.m == DEFAULT_M == 5
    assert enc.kb * enc.blk_l == enc.n_dim == N_DIM


# ---------------------------------------------------------------------------
# The density-dial retrieval-gain discriminator (the certified finding).
# ---------------------------------------------------------------------------

def test_m5_density_gain_over_m3_discriminator_fires():
    r1, r3, r5 = [], [], []
    for s in _SEEDS:
        X = _codebook(np.random.default_rng(s))
        c1 = GsbcGradedEncoder(n_dim=N_DIM, m=1).encode_dense_batch(X)
        c3 = GsbcGradedEncoder(n_dim=N_DIM, m=3).encode_dense_batch(X)
        c5 = GsbcGradedEncoder(n_dim=N_DIM, m=5).encode_dense_batch(X)
        a1, a3, a5 = _ret_agree10(X, c1), _ret_agree10(X, c3), _ret_agree10(X, c5)
        # density ordering holds every seed (denser graded code = higher fidelity)
        assert a5 > a3 > a1, f"seed {s}: ordering broke m5={a5:.3f} m3={a3:.3f} m1={a1:.3f}"
        # ship density m5 clears the 0.30 ingest bar every seed
        assert a5 > _INGEST_BAR, f"seed {s}: m5 ret_agree10 {a5:.3f} <= {_INGEST_BAR}"
        r1.append(a1); r3.append(a3); r5.append(a5)
    mean3, mean5 = float(np.mean(r3)), float(np.mean(r5))
    # coarse m3 sits at/below the bar (fails to robustly clear it); m5 is the ship
    assert mean3 <= 0.32, f"m3 mean {mean3:.3f} unexpectedly high (regime drift)"
    assert mean5 >= 0.38, f"m5 mean {mean5:.3f} below ship-density expectation"
    # discriminator margin: the density lift is substantial, not a knife-edge tie
    assert (mean5 - mean3) >= 0.08, f"density-lift gap {mean5 - mean3:.3f} too small"


# ---------------------------------------------------------------------------
# Registry: selectable-by-name, additive, no-regression, fail-loud text path.
# ---------------------------------------------------------------------------

def test_registry_default_is_char_trigram_no_regression():
    assert DEFAULT_ENCODER == "char_trigram_v1"
    for name in (None, "default", "char_trigram_v1"):
        enc = resolve_kb_encoder(name, N_DIM)
        assert isinstance(enc, CharTrigramEncoder)
        assert enc.n_dim == N_DIM


def test_registry_selects_gsbc_graded_m5():
    enc = resolve_kb_encoder("gsbc_graded_m5", N_DIM)
    assert isinstance(enc, GsbcGradedEncoder)
    assert enc.m == 5 and enc.n_dim == N_DIM
    assert CAPABILITIES["gsbc_graded_m5"]["requires_text_frontend"] is True
    assert CAPABILITIES["char_trigram_v1"]["requires_text_frontend"] is False


def test_registry_unknown_encoder_raises():
    import pytest
    with pytest.raises(ValueError):
        resolve_kb_encoder("no_such_encoder", N_DIM)


def test_gsbc_text_path_fail_loud_without_teacher():
    import pytest
    enc = resolve_kb_encoder("gsbc_graded_m5", N_DIM)
    with pytest.raises(RuntimeError):
        enc.encode("some concept name")


def test_gsbc_text_path_with_stub_teacher_roundtrips_to_graded_code():
    class _StubTeacher:
        """Minimal text->dense stand-in (deterministic hash embedding)."""
        def __init__(self, n_dim: int) -> None:
            self.n_dim = n_dim
        def encode(self, text: str) -> np.ndarray:
            g = np.random.default_rng(abs(hash(text)) % (2 ** 32))
            return g.standard_normal(self.n_dim).astype(np.float32)

    enc = GsbcGradedEncoder(n_dim=N_DIM, m=5, teacher=_StubTeacher(N_DIM))
    code = enc.encode("mitochondrion")
    assert code.shape == (N_DIM,)
    blocks = code.reshape(DEFAULT_KB, DEFAULT_BLK_L)
    assert np.all(code >= 0.0)
    assert np.allclose(blocks.sum(axis=-1), 1.0, atol=1e-5)
    assert np.all((blocks > 0.0).sum(axis=-1) == 5)
