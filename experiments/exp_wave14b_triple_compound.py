"""Triple compound: random replay + R10 + R3.

The three biggest post-shift wins act on different mechanisms:
- Random replay (R7 finding): modifies WHICH gradients W sees during Phase B
- R10 linear-fusion: modifies the RETRIEVAL kernel at eval
- R3 readout-bias: modifies the W READOUT logits at eval

If orthogonal, combined post-shift gain could approach +0.4 to +0.6 bpc.
That would put us in "substrate recovers from catastrophic forgetting
nearly entirely" territory.

Tested at K=32 (where R10 effect is robust at t=29), 3 seeds.

Eight conditions = 2^3 (replay on/off × R10 on/off × R3 on/off):
- baseline (no replay, no R10, no R3)
- random replay only
- R10 only
- R3 only
- random + R10
- random + R3
- R10 + R3
- random + R10 + R3   <-- the triple

Decision: if triple > max(replay+R10, replay+R3, R10+R3) by >=0.05 bpc,
all three are orthogonal. If triple ~= best pair, two of three are
redundant. If triple ~= single best, none compound.
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
K = 32  # chosen: R10 robust at K=32 with t=29
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
REPLAY_FRACTION = 0.5

SEEDS = [17, 23, 31]


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


def train_phase_b(W_start, byte_atoms, pos_atoms, train_b,
                  pool_ctx, pool_lbl, do_replay, seed):
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
            ctxs_b = build_ctx(byte_atoms, pos_atoms, idx_batch)
            if do_replay:
                n_replay = max(1, int(B * REPLAY_FRACTION))
                i = torch.randint(0, pool_used, (n_replay,), generator=gen).to(DEVICE)
                ctxs = torch.cat([ctxs_b, pool_ctx[i]], dim=0)
                tgts = torch.cat([tgt_batch, pool_lbl[i]], dim=0)
            else:
                ctxs = ctxs_b
                tgts = tgt_batch
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


def eval_mode(W, byte_atoms, pos_atoms, test_bytes, pool_vecs, pool_labels,
              pool_used, ppmi, pool_byte_at_pos, vote_logp, use_r10, use_r3):
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
        # W readout with optional R3 bias
        q = ctxs @ W.T
        q = shifted_relu(q, RELU_B)
        sims = (byte_atoms @ q.T) / N
        if use_r3:
            query_active = compute_query_concept_activation(idx_b, ppmi)
            concept_logits = (query_active @ vote_logp).T
            combined_logits = BETA * sims + GAMMA * concept_logits
        else:
            combined_logits = BETA * sims
        P_W = torch.softmax(combined_logits, dim=0)

        # Retrieval with optional R10 fusion
        if use_r10:
            scores_a = factored_scores(idx_b, active, byte_atoms, pos_atoms,
                                        C3_POSITIONS, N)
            query_active2 = compute_query_concept_activation(idx_b, ppmi)
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
    vote_logp = compute_concept_target_vote(pool_byte_at_pos, labels_A[:used_A], ppmi)

    # Initial bpc on test_a (pre-shift baseline reference)
    bpc_a_initial = eval_mode(W_A, byte_atoms, pos_atoms, test_a, pool_A, labels_A,
                              used_A, ppmi, pool_byte_at_pos, vote_logp,
                              use_r10=False, use_r3=False)

    # Two Phase B variants: no-replay vs random-replay
    W_no_replay = train_phase_b(W_A, byte_atoms, pos_atoms, train_b,
                                pool_A[:used_A], labels_A[:used_A], do_replay=False, seed=seed + 100)
    W_replay = train_phase_b(W_A, byte_atoms, pos_atoms, train_b,
                              pool_A[:used_A], labels_A[:used_A], do_replay=True, seed=seed + 200)

    results = {}
    for replay_name, W_use in [("noR", W_no_replay), ("yesR", W_replay)]:
        for r10 in [False, True]:
            for r3 in [False, True]:
                key = f"{replay_name}_r10={int(r10)}_r3={int(r3)}"
                bpc = eval_mode(W_use, byte_atoms, pos_atoms, test_a,
                                 pool_A, labels_A, used_A,
                                 ppmi, pool_byte_at_pos, vote_logp,
                                 use_r10=r10, use_r3=r3)
                bwt = bpc_a_initial - bpc
                results[key] = {"bpc_a_post": bpc, "bwt": bwt}
    return bpc_a_initial, results


def main():
    _say(f"Triple compound: random replay x R10 x R3 at K={K}")
    _say(f"  SEEDS={SEEDS}  LAMBDA={LAMBDA_LINEAR}  GAMMA={GAMMA}  REPLAY_FRAC={REPLAY_FRACTION}")

    all_results = []
    for seed in SEEDS:
        _say(f"\n=== seed={seed} ===")
        bpc_init, results = run_one(seed)
        _say(f"  Phase A bpc_a: {bpc_init:.4f}")
        for key, r in results.items():
            _say(f"  {key:24s}  bpc_a_post={r['bpc_a_post']:.4f}  BWT={r['bwt']:+.4f}")
        all_results.append({"seed": seed, "bpc_a_initial": bpc_init, "results": results})

    _say(f"\n========= TRIPLE COMPOUND VERDICT =========")
    # Aggregate across seeds
    keys = list(all_results[0]["results"].keys())
    mean_bwt = {k: sum(r["results"][k]["bwt"] for r in all_results) / len(all_results)
                for k in keys}
    for k in keys:
        _say(f"  {k:24s}  mean BWT={mean_bwt[k]:+.4f}")

    baseline = mean_bwt["noR_r10=0_r3=0"]
    triple = mean_bwt["yesR_r10=1_r3=1"]
    triple_gain = triple - baseline
    _say(f"\n  Baseline (no replay, no R10, no R3): BWT={baseline:+.4f}")
    _say(f"  TRIPLE (replay + R10 + R3):           BWT={triple:+.4f}")
    _say(f"  Triple total gain over baseline:      {triple_gain:+.4f}")

    # Check orthogonality vs best pair: count which mechanisms are active
    def active_count(k):
        parts = k.split("_")
        replay = 1 if parts[0] == "yesR" else 0
        r10 = 1 if "r10=1" in k else 0
        r3 = 1 if "r3=1" in k else 0
        return replay + r10 + r3
    pair_keys = [k for k in keys if active_count(k) == 2]
    best_pair = max(mean_bwt[k] for k in pair_keys)
    _say(f"  Best pair (replay+R10, replay+R3, R10+R3): {best_pair:+.4f}")
    _say(f"  Triple vs best pair: {triple - best_pair:+.4f}")
    if triple - best_pair >= 0.05:
        _say(f"  ORTHOGONAL: all three compound; ship the triple stack")
    elif triple - best_pair >= 0.02:
        _say(f"  PARTIAL: small but real gain over best pair")
    else:
        _say(f"  REDUNDANT: triple <= best pair within noise; pick one mechanism")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_triple_compound"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps({
        "K": K, "SEEDS": SEEDS, "all_results": all_results,
        "mean_bwt": mean_bwt,
        "triple_gain_vs_baseline": triple_gain,
        "triple_vs_best_pair": triple - best_pair,
    }, indent=2))


if __name__ == "__main__":
    main()
