"""Wave 14.B M2 CP tensor: third-order tensor decomposition of co-occurrence.

Per the unbiased research synthesis (priority #3):
"CP tensor decomposition of (atom, position, atom)" — only method with
Kruskal uniqueness guarantee that uses the positional structure intrinsic
to HDC bundles.

Algorithm:
1. Build third-order co-occurrence tensor T[a, p, b] = count of (atom a
   at position p, atom b at SOME other position) in pool entries.
2. CP decomposition: T ≈ sum_r u_r ⊗ v_r ⊗ w_r (sum of rank-1 tensors)
3. Each factor (u_r, v_r, w_r) is a concept template: u_r is the atom
   distribution, v_r is the position distribution, w_r is the partner-atom
   distribution.
4. Convert to HDC concept atom = weighted sum of (atom × position) bindings.

Kruskal's uniqueness: if k_U + k_V + k_W >= 2R + 2, decomposition is
unique up to scaling/permutation. For random atoms in our setting,
Kruskal rank is full → uniqueness guaranteed.

Per Anandkumar-Ge-Hsu-Kakade-Telgarsky 2014, method-of-moments gives
provable polynomial-time recovery.
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
CP_RANK = 32
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


def build_cooccurrence_tensor(pool_byte_at_pos, num_atoms, num_positions):
    """Build T[a, p, b] = count of (atom a at position p, atom b at any other position)."""
    T = torch.zeros((num_atoms, num_positions, num_atoms), dtype=torch.float32, device=DEVICE)
    P_entries = pool_byte_at_pos.shape[0]
    for entry_idx in range(P_entries):
        bytes_at = pool_byte_at_pos[entry_idx]
        for i in range(num_positions):
            a = bytes_at[i].item()
            for j in range(num_positions):
                if i == j:
                    continue
                b = bytes_at[j].item()
                T[a, i, b] += 1.0
    return T


def cp_decomposition(T_np, rank, n_iter=100, tol=1e-4):
    """Simple ALS CP decomposition. T ≈ sum_r u_r ⊗ v_r ⊗ w_r."""
    I, J, K_dim = T_np.shape
    rng = np.random.default_rng(SEED)
    U = rng.normal(0, 1, (I, rank)).astype(np.float32)
    V = rng.normal(0, 1, (J, rank)).astype(np.float32)
    W = rng.normal(0, 1, (K_dim, rank)).astype(np.float32)

    T_mode0 = T_np.reshape(I, J * K_dim)
    T_mode1 = T_np.transpose(1, 0, 2).reshape(J, I * K_dim)
    T_mode2 = T_np.transpose(2, 0, 1).reshape(K_dim, I * J)

    prev_loss = float('inf')
    for it in range(n_iter):
        # Khatri-Rao products
        WV = np.einsum('ir,jr->ijr', W, V).reshape(K_dim * J, rank)
        U = T_mode0 @ WV @ np.linalg.pinv(WV.T @ WV + 1e-6 * np.eye(rank))
        WU = np.einsum('ir,jr->ijr', W, U).reshape(K_dim * I, rank)
        V = T_mode1 @ WU @ np.linalg.pinv(WU.T @ WU + 1e-6 * np.eye(rank))
        VU = np.einsum('ir,jr->ijr', V, U).reshape(J * I, rank)
        W = T_mode2 @ VU @ np.linalg.pinv(VU.T @ VU + 1e-6 * np.eye(rank))
        # Reconstruct
        T_rec = np.einsum('ir,jr,kr->ijk', U, V, W)
        loss = np.linalg.norm(T_np - T_rec) / np.linalg.norm(T_np)
        if abs(prev_loss - loss) < tol:
            break
        prev_loss = loss
    return U, V, W, loss


def build_concept_atoms_from_cp(U, V, byte_atoms, pos_atoms, n):
    """Each CP factor r → concept atom = sum over atoms&positions weighted by U_r, V_r."""
    rank = U.shape[1]
    concepts = torch.zeros((rank, n), device=byte_atoms.device)
    U_t = torch.from_numpy(U).to(DEVICE)
    V_t = torch.from_numpy(V).to(DEVICE)
    # Normalize U_r and V_r so weights are sensible
    U_t = U_t / U_t.abs().sum(dim=0, keepdim=True).clamp(min=1e-6)
    V_t = V_t / V_t.abs().sum(dim=0, keepdim=True).clamp(min=1e-6)
    for r in range(rank):
        for a in range(VOCAB_SIZE):
            for p in range(K):
                w = U_t[a, r].item() * V_t[p, r].item()
                concepts[r] += w * (byte_atoms[a] * pos_atoms[p])
    return concepts


def predict_pool_c3_cp(query_byte_indices, ctxs, vsa_bundles, vsa_used,
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

    query_concept_scores = ctxs @ concept_atoms.T / n
    concept_sim = pool_concept_scores @ query_concept_scores.T

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
    _say(f"Wave 14.B M2 CP tensor: Kruskal-uniqueness third-order decomposition")
    _say(f"  CP rank = {CP_RANK}")

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

    _say(f"\nDecomposing pool to per-position bytes...")
    pool_byte_at_pos = torch.zeros((pool_used, K), dtype=torch.long, device=DEVICE)
    for r in range(K):
        proj = pool_vecs[:pool_used] * pos_atoms[r].unsqueeze(0)
        byte_scores = proj @ byte_atoms.T / N
        pool_byte_at_pos[:, r] = byte_scores.argmax(dim=1)

    _say(f"\nBuilding (atom, position, atom) co-occurrence tensor...")
    T = build_cooccurrence_tensor(pool_byte_at_pos, VOCAB_SIZE, K)
    _say(f"  Tensor shape: {T.shape}, nnz: {(T > 0).sum().item()}, max: {T.max().item()}")

    _say(f"\nRunning ALS CP decomposition (rank {CP_RANK})...")
    T_np = T.cpu().numpy()
    U, V, W_cp, recon_err = cp_decomposition(T_np, CP_RANK, n_iter=80, tol=1e-4)
    _say(f"  Reconstruction error: {recon_err:.4f}")
    _say(f"  U: {U.shape}, V: {V.shape}, W: {W_cp.shape}")

    _say(f"\nBuilding HDC concept atoms from CP factors...")
    concept_atoms = build_concept_atoms_from_cp(U, V, byte_atoms, pos_atoms, N)
    pool_concept_scores = pool_vecs[:pool_used] @ concept_atoms.T / N

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
        bits = {"c1": 0.0, "c3_cp_product": 0.0, "c3_cp_rerank": 0.0}
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
                P_cp = predict_pool_c3_cp(idx_batch, ctxs, vsa_bundles, pool_used,
                                          byte_atoms, pos_atoms, target_pos,
                                          concept_atoms, pool_concept_scores,
                                          BETA, BYTE_BETA, CONCEPT_BETA, N,
                                          C3_MATCH_POSITIONS, mode)
                P_x = ALPHA * P_cp + (1 - ALPHA) * P_W
                bits[f"c3_cp_{mode}"] += float(-torch.log2(P_x.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)).sum())
        return {k: v / max(T_test, 1) for k, v in bits.items()}

    _say(f"\nPre-shift eval:")
    pre = eval_all(W)
    _say(f"  C1={pre['c1']:.4f}  C3+CP(prod)={pre['c3_cp_product']:.4f}  C3+CP(rerank)={pre['c3_cp_rerank']:.4f}")

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

    _say(f"\n========= CP TENSOR M2 VERDICT =========")
    _say(f"  References: C1=4.3352, C3 factored=4.2370")
    _say(f"  C1 post = {post['c1']:.4f}")
    for mode in ["product", "rerank"]:
        gap = post['c1'] - post[f'c3_cp_{mode}']
        _say(f"    C3+CP ({mode}) = {post[f'c3_cp_{mode}']:.4f}  vs C1: {gap:+.4f}")

    best_method = min(["c3_cp_product", "c3_cp_rerank"], key=lambda m: post[m])
    best_gap = post["c1"] - post[best_method]

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_m2_cp_tensor"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps(
        {"CP_RANK": CP_RANK, "recon_err": float(recon_err),
         "pre": pre, "post": post,
         "best_method": best_method, "best_gap_vs_c1": best_gap},
        indent=2, default=str))
    _say(f"\nWrote {out_dir / 'metrics.json'}")


if __name__ == "__main__":
    main()
