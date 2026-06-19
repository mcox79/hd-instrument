"""Wave 14.B C3 factored: per-position factored kernel retrieval.

Survey: Wang-Karaletsos 2024 "Compositional Sparse Attention" - factor
attention kernel as K(q,m) = Σ_r K_r(q_r, m_r) with multiplicative or
log-sum-exp aggregation. Tucker decomposition for retrieval.

C3 minimal failed because it conflated positions into a partial-ctx
vector and used a single cosine. C3 factored computes per-position
scores separately, then aggregates.

For each pool bundle:
  - For each position r in {0, 1, 2}, compute score_r = <bundle * pos_r, byte_atom[ctx_r]>
  - Aggregate (e.g., sum-of-log-scores) to get total match strength
  - Use this as the retrieval weight
Then extract position-3 via 14.B same as before.

If C3-factored > C3-minimal: the factored kernel IS better. If still
worse than C1: byte-LM just doesn't benefit from compositional retrieval.

This is the survey's recommendation literally implemented.
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
BATCH_SIZE = 64
ALPHA = 0.3
MAX_EPOCHS_B = 15
EVAL_AT = [15]
RELU_B = 0.5
N = 4096
DELTA_RULE_ALPHA = 0.3
DELTA_RULE_DECAY = 1e-4
C3_MATCH_POSITIONS = [0, 1, 2]  # match positions; pos 3 is fill-in


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
    """C3 factored: per-position kernel, aggregated as sum-of-log-softmax.

    For each pool bundle, compute K(q, m) = sum_r K_r where
    K_r = (bundle * pos_r) . byte_atom[query[r]] / N

    This factored kernel preserves position-specific information instead
    of conflating into one ctx vector.
    """
    B = query_byte_indices.shape[0]
    if vsa_used == 0:
        return torch.full((VOCAB_SIZE, B), 1.0 / VOCAB_SIZE, device=byte_atoms.device)
    active = vsa_bundles[:vsa_used]  # (P, N)
    P = active.shape[0]

    # Compute factored score for each pool entry and each query
    # For position r:
    #   bundle * pos_r = byte_atom_r_stored + noise  (size: P, N)
    #   score_r[p, b] = (bundle_p * pos_r) . byte_atom[query[b, r]] / N
    # Total: score[p, b] = sum_r score_r[p, b]
    total_scores = torch.zeros((P, B), device=byte_atoms.device)
    for r in match_positions:
        # Project pool bundles through pos_r
        pool_proj_r = active * pos_atoms[r].unsqueeze(0)  # (P, N)
        # Query byte atoms at position r
        query_atoms_r = byte_atoms[query_byte_indices[:, r]]  # (B, N)
        # Per-position score
        score_r = (pool_proj_r @ query_atoms_r.T) / n  # (P, B)
        total_scores = total_scores + score_r

    weights = torch.softmax(beta_retrieval * total_scores, dim=0)  # (P, B)

    # Extract position-3 atom from each retrieved bundle (same as C2)
    target_estimates = active * target_pos.unsqueeze(0)  # (P, N)
    byte_scores = (target_estimates @ byte_atoms.T) / n  # (P, 256)
    P_byte_per_entry = torch.softmax(beta_byte * byte_scores, dim=1)
    return P_byte_per_entry.T @ weights


def eval_all(W, byte_atoms, pos_atoms, test_idx, test_targets,
            pool_vecs, pool_labels, pool_used,
            vsa_bundles, vsa_used, target_pos, alpha):
    T_test = test_idx.shape[0]
    bits = {"c0": 0.0, "c1": 0.0, "c3f": 0.0}
    for bs in range(0, T_test, BATCH_SIZE):
        be = min(bs + BATCH_SIZE, T_test)
        idx = test_idx[bs:be]
        ctxs = build_ctx_bundles_bsc(byte_atoms, pos_atoms, idx)
        P_W = predict_W(W, ctxs, byte_atoms, BETA, N)
        tgts = test_targets[bs:be]
        p_c0 = P_W.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)
        bits["c0"] += float(-torch.log2(p_c0).sum())
        P_c = predict_pool_classical(ctxs, pool_vecs, pool_labels, pool_used, BETA, N)
        P_1 = alpha * P_c + (1 - alpha) * P_W
        bits["c1"] += float(-torch.log2(P_1.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)).sum())
        P_3f = predict_pool_c3_factored(idx, vsa_bundles, vsa_used, byte_atoms, pos_atoms,
                                        target_pos, BETA, BYTE_BETA, N, C3_MATCH_POSITIONS)
        P_3 = alpha * P_3f + (1 - alpha) * P_W
        bits["c3f"] += float(-torch.log2(P_3.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)).sum())
    return {k: v / max(T_test, 1) for k, v in bits.items()}


def prepare_test_tensors(test_bytes_bytes, byte_atoms, pos_atoms):
    pad = bytes([PAD_BYTE]) * K
    padded = pad + test_bytes_bytes
    T = len(padded) - K
    bs_tensor = torch.tensor(list(padded), dtype=torch.long).to(DEVICE)
    offsets = torch.arange(K - 1, -1, -1, device=DEVICE)
    pos = torch.arange(T, device=DEVICE)
    idx = bs_tensor[pos.unsqueeze(1) + offsets.unsqueeze(0)]
    tgts = bs_tensor[pos + K]
    return idx, tgts


def build_vsa_pool(pool_vecs, pool_labels, pool_used, byte_atoms, target_pos):
    if pool_used == 0:
        return torch.zeros_like(pool_vecs)
    target_atoms = byte_atoms[pool_labels[:pool_used]]
    return pool_vecs[:pool_used] + target_atoms * target_pos.unsqueeze(0)


def main():
    _say(f"Wave 14.B C3 factored: per-position kernel retrieval")
    _say(f"  Match positions: {C3_MATCH_POSITIONS} factored")

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
    vsa_bundles = build_vsa_pool(pool_vecs, pool_labels, pool_used, byte_atoms, target_pos)

    test_a = state["test_a"]
    train_b = state["train_b"]
    test_a_idx, test_a_targets = prepare_test_tensors(test_a, byte_atoms, pos_atoms)

    _say(f"\nPre-shift eval:")
    pre = eval_all(W, byte_atoms, pos_atoms, test_a_idx, test_a_targets,
                  pool_vecs, pool_labels, pool_used, vsa_bundles, pool_used, target_pos, ALPHA)
    _say(f"  C0={pre['c0']:.4f}  C1={pre['c1']:.4f}  C3-fact={pre['c3f']:.4f}")
    _say(f"  Pre-shift C3-fact vs C1: {pre['c1']-pre['c3f']:+.4f}")

    pad = bytes([PAD_BYTE]) * K
    padded_train_b = pad + train_b
    T_total = len(padded_train_b) - K
    train_b_bytes = torch.tensor(list(padded_train_b), dtype=torch.long).to(DEVICE)
    offsets = torch.arange(K - 1, -1, -1, device=DEVICE)
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
        post = eval_all(W, byte_atoms, pos_atoms, test_a_idx, test_a_targets,
                       pool_vecs, pool_labels, pool_used, vsa_bundles, pool_used, target_pos, ALPHA)

    post_gap = post["c1"] - post["c3f"]
    pre_gap = pre["c1"] - pre["c3f"]
    _say(f"\n========= C3 FACTORED VERDICT =========")
    _say(f"  Pre-shift  C1={pre['c1']:.4f}  C3-fact={pre['c3f']:.4f}  gap={pre_gap:+.4f}")
    _say(f"  Post-shift C1={post['c1']:.4f}  C3-fact={post['c3f']:.4f}  gap={post_gap:+.4f}")
    _say(f"  Compare to C3-minimal: post-shift gap was -0.271 (C3 minimal was worse)")
    if post_gap > 0.01:
        _say(f"  C3 FACTORED BEATS C1: factored kernel is the right formulation.")
    elif post_gap > -0.05:
        _say(f"  C3 FACTORED close to C1: factored kernel helps but not enough.")
    else:
        _say(f"  C3 FACTORED still worse than C1: byte-LM may not benefit from compositional retrieval.")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_c3_factored"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps(
        {"C3_MATCH_POSITIONS": C3_MATCH_POSITIONS,
         "pre": pre, "post": post,
         "pre_gap": pre_gap, "post_gap": post_gap},
        indent=2, default=str))
    _say(f"\nWrote {out_dir / 'metrics.json'}")


if __name__ == "__main__":
    main()
