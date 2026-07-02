"""Substrate-native character + positional HD encoder (Kanerva-style; V1 analog).

INPUT REGIME DOCSTRING BLOCK:
    Input: raw text (unicode string; ASCII in current use).
    Output: bipolar {-1, +1} HD vector of dimension n_dim.
    Regime type: SURFACE FEATURES ONLY. This encoder produces vectors that
    reflect the CHARACTER SEQUENCE of the input, bound to POSITION via HRR
    circular convolution. It does NOT know semantic identity of any word.
    Brain analog: V1 / primary sensory cortex. The role of this encoder in
    the substrate is to be the deterministic sensory front-end that
    downstream mechanisms (predictive coding, competitive allocation,
    Hebbian association) can learn to map onto concept representations.

Design:
  - Each ASCII character c gets a deterministic bipolar HD vector via hash.
  - Each position i (0 .. max_pos-1) gets a deterministic position HD vector
    via hash of "POS_<i>".
  - encode_word(w):  bundle_sign( bind(char_hd[c_i], pos_hd[i])  for i in w )
    where bind is HRR circular convolution (FFT-based; not elementwise mul).
    Bundle = sign-of-sum (sparse ties broken to +1).
  - encode_sentence(sentence): bag-of-word-HDs (order-invariant within
    sentence; order preserved within word).

Rationale for position-binding via HRR:
  - Bag-of-words alone loses order (kitten vs kittne indistinguishable).
  - HRR bind(char, pos) makes the char-position pair a single roll-hashed HD.
  - Position vectors carry roll structure that survives sum-bundle.
  - Cross-word position-key REUSE is intentional (position 0 is same across
    words) — that's fine because the downstream predictive-coding layer
    learns which position-features co-occur with which characters.

Pure substrate primitives; NO backprop; NO borrowed embeddings; NO tokenizer.
ASCII-only in code + comments. NumPy; no torch dependency (matches associative-
memory and predictive_coding modules).
"""

from __future__ import annotations

import hashlib
from typing import Iterable

import numpy as np


# ---------------------------------------------------------------------------
# Deterministic bipolar-HD generation
# ---------------------------------------------------------------------------

def _seed_for_token(token: str) -> int:
    """32-bit deterministic seed from token string."""
    h = hashlib.blake2b(token.encode("utf-8"), digest_size=4).digest()
    return int.from_bytes(h, "big")


def _bipolar_hv(seed: int, n_dim: int) -> np.ndarray:
    """Deterministic bipolar {-1, +1} HD from seed."""
    rng = np.random.default_rng(seed)
    return (rng.integers(0, 2, size=n_dim) * 2 - 1).astype(np.float32)


# ---------------------------------------------------------------------------
# HRR bind / bundle helpers (NumPy; matches hdlab.binding math for float dtype)
# ---------------------------------------------------------------------------

def _hrr_bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """HRR bind = circular convolution via FFT. Real output.

    Returns same-dtype (float32) output. Result is NOT bipolar; sign step is
    applied only at final bundle.
    """
    fa = np.fft.fft(a)
    fb = np.fft.fft(b)
    return np.real(np.fft.ifft(fa * fb)).astype(a.dtype)


def _sign_bundle(vs: np.ndarray) -> np.ndarray:
    """Sign-bundle sum(vs); ties broken to +1."""
    s = np.sum(vs, axis=0) if vs.ndim > 1 else vs
    out = np.sign(s).astype(np.float32)
    out[out == 0] = 1.0
    return out


# ---------------------------------------------------------------------------
# CharPositionalEncoder
# ---------------------------------------------------------------------------

