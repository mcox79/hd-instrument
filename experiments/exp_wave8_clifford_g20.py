"""Wave 8: Clifford / Geometric Algebra VSA — G(2,0) prototype.

TOP-PICK from the substrate audit (2026-05-18). The audit's headline:
"The Fourier transformation you're missing is the Clifford-Fourier transform
on a geometric algebra (not a re-skin of FHRR)."

Substrate design (G(2,0), the simplest non-trivial Clifford algebra):

A G(2,0) multivector has 4 components: (s, v1, v2, b) representing
    s + v1*e1 + v2*e2 + b*e1e2
where e1, e2 are basis vectors with e1^2 = e2^2 = +1, e1*e2 = -e2*e1 = e1e2.

For HDC at N=4096, stack 1024 independent G(2,0) multivectors → 4096-dim
total. Each "slot" is a 4-tuple. Binding is the geometric product applied
independently per slot. The geometric product is NON-COMMUTATIVE: e1*e2
≠ e2*e1. This gives us sequence order natively (no separate position
encoding needed if we leverage it).

Geometric product on G(2,0) per slot:
    (a + b*e1 + c*e2 + d*e1e2) * (e + f*e1 + g*e2 + h*e1e2)
   = (ae + bf + cg - dh)          [scalar part]
   + (af + be + ch - dg)*e1       [e1 part]
   + (ag + bh + ce - df)*e2       [e2 part]
   + (ah + bg - cf + de)*e1e2     [bivector part]

The bivector e1e2 squares to -1, so it acts like an imaginary unit within
each slot. This generalizes FHRR (which is roughly G(0,1) = complex numbers)
to a richer algebra with non-commutativity.

Citation:
- Ruhe et al. 2023 *Clifford Group Equivariant Neural Networks* (arXiv 2305.11141, NeurIPS 2023)
- Brandstetter et al. 2023 *Geometric Clifford Algebra Networks* (PMLR 202)
- Aerts/Czachor *Geometric Algebra representation of Binary Spatter Codes*
  (historical: shows BSC is degenerate Clifford over GF(2))

Audit estimate: 0.2-0.4 bpc improvement if grades behave like attention
heads, 2-week implementation cost.

This is a CPU-friendly prototype. Larger Clifford algebras (G(4,1) for
conformal geometry, G(3,1) for spacetime) are the natural extensions but
require ~4x more parameters per slot.

Falsification: Best Clifford variant within ±0.05 bpc of FHRR (2.4994) →
the audit's "grades act as multi-heads" claim doesn't pay off at our
scale. Best Clifford ≤ 2.44 → strong support; closes most of the gap to
the tiny-transformer baseline.
"""

from __future__ import annotations

import json
import math
import time
from pathlib import Path

import torch


torch.set_float32_matmul_precision("high")

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
SEED = 17
N_TOTAL = 4096
SLOT_DIM = 4  # G(2,0): scalar + 2 vectors + 1 bivector
N_SLOTS = N_TOTAL // SLOT_DIM  # = 1024
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


def make_clifford_atoms(k, n_slots, gen):
    """Generate k Clifford G(2,0) atoms, normalized to L2-unit per slot.

    Returns (k, n_slots, 4) real tensor.
    """
    raw = torch.randn((k, n_slots, SLOT_DIM), generator=gen)
    # Normalize each slot to unit L2 norm
    norms = raw.norm(dim=-1, keepdim=True).clamp(min=1e-8)
    return raw / norms


def clifford_geometric_product(a, b):
    """Per-slot geometric product on G(2,0).

    a, b: (..., n_slots, 4) tensors.
    Returns: (..., n_slots, 4) tensor with the geometric product per slot.
    """
    a0, a1, a2, a3 = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    b0, b1, b2, b3 = b[..., 0], b[..., 1], b[..., 2], b[..., 3]
    # G(2,0) Cayley table:
    # 1*1=1, e1^2=1, e2^2=1, (e1e2)^2=-1
    # e1*e2=e1e2, e2*e1=-e1e2
    # e1*(e1e2)=e2, (e1e2)*e1=-e2
    # e2*(e1e2)=-e1, (e1e2)*e2=e1
    c0 = a0 * b0 + a1 * b1 + a2 * b2 - a3 * b3
    c1 = a0 * b1 + a1 * b0 + a3 * b2 - a2 * b3
    c2 = a0 * b2 + a2 * b0 + a1 * b3 - a3 * b1
    c3 = a0 * b3 + a3 * b0 + a1 * b2 - a2 * b1
    return torch.stack([c0, c1, c2, c3], dim=-1)


