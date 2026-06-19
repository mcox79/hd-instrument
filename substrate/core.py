"""
substrate.core -- FHRR (Fourier Holographic Reduced Representation) primitives.

These are the foundational vector-symbolic operations shared by every PP-* primitive.
Extracted verbatim from the research cells (chain3-khop, kg-sharding, two-stage-disambig,
inverted-property-shards, etc.) into one reusable module.

Two codebook variants supported:
  - phasor:   complex64 unit-norm vectors via exp(i*theta); cphasor() / cidx_phasor()
  - bipolar:  +/-1 real vectors via sign(N(0,1)); bipolar() / cidx_bipolar()

Phasor is the primary choice (used by ~90% of cells). Bipolar is used by GDPR exact
erasure cell (because pinv downdate is well-conditioned on bipolar codebooks).

Operations:
  bind(a, b)        elementwise multiplication (vsa BIND); inverse of unbind
  unbind(a, b)      elementwise multiplication by conjugate of b
  bundle(*items)    elementwise sum (vsa BUNDLE); accumulator-style
  cidx(v, book)     cleanup memory: argmax cosine of v against codebook rows
  similarity(v, w)  cosine via real(<v, conj(w)>) for phasor; dot product for bipolar
"""
from __future__ import annotations
import math
import numpy as np
from typing import Optional, Union

DEFAULT_DIM = 8192
DEFAULT_RNG_SEED = 42


# ============================================================
# Phasor codebook (primary)
# ============================================================

def cphasor(n_items: int, dim: int = DEFAULT_DIM, rng: Optional[np.random.Generator] = None) -> np.ndarray:
    """Generate `n_items` FHRR phasor vectors of dimension `dim`.

    Each vector is complex64 with unit magnitude (phase uniformly random in [-pi, pi]).
    """
    rng = rng if rng is not None else np.random.default_rng(DEFAULT_RNG_SEED)
    ang = (rng.random((n_items, dim)) * 2 - 1) * math.pi
    return np.exp(1j * ang).astype(np.complex64)


def bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """VSA BIND: elementwise complex multiplication. a ⊛ b."""
    return a * b


def unbind(c: np.ndarray, b: np.ndarray) -> np.ndarray:
    """VSA UNBIND: multiply by conjugate to invert bind. c ⊛ b^(-1) approximates a."""
    return c * np.conj(b)


def bundle(*items: np.ndarray) -> np.ndarray:
    """VSA BUNDLE: superposition via elementwise sum. M = sum(items)."""
    if len(items) == 0:
        raise ValueError("bundle requires at least one item")
    result = items[0].copy()
    for item in items[1:]:
        result = result + item
    return result


def cidx(v: np.ndarray, book: np.ndarray) -> int:
    """Cleanup memory: index of codebook row with highest cosine to v.

    For phasor vectors, cosine ~ real(book @ conj(v)).
    """
    return int(np.argmax((book @ np.conj(v)).real))


def cidx_topk(v: np.ndarray, book: np.ndarray, k: int) -> np.ndarray:
    """Cleanup memory: top-k indices by cosine. Returns sorted ascending by index for stability."""
    scores = (book @ np.conj(v)).real
    return np.argsort(-scores)[:k]


def similarity(v: np.ndarray, w: np.ndarray) -> float:
    """Cosine similarity for phasor or bipolar vectors."""
    if np.iscomplexobj(v):
        return float(np.real(np.vdot(w, v))) / (np.linalg.norm(v) * np.linalg.norm(w) + 1e-9)
    return float(v @ w) / (np.linalg.norm(v) * np.linalg.norm(w) + 1e-9)


def normalize_phasor(v: np.ndarray) -> np.ndarray:
    """Project a complex vector onto the unit-magnitude phasor manifold (preserve phases only)."""
    return v / (np.abs(v) + 1e-9)


# ============================================================
# Bipolar codebook (for pinv-friendly variants like GDPR erase)
# ============================================================

def bipolar(n_items: int, dim: int = DEFAULT_DIM, rng: Optional[np.random.Generator] = None) -> np.ndarray:
    """Generate `n_items` bipolar {-1, +1} vectors of dimension `dim`."""
    rng = rng if rng is not None else np.random.default_rng(DEFAULT_RNG_SEED)
    return np.sign(rng.standard_normal((n_items, dim))).astype(np.float32)


