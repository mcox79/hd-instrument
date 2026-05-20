"""ICL scaling: how does ICL gain scale with POOL_SIZE?

Per wave14f_icl_scaling_laws_research:
- ICL gain log-linear in P (no saturation across literature's 9+ decades)
- VSA capacity: d >= P * log(K/delta); knee at alpha = P/d ~= 1/log K
- Critical null: if flat across P, ICL gain is encoder-side not retrieval-side
- Shuffled-pool diagnostic: shuffle pool labels; if ICL gain persists, it's not retrieval

Sweep POOL_SIZE in {512, 1024, 2048, 4096} at fixed d=4096, N=64.
Include shuffled-pool control at each POOL_SIZE.

Predicted: ICL gain rises log-linearly with P, while shuffled-pool gain stays
flat near zero. If both rise similarly, ICL gain is encoder-side.

3 seeds. ~1.5h GPU.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import torch

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
VOCAB_SIZE = 256
PAD_BYTE = 0
K = 4
N = 4096
BETA = 8.0
BATCH_SIZE = 64
MAX_EPOCHS = 15
ALPHA = 0.3
RELU_B = 0.5
DELTA_RULE_ALPHA = 0.3
DELTA_RULE_DECAY = 1e-4
N_AUGMENT = 64

POOL_SIZES = [512, 1024, 2048, 4096]
SEEDS = [17, 23, 31]


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


def train_phase_a(byte_atoms, pos_atoms, train_bytes, pool_size):
    W = torch.zeros((N, N), device=DEVICE)
    pool_v = torch.zeros((pool_size, N), device=DEVICE)
    pool_l = torch.zeros(pool_size, dtype=torch.long, device=DEVICE)
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
                    dest = (p_idx + arange[:B]) % pool_size
                    pool_v.index_copy_(0, dest, ctxs)
                    pool_l.index_copy_(0, dest, t)
                    p_idx = (p_idx + B) % pool_size
                    p_used = min(p_used + B, pool_size)
    return W, pool_v, pool_l, p_used


def chunk_corpus(byte_atoms, pos_atoms, corpus, count, gen):
    pad = bytes([PAD_BYTE]) * K
    padded = pad + corpus
    T = len(padded) - K
    if T <= 0:
        return torch.zeros((0, N), device=DEVICE), torch.zeros(0, dtype=torch.long, device=DEVICE)
    bt = torch.tensor(list(padded), dtype=torch.long).to(DEVICE)
    offs = torch.arange(K - 1, -1, -1, device=DEVICE)
    pos = torch.arange(T, device=DEVICE)
    idx_full = bt[pos.unsqueeze(1) + offs.unsqueeze(0)]
    tgts_full = bt[pos + K]
    perm = torch.randperm(T, generator=gen)[:min(count, T)].to(DEVICE)
    selected_idx = idx_full[perm]
    selected_tgts = tgts_full[perm]
    return build_ctx(byte_atoms, pos_atoms, selected_idx), selected_tgts


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


def augment(pool_v, pool_l, p_used, add_ctxs, add_tgts, pool_size):
    """Append add_ctxs to pool. If overflow, wrap-around."""
    n_new = add_ctxs.shape[0]
    new_used = min(p_used + n_new, pool_size)
    aug_v = pool_v.clone(); aug_l = pool_l.clone()
    fits = min(n_new, pool_size - p_used)
    if fits > 0:
        aug_v[p_used:p_used + fits] = add_ctxs[:fits]
        aug_l[p_used:p_used + fits] = add_tgts[:fits]
    rest = n_new - fits
    if rest > 0:
        aug_v[:rest] = add_ctxs[fits:]
        aug_l[:rest] = add_tgts[fits:]
    return aug_v, aug_l, new_used


def run_one(seed, pool_size):
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
    W_A, pool_A, labels_A, used_A = train_phase_a(byte_atoms, pos_atoms, train_a, pool_size)

    # Baseline: no augmentation
    baseline = eval_with_pool(W_A, byte_atoms, pos_atoms, test_b, pool_A, labels_A, used_A)

    # Relevant ICL: augment with N=64 corpus-B examples
    aug_gen = torch.Generator().manual_seed(seed * 7)
    add_ctxs, add_tgts = chunk_corpus(byte_atoms, pos_atoms, train_b, N_AUGMENT, aug_gen)
    aug_v, aug_l, aug_used = augment(pool_A, labels_A, used_A, add_ctxs, add_tgts, pool_size)
    relevant_bpc = eval_with_pool(W_A, byte_atoms, pos_atoms, test_b, aug_v, aug_l, aug_used)

    # Shuffled control: same augmentation contexts but shuffled labels
    shuf_idx = torch.randperm(N_AUGMENT, generator=torch.Generator().manual_seed(seed * 13)).to(DEVICE)
    shuffled_tgts = add_tgts[shuf_idx]
    aug_v_s, aug_l_s, aug_used_s = augment(pool_A, labels_A, used_A, add_ctxs, shuffled_tgts, pool_size)
    shuffled_bpc = eval_with_pool(W_A, byte_atoms, pos_atoms, test_b, aug_v_s, aug_l_s, aug_used_s)

    return {
        "pool_size": pool_size,
        "baseline_bpc": baseline,
        "relevant_bpc": relevant_bpc,
        "shuffled_bpc": shuffled_bpc,
        "relevant_gain": baseline - relevant_bpc,
        "shuffled_gain": baseline - shuffled_bpc,
        "retrieval_signal": (baseline - relevant_bpc) - (baseline - shuffled_bpc),
    }


def main():
    _say(f"ICL scaling: POOL_SIZE sweep in {POOL_SIZES}, N_aug={N_AUGMENT}, 3 seeds")
    _say(f"  + shuffled-pool control to isolate retrieval-side gain from encoder-side")

    all_results = {ps: [] for ps in POOL_SIZES}
    for seed in SEEDS:
        _say(f"\n[seed={seed}]")
        for ps in POOL_SIZES:
            r = run_one(seed, ps)
            all_results[ps].append(r)
            _say(f"  P={ps:5d}: relevant gain={r['relevant_gain']:+.4f}  shuffled gain={r['shuffled_gain']:+.4f}  retrieval signal={r['retrieval_signal']:+.4f}")

    _say("\n========= ICL SCALING VERDICT =========")
    relevant_means = []
    shuffled_means = []
    retrieval_means = []
    for ps in POOL_SIZES:
        rel_mean = sum(r["relevant_gain"] for r in all_results[ps]) / len(all_results[ps])
        shuf_mean = sum(r["shuffled_gain"] for r in all_results[ps]) / len(all_results[ps])
        retr_mean = sum(r["retrieval_signal"] for r in all_results[ps]) / len(all_results[ps])
        relevant_means.append(rel_mean); shuffled_means.append(shuf_mean); retrieval_means.append(retr_mean)
        _say(f"  P={ps:5d} (log2={math.log2(ps):.1f}): rel={rel_mean:+.4f}  shuf={shuf_mean:+.4f}  retr-signal={retr_mean:+.4f}")

    # Linear regression of relevant gain on log2(P)
    log_p = [math.log2(ps) for ps in POOL_SIZES]
    log_p_mean = sum(log_p) / len(log_p)
    rel_mean_all = sum(relevant_means) / len(relevant_means)
    slope_num = sum((log_p[i] - log_p_mean) * (relevant_means[i] - rel_mean_all) for i in range(len(POOL_SIZES)))
    slope_den = sum((log_p[i] - log_p_mean) ** 2 for i in range(len(POOL_SIZES)))
    slope = slope_num / slope_den if slope_den > 0 else 0.0
    _say(f"\n  Slope of relevant gain vs log2(P): {slope:+.4f} bpc per doubling")
    if slope > 0.01 and retrieval_means[-1] > 0.05:
        _say(f"  LOG-LINEAR SCALING CONFIRMED: ICL gain rises with P, retrieval signal dominant.")
    elif retrieval_means[-1] < 0.02 and relevant_means[-1] > 0.05:
        _say(f"  NULL CONFIRMED: ICL gain is encoder-side, not retrieval-side (shuffled = relevant).")
    else:
        _say(f"  AMBIGUOUS: slope={slope:+.4f}, retrieval signal at largest P = {retrieval_means[-1]:+.4f}")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14f_icl_scaling_pool"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps({
        "POOL_SIZES": POOL_SIZES, "SEEDS": SEEDS, "N_AUGMENT": N_AUGMENT,
        "slope_log2P": slope,
        "results": {str(ps): all_results[ps] for ps in POOL_SIZES},
    }, indent=2))


if __name__ == "__main__":
    main()
