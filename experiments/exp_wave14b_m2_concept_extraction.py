"""Wave 14.B M2 prototype: concept atom extraction from pool + C3 over consolidated.

Minimal M2 implementation per design doc. Tests whether concept atoms
mined from recurring co-occurrences add to C3 factored's retrieval.

Pipeline:
1. Decompose pool entries into (byte, position) bindings (trivial - we
   know what's in them from pool_labels and ctx construction).
2. Count co-occurrence frequencies of (byte_i @ pos_i, byte_j @ pos_j)
   pairs across all pool entries.
3. Take top-K = 100 most frequent pairs. Create concept atoms as
   bundles of these pairs.
4. For each pool entry, compute "concept signature" = scores against
   all concept atoms.
5. At query time, retrieve by combined score:
   - Per-position factored kernel (C3 factored from previous experiment)
   - PLUS concept signature similarity

Pre-registered prediction:
- If concepts capture useful structure NOT already in factored kernel:
  combined retrieval beats C3 factored alone by >0.02 bpc post-shift.
- If concepts redundant with per-position factored: no improvement.
- If concepts hurt (over-fit to A-distribution structure that B violates):
  combined retrieval underperforms.

The "additive" hypothesis the user pushed: M2 concept atoms add value
on top of C3 factored. This experiment tests that hypothesis directly.
"""

from __future__ import annotations

import json
import time
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
CONCEPT_BETA = 8.0
BATCH_SIZE = 64
ALPHA = 0.3
MAX_EPOCHS_B = 15
RELU_B = 0.5
N = 4096
DELTA_RULE_ALPHA = 0.3
DELTA_RULE_DECAY = 1e-4
NUM_CONCEPTS = 100
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


def predict_pool_c3_factored(query_byte_indices, vsa_bundles, vsa_used,
                            byte_atoms, pos_atoms, target_pos,
                            beta_retrieval, beta_byte, n,
                            match_positions):
    """C3 factored from previous experiment (matched per-position)."""
    B = query_byte_indices.shape[0]
    if vsa_used == 0:
        return torch.full((VOCAB_SIZE, B), 1.0 / VOCAB_SIZE, device=byte_atoms.device)
    active = vsa_bundles[:vsa_used]
    P = active.shape[0]
    total_scores = torch.zeros((P, B), device=byte_atoms.device)
    for r in match_positions:
        pool_proj_r = active * pos_atoms[r].unsqueeze(0)
        query_atoms_r = byte_atoms[query_byte_indices[:, r]]
        score_r = (pool_proj_r @ query_atoms_r.T) / n
        total_scores = total_scores + score_r
    weights = torch.softmax(beta_retrieval * total_scores, dim=0)
    target_estimates = active * target_pos.unsqueeze(0)
    byte_scores = (target_estimates @ byte_atoms.T) / n
    P_byte_per_entry = torch.softmax(beta_byte * byte_scores, dim=1)
    return P_byte_per_entry.T @ weights


def extract_concept_atoms(pool_labels, pool_used, byte_atoms, pos_atoms, num_concepts):
    """M2 minimal: count recurring (byte@pos, byte@pos) pairs in pool.

    For each pool entry, we know the K context bytes at positions 0..K-1
    from pool_labels (the label is the TARGET byte; context bytes come
    from the ctx that we stored).

    BUT — pool_labels stores only the target. The ctx itself is the
    stored bundle. We need to reconstruct what bytes were at what
    positions from the ctx vector via decomposition.

    Simple approach: cleanup each (ctx * pos_r) against byte_atoms to
    find the byte at position r in each pool entry.
    """
    return None  # Will fill in inline below


