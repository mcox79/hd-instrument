"""R10 K-adaptive schedule -- implements wave14c2 research recommendation.

Replaces fixed (nc=50, lam=0.3, beta=16) best-config with K-dependent:
  lam(K) = 0.7 + (0.3 - 0.7) * sigmoid((K - 8) / 3)
  beta(K) = 8 + 8 * sigmoid((K - 12) / 4)
  nc(K) = min(round(K*(K-1)/2 * 1.0), 200) but >= 10

Predicted: matches default at K=2 (which works), matches best at K>=32 (which we
have positive verdicts for).

Multi-seed at K = [2, 4, 8, 16, 32, 64, 128, 256] to compare K-adaptive vs:
  - default config (nc=100, lam=0.7, beta=8)
  - fixed best config (nc=50, lam=0.3, beta=16)
  - K-adaptive (the rescue)
"""

from __future__ import annotations

import json
import math
from collections import Counter
from pathlib import Path

import torch

torch.set_float32_matmul_precision("high")

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
VOCAB_SIZE = 256
PAD_BYTE = 0
N = 4096
BETA_BASE = 8.0
BYTE_BETA = 16.0
BATCH_SIZE = 64
POOL_SIZE = 1024
ALPHA = 0.3
MAX_EPOCHS = 15
RELU_B = 0.5
DELTA_RULE_ALPHA = 0.3
DELTA_RULE_DECAY = 1e-4

DEFAULT_NC = 100
DEFAULT_LAMBDA = 0.7
DEFAULT_BETA = 8.0
BEST_NC = 50
BEST_LAMBDA = 0.3
BEST_BETA = 16.0

SEEDS = [17, 23, 31]
K_LEVELS = [2, 4, 8, 16, 32, 64, 128, 256]


def _say(m): print(m, flush=True)


def sigmoid(x):
    return 1.0 / (1.0 + math.exp(-x))


def adaptive_lam(K):
    return 0.7 + (0.3 - 0.7) * sigmoid((K - 8) / 3.0)


def adaptive_beta(K):
    return 8.0 + 8.0 * sigmoid((K - 12) / 4.0)


def adaptive_nc(K):
    return max(10, min(round(K * (K - 1) / 2), 200))


def load_corpus_a():
    repo = Path(__file__).resolve().parent.parent
    files = [repo / "PLAN.md", repo / "NEXT_PHASE.md", repo / "README.md",
             repo / "PROGRESS.md", repo / "RESULTS.md", repo / "CLAUDE.md"]
    parts = []
    for f in files:
        if f.exists():
            parts.append(f.read_bytes()); parts.append(b"\n\n")
    return b"".join(parts)


def shuffle_bytes(data, seed):
    gen = torch.Generator().manual_seed(seed)
    perm = torch.randperm(len(data), generator=gen).tolist()
    return bytes(data[p] for p in perm)


def make_bsc(k, n, gen):
    return 2.0 * (torch.rand((k, n), generator=gen) > 0.5).float() - 1.0


def build_ctx(byte_atoms, pos_atoms, idx, K):
    b = byte_atoms[idx] * pos_atoms.unsqueeze(0)
    s = b.sum(dim=1)
    out = torch.sign(s)
    return torch.where(out == 0, torch.ones_like(out), out)


def shifted_relu(q, b):
    return torch.clamp(q - b, min=0.0)


def predict_W(W, ctxs, byte_atoms, beta, n):
    q = shifted_relu(ctxs @ W.T, RELU_B)
    sims = (byte_atoms @ q.T) / n
    return torch.softmax(beta * sims, dim=0)


def factored_scores(idx, bundles, byte_atoms, pos_atoms, positions, n):
    B = idx.shape[0]
    out = torch.zeros((bundles.shape[0], B), device=byte_atoms.device)
    for r in positions:
        proj_r = bundles * pos_atoms[r].unsqueeze(0)
        q_r = byte_atoms[idx[:, r]]
        out += (proj_r @ q_r.T) / n
    return out


def decompose_pool(pool_vecs, byte_atoms, pos_atoms, K, n):
    P = pool_vecs.shape[0]
    out = torch.zeros((P, K), dtype=torch.long, device=DEVICE)
    for r in range(K):
        proj = pool_vecs * pos_atoms[r].unsqueeze(0)
        out[:, r] = (proj @ byte_atoms.T / n).argmax(dim=1)
    return out


