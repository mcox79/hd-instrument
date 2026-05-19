"""Wave 14.B R1: Modern Hopfield retrieval over the pool (Ramsauer 2021).

Backlog R1 -- predicted 0.10-0.20 bpc payoff at our scale.

Standard retrieval: weights = softmax(beta * cosine(query, pool)), one-shot.
Modern Hopfield (Ramsauer): iterate
    xi_{t+1} = X^T * softmax(beta * X * xi_t)
for T_STEPS until convergence. The retrieval is the final fixed-point xi.
The iterative refinement saturates similarities (so the weighted average
approaches the nearest stored memory) without the brittleness of hard NN.

This is theorem-untouched. The redundancy theorem covered the CONCEPT
score against same pool. This changes the RETRIEVAL ITSELF.

R1 falsification: TRUE iff post-shift bpc improves by >= 0.05 bpc vs
the one-shot baseline (which is what current C1 / C3-factored uses).
"""

from __future__ import annotations

import json
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
POOL_SIZE = 1024
ALPHA = 0.3
MAX_EPOCHS = 15
RELU_B = 0.5
N = 4096
DELTA_RULE_ALPHA = 0.3
DELTA_RULE_DECAY = 1e-4

# Modern Hopfield params
HOPFIELD_BETAS = [4.0, 8.0, 16.0, 32.0]
HOPFIELD_STEPS = [1, 2, 4, 8]


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


def hopfield_retrieve(query, pool_vecs, pool_labels, beta, steps, n):
    """Iterative modern-Hopfield retrieval. Returns P_retr (VOCAB, B)."""
    xi = query.clone()  # (B, N)
    X = pool_vecs       # (P, N)
    for _ in range(steps):
        sims = (X @ xi.T) / n  # (P, B)
        weights = torch.softmax(beta * sims, dim=0)  # (P, B)
        xi = (X.T @ weights).T  # (B, N)
    # final retrieval weights
    sims = (X @ xi.T) / n
    weights = torch.softmax(beta * sims, dim=0)
    P_retr = torch.zeros(VOCAB_SIZE, xi.shape[0], device=DEVICE)
    P_retr.scatter_add_(0, pool_labels.unsqueeze(1).expand(-1, xi.shape[0]), weights)
    return P_retr


def train_phase_a(byte_atoms, pos_atoms, train_bytes):
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


def eval_with_hopfield(W, byte_atoms, pos_atoms, test_bytes, pool_vecs, pool_labels,
                       pool_used, hopfield_beta, hopfield_steps):
    pad = bytes([PAD_BYTE]) * K
    padded = pad + test_bytes
    T = len(padded) - K
    bt = torch.tensor(list(padded), dtype=torch.long).to(DEVICE)
    offsets = torch.arange(K - 1, -1, -1, device=DEVICE)
    pos = torch.arange(T, device=DEVICE)
    idx_all = bt[pos.unsqueeze(1) + offsets.unsqueeze(0)]
    tgts_all = bt[pos + K]
    total = 0.0
    active = pool_vecs[:pool_used]
    labels = pool_labels[:pool_used]
    for bs in range(0, T, BATCH_SIZE):
        be = min(bs + BATCH_SIZE, T)
        idx_b = idx_all[bs:be]
        tgts = tgts_all[bs:be]
        ctxs = build_ctx(byte_atoms, pos_atoms, idx_b)
        P_W = predict_W(W, ctxs, byte_atoms, BETA, N)
        if hopfield_steps == 0:
            # one-shot baseline (current C1)
            sims = (active @ ctxs.T) / N
            weights = torch.softmax(hopfield_beta * sims, dim=0)
            P_retr = torch.zeros(VOCAB_SIZE, ctxs.shape[0], device=DEVICE)
            P_retr.scatter_add_(0, labels.unsqueeze(1).expand(-1, ctxs.shape[0]), weights)
        else:
            P_retr = hopfield_retrieve(ctxs, active, labels, hopfield_beta, hopfield_steps, N)
        P = ALPHA * P_retr + (1 - ALPHA) * P_W
        p_true = P.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)
        total += float(-torch.log2(p_true).sum())
    return total / max(T, 1)


