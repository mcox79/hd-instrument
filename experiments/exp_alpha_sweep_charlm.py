"""Pool blend alpha sweep on the combined+modReLU baseline.

Direct rehabilitation of the Titans rejection: before deciding whether to gate
pool writes, measure how much the pool is contributing at all. If alpha=0 (no
pool) is already near baseline, pool-mechanism work has low ceiling.

Variants:
  alpha = 0.0  — W readout only, no pool contribution. Lower bound on importance.
  alpha = 0.1
  alpha = 0.3  — current best (2.4994)
  alpha = 0.5
  alpha = 0.7
  alpha = 1.0  — pool only, no W readout. Upper bound on pool quality.

All other hyperparams identical to combined+modReLU baseline.

Expected fingerprint per Titans diagnostic:
- alpha=0.0: probably ~2.55 (W alone, ~0.605 top-1 W readout accuracy)
- alpha=0.3: 2.4994 (baseline, pool+W blend)
- alpha=1.0: probably much worse (pool top-1 0.437 alone is much worse than W's 0.605)

If alpha=0.0 is close to 2.4994, the pool is barely contributing and pool-mechanism
work is low ceiling. If alpha=0.0 is much worse, the pool is critical.
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
DECAY = 1e-4
MAX_EPOCHS = 15
EPOCH_CHECKPOINTS = [1, 5, 10, 15]
RELU_B = 0.5

ALPHA_VALUES = [0.0, 0.1, 0.3, 0.5, 0.7, 1.0]


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


def run_config(alpha, train, test):
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
                ctxs = _build_context_bundles_batch(byte_atoms, pos_atoms, idx_batch)
                P_W = _predict_W_batch(W, ctxs, byte_atoms, BETA)
                targets = byte_atoms[tgt_batch]
                expected = P_W.T.to(byte_atoms.dtype) @ byte_atoms
                errors = targets - expected
                dW = errors.T @ ctxs.conj() / N
                if DECAY > 0:
                    W.mul_(1.0 - DECAY)
                W.add_(dW, alpha=AROUSAL)
                if epoch == 1:
                    dest = (pool_idx + arange_b[:B]) % POOL_SIZE
                    pool_vecs.index_copy_(0, dest, ctxs)
                    pool_labels.index_copy_(0, dest, tgt_batch)
                    pool_idx = (pool_idx + B) % POOL_SIZE
                    pool_used = min(pool_used + B, POOL_SIZE)
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
                    P = alpha * P_retr + (1.0 - alpha) * P_W
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
                history.append({"epoch": epoch, "test_bpc": test_bpc,
                                "argmax_accuracy": argmax_acc,
                                "pool_top1_acc": pool_acc, "w_top1_acc": w_acc,
                                "wall_s": elapsed})
                _say(f"    [alpha={alpha}] ep={epoch}  bpc={test_bpc:.4f}  arg={argmax_acc:.4f}  "
                     f"poolT1={pool_acc:.3f}  wT1={w_acc:.3f}  ({elapsed:.1f}s)")
        return {"alpha": alpha, "history": history}


def main() -> None:
    _say("Loading corpus...")
    corpus = load_corpus()
    cut = int(len(corpus) * 0.8)
    train, test = corpus[:cut], corpus[cut:]
    _say(f"  train={len(train)}, test={len(test)} bytes")
    _say(f"\nalpha sweep on combined+modReLU baseline (rehab from Titans rejection)")
    _say(f"  N={N}, K={K}, arousal={AROUSAL}, beta={BETA}, decay={DECAY}, pool={POOL_SIZE}, relu_b={RELU_B}")
    _say(f"  alpha values: {ALPHA_VALUES}")
    _say(f"  Reference: alpha=0.3 baseline = 2.4994")
    _say(f"  Question: how much is the pool actually contributing?")

    all_results = []
    t_all = time.perf_counter()
    for alpha in ALPHA_VALUES:
        _say(f"\n--- alpha = {alpha} ---")
        t0 = time.perf_counter()
        r = run_config(alpha, train, test)
        r["wall_time_s"] = time.perf_counter() - t0
        all_results.append(r)
        best = min(r["history"], key=lambda h: h["test_bpc"])
        _say(f"  Best for alpha={alpha}: ep={best['epoch']}, bpc={best['test_bpc']:.4f}")

    _say(f"\n========= SUMMARY =========")
    _say(f"{'alpha':>5s} {'best_ep':>8s} {'best_bpc':>10s} {'wT1':>6s} {'poolT1':>7s}")
    for r in all_results:
        best = min(r["history"], key=lambda h: h["test_bpc"])
        _say(f"{r['alpha']:>5.2f} {best['epoch']:>8d} {best['test_bpc']:>10.4f} "
             f"{best['w_top1_acc']:>6.3f} {best['pool_top1_acc']:>7.3f}")

    out = {"seed": SEED, "n": N, "k": K, "arousal": AROUSAL, "beta": BETA, "decay": DECAY,
           "pool_size": POOL_SIZE, "relu_b": RELU_B, "max_epochs": MAX_EPOCHS,
           "alpha_values": ALPHA_VALUES, "results": all_results,
           "wall_time_total_s": time.perf_counter() - t_all}
    out_path = Path(__file__).resolve().parent.parent / "data" / "exp_alpha_sweep_charlm"
    out_path.mkdir(parents=True, exist_ok=True)
    (out_path / "metrics.json").write_text(json.dumps(out, indent=2, default=str))
    _say(f"\nWrote {out_path / 'metrics.json'}")


if __name__ == "__main__":
    main()
