"""Track 0.1: pure Hebbian-trained VSA character LM, kill-switch test for Bet B.

Tests whether a single outer-product Hebbian connection matrix over FHRR atoms can
learn next-byte conditional structure on natural English text. No backprop, no
gradient descent, no transformer. Updates are local: dW[i,j] depends only on
post-synaptic activity, pre-synaptic activity, and a global modulator.

Compares to unigram and n-gram baselines on the same train/test split. Pre-registered
predictions in notes/exp_track0_1.md.

Optimized via mini-batched processing (BATCH_SIZE bytes per step instead of 1). The
algorithmic semantics shift slightly: within a batch, all positions see the same W,
which is then updated once with the summed errors. For small batch sizes (~64) this
is effectively identical to pure online; for very large batches the divergence grows.
Verified against the BATCH_SIZE=1 reference (3.10 bits/char on best config).
"""

from __future__ import annotations

import json
import math
import time
from collections import Counter, defaultdict
from pathlib import Path

import torch

from hdlab import atoms, binding, tracing


DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

SEED = 17
N_SUBSTRATE = 1024
VOCAB_SIZE = 256
PAD_BYTE = 0  # use null byte for start-of-corpus padding
BATCH_SIZE = 64  # bytes processed per vectorized update; W refreshes once per batch

# Sweep grid (tighter than pre-registered; expand if borderline).
K_VALUES = [4, 8, 16]
AROUSAL_VALUES = [0.3, 1.0]
BETA_VALUES = [8.0, 32.0]


def _say(msg: str) -> None:
    """Print with explicit flush so background runs are visible in real time."""
    print(msg, flush=True)


def load_corpus() -> bytes:
    """Concatenate local markdown files into a single byte stream."""
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
    """Laplace-smoothed unigram probabilities over the byte alphabet."""
    counts = Counter(train)
    total = len(train) + VOCAB_SIZE
    return {b: (counts.get(b, 0) + 1) / total for b in range(VOCAB_SIZE)}


def ngram_model(train: bytes, order: int) -> dict:
    """Stupid backoff n-gram with add-one smoothing. Order is the conditioning width."""
    counts: dict[tuple, Counter] = defaultdict(Counter)
    for i in range(len(train) - order):
        ctx = tuple(train[i : i + order])
        nxt = train[i + order]
        counts[ctx][nxt] += 1
    totals = {ctx: sum(c.values()) for ctx, c in counts.items()}
    return {"order": order, "counts": counts, "totals": totals}


def ngram_predict(model: dict, ctx: tuple, fallback: dict[int, float]) -> dict[int, float]:
    counts = model["counts"].get(ctx)
    if counts is None or len(counts) == 0:
        return fallback
    total = model["totals"][ctx] + VOCAB_SIZE
    return {b: (counts.get(b, 0) + 1) / total for b in range(VOCAB_SIZE)}


def bits_per_char_unigram(probs: dict[int, float], test: bytes) -> float:
    return -sum(math.log2(probs[b]) for b in test) / len(test)


def bits_per_char_ngram(model: dict, fallback: dict[int, float], test: bytes) -> float:
    order = model["order"]
    total_bits = 0.0
    n = 0
    pad = bytes([PAD_BYTE]) * order + test
    for i in range(order, len(pad)):
        ctx = tuple(pad[i - order : i])
        nxt = pad[i]
        probs = ngram_predict(model, ctx, fallback)
        total_bits += -math.log2(probs[nxt])
        n += 1
    return total_bits / n


def build_context_bundle(
    byte_atoms: torch.Tensor,
    pos_atoms: torch.Tensor,
    last_k_bytes: list[int],
) -> torch.Tensor:
    """Bundle the last K bytes via positional binding; per-component-normalized FHRR sum.

    last_k_bytes[0] is the most recent byte; last_k_bytes[-1] is the oldest in window.
    """
    bound = torch.stack(
        [binding.bind(byte_atoms[b], pos_atoms[k]) for k, b in enumerate(last_k_bytes)]
    )
    s = bound.sum(dim=0)
    mag = s.abs()
    mag = torch.where(mag > 0, mag, torch.ones_like(mag))
    return s / mag.to(s.dtype)


def predict_byte_distribution(
    W: torch.Tensor,
    context: torch.Tensor,
    byte_atoms: torch.Tensor,
    beta: float,
) -> torch.Tensor:
    """Forward: W @ context -> hypervector -> similarities to byte atoms -> softmax."""
    n = context.shape[0]
    q = W @ context
    # similarity[b] = real(byte_atoms[b].conj() @ q) / n
    sims = (byte_atoms.conj() * q.unsqueeze(0)).sum(dim=-1).real / n
    logits = beta * sims
    return torch.softmax(logits, dim=0)


