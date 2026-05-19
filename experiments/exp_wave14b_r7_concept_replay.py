"""Wave 14.B R7 rescue: concept-tagged interleaved replay measured on BWT.

The textbook CLS test for what concepts are SUPPOSED to do:
preserve performance on the old distribution after training on the new.

Algorithm:
1. Phase A: train W_base, build pool_A, extract PPMI concepts (50).
2. Tag each pool entry with which concepts it activates.
3. Phase B baseline: train 15 epochs on train_b, no replay. Measure
   bpc on test_a (BWT) and test_b (forward perf).
4. Phase B with concept-tagged replay:
   - For each batch of train_b, also sample K_REPLAY pool entries from
     the *concept-activating* subset of pool_A (CLS-style interleave).
   - Mix 50/50 in the loss.
5. Compare bpc_a_post and bpc_b_post between baseline and replay.

R7 falsification: TRUE iff BWT-on-A improves by >= 0.20 bpc vs no-replay,
with no more than 0.10 bpc regression on forward perf.

This is the test where the redundancy theorem does NOT apply: concepts
are guiding *which past episodes to rehearse*, not duplicating retrieval.
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
REPLAY_FRACTION = 0.5
RANDOM_REPLAY_BASELINE = True  # also test untagged-random-replay as control


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


def tag_pool_entries_by_concept(pool_byte_at_pos, ppmi_concepts):
    """For each pool entry, which concepts trigger? Returns (P, num_concepts) bool."""
    P = pool_byte_at_pos.shape[0]
    n_concepts = len(ppmi_concepts)
    tags = torch.zeros((P, n_concepts), dtype=torch.bool, device=pool_byte_at_pos.device)
    for c_idx, (i, b_i, j, b_j, _) in enumerate(ppmi_concepts):
        match = (pool_byte_at_pos[:, i] == b_i) & (pool_byte_at_pos[:, j] == b_j)
        tags[:, c_idx] = match
    return tags


def train_phase_a(byte_atoms, pos_atoms, train_bytes):
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
                if epoch == 1:
                    dest = (pool_idx + arange_b[:B]) % POOL_SIZE
                    pool_vecs.index_copy_(0, dest, ctxs)
                    pool_labels.index_copy_(0, dest, tgt_batch)
                    pool_idx = (pool_idx + B) % POOL_SIZE
                    pool_used = min(pool_used + B, POOL_SIZE)
    return W, pool_vecs, pool_labels, pool_used


def train_phase_b(W_start, byte_atoms, pos_atoms, train_bytes_b,
                  replay_pool_ctx=None, replay_pool_targets=None,
                  replay_sampler=None, gen=None):
    """Train Phase B with optional concept-tagged or random replay.

    replay_pool_ctx: (P_active, N) pool entries usable for replay (or None).
    replay_pool_targets: (P_active,) corresponding labels.
    replay_sampler: callable(batch_size, gen) -> indices into the replay pool.
    """
    W = W_start.clone()
    pad = bytes([PAD_BYTE]) * K
    padded = pad + train_bytes_b
    T_total = len(padded) - K
    bt = torch.tensor(list(padded), dtype=torch.long).to(DEVICE)
    offsets = torch.arange(K - 1, -1, -1, device=DEVICE)
    pos = torch.arange(T_total, device=DEVICE)
    train_idx = bt[pos.unsqueeze(1) + offsets.unsqueeze(0)]
    train_targets = bt[pos + K]

    for epoch in range(MAX_EPOCHS):
        for batch_start in range(0, T_total, BATCH_SIZE):
            be = min(batch_start + BATCH_SIZE, T_total)
            idx_batch = train_idx[batch_start:be]
            tgt_batch = train_targets[batch_start:be]
            B = idx_batch.shape[0]
            ctxs_b = build_ctx(byte_atoms, pos_atoms, idx_batch)

            if replay_pool_ctx is not None and replay_sampler is not None:
                n_replay = max(1, int(B * REPLAY_FRACTION))
                replay_idx = replay_sampler(n_replay, gen)
                ctxs_replay = replay_pool_ctx[replay_idx]
                tgt_replay = replay_pool_targets[replay_idx]
                ctxs = torch.cat([ctxs_b, ctxs_replay], dim=0)
                tgts = torch.cat([tgt_batch, tgt_replay], dim=0)
            else:
                ctxs = ctxs_b
                tgts = tgt_batch

            with torch.no_grad():
                q = ctxs @ W.T
                q = shifted_relu(q, RELU_B)
                sims = (byte_atoms @ q.T) / N
                P = torch.softmax(BETA * sims, dim=0)
                target_atoms = byte_atoms[tgts]
                predicted = (P.T @ byte_atoms)
                residual = target_atoms - predicted
                dW = (residual.T @ ctxs) / N
                W.mul_(1.0 - DELTA_RULE_DECAY)
                W.add_(dW, alpha=DELTA_RULE_ALPHA)
    return W


def eval_bpc(W, byte_atoms, pos_atoms, test_bytes, pool_vecs, pool_labels, pool_used):
    pad = bytes([PAD_BYTE]) * K
    padded = pad + test_bytes
    T = len(padded) - K
    bt = torch.tensor(list(padded), dtype=torch.long).to(DEVICE)
    offsets = torch.arange(K - 1, -1, -1, device=DEVICE)
    pos = torch.arange(T, device=DEVICE)
    idx = bt[pos.unsqueeze(1) + offsets.unsqueeze(0)]
    tgts = bt[pos + K]
    total = 0.0
    for bs in range(0, T, BATCH_SIZE):
        be = min(bs + BATCH_SIZE, T)
        idx_b = idx[bs:be]
        ctxs = build_ctx(byte_atoms, pos_atoms, idx_b)
        P_W = predict_W(W, ctxs, byte_atoms, BETA, N)
        if pool_used > 0:
            active = pool_vecs[:pool_used]
            labels = pool_labels[:pool_used]
            sims = (active @ ctxs.T) / N
            weights = torch.softmax(BETA * sims, dim=0)
            P_retr = torch.zeros(VOCAB_SIZE, idx_b.shape[0], device=DEVICE)
            P_retr.scatter_add_(0, labels.unsqueeze(1).expand(-1, idx_b.shape[0]), weights)
        else:
            P_retr = torch.full_like(P_W, 1.0 / VOCAB_SIZE)
        P = ALPHA * P_retr + (1 - ALPHA) * P_W
        p_true = P.gather(0, tgts[bs:be].unsqueeze(0)).squeeze(0).clamp(min=1e-12)
        total += float(-torch.log2(p_true).sum())
    return total / max(T, 1)


def main():
    _say(f"Wave 14.B R7: concept-tagged interleaved replay vs no-replay vs random-replay")
    _say(f"  REPLAY_FRACTION = {REPLAY_FRACTION}, NUM_CONCEPTS = {NUM_CONCEPTS}")

    corpus_a = load_corpus_a()
    corpus_b = shuffle_bytes(corpus_a, seed=SEED + 1)
    split = int(0.8 * len(corpus_a))
    train_a, test_a = corpus_a[:split], corpus_a[split:]
    train_b, test_b = corpus_b[:int(0.8 * len(corpus_b))], corpus_b[int(0.8 * len(corpus_b)):]

    gen = torch.Generator().manual_seed(SEED)
    byte_atoms = make_bsc_atoms(VOCAB_SIZE, N, gen).to(DEVICE)
    pos_atoms = make_bsc_atoms(K, N, gen).to(DEVICE)

    # === Phase A ===
    _say(f"\n[Phase A] Training W_base, building pool_A...")
    W_A, pool_A, labels_A, used_A = train_phase_a(byte_atoms, pos_atoms, train_a)
    bpc_a_initial = eval_bpc(W_A, byte_atoms, pos_atoms, test_a, pool_A, labels_A, used_A)
    _say(f"  Phase A bpc on test_a: {bpc_a_initial:.4f}")

    # === PPMI concept extraction + tagging ===
    _say(f"\n[Concepts] Extracting PPMI patterns + tagging pool entries...")
    pool_byte_at_pos = torch.zeros((used_A, K), dtype=torch.long, device=DEVICE)
    for r in range(K):
        proj = pool_A[:used_A] * pos_atoms[r].unsqueeze(0)
        scores = proj @ byte_atoms.T / N
        pool_byte_at_pos[:, r] = scores.argmax(dim=1)
    ppmi = extract_ppmi_concepts(pool_byte_at_pos, K, NUM_CONCEPTS)
    tags = tag_pool_entries_by_concept(pool_byte_at_pos, ppmi)
    concept_active_per_entry = tags.any(dim=1)
    n_with_any_concept = int(concept_active_per_entry.sum())
    _say(f"  Pool entries activating any concept: {n_with_any_concept}/{used_A} "
         f"({100*n_with_any_concept/used_A:.1f}%)")

    concept_tagged_indices = torch.nonzero(concept_active_per_entry).squeeze(-1)
    all_indices = torch.arange(used_A, device=DEVICE)

    # === Phase B baseline (no replay) ===
    _say(f"\n[Phase B baseline] No replay...")
    gen_b1 = torch.Generator().manual_seed(SEED + 100)
    W_B_baseline = train_phase_b(W_A, byte_atoms, pos_atoms, train_b)

    # === Phase B with concept-tagged replay ===
    _say(f"\n[Phase B + concept replay]...")
    def concept_sampler(n, g):
        i = torch.randint(0, len(concept_tagged_indices), (n,), generator=g, device='cpu').to(DEVICE)
        return concept_tagged_indices[i]
    gen_b2 = torch.Generator().manual_seed(SEED + 101)
    W_B_concept = train_phase_b(
        W_A, byte_atoms, pos_atoms, train_b,
        replay_pool_ctx=pool_A[:used_A], replay_pool_targets=labels_A[:used_A],
        replay_sampler=concept_sampler, gen=gen_b2)

    # === Phase B with random-replay control ===
    if RANDOM_REPLAY_BASELINE:
        _say(f"\n[Phase B + random replay control]...")
        def random_sampler(n, g):
            i = torch.randint(0, used_A, (n,), generator=g, device='cpu').to(DEVICE)
            return all_indices[i]
        gen_b3 = torch.Generator().manual_seed(SEED + 102)
        W_B_random = train_phase_b(
            W_A, byte_atoms, pos_atoms, train_b,
            replay_pool_ctx=pool_A[:used_A], replay_pool_targets=labels_A[:used_A],
            replay_sampler=random_sampler, gen=gen_b3)

    # === Eval all three on test_a (BWT) and test_b (forward) ===
    _say(f"\n[Eval] Computing BWT (test_a) and forward (test_b) for each condition...")
    results = {}
    for name, W in [("baseline_no_replay", W_B_baseline),
                    ("concept_replay", W_B_concept),
                    ("random_replay", W_B_random) if RANDOM_REPLAY_BASELINE else (None, None)]:
        if name is None: continue
        bpc_a = eval_bpc(W, byte_atoms, pos_atoms, test_a, pool_A, labels_A, used_A)
        bpc_b = eval_bpc(W, byte_atoms, pos_atoms, test_b, pool_A, labels_A, used_A)
        results[name] = {"bpc_a_post": bpc_a, "bpc_b_post": bpc_b,
                         "bwt": bpc_a_initial - bpc_a}
        _say(f"  {name:24s}: bpc_a_post={bpc_a:.4f}  bpc_b_post={bpc_b:.4f}  "
             f"BWT={bpc_a_initial-bpc_a:+.4f}")

    _say(f"\n========= R7 VERDICT =========")
    bwt_baseline = results["baseline_no_replay"]["bwt"]
    bwt_concept = results["concept_replay"]["bwt"]
    bwt_random = results.get("random_replay", {}).get("bwt", None)
    fwd_baseline = results["baseline_no_replay"]["bpc_b_post"]
    fwd_concept = results["concept_replay"]["bpc_b_post"]

    bwt_gain_concept = bwt_concept - bwt_baseline  # positive = less forgetting
    fwd_loss_concept = fwd_concept - fwd_baseline  # positive = worse forward

    _say(f"  BWT change (concept vs no-replay): {bwt_gain_concept:+.4f}  (positive=less forgetting)")
    _say(f"  FWD cost  (concept vs no-replay): {fwd_loss_concept:+.4f}  (positive=worse on B)")
    if bwt_random is not None:
        _say(f"  BWT change (random  vs no-replay): {bwt_random - bwt_baseline:+.4f}")
        _say(f"  Concept-vs-random BWT difference:  {bwt_concept - bwt_random:+.4f}  (positive=concepts beat random)")

    if bwt_gain_concept >= 0.20 and fwd_loss_concept <= 0.10:
        _say(f"  R7 PASSES (preregistered): BWT-on-A improved >= 0.20 with no >0.10 forward cost.")
    elif bwt_gain_concept >= 0.05:
        _say(f"  R7 PARTIAL: BWT improved but below the >=0.20 threshold.")
    else:
        _say(f"  R7 FAILS: BWT did not improve meaningfully with concept-tagged replay.")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_r7_concept_replay"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps({
        "bpc_a_initial": bpc_a_initial,
        "REPLAY_FRACTION": REPLAY_FRACTION,
        "NUM_CONCEPTS": NUM_CONCEPTS,
        "pool_pct_with_any_concept": 100 * n_with_any_concept / used_A,
        "results": results,
    }, indent=2))


if __name__ == "__main__":
    main()
