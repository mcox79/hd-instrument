"""R10 with hyperparam-sweep-winning config at K=128, K=256, multi-seed.

Hyperparam sweep at K=64 found nc=50, lam=0.3, beta=16 gives +0.318 bpc
vs default nc=100/lam=0.7/beta=8's +0.106 -- 3x improvement.

If this multiplier transfers, K=128 (was +0.139 default) could give
~+0.42, and K=256 (was +0.193 default) could give ~+0.58. That would
make the R10 finding substantially bigger than the current headline.

3 seeds at K=128, K=256. Compares best-config to default-config in the
same run for an apples-to-apples factor.
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
N = 8192
BETA_BASE = 8.0  # for W training
BYTE_BETA = 16.0
BATCH_SIZE = 64
POOL_SIZE = 1024
ALPHA = 0.3
MAX_EPOCHS = 15
RELU_B = 0.5
DELTA_RULE_ALPHA = 0.3
DELTA_RULE_DECAY = 1e-4

# DEFAULT R10 hyperparams (used in K-sweep)
DEFAULT_NC = 100
DEFAULT_LAMBDA = 0.7
DEFAULT_BETA = 8.0

# BEST R10 hyperparams (from hyperparam sweep)
BEST_NC = 50
BEST_LAMBDA = 0.3
BEST_BETA = 16.0

SEEDS = [17, 23, 31]
K_LEVELS = [256]


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


def build_ctx(byte_atoms, pos_atoms, indices, K):
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


def decompose_pool(pool_vecs, byte_atoms, pos_atoms, K, n):
    P = pool_vecs.shape[0]
    out = torch.zeros((P, K), dtype=torch.long, device=DEVICE)
    for r in range(K):
        proj = pool_vecs * pos_atoms[r].unsqueeze(0)
        scores = proj @ byte_atoms.T / n
        out[:, r] = scores.argmax(dim=1)
    return out


def extract_ppmi(pool_byte_at_pos, K, num_concepts, k_neg=1.0):
    P = pool_byte_at_pos.shape[0]
    pair_counts = Counter()
    marginal_counts = Counter()
    total = 0
    for entry_idx in range(P):
        bytes_at = pool_byte_at_pos[entry_idx].cpu().tolist()
        for i in range(K):
            marginal_counts[(i, bytes_at[i])] += 1
            for j in range(i + 1, K):
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


def train_phase(byte_atoms, pos_atoms, train_bytes, K, build_pool, W_start=None):
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
            ctxs = build_ctx(byte_atoms, pos_atoms, idx_batch, K)
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


def eval_at_config(W, byte_atoms, pos_atoms, test_bytes, pool_vecs, pool_labels,
                   pool_used, K, ppmi, pool_byte_at_pos, lam, beta_retrieval):
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
        ctxs = build_ctx(byte_atoms, pos_atoms, idx_b, K)
        P_W = predict_W(W, ctxs, byte_atoms, BETA_BASE, N)
        scores_a = factored_scores(idx_b, active, byte_atoms, pos_atoms, C3_POSITIONS, N)
        w_a = torch.softmax(beta_retrieval * scores_a, dim=0)
        P_a = torch.zeros(VOCAB_SIZE, B, device=DEVICE)
        P_a.scatter_add_(0, labels.unsqueeze(1).expand(-1, B), w_a)
        P_a_final = ALPHA * P_a + (1 - ALPHA) * P_W
        query_active = torch.zeros((B, len(ppmi)), device=DEVICE)
        for c_idx, (i, b_i, j, b_j, _) in enumerate(ppmi):
            query_active[:, c_idx] = ((idx_b[:, i] == b_i) & (idx_b[:, j] == b_j)).float()
        s_b = concept_active @ query_active.T
        lc_logits = lam * scores_a + (1 - lam) * s_b
        w_lin = torch.softmax(beta_retrieval * lc_logits, dim=0)
        P_lin = torch.zeros(VOCAB_SIZE, B, device=DEVICE)
        P_lin.scatter_add_(0, labels.unsqueeze(1).expand(-1, B), w_lin)
        P_lin_final = ALPHA * P_lin + (1 - ALPHA) * P_W
        for key, P_final in [("a_only", P_a_final), ("linear", P_lin_final)]:
            p_true = P_final.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)
            totals[key] += float(-torch.log2(p_true).sum())
    return {k: v / max(T, 1) for k, v in totals.items()}


def run_one(K, seed):
    corpus_a = load_corpus_a()
    corpus_b = shuffle_bytes(corpus_a, seed=seed + 1)
    split = int(0.8 * len(corpus_a))
    train_a, test_a = corpus_a[:split], corpus_a[split:]
    train_b = corpus_b[:int(0.8 * len(corpus_b))]
    gen = torch.Generator().manual_seed(seed)
    byte_atoms = make_bsc_atoms(VOCAB_SIZE, N, gen).to(DEVICE)
    pos_atoms = make_bsc_atoms(K, N, gen).to(DEVICE)
    W_A, pool_A, labels_A, used_A = train_phase(byte_atoms, pos_atoms, train_a, K, build_pool=True)
    pool_byte_at_pos = decompose_pool(pool_A[:used_A], byte_atoms, pos_atoms, K, N)
    # Build BOTH concept sets (default 100, best 50)
    ppmi_default = extract_ppmi(pool_byte_at_pos, K, DEFAULT_NC)
    ppmi_best = extract_ppmi(pool_byte_at_pos, K, BEST_NC)

    W_AB, _, _, _ = train_phase(byte_atoms, pos_atoms, train_b, K, build_pool=False, W_start=W_A)

    # Default config eval
    pre_d = eval_at_config(W_A, byte_atoms, pos_atoms, test_a, pool_A, labels_A, used_A, K,
                            ppmi_default, pool_byte_at_pos, DEFAULT_LAMBDA, DEFAULT_BETA)
    post_d = eval_at_config(W_AB, byte_atoms, pos_atoms, test_a, pool_A, labels_A, used_A, K,
                             ppmi_default, pool_byte_at_pos, DEFAULT_LAMBDA, DEFAULT_BETA)
    # Best config eval
    pre_b = eval_at_config(W_A, byte_atoms, pos_atoms, test_a, pool_A, labels_A, used_A, K,
                            ppmi_best, pool_byte_at_pos, BEST_LAMBDA, BEST_BETA)
    post_b = eval_at_config(W_AB, byte_atoms, pos_atoms, test_a, pool_A, labels_A, used_A, K,
                             ppmi_best, pool_byte_at_pos, BEST_LAMBDA, BEST_BETA)
    return {
        "default": {"pre": pre_d, "post": post_d,
                     "pre_gap": pre_d["a_only"] - pre_d["linear"],
                     "post_gap": post_d["a_only"] - post_d["linear"]},
        "best": {"pre": pre_b, "post": post_b,
                  "pre_gap": pre_b["a_only"] - pre_b["linear"],
                  "post_gap": post_b["a_only"] - post_b["linear"]},
    }


def main():
    _say(f"R10 best-config multi-seed at K in {K_LEVELS}")
    _say(f"  default: nc={DEFAULT_NC}, lam={DEFAULT_LAMBDA}, beta={DEFAULT_BETA}")
    _say(f"  best:    nc={BEST_NC}, lam={BEST_LAMBDA}, beta={BEST_BETA}")

    all_results = {}
    for K in K_LEVELS:
        _say(f"\n=== K={K} ===")
        results = []
        for seed in SEEDS:
            _say(f"\n[K={K}, seed={seed}]")
            r = run_one(K, seed)
            _say(f"  default: pre_gap={r['default']['pre_gap']:+.4f}  post_gap={r['default']['post_gap']:+.4f}")
            _say(f"  best:    pre_gap={r['best']['pre_gap']:+.4f}  post_gap={r['best']['post_gap']:+.4f}")
            results.append({"seed": seed, **r})
        all_results[K] = results

    _say(f"\n========= BEST vs DEFAULT VERDICT =========")
    for K in K_LEVELS:
        rs = all_results[K]
        def_post = sum(r["default"]["post_gap"] for r in rs) / len(rs)
        best_post = sum(r["best"]["post_gap"] for r in rs) / len(rs)
        def_post_sd = (sum((r["default"]["post_gap"] - def_post) ** 2 for r in rs) / (len(rs)-1)) ** 0.5
        best_post_sd = (sum((r["best"]["post_gap"] - best_post) ** 2 for r in rs) / (len(rs)-1)) ** 0.5
        _say(f"  K={K}: default post_gap mean={def_post:+.4f} sd={def_post_sd:.4f}")
        _say(f"  K={K}: best    post_gap mean={best_post:+.4f} sd={best_post_sd:.4f}")
        _say(f"  K={K}: improvement = {best_post - def_post:+.4f} bpc ({100*(best_post-def_post)/abs(def_post):.0f}% over default)")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_r10_best_config_N8192_K256"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps({
        "K_LEVELS": K_LEVELS, "SEEDS": SEEDS,
        "DEFAULT_CFG": {"nc": DEFAULT_NC, "lam": DEFAULT_LAMBDA, "beta": DEFAULT_BETA},
        "BEST_CFG": {"nc": BEST_NC, "lam": BEST_LAMBDA, "beta": BEST_BETA},
        "all_results": {str(K): all_results[K] for K in K_LEVELS},
    }, indent=2))


if __name__ == "__main__":
    main()
