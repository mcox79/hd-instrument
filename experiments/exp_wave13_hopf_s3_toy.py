"""Wave 13 Phase A: S_3 group algebra VSA — toy capacity test.

Per the design doc (notes/wave13_hopf_design.md), Phase A is a toy
capacity test on the smallest non-abelian group S_3, not the full
byte-LM integration.

The test:
1. Generate random "atoms" in k[S_3]^stack — each atom is 682 stacked
   coefficient vectors of dim 6 (one per group element).
2. Verify the binding operation (group-algebra convolution) is
   actually non-commutative.
3. Run a capacity test: bind K atoms, bundle, unbind via antipode,
   measure top-1 recovery accuracy. Compare to FHRR at matched dim.

If S_3 binding has capacity advantage at our K=4 setting, then Hopf VSA
is worth the full byte-LM integration (Phase B).

This is a 100% CPU experiment, ~5 min runtime.
"""

from __future__ import annotations

import json
import math
import time
from pathlib import Path

import torch


SEED = 17
GROUP_ORDER = 6  # |S_3|
STACK = 682      # 682 * 6 = 4092 ≈ 4096
N_TOTAL = STACK * GROUP_ORDER
NUM_ATOMS = 256
K_VALUES = [1, 2, 4, 8, 16]
NUM_TRIALS = 100


def _say(msg: str) -> None:
    print(msg, flush=True)


# S_3 elements indexed 0..5: e, (12), (13), (23), (123), (132)
# Multiplication table: S3_MUL[a][b] = a * b
S3_MUL = torch.tensor([
    [0, 1, 2, 3, 4, 5],   # e * x = x
    [1, 0, 4, 5, 2, 3],   # (12) * x
    [2, 5, 0, 4, 3, 1],   # (13) * x
    [3, 4, 5, 0, 1, 2],   # (23) * x
    [4, 3, 1, 2, 5, 0],   # (123) * x
    [5, 2, 3, 1, 0, 4],   # (132) * x
], dtype=torch.long)

# Group inverses: g^{-1}
S3_INV = torch.tensor([0, 1, 2, 3, 5, 4], dtype=torch.long)


def precompute_convolution_tensor():
    """Precompute T[i, j, k] = 1 if g_i * g_j = g_k else 0.

    Then (a * b)[k] = sum_{i,j} T[i, j, k] · a[i] · b[j].
    Equivalent matrix form: (a * b) = a @ M @ b.T where M[i, j] is a one-hot for the result.

    For efficient batched computation, we store T as a (6, 6, 6) sparse tensor.
    """
    T = torch.zeros((GROUP_ORDER, GROUP_ORDER, GROUP_ORDER))
    for i in range(GROUP_ORDER):
        for j in range(GROUP_ORDER):
            k = S3_MUL[i, j].item()
            T[i, j, k] = 1.0
    return T


def s3_group_convolution(a, b, T):
    """Per-stack group convolution.

    a, b: (..., STACK, GROUP_ORDER) tensors
    T: (GROUP_ORDER, GROUP_ORDER, GROUP_ORDER) convolution structure tensor
    Returns: (..., STACK, GROUP_ORDER) result.
    """
    # (a * b)[..., s, k] = sum_{i, j} T[i, j, k] * a[..., s, i] * b[..., s, j]
    # = sum_i a[..., s, i] * sum_j T[i, j, k] * b[..., s, j]
    # = sum_i a[..., s, i] * (T[i, :, :].T @ b[..., s, :])
    # Best to use einsum
    return torch.einsum("ijk,...si,...sj->...sk", T, a, b)


def s3_antipode(a):
    """Per-stack antipode: a'[..., s, g] = a[..., s, g^{-1}]."""
    # For each group element index, look up the inverse
    return a[..., S3_INV]


def make_s3_atoms(n_atoms, gen):
    """Random S_3 group algebra atoms, L2-normalized per stack site."""
    raw = torch.randn((n_atoms, STACK, GROUP_ORDER), generator=gen)
    norms = raw.norm(dim=-1, keepdim=True).clamp(min=1e-8)
    return raw / norms


