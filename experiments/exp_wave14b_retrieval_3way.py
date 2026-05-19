"""Wave 14.B 3-way retrieval comparison: hard NN vs fixed soft vs annealed soft.

The three viable production strategies all share the same architecture
(W matrix + pool retrieval) but differ in how they score pool entries:

  - HARD NN: argmax + one-hot label (mostly monotone in P)
  - FIXED SOFT: softmax(beta=8) (inverted-U from Velickovic 2024)
  - ANNEALED SOFT: softmax(beta_0 * sqrt(log P / log P_0)) (monotone fix)

We've tested each separately. This combines them in one sweep so the
deployment question ("which retrieval strategy to ship?") has direct
empirical data.

Conservative parameter variant: same Phase A + B architecture as before,
three retrieval functions tested in parallel.
"""

from __future__ import annotations

import json
import math
import time
import os
from pathlib import Path

import torch


torch.set_num_threads(max(1, os.cpu_count() or 1))
DEVICE = torch.device("cpu")
SEED = 17
VOCAB_SIZE = 256
PAD_BYTE = 0
K = 4
BETA = 8.0
P_BASELINE = 1024
BATCH_SIZE = 64
ALPHA = 0.3
MAX_EPOCHS = 15
RELU_B = 0.5
N = 4096
DELTA_RULE_ALPHA = 0.3
DELTA_RULE_DECAY = 1e-4
POOL_SIZES = [256, 1024, 4096, 16384]


def _say(msg):
    print(msg, flush=True)


def scaled_beta(P):
    return BETA * math.sqrt(math.log(P) / math.log(P_BASELINE))


def load_corpus_a():
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


def shuffle_bytes(data, seed):
    gen = torch.Generator().manual_seed(seed)
    perm = torch.randperm(len(data), generator=gen).tolist()
    out = bytearray(len(data))
    for i, p in enumerate(perm):
        out[i] = data[p]
    return bytes(out)


def make_bsc_atoms(k, n, gen):
    raw = torch.rand((k, n), generator=gen)
    return (2.0 * (raw > 0.5).float() - 1.0)


def build_ctx_bundles_bsc(byte_atoms, pos_atoms, indices):
    bound = byte_atoms[indices] * pos_atoms.unsqueeze(0)
    summed = bound.sum(dim=1)
    out = torch.sign(summed)
    return torch.where(out == 0, torch.ones_like(out), out)


def shifted_relu(q, b):
    return torch.clamp(q - b, min=0.0)


def predict_W(W, ctxs, byte_atoms, beta, n):
    q = ctxs @ W.T
    q = shifted_relu(q, RELU_B)
    sims = (byte_atoms @ q.T) / n
    return torch.softmax(beta * sims, dim=0)


def pool_soft(ctxs, pool_vecs, pool_labels, pool_used, beta, n):
    B = ctxs.shape[0]
    active = pool_vecs[:pool_used]
    labels = pool_labels[:pool_used]
    sims = (active @ ctxs.T) / n
    weights = torch.softmax(beta * sims, dim=0)
    P_retr = torch.zeros(VOCAB_SIZE, B, device=ctxs.device)
    P_retr.scatter_add_(0, labels.unsqueeze(1).expand(-1, B), weights)
    return P_retr


def pool_hard(ctxs, pool_vecs, pool_labels, pool_used, n):
    B = ctxs.shape[0]
    active = pool_vecs[:pool_used]
    labels = pool_labels[:pool_used]
    sims = (active @ ctxs.T) / n
    top_idx = sims.argmax(dim=0)
    top_labels = labels[top_idx]
    P_retr = torch.zeros(VOCAB_SIZE, B, device=ctxs.device)
    P_retr.scatter_(0, top_labels.unsqueeze(0), 1.0)
    return P_retr * 0.99 + 0.01 / VOCAB_SIZE