def main():
    _say(f"Wave 14.B R1: Modern Hopfield retrieval (Ramsauer 2021)")
    _say(f"  beta grid: {HOPFIELD_BETAS}")
    _say(f"  steps grid: {HOPFIELD_STEPS}")

    corpus_a = load_corpus_a()
    corpus_b = shuffle_bytes(corpus_a, seed=SEED + 1)
    split = int(0.8 * len(corpus_a))
    train_a, test_a = corpus_a[:split], corpus_a[split:]
    train_b = corpus_b[:int(0.8 * len(corpus_b))]

    gen = torch.Generator().manual_seed(SEED)
    byte_atoms = make_bsc_atoms(VOCAB_SIZE, N, gen).to(DEVICE)
    pos_atoms = make_bsc_atoms(K, N, gen).to(DEVICE)

    _say(f"\n[Phase A] Training W and pool...")
    W_A, pool_A, labels_A, used_A = train_phase_a(byte_atoms, pos_atoms, train_a)

    _say(f"\n[Pre-shift] Modern-Hopfield sweep on test_a...")
    baseline_pre = eval_with_hopfield(W_A, byte_atoms, pos_atoms, test_a,
                                      pool_A, labels_A, used_A,
                                      hopfield_beta=BETA, hopfield_steps=0)
    _say(f"  one-shot (current C1) bpc: {baseline_pre:.4f}")
    pre_grid = {}
    for hb in HOPFIELD_BETAS:
        for hs in HOPFIELD_STEPS:
            bpc = eval_with_hopfield(W_A, byte_atoms, pos_atoms, test_a,
                                     pool_A, labels_A, used_A, hb, hs)
            pre_grid[(hb, hs)] = bpc
            _say(f"  beta={hb:5.1f} steps={hs} bpc={bpc:.4f}  delta={baseline_pre-bpc:+.4f}")

    # Phase B
    _say(f"\n[Phase B] Continual training on B...")
    W_AB = W_A.clone()
    pad = bytes([PAD_BYTE]) * K
    padded_b = pad + train_b
    T_total = len(padded_b) - K
    bt = torch.tensor(list(padded_b), dtype=torch.long).to(DEVICE)
    offsets = torch.arange(K - 1, -1, -1, device=DEVICE)
    pos = torch.arange(T_total, device=DEVICE)
    train_b_idx = bt[pos.unsqueeze(1) + offsets.unsqueeze(0)]
    train_b_tgts = bt[pos + K]
    for epoch in range(MAX_EPOCHS):
        for batch_start in range(0, T_total, BATCH_SIZE):
            be = min(batch_start + BATCH_SIZE, T_total)
            idx_batch = train_b_idx[batch_start:be]
            tgt_batch = train_b_tgts[batch_start:be]
            ctxs = build_ctx(byte_atoms, pos_atoms, idx_batch)
            with torch.no_grad():
                q = ctxs @ W_AB.T
                q = shifted_relu(q, RELU_B)
                sims = (byte_atoms @ q.T) / N
                P = torch.softmax(BETA * sims, dim=0)
                target_atoms = byte_atoms[tgt_batch]
                predicted = (P.T @ byte_atoms)
                residual = target_atoms - predicted
                dW = (residual.T @ ctxs) / N
                W_AB.mul_(1.0 - DELTA_RULE_DECAY)
                W_AB.add_(dW, alpha=DELTA_RULE_ALPHA)

    _say(f"\n[Post-shift] Modern-Hopfield sweep on test_a (BWT)...")
    baseline_post = eval_with_hopfield(W_AB, byte_atoms, pos_atoms, test_a,
                                       pool_A, labels_A, used_A,
                                       hopfield_beta=BETA, hopfield_steps=0)
    _say(f"  one-shot (current C1) bpc: {baseline_post:.4f}")
    post_grid = {}
    for hb in HOPFIELD_BETAS:
        for hs in HOPFIELD_STEPS:
            bpc = eval_with_hopfield(W_AB, byte_atoms, pos_atoms, test_a,
                                     pool_A, labels_A, used_A, hb, hs)
            post_grid[(hb, hs)] = bpc
            _say(f"  beta={hb:5.1f} steps={hs} bpc={bpc:.4f}  delta={baseline_post-bpc:+.4f}")

    _say(f"\n========= R1 VERDICT =========")
    pre_best = min((v, k) for k, v in pre_grid.items())
    post_best = min((v, k) for k, v in post_grid.items())
    _say(f"  Pre-shift one-shot:  {baseline_pre:.4f}")
    _say(f"  Pre-shift best Hopf: {pre_best[0]:.4f} at beta={pre_best[1][0]}, steps={pre_best[1][1]}  "
         f"(gain {baseline_pre-pre_best[0]:+.4f})")
    _say(f"  Post-shift one-shot: {baseline_post:.4f}")
    _say(f"  Post-shift best Hopf:{post_best[0]:.4f} at beta={post_best[1][0]}, steps={post_best[1][1]}  "
         f"(gain {baseline_post-post_best[0]:+.4f})")

    post_gain = baseline_post - post_best[0]
    if post_gain >= 0.05:
        _say(f"  R1 PASSES: modern Hopfield retrieval beats one-shot by {post_gain:+.4f} bpc post-shift.")
    else:
        _say(f"  R1 FAILS: best Hopfield gain {post_gain:+.4f} < 0.05 threshold.")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_r1_modern_hopfield"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps({
        "HOPFIELD_BETAS": HOPFIELD_BETAS,
        "HOPFIELD_STEPS": HOPFIELD_STEPS,
        "pre_one_shot": baseline_pre,
        "post_one_shot": baseline_post,
        "pre_grid": {f"{k[0]}_{k[1]}": v for k, v in pre_grid.items()},
        "post_grid": {f"{k[0]}_{k[1]}": v for k, v in post_grid.items()},
    }, indent=2))


if __name__ == "__main__":
    main()
