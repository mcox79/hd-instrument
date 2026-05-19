"""Stein prediction #1: replay at K=4 should HURT pre-shift bpc.

At K=4, B=5, bundle SNR (2B-1)/N ≈ 0.0022 -- low-noise regime. Random
replay injects W toward stale-A target -- pure bias under Stein's
shrinkage-dominance framework.

Test: train Phase A with REPLAY_FRACTION mixed in during training
itself (NOT Phase B). REPLAY_FRACTION in {0, 0.25, 0.5, 0.9}. Measure
PRE-SHIFT bpc on test_A (no Phase B at all).

Stein prediction: pre-shift bpc grows monotonically with replay fraction.
Falsifier: replay fraction 0.9 doesn't hurt pre-shift bpc.

Note: this is a different replay than R7. R7 was "replay DURING PHASE B
helps BWT recovery." This is "replay during PHASE A hurts pre-shift bpc
because there's no W-drift to correct -- replay is pure bias."

3 seeds.
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
N = 4096
BETA = 8.0
BYTE_BETA = 16.0
BATCH_SIZE = 64
POOL_SIZE = 1024
ALPHA = 0.3
MAX_EPOCHS = 15
RELU_B = 0.5
DELTA_RULE_ALPHA = 0.3
DELTA_RULE_DECAY = 1e-4

REPLAY_FRACTIONS = [0.0, 0.25, 0.5, 0.9]


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


def train_phase_a_with_replay(byte_atoms, pos_atoms, train_bytes, replay_fraction, seed):
    """Phase A training but with random replay from EARLIER training samples mixed in.
    Tests if replay-as-bias hurts when there's no drift to correct."""
    W = torch.zeros((N, N), dtype=torch.float32, device=DEVICE)
    # Replay pool grows during training -- accumulates first 1024 ctxs
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
    gen_replay = torch.Generator().manual_seed(seed + 100)

    for epoch in range(1, MAX_EPOCHS + 1):
        for batch_start in range(0, T_total, BATCH_SIZE):
            be = min(batch_start + BATCH_SIZE, T_total)
            idx_batch = train_idx[batch_start:be]
            tgt_batch = train_targets[batch_start:be]
            B = idx_batch.shape[0]
            ctxs_fresh = build_ctx(byte_atoms, pos_atoms, idx_batch)

            # Replay (if pool has entries and fraction > 0)
            if replay_fraction > 0 and pool_used > 0:
                n_replay = max(1, int(B * replay_fraction))
                ri = torch.randint(0, pool_used, (n_replay,), generator=gen_replay).to(DEVICE)
                ctxs = torch.cat([ctxs_fresh, pool_vecs[ri]], dim=0)
                tgts = torch.cat([tgt_batch, pool_labels[ri]], dim=0)
            else:
                ctxs = ctxs_fresh
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
                # Accumulate FRESH ctxs into pool (epoch 1 only)
                if epoch == 1:
                    dest = (pool_idx + arange_b[:B]) % POOL_SIZE
                    pool_vecs.index_copy_(0, dest, ctxs_fresh)
                    pool_labels.index_copy_(0, dest, tgt_batch)
                    pool_idx = (pool_idx + B) % POOL_SIZE
                    pool_used = min(pool_used + B, POOL_SIZE)
    return W, pool_vecs, pool_labels, pool_used


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
    _say(f"Stein prediction #1: replay during Phase A hurts pre-shift bpc at K={K}")
    _say(f"  REPLAY_FRACTIONS={REPLAY_FRACTIONS}  SEEDS={SEEDS}")

    all_results = {}
    for rf in REPLAY_FRACTIONS:
        _say(f"\n=== REPLAY_FRACTION={rf} ===")
        results = []
        for seed in SEEDS:
            corpus_a = load_corpus_a()
            split = int(0.8 * len(corpus_a))
            train_a, test_a = corpus_a[:split], corpus_a[split:]
            gen = torch.Generator().manual_seed(seed)
            byte_atoms = make_bsc_atoms(VOCAB_SIZE, N, gen).to(DEVICE)
            pos_atoms = make_bsc_atoms(K, N, gen).to(DEVICE)
            W_A, pool_A, labels_A, used_A = train_phase_a_with_replay(
                byte_atoms, pos_atoms, train_a, rf, seed)
            bpc = eval_bpc(W_A, byte_atoms, pos_atoms, test_a, pool_A, labels_A, used_A)
            _say(f"  seed={seed}: pre-shift bpc={bpc:.4f}")
            results.append({"seed": seed, "bpc_a": bpc})
        mean_bpc = sum(r["bpc_a"] for r in results) / len(results)
        sd_bpc = (sum((r["bpc_a"] - mean_bpc) ** 2 for r in results) / (len(results)-1)) ** 0.5
        all_results[rf] = {"mean": mean_bpc, "sd": sd_bpc, "results": results}
        _say(f"  mean bpc={mean_bpc:.4f}  sd={sd_bpc:.4f}")

    _say(f"\n========= STEIN PRED #1 VERDICT =========")
    baseline = all_results[0.0]["mean"]
    for rf in REPLAY_FRACTIONS:
        delta = all_results[rf]["mean"] - baseline
        _say(f"  rf={rf:.2f}: pre-shift bpc={all_results[rf]['mean']:.4f}  delta={delta:+.4f}")
    if all_results[0.9]["mean"] > baseline + 0.02:
        _say(f"  CONFIRMED: replay at 0.9 hurts pre-shift by {all_results[0.9]['mean']-baseline:+.4f}. Stein prediction holds.")
    else:
        _say(f"  REJECTED: replay at 0.9 does NOT hurt pre-shift bpc. Stein prediction fails at K=4.")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_replay_preshift_K4"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps({
        "K": K, "SEEDS": SEEDS, "REPLAY_FRACTIONS": REPLAY_FRACTIONS,
        "results": {str(rf): all_results[rf] for rf in REPLAY_FRACTIONS},
    }, indent=2))


if __name__ == "__main__":
    main()
