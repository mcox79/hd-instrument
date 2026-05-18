"""DeltaNet explicit-erase variants vs. our softmax-cleaned delta rule.

Citation: Yang et al. arXiv 2406.06484 "Parallelizing Linear Transformers with
the Delta Rule" (DeltaNet, 2024). Their update: W_new = W (I - k k^T) + v k^T,
i.e. W += (v - W k) k^T. This is a delta rule with explicit erase of the
previous value at key k, no softmax in the loop.

Our current update (combined+modReLU baseline, 2.4994 bpc):
  q = W @ ctx
  q = modReLU(q, b=0.5)
  P_W = softmax(beta * sim(byte_atoms, q))
  expected = P_W.T @ byte_atoms     # probability-weighted byte codebook avg
  err = target_atom - expected
  dW = err ⊗ ctx.conj() / N
  W = (1-decay) W + alpha * dW

The error here is a *cleaned* error in codebook space: the readout is projected
through softmax over the 256-byte codebook, giving an "expected next byte
atom". DeltaNet's update is a *raw* readout error: target - W @ ctx, with no
cleanup.

Hypothesis: cleaned-error update should be more sample-efficient on small data
(codebook prior reduces variance), but DeltaNet-style raw error may push W
further off a degenerate solution at convergence. Run both and compare.

Variants:
  A. baseline_cleaned        — current best (softmax cleanup, modReLU)
  B. raw_delta               — DeltaNet-style: err = target - W @ ctx
                              (no modReLU, no softmax cleanup)
  C. raw_delta_with_modrelu  — DeltaNet-style with modReLU on readout
  D. pure_hebbian            — no error subtraction: dW = target ⊗ ctx
                              (just the simplest associative rule, control)
  E. cleaned_no_modrelu      — softmax cleanup but no modReLU
                              (isolates whether the gain is from modReLU or cleanup)
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import torch

from hdlab import atoms, tracing


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

VARIANTS = [
    "baseline_cleaned",
    "raw_delta",
    "raw_delta_with_modrelu",
    "pure_hebbian",
    "cleaned_no_modrelu",
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


def _build_context_bundles_batch(byte_atoms, pos_atoms, indices):
    bound = byte_atoms[indices] * pos_atoms.unsqueeze(0)
    summed = bound.sum(dim=1)
    mag = summed.abs().clamp(min=1e-8)
    return summed / mag.to(summed.dtype)


def magnitude_relu(q, b):
    eps = 1e-9
    mag = q.abs().clamp(min=eps)
    new_mag = torch.clamp(mag - b, min=0.0)
    return q * (new_mag / mag).to(q.dtype)


def _readout(W, ctxs, use_modrelu):
    q = ctxs @ W.T
    if use_modrelu:
        q = magnitude_relu(q, RELU_B)
    return q


def _predict_from_readout(q, byte_atoms, beta):
    n = q.shape[1]
    sims = (byte_atoms.conj() @ q.T).real / n
    return torch.softmax(beta * sims, dim=0)


def _predict_pool_batch(ctxs, pool_vecs, pool_labels, pool_used, beta):
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


def compute_dW(variant, W, ctxs, tgt_byte_atoms, byte_atoms, beta, n):
    """Return dW per the variant's update rule."""
    if variant == "baseline_cleaned":
        q = _readout(W, ctxs, use_modrelu=True)
        P = _predict_from_readout(q, byte_atoms, beta)
        expected = P.T.to(byte_atoms.dtype) @ byte_atoms
        err = tgt_byte_atoms - expected
        return err.T @ ctxs.conj() / n
    if variant == "raw_delta":
        q = _readout(W, ctxs, use_modrelu=False)
        err = tgt_byte_atoms - q
        return err.T @ ctxs.conj() / n
    if variant == "raw_delta_with_modrelu":
        q = _readout(W, ctxs, use_modrelu=True)
        err = tgt_byte_atoms - q
        return err.T @ ctxs.conj() / n
    if variant == "pure_hebbian":
        return tgt_byte_atoms.T @ ctxs.conj() / n
    if variant == "cleaned_no_modrelu":
        q = _readout(W, ctxs, use_modrelu=False)
        P = _predict_from_readout(q, byte_atoms, beta)
        expected = P.T.to(byte_atoms.dtype) @ byte_atoms
        err = tgt_byte_atoms - expected
        return err.T @ ctxs.conj() / n
    raise ValueError(variant)


def _predict_W_eval(variant, W, ctxs, byte_atoms, beta):
    """Test-time readout, same as training for the variant."""
    use_modrelu = variant in ("baseline_cleaned", "raw_delta_with_modrelu")
    q = _readout(W, ctxs, use_modrelu=use_modrelu)
    return _predict_from_readout(q, byte_atoms, beta)


