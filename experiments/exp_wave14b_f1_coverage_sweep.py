"""F1 rescue: coverage-varied concept replay (per literature agent's rec).

R7 showed concept-tagged replay (12.4% coverage) loses to random by 0.53 bpc.
The literature predicts this is a coverage-vs-relevance issue at small buffer.
F1 sweeps the concept-coverage filter strictness and checks if monotone
improvement toward random emerges as coverage grows.

Conditions: replay sampled from
- top-10 PPMI concepts (sharpest filter)
- top-50 (R7's setting)
- top-200 (broader)
- top-1000 (very broad)
- "concept_active or 1-byte Hamming neighbor active" (expand by structural proximity)
- random (control)

Falsification: TRUE iff at least one concept-coverage condition beats random
by >= 0.05 bpc BWT. Concept signal genuinely adds value.
"""

from __future__ import annotations

import json
import math
from collections import Counter
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
COVERAGE_K_LEVELS = [10, 50, 200, 1000]


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


def extract_ppmi(pool_byte_at_pos, K_pos, num_concepts, k_neg=1.0):
    P = pool_byte_at_pos.shape[0]
    pair_counts = Counter()
    marginal_counts = Counter()
    total = 0
    for entry_idx in range(P):
        bytes_at = pool_byte_at_pos[entry_idx].cpu().tolist()
        for i in range(K_pos):
            marginal_counts[(i, bytes_at[i])] += 1
            for j in range(i + 1, K_pos):
                pair_counts[(i, bytes_at[i], j, bytes_at[j])] += 1
                total += 1
    scores = []
    for (i, b_i, j, b_j), cnt in pair_counts.items():
        p_ab = cnt / total
        p_a = marginal_counts[(i, b_i)] / P
        p_b = marginal_counts[(j, b_j)] / P
        if p_a > 0 and p_b > 0 and p_ab > 0:
            pmi = math.log(p_ab / (p_a * p_b ** 0.75 + 1e-12)) - math.log(k_neg)
            scores.append((i, b_i, j, b_j, max(0.0, pmi)))
    scores.sort(key=lambda x: -x[4])
    return scores[:num_concepts]


def decompose_pool(pool_vecs, byte_atoms, pos_atoms, n):
    P = pool_vecs.shape[0]
    out = torch.zeros((P, K), dtype=torch.long, device=DEVICE)
    for r in range(K):
        proj = pool_vecs * pos_atoms[r].unsqueeze(0)
        scores = proj @ byte_atoms.T / n
        out[:, r] = scores.argmax(dim=1)
    return out


