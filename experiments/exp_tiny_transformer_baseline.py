"""Tiny transformer baseline for Track 0.1 comparison.

Same corpus, same train/test split, same byte-level vocab as exp_pure_hebbian_charlm.
Trains a small decoder-only transformer with standard gradient descent and AdamW.
Reports test bits-per-character so we can directly compare against the Hebbian-VSA result.

Target: ~500K-1M parameters, wall-time budget capped (default 10 min), context window 32.
This is the "real ML baseline" ceiling for the kill-switch test.
"""

from __future__ import annotations

import json
import math
import time
from pathlib import Path

import torch
import torch.nn as nn
import torch.nn.functional as F




DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
SEED = 17
VOCAB_SIZE = 256
PAD_BYTE = 0
D_MODEL = 128
N_HEADS = 4
N_LAYERS = 4
CONTEXT = 32
BATCH = 64
LR = 3e-4
WD = 0.01
TIME_BUDGET_S = 600  # 10 minutes wall-clock cap


def _say(msg: str) -> None:
    print(msg, flush=True)


def load_corpus() -> bytes:
    repo = Path(__file__).resolve().parent.parent
    files = [
        repo / "PLAN.md",
        repo / "NEXT_PHASE.md",
        repo / "README.md",
        repo / "PROGRESS.md",
        repo / "RESULTS.md",
        repo / "CLAUDE.md",
    ]
    parts = []
    for f in files:
        if f.exists():
            parts.append(f.read_bytes())
            parts.append(b"\n\n")
    return b"".join(parts)


def train_test_split(corpus: bytes, train_frac: float = 0.8) -> tuple[bytes, bytes]:
    cut = int(len(corpus) * train_frac)
    return corpus[:cut], corpus[cut:]


class TinyTransformer(nn.Module):
    def __init__(self, vocab: int, d_model: int, n_heads: int, n_layers: int, max_len: int):
        super().__init__()
        self.embed = nn.Embedding(vocab, d_model)
        self.pos = nn.Embedding(max_len, d_model)
        layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=n_heads,
            dim_feedforward=4 * d_model,
            batch_first=True,
            activation="gelu",
            dropout=0.0,
        )
        self.encoder = nn.TransformerEncoder(layer, num_layers=n_layers)
        self.head = nn.Linear(d_model, vocab)
        self.max_len = max_len

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        T = x.shape[1]
        pos = torch.arange(T, device=x.device)
        h = self.embed(x) + self.pos(pos).unsqueeze(0)
        mask = torch.triu(torch.ones(T, T, device=x.device), diagonal=1).bool()
        h = self.encoder(h, mask=mask)
        return self.head(h)


def make_batches(data: bytes, context: int, batch: int, gen: torch.Generator) -> torch.Tensor:
    """Sample batch random contiguous chunks of length context+1 from data."""
    n = len(data)
    starts = torch.randint(0, n - context - 1, (batch,), generator=gen)
    chunks = torch.stack([torch.tensor(list(data[s : s + context + 1]), dtype=torch.long).to(DEVICE) for s in starts])
    return chunks


def evaluate_bpc(model: TinyTransformer, train_bytes: bytes, test_bytes: bytes, context: int) -> float:
    """Slide context-sized window over test; sum cross-entropy of true byte at each position.

    For positions near the start of test, prepend trailing bytes from train so the model always
    sees a full context window (no PAD bias).
    """
    model.eval()
    pre = train_bytes[-context:] if len(train_bytes) >= context else (bytes([PAD_BYTE]) * (context - len(train_bytes)) + train_bytes)
    stream = pre + test_bytes
    total_bits = 0.0
    n = 0
    with torch.no_grad():
        # Process in chunks for efficiency.
        chunk = 256
        for start in range(context, len(stream), chunk):
            end = min(start + chunk, len(stream))
            inputs = []
            targets = []
            for i in range(start, end):
                inputs.append(list(stream[i - context : i]))
                targets.append(stream[i])
            if not inputs:
                continue
            x = torch.tensor(inputs, dtype=torch.long)
            t = torch.tensor(targets, dtype=torch.long)
            logits = model(x)[:, -1, :]  # only need last position
            logp = F.log_softmax(logits, dim=-1)
            bits = -logp.gather(1, t.unsqueeze(1)).squeeze(1) / math.log(2)
            total_bits += float(bits.sum())
            n += t.numel()
    model.train()
    return total_bits / max(n, 1)


