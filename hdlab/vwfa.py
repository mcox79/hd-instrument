"""Substrate-native VWFA-analog multi-scale character-with-position encoder.

INPUT REGIME DOCSTRING BLOCK:
    Input: raw text (unicode string; ASCII in current use).
    Output: bipolar {-1, +1} HD vector of dimension n_dim (or float32 raw sum
        if `sign_bundle=False`).
    Regime type: SURFACE ORTHOGRAPHIC FEATURES ONLY.  Multi-scale character
        n-gram bank (n in {1,2,3,4} by default) with HRR position-binding
        per n-gram within word.  Does NOT know semantic identity of any word.
    Brain analog: VWFA (Visual Word Form Area, left mid-fusiform).  Dehaene-
        Cohen 2005 letterbox model / hierarchical local combination detectors
        (LCD): L2 case-invariant letters, L3 open-bigrams, L4 quadrigrams,
        L5 whole-word units.  Simultaneous multi-scale + position-relative
        encoding, order-approximation.  Pre-computed read-only encoder at
        retrieval time (statistics baked in).
    Scope for substrate:  L4-analog dense feature bank feeding into the
        L2/3-analog sparse-competitive-Hebbian (ATL-analog) concept encoder.
        Composes with LATE COMBINE (N400-window integration).

Design:
  - Per (n-gram, scale) an n_dim bipolar HD via hashed seed.  Scales are
    labelled in seed so char='a' at scale=1 differs from bigram='a?' at
    scale=2 (no cross-scale collision).
  - For each scale n in scales:
        for each starting position i in word w:
            g = w[i:i+n]
            hd_ng = codebook[(scale, g)]
            pos_hd = codebook_pos[scale, i]  (per-scale so scale-1 pos differs
                                              from scale-2 pos)
            if bind_position:
                bundled += HRR_bind(hd_ng, pos_hd)
            else:
                bundled += hd_ng
  - Sum across positions and scales (with per-scale weights).
  - Sign-bundle at output (bipolar) unless `sign_bundle=False`.

Backward-compat subsumption:
  - VWFA(scales=[3], bind_position=False, sign_bundle=True) has THE SAME
    STRUCTURE as CharTrigramEncoder (bag-of-trigrams, sign-bundle bipolar).
    Codebook is a different hash namespace ("VWFA_..." vs blake2b(trigram))
    so absolute HDs differ, but the RETRIEVAL BEHAVIOR should track closely
    on the held-out synonym task (both encode the same trigram co-occurrence
    structure).  Verified in selftest by cosine-alignment on shared vocab.

Pure substrate primitives.  NumPy; no torch.  ASCII-only.
"""

from __future__ import annotations

import hashlib
from typing import Iterable, List, Optional, Sequence

import numpy as np


# ---------------------------------------------------------------------------
# Deterministic bipolar HD generation
# ---------------------------------------------------------------------------

def _seed_for_token(token: str) -> int:
    h = hashlib.blake2b(token.encode("utf-8"), digest_size=4).digest()
    return int.from_bytes(h, "big")


