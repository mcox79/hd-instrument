"""R10 + R3 combination: do the two independent M2 wins compound?

R10 alone (K=32, linear fusion): post-shift +0.048 bpc gain
R3 alone (K=4, readout bias gamma=0.5): post-shift +0.154 bpc gain

Both are concept-augmented retrieval on the SAME pool but in different
ways:
- R10 modifies the RETRIEVAL kernel (linear fusion of A + concept score)
- R3 modifies the READOUT W (logits += gamma * concept_target_vote)

These mechanisms are orthogonal in principle. Test at K=16 and K=32
whether they compound or partially redundant.

Conditions tested:
- baseline (no concepts anywhere)
- R3 only (gamma=0.5 readout bias)
- R10 only (linear-fusion retrieval at K)
- R10+R3 combined

Decision: if combined post-shift gain > max(R3_alone, R10_alone) by
>=0.02, they compound (orthogonal mechanisms). If they're ~equal to
the larger, they're partially redundant.
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
GAMMA = 0.5

SEEDS = [17, 23, 31]
K_LEVELS = [16, 32]


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
    return vote_logp


def compute_query_concept_activation(indices, ppmi_concepts):
    B = indices.shape[0]
    n_concepts = len(ppmi_concepts)
    active = torch.zeros((B, n_concepts), device=DEVICE)
    for c_idx, (i, b_i, j, b_j, _) in enumerate(ppmi_concepts):
        active[:, c_idx] = ((indices[:, i] == b_i) & (indices[:, j] == b_j)).float()
    return active


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


def eval_mode(W, byte_atoms, pos_atoms, test_bytes, pool_vecs, pool_labels,
              pool_used, K, ppmi_concepts, pool_byte_at_pos, vote_logp,
              mode):
    """mode in {'baseline', 'r3', 'r10', 'r10_r3'}."""
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

        # W readout (with optional R3 bias)
        q = ctxs @ W.T
        q = shifted_relu(q, RELU_B)
        sims = (byte_atoms @ q.T) / N  # (VOCAB, B)
        if mode in ("r3", "r10_r3"):
            query_active = compute_query_concept_activation(idx_b, ppmi_concepts)
            concept_logits = (query_active @ vote_logp).T  # (VOCAB, B)
            combined_logits = BETA * sims + GAMMA * concept_logits
        else:
            combined_logits = BETA * sims
        P_W = torch.softmax(combined_logits, dim=0)

        # Retrieval branch (with optional R10 fusion)
        if mode in ("r10", "r10_r3"):
            scores_a = factored_scores(idx_b, active, byte_atoms, pos_atoms,
                                        C3_POSITIONS, N)
            query_active2 = compute_query_concept_activation(idx_b, ppmi_concepts)
            s_b = concept_active @ query_active2.T
            lc_logits = LAMBDA_LINEAR * scores_a + (1 - LAMBDA_LINEAR) * s_b
            w = torch.softmax(BETA * lc_logits, dim=0)
        else:
            sims_p = (active @ ctxs.T) / N
            w = torch.softmax(BETA * sims_p, dim=0)
        P_retr = torch.zeros(VOCAB_SIZE, B, device=DEVICE)
        P_retr.scatter_add_(0, labels.unsqueeze(1).expand(-1, B), w)
        P = ALPHA * P_retr + (1 - ALPHA) * P_W
        p_true = P.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)
        total += float(-torch.log2(p_true).sum())
    return total / max(T, 1)


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
    vote_logp = compute_concept_target_vote(pool_byte_at_pos, labels_A[:used_A], ppmi)

    def eval4(W_use):
        return {m: eval_mode(W_use, byte_atoms, pos_atoms, test_a, pool_A,
                              labels_A, used_A, K, ppmi, pool_byte_at_pos,
                              vote_logp, m)
                for m in ["baseline", "r3", "r10", "r10_r3"]}

    pre = eval4(W_A)
    W_AB, _, _, _ = train_phase(byte_atoms, pos_atoms, train_b, K, build_pool=False, W_start=W_A)
    post = eval4(W_AB)
    return pre, post


def main():
    _say(f"R10 + R3 combination: do they compound?")
    _say(f"  GAMMA={GAMMA}  LAMBDA_LINEAR={LAMBDA_LINEAR}  SEEDS={SEEDS}")

    all_results = {}
    for K in K_LEVELS:
        _say(f"\n=== K={K} ===")
        results = []
        for seed in SEEDS:
            _say(f"\n[K={K}, seed={seed}]")
            pre, post = run_one(K, seed)
            _say(f"  pre  baseline={pre['baseline']:.4f}  r3={pre['r3']:.4f}  r10={pre['r10']:.4f}  r10+r3={pre['r10_r3']:.4f}")
            _say(f"  post baseline={post['baseline']:.4f}  r3={post['r3']:.4f}  r10={post['r10']:.4f}  r10+r3={post['r10_r3']:.4f}")
            results.append({"seed": seed, "pre": pre, "post": post})
        all_results[K] = results

    _say(f"\n========= R10+R3 VERDICT =========")
    for K in K_LEVELS:
        results = all_results[K]
        for cond in ["r3", "r10", "r10_r3"]:
            gains_post = [r["post"]["baseline"] - r["post"][cond] for r in results]
            mean = sum(gains_post) / len(gains_post)
            _say(f"  K={K:3d}  {cond:8s}  post gain mean={mean:+.4f}")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_r10_r3_combined"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps({
        "SEEDS": SEEDS, "K_LEVELS": K_LEVELS, "GAMMA": GAMMA,
        "all_results": {str(K): all_results[K] for K in K_LEVELS},
    }, indent=2))


if __name__ == "__main__":
    main()
