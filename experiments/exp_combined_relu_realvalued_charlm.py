"""Real-valued port of combined+modReLU baseline.

Stores FHRR vectors as a pair (re, im) of FP32 tensors instead of complex64.
Replaces every complex matmul with 4 real matmuls. This enables Tensor Core
acceleration via TF32 (FP32 matmul automatically uses Tensor Cores at TF19
precision when torch.set_float32_matmul_precision('high') is set).

Goal: match the complex64 baseline (2.4994 at N=4096) within FP32 tolerance,
then measure speedup at large N where the complex64 implementation was
bandwidth-bound on cuBLAS FP32-CUDA-core fallback.

Verification: same SEED, same hyperparams, same data. Expected output:
test_bpc within ±0.01 of 2.4994 at N=4096. If not, the port has a bug.
"""

from __future__ import annotations

import json
import math
import time
from pathlib import Path

import torch


# Enable Tensor Cores for real-valued FP32 matmul.
torch.set_float32_matmul_precision("high")

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
SEED = 17
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

N_VALUES = [4096, 8192, 16384]


def _say(msg: str) -> None:
    print(msg, flush=True)


def make_atoms_real(k: int, n: int, gen: torch.Generator) -> tuple[torch.Tensor, torch.Tensor]:
    """Generate k FHRR atoms as (re, im) tensors of shape (k, n) each, FP32 unit-magnitude.

    Identical phase sampling to make_atom_fhrr; produces numerically equivalent atoms.
    """
    phases = torch.rand((k, n), generator=gen) * (2.0 * math.pi)
    return torch.cos(phases).to(torch.float32), torch.sin(phases).to(torch.float32)


def cmul(a_re, a_im, b_re, b_im):
    """Elementwise complex multiply."""
    return a_re * b_re - a_im * b_im, a_re * b_im + a_im * b_re


def cmatmul(A_re, A_im, B_re, B_im):
    """Complex matmul A @ B. Each input is (Re, Im) real tensors."""
    return A_re @ B_re - A_im @ B_im, A_re @ B_im + A_im @ B_re


def cabs(re, im, eps=1e-9):
    """Elementwise complex magnitude with floor."""
    return torch.sqrt(re * re + im * im).clamp(min=eps)


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


def build_ctx_bundles_real(batom_re, batom_im, patom_re, patom_im, indices):
    """For each sequence of K byte indices, bind with positions and bundle (sum + normalize).

    indices: (B, K) long
    batom_re/im: (V, N) real
    patom_re/im: (K, N) real
    Returns: ctx_re, ctx_im each (B, N), unit-magnitude per element.
    """
    # Gather byte atoms at indices: shape (B, K, N) each
    bre = batom_re[indices]
    bim = batom_im[indices]
    # Broadcast multiply with position atoms (K, N) → (B, K, N)
    pre = patom_re.unsqueeze(0)
    pim = patom_im.unsqueeze(0)
    bound_re = bre * pre - bim * pim
    bound_im = bre * pim + bim * pre
    # Sum across K
    sre = bound_re.sum(dim=1)
    sim = bound_im.sum(dim=1)
    # Normalize by magnitude
    mag = cabs(sre, sim)
    return sre / mag, sim / mag


def magnitude_relu_real(re, im, b):
    """modReLU on a complex-valued tensor stored as (re, im). Subtracts b from magnitude, clamps at 0."""
    mag = cabs(re, im)
    new_mag = torch.clamp(mag - b, min=0.0)
    scale = new_mag / mag
    return re * scale, im * scale


def predict_W_real(W_re, W_im, ctx_re, ctx_im, batom_re, batom_im, beta, n, use_modrelu=True):
    """Forward W readout, modReLU, codebook softmax."""
    # q = W @ ctx  (W is (N,N), ctx is (B,N))  → q is (B, N) but actually we compute ctx @ W.T
    # ctxs @ W.T: (B,N) @ (N,N).T = (B,N)
    q_re, q_im = cmatmul(ctx_re, ctx_im, W_re.T, W_im.T)
    if use_modrelu:
        q_re, q_im = magnitude_relu_real(q_re, q_im, RELU_B)
    # similarity = real( byte_atoms.conj() @ q.T ) / n  → (V, B)
    # batom.conj() = (re, -im).  product = (re, -im) * q  → real part = re*q_re + im*q_im (after conj flip)
    # Actually: sim[v, b] = real( sum_n conj(batom[v,n]) * q[b,n] )
    #                    = sum_n (batom_re[v,n] * q_re[b,n] + batom_im[v,n] * q_im[b,n])
    # = batom_re @ q_re.T + batom_im @ q_im.T  (both FP32 matmuls → TC accelerated)
    sims = (batom_re @ q_re.T + batom_im @ q_im.T) / n
    return torch.softmax(beta * sims, dim=0)


