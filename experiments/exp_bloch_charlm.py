"""Track 0.1: Bloch / randomized-DFT substrate for the Hebbian-VSA char LM.

Replaces the standard random-IID FHRR atoms (uniform phases on [0, 2π)) with
"randomized DFT" atoms whose phases are integer multiples of 2π/N plus a random
global offset:

    atom_k(j) = exp(i * (2π * k * j / N + sigma_k)) / sqrt(N)

This preserves the spectral concentration of a single Fourier mode while killing
the deterministic "bind = group addition" aliasing that would otherwise collapse
binding chains onto the cyclic group Z_N.

Per Frady, Kleyko & Sommer 2018 (Neural Computation 30(6):1449), structured
substrates have the same asymptotic SNR scaling N/(M-1) as random IID, but
lower-variance crosstalk -- the constant in the capacity bound is tighter. This
is a complement to Krotov; expected gain on a fixed bundle-saturation problem
is constant-factor (~0.05-0.15 bits/char) not exponential.

Tests three substrate variants at the best Track 0.1 hyperparameters.
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
BETA = 8.0
BATCH_SIZE = 64


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


def bits_per_char_unigram(probs, test):
    return -sum(math.log2(probs[b]) for b in test) / len(test)


def make_atom_random_iid(n: int, gen: torch.Generator) -> torch.Tensor:
    """Standard FHRR atom: uniform random phases in [0, 2π)."""
    phases = torch.rand(n, generator=gen) * (2.0 * math.pi)
    return torch.complex(torch.cos(phases), torch.sin(phases)).to(torch.complex64)


def make_atom_dft_pure(n: int, k: int) -> torch.Tensor:
    """Pure DFT column k: phases = 2π * k * j / n for j in [0, n).

    Bind(atom_k, atom_l) = atom_{(k+l) mod n} -- group structure under cyclic group.
    """
    j = torch.arange(n, dtype=torch.float32, device=DEVICE)
    phases = 2.0 * math.pi * k * j / n
    return torch.complex(torch.cos(phases), torch.sin(phases)).to(torch.complex64)


def make_atom_dft_randomized(n: int, k: int, gen: torch.Generator) -> torch.Tensor:
    """Randomized-DFT atom (Frady recipe): DFT column k + random global phase offset.

    The per-atom random global phase breaks deterministic group aliasing while
    keeping the spectral concentration of a single Fourier mode.
    """
    j = torch.arange(n, dtype=torch.float32, device=DEVICE)
    sigma = float(torch.rand(1, generator=gen).item()) * 2.0 * math.pi
    phases = 2.0 * math.pi * k * j / n + sigma
    return torch.complex(torch.cos(phases), torch.sin(phases)).to(torch.complex64)


def make_byte_atoms(
    n: int,
    method: str,
    gen: torch.Generator,
) -> torch.Tensor:
    """Generate VOCAB_SIZE byte atoms using the chosen method.

    method:
      - "iid": random IID phases (the baseline)
      - "dft_pure": exact DFT columns at random distinct indices
      - "dft_randomized": DFT columns + per-atom random global phase
    """
    if method == "iid":
        return torch.stack([make_atom_random_iid(n, gen) for _ in range(VOCAB_SIZE)])
    elif method == "dft_pure":
        # Distinct k indices, uniformly spread
        k_indices = torch.randperm(n, generator=gen)[:VOCAB_SIZE].tolist()
        return torch.stack([make_atom_dft_pure(n, k) for k in k_indices])
    elif method == "dft_randomized":
        k_indices = torch.randperm(n, generator=gen)[:VOCAB_SIZE].tolist()
        return torch.stack([make_atom_dft_randomized(n, k, gen) for k in k_indices])
    else:
        raise ValueError(f"Unknown method: {method}")


def make_pos_atoms(n: int, k: int, method: str, gen: torch.Generator) -> torch.Tensor:
    """Position-role atoms in the same family as byte atoms."""
    if method == "iid":
        return torch.stack([make_atom_random_iid(n, gen) for _ in range(k)])
    elif method == "dft_pure":
        k_indices = torch.randperm(n, generator=gen)[:k].tolist()
        return torch.stack([make_atom_dft_pure(n, ki) for ki in k_indices])
    elif method == "dft_randomized":
        k_indices = torch.randperm(n, generator=gen)[:k].tolist()
        return torch.stack([make_atom_dft_randomized(n, ki, gen) for ki in k_indices])
    else:
        raise ValueError(method)


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


def train_bloch_hebbian(
    train, test, n_dim, k, arousal, beta, substrate_method, seed,
    label="", batch_size=BATCH_SIZE,
):
    quiet = tracing.TraceBus(enabled=False)
    with tracing.using(quiet):
        gen = torch.Generator().manual_seed(seed)
        byte_atoms = make_byte_atoms(n_dim, substrate_method, gen)
        pos_atoms = make_pos_atoms(n_dim, k, substrate_method, gen)
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
            probs = _predict_batch(W, ctxs, byte_atoms, beta)
            p_true = probs.gather(0, tgt_batch.unsqueeze(0)).squeeze(0).clamp(min=1e-12)
            total_bits += float(-torch.log2(p_true).sum())
            n_seen += B

            targets = byte_atoms[tgt_batch]
            expected = probs.T.to(byte_atoms.dtype) @ byte_atoms
            errors = targets - expected
            dW = errors.T @ ctxs.conj() / n_dim
            W.add_(dW, alpha=arousal)

            if batch_start <= T_total // 2 < batch_end:
                elapsed = time.perf_counter() - t_start
                _say(f"    [{label}] 50%  rolling_bpc={total_bits/max(n_seen,1):.3f}  elapsed={elapsed:.1f}s")

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
            "n_substrate": n_dim, "k": k, "arousal": arousal, "beta": beta,
            "substrate_method": substrate_method, "seed": seed, "batch_size": batch_size,
            "train_bpc": train_bpc, "test_bpc": test_bpc,
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
    _say(f"  IID random substrate (Track 0.1 baseline): 3.16")
    _say(f"  Tiny transformer (ceiling):                2.39")

    methods = ["iid", "dft_pure", "dft_randomized"]
    _say(f"\nSubstrate sweep (N={N_SUBSTRATE}, K={K_BEST}, arousal={AROUSAL}, beta={BETA}):")

    results: list[dict] = []
    for method in methods:
        label = f"substrate={method}"
        _say(f"\n  Starting {label}")
        t0 = time.perf_counter()
        r = train_bloch_hebbian(
            train, test, N_SUBSTRATE, K_BEST, AROUSAL, BETA, method, SEED, label=label,
        )
        r["wall_time_s"] = time.perf_counter() - t0
        results.append(r)
        _say(
            f"  DONE {label}  test_bpc={r['test_bpc']:.4f}  gap={r['train_test_gap']:+.3f}  "
            f"({r['wall_time_s']:.1f}s)"
        )

    results.sort(key=lambda r: r["test_bpc"])
    best = results[0]
    _say(f"\nBest substrate: {best['substrate_method']}")
    _say(f"  test bits/char = {best['test_bpc']:.4f}")
    _say(f"  vs IID baseline = 3.16  (delta = {3.16 - best['test_bpc']:+.3f})")

    out = {
        "seed": SEED, "n_substrate": N_SUBSTRATE, "k": K_BEST, "arousal": AROUSAL, "beta": BETA,
        "sweep_results": results,
        "best": {"method": best["substrate_method"], "test_bpc": best["test_bpc"]},
        "headline": f"Best substrate {best['substrate_method']} test bpc = {best['test_bpc']:.3f}",
    }
    out_path = Path(__file__).resolve().parent.parent / "data" / "exp_bloch_charlm"
    out_path.mkdir(parents=True, exist_ok=True)
    (out_path / "metrics.json").write_text(json.dumps(out, indent=2, default=str))
    _say(f"\nWrote {out_path / 'metrics.json'}")


if __name__ == "__main__":
    main()
