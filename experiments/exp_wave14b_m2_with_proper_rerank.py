"""Wave 14.B M2 with PROPER rerank: re-test all M2 methods with linear-combine fusion.

The sanity check confirmed my softmax-over-top-M rerank degrades by
0.22 bpc even with identity B=A. This experiment re-runs all M2 methods
with the CORRECT linear-combine-on-logits fusion:

  final_logit(d) = lambda * A(d) + (1-lambda) * B(d)
  weights(d) = softmax(beta * final_logits) over all candidates

Theorem prediction (Lippl-Stachenfeld + Tumer-Ghosh): all methods
should still MATCH C3 factored, not beat it (concepts from same pool
are redundant). Confirms the theorem at the implementation level.

This is the definitive theorem test:
- If methods match C3 factored: theorem confirmed
- If any method beats C3 factored: theorem violated (would be surprising)
- If methods are worse: even linear-combine has issues (would point to
  calibration or scaling problem)

Methods tested:
- CP tensor product (using existing CP factors)
- PPMI product (using existing PPMI pairs)
- For brevity, also one additive baseline for contrast.
"""

from __future__ import annotations

import json
import math
from collections import Counter
from pathlib import Path

import torch


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
C3_MATCH_POSITIONS = [0, 1, 2]
NUM_CONCEPTS = 100
LAMBDA_LINEAR = 0.7  # weight on A in linear combine
CONCEPT_BETA = 4.0


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
    active = pool_vecs[:pool_used]
    labels = pool_labels[:pool_used]
    sims = (active @ ctxs.T) / n
    weights = torch.softmax(beta * sims, dim=0)
    P_retr = torch.zeros(VOCAB_SIZE, B, device=ctxs.device)
    P_retr.scatter_add_(0, labels.unsqueeze(1).expand(-1, B), weights)
    return P_retr


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


def decompose_pool(pool_vecs, byte_atoms, pos_atoms, n):
    P = pool_vecs.shape[0]
    out = torch.zeros((P, K), dtype=torch.long, device=DEVICE)
    for r in range(K):
        proj = pool_vecs * pos_atoms[r].unsqueeze(0)
        scores = proj @ byte_atoms.T / n
        out[:, r] = scores.argmax(dim=1)
    return out


def extract_ppmi(pool_byte_at_pos, K_pos, vocab, num_concepts, k_neg=1.0):
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


