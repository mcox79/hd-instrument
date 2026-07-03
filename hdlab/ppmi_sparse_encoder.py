"""PPMI/SVD-then-threshold sparse encoder for text -> HD retrieval.

Substrate-native, forward-only, closed-form. Alternative to competitive-Hebbian
for concept-encoding on real content (per ML/AI drill 5x-5/5 rec 2026-07-02).

Method (SPOWV Faruqui 2015 arXiv:1506.02004; SPINE Subramanian 2018
arXiv:1711.08792; Random Indexing Sahlgren):
  1. Vocabulary of terms (char-trigrams by default).
  2. Term x concept-label co-occurrence matrix from (sentence, label) pairs.
  3. PPMI transform: PPMI(t,c) = max(0, log(P(t,c) / (P(t) * P(c))))
  4. SVD reduce to n_dim dimensions.
  5. Encode text: sum term-vectors then top-k threshold then bipolar sign.

Zero external LLM. Substrate-native co-occurrence statistics only. Less
brain-analog than competitive-Hebbian but empirical support in text
literature.

INPUT REGIME:
  - fit(sentences, concept_labels): supervised (sentence, concept_label) pairs.
  - encode(text): returns dense float HD suitable for cosine argmax.
  - encode_sparse(text): returns k-sparse bipolar HD.

ASCII-only. No emojis. No em dashes.
"""
from __future__ import annotations

import hashlib
from typing import Iterable, List, Optional, Sequence

import numpy as np


def _trigrams(text: str, pad_char: str = " ") -> List[str]:
    """Overlapping char-trigrams with pad-char boundary markers."""
    t = pad_char + text.lower().replace("_", " ") + pad_char
    if len(t) < 3:
        return [t]
    return [t[i:i + 3] for i in range(len(t) - 2)]


