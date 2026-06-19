"""Dendritic nonlinearity on W readout — brain-inspired test.

Every biological neuron does nonlinear integration of inputs (Polsky-Mel-Schiller
2004 *Nat Neurosci*; Beniaguev-Segev-London 2021 *Neuron* — a single L5 pyramidal
needs a 5-8 layer TCN to mimic its input-output function).

Our W @ context is purely linear. Adding pointwise nonlinearity on q = W @ context
BEFORE the cleanup softmax should amplify correct matches and suppress noise.

This is NOT the same as Krotov polynomial cleanup (which failed). Krotov applies
nonlinearity to SIMILARITY scores (post-cleanup); this applies nonlinearity to
the W output VECTOR (pre-cleanup). Different failure modes.

For complex FHRR vectors we have several pointwise nonlinearity choices:
- magnitude_tanh: preserve phase, apply tanh to magnitude (caps mag growth)
- magnitude_relu: zero out small-magnitude components (modReLU-style)
- real_imag_tanh: tanh on real and imaginary parts independently
- magnitude_sigmoid: smooth gating on magnitude

Run on the best combined config (N=4096, pool, multi-epoch + decay), short epochs
to compare against the 2.505 bpc baseline.
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

# Nonlinearity variants to test. None = baseline (no nonlinearity, control).
NL_VARIANTS = [
    ("baseline_linear", None, 1.0),
    ("magnitude_tanh_alpha_1", "magnitude_tanh", 1.0),
    ("magnitude_tanh_alpha_3", "magnitude_tanh", 3.0),
    ("magnitude_relu_b_0.5", "magnitude_relu", 0.5),
    ("magnitude_sigmoid_alpha_2", "magnitude_sigmoid", 2.0),
    ("real_imag_tanh", "real_imag_tanh", 1.0),
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


def dendritic_nl(q: torch.Tensor, mode: str, alpha: float) -> torch.Tensor:
    """Pointwise dendritic-style nonlinearity on complex hypervector q.

    mode='magnitude_tanh': q' = q * tanh(alpha * |q|) / |q|  (preserves phase, caps magnitude)
    mode='magnitude_relu': q' = q * max(0, |q| - alpha) / |q|  (modReLU-style, zeros small mags)
    mode='magnitude_sigmoid': q' = q * sigmoid(alpha * (|q| - 0.5)) / |q|  (smooth gating)
    mode='real_imag_tanh': tanh on real and imag parts independently
    mode=None: identity (baseline)
    """
    if mode is None:
        return q
    eps = 1e-9
    if mode == "magnitude_tanh":
        mag = q.abs().clamp(min=eps)
        new_mag = torch.tanh(alpha * mag)
        return q * (new_mag / mag).to(q.dtype)
    elif mode == "magnitude_relu":
        mag = q.abs().clamp(min=eps)
        new_mag = torch.clamp(mag - alpha, min=0.0)
        return q * (new_mag / mag).to(q.dtype)
    elif mode == "magnitude_sigmoid":
        mag = q.abs().clamp(min=eps)
        new_mag = torch.sigmoid(alpha * (mag - 0.5)) * mag  # gate-like
        return q * (new_mag / mag).to(q.dtype)
    elif mode == "real_imag_tanh":
        return torch.complex(torch.tanh(alpha * q.real), torch.tanh(alpha * q.imag))
    else:
        raise ValueError(f"unknown nl mode: {mode}")


def _predict_W_batch(W, ctxs, byte_atoms, beta, nl_mode, nl_alpha):
    n = ctxs.shape[1]
    q = ctxs @ W.T
    q = dendritic_nl(q, nl_mode, nl_alpha)
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


def run_config(nl_label, nl_mode, nl_alpha, train, test):
    quiet = tracing.TraceBus(enabled=False)
    with tracing.using(quiet):
        gen = torch.Generator().manual_seed(SEED)
        byte_atoms = torch.stack([atoms.make_atom_fhrr(N_SUBSTRATE, gen) for _ in range(VOCAB_SIZE)]).to(DEVICE)
        pos_atoms = torch.stack([atoms.make_atom_fhrr(N_SUBSTRATE, gen) for _ in range(K)]).to(DEVICE)
        W = torch.zeros((N_SUBSTRATE, N_SUBSTRATE), dtype=torch.complex64, device=DEVICE)
        pool_vecs = torch.zeros((POOL_SIZE, N_SUBSTRATE), dtype=torch.complex64, device=DEVICE)
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
                P_W = _predict_W_batch(W, ctxs, byte_atoms, BETA, nl_mode, nl_alpha)
                targets = byte_atoms[tgt_batch]
                expected = P_W.T.to(byte_atoms.dtype) @ byte_atoms
                errors = targets - expected
                dW = errors.T @ ctxs.conj() / N_SUBSTRATE
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
                for bs in range(0, T_test, BATCH_SIZE):
                    be = min(bs + BATCH_SIZE, T_test)
                    ctxs = _build_context_bundles_batch(byte_atoms, pos_atoms, test_idx[bs:be])
                    P_W = _predict_W_batch(W, ctxs, byte_atoms, BETA, nl_mode, nl_alpha)
                    P_retr = _predict_pool_batch(ctxs, pool_vecs, pool_labels, pool_used, BETA)
                    P = ALPHA * P_retr + (1.0 - ALPHA) * P_W
                    p_true = P.gather(0, test_targets[bs:be].unsqueeze(0)).squeeze(0).clamp(min=1e-12)
                    total_bits += float(-torch.log2(p_true).sum())
                    argmax_pred = P.argmax(dim=0)
                    argmax_correct += int((argmax_pred == test_targets[bs:be]).sum())
                test_bpc = total_bits / max(T_test, 1)
                argmax_acc = argmax_correct / max(T_test, 1)
                w_norm = float(W.abs().pow(2).sum().sqrt())
                elapsed = time.perf_counter() - t_start
                history.append({"epoch": epoch, "test_bpc": test_bpc, "argmax_accuracy": argmax_acc, "w_frobenius": w_norm, "wall_s": elapsed})
                _say(f"    [{nl_label}] epoch={epoch}  test_bpc={test_bpc:.4f}  argmax={argmax_acc:.4f}  W_norm={w_norm:.1f}  ({elapsed:.1f}s)")

        return {"nl_label": nl_label, "nl_mode": nl_mode, "nl_alpha": nl_alpha, "history": history}


def main() -> None:
    _say("Loading corpus...")
    corpus = load_corpus()
    train, test = train_test_split(corpus, 0.8)
    _say(f"  train={len(train)}, test={len(test)} bytes")
    _say(f"\nDendritic nonlinearity sweep (N={N_SUBSTRATE}, K={K}, beta={BETA}, decay={DECAY})")
    _say(f"  pool_size={POOL_SIZE}, alpha={ALPHA}, max_epochs={MAX_EPOCHS}")
    _say(f"  Variants: {[v[0] for v in NL_VARIANTS]}")
    _say(f"\nReferences:")
    _say(f"  Combined baseline (this config, no NL, 5 epochs): 2.544 bpc (per session log)")
    _say(f"  Combined baseline (15 epochs converged):           2.505 bpc")
    _say(f"  Tiny transformer ceiling:                         2.39 bpc")

    all_results = []
    t_start = time.perf_counter()
    for nl_label, nl_mode, nl_alpha in NL_VARIANTS:
        _say(f"\n--- {nl_label} (mode={nl_mode}, alpha={nl_alpha}) ---")
        t0 = time.perf_counter()
        r = run_config(nl_label, nl_mode, nl_alpha, train, test)
        r["wall_time_s"] = time.perf_counter() - t0
        all_results.append(r)
        _say(f"  (config wall time: {r['wall_time_s']:.1f}s)")

    _say(f"\n========= SUMMARY (final epoch test_bpc) =========")
    _say(f"{'variant':30s} {'epoch1':>10s} {'epoch3':>10s} {'epoch5':>10s}")
    for r in all_results:
        h = r["history"]
        bpc_by_epoch = {hh["epoch"]: hh["test_bpc"] for hh in h}
        _say(
            f"{r['nl_label']:30s} "
            f"{bpc_by_epoch.get(1, float('nan')):>10.4f} "
            f"{bpc_by_epoch.get(3, float('nan')):>10.4f} "
            f"{bpc_by_epoch.get(5, float('nan')):>10.4f}"
        )

    # Find best across all epochs and variants.
    best = None
    for r in all_results:
        for h in r["history"]:
            if best is None or h["test_bpc"] < best["test_bpc"]:
                best = {**h, "nl_label": r["nl_label"], "nl_mode": r["nl_mode"], "nl_alpha": r["nl_alpha"]}
    _say(f"\nGlobal best: {best['nl_label']}, epoch={best['epoch']}, test_bpc={best['test_bpc']:.4f}")
    _say(f"  vs baseline (no NL, 5 epochs): 2.544 (delta {2.544 - best['test_bpc']:+.4f})")
    _say(f"  vs baseline (no NL, 15 epochs converged): 2.505 (delta {2.505 - best['test_bpc']:+.4f})")
    _say(f"  vs transformer ceiling 2.39: gap {best['test_bpc'] - 2.39:.4f}")

    _say(f"\nTotal wall time: {time.perf_counter() - t_start:.1f}s")

    out = {
        "seed": SEED, "n_substrate": N_SUBSTRATE, "k": K, "arousal": AROUSAL, "beta": BETA,
        "pool_size": POOL_SIZE, "alpha": ALPHA, "decay": DECAY, "max_epochs": MAX_EPOCHS,
        "variants": [{"label": v[0], "mode": v[1], "alpha": v[2]} for v in NL_VARIANTS],
        "results": all_results,
        "best": best,
        "headline": f"Dendritic NL best: {best['nl_label']} test_bpc={best['test_bpc']:.3f}",
    }
    out_path = Path(__file__).resolve().parent.parent / "data" / "exp_dendritic_nl_charlm"
    out_path.mkdir(parents=True, exist_ok=True)
    (out_path / "metrics.json").write_text(json.dumps(out, indent=2, default=str))
    _say(f"\nWrote {out_path / 'metrics.json'}")


if __name__ == "__main__":
    main()
