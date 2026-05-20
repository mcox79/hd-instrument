"""R3 with corpus-disjoint concepts -- tests "shared evidence base" hypothesis.

Compound-falsification research synthesis said R3, R10, replay don't stack
because they all consume the same evidence base (pool_A's bigram patterns).

This experiment uses concepts extracted from a corpus chunk that W was NOT
trained on. If R3-disjoint compounds with replay+R10 where R3-same didn't,
the shared-evidence hypothesis is confirmed and we have a path to real
compounding.

Conditions at K=4, 3 seeds:
  - off       : no R3, no replay
  - r3_same   : R3 with concepts from pool_A (training data, same as before)
  - r3_disj   : R3 with concepts from held-out chunk (W never saw it)
  - r3_same_replay : R3-same + random replay
  - r3_disj_replay : R3-disj + random replay (the key test)

If r3_disj_replay - r3_same_replay > 0.03 bpc post-shift, hypothesis confirmed.
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
K = 64
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
REPLAY_FRACTION = 0.5


def _say(msg):
    print(msg, flush=True)


def load_corpus():
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


def chunk_bytes_to_K_positions(corpus_bytes, max_entries):
    """Convert a byte sequence into a (P, K) tensor of byte indices at K positions.
    Used to build a 'synthetic pool' from a held-out chunk without W training."""
    pad = bytes([PAD_BYTE]) * K
    padded = pad + corpus_bytes
    T_total = len(padded) - K
    if T_total <= 0:
        return torch.zeros((0, K), dtype=torch.long, device=DEVICE), torch.zeros(0, dtype=torch.long, device=DEVICE)
    bt = torch.tensor(list(padded), dtype=torch.long).to(DEVICE)
    offsets = torch.arange(K - 1, -1, -1, device=DEVICE)
    pos = torch.arange(T_total, device=DEVICE)
    idx = bt[pos.unsqueeze(1) + offsets.unsqueeze(0)]
    tgts = bt[pos + K]
    n_take = min(max_entries, T_total)
    if n_take < T_total:
        gen = torch.Generator(device="cpu").manual_seed(0)
        perm = torch.randperm(T_total, generator=gen)[:n_take].to(DEVICE)
        idx = idx[perm]
        tgts = tgts[perm]
    return idx, tgts


def compute_vote_logp_laplace(byte_at_pos, labels, ppmi, alpha):
    n_concepts = len(ppmi)
    counts = torch.zeros((n_concepts, VOCAB_SIZE), device=DEVICE)
    for c_idx, (i, b_i, j, b_j, _) in enumerate(ppmi):
        mask = (byte_at_pos[:, i] == b_i) & (byte_at_pos[:, j] == b_j)
        if mask.any():
            tgts = labels[mask]
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


def train_phase_b(byte_atoms, pos_atoms, train_bytes, W_start, pool_vecs, pool_labels,
                  pool_used, replay_fraction):
    W = W_start.clone()
    pad = bytes([PAD_BYTE]) * K
    padded = pad + train_bytes
    T_total = len(padded) - K
    bt = torch.tensor(list(padded), dtype=torch.long).to(DEVICE)
    offsets = torch.arange(K - 1, -1, -1, device=DEVICE)
    pos = torch.arange(T_total, device=DEVICE)
    train_idx = bt[pos.unsqueeze(1) + offsets.unsqueeze(0)]
    train_targets = bt[pos + K]
    gen = torch.Generator(device="cpu").manual_seed(99)
    for epoch in range(MAX_EPOCHS):
        for batch_start in range(0, T_total, BATCH_SIZE):
            be = min(batch_start + BATCH_SIZE, T_total)
            idx_batch = train_idx[batch_start:be]
            tgt_batch = train_targets[batch_start:be]
            ctxs = build_ctx(byte_atoms, pos_atoms, idx_batch)
            B = ctxs.shape[0]
            if replay_fraction > 0 and pool_used > 0:
                n_replay = int(B * replay_fraction)
                if n_replay > 0:
                    replay_idx = torch.randint(0, pool_used, (n_replay,), generator=gen).to(DEVICE)
                    replay_ctxs = pool_vecs[replay_idx]
                    replay_tgts = pool_labels[replay_idx]
                    ctxs = torch.cat([ctxs[:B - n_replay], replay_ctxs], dim=0)
                    tgt_batch = torch.cat([tgt_batch[:B - n_replay], replay_tgts], dim=0)
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


def eval_with_r3(W, byte_atoms, pos_atoms, test_bytes, pool_vecs, pool_labels,
                 pool_used, ppmi, vote_logp, use_r3):
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
        sims_p = (active @ ctxs.T) / N
        weights_p = torch.softmax(BETA * sims_p, dim=0)
        P_retr = torch.zeros(VOCAB_SIZE, B, device=DEVICE)
        P_retr.scatter_add_(0, labels.unsqueeze(1).expand(-1, B), weights_p)
        P = ALPHA * P_retr + (1 - ALPHA) * P_W
        p_true = P.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)
        total += float(-torch.log2(p_true).sum())
    return total / max(T, 1)


def run_one(seed):
    corpus = load_corpus()
    # Split: 60% train, 20% concept_source (W never sees), 20% test
    n = len(corpus)
    train_end = int(0.6 * n)
    concept_end = int(0.8 * n)
    train_a = corpus[:train_end]
    concept_disj_bytes = corpus[train_end:concept_end]
    test_a = corpus[concept_end:]
    corpus_b = shuffle_bytes(corpus[:concept_end], seed=seed + 1)
    train_b = corpus_b[:int(0.75 * len(corpus_b))]

    gen = torch.Generator().manual_seed(seed)
    byte_atoms = make_bsc_atoms(VOCAB_SIZE, N, gen).to(DEVICE)
    pos_atoms = make_bsc_atoms(K, N, gen).to(DEVICE)

    W_A, pool_A, labels_A, used_A = train_phase_a(byte_atoms, pos_atoms, train_a)

    # SAME concepts: from pool_A (training pool, W has seen this evidence)
    pool_byte_same = decompose_pool(pool_A[:used_A], byte_atoms, pos_atoms, N)
    ppmi_same = extract_ppmi(pool_byte_same, K, NUM_CONCEPTS)
    vote_logp_same = compute_vote_logp_laplace(pool_byte_same, labels_A[:used_A],
                                                ppmi_same, LAPLACE_ALPHA)

    # DISJOINT concepts: from the concept_source chunk (W never saw)
    disj_idx, disj_tgts = chunk_bytes_to_K_positions(concept_disj_bytes, POOL_SIZE)
    ppmi_disj = extract_ppmi(disj_idx, K, NUM_CONCEPTS)
    vote_logp_disj = compute_vote_logp_laplace(disj_idx, disj_tgts, ppmi_disj, LAPLACE_ALPHA)

    # Phase B with and without replay
    W_AB_no = train_phase_b(byte_atoms, pos_atoms, train_b, W_A, pool_A, labels_A,
                             used_A, replay_fraction=0.0)
    W_AB_replay = train_phase_b(byte_atoms, pos_atoms, train_b, W_A, pool_A, labels_A,
                                 used_A, replay_fraction=REPLAY_FRACTION)

    # 5 post-shift conditions: off / r3-same / r3-disj / r3-same+replay / r3-disj+replay
    post_off = eval_with_r3(W_AB_no, byte_atoms, pos_atoms, test_a, pool_A, labels_A,
                             used_A, ppmi_same, vote_logp_same, use_r3=False)
    post_r3same = eval_with_r3(W_AB_no, byte_atoms, pos_atoms, test_a, pool_A, labels_A,
                                used_A, ppmi_same, vote_logp_same, use_r3=True)
    post_r3disj = eval_with_r3(W_AB_no, byte_atoms, pos_atoms, test_a, pool_A, labels_A,
                                used_A, ppmi_disj, vote_logp_disj, use_r3=True)
    post_replay_off = eval_with_r3(W_AB_replay, byte_atoms, pos_atoms, test_a, pool_A,
                                    labels_A, used_A, ppmi_same, vote_logp_same, use_r3=False)
    post_replay_r3same = eval_with_r3(W_AB_replay, byte_atoms, pos_atoms, test_a, pool_A,
                                       labels_A, used_A, ppmi_same, vote_logp_same, use_r3=True)
    post_replay_r3disj = eval_with_r3(W_AB_replay, byte_atoms, pos_atoms, test_a, pool_A,
                                       labels_A, used_A, ppmi_disj, vote_logp_disj, use_r3=True)

    return {
        "post_off": post_off,
        "post_r3same": post_r3same,
        "post_r3disj": post_r3disj,
        "post_replay_off": post_replay_off,
        "post_replay_r3same": post_replay_r3same,
        "post_replay_r3disj": post_replay_r3disj,
        "r3same_gain": post_off - post_r3same,
        "r3disj_gain": post_off - post_r3disj,
        "replay_gain": post_off - post_replay_off,
        "r3same_compound_gain": post_replay_off - post_replay_r3same,
        "r3disj_compound_gain": post_replay_off - post_replay_r3disj,
    }


def main():
    _say(f"R3 disjoint-concepts at K={K} -- tests shared-evidence-base hypothesis")
    _say(f"  same    = concepts from pool_A (W trained on this)")
    _say(f"  disj    = concepts from held-out chunk (W never saw)")
    _say(f"  replay_fraction = {REPLAY_FRACTION}")

    results = []
    for seed in SEEDS:
        _say(f"\n[seed={seed}]")
        r = run_one(seed)
        _say(f"  post_off            = {r['post_off']:.4f}")
        _say(f"  r3same gain (alone) = {r['r3same_gain']:+.4f}")
        _say(f"  r3disj gain (alone) = {r['r3disj_gain']:+.4f}")
        _say(f"  replay gain (alone) = {r['replay_gain']:+.4f}")
        _say(f"  r3same gain (atop replay) = {r['r3same_compound_gain']:+.4f}")
        _say(f"  r3disj gain (atop replay) = {r['r3disj_compound_gain']:+.4f}")
        results.append({"seed": seed, **r})

    _say(f"\n========= SHARED-EVIDENCE-BASE VERDICT =========")
    mean_r3same_compound = sum(r["r3same_compound_gain"] for r in results) / len(results)
    mean_r3disj_compound = sum(r["r3disj_compound_gain"] for r in results) / len(results)
    delta = mean_r3disj_compound - mean_r3same_compound
    _say(f"  r3same atop replay: mean = {mean_r3same_compound:+.4f}")
    _say(f"  r3disj atop replay: mean = {mean_r3disj_compound:+.4f}")
    _say(f"  delta (disj - same) = {delta:+.4f}")
    if delta >= 0.03:
        _say(f"  HYPOTHESIS CONFIRMED: disjoint concepts compound with replay where same don't")
    elif delta >= 0.005:
        _say(f"  WEAK SIGNAL: small but positive direction")
    else:
        _say(f"  HYPOTHESIS REJECTED: disjoint concepts don't compound any better")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_r3_disjoint_K64"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps({
        "K": K, "SEEDS": SEEDS,
        "results": results,
        "mean_r3same_compound": mean_r3same_compound,
        "mean_r3disj_compound": mean_r3disj_compound,
        "delta": delta,
    }, indent=2))


if __name__ == "__main__":
    main()
