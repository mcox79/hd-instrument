"""A1 rescue: cubic byte_a * byte_b * pos binding for basis modification.

Per research-agent recommendation: top in-basis rescue. The failure of
basis_modification was that PPMI concept atoms were LINEAR combinations
of byte*pos terms already in ctx. A1 fixes this by using CUBIC bindings:
  concept_atom[c] = byte_atom[b_i] * byte_atom[b_j] * pair_pos_atom

The triple product byte*byte*pos lives in a SUBSPACE ORTHOGONAL TO
{byte*pos} in expectation -- formally, <byte_i, byte_i*byte_j> ~ 0
since byte_j is zero-mean.

This is what the original attempt mistakenly thought it was doing.
Smolensky 1990 TPR grade-counting gives the formal argument.

Predicted gain: 0.05-0.15 bpc on byte-LM pre-shift, scaling with PPMI
mass. Falsifier: |delta bpc| < 0.01.
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
POOL_SIZE = 1024
ALPHA = 0.3
MAX_EPOCHS = 15
RELU_B = 0.5
N = 4096
DELTA_RULE_ALPHA = 0.3
DELTA_RULE_DECAY = 1e-4
NUM_CONCEPTS = 50


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


def build_ctx_baseline(byte_atoms, pos_atoms, indices):
    bound = byte_atoms[indices] * pos_atoms.unsqueeze(0)
    summed = bound.sum(dim=1)
    out = torch.sign(summed)
    return torch.where(out == 0, torch.ones_like(out), out)


def build_ctx_cubic(byte_atoms, pos_atoms, pair_pos_atoms, indices, ppmi_pairs):
    """ctx = byte*pos sum + cubic terms (byte_a * byte_b * pair_pos) for active pairs."""
    bound = byte_atoms[indices] * pos_atoms.unsqueeze(0)
    summed = bound.sum(dim=1)
    # Add cubic terms for triggered PPMI pairs
    B = indices.shape[0]
    for c_idx, (i, b_i, j, b_j, _) in enumerate(ppmi_pairs):
        active = (indices[:, i] == b_i) & (indices[:, j] == b_j)
        if active.any():
            # cubic = byte_atom[b_i] * byte_atom[b_j] * pair_pos_atoms[c_idx]
            cubic_term = byte_atoms[b_i] * byte_atoms[b_j] * pair_pos_atoms[c_idx]
            summed[active] += cubic_term.unsqueeze(0)
    out = torch.sign(summed)
    return torch.where(out == 0, torch.ones_like(out), out)


def shifted_relu(q, b):
    return torch.clamp(q - b, min=0.0)


def predict_W(W, ctxs, byte_atoms, beta, n):
    q = ctxs @ W.T
    q = shifted_relu(q, RELU_B)
    sims = (byte_atoms @ q.T) / n
    return torch.softmax(beta * sims, dim=0)


def extract_ppmi(pool_byte_at_pos, K, num_concepts, k_neg=1.0):
    P = pool_byte_at_pos.shape[0]
    pair_counts = Counter()
    marginal_counts = Counter()
    total = 0
    for entry_idx in range(P):
        bytes_at = pool_byte_at_pos[entry_idx].cpu().tolist()
        for i in range(K):
            marginal_counts[(i, bytes_at[i])] += 1
            for j in range(i + 1, K):
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


def decompose_pool(pool_vecs, byte_atoms, pos_atoms, n):
    P = pool_vecs.shape[0]
    out = torch.zeros((P, K), dtype=torch.long, device=DEVICE)
    for r in range(K):
        proj = pool_vecs * pos_atoms[r].unsqueeze(0)
        scores = proj @ byte_atoms.T / n
        out[:, r] = scores.argmax(dim=1)
    return out


def train_phase_a(byte_atoms, pos_atoms, train_bytes,
                  pair_pos_atoms=None, ppmi_pairs=None):
    """If ppmi_pairs is None, baseline build_ctx. Else, cubic-extended ctx."""
    W = torch.zeros((N, N), dtype=torch.float32, device=DEVICE)
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
            if ppmi_pairs is None:
                ctxs = build_ctx_baseline(byte_atoms, pos_atoms, idx_batch)
            else:
                ctxs = build_ctx_cubic(byte_atoms, pos_atoms, pair_pos_atoms,
                                       idx_batch, ppmi_pairs)
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
                if epoch == 1:
                    dest = (pool_idx + arange_b[:B]) % POOL_SIZE
                    pool_vecs.index_copy_(0, dest, ctxs)
                    pool_labels.index_copy_(0, dest, tgt_batch)
                    pool_idx = (pool_idx + B) % POOL_SIZE
                    pool_used = min(pool_used + B, POOL_SIZE)
    return W, pool_vecs, pool_labels, pool_used


def eval_bpc(W, byte_atoms, pos_atoms, test_bytes, pool_vecs, pool_labels,
             pool_used, pair_pos_atoms=None, ppmi_pairs=None):
    pad = bytes([PAD_BYTE]) * K
    padded = pad + test_bytes
    T = len(padded) - K
    bt = torch.tensor(list(padded), dtype=torch.long).to(DEVICE)
    offsets = torch.arange(K - 1, -1, -1, device=DEVICE)
    pos = torch.arange(T, device=DEVICE)
    idx_all = bt[pos.unsqueeze(1) + offsets.unsqueeze(0)]
    tgts_all = bt[pos + K]
    total = 0.0
    for bs in range(0, T, BATCH_SIZE):
        be = min(bs + BATCH_SIZE, T)
        idx_b = idx_all[bs:be]
        tgts = tgts_all[bs:be]
        if ppmi_pairs is None:
            ctxs = build_ctx_baseline(byte_atoms, pos_atoms, idx_b)
        else:
            ctxs = build_ctx_cubic(byte_atoms, pos_atoms, pair_pos_atoms,
                                   idx_b, ppmi_pairs)
        P_W = predict_W(W, ctxs, byte_atoms, BETA, N)
        active = pool_vecs[:pool_used]
        labels = pool_labels[:pool_used]
        sims = (active @ ctxs.T) / N
        weights = torch.softmax(BETA * sims, dim=0)
        P_retr = torch.zeros(VOCAB_SIZE, idx_b.shape[0], device=DEVICE)
        P_retr.scatter_add_(0, labels.unsqueeze(1).expand(-1, idx_b.shape[0]), weights)
        P = ALPHA * P_retr + (1 - ALPHA) * P_W
        p_true = P.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)
        total += float(-torch.log2(p_true).sum())
    return total / max(T, 1)


def main():
    _say(f"A1 rescue: cubic byte_a * byte_b * pair_pos binding for basis mod")
    _say(f"  NUM_CONCEPTS={NUM_CONCEPTS}")

    corpus_a = load_corpus_a()
    corpus_b = shuffle_bytes(corpus_a, seed=SEED + 1)
    split = int(0.8 * len(corpus_a))
    train_a, test_a = corpus_a[:split], corpus_a[split:]
    train_b = corpus_b[:int(0.8 * len(corpus_b))]

    gen = torch.Generator().manual_seed(SEED)
    byte_atoms = make_bsc_atoms(VOCAB_SIZE, N, gen).to(DEVICE)
    pos_atoms = make_bsc_atoms(K, N, gen).to(DEVICE)

    # Baseline Phase A
    _say(f"\n[Baseline] Phase A with standard ctx...")
    W_base, pool_base, labels_base, used_base = train_phase_a(byte_atoms, pos_atoms, train_a)
    bpc_base_a = eval_bpc(W_base, byte_atoms, pos_atoms, test_a, pool_base, labels_base, used_base)
    _say(f"  Baseline pre-shift bpc: {bpc_base_a:.4f}")

    # Extract PPMI patterns
    pool_byte_at_pos = decompose_pool(pool_base[:used_base], byte_atoms, pos_atoms, N)
    ppmi = extract_ppmi(pool_byte_at_pos, K, NUM_CONCEPTS)
    _say(f"  Extracted {len(ppmi)} PPMI patterns")

    # Build pair_pos atoms (one per concept, all independent of byte_atoms)
    pair_pos_gen = torch.Generator().manual_seed(SEED + 9999)
    pair_pos_atoms = make_bsc_atoms(NUM_CONCEPTS, N, pair_pos_gen).to(DEVICE)

    # Sanity check: cubic terms should be ~orthogonal to byte*pos basis
    # E[<byte_i, byte_i*byte_j*pair_pos>] = <byte_i, byte_i> * E[byte_j] * E[pair_pos] = N * 0 * 0 ~ 0
    sample_cubic = byte_atoms[ppmi[0][1]] * byte_atoms[ppmi[0][3]] * pair_pos_atoms[0]
    overlap_with_byte = (sample_cubic @ byte_atoms.T / N).abs()
    overlap_with_pos = (sample_cubic @ pos_atoms.T / N).abs()
    _say(f"  Cubic-vs-byte overlap: mean={overlap_with_byte.mean():.4f} max={overlap_with_byte.max():.4f}")
    _say(f"  Cubic-vs-pos overlap:  mean={overlap_with_pos.mean():.4f} max={overlap_with_pos.max():.4f}")
    _say(f"  (expected ~1/sqrt(N)={1/math.sqrt(N):.4f})")

    # Cubic Phase A
    _say(f"\n[Cubic] Phase A with byte*byte*pair_pos extension...")
    W_cubic, pool_cubic, labels_cubic, used_cubic = train_phase_a(
        byte_atoms, pos_atoms, train_a, pair_pos_atoms=pair_pos_atoms, ppmi_pairs=ppmi)
    bpc_cubic_a = eval_bpc(W_cubic, byte_atoms, pos_atoms, test_a, pool_cubic, labels_cubic, used_cubic,
                           pair_pos_atoms=pair_pos_atoms, ppmi_pairs=ppmi)
    _say(f"  Cubic pre-shift bpc: {bpc_cubic_a:.4f}")
    _say(f"  Pre-shift delta: {bpc_base_a - bpc_cubic_a:+.4f}")

    # Phase B (continual)
    _say(f"\n[Phase B] Continual training on B for both...")
    pad = bytes([PAD_BYTE]) * K
    padded_b = pad + train_b
    T_total = len(padded_b) - K
    bt = torch.tensor(list(padded_b), dtype=torch.long).to(DEVICE)
    offsets = torch.arange(K - 1, -1, -1, device=DEVICE)
    pos = torch.arange(T_total, device=DEVICE)
    train_b_idx = bt[pos.unsqueeze(1) + offsets.unsqueeze(0)]
    train_b_tgts = bt[pos + K]

    for use_cubic, W_, label in [(False, W_base, "baseline"), (True, W_cubic, "cubic")]:
        for epoch in range(MAX_EPOCHS):
            for batch_start in range(0, T_total, BATCH_SIZE):
                be = min(batch_start + BATCH_SIZE, T_total)
                idx_batch = train_b_idx[batch_start:be]
                tgt_batch = train_b_tgts[batch_start:be]
                if use_cubic:
                    ctxs = build_ctx_cubic(byte_atoms, pos_atoms, pair_pos_atoms, idx_batch, ppmi)
                else:
                    ctxs = build_ctx_baseline(byte_atoms, pos_atoms, idx_batch)
                with torch.no_grad():
                    q = ctxs @ W_.T
                    q = shifted_relu(q, RELU_B)
                    sims = (byte_atoms @ q.T) / N
                    P = torch.softmax(BETA * sims, dim=0)
                    target_atoms = byte_atoms[tgt_batch]
                    predicted = (P.T @ byte_atoms)
                    residual = target_atoms - predicted
                    dW = (residual.T @ ctxs) / N
                    W_.mul_(1.0 - DELTA_RULE_DECAY)
                    W_.add_(dW, alpha=DELTA_RULE_ALPHA)

    bpc_base_post = eval_bpc(W_base, byte_atoms, pos_atoms, test_a, pool_base, labels_base, used_base)
    bpc_cubic_post = eval_bpc(W_cubic, byte_atoms, pos_atoms, test_a, pool_cubic, labels_cubic, used_cubic,
                              pair_pos_atoms=pair_pos_atoms, ppmi_pairs=ppmi)

    _say(f"\n========= A1 CUBIC VERDICT =========")
    _say(f"  Pre-shift  baseline={bpc_base_a:.4f}  cubic={bpc_cubic_a:.4f}  delta={bpc_base_a-bpc_cubic_a:+.4f}")
    _say(f"  Post-shift baseline={bpc_base_post:.4f}  cubic={bpc_cubic_post:.4f}  delta={bpc_base_post-bpc_cubic_post:+.4f}")
    _say(f"  BWT baseline={bpc_base_a-bpc_base_post:+.4f}  cubic={bpc_cubic_a-bpc_cubic_post:+.4f}")

    pre_gain = bpc_base_a - bpc_cubic_a
    post_gain = bpc_base_post - bpc_cubic_post
    if pre_gain >= 0.05 or post_gain >= 0.05:
        _say(f"  A1 PASSES: cubic binding shows a real basis-modification gain (>=0.05 bpc).")
    elif abs(pre_gain) > 0.01 or abs(post_gain) > 0.01:
        _say(f"  A1 PARTIAL: |delta| > 0.01 but below 0.05 threshold.")
    else:
        _say(f"  A1 FAILS: cubic binding null (|delta| < 0.01). Even orthogonal-subspace terms add nothing at K=4.")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_a1_cubic_binding"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps({
        "NUM_CONCEPTS": NUM_CONCEPTS,
        "bpc_baseline_pre": bpc_base_a,
        "bpc_cubic_pre": bpc_cubic_a,
        "bpc_baseline_post": bpc_base_post,
        "bpc_cubic_post": bpc_cubic_post,
        "pre_shift_gain": pre_gain,
        "post_shift_gain": post_gain,
        "cubic_byte_overlap_mean": float(overlap_with_byte.mean()),
    }, indent=2))


if __name__ == "__main__":
    main()
