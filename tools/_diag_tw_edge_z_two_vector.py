"""Measure tw_edge_z spectral observable on algebra_hrr (structural) and
composite_hrr (identity-augmented) per strategy_request v587 RESCUE-2.

Baseline (substrate memory): tw_edge_z = -2.26 on algebra_hrr at pre-fix state.
HP gate: delta tw_edge_z <= +0.30 from baseline (i.e., remain <= -1.96).
HARD_FAIL: tw_edge_z shifts toward 0 by more than +0.30.
"""
from pathlib import Path
import sys
sys.path.insert(0, '.')

import numpy as np
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.algebra_index import AlgebraIndex
from backend.substrate_index.spectral import spectral_observability

ps = PartitionedStore(Path("data/substrate_index"))
ai = AlgebraIndex(dim=1024)
ai.build(ps)

def codebook(field):
    rows = []
    for aid, av in ai._atom_vectors.items():
        v = getattr(av, field)
        if v is not None:
            rows.append(v)
    return np.stack(rows)

print(f"\n{'field':14s} {'M':>4s} {'N':>5s} {'tw_edge_z':>10s} {'verdict':>10s}")
for field in ("algebra_hrr", "composite_hrr"):
    M = codebook(field)
    obs = spectral_observability(M.astype(np.float64))
    z = obs.tw_edge_z
    print(f"{field:14s} {obs.M:>4d} {obs.N:>5d} {z!r:>10s}")

# Strategy gate
M_alg = codebook("algebra_hrr").astype(np.float64)
M_comp = codebook("composite_hrr").astype(np.float64)
z_alg = spectral_observability(M_alg).tw_edge_z
z_comp = spectral_observability(M_comp).tw_edge_z

print(f"\nalgebra_hrr tw_edge_z: {z_alg}")
print(f"composite_hrr tw_edge_z: {z_comp}")

# Strategy baseline = -2.26 (from substrate memory)
baseline = -2.26
if z_alg is not None and z_comp is not None:
    delta = z_comp - baseline
    print(f"\nstructural baseline (memory): {baseline}")
    print(f"composite_hrr delta vs baseline: {delta:+.4f}")
    if delta <= 0.30:
        print(f"HP gate (delta <= +0.30): PASS")
    elif delta <= 0.60:
        print(f"MIDDLE: HARD_FAIL trigger if delta > +0.30")
    else:
        print(f"HARD_FAIL: delta > +0.30 = clustering shifted toward random")
