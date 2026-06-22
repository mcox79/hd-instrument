"""Substrate-native character-trigram bag-of-HD encoder — zero-external-model text→vector.

Pure-substrate text encoding via classical VSA/HDC text-encoding (Kanerva-style
bag-of-trigrams). For each input string, extract overlapping char-trigrams, look up
each trigram's bipolar HD vector in a deterministic per-trigram codebook (seeded
from trigram content via hash), and bundle (sum + sign) into a single HD vector.

No backprop, no transformer, no MiniLM. Pure substrate primitives:
  - Bipolar {-1, +1} HD vectors of dim n_dim
  - Hebbian/bundling sum-and-sign over trigram set
  - Cosine similarity for retrieval

Trade-offs vs MiniLM (honest scope):
  - PRO: zero external model dependency; runs on any platform; ~microseconds per text;
    deterministic; trivially reproducible; substrate-only-decode gate intact at ALL stages
    (not just retrieval — also at encode).
  - CON: loses deep semantic similarity. Will match exact-name + char-overlap paraphrases
    (cat/cats/kitten share no trigrams — would NOT match). Order-bag (no positional info).
  - SCOPE: an architectural demonstration that substrate CAN encode English without any
    external model. Not a full replacement for MiniLM's semantic quality — that requires
    the L2 substrate-native LM (g1 generation + char-LM closure post bigram-gap).

Used by tools/substrate_repl.py + dashboard chat as the "substrate-native" mode that
parallels the MiniLM "semantic" mode. User can compare the two.
"""

from __future__ import annotations

import hashlib
import time
from typing import Iterable

import numpy as np

from . import tracing


def _seed_for_trigram(trigram: str) -> int:
    """Deterministic 32-bit seed from trigram content (so the same trigram always maps to the same HD)."""
    h = hashlib.blake2b(trigram.encode("utf-8"), digest_size=4).digest()
    return int.from_bytes(h, "big")


def _bipolar_hv(seed: int, n_dim: int) -> np.ndarray:
    """Per-trigram bipolar {-1, +1} hypervector; deterministic from trigram seed."""
    rng = np.random.default_rng(seed)
    return (rng.integers(0, 2, size=n_dim) * 2 - 1).astype(np.float32)


class CharTrigramEncoder:
    """Substrate-native text→HD encoder via bag-of-char-trigrams.

    Each text is mapped to a single n_dim-dim bipolar HD vector by:
      1. Extracting overlapping char-trigrams (with start/end pad)
      2. Looking up each trigram's deterministic bipolar HD (cached)
      3. Summing (bundling) the per-trigram HDs
      4. Applying sign() to recover bipolar form

    Composes with hdlab.kg_traversal.KGStore (encode entity names with this instead of MiniLM)
    + hdlab.memory.Codebook (the encoded vector is the codebook key) + any substrate primitive
    that consumes HD vectors. Zero external model dependency.
    """

    def __init__(self, n_dim: int = 4096, pad_char: str = " ") -> None:
        self.n_dim = n_dim
        self.pad_char = pad_char
        self._cache: dict[str, np.ndarray] = {}
        self._n_unique_trigrams: int = 0

    def _trigrams(self, text: str) -> list[str]:
        """Generate overlapping char-trigrams with pad-char start/end markers."""
        t = self.pad_char + text.lower().replace("_", " ") + self.pad_char
        return [t[i:i + 3] for i in range(len(t) - 2)] if len(t) >= 3 else [t]

    def _hv_for_trigram(self, trigram: str) -> np.ndarray:
        cached = self._cache.get(trigram)
        if cached is not None:
            return cached
        hv = _bipolar_hv(_seed_for_trigram(trigram), self.n_dim)
        self._cache[trigram] = hv
        self._n_unique_trigrams = len(self._cache)
        return hv

    def encode(self, text: str) -> np.ndarray:
        """Encode a single text into a bipolar HD vector via bag-of-trigrams bundling."""
        t0 = time.perf_counter_ns()
        trigrams = self._trigrams(text)
        if not trigrams:
            return np.zeros(self.n_dim, dtype=np.float32)
        accum = np.zeros(self.n_dim, dtype=np.float32)
        for tri in trigrams:
            accum += self._hv_for_trigram(tri)
        # Sign-bundle: bipolar majority vote
        out = np.sign(accum).astype(np.float32)
        out[out == 0] = 1.0  # break ties deterministically
        tracing.emit(
            "char_trigram_encoder.encode",
            {"n_dim": self.n_dim, "n_trigrams": len(trigrams)},
            None,
            elapsed_ns=time.perf_counter_ns() - t0,
        )
        return out

    def encode_batch(self, texts: Iterable[str]) -> np.ndarray:
        """Encode a list/iterable of texts; returns [N, n_dim] array."""
        texts = list(texts)
        out = np.zeros((len(texts), self.n_dim), dtype=np.float32)
        for i, t in enumerate(texts):
            out[i] = self.encode(t)
        return out

    def nearest(self, query: str, codebook: np.ndarray, names: list[str], k: int = 5) -> list[dict]:
        """Find top-k nearest entries in `codebook` to `encode(query)` by cosine similarity.

        codebook: [N, n_dim] pre-encoded matrix; names: [N] entity names.
        Returns: list of {entity, cosine} dicts sorted desc.
        """
        q = self.encode(query)
        q_norm = q / (np.linalg.norm(q) + 1e-8)
        cb_norms = np.linalg.norm(codebook, axis=1, keepdims=True) + 1e-8
        cb_unit = codebook / cb_norms
        sims = cb_unit @ q_norm
        top_idx = np.argsort(sims)[-k:][::-1]
        return [{"entity": names[int(i)], "cosine": float(sims[int(i)])} for i in top_idx]

    def __len__(self) -> int:
        """# unique trigrams seen (cache size; grows monotonically)."""
        return self._n_unique_trigrams

    def __repr__(self) -> str:
        return f"CharTrigramEncoder(n_dim={self.n_dim}, n_unique_trigrams={self._n_unique_trigrams})"