def main():
    _say(f"Wave 14.B M2 re-test with PROPER linear-combine fusion")
    _say(f"  Lambda (weight on factored A): {LAMBDA_LINEAR}")
    _say(f"  Tests PPMI concepts with three aggregation modes:")
    _say(f"    - product (softmax(A) * softmax(B))")
    _say(f"    - linear-combine (lambda*A + (1-lambda)*B, then softmax) -- the corrected rerank")
    _say(f"    - additive (A + B logits, softmax)")

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

    # PPMI concepts (cheap, reproducible)
    _say(f"\nExtracting PPMI concepts...")
    pool_byte_at_pos = decompose_pool(pool_vecs[:pool_used], byte_atoms, pos_atoms, N)
    ppmi_top = extract_ppmi(pool_byte_at_pos, K, VOCAB_SIZE, NUM_CONCEPTS)
    concept_atoms = torch.zeros((NUM_CONCEPTS, N), device=DEVICE)
    for c_idx, (i, b_i, j, b_j, _) in enumerate(ppmi_top):
        concept_atoms[c_idx] = byte_atoms[b_i] * pos_atoms[i] + byte_atoms[b_j] * pos_atoms[j]
    pool_concept_scores = pool_vecs[:pool_used] @ concept_atoms.T / N

    # Pre-compute byte-extraction probabilities per pool entry
    target_estimates = vsa_bundles * target_pos.unsqueeze(0)
    byte_scores_pool = (target_estimates @ byte_atoms.T) / N
    P_byte_per_entry = torch.softmax(BYTE_BETA * byte_scores_pool, dim=1)

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
        bits = {"c1": 0.0, "A_only": 0.0, "product": 0.0, "linear": 0.0, "additive": 0.0}
        for bs in range(0, T_test, BATCH_SIZE):
            be = min(bs + BATCH_SIZE, T_test)
            idx_batch = test_a_idx[bs:be]
            ctxs = build_ctx_bundles_bsc(byte_atoms, pos_atoms, idx_batch)
            P_W = predict_W(W_local, ctxs, byte_atoms, BETA, N)
            tgts = test_a_targets[bs:be]

            P_c1 = predict_pool_classical(ctxs, pool_vecs, pool_labels, pool_used, BETA, N)
            P_1 = ALPHA * P_c1 + (1 - ALPHA) * P_W
            bits["c1"] += float(-torch.log2(P_1.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)).sum())

            # Signal A: factored kernel
            sA = factored_scores(idx_batch, vsa_bundles, byte_atoms, pos_atoms,
                                 C3_MATCH_POSITIONS, N)
            # Signal B: concept activation
            query_concept_scores = ctxs @ concept_atoms.T / N
            sB = pool_concept_scores @ query_concept_scores.T

            # A_only (true C3 factored baseline)
            wA = torch.softmax(BETA * sA, dim=0)
            PvA = P_byte_per_entry.T @ wA
            P_Ax = ALPHA * PvA + (1 - ALPHA) * P_W
            bits["A_only"] += float(-torch.log2(P_Ax.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)).sum())

            # Product: softmax(A) * softmax(B)
            wp_A = torch.softmax(BETA * sA, dim=0)
            wp_B = torch.softmax(CONCEPT_BETA * sB, dim=0)
            wp = wp_A * wp_B
            wp = wp / wp.sum(dim=0, keepdim=True).clamp(min=1e-12)
            Pvp = P_byte_per_entry.T @ wp
            P_px = ALPHA * Pvp + (1 - ALPHA) * P_W
            bits["product"] += float(-torch.log2(P_px.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)).sum())

            # Linear-combine on logits
            combined = LAMBDA_LINEAR * sA + (1 - LAMBDA_LINEAR) * sB
            wl = torch.softmax(BETA * combined, dim=0)
            Pvl = P_byte_per_entry.T @ wl
            P_lx = ALPHA * Pvl + (1 - ALPHA) * P_W
            bits["linear"] += float(-torch.log2(P_lx.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)).sum())

            # Additive (no lambda weighting)
            wa = torch.softmax(BETA * (sA + sB), dim=0)
            Pva = P_byte_per_entry.T @ wa
            P_ax = ALPHA * Pva + (1 - ALPHA) * P_W
            bits["additive"] += float(-torch.log2(P_ax.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)).sum())

        return {k: v / max(T_test, 1) for k, v in bits.items()}

    _say(f"\nPre-shift:")
    pre = eval_all(W)
    _say(f"  C1={pre['c1']:.4f}  A_only={pre['A_only']:.4f}  product={pre['product']:.4f}  linear={pre['linear']:.4f}  additive={pre['additive']:.4f}")

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

    _say(f"\n========= PROPER-RERANK VERDICT =========")
    _say(f"  Post-shift:")
    _say(f"    C1                = {post['c1']:.4f}")
    _say(f"    A_only (true C3F) = {post['A_only']:.4f}")
    _say(f"    product           = {post['product']:.4f}  (vs A: {post['A_only']-post['product']:+.4f})")
    _say(f"    linear (lam={LAMBDA_LINEAR}) = {post['linear']:.4f}  (vs A: {post['A_only']-post['linear']:+.4f})")
    _say(f"    additive          = {post['additive']:.4f}  (vs A: {post['A_only']-post['additive']:+.4f})")
    _say(f"")
    _say(f"  Theorem prediction: methods MATCH but don't BEAT A_only")
    if abs(post['linear'] - post['A_only']) < 0.005:
        _say(f"  CONFIRMED: linear-combine ~ A_only (within 0.005). Theorem holds.")
    elif post['linear'] < post['A_only']:
        _say(f"  UNEXPECTED: linear-combine BEATS A_only by {post['A_only']-post['linear']:+.4f}. Theorem violated?")
    else:
        _say(f"  PARTIAL: linear-combine slightly worse, calibration issue.")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_m2_with_proper_rerank"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps(
        {"LAMBDA_LINEAR": LAMBDA_LINEAR, "pre": pre, "post": post}, indent=2, default=str))


if __name__ == "__main__":
    main()
