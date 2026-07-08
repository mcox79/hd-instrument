"""Scaffold-free witness for BSC (Binary Spatter Code) binding in hdlab.binding.

BSC is bipolar {-1,+1}: bind = elementwise multiply (exactly self-inverse for bipolar b),
unbind = bind again, bundle = majority sign of the sum (ties to +1). This witness checks:
- exact self-inverse recovery of bind/unbind (int8 and float32),
- commutativity of bind,
- bit-equality against the read-only reference oracle (reference/bsc.py),
- majority-vote correctness + tie-break of bundle,
- 2-D input validation on bundle,
- capacity scaling consistent with the Week 8 law k_50% ~ N^1.004 (near-linear): the
  measured exponent from a two-point (N=512 vs N=1024) role-filler bundle sweep is within
  tolerance of theory.bsc_capacity_exponent().

Passes with tracing=False (no trace bus is set; hdlab.tracing.emit is a no-op).
"""
from __future__ import annotations

import math

import pytest
import torch

from hdlab import binding
from reference import bsc as ref_bsc
from verification import theory


def _bipolar(shape, gen: torch.Generator) -> torch.Tensor:
    """Random bipolar {-1,+1} int8 tensor of the given shape."""
    return (2 * torch.randint(0, 2, shape, generator=gen) - 1).to(torch.int8)


def test_bind_unbind_self_inverse_exact_int8() -> None:
    """unbind(bind(a, b), b) == a bit-exactly for bipolar int8 vectors."""
    gen = torch.Generator().manual_seed(0)
    a = _bipolar((1024,), gen)
    b = _bipolar((1024,), gen)
    c = binding.bsc_bind(a, b)
    rec = binding.bsc_unbind(c, b)
    assert torch.equal(rec, a)
    assert rec.dtype == torch.int8


def test_bind_unbind_self_inverse_exact_float32() -> None:
    """unbind(bind(a, b), b) == a bit-exactly for bipolar float32 vectors (b*b == 1 exactly)."""
    gen = torch.Generator().manual_seed(1)
    a = _bipolar((1024,), gen).to(torch.float32)
    b = _bipolar((1024,), gen).to(torch.float32)
    c = binding.bsc_bind(a, b)
    rec = binding.bsc_unbind(c, b)
    assert torch.equal(rec, a)
    assert rec.dtype == torch.float32


def test_bind_commutative() -> None:
    """bind(a, b) == bind(b, a) (elementwise multiply is commutative)."""
    gen = torch.Generator().manual_seed(2)
    a = _bipolar((512,), gen)
    b = _bipolar((512,), gen)
    assert torch.equal(binding.bsc_bind(a, b), binding.bsc_bind(b, a))


def test_matches_reference_oracle() -> None:
    """binding.bsc_* is bit-identical to the read-only reference oracle (reference/bsc.py)."""
    gen = torch.Generator().manual_seed(3)
    a = ref_bsc.make_atom(1024, gen)
    b = ref_bsc.make_atom(1024, gen)
    assert torch.equal(binding.bsc_bind(a, b), ref_bsc.bind(a, b))
    c = binding.bsc_bind(a, b)
    assert torch.equal(binding.bsc_unbind(c, b), ref_bsc.unbind(c, b))
    stack = torch.stack([ref_bsc.make_atom(1024, gen) for _ in range(9)])
    assert torch.equal(binding.bsc_bundle(stack), ref_bsc.bundle(stack))


def test_bundle_majority_and_tie_break() -> None:
    """bundle is column-wise majority sign; exact ties (sum == 0) resolve to +1."""
    v = torch.tensor([[1, 1, -1], [1, -1, -1], [-1, 1, 1]], dtype=torch.int8)
    # column sums = [1, 1, -1] -> [+1, +1, -1]
    assert binding.bsc_bundle(v).tolist() == [1, 1, -1]
    tie = torch.tensor([[1, -1], [-1, 1]], dtype=torch.int8)  # column sums [0, 0]
    assert binding.bsc_bundle(tie).tolist() == [1, 1]
    same = torch.stack([torch.tensor([1, -1, 1, -1], dtype=torch.int8)] * 5)
    assert torch.equal(binding.bsc_bundle(same), same[0])


