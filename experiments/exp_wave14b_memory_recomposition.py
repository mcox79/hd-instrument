"""Wave 14.B Memory Recomposition: synthesize bundles from parts of others.

Builds on memory_editing's success. Where editing changes ONE position of
ONE bundle, recomposition takes parts from MULTIPLE bundles and synthesizes
a new bundle.

Algorithm:
1. Take two pool bundles c_A and c_B with known atoms.
2. Decompose both via 14.B.
3. Construct c_new = positions {0,1} from A + positions {2,3} from B.
4. Verify: c_new decomposes back to the expected mixed contents.
5. Verify: c_new's cosine to c_A and c_B reflects the 50/50 mixture.
6. Verify: c_new constructed via decompose-recompose path equals c_new
   constructed directly from the mixed byte indices.

This demonstrates compositional MEMORY SYNTHESIS — taking parts of
distinct experiences and creating a new structured representation.
No vector DB can do this natively.
"""

from __future__ import annotations

import json
from pathlib import Path

import torch


DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
SEED = 17
VOCAB_SIZE = 256
K = 4
N = 4096
NUM_TRIALS = 100
SWAP_POSITIONS_FROM_B = [2, 3]


def _say(msg):
    print(msg, flush=True)


def make_bsc_atoms(k, n, gen):
    raw = torch.rand((k, n), generator=gen)
    return (2.0 * (raw > 0.5).float() - 1.0)


def build_ctx_bundle(byte_atoms, pos_atoms, indices):
    bound = byte_atoms[indices] * pos_atoms.unsqueeze(0)
    summed = bound.sum(dim=1)
    out = torch.sign(summed)
    return torch.where(out == 0, torch.ones_like(out), out)


def decompose_bundle(c, pos_atoms, byte_atoms):
    recovered = []
    for r in range(K):
        projected = c * pos_atoms[r]
        scores = byte_atoms @ projected / N
        recovered.append(int(scores.argmax().item()))
    return recovered


