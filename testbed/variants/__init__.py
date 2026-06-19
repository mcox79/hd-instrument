"""Substrate variants package.

A variant is a small subclass of SubstrateMemory that overrides one or two
operations (store / retrieve / edit / delete / __init__) to test a specific
hypothesis. The reference implementation is testbed/substrate_memory.py;
variants do NOT modify it. All variants implement the full MemoryBackend ABC
through inheritance and can be driven by the same harness / scenarios.

VARIANT_REGISTRY maps short name -> class. The harness build_backend factory
reads this registry to instantiate variants by name. To add a variant, drop
a new module under testbed/variants/ exporting a SubstrateMemory subclass
and append it to VARIANT_REGISTRY.

Naming convention:
    substrate_v1                  - reference impl (alias: substrate)
    substrate_v2_softdelete       - soft anti-Hebbian iterative erase
    substrate_v3_kerdock          - kerdock-structured codebook
    substrate_v4_double_hebbian   - dual outer-product writes
"""

from __future__ import annotations

from testbed.variants.v1_reference import SubstrateV1Reference
from testbed.variants.v2_softdelete import SubstrateV2Softdelete
from testbed.variants.v3_kerdock import SubstrateV3Kerdock
from testbed.variants.v4_double_hebbian import SubstrateV4DoubleHebbian
from testbed.variants.sharded_substrate import ShardedSubstrate
from testbed.variants.factorized_substrate import FactorizedSubstrate
from testbed.variants.hierarchical_substrate import HierarchicalSubstrate
from testbed.variants.cached_substrate import CachedSubstrate

VARIANT_REGISTRY: dict[str, type] = {
    "substrate_v1": SubstrateV1Reference,
    "substrate_v2_softdelete": SubstrateV2Softdelete,
    "substrate_v3_kerdock": SubstrateV3Kerdock,
    "substrate_v4_double_hebbian": SubstrateV4DoubleHebbian,
    "substrate_sharded": ShardedSubstrate,
    "substrate_factorized": FactorizedSubstrate,
    "substrate_hierarchical": HierarchicalSubstrate,
    "substrate_cached": CachedSubstrate,
}

__all__ = [
    "VARIANT_REGISTRY",
    "SubstrateV1Reference",
    "SubstrateV2Softdelete",
    "SubstrateV3Kerdock",
    "SubstrateV4DoubleHebbian",
    "ShardedSubstrate",
    "FactorizedSubstrate",
    "HierarchicalSubstrate",
    "CachedSubstrate",
]
