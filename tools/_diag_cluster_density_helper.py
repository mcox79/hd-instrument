"""Quick smoke test for cluster_density.py helper (Phase-2-light pre-stage)."""
from pathlib import Path
import sys
sys.path.insert(0, '.')

import numpy as np
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.algebra_index import AlgebraIndex
from backend.substrate_index.cluster_density import (
    cluster_atom_counts,
    cluster_centroids,
    nearest_cluster_with_density,
    proposal_route,
)

ps = PartitionedStore(Path("data/substrate_index"))
ai = AlgebraIndex(dim=1024)
ai.build(ps)

print("=== cluster densities ===")
counts = cluster_atom_counts(ps)
for cid in sorted(counts.keys()):
    print(f"  cluster {cid:>3d}: {counts[cid]:>4d} atoms")

print(f"\n=== cluster centroids (structural / algebra_hrr) ===")
centroids = cluster_centroids(ps, ai, vector_mode="structural")
print(f"computed {len(centroids)} centroids (dim={list(centroids.values())[0].shape if centroids else 'N/A'})")

print(f"\n=== nearest_cluster_with_density (test with backpropagation candidate name) ===")
# Simulate a candidate vector by parsing "backpropagation" via name HRR
test_name = "backpropagation chain rule gradient deep_learning_optimization"
cand = ai._name_vec_from_text(test_name) if hasattr(ai, "_name_vec_from_text") else None
if cand is None:
    # build name_vec inline since _name_vec_from_text doesn't exist
    tokens = [t.strip().lower() for t in test_name.split() if len(t.strip()) >= 2]
    vecs = [ai._filler_vector(t) for t in tokens]
    cand = ai._bundle(vecs)

cid, density, sim = nearest_cluster_with_density(cand, ps, ai, vector_mode="structural")
print(f"  nearest cluster: {cid}")
print(f"  density: {density} atoms")
print(f"  cosine similarity to centroid: {sim:.4f}")

print(f"\n=== proposal_route decision ===")
route = proposal_route(cand, ps, ai)
for k, v in route.items():
    print(f"  {k}: {v}")
