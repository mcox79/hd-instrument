"""ICL × RSB synergy: does ICL gain depend on tree-cluster membership of added examples?

Per wave14f_icl_rsb_synergy_research:
- Tree-close augmentation wins on populated-branch queries at small N (schema refine)
- Tree-distant wins on OOD/complex tasks or large N (gap fill)
- Sibling-branch dominated

Lean 3-cell test (instead of 2x3x3 factorial):
- Build single-linkage tree on pool_A entries
- For each test query, find nearest cluster (mid-level cut of the tree)
- Add N=64 corpus-B examples in 3 conditions:
  * close: examples that land in same cluster as queries
  * sibling: examples in sibling cluster
  * distant: examples in farthest cluster
- Measure ICL gain (vs no-augmentation baseline) at K=4 only (where ICL is strongest)

3 seeds. ~30-45 min GPU.
"""

from __future__ import annotations

import json
from pathlib import Path

import torch

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
N_AUGMENT = 64
NUM_CLUSTERS = 8  # cut tree at this level


def _say(m): print(m, flush=True)


def load_corpus_a():
    repo = Path(__file__).resolve().parent.parent
    files = [repo / "PLAN.md", repo / "NEXT_PHASE.md", repo / "README.md",
             repo / "PROGRESS.md", repo / "RESULTS.md", repo / "CLAUDE.md"]
    parts = []
    for f in files:
        if f.exists():
            parts.append(f.read_bytes()); parts.append(b"\n\n")
    return b"".join(parts)


def load_corpus_b():
    repo = Path(__file__).resolve().parent.parent
    exp_dir = repo / "experiments"
    parts = []
    for f in [exp_dir / "exp_wave14b_r10_best_config_multiseed.py",
              exp_dir / "exp_wave14d_in_context_learning_via_pool.py",
              exp_dir / "run_overnight_queue.py"]:
        if f.exists():
            parts.append(f.read_bytes()); parts.append(b"\n\n")
    return b"".join(parts)


def make_bsc(k, n, gen):
    return 2.0 * (torch.rand((k, n), generator=gen) > 0.5).float() - 1.0


def build_ctx(byte_atoms, pos_atoms, idx):
    b = byte_atoms[idx] * pos_atoms.unsqueeze(0)
    out = torch.sign(b.sum(dim=1))
    return torch.where(out == 0, torch.ones_like(out), out)


def relu_shift(q, b): return torch.clamp(q - b, min=0.0)


def train_phase_a(byte_atoms, pos_atoms, train_bytes):
    W = torch.zeros((N, N), device=DEVICE)
    pool_v = torch.zeros((POOL_SIZE, N), device=DEVICE)
    pool_l = torch.zeros(POOL_SIZE, dtype=torch.long, device=DEVICE)
    p_idx, p_used = 0, 0
    arange = torch.arange(BATCH_SIZE, device=DEVICE)
    pad = bytes([PAD_BYTE]) * K
    padded = pad + train_bytes
    T = len(padded) - K
    bt = torch.tensor(list(padded), dtype=torch.long).to(DEVICE)
    offs = torch.arange(K - 1, -1, -1, device=DEVICE)
    pos = torch.arange(T, device=DEVICE)
    idx = bt[pos.unsqueeze(1) + offs.unsqueeze(0)]
    tgt = bt[pos + K]
    for epoch in range(1, MAX_EPOCHS + 1):
        for bs in range(0, T, BATCH_SIZE):
            be = min(bs + BATCH_SIZE, T)
            B = be - bs
            ctxs = build_ctx(byte_atoms, pos_atoms, idx[bs:be])
            t = tgt[bs:be]
            with torch.no_grad():
                q = relu_shift(ctxs @ W.T, RELU_B)
                sims = (byte_atoms @ q.T) / N
                P = torch.softmax(BETA * sims, dim=0)
                resid = byte_atoms[t] - (P.T @ byte_atoms)
                dW = (resid.T @ ctxs) / N
                W.mul_(1.0 - DELTA_RULE_DECAY); W.add_(dW, alpha=DELTA_RULE_ALPHA)
                if epoch == 1:
                    dest = (p_idx + arange[:B]) % POOL_SIZE
                    pool_v.index_copy_(0, dest, ctxs)
                    pool_l.index_copy_(0, dest, t)
                    p_idx = (p_idx + B) % POOL_SIZE
                    p_used = min(p_used + B, POOL_SIZE)
    return W, pool_v, pool_l, p_used


def cluster_pool_kmeans(pool, num_clusters, gen):
    """Simple k-means in bipolar space. Returns cluster assignment per pool entry."""
    P = pool.shape[0]
    init = torch.randperm(P, generator=gen)[:num_clusters]
    centroids = pool[init].clone()
    for it in range(15):
        sims = pool @ centroids.T / N
        assignments = sims.argmax(dim=1)
        new_centroids = torch.zeros_like(centroids)
        for c in range(num_clusters):
            mask = assignments == c
            if mask.any():
                mean = pool[mask].mean(dim=0)
                cnew = torch.sign(mean)
                new_centroids[c] = torch.where(cnew == 0, torch.ones_like(cnew), cnew)
            else:
                new_centroids[c] = centroids[c]
        if (new_centroids == centroids).all():
            break
        centroids = new_centroids
    sims = pool @ centroids.T / N
    return centroids, sims.argmax(dim=1)


