"""L2 rotational test per VSA position-is-meaning 5-level framework.

L1 (categorical clustering): PASSED 10/10 with ratios 22x-500M+ (memory).
L2 (rotational difference): this test.

Per Research direction (Cycle 50 Priority 1):
> for each inverse pair (A, A_inverse), the bind(A, A_inverse) operation
> should produce a CONSISTENT "inverse-relation residue" vector across
> different inverse pairs (encoding the rotational direction of the inverse).
> If substrate position-is-meaning at rotational level, residue vectors
> across inverse pairs should be SIMILAR; vs random pairs DIFFERENT.

Pre-reg HP gate (Research draft): mean cos(residue_pair_i, residue_pair_j)
for inverse pairs minus mean cos(residue_inverse, residue_random) >= 0.20 lift.

Inverse pairs in current 1742-atom state:
- math::T2/fhrr_bind <-> math::T2/fhrr_unbind
- math::T2/circular_convolution <-> math::T2/circular_correlation
- math::T3/discrete_fourier_transform <-> math::T2/inverse_fourier_transform
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

# Use composite_hrr (identity-augmented) since algebra_hrr has same-cluster
# collisions BY DESIGN -- L2 test on algebra_hrr would have inverse pair atoms
# with identical algebra_hrr at cos=1.0. Identity-mode disambiguates them.
def get_v(qid):
    av = ai._atom_vectors.get(qid)
    return av.composite_hrr if av is not None else None

# Hadamard binding (substrate-default)
def bind(a, b):
    r = a * b
    n = np.linalg.norm(r)
    return r / (n + 1e-12)

# Confirmed inverse pairs
INVERSE_PAIRS = [
    # Confirmed semantic inverses (atoms exist in 1742-atom corpus)
    ("math::T2/fhrr_bind", "math::T2/fhrr_unbind"),
    ("math::T3/forward_algorithm_atom", "math::T3/backward_algorithm_atom"),
    # Missing pairs noted: circular_convolution/correlation + DFT/IDFT + gradient_descent/ascent
    # Authoring gap; L2 test runs on 2 confirmed pairs
]

# Verify all atoms present
print("=== inverse pairs ===")
residues_inverse = []
for a, b in INVERSE_PAIRS:
    va = get_v(a)
    vb = get_v(b)
    if va is None or vb is None:
        print(f"  SKIP {a} <-> {b} (missing)")
        continue
    r = bind(va, vb)
    residues_inverse.append((a, b, r))
    print(f"  {a:55s} <-> {b}")

print(f"\nfound {len(residues_inverse)} usable inverse pairs")

# Pairwise similarity within inverse-pair residues
print("\n=== pairwise residue similarities (inverse pairs) ===")
sims_within = []
for i, (a1, b1, r1) in enumerate(residues_inverse):
    for j, (a2, b2, r2) in enumerate(residues_inverse[i+1:], i+1):
        s = float(r1 @ r2)
        sims_within.append(s)
        print(f"  {a1.split('/')[-1]:25s} x {a2.split('/')[-1]:25s}  cos={s:+.4f}")

mean_inverse_residue_sim = np.mean(sims_within) if sims_within else 0
print(f"\nmean inverse-pair residue similarity: {mean_inverse_residue_sim:+.4f}")

# Random-pair baseline residues
print("\n=== random-pair baseline (50 random non-inverse pairs) ===")
all_qids = [a.qualified_id for a in ps.all_atoms() if get_v(a.qualified_id) is not None]
inverse_set = set()
for a, b in INVERSE_PAIRS:
    inverse_set.add((a, b))
    inverse_set.add((b, a))

random.seed(42)
random_residues = []
for _ in range(50):
    a, b = random.sample(all_qids, 2)
    if (a, b) in inverse_set:
        continue
    va, vb = get_v(a), get_v(b)
    if va is None or vb is None:
        continue
    r = bind(va, vb)
    random_residues.append(r)

# Average residue similarity inverse-to-random
sims_cross = []
for _, _, r_inv in residues_inverse:
    for r_rnd in random_residues:
        sims_cross.append(float(r_inv @ r_rnd))

mean_cross = np.mean(sims_cross) if sims_cross else 0
print(f"mean inverse-residue x random-residue similarity: {mean_cross:+.4f}")

lift = mean_inverse_residue_sim - mean_cross
print(f"\n=== L2 verdict ===")
print(f"lift (inverse-cluster residue sim - inverse-vs-random sim) = {lift:+.4f}")
hp = lift >= 0.20
mid = 0.10 <= lift < 0.20
print(f"HP gate (>= +0.20): {'PASS' if hp else 'fail'}")
print(f"MIDDLE (0.10-0.20):  {'MIDDLE' if mid else ''}")
print(f"HARD_FAIL (< 0.10):  {'FAIL' if lift < 0.10 else ''}")