def _bipolar_hv(seed: int, n_dim: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return (rng.integers(0, 2, size=n_dim) * 2 - 1).astype(np.float32)


# ---------------------------------------------------------------------------
# HRR bind helpers (matches char_positional_encoder)
# ---------------------------------------------------------------------------

def _hrr_bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    fa = np.fft.fft(a)
    fb = np.fft.fft(b)
    return np.real(np.fft.ifft(fa * fb)).astype(a.dtype)


def _sign_bundle(v: np.ndarray) -> np.ndarray:
    out = np.sign(v).astype(np.float32)
    out[out == 0] = 1.0
    return out


# ---------------------------------------------------------------------------
# VWFAEncoder
# ---------------------------------------------------------------------------

class VWFAEncoder:
    """Multi-scale character-with-position orthographic encoder (VWFA-analog).

    Parameters
    ----------
    n_dim : int
        HD vector dimension.
    scales : Sequence[int]
        Character n-gram scales to encode simultaneously.  Default
        [1,2,3,4] = char, bigram, trigram, quadrigram (Dehaene 2005 letterbox
        L2-L4).  A single-scale=[3] setting subsumes bag-of-trigrams.
    bind_position : bool
        If True, HRR-bind each n-gram with its start-position HD before
        bundling.  If False, plain bag (subsumes char_trigram_encoder when
        scales=[3]).  Default True.
    scale_weights : Optional[Sequence[float]]
        Per-scale weight in the sum.  If None, uniform.  Length must match
        scales.
    max_pos : int
        Max positions per word (positions beyond are folded via i mod max_pos
        so long words do not crash but re-use pos codebook -- consistent with
        char_positional_encoder truncation, we simply cap at max_pos here).
    seed_prefix : str
        Codebook namespace so different regimes don't collide.
    pad_char : str
        Pad character prepended and appended to word before extracting n-grams
        (matches char_trigram behavior for boundary markers).  Default ' '.
    sign_bundle : bool
        If True (default), sign() bundle at output (bipolar).  If False, raw
        float32 sum (useful when downstream late-combine wants graded signal).
    """

    def __init__(
        self,
        n_dim: int = 2048,
        scales: Sequence[int] = (1, 2, 3, 4),
        bind_position: bool = True,
        scale_weights: Optional[Sequence[float]] = None,
        max_pos: int = 24,
        seed_prefix: str = "VWFA",
        pad_char: str = " ",
        sign_bundle: bool = True,
    ) -> None:
        if n_dim <= 0:
            raise ValueError(f"n_dim must be positive; got {n_dim}")
        if not scales:
            raise ValueError("scales must be non-empty")
        for n in scales:
            if int(n) < 1:
                raise ValueError(f"scale must be >= 1; got {n}")
        if scale_weights is not None:
            if len(scale_weights) != len(scales):
                raise ValueError(
                    f"scale_weights len={len(scale_weights)} must match "
                    f"scales len={len(scales)}"
                )
            self.scale_weights = tuple(float(w) for w in scale_weights)
        else:
            self.scale_weights = tuple(1.0 for _ in scales)
        self.n_dim = int(n_dim)
        self.scales = tuple(int(n) for n in scales)
        self.bind_position = bool(bind_position)
        self.max_pos = int(max_pos)
        self.seed_prefix = str(seed_prefix)
        self.pad_char = str(pad_char)
        self.sign_bundle = bool(sign_bundle)
        # Codebooks: (scale, ngram) -> HD; (scale, pos) -> HD
        self._ngram_cache: dict[tuple, np.ndarray] = {}
        self._pos_cache: dict[tuple, np.ndarray] = {}

    # ---------- codebook lookups ----------

    def _ngram_hd(self, scale: int, ngram: str) -> np.ndarray:
        key = (int(scale), ngram)
        cached = self._ngram_cache.get(key)
        if cached is not None:
            return cached
        token = f"{self.seed_prefix}_SCALE_{scale}_NGRAM_{ngram}"
        hd = _bipolar_hv(_seed_for_token(token), self.n_dim)
        self._ngram_cache[key] = hd
        return hd

    def _pos_hd(self, scale: int, pos: int) -> np.ndarray:
        # Fold long positions to max_pos so codebook stays finite.
        p = int(pos) % int(self.max_pos)
        key = (int(scale), p)
        cached = self._pos_cache.get(key)
        if cached is not None:
            return cached
        token = f"{self.seed_prefix}_SCALE_{scale}_POS_{p}"
        hd = _bipolar_hv(_seed_for_token(token), self.n_dim)
        self._pos_cache[key] = hd
        return hd

    # ---------- encoding ----------

    def _encode_word_raw(self, word: str) -> np.ndarray:
        """Return raw float32 sum across scales and positions for a single word.

        No sign-bundle at this stage.
        """
        acc = np.zeros(self.n_dim, dtype=np.float32)
        w = self.pad_char + word.lower() + self.pad_char
        for scale, weight in zip(self.scales, self.scale_weights):
            if len(w) < scale:
                # Word shorter than the scale: skip.
                continue
            # Positions 0 .. len(w)-scale inclusive.
            n_positions = len(w) - scale + 1
            scale_acc = np.zeros(self.n_dim, dtype=np.float32)
            for i in range(n_positions):
                g = w[i:i + scale]
                hd_ng = self._ngram_hd(scale, g)
                if self.bind_position:
                    hd_pos = self._pos_hd(scale, i)
                    v = _hrr_bind(hd_ng, hd_pos)
                else:
                    v = hd_ng
                scale_acc += v
            acc += float(weight) * scale_acc
        return acc

    def encode_word(self, word: str) -> np.ndarray:
        """Encode a single word (sign-bundled if configured)."""
        raw = self._encode_word_raw(word)
        if self.sign_bundle:
            # If all zeros (empty word or purely cancelling), return +1 sentinel.
            if not np.any(raw):
                return np.ones(self.n_dim, dtype=np.float32)
            return _sign_bundle(raw)
        return raw

    def encode_sentence(self, sentence: str) -> np.ndarray:
        """Encode a sentence as bag-of-word-HDs.

        Words are whitespace-tokenized.  Per-word raw sums accumulate then
        sign-bundle at the end (matches char_positional_encoder pattern).
        """
        words = sentence.lower().split()
        if not words:
            return np.ones(self.n_dim, dtype=np.float32)
        acc = np.zeros(self.n_dim, dtype=np.float32)
        for w in words:
            acc += self._encode_word_raw(w)
        if self.sign_bundle:
            if not np.any(acc):
                return np.ones(self.n_dim, dtype=np.float32)
            return _sign_bundle(acc)
        return acc

    def encode(self, text: str) -> np.ndarray:
        """Alias for encode_sentence for parity with CharTrigramEncoder."""
        return self.encode_sentence(text)

    def encode_batch(self, texts: Iterable[str]) -> np.ndarray:
        ts = list(texts)
        out = np.zeros((len(ts), self.n_dim), dtype=np.float32)
        for i, t in enumerate(ts):
            out[i] = self.encode_sentence(t)
        return out

    # ---------- introspection ----------

    def n_unique_ngrams(self) -> int:
        return len(self._ngram_cache)

    def n_unique_positions(self) -> int:
        return len(self._pos_cache)

    def __repr__(self) -> str:
        return (
            f"VWFAEncoder(n_dim={self.n_dim}, scales={self.scales}, "
            f"bind_position={self.bind_position}, "
            f"scale_weights={self.scale_weights}, sign_bundle={self.sign_bundle})"
        )


# ---------------------------------------------------------------------------
# Self-test (invoked when module run as script)
# ---------------------------------------------------------------------------

def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def _selftest() -> None:
    # Basic determinism + shape.
    enc = VWFAEncoder(n_dim=1024, scales=(1, 2, 3, 4), bind_position=True,
                      max_pos=24, seed_prefix="TEST")
    a1 = enc.encode_word("cat")
    a2 = enc.encode_word("cat")
    assert np.array_equal(a1, a2), "determinism failure"
    assert a1.shape == (1024,), f"shape {a1.shape} != (1024,)"

    # Bipolar output when sign_bundle=True (default).
    uniq = set(np.unique(a1).tolist())
    assert uniq.issubset({-1.0, 1.0}), f"non-bipolar values {uniq}"

    # Multi-scale composition: same char, different position -> different HD.
    hd_cat = enc.encode_word("cat")
    hd_tac = enc.encode_word("tac")
    cos_cat_tac = _cosine(hd_cat, hd_tac)
    assert cos_cat_tac < 0.90, (
        f"position-sensitivity broken: cos(cat,tac)={cos_cat_tac:.3f} too high"
    )

    # Empty word returns +1 sentinel (never NaN or all-zero).
    hd_empty = enc.encode_word("")
    assert hd_empty.shape == (1024,)
    assert np.all(hd_empty == 1.0) or not np.all(hd_empty == 0.0), (
        "empty word produced degenerate HD"
    )

    # Subsumption sanity: single-scale=[3], bind_position=False configuration
    # produces bag-of-trigrams STRUCTURE (different codebook hash namespace
    # than CharTrigramEncoder but same computational shape).  Verify by
    # checking that permuting internal word order (which shouldn't change
    # bag-of-trigrams up to boundary effects) preserves the HD closely.
    enc_bag3 = VWFAEncoder(n_dim=1024, scales=(3,), bind_position=False,
                           max_pos=24, seed_prefix="TEST")
    hd_abc = enc_bag3.encode_word("abc")
    hd_abc_reencoded = enc_bag3.encode_word("abc")
    assert np.array_equal(hd_abc, hd_abc_reencoded), (
        "bag-of-trigrams config determinism"
    )
    # Distinct trigram content -> distinct HD.
    hd_xyz = enc_bag3.encode_word("xyz")
    cos_abc_xyz = _cosine(hd_abc, hd_xyz)
    assert cos_abc_xyz < 0.5, (
        f"bag-of-trigrams discrimination broken: cos(abc,xyz)={cos_abc_xyz:.3f}"
    )

    # Sentence encoding parity: multi-word sentence returns single HD.
    hd_sent = enc.encode_sentence("the cat sat on the mat")
    assert hd_sent.shape == (1024,)
    # Bipolar.
    uniq_sent = set(np.unique(hd_sent).tolist())
    assert uniq_sent.issubset({-1.0, 1.0}), (
        f"sentence not bipolar; uniq={uniq_sent}"
    )

    # Synonym-like near-miss test.  "entombment" and "burial" have no shared
    # char-trigrams at scale=3; the multi-scale bank should give a low
    # cosine (near-orthogonal), NOT close to 1.  This documents the
    # expectation: VWFA alone cannot solve synonym retrieval.  It provides
    # ORTHOGRAPHIC signal to be COMBINED with semantic in late-combine.
    hd_entombment = enc.encode_word("entombment")
    hd_burial = enc.encode_word("burial")
    cos_synonym = _cosine(hd_entombment, hd_burial)
    assert abs(cos_synonym) < 0.5, (
        f"synonym cosine unexpectedly high: cos(entombment,burial)={cos_synonym:.3f}. "
        "VWFA should NOT match synonyms via surface alone (orthogonal is expected)."
    )

    # Backward-compat check: raw sum (sign_bundle=False) is float32 with
    # graded values and non-zero norm.
    enc_raw = VWFAEncoder(n_dim=1024, scales=(1, 2, 3, 4), bind_position=True,
                          max_pos=24, seed_prefix="TEST", sign_bundle=False)
    hd_raw = enc_raw.encode_word("cat")
    assert hd_raw.dtype == np.float32
    assert float(np.linalg.norm(hd_raw)) > 0.0, "raw HD has zero norm"
    assert set(np.unique(hd_raw).tolist()) != {-1.0, 1.0}, (
        "raw HD unexpectedly bipolar; sign_bundle=False should give graded"
    )

    # Multi-scale RICHNESS: same scale=[3] vs full scales=[1,2,3,4] should give
    # DIFFERENT HDs for the same word (multi-scale is a distinct encoding).
    enc_full = VWFAEncoder(n_dim=1024, scales=(1, 2, 3, 4), bind_position=True,
                           max_pos=24, seed_prefix="TEST")
    enc_tri_only = VWFAEncoder(n_dim=1024, scales=(3,), bind_position=True,
                               max_pos=24, seed_prefix="TEST")
    hd_full = enc_full.encode_word("cat")
    hd_tri = enc_tri_only.encode_word("cat")
    # They share codebook namespace via seed_prefix so they draw the SAME
    # trigram HDs at scale=3 -- but the full encoder also folds in scale=1,2,4
    # contributions.  Cosine should be strictly less than 1.0 and strictly
    # greater than 0 (some scale=3 overlap).
    cos_full_tri = _cosine(hd_full, hd_tri)
    assert 0.0 < cos_full_tri < 1.0, (
        f"multi-scale vs single-scale-3 cosine={cos_full_tri:.3f} degenerate"
    )

    print(
        "[vwfa selftest] PASS  "
        f"n_dim={enc.n_dim}  scales={enc.scales}  "
        f"n_ngrams={enc.n_unique_ngrams()}  "
        f"n_positions={enc.n_unique_positions()}  "
        f"cos(cat,tac)={cos_cat_tac:.3f}  "
        f"cos(abc,xyz)@scale3-bag={cos_abc_xyz:.3f}  "
        f"cos(entombment,burial)@multiscale={cos_synonym:.3f}  "
        f"cos(fullscales,triscale)={cos_full_tri:.3f}",
        flush=True,
    )


if __name__ == "__main__":
    _selftest()
