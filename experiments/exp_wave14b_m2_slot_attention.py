"""Wave 14.B M2 slot attention: competitive concept discovery from pool.

Most ambitious M2 variant. Replaces minimal M2's "count top-K bigrams"
with Locatello 2020-style iterative slot attention. Slots are competing
latent concept atoms that emerge from iterative assignment.

Algorithm:
1. Initialize K_slots random unit vectors as concept seeds.
2. For T iterations:
   - Compute similarities: sim[p, k] = (pool_entry_p . slot_k) / ||slot_k||
   - Attention: weights[p, k] = softmax_over_k(beta * sim)
   - Slot update: slot_k = weighted average of pool entries assigned to it
3. After convergence, slots are emergent concept atoms.

Compared to minimal M2:
- Discovers ABSTRACT patterns by clustering, not SURFACE patterns by counting
- Slots COMPETE (winner-take-most), enforcing differentiation
- Iterative refinement instead of one-shot counting
- Number of slots is small (16-32) so concepts are high-quality

At retrieval time, use slot loadings as concept signatures, combined
with C3 factored via product (multiplicative aggregation, not additive).

Pre-registered hypothesis:
- If slot attention finds structural patterns: C3 + slot beats C3 alone
- If slots end up just clustering surface frequencies: similar regression as minimal M2
- If slots collapse (all become identical): clear failure mode, easy to detect

Most ambitious from the unbiased options. If this fails, fallback to NMF
or PMI-based approaches.
"""

from __future__ import annotations

import json
import time
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
SLOT_BETA = 4.0
BATCH_SIZE = 64
ALPHA = 0.3
MAX_EPOCHS_B = 15
RELU_B = 0.5
N = 4096
DELTA_RULE_ALPHA = 0.3
DELTA_RULE_DECAY = 1e-4
NUM_SLOTS = 16
SLOT_ITERS = 20
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


def slot_attention(pool_vecs, num_slots, num_iters, beta_slot, n, gen):
    """Locatello-style slot attention to extract emergent concepts.

    Args:
        pool_vecs: (P, N) pool entries
        num_slots: number of competing slots
        num_iters: iterations of attention refinement
        beta_slot: softmax temperature for slot assignment
        gen: torch generator

    Returns:
        slots: (num_slots, N) - emergent concept atoms
        loadings: (P, num_slots) - final slot assignment for each pool entry
    """
    P = pool_vecs.shape[0]
    # Initialize slots from random pool entries (better than pure random)
    init_idx = torch.randperm(P, generator=gen)[:num_slots]
    slots = pool_vecs[init_idx].clone()
    # Add small jitter so they differentiate
    jitter = (torch.randn(slots.shape, generator=gen) * 0.01).to(slots.device)
    slots = slots + jitter
    # Normalize slots
    slots = slots / slots.norm(dim=1, keepdim=True).clamp(min=1e-12)

    for it in range(num_iters):
        # Similarities between pool entries and slots
        # Normalize pool entries too for cosine similarity
        pool_norms = pool_vecs.norm(dim=1, keepdim=True).clamp(min=1e-12)
        pool_normalized = pool_vecs / pool_norms
        sims = pool_normalized @ slots.T  # (P, num_slots)

        # Softmax over slots: each pool entry assigns to slots
        attention = torch.softmax(beta_slot * sims, dim=1)  # (P, num_slots)

        # Normalize over pool entries: each slot gets proportional weight
        weights = attention / attention.sum(dim=0, keepdim=True).clamp(min=1e-12)  # (P, num_slots)

        # Slot update: weighted average of pool entries
        slots_new = weights.T @ pool_vecs  # (num_slots, N)
        # Normalize again
        slots_new = slots_new / slots_new.norm(dim=1, keepdim=True).clamp(min=1e-12)
        slots = slots_new

    # Final loadings: how strongly does each pool entry activate each slot?
    pool_norms = pool_vecs.norm(dim=1, keepdim=True).clamp(min=1e-12)
    pool_normalized = pool_vecs / pool_norms
    final_loadings = pool_normalized @ slots.T  # (P, num_slots)

    return slots, final_loadings


