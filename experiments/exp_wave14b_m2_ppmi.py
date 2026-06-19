"""Wave 14.B M2 PPMI: positive pointwise mutual information baseline.

Per the unbiased research synthesis: PPMI is "the highest-probability fix"
to the minimal-M2 failure. The diagnosed bug was that minimal M2 ranks by
P(a,b) which is dominated by marginal frequency. PPMI explicitly corrects
for this:

  PPMI(a,b) = max(0, log(P(a,b) * N / (P(a) * P(b)^0.75)) - log(k))

Top-K PPMI pairs are pairs whose co-occurrence EXCEEDS independence
prediction — the surface-vs-structure distinction the survey identified.

This is the simplest fix per the survey: drop-in replacement for raw
counts. Cheap baseline that should be tested first.

Plus: NMF on the PPMI matrix is a second-stage option per the survey
(word2vec/GloVe factorize PPMI). We test PPMI alone here; NMF-on-PPMI
could be a follow-up.
"""

from __future__ import annotations

import json
import time
from collections import Counter
from pathlib import Path

import torch
import math


torch.set_float32_matmul_precision("high")

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
SEED = 17
VOCAB_SIZE = 256
PAD_BYTE = 0
K = 4
BETA = 8.0
BYTE_BETA = 16.0
BATCH_SIZE = 64
ALPHA = 0.3
MAX_EPOCHS_B = 15
RELU_B = 0.5
N = 4096
DELTA_RULE_ALPHA = 0.3
DELTA_RULE_DECAY = 1e-4
NUM_CONCEPTS = 100
PPMI_K = 1.0  # negative-sample correction factor
CONCEPT_BETA = 4.0
C3_MATCH_POSITIONS = [0, 1, 2]


def _say(msg):
    print(msg, flush=True)


def build_ctx_bundles_bsc(byte_atoms, pos_atoms, indices):
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


def predict_pool_classical(ctxs, pool_vecs, pool_labels, pool_used, beta, n):
    B = ctxs.shape[0]
    if pool_used == 0:
        return torch.full((VOCAB_SIZE, B), 1.0 / VOCAB_SIZE, device=ctxs.device)
    active = pool_vecs[:pool_used]
    labels = pool_labels[:pool_used]
    sims = (active @ ctxs.T) / n
    weights = torch.softmax(beta * sims, dim=0)
    P_retr = torch.zeros(VOCAB_SIZE, B, device=ctxs.device)
    P_retr.scatter_add_(0, labels.unsqueeze(1).expand(-1, B), weights)
    return P_retr


def extract_ppmi_pairs(pool_byte_at_pos, K_positions, vocab, num_concepts, k_neg):
    """Compute PPMI(a@p_i, b@p_j) and return top concepts by PPMI score.

    Returns: list of (i, byte_i, j, byte_j, ppmi_score)
    """
    P = pool_byte_at_pos.shape[0]
    pair_counts = Counter()
    marginal_counts = Counter()
    total = 0
    for entry_idx in range(P):
        bytes_at = pool_byte_at_pos[entry_idx].cpu().tolist()
        for i in range(K_positions):
            marginal_counts[(i, bytes_at[i])] += 1
            for j in range(i + 1, K_positions):
                pair_counts[(i, bytes_at[i], j, bytes_at[j])] += 1
                total += 1
    # PPMI for each observed pair
    ppmi_scores = []
    total_marginal = P  # each entry contributes once per position
    for (i, b_i, j, b_j), cnt in pair_counts.items():
        # P(a, b) = cnt / total_pairs
        # P(a) = marginal[(i, b_i)] / total_marginal
        # P(b) = marginal[(j, b_j)] / total_marginal
        p_ab = cnt / total
        p_a = marginal_counts[(i, b_i)] / total_marginal
        # Mikolov smoothing: P(b)^0.75 / sum_b' P(b')^0.75
        p_b = marginal_counts[(j, b_j)] / total_marginal
        # PPMI with shift
        if p_a > 0 and p_b > 0 and p_ab > 0:
            pmi = math.log(p_ab / (p_a * p_b ** 0.75 + 1e-12)) - math.log(k_neg)
            ppmi = max(0.0, pmi)
            ppmi_scores.append((i, b_i, j, b_j, ppmi))
    # Sort by PPMI descending
    ppmi_scores.sort(key=lambda x: -x[4])
    return ppmi_scores[:num_concepts]


