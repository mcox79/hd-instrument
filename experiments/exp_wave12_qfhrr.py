"""Wave 12: qFHRR — 4-bit quantized-phase FHRR.

Audit recommendation (substrate dive, 2026-05-18): cheap exploration that
quantizes FHRR phases to 4 bits per dimension (16 discrete phase angles).
Memory drops by ~16x; arithmetic stays similar; phase precision drops.

Citation: arXiv 2604.25939 *qFHRR: quantized-phase FHRR for memory-efficient
HDC*. Reports phase quantization to 3-4 bits/dim with minimal accuracy
degradation in classification tasks. We test it on byte-LM.

Mechanism:
- Atom = (cos(phase), sin(phase)) where phase ∈ {0, 2π/16, 4π/16, ..., 30π/16}
- Equivalently: pick one of 16 discrete unit-magnitude complex numbers per dim
- Binding = elementwise complex multiply (output may not be on the quantized grid
  but we re-quantize at READ TIME if we want; bound atoms can live continuous)
- Cleanup = standard FHRR cleanup
- Storage = 4 bits/dim instead of 64 bits (complex64) → 16x smaller

Variants:
- Q4: 4 bits/dim (16 phase levels) — the paper's main recipe
- Q5: 5 bits/dim (32 levels) — finer
- Q3: 3 bits/dim (8 levels) — coarser stress test
- Q1: 1 bit/dim (2 levels: ±1 only) — extreme; collapses to MAP/BSC-like

Expected: minimal bpc drift (~0.005-0.02 worse than full FHRR) with huge
memory savings. Could enable wider N at same RAM.

Falsification criterion: if Q4 is more than 0.05 bpc worse than FHRR
baseline (2.4994 at N=4096), the audit's "minimal accuracy degradation"
claim doesn't transfer to byte-LM at our scale.
"""

from __future__ import annotations

import json
import math
import time
from pathlib import Path

import torch


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
EVAL_AT = [5, 15]
RELU_B = 0.5

# Bits per dimension to test
BITS_VARIANTS = [4, 5, 3, 1]  # 4 first as the recommended setting


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


def make_qfhrr_atoms(k, n, bits, gen):
    """Generate k FHRR atoms with phases quantized to 2^bits levels."""
    n_levels = 2 ** bits
    # Sample uniformly from {0, 1, ..., n_levels-1}
    discrete = torch.randint(0, n_levels, (k, n), generator=gen)
    # Map to phase angles
    phases = (discrete.float() / n_levels) * (2.0 * math.pi)
    return torch.complex(torch.cos(phases), torch.sin(phases)).to(torch.complex64)


def build_ctx_bundles(byte_atoms, pos_atoms, indices):
    bound = byte_atoms[indices] * pos_atoms.unsqueeze(0)
    summed = bound.sum(dim=1)
    mag = summed.abs().clamp(min=1e-8)
    return summed / mag.to(summed.dtype)


def magnitude_relu(q, b):
    eps = 1e-9
    mag = q.abs().clamp(min=eps)
    new_mag = torch.clamp(mag - b, min=0.0)
    return q * (new_mag / mag).to(q.dtype)


def predict_W(W, ctxs, byte_atoms, beta):
    n = ctxs.shape[1]
    q = ctxs @ W.T
    q = magnitude_relu(q, RELU_B)
    sims = (byte_atoms.conj() @ q.T).real / n
    return torch.softmax(beta * sims, dim=0)


def predict_pool(ctxs, pool_vecs, pool_labels, pool_used, beta):
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


def run_variant(bits, train, test):
    gen = torch.Generator().manual_seed(SEED)
    byte_atoms = make_qfhrr_atoms(VOCAB_SIZE, N, bits, gen).to(DEVICE)
    pos_atoms = make_qfhrr_atoms(K, N, bits, gen).to(DEVICE)
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
            ctxs = build_ctx_bundles(byte_atoms, pos_atoms, idx_batch)
            P_W = predict_W(W, ctxs, byte_atoms, BETA)
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
        if epoch in EVAL_AT:
            total_bits = 0.0
            argmax_correct = 0
            for bs in range(0, T_test, BATCH_SIZE):
                be = min(bs + BATCH_SIZE, T_test)
                ctxs = build_ctx_bundles(byte_atoms, pos_atoms, test_idx[bs:be])
                P_W = predict_W(W, ctxs, byte_atoms, BETA)
                P_retr = predict_pool(ctxs, pool_vecs, pool_labels, pool_used, BETA)
                P = ALPHA * P_retr + (1.0 - ALPHA) * P_W
                tgts = test_targets[bs:be]
                p_true = P.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)
                total_bits += float(-torch.log2(p_true).sum())
                argmax_correct += int((P.argmax(dim=0) == tgts).sum())
            test_bpc = total_bits / max(T_test, 1)
            argmax_acc = argmax_correct / max(T_test, 1)
            elapsed = time.perf_counter() - t_start
            history.append({"epoch": epoch, "test_bpc": test_bpc, "argmax_accuracy": argmax_acc,
                            "wall_s": elapsed})
            _say(f"    [Q{bits}] ep={epoch}  bpc={test_bpc:.4f}  arg={argmax_acc:.4f}  ({elapsed:.1f}s)")
    return {"bits": bits, "history": history}


def main() -> None:
    _say("Loading corpus...")
    corpus = load_corpus()
    cut = int(len(corpus) * 0.8)
    train, test = corpus[:cut], corpus[cut:]
    _say(f"  train={len(train)}, test={len(test)} bytes")
    _say(f"\nWave 12: qFHRR phase-quantization sweep")
    _say(f"  N={N}, K={K}, bits_variants={BITS_VARIANTS}")
    _say(f"  Reference (full FHRR complex64): 2.4994")
    _say(f"  Lit: arXiv 2604.25939 qFHRR")
    _say(f"  Hypothesis: Q4 (16 phase levels) within 0.02 bpc of full FHRR")

    all_results = []
    t_all = time.perf_counter()
    for bits in BITS_VARIANTS:
        _say(f"\n--- Q{bits} ({2**bits} phase levels) ---")
        r = run_variant(bits, train, test)
        all_results.append(r)
        best = min(r["history"], key=lambda h: h["test_bpc"])
        _say(f"  Best Q{bits}: ep={best['epoch']}, bpc={best['test_bpc']:.4f}")

    _say(f"\n========= SUMMARY =========")
    _say(f"{'bits':>5s} {'levels':>7s} {'best_bpc':>10s} {'delta_vs_FHRR':>15s}")
    for r in all_results:
        best = min(r["history"], key=lambda h: h["test_bpc"])["test_bpc"]
        delta = best - 2.4994
        _say(f"{r['bits']:>5d} {2**r['bits']:>7d} {best:>10.4f} {delta:>+15.4f}")

    out = {"seed": SEED, "n": N, "k": K, "bits_variants": BITS_VARIANTS,
           "max_epochs": MAX_EPOCHS, "results": all_results,
           "wall_time_total_s": time.perf_counter() - t_all}
    out_path = Path(__file__).resolve().parent.parent / "data" / "exp_wave12_qfhrr"
    out_path.mkdir(parents=True, exist_ok=True)
    (out_path / "metrics.json").write_text(json.dumps(out, indent=2, default=str))
    _say(f"\nWrote {out_path / 'metrics.json'}")


if __name__ == "__main__":
    main()