def find_query_clusters(queries, centroids):
    sims = queries @ centroids.T / N
    return sims.argmax(dim=1)


def chunk_corpus_to_ctxs(byte_atoms, pos_atoms, corpus_bytes, count, gen):
    pad = bytes([PAD_BYTE]) * K
    padded = pad + corpus_bytes
    T = len(padded) - K
    if T <= 0:
        return torch.zeros((0, N), device=DEVICE), torch.zeros(0, dtype=torch.long, device=DEVICE)
    bt = torch.tensor(list(padded), dtype=torch.long).to(DEVICE)
    offs = torch.arange(K - 1, -1, -1, device=DEVICE)
    pos = torch.arange(T, device=DEVICE)
    idx = bt[pos.unsqueeze(1) + offs.unsqueeze(0)]
    tgts = bt[pos + K]
    perm = torch.randperm(T, generator=gen)[:min(count, T)].to(DEVICE)
    selected_idx = idx[perm]
    selected_tgts = tgts[perm]
    ctxs = build_ctx(byte_atoms, pos_atoms, selected_idx)
    return ctxs, selected_tgts


def eval_with_pool(W, byte_atoms, pos_atoms, test_bytes, pool_v, pool_l, p_used):
    pad = bytes([PAD_BYTE]) * K
    padded = pad + test_bytes
    T = len(padded) - K
    bt = torch.tensor(list(padded), dtype=torch.long).to(DEVICE)
    offs = torch.arange(K - 1, -1, -1, device=DEVICE)
    pos = torch.arange(T, device=DEVICE)
    idx = bt[pos.unsqueeze(1) + offs.unsqueeze(0)]
    tgts = bt[pos + K]
    total = 0.0
    active = pool_v[:p_used]
    labels = pool_l[:p_used]
    for bs in range(0, T, BATCH_SIZE):
        be = min(bs + BATCH_SIZE, T)
        idx_b = idx[bs:be]
        t = tgts[bs:be]
        B = idx_b.shape[0]
        ctxs = build_ctx(byte_atoms, pos_atoms, idx_b)
        q = relu_shift(ctxs @ W.T, RELU_B)
        sims = (byte_atoms @ q.T) / N
        P_W = torch.softmax(BETA * sims, dim=0)
        sims_p = (active @ ctxs.T) / N
        w_p = torch.softmax(BETA * sims_p, dim=0)
        P_retr = torch.zeros(VOCAB_SIZE, B, device=DEVICE)
        P_retr.scatter_add_(0, labels.unsqueeze(1).expand(-1, B), w_p)
        P = ALPHA * P_retr + (1 - ALPHA) * P_W
        p_true = P.gather(0, t.unsqueeze(0)).squeeze(0).clamp(min=1e-12)
        total += float(-torch.log2(p_true).sum())
    return total / max(T, 1)


def augment_pool_with_indices(pool_v, pool_l, p_used, add_ctxs, add_tgts):
    """Add N entries to the pool. Returns new (pool_v, pool_l, used) without modifying originals."""
    n_new = add_ctxs.shape[0]
    new_used = min(p_used + n_new, POOL_SIZE)
    aug_v = pool_v.clone()
    aug_l = pool_l.clone()
    fits = min(n_new, POOL_SIZE - p_used)
    if fits > 0:
        aug_v[p_used:p_used + fits] = add_ctxs[:fits]
        aug_l[p_used:p_used + fits] = add_tgts[:fits]
    rest = n_new - fits
    if rest > 0:
        # overwrite oldest
        aug_v[:rest] = add_ctxs[fits:]
        aug_l[:rest] = add_tgts[fits:]
    return aug_v, aug_l, new_used


