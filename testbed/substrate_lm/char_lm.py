"""SubstrateCharLM -- 4-primitive substrate-native character language model.

Streaming bigram-style character LM trained ENTIRELY through the substrate's
4-primitive core (no gradient descent, no backprop, no optimizer).

Architecture:
  - Each character is encoded to a bipolar code in {-1, +1}^N via a fixed
    hashed-projection per-char codebook (deterministic given seed).
  - "Context" code at position t = code(char_{t-1}). (Bigram context; the
    simplest architecturally-sound choice -- no positional encoding required,
    no need for a separate query/key projection.)
  - Training: for each (context_char, next_char) pair, write the joint pattern
    (context XOR next, via bipolar product) into layer-0 substrate. Streaming
    Hopfield. When a positive (context, next) pair is observed, sample a
    random in-batch negative and apply anti-Hebbian contrastive on layer-1.
    Higher layers (2, 3) consume the output of stacked retrieval at the
    previous layer (their write rule re-encodes the retrieved representation).
  - Inference: given context, forward through stack; for predicted bipolar
    code, score every char-code in the vocab by cosine similarity; softmax
    cosine scores -> probability distribution over next chars; BPC = mean
    -log2(p(true_next)).

NO gradient descent at ANY layer.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from testbed.substrate_lm.primitives import (  # noqa: E402
    StackedSubstrate,
    anti_hebbian_contrastive_update,
    hebbian_write,
    hierarchical_recurrent_retrieve,
    primitive_health_report,
    ALPHA_C_HOPFIELD,
)


def _bipolar_hash_codebook(
    vocab: Sequence[str], N: int, seed: int
) -> Dict[str, np.ndarray]:
    """Deterministic bipolar codebook: stable random {-1,+1}^N per character."""
    rng = np.random.default_rng(seed)
    cb: Dict[str, np.ndarray] = {}
    for ch in vocab:
        # Per-char rng for reproducibility independent of vocab ordering.
        local = np.random.default_rng(rng.integers(0, 2**31 - 1))
        cb[ch] = local.choice([-1.0, 1.0], size=N).astype(np.float32)
    return cb


def _bipolar_bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """VSA bind via element-wise product (Plate/Kanerva style); bipolar-preserving."""
    return (a * b).astype(np.float32)


class SubstrateCharLM:
    """4-primitive substrate-native character LM.

    Args:
        n_layers:          Number of stacked substrate layers (default 4).
        N:                 Substrate dimensionality (default 2048).
        alpha_max:         Per-layer alpha cap (default 0.10 < 0.138 = alpha_c).
        n_steps_per_layer: Recurrent retrieval steps per layer (default 3).
        seed:              RNG seed (codebook + contrastive negative sampling).
    """

    def __init__(
        self,
        n_layers: int = 4,
        N: int = 2048,
        alpha_max: float = 0.10,
        n_steps_per_layer: int = 3,
        seed: int = 17,
    ) -> None:
        self.n_layers = int(n_layers)
        self.N = int(N)
        self.alpha_max = float(alpha_max)
        self.n_steps_per_layer = int(n_steps_per_layer)
        self.seed = int(seed)
        self._rng = np.random.default_rng(self.seed)
        self.stack = StackedSubstrate(
            n_layers=self.n_layers,
            N=self.N,
            alpha_max=self.alpha_max,
            n_steps_per_layer=self.n_steps_per_layer,
        )
        # Codebook + vocab built at fit-time.
        self.vocab: List[str] = []
        self.codebook: Dict[str, np.ndarray] = {}
        # Code matrix for fast scoring: (V, N) float32, row k = code(vocab[k]).
        self._code_matrix: Optional[np.ndarray] = None
        # Health snapshots collected during fit (for the HP gate).
        self.health_snapshots: List[dict] = []
        # Number of (context, next) writes consumed.
        self.n_train_pairs: int = 0
        self._fitted = False

    # ------------------------------------------------------------------
    # Codebook
    # ------------------------------------------------------------------

    def _build_codebook(self, vocab_set: set) -> None:
        self.vocab = sorted(vocab_set)
        self.codebook = _bipolar_hash_codebook(
            self.vocab, self.N, seed=self.seed + 101
        )
        self._code_matrix = np.stack(
            [self.codebook[ch] for ch in self.vocab], axis=0
        ).astype(np.float32)

    def _ctx_code(self, ch: str) -> np.ndarray:
        """Bipolar context code for the most recent character (bigram context)."""
        # Unknown character: return the bipolar code of a stable proxy (' ' if
        # present, else first vocab entry).
        if ch in self.codebook:
            return self.codebook[ch]
        if " " in self.codebook:
            return self.codebook[" "]
        return self.codebook[self.vocab[0]]

    # ------------------------------------------------------------------
    # Fit (streaming Hebbian + contrastive)
    # ------------------------------------------------------------------

    def fit(
        self,
        corpus: str,
        n_chars_train: Optional[int] = None,
        char_vocab: Optional[set] = None,
        health_every: int = 500,
        verbose: bool = True,
    ) -> dict:
        """Stream-train the substrate over the (bigram) char corpus.

        Stops writing as soon as ANY layer reaches alpha_max (Error-Correction-Chain).

        Returns a dict with timing + final alpha-per-layer + health snapshots.
        """
        if char_vocab is None:
            char_vocab = set(corpus)
        if " " not in char_vocab:
            char_vocab = set(char_vocab) | {" "}
        self._build_codebook(char_vocab)

        n_train = len(corpus) if n_chars_train is None else min(n_chars_train, len(corpus))
        # We can only learn bigrams up to n_train - 1.
        n_pairs_max = max(0, n_train - 1)

        if verbose:
            print(
                f"[SubstrateCharLM.fit] n_layers={self.n_layers} N={self.N} "
                f"alpha_max={self.alpha_max} n_steps={self.n_steps_per_layer} "
                f"vocab={len(self.vocab)} pairs_target={n_pairs_max}",
                flush=True,
            )

        # Pre-build vocab-indexed code matrix for negative sampling.
        vocab_codes = self._code_matrix  # (V, N)
        assert vocab_codes is not None
        V = vocab_codes.shape[0]

        import time
        t0 = time.time()
        n_consumed = 0
        n_pos = 0
        n_neg = 0
        for i in range(n_pairs_max):
            if self.stack.any_layer_full():
                if verbose:
                    print(
                        f"  alpha_max reached after {n_consumed} pairs "
                        f"(alphas={['%.3f' % a for a in self.stack.alphas()]}); "
                        f"stopping writes.",
                        flush=True,
                    )
                break
            ctx_ch = corpus[i]
            nxt_ch = corpus[i + 1]
            ctx_code = self._ctx_code(ctx_ch)
            nxt_code = self._ctx_code(nxt_ch)

            # Joint bipolar pattern: bind context with next-char.
            joint = _bipolar_bind(ctx_code, nxt_code)

            # ----- Layer 0: Hopfield-write the joint pattern (Primitive 1).
            if not self.stack.layer_full(0):
                self.stack.write_hebbian(0, joint)
                n_pos += 1

            # ----- Layer 1: anti-Hebbian contrastive (Primitive 2).
            # Positive pair: (ctx, nxt). Negative pair: (ctx, random-other-char).
            if not self.stack.layer_full(1) and V > 1:
                neg_idx = int(self._rng.integers(0, V))
                # Ensure negative isn't the same as the true next character.
                while self.vocab[neg_idx] == nxt_ch:
                    neg_idx = int(self._rng.integers(0, V))
                neg_code = vocab_codes[neg_idx]
                self.stack.write_contrastive(
                    layer=1,
                    xi_pos_a=ctx_code,
                    xi_pos_b=nxt_code,
                    xi_neg_a=ctx_code,
                    xi_neg_b=neg_code,
                    lr=1.0,
                )
                n_neg += 1

            # ----- Layers 2+ : write the joint pattern but routed THROUGH the
            # stack's earlier layers (so higher layers store distilled/cleaned
            # representations of the same fact). This is the "stacked
            # composition" usage of Primitives 3+4.
            if self.n_layers >= 3:
                # Pass the joint through layer 0 + layer 1, store at layer 2.
                if not self.stack.layer_full(2):
                    h = hierarchical_recurrent_retrieve(
                        self.stack.Ws[0], joint, n_steps=self.n_steps_per_layer
                    )
                    h = hierarchical_recurrent_retrieve(
                        self.stack.Ws[1], h, n_steps=self.n_steps_per_layer
                    )
                    self.stack.write_hebbian(2, h)
            if self.n_layers >= 4:
                if not self.stack.layer_full(3):
                    # Use the layer-2 retrieval as the layer-3 stored pattern.
                    h = hierarchical_recurrent_retrieve(
                        self.stack.Ws[0], joint, n_steps=self.n_steps_per_layer
                    )
                    h = hierarchical_recurrent_retrieve(
                        self.stack.Ws[1], h, n_steps=self.n_steps_per_layer
                    )
                    h = hierarchical_recurrent_retrieve(
                        self.stack.Ws[2], h, n_steps=self.n_steps_per_layer
                    )
                    self.stack.write_hebbian(3, h)

            n_consumed += 1
            if health_every > 0 and (n_consumed % health_every == 0):
                snap = primitive_health_report(self.stack)
                snap["pairs_consumed"] = n_consumed
                self.health_snapshots.append(snap)
                if verbose:
                    print(
                        f"  pair {n_consumed}/{n_pairs_max} "
                        f"alphas={['%.3f' % a for a in self.stack.alphas()]} "
                        f"any_collapse={snap['any_primitive_collapse']}",
                        flush=True,
                    )

        train_wall_s = time.time() - t0
        self.n_train_pairs = n_consumed
        self._fitted = True
        # Final health snapshot.
        final_health = primitive_health_report(self.stack)
        final_health["pairs_consumed"] = n_consumed
        self.health_snapshots.append(final_health)

        if verbose:
            print(
                f"[SubstrateCharLM.fit] done: {n_consumed} pairs in "
                f"{train_wall_s:.2f}s; max_alpha={self.stack.max_alpha():.3f}; "
                f"any_collapse={final_health['any_primitive_collapse']}",
                flush=True,
            )

        return {
            "train_wall_s": float(train_wall_s),
            "n_train_pairs": int(n_consumed),
            "n_pos_pairs": int(n_pos),
            "n_neg_pairs": int(n_neg),
            "final_alphas": self.stack.alphas(),
            "any_primitive_collapse": bool(final_health["any_primitive_collapse"]),
            "n_health_snapshots": len(self.health_snapshots),
        }

    # ------------------------------------------------------------------
    # Inference / scoring
    # ------------------------------------------------------------------

    def _predict_logits(self, ctx_ch: str) -> np.ndarray:
        """Return (V,) log-probability-proportional scores over the vocab."""
        assert self._fitted and self._code_matrix is not None
        ctx_code = self._ctx_code(ctx_ch)
        # Retrieve via stacked recurrent retrieval.
        retrieved = self.stack.forward(ctx_code)
        # The joint stored pattern was bind(ctx, next) = ctx * next, so to
        # recover next we unbind: next ~= ctx * retrieved (bipolar product is
        # self-inverse). Score each vocab char by its cosine with the unbound
        # estimate.
        next_est = (ctx_code * retrieved).astype(np.float32)
        # Cosine scores against every vocab code.
        # vocab_codes: (V, N); next_est: (N,). Both bipolar so norm = sqrt(N).
        dots = self._code_matrix @ next_est  # (V,)
        norms = np.linalg.norm(self._code_matrix, axis=1) * (
            np.linalg.norm(next_est) + 1e-30
        )
        cos = dots / (norms + 1e-30)
        return cos.astype(np.float32)

    def predict_proba(self, ctx_ch: str, temperature: float = 1.0) -> np.ndarray:
        """Soft-max over cosine scores -> probability over next-char vocab."""
        logits = self._predict_logits(ctx_ch)
        # Scale by temperature; subtract max for numerical stability.
        z = (logits / max(temperature, 1e-6)).astype(np.float64)
        z = z - np.max(z)
        ez = np.exp(z)
        p = ez / max(np.sum(ez), 1e-30)
        return p.astype(np.float32)

    def score_bpc(self, corpus: str, temperature: float = 1.0) -> dict:
        """Compute bits-per-character on `corpus` (held-out test).

        BPC = mean over positions t in [1, len-1] of -log2(p(corpus[t] | corpus[t-1])).
        Lower is better. Uniform-vocab baseline = log2(|vocab|).
        """
        assert self._fitted
        if len(corpus) < 2:
            return {"bpc": float("inf"), "n_scored": 0, "uniform_bpc": 0.0}
        # Cache vocab idx
        ch_to_idx = {ch: i for i, ch in enumerate(self.vocab)}
        log2 = np.log2
        ent_sum = 0.0
        n_scored = 0
        for t in range(1, len(corpus)):
            ctx_ch = corpus[t - 1]
            nxt_ch = corpus[t]
            if nxt_ch not in ch_to_idx:
                continue  # skip OOV positions (synthetic vs HF mismatch)
            p = self.predict_proba(ctx_ch, temperature=temperature)
            p_nxt = float(max(p[ch_to_idx[nxt_ch]], 1e-12))
            ent_sum += -float(log2(p_nxt))
            n_scored += 1
        bpc = ent_sum / max(n_scored, 1)
        uniform_bpc = float(np.log2(max(len(self.vocab), 1)))
        return {"bpc": float(bpc), "n_scored": int(n_scored), "uniform_bpc": uniform_bpc}

    # ------------------------------------------------------------------
    # Health
    # ------------------------------------------------------------------

    def primitive_health(self) -> dict:
        return primitive_health_report(self.stack)


# ----------------------------------------------------------------------
# Self-test (smoke-grade end-to-end pipeline)
# ----------------------------------------------------------------------

def _selftest() -> None:
    """End-to-end mini-pipeline at N=128 to verify train + score."""
    from testbed.substrate_lm.data import wikitext2_char_corpus

    corpus = wikitext2_char_corpus(split="train", max_chars=2000)
    test = wikitext2_char_corpus(split="validation", max_chars=400)
    vocab = set(corpus) | set(test)

    lm = SubstrateCharLM(n_layers=2, N=128, alpha_max=0.10, n_steps_per_layer=3, seed=7)
    info = lm.fit(corpus, char_vocab=vocab, verbose=False)
    assert info["n_train_pairs"] > 0, "fit did not consume any pairs"

    score = lm.score_bpc(test)
    print(
        f"[SubstrateCharLM selftest] train_pairs={info['n_train_pairs']} "
        f"train_wall_s={info['train_wall_s']:.2f} bpc={score['bpc']:.3f} "
        f"uniform_bpc={score['uniform_bpc']:.3f} n_scored={score['n_scored']} "
        f"alphas={['%.3f' % a for a in info['final_alphas']]} "
        f"collapse={info['any_primitive_collapse']}",
        flush=True,
    )
    # BPC should be finite and at least not infinite.
    assert np.isfinite(score["bpc"]), f"BPC is non-finite: {score['bpc']}"
    # No primitive collapse.
    assert not info["any_primitive_collapse"], "primitive collapsed in selftest"
    print("[SubstrateCharLM selftest] PASS", flush=True)


if __name__ == "__main__":
    _selftest()
