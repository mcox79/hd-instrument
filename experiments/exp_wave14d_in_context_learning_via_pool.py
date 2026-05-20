"""In-context learning via pool: does adding test-domain examples to the pool
at query time improve predictions on a novel domain?

Hypothesis: pool retrieval functions as an implicit context window. Adding N
examples from a novel domain to the pool at query time should improve bpc on
that domain IF the substrate has ICL-like adaptation.

Confound control: also test adding N random IRRELEVANT examples from corpus A.
If bpc improves more with corpus-B examples than corpus-A examples, ICL is real.

Design (3 seeds, K=4):
- Phase A: train W + build pool from project markdown (corpus A)
- Eval on Python source code (corpus B) -- genuinely different byte distribution
- Modes (each evaluated on corpus B test chunks):
  - off:        W only (baseline)
  - pool_A:     W + corpus-A pool retrieval (standard)
  - pool_A_plus_N_irrelevant: W + pool augmented with N random corpus-A entries (control)
  - pool_A_plus_N_relevant:   W + pool augmented with N corpus-B examples (the ICL test)
- N in {0, 4, 16, 64}

ICL confirmed if: pool_A_plus_64_relevant bpc < pool_A_plus_64_irrelevant bpc
by >= 0.05 bpc consistently across seeds.
"""

from __future__ import annotations

import json
from pathlib import Path

import torch


torch.set_float32_matmul_precision("high")

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
VOCAB_SIZE = 256
PAD_BYTE = 0
K = 4
N = 4096
BETA = 8.0
BATCH_SIZE = 64
POOL_SIZE = 1024
ALPHA = 0.3
MAX_EPOCHS = 15
RELU_B = 0.5
DELTA_RULE_ALPHA = 0.3
DELTA_RULE_DECAY = 1e-4

SEEDS = [17, 23, 31]
N_EXAMPLES = [0, 4, 16, 64]


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


def load_corpus_b_python_code():
    """Corpus B = Python source from experiments/. Different distribution from markdown."""
    repo = Path(__file__).resolve().parent.parent
    exp_dir = repo / "experiments"
    parts = []
    # Pick stable, large Python files to ensure reasonable corpus_b size
    candidates = [
        exp_dir / "exp_wave14b_r10_best_config_multiseed.py",
        exp_dir / "exp_wave14b_r3_disjoint_concepts.py",
        exp_dir / "exp_wave14b_r3_unigram_diagnostic.py",
        exp_dir / "exp_wave14b_replay_preshift_K4.py",
        exp_dir / "exp_wave14b_r10_K128_K256_multiseed.py",
        exp_dir / "run_overnight_queue.py",
    ]
    for f in candidates:
        if f.exists():
            parts.append(f.read_bytes())
            parts.append(b"\n\n")
    return b"".join(parts)


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


def chunk_bytes_to_K_positions(corpus_bytes, max_entries, seed=0):
    """Convert byte sequence into (idx, tgt) tensors. Used to build ICL example sets."""
    pad = bytes([PAD_BYTE]) * K
    padded = pad + corpus_bytes
    T_total = len(padded) - K
    if T_total <= 0:
        return torch.zeros((0, K), dtype=torch.long, device=DEVICE), torch.zeros(0, dtype=torch.long, device=DEVICE)
    bt = torch.tensor(list(padded), dtype=torch.long).to(DEVICE)
    offsets = torch.arange(K - 1, -1, -1, device=DEVICE)
    pos = torch.arange(T_total, device=DEVICE)
    idx = bt[pos.unsqueeze(1) + offsets.unsqueeze(0)]
    tgts = bt[pos + K]
    n_take = min(max_entries, T_total)
    if n_take < T_total:
        cpu_gen = torch.Generator().manual_seed(seed)
        perm = torch.randperm(T_total, generator=cpu_gen)[:n_take].to(DEVICE)
        idx = idx[perm]
        tgts = tgts[perm]
    return idx, tgts


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


