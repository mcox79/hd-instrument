"""Wave 4.6: Gradient W + learnable atom offsets (BSC substrate).

Audit recommendation (2026-05-18): the second-cheapest backprop addition.
Tests whether the fixed-random-atoms constraint costs perplexity.

Atom representation: atom_v = sign(random_v + Δ_v) at training, where Δ_v
is a learnable per-byte offset initialized to zero. With small L2 weight
decay on Δ, atoms stay near-orthogonal but can drift to capture functional
similarity (e.g., vowels cluster, punctuation clusters).

Subtle implementation choice: BSC atoms are ±1. To make them differentiable,
keep a continuous "logit" representation `atom_logit_v = random_v + Δ_v`
and use straight-through estimator: forward = sign(logit), backward = identity
(or clipped). This is the standard recipe from Binary Connect / BNN literature
(ReSTE, arXiv 2308.06689).

Citation:
- Imani lab "Hyperdimensional Computing with Adaptive Encoder" (Frontiers
  2024) — the canonical reference for learnable HDC atoms.
- ReSTE 2023 (arXiv 2308.06689) — straight-through estimator for sign().
- THDC 2026 (arXiv 2602.00116) — end-to-end backprop on HDC.

Expected (per audit):
- 0.05-0.15 bpc gain over Wave 4.5 (gradient W with frozen atoms)
- Combined with Wave 4.5: 0.15-0.35 bpc gain over delta-rule baseline

What we lose:
- Some atom orthogonality (controlled by Δ weight decay)
- The "fixed random substrate" framing is partly relaxed

Variants:
- Δ weight decay ∈ {1e-2, 1e-3, 1e-4} — controls how much atoms drift
- AdamW lr fixed at 1e-2 (will be tuned in Wave 4.5 first)
- N=4096 (faster iteration; can extend to N=8192 if H supported)
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
BETA = 8.0
BATCH_SIZE = 64
POOL_SIZE = 1024
ALPHA = 0.3
MAX_EPOCHS = 15
EVAL_AT = [5, 15]
RELU_B = 0.5

LR = 1e-2
DELTA_WEIGHT_DECAYS = [1e-2, 1e-3, 1e-4]
W_WEIGHT_DECAY = 1e-4


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


def make_bsc_atoms_random(k, n, gen):
    """Returns the fixed random ±1 component of atoms. Δ is added on top."""
    raw = torch.rand((k, n), generator=gen)
    return (2.0 * (raw > 0.5).float() - 1.0)


class SignSTE(torch.autograd.Function):
    """sign() with identity straight-through estimator (clipped to [-1, 1])."""
    @staticmethod
    def forward(ctx, x):
        ctx.save_for_backward(x)
        return torch.sign(torch.where(x == 0, torch.ones_like(x), x))

    @staticmethod
    def backward(ctx, grad_output):
        (x,) = ctx.saved_tensors
        # Clipped identity STE: pass gradient through where |x| ≤ 1, else 0
        mask = (x.abs() <= 1.0).float()
        return grad_output * mask


def sign_ste(x):
    return SignSTE.apply(x)


def build_ctx_bundles_bsc(byte_atoms, pos_atoms, indices):
    bound = byte_atoms[indices] * pos_atoms.unsqueeze(0)
    summed = bound.sum(dim=1)
    out = sign_ste(summed)
    return out


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


def run_variant(delta_wd, train, test):
    gen = torch.Generator().manual_seed(SEED)
    # Fixed random component of byte atoms; learnable offsets
    byte_atoms_random = make_bsc_atoms_random(VOCAB_SIZE, N, gen).to(DEVICE)
    pos_atoms_random = make_bsc_atoms_random(K, N, gen).to(DEVICE)
    byte_offsets = torch.nn.Parameter(torch.zeros((VOCAB_SIZE, N), device=DEVICE))
    pos_offsets = torch.nn.Parameter(torch.zeros((K, N), device=DEVICE))
    W = torch.nn.Parameter(torch.zeros((N, N), dtype=torch.float32, device=DEVICE))

    # Two parameter groups: W (W_decay), atom offsets (delta_wd)
    optimizer = torch.optim.AdamW([
        {"params": [W], "weight_decay": W_WEIGHT_DECAY},
        {"params": [byte_offsets, pos_offsets], "weight_decay": delta_wd},
    ], lr=LR)

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

    def effective_atoms():
        # ste_sign on (random + Δ) — straight-through estimator for binary atom
        byte_atoms = sign_ste(byte_atoms_random + byte_offsets)
        pos_atoms = sign_ste(pos_atoms_random + pos_offsets)
        return byte_atoms, pos_atoms

    history = []
    t_start = time.perf_counter()
    for epoch in range(1, MAX_EPOCHS + 1):
        for batch_start in range(0, T_total, BATCH_SIZE):
            be = min(batch_start + BATCH_SIZE, T_total)
            idx_batch = train_idx[batch_start:be]
            tgt_batch = train_targets[batch_start:be]
            B = idx_batch.shape[0]
            byte_atoms, pos_atoms = effective_atoms()
            ctxs = build_ctx_bundles_bsc(byte_atoms, pos_atoms, idx_batch)
            P_W = predict_W(W, ctxs, byte_atoms, BETA, N)
            log_P = torch.log(P_W.clamp(min=1e-12))
            log_p_true = log_P.gather(0, tgt_batch.unsqueeze(0)).squeeze(0)
            loss = -log_p_true.mean()
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
                byte_atoms, pos_atoms = effective_atoms()
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
                byte_offset_norm = float(byte_offsets.detach().pow(2).sum().sqrt())
                w_frob = float(W.detach().pow(2).sum().sqrt())
                elapsed = time.perf_counter() - t_start
                history.append({"epoch": epoch, "test_bpc": test_bpc,
                                "argmax_accuracy": argmax_acc, "w_frob": w_frob,
                                "byte_offset_norm": byte_offset_norm, "wall_s": elapsed})
                _say(f"    [delta_wd={delta_wd:.0e}] ep={epoch}  bpc={test_bpc:.4f}  "
                     f"arg={argmax_acc:.4f}  ||W||={w_frob:.1f}  "
                     f"||Dbyte||={byte_offset_norm:.2f}  ({elapsed:.1f}s)")
    return {"delta_wd": delta_wd, "history": history}


def main() -> None:
    _say("Loading corpus...")
    corpus = load_corpus()
    cut = int(len(corpus) * 0.8)
    train, test = corpus[:cut], corpus[cut:]
    _say(f"  train={len(train)}, test={len(test)} bytes")
    _say(f"\nWave 4.6: Gradient W + learnable atom offsets (BSC substrate)")
    _say(f"  N={N}, K={K}, beta={BETA}, pool={POOL_SIZE}, alpha={ALPHA}, relu_b={RELU_B}")
    _say(f"  LR={LR}, W weight_decay={W_WEIGHT_DECAY}")
    _say(f"  Atom offset weight decay sweep: {DELTA_WEIGHT_DECAYS}")
    _say(f"  Baseline (BSC delta-rule N=4096): 2.4817")
    _say(f"  Wave 4.5 expected: 2.30-2.40")
    _say(f"  Wave 4.6 expected: 2.25-2.35 (per audit, 0.05-0.15 gain over 4.5)")
    _say(f"  Lit: Imani 2024 Frontiers; ReSTE 2023; THDC 2026")

    all_results = []
    t_all = time.perf_counter()
    for delta_wd in DELTA_WEIGHT_DECAYS:
        _say(f"\n--- delta weight decay = {delta_wd:.0e} ---")
        t0 = time.perf_counter()
        r = run_variant(delta_wd, train, test)
        r["wall_time_s"] = time.perf_counter() - t0
        all_results.append(r)
        best = min(r["history"], key=lambda h: h["test_bpc"])
        _say(f"  Best: ep={best['epoch']}, bpc={best['test_bpc']:.4f}, "
             f"||Dbyte||={best['byte_offset_norm']:.2f}")

    _say(f"\n========= SUMMARY =========")
    _say(f"{'delta_wd':>8s} {'best_ep':>8s} {'best_bpc':>10s} {'||Dbyte||':>11s} {'delta_vs_BSC':>14s}")
    for r in all_results:
        best = min(r["history"], key=lambda h: h["test_bpc"])
        delta = best["test_bpc"] - 2.4817
        _say(f"{r['delta_wd']:>8.0e} {best['epoch']:>8d} {best['test_bpc']:>10.4f} "
             f"{best['byte_offset_norm']:>11.2f} {delta:>+14.4f}")

    out = {"seed": SEED, "n": N, "k": K, "beta": BETA, "pool_size": POOL_SIZE,
           "alpha": ALPHA, "relu_b": RELU_B, "max_epochs": MAX_EPOCHS,
           "lr": LR, "w_weight_decay": W_WEIGHT_DECAY,
           "delta_weight_decays": DELTA_WEIGHT_DECAYS,
           "results": all_results,
           "wall_time_total_s": time.perf_counter() - t_all}
    out_path = Path(__file__).resolve().parent.parent / "data" / "exp_wave46_learnable_offsets"
    out_path.mkdir(parents=True, exist_ok=True)
    (out_path / "metrics.json").write_text(json.dumps(out, indent=2, default=str))
    _say(f"\nWrote {out_path / 'metrics.json'}")


if __name__ == "__main__":
    main()