def build_ctx_bundles_clifford(byte_atoms, pos_atoms, indices):
    """Bind byte_atoms[indices] with pos_atoms (per K), bundle by sum + normalize.

    byte_atoms: (V, n_slots, 4)
    pos_atoms:  (K, n_slots, 4)
    indices:    (B, K) long
    Returns: (B, n_slots, 4) bundled context.
    """
    # Gather byte atoms used: (B, K, n_slots, 4)
    byte_used = byte_atoms[indices]
    # Broadcast pos atoms: (1, K, n_slots, 4)
    pos_b = pos_atoms.unsqueeze(0)
    # Bind per (b, k, slot)
    bound = clifford_geometric_product(byte_used, pos_b)  # (B, K, n_slots, 4)
    # Bundle: sum over K, then per-slot L2 normalize
    summed = bound.sum(dim=1)  # (B, n_slots, 4)
    norms = summed.norm(dim=-1, keepdim=True).clamp(min=1e-8)
    return summed / norms


def shifted_relu(q, b):
    """Apply ReLU to L2 norm of each slot, preserving direction."""
    n_slots = q.shape[-2]
    norms = q.norm(dim=-1, keepdim=True).clamp(min=1e-9)
    new_norms = torch.clamp(norms - b, min=0.0)
    return q * (new_norms / norms)


def predict_W_clifford(W, ctxs, byte_atoms, beta, n_total):
    """W readout via flattened matmul + slot-wise ReLU + codebook similarity.

    W is (N_TOTAL, N_TOTAL) real-valued. ctxs flattened to (B, N_TOTAL).
    """
    B = ctxs.shape[0]
    ctxs_flat = ctxs.reshape(B, n_total)
    q_flat = ctxs_flat @ W.T  # (B, N_TOTAL)
    q = q_flat.reshape(B, N_SLOTS, SLOT_DIM)
    q = shifted_relu(q, RELU_B)
    # Similarity: inner product (treating each slot as a 4-vector)
    # sims[v, b] = sum_slot <byte_v_slot, q_b_slot> / N_SLOTS
    byte_flat = byte_atoms.reshape(VOCAB_SIZE, n_total)
    q_flat = q.reshape(B, n_total)
    sims = (byte_flat @ q_flat.T) / n_total
    return torch.softmax(beta * sims, dim=0)


def predict_pool_clifford(ctxs, pool_vecs, pool_labels, pool_used, beta, n_total):
    B = ctxs.shape[0]
    if pool_used == 0:
        return torch.full((VOCAB_SIZE, B), 1.0 / VOCAB_SIZE, device=ctxs.device)
    ctxs_flat = ctxs.reshape(B, n_total)
    active = pool_vecs[:pool_used]
    labels = pool_labels[:pool_used]
    sims = (active @ ctxs_flat.T) / n_total
    weights = torch.softmax(beta * sims, dim=0)
    P_retr = torch.zeros(VOCAB_SIZE, B, device=ctxs.device)
    P_retr.scatter_add_(0, labels.unsqueeze(1).expand(-1, B), weights)
    return P_retr


