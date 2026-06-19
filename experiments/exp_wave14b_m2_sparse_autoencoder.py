"""Wave 14.B M2 sparse autoencoder: Top-K SAE for concept extraction.

Per the unbiased research synthesis (Templeton 2024, Gao 2024,
Bussmann 2024, Rajamanoharan 2024): Top-K sparse autoencoders are the
current frontier for extracting monosemantic features from
high-dimensional representations.

Algorithm:
1. Encoder: h = TopK(W_e @ v + b_e)  -- ReLU implicit via TopK
2. Decoder: v_hat = W_d @ h           -- W_d column-normalized
3. Loss: ||v - v_hat||^2

The dictionary W_d (columns) becomes our concept atoms. Each pool entry
activates K of them, giving an explicit sparse decomposition.

For retrieval: query is encoded to its sparse code, similarity computed
in code space (where similar entries activate overlapping features).

This is the highest-empirical-ceiling method per the survey. Scales to
much larger feature dictionaries than co-occurrence approaches.

Pre-registered:
- If SAE dictionary captures structural patterns: C3 + SAE beats C3
  factored alone (post-shift)
- If SAE collapses or finds trivial features: similar regression as
  minimal M2 / slot attention
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import torch
import torch.nn as nn


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
SAE_DICT_SIZE = 256  # ~8x overcomplete relative to bundle dim (a la Templeton 2024)
SAE_TOP_K = 8  # active features per bundle
SAE_TRAIN_EPOCHS = 200
SAE_LR = 1e-3
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


def train_topk_sae(pool_vecs, dict_size, top_k, epochs, lr, n):
    """Train Top-K SAE on pool vectors. Returns the trained encoder/decoder."""
    pool_size = pool_vecs.shape[0]
    # Encoder weights W_e (dict_size, N), bias b_e (dict_size,)
    W_e = torch.randn((dict_size, n), device=DEVICE) / (n ** 0.5)
    b_e = torch.zeros(dict_size, device=DEVICE)
    # Decoder weights W_d (n, dict_size), column-normalized
    W_d = torch.randn((n, dict_size), device=DEVICE) / (dict_size ** 0.5)
    W_d = W_d / W_d.norm(dim=0, keepdim=True).clamp(min=1e-12)

    W_e.requires_grad_(True)
    b_e.requires_grad_(True)
    W_d.requires_grad_(True)
    optimizer = torch.optim.AdamW([W_e, b_e, W_d], lr=lr, weight_decay=0)

    losses = []
    for epoch in range(epochs):
        # Encode
        pre = pool_vecs @ W_e.T + b_e  # (P, dict_size)
        # Top-K activation
        topk_vals, topk_idx = pre.topk(k=top_k, dim=1)
        h = torch.zeros_like(pre)
        h.scatter_(1, topk_idx, torch.clamp(topk_vals, min=0))  # ReLU + TopK
        # Decode
        v_hat = h @ W_d.T  # (P, N)
        # Loss
        loss = ((pool_vecs - v_hat) ** 2).mean()
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        # Re-normalize decoder columns
        with torch.no_grad():
            W_d.data = W_d.data / W_d.data.norm(dim=0, keepdim=True).clamp(min=1e-12)
        losses.append(loss.item())

    return W_e.detach(), b_e.detach(), W_d.detach(), losses


def encode_sae(v, W_e, b_e, top_k):
    """Encode vectors using trained SAE: returns sparse codes (P, dict_size)."""
    pre = v @ W_e.T + b_e
    topk_vals, topk_idx = pre.topk(k=top_k, dim=1)
    h = torch.zeros_like(pre)
    h.scatter_(1, topk_idx, torch.clamp(topk_vals, min=0))
    return h


def predict_pool_c3_with_sae(query_byte_indices, ctxs, vsa_bundles, vsa_used,
                              byte_atoms, pos_atoms, target_pos,
                              W_e, b_e, pool_codes,
                              beta_retrieval, beta_byte, beta_sae, n,
                              match_positions, aggregation):
    """C3 factored + SAE concept similarity."""
    B = query_byte_indices.shape[0]
    P = vsa_bundles.shape[0]

    # C3 factored scores
    factored_scores = torch.zeros((P, B), device=byte_atoms.device)
    for r in match_positions:
        pool_proj_r = vsa_bundles * pos_atoms[r].unsqueeze(0)
        query_atoms_r = byte_atoms[query_byte_indices[:, r]]
        factored_scores += (pool_proj_r @ query_atoms_r.T) / n

    # SAE: encode queries, compute code similarity to pool codes
    query_codes = encode_sae(ctxs, W_e, b_e, SAE_TOP_K)  # (B, dict_size)
    sae_scores = pool_codes @ query_codes.T  # (P, B) — dot product of sparse codes

    if aggregation == "product":
        wf = torch.softmax(beta_retrieval * factored_scores, dim=0)
        ws = torch.softmax(beta_sae * sae_scores, dim=0)
        combined = wf * ws
        combined = combined / combined.sum(dim=0, keepdim=True).clamp(min=1e-12)
    elif aggregation == "rerank":
        TOP_K_RERANK = 16
        topk_idx = torch.topk(factored_scores, k=min(TOP_K_RERANK, P), dim=0).indices
        combined = torch.zeros((P, B), device=byte_atoms.device)
        for b in range(B):
            local_idx = topk_idx[:, b]
            local_sae = sae_scores[local_idx, b]
            local_weights = torch.softmax(beta_sae * local_sae, dim=0)
            combined[local_idx, b] = local_weights
    else:
        combined = torch.softmax(beta_retrieval * (factored_scores + sae_scores), dim=0)

    target_estimates = vsa_bundles * target_pos.unsqueeze(0)
    byte_scores = (target_estimates @ byte_atoms.T) / n
    P_byte_per_entry = torch.softmax(beta_byte * byte_scores, dim=1)
    return P_byte_per_entry.T @ combined


def main():
    _say(f"Wave 14.B M2 Top-K SAE: sparse autoencoder concept extraction")
    _say(f"  dict_size={SAE_DICT_SIZE}, top_k={SAE_TOP_K}, train_epochs={SAE_TRAIN_EPOCHS}")

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

    # Train SAE on pool entries
    _say(f"\nTraining Top-K SAE on {pool_used} pool entries...")
    W_e, b_e, W_d, losses = train_topk_sae(pool_vecs[:pool_used], SAE_DICT_SIZE, SAE_TOP_K,
                                            SAE_TRAIN_EPOCHS, SAE_LR, N)
    _say(f"  Final loss: {losses[-1]:.6f}  (started: {losses[0]:.6f})")
    _say(f"  Loss reduction: {(losses[0] - losses[-1]) / losses[0] * 100:.1f}%")

    # Encode pool entries
    pool_codes = encode_sae(pool_vecs[:pool_used], W_e, b_e, SAE_TOP_K)
    _say(f"  Pool codes: {pool_codes.shape}, sparsity: {(pool_codes > 0).float().mean():.3f}")

    # Diagnostic: dictionary uniqueness
    W_d_pairwise = W_d.T @ W_d
    off_diag = W_d_pairwise - torch.eye(SAE_DICT_SIZE, device=DEVICE)
    max_pair = off_diag.abs().max().item()
    mean_pair = off_diag.abs().mean().item()
    _say(f"  Dict uniqueness: max pair {max_pair:.3f}, mean {mean_pair:.3f}")

    # Eval setup
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

    def eval_all(W_local, sae_beta=4.0):
        bits = {"c1": 0.0, "c3_sae_product": 0.0, "c3_sae_rerank": 0.0}
        for bs in range(0, T_test, BATCH_SIZE):
            be = min(bs + BATCH_SIZE, T_test)
            idx_batch = test_a_idx[bs:be]
            ctxs = build_ctx_bundles_bsc(byte_atoms, pos_atoms, idx_batch)
            P_W = predict_W(W_local, ctxs, byte_atoms, BETA, N)
            tgts = test_a_targets[bs:be]
            P_c1 = predict_pool_classical(ctxs, pool_vecs, pool_labels, pool_used, BETA, N)
            P_1 = ALPHA * P_c1 + (1 - ALPHA) * P_W
            bits["c1"] += float(-torch.log2(P_1.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)).sum())
            for mode in ["product", "rerank"]:
                P_sae = predict_pool_c3_with_sae(idx_batch, ctxs, vsa_bundles, pool_used,
                                                  byte_atoms, pos_atoms, target_pos,
                                                  W_e, b_e, pool_codes,
                                                  BETA, BYTE_BETA, sae_beta, N,
                                                  C3_MATCH_POSITIONS, mode)
                P_x = ALPHA * P_sae + (1 - ALPHA) * P_W
                bits[f"c3_sae_{mode}"] += float(-torch.log2(P_x.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)).sum())
        return {k: v / max(T_test, 1) for k, v in bits.items()}

    _say(f"\nPre-shift eval:")
    pre = eval_all(W)
    _say(f"  C1={pre['c1']:.4f}  C3+SAE(prod)={pre['c3_sae_product']:.4f}  C3+SAE(rerank)={pre['c3_sae_rerank']:.4f}")

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

    _say(f"\n========= SAE M2 VERDICT =========")
    _say(f"  References:")
    _say(f"    C1 post: 4.3352, C3 factored alone: 4.2370 (+0.098)")
    _say(f"    C3+slot-best: see slot attention result")
    _say(f"  SAE variants:")
    _say(f"    C1 post = {post['c1']:.4f}")
    _say(f"    C3+SAE (product) = {post['c3_sae_product']:.4f}  vs C1: {post['c1']-post['c3_sae_product']:+.4f}")
    _say(f"    C3+SAE (rerank)  = {post['c3_sae_rerank']:.4f}   vs C1: {post['c1']-post['c3_sae_rerank']:+.4f}")

    best_method = min(["c3_sae_product", "c3_sae_rerank"], key=lambda m: post[m])
    best_gap = post["c1"] - post[best_method]
    _say(f"  Best: {best_method} with gap {best_gap:+.4f} vs C1")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_m2_sparse_autoencoder"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps(
        {"SAE_DICT_SIZE": SAE_DICT_SIZE, "SAE_TOP_K": SAE_TOP_K, "SAE_TRAIN_EPOCHS": SAE_TRAIN_EPOCHS,
         "final_train_loss": losses[-1], "loss_reduction_pct": (losses[0] - losses[-1]) / losses[0] * 100,
         "dict_uniqueness_max": max_pair, "dict_uniqueness_mean": mean_pair,
         "pre": pre, "post": post,
         "best_method": best_method, "best_gap_vs_c1": best_gap},
        indent=2, default=str))
    _say(f"\nWrote {out_dir / 'metrics.json'}")


if __name__ == "__main__":
    main()
