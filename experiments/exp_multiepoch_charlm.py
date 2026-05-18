"""Multi-epoch Hebbian: does iterating over the training corpus help?

The signal-profiling experiment showed W's argmax accuracy is 54.6% — meaning W
points at the correct byte just over half the time. The remaining 0.45-bit gap
to the transformer ceiling is mostly here, NOT in the bundle or the cleanup.

Hypothesis: single-pass Hebbian gives W only one chance to refine each
association. Multi-epoch lets W iterate without being backprop. The brain
replays experiences during sleep; local learning rules can iterate.

This experiment runs N=1024 baseline (K=4, arousal=0.3, beta=8) for varying
epochs and reports test bits/char + W's argmax accuracy at each checkpoint.
"""

from __future__ import annotations

import json
import math
import time
from collections import Counter
from pathlib import Path

import torch

from hdlab import atoms, binding, tracing




DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
SEED = 17
N_SUBSTRATE = 1024
VOCAB_SIZE = 256
PAD_BYTE = 0
K = 4
AROUSAL = 0.3
BETA = 8.0
BATCH_SIZE = 64

# Checkpoint after these epoch counts.
EPOCH_CHECKPOINTS = [1, 2, 3, 5, 10, 20]


def _say(msg: str) -> None:
    print(msg, flush=True)