def run_one_pool_size(pool_size, byte_atoms, pos_atoms, train_a, train_b, test_a):
    beta_annealed = scaled_beta(pool_size)
    W = torch.zeros((N, N), dtype=torch.float32, device=DEVICE)
    pool_vecs = torch.zeros((pool_size, N), dtype=torch.float32, device=DEVICE)
    pool_labels = torch.zeros(pool_size, dtype=torch.long, device=DEVICE)
    pool_used = 0
    pool_idx = 0
    arange_b = torch.arange(BATCH_SIZE, device=DEVICE)
    pad = bytes([PAD_BYTE]) * K

    padded_train_a = pad + train_a
    T_total_a = len(padded_train_a) - K
    train_a_bytes = torch.tensor(list(padded_train_a), dtype=torch.long).to(DEVICE)
    offsets = torch.arange(K - 1, -1, -1, device=DEVICE)
    pos_train_a = torch.arange(T_total_a, device=DEVICE)
    train_a_idx = train_a_bytes[pos_train_a.unsqueeze(1) + offsets.unsqueeze(0)]
    train_a_targets = train_a_bytes[pos_train_a + K]

    for epoch in range(1, MAX_EPOCHS + 1):
        for batch_start in range(0, T_total_a, BATCH_SIZE):
            be = min(batch_start + BATCH_SIZE, T_total_a)
            idx_batch = train_a_idx[batch_start:be]
            tgt_batch = train_a_targets[batch_start:be]
            B = idx_batch.shape[0]
            ctxs = build_ctx_bundles_bsc(byte_atoms, pos_atoms, idx_batch)
            with torch.no_grad():
                q = ctxs @ W.T
                q = shifted_relu(q, RELU_B)
                sims = (byte_atoms @ q.T) / N
                P = torch.softmax(BETA * sims, dim=0)
                target_atoms_a = byte_atoms[tgt_batch]
                predicted = (P.T @ byte_atoms)
                residual = target_atoms_a - predicted
                dW = (residual.T @ ctxs) / N
                W.mul_(1.0 - DELTA_RULE_DECAY)
                W.add_(dW, alpha=DELTA_RULE_ALPHA)
                if epoch == 1:
                    dest = (pool_idx + arange_b[:B]) % pool_size
                    pool_vecs.index_copy_(0, dest, ctxs)
                    pool_labels.index_copy_(0, dest, tgt_batch)
                    pool_idx = (pool_idx + B) % pool_size
                    pool_used = min(pool_used + B, pool_size)

    # Train on B
    padded_train_b = pad + train_b
    T_total_b = len(padded_train_b) - K
    train_b_bytes = torch.tensor(list(padded_train_b), dtype=torch.long).to(DEVICE)
    pos_train_b = torch.arange(T_total_b, device=DEVICE)
    train_b_idx = train_b_bytes[pos_train_b.unsqueeze(1) + offsets.unsqueeze(0)]
    train_b_targets = train_b_bytes[pos_train_b + K]

    for epoch in range(MAX_EPOCHS):
        for batch_start in range(0, T_total_b, BATCH_SIZE):
            be = min(batch_start + BATCH_SIZE, T_total_b)
            idx_batch = train_b_idx[batch_start:be]
            tgt_batch = train_b_targets[batch_start:be]
            ctxs = build_ctx_bundles_bsc(byte_atoms, pos_atoms, idx_batch)
            with torch.no_grad():
                q = ctxs @ W.T
                q = shifted_relu(q, RELU_B)
                sims = (byte_atoms @ q.T) / N
                P = torch.softmax(BETA * sims, dim=0)
                target_atoms_b = byte_atoms[tgt_batch]
                predicted = (P.T @ byte_atoms)
                residual = target_atoms_b - predicted
                dW = (residual.T @ ctxs) / N
                W.mul_(1.0 - DELTA_RULE_DECAY)
                W.add_(dW, alpha=DELTA_RULE_ALPHA)

    # Eval 3 ways on test_A
    pad = bytes([PAD_BYTE]) * K
    padded_test = pad + test_a
    T_test = len(padded_test) - K
    test_bytes = torch.tensor(list(padded_test), dtype=torch.long).to(DEVICE)
    pos_test = torch.arange(T_test, device=DEVICE)
    test_idx = test_bytes[pos_test.unsqueeze(1) + offsets.unsqueeze(0)]
    test_targets = test_bytes[pos_test + K]

    bits = {"hard": 0.0, "fixed_soft": 0.0, "annealed_soft": 0.0}
    for bs in range(0, T_test, BATCH_SIZE):
        be = min(bs + BATCH_SIZE, T_test)
        ctxs = build_ctx_bundles_bsc(byte_atoms, pos_atoms, test_idx[bs:be])
        P_W = predict_W(W, ctxs, byte_atoms, BETA, N)
        tgts = test_targets[bs:be]
        # Hard
        P_h = pool_hard(ctxs, pool_vecs, pool_labels, pool_used, N)
        P_1 = ALPHA * P_h + (1 - ALPHA) * P_W
        bits["hard"] += float(-torch.log2(P_1.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)).sum())
        # Fixed soft beta=8
        P_fs = pool_soft(ctxs, pool_vecs, pool_labels, pool_used, BETA, N)
        P_2 = ALPHA * P_fs + (1 - ALPHA) * P_W
        bits["fixed_soft"] += float(-torch.log2(P_2.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)).sum())
        # Annealed soft
        P_as = pool_soft(ctxs, pool_vecs, pool_labels, pool_used, beta_annealed, N)
        P_3 = ALPHA * P_as + (1 - ALPHA) * P_W
        bits["annealed_soft"] += float(-torch.log2(P_3.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)).sum())

    return {"pool_size": pool_size, "beta_annealed": beta_annealed,
           "hard": bits["hard"] / T_test,
           "fixed_soft": bits["fixed_soft"] / T_test,
           "annealed_soft": bits["annealed_soft"] / T_test}