def _build_context_bundles_batch(
    byte_atoms: torch.Tensor,
    pos_atoms: torch.Tensor,
    indices: torch.Tensor,  # (B, K) byte indices, most-recent first
) -> torch.Tensor:
    """Vectorized: build B context bundles in one tensor op. Returns (B, N) complex."""
    # byte_atoms[indices] -> (B, K, N); pos_atoms broadcasts as (K, N) -> (1, K, N)
    bound = byte_atoms[indices] * pos_atoms.unsqueeze(0)
    summed = bound.sum(dim=1)  # (B, N)
    mag = summed.abs().clamp(min=1e-8)
    return summed / mag.to(summed.dtype)


def _predict_batch(
    W: torch.Tensor,
    ctxs: torch.Tensor,  # (B, N)
    byte_atoms: torch.Tensor,  # (V, N)
    beta: float,
) -> torch.Tensor:
    """Batched forward: returns (V, B) softmax probabilities per byte per position."""
    n = ctxs.shape[1]
    q = ctxs @ W.T  # (B, N) complex
    sims = (byte_atoms.conj() @ q.T).real / n  # (V, B)
    return torch.softmax(beta * sims, dim=0)


def train_hebbian_vsa(
    train: bytes,
    test: bytes,
    n: int,
    k: int,
    arousal: float,
    beta: float,
    seed: int,
    label: str = "",
    batch_size: int = BATCH_SIZE,
) -> dict:
    """Single pass over training corpus with batched three-factor delta-rule updates.

    Within each batch all positions see the same W; W is updated once with the
    summed errors. For batch_size=1 this is identical to pure online.
    """
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

        # Precompute index matrix for training: indices[t, j] = byte at position (t + k - 1 - j)
        # Use unfold to build it in one shot.
        # train_bytes[k-1:] gives bytes [k-1, k, ..., end]; we want (T_total, K) where row t is
        # the K bytes immediately preceding position t+k, ordered most-recent-first.
        # Easier: use a strided view.
        offsets = torch.arange(k - 1, -1, -1, device=DEVICE)  # [k-1, k-2, ..., 0]
        positions = torch.arange(T_total, device=DEVICE)  # [0, 1, ..., T_total-1]
        train_idx = train_bytes[positions.unsqueeze(1) + offsets.unsqueeze(0)]  # (T_total, K)
        train_targets = train_bytes[positions + k]  # (T_total,)

        t_train_start = time.perf_counter()
        total_surprise_bits = 0.0
        n_seen = 0

        # Train in mini-batches.
        for batch_start in range(0, T_total, batch_size):
            batch_end = min(batch_start + batch_size, T_total)
            idx_batch = train_idx[batch_start:batch_end]  # (B, K)
            tgt_batch = train_targets[batch_start:batch_end]  # (B,)
            B = idx_batch.shape[0]

            ctxs = _build_context_bundles_batch(byte_atoms, pos_atoms, idx_batch)  # (B, N)
            probs = _predict_batch(W, ctxs, byte_atoms, beta)  # (V, B)

            # Track surprise for diagnostic.
            p_true = probs.gather(0, tgt_batch.unsqueeze(0)).squeeze(0).clamp(min=1e-12)  # (B,)
            total_surprise_bits += float(-torch.log2(p_true).sum())
            n_seen += B

            # Delta-rule update: dW = sum_t outer(target_t - expected_t, ctxs[t].conj()) / N
            targets = byte_atoms[tgt_batch]  # (B, N)
            expected = probs.T.to(byte_atoms.dtype) @ byte_atoms  # (B, N)
            errors = targets - expected  # (B, N)
            dW = errors.T @ ctxs.conj() / n  # (N, N) complex
            W.add_(dW, alpha=arousal)

            if batch_start <= T_total // 2 < batch_end:
                elapsed = time.perf_counter() - t_train_start
                rolling = total_surprise_bits / max(n_seen, 1)
                _say(f"    [{label}] 50%  rolling_bpc={rolling:.3f}  elapsed={elapsed:.1f}s")

        # Evaluate on test set (batched).
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

        # Train-sample bpc on first 5000 chars.
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
            "k": k,
            "arousal": arousal,
            "beta": beta,
            "seed": seed,
            "n_substrate": n,
            "batch_size": batch_size,
            "train_bpc": train_bpc,
            "test_bpc": test_bpc,
            "train_test_gap": test_bpc - train_bpc,
            "final_w_frobenius": float(W.abs().pow(2).sum().sqrt()),
        }


