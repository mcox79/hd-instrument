"""R10 deep dive: K-sweep + multi-seed verification.

Per research-agent recommendation after R10 single-seed test failed
preregistered 0.03 threshold by a hair (+0.024 pre, +0.009 post).
Agent flagged: theorem (Lippl-Stachenfeld 2025) is noise-free, doesn't
formally apply at K=16 where bundle interference is real. Need:
- multi-seed (5 seeds at K=16) for variance bounds
- K-sweep (K in {4, 8, 12, 16, 24, 32}) to test monotonicity

Decision rule (preregistered):
- If 5-seed mean(linear - A_only) post-shift > 0.015 with SE < 0.008
  -> redundancy corollary FAILS at noisy K, M1/M2/M4 live
- If mean < 0.005 with SD ~0.01 -> kill hypothesis cleanly
- K-sweep: monotone gap vs K = R10 was under-powered;
  peak at moderate K = independent-noise signature
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
LAMBDA_LINEAR = 0.7

SEEDS = [17, 23, 31, 41, 53]
K_SWEEP = [4, 8, 12, 16, 24, 32]


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
    P = vsa_bundles.shape[0]
    B = query_byte_indices.shape[0]
    scores = torch.zeros((P, B), device=byte_atoms.device)
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
                P = torch.softmax(BETA * sims, dim=0)
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
               pool_used, K, ppmi_concepts, pool_byte_at_pos):
    pad = bytes([PAD_BYTE]) * K
    padded = pad + test_bytes
    T = len(padded) - K
    bt = torch.tensor(list(padded), dtype=torch.long).to(DEVICE)
    offsets = torch.arange(K - 1, -1, -1, device=DEVICE)
    pos = torch.arange(T, device=DEVICE)
    idx_all = bt[pos.unsqueeze(1) + offsets.unsqueeze(0)]
    tgts_all = bt[pos + K]
    totals = {"c1": 0.0, "a_only": 0.0, "linear": 0.0}
    active = pool_vecs[:pool_used]
    labels = pool_labels[:pool_used]
    C3_POSITIONS = list(range(K - 1))

    # Precompute pool concept-active matrix
    concept_active = torch.zeros((pool_used, len(ppmi_concepts)), device=DEVICE)
    for c_idx, (i, b_i, j, b_j, _) in enumerate(ppmi_concepts):
        m = (pool_byte_at_pos[:, i] == b_i) & (pool_byte_at_pos[:, j] == b_j)
        concept_active[:, c_idx] = m.float()

    for bs in range(0, T, BATCH_SIZE):
        be = min(bs + BATCH_SIZE, T)
        idx_b = idx_all[bs:be]
        tgts = tgts_all[bs:be]
        B = idx_b.shape[0]
        ctxs = build_ctx(byte_atoms, pos_atoms, idx_b, K)
        P_W = predict_W(W, ctxs, byte_atoms, BETA, N)

        # C1
        sims_c1 = (active @ ctxs.T) / N
        weights_c1 = torch.softmax(BETA * sims_c1, dim=0)
        P_c1 = torch.zeros(VOCAB_SIZE, B, device=DEVICE)
        P_c1.scatter_add_(0, labels.unsqueeze(1).expand(-1, B), weights_c1)
        P_c1_final = ALPHA * P_c1 + (1 - ALPHA) * P_W

        # A_only (factored)
        scores_a = factored_scores(idx_b, active, byte_atoms, pos_atoms, C3_POSITIONS, N)
        w_a = torch.softmax(BETA * scores_a, dim=0)
        P_a = torch.zeros(VOCAB_SIZE, B, device=DEVICE)
        P_a.scatter_add_(0, labels.unsqueeze(1).expand(-1, B), w_a)
        P_a_final = ALPHA * P_a + (1 - ALPHA) * P_W

        # Concept score for this batch
        query_active = torch.zeros((B, len(ppmi_concepts)), device=DEVICE)
        for c_idx, (i, b_i, j, b_j, _) in enumerate(ppmi_concepts):
            query_active[:, c_idx] = ((idx_b[:, i] == b_i) & (idx_b[:, j] == b_j)).float()
        # s_b[pool_idx, batch_idx] = sum_c (query_active[batch, c] * pool_active[pool, c])
        s_b = concept_active @ query_active.T

        # Linear combine
        lc_logits = LAMBDA_LINEAR * scores_a + (1 - LAMBDA_LINEAR) * s_b
        w_lin = torch.softmax(BETA * lc_logits, dim=0)
        P_lin = torch.zeros(VOCAB_SIZE, B, device=DEVICE)
        P_lin.scatter_add_(0, labels.unsqueeze(1).expand(-1, B), w_lin)
        P_lin_final = ALPHA * P_lin + (1 - ALPHA) * P_W

        for key, P_final in [("c1", P_c1_final), ("a_only", P_a_final), ("linear", P_lin_final)]:
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
    ppmi = extract_ppmi(pool_byte_at_pos, K, NUM_CONCEPTS)
    pre = eval_modes(W_A, byte_atoms, pos_atoms, test_a, pool_A, labels_A, used_A, K, ppmi, pool_byte_at_pos)

    W_AB, _, _, _ = train_phase(byte_atoms, pos_atoms, train_b, K, build_pool=False, W_start=W_A)
    post = eval_modes(W_AB, byte_atoms, pos_atoms, test_a, pool_A, labels_A, used_A, K, ppmi, pool_byte_at_pos)
    return pre, post


def main():
    _say(f"R10 deep dive: K-sweep + multi-seed")
    _say(f"  K_SWEEP={K_SWEEP}  SEEDS={SEEDS}")

    # Multi-seed at K=16
    _say(f"\n=== Multi-seed at K=16 ===")
    k16_results = []
    for seed in SEEDS:
        _say(f"\n[seed={seed}, K=16]")
        pre, post = run_one(16, seed)
        gap_pre = pre["a_only"] - pre["linear"]
        gap_post = post["a_only"] - post["linear"]
        _say(f"  pre  A_only={pre['a_only']:.4f}  linear={pre['linear']:.4f}  gap={gap_pre:+.4f}")
        _say(f"  post A_only={post['a_only']:.4f}  linear={post['linear']:.4f}  gap={gap_post:+.4f}")
        k16_results.append({"seed": seed, "pre": pre, "post": post,
                            "gap_pre": gap_pre, "gap_post": gap_post})

    # K-sweep at single seed (17)
    _say(f"\n=== K-sweep at seed=17 ===")
    ksweep_results = []
    for K in K_SWEEP:
        if K == 16:
            # Use multi-seed entry for K=16
            r = next(r for r in k16_results if r["seed"] == 17)
            pre, post = r["pre"], r["post"]
        else:
            _say(f"\n[K={K}]")
            pre, post = run_one(K, 17)
        gap_pre = pre["a_only"] - pre["linear"]
        gap_post = post["a_only"] - post["linear"]
        _say(f"  K={K:3d}  pre gap={gap_pre:+.4f}  post gap={gap_post:+.4f}")
        ksweep_results.append({"K": K, "pre": pre, "post": post,
                               "gap_pre": gap_pre, "gap_post": gap_post})

    _say(f"\n========= R10 DEEP DIVE VERDICT =========")
    # Statistics for K=16 multi-seed
    gaps_pre = [r["gap_pre"] for r in k16_results]
    gaps_post = [r["gap_post"] for r in k16_results]
    mean_pre = sum(gaps_pre) / len(gaps_pre)
    mean_post = sum(gaps_post) / len(gaps_post)
    sd_pre = (sum((g - mean_pre) ** 2 for g in gaps_pre) / (len(gaps_pre) - 1)) ** 0.5
    sd_post = (sum((g - mean_post) ** 2 for g in gaps_post) / (len(gaps_post) - 1)) ** 0.5
    se_pre = sd_pre / (len(gaps_pre) ** 0.5)
    se_post = sd_post / (len(gaps_post) ** 0.5)

    _say(f"  K=16 multi-seed (n={len(SEEDS)}):")
    _say(f"    pre  mean={mean_pre:+.4f}  sd={sd_pre:.4f}  se={se_pre:.4f}  t={mean_pre/se_pre if se_pre>0 else 0:.2f}")
    _say(f"    post mean={mean_post:+.4f}  sd={sd_post:.4f}  se={se_post:.4f}  t={mean_post/se_post if se_post>0 else 0:.2f}")
    _say(f"  (one-sample t critical at p<0.05 df=4 is 2.78)")

    _say(f"\n  K-sweep gap (linear-A_only):")
    for r in ksweep_results:
        _say(f"    K={r['K']:3d}  pre={r['gap_pre']:+.4f}  post={r['gap_post']:+.4f}")

    if mean_post > 0.015 and (mean_post / se_post if se_post > 0 else 0) > 2.78:
        _say(f"\n  REJECT NULL: redundancy corollary FAILS at K=16 (post-shift)")
    elif abs(mean_post) < 0.005:
        _say(f"\n  CONFIRM NULL: gap is within noise even at K=16")
    else:
        _say(f"\n  INCONCLUSIVE: mean +0.0XX with n={len(SEEDS)} insufficient power")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_r10_ksweep_multiseed"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps({
        "SEEDS": SEEDS, "K_SWEEP": K_SWEEP,
        "k16_multi_seed": k16_results,
        "k_sweep_seed17": ksweep_results,
        "stats_k16": {"mean_pre": mean_pre, "sd_pre": sd_pre, "se_pre": se_pre,
                      "mean_post": mean_post, "sd_post": sd_post, "se_post": se_post},
    }, indent=2))


if __name__ == "__main__":
    main()
