"""R3-Laplace ALONE at K=4 -- settles the +0.154 mystery.

Original R3 (broken log+epsilon normalizer) at K=4 gave +0.154 post-shift
gain vs no-concept baseline (3 seeds, t=33). With Laplace smoothing,
R3 is NEUTRAL when combined with replay+R10 (delta ~0.003) -- but that
test conflates "R3 has no signal" with "R3 redundant with replay+R10."

This experiment is the decisive test. No replay, no R10. Just W readout
with optional R3-Laplace bias, K=4, 3 seeds.

Three possible outcomes:
- +0.10 to +0.16: original +0.154 was REAL; effect survives variance fix
- +0.00 to +0.04: original was variance-explosion artifact (broken normalizer)
- mean ~0 with wide spread: original was seed-luck, not a real effect
"""

from __future__ import annotations

import json
import math
from collections import Counter
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
NUM_CONCEPTS = 100
LAPLACE_ALPHA = 1.0
GAMMA = 0.5


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


def decompose_pool(pool_vecs, byte_atoms, pos_atoms, n):
    P = pool_vecs.shape[0]
    out = torch.zeros((P, K), dtype=torch.long, device=DEVICE)
    for r in range(K):
        proj = pool_vecs * pos_atoms[r].unsqueeze(0)
        scores = proj @ byte_atoms.T / n
        out[:, r] = scores.argmax(dim=1)
    return out


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


def compute_vote_logp_laplace(pool_byte_at_pos, pool_labels, ppmi, alpha):
    n_concepts = len(ppmi)
    counts = torch.zeros((n_concepts, VOCAB_SIZE), device=DEVICE)
    for c_idx, (i, b_i, j, b_j, _) in enumerate(ppmi):
        mask = (pool_byte_at_pos[:, i] == b_i) & (pool_byte_at_pos[:, j] == b_j)
        if mask.any():
            tgts = pool_labels[mask]
            for t in tgts.cpu().tolist():
                counts[c_idx, t] += 1
    row_sums = counts.sum(dim=1, keepdim=True)
    vote_p = (counts + alpha) / (row_sums + VOCAB_SIZE * alpha)
    vote_logp = torch.log(vote_p)
    vote_logp = vote_logp - vote_logp.mean(dim=1, keepdim=True)
    return vote_logp


def query_active(indices, ppmi):
    B = indices.shape[0]
    n_concepts = len(ppmi)
    active = torch.zeros((B, n_concepts), device=DEVICE)
    for c_idx, (i, b_i, j, b_j, _) in enumerate(ppmi):
        active[:, c_idx] = ((indices[:, i] == b_i) & (indices[:, j] == b_j)).float()
    return active


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


def eval_r3_alone(W, byte_atoms, pos_atoms, test_bytes, pool_vecs, pool_labels,
                  pool_used, ppmi, vote_logp, use_r3):
    """Phase B eval: classic pool retrieval + W readout (optional R3 bias).
    NO R10 linear fusion, NO replay. Plain substrate."""
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
        B = idx_b.shape[0]
        ctxs = build_ctx(byte_atoms, pos_atoms, idx_b)
        q = ctxs @ W.T
        q = shifted_relu(q, RELU_B)
        sims = (byte_atoms @ q.T) / N
        if use_r3:
            qa = query_active(idx_b, ppmi)
            concept_logits = (qa @ vote_logp).T
            combined_logits = BETA * sims + GAMMA * concept_logits
        else:
            combined_logits = BETA * sims
        P_W = torch.softmax(combined_logits, dim=0)
        # Plain classical pool retrieval (no R10 linear fusion)
        sims_p = (active @ ctxs.T) / N
        weights_p = torch.softmax(BETA * sims_p, dim=0)
        P_retr = torch.zeros(VOCAB_SIZE, B, device=DEVICE)
        P_retr.scatter_add_(0, labels.unsqueeze(1).expand(-1, B), weights_p)
        P = ALPHA * P_retr + (1 - ALPHA) * P_W
        p_true = P.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)
        total += float(-torch.log2(p_true).sum())
    return total / max(T, 1)


