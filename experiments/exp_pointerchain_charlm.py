"""Track 0.1b: pointer-chain HDC character LM (batched).

Same byte-level setup as exp_pure_hebbian_charlm, augmented with an addressable
ring-buffer pool of past (context-bundle, next-byte) pairs. At prediction time we
mix the connection-matrix prediction with a retrieval distribution derived from the
pool. Tests whether effective context length can grow without inflating the bundled
working memory.

Pre-registered in notes/exp_track0_1b.md. Uses the same batched inner-loop optimization
as the main Hebbian-VSA experiment; within a batch, all positions see the same W
AND the same pool snapshot.
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
AROUSAL_BEST = 0.3
BETA_BEST = 8.0
BATCH_SIZE = 64

POOL_SIZES = [64, 256, 1024]
ALPHAS = [0.3, 0.5, 0.7, 1.0]


def _say(msg: str) -> None:
    print(msg, flush=True)


def load_corpus() -> bytes:
    repo = Path(__file__).resolve().parent.parent
    files = [
        repo / "PLAN.md",
        repo / "NEXT_PHASE.md",
        repo / "README.md",
        repo / "PROGRESS.md",
        repo / "RESULTS.md",
        repo / "CLAUDE.md",
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


def _build_context_bundles_batch(
    byte_atoms: torch.Tensor,
    pos_atoms: torch.Tensor,
    indices: torch.Tensor,
) -> torch.Tensor:
    bound = byte_atoms[indices] * pos_atoms.unsqueeze(0)
    summed = bound.sum(dim=1)
    mag = summed.abs().clamp(min=1e-8)
    return summed / mag.to(summed.dtype)


def _predict_W_batch(
    W: torch.Tensor, ctxs: torch.Tensor, byte_atoms: torch.Tensor, beta: float
) -> torch.Tensor:
    n = ctxs.shape[1]
    q = ctxs @ W.T
    sims = (byte_atoms.conj() @ q.T).real / n
    return torch.softmax(beta * sims, dim=0)


def _predict_pool_batch(
    ctxs: torch.Tensor,  # (B, N)
    pool_vecs: torch.Tensor,  # (M, N)
    pool_labels: torch.Tensor,  # (M,)
    pool_used: int,
    beta: float,
) -> torch.Tensor:
    """Returns (V, B) retrieval distribution per batch position."""
    B = ctxs.shape[0]
    if pool_used == 0:
        return torch.full((VOCAB_SIZE, B), 1.0 / VOCAB_SIZE, device=ctxs.device)
    n = ctxs.shape[1]
    active = pool_vecs[:pool_used]  # (M_a, N)
    labels = pool_labels[:pool_used]  # (M_a,)
    sims = (active.conj() @ ctxs.T).real / n  # (M_a, B)
    weights = torch.softmax(beta * sims, dim=0)  # (M_a, B)
    P_retr = torch.zeros(VOCAB_SIZE, B, device=ctxs.device)
    P_retr.scatter_add_(0, labels.unsqueeze(1).expand(-1, B), weights)
    return P_retr


def train_pointerchain_vsa(
    train: bytes,
    test: bytes,
    n: int,
    k: int,
    arousal: float,
    beta: float,
    pool_size: int,
    alpha: float,
    seed: int,
    label: str = "",
    batch_size: int = BATCH_SIZE,
) -> dict:
    quiet = tracing.TraceBus(enabled=False)
    with tracing.using(quiet):
        gen = torch.Generator().manual_seed(seed)
        byte_atoms = torch.stack([atoms.make_atom_fhrr(n, gen) for _ in range(VOCAB_SIZE)]).to(DEVICE)
        pos_atoms = torch.stack([atoms.make_atom_fhrr(n, gen) for _ in range(k)]).to(DEVICE)

        W = torch.zeros((n, n), dtype=torch.complex64, device=DEVICE)
        pool_vecs = torch.zeros((pool_size, n), dtype=torch.complex64, device=DEVICE)
        pool_labels = torch.zeros(pool_size, dtype=torch.long, device=DEVICE)
        pool_used = 0
        pool_idx = 0

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
        total_surprise_bits = 0.0
        n_seen = 0

        for batch_start in range(0, T_total, batch_size):
            batch_end = min(batch_start + batch_size, T_total)
            idx_batch = train_idx[batch_start:batch_end]
            tgt_batch = train_targets[batch_start:batch_end]
            B = idx_batch.shape[0]

            ctxs = _build_context_bundles_batch(byte_atoms, pos_atoms, idx_batch)
            P_W = _predict_W_batch(W, ctxs, byte_atoms, beta)
            P_retr = _predict_pool_batch(ctxs, pool_vecs, pool_labels, pool_used, beta)
            P = alpha * P_retr + (1.0 - alpha) * P_W  # (V, B)

            p_true = P.gather(0, tgt_batch.unsqueeze(0)).squeeze(0).clamp(min=1e-12)
            total_surprise_bits += float(-torch.log2(p_true).sum())
            n_seen += B

            # Delta-rule update on W using P_W (so W learns independently of pool).
            targets = byte_atoms[tgt_batch]
            expected = P_W.T.to(byte_atoms.dtype) @ byte_atoms
            errors = targets - expected
            dW = errors.T @ ctxs.conj() / n
            W.add_(dW, alpha=arousal)

            # Pool update: write the batch's contexts and targets into ring slots.
            for b in range(B):
                pool_vecs[pool_idx] = ctxs[b]
                pool_labels[pool_idx] = tgt_batch[b]
                pool_idx = (pool_idx + 1) % pool_size
                pool_used = min(pool_used + 1, pool_size)

            if batch_start <= T_total // 2 < batch_end:
                elapsed = time.perf_counter() - t_start
                _say(f"    [{label}] 50%  rolling_bpc={total_surprise_bits/max(n_seen,1):.3f}  elapsed={elapsed:.1f}s")

        # Eval (W and pool frozen).
        T_test = len(padded_test) - k
        offsets = torch.arange(k - 1, -1, -1, device=DEVICE)
        positions = torch.arange(T_test, device=DEVICE)
        test_idx = test_bytes[positions.unsqueeze(1) + offsets.unsqueeze(0)]
        test_targets = test_bytes[positions + k]

        total_test_bits = 0.0
        for bs in range(0, T_test, batch_size):
            be = min(bs + batch_size, T_test)
            ctxs = _build_context_bundles_batch(byte_atoms, pos_atoms, test_idx[bs:be])
            P_W = _predict_W_batch(W, ctxs, byte_atoms, beta)
            P_retr = _predict_pool_batch(ctxs, pool_vecs, pool_labels, pool_used, beta)
            P = alpha * P_retr + (1.0 - alpha) * P_W
            p_true = P.gather(0, test_targets[bs:be].unsqueeze(0)).squeeze(0).clamp(min=1e-12)
            total_test_bits += float(-torch.log2(p_true).sum())
        test_bpc = total_test_bits / max(T_test, 1)

        T_eval = min(5000, T_total)
        total_train_bits = 0.0
        for bs in range(0, T_eval, batch_size):
            be = min(bs + batch_size, T_eval)
            ctxs = _build_context_bundles_batch(byte_atoms, pos_atoms, train_idx[bs:be])
            P_W = _predict_W_batch(W, ctxs, byte_atoms, beta)
            P_retr = _predict_pool_batch(ctxs, pool_vecs, pool_labels, pool_used, beta)
            P = alpha * P_retr + (1.0 - alpha) * P_W
            p_true = P.gather(0, train_targets[bs:be].unsqueeze(0)).squeeze(0).clamp(min=1e-12)
            total_train_bits += float(-torch.log2(p_true).sum())
        train_bpc = total_train_bits / max(T_eval, 1)

        return {
            "k": k,
            "arousal": arousal,
            "beta": beta,
            "pool_size": pool_size,
            "alpha": alpha,
            "seed": seed,
            "n_substrate": n,
            "batch_size": batch_size,
            "train_bpc": train_bpc,
            "test_bpc": test_bpc,
            "train_test_gap": test_bpc - train_bpc,
            "final_pool_used": pool_used,
        }


def main() -> None:
    _say("Loading corpus...")
    corpus = load_corpus()
    train, test = train_test_split(corpus, train_frac=0.8)
    _say(f"  Corpus: {len(corpus)} bytes; train={len(train)}, test={len(test)}")

    uni = unigram_model(train)
    uni_test_bpc = bits_per_char_unigram(uni, test)
    _say(f"\nBaselines:")
    _say(f"  Unigram:                 {uni_test_bpc:.4f}")
    _say(f"  Hebbian-VSA (Track 0.1): 3.16  (batched reference, no pool)")
    _say(f"  Tiny transformer:        2.39  (reference ceiling)")

    total_configs = len(POOL_SIZES) * len(ALPHAS)
    _say(f"\nPointer-chain sweep (N={N_SUBSTRATE}, K={K_BEST}, arousal={AROUSAL_BEST}, beta={BETA_BEST}, batch={BATCH_SIZE}):")
    _say(f"  {total_configs} configs running sequentially")

    results: list[dict] = []
    t_start = time.perf_counter()
    idx = 0
    for pool_size in POOL_SIZES:
        for alpha in ALPHAS:
            idx += 1
            label = f"cfg {idx}/{total_configs} M={pool_size} a={alpha}"
            _say(f"\n  Starting {label}")
            t0 = time.perf_counter()
            r = train_pointerchain_vsa(
                train, test, N_SUBSTRATE, K_BEST, AROUSAL_BEST, BETA_BEST,
                pool_size, alpha, SEED, label=label,
            )
            r["wall_time_s"] = time.perf_counter() - t0
            results.append(r)
            _say(
                f"  DONE {label}  test_bpc={r['test_bpc']:.4f}  gap={r['train_test_gap']:+.3f}  "
                f"({r['wall_time_s']:.1f}s)"
            )
    total_wall = time.perf_counter() - t_start

    results.sort(key=lambda r: r["test_bpc"])
    best = results[0]
    _say(f"\nBest config: pool_size={best['pool_size']}, alpha={best['alpha']}")
    _say(f"  Pointer-chain test bits/char = {best['test_bpc']:.4f}")
    _say(f"  vs Hebbian-VSA (no pool, batched ref) = 3.16")
    _say(f"  vs Tiny transformer (best)            = 2.39")

    hebbian_ref = 3.16
    if best["test_bpc"] < hebbian_ref - 0.5:
        verdict = "ADDRESSING WORKS: pointer-chain beats single-bundle Hebbian by >0.5 bits/char"
    elif best["test_bpc"] < hebbian_ref - 0.1:
        verdict = "Marginal improvement: pointer-chain helps but not dramatically"
    elif best["test_bpc"] < hebbian_ref + 0.1:
        verdict = "Roughly tied with single-bundle Hebbian (pool not helping)"
    else:
        verdict = "Pointer-chain WORSE than single-bundle (unexpected)"
    _say(f"\nPre-registered verdict: {verdict}")

    _say(f"\nFull ranking (best -> worst by test_bpc):")
    for r in results:
        _say(
            f"  M={r['pool_size']:4d} a={r['alpha']:.1f}  test_bpc={r['test_bpc']:.4f}  "
            f"gap={r['train_test_gap']:+.3f}"
        )
    _say(f"\nTotal wall time: {total_wall:.1f}s")

    out = {
        "n_substrate": N_SUBSTRATE,
        "k": K_BEST,
        "arousal": AROUSAL_BEST,
        "beta": BETA_BEST,
        "seed": SEED,
        "batch_size": BATCH_SIZE,
        "sweep_results": results,
        "best_config": {
            "pool_size": best["pool_size"],
            "alpha": best["alpha"],
            "test_bpc": best["test_bpc"],
            "train_bpc": best["train_bpc"],
        },
        "reference_hebbian_vsa_batched": 3.16,
        "reference_tiny_transformer": 2.39,
        "verdict": verdict,
        "headline": f"Pointer-chain best test bpc = {best['test_bpc']:.3f} vs Hebbian-VSA = 3.16, transformer = 2.39",
    }

    out_path = Path(__file__).resolve().parent.parent / "data" / "exp_pointerchain_charlm"
    out_path.mkdir(parents=True, exist_ok=True)
    (out_path / "metrics.json").write_text(json.dumps(out, indent=2, default=str))
    _say(f"\nWrote {out_path / 'metrics.json'}")


if __name__ == "__main__":
    main()
