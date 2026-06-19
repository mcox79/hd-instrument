"""BSC (Binary Spatter Codes) port of the combined+modReLU baseline.

Substrate change: FHRR (complex64 unit-magnitude phasors) → BSC (real-valued
±1 binary vectors). Binding is elementwise multiplication (XOR-like).
Bundling is sum (signed or continuous). Operations are real-valued throughout.

Why this is "brain-closer" than FHRR:
- Cortical population activity is closer to binary (firing or not) than
  to complex phasors. FHRR's phase code is mathematically elegant but has
  no obvious neural analog.
- BSC is the canonical substrate cited in the original VSA-as-brain-model
  literature (Kanerva 2009, "Hyperdimensional Computing: An Introduction").
- XOR-like binding has been proposed as a cortical mechanism (Plate 2003,
  also Lipasti-Klyko hardware-mapping work).

Why this MIGHT also be faster on consumer GPU:
- Real FP32 matmul DOES use Tensor Cores via TF32. cuBLAS complex64 does NOT.
- Per the dtype investigation, the only "free" speedup was switching to a
  real-valued substrate; we're now doing that as a deliberate scientific
  experiment, not a hacky speedup.

Architecture (mirrors combined+modReLU exactly except substrate):
- byte_atoms: 256 atoms of N dim, ±1
- pos_atoms: K atoms of N dim, ±1
- ctx[b] = sign(sum_k byte_atoms[idx_bk] * pos_atoms[k]) — bundled binding
- W: (N, N) real, initialized 0
- predict: q = W @ ctx; sims = byte_atoms @ q.T / N; P = softmax(β·sims)
- learn: err = target - softmax_weighted_avg(byte_atoms); dW = err.T @ ctx / N
- pool: stores (ctx, target) pairs; retrieves via cosine sim of binary vectors

Pre-mortem candidate failures:
1. BSC ceiling is structurally below FHRR at small N — BSC has fewer bits
   per dimension. Frady-Kleyko-Sommer capacity for BSC scales as N (vs N/2
   per dimension for FHRR phase code). Could underperform at N=4096.
2. The signed-bundle (sign of sum) discretization may hurt the delta rule
   gradient signal. Mitigation: keep bundle continuous (sum without sign)
   like FHRR.
3. The modReLU equivalent on real vectors is just ReLU — completely
   different geometry than complex modReLU.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import torch


# Enable TF32 for real-valued matmul — actually engages tensor cores on Ada Lovelace.
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

# Variants to test the design choices:
#   "bsc_continuous_no_relu": continuous bundle (no sign), no readout NL
#   "bsc_continuous_relu":    continuous bundle, ReLU(q - b) readout NL
#   "bsc_signed_no_relu":     sign(sum) bundle, no readout NL
#   "bsc_signed_relu":        sign(sum) bundle, ReLU(q - b) readout NL
VARIANTS = [
    "bsc_continuous_no_relu",
    "bsc_continuous_relu",
    "bsc_signed_no_relu",
    "bsc_signed_relu",
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


def make_bsc_atoms(k, n, gen):
    """Generate k BSC atoms of dim n as ±1 vectors. FP32."""
    raw = torch.rand((k, n), generator=gen)
    return (2.0 * (raw > 0.5).float() - 1.0)  # ±1


def build_ctx_bundles_bsc(byte_atoms, pos_atoms, indices, signed_bundle):
    """For each row of indices (B, K), bind byte_atoms[idx] * pos_atoms, sum across K.

    Returns (B, N) tensor. If signed_bundle: sign(sum). Else: sum / K (continuous).
    """
    bound = byte_atoms[indices] * pos_atoms.unsqueeze(0)  # (B, K, N)
    summed = bound.sum(dim=1)  # (B, N)
    if signed_bundle:
        # sign(0) = 0 in torch; break ties to +1 for stability
        out = torch.sign(summed)
        out = torch.where(out == 0, torch.ones_like(out), out)
        return out
    else:
        return summed / float(K)


def shifted_relu(q, b):
    """ReLU(q - b) — analog of magnitude_relu for real-valued q."""
    return torch.clamp(q - b, min=0.0)


def predict_W_bsc(W, ctxs, byte_atoms, beta, use_relu):
    """W readout + optional shifted-ReLU + similarity softmax."""
    n = ctxs.shape[1]
    q = ctxs @ W.T  # (B, N) — single FP32 Tensor-Core-accelerated matmul
    if use_relu:
        q = shifted_relu(q, RELU_B)
    # similarity[v, b] = sum_n byte_atoms[v, n] * q[b, n] / n
    sims = (byte_atoms @ q.T) / n
    return torch.softmax(beta * sims, dim=0)


def predict_pool_bsc(ctxs, pool_vecs, pool_labels, pool_used, beta):
    """Pool retrieval via real-valued cosine."""
    B = ctxs.shape[0]
    if pool_used == 0:
        return torch.full((VOCAB_SIZE, B), 1.0 / VOCAB_SIZE, device=ctxs.device)
    n = ctxs.shape[1]
    active = pool_vecs[:pool_used]
    labels = pool_labels[:pool_used]
    sims = (active @ ctxs.T) / n
    weights = torch.softmax(beta * sims, dim=0)
    P_retr = torch.zeros(VOCAB_SIZE, B, device=ctxs.device)
    P_retr.scatter_add_(0, labels.unsqueeze(1).expand(-1, B), weights)
    return P_retr


def run_config(variant, train, test):
    use_relu = "relu" in variant and "no_relu" not in variant
    signed_bundle = "signed" in variant

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
            ctxs = build_ctx_bundles_bsc(byte_atoms, pos_atoms, idx_batch, signed_bundle)
            P_W = predict_W_bsc(W, ctxs, byte_atoms, BETA, use_relu)
            # Hebbian delta update
            targets = byte_atoms[tgt_batch]  # (B, N) ±1
            expected = P_W.T @ byte_atoms     # (B, V) @ (V, N) = (B, N)
            errors = targets - expected
            dW = errors.T @ ctxs / N
            if DECAY > 0:
                W.mul_(1.0 - DECAY)
            W.add_(dW, alpha=AROUSAL)
            if epoch == 1:
                dest = (pool_idx + arange_b[:B]) % POOL_SIZE
                pool_vecs.index_copy_(0, dest, ctxs)
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
                ctxs = build_ctx_bundles_bsc(byte_atoms, pos_atoms, test_idx[bs:be], signed_bundle)
                P_W = predict_W_bsc(W, ctxs, byte_atoms, BETA, use_relu)
                P_retr = predict_pool_bsc(ctxs, pool_vecs, pool_labels, pool_used, BETA)
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
            _say(f"    [{variant}] ep={epoch}  bpc={test_bpc:.4f}  arg={argmax_acc:.4f}  "
                 f"poolT1={pool_acc:.3f}  wT1={w_acc:.3f}  ||W||={w_frob:.1f}  ({elapsed:.1f}s)")
    return {"variant": variant, "history": history}


def main() -> None:
    _say("Loading corpus...")
    corpus = load_corpus()
    cut = int(len(corpus) * 0.8)
    train, test = corpus[:cut], corpus[cut:]
    _say(f"  train={len(train)}, test={len(test)} bytes")
    _say(f"\nBSC substrate port — brain-closer basis experiment")
    _say(f"  N={N}, K={K}, arousal={AROUSAL}, beta={BETA}, decay={DECAY}, pool={POOL_SIZE}")
    _say(f"  variants: {VARIANTS}")
    _say(f"  Reference (FHRR combined+modReLU): 2.4994")
    _say(f"  Lit: Kanerva 2009 'HD computing introduction'; Plate 2003 BSC")
    _say(f"  Hypothesis: BSC could outperform OR underperform; both are informative")

    all_results = []
    t_all = time.perf_counter()
    for variant in VARIANTS:
        _say(f"\n--- {variant} ---")
        t0 = time.perf_counter()
        r = run_config(variant, train, test)
        r["wall_time_s"] = time.perf_counter() - t0
        all_results.append(r)
        best = min(r["history"], key=lambda h: h["test_bpc"])
        _say(f"  Best for {variant}: ep={best['epoch']}, bpc={best['test_bpc']:.4f}")

    _say(f"\n========= SUMMARY =========")
    _say(f"{'variant':>26s} {'best_ep':>8s} {'best_bpc':>10s} {'wT1':>6s} {'poolT1':>7s}")
    for r in all_results:
        best = min(r["history"], key=lambda h: h["test_bpc"])
        _say(f"{r['variant']:>26s} {best['epoch']:>8d} {best['test_bpc']:>10.4f} "
             f"{best['w_top1_acc']:>6.3f} {best['pool_top1_acc']:>7.3f}")
    _say(f"\n  Reference FHRR combined+modReLU: 2.4994")
    _say(f"  Best BSC variant delta vs FHRR: {min(r['history'], key=lambda h: h['test_bpc'])['test_bpc'] - 2.4994:+.4f} for {r['variant']}")

    out = {"seed": SEED, "n": N, "k": K, "arousal": AROUSAL, "beta": BETA, "decay": DECAY,
           "pool_size": POOL_SIZE, "alpha": ALPHA, "relu_b": RELU_B, "max_epochs": MAX_EPOCHS,
           "variants": VARIANTS, "results": all_results, "substrate": "BSC",
           "wall_time_total_s": time.perf_counter() - t_all}
    out_path = Path(__file__).resolve().parent.parent / "data" / "exp_bsc_charlm"
    out_path.mkdir(parents=True, exist_ok=True)
    (out_path / "metrics.json").write_text(json.dumps(out, indent=2, default=str))
    _say(f"\nWrote {out_path / 'metrics.json'}")


if __name__ == "__main__":
    main()