class CharPositionalEncoder:
    """Character + positional HD encoder producing bipolar sentence HDs.

    Deterministic given (n_dim, seed_char_prefix, seed_pos_prefix). Cached
    per-char and per-position HDs for reuse across the corpus.
    """

    def __init__(
        self,
        n_dim: int = 4096,
        max_pos: int = 32,
        seed_prefix: str = "SPOKE1",
    ) -> None:
        if n_dim <= 0:
            raise ValueError(f"n_dim must be positive; got {n_dim}")
        if max_pos <= 0:
            raise ValueError(f"max_pos must be positive; got {max_pos}")
        self.n_dim = int(n_dim)
        self.max_pos = int(max_pos)
        self.seed_prefix = seed_prefix
        self._char_cache: dict[str, np.ndarray] = {}
        self._pos_cache: dict[int, np.ndarray] = {}

    def _char_hd(self, c: str) -> np.ndarray:
        if c in self._char_cache:
            return self._char_cache[c]
        hd = _bipolar_hv(
            _seed_for_token(f"{self.seed_prefix}_CHAR_{c}"), self.n_dim
        )
        self._char_cache[c] = hd
        return hd

    def _pos_hd(self, i: int) -> np.ndarray:
        if i in self._pos_cache:
            return self._pos_cache[i]
        hd = _bipolar_hv(
            _seed_for_token(f"{self.seed_prefix}_POS_{i}"), self.n_dim
        )
        self._pos_cache[i] = hd
        return hd

    def encode_word(self, word: str) -> np.ndarray:
        """Encode a single word via HRR bind(char, pos) + sign-bundle.

        Truncates word at max_pos characters (positions 0..max_pos-1).
        Empty word returns all +1 vector (deterministic sentinel).
        """
        if len(word) == 0:
            out = np.ones(self.n_dim, dtype=np.float32)
            return out
        w = word[: self.max_pos]
        parts = np.zeros((len(w), self.n_dim), dtype=np.float32)
        for i, c in enumerate(w):
            parts[i] = _hrr_bind(self._char_hd(c), self._pos_hd(i))
        return _sign_bundle(parts)

    def encode_sentence(self, sentence: str) -> np.ndarray:
        """Encode a sentence as bag-of-word-HDs (order invariant across words).

        Lowercased, whitespace-tokenized. Non-alphanumeric chars kept
        (position-encoding handles them). Empty sentence returns +1 sentinel.
        """
        words = sentence.lower().split()
        if len(words) == 0:
            return np.ones(self.n_dim, dtype=np.float32)
        parts = np.zeros((len(words), self.n_dim), dtype=np.float32)
        for i, w in enumerate(words):
            parts[i] = self.encode_word(w)
        return _sign_bundle(parts)

    def encode_sentence_masked(
        self, sentence: str, mask_word: str
    ) -> np.ndarray:
        """Encode sentence dropping any occurrence of mask_word (context-only).

        Used by concept-encoder arms to build the CONTEXT vector (all words
        except the target concept word). Case-insensitive match.
        """
        words = [w for w in sentence.lower().split() if w != mask_word.lower()]
        if len(words) == 0:
            return np.ones(self.n_dim, dtype=np.float32)
        parts = np.zeros((len(words), self.n_dim), dtype=np.float32)
        for i, w in enumerate(words):
            parts[i] = self.encode_word(w)
        return _sign_bundle(parts)

    def encode_batch(self, sentences: Iterable[str]) -> np.ndarray:
        """Batch-encode sentences; returns [B, n_dim] bipolar array."""
        sents = list(sentences)
        out = np.zeros((len(sents), self.n_dim), dtype=np.float32)
        for i, s in enumerate(sents):
            out[i] = self.encode_sentence(s)
        return out

    def n_unique_chars(self) -> int:
        return len(self._char_cache)

    def n_unique_positions(self) -> int:
        return len(self._pos_cache)


# ---------------------------------------------------------------------------
# Self-test (invoked when module run as script)
# ---------------------------------------------------------------------------

def _selftest() -> None:
    enc = CharPositionalEncoder(n_dim=1024, max_pos=16, seed_prefix="TEST")

    # Determinism: same word twice returns bit-identical HD.
    a = enc.encode_word("cat")
    b = enc.encode_word("cat")
    assert np.array_equal(a, b), "determinism failure: cat != cat"

    # Bipolar output: all entries are +-1.
    unique_vals = set(np.unique(a).tolist())
    assert unique_vals.issubset({-1.0, 1.0}), (
        f"word HD not bipolar; unique values = {unique_vals}"
    )

    # Position-sensitivity: "cat" vs "tac" (same chars, different positions).
    c = enc.encode_word("tac")
    cos_cat_tac = float(np.dot(a, c)) / float(len(a))
    # Not identical (differ significantly): position binding must differentiate.
    assert cos_cat_tac < 0.5, (
        f"position-sensitivity broken: cos(cat,tac)={cos_cat_tac:.3f} too high"
    )

    # Sentence encoding: same sentence twice -> same HD.
    s1 = enc.encode_sentence("the cat sat on the mat")
    s2 = enc.encode_sentence("the cat sat on the mat")
    assert np.array_equal(s1, s2), "sentence determinism failure"

    # Order-invariance ACROSS WORDS (bag-of-words): word-order permutations
    # of the same word set should still align highly (they are literally the
    # sign-bundle sum of the same word HDs).
    s3 = enc.encode_sentence("mat the on sat cat the")
    cos_s1_s3 = float(np.dot(s1, s3)) / float(len(s1))
    assert cos_s1_s3 > 0.95, (
        f"bag-of-words order-invariance broken: cos={cos_s1_s3:.3f}"
    )

    # Masked encoding excludes the concept word.
    s_full = enc.encode_sentence("the cat sat on the mat")
    s_ctx = enc.encode_sentence_masked("the cat sat on the mat", "cat")
    s_no_cat = enc.encode_sentence("the sat on the mat")
    assert np.array_equal(s_ctx, s_no_cat), (
        "masked encoding must equal sentence with the concept removed"
    )
    cos_full_ctx = float(np.dot(s_full, s_ctx)) / float(len(s_full))
    # They should be similar but NOT identical (cat contributes to bundle).
    assert 0.3 < cos_full_ctx < 0.99, (
        f"masked-context cos={cos_full_ctx:.3f} out of expected band"
    )

    # Truncation: word longer than max_pos is truncated (does not crash).
    long_word = "a" * 100
    hd_long = enc.encode_word(long_word)
    assert hd_long.shape == (enc.n_dim,)

    print(
        f"[char_positional_encoder selftest] PASS  "
        f"n_dim={enc.n_dim}  n_chars={enc.n_unique_chars()}  "
        f"n_positions={enc.n_unique_positions()}  "
        f"cos_cat_tac={cos_cat_tac:.3f}  cos_bag_permute={cos_s1_s3:.3f}  "
        f"cos_full_vs_ctx={cos_full_ctx:.3f}",
        flush=True,
    )


if __name__ == "__main__":
    _selftest()
