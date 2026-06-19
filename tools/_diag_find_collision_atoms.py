"""Find the 32 collision atoms locally by computing pairwise cosine on algebra HRR matrix.

Per Exp-Dev's near_dup_diagnostic + Strategy's RESCUE-2 request: surface the
49 pairs at cos > 0.99 + their unique atoms (the ~32 collision atoms).
"""
from pathlib import Path
import sys
sys.path.insert(0, '.')

import numpy as np
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.algebra_index import AlgebraIndex

ps = PartitionedStore(Path("data/substrate_index"))
ai = AlgebraIndex(dim=1024)
ai.build(ps)

import sys as _sys
USE_COMPOSITE = "--composite" in _sys.argv
field = "composite_hrr" if USE_COMPOSITE else "algebra_hrr"
print(f"using field: {field}")

ids = []
vecs = []
for aid, av in ai._atom_vectors.items():
    v = getattr(av, field)
    if v is not None:
        ids.append(aid)
        vecs.append(v)

M = np.stack(vecs)
print(f"algebra atoms: {len(ids)}")

# Compute pairwise cosine
cos = M @ M.T  # all vectors are L2-normalized by AlgebraIndex.build

# Find pairs with cos > 0.99 (excluding diagonal)
pairs_99 = []
pairs_95 = []
N = len(ids)
for i in range(N):
    for j in range(i + 1, N):
        c = float(cos[i, j])
        if c > 0.99:
            pairs_99.append((c, ids[i], ids[j]))
        elif c > 0.95:
            pairs_95.append((c, ids[i], ids[j]))

pairs_99.sort(key=lambda x: -x[0])
pairs_95.sort(key=lambda x: -x[0])

print(f"\nPAIRS cos > 0.99: {len(pairs_99)}")
for c, a, b in pairs_99[:55]:
    print(f"  cos={c:.4f}  {a}  <->  {b}")

print(f"\nPAIRS 0.95 < cos <= 0.99: {len(pairs_95)} (top 20)")
for c, a, b in pairs_95[:20]:
    print(f"  cos={c:.4f}  {a}  <->  {b}")

# Unique colliding atoms
colliding_atoms = set()
for _, a, b in pairs_99:
    colliding_atoms.add(a)
    colliding_atoms.add(b)
print(f"\nUNIQUE atoms in cos>0.99 pairs: {len(colliding_atoms)}")
for q in sorted(colliding_atoms):
    print(f"  {q}")
