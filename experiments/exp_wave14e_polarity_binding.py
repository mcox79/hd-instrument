"""Polarity binding — can substrate distinguish "X is Y" from "X is NOT Y"?

Add a third atom factor: polarity ε ∈ {-1, +1}. Bundle becomes:
B = sign(sum_i polarity_i * byte_atom[b_i] * pos_atom[i])

For BSC, polarity = ±1 scalar is the simplest negation primitive.

Minimal test:
- Encode 100 "positive" facts: bundles with polarity=+1
- Encode 100 "negative" facts with same byte content but polarity=-1
- Query each: which polarity does substrate report?
- Pass: >= 90% correct polarity discrimination.

If passes, substrate can natively represent negation.
"""

from __future__ import annotations

import json
from pathlib import Path

import torch

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
N = 4096
K = 4
VOCAB_SIZE = 256
NUM_FACTS = 100
SEED = 17


def _say(m): print(m, flush=True)


def make_bsc(k, n, gen):
    return 2.0 * (torch.rand((k, n), generator=gen) > 0.5).float() - 1.0


def build_polarity_bundle(byte_atoms, pos_atoms, polarity_atom, byte_indices, polarity_sign):
    """Bundle = sign(sum_i polarity_sign * byte_atom[b_i] * pos_atom[i])."""
    bound = byte_atoms[byte_indices] * pos_atoms  # (K, N)
    if polarity_sign == -1:
        # Apply polarity as element-wise multiplication with polarity_atom
        bound = bound * polarity_atom.unsqueeze(0)
    summed = bound.sum(dim=0)
    out = torch.sign(summed)
    return torch.where(out == 0, torch.ones_like(out), out)


def decode_polarity(bundle, byte_atoms, pos_atoms, polarity_atom, byte_indices):
    """Project bundle onto: pos*byte for positive, pos*byte*polarity for negative.
    Larger projection = that polarity."""
    # Positive projection
    pos_proj = (byte_atoms[byte_indices] * pos_atoms).sum(dim=0)
    pos_score = float((bundle @ pos_proj).item()) / N
    # Negative projection
    neg_proj = (byte_atoms[byte_indices] * pos_atoms * polarity_atom.unsqueeze(0)).sum(dim=0)
    neg_score = float((bundle @ neg_proj).item()) / N
    return pos_score, neg_score


def main():
    _say(f"Polarity binding probe: N={N}, K={K}, {NUM_FACTS} positive + {NUM_FACTS} negative facts")
    gen = torch.Generator().manual_seed(SEED)
    byte_atoms = make_bsc(VOCAB_SIZE, N, gen).to(DEVICE)
    pos_atoms = make_bsc(K, N, gen).to(DEVICE)
    polarity_atom = make_bsc(1, N, gen).squeeze(0).to(DEVICE)

    # Generate random "facts": each is a K-byte sequence
    fact_gen = torch.Generator().manual_seed(SEED * 7)
    facts = torch.randint(0, VOCAB_SIZE, (NUM_FACTS, K), generator=fact_gen).to(DEVICE)

    # Encode each as positive and negative bundles
    pos_bundles = torch.stack([build_polarity_bundle(byte_atoms, pos_atoms, polarity_atom, facts[i], +1) for i in range(NUM_FACTS)])
    neg_bundles = torch.stack([build_polarity_bundle(byte_atoms, pos_atoms, polarity_atom, facts[i], -1) for i in range(NUM_FACTS)])

    correct_pos = 0
    correct_neg = 0
    pos_scores_pos = []  # positive-bundle's pos_score
    neg_scores_pos = []  # positive-bundle's neg_score
    for i in range(NUM_FACTS):
        ps, ns = decode_polarity(pos_bundles[i], byte_atoms, pos_atoms, polarity_atom, facts[i])
        pos_scores_pos.append(ps); neg_scores_pos.append(ns)
        if ps > ns: correct_pos += 1
    pos_scores_neg = []
    neg_scores_neg = []
    for i in range(NUM_FACTS):
        ps, ns = decode_polarity(neg_bundles[i], byte_atoms, pos_atoms, polarity_atom, facts[i])
        pos_scores_neg.append(ps); neg_scores_neg.append(ns)
        if ns > ps: correct_neg += 1

    pos_acc = correct_pos / NUM_FACTS
    neg_acc = correct_neg / NUM_FACTS

    _say(f"\n  Positive bundle disc: {pos_acc*100:.1f}% identified as positive")
    _say(f"  Negative bundle disc: {neg_acc*100:.1f}% identified as negative")
    _say(f"  Mean pos_score for positive bundles: {sum(pos_scores_pos)/len(pos_scores_pos):+.4f}")
    _say(f"  Mean neg_score for positive bundles: {sum(neg_scores_pos)/len(neg_scores_pos):+.4f}")
    _say(f"  Mean pos_score for negative bundles: {sum(pos_scores_neg)/len(pos_scores_neg):+.4f}")
    _say(f"  Mean neg_score for negative bundles: {sum(neg_scores_neg)/len(neg_scores_neg):+.4f}")

    mean_acc = (pos_acc + neg_acc) / 2
    if mean_acc >= 0.9:
        _say(f"\n  PASS: substrate distinguishes polarity at {mean_acc*100:.1f}%. Negation primitive viable.")
    elif mean_acc >= 0.7:
        _say(f"\n  PARTIAL: {mean_acc*100:.1f}%. Polarity factor adds noise but works mostly.")
    else:
        _say(f"\n  WEAK: {mean_acc*100:.1f}%. Polarity factor inadequately distinguishes.")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14e_polarity_binding"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps({
        "N": N, "K": K, "NUM_FACTS": NUM_FACTS,
        "pos_accuracy": pos_acc, "neg_accuracy": neg_acc, "mean_accuracy": mean_acc,
    }, indent=2))


if __name__ == "__main__":
    main()
