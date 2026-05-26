"""Sparse dictionary learning vs PPMI head-to-head at K=64.

Per wave14d_self_supervised_concepts_research.md, online sparse dictionary
learning (Mairal 2009) applied directly to pool bundle vectors should escape
the Lippl-Stachenfeld 2025 redundancy ceiling that PPMI is subject to.

PPMI computes pair statistics on argmax-decoded bytes -- it's a Borel function
of argmax(G), bounded by the redundancy ceiling. Sparse coding operates on
the raw bundle including interference mass argmax discards, escaping that
ceiling.

Predicted gain at K=512: +0.05 to +0.15 over R10 baseline.
Test K=64 (decisive, fast). Pass if mean gain > 0.02 bpc with t > 2.

5 seeds, 75 GPU-min budget.
"""

from __future__ import annotations

import json
import math
from collections import Counter
from pathlib import Path

import torch


torch.set_float32_matmul_precision("high")

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
VOCAB_SIZE = 256
PAD_BYTE = 0
K = 64
N = 4096
BETA_BASE = 8.0
BYTE_BETA = 16.0
BATCH_SIZE = 64
POOL_SIZE = 1024
ALPHA = 0.3
MAX_EPOCHS = 15
RELU_B = 0.5
DELTA_RULE_ALPHA = 0.3
DELTA_RULE_DECAY = 1e-4

# Best R10 config (from hyperparam sweep)
BEST_NC = 50
BEST_LAMBDA = 0.3
BEST_BETA = 16.0

# Sparse coding parameters
SPARSE_NC = 50  # match PPMI concept count for fair comparison
SPARSE_L1 = 0.1  # sparsity penalty
SPARSE_LR = 0.05  # online dictionary learning rate
SPARSE_PASSES = 3  # passes over pool

SEEDS = [17, 23, 31, 37, 41]


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


def learn_sparse_dictionary(pool_vecs, num_atoms, l1_penalty, lr, passes, seed):
    """Online sparse dictionary learning (Mairal-style) on pool bundles.
    Returns dictionary D of shape (num_atoms, N) -- normalized rows."""
    pool_used = pool_vecs.shape[0]
    if pool_used == 0:
        return torch.zeros((num_atoms, N), device=DEVICE)
    gen = torch.Generator().manual_seed(seed)
    # Initialize D from random pool subset
    if pool_used >= num_atoms:
        init_idx = torch.randperm(pool_used, generator=gen)[:num_atoms]
        D = pool_vecs[init_idx].clone()
    else:
        D = torch.zeros((num_atoms, N), device=DEVICE)
        D[:pool_used] = pool_vecs.clone()
        D[pool_used:] = (2.0 * (torch.rand((num_atoms - pool_used, N), generator=gen) > 0.5).float() - 1.0).to(DEVICE)
    # Normalize rows of D
    norms = D.norm(dim=1, keepdim=True).clamp(min=1e-8)
    D = D / norms

    # Online updates
    for _ in range(passes):
        for i in range(pool_used):
            x = pool_vecs[i]
            # Encode x via soft-thresholding (FISTA-lite)
            corrs = D @ x / N
            alphas = torch.sign(corrs) * torch.clamp(corrs.abs() - l1_penalty, min=0.0)
            # Update D with residual (gradient step)
            recon = alphas @ D
            residual = x - recon
            for k in range(num_atoms):
                if alphas[k].abs() > 0:
                    D[k] = D[k] + lr * alphas[k] * residual
            # Renormalize
            norms = D.norm(dim=1, keepdim=True).clamp(min=1e-8)
            D = D / norms
    return D


def sparse_concept_activations(query_ctxs, D, l1_penalty):
    """Encode query contexts via sparse codes over D.
    Returns activations of shape (B, num_atoms)."""
    B = query_ctxs.shape[0]
    corrs = (query_ctxs @ D.T) / N  # (B, num_atoms)
    alphas = torch.sign(corrs) * torch.clamp(corrs.abs() - l1_penalty, min=0.0)
    return alphas


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
                P = torch.softmax(BETA_BASE * sims, dim=0)
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


def eval_with_concepts(W, byte_atoms, pos_atoms, test_bytes, pool_vecs, pool_labels,
                        pool_used, K_match_positions, mode, ppmi, vote_logp,
                        sparse_D, sparse_activations_pool, lam, beta_retrieval):
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
        P_W = predict_W(W, ctxs, byte_atoms, BETA_BASE, N)
        scores_a = factored_scores(idx_b, active, byte_atoms, pos_atoms, K_match_positions, N)
        w_a = torch.softmax(beta_retrieval * scores_a, dim=0)
        P_a = torch.zeros(VOCAB_SIZE, B, device=DEVICE)
        P_a.scatter_add_(0, labels.unsqueeze(1).expand(-1, B), w_a)
        if mode == "ppmi":
            concept_active = torch.zeros((pool_used, len(ppmi)), device=DEVICE)
            for c_idx, (i, b_i, j, b_j, _) in enumerate(ppmi):
                m = (pool_byte_at_pos[:, i] == b_i) & (pool_byte_at_pos[:, j] == b_j)
                concept_active[:, c_idx] = m.float()
            query_active = torch.zeros((B, len(ppmi)), device=DEVICE)
            for c_idx, (i, b_i, j, b_j, _) in enumerate(ppmi):
                query_active[:, c_idx] = ((idx_b[:, i] == b_i) & (idx_b[:, j] == b_j)).float()
            s_b = concept_active @ query_active.T
        elif mode == "sparse":
            # sparse_activations_pool already computed for pool entries
            # compute for query batch
            query_sparse = sparse_concept_activations(ctxs, sparse_D, SPARSE_L1)
            # s_b: pool x query similarity in sparse-activation space
            s_b = sparse_activations_pool @ query_sparse.T
        else:
            s_b = torch.zeros((pool_used, B), device=DEVICE)
        lc_logits = lam * scores_a + (1 - lam) * s_b
        w_lin = torch.softmax(beta_retrieval * lc_logits, dim=0)
        P_lin = torch.zeros(VOCAB_SIZE, B, device=DEVICE)
        P_lin.scatter_add_(0, labels.unsqueeze(1).expand(-1, B), w_lin)
        P_final = ALPHA * P_lin + (1 - ALPHA) * P_W
        p_true = P_final.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)
        total += float(-torch.log2(p_true).sum())
    return total / max(T, 1)


