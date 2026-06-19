"""Temporal binding — can substrate distinguish memories by time stamp?

Add a third atom factor: time_atom(t) = sign(sinusoidal projection of t).
Bundle = sign(sum_i time_atom(t_event) * byte_atom[b_i] * pos_atom[i])

Minimal test:
- Encode 100 (fact, time) pairs across 10 time bins.
- Query with a fact + time bin: does substrate correctly identify time of that fact?
- Pass: >= 80% correct time identification at K_time bins, where K_time=10.

Sinusoidal time encoding (Vaswani 2017): time_atom_d(t) = sign(sin(t / 10000^(2d/N)))
for d in 0..N-1.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import torch

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
N = 4096
K = 4
VOCAB_SIZE = 256
NUM_TIME_BINS = 10
NUM_FACTS_PER_TIME = 10
SEED = 17


def _say(m): print(m, flush=True)


def make_bsc(k, n, gen):
    return 2.0 * (torch.rand((k, n), generator=gen) > 0.5).float() - 1.0


def make_time_atom(t, n):
    """Vaswani-style sinusoidal time encoding, sign-quantized to bipolar."""
    d = torch.arange(n, device=DEVICE).float()
    freq = 1.0 / (10000.0 ** (2 * d / n))
    val = torch.where(d % 2 == 0, torch.sin(t * freq), torch.cos(t * freq))
    out = torch.sign(val)
    return torch.where(out == 0, torch.ones_like(out), out)


def build_temporal_bundle(byte_atoms, pos_atoms, time_atom, byte_indices):
    bound = byte_atoms[byte_indices] * pos_atoms * time_atom.unsqueeze(0)
    summed = bound.sum(dim=0)
    out = torch.sign(summed)
    return torch.where(out == 0, torch.ones_like(out), out)


def decode_time(bundle, byte_atoms, pos_atoms, time_atoms_per_bin, byte_indices):
    """Find time bin t that maximizes bundle·(time_atom(t) * byte * pos)."""
    scores = []
    for t_idx, time_atom in enumerate(time_atoms_per_bin):
        proj = (byte_atoms[byte_indices] * pos_atoms * time_atom.unsqueeze(0)).sum(dim=0)
        score = float((bundle @ proj).item()) / N
        scores.append(score)
    return int(max(range(len(scores)), key=lambda i: scores[i])), scores


def main():
    _say(f"Temporal binding probe: N={N}, K={K}, {NUM_TIME_BINS} time bins")
    gen = torch.Generator().manual_seed(SEED)
    byte_atoms = make_bsc(VOCAB_SIZE, N, gen).to(DEVICE)
    pos_atoms = make_bsc(K, N, gen).to(DEVICE)
    # Pre-compute time atoms for each bin
    time_atoms = [make_time_atom(float(t * 100 + 1), N) for t in range(NUM_TIME_BINS)]

    fact_gen = torch.Generator().manual_seed(SEED * 7)
    # Generate (fact, time) pairs
    pairs = []
    for t_bin in range(NUM_TIME_BINS):
        for _ in range(NUM_FACTS_PER_TIME):
            fact = torch.randint(0, VOCAB_SIZE, (K,), generator=fact_gen).to(DEVICE)
            pairs.append((fact, t_bin))

    bundles = [build_temporal_bundle(byte_atoms, pos_atoms, time_atoms[t], f) for f, t in pairs]

    correct = 0
    confusion = [[0] * NUM_TIME_BINS for _ in range(NUM_TIME_BINS)]
    for (fact, true_t), bundle in zip(pairs, bundles):
        pred_t, _ = decode_time(bundle, byte_atoms, pos_atoms, time_atoms, fact)
        confusion[true_t][pred_t] += 1
        if pred_t == true_t:
            correct += 1

    acc = correct / len(pairs)
    _say(f"\n  Time identification accuracy: {acc*100:.1f}% over {len(pairs)} (fact, time) pairs")
    _say(f"\n  Confusion matrix (true_t row, pred_t col):")
    for r in range(NUM_TIME_BINS):
        _say(f"    t={r}: {confusion[r]}")

    if acc >= 0.8:
        _say(f"\n  PASS: temporal binding distinguishes {NUM_TIME_BINS} time bins at {acc*100:.1f}%.")
    elif acc >= 0.5:
        _say(f"\n  PARTIAL: {acc*100:.1f}%. Above chance ({100/NUM_TIME_BINS:.0f}%) but not clean.")
    else:
        _say(f"\n  WEAK: at-chance behavior. Sinusoidal encoding may collide.")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14e_temporal_binding"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps({
        "N": N, "K": K, "NUM_TIME_BINS": NUM_TIME_BINS,
        "accuracy": acc, "n_pairs": len(pairs),
    }, indent=2))


if __name__ == "__main__":
    main()
