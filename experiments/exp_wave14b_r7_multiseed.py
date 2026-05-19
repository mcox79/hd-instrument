"""Multi-seed verification of R7's random-replay BWT result.

R7 showed random replay during Phase B recovers +0.66 bpc BWT vs no-replay.
Need to confirm this isn't a single-seed fluke before promoting to headline.

This is a CPU-friendly experiment: only 3 seeds, no concept extraction,
just the no-replay-vs-random-replay comparison.

Falsification: random replay's BWT recovery should be at least +0.30 bpc
in all 3 seeds (i.e. > 4 sigma if true variance is ~0.10).
"""

from __future__ import annotations

import json
from pathlib import Path

import torch


torch.set_float32_matmul_precision("high")

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
SEEDS = [17, 23, 31]
VOCAB_SIZE = 256
PAD_BYTE = 0
K = 4
BETA = 8.0
BYTE_BETA = 16.0
BATCH_SIZE = 64
POOL_SIZE = 1024
ALPHA = 0.3
MAX_EPOCHS = 15
RELU_B = 0.5
N = 4096
DELTA_RULE_ALPHA = 0.3
DELTA_RULE_DECAY = 1e-4
REPLAY_FRACTION = 0.5


def _say(msg):
    print(msg, flush=True)


def load_corpus_a():
    repo = Path(__file__).resolve().parent.parent
    files = [repo / "PLAN.md", repo / "NEXT_PHASE.md", repo / "README.md",
             repo / "PROGRESS.md", repo / "RESULTS.md", repo / "CLAUDE.md"]
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


def build_ctx(byte_atoms, pos_atoms, indices):
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


def train_phase_a(seed, byte_atoms, pos_atoms, train_bytes):
    W = torch.zeros((N, N), dtype=torch.float32, device=DEVICE)
    pool_vecs = torch.zeros((POOL_SIZE, N), dtype=torch.float32, device=DEVICE)
    pool_labels = torch.zeros(POOL_SIZE, dtype=torch.long, device=DEVICE)
    pool_idx = 0
    pool_used = 0
    arange_b = torch.arange(BATCH_SIZE, device=DEVICE)
    pad = bytes([PAD_BYTE]) * K
    padded = pad + train_bytes
    T_total = len(padded) - K
    bt = torch.tensor(list(padded), dtype=torch.long).to(DEVICE)
    offsets = torch.arange(K - 1, -1, -1, device=DEVICE)
    pos = torch.arange(T_total, device=DEVICE)
    train_idx = bt[pos.unsqueeze(1) + offsets.unsqueeze(0)]
    train_targets = bt[pos + K]
    for epoch in range(1, MAX_EPOCHS + 1):
        for batch_start in range(0, T_total, BATCH_SIZE):
            be = min(batch_start + BATCH_SIZE, T_total)
            idx_batch = train_idx[batch_start:be]
            tgt_batch = train_targets[batch_start:be]
            B = idx_batch.shape[0]
            ctxs = build_ctx(byte_atoms, pos_atoms, idx_batch)
            with torch.no_grad():
                q = ctxs @ W.T
                q = shifted_relu(q, RELU_B)
                sims = (byte_atoms @ q.T) / N
                P = torch.softmax(BETA * sims, dim=0)
                target_atoms = byte_atoms[tgt_batch]
                predicted = (P.T @ byte_atoms)
                residual = target_atoms - predicted
                dW = (residual.T @ ctxs) / N
                W.mul_(1.0 - DELTA_RULE_DECAY)
                W.add_(dW, alpha=DELTA_RULE_ALPHA)
                if epoch == 1:
                    dest = (pool_idx + arange_b[:B]) % POOL_SIZE
                    pool_vecs.index_copy_(0, dest, ctxs)
                    pool_labels.index_copy_(0, dest, tgt_batch)
                    pool_idx = (pool_idx + B) % POOL_SIZE
                    pool_used = min(pool_used + B, POOL_SIZE)
    return W, pool_vecs, pool_labels, pool_used


def train_phase_b(W_start, byte_atoms, pos_atoms, train_b,
                  pool_ctx, pool_lbl, pool_used, do_replay, seed):
    W = W_start.clone()
    gen = torch.Generator().manual_seed(seed)
    pad = bytes([PAD_BYTE]) * K
    padded = pad + train_b
    T_total = len(padded) - K
    bt = torch.tensor(list(padded), dtype=torch.long).to(DEVICE)
    offsets = torch.arange(K - 1, -1, -1, device=DEVICE)
    pos = torch.arange(T_total, device=DEVICE)
    train_idx = bt[pos.unsqueeze(1) + offsets.unsqueeze(0)]
    train_targets = bt[pos + K]
    for epoch in range(MAX_EPOCHS):
        for batch_start in range(0, T_total, BATCH_SIZE):
            be = min(batch_start + BATCH_SIZE, T_total)
            idx_batch = train_idx[batch_start:be]
            tgt_batch = train_targets[batch_start:be]
            B = idx_batch.shape[0]
            ctxs_b = build_ctx(byte_atoms, pos_atoms, idx_batch)
            if do_replay:
                n_replay = max(1, int(B * REPLAY_FRACTION))
                i = torch.randint(0, pool_used, (n_replay,), generator=gen).to(DEVICE)
                ctxs = torch.cat([ctxs_b, pool_ctx[i]], dim=0)
                tgts = torch.cat([tgt_batch, pool_lbl[i]], dim=0)
            else:
                ctxs = ctxs_b
                tgts = tgt_batch
            with torch.no_grad():
                q = ctxs @ W.T
                q = shifted_relu(q, RELU_B)
                sims = (byte_atoms @ q.T) / N
                P = torch.softmax(BETA * sims, dim=0)
                target_atoms = byte_atoms[tgts]
                predicted = (P.T @ byte_atoms)
                residual = target_atoms - predicted
                dW = (residual.T @ ctxs) / N
                W.mul_(1.0 - DELTA_RULE_DECAY)
                W.add_(dW, alpha=DELTA_RULE_ALPHA)
    return W


