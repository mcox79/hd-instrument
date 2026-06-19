"""PFC working-memory attractor: persistent state hypervector (BR4).

Prefrontal cortex maintains stable activity over delays via recurrent attractor
dynamics (Goldman-Rakic 1995; Wang 2001 *Trends Neurosci*). This is *activity-based*
memory, distinct from synaptic memory in W or stored memory in the pool.

We add a persistent hypervector h_t that carries an exponential moving average
of recent context. It's bound with a "memory role" atom and added to each
context bundle, giving W a chance to learn from both the recent K bytes AND
the long-running EMA summary.

Update rule (each batch):
  h_t = H_ALPHA * h_{t-1} + (1 - H_ALPHA) * last_ctx_of_batch

Bundle augmentation:
  ctx_augmented = normalize(bundle_of_K_bytes + bind(h_normalized, memory_role))

Stacked with magnitude_relu (current best). Baseline: 2.4994 bpc.
"""

from __future__ import annotations

import json
import math
import time
from collections import Counter
from pathlib import Path

import torch

from hdlab import atoms, binding, tracing


DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
SEED = 17
N_SUBSTRATE = 4096
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
EPOCH_CHECKPOINTS = [1, 3, 5, 7, 10, 12, 15]
RELU_B = 0.5
H_ALPHA = 0.95  # EMA decay for persistent state h


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


def train_test_split(corpus, train_frac=0.8):
    cut = int(len(corpus) * train_frac)
    return corpus[:cut], corpus[cut:]


def _build_context_with_h(byte_atoms, pos_atoms, m_role, h, indices):
    """Context bundle including persistent state h bound to memory role."""
    bound_pos = byte_atoms[indices] * pos_atoms.unsqueeze(0)  # (B, K, N)
    summed_pos = bound_pos.sum(dim=1)  # (B, N)
    # Bind h with its role atom
    h_bound = h * m_role  # (N,) — elementwise complex mul = bind
    summed = summed_pos + h_bound.unsqueeze(0)  # (B, N)
    mag = summed.abs().clamp(min=1e-8)
    return summed / mag.to(summed.dtype)


def magnitude_relu(q: torch.Tensor, b: float) -> torch.Tensor:
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