class PPMISparseEncoder:
    """PPMI/SVD-then-threshold sparse encoder over term/concept co-occurrence.

    fit() builds:
      - term vocabulary from training sentences (char-trigrams)
      - term x concept co-occurrence matrix
      - PPMI-transformed matrix
      - SVD-reduced term embeddings (V, n_dim)
    encode(text) sums term embeddings for text's trigrams and returns
    dense float HD; encode_sparse(text) additionally thresholds top-k by
    magnitude and returns bipolar {-1, +1} vector.
    """

    def __init__(
        self,
        n_dim: int = 2048,
        k_sparsity: float = 0.02,
        min_term_freq: int = 2,
        smoothing: float = 0.75,
        pad_char: str = " ",
        seed: int = 0,
    ) -> None:
        """
        n_dim: SVD reduced dim.
        k_sparsity: fraction of dims retained in encode_sparse (top-|k*n_dim|).
        min_term_freq: drop terms occurring < this many times in fit corpus.
        smoothing: context-distribution smoothing exponent
          (Levy/Goldberg 2015); apply P(c)^alpha before PPMI.
        pad_char: boundary pad for char-trigrams.
        seed: reserved (SVD is deterministic; kept for interface parity).
        """
        self.n_dim = int(n_dim)
        self.k_sparsity = float(k_sparsity)
        self.min_term_freq = int(min_term_freq)
        self.smoothing = float(smoothing)
        self.pad_char = pad_char
        self.seed = int(seed)
        # Fit-populated state.
        self.term_to_idx: dict = {}
        self.term_embeddings: Optional[np.ndarray] = None  # [V, n_dim] float32
        self.n_concepts: int = 0
        self.effective_n_dim: int = 0  # min(n_dim, V, C)

    # ------------------------------------------------------------------
    # fit
    # ------------------------------------------------------------------
    def fit(
        self,
        sentences: Sequence[str],
        concept_labels: np.ndarray,
    ) -> "PPMISparseEncoder":
        """Fit PPMI+SVD from (sentence, concept_label) pairs.

        sentences: list of str
        concept_labels: [N_sentences] int, values in [0, n_concepts)
        """
        if len(sentences) != len(concept_labels):
            raise ValueError(
                f"len(sentences)={len(sentences)} != "
                f"len(concept_labels)={len(concept_labels)}"
            )
        labels_arr = np.asarray(concept_labels, dtype=np.int64)
        self.n_concepts = int(labels_arr.max()) + 1 if len(labels_arr) else 0

        # Pass 1: build vocabulary with min-freq filter.
        term_counts: dict = {}
        sent_trigrams: List[List[str]] = []
        for s in sentences:
            tris = _trigrams(str(s), pad_char=self.pad_char)
            sent_trigrams.append(tris)
            for t in set(tris):  # count doc-freq, not raw freq
                term_counts[t] = term_counts.get(t, 0) + 1
        vocab = [t for t, c in term_counts.items() if c >= self.min_term_freq]
        vocab.sort()  # deterministic order
        self.term_to_idx = {t: i for i, t in enumerate(vocab)}
        V = len(vocab)
        C = int(self.n_concepts)
        if V == 0 or C == 0:
            raise RuntimeError(
                f"PPMI fit produced empty vocab/concepts (V={V} C={C}); "
                f"check min_term_freq={self.min_term_freq} or corpus size"
            )

        # Pass 2: build V x C co-occurrence matrix (doc-count).
        cooc = np.zeros((V, C), dtype=np.float64)
        for tris, lbl in zip(sent_trigrams, labels_arr):
            lbl_i = int(lbl)
            seen = set()
            for t in tris:
                idx = self.term_to_idx.get(t)
                if idx is None or idx in seen:
                    continue
                seen.add(idx)
                cooc[idx, lbl_i] += 1.0

        # PPMI transform.
        # Total count = sum cooc; P(t) = row-sum / total; P(c) = col-sum / total.
        total = float(cooc.sum())
        if total <= 0.0:
            raise RuntimeError("PPMI fit: co-occurrence matrix is all zeros")
        row_sums = cooc.sum(axis=1) + 1e-12  # [V]
        col_sums = cooc.sum(axis=0) + 1e-12  # [C]
        # Context-distribution smoothing (Levy/Goldberg 2015).
        col_sums_smoothed = col_sums ** self.smoothing
        col_sums_smoothed_total = col_sums_smoothed.sum() + 1e-12
        # PPMI = max(0, log(P(t,c) / (P(t) * P_alpha(c))))
        #      = max(0, log((cooc/total) / ((row/total) * (col_alpha/col_alpha_total))))
        #      = max(0, log(cooc * col_alpha_total / (row * col_alpha)))
        with np.errstate(divide="ignore", invalid="ignore"):
            numer = cooc * col_sums_smoothed_total
            denom = np.outer(row_sums, col_sums_smoothed)
            ratio = numer / (denom + 1e-30)
            pmi = np.log(ratio + 1e-30)
            pmi[cooc == 0.0] = 0.0
            ppmi = np.maximum(pmi, 0.0)

        # SVD-reduce to n_dim dims.
        # Use numpy SVD; PPMI matrix is V x C. Reduce to min(n_dim, V, C).
        target_dim = min(self.n_dim, V, C)
        self.effective_n_dim = int(target_dim)
        # Full SVD; take top-target_dim.
        U, S, _ = np.linalg.svd(ppmi.astype(np.float32), full_matrices=False)
        # Term embeddings = U * sqrt(S) truncated to target_dim.
        U_trunc = U[:, :target_dim]  # [V, target_dim]
        S_trunc = S[:target_dim]  # [target_dim]
        term_emb = U_trunc * np.sqrt(S_trunc + 1e-12)[None, :]
        # Pad to n_dim if target_dim < n_dim (right-zero-pad).
        if target_dim < self.n_dim:
            pad = np.zeros((V, self.n_dim - target_dim), dtype=np.float32)
            term_emb = np.concatenate([term_emb.astype(np.float32), pad], axis=1)
        self.term_embeddings = term_emb.astype(np.float32)
        return self

    # ------------------------------------------------------------------
    # encode
    # ------------------------------------------------------------------
    def encode(self, text: str) -> np.ndarray:
        """Encode text -> dense float HD [n_dim] by summing term embeddings.

        OOV terms are skipped. Returns zero vector if no in-vocab terms.
        """
        if self.term_embeddings is None:
            raise RuntimeError("encoder not fit; call fit() first")
        tris = _trigrams(str(text), pad_char=self.pad_char)
        if not tris:
            return np.zeros(self.n_dim, dtype=np.float32)
        acc = np.zeros(self.n_dim, dtype=np.float32)
        hits = 0
        for t in tris:
            idx = self.term_to_idx.get(t)
            if idx is None:
                continue
            acc += self.term_embeddings[idx]
            hits += 1
        if hits == 0:
            return np.zeros(self.n_dim, dtype=np.float32)
        return acc / float(hits)

    def encode_sparse(self, text: str) -> np.ndarray:
        """Encode text -> k-sparse bipolar {-1, 0, +1} [n_dim].

        k = round(k_sparsity * n_dim); top-k magnitude components -> sign.
        """
        dense = self.encode(text)
        k = max(1, int(round(self.k_sparsity * self.n_dim)))
        if np.all(dense == 0.0):
            return dense.astype(np.int8)
        mag = np.abs(dense)
        if k >= dense.shape[0]:
            out = np.sign(dense)
        else:
            idx = np.argpartition(-mag, k - 1)[:k]
            out = np.zeros_like(dense)
            out[idx] = np.sign(dense[idx])
        out[out == 0] = 0  # keep zeros as zeros (int8 later)
        return out.astype(np.int8)

    def encode_batch(self, texts: Iterable[str]) -> np.ndarray:
        """Batch dense encode -> [N, n_dim] float32."""
        texts = list(texts)
        out = np.zeros((len(texts), self.n_dim), dtype=np.float32)
        for i, t in enumerate(texts):
            out[i] = self.encode(t)
        return out


