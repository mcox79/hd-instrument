"""Wave 13.3: Resonator Network adapted for Sweedler H_4.

Per the literature audit (notes/hopf_algebra_survey.md + post-Wave-13.2
follow-up): the right algorithm for cleanup in non-commutative VSA is
Resonator Networks (Frady-Kent-Olshausen-Sommer 2020, arXiv:2007.03748;
Renner et al. 2024 Nature Machine Intelligence for non-commutative
extensions, arXiv:2208.12880).

My earlier Δ-SVD approach was structurally doomed because Δ is an algebra
homomorphism (Δ(a·b) = Δ(a)·Δ(b)), not a rank-preserving decomposition.
Resonators sidestep this entirely.

The algorithm (alternating-projection cleanup):
1. For c = a·b with a, b from codebook C: initialize candidate y_hat
   (e.g., random codebook entry).
2. Solve a·y_hat ≈ c by least-squares in the regular representation:
   for fixed y_hat, the map a -> a·y_hat is linear (4x4 matrix R_y_hat).
   So a_hat = R_y_hat^+ · c (pseudoinverse times c).
3. Project a_hat onto codebook C: pick nearest atom.
4. Now fix a_hat, solve a_hat·b = c for b: b_hat = L_a_hat^+ · c.
5. Project b_hat onto codebook.
6. Repeat from 2 until convergence.

For stacked H_4 (1024 copies), each slot's 4x4 linear system is tiny;
iteration is fast. The full algorithm is O(stacks · iters · 4^3 +
iters · |C| · stacks · 4) per cleanup query.

Test: same as Wave 13.2 (binary bind, K=2 recovery). The resonator should
recover constituents at MUCH higher accuracy than naive cleanup.

If resonator recovery > 50% (vs naive 0%), Hopf-VSA cleanup is solved
and we can move to byte-LM integration.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import torch


SEED = 17
H_DIM = 4
STACK = 256       # smaller stack for faster resonator iteration; can scale up later
N_TOTAL = STACK * H_DIM
NUM_ATOMS = 32    # smaller codebook for clearer test
NUM_TRIALS = 50
MAX_RESONATOR_ITERS = 30


def _say(msg: str) -> None:
    print(msg, flush=True)


# ============================================================
# H_4 algebra (copied from Wave 13.2)
# ============================================================

def build_h4_multiplication_tensor():
    T = torch.zeros((H_DIM, H_DIM, H_DIM))
    T[0, 0, 0] = 1.0
    T[0, 1, 1] = 1.0
    T[0, 2, 2] = 1.0
    T[0, 3, 3] = 1.0
    T[1, 0, 1] = 1.0
    T[1, 1, 0] = 1.0
    T[1, 2, 3] = 1.0
    T[1, 3, 2] = 1.0
    T[2, 0, 2] = 1.0
    T[2, 1, 3] = -1.0
    T[3, 0, 3] = 1.0
    T[3, 1, 2] = -1.0
    return T


def h4_multiply(a, b, T):
    return torch.einsum('ijk,...si,...sj->...sk', T, a, b)


def make_h4_atoms(n_atoms, gen):
    raw = torch.randn((n_atoms, STACK, H_DIM), generator=gen)
    norms = raw.norm(dim=-1, keepdim=True).clamp(min=1e-8)
    return raw / norms


# ============================================================
# Regular representation: for each y, build L_y (left-multiplication matrix)
# such that L_y · v = y · v in H_4. L_y has shape (H_DIM, H_DIM) per slot.
# ============================================================

def build_left_mult_matrix(y, T):
    """Given y (..., STACK, H_DIM), return L_y (..., STACK, H_DIM, H_DIM)
    such that (L_y @ v)[..., s, k] = (y · v)[..., s, k].

    (y · v)[k] = sum_{i, j} T[i, j, k] y[i] v[j]
    So L_y[k, j] = sum_i T[i, j, k] y[i]
    """
    # T shape: (H_DIM, H_DIM, H_DIM) indexed (i, j, k)
    # y shape: (..., STACK, H_DIM) indexed (..., s, i)
    # L_y[..., s, k, j] = sum_i T[i, j, k] y[..., s, i]
    return torch.einsum('ijk,...si->...skj', T, y)


def build_right_mult_matrix(x, T):
    """Given x (..., STACK, H_DIM), return R_x (..., STACK, H_DIM, H_DIM)
    such that (R_x @ y)[..., s, k] = (y · x)[..., s, k].

    (y · x)[k] = sum_{i, j} T[i, j, k] y[i] x[j]
    For fixed x, this is linear in y: R_x[k, i] = sum_j T[i, j, k] x[j]
    """
    return torch.einsum('ijk,...sj->...ski', T, x)


# ============================================================
# Resonator network for H_4
# ============================================================

def _resonator_single_restart(c, codebook, T, init_a, init_b, max_iters):
    """One run of alternating projection with given initialization."""
    V = codebook.shape[0]
    a_idx = init_a
    b_idx = init_b
    a_hat = codebook[a_idx]
    b_hat = codebook[b_idx]
    prev_a, prev_b = a_idx, b_idx
    for it in range(max_iters):
        # Step A: fix b_hat, solve a_hat · b_hat = c for a_hat
        M_a = build_right_mult_matrix(b_hat, T)
        a_solved = torch.linalg.lstsq(M_a, c.unsqueeze(-1)).solution.squeeze(-1)
        sims_a = (codebook.reshape(V, -1) @ a_solved.reshape(-1))
        a_idx = sims_a.argmax().item()
        a_hat = codebook[a_idx]
        # Step B: fix a_hat, solve b_hat
        M_b = build_left_mult_matrix(a_hat, T)
        b_solved = torch.linalg.lstsq(M_b, c.unsqueeze(-1)).solution.squeeze(-1)
        sims_b = (codebook.reshape(V, -1) @ b_solved.reshape(-1))
        b_idx = sims_b.argmax().item()
        b_hat = codebook[b_idx]
        if a_idx == prev_a and b_idx == prev_b and it > 0:
            break
        prev_a, prev_b = a_idx, b_idx
    # Score: reconstruction error
    reconstructed = h4_multiply(codebook[a_idx].unsqueeze(0), codebook[b_idx].unsqueeze(0), T).squeeze(0)
    error = (reconstructed - c).pow(2).sum().item()
    return a_idx, b_idx, it + 1, error


def resonator_cleanup_h4(c, codebook, T, max_iters=MAX_RESONATOR_ITERS, num_restarts=10, gen=None):
    """Alternating-projection cleanup with multiple random restarts.

    Returns the best (a_hat_idx, b_hat_idx) by reconstruction error.
    """
    V = codebook.shape[0]
    if gen is None:
        gen = torch.Generator().manual_seed(0)
    best_a, best_b, best_iters, best_err = -1, -1, -1, float("inf")
    # Always include the (0, 1) fixed init for reproducibility
    init_pairs = [(0, 1 if V > 1 else 0)]
    # Add random restarts
    for _ in range(num_restarts - 1):
        ai = torch.randint(0, V, (1,), generator=gen).item()
        bi = torch.randint(0, V, (1,), generator=gen).item()
        if ai == bi and V > 1:
            bi = (bi + 1) % V
        init_pairs.append((ai, bi))
    for init_a, init_b in init_pairs:
        a, b, iters, err = _resonator_single_restart(c, codebook, T, init_a, init_b, max_iters)
        if err < best_err:
            best_err = err
            best_a, best_b, best_iters = a, b, iters
    return best_a, best_b, best_iters


def main() -> None:
    _say("Wave 13.3: Resonator Network adapted for Sweedler H_4")
    _say(f"  H_DIM={H_DIM}, STACK={STACK}, N_TOTAL={N_TOTAL}")
    _say(f"  num_atoms={NUM_ATOMS}, num_trials={NUM_TRIALS}, max_iters={MAX_RESONATOR_ITERS}")
    _say(f"  Algorithm: alternating-projection least-squares in regular representation")
    _say(f"  Reference: Frady-Kent 2020 + Renner 2024 (non-commutative extension)")

    T = build_h4_multiplication_tensor()
    gen = torch.Generator().manual_seed(SEED)
    atoms = make_h4_atoms(NUM_ATOMS, gen)
    _say(f"\nGenerated codebook: {tuple(atoms.shape)}")

    # Binary bind cleanup test
    _say(f"\nBinary bind cleanup test:")
    naive_correct = 0
    resonator_correct_either = 0
    resonator_correct_both = 0
    converge_iters = []
    for trial in range(NUM_TRIALS):
        tgen = torch.Generator().manual_seed(SEED + 5000 + trial)
        a_idx_true = torch.randint(0, NUM_ATOMS, (1,), generator=tgen).item()
        b_idx_true = torch.randint(0, NUM_ATOMS, (1,), generator=tgen).item()
        if a_idx_true == b_idx_true:
            b_idx_true = (b_idx_true + 1) % NUM_ATOMS
        a = atoms[a_idx_true]
        b = atoms[b_idx_true]
        c = h4_multiply(a.unsqueeze(0), b.unsqueeze(0), T).squeeze(0)

        # Naive cleanup baseline: top-2 codebook entries by inner product with c
        c_flat = c.reshape(-1)
        atoms_flat = atoms.reshape(NUM_ATOMS, -1)
        sims = atoms_flat @ c_flat
        top2 = sims.topk(2).indices.tolist()
        if a_idx_true in top2 and b_idx_true in top2:
            naive_correct += 1

        # Resonator network
        a_hat, b_hat, iters = resonator_cleanup_h4(c, atoms, T)
        converge_iters.append(iters)
        # Check if both true atoms were identified (order-insensitive)
        found = {a_hat, b_hat}
        expected = {a_idx_true, b_idx_true}
        if found == expected:
            resonator_correct_both += 1
        if a_idx_true in found or b_idx_true in found:
            resonator_correct_either += 1

    avg_iters = sum(converge_iters) / len(converge_iters)
    _say(f"  Naive top-2 cleanup:                {naive_correct}/{NUM_TRIALS} ({100*naive_correct/NUM_TRIALS:.0f}%)")
    _say(f"  Resonator (BOTH atoms recovered):   {resonator_correct_both}/{NUM_TRIALS} ({100*resonator_correct_both/NUM_TRIALS:.0f}%)")
    _say(f"  Resonator (at least 1 recovered):   {resonator_correct_either}/{NUM_TRIALS} ({100*resonator_correct_either/NUM_TRIALS:.0f}%)")
    _say(f"  Average iterations to convergence:  {avg_iters:.1f}/{MAX_RESONATOR_ITERS}")

    _say(f"\n========= SUMMARY =========")
    if resonator_correct_both >= NUM_TRIALS // 2:
        _say(f"  RESONATOR WORKS: Hopf-VSA cleanup via resonator is validated.")
        _say(f"  Next: integrate into byte-LM (Wave 13.4) or extend to Drinfeld D(S_3).")
    elif resonator_correct_either >= NUM_TRIALS // 2:
        _say(f"  PARTIAL: resonator finds ONE atom but not the pair. Algorithm needs refinement.")
        _say(f"  Possible fix: better initialization (multiple restarts), longer iteration.")
    else:
        _say(f"  RESONATOR FAILS at this configuration. Investigate:")
        _say(f"  - Are 4x4 lstsq problems numerically conditioned?")
        _say(f"  - Is the codebook size too small? Too large?")
        _say(f"  - Need different initialization or update rule?")

    out = {"seed": SEED, "h_dim": H_DIM, "stack": STACK, "n_total": N_TOTAL,
           "num_atoms": NUM_ATOMS, "num_trials": NUM_TRIALS, "max_iters": MAX_RESONATOR_ITERS,
           "naive_correct": naive_correct,
           "resonator_both": resonator_correct_both,
           "resonator_either": resonator_correct_either,
           "avg_iters": avg_iters}
    out_path = Path(__file__).resolve().parent.parent / "data" / "exp_wave13_3_hopf_resonator"
    out_path.mkdir(parents=True, exist_ok=True)
    (out_path / "metrics.json").write_text(json.dumps(out, indent=2, default=str))
    _say(f"\nWrote {out_path / 'metrics.json'}")


if __name__ == "__main__":
    main()
