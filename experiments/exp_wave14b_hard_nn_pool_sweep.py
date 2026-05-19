"""Wave 14.B hard-NN retrieval pool sweep — alternative to softmax annealing.

The pool-size theory survey predicted: hard nearest-neighbor retrieval is
monotone non-decreasing in P (argmax invariant to worse entries). Test
directly: replace softmax-weighted pool retrieval with hard top-1
(one-hot on the closest entry).

If hard-NN gives monotone improvement with P (no inverted-U), we have
TWO valid production strategies:
A) Soft retrieval + temperature scheduling (the annealing fix)
B) Hard retrieval (no temperature tuning needed)

Comparison: same Phase B.2 setup, but pool retrieval uses argmax+one-hot
instead of softmax.
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
BETA = 8.0
BYTE_BETA = 16.0
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


def predict_pool_hard_nn(ctxs, pool_vecs, pool_labels, pool_used, n):
    """Hard nearest-neighbor: top-1 entry by cosine, one-hot label."""
    B = ctxs.shape[0]
    if pool_used == 0:
        return torch.full((VOCAB_SIZE, B), 1.0 / VOCAB_SIZE, device=ctxs.device)
    active = pool_vecs[:pool_used]
    labels = pool_labels[:pool_used]
    sims = (active @ ctxs.T) / n  # (P, B)
    top_idx = sims.argmax(dim=0)  # (B,)
    top_labels = labels[top_idx]  # (B,)
    P_retr = torch.zeros(VOCAB_SIZE, B, device=ctxs.device)
    P_retr.scatter_(0, top_labels.unsqueeze(0), 1.0)
    # Smooth slightly to avoid log(0) on miss
    P_retr = P_retr * 0.99 + (1.0 - 0.99) / VOCAB_SIZE
    return P_retr


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


def eval_all(W, byte_atoms, pos_atoms, test_idx, test_targets,
            pool_vecs, pool_labels, pool_used, alpha):
    T_test = test_idx.shape[0]
    bits = {"c1_soft": 0.0, "c1_hard": 0.0}
    for bs in range(0, T_test, BATCH_SIZE):
        be = min(bs + BATCH_SIZE, T_test)
        ctxs = build_ctx_bundles_bsc(byte_atoms, pos_atoms, test_idx[bs:be])
        P_W = predict_W(W, ctxs, byte_atoms, BETA, N)
        tgts = test_targets[bs:be]
        P_soft = predict_pool_classical(ctxs, pool_vecs, pool_labels, pool_used, BETA, N)
        P_1s = alpha * P_soft + (1 - alpha) * P_W
        bits["c1_soft"] += float(-torch.log2(P_1s.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)).sum())
        P_hard = predict_pool_hard_nn(ctxs, pool_vecs, pool_labels, pool_used, N)
        P_1h = alpha * P_hard + (1 - alpha) * P_W
        bits["c1_hard"] += float(-torch.log2(P_1h.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)).sum())
    return {k: v / max(T_test, 1) for k, v in bits.items()}


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


def run_one_pool_size(pool_size, byte_atoms, pos_atoms, train_a, train_b, test_a):
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

    test_a_idx, test_a_targets = prepare_test_tensors(test_a, byte_atoms, pos_atoms)
    pre = eval_all(W, byte_atoms, pos_atoms, test_a_idx, test_a_targets,
                  pool_vecs, pool_labels, pool_used, ALPHA)

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

    post = eval_all(W, byte_atoms, pos_atoms, test_a_idx, test_a_targets,
                   pool_vecs, pool_labels, pool_used, ALPHA)
    return {"pool_size": pool_size, "pool_used": pool_used,
           "pre": pre, "post": post}


def main():
    _say(f"Wave 14.B hard-NN retrieval pool sweep")
    _say(f"  Compares soft (fixed beta=8) vs hard (top-1) retrieval across P")

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
    _say(f"\n  {'pool':>7} | {'soft post':>9} | {'hard post':>9} | {'diff':>7} | {'wall':>5}")
    _say(f"  {'-'*7}-+-{'-'*9}-+-{'-'*9}-+-{'-'*7}-+-{'-'*5}")
    for ps in POOL_SIZES:
        t0 = time.perf_counter()
        r = run_one_pool_size(ps, byte_atoms, pos_atoms, train_a, train_b, test_a)
        dt = time.perf_counter() - t0
        diff = r["post"]["c1_soft"] - r["post"]["c1_hard"]  # positive = hard better
        _say(f"  {ps:>7} | {r['post']['c1_soft']:>9.4f} | {r['post']['c1_hard']:>9.4f} | "
             f"{diff:>+7.4f} | {dt:>4.0f}s")
        results.append(r)

    _say(f"\n========= INTERPRETATION =========")
    # Check monotonicity of hard
    hards = [r["post"]["c1_hard"] for r in results]
    monotone = all(hards[i+1] <= hards[i] + 0.01 for i in range(len(hards)-1))
    if monotone:
        _say(f"  HARD-NN is MONOTONE (or close) in P. Confirms theory: argmax")
        _say(f"  retrieval doesn't suffer from softmax distractor catch-up.")
    else:
        _say(f"  Hard-NN also degrades — pool composition is the issue, not softmax.")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_hard_nn_pool_sweep"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps(
        {"pool_sizes": POOL_SIZES, "results": results,
         "elapsed_s": time.perf_counter() - t_start},
        indent=2, default=str))
    _say(f"\nWrote {out_dir / 'metrics.json'}")


if __name__ == "__main__":
    main()