def predict_pool_real(ctx_re, ctx_im, pool_re, pool_im, pool_labels, pool_used, beta, n):
    """Pool retrieval via real-valued cosine similarity over active pool entries."""
    B = ctx_re.shape[0]
    if pool_used == 0:
        return torch.full((VOCAB_SIZE, B), 1.0 / VOCAB_SIZE, device=ctx_re.device)
    active_re = pool_re[:pool_used]
    active_im = pool_im[:pool_used]
    labels = pool_labels[:pool_used]
    # sims[p, b] = real( conj(pool[p]) . ctx[b] ) / n
    sims = (active_re @ ctx_re.T + active_im @ ctx_im.T) / n
    weights = torch.softmax(beta * sims, dim=0)
    P_retr = torch.zeros(VOCAB_SIZE, B, device=ctx_re.device)
    P_retr.scatter_add_(0, labels.unsqueeze(1).expand(-1, B), weights)
    return P_retr


def run_config(N: int, train: bytes, test: bytes):
    gen = torch.Generator().manual_seed(SEED)
    batom_re, batom_im = make_atoms_real(VOCAB_SIZE, N, gen)
    batom_re, batom_im = batom_re.to(DEVICE), batom_im.to(DEVICE)
    patom_re, patom_im = make_atoms_real(K, N, gen)
    patom_re, patom_im = patom_re.to(DEVICE), patom_im.to(DEVICE)
    W_re = torch.zeros((N, N), dtype=torch.float32, device=DEVICE)
    W_im = torch.zeros((N, N), dtype=torch.float32, device=DEVICE)
    pool_re = torch.zeros((POOL_SIZE, N), dtype=torch.float32, device=DEVICE)
    pool_im = torch.zeros((POOL_SIZE, N), dtype=torch.float32, device=DEVICE)
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
            ctx_re, ctx_im = build_ctx_bundles_real(batom_re, batom_im, patom_re, patom_im, idx_batch)
            P_W = predict_W_real(W_re, W_im, ctx_re, ctx_im, batom_re, batom_im, BETA, N, use_modrelu=True)
            # expected = P_W.T @ byte_atoms  (B,V) @ (V,N) = (B,N) — applied to both re/im
            P_WT = P_W.T  # (B, V)
            exp_re = P_WT @ batom_re
            exp_im = P_WT @ batom_im
            tgt_re = batom_re[tgt_batch]  # (B, N)
            tgt_im = batom_im[tgt_batch]
            err_re = tgt_re - exp_re
            err_im = tgt_im - exp_im
            # dW = errors.T @ ctxs.conj() / N
            # (N, B) @ (B, N) for complex: dW = err.T * ctx.conj => 4 FP32 matmuls
            # ctxs.conj = (ctx_re, -ctx_im)
            # dW_re = err_re.T @ ctx_re + err_im.T @ (-ctx_im) * (-1)?  Wait let's do it carefully.
            # (a + ib)(c + id) = (ac - bd) + i(bc + ad)
            # err.T @ ctx.conj where ctx.conj = ctx_re - i*ctx_im
            # so (err_re + i*err_im).T @ (ctx_re - i*ctx_im)
            # = err_re.T @ ctx_re + err_im.T @ ctx_im + i(err_im.T @ ctx_re - err_re.T @ ctx_im)
            dW_re = (err_re.T @ ctx_re + err_im.T @ ctx_im) / N
            dW_im = (err_im.T @ ctx_re - err_re.T @ ctx_im) / N
            if DECAY > 0:
                W_re.mul_(1.0 - DECAY)
                W_im.mul_(1.0 - DECAY)
            W_re.add_(dW_re, alpha=AROUSAL)
            W_im.add_(dW_im, alpha=AROUSAL)
            if epoch == 1:
                # Vectorized pool insertion
                dest = (pool_idx + arange_b[:B]) % POOL_SIZE
                pool_re.index_copy_(0, dest, ctx_re)
                pool_im.index_copy_(0, dest, ctx_im)
                pool_labels.index_copy_(0, dest, tgt_batch)
                pool_idx = (pool_idx + B) % POOL_SIZE
                pool_used = min(pool_used + B, POOL_SIZE)
        if epoch in EPOCH_CHECKPOINTS:
            total_bits = 0.0
            argmax_correct = 0
            for bs in range(0, T_test, BATCH_SIZE):
                be = min(bs + BATCH_SIZE, T_test)
                ctx_re, ctx_im = build_ctx_bundles_real(batom_re, batom_im, patom_re, patom_im, test_idx[bs:be])
                P_W = predict_W_real(W_re, W_im, ctx_re, ctx_im, batom_re, batom_im, BETA, N, use_modrelu=True)
                P_retr = predict_pool_real(ctx_re, ctx_im, pool_re, pool_im, pool_labels, pool_used, BETA, N)
                P = ALPHA * P_retr + (1.0 - ALPHA) * P_W
                tgts = test_targets[bs:be]
                p_true = P.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)
                total_bits += float(-torch.log2(p_true).sum())
                argmax_correct += int((P.argmax(dim=0) == tgts).sum())
            test_bpc = total_bits / max(T_test, 1)
            argmax_acc = argmax_correct / max(T_test, 1)
            elapsed = time.perf_counter() - t_start
            history.append({"epoch": epoch, "test_bpc": test_bpc, "argmax_accuracy": argmax_acc, "wall_s": elapsed})
            _say(f"    epoch={epoch}  test_bpc={test_bpc:.4f}  argmax={argmax_acc:.4f}  ({elapsed:.1f}s)")
    return {"N": N, "history": history}