def predict_pool_c3_ppmi(query_byte_indices, ctxs, vsa_bundles, vsa_used,
                          byte_atoms, pos_atoms, target_pos,
                          concept_atoms, pool_concept_scores,
                          beta_retrieval, beta_byte, beta_concept, n,
                          match_positions, aggregation):
    B = query_byte_indices.shape[0]
    P = vsa_bundles.shape[0]
    factored_scores = torch.zeros((P, B), device=byte_atoms.device)
    for r in match_positions:
        pool_proj_r = vsa_bundles * pos_atoms[r].unsqueeze(0)
        query_atoms_r = byte_atoms[query_byte_indices[:, r]]
        factored_scores += (pool_proj_r @ query_atoms_r.T) / n

    # Query concept activation
    query_concept_scores = ctxs @ concept_atoms.T / n  # (B, num_concepts)
    concept_sim = pool_concept_scores @ query_concept_scores.T  # (P, B)

    if aggregation == "product":
        wf = torch.softmax(beta_retrieval * factored_scores, dim=0)
        wc = torch.softmax(beta_concept * concept_sim, dim=0)
        combined = wf * wc
        combined = combined / combined.sum(dim=0, keepdim=True).clamp(min=1e-12)
    elif aggregation == "rerank":
        TOP_K_RR = 16
        topk_idx = torch.topk(factored_scores, k=min(TOP_K_RR, P), dim=0).indices
        combined = torch.zeros((P, B), device=byte_atoms.device)
        for b in range(B):
            local_idx = topk_idx[:, b]
            local_cs = concept_sim[local_idx, b]
            local_weights = torch.softmax(beta_concept * local_cs, dim=0)
            combined[local_idx, b] = local_weights
    else:
        combined = torch.softmax(beta_retrieval * (factored_scores + concept_sim), dim=0)

    target_estimates = vsa_bundles * target_pos.unsqueeze(0)
    byte_scores = (target_estimates @ byte_atoms.T) / n
    P_byte_per_entry = torch.softmax(beta_byte * byte_scores, dim=1)
    return P_byte_per_entry.T @ combined