def run_one(seed):
    corpus_a = load_corpus_a()
    corpus_b = shuffle_bytes(corpus_a, seed=seed + 1)
    split = int(0.8 * len(corpus_a))
    train_a, test_a = corpus_a[:split], corpus_a[split:]
    train_b = corpus_b[:int(0.8 * len(corpus_b))]
    gen = torch.Generator().manual_seed(seed)
    byte_atoms = make_bsc_atoms(VOCAB_SIZE, N, gen).to(DEVICE)
    pos_atoms = make_bsc_atoms(K, N, gen).to(DEVICE)

    W_A, pool_A, labels_A, used_A = train_phase_a(byte_atoms, pos_atoms, train_a)
    pool_byte_at_pos = decompose_pool(pool_A[:used_A], byte_atoms, pos_atoms, N)
    ppmi = extract_ppmi(pool_byte_at_pos, K, NUM_CONCEPTS)
    vote_logp = compute_vote_logp_laplace(pool_byte_at_pos, labels_A[:used_A], ppmi, LAPLACE_ALPHA)

    # Pre-shift evals (Phase A only, no Phase B)
    pre_no = eval_r3_alone(W_A, byte_atoms, pos_atoms, test_a, pool_A, labels_A,
                            used_A, ppmi, vote_logp, use_r3=False)
    pre_r3 = eval_r3_alone(W_A, byte_atoms, pos_atoms, test_a, pool_A, labels_A,
                            used_A, ppmi, vote_logp, use_r3=True)

    # Phase B (no replay)
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

    post_no = eval_r3_alone(W_AB, byte_atoms, pos_atoms, test_a, pool_A, labels_A,
                             used_A, ppmi, vote_logp, use_r3=False)
    post_r3 = eval_r3_alone(W_AB, byte_atoms, pos_atoms, test_a, pool_A, labels_A,
                             used_A, ppmi, vote_logp, use_r3=True)

    return {
        "pre_no": pre_no, "pre_r3": pre_r3,
        "post_no": post_no, "post_r3": post_r3,
        "pre_gain": pre_no - pre_r3,
        "post_gain": post_no - post_r3,
    }


def main():
    _say(f"R3-Laplace ALONE at K={K} (no replay, no R10) -- settles the +0.154 mystery")

    results = []
    for seed in SEEDS:
        _say(f"\n[seed={seed}]")
        r = run_one(seed)
        _say(f"  pre  no={r['pre_no']:.4f}  r3={r['pre_r3']:.4f}  gain={r['pre_gain']:+.4f}")
        _say(f"  post no={r['post_no']:.4f}  r3={r['post_r3']:.4f}  gain={r['post_gain']:+.4f}")
        results.append({"seed": seed, **r})

    _say(f"\n========= R3-ALONE-LAPLACE VERDICT =========")
    mean_pre = sum(r["pre_gain"] for r in results) / len(results)
    mean_post = sum(r["post_gain"] for r in results) / len(results)
    sd_post = (sum((r["post_gain"] - mean_post) ** 2 for r in results) / (len(results)-1)) ** 0.5
    se_post = sd_post / (len(results) ** 0.5)
    _say(f"  pre mean gain: {mean_pre:+.4f}")
    _say(f"  post mean gain: {mean_post:+.4f}  sd={sd_post:.4f}  t={mean_post/se_post if se_post>0 else 0:.2f}")
    _say(f"  Original broken-R3 post-shift gain at K=4 (3 seeds): +0.154")

    if mean_post >= 0.10:
        _say(f"  ORIGINAL +0.154 WAS REAL: Laplace-R3-alone still gives substantial gain")
    elif mean_post >= 0.04:
        _say(f"  PARTIAL: real effect but smaller than the broken-normalizer measurement")
    elif mean_post >= 0.01:
        _say(f"  MOSTLY ARTIFACT: broken-normalizer contributed most of +0.154")
    else:
        _say(f"  FULLY ARTIFACT: +0.154 was a broken-normalizer effect; retract")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_r3_alone_laplace"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps({
        "K": K, "SEEDS": SEEDS, "LAPLACE_ALPHA": LAPLACE_ALPHA,
        "results": results,
        "mean_post_gain": mean_post, "sd_post_gain": sd_post,
    }, indent=2))


if __name__ == "__main__":
    main()
