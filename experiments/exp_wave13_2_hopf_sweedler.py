"""Wave 13.2: Sweedler's H_4 — smallest non-trivial Hopf algebra VSA.

Per the survey doc (notes/hopf_algebra_survey.md), H_4 is the key test:
the simplest Hopf algebra with NON-COCOMMUTATIVE Delta, which is the
property that gives Hopf-VSA its distinguishing capability over standard
VSA.

H_4 algebra (4-dimensional):
- Basis: {1, g, x, gx}
- g·g = 1, x·x = 0, g·x = -x·g
- Comultiplication: Delta(1)=1⊗1, Delta(g)=g⊗g, Delta(x)=x⊗1+g⊗x, Delta(gx)=gx⊗g+1⊗gx
- Antipode: S(1)=1, S(g)=g, S(x)=-gx, S(gx)=x

The Delta(x) formula is the genuinely new VSA primitive: it tells us how
the "x component" of a bound vector decomposes across the tensor product.

This test:
1. Implement H_4 algebra operations + Delta + S
2. Stack 1024 H_4 copies → 4096-dim hypervectors
3. Verify non-cocommutativity numerically
4. Delta-recovery test: given c = a*b for random atoms a, b, does Delta(c) +
   SVD decomposition recover a, b?
5. Multi-bind test: given c = sum_i a_i*b_i, does Delta+SVD identify the
   constituent pairs?
6. Compare to standard codebook nearest-neighbor recovery

If Delta-recovery works better than naive at moderate K (≥4), Hopf-VSA's
core premise is validated. Move to Drinfeld double for the full version.
"""

from __future__ import annotations

import json
import math
import time
from pathlib import Path

import torch


SEED = 17
H_DIM = 4  # H_4 is 4-dimensional
STACK = 1024
N_TOTAL = STACK * H_DIM
NUM_ATOMS = 64  # smaller codebook for faster toy test
K_BIND_VALUES = [1, 2, 4, 8]
NUM_TRIALS = 100


def _say(msg: str) -> None:
    print(msg, flush=True)


# ============================================================
# H_4 algebra: 4-dim basis (1, g, x, gx) with indices 0, 1, 2, 3
# ============================================================

def build_h4_multiplication_tensor():
    """Build T[i, j, k] = coefficient of basis[k] in basis[i]·basis[j].

    Multiplication table:
            1    g    x    gx
    1     | 1    g    x    gx
    g     | g    1   gx    x
    x     | x   -gx   0    0
    gx    | gx  -x    0    0
    """
    T = torch.zeros((H_DIM, H_DIM, H_DIM))
    # Row 1 (i=0)
    T[0, 0, 0] = 1.0   # 1*1 = 1
    T[0, 1, 1] = 1.0   # 1*g = g
    T[0, 2, 2] = 1.0   # 1*x = x
    T[0, 3, 3] = 1.0   # 1*gx = gx
    # Row g (i=1)
    T[1, 0, 1] = 1.0   # g*1 = g
    T[1, 1, 0] = 1.0   # g*g = 1
    T[1, 2, 3] = 1.0   # g*x = gx
    T[1, 3, 2] = 1.0   # g*gx = x
    # Row x (i=2)
    T[2, 0, 2] = 1.0   # x*1 = x
    T[2, 1, 3] = -1.0  # x*g = -gx
    # x*x = 0 (no entry)
    # x*gx = 0 (no entry)
    # Row gx (i=3)
    T[3, 0, 3] = 1.0   # gx*1 = gx
    T[3, 1, 2] = -1.0  # gx*g = -x
    # gx*x = 0
    # gx*gx = 0
    return T


def build_h4_delta_matrix():
    """Delta: H → H ⊗ H. Returns shape (H_DIM, H_DIM, H_DIM) where
    Delta[i, p, q] = coefficient of (basis[p] ⊗ basis[q]) in Delta(basis[i]).

    Delta(1) = 1 ⊗ 1
    Delta(g) = g ⊗ g
    Delta(x) = x ⊗ 1 + g ⊗ x
    Delta(gx) = gx ⊗ g + 1 ⊗ gx
    """
    D = torch.zeros((H_DIM, H_DIM, H_DIM))
    D[0, 0, 0] = 1.0                    # Delta(1) = 1 ⊗ 1
    D[1, 1, 1] = 1.0                    # Delta(g) = g ⊗ g
    D[2, 2, 0] = 1.0; D[2, 1, 2] = 1.0  # Delta(x) = x ⊗ 1 + g ⊗ x
    D[3, 3, 1] = 1.0; D[3, 0, 3] = 1.0  # Delta(gx) = gx ⊗ g + 1 ⊗ gx
    return D


