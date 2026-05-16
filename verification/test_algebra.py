"""Algebraic identity tests for FHRR and HRR. Runs with tracing disabled."""

from __future__ import annotations

import torch
from hypothesis import given, settings
from hypothesis import strategies as st

from hdlab import atoms, binding


@settings(max_examples=15, deadline=None)
@given(n=st.sampled_from([512, 1024]), seed=st.integers(min_value=0, max_value=10000))
def test_fhrr_bind_unbind_inverse(n: int, seed: int) -> None:
    """unbind(bind(a, b), b) ~= a for FHRR (essentially exact: unit-magnitude atoms)."""
    gen = torch.Generator().manual_seed(seed)
    a = atoms.make_atom_fhrr(n, gen)
    b = atoms.make_atom_fhrr(n, gen)
    c = binding.bind(a, b)
    a_rec = binding.unbind(c, b)
    sim = atoms.similarity(a, a_rec)
    assert float(sim) > 0.999, f"FHRR exact-inverse sim too low: {float(sim)}"


@settings(max_examples=15, deadline=None)
@given(n=st.sampled_from([1024, 4096]), seed=st.integers(min_value=0, max_value=10000))
def test_hrr_bind_unbind_inverse(n: int, seed: int) -> None:
    """unbind(bind(a, b), b) ~= a for HRR (approximate inverse via involution)."""
    gen = torch.Generator().manual_seed(seed)
    a = atoms.make_atom_hrr(n, gen)
    b = atoms.make_atom_hrr(n, gen)
    c = binding.bind(a, b)
    a_rec = binding.unbind(c, b)
    sim = atoms.similarity(a, a_rec)
    assert float(sim) > 0.5, f"HRR inverse sim too low at N={n}: {float(sim)}"


@settings(max_examples=10, deadline=None)
@given(n=st.sampled_from([512, 1024]), seed=st.integers(min_value=0, max_value=10000))
def test_bind_commutative_fhrr(n: int, seed: int) -> None:
    """bind(a, b) == bind(b, a) for FHRR."""
    gen = torch.Generator().manual_seed(seed)
    a = atoms.make_atom_fhrr(n, gen)
    b = atoms.make_atom_fhrr(n, gen)
    assert torch.allclose(binding.bind(a, b), binding.bind(b, a))


@settings(max_examples=10, deadline=None)
@given(n=st.sampled_from([512, 1024]), seed=st.integers(min_value=0, max_value=10000))
def test_bind_commutative_hrr(n: int, seed: int) -> None:
    """bind(a, b) == bind(b, a) for HRR (within float tolerance)."""
    gen = torch.Generator().manual_seed(seed)
    a = atoms.make_atom_hrr(n, gen)
    b = atoms.make_atom_hrr(n, gen)
    assert torch.allclose(binding.bind(a, b), binding.bind(b, a), atol=1e-5)