def eval_with_pool(W, byte_atoms, pos_atoms, test_bytes, pool_vecs, pool_labels,
                   pool_used, use_pool):
    pad = bytes([PAD_BYTE]) * K
    padded = pad + test_bytes
    T = len(padded) - K
    bt = torch.tensor(list(padded), dtype=torch.long).to(DEVICE)
    offsets = torch.arange(K - 1, -1, -1, device=DEVICE)
    pos = torch.arange(T, device=DEVICE)
    idx_all = bt[pos.unsqueeze(1) + offsets.unsqueeze(0)]
    tgts_all = bt[pos + K]
    total = 0.0
    active = pool_vecs[:pool_used] if pool_used > 0 else None
    labels = pool_labels[:pool_used] if pool_used > 0 else None
    for bs in range(0, T, BATCH_SIZE):
        be = min(bs + BATCH_SIZE, T)
        idx_b = idx_all[bs:be]
        tgts = tgts_all[bs:be]
        B = idx_b.shape[0]
        ctxs = build_ctx(byte_atoms, pos_atoms, idx_b)
        q = ctxs @ W.T
        q = shifted_relu(q, RELU_B)
        sims = (byte_atoms @ q.T) / N
        P_W = torch.softmax(BETA * sims, dim=0)
        if use_pool and pool_used > 0:
            sims_p = (active @ ctxs.T) / N
            weights_p = torch.softmax(BETA * sims_p, dim=0)
            P_retr = torch.zeros(VOCAB_SIZE, B, device=DEVICE)
            P_retr.scatter_add_(0, labels.unsqueeze(1).expand(-1, B), weights_p)
            P = ALPHA * P_retr + (1 - ALPHA) * P_W
        else:
            P = P_W
        p_true = P.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)
        total += float(-torch.log2(p_true).sum())
    return total / max(T, 1)


def augment_pool(pool_vecs, pool_labels, pool_used, new_idx_batch, new_tgts,
                 byte_atoms, pos_atoms):
    """Add N new K-grams + targets to the pool. Returns updated pool."""
    n_new = new_idx_batch.shape[0]
    if n_new == 0:
        return pool_vecs, pool_labels, pool_used
    new_ctxs = build_ctx(byte_atoms, pos_atoms, new_idx_batch)
    # Append (no cycling -- we want the new examples to be present)
    new_used = min(pool_used + n_new, POOL_SIZE)
    augmented_vecs = pool_vecs.clone()
    augmented_labels = pool_labels.clone()
    if pool_used + n_new <= POOL_SIZE:
        augmented_vecs[pool_used:pool_used + n_new] = new_ctxs
        augmented_labels[pool_used:pool_used + n_new] = new_tgts
    else:
        # Overwrite oldest entries (FIFO) to keep new examples in
        room = POOL_SIZE - pool_used
        augmented_vecs[pool_used:] = new_ctxs[:room]
        augmented_labels[pool_used:] = new_tgts[:room]
        remaining = n_new - room
        if remaining > 0:
            augmented_vecs[:remaining] = new_ctxs[room:]
            augmented_labels[:remaining] = new_tgts[room:]
    return augmented_vecs, augmented_labels, new_used


