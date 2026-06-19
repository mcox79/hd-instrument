"""Wave 14.B Replay mechanism sweep -- followup to R7's surprise headline.

R7 found random replay during Phase B recovers +0.66 bpc BWT vs no-replay
(better than C3 factored's +0.098 win). Need to characterize:
- Does the win scale with replay ratio?
- Is random the best prioritization, or is some other scheme better?
- How does replay-buffer size matter?

Conditions tested:
- baseline (no replay)
- random replay at ratios {0.1, 0.25, 0.5, 0.75, 1.0}
- recency-weighted replay (oldest-first) at ratio 0.5
- recency-weighted replay (newest-first) at ratio 0.5
- loss-prioritized replay (replay entries where current W mispredicts) at ratio 0.5

Primary metric: BWT on test_a after Phase B. Secondary: bpc on test_b
(forward perf must not collapse).

Falsification: random@50% remains best, OR another scheme beats it by
>= 0.05 bpc BWT.
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
REPLAY_RATIOS = [0.0, 0.1, 0.25, 0.5, 0.75, 1.0]


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
                  pool_ctxs, pool_labels_, sampler, gen):
    W = W_start.clone()
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
            if sampler is not None:
                replay_idx = sampler(B, gen, W)
                if replay_idx is not None and len(replay_idx) > 0:
                    ctxs = torch.cat([ctxs_b, pool_ctxs[replay_idx]], dim=0)
                    tgts = torch.cat([tgt_batch, pool_labels_[replay_idx]], dim=0)
                else:
                    ctxs = ctxs_b
                    tgts = tgt_batch
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
    _say(f"Wave 14.B Replay Mechanism Sweep (followup to R7)")
    _say(f"  REPLAY_RATIOS: {REPLAY_RATIOS}")

    corpus_a = load_corpus_a()
    corpus_b = shuffle_bytes(corpus_a, seed=SEED + 1)
    split = int(0.8 * len(corpus_a))
    train_a, test_a = corpus_a[:split], corpus_a[split:]
    train_b, test_b = corpus_b[:int(0.8 * len(corpus_b))], corpus_b[int(0.8 * len(corpus_b)):]

    gen_atoms = torch.Generator().manual_seed(SEED)
    byte_atoms = make_bsc_atoms(VOCAB_SIZE, N, gen_atoms).to(DEVICE)
    pos_atoms = make_bsc_atoms(K, N, gen_atoms).to(DEVICE)

    _say(f"\n[Phase A] Training W and pool...")
    W_A, pool_A, labels_A, used_A = train_phase_a(byte_atoms, pos_atoms, train_a)
    bpc_a_initial = eval_bpc(W_A, byte_atoms, pos_atoms, test_a, pool_A, labels_A, used_A)
    _say(f"  Phase A bpc on test_a: {bpc_a_initial:.4f}")

    pool_ctx = pool_A[:used_A]
    pool_lbl = labels_A[:used_A]

    results = {}

    # === Replay ratio sweep (random) ===
    _say(f"\n[Replay ratio sweep: random]")
    for ratio in REPLAY_RATIOS:
        name = f"random_r{int(ratio*100):03d}"
        if ratio == 0.0:
            gen_b = torch.Generator().manual_seed(SEED + 200)
            W_B = train_phase_b(W_A, byte_atoms, pos_atoms, train_b,
                                pool_ctx, pool_lbl, sampler=None, gen=gen_b)
        else:
            def make_random_sampler(r):
                def sampler(B, g, W_now):
                    n = max(1, int(B * r))
                    i = torch.randint(0, used_A, (n,), generator=g, device='cpu').to(DEVICE)
                    return i
                return sampler
            gen_b = torch.Generator().manual_seed(SEED + 200 + int(ratio * 100))
            W_B = train_phase_b(W_A, byte_atoms, pos_atoms, train_b,
                                pool_ctx, pool_lbl,
                                sampler=make_random_sampler(ratio), gen=gen_b)
        bpc_a = eval_bpc(W_B, byte_atoms, pos_atoms, test_a, pool_A, labels_A, used_A)
        bpc_b = eval_bpc(W_B, byte_atoms, pos_atoms, test_b, pool_A, labels_A, used_A)
        bwt = bpc_a_initial - bpc_a
        results[name] = {"bpc_a_post": bpc_a, "bpc_b_post": bpc_b, "bwt": bwt}
        _say(f"  {name:18s}: bpc_a_post={bpc_a:.4f}  bpc_b_post={bpc_b:.4f}  BWT={bwt:+.4f}")

    # === Other prioritization schemes at ratio 0.5 ===
    _say(f"\n[Other prioritization schemes at ratio=0.5]")

    # Recency-weighted: oldest first (older entries replayed more)
    def make_recency_old(r):
        def sampler(B, g, W_now):
            n = max(1, int(B * r))
            # Weighted toward index 0 (oldest)
            weights = torch.linspace(1.0, 0.1, used_A, device=DEVICE)
            i = torch.multinomial(weights, n, replacement=True, generator=torch.Generator().manual_seed(g.initial_seed() + 1)).to(DEVICE) \
                if False else torch.multinomial(weights, n, replacement=True).to(DEVICE)
            return i
        return sampler
    def make_recency_new(r):
        def sampler(B, g, W_now):
            n = max(1, int(B * r))
            weights = torch.linspace(0.1, 1.0, used_A, device=DEVICE)
            i = torch.multinomial(weights, n, replacement=True).to(DEVICE)
            return i
        return sampler
    def make_loss_priority(r):
        def sampler(B, g, W_now):
            n = max(1, int(B * r))
            with torch.no_grad():
                q = pool_ctx @ W_now.T
                q = shifted_relu(q, RELU_B)
                sims = (byte_atoms @ q.T) / N
                P_pred = torch.softmax(BETA * sims, dim=0)
                p_true = P_pred.gather(0, pool_lbl.unsqueeze(0)).squeeze(0).clamp(min=1e-12)
                loss = -torch.log(p_true)
            weights = loss / (loss.sum() + 1e-12)
            i = torch.multinomial(weights, n, replacement=True).to(DEVICE)
            return i
        return sampler

    for name, sampler in [("recency_oldest_r050", make_recency_old(0.5)),
                          ("recency_newest_r050", make_recency_new(0.5)),
                          ("loss_priority_r050", make_loss_priority(0.5))]:
        gen_b = torch.Generator().manual_seed(SEED + 300)
        W_B = train_phase_b(W_A, byte_atoms, pos_atoms, train_b,
                            pool_ctx, pool_lbl, sampler=sampler, gen=gen_b)
        bpc_a = eval_bpc(W_B, byte_atoms, pos_atoms, test_a, pool_A, labels_A, used_A)
        bpc_b = eval_bpc(W_B, byte_atoms, pos_atoms, test_b, pool_A, labels_A, used_A)
        bwt = bpc_a_initial - bpc_a
        results[name] = {"bpc_a_post": bpc_a, "bpc_b_post": bpc_b, "bwt": bwt}
        _say(f"  {name:22s}: bpc_a_post={bpc_a:.4f}  bpc_b_post={bpc_b:.4f}  BWT={bwt:+.4f}")

    _say(f"\n========= REPLAY SWEEP VERDICT =========")
    # Best BWT
    best = max(results.items(), key=lambda kv: kv[1]["bwt"])
    baseline_bwt = results["random_r000"]["bwt"]
    _say(f"  Best BWT condition: {best[0]} = {best[1]['bwt']:+.4f}  "
         f"(baseline no-replay BWT = {baseline_bwt:+.4f})")
    _say(f"  Recovery vs baseline: {best[1]['bwt'] - baseline_bwt:+.4f} bpc")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_replay_mechanism_sweep"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps({
        "bpc_a_initial": bpc_a_initial,
        "REPLAY_RATIOS": REPLAY_RATIOS,
        "results": results,
    }, indent=2))


if __name__ == "__main__":
    main()
