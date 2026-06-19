"""ICL via pool v2 — research-recommended design changes applied.

Per wave14d_icl_via_pool_research.md, v1 was structurally right but underpowered:
1. Corpus B too close to A (markdown vs Python both ASCII English). v2 uses JSON
   from data/session_events.jsonl + queue logs -- much different byte distribution.
2. N range too narrow. v2: {0, 4, 16, 64, 256, 1024, 2048}.
3. ALPHA=0.3 caps achievable delta. v2: sweep ALPHA in {0.3, 0.5, 0.7, 1.0}.
4. POOL_SIZE=1024 too small when N>1024 (FIFO evicts the test entries).
   v2: POOL_SIZE=4096.
5. 5 seeds + threshold 0.015 with t-test (was 3 seeds, 0.05).

Reports pool-weight entropy at eval to detect retrieval collapse.

ICL confirmed if relevant - irrelevant >= 0.015 bpc with t >= 2 across 5 seeds.
"""

from __future__ import annotations

import json
import math
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
POOL_SIZE = 4096
MAX_EPOCHS = 15
RELU_B = 0.5
DELTA_RULE_ALPHA = 0.3
DELTA_RULE_DECAY = 1e-4

SEEDS = [17, 23, 31, 37, 41]
N_EXAMPLES = [0, 4, 16, 64, 256, 1024, 2048]
ALPHA_VALUES = [0.3, 0.5, 0.7, 1.0]
ICL_THRESHOLD = 0.015


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


def load_corpus_b_json():
    """Corpus B = JSON event stream + metrics JSONs. Much different distribution from markdown."""
    repo = Path(__file__).resolve().parent.parent
    parts = []
    # session_events.jsonl is the largest JSON-y file in the repo
    sess_log = repo / "data" / "session_events.jsonl"
    if sess_log.exists():
        parts.append(sess_log.read_bytes())
    # All queue.json files
    for qfile in [repo / "data" / "overnight_queue" / "queue.json",
                   repo / "data" / "remote_cpu_queue" / "queue.json"]:
        if qfile.exists():
            parts.append(qfile.read_bytes())
    # All experiment metrics.json files
    for d in (repo / "data").glob("exp_*"):
        m = d / "metrics.json"
        if m.exists():
            parts.append(m.read_bytes())
            parts.append(b"\n")
    # Pad with multiple copies if too short
    combined = b"\n".join(parts)
    while len(combined) < 30000:
        combined = combined + b"\n" + combined
    return combined


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
    pad = bytes([PAD_BYTE]) * K
    padded = pad + corpus_bytes
    T_total = len(padded) - K
    if T_total <= 0:
        return (torch.zeros((0, K), dtype=torch.long, device=DEVICE),
                torch.zeros(0, dtype=torch.long, device=DEVICE))
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
                   pool_used, alpha, return_entropy=False):
    pad = bytes([PAD_BYTE]) * K
    padded = pad + test_bytes
    T = len(padded) - K
    bt = torch.tensor(list(padded), dtype=torch.long).to(DEVICE)
    offsets = torch.arange(K - 1, -1, -1, device=DEVICE)
    pos = torch.arange(T, device=DEVICE)
    idx_all = bt[pos.unsqueeze(1) + offsets.unsqueeze(0)]
    tgts_all = bt[pos + K]
    total = 0.0
    pool_entropy_sum = 0.0
    entropy_count = 0
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
        if pool_used > 0 and alpha > 0:
            sims_p = (active @ ctxs.T) / N
            weights_p = torch.softmax(BETA * sims_p, dim=0)
            if return_entropy:
                # Compute pool-weight entropy per query
                entropy_per_query = -(weights_p * torch.log(weights_p.clamp(min=1e-12))).sum(dim=0)
                pool_entropy_sum += float(entropy_per_query.sum())
                entropy_count += B
            P_retr = torch.zeros(VOCAB_SIZE, B, device=DEVICE)
            P_retr.scatter_add_(0, labels.unsqueeze(1).expand(-1, B), weights_p)
            P = alpha * P_retr + (1 - alpha) * P_W
        else:
            P = P_W
        p_true = P.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)
        total += float(-torch.log2(p_true).sum())
    avg_bpc = total / max(T, 1)
    if return_entropy and entropy_count > 0:
        return avg_bpc, pool_entropy_sum / entropy_count
    return avg_bpc, None


