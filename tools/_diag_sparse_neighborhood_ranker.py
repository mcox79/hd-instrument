"""Smoke test for sparse_neighborhood_ranking.py helper.

Generates 5 candidate "atom names" + ranks them. Confirms sparse-neighborhood-first
priority works.
"""
from pathlib import Path
import sys
sys.path.insert(0, '.')

import numpy as np
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.algebra_index import AlgebraIndex
from backend.substrate_index.sparse_neighborhood_ranking import rank_candidates_sparse_first


def name_vec(ai, name):
    tokens = [t.strip().lower() for t in name.split() if len(t.strip()) >= 2]
    if not tokens:
        return None
    vecs = [ai._filler_vector(t) for t in tokens]
    return ai._bundle(vecs)


ps = PartitionedStore(Path("data/substrate_index"))
ai = AlgebraIndex(dim=1024)
ai.build(ps)

candidates_text = [
    ("backpropagation chain rule gradient", "Q33 backprop missing atom (high path-to-HP value)"),
    ("convolutional neural network deep learning", "potentially in saturated cluster"),
    ("quantum entanglement bell pair", "low-density cluster?"),
    ("monte carlo tree search reinforcement learning", "RL cluster (12) is dense"),
    ("topological data analysis persistent homology", "very novel; new cluster"),
]

cands = [(label, name_vec(ai, text)) for text, label in candidates_text]

ranked = rank_candidates_sparse_first(cands, ps, ai)
print(f"{'rank':>4s} {'route':<20s} {'cluster':>7s} {'density':>7s} {'novelty':>8s} {'score':>6s}  description")
for i, r in enumerate(ranked):
    print(f"  {i+1:>2d}  {r.route:<20s} {r.nearest_cluster!s:>7s} {r.nearest_density:>7d} {r.novelty:>8.3f} {r.rank_score:>6.3f}  {r.candidate_id}")