def run_one(seed):
    corpus_a = load_corpus_a()
    corpus_b = load_corpus_b_python_code()
    _say(f"  corpus_a={len(corpus_a)} bytes, corpus_b={len(corpus_b)} bytes")
    split_a = int(0.8 * len(corpus_a))
    train_a = corpus_a[:split_a]
    # Split corpus_b: training half (source for ICL examples) + test half
    split_b = int(0.7 * len(corpus_b))
    train_b = corpus_b[:split_b]
    test_b = corpus_b[split_b:]

    gen = torch.Generator().manual_seed(seed)
    byte_atoms = make_bsc_atoms(VOCAB_SIZE, N, gen).to(DEVICE)
    pos_atoms = make_bsc_atoms(K, N, gen).to(DEVICE)

    W_A, pool_A, labels_A, used_A = train_phase_a(byte_atoms, pos_atoms, train_a)

    # Baseline modes
    off_bpc = eval_with_pool(W_A, byte_atoms, pos_atoms, test_b, pool_A, labels_A,
                              used_A, use_pool=False)
    pool_A_bpc = eval_with_pool(W_A, byte_atoms, pos_atoms, test_b, pool_A, labels_A,
                                 used_A, use_pool=True)

    # ICL modes: augment pool with N examples either from corpus_a or corpus_b
    results = {"off": off_bpc, "pool_A": pool_A_bpc}
    for n_examples in N_EXAMPLES:
        if n_examples == 0:
            results[f"irrelevant_N{n_examples}"] = pool_A_bpc
            results[f"relevant_N{n_examples}"] = pool_A_bpc
            continue
        # Irrelevant: random corpus_a K-grams (not from W's training set, sampled freshly)
        irr_idx, irr_tgts = chunk_bytes_to_K_positions(train_a, n_examples, seed=seed * 100)
        aug_vecs, aug_labels, aug_used = augment_pool(pool_A, labels_A, used_A,
                                                       irr_idx, irr_tgts, byte_atoms, pos_atoms)
        results[f"irrelevant_N{n_examples}"] = eval_with_pool(W_A, byte_atoms, pos_atoms,
                                                                test_b, aug_vecs, aug_labels,
                                                                aug_used, use_pool=True)
        # Relevant: K-grams from train_b (the novel domain)
        rel_idx, rel_tgts = chunk_bytes_to_K_positions(train_b, n_examples, seed=seed * 100)
        aug_vecs, aug_labels, aug_used = augment_pool(pool_A, labels_A, used_A,
                                                       rel_idx, rel_tgts, byte_atoms, pos_atoms)
        results[f"relevant_N{n_examples}"] = eval_with_pool(W_A, byte_atoms, pos_atoms,
                                                              test_b, aug_vecs, aug_labels,
                                                              aug_used, use_pool=True)

    return results


def main():
    _say(f"ICL via pool: K={K}, N_examples={N_EXAMPLES}, 3 seeds")
    _say(f"  Corpus A: project markdown (W trained on this)")
    _say(f"  Corpus B: Python source from experiments/ (novel distribution)")
    _say(f"  Test: bpc on corpus_B test split with pool augmentation")

    all_results = []
    for seed in SEEDS:
        _say(f"\n[seed={seed}]")
        r = run_one(seed)
        _say(f"  off            = {r['off']:.4f}")
        _say(f"  pool_A         = {r['pool_A']:.4f}  delta_vs_off={r['off']-r['pool_A']:+.4f}")
        for n in N_EXAMPLES:
            if n == 0:
                continue
            irr = r[f"irrelevant_N{n}"]
            rel = r[f"relevant_N{n}"]
            _say(f"  N={n:3d} irrelevant={irr:.4f}  relevant={rel:.4f}  ICL_delta={irr-rel:+.4f}")
        all_results.append({"seed": seed, **r})

    _say("\n========= ICL VERDICT =========")
    for n in N_EXAMPLES:
        if n == 0:
            continue
        irr_mean = sum(r[f"irrelevant_N{n}"] for r in all_results) / len(all_results)
        rel_mean = sum(r[f"relevant_N{n}"] for r in all_results) / len(all_results)
        icl_delta = irr_mean - rel_mean
        _say(f"  N={n:3d} mean: irrelevant={irr_mean:.4f}  relevant={rel_mean:.4f}  ICL_gain={icl_delta:+.4f}")

    final_delta = ((sum(r["irrelevant_N64"] for r in all_results) - sum(r["relevant_N64"] for r in all_results))
                    / len(all_results))
    if final_delta >= 0.05:
        _say(f"\n  ICL CONFIRMED: relevant-pool gains {final_delta:+.4f} bpc over irrelevant at N=64.")
    elif final_delta >= 0.01:
        _say(f"\n  WEAK SIGNAL: small ICL effect, {final_delta:+.4f} bpc")
    elif final_delta >= -0.01:
        _say(f"\n  NO ICL: pool augmentation is distribution-agnostic ({final_delta:+.4f} bpc).")
    else:
        _say(f"\n  REVERSE: irrelevant examples HELP more than relevant ({final_delta:+.4f}). Suggests pool relevance isn't what we thought.")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14d_in_context_learning_via_pool"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps({
        "K": K, "N_EXAMPLES": N_EXAMPLES, "SEEDS": SEEDS,
        "results": all_results,
    }, indent=2))


if __name__ == "__main__":
    main()