def run_config(variant, train, test):
    quiet = tracing.TraceBus(enabled=False)
    with tracing.using(quiet):
        gen = torch.Generator().manual_seed(SEED)
        byte_atoms = torch.stack([atoms.make_atom_fhrr(N, gen) for _ in range(VOCAB_SIZE)]).to(DEVICE)
        pos_atoms = torch.stack([atoms.make_atom_fhrr(N, gen) for _ in range(K)]).to(DEVICE)
        W = torch.zeros((N, N), dtype=torch.complex64, device=DEVICE)
        pool_vecs = torch.zeros((POOL_SIZE, N), dtype=torch.complex64, device=DEVICE)
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
                targets = byte_atoms[tgt_batch]
                dW = compute_dW(variant, W, ctxs, targets, byte_atoms, BETA, N)
                if DECAY > 0:
                    W.mul_(1.0 - DECAY)
                W.add_(dW, alpha=AROUSAL)
                if epoch == 1:
                    for b in range(B):
                        pool_vecs[pool_idx] = ctxs[b]
                        pool_labels[pool_idx] = tgt_batch[b]
                        pool_idx = (pool_idx + 1) % POOL_SIZE
                        pool_used = min(pool_used + 1, POOL_SIZE)

            if epoch in EPOCH_CHECKPOINTS:
                total_bits = 0.0
                argmax_correct = 0
                pool_top1_correct = 0
                w_top1_correct = 0
                for bs in range(0, T_test, BATCH_SIZE):
                    be = min(bs + BATCH_SIZE, T_test)
                    ctxs = _build_context_bundles_batch(byte_atoms, pos_atoms, test_idx[bs:be])
                    P_W = _predict_W_eval(variant, W, ctxs, byte_atoms, BETA)
                    P_retr = _predict_pool_batch(ctxs, pool_vecs, pool_labels, pool_used, BETA)
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
                w_frob = float(W.abs().pow(2).sum().sqrt())
                elapsed = time.perf_counter() - t_start
                history.append({
                    "epoch": epoch, "test_bpc": test_bpc,
                    "argmax_accuracy": argmax_acc, "pool_top1_acc": pool_acc,
                    "w_top1_acc": w_acc, "w_frob": w_frob, "wall_s": elapsed,
                })
                _say(f"    [{variant}] ep={epoch}  bpc={test_bpc:.4f}  arg={argmax_acc:.4f}  "
                     f"poolT1={pool_acc:.3f}  wT1={w_acc:.3f}  ||W||={w_frob:.1f}  ({elapsed:.1f}s)")
        return {"variant": variant, "history": history}


def main() -> None:
    _say("Loading corpus...")
    corpus = load_corpus()
    cut = int(len(corpus) * 0.8)
    train, test = corpus[:cut], corpus[cut:]
    _say(f"  train={len(train)}, test={len(test)} bytes")
    _say(f"\nDeltaNet variants vs softmax-cleaned delta rule")
    _say(f"  N={N}, K={K}, arousal={AROUSAL}, beta={BETA}, decay={DECAY}, pool={POOL_SIZE}, relu_b={RELU_B}")
    _say(f"  Reference: baseline_cleaned = 2.4994")
    _say(f"  Lit: Yang et al. 2024 DeltaNet (arXiv 2406.06484); raw error variant")

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
    _say(f"{'variant':>26s} {'best_ep':>8s} {'best_bpc':>10s} {'wT1':>6s} {'||W||':>8s}")
    for r in all_results:
        best = min(r["history"], key=lambda h: h["test_bpc"])
        _say(f"{r['variant']:>26s} {best['epoch']:>8d} {best['test_bpc']:>10.4f} "
             f"{best['w_top1_acc']:>6.3f} {best['w_frob']:>8.1f}")

    out = {"seed": SEED, "n": N, "k": K, "arousal": AROUSAL, "beta": BETA, "decay": DECAY,
           "pool_size": POOL_SIZE, "alpha": ALPHA, "relu_b": RELU_B, "max_epochs": MAX_EPOCHS,
           "variants": VARIANTS, "results": all_results,
           "wall_time_total_s": time.perf_counter() - t_all}
    out_path = Path(__file__).resolve().parent.parent / "data" / "exp_deltanet_variants_charlm"
    out_path.mkdir(parents=True, exist_ok=True)
    (out_path / "metrics.json").write_text(json.dumps(out, indent=2, default=str))
    _say(f"\nWrote {out_path / 'metrics.json'}")
    _say(f"Total wall: {time.perf_counter() - t_all:.1f}s")


if __name__ == "__main__":
    main()
