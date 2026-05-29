# Substrate variants

This directory holds substrate variants registered with the testbed harness.
A variant is a small subclass of `SubstrateMemory` (the v1 reference impl in
`testbed/substrate_memory.py`) that overrides one or two operations to test a
specific hypothesis. The rest of the `MemoryBackend` ABC surface is inherited.

The harness instantiates variants by name through `VARIANT_REGISTRY`
(`testbed/variants/__init__.py`) and runs them through the same scenarios as
the reference, so any variant can be benchmarked end-to-end with:

    python -m testbed smoke --backend substrate_v1
    python -m testbed run --scenario all --backend substrate_v2_softdelete --config testbed/configs/smoke.yaml

## Variants pattern

Each variant follows a tight discipline:

1. Inherit from `SubstrateMemory`.
2. Set `name = "substrate_vN_<short_label>"`.
3. Override ONLY the methods that implement the hypothesis.
4. Inherit everything else (persistence, audit, `__len__`, `supports_killer_features`).
5. Register in `VARIANT_REGISTRY`.

This keeps each variant readable as a delta against v1. If a variant ends up
overriding more than three methods you should ask whether it really belongs
as a sibling impl rather than a subclass.

## Registered variants

| name | override surface | hypothesis tested |
| --- | --- | --- |
| `substrate_v1` | none | reference; v1 alias used as baseline |
| `substrate_v2_softdelete` | `delete` | iterative soft anti-Hebbian erase (alpha=0.5, 3 steps) lowers TCFT var_ratio at some cost to structural-erase noise |
| `substrate_v3_kerdock` | `__init__` | Kerdock 4-coset codebook isolation improves KF-2 max_isolation and TCFT var_ratio versus BSC; degrades to BSC at odd log2(N) |
| `substrate_v4_double_hebbian` | `store`, `edit`, `delete` | dual cyclic-shifted outer-product writes raise SNR for point recall above capacity, at the cost of KF-1 isolation and codebook utilisation |

## Adding a variant

1. Copy `v4_double_hebbian.py` to `v5_<yourname>.py`.
2. Rename the class and set `name = "substrate_v5_<yourname>"`.
3. Replace the overridden methods with your hypothesis. Delete every
   method you do not need to override; inheritance picks them up.
4. Register the class in `VARIANT_REGISTRY` inside `__init__.py`.
5. Smoke-test locally:

       python -m testbed smoke --backend substrate_v5_yourname

   then run the standard scenario suite:

       python -m testbed run --scenario all --backend substrate_v5_yourname --config testbed/configs/smoke.yaml

6. If the variant has structural prerequisites (e.g. Kerdock needs even
   log2(N)) implement them as a soft fallback with a stderr warning so
   smoke tests do not crash.

## What variants are NOT for

- Changing the `MemoryBackend` ABC surface. If you need new methods on the
  ABC the change belongs in `testbed/api.py` with a corresponding default
  implementation on `MemoryBackend`.
- Hyperparameter sweeps over an unchanged mechanism. Sweep `beta`,
  `codebook_scale`, `seed`, etc. through config files instead.
- Multi-variant compositions. If you want to test
  v2_softdelete + v3_kerdock, write a `v6_kerdock_softdelete` subclass
  that explicitly composes both overrides.
