"""Quick cleanup F1 + F3 test on the 54 collision atoms.

F1: single-atom retrieval -- for each atom A, query = algebra_hrr(A); top-1 must be A.
F3: 3-binding bundle recovery -- bundle algebra_hrr(A, B, C); decode each via cosine.
    Pass if all 3 recovered (top-3 contains the 3 source atoms).

Pre-reg HP: F1 >= 0.95 / F3 >= 0.93 on collision subset.
Baseline (pre-population): F1 = 0.8667 / F3 = 0.8296.
Dedup upper bound: 1.0 / 1.0.
"""
from pathlib import Path
import sys
sys.path.insert(0, '.')

import numpy as np
import random
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.algebra_index import AlgebraIndex

random.seed(42)
np.random.seed(42)

ps = PartitionedStore(Path("data/substrate_index"))
ai = AlgebraIndex(dim=1024)
ai.build(ps)

# Build the full algebra matrix
ids = []
vecs = []
# Use IDENTITY-augmented composite_hrr per two-vector architecture (PP-410):
# cleanup/compose/decode use composite_hrr (identity-augmented); structural
# similarity uses algebra_hrr (plain). This test measures atom-identity recovery.
for aid, av in ai._atom_vectors.items():
    if av.composite_hrr is not None:
        ids.append(aid)
        vecs.append(av.composite_hrr)
M = np.stack(vecs)
id_to_idx = {a: i for i, a in enumerate(ids)}
print(f"algebra atoms: {len(ids)}")

COLLISION_ATOMS = [
    "concept::MWP/ROLE_ARG0_agent", "concept::MWP/ROLE_ARG1_theme",
    "concept::MWP/ROLE_ARG2_recipient", "concept::MWP/ROLE_ARGM_LOC_location",
    "concept::MWP/ROLE_ARGM_TMP_time",
    "math::T1/category", "math::T1/cauchy_sequence", "math::T1/characteristic_function",
    "math::T1/concentration_inequality", "math::T1/continuity", "math::T1/convex_function",
    "math::T1/cross_entropy", "math::T1/duality_optimization", "math::T1/expectation_variance",
    "math::T1/group", "math::T1/jacobian_matrix", "math::T1/kkt_conditions",
    "math::T1/kullback_leibler_divergence", "math::T1/lagrange_multiplier",
    "math::T1/matrix", "math::T1/matrix_norms", "math::T1/measure_space",
    "math::T1/metric_space", "math::T1/module_ring", "math::T1/monoid",
    "math::T1/newton_method", "math::T1/null_space", "math::T1/pde",
    "math::T1/probability_space", "math::T1/rank_nullity_theorem", "math::T1/renyi_divergence",
    "math::T1/ring_field", "math::T1/topological_space", "math::T1/tracy_widom_distribution",
    "math::T3/backward_algorithm_atom", "math::T3/bpe_tokenization", "math::T3/cyk_parser",
    "math::T3/digital_filter_design", "math::T3/earley_parser", "math::T3/euclidean_distance",
    "math::T3/fast_fourier_transform", "math::T3/finite_state_transducer",
    "math::T3/forward_algorithm_atom", "math::T3/glove_embedding",
    "math::T3/hierarchical_clustering", "math::T3/hmm_emission", "math::T3/hmm_transition",
    "math::T3/k_means_clustering", "math::T3/lbfgs_quasi_newton", "math::T3/normal_form_NF",
    "math::T3/sentencepiece_tokenizer", "math::T3/tw_edge_z", "math::T3/wavelet_transform",
    "math::T3/word2vec_embedding",
]

collision_indices = [id_to_idx[a] for a in COLLISION_ATOMS if a in id_to_idx]
print(f"collision atoms found: {len(collision_indices)} / {len(COLLISION_ATOMS)}")

# F1 test: single-atom retrieval
f1_passes = 0
f1_fails = []
for idx in collision_indices:
    query = M[idx]
    scores = M @ query
    top1 = int(np.argmax(scores))
    if top1 == idx:
        f1_passes += 1
    else:
        f1_fails.append((ids[idx], ids[top1], float(scores[top1])))

f1 = f1_passes / len(collision_indices)
print(f"\n=== F1 (single-binding cleanup) ===")
print(f"  pass: {f1_passes}/{len(collision_indices)} = {f1:.4f}")
print(f"  HP gate: >= 0.95 -> {'PASS' if f1 >= 0.95 else 'FAIL'}")
if f1_fails:
    print(f"  failures (top 5):")
    for a, t, s in f1_fails[:5]:
        print(f"    {a} -> retrieved {t} (cos={s:.4f})")

# F3 test: 3-atom bundle recovery
def bundle_normalize(vecs):
    s = np.sum(vecs, axis=0)
    return s / (np.linalg.norm(s) + 1e-12)

f3_trials = 50
f3_passes = 0
f3_pair_passes_total = 0
random.seed(42)
for _ in range(f3_trials):
    triple = random.sample(collision_indices, 3)
    bundle = bundle_normalize([M[i] for i in triple])
    scores = M @ bundle
    # Top-3 retrieval
    top3 = set(int(i) for i in np.argsort(-scores)[:3])
    pair_passes = len(top3 & set(triple))
    f3_pair_passes_total += pair_passes
    if pair_passes == 3:
        f3_passes += 1

f3 = f3_passes / f3_trials
f3_partial = f3_pair_passes_total / (f3_trials * 3)
print(f"\n=== F3 (3-binding bundle cleanup) ===")
print(f"  full-triple pass: {f3_passes}/{f3_trials} = {f3:.4f}")
print(f"  per-atom partial: {f3_pair_passes_total}/{f3_trials * 3} = {f3_partial:.4f}")
print(f"  HP gate F3 >= 0.93 (full-triple): {'PASS' if f3 >= 0.93 else 'FAIL'}")
print(f"  HP gate F3 >= 0.93 (per-atom partial): {'PASS' if f3_partial >= 0.93 else 'FAIL'}")