def load_corpus() -> bytes:
    repo = Path(__file__).resolve().parent.parent
    files = [
        repo / "PLAN.md", repo / "NEXT_PHASE.md", repo / "README.md",
        repo / "PROGRESS.md", repo / "RESULTS.md", repo / "CLAUDE.md",
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


def _build_context_bundles_batch(byte_atoms, pos_atoms, indices):
    bound = byte_atoms[indices] * pos_atoms.unsqueeze(0)
    summed = bound.sum(dim=1)
    mag = summed.abs().clamp(min=1e-8)
    return summed / mag.to(summed.dtype)


def _predict_batch(W, ctxs, byte_atoms, beta):
    n = ctxs.shape[1]
    q = ctxs @ W.T
    sims = (byte_atoms.conj() @ q.T).real / n
    return torch.softmax(beta * sims, dim=0), sims


def train_epoch(W, byte_atoms, pos_atoms, train_idx, train_targets, beta, arousal, batch_size, n_dim):
    """One pass over training data with batched delta-rule updates. Mutates W in place."""
    T_total = train_idx.shape[0]
    for batch_start in range(0, T_total, batch_size):
        be = min(batch_start + batch_size, T_total)
        idx_batch = train_idx[batch_start:be]
        tgt_batch = train_targets[batch_start:be]

        ctxs = _build_context_bundles_batch(byte_atoms, pos_atoms, idx_batch)
        probs, _ = _predict_batch(W, ctxs, byte_atoms, beta)

        targets = byte_atoms[tgt_batch]
        expected = probs.T.to(byte_atoms.dtype) @ byte_atoms
        errors = targets - expected
        dW = errors.T @ ctxs.conj() / n_dim
        W.add_(dW, alpha=arousal)


def eval_test(W, byte_atoms, pos_atoms, test_idx, test_targets, beta, batch_size, n_dim):
    """Compute test bits/char and W's argmax accuracy."""
    T_test = test_idx.shape[0]
    total_bits = 0.0
    n_argmax_correct = 0
    margins_sum = 0.0
    correct_sims_sum = 0.0
    max_wrong_sims_sum = 0.0

    for bs in range(0, T_test, batch_size):
        be = min(bs + batch_size, T_test)
        ctxs = _build_context_bundles_batch(byte_atoms, pos_atoms, test_idx[bs:be])
        probs, sims = _predict_batch(W, ctxs, byte_atoms, beta)
        p_true = probs.gather(0, test_targets[bs:be].unsqueeze(0)).squeeze(0).clamp(min=1e-12)
        total_bits += float(-torch.log2(p_true).sum())

        argmax_pred = sims.argmax(dim=0)
        n_argmax_correct += int((argmax_pred == test_targets[bs:be]).sum())

        true_sims = sims.gather(0, test_targets[bs:be].unsqueeze(0)).squeeze(0)
        masked = sims.clone()
        masked.scatter_(0, test_targets[bs:be].unsqueeze(0), float("-inf"))
        max_wrong = masked.max(dim=0).values
        margins_sum += float((true_sims - max_wrong).sum())
        correct_sims_sum += float(true_sims.sum())
        max_wrong_sims_sum += float(max_wrong.sum())

    return {
        "test_bpc": total_bits / max(T_test, 1),
        "argmax_accuracy": n_argmax_correct / max(T_test, 1),
        "mean_margin": margins_sum / max(T_test, 1),
        "mean_correct_sim": correct_sims_sum / max(T_test, 1),
        "mean_max_wrong_sim": max_wrong_sims_sum / max(T_test, 1),
    }


def main() -> None:
    _say("Loading corpus...")
    corpus = load_corpus()
    train, test = train_test_split(corpus, 0.8)
    _say(f"  train={len(train)}, test={len(test)} bytes")

    quiet = tracing.TraceBus(enabled=False)
    with tracing.using(quiet):
        gen = torch.Generator().manual_seed(SEED)
        byte_atoms = torch.stack([atoms.make_atom_fhrr(N_SUBSTRATE, gen) for _ in range(VOCAB_SIZE)]).to(DEVICE)
        pos_atoms = torch.stack([atoms.make_atom_fhrr(N_SUBSTRATE, gen) for _ in range(K)]).to(DEVICE)
        W = torch.zeros((N_SUBSTRATE, N_SUBSTRATE), dtype=torch.complex64, device=DEVICE)

        pad = bytes([PAD_BYTE]) * K
        padded_train = pad + train
        padded_test = pad + test
        T_total = len(padded_train) - K
        T_test = len(padded_test) - K

        train_bytes = torch.tensor(list(padded_train), dtype=torch.long).to(DEVICE)
        test_bytes = torch.tensor(list(padded_test), dtype=torch.long).to(DEVICE)
        offsets = torch.arange(K - 1, -1, -1, device=DEVICE)
        positions_train = torch.arange(T_total, device=DEVICE)
        positions_test = torch.arange(T_test, device=DEVICE)
        train_idx = train_bytes[positions_train.unsqueeze(1) + offsets.unsqueeze(0)]
        train_targets = train_bytes[positions_train + K]
        test_idx = test_bytes[positions_test.unsqueeze(1) + offsets.unsqueeze(0)]
        test_targets = test_bytes[positions_test + K]

        _say(f"\nMulti-epoch sweep: N={N_SUBSTRATE}, K={K}, arousal={AROUSAL}, beta={BETA}")
        _say(f"  Checkpoints: {EPOCH_CHECKPOINTS}")
        _say(f"\n{'Epoch':>6s} {'test_bpc':>10s} {'argmax_acc':>11s} {'mean_margin':>12s} {'corr_sim':>10s} {'wrong_sim':>10s} {'W_norm':>10s} {'wall_s':>8s}")

        history = []
        epoch = 0
        t_start = time.perf_counter()

        # Initial state (epoch 0 - just zeros).
        initial = eval_test(W, byte_atoms, pos_atoms, test_idx, test_targets, BETA, BATCH_SIZE, N_SUBSTRATE)
        w_norm = float(W.abs().pow(2).sum().sqrt())
        history.append({"epoch": 0, **initial, "w_frobenius": w_norm, "wall_s": 0.0})
        _say(
            f"{0:>6d} {initial['test_bpc']:>10.4f} {initial['argmax_accuracy']:>11.4f} "
            f"{initial['mean_margin']:>12.4f} {initial['mean_correct_sim']:>10.4f} "
            f"{initial['mean_max_wrong_sim']:>10.4f} {w_norm:>10.2f} {0.0:>8.1f}"
        )

        max_epoch = max(EPOCH_CHECKPOINTS)
        for epoch in range(1, max_epoch + 1):
            train_epoch(W, byte_atoms, pos_atoms, train_idx, train_targets, BETA, AROUSAL, BATCH_SIZE, N_SUBSTRATE)
            if epoch in EPOCH_CHECKPOINTS:
                metrics = eval_test(W, byte_atoms, pos_atoms, test_idx, test_targets, BETA, BATCH_SIZE, N_SUBSTRATE)
                w_norm = float(W.abs().pow(2).sum().sqrt())
                elapsed = time.perf_counter() - t_start
                history.append({"epoch": epoch, **metrics, "w_frobenius": w_norm, "wall_s": elapsed})
                _say(
                    f"{epoch:>6d} {metrics['test_bpc']:>10.4f} {metrics['argmax_accuracy']:>11.4f} "
                    f"{metrics['mean_margin']:>12.4f} {metrics['mean_correct_sim']:>10.4f} "
                    f"{metrics['mean_max_wrong_sim']:>10.4f} {w_norm:>10.2f} {elapsed:>8.1f}"
                )

        _say(f"\nTotal wall time: {time.perf_counter() - t_start:.1f}s")

        best_epoch = min(history, key=lambda h: h["test_bpc"])
        _say(f"\nBest epoch: {best_epoch['epoch']}  test_bpc={best_epoch['test_bpc']:.4f}  argmax_acc={best_epoch['argmax_accuracy']:.4f}")
        _say(f"  vs single-pass baseline: 3.16 (delta {3.16 - best_epoch['test_bpc']:+.4f})")
        _say(f"  vs combined N=4096+pool: 2.84 (delta {2.84 - best_epoch['test_bpc']:+.4f})")
        _say(f"  vs transformer ceiling: 2.39 (gap {best_epoch['test_bpc'] - 2.39:.4f})")

        initial_acc = history[1]["argmax_accuracy"]
        best_acc = best_epoch["argmax_accuracy"]
        _say(f"\nArgmax accuracy improvement: {initial_acc:.4f} (epoch 1) -> {best_acc:.4f} (epoch {best_epoch['epoch']})")

    out = {
        "seed": SEED, "n_substrate": N_SUBSTRATE, "k": K, "arousal": AROUSAL, "beta": BETA,
        "epoch_checkpoints": EPOCH_CHECKPOINTS,
        "history": history,
        "best_epoch": best_epoch,
        "headline": f"Multi-epoch best test bpc = {best_epoch['test_bpc']:.3f} at epoch {best_epoch['epoch']}",
    }
    out_path = Path(__file__).resolve().parent.parent / "data" / "exp_multiepoch_charlm"
    out_path.mkdir(parents=True, exist_ok=True)
    (out_path / "metrics.json").write_text(json.dumps(out, indent=2, default=str))
    _say(f"\nWrote {out_path / 'metrics.json'}")


if __name__ == "__main__":
    main()