def run_one(seed):
    global pool_byte_at_pos  # used inside eval (yes, ugly, but local rewrite needed)
    corpus_a = load_corpus_a()
    corpus_b = shuffle_bytes(corpus_a, seed=seed + 1)
    split = int(0.8 * len(corpus_a))
    train_a, test_a = corpus_a[:split], corpus_a[split:]
    train_b = corpus_b[:int(0.8 * len(corpus_b))]
    gen = torch.Generator().manual_seed(seed)
    byte_atoms = make_bsc_atoms(VOCAB_SIZE, N, gen).to(DEVICE)
    pos_atoms = make_bsc_atoms(K, N, gen).to(DEVICE)
    W_A, pool_A, labels_A, used_A = train_phase(byte_atoms, pos_atoms, train_a, build_pool=True)
    pool_byte_at_pos = decompose_pool(pool_A[:used_A], byte_atoms, pos_atoms, N)
    ppmi = extract_ppmi(pool_byte_at_pos, K, BEST_NC)
    sparse_D = learn_sparse_dictionary(pool_A[:used_A], SPARSE_NC, SPARSE_L1,
                                         SPARSE_LR, SPARSE_PASSES, seed)
    sparse_pool_activations = sparse_concept_activations(pool_A[:used_A], sparse_D, SPARSE_L1)
    W_AB, _, _, _ = train_phase(byte_atoms, pos_atoms, train_b, build_pool=False, W_start=W_A)

    C3_POSITIONS = list(range(K - 1))
    # PPMI baseline (R10 best-config) post-shift
    bpc_ppmi = eval_with_concepts(W_AB, byte_atoms, pos_atoms, test_a, pool_A, labels_A,
                                    used_A, C3_POSITIONS, "ppmi", ppmi, None, None, None,
                                    BEST_LAMBDA, BEST_BETA)
    # Sparse coding
    bpc_sparse = eval_with_concepts(W_AB, byte_atoms, pos_atoms, test_a, pool_A, labels_A,
                                      used_A, C3_POSITIONS, "sparse", ppmi, None,
                                      sparse_D, sparse_pool_activations, BEST_LAMBDA, BEST_BETA)
    return {"bpc_ppmi": bpc_ppmi, "bpc_sparse": bpc_sparse,
            "sparse_minus_ppmi": bpc_ppmi - bpc_sparse}


def main():
    _say(f"Sparse coding vs PPMI at K={K} ({len(SEEDS)} seeds, R10 best-config + sparse swap)")
    _say(f"  PPMI: {BEST_NC} concepts, lam={BEST_LAMBDA}, beta={BEST_BETA}")
    _say(f"  Sparse: {SPARSE_NC} atoms, L1={SPARSE_L1}, lr={SPARSE_LR}, passes={SPARSE_PASSES}")
    results = []
    for seed in SEEDS:
        _say(f"\n[seed={seed}]")
        r = run_one(seed)
        _say(f"  bpc(R10-PPMI)={r['bpc_ppmi']:.4f}  bpc(R10-sparse)={r['bpc_sparse']:.4f}  delta={r['sparse_minus_ppmi']:+.4f}")
        results.append({"seed": seed, **r})
    _say("\n========= SPARSE vs PPMI VERDICT =========")
    deltas = [r["sparse_minus_ppmi"] for r in results]
    mean_delta = sum(deltas) / len(deltas)
    sd = (sum((d - mean_delta) ** 2 for d in deltas) / (len(deltas) - 1)) ** 0.5
    se = sd / (len(deltas) ** 0.5)
    t = mean_delta / se if se > 0 else 0.0
    _say(f"  mean delta = {mean_delta:+.4f}  sd={sd:.4f}  t={t:+.2f}")
    if mean_delta >= 0.02 and t >= 2.0:
        _say(f"  SPARSE WINS: sparse atoms beat PPMI by {mean_delta:+.4f} bpc.")
    elif mean_delta >= 0.005:
        _say(f"  WEAK: sparse slightly better but insignificant.")
    else:
        _say(f"  NO WIN: sparse does not beat PPMI on this corpus at K={K}.")
    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14d_sparse_vs_ppmi"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps({
        "K": K, "SEEDS": SEEDS, "SPARSE_NC": SPARSE_NC, "SPARSE_L1": SPARSE_L1,
        "results": results, "mean_delta": mean_delta, "sd": sd, "t": t,
    }, indent=2))


if __name__ == "__main__":
    main()