def main() -> None:
    _say("Loading corpus...")
    corpus = load_corpus()
    cut = int(len(corpus) * 0.8)
    train, test = corpus[:cut], corpus[cut:]
    _say(f"  train={len(train)}, test={len(test)} bytes")
    _say(f"\nReal-valued FHRR port (TF32 enabled)")
    _say(f"  device={DEVICE}, dtype=float32 paired")
    _say(f"  N_VALUES={N_VALUES}, K={K}, arousal={AROUSAL}, beta={BETA}, decay={DECAY}, pool={POOL_SIZE}, relu_b={RELU_B}")
    _say(f"  Baseline (complex64 path, N=4096, GPU): 2.4994")
    _say(f"  Baseline (complex64 path, N=8192, GPU): 2.4774")

    all_results = []
    for N in N_VALUES:
        _say(f"\n--- N = {N} ---")
        t0 = time.perf_counter()
        try:
            r = run_config(N, train, test)
            r["wall_time_s"] = time.perf_counter() - t0
            all_results.append(r)
            best = min(r["history"], key=lambda h: h["test_bpc"])
            _say(f"  Best for N={N}: epoch={best['epoch']}, test_bpc={best['test_bpc']:.4f}, wall={r['wall_time_s']:.1f}s")
        except torch.cuda.OutOfMemoryError as e:
            _say(f"  OOM at N={N}: {e}")
            torch.cuda.empty_cache()
            all_results.append({"N": N, "error": "OOM"})

    _say(f"\n========= SUMMARY =========")
    _say(f"{'N':>6s} {'best_ep':>8s} {'best_bpc':>10s} {'wall_s':>9s}")
    for r in all_results:
        if "history" in r:
            best = min(r["history"], key=lambda h: h["test_bpc"])
            _say(f"{r['N']:>6d} {best['epoch']:>8d} {best['test_bpc']:>10.4f} {r['wall_time_s']:>9.1f}")
        else:
            _say(f"{r['N']:>6d} {'-':>8s} {r.get('error', 'unknown'):>10s}")

    out = {"seed": SEED, "k": K, "arousal": AROUSAL, "beta": BETA, "decay": DECAY,
           "pool_size": POOL_SIZE, "alpha": ALPHA, "relu_b": RELU_B, "max_epochs": MAX_EPOCHS,
           "n_values": N_VALUES, "dtype": "float32-paired", "tf32": True, "results": all_results}
    out_path = Path(__file__).resolve().parent.parent / "data" / "exp_combined_relu_realvalued_charlm"
    out_path.mkdir(parents=True, exist_ok=True)
    (out_path / "metrics.json").write_text(json.dumps(out, indent=2, default=str))
    _say(f"\nWrote {out_path / 'metrics.json'}")


if __name__ == "__main__":
    main()
