"""N scaling sweep: how does the basin floor change with substrate dimensionality?

Best so far: 2.4963 at N=4096. Theory says capacity scales linearly with N, so
larger N should produce a lower basin floor — but how much lower?

This script runs the combined+relu config at three substrate sizes:
  N=4096  (current best, baseline)
  N=8192  (2x: should help ~0.02-0.05 bpc)
  N=16384 (4x: should help more, but memory pressure on 8GB GPU)

15 epochs each, all stacked best practices (multi-epoch + decay + pool + relu).
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
VOCAB_SIZE = 256
PAD_BYTE = 0
K = 4
AROUSAL = 0.3
BETA = 8.0
BATCH_SIZE = 64
POOL_SIZE = 1024
ALPHA = 0.3
DECAY = 1e-4
MAX_EPOCHS = 15
EPOCH_CHECKPOINTS = [1, 5, 10, 15]
RELU_B = 0.5

N_VALUES = [4096, 8192, 16384]


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


def magnitude_relu(q, b):
    eps = 1e-9
    mag = q.abs().clamp(min=eps)
    new_mag = torch.clamp(mag - b, min=0.0)
    return q * (new_mag / mag).to(q.dtype)


def _predict_W_batch(W, ctxs, byte_atoms, beta):
    n = ctxs.shape[1]
    q = ctxs @ W.T
    q = magnitude_relu(q, RELU_B)
    sims = (byte_atoms.conj() @ q.T).real / n
    return torch.softmax(beta * sims, dim=0)


def _predict_pool_batch(ctxs, pool_vecs, pool_labels, pool_used, beta):
    B = ctxs.shape[0]
    if pool_used == 0:
        return torch.full((VOCAB_SIZE, B), 1.0 / VOCAB_SIZE, device=ctxs.device)
    n = ctxs.shape[1]
    active = pool_vecs[:pool_used]
    labels = pool_labels[:pool_used]
    sims = (active.conj() @ ctxs.T).real / n
    weights = torch.softmax(beta * sims, dim=0)
    P_retr = torch.zeros(VOCAB_SIZE, B, device=ctxs.device)
    P_retr.scatter_add_(0, labels.unsqueeze(1).expand(-1, B), weights)
    return P_retr


def run_config(N: int, train, test):
    quiet = tracing.TraceBus(enabled=False)
    with tracing.using(quiet):
        gen = torch.Generator().manual_seed(SEED)
        byte_atoms = torch.stack([atoms.make_atom_fhrr(N, gen) for _ in range(VOCAB_SIZE)]).to(DEVICE)
        pos_atoms = torch.stack([atoms.make_atom_fhrr(N, gen) for _ in range(K)]).to(DEVICE)
        W = torch.zeros((N, N), dtype=torch.complex64, device=DEVICE)
        pool_vecs = torch.zeros((POOL_SIZE, N), dtype=torch.complex64, device=DEVICE)
        pool_labels = torch.zeros(POOL_SIZE, dtype=torch.long, device=DEVICE)
        pool_used = 0
        pool_idx = 0

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

        history = []
        t_start = time.perf_counter()
        for epoch in range(1, MAX_EPOCHS + 1):
            for batch_start in range(0, T_total, BATCH_SIZE):
                be = min(batch_start + BATCH_SIZE, T_total)
                idx_batch = train_idx[batch_start:be]
                tgt_batch = train_targets[batch_start:be]
                B = idx_batch.shape[0]
                ctxs = _build_context_bundles_batch(byte_atoms, pos_atoms, idx_batch)
                P_W = _predict_W_batch(W, ctxs, byte_atoms, BETA)
                targets = byte_atoms[tgt_batch]
                expected = P_W.T.to(byte_atoms.dtype) @ byte_atoms
                errors = targets - expected
                dW = errors.T @ ctxs.conj() / N
                if DECAY > 0:
                    W.mul_(1.0 - DECAY)
                W.add_(dW, alpha=AROUSAL)
                if epoch == 1:
                    for b in range(B):
                        pool_vecs[pool_idx] = ctxs[b]
                        pool_labels[pool_idx] = tgt_batch[b]
                        pool_idx = (pool_idx + 1) % POOL_SIZE
                        pool_used = min(pool_used + 1, POOL_SIZE)
            if epoch in EPOCH_CHECKPOINTS:
                total_bits = 0.0
                argmax_correct = 0
                for bs in range(0, T_test, BATCH_SIZE):
                    be = min(bs + BATCH_SIZE, T_test)
                    ctxs = _build_context_bundles_batch(byte_atoms, pos_atoms, test_idx[bs:be])
                    P_W = _predict_W_batch(W, ctxs, byte_atoms, BETA)
                    P_retr = _predict_pool_batch(ctxs, pool_vecs, pool_labels, pool_used, BETA)
                    P = ALPHA * P_retr + (1.0 - ALPHA) * P_W
                    p_true = P.gather(0, test_targets[bs:be].unsqueeze(0)).squeeze(0).clamp(min=1e-12)
                    total_bits += float(-torch.log2(p_true).sum())
                    argmax_pred = P.argmax(dim=0)
                    argmax_correct += int((argmax_pred == test_targets[bs:be]).sum())
                test_bpc = total_bits / max(T_test, 1)
                argmax_acc = argmax_correct / max(T_test, 1)
                elapsed = time.perf_counter() - t_start
                history.append({"epoch": epoch, "test_bpc": test_bpc, "argmax_accuracy": argmax_acc, "wall_s": elapsed})
                _say(f"    epoch={epoch}  test_bpc={test_bpc:.4f}  argmax={argmax_acc:.4f}  ({elapsed:.1f}s)")
        return {"N": N, "history": history}


def main() -> None:
    _say("Loading corpus...")
    corpus = load_corpus()
    train, test = train_test_split(corpus, 0.8)
    _say(f"  train={len(train)}, test={len(test)} bytes")
    _say(f"\nN scaling sweep: {N_VALUES}")
    _say(f"  K={K}, arousal={AROUSAL}, beta={BETA}, decay={DECAY}, pool={POOL_SIZE}")
    _say(f"  Baseline (N=4096, GPU): 2.4994")

    all_results = []
    for N in N_VALUES:
        _say(f"\n--- N = {N} ---")
        t0 = time.perf_counter()
        try:
            r = run_config(N, train, test)
            r["wall_time_s"] = time.perf_counter() - t0
            all_results.append(r)
            best = min(r["history"], key=lambda h: h["test_bpc"])
            _say(f"  Best for N={N}: epoch={best['epoch']}, test_bpc={best['test_bpc']:.4f}")
        except torch.cuda.OutOfMemoryError as e:
            _say(f"  OOM at N={N}: {e}")
            torch.cuda.empty_cache()
            all_results.append({"N": N, "error": "OOM"})

    _say(f"\n========= SUMMARY =========")
    _say(f"{'N':>6s} {'best epoch':>11s} {'best bpc':>10s}")
    for r in all_results:
        if "history" in r:
            best = min(r["history"], key=lambda h: h["test_bpc"])
            _say(f"{r['N']:>6d} {best['epoch']:>11d} {best['test_bpc']:>10.4f}")
        else:
            _say(f"{r['N']:>6d} {'-':>11s} {r.get('error', 'unknown'):>10s}")

    out = {"seed": SEED, "k": K, "arousal": AROUSAL, "beta": BETA, "decay": DECAY,
           "pool_size": POOL_SIZE, "alpha": ALPHA, "relu_b": RELU_B, "max_epochs": MAX_EPOCHS,
           "n_values": N_VALUES, "results": all_results}
    out_path = Path(__file__).resolve().parent.parent / "data" / "exp_n_scaling_charlm"
    out_path.mkdir(parents=True, exist_ok=True)
    (out_path / "metrics.json").write_text(json.dumps(out, indent=2, default=str))
    _say(f"\nWrote {out_path / 'metrics.json'}")


if __name__ == "__main__":
    main()
