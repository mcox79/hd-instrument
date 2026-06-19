"""Wave 14.B Memory Editing: decompose → modify → rebundle.

Demonstrates CRUD-style memory editing that no vector DB can do natively.

Algorithm:
1. Take a pool entry bundle: c = byte_a*pos_0 + byte_b*pos_1 + byte_c*pos_2 + byte_d*pos_3
2. Decompose via 14.B (cleanup against codebook per position)
3. Identify the original 4 byte indices
4. Replace position-3's atom with a DIFFERENT byte (the "edit" operation)
5. Re-bundle: c_edited = byte_a*pos_0 + byte_b*pos_1 + byte_c*pos_2 + byte_NEW*pos_3
6. Verify: c_edited retrieves the same memory STRUCTURE except at position 3

Three correctness checks:
A. **Round-trip fidelity**: decompose-then-rebundle with NO edit should equal the
   original bundle (mod bipolar quantization noise). If round-trip works, the
   substrate supports lossless edit operations.
B. **Single-edit semantics**: edit changes ONLY the target position, not others.
   Verify the edited bundle's decomposition gives original_bytes except at position 3.
C. **Retrieval behavior**: query a pool that contains both the original AND the
   edited bundle. Confirm they're distinct entries via cosine.

This is the experimental version of "vector DB CRUD" for HDC memory.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import torch


torch.set_float32_matmul_precision("high")

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
SEED = 17
VOCAB_SIZE = 256
PAD_BYTE = 0
K = 4
BETA = 8.0
N = 4096
NUM_TRIALS = 100


def _say(msg):
    print(msg, flush=True)


def make_bsc_atoms(k, n, gen):
    raw = torch.rand((k, n), generator=gen)
    return (2.0 * (raw > 0.5).float() - 1.0)


def build_ctx_bundles_bsc(byte_atoms, pos_atoms, indices):
    """Standard BSC bundle: sign(sum of (byte_atom * pos_atom))."""
    bound = byte_atoms[indices] * pos_atoms.unsqueeze(0)
    summed = bound.sum(dim=1)
    out = torch.sign(summed)
    return torch.where(out == 0, torch.ones_like(out), out)


def decompose_bundle(c, pos_atoms, byte_atoms):
    """14.B-style decomposition: for each position, project & cleanup against codebook.
    Returns: K-tuple of recovered byte indices."""
    recovered = []
    for r in range(K):
        # bundle * pos_r = byte_at_pos_r + noise
        projected = c * pos_atoms[r]
        scores = byte_atoms @ projected / N  # cosine-like
        recovered.append(int(scores.argmax().item()))
    return recovered


def main():
    _say(f"Wave 14.B Memory Editing experiment")
    _say(f"  Tests: decompose -> modify position 3 -> rebundle")

    gen = torch.Generator().manual_seed(SEED)
    byte_atoms = make_bsc_atoms(VOCAB_SIZE, N, gen).to(DEVICE)
    pos_atoms = make_bsc_atoms(K, N, gen).to(DEVICE)

    # === Test A: round-trip fidelity (decompose -> rebundle without edit) ===
    _say(f"\n[A] Round-trip fidelity (decompose then rebundle with NO edit):")
    rt_correct = 0
    rt_failures = []
    gen_trial = torch.Generator().manual_seed(SEED + 1)
    for trial in range(NUM_TRIALS):
        # Random source bundle
        original_indices = torch.randint(0, VOCAB_SIZE, (K,), generator=gen_trial).tolist()
        c_orig = build_ctx_bundles_bsc(byte_atoms, pos_atoms,
                                        torch.tensor([original_indices], device=DEVICE))[0]
        # Decompose
        recovered = decompose_bundle(c_orig, pos_atoms, byte_atoms)
        # Rebundle (no edit)
        c_rebundled = build_ctx_bundles_bsc(byte_atoms, pos_atoms,
                                             torch.tensor([recovered], device=DEVICE))[0]
        # Check equality
        if recovered == original_indices:
            rt_correct += 1
        else:
            if len(rt_failures) < 3:
                rt_failures.append((original_indices, recovered))
    rt_rate = rt_correct / NUM_TRIALS
    _say(f"  Decomposition recovery: {rt_correct}/{NUM_TRIALS} = {100*rt_rate:.1f}%")
    if rt_failures:
        _say(f"  Sample failures: {rt_failures[:3]}")

    # === Test B: single-edit semantics ===
    _say(f"\n[B] Single-edit at position 3:")
    edit_pos_correct = 0  # position 3 changed to target byte
    other_pos_correct = 0  # positions 0,1,2 unchanged
    full_edit_correct = 0  # both conditions
    gen_trial = torch.Generator().manual_seed(SEED + 2)
    for trial in range(NUM_TRIALS):
        original_indices = torch.randint(0, VOCAB_SIZE, (K,), generator=gen_trial).tolist()
        c_orig = build_ctx_bundles_bsc(byte_atoms, pos_atoms,
                                        torch.tensor([original_indices], device=DEVICE))[0]
        # Edit: pick a different byte for position 3
        new_byte = int(torch.randint(0, VOCAB_SIZE, (1,), generator=gen_trial).item())
        while new_byte == original_indices[3]:
            new_byte = int(torch.randint(0, VOCAB_SIZE, (1,), generator=gen_trial).item())
        # Decompose original
        recovered = decompose_bundle(c_orig, pos_atoms, byte_atoms)
        # Apply edit
        edited_indices = recovered[:3] + [new_byte]
        # Rebundle
        c_edited = build_ctx_bundles_bsc(byte_atoms, pos_atoms,
                                          torch.tensor([edited_indices], device=DEVICE))[0]
        # Decompose edited bundle and verify
        edited_recovered = decompose_bundle(c_edited, pos_atoms, byte_atoms)
        if edited_recovered[3] == new_byte:
            edit_pos_correct += 1
        if edited_recovered[:3] == original_indices[:3]:
            other_pos_correct += 1
        if edited_recovered[:3] == original_indices[:3] and edited_recovered[3] == new_byte:
            full_edit_correct += 1
    _say(f"  Edit applied (pos 3 = new_byte):    {edit_pos_correct}/{NUM_TRIALS} = {100*edit_pos_correct/NUM_TRIALS:.1f}%")
    _say(f"  Other positions preserved (0,1,2):  {other_pos_correct}/{NUM_TRIALS} = {100*other_pos_correct/NUM_TRIALS:.1f}%")
    _say(f"  Full edit correct (both):           {full_edit_correct}/{NUM_TRIALS} = {100*full_edit_correct/NUM_TRIALS:.1f}%")

    # === Test C: edited bundle distinct from original via cosine ===
    _say(f"\n[C] Edited bundle distinct from original:")
    cos_diffs = []
    gen_trial = torch.Generator().manual_seed(SEED + 3)
    for trial in range(NUM_TRIALS):
        original_indices = torch.randint(0, VOCAB_SIZE, (K,), generator=gen_trial).tolist()
        c_orig = build_ctx_bundles_bsc(byte_atoms, pos_atoms,
                                        torch.tensor([original_indices], device=DEVICE))[0]
        new_byte = int(torch.randint(0, VOCAB_SIZE, (1,), generator=gen_trial).item())
        while new_byte == original_indices[3]:
            new_byte = int(torch.randint(0, VOCAB_SIZE, (1,), generator=gen_trial).item())
        edited_indices = original_indices[:3] + [new_byte]
        c_edited = build_ctx_bundles_bsc(byte_atoms, pos_atoms,
                                          torch.tensor([edited_indices], device=DEVICE))[0]
        cos = float((c_orig @ c_edited) / (c_orig.norm() * c_edited.norm() + 1e-12))
        cos_diffs.append(cos)
    mean_cos = sum(cos_diffs) / len(cos_diffs)
    _say(f"  Mean cosine(original, edited): {mean_cos:.4f}")
    _say(f"  Expected ~0.5 if 3/4 positions match and pos 3 is random")

    # === Test D: comparison with constructed-from-scratch equivalent ===
    _say(f"\n[D] Decompose-edit-rebundle equivalent to direct construction?")
    direct_match = 0
    gen_trial = torch.Generator().manual_seed(SEED + 4)
    for trial in range(NUM_TRIALS):
        original_indices = torch.randint(0, VOCAB_SIZE, (K,), generator=gen_trial).tolist()
        c_orig = build_ctx_bundles_bsc(byte_atoms, pos_atoms,
                                        torch.tensor([original_indices], device=DEVICE))[0]
        new_byte = int(torch.randint(0, VOCAB_SIZE, (1,), generator=gen_trial).item())
        edited_indices = original_indices[:3] + [new_byte]
        # Path 1: decompose-edit-rebundle (the "edit operation" path)
        recovered = decompose_bundle(c_orig, pos_atoms, byte_atoms)
        c_via_edit = build_ctx_bundles_bsc(byte_atoms, pos_atoms,
                                            torch.tensor([recovered[:3] + [new_byte]], device=DEVICE))[0]
        # Path 2: directly construct the edited bundle (the "ground truth")
        c_direct = build_ctx_bundles_bsc(byte_atoms, pos_atoms,
                                          torch.tensor([edited_indices], device=DEVICE))[0]
        # Compare
        if torch.equal(c_via_edit, c_direct):
            direct_match += 1
    _say(f"  decompose-edit-rebundle == direct-construct: {direct_match}/{NUM_TRIALS} = {100*direct_match/NUM_TRIALS:.1f}%")
    _say(f"  If 100%: edit is mathematically equivalent to constructing from scratch.")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_memory_editing"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps({
        "round_trip_recovery_rate": rt_rate,
        "edit_position_correct": edit_pos_correct / NUM_TRIALS,
        "other_positions_preserved": other_pos_correct / NUM_TRIALS,
        "full_edit_correct": full_edit_correct / NUM_TRIALS,
        "mean_cos_orig_vs_edited": mean_cos,
        "edit_equiv_to_direct_construct": direct_match / NUM_TRIALS,
    }, indent=2))

    _say(f"\n========= MEMORY EDITING VERDICT =========")
    if rt_rate >= 0.98 and full_edit_correct / NUM_TRIALS >= 0.98 and direct_match / NUM_TRIALS >= 0.95:
        _say(f"  EDITING WORKS: substrate supports lossless CRUD operations.")
        _say(f"  This is a unique capability vs vector DBs.")
    elif rt_rate >= 0.9:
        _say(f"  EDITING MOSTLY WORKS: some imperfection from quantization.")
    else:
        _say(f"  EDITING IMPERFECT: round-trip recovery below 90%. Investigate.")


if __name__ == "__main__":
    main()
