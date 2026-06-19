"""Minimal 4-layer char-level GRU baseline for Probe 11+ HP-band reference.

Intentionally TINY -- this is the "gradient-trained reference" the substrate-LM
gets compared against in HP/MIDDLE/HF bands. NOT a competitive baseline.

Target: trains in ~half the time of substrate-LM at smoke; well-tuned char-RNNs
are NOT this script's purpose. We use:
  - 4-layer GRU
  - small hidden size (default 64)
  - Adam optimizer at constant lr (no schedule)
  - ~1 epoch over the corpus (streaming, batch of consecutive chars)
"""
from __future__ import annotations

import math
import time
from typing import Dict, List, Optional, Sequence

import numpy as np


class GradientCharLM:
    """4-layer GRU char-LM, trained with Adam + cross-entropy.

    Tiny by design: hidden=64, batch=64 chars, ~1 streaming pass over the corpus.
    """

    def __init__(
        self,
        n_layers: int = 4,
        hidden: int = 64,
        seq_len: int = 64,
        batch_size: int = 32,
        lr: float = 5e-3,
        seed: int = 17,
        device: Optional[str] = None,
    ) -> None:
        import torch

        self.torch = torch
        self.n_layers = int(n_layers)
        self.hidden = int(hidden)
        self.seq_len = int(seq_len)
        self.batch_size = int(batch_size)
        self.lr = float(lr)
        self.seed = int(seed)
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        self.device = device
        torch.manual_seed(self.seed)
        self.vocab: List[str] = []
        self.ch_to_idx: Dict[str, int] = {}
        self.model: Optional["torch.nn.Module"] = None  # type: ignore[name-defined]
        self._fitted = False

    # ------------------------------------------------------------------
    # Build / fit
    # ------------------------------------------------------------------

    def _build(self, vocab_size: int) -> None:
        import torch
        import torch.nn as nn

        class _GRU(nn.Module):
            def __init__(self, V, H, L):
                super().__init__()
                self.emb = nn.Embedding(V, H)
                self.gru = nn.GRU(H, H, num_layers=L, batch_first=True)
                self.out = nn.Linear(H, V)

            def forward(self, x, h=None):
                e = self.emb(x)
                y, h = self.gru(e, h)
                return self.out(y), h

        self.model = _GRU(vocab_size, self.hidden, self.n_layers).to(self.device)

    def fit(
        self,
        corpus: str,
        n_chars_train: Optional[int] = None,
        char_vocab: Optional[set] = None,
        max_epochs: int = 1,
        verbose: bool = True,
    ) -> dict:
        import torch
        import torch.nn as nn

        if char_vocab is None:
            char_vocab = set(corpus)
        self.vocab = sorted(char_vocab)
        self.ch_to_idx = {ch: i for i, ch in enumerate(self.vocab)}
        V = len(self.vocab)

        self._build(V)
        assert self.model is not None
        opt = torch.optim.Adam(self.model.parameters(), lr=self.lr)
        crit = nn.CrossEntropyLoss()

        n_train = len(corpus) if n_chars_train is None else min(n_chars_train, len(corpus))
        # Convert corpus prefix to idx tensor on device.
        # Filter OOV chars (shouldn't happen if vocab was derived from corpus).
        idx_list = [self.ch_to_idx[c] for c in corpus[:n_train] if c in self.ch_to_idx]
        idx_arr = np.asarray(idx_list, dtype=np.int64)
        data = torch.from_numpy(idx_arr).to(self.device)
        total_chars = data.numel()

        # Streaming batches of (batch_size, seq_len) sequences sampled uniformly.
        rng = np.random.default_rng(self.seed)
        n_steps = max(1, total_chars // (self.batch_size * self.seq_len)) * max_epochs

        t0 = time.time()
        losses: List[float] = []
        self.model.train()
        for step in range(n_steps):
            # Sample starting indices.
            starts = rng.integers(0, max(1, total_chars - self.seq_len - 1),
                                  size=self.batch_size)
            x_batch = torch.stack(
                [data[s : s + self.seq_len] for s in starts], dim=0
            )
            y_batch = torch.stack(
                [data[s + 1 : s + self.seq_len + 1] for s in starts], dim=0
            )
            logits, _ = self.model(x_batch)
            loss = crit(logits.reshape(-1, V), y_batch.reshape(-1))
            opt.zero_grad()
            loss.backward()
            opt.step()
            losses.append(float(loss.item()))
            if verbose and (step % max(1, n_steps // 5) == 0 or step == n_steps - 1):
                print(
                    f"[GradientCharLM] step {step+1}/{n_steps} loss={loss.item():.4f}",
                    flush=True,
                )

        train_wall_s = time.time() - t0
        self._fitted = True
        return {
            "train_wall_s": float(train_wall_s),
            "n_steps": int(n_steps),
            "final_loss": float(losses[-1] if losses else float("inf")),
            "n_chars_train": int(total_chars),
        }

    # ------------------------------------------------------------------
    # Score
    # ------------------------------------------------------------------

    def score_bpc(self, corpus: str) -> dict:
        """BPC = (1/n) sum_t -log2 p(c_t | c_{<t})."""
        import torch
        import torch.nn.functional as F

        assert self._fitted and self.model is not None
        idx_list = [self.ch_to_idx.get(c, -1) for c in corpus]
        # Mask OOV.
        if all(i < 0 for i in idx_list):
            return {"bpc": float("inf"), "n_scored": 0, "uniform_bpc": 0.0}
        # Keep only positions where both context and target are in-vocab.
        n = len(idx_list)
        ctx_idxs = []
        tgt_idxs = []
        for t in range(1, n):
            if idx_list[t - 1] >= 0 and idx_list[t] >= 0:
                ctx_idxs.append(idx_list[t - 1])
                tgt_idxs.append(idx_list[t])
        if not ctx_idxs:
            return {"bpc": float("inf"), "n_scored": 0, "uniform_bpc": 0.0}

        self.model.eval()
        # Sequence-mode scoring: feed the full sequence in chunks.
        V = len(self.vocab)
        ent_sum = 0.0
        n_scored = 0
        chunk = 1024
        # Build a single long tensor of in-vocab chars (preserving order).
        in_vocab_seq = [i for i in idx_list if i >= 0]
        seq = torch.tensor(in_vocab_seq, dtype=torch.long, device=self.device)
        with torch.no_grad():
            for start in range(0, max(1, seq.numel() - 1), chunk):
                end = min(seq.numel() - 1, start + chunk)
                if end <= start:
                    break
                x = seq[start:end].unsqueeze(0)
                y_target = seq[start + 1 : end + 1]
                logits, _ = self.model(x)
                logp = F.log_softmax(logits.squeeze(0), dim=-1)  # (T, V)
                # Gather log-prob of true targets.
                lp = logp.gather(1, y_target.unsqueeze(1)).squeeze(1)  # (T,)
                # log2 = ln / ln(2)
                ent_sum += float((-lp / math.log(2.0)).sum().item())
                n_scored += int(lp.numel())

        bpc = ent_sum / max(n_scored, 1)
        uniform_bpc = float(np.log2(max(V, 1)))
        return {"bpc": float(bpc), "n_scored": int(n_scored), "uniform_bpc": uniform_bpc}


def _selftest() -> None:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from testbed.substrate_lm.data import wikitext2_char_corpus

    corpus = wikitext2_char_corpus(split="train", max_chars=4000)
    test = wikitext2_char_corpus(split="validation", max_chars=400)
    vocab = set(corpus) | set(test)
    lm = GradientCharLM(n_layers=2, hidden=32, seq_len=32, batch_size=16,
                        lr=5e-3, seed=7)
    info = lm.fit(corpus, char_vocab=vocab, max_epochs=1, verbose=False)
    score = lm.score_bpc(test)
    print(
        f"[GradientCharLM selftest] train_wall_s={info['train_wall_s']:.2f} "
        f"n_steps={info['n_steps']} bpc={score['bpc']:.3f} "
        f"uniform_bpc={score['uniform_bpc']:.3f} n_scored={score['n_scored']}",
        flush=True,
    )
    assert np.isfinite(score["bpc"]), "baseline BPC non-finite"
    print("[GradientCharLM selftest] PASS", flush=True)


if __name__ == "__main__":
    _selftest()
