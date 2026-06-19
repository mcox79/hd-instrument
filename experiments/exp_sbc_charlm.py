"""Sparse Block Codes (SBC / MMB) substrate port.

Citation:
- Laiho et al. 2015 *High-Dimensional Computing with Sparse Vectors*
  (CogSci 2015) — original sparse block-code formulation.
- Frady, Kleyko, Sommer 2021 *Variable Binding for Sparse Distributed
  Representations: Theory and Applications* (arXiv 2009.06734) — modern
  formalization, capacity analysis, MMB binding.

Substrate:
- Total dimension N = M × B_size, partitioned into M blocks of size B_size.
- Each atom has EXACTLY ONE active position per block (sparsity = M/N = 1/B_size).
- Equivalently: an atom is M integers in [0, B_size).

Operations:
- Binding (MMB): per-block modular index addition.
  bind(a, b)[m] = (a_idx[m] + b_idx[m]) mod B_size
- Bundling: per-block argmax vote.
  bundle(a_1, ..., a_K)[m] = argmax_j #{k : a_k_idx[m] == j}
- Similarity: fraction of blocks where two atoms have the same active index.

Brain mapping: dentate gyrus granule cells and cerebellar granule cells use
sparse population codes with ~1-5% activity. Sparse codes are believed to
underpin pattern separation — keeping memories distinct over time.

Prediction (per playbook discussion):
- Perplexity at small N: comparable to FHRR/BSC, perhaps slightly worse
  due to fewer "soft" features.
- Wave 3a continual learning: sparse codes predicted to WIN on retention
  (pattern separation, less interference).

Variants (sparsity sweep):
1. sbc_M64_no_relu:  N=4096, B_size=64, M=64  (sparsity 1.56%)
2. sbc_M64_relu:     same with ReLU readout NL
3. sbc_M128_no_relu: B_size=32, M=128 (sparsity 3.12%)
4. sbc_M32_no_relu:  B_size=128, M=32 (sparsity 0.78%)
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import torch
import torch.nn.functional as F


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
ALPHA = 0.3
DECAY = 1e-4
MAX_EPOCHS = 15
EPOCH_CHECKPOINTS = [1, 5, 10, 15]
RELU_B = 0.5

# (label, B_size, use_relu)
VARIANTS = [
    ("sbc_M64_no_relu",  64,  False),
    ("sbc_M64_relu",     64,  True),
    ("sbc_M128_no_relu", 32,  False),
    ("sbc_M32_no_relu",  128, False),
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


def make_sbc_atoms(k_atoms, M, B_size, gen):
    """Returns (k_atoms, M) int tensor; each row is M indices in [0, B_size).
    Equivalently: a sparse binary vector with M ones (one per block)."""
    return torch.randint(0, B_size, (k_atoms, M), generator=gen)


def sbc_to_dense(atom_idx, M, B_size, device):
    """Convert (..., M) int idx tensor to dense (..., N) FP32 binary one-hot-per-block."""
    # Use one_hot then flatten the M-block dimension into N
    one_hot = F.one_hot(atom_idx, num_classes=B_size)  # (..., M, B_size)
    *batch_dims, _, _ = one_hot.shape
    return one_hot.reshape(*batch_dims, M * B_size).float().to(device)


def sbc_bind(a_idx, b_idx, B_size):
    """Per-block modular index addition. Broadcasts naturally."""
    return (a_idx + b_idx) % B_size


def sbc_bundle_vote(stacked_idx, B_size):
    """Bundle K atoms by per-block argmax vote.

    stacked_idx: (..., K, M) int → returns (..., M) int.
    Tie-breaking: argmax returns the first occurrence (lowest index).
    """
    # one_hot: (..., K, M, B_size). Sum over K → (..., M, B_size). Argmax over last dim.
    one_hot = F.one_hot(stacked_idx, num_classes=B_size).float()
    counts = one_hot.sum(dim=-3)  # collapse K
    return counts.argmax(dim=-1)


def build_ctx_bundles_sbc(byte_atoms_idx, pos_atoms_idx, B_size, indices, M):
    """Build context bundle for a batch.

    byte_atoms_idx: (V, M) int
    pos_atoms_idx: (K, M) int
    indices: (B, K) long — byte indices per batch element
    Returns: (B, M) int — bundled context atom indices.
    """
    # Gather byte atoms used: (B, K, M)
    byte_used = byte_atoms_idx[indices]
    # Bind with positions: (B, K, M)
    bound = sbc_bind(byte_used, pos_atoms_idx.unsqueeze(0), B_size)
    # Bundle K → (B, M)
    return sbc_bundle_vote(bound, B_size)


def shifted_relu(q, b):
    return torch.clamp(q - b, min=0.0)


def predict_W_sbc(W, ctx_dense, byte_dense, M, beta, use_relu):
    """W readout via dense matmul (Tensor-Core accelerated)."""
    q = ctx_dense @ W.T  # (B, N) @ (N, N).T = (B, N)
    if use_relu:
        q = shifted_relu(q, RELU_B)
    # similarity[v, b] = byte_v_dense . q_b / M (normalize by number of active positions)
    sims = (byte_dense @ q.T) / M
    return torch.softmax(beta * sims, dim=0)


def predict_pool_sbc(ctx_dense, pool_vecs, pool_labels, pool_used, beta, M):
    B = ctx_dense.shape[0]
    if pool_used == 0:
        return torch.full((VOCAB_SIZE, B), 1.0 / VOCAB_SIZE, device=ctx_dense.device)
    active = pool_vecs[:pool_used]
    labels = pool_labels[:pool_used]
    sims = (active @ ctx_dense.T) / M
    weights = torch.softmax(beta * sims, dim=0)
    P_retr = torch.zeros(VOCAB_SIZE, B, device=ctx_dense.device)
    P_retr.scatter_add_(0, labels.unsqueeze(1).expand(-1, B), weights)
    return P_retr


def run_config(label, B_size, use_relu, train, test):
    M = N // B_size
    assert M * B_size == N, f"N={N} must be divisible by B_size={B_size}"

    gen = torch.Generator().manual_seed(SEED)
    byte_atoms_idx = make_sbc_atoms(VOCAB_SIZE, M, B_size, gen).to(DEVICE)
    pos_atoms_idx = make_sbc_atoms(K, M, B_size, gen).to(DEVICE)
    byte_dense = sbc_to_dense(byte_atoms_idx, M, B_size, DEVICE)  # (V, N)

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
            ctx_idx = build_ctx_bundles_sbc(byte_atoms_idx, pos_atoms_idx, B_size, idx_batch, M)
            ctx_dense = sbc_to_dense(ctx_idx, M, B_size, DEVICE)
            P_W = predict_W_sbc(W, ctx_dense, byte_dense, M, BETA, use_relu)
            # Hebbian delta update on W (dense)
            targets_dense = byte_dense[tgt_batch]  # (B, N) sparse binary
            expected = P_W.T @ byte_dense  # (B, V) @ (V, N) = (B, N) continuous
            errors = targets_dense - expected
            dW = errors.T @ ctx_dense / N  # (N, B) @ (B, N)
            if DECAY > 0:
                W.mul_(1.0 - DECAY)
            W.add_(dW, alpha=AROUSAL)
            if epoch == 1:
                dest = (pool_idx + arange_b[:B]) % POOL_SIZE
                pool_vecs.index_copy_(0, dest, ctx_dense)
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
                ctx_idx = build_ctx_bundles_sbc(byte_atoms_idx, pos_atoms_idx, B_size, test_idx[bs:be], M)
                ctx_dense = sbc_to_dense(ctx_idx, M, B_size, DEVICE)
                P_W = predict_W_sbc(W, ctx_dense, byte_dense, M, BETA, use_relu)
                P_retr = predict_pool_sbc(ctx_dense, pool_vecs, pool_labels, pool_used, BETA, M)
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
            w_frob = float(W.pow(2).sum().sqrt())
            elapsed = time.perf_counter() - t_start
            history.append({"epoch": epoch, "test_bpc": test_bpc,
                            "argmax_accuracy": argmax_acc,
                            "pool_top1_acc": pool_acc, "w_top1_acc": w_acc,
                            "w_frob": w_frob, "wall_s": elapsed})
            _say(f"    [{label}] ep={epoch}  bpc={test_bpc:.4f}  arg={argmax_acc:.4f}  "
                 f"poolT1={pool_acc:.3f}  wT1={w_acc:.3f}  ||W||={w_frob:.1f}  ({elapsed:.1f}s)")
    return {"label": label, "B_size": B_size, "M": M, "use_relu": use_relu, "history": history}


def main() -> None:
    _say("Loading corpus...")
    corpus = load_corpus()
    cut = int(len(corpus) * 0.8)
    train, test = corpus[:cut], corpus[cut:]
    _say(f"  train={len(train)}, test={len(test)} bytes")
    _say(f"\nSparse Block Codes (SBC / MMB) substrate experiment")
    _say(f"  N={N}, K={K}, arousal={AROUSAL}, beta={BETA}, decay={DECAY}, pool={POOL_SIZE}")
    _say(f"  variants: {[v[0] for v in VARIANTS]}")
    _say(f"  Reference (FHRR combined+modReLU): 2.4994")
    _say(f"  Reference (BSC signed+relu): 2.4817")
    _say(f"  Lit: Laiho 2015; Frady-Kleyko-Sommer 2021 (arXiv 2009.06734)")
    _say(f"  Brain mapping: dentate gyrus / cerebellar granule cells")
    _say(f"  Prediction: comparable perplexity at small N; expected to win on")
    _say(f"  continual learning (Wave 3a) due to pattern separation")

    all_results = []
    t_all = time.perf_counter()
    for label, B_size, use_relu in VARIANTS:
        _say(f"\n--- {label} (B_size={B_size}, M={N // B_size}, sparsity={(N // B_size) / N * 100:.2f}%) ---")
        t0 = time.perf_counter()
        r = run_config(label, B_size, use_relu, train, test)
        r["wall_time_s"] = time.perf_counter() - t0
        all_results.append(r)
        best = min(r["history"], key=lambda h: h["test_bpc"])
        _say(f"  Best for {label}: ep={best['epoch']}, bpc={best['test_bpc']:.4f}")

    _say(f"\n========= SUMMARY =========")
    _say(f"{'variant':>22s} {'best_ep':>8s} {'best_bpc':>10s} {'wT1':>6s} {'poolT1':>7s} {'wall':>7s}")
    for r in all_results:
        best = min(r["history"], key=lambda h: h["test_bpc"])
        _say(f"{r['label']:>22s} {best['epoch']:>8d} {best['test_bpc']:>10.4f} "
             f"{best['w_top1_acc']:>6.3f} {best['pool_top1_acc']:>7.3f} {r['wall_time_s']:>7.1f}")
    _say(f"\n  Reference FHRR combined+modReLU: 2.4994")
    _say(f"  Reference BSC signed+relu:        2.4817")
    best_overall = None
    for r in all_results:
        if "history" not in r: continue
        for h in r["history"]:
            if best_overall is None or h["test_bpc"] < best_overall["bpc"]:
                best_overall = {"bpc": h["test_bpc"], "label": r["label"], "ep": h["epoch"]}
    _say(f"  Best SBC variant: {best_overall['label']} ep={best_overall['ep']} bpc={best_overall['bpc']:.4f}")
    _say(f"  Delta vs FHRR: {best_overall['bpc'] - 2.4994:+.4f}")
    _say(f"  Delta vs BSC: {best_overall['bpc'] - 2.4817:+.4f}")

    out = {"seed": SEED, "n": N, "k": K, "arousal": AROUSAL, "beta": BETA, "decay": DECAY,
           "pool_size": POOL_SIZE, "alpha": ALPHA, "relu_b": RELU_B, "max_epochs": MAX_EPOCHS,
           "variants": [{"label": v[0], "B_size": v[1], "use_relu": v[2]} for v in VARIANTS],
           "results": all_results, "substrate": "SBC-MMB",
           "wall_time_total_s": time.perf_counter() - t_all}
    out_path = Path(__file__).resolve().parent.parent / "data" / "exp_sbc_charlm"
    out_path.mkdir(parents=True, exist_ok=True)
    (out_path / "metrics.json").write_text(json.dumps(out, indent=2, default=str))
    _say(f"\nWrote {out_path / 'metrics.json'}")


if __name__ == "__main__":
    main()