def main() -> None:
    _say("Loading corpus...")
    corpus = load_corpus()
    train, test = train_test_split(corpus, train_frac=0.8)
    _say(f"  Corpus: {len(corpus)} bytes; train={len(train)}, test={len(test)}")

    torch.manual_seed(SEED)
    gen = torch.Generator().manual_seed(SEED)

    model = TinyTransformer(VOCAB_SIZE, D_MODEL, N_HEADS, N_LAYERS, CONTEXT)
    n_params = sum(p.numel() for p in model.parameters())
    _say(f"  Model params: {n_params:,}  (d_model={D_MODEL}, layers={N_LAYERS}, heads={N_HEADS}, ctx={CONTEXT})")

    opt = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=WD)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=1000)

    _say(f"\nTraining (wall-time budget {TIME_BUDGET_S}s)...")
    t_start = time.perf_counter()
    step = 0
    best_test_bpc = float("inf")
    history: list[dict] = []
    eval_every_s = 30
    next_eval = time.perf_counter() + eval_every_s

    model.train()
    while True:
        elapsed = time.perf_counter() - t_start
        if elapsed > TIME_BUDGET_S:
            break

        batch = make_batches(train, CONTEXT, BATCH, gen)
        x = batch[:, :-1]
        y = batch[:, 1:]
        logits = model(x)
        loss = F.cross_entropy(logits.reshape(-1, VOCAB_SIZE), y.reshape(-1))
        opt.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        sched.step()
        step += 1

        if time.perf_counter() >= next_eval:
            test_bpc = evaluate_bpc(model, train, test, CONTEXT)
            train_loss_bpc = float(loss) / math.log(2)
            history.append({
                "step": step,
                "elapsed_s": elapsed,
                "train_loss_bpc": train_loss_bpc,
                "test_bpc": test_bpc,
            })
            best_test_bpc = min(best_test_bpc, test_bpc)
            _say(
                f"  step={step:5d}  elapsed={elapsed:5.1f}s  "
                f"train_loss_bpc={train_loss_bpc:.3f}  test_bpc={test_bpc:.3f}  "
                f"best={best_test_bpc:.3f}"
            )
            next_eval = time.perf_counter() + eval_every_s

    # Final evaluation.
    final_test_bpc = evaluate_bpc(model, train, test, CONTEXT)
    best_test_bpc = min(best_test_bpc, final_test_bpc)

    _say(f"\nFinal test bits/char: {final_test_bpc:.4f}")
    _say(f"Best test bits/char during training: {best_test_bpc:.4f}")
    _say(f"Total wall time: {time.perf_counter() - t_start:.1f}s")
    _say(f"Total training steps: {step}")

    # Compare against pre-loaded Hebbian-VSA result and classical baselines.
    hebbian_best = 3.10  # from exp_pure_hebbian_charlm metrics.json, best config
    _say(f"\nComparison (test bits/char on identical split):")
    _say(f"  Unigram:                 5.7383")
    _say(f"  2-gram (best classical): 4.9047")
    _say(f"  Hebbian-VSA (best):      {hebbian_best:.4f}")
    _say(f"  Tiny transformer (best): {best_test_bpc:.4f}")

    if best_test_bpc < hebbian_best - 1.0:
        verdict = "TRANSFORMER CLEARLY BEATS HEBBIAN-VSA"
    elif best_test_bpc < hebbian_best - 0.3:
        verdict = "Transformer moderately better"
    elif best_test_bpc < hebbian_best + 0.3:
        verdict = "Roughly tied"
    else:
        verdict = "Hebbian-VSA competitive or better (surprising)"
    _say(f"\nVerdict: {verdict}")

    out = {
        "n_params": n_params,
        "context": CONTEXT,
        "d_model": D_MODEL,
        "n_layers": N_LAYERS,
        "n_heads": N_HEADS,
        "lr": LR,
        "time_budget_s": TIME_BUDGET_S,
        "total_steps": step,
        "final_test_bpc": final_test_bpc,
        "best_test_bpc": best_test_bpc,
        "history": history,
        "comparison": {
            "unigram": 5.7383,
            "two_gram": 4.9047,
            "hebbian_vsa_best": hebbian_best,
            "tiny_transformer_best": best_test_bpc,
        },
        "verdict": verdict,
        "headline": (
            f"Tiny transformer ({n_params/1e6:.2f}M params, ctx={CONTEXT}) "
            f"best test bpc = {best_test_bpc:.3f} vs Hebbian-VSA = {hebbian_best:.3f}"
        ),
    }

    out_path = Path(__file__).resolve().parent.parent / "data" / "exp_tiny_transformer_baseline"
    out_path.mkdir(parents=True, exist_ok=True)
    (out_path / "metrics.json").write_text(json.dumps(out, indent=2, default=str))
    _say(f"\nWrote {out_path / 'metrics.json'}")


if __name__ == "__main__":
    main()
