"""Wave 4.5 v4: Plain SGD test of preconditioner hypothesis.

v3 with MSE loss + AdamW failed to close the gap to delta rule
(-0.71 to -0.95 bpc across LRs and N values). The remaining hypothesis
from the rehabilitation list: Adam's per-coordinate preconditioning
distorts the prediction landscape. Plain SGD has no preconditioning -
gradient direction is preserved as-is.

If SGD closes the gap to delta rule: preconditioner story confirmed,
and the delta rule's optimality is just "stochastic gradient with
no extra preconditioning, on MSE in codebook space."

If SGD doesn't close: deeper architectural or interaction mismatch.

Single N=4096 (cleanest comparison with v3). LR sweep is wider for SGD
since lack of preconditioning means we need larger raw rates. The
delta rule's alpha=0.3 with batch_size=64 corresponds to SGD lr ~ 10
(since SGD step = lr * 2/batch * residual * ctx, matching delta_rule
step = alpha * residual * ctx).

Reference (delta rule N=4096): 2.4817 bpc.
v3 (AdamW MSE loss): 3.3228 best, gap -0.84.

Test config:
- Optimizer: torch.optim.SGD, momentum=0 (no momentum complication)
- Loss: MSE in codebook space (same as v3)
- W init: identity
- No ReLU
- LR sweep: [0.1, 1.0, 10.0, 30.0]
- 15 epochs
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import torch


torch.set_float32_matmul_precision("high")

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
SEED = 17
VOCAB_SIZE = 256
PAD_BYTE = 0
K = 4
BETA = 8.0
BATCH_SIZE = 64
POOL_SIZE = 1024
ALPHA = 0.3
MAX_EPOCHS = 15
EVAL_AT = [5, 15]
RELU_B = 0.5
N = 4096
WEIGHT_DECAY = 1e-4
LR_SWEEP_SGD = [0.1, 1.0, 10.0, 30.0]
DELTA_RULE_REFERENCE = 2.4817


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


def make_bsc_atoms(k, n, gen):
    raw = torch.rand((k, n), generator=gen)
    return (2.0 * (raw > 0.5).float() - 1.0)


def build_ctx_bundles_bsc(byte_atoms, pos_atoms, indices):
    bound = byte_atoms[indices] * pos_atoms.unsqueeze(0)
    summed = bound.sum(dim=1)
    out = torch.sign(summed)
    return torch.where(out == 0, torch.ones_like(out), out)


def predict_W(W, ctxs, byte_atoms, beta, n):
    q = ctxs @ W.T
    sims = (byte_atoms @ q.T) / n
    return torch.softmax(beta * sims, dim=0)


def predict_pool(ctxs, pool_vecs, pool_labels, pool_used, beta, n):
    B = ctxs.shape[0]
    if pool_used == 0:
        return torch.full((VOCAB_SIZE, B), 1.0 / VOCAB_SIZE, device=ctxs.device)
    active = pool_vecs[:pool_used]
    labels = pool_labels[:pool_used]
    sims = (active @ ctxs.T) / n
    weights = torch.softmax(BETA * sims, dim=0)
    P_retr = torch.zeros(VOCAB_SIZE, B, device=ctxs.device)
    P_retr.scatter_add_(0, labels.unsqueeze(1).expand(-1, B), weights)
    return P_retr


def run_sgd_variant(lr, train, test):
    gen = torch.Generator().manual_seed(SEED)
    byte_atoms = make_bsc_atoms(VOCAB_SIZE, N, gen).to(DEVICE)
    pos_atoms = make_bsc_atoms(K, N, gen).to(DEVICE)
    W = torch.nn.Parameter(torch.eye(N, dtype=torch.float32, device=DEVICE))
    optimizer = torch.optim.SGD([W], lr=lr, momentum=0.0, weight_decay=WEIGHT_DECAY)

    pool_vecs = torch.zeros((POOL_SIZE, N), dtype=torch.float32, device=DEVICE)
    pool_labels = torch.zeros(POOL_SIZE, dtype=torch.long, device=DEVICE)
    pool_used = 0
    pool_idx = 0
    arange_b = torch.arange(BATCH_SIZE, device=DEVICE)

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
    t_start = time.perf_counter()
    for epoch in range(1, MAX_EPOCHS + 1):
        for batch_start in range(0, T_total, BATCH_SIZE):
            be = min(batch_start + BATCH_SIZE, T_total)
            idx_batch = train_idx[batch_start:be]
            tgt_batch = train_targets[batch_start:be]
            B = idx_batch.shape[0]
            ctxs = build_ctx_bundles_bsc(byte_atoms, pos_atoms, idx_batch)
            q = ctxs @ W.T
            target_atoms = byte_atoms[tgt_batch]
            loss = ((q - target_atoms) ** 2).mean()
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            if epoch == 1:
                with torch.no_grad():
                    dest = (pool_idx + arange_b[:B]) % POOL_SIZE
                    pool_vecs.index_copy_(0, dest, ctxs.detach())
                    pool_labels.index_copy_(0, dest, tgt_batch)
                    pool_idx = (pool_idx + B) % POOL_SIZE
                    pool_used = min(pool_used + B, POOL_SIZE)
        if epoch in EVAL_AT:
            with torch.no_grad():
                total_bits = 0.0
                argmax_correct = 0
                for bs in range(0, T_test, BATCH_SIZE):
                    be = min(bs + BATCH_SIZE, T_test)
                    ctxs = build_ctx_bundles_bsc(byte_atoms, pos_atoms, test_idx[bs:be])
                    P_W = predict_W(W, ctxs, byte_atoms, BETA, N)
                    P_retr = predict_pool(ctxs, pool_vecs, pool_labels, pool_used, BETA, N)
                    P = ALPHA * P_retr + (1.0 - ALPHA) * P_W
                    tgts = test_targets[bs:be]
                    p_true = P.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)
                    total_bits += float(-torch.log2(p_true).sum())
                    argmax_correct += int((P.argmax(dim=0) == tgts).sum())
                test_bpc = total_bits / max(T_test, 1)
                argmax_acc = argmax_correct / max(T_test, 1)
                w_frob = float(W.detach().pow(2).sum().sqrt())
                elapsed = time.perf_counter() - t_start
                history.append({"epoch": epoch, "test_bpc": test_bpc,
                                "argmax_accuracy": argmax_acc, "w_frob": w_frob,
                                "wall_s": elapsed})
                _say(f"    [SGD N={N} lr={lr:.0e}] ep={epoch}  bpc={test_bpc:.4f}  arg={argmax_acc:.4f}  ||W||={w_frob:.1f}  ({elapsed:.1f}s)")
    return history


def main() -> None:
    _say(f"Wave 4.5 v4: Plain SGD test (no preconditioning)")
    _say(f"  Reference (delta rule N=4096): {DELTA_RULE_REFERENCE}")
    _say(f"  v3 (AdamW MSE loss best): 3.3228 (gap -0.84)")
    _say(f"  Hypothesis: Adam's preconditioner causes the gap. Plain SGD should close it.")
    _say(f"  LR sweep: {LR_SWEEP_SGD}")

    corpus = load_corpus()
    split = int(0.8 * len(corpus))
    train, test = corpus[:split], corpus[split:]
    _say(f"  train={len(train)}, test={len(test)} bytes")

    results = []
    for lr in LR_SWEEP_SGD:
        _say(f"\n  Plain SGD (lr={lr})")
        history = run_sgd_variant(lr, train, test)
        best = min(history, key=lambda h: h["test_bpc"])
        delta = DELTA_RULE_REFERENCE - best["test_bpc"]
        _say(f"    Best: bpc={best['test_bpc']:.4f}  vs delta_rule={DELTA_RULE_REFERENCE}  (gap: {delta:+.4f})")
        results.append({"lr": lr, "history": history, "best_bpc": best["test_bpc"],
                       "gap_vs_delta": delta})

    _say(f"\n========= SUMMARY =========")
    _say(f"  {'lr':>10}  {'best_bpc':>10}  {'gap_vs_delta':>14}")
    for r in results:
        _say(f"  {r['lr']:>10}  {r['best_bpc']:>10.4f}  {r['gap_vs_delta']:>+14.4f}")

    best_r = min(results, key=lambda r: r["best_bpc"])
    _say(f"\n  Best SGD config: lr={best_r['lr']}, bpc={best_r['best_bpc']:.4f}")
    if abs(best_r["gap_vs_delta"]) < 0.05:
        _say(f"  HYPOTHESIS SUPPORTED: gap closes to within 0.05 bpc. Preconditioner story confirmed.")
    elif best_r["gap_vs_delta"] > 0:
        _say(f"  PARTIAL: SGD beats Adam but does not match delta rule. Preconditioner is PART of the gap.")
    else:
        _say(f"  HYPOTHESIS WEAK: SGD also underperforms. Gap is not (only) preconditioner.")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave45_v4_sgd"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = {"N": N, "lr_sweep": LR_SWEEP_SGD, "results": results,
           "delta_rule_reference": DELTA_RULE_REFERENCE}
    (out_dir / "metrics.json").write_text(json.dumps(out, indent=2, default=str))
    _say(f"\nWrote {out_dir / 'metrics.json'}")


if __name__ == "__main__":
    main()
