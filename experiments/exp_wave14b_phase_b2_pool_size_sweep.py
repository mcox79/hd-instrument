"""Wave 14.B Phase B.2 POOL_SIZE sweep at BYTE_BETA=16.

Parameter variant of phase_b2_alpha_with_beta16. With the BETA=16 fix
confirmed, how does C2 (and C1) scale with pool size? Real-world agent
memory may have pool of 10K-1M entries; we've only tested 1024.

Sweep POOL_SIZE in {256, 1024, 4096, 16384}. Note: Phase A's pool is
populated during first-epoch training; we need to retrain Phase A at
each pool size since pool_used depends on training trajectory.

Pre-registered:
- Larger pool should give better BWT (more A-knowledge retained).
- C2 should track C1 at all pool sizes (BETA=16 robustness).
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import torch


torch.set_float32_matmul_precision("high")

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
SEED = 17
VOCAB_SIZE = 256
PAD_BYTE = 0
K = 4
BETA_RETRIEVAL = 8.0
BYTE_BETA = 16.0
BATCH_SIZE = 64
ALPHA = 0.3
MAX_EPOCHS = 15
RELU_B = 0.5
N = 4096
DELTA_RULE_ALPHA = 0.3
DELTA_RULE_DECAY = 1e-4
POOL_SIZES = [256, 1024, 4096, 16384]


def _say(msg: str) -> None:
    print(msg, flush=True)


def load_corpus_a() -> bytes:
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


def shuffle_bytes(data: bytes, seed: int) -> bytes:
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


def predict_pool_classical(ctxs, pool_vecs, pool_labels, pool_used, beta, n):
    B = ctxs.shape[0]
    if pool_used == 0:
        return torch.full((VOCAB_SIZE, B), 1.0 / VOCAB_SIZE, device=ctxs.device)
    active = pool_vecs[:pool_used]
    labels = pool_labels[:pool_used]
    sims = (active @ ctxs.T) / n
    weights = torch.softmax(beta * sims, dim=0)
    P_retr = torch.zeros(VOCAB_SIZE, B, device=ctxs.device)
    P_retr.scatter_add_(0, labels.unsqueeze(1).expand(-1, B), weights)
    return P_retr


def predict_pool_vsa(ctxs, vsa_bundles, vsa_used, target_pos, byte_atoms,
                    beta_retrieval, beta_byte, n):
    B = ctxs.shape[0]
    if vsa_used == 0:
        return torch.full((VOCAB_SIZE, B), 1.0 / VOCAB_SIZE, device=ctxs.device)
    active = vsa_bundles[:vsa_used]
    sims = (active @ ctxs.T) / n
    weights = torch.softmax(beta_retrieval * sims, dim=0)
    target_estimates = active * target_pos.unsqueeze(0)
    byte_scores = (target_estimates @ byte_atoms.T) / n
    P_byte_per_entry = torch.softmax(beta_byte * byte_scores, dim=1)
    return P_byte_per_entry.T @ weights


def build_vsa_pool(pool_vecs, pool_labels, pool_used, byte_atoms, target_pos):
    if pool_used == 0:
        return torch.zeros_like(pool_vecs)
    target_atoms = byte_atoms[pool_labels[:pool_used]]
    return pool_vecs[:pool_used] + target_atoms * target_pos.unsqueeze(0)


def prepare_test_tensors(test_bytes_bytes, byte_atoms, pos_atoms):
    pad = bytes([PAD_BYTE]) * K
    padded = pad + test_bytes_bytes
    T = len(padded) - K
    bs_tensor = torch.tensor(list(padded), dtype=torch.long).to(DEVICE)
    offsets = torch.arange(K - 1, -1, -1, device=DEVICE)
    pos = torch.arange(T, device=DEVICE)
    idx = bs_tensor[pos.unsqueeze(1) + offsets.unsqueeze(0)]
    tgts = bs_tensor[pos + K]
    return idx, tgts


def run_one_pool_size(pool_size, byte_atoms, pos_atoms, target_pos,
                     train_a, train_b, test_a):
    W = torch.zeros((N, N), dtype=torch.float32, device=DEVICE)
    pool_vecs = torch.zeros((pool_size, N), dtype=torch.float32, device=DEVICE)
    pool_labels = torch.zeros(pool_size, dtype=torch.long, device=DEVICE)
    pool_used = 0
    pool_idx = 0
    arange_b = torch.arange(BATCH_SIZE, device=DEVICE)
    pad = bytes([PAD_BYTE]) * K

    # Phase A
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
                P = torch.softmax(BETA_RETRIEVAL * sims, dim=0)
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

    test_a_idx, test_a_targets = prepare_test_tensors(test_a, byte_atoms, pos_atoms)
    vsa_bundles = build_vsa_pool(pool_vecs, pool_labels, pool_used, byte_atoms, target_pos)

    def eval_all(W_local):
        T_test = test_a_idx.shape[0]
        bits_c1 = 0.0
        bits_c2 = 0.0
        for bs in range(0, T_test, BATCH_SIZE):
            be = min(bs + BATCH_SIZE, T_test)
            ctxs = build_ctx_bundles_bsc(byte_atoms, pos_atoms, test_a_idx[bs:be])
            P_W = predict_W(W_local, ctxs, byte_atoms, BETA_RETRIEVAL, N)
            tgts = test_a_targets[bs:be]
            P_c = predict_pool_classical(ctxs, pool_vecs, pool_labels, pool_used, BETA_RETRIEVAL, N)
            P_1 = ALPHA * P_c + (1 - ALPHA) * P_W
            bits_c1 += float(-torch.log2(P_1.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)).sum())
            P_v = predict_pool_vsa(ctxs, vsa_bundles, pool_used, target_pos, byte_atoms,
                                   BETA_RETRIEVAL, BYTE_BETA, N)
            P_2 = ALPHA * P_v + (1 - ALPHA) * P_W
            bits_c2 += float(-torch.log2(P_2.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)).sum())
        return bits_c1 / T_test, bits_c2 / T_test

    pre_c1, pre_c2 = eval_all(W)

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
                P = torch.softmax(BETA_RETRIEVAL * sims, dim=0)
                target_atoms_b = byte_atoms[tgt_batch]
                predicted = (P.T @ byte_atoms)
                residual = target_atoms_b - predicted
                dW = (residual.T @ ctxs) / N
                W.mul_(1.0 - DELTA_RULE_DECAY)
                W.add_(dW, alpha=DELTA_RULE_ALPHA)

    post_c1, post_c2 = eval_all(W)
    return {"pool_size": pool_size, "pool_used": pool_used,
           "pre_c1": pre_c1, "pre_c2": pre_c2,
           "post_c1": post_c1, "post_c2": post_c2,
           "gap_post": post_c1 - post_c2}


def main():
    _say(f"Wave 14.B Phase B.2 POOL_SIZE sweep at BYTE_BETA={BYTE_BETA}")
    _say(f"  Sweep: {POOL_SIZES}")

    corpus_a = load_corpus_a()
    corpus_b = shuffle_bytes(corpus_a, seed=SEED + 1)
    split = int(0.8 * len(corpus_a))
    train_a, test_a = corpus_a[:split], corpus_a[split:]
    train_b = corpus_b[:int(0.8 * len(corpus_b))]

    gen = torch.Generator().manual_seed(SEED)
    byte_atoms = make_bsc_atoms(VOCAB_SIZE, N, gen).to(DEVICE)
    pos_atoms = make_bsc_atoms(K, N, gen).to(DEVICE)
    target_pos_gen = torch.Generator().manual_seed(SEED + 99)
    target_pos_bits = torch.randint(0, 2, (N,), generator=target_pos_gen)
    target_pos = (target_pos_bits * 2 - 1).to(torch.float32).to(DEVICE)

    results = []
    t_start = time.perf_counter()
    _say(f"\n  {'pool':>7} | {'pool_used':>10} | {'post C1':>8} | {'post C2':>8} | {'gap':>8} | {'wall':>5}")
    _say(f"  {'-'*7}-+-{'-'*10}-+-{'-'*8}-+-{'-'*8}-+-{'-'*8}-+-{'-'*5}")
    for ps in POOL_SIZES:
        t0 = time.perf_counter()
        r = run_one_pool_size(ps, byte_atoms, pos_atoms, target_pos, train_a, train_b, test_a)
        dt = time.perf_counter() - t0
        _say(f"  {ps:>7} | {r['pool_used']:>10} | {r['post_c1']:>8.4f} | {r['post_c2']:>8.4f} | "
             f"{r['gap_post']:>+8.4f} | {dt:>4.0f}s")
        results.append(r)

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_phase_b2_pool_size_sweep"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps(
        {"BYTE_BETA": BYTE_BETA, "pool_sizes": POOL_SIZES, "results": results,
         "elapsed_s": time.perf_counter() - t_start},
        indent=2, default=str))
    _say(f"\nWrote {out_dir / 'metrics.json'}")


if __name__ == "__main__":
    main()
