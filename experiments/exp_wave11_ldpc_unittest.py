"""Wave 11 Phase A: LDPC-cleanup unit test.

Goal: validate the core LDPC-cleanup mechanism in isolation, BEFORE
integrating into the byte-LM (which would be Phase B and is a 1-week+
job per the design doc).

Setup:
1. Generate a regular (n, k) LDPC parity-check matrix H using a random
   row-and-column-weight constraint.
2. Find a basis of the null space of H (mod 2) — these are valid
   codewords. Pick 256 of them as "byte atoms" for the unit test.
3. Add bit-flip noise at various SNRs (5%, 10%, 20%, 30% flip rate).
4. Try to recover the original atom using:
   (a) Plain nearest-neighbor over the 256-atom codebook (baseline)
   (b) Bit-flipping LDPC decoder, then nearest-neighbor
5. Report recovery rate vs noise level.

Hypothesis: at moderate noise (10-20% flip), LDPC decoding will
substantially outperform plain nearest-neighbor because it leverages
the parity-check structure of the codebook.

Falsification: if (b) ≤ (a) within ±1% at all noise levels, the LDPC
structure doesn't help at this scale and Phase B (full byte-LM
integration) is not worth pursuing.

Code is self-contained (no pyldpc or other libraries needed).
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import torch


SEED = 17
N = 1024          # smaller n for unit test (faster)
K_INFO = 512      # information bits (so rate 1/2)
W_R = 3           # column weight (each variable in this many checks)
W_C = 6           # row weight (each check has this many variables)
NUM_ATOMS = 256   # codebook size for cleanup test
NUM_TRIALS = 200  # noisy trials per noise level
NOISE_LEVELS = [0.02, 0.05, 0.10, 0.15, 0.20, 0.30]
BP_ITERS = 30


def _say(msg: str) -> None:
    print(msg, flush=True)


def make_regular_ldpc_H(n, k_info, w_r, w_c, gen):
    """Build a regular (w_r, w_c) LDPC parity-check matrix H of shape (n-k, n).

    Uses random construction: each column has w_r ones placed at random row
    positions. Doesn't strictly enforce row weight w_c uniformly — true
    regular construction requires Gallager or PEG algorithm. This is a
    "near-regular" simplification for the unit test.
    """
    m = n - k_info  # number of parity checks
    H = torch.zeros((m, n), dtype=torch.float32)
    # For each column, pick w_r random rows
    for col in range(n):
        rows = torch.randperm(m, generator=gen)[:w_r]
        H[rows, col] = 1.0
    return H


def find_codewords_via_null_space(H, num_codewords, gen):
    """Find num_codewords solutions to H * c = 0 (mod 2) by Gauss elimination.

    Returns (num_codewords, n) tensor of ±1 codewords.
    """
    m, n = H.shape
    # Convert H to row-reduced echelon form over GF(2)
    H_work = H.clone() % 2
    pivot_cols = []
    row = 0
    for col in range(n):
        if row >= m:
            break
        # Find pivot
        pivot_row = None
        for r in range(row, m):
            if H_work[r, col] == 1:
                pivot_row = r
                break
        if pivot_row is None:
            continue
        # Swap
        if pivot_row != row:
            H_work[[row, pivot_row]] = H_work[[pivot_row, row]]
        # Eliminate
        for r in range(m):
            if r != row and H_work[r, col] == 1:
                H_work[r] = (H_work[r] + H_work[row]) % 2
        pivot_cols.append(col)
        row += 1
    # Free columns are non-pivot columns
    free_cols = [c for c in range(n) if c not in set(pivot_cols)]
    # Codewords: each free column gives a basis vector for the null space
    # The basis has dim len(free_cols)
    null_dim = len(free_cols)
    if null_dim == 0:
        raise RuntimeError(f"Null space is empty (H has rank {len(pivot_cols)} = n={n})")
    # Build basis vectors
    basis = []
    for fc_idx, fc in enumerate(free_cols):
        v = torch.zeros(n, dtype=torch.float32)
        v[fc] = 1.0
        # Solve for pivot columns: for each pivot row, set v[pivot_col] = H_work[row, fc]
        for row_i, pc in enumerate(pivot_cols):
            v[pc] = H_work[row_i, fc]
        basis.append(v)
    basis = torch.stack(basis)  # (null_dim, n) in {0, 1}
    # Generate codewords as random GF(2) combinations of basis vectors
    codewords_01 = []
    for _ in range(num_codewords):
        coeffs = torch.randint(0, 2, (null_dim,), generator=gen).float()
        cw = (coeffs @ basis) % 2
        codewords_01.append(cw)
    codewords_01 = torch.stack(codewords_01)
    # Convert {0, 1} → {-1, +1}
    return 2.0 * codewords_01 - 1.0  # (num_codewords, n)


def bit_flip_decoder(H, y_pm1, max_iters):
    """Gallager-A-style bit-flipping decoder for LDPC.

    Input: H (m, n), y_pm1 (n,) noisy ±1 codeword candidate.
    Output: decoded ±1 vector after up to max_iters flips.

    Algorithm:
    1. Compute syndromes s = H * (y → 0/1) mod 2.
    2. For each bit, count how many of its parity checks are unsatisfied.
    3. Flip the bit with the most unsatisfied checks (or any tied).
    4. Repeat until syndromes are all 0 or max_iters reached.
    """
    # Convert ±1 to {0, 1}
    y = ((y_pm1 + 1) / 2).round().clamp(0, 1)
    H_int = H.long()
    for it in range(max_iters):
        s = (H_int @ y.long()) % 2  # (m,)
        if s.sum() == 0:
            break  # codeword reached
        # For each bit, count unsatisfied checks
        # H_int[r, c] = 1 means check r involves bit c
        # bit_unsat[c] = sum_r H_int[r, c] * s[r]
        bit_unsat = (H_int.T @ s.long()).float()
        # Flip the bit with the highest unsat count
        flip_idx = bit_unsat.argmax().item()
        y[flip_idx] = 1 - y[flip_idx]
    return 2.0 * y - 1.0  # back to ±1


def add_bit_flip_noise(codeword, flip_rate, gen):
    """Flip each bit independently with prob flip_rate."""
    n = codeword.shape[0]
    flips = (torch.rand(n, generator=gen) < flip_rate).float()
    # ±1 * (1 - 2*flip) = flip sign where flip==1
    return codeword * (1.0 - 2.0 * flips)


def nearest_neighbor_recover(noisy, codebook):
    """Find nearest codebook entry by inner product (cosine equivalent for ±1)."""
    sims = codebook @ noisy
    best_idx = sims.argmax().item()
    return codebook[best_idx]


def main() -> None:
    _say("Wave 11 Phase A: LDPC cleanup unit test")
    _say(f"  n={N}, k_info={K_INFO}, w_r={W_R}, w_c={W_C}")
    _say(f"  Num atoms in codebook: {NUM_ATOMS}")
    _say(f"  Noise levels (bit-flip rate): {NOISE_LEVELS}")
    _say(f"  Trials per noise level: {NUM_TRIALS}")
    _say(f"  BP iterations: {BP_ITERS}")

    gen = torch.Generator().manual_seed(SEED)
    _say(f"\nGenerating LDPC parity-check matrix...")
    H = make_regular_ldpc_H(N, K_INFO, W_R, W_C, gen)
    _say(f"  H shape: {tuple(H.shape)}; nnz: {int(H.sum())}")

    _say(f"Finding null-space basis & generating {NUM_ATOMS} codewords...")
    codebook = find_codewords_via_null_space(H, NUM_ATOMS, gen)
    _say(f"  Codebook shape: {tuple(codebook.shape)}")
    # Sanity check: verify these are valid codewords (H * c = 0)
    sample_c = codebook[0]
    sample_c_01 = ((sample_c + 1) / 2).round().clamp(0, 1)
    syndrome = (H.long() @ sample_c_01.long()) % 2
    _say(f"  Sanity: H * (first codeword) has {int(syndrome.sum())} unsatisfied checks (should be 0)")

    _say(f"\nRunning noise/recovery trials...")
    results = []
    for noise_rate in NOISE_LEVELS:
        nn_correct = 0
        ldpc_correct = 0
        for trial in range(NUM_TRIALS):
            trial_gen = torch.Generator().manual_seed(SEED + trial * 1000 + int(noise_rate * 1e6))
            atom_idx = torch.randint(0, NUM_ATOMS, (1,), generator=trial_gen).item()
            atom = codebook[atom_idx]
            noisy = add_bit_flip_noise(atom, noise_rate, trial_gen)
            # Path A: plain nearest-neighbor over codebook
            nn_pred = nearest_neighbor_recover(noisy, codebook)
            if torch.allclose(nn_pred, atom):
                nn_correct += 1
            # Path B: LDPC bit-flip decode, then nearest-neighbor over codebook
            ldpc_decoded = bit_flip_decoder(H, noisy, BP_ITERS)
            ldpc_pred = nearest_neighbor_recover(ldpc_decoded, codebook)
            if torch.allclose(ldpc_pred, atom):
                ldpc_correct += 1
        nn_rate = nn_correct / NUM_TRIALS
        ldpc_rate = ldpc_correct / NUM_TRIALS
        results.append({"noise": noise_rate, "nn_acc": nn_rate, "ldpc_acc": ldpc_rate})
        _say(f"  noise={noise_rate:.2f}: nn_acc={nn_rate:.3f}  ldpc_acc={ldpc_rate:.3f}  delta={ldpc_rate-nn_rate:+.3f}")

    _say(f"\n========= SUMMARY =========")
    _say(f"{'noise':>6s} {'nn_acc':>8s} {'ldpc_acc':>10s} {'delta':>8s}")
    for r in results:
        _say(f"{r['noise']:>6.2f} {r['nn_acc']:>8.3f} {r['ldpc_acc']:>10.3f} {r['ldpc_acc']-r['nn_acc']:>+8.3f}")

    avg_advantage = sum(r["ldpc_acc"] - r["nn_acc"] for r in results) / len(results)
    _say(f"\n  Avg LDPC vs NN cleanup advantage: {avg_advantage:+.3f}")
    if avg_advantage > 0.05:
        _say(f"  PHASE A SUPPORT: LDPC cleanup adds non-trivial recovery. Worth Phase B byte-LM integration.")
    elif avg_advantage > 0.01:
        _say(f"  PHASE A WEAK: LDPC cleanup helps marginally. Phase B is borderline.")
    else:
        _say(f"  PHASE A REJECT: LDPC cleanup doesn't help in this regime. Skip Phase B.")

    out = {"seed": SEED, "n": N, "k_info": K_INFO, "w_r": W_R, "w_c": W_C,
           "num_atoms": NUM_ATOMS, "num_trials": NUM_TRIALS, "bp_iters": BP_ITERS,
           "results": results, "avg_advantage": avg_advantage}
    out_path = Path(__file__).resolve().parent.parent / "data" / "exp_wave11_ldpc_unittest"
    out_path.mkdir(parents=True, exist_ok=True)
    (out_path / "metrics.json").write_text(json.dumps(out, indent=2, default=str))
    _say(f"\nWrote {out_path / 'metrics.json'}")


if __name__ == "__main__":
    main()
