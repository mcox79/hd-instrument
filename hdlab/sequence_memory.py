"""Sequence-binding primitive: offline-Hebbian-bound ordered pair store.

Architecture validated by `exp_c3_compressed_sequence_replay_v1` cell-land
2026-06-22 (commit a27939c5; HARD_PASS at every depth [1,3,5,7,10] on full
config K=20 N_DIM=4096; delta=1.0, order_delta=1.0, W_unchanged_by_sleep
invariant True at every arm; n_llm=0). Composes with `Codebook` cleanup +
`HebbianAssociations` (the W matrix); orthogonal to both (the S matrix is
the substrate's sequence-binding primitive, NOT a content store and NOT a
co-occurrence weight table).

Honest-scope (META atom proposal 2026-06-22): the substrate is software so
there is no Hebbian STDP temporal window; the architectural win is the
SEPARATE S matrix + offline ordered-pair writes + W-vs-S separation, NOT
the temporal-compression schedule from the biological motivation (Wilson &
McNaughton 1994 SWR compression). Arm D (ONLINE_NO_GAP) reproduces Arm B
(COMPRESSED) exactly because software writes at arbitrary precision
regardless of pair-spacing. Use `bind_sequence` for the standard
architectural primitive; the `sleep_compression_ratio` parameter is a
cosmetic hyperparameter retained for biological-framing consistency only.
"""

from __future__ import annotations

import time

import torch

from . import tracing


class SequenceMatrix:
    """Ordered-pair sequence-binding store; the substrate's sequence primitive.

    Holds an N_DIM x N_DIM matrix S such that S @ k_prev approximates k_next
    for any ordered pair (k_prev, k_next) bound via `bind_pair`. Sequences
    are bound as adjacent pairs.

    Crucially: writes ONLY mutate S, NEVER the W matrix used by
    HebbianAssociations / Codebook content storage. The W-vs-S separation is
    the architectural invariant verified by c3 cell at every arm.
    """

    def __init__(self, n_dim: int, dtype: torch.dtype = torch.float32) -> None:
        self.n_dim = n_dim
        self.dtype = dtype
        self.S = torch.zeros(n_dim, n_dim, dtype=dtype)
        self._n_pairs_bound = 0

    def __len__(self) -> int:
        return self._n_pairs_bound

    def bind_pair(self, k_prev: torch.Tensor, k_next: torch.Tensor) -> None:
        """Hebbian outer-product write of one ordered pair: S += k_next ⊗ k_prev."""
        t0 = time.perf_counter_ns()
        if k_prev.shape != (self.n_dim,) or k_next.shape != (self.n_dim,):
            raise ValueError(
                f"Expected key shape ({self.n_dim},); got prev={tuple(k_prev.shape)}, next={tuple(k_next.shape)}"
            )
        self.S.add_(torch.outer(k_next.to(self.dtype), k_prev.to(self.dtype)))
        self._n_pairs_bound += 1
        tracing.emit(
            "sequence_memory.bind_pair",
            {"n_dim": self.n_dim},
            {"n_pairs": self._n_pairs_bound},
            elapsed_ns=time.perf_counter_ns() - t0,
        )

    def bind_sequence(self, keys: torch.Tensor) -> None:
        """Bind all adjacent ordered pairs in keys (shape [T, n_dim]).

        Equivalent to calling bind_pair for each (keys[t-1], keys[t]) with t in
        [1, T). The offline-pass-vs-online distinction is moot in software (no
        Hebbian window); kept as a single bind primitive.
        """
        if keys.ndim != 2 or keys.shape[1] != self.n_dim:
            raise ValueError(f"Expected keys shape [T, {self.n_dim}]; got {tuple(keys.shape)}")
        for t in range(1, keys.shape[0]):
            self.bind_pair(keys[t - 1], keys[t])

    def predict_next(self, k_prev: torch.Tensor) -> torch.Tensor:
        """Retrieve predicted next key as S @ k_prev. Substrate-only; no LLM call."""
        if k_prev.shape != (self.n_dim,):
            raise ValueError(f"Expected query shape ({self.n_dim},); got {tuple(k_prev.shape)}")
        return self.S @ k_prev.to(self.dtype)

    def chain_predict(self, k_start: torch.Tensor, depth: int, codebook=None) -> list[torch.Tensor]:
        """Iterate predict_next `depth` times. Optional codebook for per-step cleanup.

        With codebook cleanup at each step, the chain is bounded by the codebook's
        nearest-neighbor lookup (the substrate's content-addressing primitive).
        Without cleanup, the raw S-matrix outputs may drift toward the column-sum
        attractor — codebook cleanup is the architectural complement.
        """
        preds: list[torch.Tensor] = []
        k = k_start
        for _ in range(depth):
            k = self.predict_next(k)
            if codebook is not None and len(codebook) > 0:
                stacked = torch.stack(codebook._vectors)
                from . import atoms
                sims = atoms.similarity(k, stacked)
                best = int(sims.argmax())
                k = codebook._vectors[best].clone()
            preds.append(k)
        return preds

    def matrix_norm(self) -> float:
        """Frobenius norm of S; a diagnostic for binding-volume / saturation tracking."""
        return float(torch.linalg.norm(self.S))

    def reset(self) -> None:
        """Zero out S (use sparingly; sequence-binding is a long-lived store)."""
        self.S.zero_()
        self._n_pairs_bound = 0
