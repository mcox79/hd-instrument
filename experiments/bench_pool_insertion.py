"""Benchmark: pool insertion for-loop vs vectorized index_copy_.

Measures the cost of the pool insertion path at N=4096 and N=16384,
isolating the Python-loop overhead identified in the N-scaling slowdown audit.

Run on the desktop GPU with N values matching the actual experiment.
"""

from __future__ import annotations

import time

import torch


DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
BATCH_SIZE = 64
POOL_SIZE = 1024
N_BATCHES = 615  # roughly the N-scaling experiment's epoch count

print(f"device={DEVICE}, batch_size={BATCH_SIZE}, pool_size={POOL_SIZE}, n_batches={N_BATCHES}")


def bench_forloop(N):
    pool_vecs = torch.zeros((POOL_SIZE, N), dtype=torch.complex64, device=DEVICE)
    pool_labels = torch.zeros(POOL_SIZE, dtype=torch.long, device=DEVICE)
    pool_idx = 0
    pool_used = 0
    # Pre-generate ctx batches and target labels.
    all_ctxs = torch.randn((N_BATCHES, BATCH_SIZE, N), dtype=torch.complex64, device=DEVICE)
    all_tgts = torch.randint(0, 256, (N_BATCHES, BATCH_SIZE), dtype=torch.long, device=DEVICE)
    torch.cuda.synchronize()
    t0 = time.perf_counter()
    for batch in range(N_BATCHES):
        ctxs = all_ctxs[batch]
        tgts = all_tgts[batch]
        B = ctxs.shape[0]
        for b in range(B):
            pool_vecs[pool_idx] = ctxs[b]
            pool_labels[pool_idx] = tgts[b]
            pool_idx = (pool_idx + 1) % POOL_SIZE
            pool_used = min(pool_used + 1, POOL_SIZE)
    torch.cuda.synchronize()
    return time.perf_counter() - t0


def bench_vectorized(N):
    pool_vecs = torch.zeros((POOL_SIZE, N), dtype=torch.complex64, device=DEVICE)
    pool_labels = torch.zeros(POOL_SIZE, dtype=torch.long, device=DEVICE)
    pool_idx = 0
    pool_used = 0
    all_ctxs = torch.randn((N_BATCHES, BATCH_SIZE, N), dtype=torch.complex64, device=DEVICE)
    all_tgts = torch.randint(0, 256, (N_BATCHES, BATCH_SIZE), dtype=torch.long, device=DEVICE)
    arange_b = torch.arange(BATCH_SIZE, device=DEVICE)
    torch.cuda.synchronize()
    t0 = time.perf_counter()
    for batch in range(N_BATCHES):
        ctxs = all_ctxs[batch]
        tgts = all_tgts[batch]
        B = ctxs.shape[0]
        dest = (pool_idx + arange_b[:B]) % POOL_SIZE
        pool_vecs.index_copy_(0, dest, ctxs)
        pool_labels.index_copy_(0, dest, tgts)
        pool_idx = (pool_idx + B) % POOL_SIZE
        pool_used = min(pool_used + B, POOL_SIZE)
    torch.cuda.synchronize()
    return time.perf_counter() - t0


def bench_train_step(N):
    """Simulate one epoch of the W training step at N. Measures the W-update cost
    separate from pool insertion."""
    W = torch.zeros((N, N), dtype=torch.complex64, device=DEVICE)
    byte_atoms = torch.randn((256, N), dtype=torch.complex64, device=DEVICE)
    byte_atoms = byte_atoms / byte_atoms.abs().clamp(min=1e-8).to(byte_atoms.dtype)
    decay = 1e-4
    arousal = 0.3
    all_ctxs = torch.randn((N_BATCHES, BATCH_SIZE, N), dtype=torch.complex64, device=DEVICE)
    all_ctxs = all_ctxs / all_ctxs.abs().clamp(min=1e-8).to(all_ctxs.dtype)
    all_tgts = torch.randint(0, 256, (N_BATCHES, BATCH_SIZE), dtype=torch.long, device=DEVICE)
    torch.cuda.synchronize()
    t0 = time.perf_counter()
    for batch in range(N_BATCHES):
        ctxs = all_ctxs[batch]
        tgts = all_tgts[batch]
        # forward
        q = ctxs @ W.T
        sims = (byte_atoms.conj() @ q.T).real / N
        P_W = torch.softmax(8.0 * sims, dim=0)
        # error
        targets = byte_atoms[tgts]
        expected = P_W.T.to(byte_atoms.dtype) @ byte_atoms
        errors = targets - expected
        dW = errors.T @ ctxs.conj() / N
        W.mul_(1.0 - decay)
        W.add_(dW, alpha=arousal)
    torch.cuda.synchronize()
    return time.perf_counter() - t0


for N in [4096, 16384]:
    print(f"\n=== N = {N} ===")
    # Warm-up
    _ = bench_forloop(N)
    t_forloop = bench_forloop(N)
    print(f"  Python for-loop pool insertion: {t_forloop:.2f}s ({1000*t_forloop/N_BATCHES:.1f}ms/batch)")
    t_vec = bench_vectorized(N)
    print(f"  Vectorized pool insertion:      {t_vec:.2f}s ({1000*t_vec/N_BATCHES:.1f}ms/batch)")
    print(f"  Speedup: {t_forloop / max(t_vec, 1e-9):.1f}x")
    t_train = bench_train_step(N)
    print(f"  W update + forward (no pool):   {t_train:.2f}s ({1000*t_train/N_BATCHES:.1f}ms/batch)")
    print(f"  Pool-insertion overhead share:  {100 * t_forloop / (t_forloop + t_train):.1f}%")