def run_one(seed):
    corpus_a = load_corpus_a()
    corpus_b = load_corpus_b()
    split_a = int(0.8 * len(corpus_a))
    train_a = corpus_a[:split_a]
    split_b = int(0.7 * len(corpus_b))
    train_b = corpus_b[:split_b]
    test_b = corpus_b[split_b:]
    gen = torch.Generator().manual_seed(seed)
    byte_atoms = make_bsc(VOCAB_SIZE, N, gen).to(DEVICE)
    pos_atoms = make_bsc(K, N, gen).to(DEVICE)

    W_A, pool_A, labels_A, used_A = train_phase_a(byte_atoms, pos_atoms, train_a)

    # Cluster the pool
    centroids, assignments = cluster_pool_kmeans(pool_A[:used_A], NUM_CLUSTERS, gen)

    # Build augmentation candidates from corpus_b
    aug_gen = torch.Generator().manual_seed(seed * 7)
    aug_ctxs, aug_tgts = chunk_corpus_to_ctxs(byte_atoms, pos_atoms, train_b, count=N_AUGMENT * 8, gen=aug_gen)
    # Assign aug_ctxs to clusters
    aug_assignments = (aug_ctxs @ centroids.T / N).argmax(dim=1)

    # For "close/sibling/distant" we need to know the dominant query cluster on test_b.
    # Build test_b query ctxs and find their dominant cluster.
    test_query_ctxs, _ = chunk_corpus_to_ctxs(byte_atoms, pos_atoms, test_b, count=256, gen=torch.Generator().manual_seed(seed * 11))
    query_clusters = find_query_clusters(test_query_ctxs, centroids)
    # Most common cluster among queries
    cluster_counts = torch.bincount(query_clusters, minlength=NUM_CLUSTERS)
    target_cluster = int(cluster_counts.argmax().item())
    # Sibling = the next most-common cluster
    other_counts = cluster_counts.clone(); other_counts[target_cluster] = -1
    sibling_cluster = int(other_counts.argmax().item())
    # Distant = the LEAST overlapping centroid with target
    centroid_sims = centroids @ centroids[target_cluster] / N
    centroid_sims[target_cluster] = float("inf")
    distant_cluster = int(centroid_sims.argmin().item())
    _say(f"  seed={seed}: target={target_cluster} (count={int(cluster_counts[target_cluster])}), sibling={sibling_cluster}, distant={distant_cluster}")

    # For each condition, pick N_AUGMENT examples from the target cluster
    close_mask = aug_assignments == target_cluster
    sibling_mask = aug_assignments == sibling_cluster
    distant_mask = aug_assignments == distant_cluster

    results = {}
    # baseline: no augmentation
    baseline_bpc = eval_with_pool(W_A, byte_atoms, pos_atoms, test_b, pool_A, labels_A, used_A)
    results["baseline_no_augment"] = baseline_bpc

    for label, mask in [("close", close_mask), ("sibling", sibling_mask), ("distant", distant_mask)]:
        sel_idx = torch.nonzero(mask).squeeze(1)
        if len(sel_idx) == 0:
            _say(f"  {label}: no candidates in this cluster, skipping")
            results[label] = None
            continue
        take = sel_idx[:N_AUGMENT]
        add_ctxs = aug_ctxs[take]
        add_tgts = aug_tgts[take]
        aug_v, aug_l, aug_used = augment_pool_with_indices(pool_A, labels_A, used_A, add_ctxs, add_tgts)
        bpc = eval_with_pool(W_A, byte_atoms, pos_atoms, test_b, aug_v, aug_l, aug_used)
        results[label] = bpc
        _say(f"  {label}: {len(take)} examples, bpc={bpc:.4f}, gain vs baseline = {baseline_bpc - bpc:+.4f}")

    return results


def main():
    _say(f"ICL x RSB synergy: K={K}, N_aug={N_AUGMENT}, {NUM_CLUSTERS} clusters, 3 seeds")
    all_results = []
    for seed in SEEDS:
        _say(f"\n[seed={seed}]")
        r = run_one(seed)
        all_results.append({"seed": seed, **r})

    _say("\n========= ICL x RSB SYNERGY VERDICT =========")
    for label in ["close", "sibling", "distant"]:
        gains = []
        for r in all_results:
            if r[label] is not None:
                gains.append(r["baseline_no_augment"] - r[label])
        if gains:
            mean_gain = sum(gains) / len(gains)
            sd = (sum((g - mean_gain) ** 2 for g in gains) / max(len(gains)-1, 1)) ** 0.5
            _say(f"  {label:8s}: mean gain = {mean_gain:+.4f}  (sd={sd:.4f}, n={len(gains)})")

    # Determine pattern
    close_mean = sum(r["baseline_no_augment"] - r["close"] for r in all_results if r["close"] is not None) / max(sum(1 for r in all_results if r["close"] is not None), 1)
    distant_mean = sum(r["baseline_no_augment"] - r["distant"] for r in all_results if r["distant"] is not None) / max(sum(1 for r in all_results if r["distant"] is not None), 1)
    if close_mean > distant_mean + 0.02:
        _say(f"\n  TREE-CLOSE dominant: same-cluster augmentation gives {close_mean - distant_mean:+.4f} more gain")
    elif distant_mean > close_mean + 0.02:
        _say(f"\n  TREE-DISTANT dominant: gap-fill outweighs schema-refinement")
    else:
        _say(f"\n  NO STRONG PREFERENCE: cluster placement doesn't dominate gain")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14f_icl_rsb_synergy"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps({
        "K": K, "N_AUGMENT": N_AUGMENT, "NUM_CLUSTERS": NUM_CLUSTERS,
        "SEEDS": SEEDS, "results": all_results,
    }, indent=2))


if __name__ == "__main__":
    main()