def make_fhrr_atoms_real_view(n_atoms, gen):
    """FHRR baseline at matched dim (treating as real 4092-dim phasor representations)."""
    phases = torch.rand((n_atoms, N_TOTAL // 2), generator=gen) * (2 * math.pi)
    return torch.stack([torch.cos(phases), torch.sin(phases)], dim=-1).reshape(n_atoms, N_TOTAL)


def main() -> None:
    _say("Wave 13 Phase A: S_3 group algebra VSA — toy capacity test")
    _say(f"  GROUP_ORDER={GROUP_ORDER}, STACK={STACK}, N_TOTAL={N_TOTAL}")
    _say(f"  num_atoms={NUM_ATOMS}, K_values={K_VALUES}, num_trials={NUM_TRIALS}")

    T = precompute_convolution_tensor()
    gen = torch.Generator().manual_seed(SEED)

    # Sanity check: verify non-commutativity
    _say(f"\nSanity check: non-commutativity of S_3 group convolution")
    a = torch.randn(1, STACK, GROUP_ORDER)
    b = torch.randn(1, STACK, GROUP_ORDER)
    ab = s3_group_convolution(a, b, T)
    ba = s3_group_convolution(b, a, T)
    diff = (ab - ba).abs().max().item()
    _say(f"  max |ab - ba| = {diff:.6f}  (should be substantial, > 0.1)")
    if diff < 0.01:
        _say(f"  WARNING: binding looks commutative! Implementation bug?")

    # Sanity check: antipode unbinds
    _say(f"\nSanity check: antipode unbinds")
    a = torch.randn(1, STACK, GROUP_ORDER)
    a_norm = a / a.norm(dim=-1, keepdim=True).clamp(min=1e-8)
    b = torch.randn(1, STACK, GROUP_ORDER)
    b_norm = b / b.norm(dim=-1, keepdim=True).clamp(min=1e-8)
    bound = s3_group_convolution(a_norm, b_norm, T)
    # To unbind a, multiply by antipode(a) from left: antipode(a) * (a * b) = b (if a is invertible)
    a_inv = s3_antipode(a_norm)
    unbound = s3_group_convolution(a_inv, bound, T)
    sim_with_b = (unbound * b_norm).sum().item() / (STACK * GROUP_ORDER)
    sim_with_other = (unbound * a_norm).sum().item() / (STACK * GROUP_ORDER)
    _say(f"  similarity(antipode(a) * (a*b), b) = {sim_with_b:.4f}  (should be high)")
    _say(f"  similarity(antipode(a) * (a*b), a) = {sim_with_other:.4f}  (should be near 0)")

    # Generate atom codebook
    _say(f"\nGenerating S_3 codebook ({NUM_ATOMS} atoms)...")
    s3_atoms = make_s3_atoms(NUM_ATOMS, gen)
    _say(f"  shape: {tuple(s3_atoms.shape)}")

    # Generate FHRR codebook for baseline
    fhrr_atoms = make_fhrr_atoms_real_view(NUM_ATOMS, gen)
    _say(f"  FHRR baseline shape: {tuple(fhrr_atoms.shape)}")

    # Capacity test
    _say(f"\nCapacity test: K-fold bind + bundle + unbind, recover atom 0")
    results = []
    for K in K_VALUES:
        s3_correct = 0
        fhrr_correct = 0
        for trial in range(NUM_TRIALS):
            tg = torch.Generator().manual_seed(SEED + 1000 * trial + K)
            # Pick K position-atom indices
            pos_indices_s3 = torch.randperm(NUM_ATOMS, generator=tg)[:K]
            pos_indices_fhrr = pos_indices_s3.clone()
            # Bind: target_atom * pos_1, target_atom * pos_2, ... target_atom * pos_K
            # No actually for HDC bundle test: bundle K different (val, pos) pairs
            # We're testing: given the bundle = sum_i (val_i * pos_i), recover val_0 given pos_0
            val_indices = torch.randperm(NUM_ATOMS, generator=tg)[:K]

            # S_3 version
            bundle_s3 = torch.zeros((STACK, GROUP_ORDER))
            for i in range(K):
                bound_i = s3_group_convolution(
                    s3_atoms[val_indices[i]].unsqueeze(0),
                    s3_atoms[pos_indices_s3[i]].unsqueeze(0),
                    T
                ).squeeze(0)
                bundle_s3 = bundle_s3 + bound_i
            # Recover val_0: unbind pos_0
            unbound_s3 = s3_group_convolution(
                s3_antipode(s3_atoms[pos_indices_s3[0]]).unsqueeze(0),
                bundle_s3.unsqueeze(0),
                T
            ).squeeze(0)
            # Find nearest atom in codebook
            sims = (s3_atoms.reshape(NUM_ATOMS, -1) @ unbound_s3.reshape(-1))
            best_s3 = sims.argmax().item()
            if best_s3 == val_indices[0].item():
                s3_correct += 1

            # FHRR version (elementwise multiply, no group structure)
            bundle_fhrr = torch.zeros(N_TOTAL)
            for i in range(K):
                bound_i = fhrr_atoms[val_indices[i]] * fhrr_atoms[pos_indices_fhrr[i]]
                bundle_fhrr = bundle_fhrr + bound_i
            # Recover val_0: unbind pos_0 (for real-FHRR-like, multiply by pos_0 again)
            unbound_fhrr = fhrr_atoms[pos_indices_fhrr[0]] * bundle_fhrr
            sims = fhrr_atoms @ unbound_fhrr
            best_fhrr = sims.argmax().item()
            if best_fhrr == val_indices[0].item():
                fhrr_correct += 1

        s3_acc = s3_correct / NUM_TRIALS
        fhrr_acc = fhrr_correct / NUM_TRIALS
        results.append({"K": K, "s3_acc": s3_acc, "fhrr_acc": fhrr_acc})
        _say(f"  K={K:2d}: S_3 recovery={s3_acc:.3f}  FHRR recovery={fhrr_acc:.3f}  delta={s3_acc-fhrr_acc:+.3f}")

    _say(f"\n========= SUMMARY =========")
    _say(f"  Capacity comparison: S_3 group algebra vs FHRR at matched dim")
    for r in results:
        _say(f"  K={r['K']:2d}: S_3={r['s3_acc']:.3f}  FHRR={r['fhrr_acc']:.3f}  Δ={r['s3_acc']-r['fhrr_acc']:+.3f}")

    avg_s3 = sum(r["s3_acc"] for r in results) / len(results)
    avg_fhrr = sum(r["fhrr_acc"] for r in results) / len(results)
    _say(f"\n  Avg: S_3 = {avg_s3:.3f}, FHRR = {avg_fhrr:.3f}, Δ = {avg_s3 - avg_fhrr:+.3f}")
    if avg_s3 > avg_fhrr + 0.05:
        _say(f"  Phase A SUPPORT: S_3 group algebra has capacity advantage. Worth Phase B byte-LM.")
    elif avg_s3 > avg_fhrr - 0.02:
        _say(f"  Phase A NEUTRAL: roughly matched. Group algebra doesn't add capacity but doesn't hurt.")
    else:
        _say(f"  Phase A REJECT: S_3 group algebra underperforms. Skip Phase B.")

    out = {"seed": SEED, "group_order": GROUP_ORDER, "stack": STACK, "n_total": N_TOTAL,
           "num_atoms": NUM_ATOMS, "K_values": K_VALUES, "num_trials": NUM_TRIALS,
           "results": results, "avg_s3": avg_s3, "avg_fhrr": avg_fhrr}
    out_path = Path(__file__).resolve().parent.parent / "data" / "exp_wave13_hopf_s3_toy"
    out_path.mkdir(parents=True, exist_ok=True)
    (out_path / "metrics.json").write_text(json.dumps(out, indent=2, default=str))
    _say(f"\nWrote {out_path / 'metrics.json'}")


if __name__ == "__main__":
    main()
