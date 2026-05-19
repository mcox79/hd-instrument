"""Wave 14.B R10 rescue: M2 retest at K=16 where bundle interference is real.

At K=4 the M2 grid found product fusion matches C3-factored exactly
(theorem upheld). The theorem assumes the concept and retrieval signals
share information. But at K=4, ctx is 4 terms in N=4096 -- way below
capacity, so retrieval has near-perfect SNR and concepts can't add
anything.

At K=16, ctx is 16 terms in N=4096. Bundle interference grows as O(K/N)
and the per-position decompose accuracy starts to degrade. THIS is the
regime where:
  - Retrieval signal becomes noisier (fewer SNR margin)
  - Concept patterns might carry information that survived bundling
  - The product/linear/additive fusion modes might genuinely beat A_only

R10 falsification: TRUE iff at K=16, any concept-fusion mode beats
C3-factored A_only by >= 0.03 bpc on post-shift bpc.
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
K = 16  # KEY DIFFERENCE: 4x larger context
BETA = 8.0
BYTE_BETA = 16.0
BATCH_SIZE = 64
POOL_SIZE = 1024
ALPHA = 0.3
MAX_EPOCHS = 15
RELU_B = 0.5
N = 4096
DELTA_RULE_ALPHA = 0.3
DELTA_RULE_DECAY = 1e-4
NUM_CONCEPTS = 100
LAMBDA_LINEAR = 0.7
C3_MATCH_POSITIONS = list(range(K - 1))  # all but the last position


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


def predict_W(W, ctxs, byte_atoms, beta, n):
    q = ctxs @ W.T
    q = shifted_relu(q, RELU_B)
    sims = (byte_atoms @ q.T) / n
    return torch.softmax(beta * sims, dim=0)


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


def decompose_pool(pool_vecs, byte_atoms, pos_atoms, k_pos, n):
    P = pool_vecs.shape[0]
    out = torch.zeros((P, k_pos), dtype=torch.long, device=DEVICE)
    for r in range(k_pos):
        proj = pool_vecs * pos_atoms[r].unsqueeze(0)
        scores = proj @ byte_atoms.T / n
        out[:, r] = scores.argmax(dim=1)
    return out


def extract_ppmi(pool_byte_at_pos, K_pos, num_concepts, k_neg=1.0):
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


def train_phase(W_start, byte_atoms, pos_atoms, train_bytes, build_pool):
    W = W_start.clone() if W_start is not None else torch.zeros((N, N), dtype=torch.float32, device=DEVICE)
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
                if build_pool and epoch == 1:
                    dest = (pool_idx + arange_b[:B]) % POOL_SIZE
                    pool_vecs.index_copy_(0, dest, ctxs)
                    pool_labels.index_copy_(0, dest, tgt_batch)
                    pool_idx = (pool_idx + B) % POOL_SIZE
                    pool_used = min(pool_used + B, POOL_SIZE)
    return W, pool_vecs, pool_labels, pool_used


def eval_all_modes(W, byte_atoms, pos_atoms, test_bytes, pool_vecs, pool_labels,
                   pool_used, ppmi_concepts):
    """Eval bpc under {C1, A_only, product, linear, additive} fusion modes."""
    pad = bytes([PAD_BYTE]) * K
    padded = pad + test_bytes
    T = len(padded) - K
    bt = torch.tensor(list(padded), dtype=torch.long).to(DEVICE)
    offsets = torch.arange(K - 1, -1, -1, device=DEVICE)
    pos = torch.arange(T, device=DEVICE)
    idx_all = bt[pos.unsqueeze(1) + offsets.unsqueeze(0)]
    tgts_all = bt[pos + K]
    totals = {"c1": 0.0, "a_only": 0.0, "product": 0.0, "linear": 0.0, "additive": 0.0}

    active = pool_vecs[:pool_used]
    labels = pool_labels[:pool_used]

    for bs in range(0, T, BATCH_SIZE):
        be = min(bs + BATCH_SIZE, T)
        idx_b = idx_all[bs:be]
        tgts = tgts_all[bs:be]
        B = idx_b.shape[0]
        ctxs = build_ctx(byte_atoms, pos_atoms, idx_b)
        P_W = predict_W(W, ctxs, byte_atoms, BETA, N)

        sims_c1 = (active @ ctxs.T) / N
        weights_c1 = torch.softmax(BETA * sims_c1, dim=0)
        P_c1 = torch.zeros(VOCAB_SIZE, B, device=DEVICE)
        P_c1.scatter_add_(0, labels.unsqueeze(1).expand(-1, B), weights_c1)
        P_c1_final = ALPHA * P_c1 + (1 - ALPHA) * P_W

        scores_factored = factored_scores(idx_b, active, byte_atoms, pos_atoms,
                                          C3_MATCH_POSITIONS, N)
        w_a = torch.softmax(BETA * scores_factored, dim=0)
        P_a = torch.zeros(VOCAB_SIZE, B, device=DEVICE)
        P_a.scatter_add_(0, labels.unsqueeze(1).expand(-1, B), w_a)
        P_a_final = ALPHA * P_a + (1 - ALPHA) * P_W

        # Concept score (PPMI on this query)
        concept_score = torch.zeros((pool_used, B), device=DEVICE)
        for c_idx, (i, b_i, j, b_j, _ppmi) in enumerate(ppmi_concepts):
            query_match = (idx_b[:, i] == b_i) & (idx_b[:, j] == b_j)
            pool_match = (decompose_pool(active, byte_atoms, pos_atoms, K, N)[:, i] == b_i) & \
                         (decompose_pool(active, byte_atoms, pos_atoms, K, N)[:, j] == b_j)
            mask = pool_match.unsqueeze(1) & query_match.unsqueeze(0)
            concept_score += mask.float()
        # normalize concept score across pool
        s_b = concept_score

        # product: softmax(A) * softmax(B)
        w_prod = torch.softmax(BETA * scores_factored, dim=0) * torch.softmax(BETA * s_b, dim=0)
        w_prod = w_prod / (w_prod.sum(dim=0, keepdim=True) + 1e-12)
        P_prod = torch.zeros(VOCAB_SIZE, B, device=DEVICE)
        P_prod.scatter_add_(0, labels.unsqueeze(1).expand(-1, B), w_prod)
        P_prod_final = ALPHA * P_prod + (1 - ALPHA) * P_W

        # linear combine on logits
        lc_logits = LAMBDA_LINEAR * scores_factored + (1 - LAMBDA_LINEAR) * s_b
        w_lin = torch.softmax(BETA * lc_logits, dim=0)
        P_lin = torch.zeros(VOCAB_SIZE, B, device=DEVICE)
        P_lin.scatter_add_(0, labels.unsqueeze(1).expand(-1, B), w_lin)
        P_lin_final = ALPHA * P_lin + (1 - ALPHA) * P_W

        # additive logits, normalized
        add_logits = scores_factored + s_b
        w_add = torch.softmax(BETA * add_logits, dim=0)
        P_add = torch.zeros(VOCAB_SIZE, B, device=DEVICE)
        P_add.scatter_add_(0, labels.unsqueeze(1).expand(-1, B), w_add)
        P_add_final = ALPHA * P_add + (1 - ALPHA) * P_W

        for key, P_final in [("c1", P_c1_final), ("a_only", P_a_final),
                             ("product", P_prod_final), ("linear", P_lin_final),
                             ("additive", P_add_final)]:
            p_true = P_final.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)
            totals[key] += float(-torch.log2(p_true).sum())

    return {k: v / max(T, 1) for k, v in totals.items()}


def main():
    _say(f"Wave 14.B R10: M2 retest at K={K} (bundle-interference regime)")

    corpus_a = load_corpus_a()
    corpus_b = shuffle_bytes(corpus_a, seed=SEED + 1)
    split = int(0.8 * len(corpus_a))
    train_a, test_a = corpus_a[:split], corpus_a[split:]
    train_b = corpus_b[:int(0.8 * len(corpus_b))]

    gen = torch.Generator().manual_seed(SEED)
    byte_atoms = make_bsc_atoms(VOCAB_SIZE, N, gen).to(DEVICE)
    pos_atoms = make_bsc_atoms(K, N, gen).to(DEVICE)

    _say(f"\n[Phase A] Training W and pool at K={K}...")
    W_A, pool_A, labels_A, used_A = train_phase(None, byte_atoms, pos_atoms, train_a, build_pool=True)

    _say(f"\n[PPMI] Extracting concepts from pool...")
    pool_byte_at_pos = decompose_pool(pool_A[:used_A], byte_atoms, pos_atoms, K, N)
    ppmi = extract_ppmi(pool_byte_at_pos, K, NUM_CONCEPTS)
    _say(f"  {len(ppmi)} concepts extracted")

    _say(f"\n[Eval pre-shift] All fusion modes at K={K}...")
    pre_results = eval_all_modes(W_A, byte_atoms, pos_atoms, test_a,
                                 pool_A, labels_A, used_A, ppmi)
    for k, v in pre_results.items():
        _say(f"  pre {k:10s} = {v:.4f}")

    _say(f"\n[Phase B] Continual training on corpus B...")
    W_AB, _, _, _ = train_phase(W_A, byte_atoms, pos_atoms, train_b, build_pool=False)

    _say(f"\n[Eval post-shift] All fusion modes...")
    post_results = eval_all_modes(W_AB, byte_atoms, pos_atoms, test_a,
                                  pool_A, labels_A, used_A, ppmi)
    for k, v in post_results.items():
        _say(f"  post {k:10s} = {v:.4f}")

    _say(f"\n========= R10 VERDICT (K={K}) =========")
    a_only_post = post_results["a_only"]
    best_fusion = min((v, k) for k, v in post_results.items() if k not in ("c1", "a_only"))
    _say(f"  Post-shift A_only: {a_only_post:.4f}")
    _say(f"  Best fusion mode:  {best_fusion[1]} = {best_fusion[0]:.4f}  "
         f"(delta vs A_only: {a_only_post - best_fusion[0]:+.4f})")
    if a_only_post - best_fusion[0] >= 0.03:
        _say(f"  R10 PASSES: at K={K} concept fusion BEATS A_only by >=0.03 bpc.")
        _say(f"  Theorem's bundle-info-redundancy holds only at low K. The regime where")
        _say(f"  bundle interference is real makes concepts non-redundant.")
    else:
        _say(f"  R10 FAILS: even at K={K}, concept fusion does not beat A_only by >=0.03 bpc.")
        _say(f"  Theorem may be more robust than the K-scaling story suggests.")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_r10_K16_m2"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps({
        "K": K, "N": N, "NUM_CONCEPTS": NUM_CONCEPTS,
        "pre": pre_results, "post": post_results,
    }, indent=2))


if __name__ == "__main__":
    main()
