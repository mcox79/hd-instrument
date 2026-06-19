"""MIR canonical rescue: literature-faithful Aljundi 2019 recipe.

Per the MIR-loses-to-random research agent: our first MIR test was
4 axes off from the canonical recipe:
1. Soft-MIR (top-4K-random) instead of DETERMINISTIC top-K
2. Cached every 5 batches instead of EVERY BATCH
3. 50% replay ratio instead of 10-20%
4. 15-epoch cycling instead of SINGLE-PASS

This script restores all four canonical conditions. If MIR still loses
to random, the substrate is the issue. Otherwise, our first result
was just testing a degraded MIR variant.

Falsification: MIR-canonical beats random replay (at single-pass, 20%)
by >= 0.05 bpc.

This is THE definitive test of whether closed-loop replay priority
is viable on our substrate.
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
RELU_B = 0.5
N = 4096
DELTA_RULE_ALPHA = 0.3
DELTA_RULE_DECAY = 1e-4

# Phase A trains 15 epochs (build W and pool)
PHASE_A_EPOCHS = 15
# Phase B canonical: SINGLE-PASS
PHASE_B_EPOCHS_CANONICAL = 1
# Sweep against 15-epoch variant for direct comparison with first MIR run
PHASE_B_EPOCHS_MULTI = 15

REPLAY_FRACTION_CANONICAL = 0.20  # 20% replay (Aljundi-like)
REPLAY_FRACTION_HIGH = 0.50       # for direct compare


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


def loss_under_W(W, ctxs, targets, byte_atoms):
    q = ctxs @ W.T
    q = shifted_relu(q, RELU_B)
    sims = (byte_atoms @ q.T) / N
    P = torch.softmax(BETA * sims, dim=0)
    p_true = P.gather(0, targets.unsqueeze(0)).squeeze(0).clamp(min=1e-12)
    return -torch.log(p_true)


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
    for epoch in range(1, PHASE_A_EPOCHS + 1):
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
                  pool_ctx, pool_lbl, mode, replay_fraction, num_epochs, seed):
    """mode in {'none', 'random', 'mir_canonical'}."""
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
    pool_used = pool_ctx.shape[0]

    for epoch in range(num_epochs):
        for batch_start in range(0, T_total, BATCH_SIZE):
            be = min(batch_start + BATCH_SIZE, T_total)
            idx_batch = train_idx[batch_start:be]
            tgt_batch = train_targets[batch_start:be]
            B = idx_batch.shape[0]
            ctxs_b = build_ctx(byte_atoms, pos_atoms, idx_batch)

            n_replay = max(1, int(B * replay_fraction))
            if mode == "none":
                ctxs = ctxs_b
                tgts = tgt_batch
            elif mode == "random":
                i = torch.randint(0, pool_used, (n_replay,), generator=gen).to(DEVICE)
                ctxs = torch.cat([ctxs_b, pool_ctx[i]], dim=0)
                tgts = torch.cat([tgt_batch, pool_lbl[i]], dim=0)
            elif mode == "mir_canonical":
                # CANONICAL ALJUNDI: deterministic top-K, re-score EVERY batch
                with torch.no_grad():
                    q = ctxs_b @ W.T
                    q = shifted_relu(q, RELU_B)
                    sims = (byte_atoms @ q.T) / N
                    P = torch.softmax(BETA * sims, dim=0)
                    target_atoms = byte_atoms[tgt_batch]
                    predicted = (P.T @ byte_atoms)
                    residual = target_atoms - predicted
                    dW = (residual.T @ ctxs_b) / N
                    W_prime = W * (1.0 - DELTA_RULE_DECAY) + DELTA_RULE_ALPHA * dW
                    loss_old = loss_under_W(W, pool_ctx, pool_lbl, byte_atoms)
                    loss_new = loss_under_W(W_prime, pool_ctx, pool_lbl, byte_atoms)
                    score = loss_new - loss_old
                    # DETERMINISTIC top-K (no random sub-sample)
                    _, top_idx = torch.topk(score, n_replay)
                replay_idx = top_idx
                ctxs = torch.cat([ctxs_b, pool_ctx[replay_idx]], dim=0)
                tgts = torch.cat([tgt_batch, pool_lbl[replay_idx]], dim=0)

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
    _say(f"MIR CANONICAL rescue: deterministic top-K, every-batch re-score, single-pass")

    corpus_a = load_corpus_a()
    corpus_b = shuffle_bytes(corpus_a, seed=SEED + 1)
    split = int(0.8 * len(corpus_a))
    train_a, test_a = corpus_a[:split], corpus_a[split:]
    train_b = corpus_b[:int(0.8 * len(corpus_b))]

    gen = torch.Generator().manual_seed(SEED)
    byte_atoms = make_bsc_atoms(VOCAB_SIZE, N, gen).to(DEVICE)
    pos_atoms = make_bsc_atoms(K, N, gen).to(DEVICE)

    _say(f"\n[Phase A] Training W and pool ({PHASE_A_EPOCHS} epochs)...")
    W_A, pool_A, labels_A, used_A = train_phase_a(byte_atoms, pos_atoms, train_a)
    bpc_a_initial = eval_bpc(W_A, byte_atoms, pos_atoms, test_a, pool_A, labels_A, used_A)
    _say(f"  Phase A bpc_a: {bpc_a_initial:.4f}")

    pool_ctx = pool_A[:used_A]
    pool_lbl = labels_A[:used_A]

    results = {}
    # CANONICAL conditions: single-pass Phase B, 20% replay
    _say(f"\n=== CANONICAL: single-pass Phase B, replay_fraction={REPLAY_FRACTION_CANONICAL} ===")
    for mode, name in [("none", "no_replay_canonical"),
                        ("random", "random_canonical"),
                        ("mir_canonical", "mir_canonical")]:
        _say(f"\n[{name}]")
        W_B = train_phase_b(W_A, byte_atoms, pos_atoms, train_b,
                            pool_ctx, pool_lbl, mode=mode,
                            replay_fraction=REPLAY_FRACTION_CANONICAL,
                            num_epochs=PHASE_B_EPOCHS_CANONICAL,
                            seed=SEED + 200)
        bpc_a = eval_bpc(W_B, byte_atoms, pos_atoms, test_a, pool_A, labels_A, used_A)
        bwt = bpc_a_initial - bpc_a
        results[name] = {"bpc_a_post": bpc_a, "bwt": bwt}
        _say(f"  {name:22s}: bpc_a_post={bpc_a:.4f}  BWT={bwt:+.4f}")

    # Direct compare: 15-epoch + 50% replay (same as first MIR run)
    _say(f"\n=== DIRECT COMPARE: 15-epoch, replay_fraction={REPLAY_FRACTION_HIGH} ===")
    for mode, name in [("random", "random_15ep_50pct"),
                        ("mir_canonical", "mir_canonical_15ep_50pct")]:
        _say(f"\n[{name}]")
        W_B = train_phase_b(W_A, byte_atoms, pos_atoms, train_b,
                            pool_ctx, pool_lbl, mode=mode,
                            replay_fraction=REPLAY_FRACTION_HIGH,
                            num_epochs=PHASE_B_EPOCHS_MULTI,
                            seed=SEED + 200)
        bpc_a = eval_bpc(W_B, byte_atoms, pos_atoms, test_a, pool_A, labels_A, used_A)
        bwt = bpc_a_initial - bpc_a
        results[name] = {"bpc_a_post": bpc_a, "bwt": bwt}
        _say(f"  {name:24s}: bpc_a_post={bpc_a:.4f}  BWT={bwt:+.4f}")

    _say(f"\n========= MIR CANONICAL VERDICT =========")
    rand_c = results["random_canonical"]["bwt"]
    mir_c = results["mir_canonical"]["bwt"]
    gap_canonical = mir_c - rand_c
    _say(f"  CANONICAL (single-pass, 20% replay):")
    _say(f"    random BWT:        {rand_c:+.4f}")
    _say(f"    mir_canonical BWT: {mir_c:+.4f}")
    _say(f"    Gap (MIR - random): {gap_canonical:+.4f}")

    rand_15 = results["random_15ep_50pct"]["bwt"]
    mir_15 = results["mir_canonical_15ep_50pct"]["bwt"]
    gap_15ep = mir_15 - rand_15
    _say(f"\n  DIRECT COMPARE (15-epoch, 50% replay):")
    _say(f"    random BWT:                 {rand_15:+.4f}")
    _say(f"    mir_canonical BWT (det):    {mir_15:+.4f}")
    _say(f"    Gap (MIR - random):         {gap_15ep:+.4f}")

    if gap_canonical >= 0.05:
        _say(f"\n  CANONICAL PASSES: MIR > random in literature-faithful regime")
        _say(f"  Soft-MIR-in-multi-epoch was the killer, not the substrate.")
    elif gap_canonical >= 0.02:
        _say(f"\n  CANONICAL PARTIAL: MIR shows real but small advantage in canonical regime")
    else:
        _say(f"\n  CANONICAL FAILS: substrate genuinely doesn't support priority replay")
        _say(f"  Prioritization door closes structurally.")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_mir_canonical"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps({
        "bpc_a_initial": bpc_a_initial,
        "results": results,
        "gap_canonical": gap_canonical,
        "gap_15ep": gap_15ep,
    }, indent=2))


if __name__ == "__main__":
    main()
