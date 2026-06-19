"""BSC at N=16384 — does the floor move with capacity?

The FHRR N=16384 run was killed earlier because complex64 GEMM is bandwidth-
bound and per-epoch was ~10-15× the N=4096 cost. BSC uses real FP32 GEMM
which engages Tensor Cores via TF32, so N=16384 should be tractable.

Tests two questions:
1. Does the 2.48 floor at N=4096 move with 4x more substrate dimensions?
   Frady-Kleyko-Sommer capacity scales as log(N) for bundling, ~N for binding
   storage. We measured -0.022 going N=4096 → N=8192 with FHRR; if the trend
   continues, N=16384 should give another ~0.02 (so ~2.46 expected).
2. Does the BSC substrate keep its ~2x speed advantage at N=16384?
"""

from __future__ import annotations

import json
import math
import time
from pathlib import Path

import torch


torch.set_float32_matmul_precision("high")

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


def make_bsc_atoms(k, n, gen):
    raw = torch.rand((k, n), generator=gen)
    return (2.0 * (raw > 0.5).float() - 1.0)


def build_ctx_bundles_bsc_signed(byte_atoms, pos_atoms, indices):
    bound = byte_atoms[indices] * pos_atoms.unsqueeze(0)
    summed = bound.sum(dim=1)
    out = torch.sign(summed)
    out = torch.where(out == 0, torch.ones_like(out), out)
    return out


def shifted_relu(q, b):
    return torch.clamp(q - b, min=0.0)


def predict_W_bsc(W, ctxs, byte_atoms, beta):
    n = ctxs.shape[1]
    q = ctxs @ W.T
    q = shifted_relu(q, RELU_B)
    sims = (byte_atoms @ q.T) / n
    return torch.softmax(beta * sims, dim=0)


def predict_pool_bsc(ctxs, pool_vecs, pool_labels, pool_used, beta):
    B = ctxs.shape[0]
    if pool_used == 0:
        return torch.full((VOCAB_SIZE, B), 1.0 / VOCAB_SIZE, device=ctxs.device)
    n = ctxs.shape[1]
    active = pool_vecs[:pool_used]
    labels = pool_labels[:pool_used]
    sims = (active @ ctxs.T) / n
    weights = torch.softmax(beta * sims, dim=0)
    P_retr = torch.zeros(VOCAB_SIZE, B, device=ctxs.device)
    P_retr.scatter_add_(0, labels.unsqueeze(1).expand(-1, B), weights)
    return P_retr


def run_config(N, train, test):
    gen = torch.Generator().manual_seed(SEED)
    byte_atoms = make_bsc_atoms(VOCAB_SIZE, N, gen).to(DEVICE)
    pos_atoms = make_bsc_atoms(K, N, gen).to(DEVICE)
    W = torch.zeros((N, N), dtype=torch.float32, device=DEVICE)
    pool_vecs = torch.zeros((POOL_SIZE, N), dtype=torch.float32, device=DEVICE)
    pool_labels = torch.zeros(POOL_SIZE, dtype=torch.long, device=DEVICE)
    pool_used = 0
    pool_idx = 0
    arange_b = torch.arange(BATCH_SIZE, device=DEVICE)

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
            ctxs = build_ctx_bundles_bsc_signed(byte_atoms, pos_atoms, idx_batch)
            P_W = predict_W_bsc(W, ctxs, byte_atoms, BETA)
            targets = byte_atoms[tgt_batch]
            expected = P_W.T @ byte_atoms
            errors = targets - expected
            dW = errors.T @ ctxs / N
            if DECAY > 0:
                W.mul_(1.0 - DECAY)
            W.add_(dW, alpha=AROUSAL)
            if epoch == 1:
                dest = (pool_idx + arange_b[:B]) % POOL_SIZE
                pool_vecs.index_copy_(0, dest, ctxs)
                pool_labels.index_copy_(0, dest, tgt_batch)
                pool_idx = (pool_idx + B) % POOL_SIZE
                pool_used = min(pool_used + B, POOL_SIZE)
        if epoch in EPOCH_CHECKPOINTS:
            total_bits = 0.0
            argmax_correct = 0
            for bs in range(0, T_test, BATCH_SIZE):
                be = min(bs + BATCH_SIZE, T_test)
                ctxs = build_ctx_bundles_bsc_signed(byte_atoms, pos_atoms, test_idx[bs:be])
                P_W = predict_W_bsc(W, ctxs, byte_atoms, BETA)
                P_retr = predict_pool_bsc(ctxs, pool_vecs, pool_labels, pool_used, BETA)
                P = ALPHA * P_retr + (1.0 - ALPHA) * P_W
                tgts = test_targets[bs:be]
                p_true = P.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)
                total_bits += float(-torch.log2(p_true).sum())
                argmax_correct += int((P.argmax(dim=0) == tgts).sum())
            test_bpc = total_bits / max(T_test, 1)
            argmax_acc = argmax_correct / max(T_test, 1)
            elapsed = time.perf_counter() - t_start
            history.append({"epoch": epoch, "test_bpc": test_bpc, "argmax_accuracy": argmax_acc, "wall_s": elapsed})
            _say(f"    epoch={epoch}  test_bpc={test_bpc:.4f}  argmax={argmax_acc:.4f}  ({elapsed:.1f}s)")
    return {"N": N, "history": history}


