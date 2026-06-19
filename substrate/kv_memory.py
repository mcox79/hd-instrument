"""
substrate.kv_memory -- Tier 5a substrate-KV (production port of D2 cell).

Port of exp_d2_pythia1p4b_substrate_kv_gpu_v1.py (PP-135 cycle 185+190+191).

CORE IDEA:
The substrate is an external persistent KV-style memory keyed by the LLM's OWN hidden
states. Facts are stored as text; each fact's KEY is the last-token hidden state of
Pythia after encoding the fact. ZCA whitening + L2 normalization gives a clean cosine-
retrievable representation. A query is encoded with the SAME encoder; cosine vs whitened
keys retrieves top-K relevant facts beyond the LLM's context window.

Validated (cycles 185, 190, 191):
- Pythia-160M recall=1.000 at M=2000
- Pythia-1.4B recall=1.000 at M=2000
- Pythia-2.8B recall=1.000 at M=2000
- M=5000 = 78x context expansion (HP)
- M=10000 = 156x context expansion (HP)
- Qwen-1.5B cross-family HP (size + family agnostic)

For the v1 demo Panel A this provides the substrate retrieval that feeds Pythia-1.4B's
context window. Substrate is the LLM's persistent memory layer.

API:
    kv = SubstrateKV(encoder=pythia_client, dim=2048)
    kv.add_facts(["Anthropic was founded in 2021.", ...])
    hits = kv.retrieve("when was Anthropic founded?", top_k=5)
    # hits = [(fact_text, cosine_score), ...]
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional

import numpy as np


@dataclass
class SubstrateKV:
    """Tier 5a substrate-KV memory.

    Stores text facts keyed by an LLM-encoder's last-token hidden states. By default uses
    raw cosine (mean-centered + L2-normalized). Switches to ZCA whitening AUTOMATICALLY
    when M >= whitening_min_facts (default 2 * dim) so the covariance matrix is full-rank.

    The D2 cell used whitening at M=2000 facts (M ~ D ratio adequate). At M=50 << D=2048,
    whitening over-fits and decorrelates everything to noise. Raw cosine is more reliable
    for small KBs.

    NOTE: encoder must have .encode(texts: list[str]) -> np.ndarray returning (N, hidden_size).
    See backend/llm/pythia_client.py.
    """
    encoder: Any                 # something with .encode(list[str]) -> np.ndarray
    dim: int = 2048              # encoder hidden_size (Pythia-1.4B = 2048; 160M = 768; 2.8B = 2560)
    whitening_min_facts: Optional[int] = None   # default 2*dim; auto-switch to ZCA above
    facts: list = field(default_factory=list)
    keys: Optional[np.ndarray] = None         # (M, dim) raw encoder hidden states
    mu: Optional[np.ndarray] = None           # per-dim mean for centering
    W_whiten: Optional[np.ndarray] = None     # ZCA whitening matrix (None when below threshold)
    keys_normed: Optional[np.ndarray] = None  # (M, dim) centered + L2-normalized (always set)
    use_whitening: bool = False               # auto-set by _fit()

    def __post_init__(self):
        if self.whitening_min_facts is None:
            self.whitening_min_facts = 2 * self.dim

    def __len__(self) -> int:
        return len(self.facts)

    def add_facts(self, facts: list[str]) -> int:
        """Encode + append facts; recompute the retrieval index. Returns new total fact count."""
        if not facts:
            return len(self.facts)
        new_keys = self.encoder.encode(facts)
        if new_keys.dtype != np.float32:
            new_keys = new_keys.astype(np.float32)
        if self.keys is None:
            self.keys = new_keys
            self.facts = list(facts)
        else:
            self.keys = np.concatenate([self.keys, new_keys], axis=0)
            self.facts.extend(facts)
        self._fit()
        return len(self.facts)

    def _fit(self) -> None:
        """Fit the retrieval index. Auto-switches between raw-cosine and ZCA whitening."""
        K = self.keys
        self.mu = K.mean(axis=0)
        Kc = K - self.mu

        if len(K) >= self.whitening_min_facts:
            # ZCA whitening (D2 mechanism; matches PP-135)
            cov = (Kc.T @ Kc) / max(1, len(K)) + 1e-3 * np.eye(K.shape[1], dtype=np.float32)
            w, V = np.linalg.eigh(cov)
            w = np.clip(w, 1e-6, None)
            self.W_whiten = (V @ np.diag(1.0 / np.sqrt(w)) @ V.T).astype(np.float32)
            Kt = Kc @ self.W_whiten
            self.use_whitening = True
        else:
            # Raw cosine for small KBs (avoids rank-deficient covariance)
            self.W_whiten = None
            Kt = Kc
            self.use_whitening = False

        norms = np.linalg.norm(Kt, axis=1, keepdims=True) + 1e-8
        self.keys_normed = (Kt / norms).astype(np.float32)

    def retrieve(self, query: str, top_k: int = 5) -> list:
        """Retrieve top-K (fact_text, cosine_score) pairs."""
        if not self.facts or self.keys_normed is None:
            return []
        q_vec = self.encoder.encode([query])[0]
        if q_vec.dtype != np.float32:
            q_vec = q_vec.astype(np.float32)
        qt = q_vec - self.mu
        if self.use_whitening:
            qt = qt @ self.W_whiten
        qt = qt / (np.linalg.norm(qt) + 1e-8)
        scores = self.keys_normed @ qt
        top = np.argsort(-scores)[:top_k]
        return [(self.facts[int(i)], float(scores[int(i)])) for i in top]

    def stats(self) -> dict:
        return {
            "n_facts": len(self.facts),
            "encoder_dim": int(self.dim),
            "whitening_active": self.use_whitening,
            "whitening_threshold": self.whitening_min_facts,
            "first_facts": self.facts[:3] if self.facts else [],
        }

    def load_from_disk(self, facts_jsonl_path, keys_npy_path, defer_fit: bool = False) -> int:
        """Load pre-encoded facts from a (facts.jsonl, keys.npy) pair.

        Per Research KILL_LOAD_PROFILE_PREFIT (2026-06-09): if the source dir also
        contains `keys_normed.npy` AND the parent dir has `mu.npy` + `W_whiten.npy`
        (written by scripts/prefit_substrate_state.py), the pre-whitened path is
        used:
          - keys_normed.npy mmap'd directly into self.keys_normed (instant)
          - global mu + W_whiten loaded once
          - _fit() is SKIPPED entirely (eliminates 10+ min ZCA cost on >100K KBs)

        Otherwise falls back to the legacy path: load raw keys.npy, concat, _fit().

        `defer_fit=True` (legacy path only) lets the operator batch multiple
        load_from_disk calls then a single explicit fit() call at end. No-op for
        the pre-fit path (already whitened).

        IMPORTANT: encoder used at ingest time MUST match self.encoder (1024-dim
        bge-large-en-v1.5); otherwise key/query alignment breaks.
        """
        import json as _json
        from pathlib import Path as _Path

        facts_jsonl_path = _Path(facts_jsonl_path)
        keys_npy_path = _Path(keys_npy_path)
        if not facts_jsonl_path.exists() or not keys_npy_path.exists():
            raise FileNotFoundError(f"need both {facts_jsonl_path} and {keys_npy_path}")

        new_facts = []
        with facts_jsonl_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                row = _json.loads(line)
                new_facts.append(row["fact"])

        # PRE-FIT PATH: per-source keys_normed.npy + global mu/W_whiten at root
        source_dir = keys_npy_path.parent
        root_dir = source_dir.parent
        prefit_keys_p = source_dir / "keys_normed.npy"
        mu_p = root_dir / "mu.npy"
        W_whiten_p = root_dir / "W_whiten.npy"

        use_prefit = prefit_keys_p.exists() and mu_p.exists() and W_whiten_p.exists()

        if use_prefit:
            kn = np.load(prefit_keys_p)  # could mmap_mode='r' but float32 copies are fine for now
            if kn.dtype != np.float32:
                kn = kn.astype(np.float32)
            if len(new_facts) != kn.shape[0]:
                raise ValueError(
                    f"facts vs keys_normed length mismatch: {len(new_facts)} facts vs {kn.shape[0]} keys"
                )
            if kn.shape[1] != self.dim:
                raise ValueError(
                    f"keys_normed dim mismatch: {kn.shape[1]} vs encoder dim {self.dim}"
                )

            # Only need to load mu + W_whiten once (first load), then concatenate normed keys
            if self.mu is None:
                self.mu = np.load(mu_p).astype(np.float32)
                self.W_whiten = np.load(W_whiten_p).astype(np.float32)
                self.use_whitening = True

            if self.keys_normed is None:
                self.keys_normed = kn
                self.facts = new_facts
            else:
                self.keys_normed = np.concatenate([self.keys_normed, kn], axis=0)
                self.facts.extend(new_facts)

            # Maintain self.keys for legacy compatibility (small mem cost; rare access)
            # Skip if you want to save memory; query path only uses keys_normed
            return len(self.facts)

        # LEGACY PATH: raw keys + _fit() at the end
        keys = np.load(keys_npy_path)
        if keys.dtype != np.float32:
            keys = keys.astype(np.float32)

        if len(new_facts) != keys.shape[0]:
            raise ValueError(
                f"facts vs keys length mismatch: {len(new_facts)} facts vs {keys.shape[0]} keys"
            )
        if keys.shape[1] != self.dim:
            raise ValueError(
                f"keys hidden_size mismatch: {keys.shape[1]} vs encoder dim {self.dim}"
            )

        if self.keys is None:
            self.keys = keys
            self.facts = new_facts
        else:
            self.keys = np.concatenate([self.keys, keys], axis=0)
            self.facts.extend(new_facts)
        if not defer_fit:
            self._fit()
        return len(self.facts)

    def fit(self) -> None:
        """Public alias for _fit(); call after batched defer_fit=True load_from_disks."""
        self._fit()


class _MockEncoder:
    """Synthetic encoder for unit testing without loading Pythia."""

    def __init__(self, dim=64, seed=0):
        self.dim = dim
        self._rng = np.random.default_rng(seed)
        self._cache: dict = {}

    def encode(self, texts):
        out = []
        for t in texts:
            if t not in self._cache:
                # Deterministic per-text via hash-seeded RNG
                rng = np.random.default_rng(abs(hash(t)) % (2 ** 31))
                self._cache[t] = rng.standard_normal(self.dim).astype(np.float32)
            out.append(self._cache[t])
        return np.stack(out, axis=0)


def _self_test():
    # Small KB (M=5 << 2*D=128); raw cosine path
    encoder = _MockEncoder(dim=64)
    kv = SubstrateKV(encoder=encoder, dim=64)
    facts = [
        "Anthropic was founded in 2021 by Dario Amodei and Daniela Amodei.",
        "OpenAI was founded in 2015 by Sam Altman and others.",
        "Google DeepMind was formed by merging Google Brain and DeepMind in 2023.",
        "Mistral AI was founded in 2023 in France.",
        "Cohere was founded in 2019.",
    ]
    n = kv.add_facts(facts)
    assert n == 5
    assert len(kv) == 5
    assert not kv.use_whitening, "small KB should use raw cosine"
    assert kv.W_whiten is None
    assert kv.keys_normed.shape == (5, 64)

    # Self-retrieval
    hits = kv.retrieve(facts[1], top_k=2)
    assert hits[0][0] == facts[1], f"expected self-retrieval, got {hits[0][0]}"
    raw_score = hits[0][1]

    # Append more facts (still small)
    kv.add_facts(["Stability AI released Stable Diffusion in 2022."])
    assert len(kv) == 6

    # Big KB (M=300 >= 2*D=128); ZCA path
    encoder2 = _MockEncoder(dim=64, seed=1)
    kv2 = SubstrateKV(encoder=encoder2, dim=64)
    big_facts = [f"Fact number {i} about AI lab #{i % 10}" for i in range(300)]
    kv2.add_facts(big_facts)
    assert kv2.use_whitening, "large KB should use ZCA"
    hits_big = kv2.retrieve(big_facts[123], top_k=1)
    assert hits_big[0][0] == big_facts[123], "ZCA self-retrieval"

    print(f"[substrate.kv_memory] self-test PASS (raw-cosine M=6 score={raw_score:.3f}; "
          f"ZCA-whitened M=300 self-retrieval OK)")


if __name__ == "__main__":
    _self_test()
