"""Wave 14.B Basis Modification (R2 variant): independent random concept atoms.

The first basis_modification run produced a null result (delta = +/-0.0013).
Diagnosis: the PPMI concept atoms were built as
  concept_atom[c] = byte_atoms[b_i] * pos_atoms[i] + byte_atoms[b_j] * pos_atoms[j]
which is a linear combination of terms ALREADY in ctx. So binding them at a
new concept_pos re-injected correlated noise instead of expanding the basis.

This variant replaces concept atoms with fresh independent bipolar +/-1 vectors
(Frady-Sommer 2021 SLOT-style). The trigger function still uses the PPMI
patterns (so the concepts are still selected by co-occurrence statistics)
but the vectors themselves are linearly independent of byte_atom * pos_atom.

If basis modification has any chance of working, it should work here.

Per R2 falsification: TRUE iff |delta bpc| > 0.02 in either direction
(the previous experiment was ~0.001, well below noise).
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
    files = [
        repo / "PLAN.md", repo / "NEXT_PHASE.md", repo / "README.md",
        repo / "PROGRESS.md", repo / "RESULTS.md", repo / "CLAUDE.md",
    ]
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


def build_ctx_extended(byte_atoms, pos_atoms, indices,
                       concept_atoms, concept_pos, concept_triggers):
    bound = byte_atoms[indices] * pos_atoms.unsqueeze(0)
    summed = bound.sum(dim=1)
    concept_contrib = concept_triggers @ concept_atoms
    concept_contrib = concept_contrib * concept_pos.unsqueeze(0)
    summed = summed + concept_contrib
    out = torch.sign(summed)
    return torch.where(out == 0, torch.ones_like(out), out)


def shifted_relu(q, b):
    return torch.clamp(q - b, min=0.0)


def predict_W(W, ctxs, byte_atoms, beta, n):
    q = ctxs @ W.T
    q = shifted_relu(q, RELU_B)
    sims = (byte_atoms @ q.T) / n
    return torch.softmax(beta * sims, dim=0)


def extract_ppmi_concepts(pool_byte_at_pos, K_pos, num_concepts, k_neg=1.0):
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


def compute_concept_triggers(indices, ppmi_concepts):
    B = indices.shape[0]
    n_concepts = len(ppmi_concepts)
    triggers = torch.zeros((B, n_concepts), device=indices.device)
    for c_idx, (i, b_i, j, b_j, _) in enumerate(ppmi_concepts):
        match = (indices[:, i] == b_i) & (indices[:, j] == b_j)
        triggers[:, c_idx] = match.float()
    return triggers


def train_phase_a(byte_atoms, pos_atoms, train_bytes, build_ctx_fn,
                  concept_atoms=None, concept_pos=None, ppmi_concepts=None):
    W = torch.zeros((N, N), dtype=torch.float32, device=DEVICE)
    pool_vecs = torch.zeros((POOL_SIZE, N), dtype=torch.float32, device=DEVICE)
    pool_labels = torch.zeros(POOL_SIZE, dtype=torch.long, device=DEVICE)
    pool_used = 0
    pool_idx = 0
    arange_b = torch.arange(BATCH_SIZE, device=DEVICE)

    pad = bytes([PAD_BYTE]) * K
    padded_train = pad + train_bytes
    T_total = len(padded_train) - K
    train_b_tensor = torch.tensor(list(padded_train), dtype=torch.long).to(DEVICE)
    offsets = torch.arange(K - 1, -1, -1, device=DEVICE)
    pos_train = torch.arange(T_total, device=DEVICE)
    train_idx = train_b_tensor[pos_train.unsqueeze(1) + offsets.unsqueeze(0)]
    train_targets = train_b_tensor[pos_train + K]

    for epoch in range(1, MAX_EPOCHS + 1):
        for batch_start in range(0, T_total, BATCH_SIZE):
            be = min(batch_start + BATCH_SIZE, T_total)
            idx_batch = train_idx[batch_start:be]
            tgt_batch = train_targets[batch_start:be]
            B = idx_batch.shape[0]
            if ppmi_concepts is not None:
                triggers = compute_concept_triggers(idx_batch, ppmi_concepts)
                ctxs = build_ctx_fn(byte_atoms, pos_atoms, idx_batch,
                                    concept_atoms, concept_pos, triggers)
            else:
                ctxs = build_ctx_fn(byte_atoms, pos_atoms, idx_batch)
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


def eval_on_test(W, byte_atoms, pos_atoms, test_bytes, build_ctx_fn,
                pool_vecs, pool_labels, pool_used,
                concept_atoms=None, concept_pos=None, ppmi_concepts=None):
    pad = bytes([PAD_BYTE]) * K
    padded = pad + test_bytes
    T = len(padded) - K
    bs_tensor = torch.tensor(list(padded), dtype=torch.long).to(DEVICE)
    offsets = torch.arange(K - 1, -1, -1, device=DEVICE)
    pos = torch.arange(T, device=DEVICE)
    idx = bs_tensor[pos.unsqueeze(1) + offsets.unsqueeze(0)]
    tgts = bs_tensor[pos + K]
    total_bits = 0.0
    for bs in range(0, T, BATCH_SIZE):
        be = min(bs + BATCH_SIZE, T)
        idx_batch = idx[bs:be]
        if ppmi_concepts is not None:
            triggers = compute_concept_triggers(idx_batch, ppmi_concepts)
            ctxs = build_ctx_fn(byte_atoms, pos_atoms, idx_batch,
                                concept_atoms, concept_pos, triggers)
        else:
            ctxs = build_ctx_fn(byte_atoms, pos_atoms, idx_batch)
        P_W = predict_W(W, ctxs, byte_atoms, BETA, N)
        if pool_used > 0:
            active = pool_vecs[:pool_used]
            labels = pool_labels[:pool_used]
            sims = (active @ ctxs.T) / N
            weights = torch.softmax(BETA * sims, dim=0)
            P_retr = torch.zeros(VOCAB_SIZE, idx_batch.shape[0], device=DEVICE)
            P_retr.scatter_add_(0, labels.unsqueeze(1).expand(-1, idx_batch.shape[0]), weights)
        else:
            P_retr = torch.full_like(P_W, 1.0 / VOCAB_SIZE)
        P = ALPHA * P_retr + (1 - ALPHA) * P_W
        p_true = P.gather(0, tgts[bs:be].unsqueeze(0)).squeeze(0).clamp(min=1e-12)
        total_bits += float(-torch.log2(p_true).sum())
    return total_bits / max(T, 1)


def main():
    _say(f"Wave 14.B Basis Modification (R2 INDEP): independent random concept atoms")
    _say(f"  NUM_CONCEPTS = {NUM_CONCEPTS} (drawn as fresh +/-1 bipolar vectors)")

    corpus_a = load_corpus_a()
    corpus_b = shuffle_bytes(corpus_a, seed=SEED + 1)
    split = int(0.8 * len(corpus_a))
    train_a, test_a = corpus_a[:split], corpus_a[split:]
    train_b = corpus_b[:int(0.8 * len(corpus_b))]

    gen = torch.Generator().manual_seed(SEED)
    byte_atoms = make_bsc_atoms(VOCAB_SIZE, N, gen).to(DEVICE)
    pos_atoms = make_bsc_atoms(K, N, gen).to(DEVICE)

    # === Baseline Phase A (standard codebook) ===
    _say(f"\n[Baseline] Phase A with standard codebook (no concepts)...")
    W_base, pool_base, labels_base, used_base = train_phase_a(
        byte_atoms, pos_atoms, train_a, build_ctx_baseline)
    bpc_base_a = eval_on_test(W_base, byte_atoms, pos_atoms, test_a,
                              build_ctx_baseline, pool_base, labels_base, used_base)
    _say(f"  Baseline pre-shift bpc on test_A: {bpc_base_a:.4f}")

    # === Extract PPMI concepts from baseline pool (for triggers only) ===
    _say(f"\nExtracting PPMI concepts from baseline pool (used as TRIGGERS only)...")
    pool_byte_at_pos = torch.zeros((used_base, K), dtype=torch.long, device=DEVICE)
    for r in range(K):
        proj = pool_base[:used_base] * pos_atoms[r].unsqueeze(0)
        scores = proj @ byte_atoms.T / N
        pool_byte_at_pos[:, r] = scores.argmax(dim=1)
    ppmi = extract_ppmi_concepts(pool_byte_at_pos, K, NUM_CONCEPTS)
    _say(f"  Extracted {len(ppmi)} PPMI patterns to drive triggers")

    # KEY DIFFERENCE: concept atoms are fresh independent bipolar vectors,
    # NOT linear combinations of byte_atom * pos_atom terms.
    concept_atom_gen = torch.Generator().manual_seed(SEED + 7777)
    concept_atoms = make_bsc_atoms(NUM_CONCEPTS, N, concept_atom_gen).to(DEVICE)

    # Sanity check: independence from byte_atom * pos_atom basis
    # (mean abs cosine of concept_atoms with all byte_atoms should be ~1/sqrt(N))
    concept_byte_overlap = (concept_atoms @ byte_atoms.T / N).abs()
    _say(f"  Concept-byte cosine: mean={concept_byte_overlap.mean():.4f} "
         f"max={concept_byte_overlap.max():.4f} (expect ~1/sqrt(N)={1/math.sqrt(N):.4f})")

    concept_pos_gen = torch.Generator().manual_seed(SEED + 8888)
    concept_pos_bits = torch.randint(0, 2, (N,), generator=concept_pos_gen)
    concept_pos = (concept_pos_bits * 2 - 1).to(torch.float32).to(DEVICE)

    # === Extended Phase A (with INDEPENDENT concept atoms added) ===
    _say(f"\n[Extended-indep] Phase A with INDEPENDENT-random concept atoms...")
    W_ext, pool_ext, labels_ext, used_ext = train_phase_a(
        byte_atoms, pos_atoms, train_a, build_ctx_extended,
        concept_atoms=concept_atoms, concept_pos=concept_pos, ppmi_concepts=ppmi)
    bpc_ext_a = eval_on_test(W_ext, byte_atoms, pos_atoms, test_a,
                             build_ctx_extended, pool_ext, labels_ext, used_ext,
                             concept_atoms=concept_atoms, concept_pos=concept_pos,
                             ppmi_concepts=ppmi)
    _say(f"  Extended-indep pre-shift bpc on test_A: {bpc_ext_a:.4f}")
    _say(f"  Improvement: {bpc_base_a - bpc_ext_a:+.4f} bpc")

    # === Continual training on corpus B for both ===
    _say(f"\nContinual training on corpus B (both baselines)...")
    pad = bytes([PAD_BYTE]) * K
    padded_train_b = pad + train_b
    T_total = len(padded_train_b) - K
    train_b_tensor = torch.tensor(list(padded_train_b), dtype=torch.long).to(DEVICE)
    offsets = torch.arange(K - 1, -1, -1, device=DEVICE)
    pos_train = torch.arange(T_total, device=DEVICE)
    train_b_idx = train_b_tensor[pos_train.unsqueeze(1) + offsets.unsqueeze(0)]
    train_b_tgts = train_b_tensor[pos_train + K]

    for run_name, W_, build_fn, ppmi_arg, ca_arg, cp_arg in [
        ("baseline", W_base, build_ctx_baseline, None, None, None),
        ("extended-indep", W_ext, build_ctx_extended, ppmi, concept_atoms, concept_pos),
    ]:
        for epoch in range(MAX_EPOCHS):
            for batch_start in range(0, T_total, BATCH_SIZE):
                be = min(batch_start + BATCH_SIZE, T_total)
                idx_batch = train_b_idx[batch_start:be]
                tgt_batch = train_b_tgts[batch_start:be]
                if ppmi_arg is not None:
                    triggers = compute_concept_triggers(idx_batch, ppmi_arg)
                    ctxs = build_fn(byte_atoms, pos_atoms, idx_batch, ca_arg, cp_arg, triggers)
                else:
                    ctxs = build_fn(byte_atoms, pos_atoms, idx_batch)
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

    bpc_base_post = eval_on_test(W_base, byte_atoms, pos_atoms, test_a,
                                 build_ctx_baseline, pool_base, labels_base, used_base)
    bpc_ext_post = eval_on_test(W_ext, byte_atoms, pos_atoms, test_a,
                                build_ctx_extended, pool_ext, labels_ext, used_ext,
                                concept_atoms=concept_atoms, concept_pos=concept_pos,
                                ppmi_concepts=ppmi)

    _say(f"\n========= INDEP BASIS MODIFICATION VERDICT =========")
    _say(f"  Pre-shift  bpc:  baseline={bpc_base_a:.4f}  extended-indep={bpc_ext_a:.4f}  delta={bpc_base_a-bpc_ext_a:+.4f}")
    _say(f"  Post-shift bpc:  baseline={bpc_base_post:.4f}  extended-indep={bpc_ext_post:.4f}  delta={bpc_base_post-bpc_ext_post:+.4f}")
    _say(f"  BWT (pre - post): baseline={bpc_base_a-bpc_base_post:+.4f}  extended-indep={bpc_ext_a-bpc_ext_post:+.4f}")
    _say(f"")
    delta_pre = bpc_base_a - bpc_ext_a
    delta_post = bpc_base_post - bpc_ext_post
    if abs(delta_pre) > 0.02 or abs(delta_post) > 0.02:
        if delta_pre > 0.02 or delta_post > 0.02:
            _say(f"  R2 RESCUE PASSES: independent concept atoms move bpc meaningfully")
        else:
            _say(f"  R2 RESCUE FAILS (informative): adding independent concepts HURTS")
    else:
        _say(f"  R2 RESCUE NULL: |delta| < 0.02 -- still within noise, even with independent atoms")
        _say(f"  This rules out 'redundant atoms' as the cause. Basis modification at K=4 byte-LM truly does nothing.")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_basis_modification_indep"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps({
        "NUM_CONCEPTS": NUM_CONCEPTS,
        "variant": "independent_random_concept_atoms",
        "bpc_baseline_pre": bpc_base_a,
        "bpc_extended_pre": bpc_ext_a,
        "bpc_baseline_post": bpc_base_post,
        "bpc_extended_post": bpc_ext_post,
        "pre_shift_gain": bpc_base_a - bpc_ext_a,
        "post_shift_gain": bpc_base_post - bpc_ext_post,
        "concept_byte_overlap_mean": float(concept_byte_overlap.mean()),
        "concept_byte_overlap_max": float(concept_byte_overlap.max()),
    }, indent=2))


if __name__ == "__main__":
    main()