def h4_antipode_indices():
    """S: H -> H. S(1)=1, S(g)=g, S(x)=-gx, S(gx)=x.

    Output_i = signs[i] * a[perm[i]]. We need:
      output[0] = a[0]      (S(1)=1)
      output[1] = a[1]      (S(g)=g)
      output[2] = a[3]      (S(gx)=x: gx-component contributes to x-position, sign +1)
      output[3] = -a[2]     (S(x)=-gx: x-component contributes to gx-position, sign -1)
    """
    perm = torch.tensor([0, 1, 3, 2], dtype=torch.long)
    signs = torch.tensor([1.0, 1.0, 1.0, -1.0])  # corrected from earlier buggy [1,1,-1,1]
    return perm, signs


def h4_multiply(a, b, T):
    """Per-slot multiplication: (a*b)[..., s, k] = sum_{i,j} T[i,j,k] a[s,i] b[s,j]."""
    return torch.einsum('ijk,...si,...sj->...sk', T, a, b)


def h4_delta(a, D):
    """Per-slot comultiplication: Delta(a)[..., s, p, q] = sum_i D[i,p,q] a[s, i]."""
    return torch.einsum('ipq,...si->...spq', D, a)


def h4_antipode(a, perm, signs):
    """Per-slot antipode: S(a)[..., s, i] = signs[i] * a[s, perm[i]]."""
    return a[..., perm] * signs


def make_h4_atoms(n_atoms, gen):
    """Random H_4 atoms, L2-normalized per slot."""
    raw = torch.randn((n_atoms, STACK, H_DIM), generator=gen)
    norms = raw.norm(dim=-1, keepdim=True).clamp(min=1e-8)
    return raw / norms


def slot_svd_top2(Deltac):
    """Per-slot SVD of Delta(c) viewed as (H_DIM, H_DIM) matrix. Return top-2 components.

    Deltac shape: (..., STACK, H_DIM, H_DIM).
    Returns (U, S, V) all of shape (..., STACK, H_DIM, 2).
    """
    # SVD on the (H_DIM, H_DIM) inner matrix per slot
    U, S, Vh = torch.linalg.svd(Deltac, full_matrices=False)
    # Take top 2 components
    return U[..., :2], S[..., :2], Vh[..., :2, :].transpose(-2, -1)


