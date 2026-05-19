"""MIR rescues A+B+C in one experiment.

Per the MIR-failure diagnosis research agent: MIR's priority on our
substrate collapses to cosine-to-current-batch, double-counting the
retrieval branch. Three falsifiable rescues:

A) Adversarial MIR: argmin Delta_loss (test if priority is inverted)
B) Cosine-deconfounded MIR: subtract <c_i, ctxs_b> confound
C) MIR + diversity thinning (top-2K then greedy farthest-first)

All four conditions (random control + A + B + C) run in single-pass
Phase B with 20% replay (canonical regime).

Decision matrix per agent:
- A wins: priority sign-inverted (sketchy)
- B wins: deconfounding rescues MIR -- ship deconfound
- C wins: diversity-thinning rescues MIR -- ship MIR+DPP
- None wins: priority replay impossible on this substrate (H3 confirmed)
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
PHASE_A_EPOCHS = 15
PHASE_B_EPOCHS = 1  # single-pass canonical
REPLAY_FRACTION = 0.20


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


def pick_replay_indices(W, ctxs_b, tgt_b, pool_ctx, pool_lbl, byte_atoms,
                        n_replay, mode, gen):
    pool_used = pool_ctx.shape[0]
    with torch.no_grad():
        q = ctxs_b @ W.T
        q = shifted_relu(q, RELU_B)
        sims = (byte_atoms @ q.T) / N
        P = torch.softmax(BETA * sims, dim=0)
        target_atoms = byte_atoms[tgt_b]
        predicted = (P.T @ byte_atoms)
        residual = target_atoms - predicted
        dW = (residual.T @ ctxs_b) / N
        W_prime = W * (1.0 - DELTA_RULE_DECAY) + DELTA_RULE_ALPHA * dW
        loss_old = loss_under_W(W, pool_ctx, pool_lbl, byte_atoms)
        loss_new = loss_under_W(W_prime, pool_ctx, pool_lbl, byte_atoms)
        score = loss_new - loss_old

        if mode == "random":
            return torch.randint(0, pool_used, (n_replay,), generator=gen).to(DEVICE)
        elif mode == "mir_det":
            # Standard deterministic top-K (canonical baseline reproduction)
            _, top_idx = torch.topk(score, n_replay)
            return top_idx
        elif mode == "adversarial":
            # Rescue A: argmin (least-interfered)
            _, top_idx = torch.topk(-score, n_replay)
            return top_idx
        elif mode == "deconfounded":
            # Rescue B: subtract cosine-to-batch confound
            sims_to_batch = (pool_ctx @ ctxs_b.T) / N  # (P, B)
            confound = sims_to_batch.mean(dim=1)
            score_std = score.std().clamp(min=1e-6)
            confound_std = confound.std().clamp(min=1e-6)
            score_clean = score - score_std * confound / confound_std
            _, top_idx = torch.topk(score_clean, n_replay)
            return top_idx
        elif mode == "diversity":
            # Rescue C: top-2K then greedy farthest-first
            _, cand_idx = torch.topk(score, min(2 * n_replay, pool_used))
            cand_idx = cand_idx.tolist()
            chosen = [cand_idx[0]]
            remaining = list(cand_idx[1:])
            while len(chosen) < n_replay and remaining:
                chosen_ctxs = pool_ctx[torch.tensor(chosen, device=DEVICE)]
                rem_ctxs = pool_ctx[torch.tensor(remaining, device=DEVICE)]
                redund = (rem_ctxs @ chosen_ctxs.T).max(dim=1).values
                best_local = int(redund.argmin().item())
                chosen.append(remaining.pop(best_local))
            return torch.tensor(chosen[:n_replay], device=DEVICE)


def train_phase_b(W_start, byte_atoms, pos_atoms, train_b,
                  pool_ctx, pool_lbl, mode, seed):
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
    for epoch in range(PHASE_B_EPOCHS):
        for batch_start in range(0, T_total, BATCH_SIZE):
            be = min(batch_start + BATCH_SIZE, T_total)
            idx_batch = train_idx[batch_start:be]
            tgt_batch = train_targets[batch_start:be]
            B = idx_batch.shape[0]
            ctxs_b = build_ctx(byte_atoms, pos_atoms, idx_batch)
            n_replay = max(1, int(B * REPLAY_FRACTION))
            if mode == "none":
                ctxs = ctxs_b
                tgts = tgt_batch
            else:
                replay_idx = pick_replay_indices(W, ctxs_b, tgt_batch,
                                                 pool_ctx, pool_lbl, byte_atoms,
                                                 n_replay, mode, gen)
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
    _say(f"MIR rescues A+B+C: testing whether priority replay is salvageable")
    _say(f"  Single-pass Phase B, 20% replay, deterministic top-K")

    corpus_a = load_corpus_a()
    corpus_b = shuffle_bytes(corpus_a, seed=SEED + 1)
    split = int(0.8 * len(corpus_a))
    train_a, test_a = corpus_a[:split], corpus_a[split:]
    train_b = corpus_b[:int(0.8 * len(corpus_b))]

    gen = torch.Generator().manual_seed(SEED)
    byte_atoms = make_bsc_atoms(VOCAB_SIZE, N, gen).to(DEVICE)
    pos_atoms = make_bsc_atoms(K, N, gen).to(DEVICE)

    W_A, pool_A, labels_A, used_A = train_phase_a(byte_atoms, pos_atoms, train_a)
    bpc_a_initial = eval_bpc(W_A, byte_atoms, pos_atoms, test_a, pool_A, labels_A, used_A)
    _say(f"\nPhase A bpc_a: {bpc_a_initial:.4f}")

    pool_ctx = pool_A[:used_A]
    pool_lbl = labels_A[:used_A]
    results = {}

    for mode in ["none", "random", "mir_det", "adversarial", "deconfounded", "diversity"]:
        _say(f"\n[Phase B, mode={mode}]")
        W_B = train_phase_b(W_A, byte_atoms, pos_atoms, train_b,
                            pool_ctx, pool_lbl, mode=mode, seed=SEED + 200)
        bpc_a = eval_bpc(W_B, byte_atoms, pos_atoms, test_a, pool_A, labels_A, used_A)
        bwt = bpc_a_initial - bpc_a
        results[mode] = {"bpc_a_post": bpc_a, "bwt": bwt}
        _say(f"  {mode:14s}: bpc_a_post={bpc_a:.4f}  BWT={bwt:+.4f}")

    _say(f"\n========= MIR RESCUES VERDICT =========")
    rand = results["random"]["bwt"]
    _say(f"  random BWT:        {rand:+.4f}  (baseline)")
    for mode in ["mir_det", "adversarial", "deconfounded", "diversity"]:
        gap = results[mode]["bwt"] - rand
        sig = "PASS" if gap >= 0.05 else ("WEAK" if gap >= 0.02 else "FAIL")
        _say(f"  {mode:14s} BWT: {results[mode]['bwt']:+.4f}  gap_vs_random={gap:+.4f}  [{sig}]")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_mir_rescues"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps({
        "bpc_a_initial": bpc_a_initial,
        "REPLAY_FRACTION": REPLAY_FRACTION,
        "PHASE_B_EPOCHS": PHASE_B_EPOCHS,
        "results": results,
    }, indent=2))


if __name__ == "__main__":
    main()
