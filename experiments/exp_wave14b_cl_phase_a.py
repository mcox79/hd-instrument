"""Wave 14.B + Continual Learning Phase A: baseline state for Phase B.

Per notes/wave14b_continual_learning_design.md.

Goal: produce a saved state (W_A, pool_A, codebooks) that Phase B's
four conditions (C0/C1/C2/C3) can pick up.

Setup:
- Corpus A: the existing repo-text byte-LM corpus (same as Wave 4.5).
- Corpus B: byte-level shuffle of corpus A. Same byte distribution,
  no local structure. Used in Phase B to overwrite W and test BWT.
- Train baseline W on corpus A using delta-rule (BSC substrate,
  N=4096) - matches the 2.4817 bpc reference.
- Save W_A, pool entries from A, codebooks (byte_atoms, pos_atoms),
  and metadata for Phase B.

This is reusing the existing Wave 4.5 BSC architecture exactly so
that Phase B can compare apples-to-apples.
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
DELTA_RULE_ALPHA = 0.3
DELTA_RULE_DECAY = 1e-4


def _say(msg: str) -> None:
    print(msg, flush=True)


def load_corpus_a() -> bytes:
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


def shuffle_bytes(data: bytes, seed: int) -> bytes:
    gen = torch.Generator().manual_seed(seed)
    n = len(data)
    perm = torch.randperm(n, generator=gen).tolist()
    out = bytearray(n)
    for i, p in enumerate(perm):
        out[i] = data[p]
    return bytes(out)


def make_bsc_atoms(k, n, gen):
    raw = torch.rand((k, n), generator=gen)
    return (2.0 * (raw > 0.5).float() - 1.0)


def build_ctx_bundles_bsc(byte_atoms, pos_atoms, indices):
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


def predict_pool(ctxs, pool_vecs, pool_labels, pool_used, beta, n):
    B = ctxs.shape[0]
    if pool_used == 0:
        return torch.full((VOCAB_SIZE, B), 1.0 / VOCAB_SIZE, device=ctxs.device)
    active = pool_vecs[:pool_used]
    labels = pool_labels[:pool_used]
    sims = (active @ ctxs.T) / n
    weights = torch.softmax(beta * sims, dim=0)
    P_retr = torch.zeros(VOCAB_SIZE, B, device=ctxs.device)
    P_retr.scatter_add_(0, labels.unsqueeze(1).expand(-1, B), weights)
    return P_retr


def train_baseline_W(byte_atoms, pos_atoms, train: bytes, test: bytes) -> dict:
    """Train W on corpus via delta rule. Returns final state for Phase B."""
    W = torch.zeros((N, N), dtype=torch.float32, device=DEVICE)
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
                w_frob = float(W.pow(2).sum().sqrt())
                elapsed = time.perf_counter() - t_start
                history.append({"epoch": epoch, "test_bpc": test_bpc,
                                "argmax_accuracy": argmax_acc, "w_frob": w_frob,
                                "wall_s": elapsed})
                _say(f"    ep={epoch}  bpc={test_bpc:.4f}  arg={argmax_acc:.4f}  ||W||={w_frob:.1f}  ({elapsed:.1f}s)")

    return {"W": W.cpu(), "pool_vecs": pool_vecs[:pool_used].cpu(),
            "pool_labels": pool_labels[:pool_used].cpu(),
            "pool_used": pool_used, "history": history}


def main() -> None:
    _say(f"Wave 14.B + CL Phase A: baseline state for Phase B")
    _say(f"  N={N}, K={K}, seed={SEED}, device={DEVICE}")

    # Corpus A: same as Wave 4.5 baseline
    corpus_a = load_corpus_a()
    _say(f"  corpus_a: {len(corpus_a)} bytes")

    # Corpus B: byte-shuffle of A
    corpus_b = shuffle_bytes(corpus_a, seed=SEED + 1)
    _say(f"  corpus_b: {len(corpus_b)} bytes (shuffled)")
    # Verify same byte distribution
    from collections import Counter
    da = Counter(corpus_a)
    db = Counter(corpus_b)
    _say(f"  byte distribution match: {da == db}")

    # Train/test split (80/20 on each)
    split_a = int(0.8 * len(corpus_a))
    train_a, test_a = corpus_a[:split_a], corpus_a[split_a:]
    split_b = int(0.8 * len(corpus_b))
    train_b, test_b = corpus_b[:split_b], corpus_b[split_b:]

    # Shared frozen codebooks (used for both phases)
    gen = torch.Generator().manual_seed(SEED)
    byte_atoms = make_bsc_atoms(VOCAB_SIZE, N, gen).to(DEVICE)
    pos_atoms = make_bsc_atoms(K, N, gen).to(DEVICE)

    _say(f"\nTraining baseline W on corpus A (delta rule, {MAX_EPOCHS} epochs)...")
    state_a = train_baseline_W(byte_atoms, pos_atoms, train_a, test_a)

    # Also evaluate W_A on corpus B test set (to know the pre-shift B perplexity)
    _say(f"\nEvaluating W_A on corpus B test set (cross-corpus baseline)...")
    with torch.no_grad():
        W_a = state_a["W"].to(DEVICE)
        pool_vecs = state_a["pool_vecs"].to(DEVICE)
        pool_labels = state_a["pool_labels"].to(DEVICE)
        pool_used = state_a["pool_used"]

        pad = bytes([PAD_BYTE]) * K
        padded_test_b = pad + test_b
        T_test = len(padded_test_b) - K
        test_b_bytes = torch.tensor(list(padded_test_b), dtype=torch.long).to(DEVICE)
        offsets = torch.arange(K - 1, -1, -1, device=DEVICE)
        pos_test = torch.arange(T_test, device=DEVICE)
        test_b_idx = test_b_bytes[pos_test.unsqueeze(1) + offsets.unsqueeze(0)]
        test_b_targets = test_b_bytes[pos_test + K]

        total_bits = 0.0
        for bs in range(0, T_test, BATCH_SIZE):
            be = min(bs + BATCH_SIZE, T_test)
            ctxs = build_ctx_bundles_bsc(byte_atoms, pos_atoms, test_b_idx[bs:be])
            P_W = predict_W(W_a, ctxs, byte_atoms, BETA, N)
            P_retr = predict_pool(ctxs, pool_vecs, pool_labels, pool_used, BETA, N)
            P = ALPHA * P_retr + (1.0 - ALPHA) * P_W
            tgts = test_b_targets[bs:be]
            p_true = P.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)
            total_bits += float(-torch.log2(p_true).sum())
        bpc_b_from_a = total_bits / max(T_test, 1)
        _say(f"  W_A on test_B: bpc={bpc_b_from_a:.4f}  (compare with future W_B on test_B)")

    # Save state
    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_cl_phase_a"
    out_dir.mkdir(parents=True, exist_ok=True)
    torch.save({
        "W_A": state_a["W"],
        "pool_vecs_A": state_a["pool_vecs"],
        "pool_labels_A": state_a["pool_labels"],
        "pool_used_A": state_a["pool_used"],
        "byte_atoms": byte_atoms.cpu(),
        "pos_atoms": pos_atoms.cpu(),
        "train_a": train_a, "test_a": test_a,
        "train_b": train_b, "test_b": test_b,
        "history_A": state_a["history"],
        "config": {"N": N, "K": K, "VOCAB_SIZE": VOCAB_SIZE, "BATCH_SIZE": BATCH_SIZE,
                  "POOL_SIZE": POOL_SIZE, "ALPHA": ALPHA, "BETA": BETA,
                  "DELTA_RULE_ALPHA": DELTA_RULE_ALPHA, "DELTA_RULE_DECAY": DELTA_RULE_DECAY,
                  "MAX_EPOCHS": MAX_EPOCHS, "SEED": SEED},
    }, out_dir / "state.pt")
    metrics = {"history_A": state_a["history"],
               "final_test_a_bpc": state_a["history"][-1]["test_bpc"],
               "W_A_on_test_B_bpc": bpc_b_from_a}
    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2, default=str))
    _say(f"\nSaved state to {out_dir}")
    _say(f"  state.pt: W_A, pool_A, codebooks, corpus splits")
    _say(f"  metrics.json: history + cross-corpus baseline")


if __name__ == "__main__":
    main()
