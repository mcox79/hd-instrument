"""DG-style sparse projector before pool storage.

Dentate gyrus expands ~200K EC inputs to ~1M granule cells (5x sparsifying
expansion), with k-WTA-like activity (~2-4% of cells active). Result: highly
overlapping inputs become highly orthogonal sparse codes BEFORE storage in
the autoassociative CA3 attractor.

Our pointer-chain pool stores raw FHRR context bundles. Similar contexts give
similar bundles, which interfere on retrieval. Adding a DG-style sparse
projector before pool storage should reduce destructive interference and
recover some of the 0.115-bit gap.

Implementation:
1. Initialize an expansion projector P: random FHRR-style 4N-by-N projection
   (or N-by-N rotation + selection — both decorrelate but the expansion
    variant adds capacity).
2. For each context c: expanded = P @ c, then keep only top-k% by magnitude
   (k-WTA sparsification).
3. Store the SPARSIFIED context in the pool; retrieval uses the same
   projection + sparsification on the query.

The W matrix continues to operate on raw context bundles (unchanged).
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
EXPANSION_FACTOR = 4  # DG: ~5x expansion. We use 4x for memory.
VOCAB_SIZE = 256
PAD_BYTE = 0
K = 4
AROUSAL = 0.3
BETA = 8.0
BATCH_SIZE = 64
POOL_SIZE = 1024
ALPHA = 0.3
DECAY = 1e-4
MAX_EPOCHS = 5
EPOCH_CHECKPOINTS = [1, 3, 5]

# Sparsity sweep: fraction of components to keep after k-WTA.
SPARSITY_VARIANTS = [
    ("baseline_no_dg", None),
    ("dg_keep_top_20pct", 0.20),
    ("dg_keep_top_10pct", 0.10),
    ("dg_keep_top_5pct", 0.05),
    ("dg_keep_top_2pct", 0.02),
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


def train_test_split(corpus, train_frac=0.8):
    cut = int(len(corpus) * train_frac)
    return corpus[:cut], corpus[cut:]


def _build_context_bundles_batch(byte_atoms, pos_atoms, indices):
    bound = byte_atoms[indices] * pos_atoms.unsqueeze(0)
    summed = bound.sum(dim=1)
    mag = summed.abs().clamp(min=1e-8)
    return summed / mag.to(summed.dtype)


def dg_project_batch(c_batch: torch.Tensor, dg_basis: torch.Tensor, keep_frac: float | None) -> torch.Tensor:
    """Project context batch through DG sparse expansion + k-WTA.

    c_batch: (B, N) complex
    dg_basis: (M_exp, N) complex projection basis (M_exp = expansion_factor * N)
    keep_frac: fraction of expanded components to keep (None = no DG, identity)
    Returns: (B, M_exp) sparsified expansion, or (B, N) if keep_frac is None.
    """
    if keep_frac is None:
        return c_batch
    expanded = c_batch @ dg_basis.T  # (B, M_exp)
    mag = expanded.abs()
    B, M_exp = mag.shape
    k = max(1, int(keep_frac * M_exp))
    # For each row, find threshold (k-th largest value) and zero out below
    topk_vals, _ = mag.topk(k, dim=1)
    thresholds = topk_vals[:, -1:]
    mask = mag >= thresholds
    return expanded * mask.to(expanded.dtype)


def _predict_W_batch(W, ctxs, byte_atoms, beta):
    """W readout — uses raw context, not DG-projected."""
    n = ctxs.shape[1]
    q = ctxs @ W.T
    sims = (byte_atoms.conj() @ q.T).real / n
    return torch.softmax(beta * sims, dim=0)


def _predict_pool_batch(ctxs_dg, pool_vecs, pool_labels, pool_used, beta):
    """Pool retrieval — uses DG-projected contexts."""
    B = ctxs_dg.shape[0]
    if pool_used == 0:
        return torch.full((VOCAB_SIZE, B), 1.0 / VOCAB_SIZE, device=ctxs_dg.device)
    n = ctxs_dg.shape[1]
    active = pool_vecs[:pool_used]
    labels = pool_labels[:pool_used]
    # Cosine-like similarity in the expanded sparse space
    # Use raw inner product divided by sqrt of nonzero count for normalization
    sims = (active.conj() @ ctxs_dg.T).real / max(n, 1)
    weights = torch.softmax(beta * sims, dim=0)
    P_retr = torch.zeros(VOCAB_SIZE, B, device=ctxs_dg.device)
    P_retr.scatter_add_(0, labels.unsqueeze(1).expand(-1, B), weights)
    return P_retr


def run_config(label, keep_frac, train, test):
    quiet = tracing.TraceBus(enabled=False)
    with tracing.using(quiet):
        gen = torch.Generator().manual_seed(SEED)
        byte_atoms = torch.stack([atoms.make_atom_fhrr(N_SUBSTRATE, gen) for _ in range(VOCAB_SIZE)]).to(DEVICE)
        pos_atoms = torch.stack([atoms.make_atom_fhrr(N_SUBSTRATE, gen) for _ in range(K)]).to(DEVICE)
        W = torch.zeros((N_SUBSTRATE, N_SUBSTRATE), dtype=torch.complex64, device=DEVICE)

        # DG basis: random FHRR atoms of dimension M_exp = expansion_factor * N
        if keep_frac is None:
            dg_basis = None
            pool_dim = N_SUBSTRATE
        else:
            M_exp = EXPANSION_FACTOR * N_SUBSTRATE
            dg_basis = torch.stack([atoms.make_atom_fhrr(N_SUBSTRATE, gen) for _ in range(M_exp)]).to(DEVICE)
            pool_dim = M_exp

        pool_vecs = torch.zeros((POOL_SIZE, pool_dim), dtype=torch.complex64, device=DEVICE)
        pool_labels = torch.zeros(POOL_SIZE, dtype=torch.long, device=DEVICE)
        pool_used = 0
        pool_idx = 0

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
                dW = errors.T @ ctxs.conj() / N_SUBSTRATE
                if DECAY > 0:
                    W.mul_(1.0 - DECAY)
                W.add_(dW, alpha=AROUSAL)
                # Update pool with DG-projected contexts (only first epoch).
                if epoch == 1:
                    ctxs_dg = dg_project_batch(ctxs, dg_basis, keep_frac) if dg_basis is not None else ctxs
                    for b in range(B):
                        pool_vecs[pool_idx] = ctxs_dg[b]
                        pool_labels[pool_idx] = tgt_batch[b]
                        pool_idx = (pool_idx + 1) % POOL_SIZE
                        pool_used = min(pool_used + 1, POOL_SIZE)

            if epoch in EPOCH_CHECKPOINTS:
                total_bits = 0.0
                argmax_correct = 0
                for bs in range(0, T_test, BATCH_SIZE):
                    be = min(bs + BATCH_SIZE, T_test)
                    ctxs = _build_context_bundles_batch(byte_atoms, pos_atoms, test_idx[bs:be])
                    P_W = _predict_W_batch(W, ctxs, byte_atoms, BETA)
                    ctxs_dg = dg_project_batch(ctxs, dg_basis, keep_frac) if dg_basis is not None else ctxs
                    P_retr = _predict_pool_batch(ctxs_dg, pool_vecs, pool_labels, pool_used, BETA)
                    P = ALPHA * P_retr + (1.0 - ALPHA) * P_W
                    p_true = P.gather(0, test_targets[bs:be].unsqueeze(0)).squeeze(0).clamp(min=1e-12)
                    total_bits += float(-torch.log2(p_true).sum())
                    argmax_pred = P.argmax(dim=0)
                    argmax_correct += int((argmax_pred == test_targets[bs:be]).sum())
                test_bpc = total_bits / max(T_test, 1)
                argmax_acc = argmax_correct / max(T_test, 1)
                elapsed = time.perf_counter() - t_start
                history.append({"epoch": epoch, "test_bpc": test_bpc, "argmax_accuracy": argmax_acc, "wall_s": elapsed})
                _say(f"    [{label}] epoch={epoch}  test_bpc={test_bpc:.4f}  argmax={argmax_acc:.4f}  ({elapsed:.1f}s)")

        return {"label": label, "keep_frac": keep_frac, "history": history}


def main() -> None:
    _say("Loading corpus...")
    corpus = load_corpus()
    train, test = train_test_split(corpus, 0.8)
    _say(f"  train={len(train)}, test={len(test)} bytes")
    _say(f"\nDG sparse projector sweep (N={N_SUBSTRATE}, expansion={EXPANSION_FACTOR}x)")
    _say(f"  K={K}, beta={BETA}, decay={DECAY}, pool_size={POOL_SIZE}, alpha={ALPHA}")
    _say(f"  Variants: {[v[0] for v in SPARSITY_VARIANTS]}")
    _say(f"\nReferences:")
    _say(f"  Baseline (no DG, 5 epochs): 2.544 bpc")
    _say(f"  Baseline (no DG, converged 15 epochs): 2.505 bpc")
    _say(f"  Tiny transformer ceiling: 2.39 bpc")

    all_results = []
    t_start = time.perf_counter()
    for label, keep_frac in SPARSITY_VARIANTS:
        _say(f"\n--- {label} (keep_frac={keep_frac}) ---")
        t0 = time.perf_counter()
        r = run_config(label, keep_frac, train, test)
        r["wall_time_s"] = time.perf_counter() - t0
        all_results.append(r)
        _say(f"  (config wall time: {r['wall_time_s']:.1f}s)")

    _say(f"\n========= SUMMARY (final epoch test_bpc) =========")
    _say(f"{'variant':30s} {'epoch1':>10s} {'epoch3':>10s} {'epoch5':>10s}")
    for r in all_results:
        h = r["history"]
        bpc_by_epoch = {hh["epoch"]: hh["test_bpc"] for hh in h}
        _say(
            f"{r['label']:30s} "
            f"{bpc_by_epoch.get(1, float('nan')):>10.4f} "
            f"{bpc_by_epoch.get(3, float('nan')):>10.4f} "
            f"{bpc_by_epoch.get(5, float('nan')):>10.4f}"
        )

    best = None
    for r in all_results:
        for h in r["history"]:
            if best is None or h["test_bpc"] < best["test_bpc"]:
                best = {**h, "label": r["label"], "keep_frac": r["keep_frac"]}
    _say(f"\nGlobal best: {best['label']}, epoch={best['epoch']}, test_bpc={best['test_bpc']:.4f}")
    _say(f"  vs baseline (5 epochs): 2.544 (delta {2.544 - best['test_bpc']:+.4f})")
    _say(f"  vs baseline (converged): 2.505 (delta {2.505 - best['test_bpc']:+.4f})")
    _say(f"  vs transformer 2.39: gap {best['test_bpc'] - 2.39:.4f}")
    _say(f"\nTotal wall time: {time.perf_counter() - t_start:.1f}s")

    out = {
        "seed": SEED, "n_substrate": N_SUBSTRATE, "expansion_factor": EXPANSION_FACTOR,
        "k": K, "arousal": AROUSAL, "beta": BETA,
        "pool_size": POOL_SIZE, "alpha": ALPHA, "decay": DECAY, "max_epochs": MAX_EPOCHS,
        "variants": [{"label": v[0], "keep_frac": v[1]} for v in SPARSITY_VARIANTS],
        "results": all_results,
        "best": best,
        "headline": f"DG sparse projector best: {best['label']} test_bpc={best['test_bpc']:.3f}",
    }
    out_path = Path(__file__).resolve().parent.parent / "data" / "exp_dg_projector_charlm"
    out_path.mkdir(parents=True, exist_ok=True)
    (out_path / "metrics.json").write_text(json.dumps(out, indent=2, default=str))
    _say(f"\nWrote {out_path / 'metrics.json'}")


if __name__ == "__main__":
    main()