def main():
    _say(f"Wave 14.B M2 PPMI: PMI-corrected concept extraction")
    _say(f"  num_concepts={NUM_CONCEPTS}, PPMI smoothing k={PPMI_K}")

    state_path = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_cl_phase_a" / "state.pt"
    state = torch.load(state_path, weights_only=False)
    W = state["W_A"].to(DEVICE).clone()
    pool_vecs = state["pool_vecs_A"].to(DEVICE)
    pool_labels = state["pool_labels_A"].to(DEVICE)
    pool_used = int(state["pool_used_A"])
    byte_atoms = state["byte_atoms"].to(DEVICE)
    pos_atoms = state["pos_atoms"].to(DEVICE)

    target_pos_gen = torch.Generator().manual_seed(SEED + 99)
    target_pos_bits = torch.randint(0, 2, (N,), generator=target_pos_gen)
    target_pos = (target_pos_bits * 2 - 1).to(torch.float32).to(DEVICE)
    vsa_bundles = pool_vecs[:pool_used] + byte_atoms[pool_labels[:pool_used]] * target_pos.unsqueeze(0)

    # Decompose pool to per-position bytes
    _say(f"\nDecomposing pool to per-position bytes...")
    pool_byte_at_pos = torch.zeros((pool_used, K), dtype=torch.long, device=DEVICE)
    for r in range(K):
        proj = pool_vecs[:pool_used] * pos_atoms[r].unsqueeze(0)
        byte_scores = proj @ byte_atoms.T / N
        pool_byte_at_pos[:, r] = byte_scores.argmax(dim=1)

    # Extract PPMI-ranked top pairs
    _say(f"\nExtracting top {NUM_CONCEPTS} pairs by PPMI...")
    ppmi_top = extract_ppmi_pairs(pool_byte_at_pos, K, VOCAB_SIZE, NUM_CONCEPTS, PPMI_K)
    _say(f"  Top-3 PPMI pairs: {[(p[:4], round(p[4], 3)) for p in ppmi_top[:3]]}")

    # Compare to top by raw count
    _say(f"\n  For comparison, minimal-M2 top-3 by raw count were:")
    _say(f"    ((0, 124, 1, 32), 24), ((1, 124, 2, 32), 24), ((2, 124, 3, 32), 24)  # surface ASCII")

    # Build concept atoms
    concept_atoms = torch.zeros((NUM_CONCEPTS, N), device=DEVICE)
    for c_idx, (i, b_i, j, b_j, score) in enumerate(ppmi_top):
        concept_atoms[c_idx] = byte_atoms[b_i] * pos_atoms[i] + byte_atoms[b_j] * pos_atoms[j]
    pool_concept_scores = pool_vecs[:pool_used] @ concept_atoms.T / N

    # Eval
    test_a = state["test_a"]
    train_b = state["train_b"]
    pad = bytes([PAD_BYTE]) * K
    padded_test = pad + test_a
    T_test = len(padded_test) - K
    test_bytes = torch.tensor(list(padded_test), dtype=torch.long).to(DEVICE)
    offsets = torch.arange(K - 1, -1, -1, device=DEVICE)
    pos_test = torch.arange(T_test, device=DEVICE)
    test_a_idx = test_bytes[pos_test.unsqueeze(1) + offsets.unsqueeze(0)]
    test_a_targets = test_bytes[pos_test + K]

    def eval_all(W_local):
        bits = {"c1": 0.0, "c3_ppmi_product": 0.0, "c3_ppmi_rerank": 0.0, "c3_ppmi_additive": 0.0}
        for bs in range(0, T_test, BATCH_SIZE):
            be = min(bs + BATCH_SIZE, T_test)
            idx_batch = test_a_idx[bs:be]
            ctxs = build_ctx_bundles_bsc(byte_atoms, pos_atoms, idx_batch)
            P_W = predict_W(W_local, ctxs, byte_atoms, BETA, N)
            tgts = test_a_targets[bs:be]
            P_c1 = predict_pool_classical(ctxs, pool_vecs, pool_labels, pool_used, BETA, N)
            P_1 = ALPHA * P_c1 + (1 - ALPHA) * P_W
            bits["c1"] += float(-torch.log2(P_1.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)).sum())
            for mode in ["product", "rerank", "additive"]:
                P_p = predict_pool_c3_ppmi(idx_batch, ctxs, vsa_bundles, pool_used,
                                            byte_atoms, pos_atoms, target_pos,
                                            concept_atoms, pool_concept_scores,
                                            BETA, BYTE_BETA, CONCEPT_BETA, N,
                                            C3_MATCH_POSITIONS, mode)
                P_x = ALPHA * P_p + (1 - ALPHA) * P_W
                bits[f"c3_ppmi_{mode}"] += float(-torch.log2(P_x.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)).sum())
        return {k: v / max(T_test, 1) for k, v in bits.items()}

    _say(f"\nPre-shift eval:")
    pre = eval_all(W)
    _say(f"  C1={pre['c1']:.4f}  C3+PPMI(prod)={pre['c3_ppmi_product']:.4f}  "
         f"C3+PPMI(rerank)={pre['c3_ppmi_rerank']:.4f}  C3+PPMI(add)={pre['c3_ppmi_additive']:.4f}")

    padded_train_b = pad + train_b
    T_total = len(padded_train_b) - K
    train_b_bytes = torch.tensor(list(padded_train_b), dtype=torch.long).to(DEVICE)
    pos_train = torch.arange(T_total, device=DEVICE)
    train_b_idx = train_b_bytes[pos_train.unsqueeze(1) + offsets.unsqueeze(0)]
    train_b_targets = train_b_bytes[pos_train + K]

    _say(f"\nContinual training on corpus B...")
    for epoch in range(MAX_EPOCHS_B):
        for batch_start in range(0, T_total, BATCH_SIZE):
            be = min(batch_start + BATCH_SIZE, T_total)
            idx_batch = train_b_idx[batch_start:be]
            tgt_batch = train_b_targets[batch_start:be]
            ctxs = build_ctx_bundles_bsc(byte_atoms, pos_atoms, idx_batch)
            with torch.no_grad():
                q = ctxs @ W.T
                q = shifted_relu(q, RELU_B)
                sims = (byte_atoms @ q.T) / N
                P = torch.softmax(BETA * sims, dim=0)
                target_atoms_b = byte_atoms[tgt_batch]
                predicted = (P.T @ byte_atoms)
                residual = target_atoms_b - predicted
                dW = (residual.T @ ctxs) / N
                W.mul_(1.0 - DELTA_RULE_DECAY)
                W.add_(dW, alpha=DELTA_RULE_ALPHA)

    with torch.no_grad():
        post = eval_all(W)

    _say(f"\n========= PPMI M2 VERDICT =========")
    _say(f"  References: C1 post=4.3352, C3 factored=4.2370 (+0.098), minimal-M2-concept=4.5015 (-0.166)")
    _say(f"    C1 post = {post['c1']:.4f}")
    for mode in ["product", "rerank", "additive"]:
        gap = post['c1'] - post[f'c3_ppmi_{mode}']
        _say(f"    C3+PPMI ({mode}) = {post[f'c3_ppmi_{mode}']:.4f}  vs C1: {gap:+.4f}")

    best_method = min(["c3_ppmi_product", "c3_ppmi_rerank", "c3_ppmi_additive"], key=lambda m: post[m])
    best_gap = post["c1"] - post[best_method]
    _say(f"  Best: {best_method} gap {best_gap:+.4f}")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_m2_ppmi"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps(
        {"NUM_CONCEPTS": NUM_CONCEPTS, "PPMI_K": PPMI_K,
         "pre": pre, "post": post,
         "top_3_ppmi": [str(p) for p in ppmi_top[:3]],
         "best_method": best_method, "best_gap_vs_c1": best_gap},
        indent=2, default=str))
    _say(f"\nWrote {out_dir / 'metrics.json'}")


if __name__ == "__main__":
    main()