# ---------------------------------------------------------------------------
# Random Indexing (Sahlgren) reference implementation for cell arm parity.
# ---------------------------------------------------------------------------


def _random_indexing_hv(term: str, n_dim: int, k_signs: int) -> np.ndarray:
    """Deterministic sparse ternary random-index vector per term.

    k_signs = # nonzeros; half +1 half -1 (Sahlgren-style).
    """
    h = hashlib.blake2b(term.encode("utf-8"), digest_size=8).digest()
    seed = int.from_bytes(h, "big") & 0x7FFFFFFF
    rng = np.random.default_rng(seed)
    idx = rng.choice(n_dim, size=k_signs, replace=False)
    signs = rng.integers(0, 2, size=k_signs) * 2 - 1
    v = np.zeros(n_dim, dtype=np.float32)
    v[idx] = signs.astype(np.float32)
    return v


class RandomIndexingEncoder:
    """Sahlgren-style Random Indexing text encoder over char-trigrams.

    Accumulates term-vectors (deterministic sparse ternary per trigram) for
    every trigram in text. Trained accumulation over concept-labeled corpus
    yields per-concept context vectors; a fresh text encodes as bundled
    sum of trigram vectors.

    No PPMI, no SVD. Uses accumulated co-occurrence via bundling.
    """

    def __init__(
        self,
        n_dim: int = 2048,
        k_signs: int = 8,
        pad_char: str = " ",
    ) -> None:
        self.n_dim = int(n_dim)
        self.k_signs = int(k_signs)
        self.pad_char = pad_char
        self._cache: dict = {}

    def _hv(self, term: str) -> np.ndarray:
        cached = self._cache.get(term)
        if cached is not None:
            return cached
        v = _random_indexing_hv(term, self.n_dim, self.k_signs)
        self._cache[term] = v
        return v

    def encode(self, text: str) -> np.ndarray:
        tris = _trigrams(str(text), pad_char=self.pad_char)
        if not tris:
            return np.zeros(self.n_dim, dtype=np.float32)
        acc = np.zeros(self.n_dim, dtype=np.float32)
        for t in tris:
            acc += self._hv(t)
        return acc

    def encode_batch(self, texts: Iterable[str]) -> np.ndarray:
        texts = list(texts)
        out = np.zeros((len(texts), self.n_dim), dtype=np.float32)
        for i, t in enumerate(texts):
            out[i] = self.encode(t)
        return out


