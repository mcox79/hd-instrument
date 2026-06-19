"""Multi-hop reasoning across bundles — placeholder for research-informed v2.

Minimal probe: encode 50 (A, B) facts as bundles where one position holds A
and another holds B. For each fact bundle find pair "where does B link to C"
and chain to produce (A, C).

Mechanism: decompose B₁ at position 1 (get B), find B₂ with B at position 0
(get the chain bundle), decompose B₂ at position 1 (get C). Construct
B₃ = A·pos₀ + C·pos₁.

Verify: decompose B₃ at position 1 -> should return C.

This is the simplest possible compositional chain. v2 (after research) will
add deeper chains, sparse-code chains, and resonator-based chaining.
"""

from __future__ import annotations

import json
from pathlib import Path

import torch

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
N = 4096
VOCAB_SIZE = 256
NUM_FACTS = 50
SEED = 17


def _say(m): print(m, flush=True)


def make_bsc(k, n, gen):
    return 2.0 * (torch.rand((k, n), generator=gen) > 0.5).float() - 1.0


def build_pair_bundle(byte_atoms, pos_atoms, byte_a, byte_b):
    """Bundle = sign(byte_atoms[a]*pos_atoms[0] + byte_atoms[b]*pos_atoms[1])."""
    bundle = byte_atoms[byte_a] * pos_atoms[0] + byte_atoms[byte_b] * pos_atoms[1]
    out = torch.sign(bundle)
    return torch.where(out == 0, torch.ones_like(out), out)


def decode_at_pos(bundle, byte_atoms, pos_atoms, position):
    proj = bundle * pos_atoms[position]
    scores = byte_atoms @ proj / N
    return int(scores.argmax().item())


def main():
    _say(f"Multi-hop reasoning probe (v1): N={N}, {NUM_FACTS} facts")
    gen = torch.Generator().manual_seed(SEED)
    byte_atoms = make_bsc(VOCAB_SIZE, N, gen).to(DEVICE)
    pos_atoms = make_bsc(2, N, gen).to(DEVICE)

    # Generate a chain: bytes B0 -> B1, B1 -> B2, B2 -> B3, ...
    # Each fact i: (byte[i], byte[i+1])
    fact_gen = torch.Generator().manual_seed(SEED * 7)
    chain_bytes = torch.randint(0, VOCAB_SIZE, (NUM_FACTS + 1,), generator=fact_gen).tolist()
    bundles = [build_pair_bundle(byte_atoms, pos_atoms, chain_bytes[i], chain_bytes[i+1])
                for i in range(NUM_FACTS)]

    # 2-hop test: from bundle[0]=(B0,B1) and bundle[1]=(B1,B2), derive (B0,B2)
    correct_2hop = 0
    for i in range(NUM_FACTS - 1):
        B1 = bundles[i]; B2 = bundles[i+1]
        # Decompose B1 at pos 1 -> should give chain_bytes[i+1]
        mid_byte = decode_at_pos(B1, byte_atoms, pos_atoms, 1)
        # Decompose B2 at pos 0 -> should also give chain_bytes[i+1]
        check_mid = decode_at_pos(B2, byte_atoms, pos_atoms, 0)
        if mid_byte != check_mid: continue  # chain inconsistent
        # Decompose B2 at pos 1 -> gives chain_bytes[i+2]
        end_byte = decode_at_pos(B2, byte_atoms, pos_atoms, 1)
        # Construct chained bundle (B0 -> B2)
        start_byte = decode_at_pos(B1, byte_atoms, pos_atoms, 0)
        chained = build_pair_bundle(byte_atoms, pos_atoms, start_byte, end_byte)
        # Verify
        recovered_end = decode_at_pos(chained, byte_atoms, pos_atoms, 1)
        if recovered_end == chain_bytes[i+2]:
            correct_2hop += 1

    acc_2hop = correct_2hop / (NUM_FACTS - 1)
    _say(f"\n  2-hop chain accuracy: {acc_2hop*100:.1f}%")

    # 3-hop test
    correct_3hop = 0
    for i in range(NUM_FACTS - 2):
        start = chain_bytes[i]
        mid1 = decode_at_pos(bundles[i], byte_atoms, pos_atoms, 1)
        mid2 = decode_at_pos(bundles[i+1], byte_atoms, pos_atoms, 1)
        end = decode_at_pos(bundles[i+2], byte_atoms, pos_atoms, 1)
        # All decompositions must match ground truth for chain to work
        if mid1 == chain_bytes[i+1] and mid2 == chain_bytes[i+2] and end == chain_bytes[i+3]:
            chained = build_pair_bundle(byte_atoms, pos_atoms, start, end)
            recovered = decode_at_pos(chained, byte_atoms, pos_atoms, 1)
            if recovered == chain_bytes[i+3]:
                correct_3hop += 1

    acc_3hop = correct_3hop / max(NUM_FACTS - 2, 1)
    _say(f"  3-hop chain accuracy: {acc_3hop*100:.1f}%")

    if acc_2hop >= 0.8:
        _say(f"\n  PASS (2-hop): substrate supports 2-hop chains at {acc_2hop*100:.1f}%.")
    if acc_3hop >= 0.5:
        _say(f"  PASS (3-hop): substrate supports 3-hop chains at {acc_3hop*100:.1f}%.")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14e_multi_hop_reasoning"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps({
        "N": N, "NUM_FACTS": NUM_FACTS,
        "acc_2hop": acc_2hop, "acc_3hop": acc_3hop,
    }, indent=2))


if __name__ == "__main__":
    main()
