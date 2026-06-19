"""Wave 14.B rerank sanity check: identity rerank (B = A).

Per the survey: the critical diagnostic for the rerank implementation
bug is to set B = A. If implementation is correct, identity rerank
should match A-alone. If it underperforms, the rerank pipeline is
broken independent of which B signal is used.

This tests my buggy softmax-over-top-M algorithm vs:
- A-alone (factored kernel only, what we observed at 4.2370)
- Corrected rerank: linear combination on logits (RRF-style)

Three rerank implementations compared:
1. BUGGY (current): softmax over top-M concept scores only, discards A
2. LINEAR: final = lambda * A + (1-lambda) * B, softmax over all
3. RRF: reciprocal rank fusion (Cormack 2009)

When B = A (identity), 1 should fail (underperform A), 2 and 3 should match A.
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
RELU_B = 0.5
N = 4096
DELTA_RULE_ALPHA = 0.3
DELTA_RULE_DECAY = 1e-4
C3_MATCH_POSITIONS = [0, 1, 2]
TOP_K_RR = 16
RRF_K = 60


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


def buggy_rerank(scores_A, scores_B, top_k, beta_b):
    """My broken rerank: softmax(B[top_M(A)]). Discards A scores within top-M."""
    P, B = scores_A.shape
    topk_idx = torch.topk(scores_A, k=min(top_k, P), dim=0).indices
    combined = torch.zeros_like(scores_A)
    for b in range(B):
        local_idx = topk_idx[:, b]
        local_b = scores_B[local_idx, b]
        local_w = torch.softmax(beta_b * local_b, dim=0)
        combined[local_idx, b] = local_w
    return combined


def linear_combine(scores_A, scores_B, lam, beta):
    """Linear combination on logits: lam*A + (1-lam)*B, then softmax."""
    combined_logits = lam * scores_A + (1 - lam) * scores_B
    return torch.softmax(beta * combined_logits, dim=0)


def rrf_combine(scores_A, scores_B, k_rrf):
    """Reciprocal Rank Fusion (Cormack 2009)."""
    P, B = scores_A.shape
    # Get ranks of each entry per query in each signal
    rank_A = scores_A.argsort(dim=0, descending=True).argsort(dim=0) + 1  # ranks 1..P
    rank_B = scores_B.argsort(dim=0, descending=True).argsort(dim=0) + 1
    rrf = 1.0 / (k_rrf + rank_A.float()) + 1.0 / (k_rrf + rank_B.float())
    weights = rrf / rrf.sum(dim=0, keepdim=True).clamp(min=1e-12)
    return weights


def predict_with_signals(scores_A, scores_B, target_extracts, beta_A, beta_byte, n, mode):
    """Apply combination mode to two signals, then weight target extracts."""
    if mode == "A_only":
        weights = torch.softmax(beta_A * scores_A, dim=0)
    elif mode == "B_only":
        weights = torch.softmax(beta_A * scores_B, dim=0)
    elif mode == "buggy_rerank":
        weights = buggy_rerank(scores_A, scores_B, TOP_K_RR, beta_A)
    elif mode == "linear":
        weights = linear_combine(scores_A, scores_B, 0.5, beta_A)
    elif mode == "rrf":
        weights = rrf_combine(scores_A, scores_B, RRF_K)
    else:
        raise ValueError(mode)
    return target_extracts.T @ weights


def main():
    _say(f"Wave 14.B rerank sanity check: identity rerank (B = A)")
    _say(f"  Comparing: A_only, buggy_rerank, linear_combine, rrf")

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

    # Pre-compute byte-extraction probabilities per pool entry (same for all modes)
    target_estimates = vsa_bundles * target_pos.unsqueeze(0)
    byte_scores_pool = (target_estimates @ byte_atoms.T) / N
    P_byte_per_entry = torch.softmax(BYTE_BETA * byte_scores_pool, dim=1)  # (P, 256)

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
        bits = {"c1": 0.0, "A_only": 0.0, "buggy_rerank": 0.0, "linear": 0.0, "rrf": 0.0}
        for bs in range(0, T_test, BATCH_SIZE):
            be = min(bs + BATCH_SIZE, T_test)
            idx_batch = test_a_idx[bs:be]
            ctxs = build_ctx_bundles_bsc(byte_atoms, pos_atoms, idx_batch)
            P_W = predict_W(W_local, ctxs, byte_atoms, BETA, N)
            tgts = test_a_targets[bs:be]
            P_c1 = predict_pool_classical(ctxs, pool_vecs, pool_labels, pool_used, BETA, N)
            P_1 = ALPHA * P_c1 + (1 - ALPHA) * P_W
            bits["c1"] += float(-torch.log2(P_1.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)).sum())

            # IDENTITY: B = A (use factored scores as both signals)
            sA = factored_scores(idx_batch, vsa_bundles, byte_atoms, pos_atoms, C3_MATCH_POSITIONS, N)
            sB = sA  # identity

            for mode in ["A_only", "buggy_rerank", "linear", "rrf"]:
                P_v = predict_with_signals(sA, sB, P_byte_per_entry, BETA, BYTE_BETA, N, mode)
                P_x = ALPHA * P_v + (1 - ALPHA) * P_W
                bits[mode] += float(-torch.log2(P_x.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)).sum())
        return {k: v / max(T_test, 1) for k, v in bits.items()}

    _say(f"\nPre-shift eval (IDENTITY rerank, B=A):")
    pre = eval_all(W)
    _say(f"  C1={pre['c1']:.4f}  A_only={pre['A_only']:.4f}  buggy={pre['buggy_rerank']:.4f}  linear={pre['linear']:.4f}  rrf={pre['rrf']:.4f}")

    # Train on B
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

    _say(f"\n========= RERANK SANITY CHECK VERDICT =========")
    _say(f"  Post-shift (B = A, identity rerank):")
    _say(f"    A_only         = {post['A_only']:.4f}  (the true C3 factored)")
    _say(f"    buggy_rerank   = {post['buggy_rerank']:.4f}  (my broken algorithm)")
    _say(f"    linear_combine = {post['linear']:.4f}  (lambda=0.5, RFR-style)")
    _say(f"    rrf            = {post['rrf']:.4f}  (Cormack 2009)")
    _say(f"")
    _say(f"  Expected: A_only ≈ linear ≈ rrf (B=A means redundant signal)")
    _say(f"  Expected: buggy_rerank significantly worse if bug confirmed")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_rerank_sanity_check"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps(
        {"pre": pre, "post": post}, indent=2, default=str))
    _say(f"\nWrote {out_dir / 'metrics.json'}")


if __name__ == "__main__":
    main()
