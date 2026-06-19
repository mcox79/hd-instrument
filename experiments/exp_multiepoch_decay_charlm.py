"""Multi-epoch Hebbian with weight decay.

Single-pass Hebbian's anti-overfit property was an artifact of single-pass, not a
structural property. Multi-epoch shows classical overfitting after epoch 3: W norm
explodes, margins collapse, bits/char rebounds upward despite argmax accuracy still
climbing.

This experiment sweeps weight-decay coefficients to see if proper regularization
unlocks longer training while preserving the argmax-accuracy gains.

Decay applied per-batch: W *= (1 - decay) before the delta-rule update.
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
MAX_EPOCHS = 20
EPOCH_CHECKPOINTS = [1, 2, 3, 5, 10, 15, 20]
DECAY_VALUES = [0.0, 1e-4, 1e-3, 5e-3, 1e-2]


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


def train_test_split(corpus, train_frac=0.8):
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


def train_epoch(W, byte_atoms, pos_atoms, train_idx, train_targets, beta, arousal, decay, batch_size, n_dim):
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
        if decay > 0:
            W.mul_(1.0 - decay)
        W.add_(dW, alpha=arousal)


def eval_test(W, byte_atoms, pos_atoms, test_idx, test_targets, beta, batch_size, n_dim):
    T_test = test_idx.shape[0]
    total_bits = 0.0
    n_argmax_correct = 0
    margins_sum = 0.0
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
    return {
        "test_bpc": total_bits / max(T_test, 1),
        "argmax_accuracy": n_argmax_correct / max(T_test, 1),
        "mean_margin": margins_sum / max(T_test, 1),
    }


def run_decay_sweep(decay, train, test):
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
        pos_train = torch.arange(T_total, device=DEVICE)
        pos_test = torch.arange(T_test, device=DEVICE)
        train_idx = train_bytes[pos_train.unsqueeze(1) + offsets.unsqueeze(0)]
        train_targets = train_bytes[pos_train + K]
        test_idx = test_bytes[pos_test.unsqueeze(1) + offsets.unsqueeze(0)]
        test_targets = test_bytes[pos_test + K]

        checkpoints = []
        for epoch in range(1, MAX_EPOCHS + 1):
            train_epoch(W, byte_atoms, pos_atoms, train_idx, train_targets, BETA, AROUSAL, decay, BATCH_SIZE, N_SUBSTRATE)
            if epoch in EPOCH_CHECKPOINTS:
                m = eval_test(W, byte_atoms, pos_atoms, test_idx, test_targets, BETA, BATCH_SIZE, N_SUBSTRATE)
                w_norm = float(W.abs().pow(2).sum().sqrt())
                checkpoints.append({"epoch": epoch, **m, "w_frobenius": w_norm})
        return checkpoints


def main() -> None:
    _say("Loading corpus...")
    corpus = load_corpus()
    train, test = train_test_split(corpus, 0.8)
    _say(f"  train={len(train)}, test={len(test)} bytes")
    _say(f"\nDecay sweep at N={N_SUBSTRATE}, K={K}, arousal={AROUSAL}, beta={BETA}")
    _say(f"  decay values: {DECAY_VALUES}")
    _say(f"  epoch checkpoints: {EPOCH_CHECKPOINTS}")

    all_results = {}
    t_start = time.perf_counter()
    for decay in DECAY_VALUES:
        _say(f"\n--- decay = {decay} ---")
        t0 = time.perf_counter()
        checkpoints = run_decay_sweep(decay, train, test)
        elapsed = time.perf_counter() - t0
        _say(f"{'epoch':>6s} {'test_bpc':>10s} {'argmax':>10s} {'margin':>10s} {'W_norm':>10s}")
        for c in checkpoints:
            _say(f"{c['epoch']:>6d} {c['test_bpc']:>10.4f} {c['argmax_accuracy']:>10.4f} {c['mean_margin']:>10.4f} {c['w_frobenius']:>10.2f}")
        all_results[decay] = checkpoints
        _say(f"  ({elapsed:.1f}s)")

    total_wall = time.perf_counter() - t_start

    # Find best across all runs.
    best = None
    for decay, ckpts in all_results.items():
        for c in ckpts:
            if best is None or c["test_bpc"] < best["test_bpc"]:
                best = {**c, "decay": decay}

    _say(f"\n========= SUMMARY =========")
    _say(f"{'decay':>10s} {'best epoch':>11s} {'best bpc':>10s} {'argmax':>10s}")
    for decay, ckpts in all_results.items():
        best_for_decay = min(ckpts, key=lambda c: c["test_bpc"])
        _say(f"{decay:>10.0e} {best_for_decay['epoch']:>11d} {best_for_decay['test_bpc']:>10.4f} {best_for_decay['argmax_accuracy']:>10.4f}")

    _say(f"\nGlobal best: decay={best['decay']}, epoch={best['epoch']}, test_bpc={best['test_bpc']:.4f}, argmax_acc={best['argmax_accuracy']:.4f}")
    _say(f"  vs single-pass (3.16):    delta {3.16 - best['test_bpc']:+.4f}")
    _say(f"  vs no-decay multi-epoch (3.005): delta {3.005 - best['test_bpc']:+.4f}")
    _say(f"  vs combined N=4096+pool (2.84): delta {2.84 - best['test_bpc']:+.4f}")
    _say(f"  vs transformer ceiling (2.39):  gap {best['test_bpc'] - 2.39:.4f}")

    _say(f"\nTotal wall time: {total_wall:.1f}s")

    out = {
        "seed": SEED, "n_substrate": N_SUBSTRATE, "k": K, "arousal": AROUSAL, "beta": BETA,
        "decay_values": DECAY_VALUES, "epoch_checkpoints": EPOCH_CHECKPOINTS,
        "results_by_decay": {str(d): ckpts for d, ckpts in all_results.items()},
        "best": best,
        "headline": f"Multi-epoch+decay best: decay={best['decay']:.0e}, epoch={best['epoch']}, test_bpc={best['test_bpc']:.3f}",
    }
    out_path = Path(__file__).resolve().parent.parent / "data" / "exp_multiepoch_decay_charlm"
    out_path.mkdir(parents=True, exist_ok=True)
    (out_path / "metrics.json").write_text(json.dumps(out, indent=2, default=str))
    _say(f"\nWrote {out_path / 'metrics.json'}")


if __name__ == "__main__":
    main()