# ---------------------------------------------------------------------------
# Self-test.
# ---------------------------------------------------------------------------


def _selftest() -> None:
    """Verify PPMI transform correctness + SVD reduction + sparse output."""
    # Toy corpus: 3 concepts, each with 4 sentences containing telltale terms.
    sentences = [
        "cat feline pet purr",
        "cat pet whiskers meow",
        "cat feline paws claws",
        "kitten cat baby pet",
        "dog canine bark loyal",
        "dog bark wolf ancestor",
        "dog canine pet leash",
        "puppy dog young pet",
        "airplane jet wing fly",
        "airplane pilot cockpit sky",
        "jet aircraft engine turbine",
        "helicopter rotor sky airplane",
    ]
    labels = np.array([0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2], dtype=np.int64)
    enc = PPMISparseEncoder(n_dim=64, k_sparsity=0.25, min_term_freq=1, seed=11)
    enc.fit(sentences, labels)
    assert enc.term_embeddings is not None
    assert enc.term_embeddings.shape[1] == 64, (
        f"term_embeddings n_dim mismatch: {enc.term_embeddings.shape}"
    )
    # Effective dim should be <= min(V, C, n_dim) = min(V, 3, 64) = 3.
    assert enc.effective_n_dim <= 3, (
        f"effective_n_dim expected <=3, got {enc.effective_n_dim}"
    )
    # Encode dense.
    dense_cat = enc.encode("cat pet feline")
    dense_dog = enc.encode("dog canine bark")
    dense_plane = enc.encode("airplane pilot")
    assert dense_cat.shape == (64,), f"encode shape: {dense_cat.shape}"
    # cat query should be closer (cosine) to a cat-training sentence than
    # to a dog-training sentence.
    def _cos(a, b):
        na = np.linalg.norm(a) + 1e-8
        nb = np.linalg.norm(b) + 1e-8
        return float((a @ b) / (na * nb))
    ref_cat = enc.encode("cat feline pet purr")
    ref_dog = enc.encode("dog canine bark loyal")
    ref_plane = enc.encode("airplane jet wing fly")
    assert _cos(dense_cat, ref_cat) > _cos(dense_cat, ref_dog), (
        "PPMI encoder failed: cat query closer to dog than to cat sentence"
    )
    assert _cos(dense_plane, ref_plane) > _cos(dense_plane, ref_dog), (
        "PPMI encoder failed: airplane query closer to dog than to airplane"
    )
    # Sparse encode: check k-sparsity.
    sparse_cat = enc.encode_sparse("cat pet feline")
    nz = int((sparse_cat != 0).sum())
    k_expected = max(1, int(round(0.25 * 64)))  # 16
    assert nz <= k_expected, (
        f"sparse encode: {nz} nonzeros > k_expected={k_expected}"
    )
    # Random Indexing self-check.
    ri = RandomIndexingEncoder(n_dim=64, k_signs=4)
    ri_cat = ri.encode("cat feline pet purr")
    ri_dog = ri.encode("dog canine bark loyal")
    assert ri_cat.shape == (64,)
    # Deterministic: same term -> same vector.
    v1 = ri._hv("cat")
    v2 = ri._hv("cat")
    assert np.array_equal(v1, v2), "RI: same term produced different vectors"
    print("ppmi_sparse_encoder selftest: PASS "
          f"(V={len(enc.term_to_idx)} effective_dim={enc.effective_n_dim} "
          f"sparse_nz={nz}/{k_expected})")


if __name__ == "__main__":
    _selftest()
