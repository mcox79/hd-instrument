"""Substrate v1: the reference implementation.

This variant is a thin alias over SubstrateMemory (testbed/substrate_memory.py).
It changes ZERO behavior; it exists so the variants framework treats the
reference impl as a first-class registry entry rather than a hard-coded
special case. Every other variant is benchmarked against substrate_v1.

If you want to know what substrate_v1 does, read substrate_memory.py:
  - BSC codebook (random plus/minus 1, C = codebook_scale * N)
  - Outer-product Hebbian write: W += outer(value_atom, key_atom) / N
  - Softmax retrieve over codebook similarities, beta=32.0
  - Exact-subtract edit (subtract old outer, add new outer)
  - Exact-subtract delete + TCFT variance ratio reporting
"""

from __future__ import annotations

from testbed.substrate_memory import SubstrateMemory


class SubstrateV1Reference(SubstrateMemory):
    """Reference substrate. Pure alias; inherits every method unchanged."""

    name = "substrate_v1"
