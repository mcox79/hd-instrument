"""R3 with Laplace smoothing -- the agent's single decisive compound test.

Previous R3 used vote_logp = log(count + 1e-6), zero-meaned. Research
showed this creates ~14-unit logit spikes that swamp retrieval at
K>=16. Fix: proper Laplace/Dirichlet smoothing.

  vote_p = (count + alpha) / (sum + 256*alpha)  # probability with smoothing
  vote_logp = log(vote_p)
  vote_logp -= vote_logp.mean(dim=1, keepdim=True)  # center

With alpha=1: zero counts become log(1/(256+ε)) ≈ -5.5, not -13.8.
Variance drops ~6x. Sparse rows get gracefully-degraded magnitude.

Test at K=32 with NUM_CONCEPTS=100 (small, well-estimated set). If
compound is real, R3-Laplace + replay + R10 should match or beat
replay+R10-only (-0.87 BWT).

Decision rule:
- BWT >= -0.82 (better than replay+R10): compound REAL -- ship R3-Laplace
- BWT in (-0.92, -0.82) (~same as replay-only): R3 compound at K=32 was
  implementation-broken; correct R3 is now silent / no-harm at high K
- BWT < -0.92: R3 truly closed even with smoothing -- move on to
  MI-selected concepts as the last rehab axis

Also tests R3-Laplace at K=4 to verify it preserves the +0.154 win
(K=4 is where R3 worked with the old normalizer; should still work).
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
LAMBDA_LINEAR = 0.7
GAMMA = 0.5
REPLAY_FRACTION = 0.5
LAPLACE_ALPHA = 1.0
NUM_CONCEPTS = 100

K_LEVELS = [4, 32]


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


def compute_vote_logp_LAPLACE(pool_byte_at_pos, pool_labels, ppmi, alpha):
    """Proper Laplace smoothing: vote_p = (count + alpha) / (sum + V*alpha)."""
    n_concepts = len(ppmi)
    counts = torch.zeros((n_concepts, VOCAB_SIZE), device=DEVICE)
    for c_idx, (i, b_i, j, b_j, _) in enumerate(ppmi):
        mask = (pool_byte_at_pos[:, i] == b_i) & (pool_byte_at_pos[:, j] == b_j)
        if mask.any():
            tgts = pool_labels[mask]
            for t in tgts.cpu().tolist():
                counts[c_idx, t] += 1
    row_sums = counts.sum(dim=1, keepdim=True)  # (n_concepts, 1)
    vote_p = (counts + alpha) / (row_sums + VOCAB_SIZE * alpha)
    vote_logp = torch.log(vote_p)
    vote_logp = vote_logp - vote_logp.mean(dim=1, keepdim=True)
    return vote_logp


def compute_vote_logp_BROKEN(pool_byte_at_pos, pool_labels, ppmi):
    """Original broken normalizer for comparison."""
    n_concepts = len(ppmi)
    counts = torch.zeros((n_concepts, VOCAB_SIZE), device=DEVICE)
    for c_idx, (i, b_i, j, b_j, _) in enumerate(ppmi):
        mask = (pool_byte_at_pos[:, i] == b_i) & (pool_byte_at_pos[:, j] == b_j)
        if mask.any():
            tgts = pool_labels[mask]
            for t in tgts.cpu().tolist():
                counts[c_idx, t] += 1
    vote_logp = torch.log(counts + 1e-6)
    vote_logp = vote_logp - vote_logp.mean(dim=1, keepdim=True)
    return vote_logp


def query_active(indices, ppmi):
    B = indices.shape[0]
    n_concepts = len(ppmi)
    active = torch.zeros((B, n_concepts), device=DEVICE)
    for c_idx, (i, b_i, j, b_j, _) in enumerate(ppmi):
        active[:, c_idx] = ((indices[:, i] == b_i) & (indices[:, j] == b_j)).float()
    return active


def train_phase_a(byte_atoms, pos_atoms, train_bytes, K):
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
                if epoch == 1:
                    dest = (pool_idx + arange_b[:B]) % POOL_SIZE
                    pool_vecs.index_copy_(0, dest, ctxs)
                    pool_labels.index_copy_(0, dest, tgt_batch)
                    pool_idx = (pool_idx + B) % POOL_SIZE
                    pool_used = min(pool_used + B, POOL_SIZE)
    return W, pool_vecs, pool_labels, pool_used


def train_phase_b_replay(W_start, byte_atoms, pos_atoms, train_b,
                          pool_ctx, pool_lbl, K, seed):
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
    pool_used = pool_ctx.shape[0]
    for epoch in range(MAX_EPOCHS):
        for batch_start in range(0, T_total, BATCH_SIZE):
            be = min(batch_start + BATCH_SIZE, T_total)
            idx_batch = train_idx[batch_start:be]
            tgt_batch = train_targets[batch_start:be]
            B = idx_batch.shape[0]
            ctxs_b = build_ctx(byte_atoms, pos_atoms, idx_batch, K)
            n_replay = max(1, int(B * REPLAY_FRACTION))
            i = torch.randint(0, pool_used, (n_replay,), generator=gen).to(DEVICE)
            ctxs = torch.cat([ctxs_b, pool_ctx[i]], dim=0)
            tgts = torch.cat([tgt_batch, pool_lbl[i]], dim=0)
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


def eval_combined(W, byte_atoms, pos_atoms, test_bytes, pool_vecs, pool_labels,
                  pool_used, ppmi, r10_active, r3_vote_logp, K, use_r3):
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
    for bs in range(0, T, BATCH_SIZE):
        be = min(bs + BATCH_SIZE, T)
        idx_b = idx_all[bs:be]
        tgts = tgts_all[bs:be]
        B = idx_b.shape[0]
        ctxs = build_ctx(byte_atoms, pos_atoms, idx_b, K)
        q = ctxs @ W.T
        q = shifted_relu(q, RELU_B)
        sims = (byte_atoms @ q.T) / N
        if use_r3:
            qa = query_active(idx_b, ppmi)
            concept_logits = (qa @ r3_vote_logp).T
            combined_logits = BETA * sims + GAMMA * concept_logits
        else:
            combined_logits = BETA * sims
        P_W = torch.softmax(combined_logits, dim=0)
        # R10 retrieval-fusion (always on)
        scores_a = factored_scores(idx_b, active, byte_atoms, pos_atoms, C3_POSITIONS, N)
        qa_r10 = query_active(idx_b, ppmi)
        s_b = r10_active @ qa_r10.T
        lc_logits = LAMBDA_LINEAR * scores_a + (1 - LAMBDA_LINEAR) * s_b
        w = torch.softmax(BETA * lc_logits, dim=0)
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
    W_A, pool_A, labels_A, used_A = train_phase_a(byte_atoms, pos_atoms, train_a, K)
    pool_byte_at_pos = decompose_pool(pool_A[:used_A], byte_atoms, pos_atoms, K, N)
    ppmi = extract_ppmi(pool_byte_at_pos, K, NUM_CONCEPTS)

    vote_laplace = compute_vote_logp_LAPLACE(pool_byte_at_pos, labels_A[:used_A], ppmi, LAPLACE_ALPHA)
    vote_broken = compute_vote_logp_BROKEN(pool_byte_at_pos, labels_A[:used_A], ppmi)

    # R10 active matrix (pool)
    r10_active = torch.zeros((used_A, NUM_CONCEPTS), device=DEVICE)
    for c_idx, (i, b_i, j, b_j, _) in enumerate(ppmi):
        m = (pool_byte_at_pos[:, i] == b_i) & (pool_byte_at_pos[:, j] == b_j)
        r10_active[:, c_idx] = m.float()

    # Initial bpc for BWT reference
    bpc_a_initial = eval_combined(W_A, byte_atoms, pos_atoms, test_a, pool_A, labels_A,
                                   used_A, ppmi, r10_active, vote_laplace, K, use_r3=False)

    W_AB = train_phase_b_replay(W_A, byte_atoms, pos_atoms, train_b,
                                 pool_A[:used_A], labels_A[:used_A], K, seed + 200)

    bpc_r10_only = eval_combined(W_AB, byte_atoms, pos_atoms, test_a, pool_A, labels_A,
                                  used_A, ppmi, r10_active, vote_laplace, K, use_r3=False)
    bpc_r10_r3_laplace = eval_combined(W_AB, byte_atoms, pos_atoms, test_a, pool_A, labels_A,
                                        used_A, ppmi, r10_active, vote_laplace, K, use_r3=True)
    bpc_r10_r3_broken = eval_combined(W_AB, byte_atoms, pos_atoms, test_a, pool_A, labels_A,
                                       used_A, ppmi, r10_active, vote_broken, K, use_r3=True)

    # Sanity: variance of the two vote_logp matrices
    laplace_std = float(vote_laplace.std())
    broken_std = float(vote_broken.std())

    return {
        "bpc_a_initial": bpc_a_initial,
        "replay_R10_only": bpc_r10_only,
        "replay_R10_R3laplace": bpc_r10_r3_laplace,
        "replay_R10_R3broken": bpc_r10_r3_broken,
        "vote_laplace_std": laplace_std,
        "vote_broken_std": broken_std,
    }


def main():
    _say(f"R3 with Laplace smoothing (alpha={LAPLACE_ALPHA}) at K in {K_LEVELS}")

    all_results = {}
    for K in K_LEVELS:
        _say(f"\n=== K={K} ===")
        results = []
        for seed in SEEDS:
            _say(f"\n[K={K}, seed={seed}]")
            r = run_one(K, seed)
            _say(f"  Phase A bpc_a: {r['bpc_a_initial']:.4f}")
            _say(f"  vote_logp std: laplace={r['vote_laplace_std']:.3f}  broken={r['vote_broken_std']:.3f}")
            _say(f"  replay_R10_only:      bpc={r['replay_R10_only']:.4f}  BWT={r['bpc_a_initial']-r['replay_R10_only']:+.4f}")
            _say(f"  replay_R10_R3laplace: bpc={r['replay_R10_R3laplace']:.4f}  BWT={r['bpc_a_initial']-r['replay_R10_R3laplace']:+.4f}")
            _say(f"  replay_R10_R3broken:  bpc={r['replay_R10_R3broken']:.4f}  BWT={r['bpc_a_initial']-r['replay_R10_R3broken']:+.4f}")
            results.append({"seed": seed, **r})
        all_results[K] = results

    _say(f"\n========= R3 LAPLACE VERDICT =========")
    for K in K_LEVELS:
        rs = all_results[K]
        mean_r10 = sum(r["replay_R10_only"] - r["bpc_a_initial"] for r in rs) / len(rs)
        mean_laplace = sum(r["replay_R10_R3laplace"] - r["bpc_a_initial"] for r in rs) / len(rs)
        mean_broken = sum(r["replay_R10_R3broken"] - r["bpc_a_initial"] for r in rs) / len(rs)
        # convert to BWT (init - post)
        mean_r10_bwt = -mean_r10
        mean_laplace_bwt = -mean_laplace
        mean_broken_bwt = -mean_broken
        _say(f"  K={K}: replay_R10_only BWT={mean_r10_bwt:+.4f}")
        _say(f"  K={K}: replay_R10_R3laplace BWT={mean_laplace_bwt:+.4f}  delta={mean_laplace_bwt - mean_r10_bwt:+.4f}")
        _say(f"  K={K}: replay_R10_R3broken  BWT={mean_broken_bwt:+.4f}  delta={mean_broken_bwt - mean_r10_bwt:+.4f}")
        if mean_laplace_bwt > mean_r10_bwt + 0.03:
            _say(f"  K={K} VERDICT: COMPOUND REAL. R3-Laplace gains over R10-only.")
        elif abs(mean_laplace_bwt - mean_r10_bwt) <= 0.03:
            _say(f"  K={K} VERDICT: NEUTRAL. R3-Laplace = R10-only within noise.")
        else:
            _say(f"  K={K} VERDICT: R3-Laplace still hurts. Compound truly closed.")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_r3_laplace"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps({
        "K_LEVELS": K_LEVELS, "SEEDS": SEEDS, "LAPLACE_ALPHA": LAPLACE_ALPHA,
        "all_results": {str(K): all_results[K] for K in K_LEVELS},
    }, indent=2))


if __name__ == "__main__":
    main()
