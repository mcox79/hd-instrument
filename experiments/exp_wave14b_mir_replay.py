"""A7 rescue: MIR (Maximally Interfered Retrieval) replay -- closed-loop priority.

Per research-agent recommendation: literature-strongest method for
small-buffer supervised CL (Aljundi 2019 NeurIPS). Closed-loop by
construction: priority = entries whose loss MOST increases under the
proposed update.

Our linear delta-rule makes the virtual W' free:
  W' = W + alpha * residual_B.T @ ctxs_B / N

For each pool entry i:
  score_i = loss(c_i, W') - loss(c_i, W)
Pick top-K positive (most-increased loss) for replay.

Compare to random replay (control) and no-replay baseline.

Falsifier: TRUE iff MIR beats random by >= 0.10 bpc on BWT.
If MIR loses to random, prioritization door closes for this substrate.
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
REPLAY_FRACTION = 0.5
MIR_RESCORE_EVERY_N_BATCHES = 5  # how often to re-rank pool by MIR


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
    """Return per-entry log-loss given W."""
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
                  pool_ctx, pool_lbl, mode, seed):
    """mode in {'none', 'random', 'mir'}."""
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

    cached_mir_order = None
    batch_counter = 0

    for epoch in range(MAX_EPOCHS):
        for batch_start in range(0, T_total, BATCH_SIZE):
            be = min(batch_start + BATCH_SIZE, T_total)
            idx_batch = train_idx[batch_start:be]
            tgt_batch = train_targets[batch_start:be]
            B = idx_batch.shape[0]
            ctxs_b = build_ctx(byte_atoms, pos_atoms, idx_batch)

            if mode == "none":
                ctxs = ctxs_b
                tgts = tgt_batch
            elif mode == "random":
                n_replay = max(1, int(B * REPLAY_FRACTION))
                i = torch.randint(0, pool_used, (n_replay,), generator=gen).to(DEVICE)
                ctxs = torch.cat([ctxs_b, pool_ctx[i]], dim=0)
                tgts = torch.cat([tgt_batch, pool_lbl[i]], dim=0)
            elif mode == "mir":
                n_replay = max(1, int(B * REPLAY_FRACTION))
                # Re-score pool by virtual-update loss change every N batches
                if cached_mir_order is None or batch_counter % MIR_RESCORE_EVERY_N_BATCHES == 0:
                    # Compute virtual W' from current batch
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
                        # Loss change for each pool entry
                        loss_old = loss_under_W(W, pool_ctx, pool_lbl, byte_atoms)
                        loss_new = loss_under_W(W_prime, pool_ctx, pool_lbl, byte_atoms)
                        score = loss_new - loss_old  # positive = interfered with
                        cached_mir_order = torch.argsort(score, descending=True)
                # Sample top-n_replay from interfered entries with some randomness
                # (top quartile + random within it for robustness)
                top_set = cached_mir_order[:max(n_replay * 4, n_replay)]
                i_local = torch.randint(0, len(top_set), (n_replay,), generator=gen).to(DEVICE)
                replay_idx = top_set[i_local]
                ctxs = torch.cat([ctxs_b, pool_ctx[replay_idx]], dim=0)
                tgts = torch.cat([tgt_batch, pool_lbl[replay_idx]], dim=0)
                batch_counter += 1

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
    _say(f"A7 MIR replay: closed-loop priority")

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
    bpc_a_initial = eval_bpc(W_A, byte_atoms, pos_atoms, test_a, pool_A, labels_A, used_A)
    _say(f"  Phase A bpc_a: {bpc_a_initial:.4f}")

    pool_ctx = pool_A[:used_A]
    pool_lbl = labels_A[:used_A]

    results = {}
    for mode, name in [("none", "no_replay"), ("random", "random_replay"), ("mir", "mir_replay")]:
        _say(f"\n[Phase B, {name}]")
        W_B = train_phase_b(W_A, byte_atoms, pos_atoms, train_b,
                            pool_ctx, pool_lbl, mode=mode, seed=SEED + 200)
        bpc_a = eval_bpc(W_B, byte_atoms, pos_atoms, test_a, pool_A, labels_A, used_A)
        bwt = bpc_a_initial - bpc_a
        results[name] = {"bpc_a_post": bpc_a, "bwt": bwt}
        _say(f"  {name:18s}: bpc_a_post={bpc_a:.4f}  BWT={bwt:+.4f}")

    _say(f"\n========= A7 MIR VERDICT =========")
    bwt_random = results["random_replay"]["bwt"]
    bwt_mir = results["mir_replay"]["bwt"]
    bwt_no = results["no_replay"]["bwt"]
    _say(f"  no_replay BWT:     {bwt_no:+.4f}")
    _say(f"  random_replay BWT: {bwt_random:+.4f}")
    _say(f"  mir_replay BWT:    {bwt_mir:+.4f}")
    _say(f"  MIR vs random:     {bwt_mir - bwt_random:+.4f}")
    if bwt_mir - bwt_random >= 0.10:
        _say(f"  A7 PASSES: MIR beats random by >= 0.10 bpc BWT")
    elif bwt_mir - bwt_random >= 0.03:
        _say(f"  A7 PARTIAL: MIR beats random by some margin")
    else:
        _say(f"  A7 FAILS: MIR doesn't beat random; prioritization door closes")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_mir_replay"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps({
        "bpc_a_initial": bpc_a_initial,
        "REPLAY_FRACTION": REPLAY_FRACTION,
        "MIR_RESCORE_EVERY_N_BATCHES": MIR_RESCORE_EVERY_N_BATCHES,
        "results": results,
    }, indent=2))


if __name__ == "__main__":
    main()
