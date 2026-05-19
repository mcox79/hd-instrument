"""R10 follow-up: K=32 and K=64 multi-seed to confirm theorem-breaking.

R10 single-seed K-sweep showed monotone post-shift gap in K, peaking
at K=32 with +0.049 bpc (above 0.03 threshold). With n=1 we can't
trust it. K=16 multi-seed (n=5) gave t=23.9 pre / t=5.1 post -- already
significant. Now confirming the headline at K=32 with statistical power.

Also tests K=64 to see if gap keeps growing past K=32.

Decision rule:
- K=32 mean post-shift gap > 0.030 with t > 2.78 -> theorem breaks at K=32
- K=64 mean post-shift gap > K=32 -> gap grows monotonically (M1/M4 confirmed)
- K=64 mean < K=32 -> peaks somewhere mid-range (independent-noise signature)
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
K_LEVELS = [32, 64]


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
        sims_c1 = (active @ ctxs.T) / N
        weights_c1 = torch.softmax(BETA * sims_c1, dim=0)
        P_c1 = torch.zeros(VOCAB_SIZE, B, device=DEVICE)
        P_c1.scatter_add_(0, labels.unsqueeze(1).expand(-1, B), weights_c1)
        P_c1_final = ALPHA * P_c1 + (1 - ALPHA) * P_W

        scores_a = factored_scores(idx_b, active, byte_atoms, pos_atoms, C3_POSITIONS, N)
        w_a = torch.softmax(BETA * scores_a, dim=0)
        P_a = torch.zeros(VOCAB_SIZE, B, device=DEVICE)
        P_a.scatter_add_(0, labels.unsqueeze(1).expand(-1, B), w_a)
        P_a_final = ALPHA * P_a + (1 - ALPHA) * P_W

        query_active = torch.zeros((B, len(ppmi_concepts)), device=DEVICE)
        for c_idx, (i, b_i, j, b_j, _) in enumerate(ppmi_concepts):
            query_active[:, c_idx] = ((idx_b[:, i] == b_i) & (idx_b[:, j] == b_j)).float()
        s_b = concept_active @ query_active.T
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
    _say(f"R10 K=32, K=64 multi-seed: confirm theorem-breaking at high K")
    _say(f"  K_LEVELS={K_LEVELS}  SEEDS={SEEDS}")

    all_results = {}
    for K in K_LEVELS:
        _say(f"\n=== K={K} multi-seed ===")
        results = []
        for seed in SEEDS:
            _say(f"\n[K={K}, seed={seed}]")
            pre, post = run_one(K, seed)
            gap_pre = pre["a_only"] - pre["linear"]
            gap_post = post["a_only"] - post["linear"]
            _say(f"  pre  A_only={pre['a_only']:.4f}  linear={pre['linear']:.4f}  gap={gap_pre:+.4f}")
            _say(f"  post A_only={post['a_only']:.4f}  linear={post['linear']:.4f}  gap={gap_post:+.4f}")
            results.append({"seed": seed, "pre": pre, "post": post,
                            "gap_pre": gap_pre, "gap_post": gap_post})
        all_results[K] = results

        gaps_pre = [r["gap_pre"] for r in results]
        gaps_post = [r["gap_post"] for r in results]
        mean_pre = sum(gaps_pre) / len(gaps_pre)
        mean_post = sum(gaps_post) / len(gaps_post)
        sd_pre = (sum((g - mean_pre) ** 2 for g in gaps_pre) / (len(gaps_pre) - 1)) ** 0.5
        sd_post = (sum((g - mean_post) ** 2 for g in gaps_post) / (len(gaps_post) - 1)) ** 0.5
        se_pre = sd_pre / (len(gaps_pre) ** 0.5)
        se_post = sd_post / (len(gaps_post) ** 0.5)
        _say(f"\n  K={K} stats:")
        _say(f"    pre  mean={mean_pre:+.4f}  sd={sd_pre:.4f}  t={mean_pre/se_pre if se_pre>0 else 0:.2f}")
        _say(f"    post mean={mean_post:+.4f}  sd={sd_post:.4f}  t={mean_post/se_post if se_post>0 else 0:.2f}")

    _say(f"\n========= R10 K=32+K=64 VERDICT =========")
    for K in K_LEVELS:
        gaps = [r["gap_post"] for r in all_results[K]]
        mean = sum(gaps) / len(gaps)
        sd = (sum((g - mean) ** 2 for g in gaps) / (len(gaps) - 1)) ** 0.5
        se = sd / (len(gaps) ** 0.5)
        t = mean / se if se > 0 else 0
        sig = "(p<0.05)" if t > 2.78 else "(NS)"
        _say(f"  K={K}: post mean={mean:+.4f}  t={t:.2f} {sig}")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_r10_K32_K64_multiseed"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps({
        "SEEDS": SEEDS, "K_LEVELS": K_LEVELS,
        "all_results": {str(K): all_results[K] for K in K_LEVELS},
    }, indent=2))


if __name__ == "__main__":
    main()
