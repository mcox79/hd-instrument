"""Substrate-native generation primitive — substrate emits sequences without LLM.

Operationalizes the g1_substrate_native_generation_v1 cell mechanism (MEASURED_MECHANISM
2026-06-22; commit 7083c38b atomize). Composes hdlab.sequence_memory.SequenceMatrix (the
S matrix from c3 CERT 586) with Langevin noise injection and codebook attractor cleanup
to autoregressively generate state sequences.

Honest scope per Skunkworks ruling: g1 LANDED MEASURED_MECHANISM (not chain-grade) because
the test regime (190 pair-writes at N_DIM=4096) operates BELOW substrate Hebbian capacity
~327 — substrate cannot fail by construction at that density. The mechanism-shape signal
IS valid (cleanup is load-bearing per the 4-arm discriminator; META atom in Store), and
substrate-native generation works in that regime. Chain-grade evidence above capacity
saturation requires g1b capacity-sweep follow-on (in flight).

Cleanup is the LOAD-BEARING complement: raw retrieval (S @ k_prev) drifts at depth;
Langevin without cleanup is WORSE (noise compounds); only S + Langevin + codebook NN
cleanup maintains trajectory coherence. The codebook attractor pulls noisy outputs back
to learned sequence states at each step.

Architecture:
  generate(start_key, depth, codebook, sigma) ->
    for t in 1..depth:
      k_t_predicted = S @ k_{t-1}                           # autoregressive S retrieval
      k_t_noisy     = k_t_predicted + sigma * randn         # Langevin noise injection
      k_t_clean     = argmax_e cos(k_t_noisy, codebook[e])  # attractor cleanup
      yield k_t_clean

Substrate-only-decode gate: zero LLM calls. W matrix (content store) is unchanged by
generation - only S matrix (sequence store) is read; codebook is read-only for cleanup.

Composes with hdlab.sequence_memory.SequenceMatrix (provides S) +
hdlab.kg_traversal.KGStore (provides E codebook + W matrix; W unchanged by generation) +
hdlab.char_trigram_encoder (zero-external-model input encoder; closes the bidirectional
substrate-native loop).
"""

from __future__ import annotations

import time

import torch

from . import tracing
from .sequence_memory import SequenceMatrix


def _normalize(v: torch.Tensor, eps: float = 1e-8) -> torch.Tensor:
    return v / (torch.linalg.norm(v) + eps)


class SubstrateGenerator:
    """Substrate-native autoregressive generator over a learned SequenceMatrix.

    Holds a reference to a SequenceMatrix (S) and a codebook of allowed states (the cleanup
    attractor basis). On each generation step, retrieves S @ k_prev, injects Langevin noise,
    and snaps to nearest codebook entry. Returns the snapped state (an entity-key from the
    substrate's vocabulary).
    """

    def __init__(self, S: SequenceMatrix, codebook: torch.Tensor, sigma_scale: float = 0.1) -> None:
        """
        Args:
            S: SequenceMatrix with ingested ordered-pair sequences (the substrate's S matrix)
            codebook: [N_codebook, n_dim] tensor of allowed cleanup states (e.g. KGStore.E
                      or any HD entity codebook)
            sigma_scale: Langevin noise scale as a fraction of mean(|S @ k|); 0.1 default
                         matches g1 cell pre-reg (Karuvally-Sejnowski-flavored injection level)
        """
        if S.n_dim != codebook.shape[1]:
            raise ValueError(f"S n_dim={S.n_dim} != codebook n_dim={codebook.shape[1]}")
        self.S = S
        self.codebook = codebook.to(torch.float32)
        self.sigma_scale = sigma_scale
        self.n_codebook = codebook.shape[0]
        self.n_dim = S.n_dim

    def _cleanup(self, k_noisy: torch.Tensor) -> tuple[int, torch.Tensor]:
        """Nearest codebook entry to k_noisy (cosine sim). Returns (idx, k_clean)."""
        k_norm = _normalize(k_noisy.to(torch.float32))
        cb_norms = torch.linalg.norm(self.codebook, dim=1, keepdim=True) + 1e-8
        cb_unit = self.codebook / cb_norms
        sims = cb_unit @ k_norm
        idx = int(sims.argmax())
        return idx, self.codebook[idx].clone()

    def generate_step(
        self,
        k_prev: torch.Tensor,
        rng: torch.Generator | None = None,
    ) -> tuple[int, torch.Tensor]:
        """One autoregressive step: returns (cleaned_codebook_idx, cleaned_key_vector)."""
        if k_prev.shape != (self.n_dim,):
            raise ValueError(f"Expected k_prev shape ({self.n_dim},); got {tuple(k_prev.shape)}")
        k_predicted = self.S.predict_next(k_prev)
        sigma = self.sigma_scale * float(torch.linalg.norm(k_predicted))
        if rng is not None:
            noise = torch.randn(self.n_dim, generator=rng) * sigma
        else:
            noise = torch.randn(self.n_dim) * sigma
        k_noisy = k_predicted + noise
        return self._cleanup(k_noisy)

    def generate(
        self,
        start_key: torch.Tensor,
        depth: int,
        rng: torch.Generator | None = None,
    ) -> list[int]:
        """Generate a sequence of `depth` codebook indices starting from start_key."""
        t0 = time.perf_counter_ns()
        k = start_key.to(torch.float32)
        path = []
        for _ in range(depth):
            idx, k = self.generate_step(k, rng=rng)
            path.append(idx)
        tracing.emit(
            "generation.generate",
            {"depth": depth, "n_codebook": self.n_codebook, "sigma_scale": self.sigma_scale},
            {"n_distinct": len(set(path))},
            elapsed_ns=time.perf_counter_ns() - t0,
        )
        return path

    def generate_with_names(
        self,
        start_key: torch.Tensor,
        depth: int,
        idx_to_name: list[str],
        rng: torch.Generator | None = None,
    ) -> list[str]:
        """Convenience: generate + map indices through idx_to_name."""
        if len(idx_to_name) != self.n_codebook:
            raise ValueError(f"idx_to_name len {len(idx_to_name)} != n_codebook {self.n_codebook}")
        path = self.generate(start_key, depth, rng=rng)
        return [idx_to_name[i] for i in path]

    def __repr__(self) -> str:
        return f"SubstrateGenerator(S=SequenceMatrix(n_dim={self.n_dim}, n_pairs={len(self.S)}), n_codebook={self.n_codebook}, sigma_scale={self.sigma_scale})"
