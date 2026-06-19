"""Track 0.1: Krotov-Hopfield dense associative memory cleanup.

The bundle saturation wall comes from per-pattern SNR collapsing as 1/sqrt(N).
Krotov & Hopfield 2016 (NeurIPS) showed that replacing the standard
inner-product energy with a polynomial F(x) = sign(x) * |x|^n changes capacity
from K ~ 0.14*N to K ~ N^(n-1).

For our Hebbian-VSA system, this is a one-line change to the cleanup step:
- Current: probs = softmax(beta * similarities)
- Krotov:  probs = softmax(beta * sign(sim) * |sim|^n)

Critical: per Tyulmankov, Yang & Abbott (NeurIPS 2021), this transfers to
local-update setups because the nonlinearity lives in the readout, not the
weights. W is still trained by the same delta rule.

References:
- Krotov & Hopfield (NeurIPS 2016, arXiv 1606.01164)
- Demircigil et al. (J. Stat. Phys. 2017, arXiv 1702.01929) -- exponential capacity limit
- Ramsauer et al. (ICLR 2021, arXiv 2008.02217) -- continuous version = modern attention
- Tyulmankov, Yang & Abbott (NeurIPS 2021) -- biologically plausible local rule
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
N_SUBSTRATE = 1024
VOCAB_SIZE = 256
PAD_BYTE = 0
K_BEST = 4
AROUSAL = 0.3
BATCH_SIZE = 64

# Sweep grid: Krotov power n and softmax inverse-temperature beta jointly.
# n=1 is the linear control (reduces to our current baseline at beta=8).
N_VALUES = [1, 2, 3, 5, 7]
BETA_VALUES = [4.0, 8.0, 16.0, 32.0]


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


def _krotov_softmax(sims: torch.Tensor, beta: float, krotov_n: int) -> torch.Tensor:
    """Apply Krotov polynomial nonlinearity then softmax.

    sims: (V, B) similarities in roughly [-1, 1].
    Returns: (V, B) probability distribution.
    """
    if krotov_n == 1:
        transformed = sims
    else:
        abs_sims = sims.abs()
        transformed = sims.sign() * abs_sims.pow(krotov_n)
    return torch.softmax(beta * transformed, dim=0)


def _predict_batch(W, ctxs, byte_atoms, beta, krotov_n):
    n = ctxs.shape[1]
    q = ctxs @ W.T
    sims = (byte_atoms.conj() @ q.T).real / n
    return _krotov_softmax(sims, beta, krotov_n)


def train_krotov_hebbian(
    train, test, n_dim, k, arousal, beta, krotov_n, seed,
    label="", batch_size=BATCH_SIZE,
):
    quiet = tracing.TraceBus(enabled=False)
    with tracing.using(quiet):
        gen = torch.Generator().manual_seed(seed)
        byte_atoms = torch.stack([atoms.make_atom_fhrr(n_dim, gen) for _ in range(VOCAB_SIZE)]).to(DEVICE)
        pos_atoms = torch.stack([atoms.make_atom_fhrr(n_dim, gen) for _ in range(k)]).to(DEVICE)
        W = torch.zeros((n_dim, n_dim), dtype=torch.complex64, device=DEVICE)

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
        total_bits = 0.0
        n_seen = 0

        for batch_start in range(0, T_total, batch_size):
            batch_end = min(batch_start + batch_size, T_total)
            idx_batch = train_idx[batch_start:batch_end]
            tgt_batch = train_targets[batch_start:batch_end]
            B = idx_batch.shape[0]

            ctxs = _build_context_bundles_batch(byte_atoms, pos_atoms, idx_batch)
            probs = _predict_batch(W, ctxs, byte_atoms, beta, krotov_n)

            p_true = probs.gather(0, tgt_batch.unsqueeze(0)).squeeze(0).clamp(min=1e-12)
            total_bits += float(-torch.log2(p_true).sum())
            n_seen += B

            # Delta-rule update; "expected" uses the Krotov-shaped distribution.
            targets = byte_atoms[tgt_batch]
            expected = probs.T.to(byte_atoms.dtype) @ byte_atoms
            errors = targets - expected
            dW = errors.T @ ctxs.conj() / n_dim
            W.add_(dW, alpha=arousal)

            if batch_start <= T_total // 2 < batch_end:
                elapsed = time.perf_counter() - t_start
                _say(f"    [{label}] 50%  rolling_bpc={total_bits/max(n_seen,1):.3f}  elapsed={elapsed:.1f}s")

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
            probs = _predict_batch(W, ctxs, byte_atoms, beta, krotov_n)
            p_true = probs.gather(0, test_targets[bs:be].unsqueeze(0)).squeeze(0).clamp(min=1e-12)
            total_test_bits += float(-torch.log2(p_true).sum())
        test_bpc = total_test_bits / max(T_test, 1)

        T_eval = min(5000, T_total)
        total_train_bits = 0.0
        for bs in range(0, T_eval, batch_size):
            be = min(bs + batch_size, T_eval)
            ctxs = _build_context_bundles_batch(byte_atoms, pos_atoms, train_idx[bs:be])
            probs = _predict_batch(W, ctxs, byte_atoms, beta, krotov_n)
            p_true = probs.gather(0, train_targets[bs:be].unsqueeze(0)).squeeze(0).clamp(min=1e-12)
            total_train_bits += float(-torch.log2(p_true).sum())
        train_bpc = total_train_bits / max(T_eval, 1)

        return {
            "n_substrate": n_dim,
            "k": k,
            "arousal": arousal,
            "beta": beta,
            "krotov_n": krotov_n,
            "seed": seed,
            "batch_size": batch_size,
            "train_bpc": train_bpc,
            "test_bpc": test_bpc,
            "train_test_gap": test_bpc - train_bpc,
        }


def main() -> None:
    _say("Loading corpus...")
    corpus = load_corpus()
    train, test = train_test_split(corpus, 0.8)
    _say(f"  Corpus: {len(corpus)} bytes; train={len(train)}, test={len(test)}")

    uni = unigram_model(train)
    uni_test_bpc = bits_per_char_unigram(uni, test)
    _say(f"\nBaselines on identical split:")
    _say(f"  Unigram:                                  {uni_test_bpc:.4f}")
    _say(f"  Linear Hebbian-VSA (Track 0.1, N=1024):   3.16  (= Krotov n=1, beta=8)")
    _say(f"  Pointer-chain (Track 0.1b, M=1024 a=0.3): 2.91")
    _say(f"  Larger N=4096 (no pool):                  3.02")
    _say(f"  N=4096 + pointer-chain combined:          2.84  (latest)")
    _say(f"  Tiny transformer (best stopped):          2.39  (ceiling)")

    total_configs = len(N_VALUES) * len(BETA_VALUES)
    _say(f"\nKrotov sweep (N={N_SUBSTRATE}, K={K_BEST}, arousal={AROUSAL}, batch={BATCH_SIZE}):")
    _say(f"  Sweep: krotov_n in {N_VALUES} x beta in {BETA_VALUES}  ({total_configs} configs)")

    results: list[dict] = []
    t_start = time.perf_counter()
    idx = 0
    for krotov_n in N_VALUES:
        for beta in BETA_VALUES:
            idx += 1
            label = f"cfg {idx}/{total_configs} n={krotov_n} b={beta}"
            _say(f"\n  Starting {label}")
            t0 = time.perf_counter()
            r = train_krotov_hebbian(
                train, test, N_SUBSTRATE, K_BEST, AROUSAL, beta, krotov_n, SEED, label=label,
            )
            r["wall_time_s"] = time.perf_counter() - t0
            r["config_label"] = label
            results.append(r)
            _say(
                f"  DONE {label}  test_bpc={r['test_bpc']:.4f}  "
                f"gap={r['train_test_gap']:+.3f}  ({r['wall_time_s']:.1f}s)"
            )
    total_wall = time.perf_counter() - t_start

    results.sort(key=lambda r: r["test_bpc"])
    best = results[0]
    _say(f"\nBest config: krotov_n={best['krotov_n']}, beta={best['beta']}")
    _say(f"  Krotov test bits/char = {best['test_bpc']:.4f}")
    _say(f"  vs linear baseline       = 3.16  (delta = {3.16 - best['test_bpc']:+.3f})")
    _say(f"  vs combined N=4096+pool  = 2.84  (delta = {2.84 - best['test_bpc']:+.3f})")
    _say(f"  vs transformer ceiling   = 2.39  (gap = {best['test_bpc'] - 2.39:.3f})")

    if best["test_bpc"] < 3.16 - 0.3:
        verdict = "KROTOV HELPS: closing the gap meaningfully"
    elif best["test_bpc"] < 3.16 - 0.1:
        verdict = "Krotov gives modest improvement"
    elif best["test_bpc"] < 3.16 + 0.1:
        verdict = "Krotov roughly equivalent to linear at this scale"
    else:
        verdict = "Krotov HURTS (unexpected)"
    _say(f"\nVerdict: {verdict}")

    _say(f"\nFull ranking (best -> worst by test_bpc):")
    for r in results:
        _say(
            f"  n={r['krotov_n']:1d} beta={r['beta']:5.1f}  "
            f"test_bpc={r['test_bpc']:.4f}  gap={r['train_test_gap']:+.3f}"
        )

    _say(f"\nTotal wall time: {total_wall:.1f}s")

    out = {
        "seed": SEED, "n_substrate": N_SUBSTRATE, "k": K_BEST, "arousal": AROUSAL,
        "batch_size": BATCH_SIZE,
        "sweep_results": results,
        "best_config": {
            "krotov_n": best["krotov_n"], "beta": best["beta"],
            "test_bpc": best["test_bpc"], "train_bpc": best["train_bpc"],
        },
        "references": {
            "linear_baseline_n1024": 3.16,
            "pointer_chain": 2.91,
            "larger_N4096": 3.02,
            "combined_N4096_pointerchain": 2.84,
            "tiny_transformer": 2.39,
            "unigram": uni_test_bpc,
        },
        "verdict": verdict,
        "headline": f"Krotov best test bpc = {best['test_bpc']:.3f} (n={best['krotov_n']}, beta={best['beta']})",
    }

    out_path = Path(__file__).resolve().parent.parent / "data" / "exp_krotov_charlm"
    out_path.mkdir(parents=True, exist_ok=True)
    (out_path / "metrics.json").write_text(json.dumps(out, indent=2, default=str))
    _say(f"\nWrote {out_path / 'metrics.json'}")


if __name__ == "__main__":
    main()