def test_bundle_requires_2d() -> None:
    """bsc_bundle rejects non-2-D input (no silent misuse)."""
    gen = torch.Generator().manual_seed(4)
    with pytest.raises(ValueError):
        binding.bsc_bundle(_bipolar((256,), gen))
    with pytest.raises(ValueError):
        binding.bsc_bundle(_bipolar((2, 3, 4), gen))


def _rolefiller_recovery_acc(codebook: torch.Tensor, n: int, k: int,
                             n_trials: int, gen: torch.Generator) -> float:
    """Mean fraction of (key,value) bindings recovered from a BSC bundle at load k."""
    v = codebook.shape[0]
    correct = 0
    total = 0
    for _ in range(n_trials):
        keys = _bipolar((k, n), gen).to(torch.float32)
        val_idx = torch.randint(0, v, (k,), generator=gen)
        bound = binding.bsc_bind(keys, codebook[val_idx])  # (k, n)
        s = binding.bsc_bundle(bound)                       # (n,)
        for j in range(k):
            vhat = binding.bsc_unbind(s, keys[j])           # (n,)
            pred = int(torch.argmax(codebook @ vhat))
            correct += int(pred == int(val_idx[j]))
            total += 1
    return correct / total


def _k50(n: int, seed: int, v: int = 256, n_trials: int = 25) -> tuple[float, float]:
    """Estimate k_50% (bundle load at which recovery crosses 0.5) via a role-filler sweep.

    Returns (k50, acc_at_small_k). k50 is linear-interpolated at the first grid crossing of 0.5.
    """
    gen = torch.Generator().manual_seed(seed)
    codebook = _bipolar((v, n), gen).to(torch.float32)
    grid = [8, 24, 48, 72, 96, 128, 160, 200, 240]
    accs = [_rolefiller_recovery_acc(codebook, n, k, n_trials, gen) for k in grid]
    k50 = None
    for i in range(len(grid) - 1):
        a0, a1 = accs[i], accs[i + 1]
        if a0 >= 0.5 >= a1:
            t = 0.0 if a0 == a1 else (a0 - 0.5) / (a0 - a1)
            k50 = grid[i] + t * (grid[i + 1] - grid[i])
            break
    return k50, accs[0]


def test_capacity_scaling_consistent_with_law() -> None:
    """Measured k_50% roughly doubles from N=512 to N=1024 -> exponent ~ theory 1.004."""
    k50_512, acc0_512 = _k50(512, seed=10)
    k50_1024, acc0_1024 = _k50(1024, seed=11)
    # deep sub-capacity recovery is near-perfect
    assert acc0_512 > 0.98, f"N=512 acc at k=8 too low: {acc0_512:.3f}"
    assert acc0_1024 > 0.98, f"N=1024 acc at k=8 too low: {acc0_1024:.3f}"
    # a 0.5 crossing must exist in range for both N (bundle capacity is finite here)
    assert k50_512 is not None, "no 0.5 crossing found at N=512; widen the sweep grid"
    assert k50_1024 is not None, "no 0.5 crossing found at N=1024; widen the sweep grid"
    # capacity grows with N
    assert k50_1024 > k50_512, f"k50 did not grow with N: {k50_512:.1f} -> {k50_1024:.1f}"
    # exponent a where k50 ~ N^a: a = log2(k50_1024 / k50_512) (N doubles 512 -> 1024)
    exponent = math.log2(k50_1024 / k50_512)
    expected = theory.bsc_capacity_exponent()
    assert abs(exponent - expected) < 0.55, (
        f"BSC capacity exponent {exponent:.3f} (k50 {k50_512:.1f} -> {k50_1024:.1f}) "
        f"inconsistent with law N^{expected} (Week 8)"
    )
