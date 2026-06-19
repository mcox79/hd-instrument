"""Track 0.1 v2: targeted architectural improvements on the Hebbian-VSA character LM.

Tests three improvements over the Track 0.1 baseline (3.16 bits/char) without
adding backprop or pointer-chain:

1. Larger substrate (N): more dimensions = less bundling crosstalk.
2. Surprise-modulated arousal: effective learning rate scales with current
   prediction surprise (high surprise -> learn more; low surprise -> learn less).
   Biologically motivated by NE/dopamine phasic responses.
3. Homeostatic multiplicative decay on W: W <- (1 - decay) * W each batch.
   Prevents drift; analog of Turrigiano synaptic scaling.

Sweep configs probe each individually and in combination. Compared to baseline
3.16 (N=1024, no surprise modulation, no decay) and to transformer ceiling 2.39.
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
VOCAB_SIZE = 256
PAD_BYTE = 0
K_BEST = 4
AROUSAL_BASE = 0.3
BETA = 8.0
BATCH_SIZE = 64
SURPRISE_REF_BITS = 2.0  # reference surprise level for modulation factor

# Sweep configurations. Each: (label, N, surprise_scale, decay).
CONFIGS = [
    ("A baseline N=1024",              1024, 0.0,  0.0),
    ("B larger N=2048",                2048, 0.0,  0.0),
    ("C larger N=4096",                4096, 0.0,  0.0),
    ("D surprise mod, N=1024",         1024, 1.0,  0.0),
    ("E decay, N=1024",                1024, 0.0,  1e-4),
    ("F surprise+decay, N=1024",       1024, 1.0,  1e-4),
    ("G surprise+decay, N=2048",       2048, 1.0,  1e-4),
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


def train_test_split(corpus: bytes, train_frac: float = 0.8) -> tuple[bytes, bytes]:
    cut = int(len(corpus) * train_frac)
    return corpus[:cut], corpus[cut:]


def unigram_model(train: bytes) -> dict[int, float]:
    counts = Counter(train)
    total = len(train) + VOCAB_SIZE
    return {b: (counts.get(b, 0) + 1) / total for b in range(VOCAB_SIZE)}


def bits_per_char_unigram(probs: dict[int, float], test: bytes) -> float:
    return -sum(math.log2(probs[b]) for b in test) / len(test)


def _build_context_bundles_batch(byte_atoms, pos_atoms, indices):
    bound = byte_atoms[indices] * pos_atoms.unsqueeze(0)
    summed = bound.sum(dim=1)
    mag = summed.abs().clamp(min=1e-8)
    return summed / mag.to(summed.dtype)


def _predict_batch(W, ctxs, byte_atoms, beta):
    n = ctxs.shape[1]
    q = ctxs @ W.T
    sims = (byte_atoms.conj() @ q.T).real / n
    return torch.softmax(beta * sims, dim=0)


def train_hebbian_v2(
    train, test, n, k, arousal_base, beta, surprise_scale, decay, seed, label="",
    batch_size=BATCH_SIZE,
):
    quiet = tracing.TraceBus(enabled=False)
    with tracing.using(quiet):
        gen = torch.Generator().manual_seed(seed)
        byte_atoms = torch.stack([atoms.make_atom_fhrr(n, gen) for _ in range(VOCAB_SIZE)]).to(DEVICE)
        pos_atoms = torch.stack([atoms.make_atom_fhrr(n, gen) for _ in range(k)]).to(DEVICE)
        W = torch.zeros((n, n), dtype=torch.complex64, device=DEVICE)

        pad = bytes([PAD_BYTE]) * k
        padded_train = pad + train
        padded_test = pad + test

        T_total = len(padded_train) - k
        train_bytes = torch.tensor(list(padded_train), dtype=torch.long).to(DEVICE)
        test_bytes = torch.tensor(list(padded_test), dtype=torch.long).to(DEVICE)

        offsets = torch.arange(k - 1, -1, -1, device=DEVICE)
        positions = torch.arange(T_total, device=DEVICE)
        train_idx = train_bytes[positions.unsqueeze(1) + offsets.unsqueeze(0)]
        train_targets = train_bytes[positions + k]

        t_start = time.perf_counter()
        total_bits_seen = 0.0
        n_seen = 0
        applied_arousals: list[float] = []

        for batch_start in range(0, T_total, batch_size):
            batch_end = min(batch_start + batch_size, T_total)
            idx_batch = train_idx[batch_start:batch_end]
            tgt_batch = train_targets[batch_start:batch_end]
            B = idx_batch.shape[0]

            ctxs = _build_context_bundles_batch(byte_atoms, pos_atoms, idx_batch)
            probs = _predict_batch(W, ctxs, byte_atoms, beta)
            p_true = probs.gather(0, tgt_batch.unsqueeze(0)).squeeze(0).clamp(min=1e-12)
            batch_bits = float(-torch.log2(p_true).sum())
            total_bits_seen += batch_bits
            n_seen += B

            # Surprise-modulated arousal: scale base arousal by batch surprise relative to a reference.
            mean_surp_bits = batch_bits / B
            mod_factor = max(0.1, min(3.0, mean_surp_bits / SURPRISE_REF_BITS))
            effective_arousal = arousal_base * (1.0 + surprise_scale * (mod_factor - 1.0))
            applied_arousals.append(effective_arousal)

            # Delta-rule update with homeostatic decay.
            targets = byte_atoms[tgt_batch]
            expected = probs.T.to(byte_atoms.dtype) @ byte_atoms
            errors = targets - expected
            dW = errors.T @ ctxs.conj() / n

            if decay > 0:
                W.mul_(1.0 - decay)
            W.add_(dW, alpha=effective_arousal)

            if batch_start <= T_total // 2 < batch_end:
                elapsed = time.perf_counter() - t_start
                _say(
                    f"    [{label}] 50%  rolling_bpc={total_bits_seen/max(n_seen,1):.3f}  "
                    f"effective_arousal_mean={sum(applied_arousals)/len(applied_arousals):.3f}  "
                    f"elapsed={elapsed:.1f}s"
                )

        # Eval (W frozen).
        T_test = len(padded_test) - k
        offsets = torch.arange(k - 1, -1, -1, device=DEVICE)
        positions = torch.arange(T_test, device=DEVICE)
        test_idx = test_bytes[positions.unsqueeze(1) + offsets.unsqueeze(0)]
        test_targets = test_bytes[positions + k]

        total_test_bits = 0.0
        for bs in range(0, T_test, batch_size):
            be = min(bs + batch_size, T_test)
            ctxs = _build_context_bundles_batch(byte_atoms, pos_atoms, test_idx[bs:be])
            probs = _predict_batch(W, ctxs, byte_atoms, beta)
            p_true = probs.gather(0, test_targets[bs:be].unsqueeze(0)).squeeze(0).clamp(min=1e-12)
            total_test_bits += float(-torch.log2(p_true).sum())
        test_bpc = total_test_bits / max(T_test, 1)

        T_eval = min(5000, T_total)
        total_train_bits = 0.0
        for bs in range(0, T_eval, batch_size):
            be = min(bs + batch_size, T_eval)
            ctxs = _build_context_bundles_batch(byte_atoms, pos_atoms, train_idx[bs:be])
            probs = _predict_batch(W, ctxs, byte_atoms, beta)
            p_true = probs.gather(0, train_targets[bs:be].unsqueeze(0)).squeeze(0).clamp(min=1e-12)
            total_train_bits += float(-torch.log2(p_true).sum())
        train_bpc = total_train_bits / max(T_eval, 1)

        return {
            "n_substrate": n,
            "k": k,
            "arousal_base": arousal_base,
            "beta": beta,
            "surprise_scale": surprise_scale,
            "decay": decay,
            "seed": seed,
            "batch_size": batch_size,
            "train_bpc": train_bpc,
            "test_bpc": test_bpc,
            "train_test_gap": test_bpc - train_bpc,
            "mean_effective_arousal": sum(applied_arousals) / max(len(applied_arousals), 1),
            "final_w_frobenius": float(W.abs().pow(2).sum().sqrt()),
        }


def main() -> None:
    _say("Loading corpus...")
    corpus = load_corpus()
    train, test = train_test_split(corpus, train_frac=0.8)
    _say(f"  Corpus: {len(corpus)} bytes; train={len(train)}, test={len(test)}")

    uni = unigram_model(train)
    uni_test_bpc = bits_per_char_unigram(uni, test)
    _say(f"\nBaselines on identical split:")
    _say(f"  Unigram:                                       {uni_test_bpc:.4f}")
    _say(f"  Hebbian-VSA baseline (Track 0.1, N=1024):      3.16  (reference)")
    _say(f"  Pointer-chain best (Track 0.1b, M=1024 a=0.3): 2.91  (architecture extension)")
    _say(f"  Tiny transformer (best stopped):               2.39  (ceiling)")

    _say(f"\nv2 sweep: N, surprise modulation, homeostatic decay")
    _say(f"  K={K_BEST}, beta={BETA}, arousal_base={AROUSAL_BASE}, batch={BATCH_SIZE}, seed={SEED}")
    _say(f"  Surprise modulation: effective_arousal = base * (1 + scale * (surp/{SURPRISE_REF_BITS} - 1))")

    results: list[dict] = []
    t_start = time.perf_counter()
    for label, n, surp_scale, decay in CONFIGS:
        _say(f"\n  Starting {label}  (N={n}, surp_scale={surp_scale}, decay={decay})")
        t0 = time.perf_counter()
        r = train_hebbian_v2(
            train, test, n, K_BEST, AROUSAL_BASE, BETA, surp_scale, decay, SEED, label=label,
        )
        r["wall_time_s"] = time.perf_counter() - t0
        r["config_label"] = label
        results.append(r)
        _say(
            f"  DONE {label}  test_bpc={r['test_bpc']:.4f}  gap={r['train_test_gap']:+.3f}  "
            f"mean_arousal={r['mean_effective_arousal']:.3f}  ({r['wall_time_s']:.1f}s)"
        )
    total_wall = time.perf_counter() - t_start

    results.sort(key=lambda r: r["test_bpc"])
    best = results[0]
    _say(f"\nBest config: {best['config_label']}")
    _say(f"  test bits/char = {best['test_bpc']:.4f}")
    _say(f"  vs Hebbian-VSA baseline = 3.16  (delta = {3.16 - best['test_bpc']:+.3f})")
    _say(f"  vs pointer-chain best   = 2.91  (delta = {2.91 - best['test_bpc']:+.3f})")
    _say(f"  vs transformer ceiling  = 2.39  (gap = {best['test_bpc'] - 2.39:.3f})")

    _say(f"\nFull ranking (best -> worst by test_bpc):")
    for r in results:
        _say(
            f"  {r['config_label']:30s}  N={r['n_substrate']:4d}  "
            f"surp={r['surprise_scale']:.1f} decay={r['decay']:.0e}  "
            f"test_bpc={r['test_bpc']:.4f}  gap={r['train_test_gap']:+.3f}"
        )

    _say(f"\nTotal wall time: {total_wall:.1f}s")

    out = {
        "seed": SEED,
        "k": K_BEST,
        "beta": BETA,
        "arousal_base": AROUSAL_BASE,
        "batch_size": BATCH_SIZE,
        "sweep_results": results,
        "best_config": {
            "label": best["config_label"],
            "n_substrate": best["n_substrate"],
            "surprise_scale": best["surprise_scale"],
            "decay": best["decay"],
            "test_bpc": best["test_bpc"],
            "train_bpc": best["train_bpc"],
        },
        "references": {
            "hebbian_v1_baseline": 3.16,
            "pointer_chain_best": 2.91,
            "tiny_transformer_best": 2.39,
            "unigram": uni_test_bpc,
        },
        "headline": f"v2 best test bpc = {best['test_bpc']:.3f} ({best['config_label']}) vs baseline 3.16, transformer 2.39",
    }

    out_path = Path(__file__).resolve().parent.parent / "data" / "exp_hebbian_v2_charlm"
    out_path.mkdir(parents=True, exist_ok=True)
    (out_path / "metrics.json").write_text(json.dumps(out, indent=2, default=str))
    _say(f"\nWrote {out_path / 'metrics.json'}")


if __name__ == "__main__":
    main()