def main():
    _say(f"Wave 14.B 3-way retrieval comparison on CPU")
    _say(f"  Pool sizes: {POOL_SIZES}, threads={torch.get_num_threads()}")

    corpus_a = load_corpus_a()
    corpus_b = shuffle_bytes(corpus_a, seed=SEED + 1)
    split = int(0.8 * len(corpus_a))
    train_a, test_a = corpus_a[:split], corpus_a[split:]
    train_b = corpus_b[:int(0.8 * len(corpus_b))]

    gen = torch.Generator().manual_seed(SEED)
    byte_atoms = make_bsc_atoms(VOCAB_SIZE, N, gen).to(DEVICE)
    pos_atoms = make_bsc_atoms(K, N, gen).to(DEVICE)

    results = []
    t_start = time.perf_counter()
    _say(f"\n  {'pool':>7} | {'beta-a':>6} | {'hard':>7} | {'fixed':>7} | {'annealed':>8} | {'wall':>5}")
    _say(f"  {'-'*7}-+-{'-'*6}-+-{'-'*7}-+-{'-'*7}-+-{'-'*8}-+-{'-'*5}")
    for ps in POOL_SIZES:
        t0 = time.perf_counter()
        r = run_one_pool_size(ps, byte_atoms, pos_atoms, train_a, train_b, test_a)
        dt = time.perf_counter() - t0
        _say(f"  {ps:>7} | {r['beta_annealed']:>6.2f} | {r['hard']:>7.4f} | {r['fixed_soft']:>7.4f} | "
             f"{r['annealed_soft']:>8.4f} | {dt:>4.0f}s")
        results.append(r)

    _say(f"\n========= INTERPRETATION =========")
    # Find best at each pool size
    for r in results:
        best_method = min(["hard", "fixed_soft", "annealed_soft"], key=lambda m: r[m])
        _say(f"  P={r['pool_size']}: best = {best_method} ({r[best_method]:.4f})")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_retrieval_3way"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps(
        {"pool_sizes": POOL_SIZES, "results": results,
         "elapsed_s": time.perf_counter() - t_start},
        indent=2, default=str))
    _say(f"\nWrote {out_dir / 'metrics.json'}")


if __name__ == "__main__":
    main()