def augment_pool(pool_vecs, pool_labels, pool_used, new_idx, new_tgts,
                 byte_atoms, pos_atoms):
    n_new = new_idx.shape[0]
    if n_new == 0:
        return pool_vecs, pool_labels, pool_used
    new_ctxs = build_ctx(byte_atoms, pos_atoms, new_idx)
    new_used = min(pool_used + n_new, POOL_SIZE)
    aug_vecs = pool_vecs.clone()
    aug_labels = pool_labels.clone()
    if pool_used + n_new <= POOL_SIZE:
        aug_vecs[pool_used:pool_used + n_new] = new_ctxs
        aug_labels[pool_used:pool_used + n_new] = new_tgts
    else:
        room = POOL_SIZE - pool_used
        aug_vecs[pool_used:] = new_ctxs[:room]
        aug_labels[pool_used:] = new_tgts[:room]
        remaining = n_new - room
        if remaining > 0:
            aug_vecs[:remaining] = new_ctxs[room:]
            aug_labels[:remaining] = new_tgts[room:]
    return aug_vecs, aug_labels, new_used


def run_one(seed):
    corpus_a = load_corpus_a()
    corpus_b = load_corpus_b_json()
    split_a = int(0.8 * len(corpus_a))
    train_a = corpus_a[:split_a]
    split_b = int(0.7 * len(corpus_b))
    train_b = corpus_b[:split_b]
    test_b = corpus_b[split_b:]

    gen = torch.Generator().manual_seed(seed)
    byte_atoms = make_bsc_atoms(VOCAB_SIZE, N, gen).to(DEVICE)
    pos_atoms = make_bsc_atoms(K, N, gen).to(DEVICE)

    W_A, pool_A, labels_A, used_A = train_phase_a(byte_atoms, pos_atoms, train_a)

    results = {}
    # Baselines per alpha
    for alpha in ALPHA_VALUES:
        off_bpc, _ = eval_with_pool(W_A, byte_atoms, pos_atoms, test_b,
                                     pool_A, labels_A, used_A, 0.0)
        pool_A_bpc, pool_A_entropy = eval_with_pool(W_A, byte_atoms, pos_atoms, test_b,
                                                     pool_A, labels_A, used_A, alpha,
                                                     return_entropy=True)
        results[f"alpha{alpha}_off"] = off_bpc
        results[f"alpha{alpha}_pool_A"] = pool_A_bpc
        results[f"alpha{alpha}_pool_A_entropy"] = pool_A_entropy

    # ICL modes: irrelevant + relevant at each N for each alpha
    for n_examples in N_EXAMPLES:
        if n_examples == 0:
            continue
        irr_idx, irr_tgts = chunk_bytes_to_K_positions(train_a, n_examples, seed=seed * 100 + 1)
        rel_idx, rel_tgts = chunk_bytes_to_K_positions(train_b, n_examples, seed=seed * 100 + 2)
        aug_vecs_irr, aug_labels_irr, aug_used_irr = augment_pool(
            pool_A, labels_A, used_A, irr_idx, irr_tgts, byte_atoms, pos_atoms)
        aug_vecs_rel, aug_labels_rel, aug_used_rel = augment_pool(
            pool_A, labels_A, used_A, rel_idx, rel_tgts, byte_atoms, pos_atoms)
        for alpha in ALPHA_VALUES:
            irr_bpc, _ = eval_with_pool(W_A, byte_atoms, pos_atoms, test_b,
                                         aug_vecs_irr, aug_labels_irr, aug_used_irr, alpha)
            rel_bpc, rel_ent = eval_with_pool(W_A, byte_atoms, pos_atoms, test_b,
                                                aug_vecs_rel, aug_labels_rel, aug_used_rel,
                                                alpha, return_entropy=True)
            results[f"alpha{alpha}_irr_N{n_examples}"] = irr_bpc
            results[f"alpha{alpha}_rel_N{n_examples}"] = rel_bpc
            results[f"alpha{alpha}_rel_N{n_examples}_entropy"] = rel_ent

    return results


