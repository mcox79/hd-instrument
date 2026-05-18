"""Titans-style surprise-gated pool writes.

Citation: Behrouz, Zhong et al. arXiv 2501.00663 "Titans: Learning to Memorize
at Test Time" (Jan 2025). They show that scaling fast/episodic memory benefits
strongly from a *surprise* gate on memory writes — only commit (key, value)
to long-term memory when the per-token prediction loss / gradient norm exceeds
a threshold. Mechanism is closely related to predictive-coding error gating
and to phasic-NE arousal modulation in the brain.

Why this matters for us: our pool currently writes every (context, target)
pair in the first epoch indiscriminately. Easy/frequent bytes (spaces, common
letters) flood the pool and crowd out rare/informative items. A surprise gate
should improve pool retrieval quality directly, and (because pool retrieval
shows up in the ALPHA-mixed prediction) improve test bpc.

Implementation: at training time, after computing P_W(ctx) and the per-token
bits loss `bits = -log2 P(target | ctx)`, write to the pool only if
`bits > tau` for some threshold tau (or `bits > beta * running_mean(bits)`).

Sweep tau across a few values. Compare to:
- baseline (no gate, write everything from epoch 1) = 2.4994
- gate at the median (~50% of items, see if compression helps)
- gate at quartile (~25% of items, aggressive)
- gate at top decile (~10% of items, very selective)
- adaptive gate: write if bits > running_mean(bits)

Also measure pool-retrieval top-1 accuracy as the direct quality signal.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import torch

from hdlab import atoms, tracing


DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
SEED = 17
N = 4096
VOCAB_SIZE = 256
PAD_BYTE = 0
K = 4
AROUSAL = 0.3
BETA = 8.0
BATCH_SIZE = 64
POOL_SIZE = 1024
ALPHA = 0.3
DECAY = 1e-4
MAX_EPOCHS = 15
EPOCH_CHECKPOINTS = [1, 5, 10, 15]
RELU_B = 0.5

# Surprise gate variants. Each variant specifies a strategy and threshold.
#   "none": baseline (write everything from epoch 1)
#   "fixed": write if bits > tau_bits (in bits/char)
#   "adaptive": write if bits > running_mean(bits) * scale
#   "topk_per_batch": write the top-k highest-loss items per batch
VARIANTS = [
    ("baseline_no_gate", "none", None),
    ("fixed_tau_3.0", "fixed", 3.0),
    ("fixed_tau_4.0", "fixed", 4.0),
    ("fixed_tau_5.0", "fixed", 5.0),
    ("adaptive_1.0x_mean", "adaptive", 1.0),
    ("adaptive_1.5x_mean", "adaptive", 1.5),
    ("top25pct_per_batch", "topk_frac", 0.25),
    ("top10pct_per_batch", "topk_frac", 0.10),
]


def _say(msg: str) -> None:
    print(msg, flush=True)


def load_corpus() -> bytes:
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


def _build_context_bundles_batch(byte_atoms, pos_atoms, indices):
    bound = byte_atoms[indices] * pos_atoms.unsqueeze(0)
    summed = bound.sum(dim=1)
    mag = summed.abs().clamp(min=1e-8)
    return summed / mag.to(summed.dtype)


def magnitude_relu(q, b):
    eps = 1e-9
    mag = q.abs().clamp(min=eps)
    new_mag = torch.clamp(mag - b, min=0.0)
    return q * (new_mag / mag).to(q.dtype)


def _predict_W_batch(W, ctxs, byte_atoms, beta):
    n = ctxs.shape[1]
    q = ctxs @ W.T
    q = magnitude_relu(q, RELU_B)
    sims = (byte_atoms.conj() @ q.T).real / n
    return torch.softmax(beta * sims, dim=0)


def _predict_pool_batch(ctxs, pool_vecs, pool_labels, pool_used, beta):
    B = ctxs.shape[0]
    if pool_used == 0:
        return torch.full((VOCAB_SIZE, B), 1.0 / VOCAB_SIZE, device=ctxs.device)
    n = ctxs.shape[1]
    active = pool_vecs[:pool_used]
    labels = pool_labels[:pool_used]
    sims = (active.conj() @ ctxs.T).real / n
    weights = torch.softmax(beta * sims, dim=0)
    P_retr = torch.zeros(VOCAB_SIZE, B, device=ctxs.device)
    P_retr.scatter_add_(0, labels.unsqueeze(1).expand(-1, B), weights)
    return P_retr


def compute_write_mask(bits_batch, strategy, threshold, running_mean_bits):
    """Returns boolean mask of which batch items should be written to pool.

    bits_batch: (B,) per-token bits loss
    strategy: "none" | "fixed" | "adaptive" | "topk_frac"
    threshold: float meaning depends on strategy
    running_mean_bits: scalar running mean of bits seen so far
    """
    B = bits_batch.shape[0]
    if strategy == "none":
        return torch.ones(B, dtype=torch.bool, device=bits_batch.device)
    if strategy == "fixed":
        return bits_batch > threshold
    if strategy == "adaptive":
        return bits_batch > (running_mean_bits * threshold)
    if strategy == "topk_frac":
        k = max(1, int(threshold * B))
        topk_vals, _ = bits_batch.topk(k)
        cutoff = topk_vals[-1]
        return bits_batch >= cutoff
    raise ValueError(f"unknown strategy: {strategy}")


def run_config(label, strategy, threshold, train, test):
    quiet = tracing.TraceBus(enabled=False)
    with tracing.using(quiet):
        gen = torch.Generator().manual_seed(SEED)
        byte_atoms = torch.stack([atoms.make_atom_fhrr(N, gen) for _ in range(VOCAB_SIZE)]).to(DEVICE)
        pos_atoms = torch.stack([atoms.make_atom_fhrr(N, gen) for _ in range(K)]).to(DEVICE)
        W = torch.zeros((N, N), dtype=torch.complex64, device=DEVICE)
        pool_vecs = torch.zeros((POOL_SIZE, N), dtype=torch.complex64, device=DEVICE)
        pool_labels = torch.zeros(POOL_SIZE, dtype=torch.long, device=DEVICE)
        pool_used = 0
        pool_idx = 0
        running_sum_bits = 0.0
        running_count = 0

        pad = bytes([PAD_BYTE]) * K
        padded_train = pad + train
        padded_test = pad + test
        T_total = len(padded_train) - K
        T_test = len(padded_test) - K
        train_bytes = torch.tensor(list(padded_train), dtype=torch.long).to(DEVICE)
        test_bytes = torch.tensor(list(padded_test), dtype=torch.long).to(DEVICE)
        offsets = torch.arange(K - 1, -1, -1, device=DEVICE)
        pos_train = torch.arange(T_total, device=DEVICE)
        pos_test = torch.arange(T_test, device=DEVICE)
        train_idx = train_bytes[pos_train.unsqueeze(1) + offsets.unsqueeze(0)]
        train_targets = train_bytes[pos_train + K]
        test_idx = test_bytes[pos_test.unsqueeze(1) + offsets.unsqueeze(0)]
        test_targets = test_bytes[pos_test + K]

        history = []
        write_count_log = 0
        seen_count_log = 0
        t_start = time.perf_counter()
        for epoch in range(1, MAX_EPOCHS + 1):
            for batch_start in range(0, T_total, BATCH_SIZE):
                be = min(batch_start + BATCH_SIZE, T_total)
                idx_batch = train_idx[batch_start:be]
                tgt_batch = train_targets[batch_start:be]
                B = idx_batch.shape[0]
                ctxs = _build_context_bundles_batch(byte_atoms, pos_atoms, idx_batch)
                P_W = _predict_W_batch(W, ctxs, byte_atoms, BETA)
                # Per-token bits loss for surprise computation
                p_true = P_W.gather(0, tgt_batch.unsqueeze(0)).squeeze(0).clamp(min=1e-12)
                bits_batch = -torch.log2(p_true)
                # Hebbian delta update on W (unchanged)
                targets = byte_atoms[tgt_batch]
                expected = P_W.T.to(byte_atoms.dtype) @ byte_atoms
                errors = targets - expected
                dW = errors.T @ ctxs.conj() / N
                if DECAY > 0:
                    W.mul_(1.0 - DECAY)
                W.add_(dW, alpha=AROUSAL)
                # Pool write decision: only first epoch (matches baseline behavior)
                if epoch == 1:
                    rmb = running_sum_bits / max(running_count, 1)
                    write_mask = compute_write_mask(bits_batch, strategy, threshold, rmb)
                    written = int(write_mask.sum())
                    seen_count_log += B
                    write_count_log += written
                    if written > 0:
                        for b in range(B):
                            if not bool(write_mask[b]):
                                continue
                            pool_vecs[pool_idx] = ctxs[b]
                            pool_labels[pool_idx] = tgt_batch[b]
                            pool_idx = (pool_idx + 1) % POOL_SIZE
                            pool_used = min(pool_used + 1, POOL_SIZE)
                    running_sum_bits += float(bits_batch.sum())
                    running_count += B

            if epoch in EPOCH_CHECKPOINTS:
                total_bits = 0.0
                argmax_correct = 0
                pool_top1_correct = 0
                w_top1_correct = 0
                for bs in range(0, T_test, BATCH_SIZE):
                    be = min(bs + BATCH_SIZE, T_test)
                    ctxs = _build_context_bundles_batch(byte_atoms, pos_atoms, test_idx[bs:be])
                    P_W = _predict_W_batch(W, ctxs, byte_atoms, BETA)
                    P_retr = _predict_pool_batch(ctxs, pool_vecs, pool_labels, pool_used, BETA)
                    P = ALPHA * P_retr + (1.0 - ALPHA) * P_W
                    tgts = test_targets[bs:be]
                    p_true = P.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)
                    total_bits += float(-torch.log2(p_true).sum())
                    argmax_correct += int((P.argmax(dim=0) == tgts).sum())
                    pool_top1_correct += int((P_retr.argmax(dim=0) == tgts).sum())
                    w_top1_correct += int((P_W.argmax(dim=0) == tgts).sum())
                test_bpc = total_bits / max(T_test, 1)
                argmax_acc = argmax_correct / max(T_test, 1)
                pool_acc = pool_top1_correct / max(T_test, 1)
                w_acc = w_top1_correct / max(T_test, 1)
                elapsed = time.perf_counter() - t_start
                write_rate = write_count_log / max(seen_count_log, 1)
                history.append({
                    "epoch": epoch, "test_bpc": test_bpc,
                    "argmax_accuracy": argmax_acc, "pool_top1_acc": pool_acc,
                    "w_top1_acc": w_acc, "wall_s": elapsed,
                    "pool_used": pool_used, "write_rate_epoch1": write_rate,
                })
                _say(f"    [{label}] ep={epoch}  bpc={test_bpc:.4f}  arg={argmax_acc:.4f}  "
                     f"poolT1={pool_acc:.3f}  wT1={w_acc:.3f}  pool={pool_used}  wr={write_rate:.2f}  ({elapsed:.1f}s)")
        return {"label": label, "strategy": strategy, "threshold": threshold, "history": history}


def main() -> None:
    _say("Loading corpus...")
    corpus = load_corpus()
    cut = int(len(corpus) * 0.8)
    train, test = corpus[:cut], corpus[cut:]
    _say(f"  train={len(train)}, test={len(test)} bytes")
    _say(f"\nTitans-style surprise-gated pool sweep")
    _say(f"  N={N}, K={K}, arousal={AROUSAL}, beta={BETA}, decay={DECAY}, pool={POOL_SIZE}, relu_b={RELU_B}")
    _say(f"  Reference: baseline_no_gate = 2.4994 (combined+modReLU)")
    _say(f"  Lit: Behrouz-Zhong et al. 2025 Titans (arXiv 2501.00663)")
    _say(f"  Prediction: surprise gate should improve pool quality, lowering bpc")

    all_results = []
    t_all = time.perf_counter()
    for label, strategy, threshold in VARIANTS:
        _say(f"\n--- {label} (strategy={strategy}, threshold={threshold}) ---")
        t0 = time.perf_counter()
        r = run_config(label, strategy, threshold, train, test)
        r["wall_time_s"] = time.perf_counter() - t0
        all_results.append(r)
        best = min(r["history"], key=lambda h: h["test_bpc"])
        _say(f"  Best for {label}: ep={best['epoch']}, bpc={best['test_bpc']:.4f}, "
             f"pool_used={best['pool_used']}, wr={best['write_rate_epoch1']:.3f}")

    _say(f"\n========= SUMMARY =========")
    _say(f"{'variant':>22s} {'best_ep':>8s} {'best_bpc':>10s} {'pool':>6s} {'wr':>6s} {'delta':>8s}")
    baseline_bpc = min(all_results[0]["history"], key=lambda h: h["test_bpc"])["test_bpc"]
    for r in all_results:
        best = min(r["history"], key=lambda h: h["test_bpc"])
        delta = best["test_bpc"] - baseline_bpc
        _say(f"{r['label']:>22s} {best['epoch']:>8d} {best['test_bpc']:>10.4f} "
             f"{best['pool_used']:>6d} {best['write_rate_epoch1']:>6.3f} {delta:>+8.4f}")

    out = {"seed": SEED, "n": N, "k": K, "arousal": AROUSAL, "beta": BETA, "decay": DECAY,
           "pool_size": POOL_SIZE, "alpha": ALPHA, "relu_b": RELU_B, "max_epochs": MAX_EPOCHS,
           "variants": [{"label": v[0], "strategy": v[1], "threshold": v[2]} for v in VARIANTS],
           "results": all_results,
           "wall_time_total_s": time.perf_counter() - t_all}
    out_path = Path(__file__).resolve().parent.parent / "data" / "exp_surprise_gated_pool_charlm"
    out_path.mkdir(parents=True, exist_ok=True)
    (out_path / "metrics.json").write_text(json.dumps(out, indent=2, default=str))
    _say(f"\nWrote {out_path / 'metrics.json'}")
    _say(f"Total wall: {time.perf_counter() - t_all:.1f}s")


if __name__ == "__main__":
    main()
