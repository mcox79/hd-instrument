"""
substrate.qcode_fhrr -- REC-1 implementation.

Deterministic mapping from Wikidata Q-codes / P-codes -> FHRR phasor vectors of dimension
N (default 8192). Each code seeds a separate numpy RNG via SHA-256, ensuring:
  - Reproducibility: same Q-code -> same vector across runs / processes / machines
  - No precomputation: only compute vectors for codes actually encountered (lazy)
  - O(1) lookup: in-memory dict cache after first generation

Per Research WIKIDATA_INGEST_OPTIMIZATION REC-1:
  "Each Q-code/P-code -> random unit-modulus complex FHRR vector at N=8192.
   FROZEN; sampled once at ingest. Mapping: QID_str -> complex128 FHRR vector.
   Labels resolved LAZILY at query time from separate cache."

Storage characteristic:
  ~16 KB per vector (8192 complex64 = 16 bytes per element).
  For 50M Q-codes: 800 GB at full precision; with REC-5 1-bit quantization, ~50 GB.
  In practice we cache vectors on-demand so memory is bounded by codes actually
  encountered in a session, not the full 50M corpus.

Usage:
    from substrate.qcode_fhrr import QCodeMapper

    mapper = QCodeMapper(dim=8192)
    v42 = mapper.get("Q42")        # FHRR vector for Douglas Adams
    p31 = mapper.get("P31")        # FHRR vector for "instance of"
    bound = bind(v42, p31)         # subject (x) predicate
"""
from __future__ import annotations
import hashlib
import math
import threading
from pathlib import Path
from typing import Optional

import numpy as np

from substrate.core import DEFAULT_DIM


# ============================================================
# Deterministic seed derivation
# ============================================================

def code_to_seed(code: str) -> int:
    """SHA-256(code) -> 64-bit integer seed for numpy.random.default_rng().

    Deterministic + collision-resistant. The same Q-code always yields the same seed.
    """
    h = hashlib.sha256(code.encode("utf-8")).digest()
    return int.from_bytes(h[:8], byteorder="big", signed=False)


def code_to_fhrr(code: str, dim: int = DEFAULT_DIM) -> np.ndarray:
    """Generate the FHRR phasor vector for `code` (Q-code or P-code).

    Deterministic: same code -> same vector. Unit-magnitude complex64.
    """
    seed = code_to_seed(code)
    rng = np.random.default_rng(seed)
    ang = (rng.random(dim) * 2 - 1) * math.pi
    return np.exp(1j * ang).astype(np.complex64)


# ============================================================
# QCodeMapper - cached lazy generator with optional disk persistence
# ============================================================

class QCodeMapper:
    """Cached Q-code -> FHRR vector mapper.

    Vectors are generated on first request and cached in memory. Optional disk
    persistence via np.savez_compressed for cross-session reuse.
    """

    def __init__(self, dim: int = DEFAULT_DIM, persist_path: Optional[Path] = None):
        self.dim = dim
        self.persist_path = persist_path
        self._cache: dict = {}
        self._lock = threading.Lock()
        if persist_path and persist_path.exists():
            self._load_from_disk()

    def get(self, code: str) -> np.ndarray:
        """Return the FHRR vector for `code`, generating + caching on first call."""
        with self._lock:
            v = self._cache.get(code)
            if v is None:
                v = code_to_fhrr(code, dim=self.dim)
                self._cache[code] = v
            return v

    def get_batch(self, codes: list) -> np.ndarray:
        """Generate / fetch vectors for a list of codes. Returns shape (len(codes), dim).

        Efficient for downstream batched operations (binding many subjects with one predicate).
        """
        vecs = np.empty((len(codes), self.dim), dtype=np.complex64)
        for i, c in enumerate(codes):
            vecs[i] = self.get(c)
        return vecs

    def __len__(self) -> int:
        return len(self._cache)

    def codes(self) -> list:
        with self._lock:
            return list(self._cache.keys())

    def save_to_disk(self, path: Optional[Path] = None) -> Path:
        """Persist current cache to disk as compressed npz."""
        path = path or self.persist_path
        if path is None:
            raise ValueError("no persist_path configured")
        path.parent.mkdir(parents=True, exist_ok=True)
        with self._lock:
            codes_arr = np.array(list(self._cache.keys()), dtype=object)
            vecs_arr = np.stack(list(self._cache.values()))
        np.savez_compressed(path, codes=codes_arr, vecs=vecs_arr)
        return path

    def _load_from_disk(self) -> None:
        data = np.load(self.persist_path, allow_pickle=True)
        codes = data["codes"]
        vecs = data["vecs"]
        with self._lock:
            for c, v in zip(codes, vecs):
                self._cache[str(c)] = v.astype(np.complex64)


# ============================================================
# Self-test
# ============================================================

def _self_test():
    """Verify determinism + properties of REC-1 FHRR Q-code vectors."""
    # Determinism: same code -> same vector
    v1 = code_to_fhrr("Q42")
    v2 = code_to_fhrr("Q42")
    assert np.array_equal(v1, v2), "code_to_fhrr not deterministic"

    # Distinctness: different codes -> different vectors
    v_q42 = code_to_fhrr("Q42")
    v_q43 = code_to_fhrr("Q43")
    cosine = float(np.real(np.vdot(v_q42, v_q43))) / (np.linalg.norm(v_q42) * np.linalg.norm(v_q43))
    assert abs(cosine) < 0.05, f"different codes should have ~0 cosine; got {cosine}"

    # Unit magnitude check (within float32 precision)
    mags = np.abs(v_q42)
    assert np.allclose(mags, 1.0, atol=1e-3), f"phasor magnitudes should be ~1; range [{mags.min()}, {mags.max()}]"

    # Mapper cache + batch
    mapper = QCodeMapper(dim=8192)
    assert len(mapper) == 0
    _ = mapper.get("Q42")
    assert len(mapper) == 1
    _ = mapper.get("Q42")  # cache hit; no growth
    assert len(mapper) == 1
    batch = mapper.get_batch(["P31", "P106", "P21"])
    assert batch.shape == (3, 8192)
    assert len(mapper) == 4  # Q42 + P31 + P106 + P21

    # Disk persistence
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        persist = Path(td) / "qcode_cache.npz"
        mapper.save_to_disk(persist)
        assert persist.exists()
        mapper2 = QCodeMapper(dim=8192, persist_path=persist)
        assert len(mapper2) == 4
        assert np.array_equal(mapper.get("Q42"), mapper2.get("Q42"))

    print(f"[substrate.qcode_fhrr] self-test PASS (dim=8192; deterministic; ~0 cosine between codes; "
          f"unit-magnitude phasors; cache + disk persist verified)")


if __name__ == "__main__":
    _self_test()