def tagged_indices_for(pool_byte_at_pos, ppmi_concepts):
    """Returns indices of pool entries activating any concept."""
    P = pool_byte_at_pos.shape[0]
    activates = torch.zeros(P, dtype=torch.bool, device=pool_byte_at_pos.device)
    for (i, b_i, j, b_j, _) in ppmi_concepts:
        m = (pool_byte_at_pos[:, i] == b_i) & (pool_byte_at_pos[:, j] == b_j)
        activates |= m
    return torch.nonzero(activates).squeeze(-1)


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
                  pool_ctx, pool_lbl, eligible_indices, seed):
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
            if eligible_indices is not None and len(eligible_indices) > 0:
                n_replay = max(1, int(B * REPLAY_FRACTION))
                i = torch.randint(0, len(eligible_indices), (n_replay,), generator=gen).to(DEVICE)
                replay_idx = eligible_indices[i]
                ctxs = torch.cat([ctxs_b, pool_ctx[replay_idx]], dim=0)
                tgts = torch.cat([tgt_batch, pool_lbl[replay_idx]], dim=0)
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
    _say(f"F1: coverage-varied concept replay (per R7 literature agent)")
    _say(f"  COVERAGE_K_LEVELS: {COVERAGE_K_LEVELS}")

    corpus_a = load_corpus_a()
    corpus_b = shuffle_bytes(corpus_a, seed=SEED + 1)
    split = int(0.8 * len(corpus_a))
    train_a, test_a = corpus_a[:split], corpus_a[split:]
    train_b = corpus_b[:int(0.8 * len(corpus_b))]

    gen_atoms = torch.Generator().manual_seed(SEED)
    byte_atoms = make_bsc_atoms(VOCAB_SIZE, N, gen_atoms).to(DEVICE)
    pos_atoms = make_bsc_atoms(K, N, gen_atoms).to(DEVICE)

    _say(f"\n[Phase A] Training W and pool...")
    W_A, pool_A, labels_A, used_A = train_phase_a(byte_atoms, pos_atoms, train_a)
    bpc_a_initial = eval_bpc(W_A, byte_atoms, pos_atoms, test_a, pool_A, labels_A, used_A)
    _say(f"  Phase A bpc_a: {bpc_a_initial:.4f}")

    pool_byte_at_pos = decompose_pool(pool_A[:used_A], byte_atoms, pos_atoms, N)
    all_ppmi = extract_ppmi(pool_byte_at_pos, K, 2000)
    _say(f"  Total PPMI patterns extracted: {len(all_ppmi)}")

    results = {}

    # Baseline no-replay
    W_no = train_phase_b(W_A, byte_atoms, pos_atoms, train_b,
                         pool_A[:used_A], labels_A[:used_A],
                         eligible_indices=None, seed=SEED + 100)
    bpc_no = eval_bpc(W_no, byte_atoms, pos_atoms, test_a, pool_A, labels_A, used_A)
    bwt_no = bpc_a_initial - bpc_no
    results["no_replay"] = {"bpc_a_post": bpc_no, "bwt": bwt_no, "coverage_pct": 0.0}
    _say(f"  no_replay:              bpc_a_post={bpc_no:.4f}  BWT={bwt_no:+.4f}")

    # Random replay (full pool)
    all_idx = torch.arange(used_A, device=DEVICE)
    W_rand = train_phase_b(W_A, byte_atoms, pos_atoms, train_b,
                           pool_A[:used_A], labels_A[:used_A],
                           eligible_indices=all_idx, seed=SEED + 101)
    bpc_rand = eval_bpc(W_rand, byte_atoms, pos_atoms, test_a, pool_A, labels_A, used_A)
    bwt_rand = bpc_a_initial - bpc_rand
    results["random_full"] = {"bpc_a_post": bpc_rand, "bwt": bwt_rand, "coverage_pct": 100.0}
    _say(f"  random_full_pool:       bpc_a_post={bpc_rand:.4f}  BWT={bwt_rand:+.4f}")

    # Concept-coverage sweep
    for k in COVERAGE_K_LEVELS:
        concepts_k = all_ppmi[:k]
        elig = tagged_indices_for(pool_byte_at_pos, concepts_k)
        coverage_pct = 100 * len(elig) / used_A
        if len(elig) == 0:
            _say(f"  top_{k:4d}:                no eligible entries (skipped)")
            continue
        W_k = train_phase_b(W_A, byte_atoms, pos_atoms, train_b,
                            pool_A[:used_A], labels_A[:used_A],
                            eligible_indices=elig, seed=SEED + 200 + k)
        bpc_k = eval_bpc(W_k, byte_atoms, pos_atoms, test_a, pool_A, labels_A, used_A)
        bwt_k = bpc_a_initial - bpc_k
        results[f"top_{k}"] = {"bpc_a_post": bpc_k, "bwt": bwt_k, "coverage_pct": coverage_pct}
        _say(f"  top_{k:4d}_concepts ({coverage_pct:5.1f}%): bpc_a_post={bpc_k:.4f}  BWT={bwt_k:+.4f}")

    _say(f"\n========= F1 VERDICT =========")
    bwt_random = results["random_full"]["bwt"]
    concept_results = [(k, v) for k, v in results.items() if k.startswith("top_")]
    best_concept = max(concept_results, key=lambda kv: kv[1]["bwt"])
    _say(f"  Random-full BWT: {bwt_random:+.4f}")
    _say(f"  Best concept-filter BWT: {best_concept[0]} = {best_concept[1]['bwt']:+.4f}  "
         f"(coverage {best_concept[1]['coverage_pct']:.1f}%)")
    gap = best_concept[1]["bwt"] - bwt_random
    _say(f"  Concept-vs-random gap: {gap:+.4f}  (positive = concepts beat random)")
    if gap >= 0.05:
        _say(f"  F1 PASSES: at least one coverage level shows concept signal beats random.")
    else:
        _say(f"  F1 FAILS: concept-filtered replay never beats random by >=0.05.")
        _say(f"  Concept signal genuinely adds no value beyond coverage selection.")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_f1_coverage_sweep"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps({
        "bpc_a_initial": bpc_a_initial,
        "results": results,
    }, indent=2))


if __name__ == "__main__":
    main()