def extract_ppmi(pool_byte_at_pos, K_pos, nc, k_neg=1.0):
    P = pool_byte_at_pos.shape[0]
    pair_counts = Counter()
    marg = Counter()
    total = 0
    for i in range(P):
        bytes_at = pool_byte_at_pos[i].cpu().tolist()
        for pi in range(K_pos):
            marg[(pi, bytes_at[pi])] += 1
            for pj in range(pi + 1, K_pos):
                pair_counts[(pi, bytes_at[pi], pj, bytes_at[pj])] += 1
                total += 1
    scores = []
    for (pi, bi, pj, bj), cnt in pair_counts.items():
        p_ab = cnt / total if total else 0
        p_a = marg[(pi, bi)] / P
        p_b = marg[(pj, bj)] / P
        if p_a > 0 and p_b > 0 and p_ab > 0:
            pmi = math.log(p_ab / (p_a * p_b ** 0.75 + 1e-12)) - math.log(k_neg)
            scores.append((pi, bi, pj, bj, max(0.0, pmi)))
    scores.sort(key=lambda x: -x[4])
    return scores[:nc]


def train_phase(byte_atoms, pos_atoms, train_bytes, K, build_pool, W_start=None):
    W = torch.zeros((N, N), device=DEVICE) if W_start is None else W_start.clone()
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
            ctxs = build_ctx(byte_atoms, pos_atoms, idx[bs:be], K)
            t = tgt[bs:be]
            with torch.no_grad():
                q = shifted_relu(ctxs @ W.T, RELU_B)
                sims = (byte_atoms @ q.T) / N
                P = torch.softmax(BETA_BASE * sims, dim=0)
                resid = byte_atoms[t] - (P.T @ byte_atoms)
                dW = (resid.T @ ctxs) / N
                W.mul_(1.0 - DELTA_RULE_DECAY); W.add_(dW, alpha=DELTA_RULE_ALPHA)
                if build_pool and epoch == 1:
                    dest = (p_idx + arange[:B]) % POOL_SIZE
                    pool_v.index_copy_(0, dest, ctxs)
                    pool_l.index_copy_(0, dest, t)
                    p_idx = (p_idx + B) % POOL_SIZE
                    p_used = min(p_used + B, POOL_SIZE)
    return W, pool_v, pool_l, p_used


def eval_cfg(W, byte_atoms, pos_atoms, test_bytes, pool_v, pool_l, p_used, K,
             ppmi, pool_byte_at_pos, lam, beta_ret):
    pad = bytes([PAD_BYTE]) * K
    padded = pad + test_bytes
    T = len(padded) - K
    bt = torch.tensor(list(padded), dtype=torch.long).to(DEVICE)
    offs = torch.arange(K - 1, -1, -1, device=DEVICE)
    pos = torch.arange(T, device=DEVICE)
    idx_all = bt[pos.unsqueeze(1) + offs.unsqueeze(0)]
    tgts_all = bt[pos + K]
    totals = {"a_only": 0.0, "linear": 0.0}
    active = pool_v[:p_used]
    labels = pool_l[:p_used]
    C3 = list(range(K - 1))
    c_active = torch.zeros((p_used, len(ppmi)), device=DEVICE)
    for c_idx, (pi, bi, pj, bj, _) in enumerate(ppmi):
        m = (pool_byte_at_pos[:, pi] == bi) & (pool_byte_at_pos[:, pj] == bj)
        c_active[:, c_idx] = m.float()
    for bs in range(0, T, BATCH_SIZE):
        be = min(bs + BATCH_SIZE, T)
        idx_b = idx_all[bs:be]
        tgts = tgts_all[bs:be]
        B = idx_b.shape[0]
        ctxs = build_ctx(byte_atoms, pos_atoms, idx_b, K)
        P_W = predict_W(W, ctxs, byte_atoms, BETA_BASE, N)
        scores_a = factored_scores(idx_b, active, byte_atoms, pos_atoms, C3, N)
        w_a = torch.softmax(beta_ret * scores_a, dim=0)
        P_a = torch.zeros(VOCAB_SIZE, B, device=DEVICE)
        P_a.scatter_add_(0, labels.unsqueeze(1).expand(-1, B), w_a)
        P_a_final = ALPHA * P_a + (1 - ALPHA) * P_W
        q_active = torch.zeros((B, len(ppmi)), device=DEVICE)
        for c_idx, (pi, bi, pj, bj, _) in enumerate(ppmi):
            q_active[:, c_idx] = ((idx_b[:, pi] == bi) & (idx_b[:, pj] == bj)).float()
        s_b = c_active @ q_active.T
        lc = lam * scores_a + (1 - lam) * s_b
        w_lin = torch.softmax(beta_ret * lc, dim=0)
        P_lin = torch.zeros(VOCAB_SIZE, B, device=DEVICE)
        P_lin.scatter_add_(0, labels.unsqueeze(1).expand(-1, B), w_lin)
        P_lin_final = ALPHA * P_lin + (1 - ALPHA) * P_W
        for k, P_final in [("a_only", P_a_final), ("linear", P_lin_final)]:
            p_true = P_final.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)
            totals[k] += float(-torch.log2(p_true).sum())
    return {k: v / max(T, 1) for k, v in totals.items()}