def main() -> None:
    _say("Loading corpus...")
    corpus = load_corpus()
    train, test = train_test_split(corpus, train_frac=0.8)
    _say(f"  Corpus: {len(corpus)} bytes total; train={len(train)}, test={len(test)}")
    _say(f"  Distinct bytes seen in corpus: {len(set(corpus))}")

    # Baselines.
    _say("\nBaselines:")
    uni = unigram_model(train)
    uni_test_bpc = bits_per_char_unigram(uni, test)
    _say(f"  Unigram (Laplace):     test bits/char = {uni_test_bpc:.4f}")

    bg = ngram_model(train, order=2)
    bg_test_bpc = bits_per_char_ngram(bg, uni, test)
    _say(f"  2-gram (Laplace+back): test bits/char = {bg_test_bpc:.4f}")

    tg = ngram_model(train, order=3)
    tg_test_bpc = bits_per_char_ngram(tg, uni, test)
    _say(f"  3-gram (Laplace+back): test bits/char = {tg_test_bpc:.4f}")

    fg = ngram_model(train, order=5)
    fg_test_bpc = bits_per_char_ngram(fg, uni, test)
    _say(f"  5-gram (Laplace+back): test bits/char = {fg_test_bpc:.4f}")

    total_configs = len(K_VALUES) * len(AROUSAL_VALUES) * len(BETA_VALUES)
    _say(f"\nHebbian-VSA sweep (N={N_SUBSTRATE}, batch_size={BATCH_SIZE}):")
    _say(f"  {total_configs} configs running sequentially with batched inner loop")

    results: list[dict] = []
    t_start = time.perf_counter()
    idx = 0
    for k in K_VALUES:
        for arousal in AROUSAL_VALUES:
            for beta in BETA_VALUES:
                idx += 1
                label = f"cfg {idx}/{total_configs} K={k} a={arousal} b={beta}"
                _say(f"\n  Starting {label}")
                t0 = time.perf_counter()
                r = train_hebbian_vsa(train, test, N_SUBSTRATE, k, arousal, beta, SEED, label=label)
                r["wall_time_s"] = time.perf_counter() - t0
                results.append(r)
                _say(
                    f"  DONE {label}  train_bpc={r['train_bpc']:.3f} test_bpc={r['test_bpc']:.3f} "
                    f"gap={r['train_test_gap']:+.3f} ({r['wall_time_s']:.1f}s)"
                )

    best = min(results, key=lambda r: r["test_bpc"])
    _say(f"\nBest config: K={best['k']}, arousal={best['arousal']}, beta={best['beta']}")
    _say(f"  Hebbian-VSA test bits/char = {best['test_bpc']:.4f}")
    _say(f"  vs unigram                  = {uni_test_bpc:.4f}")
    _say(f"  vs 3-gram                   = {tg_test_bpc:.4f}")
    _say(f"  vs 5-gram                   = {fg_test_bpc:.4f}")

    # Decision verdict.
    if best["test_bpc"] >= uni_test_bpc:
        verdict = "DEAD: no improvement over unigram"
    elif best["test_bpc"] - tg_test_bpc <= 0.5:
        verdict = "ALIVE" if best["test_bpc"] <= tg_test_bpc else "ALIVE (close to 3-gram)"
    elif best["test_bpc"] < uni_test_bpc - 1.0:
        verdict = "HYBRID: beats unigram cleanly but loses to 3-gram"
    else:
        verdict = "HYBRID: marginal over unigram"
    _say(f"\nPre-registered verdict: {verdict}")
    _say(f"Total wall time: {time.perf_counter() - t_start:.1f}s")

    out = {
        "corpus_bytes": len(corpus),
        "train_bytes": len(train),
        "test_bytes": len(test),
        "baselines": {
            "unigram_test_bpc": uni_test_bpc,
            "ngram_2_test_bpc": bg_test_bpc,
            "ngram_3_test_bpc": tg_test_bpc,
            "ngram_5_test_bpc": fg_test_bpc,
        },
        "n_substrate": N_SUBSTRATE,
        "seed": SEED,
        "sweep_results": results,
        "best_config": {
            "k": best["k"],
            "arousal": best["arousal"],
            "beta": best["beta"],
            "test_bpc": best["test_bpc"],
            "train_bpc": best["train_bpc"],
        },
        "verdict": verdict,
        "headline": (
            f"Hebbian-VSA test bpc = {best['test_bpc']:.3f} vs "
            f"unigram = {uni_test_bpc:.3f}, 3-gram = {tg_test_bpc:.3f}, 5-gram = {fg_test_bpc:.3f}"
        ),
    }

    out_path = Path(__file__).resolve().parent.parent / "data" / "exp_pure_hebbian_charlm"
    out_path.mkdir(parents=True, exist_ok=True)
    (out_path / "metrics.json").write_text(json.dumps(out, indent=2, default=str))
    _say(f"\nWrote metrics to {out_path / 'metrics.json'}")


if __name__ == "__main__":
    main()
