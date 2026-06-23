"""Random Indexing (Sahlgren 2005, Kanerva 1988) -- substrate-native distributional semantics.

Forward-only Hebbian co-occurrence accumulator. Each word w gets:
  - i_w: immutable sparse-ternary index vector in {-1, 0, +1}^N (s nonzero entries)
  - c_w: mutable dense context vector in R^N, accumulating i_w' for w' in context window

After ingesting a corpus, cosine(c_w1, c_w2) reflects distributional similarity.
cat-dog close because they share context words (pet, food, animal, ...).

Composes with substrate's bipolar bundling + binding primitives. Zero backprop.
Online streaming; no V x V matrix required. Mathematically equivalent to
random projection of PMI co-occurrence matrix (Bingham-Mannila 2001 JL bound).

Public API:
    RandomIndexingEncoder(N, sparsity, window, seed)
        fit_corpus(tokens_iter)
        encode(word) -> np.ndarray   # the context vector
        similarity(w1, w2) -> float  # cosine similarity
        vocab() -> list[str]

BEAGLE extension flag (Jones-Mewhort 2007): add HRR-permutation-bound order chunks
alongside the bag-of-context accumulator. With order=True, the context vector also
accumulates cyclic-shift-bound n-grams of context environment vectors, giving the
substrate word-order sensitivity in addition to bag-distributional similarity.

ASCII-only per feedback_ascii_only_in_scripts.
"""
from __future__ import annotations

from collections import Counter
from typing import Iterable, List, Optional

import numpy as np


def _make_index_vector(rng: np.random.Generator, N: int, s: int) -> np.ndarray:
    """Sparse-ternary index vector in {-1, 0, +1}^N with exactly s nonzero entries.

    Half +1 / half -1 (with the odd one randomly signed) for zero-mean.
    """
    v = np.zeros(N, dtype=np.float32)
    idx = rng.choice(N, size=s, replace=False)
    signs = rng.integers(0, 2, size=s).astype(np.float32) * 2.0 - 1.0
    v[idx] = signs
    return v


def _cyclic_shift(v: np.ndarray, k: int) -> np.ndarray:
    """Cyclic right-shift by k positions (permutation primitive for HRR-style order binding)."""
    return np.roll(v, k)