def main():
    _say(f"Wave 14.B Memory Recomposition experiment")
    _say(f"  Swap positions {SWAP_POSITIONS_FROM_B} from bundle B into bundle A")

    gen = torch.Generator().manual_seed(SEED)
    byte_atoms = make_bsc_atoms(VOCAB_SIZE, N, gen).to(DEVICE)
    pos_atoms = make_bsc_atoms(K, N, gen).to(DEVICE)

    # === Test A: decompose-recompose synthesis fidelity ===
    _say(f"\n[A] Synthesis fidelity (recover A's pos 0,1 + B's pos 2,3):")
    correct_synthesis = 0
    bytes_at_synthesized_positions_correct = 0
    gen_trial = torch.Generator().manual_seed(SEED + 10)
    for trial in range(NUM_TRIALS):
        a_idx = torch.randint(0, VOCAB_SIZE, (K,), generator=gen_trial).tolist()
        b_idx = torch.randint(0, VOCAB_SIZE, (K,), generator=gen_trial).tolist()
        c_A = build_ctx_bundle(byte_atoms, pos_atoms,
                              torch.tensor([a_idx], device=DEVICE))[0]
        c_B = build_ctx_bundle(byte_atoms, pos_atoms,
                              torch.tensor([b_idx], device=DEVICE))[0]
        # Decompose both
        a_recovered = decompose_bundle(c_A, pos_atoms, byte_atoms)
        b_recovered = decompose_bundle(c_B, pos_atoms, byte_atoms)
        # Recompose: keep A's pos 0,1 ; use B's pos 2,3
        new_idx = a_recovered.copy()
        for p in SWAP_POSITIONS_FROM_B:
            new_idx[p] = b_recovered[p]
        # Build the synthesized bundle
        c_new = build_ctx_bundle(byte_atoms, pos_atoms,
                                torch.tensor([new_idx], device=DEVICE))[0]
        # Verify by decomposing c_new
        c_new_recovered = decompose_bundle(c_new, pos_atoms, byte_atoms)
        # Expected: A's bytes at non-swap positions, B's bytes at swap positions
        expected = []
        for p in range(K):
            if p in SWAP_POSITIONS_FROM_B:
                expected.append(b_idx[p])
            else:
                expected.append(a_idx[p])
        if c_new_recovered == expected:
            correct_synthesis += 1
        # Bytes at the synthesized positions correct?
        bytes_ok = all(c_new_recovered[p] == expected[p] for p in SWAP_POSITIONS_FROM_B)
        if bytes_ok:
            bytes_at_synthesized_positions_correct += 1
    _say(f"  Full recovery matches expected mixed bytes: {correct_synthesis}/{NUM_TRIALS} = {100*correct_synthesis/NUM_TRIALS:.1f}%")
    _say(f"  Bytes at swapped positions correct:         {bytes_at_synthesized_positions_correct}/{NUM_TRIALS} = {100*bytes_at_synthesized_positions_correct/NUM_TRIALS:.1f}%")

    # === Test B: cosine geometry verification ===
    _say(f"\n[B] Cosine geometry of synthesized bundle:")
    cos_to_A_vals = []
    cos_to_B_vals = []
    gen_trial = torch.Generator().manual_seed(SEED + 20)
    for trial in range(NUM_TRIALS):
        a_idx = torch.randint(0, VOCAB_SIZE, (K,), generator=gen_trial).tolist()
        b_idx = torch.randint(0, VOCAB_SIZE, (K,), generator=gen_trial).tolist()
        c_A = build_ctx_bundle(byte_atoms, pos_atoms,
                              torch.tensor([a_idx], device=DEVICE))[0]
        c_B = build_ctx_bundle(byte_atoms, pos_atoms,
                              torch.tensor([b_idx], device=DEVICE))[0]
        new_idx = a_idx.copy()
        for p in SWAP_POSITIONS_FROM_B:
            new_idx[p] = b_idx[p]
        c_new = build_ctx_bundle(byte_atoms, pos_atoms,
                                torch.tensor([new_idx], device=DEVICE))[0]
        cos_to_A = float((c_new @ c_A) / (c_new.norm() * c_A.norm() + 1e-12))
        cos_to_B = float((c_new @ c_B) / (c_new.norm() * c_B.norm() + 1e-12))
        cos_to_A_vals.append(cos_to_A)
        cos_to_B_vals.append(cos_to_B)
    mean_A = sum(cos_to_A_vals) / len(cos_to_A_vals)
    mean_B = sum(cos_to_B_vals) / len(cos_to_B_vals)
    _say(f"  cos(c_new, c_A): {mean_A:.4f}  (kept {K - len(SWAP_POSITIONS_FROM_B)}/{K} positions from A)")
    _say(f"  cos(c_new, c_B): {mean_B:.4f}  (took {len(SWAP_POSITIONS_FROM_B)}/{K} positions from B)")
    _say(f"  Expected: cos_A > cos_B since more of synthesis comes from A")

    # === Test C: decompose-recompose path equals direct construction ===
    _say(f"\n[C] Synthesis via decomposition equals direct construction:")
    equiv = 0
    gen_trial = torch.Generator().manual_seed(SEED + 30)
    for trial in range(NUM_TRIALS):
        a_idx = torch.randint(0, VOCAB_SIZE, (K,), generator=gen_trial).tolist()
        b_idx = torch.randint(0, VOCAB_SIZE, (K,), generator=gen_trial).tolist()
        c_A = build_ctx_bundle(byte_atoms, pos_atoms,
                              torch.tensor([a_idx], device=DEVICE))[0]
        c_B = build_ctx_bundle(byte_atoms, pos_atoms,
                              torch.tensor([b_idx], device=DEVICE))[0]
        a_rec = decompose_bundle(c_A, pos_atoms, byte_atoms)
        b_rec = decompose_bundle(c_B, pos_atoms, byte_atoms)
        # Path 1: synth from decomposed parts
        new_idx_1 = a_rec.copy()
        for p in SWAP_POSITIONS_FROM_B:
            new_idx_1[p] = b_rec[p]
        c_via_decomp = build_ctx_bundle(byte_atoms, pos_atoms,
                                         torch.tensor([new_idx_1], device=DEVICE))[0]
        # Path 2: direct
        new_idx_2 = a_idx.copy()
        for p in SWAP_POSITIONS_FROM_B:
            new_idx_2[p] = b_idx[p]
        c_direct = build_ctx_bundle(byte_atoms, pos_atoms,
                                     torch.tensor([new_idx_2], device=DEVICE))[0]
        if torch.equal(c_via_decomp, c_direct):
            equiv += 1
    _say(f"  decompose-recompose == direct-construct: {equiv}/{NUM_TRIALS} = {100*equiv/NUM_TRIALS:.1f}%")

    _say(f"\n========= MEMORY RECOMPOSITION VERDICT =========")
    if correct_synthesis / NUM_TRIALS >= 0.98 and equiv / NUM_TRIALS >= 0.95:
        _say(f"  RECOMPOSITION WORKS: substrate supports compositional memory synthesis.")
        _say(f"  Take parts of memory A + parts of memory B -> coherent new memory.")
        _say(f"  No vector DB has this capability.")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_memory_recomposition"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps({
        "full_synthesis_correct": correct_synthesis / NUM_TRIALS,
        "swapped_bytes_correct": bytes_at_synthesized_positions_correct / NUM_TRIALS,
        "mean_cos_to_A": mean_A,
        "mean_cos_to_B": mean_B,
        "decompose_recompose_equiv_direct": equiv / NUM_TRIALS,
    }, indent=2))


if __name__ == "__main__":
    main()
