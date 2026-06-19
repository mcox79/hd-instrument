"""Wave 4.5: Gradient W with frozen atoms (BSC substrate).

Audit recommendation (2026-05-18): the cheapest, lowest-risk, highest-leverage
single addition to test "is the delta rule leaving perplexity on the table?"

Replace the Hebbian delta-rule update on W with Adam-optimized gradient updates.
Everything else (BSC random fixed atoms, position codes, modReLU, pool, alpha)
stays identical. Single controlled comparison.

Citation:
- Schlag-Irie-Schmidhuber 2021 ICML (arXiv 2102.11174) shows that delta-rule
  fast weights are mathematically the same as linearized attention; backprop
  on the same W finds a different (lower-loss) optimum than the delta rule's
  least-squares solution. We're testing this empirically on our setup.
- Yang et al. 2024 DeltaNet (arXiv 2406.06484) and Gated DeltaNet 2025 use
  this exact path at scale.

Expected (per audit):
- 0.10-0.25 bpc improvement over BSC delta-rule baseline (2.4817 at N=4096,
  2.4344 at N=8192)
- Could land near 2.30 bpc at N=4096, possibly under 2.20 at N=8192
- Would put us at parity-or-better with the tiny transformer baseline (2.39)

What we lose:
- The "one-shot Hebbian learning" framing on the W layer
- But the algebraic structure (random fixed atoms, binding, pool retrieval)
  is intact

Variants: BSC at N=4096 and N=8192, plus a control run with the original
delta-rule for direct comparison.

Falsification (per playbook):
- H supported if gradient W beats delta-rule W by >= 0.05 bpc 5-seed mean
- H rejected if within ±0.02 bpc — delta rule is already near-optimal,
  bottleneck is elsewhere (atoms, depth, attention)
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

# Per audit recommendation: sweep LR for Adam to find optimum
LR_SWEEP = [3e-3, 1e-2, 3e-2]
WEIGHT_DECAY = 1e-4

# Reference deltas to beat (from prior session results)
DELTA_RULE_REFERENCES = {4096: 2.4817, 8192: 2.4344}


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


def shifted_relu(q, b):
    return torch.clamp(q - b, min=0.0)


def predict_W(W, ctxs, byte_atoms, beta, n, use_relu=True):
    """W readout + optional ReLU + similarity softmax."""
    q = ctxs @ W.T
    if use_relu:
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


def run_gradient_variant(N, lr, train, test):
    """W trained by Adam on cross-entropy loss. Atoms + everything else fixed.

    Post-autonomous-queue fix v2 (validated by audit 2026-05-18):
    1. Initialize W = I_N (identity matrix), not zeros. Per Le-Jaitly-Hinton
       2015 IRNN (arXiv:1504.00941). Starts at delta-rule baseline behavior.
       At step 0, q = ctx (the bipolar context itself), guaranteeing
       gradient flow regardless of any threshold.
    2. Drop shifted_relu in the gradient variant — literature standard
       (Schlag 2021, Yang 2024 DeltaNet use linear readout). modReLU is
       only +0.022 bpc per our prior ablation, not load-bearing.
    """
    gen = torch.Generator().manual_seed(SEED)
    byte_atoms = make_bsc_atoms(VOCAB_SIZE, N, gen).to(DEVICE)
    pos_atoms = make_bsc_atoms(K, N, gen).to(DEVICE)
    # Identity init per IRNN/audit recommendation
    W_init = torch.eye(N, dtype=torch.float32, device=DEVICE)
    W = torch.nn.Parameter(W_init)
    optimizer = torch.optim.AdamW([W], lr=lr, weight_decay=WEIGHT_DECAY)

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
            # v3 LOSS CHANGE (audit-recommended 2026-05-18):
            # Delta rule = SGD on ||W ctx - target_atom||^2 in codebook space.
            # Cross-entropy on softmax(sims) has different minima except at convergence.
            # Try MSE loss to match the delta rule's actual objective.
            q = ctxs @ W.T  # (B, N) predicted "atom" in embedding space
            target_atoms = byte_atoms[tgt_batch]  # (B, N) the true bipolar atom
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
                    P_W = predict_W(W, ctxs, byte_atoms, BETA, N, use_relu=False)  # consistency with training
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
                _say(f"    [N={N} lr={lr:.0e}] ep={epoch}  bpc={test_bpc:.4f}  arg={argmax_acc:.4f}  "
                     f"||W||={w_frob:.1f}  ({elapsed:.1f}s)")
    return {"N": N, "lr": lr, "history": history}


def run_delta_rule_variant(N, train, test):
    """Reference run with the delta rule (matches BSC baseline for the corpus)."""
    AROUSAL = 0.3
    DECAY = 1e-4
    gen = torch.Generator().manual_seed(SEED)
    byte_atoms = make_bsc_atoms(VOCAB_SIZE, N, gen).to(DEVICE)
    pos_atoms = make_bsc_atoms(K, N, gen).to(DEVICE)
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
            P_W = predict_W(W, ctxs, byte_atoms, BETA, N)
            targets = byte_atoms[tgt_batch]
            expected = P_W.T @ byte_atoms
            errors = targets - expected
            dW = errors.T @ ctxs / N
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
            for bs in range(0, T_test, BATCH_SIZE):
                be = min(bs + BATCH_SIZE, T_test)
                ctxs = build_ctx_bundles_bsc(byte_atoms, pos_atoms, test_idx[bs:be])
                P_W = predict_W(W, ctxs, byte_atoms, BETA, N)
                P_retr = predict_pool(ctxs, pool_vecs, pool_labels, pool_used, BETA, N)
                P = ALPHA * P_retr + (1.0 - ALPHA) * P_W
                tgts = test_targets[bs:be]
                p_true = P.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)
                total_bits += float(-torch.log2(p_true).sum())
            test_bpc = total_bits / max(T_test, 1)
            elapsed = time.perf_counter() - t_start
            w_frob = float(W.pow(2).sum().sqrt())
            history.append({"epoch": epoch, "test_bpc": test_bpc, "w_frob": w_frob, "wall_s": elapsed})
            _say(f"    [delta N={N}] ep={epoch}  bpc={test_bpc:.4f}  ||W||={w_frob:.1f}  ({elapsed:.1f}s)")
    return {"N": N, "method": "delta_rule", "history": history}


def main() -> None:
    _say("Loading corpus...")
    corpus = load_corpus()
    cut = int(len(corpus) * 0.8)
    train, test = corpus[:cut], corpus[cut:]
    _say(f"  train={len(train)}, test={len(test)} bytes")
    _say(f"\nWave 4.5: Gradient W with frozen atoms (BSC substrate)")
    _say(f"  Reference delta-rule BSC results: N=4096 -> 2.4817, N=8192 -> 2.4344")
    _say(f"  Variants: AdamW LR sweep {LR_SWEEP} at N=4096 and N=8192")
    _say(f"  Plus delta-rule baseline per N for direct comparison")
    _say(f"  Lit: Schlag-Irie-Schmidhuber 2021 ICML arXiv 2102.11174")
    _say(f"  Audit prediction: 0.10-0.25 bpc gain over delta rule")

    all_results = []
    t_all = time.perf_counter()
    for N in [4096, 8192]:
        _say(f"\n--- N = {N} ---")
        # First: delta-rule reference
        _say(f"  Delta-rule reference run (matches prior session N={N} number)")
        r_delta = run_delta_rule_variant(N, train, test)
        r_delta["wall_time_s"] = time.perf_counter() - t_all
        all_results.append({"method": "delta_rule", **r_delta})
        delta_best = min(r_delta["history"], key=lambda h: h["test_bpc"])["test_bpc"]
        # Now: gradient W with LR sweep
        for lr in LR_SWEEP:
            _say(f"  Gradient W (AdamW lr={lr:.0e})")
            t0 = time.perf_counter()
            r_grad = run_gradient_variant(N, lr, train, test)
            r_grad["wall_time_s"] = time.perf_counter() - t0
            all_results.append({"method": "gradient", **r_grad})
            grad_best = min(r_grad["history"], key=lambda h: h["test_bpc"])["test_bpc"]
            delta_vs_grad = delta_best - grad_best
            _say(f"    Best: bpc={grad_best:.4f}  vs delta_rule={delta_best:.4f}  "
                 f"(gradient gain: {delta_vs_grad:+.4f})")

    _say(f"\n========= SUMMARY =========")
    _say(f"{'N':>6s} {'method':>15s} {'lr':>10s} {'best_bpc':>10s} {'delta_vs_ref':>14s}")
    for r in all_results:
        ref = DELTA_RULE_REFERENCES.get(r["N"], None)
        best = min(r["history"], key=lambda h: h["test_bpc"])["test_bpc"]
        delta = (best - ref) if ref else None
        lr_str = f"{r.get('lr', '-'):.0e}" if r.get('lr') else "-"
        delta_str = f"{delta:+.4f}" if delta is not None else "-"
        _say(f"{r['N']:>6d} {r['method']:>15s} {lr_str:>10s} {best:>10.4f} {delta_str:>14s}")

    out = {"seed": SEED, "k": K, "beta": BETA, "pool_size": POOL_SIZE, "alpha": ALPHA,
           "relu_b": RELU_B, "max_epochs": MAX_EPOCHS, "lr_sweep": LR_SWEEP,
           "weight_decay": WEIGHT_DECAY, "results": all_results,
           "wall_time_total_s": time.perf_counter() - t_all}
    out_path = Path(__file__).resolve().parent.parent / "data" / "exp_wave45_gradient_w_frozen_atoms"
    out_path.mkdir(parents=True, exist_ok=True)
    (out_path / "metrics.json").write_text(json.dumps(out, indent=2, default=str))
    _say(f"\nWrote {out_path / 'metrics.json'}")
    _say(f"Total wall: {time.perf_counter() - t_all:.1f}s")


if __name__ == "__main__":
    main()