def main() -> None:
    _say("Loading corpus...")
    corpus = load_corpus()
    cut = int(len(corpus) * 0.8)
    train, test = corpus[:cut], corpus[cut:]
    _say(f"  train={len(train)}, test={len(test)} bytes")
    _say(f"\nBSC N-scaling sweep (Tensor Core accelerated)")
    _say(f"  N_VALUES={N_VALUES}, K={K}, signed bundle + ReLU readout")
    _say(f"  Reference (BSC N=4096): 2.4817")
    _say(f"  Question: does the floor move with capacity at N=8192, N=16384?")

    all_results = []
    for N in N_VALUES:
        _say(f"\n--- N = {N} ---")
        t0 = time.perf_counter()
        try:
            r = run_config(N, train, test)
            r["wall_time_s"] = time.perf_counter() - t0
            all_results.append(r)
            best = min(r["history"], key=lambda h: h["test_bpc"])
            _say(f"  Best for N={N}: ep={best['epoch']}, bpc={best['test_bpc']:.4f}, wall={r['wall_time_s']:.1f}s")
        except torch.cuda.OutOfMemoryError as e:
            _say(f"  OOM at N={N}: {e}")
            torch.cuda.empty_cache()
            all_results.append({"N": N, "error": "OOM"})

    _say(f"\n========= SUMMARY =========")
    _say(f"{'N':>6s} {'best_ep':>8s} {'best_bpc':>10s} {'wall':>8s}")
    for r in all_results:
        if "history" in r:
            best = min(r["history"], key=lambda h: h["test_bpc"])
            _say(f"{r['N']:>6d} {best['epoch']:>8d} {best['test_bpc']:>10.4f} {r['wall_time_s']:>8.1f}")
        else:
            _say(f"{r['N']:>6d} {'-':>8s} {r.get('error', 'unknown'):>10s}")

    out = {"seed": SEED, "k": K, "arousal": AROUSAL, "beta": BETA, "decay": DECAY,
           "pool_size": POOL_SIZE, "alpha": ALPHA, "relu_b": RELU_B, "max_epochs": MAX_EPOCHS,
           "n_values": N_VALUES, "substrate": "BSC", "results": all_results}
    out_path = Path(__file__).resolve().parent.parent / "data" / "exp_bsc_n16384_charlm"
    out_path.mkdir(parents=True, exist_ok=True)
    (out_path / "metrics.json").write_text(json.dumps(out, indent=2, default=str))
    _say(f"\nWrote {out_path / 'metrics.json'}")


if __name__ == "__main__":
    main()
