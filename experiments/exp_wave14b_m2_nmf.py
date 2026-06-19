"""Wave 14.B M2 NMF: non-negative matrix factorization on atom-activation matrix.

Per the unbiased research synthesis (priority #1 in the ranked list):
"NMF on the atom-activation matrix" — HDC-native (concepts are non-
negative atom combinations), provably identifiable under Donoho-Stodden
separability (Arora-Ge-Kannan-Moitra 2012).

Algorithm:
1. For each pool entry, decompose into atom activations (per-position
   cleanup against byte_atoms).
2. Stack into X ∈ R^(M × T) where M = atoms × positions, T = pool size.
3. Run NMF: X ≈ W H with W ≥ 0, H ≥ 0.
4. Each column of W is a "concept" = non-negative mixture of original
   atom-position bindings.
5. Concept atoms in HDC = bundle of original bindings weighted by W.
6. Each pool entry has H column = its concept activation vector.

For retrieval: query concept activations vs pool concept activations.

The HDC-native property: concepts compose ADDITIVELY in the original
codebook, exactly the substrate's binding/bundling semantics.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import torch
import numpy as np


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
NMF_RANK = 32  # number of concepts
NMF_BETA = 4.0
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


def decompose_pool_to_activations(pool_vecs, byte_atoms, pos_atoms, n):
    """For each pool entry, compute atom activations at each position.
    Returns matrix X ∈ R^((VOCAB * K) × P), non-negative."""
    P = pool_vecs.shape[0]
    M = VOCAB_SIZE * K  # total atom-position bindings
    X = torch.zeros((M, P), device=pool_vecs.device)
    for r in range(K):
        projected = pool_vecs * pos_atoms[r].unsqueeze(0)  # (P, N)
        byte_scores = projected @ byte_atoms.T / n  # (P, 256)
        byte_scores = torch.clamp(byte_scores, min=0)  # non-negative for NMF
        for b in range(VOCAB_SIZE):
            X[r * VOCAB_SIZE + b] = byte_scores[:, b]
    return X


def run_nmf(X_np, rank, n_iter=200, tol=1e-4):
    """Lee-Seung multiplicative updates NMF in pure numpy. No sklearn dep."""
    M, P = X_np.shape
    rng = np.random.default_rng(SEED)
    # Random non-negative initialization
    W = rng.random((M, rank)).astype(np.float32) + 0.1
    H = rng.random((rank, P)).astype(np.float32) + 0.1
    prev_err = float('inf')
    for it in range(n_iter):
        # Update H: H = H * (W.T @ X) / (W.T @ W @ H + eps)
        numerator_H = W.T @ X_np
        denominator_H = (W.T @ W) @ H + 1e-9
        H = H * numerator_H / denominator_H
        # Update W: W = W * (X @ H.T) / (W @ H @ H.T + eps)
        numerator_W = X_np @ H.T
        denominator_W = W @ (H @ H.T) + 1e-9
        W = W * numerator_W / denominator_W
        # Convergence check every 10 iter
        if it % 10 == 0:
            err = np.linalg.norm(X_np - W @ H) / (np.linalg.norm(X_np) + 1e-9)
            if abs(prev_err - err) < tol:
                break
            prev_err = err
    final_err = np.linalg.norm(X_np - W @ H)
    return W, H, final_err


def build_concept_atoms_from_nmf(W_nmf, byte_atoms, pos_atoms, n):
    """Convert NMF column W[:, c] to HDC concept atom = bundle of weighted (byte, pos) bindings."""
    rank = W_nmf.shape[1]
    concepts = torch.zeros((rank, n), device=byte_atoms.device)
    for c in range(rank):
        # W[r*VOCAB+b, c] is the weight of "byte b at position r" in concept c
        for r in range(K):
            for b in range(VOCAB_SIZE):
                w = W_nmf[r * VOCAB_SIZE + b, c].item()
                if w > 0:
                    concepts[c] += w * (byte_atoms[b] * pos_atoms[r])
    return concepts


def predict_pool_c3_nmf(query_byte_indices, ctxs, vsa_bundles, vsa_used,
                        byte_atoms, pos_atoms, target_pos,
                        concept_atoms, pool_nmf_loadings,
                        beta_retrieval, beta_byte, beta_concept, n,
                        match_positions, aggregation):
    B = query_byte_indices.shape[0]
    P = vsa_bundles.shape[0]
    factored_scores = torch.zeros((P, B), device=byte_atoms.device)
    for r in match_positions:
        pool_proj_r = vsa_bundles * pos_atoms[r].unsqueeze(0)
        query_atoms_r = byte_atoms[query_byte_indices[:, r]]
        factored_scores += (pool_proj_r @ query_atoms_r.T) / n

    # Query concept loadings via cosine to concept atoms
    query_loadings = ctxs @ concept_atoms.T / n  # (B, rank)
    nmf_scores = pool_nmf_loadings @ query_loadings.T  # (P, B)

    if aggregation == "product":
        wf = torch.softmax(beta_retrieval * factored_scores, dim=0)
        wn = torch.softmax(beta_concept * nmf_scores, dim=0)
        combined = wf * wn
        combined = combined / combined.sum(dim=0, keepdim=True).clamp(min=1e-12)
    elif aggregation == "rerank":
        TOP_K_RR = 16
        topk_idx = torch.topk(factored_scores, k=min(TOP_K_RR, P), dim=0).indices
        combined = torch.zeros((P, B), device=byte_atoms.device)
        for b in range(B):
            local_idx = topk_idx[:, b]
            local_nmf = nmf_scores[local_idx, b]
            local_weights = torch.softmax(beta_concept * local_nmf, dim=0)
            combined[local_idx, b] = local_weights
    else:
        combined = torch.softmax(beta_retrieval * (factored_scores + nmf_scores), dim=0)

    target_estimates = vsa_bundles * target_pos.unsqueeze(0)
    byte_scores = (target_estimates @ byte_atoms.T) / n
    P_byte_per_entry = torch.softmax(beta_byte * byte_scores, dim=1)
    return P_byte_per_entry.T @ combined


def main():
    _say(f"Wave 14.B M2 NMF: provable concept extraction (HDC-native)")
    _say(f"  NMF rank = {NMF_RANK}")

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

    _say(f"\nDecomposing {pool_used} pool entries to atom activation matrix...")
    X = decompose_pool_to_activations(pool_vecs[:pool_used], byte_atoms, pos_atoms, N)
    _say(f"  Activation matrix shape: {X.shape}, max={X.max():.3f}, mean={X.mean():.3f}")

    _say(f"\nRunning NMF with rank {NMF_RANK}...")
    X_np = X.cpu().numpy()
    W_nmf, H_nmf, recon_err = run_nmf(X_np, NMF_RANK)
    _say(f"  NMF reconstruction error: {recon_err:.3f}")
    _say(f"  W shape: {W_nmf.shape}, H shape: {H_nmf.shape}")

    # Build HDC concept atoms from NMF components
    _say(f"\nBuilding HDC concept atoms from NMF factors...")
    W_nmf_t = torch.from_numpy(W_nmf).to(DEVICE)
    concept_atoms = build_concept_atoms_from_nmf(W_nmf_t, byte_atoms, pos_atoms, N)
    _say(f"  Concept atoms shape: {concept_atoms.shape}")

    # Pool entries' NMF loadings = H.T (each pool entry gets a vector of concept weights)
    pool_nmf_loadings = torch.from_numpy(H_nmf.T).to(DEVICE)  # (P, rank)
    _say(f"  Pool NMF loadings: {pool_nmf_loadings.shape}")

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
        bits = {"c1": 0.0, "c3_nmf_product": 0.0, "c3_nmf_rerank": 0.0}
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
                P_nmf = predict_pool_c3_nmf(idx_batch, ctxs, vsa_bundles, pool_used,
                                            byte_atoms, pos_atoms, target_pos,
                                            concept_atoms, pool_nmf_loadings,
                                            BETA, BYTE_BETA, NMF_BETA, N,
                                            C3_MATCH_POSITIONS, mode)
                P_x = ALPHA * P_nmf + (1 - ALPHA) * P_W
                bits[f"c3_nmf_{mode}"] += float(-torch.log2(P_x.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)).sum())
        return {k: v / max(T_test, 1) for k, v in bits.items()}

    _say(f"\nPre-shift eval:")
    pre = eval_all(W)
    _say(f"  C1={pre['c1']:.4f}  C3+NMF(prod)={pre['c3_nmf_product']:.4f}  C3+NMF(rerank)={pre['c3_nmf_rerank']:.4f}")

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

    _say(f"\n========= NMF M2 VERDICT =========")
    _say(f"  References: C1 post=4.3352, C3 factored=4.2370 (+0.098)")
    _say(f"  C1 post = {post['c1']:.4f}")
    _say(f"    C3+NMF (product) = {post['c3_nmf_product']:.4f}  vs C1: {post['c1']-post['c3_nmf_product']:+.4f}")
    _say(f"    C3+NMF (rerank)  = {post['c3_nmf_rerank']:.4f}   vs C1: {post['c1']-post['c3_nmf_rerank']:+.4f}")

    best_method = min(["c3_nmf_product", "c3_nmf_rerank"], key=lambda m: post[m])
    best_gap = post["c1"] - post[best_method]
    _say(f"  Best: {best_method} gap {best_gap:+.4f} vs C1")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_m2_nmf"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps(
        {"NMF_RANK": NMF_RANK, "recon_err": float(recon_err),
         "pre": pre, "post": post,
         "best_method": best_method, "best_gap_vs_c1": best_gap},
        indent=2, default=str))
    _say(f"\nWrote {out_dir / 'metrics.json'}")


if __name__ == "__main__":
    main()