def main() -> None:
    _say("Loading corpus...")
    corpus = load_corpus()
    train, test = train_test_split(corpus, 0.8)
    _say(f"  train={len(train)}, test={len(test)} bytes")
    _say(f"\nConfig: N={N_SUBSTRATE}, K={K}, arousal={AROUSAL}, beta={BETA}, decay={DECAY}")
    _say(f"        Persistent state h: H_ALPHA={H_ALPHA}")
    _say(f"        Dendritic relu b={RELU_B}")
    _say(f"        epochs={MAX_EPOCHS}, checkpoints {EPOCH_CHECKPOINTS}")
    _say(f"\nBaseline: combined + relu (no h) = 2.4994 bpc")

    quiet = tracing.TraceBus(enabled=False)
    with tracing.using(quiet):
        gen = torch.Generator().manual_seed(SEED)
        byte_atoms = torch.stack([atoms.make_atom_fhrr(N_SUBSTRATE, gen) for _ in range(VOCAB_SIZE)]).to(DEVICE)
        pos_atoms = torch.stack([atoms.make_atom_fhrr(N_SUBSTRATE, gen) for _ in range(K)]).to(DEVICE)
        m_role = atoms.make_atom_fhrr(N_SUBSTRATE, gen).to(DEVICE)  # memory role atom
        W = torch.zeros((N_SUBSTRATE, N_SUBSTRATE), dtype=torch.complex64, device=DEVICE)
        pool_vecs = torch.zeros((POOL_SIZE, N_SUBSTRATE), dtype=torch.complex64, device=DEVICE)
        pool_labels = torch.zeros(POOL_SIZE, dtype=torch.long, device=DEVICE)
        pool_used = 0
        pool_idx = 0
        h = torch.zeros(N_SUBSTRATE, dtype=torch.complex64, device=DEVICE)

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
                # Build context with h injected.
                h_norm = h / h.abs().clamp(min=1e-8).to(h.dtype) if epoch > 1 or batch_start > 0 else h
                ctxs = _build_context_with_h(byte_atoms, pos_atoms, m_role, h_norm, idx_batch)
                P_W = _predict_W_batch(W, ctxs, byte_atoms, BETA)
                targets = byte_atoms[tgt_batch]
                expected = P_W.T.to(byte_atoms.dtype) @ byte_atoms
                errors = targets - expected
                dW = errors.T @ ctxs.conj() / N_SUBSTRATE
                if DECAY > 0:
                    W.mul_(1.0 - DECAY)
                W.add_(dW, alpha=AROUSAL)
                if epoch == 1:
                    for b in range(B):
                        pool_vecs[pool_idx] = ctxs[b]
                        pool_labels[pool_idx] = tgt_batch[b]
                        pool_idx = (pool_idx + 1) % POOL_SIZE
                        pool_used = min(pool_used + 1, POOL_SIZE)
                # Update persistent state h with last context in batch.
                h = H_ALPHA * h + (1.0 - H_ALPHA) * ctxs[-1]
            if epoch in EPOCH_CHECKPOINTS:
                # Evaluate with current h (carried over from training).
                h_eval = h.clone()
                total_bits = 0.0
                argmax_correct = 0
                for bs in range(0, T_test, BATCH_SIZE):
                    be = min(bs + BATCH_SIZE, T_test)
                    h_norm = h_eval / h_eval.abs().clamp(min=1e-8).to(h_eval.dtype)
                    ctxs = _build_context_with_h(byte_atoms, pos_atoms, m_role, h_norm, test_idx[bs:be])
                    P_W = _predict_W_batch(W, ctxs, byte_atoms, BETA)
                    P_retr = _predict_pool_batch(ctxs, pool_vecs, pool_labels, pool_used, BETA)
                    P = ALPHA * P_retr + (1.0 - ALPHA) * P_W
                    p_true = P.gather(0, test_targets[bs:be].unsqueeze(0)).squeeze(0).clamp(min=1e-12)
                    total_bits += float(-torch.log2(p_true).sum())
                    argmax_pred = P.argmax(dim=0)
                    argmax_correct += int((argmax_pred == test_targets[bs:be]).sum())
                    # Update h_eval during eval to track state as test stream proceeds.
                    h_eval = H_ALPHA * h_eval + (1.0 - H_ALPHA) * ctxs[-1]
                test_bpc = total_bits / max(T_test, 1)
                argmax_acc = argmax_correct / max(T_test, 1)
                w_norm = float(W.abs().pow(2).sum().sqrt())
                h_norm_val = float(h.abs().mean())
                elapsed = time.perf_counter() - t_start
                history.append({"epoch": epoch, "test_bpc": test_bpc, "argmax_accuracy": argmax_acc, "w_frobenius": w_norm, "h_mean_mag": h_norm_val, "wall_s": elapsed})
                _say(f"  epoch={epoch}  test_bpc={test_bpc:.4f}  argmax={argmax_acc:.4f}  W={w_norm:.1f}  h_mag={h_norm_val:.3f}  ({elapsed:.1f}s)")

        best = min(history, key=lambda h: h["test_bpc"])
        _say(f"\nBest: epoch={best['epoch']}  test_bpc={best['test_bpc']:.4f}")
        _say(f"  vs current best (combined + relu, 2.4994): delta {2.4994 - best['test_bpc']:+.4f}")
        _say(f"  vs transformer ceiling (2.39): gap {best['test_bpc'] - 2.39:.4f}")

        out = {
            "seed": SEED, "n_substrate": N_SUBSTRATE, "k": K, "arousal": AROUSAL, "beta": BETA,
            "pool_size": POOL_SIZE, "alpha": ALPHA, "decay": DECAY, "max_epochs": MAX_EPOCHS,
            "relu_b": RELU_B, "h_alpha": H_ALPHA,
            "history": history,
            "best": best,
            "headline": f"PFC attractor + relu + pool best test bpc = {best['test_bpc']:.3f}",
        }
        out_path = Path(__file__).resolve().parent.parent / "data" / "exp_pfc_attractor_charlm"
        out_path.mkdir(parents=True, exist_ok=True)
        (out_path / "metrics.json").write_text(json.dumps(out, indent=2, default=str))
        _say(f"\nWrote {out_path / 'metrics.json'}")


if __name__ == "__main__":
    main()