def run_one(K, seed):
    corpus_a = load_corpus_a()
    corpus_b = shuffle_bytes(corpus_a, seed=seed + 1)
    split = int(0.8 * len(corpus_a))
    train_a, test_a = corpus_a[:split], corpus_a[split:]
    train_b = corpus_b[:int(0.8 * len(corpus_b))]
    gen = torch.Generator().manual_seed(seed)
    byte_atoms = make_bsc(VOCAB_SIZE, N, gen).to(DEVICE)
    pos_atoms = make_bsc(K, N, gen).to(DEVICE)
    W_A, pool_A, labels_A, used_A = train_phase(byte_atoms, pos_atoms, train_a, K, build_pool=True)
    pool_byte = decompose_pool(pool_A[:used_A], byte_atoms, pos_atoms, K, N)

    nc_adap = adaptive_nc(K)
    lam_adap = adaptive_lam(K)
    beta_adap = adaptive_beta(K)
    ppmi_default = extract_ppmi(pool_byte, K, DEFAULT_NC)
    ppmi_best = extract_ppmi(pool_byte, K, BEST_NC)
    ppmi_adap = extract_ppmi(pool_byte, K, nc_adap)

    W_AB, _, _, _ = train_phase(byte_atoms, pos_atoms, train_b, K, build_pool=False, W_start=W_A)

    pre_d = eval_cfg(W_A, byte_atoms, pos_atoms, test_a, pool_A, labels_A, used_A, K,
                      ppmi_default, pool_byte, DEFAULT_LAMBDA, DEFAULT_BETA)
    post_d = eval_cfg(W_AB, byte_atoms, pos_atoms, test_a, pool_A, labels_A, used_A, K,
                       ppmi_default, pool_byte, DEFAULT_LAMBDA, DEFAULT_BETA)
    pre_b = eval_cfg(W_A, byte_atoms, pos_atoms, test_a, pool_A, labels_A, used_A, K,
                      ppmi_best, pool_byte, BEST_LAMBDA, BEST_BETA)
    post_b = eval_cfg(W_AB, byte_atoms, pos_atoms, test_a, pool_A, labels_A, used_A, K,
                       ppmi_best, pool_byte, BEST_LAMBDA, BEST_BETA)
    pre_a = eval_cfg(W_A, byte_atoms, pos_atoms, test_a, pool_A, labels_A, used_A, K,
                      ppmi_adap, pool_byte, lam_adap, beta_adap)
    post_a = eval_cfg(W_AB, byte_atoms, pos_atoms, test_a, pool_A, labels_A, used_A, K,
                       ppmi_adap, pool_byte, lam_adap, beta_adap)

    return {
        "K": K, "seed": seed,
        "default_pre_gap": pre_d["a_only"] - pre_d["linear"],
        "default_post_gap": post_d["a_only"] - post_d["linear"],
        "best_pre_gap": pre_b["a_only"] - pre_b["linear"],
        "best_post_gap": post_b["a_only"] - post_b["linear"],
        "adaptive_pre_gap": pre_a["a_only"] - pre_a["linear"],
        "adaptive_post_gap": post_a["a_only"] - post_a["linear"],
        "adaptive_nc": nc_adap, "adaptive_lam": lam_adap, "adaptive_beta": beta_adap,
    }


def main():
    _say(f"R10 K-adaptive schedule: K in {K_LEVELS}, {len(SEEDS)} seeds")
    _say(f"  default: fixed nc=100, lam=0.7, beta=8")
    _say(f"  best:    fixed nc=50, lam=0.3, beta=16")
    _say(f"  adaptive: nc(K), lam(K), beta(K) per sigmoid schedule")
    all_results = {}
    for K in K_LEVELS:
        _say(f"\n=== K={K} (adaptive nc={adaptive_nc(K)}, lam={adaptive_lam(K):.3f}, beta={adaptive_beta(K):.2f}) ===")
        results = []
        for seed in SEEDS:
            r = run_one(K, seed)
            _say(f"  seed={seed}: default post_gap={r['default_post_gap']:+.4f}  best={r['best_post_gap']:+.4f}  ADAPTIVE={r['adaptive_post_gap']:+.4f}")
            results.append(r)
        all_results[K] = results
    _say(f"\n========= K-ADAPTIVE VERDICT =========")
    for K in K_LEVELS:
        rs = all_results[K]
        def_mean = sum(r["default_post_gap"] for r in rs) / len(rs)
        best_mean = sum(r["best_post_gap"] for r in rs) / len(rs)
        adap_mean = sum(r["adaptive_post_gap"] for r in rs) / len(rs)
        _say(f"  K={K:4d}: default={def_mean:+.4f}  best={best_mean:+.4f}  adaptive={adap_mean:+.4f}  (adap vs best: {adap_mean - best_mean:+.4f})")
    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14f_r10_K_adaptive"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps({
        "K_LEVELS": K_LEVELS, "SEEDS": SEEDS,
        "results": {str(K): all_results[K] for K in K_LEVELS},
    }, indent=2))


if __name__ == "__main__":
    main()