def eval_bpc(W, byte_atoms, pos_atoms, test_bytes, pool_vecs, pool_labels, pool_used):
    pad = bytes([PAD_BYTE]) * K
    padded = pad + test_bytes
    T = len(padded) - K
    bt = torch.tensor(list(padded), dtype=torch.long).to(DEVICE)
    offsets = torch.arange(K - 1, -1, -1, device=DEVICE)
    pos = torch.arange(T, device=DEVICE)
    idx = bt[pos.unsqueeze(1) + offsets.unsqueeze(0)]
    tgts = bt[pos + K]
    total = 0.0
    for bs in range(0, T, BATCH_SIZE):
        be = min(bs + BATCH_SIZE, T)
        idx_b = idx[bs:be]
        ctxs = build_ctx(byte_atoms, pos_atoms, idx_b)
        P_W = predict_W(W, ctxs, byte_atoms, BETA, N)
        active = pool_vecs[:pool_used]
        labels = pool_labels[:pool_used]
        sims = (active @ ctxs.T) / N
        weights = torch.softmax(BETA * sims, dim=0)
        P_retr = torch.zeros(VOCAB_SIZE, idx_b.shape[0], device=DEVICE)
        P_retr.scatter_add_(0, labels.unsqueeze(1).expand(-1, idx_b.shape[0]), weights)
        P = ALPHA * P_retr + (1 - ALPHA) * P_W
        p_true = P.gather(0, tgts[bs:be].unsqueeze(0)).squeeze(0).clamp(min=1e-12)
        total += float(-torch.log2(p_true).sum())
    return total / max(T, 1)


def main():
    _say(f"R7 multi-seed verification: random replay BWT consistency")
    _say(f"  Seeds: {SEEDS}  device: {DEVICE}")

    per_seed_results = []
    for seed in SEEDS:
        _say(f"\n=== SEED {seed} ===")
        corpus_a = load_corpus_a()
        corpus_b = shuffle_bytes(corpus_a, seed=seed + 1)
        split = int(0.8 * len(corpus_a))
        train_a, test_a = corpus_a[:split], corpus_a[split:]
        train_b = corpus_b[:int(0.8 * len(corpus_b))]

        gen_atoms = torch.Generator().manual_seed(seed)
        byte_atoms = make_bsc_atoms(VOCAB_SIZE, N, gen_atoms).to(DEVICE)
        pos_atoms = make_bsc_atoms(K, N, gen_atoms).to(DEVICE)

        W_A, pool_A, labels_A, used_A = train_phase_a(seed, byte_atoms, pos_atoms, train_a)
        bpc_a_initial = eval_bpc(W_A, byte_atoms, pos_atoms, test_a, pool_A, labels_A, used_A)
        _say(f"  Phase A bpc_a: {bpc_a_initial:.4f}")

        W_no = train_phase_b(W_A, byte_atoms, pos_atoms, train_b,
                             pool_A[:used_A], labels_A[:used_A], used_A,
                             do_replay=False, seed=seed + 100)
        W_re = train_phase_b(W_A, byte_atoms, pos_atoms, train_b,
                             pool_A[:used_A], labels_A[:used_A], used_A,
                             do_replay=True, seed=seed + 200)

        bpc_a_no = eval_bpc(W_no, byte_atoms, pos_atoms, test_a, pool_A, labels_A, used_A)
        bpc_a_re = eval_bpc(W_re, byte_atoms, pos_atoms, test_a, pool_A, labels_A, used_A)
        bwt_no = bpc_a_initial - bpc_a_no
        bwt_re = bpc_a_initial - bpc_a_re
        recovery = bwt_re - bwt_no
        _say(f"  no_replay bpc_a_post: {bpc_a_no:.4f} BWT: {bwt_no:+.4f}")
        _say(f"  random_replay bpc_a_post: {bpc_a_re:.4f} BWT: {bwt_re:+.4f}")
        _say(f"  recovery (random vs no-replay): {recovery:+.4f} bpc")
        per_seed_results.append({
            "seed": seed,
            "bpc_a_initial": bpc_a_initial,
            "bpc_a_no": bpc_a_no, "bwt_no": bwt_no,
            "bpc_a_re": bpc_a_re, "bwt_re": bwt_re,
            "recovery": recovery,
        })

    _say(f"\n========= MULTI-SEED VERDICT =========")
    recoveries = [r["recovery"] for r in per_seed_results]
    mean_rec = sum(recoveries) / len(recoveries)
    min_rec = min(recoveries)
    _say(f"  Per-seed recovery: {[f'{r:+.3f}' for r in recoveries]}")
    _say(f"  Mean recovery: {mean_rec:+.4f}  Min recovery: {min_rec:+.4f}")
    if min_rec >= 0.30:
        _say(f"  CONFIRMED: random replay recovers BWT by >= 0.30 in all seeds. Robust headline.")
    elif mean_rec >= 0.30:
        _say(f"  PROBABLE: mean recovery {mean_rec:+.4f} above threshold but one seed dropped.")
    else:
        _say(f"  REJECTED: mean recovery {mean_rec:+.4f} below threshold.")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_r7_multiseed"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps({
        "SEEDS": SEEDS, "REPLAY_FRACTION": REPLAY_FRACTION,
        "per_seed": per_seed_results,
        "mean_recovery": mean_rec,
        "min_recovery": min_rec,
    }, indent=2))


if __name__ == "__main__":
    main()
