"""Structural separation: within-cat minus between-cat cosine on algebra_hrr vs composite_hrr.

Per strategy_request v588 PP-410 HP gate: structural separation @ alpha=0.5
retained at >= 75pct of plain baseline.

algebra_hrr should match Exp-Dev's "plain" baseline (0.4666 separation).
composite_hrr should retain >= 75pct of that (>= 0.350).
"""
from pathlib import Path
import sys
sys.path.insert(0, '.')

import numpy as np
from collections import defaultdict
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.algebra_index import AlgebraIndex

ps = PartitionedStore(Path("data/substrate_index"))
ai = AlgebraIndex(dim=1024)
ai.build(ps)

def separation(field_name):
    data = []
    for atom in ps.all_atoms():
        av = ai._atom_vectors.get(atom.qualified_id)
        if av is None:
            continue
        v = getattr(av, field_name)
        if v is None:
            continue
        cat = (atom.algebra or {}).get("category_int")
        if cat is None:
            continue
        data.append((v, int(cat)))

    by_cat = defaultdict(list)
    for v, c in data:
        by_cat[c].append(v)

    # Average within-cat cosine
    within_sum = within_n = 0
    for c, vecs in by_cat.items():
        if len(vecs) < 2:
            continue
        M = np.stack(vecs)
        cos = M @ M.T
        n = len(vecs)
        iu = np.triu_indices(n, k=1)
        within_sum += float(np.sum(cos[iu]))
        within_n += len(iu[0])
    within = within_sum / within_n

    # Average between-cat cosine
    between_sum = between_n = 0
    cats = list(by_cat.keys())
    for i, c1 in enumerate(cats):
        for c2 in cats[i+1:]:
            Ma = np.stack(by_cat[c1])
            Mb = np.stack(by_cat[c2])
            cos = Ma @ Mb.T
            between_sum += float(np.sum(cos))
            between_n += cos.size
    between = between_sum / between_n
    return within, between, within - between

print("FIELD          within     between    separation")
for field in ("algebra_hrr", "composite_hrr"):
    w, b, sep = separation(field)
    print(f"  {field:12s}  {w:.4f}    {b:.4f}    {sep:.4f}")

# Strategy gate
w_alg, b_alg, sep_alg = separation("algebra_hrr")
w_comp, b_comp, sep_comp = separation("composite_hrr")
pct_retained = sep_comp / sep_alg * 100
print(f"\nstructural separation pct retained @ alpha=0.5: {pct_retained:.1f}pct")
print(f"HP gate >= 75pct: {'PASS' if pct_retained >= 75 else 'FAIL'}")
print(f"MIDDLE 60-75pct: {'MIDDLE' if 60 <= pct_retained < 75 else ''}")
print(f"HARD_FAIL < 60pct: {'FAIL' if pct_retained < 60 else ''}")
