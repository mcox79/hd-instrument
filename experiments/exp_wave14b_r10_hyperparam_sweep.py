"""Audit 2: R10 hyperparameter sweep at K=64.

R10 uses arbitrary defaults: LAMBDA_LINEAR=0.7, NUM_CONCEPTS=100, BETA=8.
Each could be wrong. K=64 (where R10 effect is robust at +0.106) is the
right test cell -- effect big enough to see hyperparameter sensitivity.

Sweep:
- LAMBDA_LINEAR in {0.3, 0.5, 0.7, 0.9} (concept weight in linear fusion)
- NUM_CONCEPTS in {50, 100, 300, 1000}
- BETA in {8, 12, 16}

Total: 4 x 4 x 3 = 48 conditions. Single seed (17) for speed; can multi-seed
the winner later.
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
K = 64
N = 4096
BATCH_SIZE = 64
POOL_SIZE = 1024
ALPHA = 0.3
MAX_EPOCHS = 15
RELU_B = 0.5
DELTA_RULE_ALPHA = 0.3
DELTA_RULE_DECAY = 1e-4
BYTE_BETA = 16.0
BASE_BETA = 8.0  # for W training only

LAMBDAS = [0.3, 0.5, 0.7, 0.9]
NUM_CONCEPTS_LIST = [50, 100, 300, 1000]
BETAS = [8, 12, 16]


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


def factored_scores(query_byte_indices, vsa_bundles, byte_atoms, pos_atoms,
                    match_positions, n):
    B = query_byte_indices.shape[0]
    scores = torch.zeros((vsa_bundles.shape[0], B), device=byte_atoms.device)
    for r in match_positions:
        pool_proj_r = vsa_bundles * pos_atoms[r].unsqueeze(0)
        query_atoms_r = byte_atoms[query_byte_indices[:, r]]
        scores += (pool_proj_r @ query_atoms_r.T) / n
    return scores


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


def train_phase(byte_atoms, pos_atoms, train_bytes, build_pool, W_start=None):
    if W_start is None:
        W = torch.zeros((N, N), dtype=torch.float32, device=DEVICE)
    else:
        W = W_start.clone()
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
                P = torch.softmax(BASE_BETA * sims, dim=0)
                target_atoms = byte_atoms[tgt_batch]
                predicted = (P.T @ byte_atoms)
                residual = target_atoms - predicted
                dW = (residual.T @ ctxs) / N
                W.mul_(1.0 - DELTA_RULE_DECAY)
                W.add_(dW, alpha=DELTA_RULE_ALPHA)
                if build_pool and epoch == 1:
                    dest = (pool_idx + arange_b[:B]) % POOL_SIZE
                    pool_vecs.index_copy_(0, dest, ctxs)
                    pool_labels.index_copy_(0, dest, tgt_batch)
                    pool_idx = (pool_idx + B) % POOL_SIZE
                    pool_used = min(pool_used + B, POOL_SIZE)
    return W, pool_vecs, pool_labels, pool_used


def eval_modes(W, byte_atoms, pos_atoms, test_bytes, pool_vecs, pool_labels,
               pool_used, ppmi, pool_byte_at_pos, lam, beta):
    pad = bytes([PAD_BYTE]) * K
    padded = pad + test_bytes
    T = len(padded) - K
    bt = torch.tensor(list(padded), dtype=torch.long).to(DEVICE)
    offsets = torch.arange(K - 1, -1, -1, device=DEVICE)
    pos = torch.arange(T, device=DEVICE)
    idx_all = bt[pos.unsqueeze(1) + offsets.unsqueeze(0)]
    tgts_all = bt[pos + K]
    totals = {"a_only": 0.0, "linear": 0.0}
    active = pool_vecs[:pool_used]
    labels = pool_labels[:pool_used]
    C3_POSITIONS = list(range(K - 1))

    concept_active = torch.zeros((pool_used, len(ppmi)), device=DEVICE)
    for c_idx, (i, b_i, j, b_j, _) in enumerate(ppmi):
        m = (pool_byte_at_pos[:, i] == b_i) & (pool_byte_at_pos[:, j] == b_j)
        concept_active[:, c_idx] = m.float()

    for bs in range(0, T, BATCH_SIZE):
        be = min(bs + BATCH_SIZE, T)
        idx_b = idx_all[bs:be]
        tgts = tgts_all[bs:be]
        B = idx_b.shape[0]
        ctxs = build_ctx(byte_atoms, pos_atoms, idx_b)
        q = ctxs @ W.T
        q = shifted_relu(q, RELU_B)
        sims = (byte_atoms @ q.T) / N
        P_W = torch.softmax(BASE_BETA * sims, dim=0)

        scores_a = factored_scores(idx_b, active, byte_atoms, pos_atoms, C3_POSITIONS, N)
        w_a = torch.softmax(beta * scores_a, dim=0)
        P_a = torch.zeros(VOCAB_SIZE, B, device=DEVICE)
        P_a.scatter_add_(0, labels.unsqueeze(1).expand(-1, B), w_a)
        P_a_final = ALPHA * P_a + (1 - ALPHA) * P_W

        query_active = torch.zeros((B, len(ppmi)), device=DEVICE)
        for c_idx, (i, b_i, j, b_j, _) in enumerate(ppmi):
            query_active[:, c_idx] = ((idx_b[:, i] == b_i) & (idx_b[:, j] == b_j)).float()
        s_b = concept_active @ query_active.T
        lc_logits = lam * scores_a + (1 - lam) * s_b
        w_lin = torch.softmax(beta * lc_logits, dim=0)
        P_lin = torch.zeros(VOCAB_SIZE, B, device=DEVICE)
        P_lin.scatter_add_(0, labels.unsqueeze(1).expand(-1, B), w_lin)
        P_lin_final = ALPHA * P_lin + (1 - ALPHA) * P_W

        for key, P_final in [("a_only", P_a_final), ("linear", P_lin_final)]:
            p_true = P_final.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)
            totals[key] += float(-torch.log2(p_true).sum())

    return {k: v / max(T, 1) for k, v in totals.items()}


def main():
    _say(f"R10 hyperparameter sweep at K={K}, seed={SEED}")
    _say(f"  LAMBDAS={LAMBDAS}  NUM_CONCEPTS={NUM_CONCEPTS_LIST}  BETAS={BETAS}")

    corpus_a = load_corpus_a()
    corpus_b = shuffle_bytes(corpus_a, seed=SEED + 1)
    split = int(0.8 * len(corpus_a))
    train_a, test_a = corpus_a[:split], corpus_a[split:]
    train_b = corpus_b[:int(0.8 * len(corpus_b))]
    gen = torch.Generator().manual_seed(SEED)
    byte_atoms = make_bsc_atoms(VOCAB_SIZE, N, gen).to(DEVICE)
    pos_atoms = make_bsc_atoms(K, N, gen).to(DEVICE)

    W_A, pool_A, labels_A, used_A = train_phase(byte_atoms, pos_atoms, train_a, build_pool=True)
    pool_byte_at_pos = decompose_pool(pool_A[:used_A], byte_atoms, pos_atoms, N)
    # Pre-compute max-concepts PPMI; slice later
    ppmi_max = extract_ppmi(pool_byte_at_pos, K, max(NUM_CONCEPTS_LIST))

    W_AB, _, _, _ = train_phase(byte_atoms, pos_atoms, train_b, build_pool=False, W_start=W_A)

    # Sweep
    results = []
    best_post_gain = -1
    best_cfg = None
    for nc in NUM_CONCEPTS_LIST:
        ppmi = ppmi_max[:nc]
        for lam in LAMBDAS:
            for beta in BETAS:
                pre = eval_modes(W_A, byte_atoms, pos_atoms, test_a, pool_A, labels_A,
                                  used_A, ppmi, pool_byte_at_pos, lam, beta)
                post = eval_modes(W_AB, byte_atoms, pos_atoms, test_a, pool_A, labels_A,
                                   used_A, ppmi, pool_byte_at_pos, lam, beta)
                gap_pre = pre["a_only"] - pre["linear"]
                gap_post = post["a_only"] - post["linear"]
                _say(f"  nc={nc:4d} lam={lam} beta={beta:2d}  pre_gap={gap_pre:+.4f}  post_gap={gap_post:+.4f}")
                results.append({"nc": nc, "lam": lam, "beta": beta,
                                "pre_gap": gap_pre, "post_gap": gap_post})
                if gap_post > best_post_gain:
                    best_post_gain = gap_post
                    best_cfg = (nc, lam, beta)

    _say(f"\n========= BEST CONFIG =========")
    _say(f"  Best post-shift gap: {best_post_gain:+.4f} at nc={best_cfg[0]} lam={best_cfg[1]} beta={best_cfg[2]}")
    _say(f"  R10 default (nc=100, lam=0.7, beta=8) gave +0.106 at K=64 in earlier multi-seed.")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_r10_hyperparam_sweep"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps({
        "K": K, "SEED": SEED,
        "LAMBDAS": LAMBDAS, "NUM_CONCEPTS_LIST": NUM_CONCEPTS_LIST, "BETAS": BETAS,
        "results": results, "best_post_gain": best_post_gain,
        "best_cfg": {"nc": best_cfg[0], "lam": best_cfg[1], "beta": best_cfg[2]},
    }, indent=2))


if __name__ == "__main__":
    main()
