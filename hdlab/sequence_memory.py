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
        # S_back: REVERSE-temporal-order pair store; populated by bind_pair_reverse.
        # Forward S holds (k_prev -> k_next); S_back holds (k_next -> k_prev) so
        # `predict_prev(k_next) = S_back @ k_next` recovers the temporal predecessor.
        # Brain grounding: hippocampal reverse-replay during sharp-wave ripples
        # (Foster-Wilson 2006; Diba-Buzsaki 2007); cell-author M5 drill 2026-06-27.
        # Honest scope: forward + reverse stores are SEPARATE matrices; reverse is
        # NOT W.T but its own Hebbian-bound ordered-pair store. (The W.T proxy used
        # by META_M7 bidirectional cell is for an associative Hebbian W, not for
        # a sequence-binding S.)
        self.S_back = torch.zeros(n_dim, n_dim, dtype=dtype)
        self._n_pairs_bound = 0
        self._n_pairs_bound_reverse = 0

    def __len__(self) -> int:
        return self._n_pairs_bound

    def bind_pair(self, k_prev: torch.Tensor, k_next: torch.Tensor) -> None:
        """Hebbian outer-product write of one ordered pair: S += k_next outer k_prev."""
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

    def bind_pair_reverse(self, k_prev: torch.Tensor, k_next: torch.Tensor) -> None:
        """Reverse-temporal-order Hebbian write: S_back += k_prev outer k_next.

        Symmetric to bind_pair but writes into S_back so that S_back @ k_next
        approximates k_prev (i.e. retrieving the temporal predecessor of k_next).
        Caller passes pairs in the SAME (k_prev, k_next) order used by bind_pair;
        the reverse-binding orientation is internal to this method.

        Brain analog: reverse-replay during SWRs propagates reward signal back to
        upstream states (TD credit assignment; Foster-Wilson 2006). Substrate
        implementation: a SEPARATE matrix, not W.T, so forward and reverse stores
        decouple and can be selectively gated (e.g. reward-gated reverse-replay
        per Ambrose-Pfeiffer-Foster 2016).
        """
        t0 = time.perf_counter_ns()
        if k_prev.shape != (self.n_dim,) or k_next.shape != (self.n_dim,):
            raise ValueError(
                f"Expected key shape ({self.n_dim},); got prev={tuple(k_prev.shape)}, next={tuple(k_next.shape)}"
            )
        self.S_back.add_(torch.outer(k_prev.to(self.dtype), k_next.to(self.dtype)))
        self._n_pairs_bound_reverse += 1
        tracing.emit(
            "sequence_memory.bind_pair_reverse",
            {"n_dim": self.n_dim},
            {"n_pairs_reverse": self._n_pairs_bound_reverse},
            elapsed_ns=time.perf_counter_ns() - t0,
        )

    def predict_prev(self, k_next: torch.Tensor) -> torch.Tensor:
        """Retrieve predicted PREVIOUS key as S_back @ k_next. Substrate-only; no LLM call.

        Inverse of predict_next; requires bind_pair_reverse to have been called for
        the trajectory. Returns the raw (uncleaned) reverse prediction; the caller
        applies codebook cleanup if needed (same pattern as predict_next).
        """
        if k_next.shape != (self.n_dim,):
            raise ValueError(f"Expected query shape ({self.n_dim},); got {tuple(k_next.shape)}")
        return self.S_back @ k_next.to(self.dtype)

    def bind_sequence_reverse(self, keys: torch.Tensor) -> None:
        """Bind all adjacent ordered pairs in keys into S_back (reverse-direction).

        Equivalent to calling bind_pair_reverse for each (keys[t-1], keys[t]) with
        t in [1, T). Convenience for ingesting a full trajectory into the reverse
        store in one call.
        """
        if keys.ndim != 2 or keys.shape[1] != self.n_dim:
            raise ValueError(f"Expected keys shape [T, {self.n_dim}]; got {tuple(keys.shape)}")
        for t in range(1, keys.shape[0]):
            self.bind_pair_reverse(keys[t - 1], keys[t])

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
        """Zero out S AND S_back (use sparingly; sequence-binding is a long-lived store)."""
        self.S.zero_()
        self.S_back.zero_()
        self._n_pairs_bound = 0
        self._n_pairs_bound_reverse = 0
