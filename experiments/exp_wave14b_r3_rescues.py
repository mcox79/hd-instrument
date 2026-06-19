"""Compound question settler: orthogonal-concept R3 + K-scaled R3.

Per compound-falsification research synthesis: R3 vanishes at K>=16
because NUM_CONCEPTS=100 fixed but pair-space grows K^2. R10+R3
interferes because both use same PPMI concepts (logit double-counting).

Two rescues:
- R3-Kscaled: NUM_CONCEPTS = 1600 at K=32 (16x baseline). Tests if
  R3-vanishing is sparsity-driven.
- R3-orthogonal: R3 uses TRIPLE PPMI patterns (i,b_i,j,b_j,k,b_k)
  while R10 still uses PAIR patterns. Different concept geometry,
  no overlap. Tests if R10+R3 interference is double-counting.

All at K=32 with random replay (the dominant CL mechanism), 3 seeds.

Decision:
- Either rescue beats replay+R10 baseline by >= 0.05 BWT -> compound REAL
- Both null/worse -> compound closed; ship replay and R10 separately
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
K = 32
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

NUM_CONCEPTS_R10 = 100        # R10 uses default pair concepts
NUM_CONCEPTS_R3_DEFAULT = 100  # R3 default (matches earlier failed test)
NUM_CONCEPTS_R3_KSCALED = 1600 # K-scaled rescue at K=32 (16x baseline)
NUM_CONCEPTS_R3_TRIPLES = 100  # orthogonal rescue: 100 triples (different geometry)


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


def extract_ppmi_pairs(pool_byte_at_pos, K_pos, num_concepts, k_neg=1.0):
    """Pair PPMI: top-N (i, b_i, j, b_j) by PMI."""
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


def extract_ppmi_triples(pool_byte_at_pos, K_pos, num_concepts, k_neg=1.0):
    """Triple PPMI: top-N (i, b_i, j, b_j, k, b_k). Orthogonal to pairs.
    Subsample positions to keep tractable at K=32."""
    P = pool_byte_at_pos.shape[0]
    triple_counts = Counter()
    marginal_counts = Counter()
    total = 0
    # At K=32, full triples = C(32,3) = 4960 position triples. Sample a subset
    # to keep this tractable -- 60 random triples is plenty for top-100 concepts
    gen = torch.Generator().manual_seed(42)
    perm = torch.randperm(K_pos, generator=gen).tolist()
    triple_positions = []
    # Take every 3rd position triple stride
    for a in range(0, K_pos - 2, 3):
        for b in range(a + 1, K_pos - 1, 3):
            for c in range(b + 1, K_pos, 3):
                triple_positions.append((a, b, c))
                if len(triple_positions) >= 60:
                    break
            if len(triple_positions) >= 60:
                break
        if len(triple_positions) >= 60:
            break

    for entry_idx in range(P):
        bytes_at = pool_byte_at_pos[entry_idx].cpu().tolist()
        for (i, j, k_pos) in triple_positions:
            marginal_counts[(i, bytes_at[i])] += 1
            triple_counts[(i, bytes_at[i], j, bytes_at[j], k_pos, bytes_at[k_pos])] += 1
            total += 1

    scores = []
    for (i, b_i, j, b_j, k_pos, b_k), cnt in triple_counts.items():
        p_abc = cnt / total
        p_a = marginal_counts[(i, b_i)] / P
        p_b = marginal_counts[(j, b_j)] / P
        p_c = marginal_counts[(k_pos, b_k)] / P
        if p_a > 0 and p_b > 0 and p_c > 0 and p_abc > 0:
            pmi = math.log(p_abc / (p_a * p_b * p_c + 1e-12)) - math.log(k_neg)
            scores.append((i, b_i, j, b_j, k_pos, b_k, max(0.0, pmi)))
    scores.sort(key=lambda x: -x[6])
    return scores[:num_concepts]


def compute_concept_target_vote_pairs(pool_byte_at_pos, pool_labels, ppmi_pairs):
    n_concepts = len(ppmi_pairs)
    vote = torch.zeros((n_concepts, VOCAB_SIZE), device=DEVICE)
    for c_idx, (i, b_i, j, b_j, _) in enumerate(ppmi_pairs):
        mask = (pool_byte_at_pos[:, i] == b_i) & (pool_byte_at_pos[:, j] == b_j)
        if mask.any():
            tgts = pool_labels[mask]
            for t in tgts.cpu().tolist():
                vote[c_idx, t] += 1
    vote_logp = torch.log(vote + 1e-6)
    vote_logp = vote_logp - vote_logp.mean(dim=1, keepdim=True)
    return vote_logp


def compute_concept_target_vote_triples(pool_byte_at_pos, pool_labels, ppmi_triples):
    n_concepts = len(ppmi_triples)
    vote = torch.zeros((n_concepts, VOCAB_SIZE), device=DEVICE)
    for c_idx, (i, b_i, j, b_j, k_pos, b_k, _) in enumerate(ppmi_triples):
        mask = (pool_byte_at_pos[:, i] == b_i) & (pool_byte_at_pos[:, j] == b_j) & \
               (pool_byte_at_pos[:, k_pos] == b_k)
        if mask.any():
            tgts = pool_labels[mask]
            for t in tgts.cpu().tolist():
                vote[c_idx, t] += 1
    vote_logp = torch.log(vote + 1e-6)
    vote_logp = vote_logp - vote_logp.mean(dim=1, keepdim=True)
    return vote_logp


def query_concept_active_pairs(indices, ppmi_pairs):
    B = indices.shape[0]
    n_concepts = len(ppmi_pairs)
    active = torch.zeros((B, n_concepts), device=DEVICE)
    for c_idx, (i, b_i, j, b_j, _) in enumerate(ppmi_pairs):
        active[:, c_idx] = ((indices[:, i] == b_i) & (indices[:, j] == b_j)).float()
    return active


def query_concept_active_triples(indices, ppmi_triples):
    B = indices.shape[0]
    n_concepts = len(ppmi_triples)
    active = torch.zeros((B, n_concepts), device=DEVICE)
    for c_idx, (i, b_i, j, b_j, k_pos, b_k, _) in enumerate(ppmi_triples):
        active[:, c_idx] = ((indices[:, i] == b_i) & (indices[:, j] == b_j) &
                             (indices[:, k_pos] == b_k)).float()
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


def train_phase_b_replay(W_start, byte_atoms, pos_atoms, train_b,
                          pool_ctx, pool_lbl, seed):
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
                  pool_used, r10_ppmi, r10_concept_active,
                  r3_mode, r3_vote_logp, r3_concept_obj):
    """r3_mode in {'off', 'pairs_default', 'pairs_kscaled', 'triples'}."""
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
        ctxs = build_ctx(byte_atoms, pos_atoms, idx_b)
        q = ctxs @ W.T
        q = shifted_relu(q, RELU_B)
        sims = (byte_atoms @ q.T) / N
        # R3 contribution to W readout
        if r3_mode == "off":
            combined_logits = BETA * sims
        elif r3_mode == "triples":
            qa = query_concept_active_triples(idx_b, r3_concept_obj)
            concept_logits = (qa @ r3_vote_logp).T
            combined_logits = BETA * sims + GAMMA * concept_logits
        else:  # pairs_default or pairs_kscaled
            qa = query_concept_active_pairs(idx_b, r3_concept_obj)
            concept_logits = (qa @ r3_vote_logp).T
            combined_logits = BETA * sims + GAMMA * concept_logits
        P_W = torch.softmax(combined_logits, dim=0)

        # R10 retrieval-fusion (always on for this experiment)
        scores_a = factored_scores(idx_b, active, byte_atoms, pos_atoms,
                                    C3_POSITIONS, N)
        qa_r10 = query_concept_active_pairs(idx_b, r10_ppmi)
        s_b = r10_concept_active @ qa_r10.T
        lc_logits = LAMBDA_LINEAR * scores_a + (1 - LAMBDA_LINEAR) * s_b
        w = torch.softmax(BETA * lc_logits, dim=0)
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
    bpc_initial = eval_combined(W_A, byte_atoms, pos_atoms, test_a, pool_A, labels_A,
                                 used_A, [], torch.zeros((1, 0), device=DEVICE),
                                 "off", None, None)

    # R10 always uses 100 pair concepts (default)
    r10_ppmi = extract_ppmi_pairs(pool_byte_at_pos, K, NUM_CONCEPTS_R10)
    r10_active = torch.zeros((used_A, NUM_CONCEPTS_R10), device=DEVICE)
    for c_idx, (i, b_i, j, b_j, _) in enumerate(r10_ppmi):
        m = (pool_byte_at_pos[:, i] == b_i) & (pool_byte_at_pos[:, j] == b_j)
        r10_active[:, c_idx] = m.float()

    # R3 variants
    r3_pairs_default = extract_ppmi_pairs(pool_byte_at_pos, K, NUM_CONCEPTS_R3_DEFAULT)
    r3_pairs_kscaled = extract_ppmi_pairs(pool_byte_at_pos, K, NUM_CONCEPTS_R3_KSCALED)
    r3_triples = extract_ppmi_triples(pool_byte_at_pos, K, NUM_CONCEPTS_R3_TRIPLES)
    _say(f"  R3 triples extracted: {len(r3_triples)}")

    vote_default = compute_concept_target_vote_pairs(pool_byte_at_pos, labels_A[:used_A], r3_pairs_default)
    vote_kscaled = compute_concept_target_vote_pairs(pool_byte_at_pos, labels_A[:used_A], r3_pairs_kscaled)
    vote_triples = compute_concept_target_vote_triples(pool_byte_at_pos, labels_A[:used_A], r3_triples)

    # Phase B with replay
    W_AB = train_phase_b_replay(W_A, byte_atoms, pos_atoms, train_b,
                                 pool_A[:used_A], labels_A[:used_A], seed + 200)

    # Evaluate each R10+R3 variant
    bpc_results = {}
    bpc_results["replay_R10_only"] = eval_combined(
        W_AB, byte_atoms, pos_atoms, test_a, pool_A, labels_A, used_A,
        r10_ppmi, r10_active, "off", None, None)
    bpc_results["replay_R10_R3default"] = eval_combined(
        W_AB, byte_atoms, pos_atoms, test_a, pool_A, labels_A, used_A,
        r10_ppmi, r10_active, "pairs_default", vote_default, r3_pairs_default)
    bpc_results["replay_R10_R3kscaled"] = eval_combined(
        W_AB, byte_atoms, pos_atoms, test_a, pool_A, labels_A, used_A,
        r10_ppmi, r10_active, "pairs_kscaled", vote_kscaled, r3_pairs_kscaled)
    bpc_results["replay_R10_R3triples"] = eval_combined(
        W_AB, byte_atoms, pos_atoms, test_a, pool_A, labels_A, used_A,
        r10_ppmi, r10_active, "triples", vote_triples, r3_triples)
    return bpc_initial, bpc_results


def main():
    _say(f"R3 rescues: K-scaled + orthogonal-triples at K={K}")
    _say(f"  R10: 100 pair concepts (default)")
    _say(f"  R3 variants: default=100 pairs / kscaled=1600 pairs / triples=100 triples")

    all_results = []
    for seed in SEEDS:
        _say(f"\n=== seed={seed} ===")
        bpc_init, results = run_one(seed)
        _say(f"  Phase A bpc_a: {bpc_init:.4f}")
        for k, v in results.items():
            bwt = bpc_init - v
            _say(f"  {k:30s}  bpc_a_post={v:.4f}  BWT={bwt:+.4f}")
        all_results.append({"seed": seed, "bpc_a_initial": bpc_init, "results": results})

    _say(f"\n========= R3 RESCUES VERDICT =========")
    keys = list(all_results[0]["results"].keys())
    mean_bwt = {}
    for k in keys:
        bwts = [r["bpc_a_initial"] - r["results"][k] for r in all_results]
        mean_bwt[k] = sum(bwts) / len(bwts)
        _say(f"  {k:30s}  mean BWT={mean_bwt[k]:+.4f}")

    baseline = mean_bwt["replay_R10_only"]
    for variant in ["replay_R10_R3default", "replay_R10_R3kscaled", "replay_R10_R3triples"]:
        gain = mean_bwt[variant] - baseline
        verdict = "PASS" if gain >= 0.05 else "WEAK" if gain >= 0.02 else "FAIL"
        _say(f"  {variant} vs R10-only: {gain:+.4f}  [{verdict}]")

    _say(f"\nIf any variant PASSES, compound mechanism is real -- ship that R3 variant.")
    _say(f"If all FAIL, compound is closed; ship random-replay and R10 as separate stories.")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_r3_rescues"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps({
        "K": K, "SEEDS": SEEDS,
        "all_results": all_results,
        "mean_bwt": mean_bwt,
    }, indent=2))


if __name__ == "__main__":
    main()
