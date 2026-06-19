"""R3 unigram diagnostic -- tests whether +0.032 R3-Laplace effect is just class-prior re-injection.

Per wave14c_r3_small_effect_mechanism_research.md, the most likely
mechanism for the small +0.032 bpc R3 effect is class-prior re-injection:
PPMI concept activations + Laplace + zero-mean produces a near-constant
additive bias proportional to (corpus-A unigram - uniform).

This experiment replaces R3 with the simplest possible class-prior:
just use the corpus-A byte unigram log-prior as the logit bias.

If unigram baseline gives +0.022 +/- 0.008, R3 IS class-prior re-injection
and should be retracted as a substrate mechanism.

If unigram gives substantially less (say +0.005) and R3 gives +0.032,
R3 has substrate-unique residual on top of the class prior.

3 seeds, K=4, plain W readout + optional unigram-prior bias vs R3-Laplace.
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


def compute_unigram_logp(train_bytes, laplace_alpha):
    counts = torch.zeros(VOCAB_SIZE, device=DEVICE)
    for b in train_bytes:
        counts[b] += 1
    p = (counts + laplace_alpha) / (counts.sum() + VOCAB_SIZE * laplace_alpha)
    logp = torch.log(p)
    return logp - logp.mean()


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
    return vote_logp - vote_logp.mean(dim=1, keepdim=True)


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


def train_phase_b(byte_atoms, pos_atoms, train_bytes, W_start):
    W = W_start.clone()
    pad = bytes([PAD_BYTE]) * K
    padded = pad + train_bytes
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
    return W


def eval_with_bias(W, byte_atoms, pos_atoms, test_bytes, pool_vecs, pool_labels,
                   pool_used, mode, ppmi, vote_logp, unigram_logp):
    """mode: 'off' | 'r3' | 'unigram'"""
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
        if mode == "r3":
            qa = query_active(idx_b, ppmi)
            concept_logits = (qa @ vote_logp).T
            combined_logits = BETA * sims + GAMMA * concept_logits
        elif mode == "unigram":
            combined_logits = BETA * sims + GAMMA * unigram_logp.unsqueeze(1)
        else:
            combined_logits = BETA * sims
        P_W = torch.softmax(combined_logits, dim=0)
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
    unigram_logp = compute_unigram_logp(train_a, LAPLACE_ALPHA)

    W_AB = train_phase_b(byte_atoms, pos_atoms, train_b, W_A)

    post_off = eval_with_bias(W_AB, byte_atoms, pos_atoms, test_a, pool_A, labels_A,
                               used_A, "off", ppmi, vote_logp, unigram_logp)
    post_r3 = eval_with_bias(W_AB, byte_atoms, pos_atoms, test_a, pool_A, labels_A,
                              used_A, "r3", ppmi, vote_logp, unigram_logp)
    post_unigram = eval_with_bias(W_AB, byte_atoms, pos_atoms, test_a, pool_A, labels_A,
                                   used_A, "unigram", ppmi, vote_logp, unigram_logp)

    return {
        "post_off": post_off,
        "post_r3": post_r3,
        "post_unigram": post_unigram,
        "r3_gain": post_off - post_r3,
        "unigram_gain": post_off - post_unigram,
        "r3_residual": (post_off - post_r3) - (post_off - post_unigram),
    }


def main():
    _say(f"R3 unigram diagnostic at K={K} -- does unigram class-prior reproduce R3's +0.032?")

    results = []
    for seed in SEEDS:
        _say(f"\n[seed={seed}]")
        r = run_one(seed)
        _say(f"  post_off     = {r['post_off']:.4f}")
        _say(f"  post_r3      = {r['post_r3']:.4f}  gain={r['r3_gain']:+.4f}")
        _say(f"  post_unigram = {r['post_unigram']:.4f}  gain={r['unigram_gain']:+.4f}")
        _say(f"  R3 residual over unigram = {r['r3_residual']:+.4f}")
        results.append({"seed": seed, **r})

    _say(f"\n========= UNIGRAM DIAGNOSTIC VERDICT =========")
    mean_r3 = sum(r["r3_gain"] for r in results) / len(results)
    mean_uni = sum(r["unigram_gain"] for r in results) / len(results)
    mean_resid = sum(r["r3_residual"] for r in results) / len(results)
    sd_resid = (sum((r["r3_residual"] - mean_resid) ** 2 for r in results) / (len(results) - 1)) ** 0.5
    _say(f"  R3 mean gain       = {mean_r3:+.4f}")
    _say(f"  Unigram mean gain  = {mean_uni:+.4f}")
    _say(f"  R3 residual (R3 - unigram) = {mean_resid:+.4f}  sd={sd_resid:.4f}")
    if mean_resid < 0.005 and abs(mean_resid) < 2 * sd_resid:
        _say(f"  R3 IS CLASS-PRIOR: unigram reproduces the effect within noise. Retract R3 as substrate mechanism.")
    elif mean_resid >= 0.01:
        _say(f"  R3 HAS RESIDUAL: substrate-unique signal beyond class prior. Keep R3.")
    else:
        _say(f"  AMBIGUOUS: small but non-zero residual. More seeds needed.")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_r3_unigram_diagnostic"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps({
        "K": K, "SEEDS": SEEDS,
        "results": results,
        "mean_r3_gain": mean_r3,
        "mean_unigram_gain": mean_uni,
        "mean_residual": mean_resid,
        "sd_residual": sd_resid,
    }, indent=2))


if __name__ == "__main__":
    main()