def predict_pool_c3_with_slots(query_byte_indices, ctxs, vsa_bundles, vsa_used,
                                byte_atoms, pos_atoms, target_pos,
                                slots, pool_loadings,
                                beta_retrieval, beta_byte, beta_slot, n,
                                match_positions, aggregation="product"):
    """C3 factored + slot-based concept similarity.

    Two retrieval signals:
    1. Per-position factored kernel (C3 factored)
    2. Slot loading similarity (query loadings vs pool loadings)

    Combined via product (multiplicative — both signals must agree for
    high retrieval weight).
    """
    B = query_byte_indices.shape[0]
    P = vsa_bundles.shape[0]

    # Signal 1: factored per-position scores
    factored_scores = torch.zeros((P, B), device=byte_atoms.device)
    for r in match_positions:
        pool_proj_r = vsa_bundles * pos_atoms[r].unsqueeze(0)
        query_atoms_r = byte_atoms[query_byte_indices[:, r]]
        factored_scores += (pool_proj_r @ query_atoms_r.T) / n

    # Signal 2: query loadings via slots, then similarity to pool loadings
    ctx_norms = ctxs.norm(dim=1, keepdim=True).clamp(min=1e-12)
    ctx_normalized = ctxs / ctx_norms
    query_loadings = ctx_normalized @ slots.T  # (B, num_slots)
    # Score: dot product of pool loadings against query loadings
    slot_scores = pool_loadings @ query_loadings.T  # (P, B)

    if aggregation == "product":
        # Multiplicative: softmax each separately, then product
        weights_fact = torch.softmax(beta_retrieval * factored_scores, dim=0)
        weights_slot = torch.softmax(beta_slot * slot_scores, dim=0)
        combined = weights_fact * weights_slot
        combined = combined / combined.sum(dim=0, keepdim=True).clamp(min=1e-12)
    elif aggregation == "rerank":
        # Top-K by factored, rerank by slots within top-K
        TOP_K = 16
        topk_idx = torch.topk(factored_scores, k=min(TOP_K, P), dim=0).indices  # (TOP_K, B)
        combined = torch.zeros((P, B), device=byte_atoms.device)
        for b in range(B):
            local_idx = topk_idx[:, b]
            local_slot = slot_scores[local_idx, b]
            local_weights = torch.softmax(beta_slot * local_slot, dim=0)
            combined[local_idx, b] = local_weights
    else:
        # Additive baseline (will likely fail like minimal M2)
        combined_scores = factored_scores + slot_scores
        combined = torch.softmax(beta_retrieval * combined_scores, dim=0)

    # Extract target estimates
    target_estimates = vsa_bundles * target_pos.unsqueeze(0)
    byte_scores = (target_estimates @ byte_atoms.T) / n
    P_byte_per_entry = torch.softmax(beta_byte * byte_scores, dim=1)
    return P_byte_per_entry.T @ combined


