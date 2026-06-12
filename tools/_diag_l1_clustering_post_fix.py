"""L1 categorical clustering test on post-fix algebra_hrr.

Per [[substrate-vsa-position-is-meaning-validated-2026-06-12]] memory:
L1 PASSED 10/10 with ratios 22x-500M+ at pre-fix state. Verify that
signature+complexity bundling into algebra_hrr (RESCUE-2) preserves
structural clustering.

Reports within-category vs between-category cosine ratio per algebra_category
(category_int). HP gate: ratio > 1.5 across most categories.
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

# Collect (qid, vec, category) for all atoms with algebra
data = []
for atom in ps.all_atoms():
    av = ai._atom_vectors.get(atom.qualified_id)
    if av is None or av.algebra_hrr is None:
        continue
    cat = (atom.algebra or {}).get("category_int")
    if cat is None:
        continue
    data.append((atom.qualified_id, av.algebra_hrr, int(cat)))

print(f"atoms with algebra+category: {len(data)}")

from collections import defaultdict
by_cat = defaultdict(list)
for qid, v, c in data:
    by_cat[c].append(v)

# Compute within-category and between-category cosine
def mean_within_cat(vecs):
    if len(vecs) < 2:
        return None
    M = np.stack(vecs)
    cos = M @ M.T
    n = len(vecs)
    iu = np.triu_indices(n, k=1)
    return float(np.mean(cos[iu]))

def mean_between(cat_vecs_a, cat_vecs_b):
    Ma = np.stack(cat_vecs_a); Mb = np.stack(cat_vecs_b)
    return float(np.mean(Ma @ Mb.T))

cats = sorted(by_cat.keys())
print(f"\nCategories: {cats}\n")
print(f"{'cat':>4} {'n':>4} {'within':>8} {'between':>8} {'ratio':>10} {'verdict':>8}")
passes = 0
total_with_pairs = 0
for c in cats:
    vecs = by_cat[c]
    w = mean_within_cat(vecs)
    if w is None:
        print(f"  {c:>3} {len(vecs):>4}  <2 atoms, skip")
        continue
    # Between = avg across all OTHER cats
    other_vecs = []
    for c2 in cats:
        if c2 != c:
            other_vecs.extend(by_cat[c2])
    if not other_vecs:
        continue
    b = mean_between(vecs, other_vecs)
    ratio = w / max(abs(b), 1e-9)
    verdict = "PASS" if ratio > 1.5 else "fail"
    if ratio > 1.5:
        passes += 1
    total_with_pairs += 1
    print(f"  {c:>3} {len(vecs):>4}  {w:8.4f}  {b:8.4f}  {ratio:10.2f}x  {verdict:>8}")

print(f"\nL1 verdict: {passes}/{total_with_pairs} categories PASS (>1.5x ratio)")
