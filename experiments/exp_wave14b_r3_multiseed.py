"""R3 multi-seed verification: concept-as-readout-bias gave +0.163 single-seed.

That's our largest M2-related win so far. Need 3-seed variance bounds.
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
NUM_CONCEPTS = 100
GAMMA = 0.5  # the winning gamma from single-seed


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


def compute_concept_target_vote(pool_byte_at_pos, pool_labels, ppmi_concepts):
    n_concepts = len(ppmi_concepts)
    vote = torch.zeros((n_concepts, VOCAB_SIZE), device=DEVICE)
    for c_idx, (i, b_i, j, b_j, _) in enumerate(ppmi_concepts):
        mask = (pool_byte_at_pos[:, i] == b_i) & (pool_byte_at_pos[:, j] == b_j)
        if mask.any():
            tgts_for_c = pool_labels[mask]
            for t in tgts_for_c.cpu().tolist():
                vote[c_idx, t] += 1
    vote_logp = torch.log(vote + 1e-6)
    vote_logp = vote_logp - vote_logp.mean(dim=1, keepdim=True)
    return vote, vote_logp


def compute_query_concept_activation(indices, ppmi_concepts):
    B = indices.shape[0]
    n_concepts = len(ppmi_concepts)
    active = torch.zeros((B, n_concepts), device=DEVICE)
    for c_idx, (i, b_i, j, b_j, _) in enumerate(ppmi_concepts):
        active[:, c_idx] = ((indices[:, i] == b_i) & (indices[:, j] == b_j)).float()
    return active


def train_phase_a(seed, byte_atoms, pos_atoms, train_bytes):
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


def eval_with_bias(W, byte_atoms, pos_atoms, test_bytes, pool_vecs, pool_labels,
                   pool_used, ppmi_concepts, vote_logp, gamma):
    pad = bytes([PAD_BYTE]) * K
    padded = pad + test_bytes
    T = len(padded) - K
    bt = torch.tensor(list(padded), dtype=torch.long).to(DEVICE)
    offsets = torch.arange(K - 1, -1, -1, device=DEVICE)
    pos = torch.arange(T, device=DEVICE)
    idx_all = bt[pos.unsqueeze(1) + offsets.unsqueeze(0)]
    tgts_all = bt[pos + K]
    total = 0.0
    for bs in range(0, T, BATCH_SIZE):
        be = min(bs + BATCH_SIZE, T)
        idx_b = idx_all[bs:be]
        tgts = tgts_all[bs:be]
        B = idx_b.shape[0]
        ctxs = build_ctx(byte_atoms, pos_atoms, idx_b)
        q = ctxs @ W.T
        q = shifted_relu(q, RELU_B)
        sims = (byte_atoms @ q.T) / N
        active = compute_query_concept_activation(idx_b, ppmi_concepts)
        concept_logits = (active @ vote_logp).T
        combined_logits = BETA * sims + gamma * concept_logits
        P_W = torch.softmax(combined_logits, dim=0)
        active_p = pool_vecs[:pool_used]
        labels_p = pool_labels[:pool_used]
        sims_p = (active_p @ ctxs.T) / N
        weights_p = torch.softmax(BETA * sims_p, dim=0)
        P_retr = torch.zeros(VOCAB_SIZE, B, device=DEVICE)
        P_retr.scatter_add_(0, labels_p.unsqueeze(1).expand(-1, B), weights_p)
        P = ALPHA * P_retr + (1 - ALPHA) * P_W
        p_true = P.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)
        total += float(-torch.log2(p_true).sum())
    return total / max(T, 1)


def main():
    _say(f"R3 multi-seed: verify gamma=0.5 +0.163 post-shift")
    _say(f"  SEEDS={SEEDS}")

    seed_results = []
    for seed in SEEDS:
        _say(f"\n=== seed={seed} ===")
        corpus_a = load_corpus_a()
        corpus_b = shuffle_bytes(corpus_a, seed=seed + 1)
        split = int(0.8 * len(corpus_a))
        train_a, test_a = corpus_a[:split], corpus_a[split:]
        train_b = corpus_b[:int(0.8 * len(corpus_b))]

        gen_atoms = torch.Generator().manual_seed(seed)
        byte_atoms = make_bsc_atoms(VOCAB_SIZE, N, gen_atoms).to(DEVICE)
        pos_atoms = make_bsc_atoms(K, N, gen_atoms).to(DEVICE)

        W_A, pool_A, labels_A, used_A = train_phase_a(seed, byte_atoms, pos_atoms, train_a)
        pool_byte_at_pos = decompose_pool(pool_A[:used_A], byte_atoms, pos_atoms, N)
        ppmi = extract_ppmi(pool_byte_at_pos, K, NUM_CONCEPTS)
        vote, vote_logp = compute_concept_target_vote(pool_byte_at_pos, labels_A[:used_A], ppmi)

        pre_no = eval_with_bias(W_A, byte_atoms, pos_atoms, test_a, pool_A, labels_A, used_A,
                                ppmi, vote_logp, 0.0)
        pre_yes = eval_with_bias(W_A, byte_atoms, pos_atoms, test_a, pool_A, labels_A, used_A,
                                 ppmi, vote_logp, GAMMA)
        _say(f"  pre  gamma=0={pre_no:.4f}  gamma=0.5={pre_yes:.4f}  gain={pre_no-pre_yes:+.4f}")

        # Phase B
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

        post_no = eval_with_bias(W_AB, byte_atoms, pos_atoms, test_a, pool_A, labels_A, used_A,
                                 ppmi, vote_logp, 0.0)
        post_yes = eval_with_bias(W_AB, byte_atoms, pos_atoms, test_a, pool_A, labels_A, used_A,
                                  ppmi, vote_logp, GAMMA)
        gain = post_no - post_yes
        _say(f"  post gamma=0={post_no:.4f}  gamma=0.5={post_yes:.4f}  gain={gain:+.4f}")
        seed_results.append({"seed": seed, "pre_no": pre_no, "pre_yes": pre_yes,
                             "post_no": post_no, "post_yes": post_yes,
                             "post_gain": gain})

    _say(f"\n========= R3 MULTI-SEED VERDICT =========")
    gains = [r["post_gain"] for r in seed_results]
    mean = sum(gains) / len(gains)
    sd = (sum((g - mean) ** 2 for g in gains) / (len(gains) - 1)) ** 0.5
    se = sd / (len(gains) ** 0.5)
    _say(f"  post_gain across seeds: {[f'{g:+.4f}' for g in gains]}")
    _say(f"  mean={mean:+.4f}  sd={sd:.4f}  se={se:.4f}  t={mean/se if se>0 else 0:.2f}")
    _say(f"  (t critical p<0.05 df=2 is 4.30)")
    if mean >= 0.05 and (mean / se if se > 0 else 0) > 4.30:
        _say(f"  R3 CONFIRMED ROBUST: gamma=0.5 readout-bias gives significant post-shift gain")
    elif mean >= 0.05:
        _say(f"  R3 ROBUST mean but n=3 underpowered for clean significance")
    else:
        _say(f"  R3 NOT ROBUST: single-seed +0.163 was an outlier")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_r3_multiseed"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps({
        "SEEDS": SEEDS, "GAMMA": GAMMA,
        "results": seed_results,
        "mean_post_gain": mean, "sd_post_gain": sd, "se_post_gain": se,
    }, indent=2))


if __name__ == "__main__":
    main()
