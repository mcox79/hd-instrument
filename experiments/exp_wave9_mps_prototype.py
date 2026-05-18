"""Wave 9: MPS-shape VSA — first prototype.

This is the SIMPLEST first cut per the design doc
(notes/wave9_mps_design.md). It uses an MPS-shape parameter vector as the
hypervector but applies FHRR-style elementwise binding. This tests
whether the MPS-shape parameter structure (L sites × d physical × χ²
bond) gives any signal over random Gaussian init at matched dim.

Full MPS-VSA with contraction-based binding is the follow-up (Wave 9.5).

Substrate design:
- L = 12 sites, d = 4 physical dim, χ = 16 bond dim
- Atom shape: (L, d, χ, χ) = (12, 4, 16, 16) = 12,288 elements
- Initialized: each site's tensor is i.i.d. Gaussian, then L2-normalized
  per site so a forward contraction at any site gives unit-norm result
- For HDC operations, the atom is treated as a flat 12,288-dim vector
- Binding: elementwise complex-style multiply (we use real here; sign-aware)
- Bundling: sum + L2 normalize
- Similarity: real inner product / N
- W: 12288 × 12288 real Hebbian-trained matrix

What we're testing: does the structured-MPS initialization (random
i.i.d. per-site tensors → flattened atom) give different bpc than a
plain random Gaussian atom at the same dimension?

Expected: NO meaningful difference. This experiment establishes a
baseline for the bigger Wave 9.5 (full MPS contraction binding).

If positive: structured init helps, push on full MPS-VSA.
If negative: it's not the shape, it's the operations. Move to Wave 9.5.

Citation: Stoudenmire & Schwab 2017 *Supervised Learning with Tensor
Networks* (NeurIPS, arXiv:1605.05775) for MPS-style ML representations;
Thomas/Smolensky 2024 *Tensor Products and HDC* (arXiv:2305.10572)
for the HDC-tensor-products connection.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import torch


torch.set_float32_matmul_precision("high")

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
SEED = 17
L_SITES = 12
PHYS_D = 4
CHI = 16
N_TOTAL = L_SITES * PHYS_D * CHI * CHI  # 12 * 4 * 256 = 12288
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


def make_mps_atoms(n_atoms, gen):
    """Generate n_atoms MPS-shape parameter vectors.

    Each atom: (L, d, chi, chi) i.i.d. Gaussian, then per-site L2-normalized
    on the (d, chi, chi) slab so the full flattened vector has bounded norm.
    Returns (n_atoms, N_TOTAL) flat tensor for downstream FHRR-style ops.
    """
    raw = torch.randn((n_atoms, L_SITES, PHYS_D, CHI, CHI), generator=gen)
    # Per-site normalize: each (PHYS_D, CHI, CHI) slab has unit Frobenius norm
    slab_norms = raw.flatten(start_dim=2).norm(dim=-1, keepdim=True)
    raw_normed = raw / slab_norms.unsqueeze(-1).unsqueeze(-1).clamp(min=1e-8)
    # Flatten to (n_atoms, N_TOTAL)
    return raw_normed.reshape(n_atoms, N_TOTAL)


def build_ctx_bundles(byte_atoms, pos_atoms, indices):
    bound = byte_atoms[indices] * pos_atoms.unsqueeze(0)
    summed = bound.sum(dim=1)
    norms = summed.norm(dim=-1, keepdim=True).clamp(min=1e-8)
    return summed / norms


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


def main() -> None:
    _say("Loading corpus...")
    corpus = load_corpus()
    cut = int(len(corpus) * 0.8)
    train, test = corpus[:cut], corpus[cut:]
    _say(f"  train={len(train)}, test={len(test)} bytes")
    _say(f"\nWave 9: MPS-shape VSA prototype")
    _say(f"  L={L_SITES} sites, d={PHYS_D} physical, chi={CHI} bond -> N_TOTAL={N_TOTAL}")
    _say(f"  Reference (FHRR N=4096): 2.4994")
    _say(f"  Reference (BSC N=4096): 2.4817")
    _say(f"  Hypothesis: MPS-shape init gives signal vs plain Gaussian")

    gen = torch.Generator().manual_seed(SEED)
    byte_atoms = make_mps_atoms(VOCAB_SIZE, gen).to(DEVICE)
    pos_atoms = make_mps_atoms(K, gen).to(DEVICE)
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
            ctxs = build_ctx_bundles(byte_atoms, pos_atoms, idx_batch)
            P_W = predict_W(W, ctxs, byte_atoms, BETA, N_TOTAL)
            targets = byte_atoms[tgt_batch]
            expected = P_W.T @ byte_atoms
            errors = targets - expected
            dW = errors.T @ ctxs / N_TOTAL
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
                P_W = predict_W(W, ctxs, byte_atoms, BETA, N_TOTAL)
                P_retr = predict_pool(ctxs, pool_vecs, pool_labels, pool_used, BETA, N_TOTAL)
                P = ALPHA * P_retr + (1.0 - ALPHA) * P_W
                tgts = test_targets[bs:be]
                p_true = P.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)
                total_bits += float(-torch.log2(p_true).sum())
                argmax_correct += int((P.argmax(dim=0) == tgts).sum())
            test_bpc = total_bits / max(T_test, 1)
            argmax_acc = argmax_correct / max(T_test, 1)
            elapsed = time.perf_counter() - t_start
            history.append({"epoch": epoch, "test_bpc": test_bpc,
                            "argmax_accuracy": argmax_acc, "wall_s": elapsed})
            _say(f"    ep={epoch}  bpc={test_bpc:.4f}  arg={argmax_acc:.4f}  ({elapsed:.1f}s)")

    best = min(history, key=lambda h: h["test_bpc"])
    _say(f"\nBest: ep={best['epoch']} bpc={best['test_bpc']:.4f}")
    _say(f"  vs FHRR: {best['test_bpc'] - 2.4994:+.4f}")

    out = {"seed": SEED, "L_sites": L_SITES, "phys_d": PHYS_D, "chi": CHI, "n_total": N_TOTAL,
           "k": K, "history": history,
           "wall_time_total_s": time.perf_counter() - t_start}
    out_path = Path(__file__).resolve().parent.parent / "data" / "exp_wave9_mps_prototype"
    out_path.mkdir(parents=True, exist_ok=True)
    (out_path / "metrics.json").write_text(json.dumps(out, indent=2, default=str))
    _say(f"\nWrote {out_path / 'metrics.json'}")


if __name__ == "__main__":
    main()