def t_statistic(values_a, values_b):
    """Welch's t for two-sample with unequal variance (5 seeds each)."""
    n_a, n_b = len(values_a), len(values_b)
    mean_a = sum(values_a) / n_a
    mean_b = sum(values_b) / n_b
    var_a = sum((v - mean_a) ** 2 for v in values_a) / (n_a - 1)
    var_b = sum((v - mean_b) ** 2 for v in values_b) / (n_b - 1)
    se = math.sqrt(var_a / n_a + var_b / n_b)
    if se < 1e-9:
        return 0.0
    return (mean_b - mean_a) / se  # t > 0 means b > a (i.e., irr > rel = ICL works)


def main():
    _say(f"ICL via pool v2: K={K}, POOL_SIZE={POOL_SIZE}, {len(SEEDS)} seeds, threshold {ICL_THRESHOLD}")
    _say(f"  Corpus A: project markdown ({len(load_corpus_a())} bytes)")
    _say(f"  Corpus B: JSON event stream + metrics ({len(load_corpus_b_json())} bytes)")
    _say(f"  N range: {N_EXAMPLES}")
    _say(f"  ALPHA range: {ALPHA_VALUES}")

    all_results = []
    for seed in SEEDS:
        _say(f"\n[seed={seed}]")
        r = run_one(seed)
        for alpha in [0.3, 1.0]:
            _say(f"  ALPHA={alpha}: off={r[f'alpha{alpha}_off']:.4f}  pool_A={r[f'alpha{alpha}_pool_A']:.4f}  pool_entropy={r[f'alpha{alpha}_pool_A_entropy']:.2f}")
            for n in N_EXAMPLES:
                if n == 0:
                    continue
                irr = r[f"alpha{alpha}_irr_N{n}"]
                rel = r[f"alpha{alpha}_rel_N{n}"]
                _say(f"    N={n:5d} irrelevant={irr:.4f}  relevant={rel:.4f}  delta={irr-rel:+.4f}")
        all_results.append({"seed": seed, **r})

    _say("\n========= ICL VERDICT (across seeds, t-test) =========")
    for alpha in ALPHA_VALUES:
        for n in N_EXAMPLES:
            if n == 0:
                continue
            irr_vals = [r[f"alpha{alpha}_irr_N{n}"] for r in all_results]
            rel_vals = [r[f"alpha{alpha}_rel_N{n}"] for r in all_results]
            mean_delta = sum(irr_vals) / len(irr_vals) - sum(rel_vals) / len(rel_vals)
            t = t_statistic(rel_vals, irr_vals)
            verdict = "ICL" if mean_delta >= ICL_THRESHOLD and t >= 2.0 else "no"
            _say(f"  alpha={alpha} N={n:5d}: delta={mean_delta:+.4f}  t={t:+.2f}  ({verdict})")

    # Find best (alpha, N) combination
    best = (-1.0, None, None)
    for alpha in ALPHA_VALUES:
        for n in N_EXAMPLES:
            if n == 0:
                continue
            irr_vals = [r[f"alpha{alpha}_irr_N{n}"] for r in all_results]
            rel_vals = [r[f"alpha{alpha}_rel_N{n}"] for r in all_results]
            mean_delta = sum(irr_vals) / len(irr_vals) - sum(rel_vals) / len(rel_vals)
            t = t_statistic(rel_vals, irr_vals)
            if mean_delta > best[0]:
                best = (mean_delta, alpha, n, t)
    _say(f"\n  Best: alpha={best[1]} N={best[2]} delta={best[0]:+.4f} t={best[3]:+.2f}")
    if best[0] >= ICL_THRESHOLD and best[3] >= 2.0:
        _say(f"  ICL CONFIRMED via pool retrieval.")
    elif best[0] >= ICL_THRESHOLD:
        _say(f"  ICL effect detected but insignificant variance.")
    else:
        _say(f"  NO ICL detected at any (alpha, N) combination.")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14d_icl_via_pool_v2"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps({
        "K": K, "POOL_SIZE": POOL_SIZE, "SEEDS": SEEDS,
        "N_EXAMPLES": N_EXAMPLES, "ALPHA_VALUES": ALPHA_VALUES,
        "ICL_THRESHOLD": ICL_THRESHOLD,
        "results": all_results,
    }, indent=2))


if __name__ == "__main__":
    main()