def main():
    _say(f"Wave 14.B M2 slot attention: competitive concept discovery")
    _say(f"  NUM_SLOTS={NUM_SLOTS}, SLOT_ITERS={SLOT_ITERS}, SLOT_BETA={SLOT_BETA}")

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

    # === Extract slots via slot attention ===
    _say(f"\nExtracting {NUM_SLOTS} concept slots via {SLOT_ITERS}-step slot attention...")
    slot_gen = torch.Generator().manual_seed(SEED + 1234)
    slots, pool_loadings = slot_attention(
        pool_vecs[:pool_used], NUM_SLOTS, SLOT_ITERS, SLOT_BETA, N, slot_gen
    )
    _say(f"  slots shape: {slots.shape}, pool_loadings shape: {pool_loadings.shape}")

    # Diagnostic: slot uniqueness (how distinct are the discovered slots?)
    slot_pairwise = slots @ slots.T  # (NUM_SLOTS, NUM_SLOTS)
    off_diag = slot_pairwise - torch.eye(NUM_SLOTS, device=DEVICE)
    max_pair = off_diag.abs().max().item()
    mean_pair = off_diag.abs().mean().item()
    _say(f"  Slot uniqueness: max pairwise sim {max_pair:.3f}, mean {mean_pair:.3f}")
    if max_pair > 0.95:
        _say(f"  WARNING: slots collapsed to near-identical. Algorithm failed.")

    # === Prepare for eval ===
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
        bits = {"c1": 0.0, "c3_slot_product": 0.0, "c3_slot_rerank": 0.0, "c3_slot_additive": 0.0}
        for bs in range(0, T_test, BATCH_SIZE):
            be = min(bs + BATCH_SIZE, T_test)
            idx_batch = test_a_idx[bs:be]
            ctxs = build_ctx_bundles_bsc(byte_atoms, pos_atoms, idx_batch)
            P_W = predict_W(W_local, ctxs, byte_atoms, BETA, N)
            tgts = test_a_targets[bs:be]

            # C1 baseline
            P_c1 = predict_pool_classical(ctxs, pool_vecs, pool_labels, pool_used, BETA, N)
            P_1 = ALPHA * P_c1 + (1 - ALPHA) * P_W
            bits["c1"] += float(-torch.log2(P_1.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)).sum())

            # C3 + slot via product
            P_c3_prod = predict_pool_c3_with_slots(idx_batch, ctxs, vsa_bundles, pool_used,
                                                    byte_atoms, pos_atoms, target_pos,
                                                    slots, pool_loadings,
                                                    BETA, BYTE_BETA, SLOT_BETA, N,
                                                    C3_MATCH_POSITIONS, "product")
            P_3p = ALPHA * P_c3_prod + (1 - ALPHA) * P_W
            bits["c3_slot_product"] += float(-torch.log2(P_3p.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)).sum())

            # C3 + slot via rerank
            P_c3_rk = predict_pool_c3_with_slots(idx_batch, ctxs, vsa_bundles, pool_used,
                                                  byte_atoms, pos_atoms, target_pos,
                                                  slots, pool_loadings,
                                                  BETA, BYTE_BETA, SLOT_BETA, N,
                                                  C3_MATCH_POSITIONS, "rerank")
            P_3r = ALPHA * P_c3_rk + (1 - ALPHA) * P_W
            bits["c3_slot_rerank"] += float(-torch.log2(P_3r.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)).sum())

            # C3 + slot via additive (baseline that should fail like minimal M2)
            P_c3_add = predict_pool_c3_with_slots(idx_batch, ctxs, vsa_bundles, pool_used,
                                                   byte_atoms, pos_atoms, target_pos,
                                                   slots, pool_loadings,
                                                   BETA, BYTE_BETA, SLOT_BETA, N,
                                                   C3_MATCH_POSITIONS, "additive")
            P_3a = ALPHA * P_c3_add + (1 - ALPHA) * P_W
            bits["c3_slot_additive"] += float(-torch.log2(P_3a.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)).sum())

        return {k: v / max(T_test, 1) for k, v in bits.items()}

    _say(f"\nPre-shift eval:")
    pre = eval_all(W)
    _say(f"  C1={pre['c1']:.4f}  C3+slot(prod)={pre['c3_slot_product']:.4f}  "
         f"C3+slot(rerank)={pre['c3_slot_rerank']:.4f}  C3+slot(add)={pre['c3_slot_additive']:.4f}")
    _say(f"  Reference: C3 factored alone pre-shift was 2.4924; C1 was 2.4817")

    # Continual training on corpus B
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

    _say(f"\n========= SLOT ATTENTION M2 VERDICT =========")
    _say(f"  References (pre-existing):")
    _say(f"    C1 post-shift: 4.3352")
    _say(f"    C3 factored alone: 4.2370 (+0.098 vs C1)")
    _say(f"    C3 + minimal-M2-concept: 4.5015 (-0.166 vs C1, REGRESSION)")
    _say(f"  Slot attention variants:")
    _say(f"    C1 post = {post['c1']:.4f}")
    _say(f"    C3 + slot (product)  = {post['c3_slot_product']:.4f}  vs C1: {post['c1']-post['c3_slot_product']:+.4f}")
    _say(f"    C3 + slot (rerank)   = {post['c3_slot_rerank']:.4f}  vs C1: {post['c1']-post['c3_slot_rerank']:+.4f}")
    _say(f"    C3 + slot (additive) = {post['c3_slot_additive']:.4f}  vs C1: {post['c1']-post['c3_slot_additive']:+.4f}")

    best_method = min(["c3_slot_product", "c3_slot_rerank", "c3_slot_additive"], key=lambda m: post[m])
    best_gap = post["c1"] - post[best_method]
    if best_gap > 0.05:
        _say(f"  BEST: {best_method} beats C1 by {best_gap:+.4f}. SLOT ATTENTION WORKS.")
    elif best_gap > 0:
        _say(f"  BEST: {best_method} marginally beats C1 by {best_gap:+.4f}.")
    else:
        _say(f"  BEST: {best_method} loses to C1 by {best_gap:+.4f}. Slot attention not enough.")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_m2_slot_attention"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps(
        {"NUM_SLOTS": NUM_SLOTS, "SLOT_ITERS": SLOT_ITERS, "SLOT_BETA": SLOT_BETA,
         "pre": pre, "post": post,
         "slot_uniqueness_max": max_pair, "slot_uniqueness_mean": mean_pair,
         "best_method": best_method, "best_gap_vs_c1": best_gap},
        indent=2, default=str))
    _say(f"\nWrote {out_dir / 'metrics.json'}")


if __name__ == "__main__":
    main()
