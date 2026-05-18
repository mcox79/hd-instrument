"""Wave 10 Phase A: 2-layer Hebbian feedforward.

Per the design doc (notes/wave10_rgflow_design.md), Phase A is the
simplest test: does adding a second delta-rule-trained W layer help at
all? Each layer trained locally (no gradient flow through Layer 0 from
Layer 1's error).

Architecture (built on the BSC substrate, our current best at 2.4817):
- Layer 0: standard BSC ctx → W_0 → modReLU → hidden h
- Layer 1: hidden h → W_1 → modReLU → second prediction
- Each layer independently delta-rule-trained on the same byte target
- Test prediction: ALPHA_layer · P_W1 + (1-ALPHA_layer) · P_W0 + ALPHA · P_pool

Hyperparams: ALPHA_layer ∈ {0.0, 0.3, 0.5, 0.7, 1.0} sweep.
ALPHA_layer=0.0 reproduces single-layer baseline.
ALPHA_layer=1.0 uses only Layer 1.

Falsification: best 2-layer variant ≤ 2.43 bpc → support.
Within ±0.02 of 2.4817 → reject (depth doesn't help at our scale).
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import torch


torch.set_float32_matmul_precision("high")

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
ALPHA_POOL = 0.3
DECAY = 1e-4
MAX_EPOCHS = 15
EVAL_AT = [5, 15]
RELU_B = 0.5

ALPHA_LAYER_SWEEP = [0.0, 0.3, 0.5, 0.7, 1.0]


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


def build_ctx_bundles(byte_atoms, pos_atoms, indices):
    bound = byte_atoms[indices] * pos_atoms.unsqueeze(0)
    summed = bound.sum(dim=1)
    out = torch.sign(summed)
    return torch.where(out == 0, torch.ones_like(out), out)


def shifted_relu(q, b):
    return torch.clamp(q - b, min=0.0)


def predict_W_layer(W, x, byte_atoms, beta, n):
    """W readout + ReLU + similarity softmax (BSC-style)."""
    q = x @ W.T
    q = shifted_relu(q, RELU_B)
    sims = (byte_atoms @ q.T) / n
    return torch.softmax(beta * sims, dim=0), q


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


def run_variant(alpha_layer, train, test):
    gen = torch.Generator().manual_seed(SEED)
    byte_atoms = make_bsc_atoms(VOCAB_SIZE, N, gen).to(DEVICE)
    pos_atoms = make_bsc_atoms(K, N, gen).to(DEVICE)
    W0 = torch.zeros((N, N), dtype=torch.float32, device=DEVICE)
    W1 = torch.zeros((N, N), dtype=torch.float32, device=DEVICE)
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
            ctxs = build_ctx_bundles(byte_atoms, pos_atoms, idx_batch)

            # Layer 0 forward + train
            P_W0, h = predict_W_layer(W0, ctxs, byte_atoms, BETA, N)
            targets = byte_atoms[tgt_batch]
            expected_0 = P_W0.T @ byte_atoms
            errors_0 = targets - expected_0
            dW0 = errors_0.T @ ctxs / N
            if DECAY > 0:
                W0.mul_(1.0 - DECAY)
            W0.add_(dW0, alpha=AROUSAL)

            # Layer 1 forward + train on h (frozen w.r.t. Layer 0)
            # h is the modReLU'd readout from Layer 0; treat it as Layer 1's input
            h_detached = h.detach()
            P_W1, _ = predict_W_layer(W1, h_detached, byte_atoms, BETA, N)
            expected_1 = P_W1.T @ byte_atoms
            errors_1 = targets - expected_1
            dW1 = errors_1.T @ h_detached / N
            if DECAY > 0:
                W1.mul_(1.0 - DECAY)
            W1.add_(dW1, alpha=AROUSAL)

            if epoch == 1:
                dest = (pool_idx + arange_b[:B]) % POOL_SIZE
                pool_vecs.index_copy_(0, dest, ctxs)
                pool_labels.index_copy_(0, dest, tgt_batch)
                pool_idx = (pool_idx + B) % POOL_SIZE
                pool_used = min(pool_used + B, POOL_SIZE)
        if epoch in EVAL_AT:
            total_bits = 0.0
            argmax_correct = 0
            for bs in range(0, T_test, BATCH_SIZE):
                be = min(bs + BATCH_SIZE, T_test)
                ctxs = build_ctx_bundles(byte_atoms, pos_atoms, test_idx[bs:be])
                P_W0, h = predict_W_layer(W0, ctxs, byte_atoms, BETA, N)
                P_W1, _ = predict_W_layer(W1, h, byte_atoms, BETA, N)
                P_W_combined = alpha_layer * P_W1 + (1.0 - alpha_layer) * P_W0
                P_retr = predict_pool(ctxs, pool_vecs, pool_labels, pool_used, BETA, N)
                P = ALPHA_POOL * P_retr + (1.0 - ALPHA_POOL) * P_W_combined
                tgts = test_targets[bs:be]
                p_true = P.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)
                total_bits += float(-torch.log2(p_true).sum())
                argmax_correct += int((P.argmax(dim=0) == tgts).sum())
            test_bpc = total_bits / max(T_test, 1)
            argmax_acc = argmax_correct / max(T_test, 1)
            elapsed = time.perf_counter() - t_start
            history.append({"epoch": epoch, "test_bpc": test_bpc,
                            "argmax_accuracy": argmax_acc, "wall_s": elapsed})
            _say(f"    [alpha_layer={alpha_layer}] ep={epoch}  bpc={test_bpc:.4f}  arg={argmax_acc:.4f}  ({elapsed:.1f}s)")
    return {"alpha_layer": alpha_layer, "history": history}


def main() -> None:
    _say("Loading corpus...")
    corpus = load_corpus()
    cut = int(len(corpus) * 0.8)
    train, test = corpus[:cut], corpus[cut:]
    _say(f"  train={len(train)}, test={len(test)} bytes")
    _say(f"\nWave 10 Phase A: 2-layer Hebbian feedforward")
    _say(f"  Substrate: BSC (our current best at 2.4817)")
    _say(f"  N={N}, K={K}, alpha_layer sweep: {ALPHA_LAYER_SWEEP}")
    _say(f"  alpha_layer=0 reproduces single-layer baseline")
    _say(f"  alpha_layer=1 uses Layer 1 only")
    _say(f"  Layer 1 trains on detached Layer 0 output (no backprop through Layer 0)")

    all_results = []
    t_all = time.perf_counter()
    for alpha_layer in ALPHA_LAYER_SWEEP:
        _say(f"\n--- alpha_layer = {alpha_layer} ---")
        r = run_variant(alpha_layer, train, test)
        all_results.append(r)
        best = min(r["history"], key=lambda h: h["test_bpc"])
        _say(f"  Best: ep={best['epoch']}, bpc={best['test_bpc']:.4f}")

    _say(f"\n========= SUMMARY =========")
    _say(f"{'alpha_layer':>12s} {'best_bpc':>10s} {'delta_vs_BSC':>14s}")
    for r in all_results:
        best = min(r["history"], key=lambda h: h["test_bpc"])["test_bpc"]
        delta = best - 2.4817
        _say(f"{r['alpha_layer']:>12.2f} {best:>10.4f} {delta:>+14.4f}")

    out = {"seed": SEED, "n": N, "k": K, "alpha_layer_sweep": ALPHA_LAYER_SWEEP,
           "results": all_results,
           "wall_time_total_s": time.perf_counter() - t_all}
    out_path = Path(__file__).resolve().parent.parent / "data" / "exp_wave10_rgflow_phaseA"
    out_path.mkdir(parents=True, exist_ok=True)
    (out_path / "metrics.json").write_text(json.dumps(out, indent=2, default=str))
    _say(f"\nWrote {out_path / 'metrics.json'}")


if __name__ == "__main__":
    main()