def main():
    _say(f"Wave 14.B M2 concept extraction + C3 over consolidated pool")
    _say(f"  num_concepts={NUM_CONCEPTS}, C3 match positions={C3_MATCH_POSITIONS}")

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

    # === STEP 1: Decompose each pool entry into (byte, position) bindings ===
    _say(f"\nDecomposing {pool_used} pool entries...")
    pool_byte_at_pos = torch.zeros((pool_used, K), dtype=torch.long, device=DEVICE)
    for r in range(K):
        # ctx * pos_r should = byte_at_position_r + noise
        # cleanup against byte codebook
        per_ctx_r_projection = pool_vecs[:pool_used] * pos_atoms[r].unsqueeze(0)  # (P, N)
        byte_scores = per_ctx_r_projection @ byte_atoms.T / N  # (P, 256)
        pool_byte_at_pos[:, r] = byte_scores.argmax(dim=1)
    _say(f"  Decomposed all pool entries.")

    # === STEP 2: Count co-occurrences of (byte, pos) pairs across pool ===
    _say(f"\nCounting co-occurrence frequencies...")
    pair_counts = Counter()
    for entry_idx in range(pool_used):
        bytes_at_pos = pool_byte_at_pos[entry_idx].cpu().tolist()
        # All pairs of (i, byte_i) with i < j
        for i in range(K):
            for j in range(i + 1, K):
                key = (i, bytes_at_pos[i], j, bytes_at_pos[j])
                pair_counts[key] += 1
    top_pairs = pair_counts.most_common(NUM_CONCEPTS)
    _say(f"  Found {len(pair_counts)} unique pairs, top {NUM_CONCEPTS} kept.")
    _say(f"  Top-3 pairs (freq): {top_pairs[:3]}")

    # === STEP 3: Build concept atoms ===
    _say(f"\nBuilding {NUM_CONCEPTS} concept atoms...")
    concept_atoms = torch.zeros((NUM_CONCEPTS, N), device=DEVICE)
    for c_idx, ((i, b_i, j, b_j), freq) in enumerate(top_pairs):
        # concept atom = bundle of (byte_i @ pos_i, byte_j @ pos_j)
        concept = byte_atoms[b_i] * pos_atoms[i] + byte_atoms[b_j] * pos_atoms[j]
        concept_atoms[c_idx] = concept
    _say(f"  Built concept atom matrix: {concept_atoms.shape}")

    # === STEP 4: Compute concept signature for each pool entry ===
    _say(f"\nComputing concept signatures for pool entries...")
    # Each pool entry's "signature" = cosine scores against all concept atoms
    pool_concept_scores = pool_vecs[:pool_used] @ concept_atoms.T / N  # (P, NUM_CONCEPTS)
    _say(f"  Pool concept signatures: {pool_concept_scores.shape}")

    # === STEP 5: Eval — C3 factored alone vs C3 factored + concept retrieval ===
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
        bits = {"c0": 0.0, "c1": 0.0, "c3f": 0.0, "c3f_concept": 0.0}
        for bs in range(0, T_test, BATCH_SIZE):
            be = min(bs + BATCH_SIZE, T_test)
            idx_batch = test_a_idx[bs:be]
            ctxs = build_ctx_bundles_bsc(byte_atoms, pos_atoms, idx_batch)
            P_W = predict_W(W_local, ctxs, byte_atoms, BETA, N)
            tgts = test_a_targets[bs:be]

            # C0
            p_c0 = P_W.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)
            bits["c0"] += float(-torch.log2(p_c0).sum())

            # C1 classical
            P_c1 = predict_pool_classical(ctxs, pool_vecs, pool_labels, pool_used, BETA, N)
            P_1 = ALPHA * P_c1 + (1 - ALPHA) * P_W
            bits["c1"] += float(-torch.log2(P_1.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)).sum())

            # C3 factored alone
            P_c3 = predict_pool_c3_factored(idx_batch, vsa_bundles, pool_used, byte_atoms, pos_atoms,
                                            target_pos, BETA, BYTE_BETA, N, C3_MATCH_POSITIONS)
            P_3 = ALPHA * P_c3 + (1 - ALPHA) * P_W
            bits["c3f"] += float(-torch.log2(P_3.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)).sum())

            # C3 factored + concept similarity
            # Compute query concept signature
            query_concept_scores = ctxs @ concept_atoms.T / N  # (B, NUM_CONCEPTS)
            # For each (pool, query) pair: score = factored + concept-sim
            B = idx_batch.shape[0]
            factored_scores = torch.zeros((pool_used, B), device=DEVICE)
            for r in C3_MATCH_POSITIONS:
                pool_proj_r = vsa_bundles * pos_atoms[r].unsqueeze(0)
                query_atoms_r = byte_atoms[idx_batch[:, r]]
                factored_scores += (pool_proj_r @ query_atoms_r.T) / N
            concept_sim = pool_concept_scores @ query_concept_scores.T  # (pool, B) — dot product of signatures
            combined_scores = factored_scores + concept_sim
            weights = torch.softmax(BETA * combined_scores, dim=0)
            target_estimates = vsa_bundles * target_pos.unsqueeze(0)
            byte_scores = (target_estimates @ byte_atoms.T) / N
            P_byte_per_entry = torch.softmax(BYTE_BETA * byte_scores, dim=1)
            P_c3_concept = P_byte_per_entry.T @ weights
            P_3c = ALPHA * P_c3_concept + (1 - ALPHA) * P_W
            bits["c3f_concept"] += float(-torch.log2(P_3c.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)).sum())

        return {k: v / max(T_test, 1) for k, v in bits.items()}

    _say(f"\nPre-shift eval:")
    pre = eval_all(W)
    _say(f"  C0={pre['c0']:.4f}  C1={pre['c1']:.4f}  C3-fact={pre['c3f']:.4f}  C3+concept={pre['c3f_concept']:.4f}")
    _say(f"  Pre-shift C3+concept vs C3-fact: {pre['c3f']-pre['c3f_concept']:+.4f}")

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

    _say(f"\n========= M2 CONCEPT EXTRACTION VERDICT =========")
    _say(f"  Pre-shift  C3-fact={pre['c3f']:.4f}  C3+concept={pre['c3f_concept']:.4f}  gap={pre['c3f']-pre['c3f_concept']:+.4f}")
    _say(f"  Post-shift C3-fact={post['c3f']:.4f}  C3+concept={post['c3f_concept']:.4f}  gap={post['c3f']-post['c3f_concept']:+.4f}")
    _say(f"  Also: C1 post={post['c1']:.4f}, C3+concept beats C1 by {post['c1']-post['c3f_concept']:+.4f}")
    post_gain = post["c3f"] - post["c3f_concept"]
    if post_gain > 0.02:
        _say(f"  CONCEPTS HELP: +{post_gain:.4f} bpc on top of C3 factored. ADDITIVE confirmed.")
    elif post_gain > -0.01:
        _say(f"  CONCEPTS NEUTRAL: C3 factored already captures the structure.")
    else:
        _say(f"  CONCEPTS HURT: signatures over-fit to corpus A.")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_m2_concept_extraction"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps(
        {"NUM_CONCEPTS": NUM_CONCEPTS, "C3_MATCH_POSITIONS": C3_MATCH_POSITIONS,
         "pre": pre, "post": post,
         "post_concept_gain_over_c3f": post_gain,
         "post_combined_vs_c1": post["c1"] - post["c3f_concept"],
         "top_3_concepts": [str(t) for t in top_pairs[:3]]},
        indent=2, default=str))
    _say(f"\nWrote {out_dir / 'metrics.json'}")


if __name__ == "__main__":
    main()