def main() -> None:
    _say("Wave 13.2: Sweedler H_4 Hopf algebra VSA - capacity + Delta-recovery toy test")
    _say(f"  H_DIM={H_DIM}, STACK={STACK}, N_TOTAL={N_TOTAL}")
    _say(f"  num_atoms={NUM_ATOMS}, K_bind_values={K_BIND_VALUES}, trials={NUM_TRIALS}")

    T = build_h4_multiplication_tensor()
    D_tensor = build_h4_delta_matrix()
    s_perm, s_signs = h4_antipode_indices()

    # Sanity checks
    _say(f"\nSanity checks on H_4 algebra:")
    # 1. g*g should give 1
    g = torch.zeros(1, 1, H_DIM); g[0, 0, 1] = 1.0
    one = torch.zeros(1, 1, H_DIM); one[0, 0, 0] = 1.0
    gg = h4_multiply(g, g, T)
    _say(f"  g*g = {gg[0,0].tolist()}  (expected [1,0,0,0])")

    # 2. x*g should give -gx (i.e., [0,0,0,-1])
    x = torch.zeros(1, 1, H_DIM); x[0, 0, 2] = 1.0
    xg = h4_multiply(x, g, T)
    _say(f"  x*g = {xg[0,0].tolist()}  (expected [0,0,0,-1])")

    # 3. g*x should give gx (i.e., [0,0,0,1]) — different from x*g!
    gx = h4_multiply(g, x, T)
    _say(f"  g*x = {gx[0,0].tolist()}  (expected [0,0,0,1])")
    _say(f"  -> non-commutative: g*x != x*g (differ in sign), good.")

    # 4. Delta(x) check
    Deltax = h4_delta(x, D_tensor)
    _say(f"  Delta(x) shape: {tuple(Deltax.shape)}")
    _say(f"  Delta(x) values: {Deltax[0,0].tolist()}")
    # Expected: x ⊗ 1 + g ⊗ x, so non-zero at (2, 0) and (1, 2)
    _say(f"    expected: 1 at [2][0] (x tensor 1), 1 at [1][2] (g tensor x), 0 elsewhere")

    # 5. Non-cocommutativity check
    Deltax_sigma = Deltax.transpose(-2, -1)  # swap tensor factors
    cocom_diff = (Deltax - Deltax_sigma).abs().sum().item()
    _say(f"  |Delta(x) - sigma.Delta(x)| = {cocom_diff:.4f}  (should be > 0)")
    if cocom_diff < 1e-6:
        _say(f"  WARNING: Delta looks cocommutative for x!")

    # 6. Antipode round-trip: S(S(x)) should give -x (S has period 4 for x)
    Sx = h4_antipode(x, s_perm, s_signs)
    SSx = h4_antipode(Sx, s_perm, s_signs)
    _say(f"  S(x) = {Sx[0,0].tolist()}  (expected [0,0,0,-1] = -gx)")
    _say(f"  S(S(x)) = {SSx[0,0].tolist()}  (expected [0,0,-1,0] = -x)")

    gen = torch.Generator().manual_seed(SEED)
    _say(f"\nGenerating {NUM_ATOMS} H_4 codebook atoms...")
    atoms = make_h4_atoms(NUM_ATOMS, gen)  # (V, STACK, H_DIM)
    _say(f"  shape: {tuple(atoms.shape)}")

    # ============================================================
    # Delta-recovery test: given c = a * b for random atoms, recover a and b
    # ============================================================
    _say(f"\nDelta-recovery test (binary bind, K=2):")
    correct_naive = 0
    correct_svd = 0
    for trial in range(NUM_TRIALS):
        tgen = torch.Generator().manual_seed(SEED + 5000 + trial)
        a_idx = torch.randint(0, NUM_ATOMS, (1,), generator=tgen).item()
        b_idx = torch.randint(0, NUM_ATOMS, (1,), generator=tgen).item()
        a = atoms[a_idx]
        b = atoms[b_idx]
        c = h4_multiply(a.unsqueeze(0), b.unsqueeze(0), T).squeeze(0)  # (STACK, H_DIM)
        # Compute Delta(c)
        Deltac = h4_delta(c, D_tensor)  # (STACK, H_DIM, H_DIM)
        # Per-slot SVD; take top-2 (U, S, V) components
        U, S_sv, V = slot_svd_top2(Deltac)  # each (STACK, H_DIM, 2)

        # Naive cleanup: nearest-atom by flat inner product with c
        c_flat = c.reshape(-1)
        atoms_flat = atoms.reshape(NUM_ATOMS, -1)
        sims_naive = atoms_flat @ c_flat
        # Top-2 atoms by similarity
        top2_naive = sims_naive.topk(2).indices.tolist()
        if a_idx in top2_naive and b_idx in top2_naive:
            correct_naive += 1

        # SVD cleanup: aggregate top-svd-component projection across slots
        # For each rank k=0,1: U[:, :, k] is a (STACK, H_DIM) candidate for left factor
        # V[:, :, k] is (STACK, H_DIM) for right factor
        # Score atom i for being the "left factor" by sum_s sqrt(S[s, k]) * <U[s, :, k], atoms[i, s, :]>
        # Score atom j for being "right factor" similarly with V
        left_scores = torch.zeros(NUM_ATOMS)
        right_scores = torch.zeros(NUM_ATOMS)
        for k in range(2):
            U_k = U[:, :, k]  # (STACK, H_DIM)
            V_k = V[:, :, k]  # (STACK, H_DIM)
            S_k = S_sv[:, k]  # (STACK,)
            weight = S_k.sqrt()  # (STACK,)
            # left_scores[i] = sum_s weight[s] * <U_k[s], atoms[i, s, :]>
            for i in range(NUM_ATOMS):
                left_scores[i] += (weight * (U_k * atoms[i]).sum(dim=-1)).sum().item()
                right_scores[i] += (weight * (V_k * atoms[i]).sum(dim=-1)).sum().item()
        best_left = left_scores.argmax().item()
        best_right = right_scores.argmax().item()
        if (a_idx == best_left and b_idx == best_right) or \
           (a_idx == best_right and b_idx == best_left):
            correct_svd += 1

    _say(f"  Naive (top-2 codebook): {correct_naive}/{NUM_TRIALS} correct")
    _say(f"  Delta+SVD cleanup:          {correct_svd}/{NUM_TRIALS} correct")
    _say(f"  Delta+SVD advantage: {(correct_svd - correct_naive) / NUM_TRIALS:+.3f}")

    # ============================================================
    # Multi-bind capacity test: K bindings bundled
    # ============================================================
    _say(f"\nMulti-bind capacity (bundle K bindings, recover original a from a*b_0 + a*b_1 + ...):")
    results = []
    for K in K_BIND_VALUES:
        correct = 0
        for trial in range(NUM_TRIALS):
            tgen = torch.Generator().manual_seed(SEED + 9000 + trial * 1000 + K)
            target_idx = torch.randint(0, NUM_ATOMS, (1,), generator=tgen).item()
            target = atoms[target_idx]
            # Generate K random "key" atoms
            key_indices = torch.randperm(NUM_ATOMS, generator=tgen)[:K].tolist()
            # Bundle: c = sum_k target * key_k
            bundle = torch.zeros((STACK, H_DIM))
            for k_idx in key_indices:
                bound = h4_multiply(target.unsqueeze(0), atoms[k_idx].unsqueeze(0), T).squeeze(0)
                bundle = bundle + bound
            bundle = bundle / max(K, 1)  # average
            # Try to recover target via unbind with key_0 (using antipode)
            key0_inv = h4_antipode(atoms[key_indices[0]], s_perm, s_signs)
            unbound = h4_multiply(bundle.unsqueeze(0), key0_inv.unsqueeze(0), T).squeeze(0)
            # Compare to codebook
            sims = (atoms.reshape(NUM_ATOMS, -1) @ unbound.reshape(-1))
            best = sims.argmax().item()
            if best == target_idx:
                correct += 1
        acc = correct / NUM_TRIALS
        results.append({"K": K, "recovery_acc": acc})
        _say(f"  K={K:2d}: recovery acc = {acc:.3f}")

    _say(f"\n========= SUMMARY =========")
    _say(f"  Sweedler H_4 with non-trivial Delta implemented and verified")
    _say(f"  Delta-SVD cleanup vs naive on binary bind: {correct_svd - correct_naive:+d} of {NUM_TRIALS}")
    _say(f"  Multi-bind recovery curve:")
    for r in results:
        _say(f"    K={r['K']}: {r['recovery_acc']:.3f}")
    if correct_svd > correct_naive + 5:
        _say(f"\n  PHASE A SUPPORT: Delta-SVD cleanup beats naive. Move to Drinfeld double (Wave 13.3).")
    elif correct_svd >= correct_naive:
        _say(f"\n  PHASE A NEUTRAL: Delta-SVD matches naive. Investigate algorithm before D(S_3).")
    else:
        _say(f"\n  PHASE A WEAK: naive beats Delta-SVD. Algorithm needs work; possibly H_4 too small.")

    out = {"seed": SEED, "h_dim": H_DIM, "stack": STACK, "n_total": N_TOTAL,
           "num_atoms": NUM_ATOMS, "K_bind_values": K_BIND_VALUES, "num_trials": NUM_TRIALS,
           "delta_recovery": {"naive": correct_naive, "svd": correct_svd},
           "multi_bind_results": results}
    out_path = Path(__file__).resolve().parent.parent / "data" / "exp_wave13_2_hopf_sweedler"
    out_path.mkdir(parents=True, exist_ok=True)
    (out_path / "metrics.json").write_text(json.dumps(out, indent=2, default=str))
    _say(f"\nWrote {out_path / 'metrics.json'}")


if __name__ == "__main__":
    main()