def cidx_bipolar(v: np.ndarray, book: np.ndarray) -> int:
    """Cleanup memory for bipolar vectors via dot-product argmax."""
    return int(np.argmax(book @ v))


# ============================================================
# Codebook builder with persistence-friendly metadata
# ============================================================

class Codebook:
    """Named codebook (entities, relations, etc.) with deterministic rng seed.

    Allows the substrate to lazily extend the codebook when new entities/relations
    appear in writes, while keeping prior assignments stable.
    """

    def __init__(self, name: str, dim: int = DEFAULT_DIM, seed: int = DEFAULT_RNG_SEED, variant: str = "phasor"):
        self.name = name
        self.dim = dim
        self.seed = seed
        self.variant = variant  # "phasor" or "bipolar"
        self._items: dict[str, int] = {}  # name -> row index
        self._vectors: Optional[np.ndarray] = None  # filled lazily
        self._rng = np.random.default_rng(seed)

    def __len__(self) -> int:
        return len(self._items)

    def add(self, name: str) -> int:
        """Add a new entity/relation by name; idempotent. Returns the row index."""
        if name in self._items:
            return self._items[name]
        idx = len(self._items)
        self._items[name] = idx
        if self.variant == "phasor":
            ang = (self._rng.random(self.dim) * 2 - 1) * math.pi
            vec = np.exp(1j * ang).astype(np.complex64)[None, :]
        else:
            vec = np.sign(self._rng.standard_normal((1, self.dim))).astype(np.float32)
        if self._vectors is None:
            self._vectors = vec
        else:
            self._vectors = np.concatenate([self._vectors, vec], axis=0)
        return idx

    def get(self, name: str) -> np.ndarray:
        """Get the vector for an entity. Raises KeyError if absent."""
        return self._vectors[self._items[name]]

    def get_or_add(self, name: str) -> np.ndarray:
        idx = self.add(name)
        return self._vectors[idx]

    def names(self) -> list[str]:
        return list(self._items.keys())

    @property
    def vectors(self) -> np.ndarray:
        if self._vectors is None:
            empty_shape = (0, self.dim)
            return np.zeros(empty_shape, dtype=np.complex64 if self.variant == "phasor" else np.float32)
        return self._vectors

    def cleanup(self, v: np.ndarray) -> str:
        """Return the name of the codebook entry closest to v."""
        idx = cidx(v, self.vectors) if self.variant == "phasor" else cidx_bipolar(v, self.vectors)
        return self.names()[idx]

    def cleanup_idx(self, v: np.ndarray) -> int:
        if self.variant == "phasor":
            return cidx(v, self.vectors)
        return cidx_bipolar(v, self.vectors)


# ============================================================
# Self-test
# ============================================================

def _self_test():
    """Verify all primitives work on a small synthetic example."""
    rng = np.random.default_rng(0)

    # Phasor primitives
    book = cphasor(8, dim=256, rng=rng)
    assert book.shape == (8, 256)
    assert book.dtype == np.complex64
    assert cidx(book[3], book) == 3, "cleanup self-recognition"

    # Bind / unbind
    a, b = book[0], book[1]
    c = bind(a, b)
    recovered = unbind(c, b)
    assert similarity(recovered, a) > 0.99, "bind/unbind roundtrip"

    # Bundle + cleanup
    sup = bundle(book[2], book[5])
    top = cidx_topk(sup, book, 2)
    assert set(top.tolist()) == {2, 5}, "bundle cleanup"

    # Bipolar
    bb = bipolar(8, dim=256, rng=rng)
    assert bb.shape == (8, 256)
    assert bb.dtype == np.float32
    assert cidx_bipolar(bb[3], bb) == 3, "bipolar cleanup"

    # Codebook
    cb = Codebook("test_entities", dim=256)
    idx_a = cb.add("alice")
    idx_b = cb.add("bob")
    assert idx_a == 0 and idx_b == 1
    assert cb.add("alice") == idx_a, "idempotent add"
    assert cb.cleanup(cb.get("alice")) == "alice"

    print("[substrate.core] self-test PASS")


if __name__ == "__main__":
    _self_test()