def main() -> None:
    _say("Loading corpus...")
    corpus = load_corpus()
    cut = int(len(corpus) * 0.8)
    train, test = corpus[:cut], corpus[cut:]
    _say(f"  train={len(train)}, test={len(test)} bytes")
    _say(f"\nWave 8: Clifford G(2,0) VSA prototype")
    _say(f"  N_TOTAL={N_TOTAL}, N_SLOTS={N_SLOTS}, SLOT_DIM={SLOT_DIM}")
    _say(f"  K={K}, arousal={AROUSAL}, beta={BETA}, decay={DECAY}, pool={POOL_SIZE}, relu_b={RELU_B}")
    _say(f"  Reference (FHRR combined+modReLU at N=4096): 2.4994")
    _say(f"  Reference (BSC signed+ReLU at N=4096): 2.4817")
    _say(f"  Audit prediction: 0.2-0.4 bpc gain if grades behave like multi-heads")
    _say(f"  Geometric product is non-commutative -> sequence order is natively free")

    gen = torch.Generator().manual_seed(SEED)
    byte_atoms = make_clifford_atoms(VOCAB_SIZE, N_SLOTS, gen).to(DEVICE)  # (V, S, 4)
    pos_atoms = make_clifford_atoms(K, N_SLOTS, gen).to(DEVICE)              # (K, S, 4)
    W = torch.zeros((N_TOTAL, N_TOTAL), dtype=torch.float32, device=DEVICE)
    pool_vecs = torch.zeros((POOL_SIZE, N_TOTAL), dtype=torch.float32, device=DEVICE)
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
            ctxs = build_ctx_bundles_clifford(byte_atoms, pos_atoms, idx_batch)  # (B, S, 4)
            P_W = predict_W_clifford(W, ctxs, byte_atoms, BETA, N_TOTAL)
            # Hebbian delta update on W
            targets_flat = byte_atoms[tgt_batch].reshape(B, N_TOTAL)
            byte_flat = byte_atoms.reshape(VOCAB_SIZE, N_TOTAL)
            expected = P_W.T @ byte_flat  # (B, V) @ (V, N) = (B, N)
            errors = targets_flat - expected
            ctxs_flat = ctxs.reshape(B, N_TOTAL)
            dW = errors.T @ ctxs_flat / N_TOTAL
            if DECAY > 0:
                W.mul_(1.0 - DECAY)
            W.add_(dW, alpha=AROUSAL)
            if epoch == 1:
                dest = (pool_idx + arange_b[:B]) % POOL_SIZE
                pool_vecs.index_copy_(0, dest, ctxs_flat)
                pool_labels.index_copy_(0, dest, tgt_batch)
                pool_idx = (pool_idx + B) % POOL_SIZE
                pool_used = min(pool_used + B, POOL_SIZE)
        if epoch in EVAL_AT:
            total_bits = 0.0
            argmax_correct = 0
            for bs in range(0, T_test, BATCH_SIZE):
                be = min(bs + BATCH_SIZE, T_test)
                ctxs = build_ctx_bundles_clifford(byte_atoms, pos_atoms, test_idx[bs:be])
                P_W = predict_W_clifford(W, ctxs, byte_atoms, BETA, N_TOTAL)
                P_retr = predict_pool_clifford(ctxs, pool_vecs, pool_labels, pool_used, BETA, N_TOTAL)
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
                            "argmax_accuracy": argmax_acc, "w_frob": w_frob, "wall_s": elapsed})
            _say(f"    epoch={epoch}  bpc={test_bpc:.4f}  arg={argmax_acc:.4f}  ||W||={w_frob:.1f}  ({elapsed:.1f}s)")

    _say(f"\n========= SUMMARY =========")
    best = min(history, key=lambda h: h["test_bpc"])
    _say(f"  Best Clifford G(2,0): ep={best['epoch']}, bpc={best['test_bpc']:.4f}")
    _say(f"  vs FHRR baseline (2.4994): delta = {best['test_bpc'] - 2.4994:+.4f}")
    _say(f"  vs BSC best (2.4817): delta = {best['test_bpc'] - 2.4817:+.4f}")

    out = {"seed": SEED, "n_total": N_TOTAL, "n_slots": N_SLOTS, "slot_dim": SLOT_DIM,
           "k": K, "arousal": AROUSAL, "beta": BETA, "decay": DECAY,
           "pool_size": POOL_SIZE, "alpha": ALPHA, "relu_b": RELU_B,
           "history": history,
           "wall_time_total_s": time.perf_counter() - t_start}
    out_path = Path(__file__).resolve().parent.parent / "data" / "exp_wave8_clifford_g20"
    out_path.mkdir(parents=True, exist_ok=True)
    (out_path / "metrics.json").write_text(json.dumps(out, indent=2, default=str))
    _say(f"\nWrote {out_path / 'metrics.json'}")


if __name__ == "__main__":
    main()