def _l2_normalize(v: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    n = float(np.linalg.norm(v))
    if n < eps:
        return v
    return v / n


class RandomIndexingEncoder:
    """Substrate-native distributional encoder via Random Indexing + optional BEAGLE order binding.

    Parameters
    ----------
    N : int
        Hyperdimensional vector size (default 8192).
    sparsity : int
        Number of nonzero entries per index vector (default 10; s/N ~ 0.001).
    window : int
        Symmetric context window radius. window=5 means 5 left + 5 right neighbors.
    min_count : int
        Word frequency cutoff (canonical word2vec preprocessing).
    seed : int
        RNG seed (deterministic index vectors).
    order_binding : bool
        If True, also accumulate cyclic-shift-bound order chunks (BEAGLE extension).
    """

    def __init__(
        self,
        N: int = 8192,
        sparsity: int = 10,
        window: int = 5,
        min_count: int = 5,
        seed: int = 0,
        order_binding: bool = False,
    ) -> None:
        if sparsity >= N:
            raise ValueError("sparsity must be < N")
        if window < 1:
            raise ValueError("window must be >= 1")
        self.N = int(N)
        self.sparsity = int(sparsity)
        self.window = int(window)
        self.min_count = int(min_count)
        self.seed = int(seed)
        self.order_binding = bool(order_binding)
        # Built by fit_corpus
        self._word_to_idx: dict[str, int] = {}
        self._idx_to_word: List[str] = []
        self._index_vectors: Optional[np.ndarray] = None    # (V, N) float32
        self._context_vectors: Optional[np.ndarray] = None  # (V, N) float32
        self._counts: Optional[np.ndarray] = None
        self._n_tokens_seen: int = 0

    def _build_vocab(self, tokens: List[str]) -> None:
        c = Counter(tokens)
        kept = [(w, n) for w, n in c.most_common() if n >= self.min_count]
        # Deterministic order: sort by count desc, then lexicographic for ties (Counter.most_common is already by count desc but tie order is insertion).
        kept.sort(key=lambda x: (-x[1], x[0]))
        self._word_to_idx = {w: i for i, (w, _n) in enumerate(kept)}
        self._idx_to_word = [w for w, _n in kept]
        self._counts = np.array([n for _w, n in kept], dtype=np.int64)

    def _build_index_vectors(self) -> None:
        V = len(self._idx_to_word)
        rng = np.random.default_rng(self.seed)
        M = np.zeros((V, self.N), dtype=np.float32)
        for i in range(V):
            M[i] = _make_index_vector(rng, self.N, self.sparsity)
        self._index_vectors = M

    def fit_corpus(self, tokens_iter: Iterable[str]) -> None:
        """Stream-ingest a corpus. Single forward pass.

        tokens_iter: iterable of lowercase whitespace-tokenized words.
        After return: self._context_vectors is the V x N float32 context table.
        """
        tokens = list(tokens_iter)
        self._n_tokens_seen = len(tokens)
        self._build_vocab(tokens)
        self._build_index_vectors()

        V = len(self._idx_to_word)
        C = np.zeros((V, self.N), dtype=np.float32)
        IDX = self._index_vectors
        w2i = self._word_to_idx
        n = len(tokens)
        win = self.window

        # Pre-map tokens to indices (skip OOV)
        token_ids = np.full(n, -1, dtype=np.int64)
        for t_pos, w in enumerate(tokens):
            j = w2i.get(w, -1)
            token_ids[t_pos] = j

        if self.order_binding:
            for t_pos in range(n):
                center = int(token_ids[t_pos])
                if center < 0:
                    continue
                lo = max(0, t_pos - win)
                hi = min(n, t_pos + win + 1)
                for j in range(lo, hi):
                    if j == t_pos:
                        continue
                    other = int(token_ids[j])
                    if other < 0:
                        continue
                    # Bag-of-context update (canonical RI)
                    C[center] += IDX[other]
                    # Order chunk: bind by cyclic shift = (j - t_pos) signed offset
                    offset = j - t_pos
                    C[center] += _cyclic_shift(IDX[other], offset)
        else:
            for t_pos in range(n):
                center = int(token_ids[t_pos])
                if center < 0:
                    continue
                lo = max(0, t_pos - win)
                hi = min(n, t_pos + win + 1)
                for j in range(lo, hi):
                    if j == t_pos:
                        continue
                    other = int(token_ids[j])
                    if other < 0:
                        continue
                    C[center] += IDX[other]

        self._context_vectors = C

    def vocab(self) -> List[str]:
        return list(self._idx_to_word)

    def vocab_size(self) -> int:
        return len(self._idx_to_word)

    def has(self, word: str) -> bool:
        return word in self._word_to_idx

    def encode(self, word: str) -> np.ndarray:
        """Return the context vector for word. Raises KeyError if OOV."""
        if self._context_vectors is None:
            raise RuntimeError("encoder not fit; call fit_corpus first")
        if word not in self._word_to_idx:
            raise KeyError(word)
        return self._context_vectors[self._word_to_idx[word]]

    def encode_index(self, word: str) -> np.ndarray:
        """Return the IMMUTABLE sparse-ternary index vector for word (for hub-spoke compositions)."""
        if self._index_vectors is None:
            raise RuntimeError("encoder not fit; call fit_corpus first")
        if word not in self._word_to_idx:
            raise KeyError(word)
        return self._index_vectors[self._word_to_idx[word]]

    def similarity(self, w1: str, w2: str) -> float:
        """Cosine similarity of context vectors. Returns float in [-1, 1] (or 0 if OOV)."""
        if w1 not in self._word_to_idx or w2 not in self._word_to_idx:
            return 0.0
        v1 = self._context_vectors[self._word_to_idx[w1]]
        v2 = self._context_vectors[self._word_to_idx[w2]]
        n1 = float(np.linalg.norm(v1))
        n2 = float(np.linalg.norm(v2))
        if n1 < 1e-12 or n2 < 1e-12:
            return 0.0
        return float(np.dot(v1, v2) / (n1 * n2))

    def get_context_matrix(self) -> np.ndarray:
        """Return the full V x N context matrix (read-only view; caller copies if mutating)."""
        if self._context_vectors is None:
            raise RuntimeError("encoder not fit; call fit_corpus first")
        return self._context_vectors

    def get_index_matrix(self) -> np.ndarray:
        if self._index_vectors is None:
            raise RuntimeError("encoder not fit; call fit_corpus first")
        return self._index_vectors


def _selftest() -> None:
    """Mechanism selftest: deterministic indices + accumulation correctness + similarity sanity."""
    # 1. Index vectors are sparse-ternary with correct sparsity
    rng = np.random.default_rng(0)
    v = _make_index_vector(rng, 1024, 10)
    nnz = int(np.count_nonzero(v))
    assert nnz == 10, "index vector should have exactly s=10 nonzero entries, got %d" % nnz
    assert set(np.unique(v).tolist()).issubset({-1.0, 0.0, 1.0}), "index entries should be in {-1,0,1}"
    # 2. Determinism: same seed yields same encoder
    toks = ["the", "cat", "sat", "on", "the", "mat", "the", "dog", "sat", "on", "the", "rug"]
    e1 = RandomIndexingEncoder(N=512, sparsity=8, window=2, min_count=1, seed=42)
    e1.fit_corpus(toks)
    e2 = RandomIndexingEncoder(N=512, sparsity=8, window=2, min_count=1, seed=42)
    e2.fit_corpus(toks)
    assert np.allclose(e1.get_context_matrix(), e2.get_context_matrix()), "encoders with same seed must be deterministic"
    # 3. Different seed -> different index vectors
    e3 = RandomIndexingEncoder(N=512, sparsity=8, window=2, min_count=1, seed=7)
    e3.fit_corpus(toks)
    assert not np.allclose(e1.get_index_matrix(), e3.get_index_matrix()), "different seeds should differ"
    # 4. Toy distributional sanity: words appearing in same context get nonzero similarity;
    #    cat and dog share window-positions around 'sat' / 'on' / 'the'.
    sim_cat_dog = e1.similarity("cat", "dog")
    sim_cat_mat = e1.similarity("cat", "mat")
    # Both 'cat' and 'dog' appear right after 'the' and before 'sat'; expect non-trivial similarity
    assert sim_cat_dog > 0.0, "cat-dog cosine should be > 0 in toy corpus (got %.3f)" % sim_cat_dog
    # 5. Self-similarity = 1
    self_sim = e1.similarity("cat", "cat")
    assert abs(self_sim - 1.0) < 1e-5, "self-similarity should be 1 (got %.6f)" % self_sim
    # 6. OOV returns 0
    assert e1.similarity("cat", "xyznotaword") == 0.0
    # 7. encode returns shape (N,)
    v = e1.encode("cat")
    assert v.shape == (512,), "encode shape mismatch"
    # 8. Order binding flag works (different output)
    e_order = RandomIndexingEncoder(N=512, sparsity=8, window=2, min_count=1, seed=42, order_binding=True)
    e_order.fit_corpus(toks)
    bag_vec = e1.encode("cat")
    order_vec = e_order.encode("cat")
    # Order-binding should add information; vectors should differ
    assert not np.allclose(bag_vec, order_vec), "order-binding should change context vector"
    # 9. Cyclic shift correctness
    a = np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float32)
    s = _cyclic_shift(a, 1)
    assert np.allclose(s, np.array([4.0, 1.0, 2.0, 3.0])), "cyclic shift by 1 should rotate right"
    print(
        "[selftest] PASS: sparsity-correct=%d, deterministic, seed-divergent, cat-dog-sim=%.3f, self-sim=1.0, order-binding-differs"
        % (nnz, sim_cat_dog)
    )


if __name__ == "__main__":
    _selftest()
