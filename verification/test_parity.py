"""Production hdlab outputs match the naive reference impl: bit-identical FHRR, tolerance for HRR."""

from __future__ import annotations

import torch

from hdlab import atoms as hd_atoms
from hdlab import binding as hd_binding
from hdlab import bundling as hd_bundling
from reference import fhrr, hrr


def test_fhrr_parity_atoms() -> None:
    """FHRR atom generation matches reference bit-identically given the same seed."""
    n = 1024
    gen_h = torch.Generator().manual_seed(42)
    gen_r = torch.Generator().manual_seed(42)
    a_h = hd_atoms.make_atom_fhrr(n, gen_h)
    a_r = fhrr.make_atom(n, gen_r)
    assert torch.equal(a_h, a_r)


def test_fhrr_parity_bind_unbind() -> None:
    n = 1024
    gen = torch.Generator().manual_seed(7)
    a = fhrr.make_atom(n, gen)
    b = fhrr.make_atom(n, gen)
    assert torch.equal(hd_binding.bind(a, b), fhrr.bind(a, b))
    c = fhrr.bind(a, b)
    assert torch.equal(hd_binding.unbind(c, b), fhrr.unbind(c, b))


def test_fhrr_parity_bundle() -> None:
    n = 1024
    gen = torch.Generator().manual_seed(9)
    vecs = torch.stack([fhrr.make_atom(n, gen) for _ in range(5)])
    assert torch.equal(hd_bundling.bundle(vecs), fhrr.bundle(vecs))


def test_hrr_parity_atoms() -> None:
    n = 1024
    gen_h = torch.Generator().manual_seed(42)
    gen_r = torch.Generator().manual_seed(42)
    a_h = hd_atoms.make_atom_hrr(n, gen_h)
    a_r = hrr.make_atom(n, gen_r)
    assert torch.allclose(a_h, a_r)


def test_hrr_parity_bind_unbind() -> None:
    n = 1024
    gen = torch.Generator().manual_seed(7)
    a = hrr.make_atom(n, gen)
    b = hrr.make_atom(n, gen)
    assert torch.allclose(hd_binding.bind(a, b), hrr.bind(a, b), atol=1e-5)
    c = hrr.bind(a, b)
    assert torch.allclose(hd_binding.unbind(c, b), hrr.unbind(c, b), atol=1e-5)


def test_hrr_parity_bundle() -> None:
    n = 1024
    gen = torch.Generator().manual_seed(9)
    vecs = torch.stack([hrr.make_atom(n, gen) for _ in range(5)])
    assert torch.allclose(hd_bundling.bundle(vecs), hrr.bundle(vecs), atol=1e-6)
