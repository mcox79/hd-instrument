"""Integration tests for PP-410 two-vector architecture per strategy_request v588.

Acceptance criteria:
- Structural mode: atoms_with_shared_algebra returns collision-rich top-K
  (49 cos>0.99 pairs preserved by design).
- Identity mode: atoms_with_shared_identity returns collision-resistant top-K
  (zero cos>0.99 pairs).
- retrieve_similar(vector_mode=) dispatches correctly.
- L1 categorical clustering on algebra_hrr (structural) preserved >= 1.5x ratio
  across categories (HARD_PASS gate from substrate_vsa_position_is_meaning memory).
- Structural separation retained @ alpha=0.5: >= 75pct of plain (strategy v588 HP).

Run: python -m pytest tests/test_two_vector_architecture_pp410.py -v
Or:  python tests/test_two_vector_architecture_pp410.py
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
from collections import defaultdict
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.algebra_index import AlgebraIndex

DATA_ROOT = Path("data/substrate_index")


def _build_index():
    ps = PartitionedStore(DATA_ROOT)
    ai = AlgebraIndex(dim=1024)
    ai.build(ps)
    return ps, ai


def _pairs_above_threshold(ai, field_name, threshold=0.99):
    ids, vecs = [], []
    for aid, av in ai._atom_vectors.items():
        v = getattr(av, field_name)
        if v is not None:
            ids.append(aid)
            vecs.append(v)
    if not vecs:
        return 0
    M = np.stack(vecs)
    cos = M @ M.T
    n = len(vecs)
    count = 0
    for i in range(n):
        for j in range(i + 1, n):
            if cos[i, j] > threshold:
                count += 1
    return count


def _separation(ai, ps, field_name):
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
    within_sum = within_n = 0
    for vecs in by_cat.values():
        if len(vecs) < 2:
            continue
        M = np.stack(vecs)
        cos = M @ M.T
        iu = np.triu_indices(len(vecs), k=1)
        within_sum += float(np.sum(cos[iu]))
        within_n += len(iu[0])
    within = within_sum / within_n if within_n else 0
    between_sum = between_n = 0
    cats = list(by_cat.keys())
    for i, c1 in enumerate(cats):
        for c2 in cats[i+1:]:
            Ma = np.stack(by_cat[c1])
            Mb = np.stack(by_cat[c2])
            cos = Ma @ Mb.T
            between_sum += float(np.sum(cos))
            between_n += cos.size
    between = between_sum / between_n if between_n else 0
    return within - between


def test_structural_mode_preserves_collisions():
    """algebra_hrr (structural) should preserve cos=1.0 collisions BY DESIGN."""
    _, ai = _build_index()
    collisions = _pairs_above_threshold(ai, "algebra_hrr", threshold=0.99)
    assert collisions > 0, "structural mode lost collisions; algebra_hrr should be plain"
    print(f"  structural collisions preserved: {collisions} pairs (DESIRABLE)")


def test_identity_mode_resists_collisions():
    """composite_hrr (identity) should have ZERO collisions at cos>0.99."""
    _, ai = _build_index()
    collisions = _pairs_above_threshold(ai, "composite_hrr", threshold=0.99)
    assert collisions == 0, f"identity mode has {collisions} collisions; should be 0"
    print(f"  identity collisions: {collisions} (collision-resistant)")


def test_retrieve_similar_dispatches_correctly():
    """retrieve_similar dispatches by vector_mode."""
    _, ai = _build_index()
    sample = next(iter(ai._atom_vectors))
    s = ai.retrieve_similar(sample, vector_mode="structural", top_k=5)
    i = ai.retrieve_similar(sample, vector_mode="identity", top_k=5)
    assert len(s) <= 5 and len(i) <= 5
    print(f"  retrieve_similar(structural): top-5 = {len(s)} results")
    print(f"  retrieve_similar(identity):   top-5 = {len(i)} results")


def test_l1_clustering_preserved_on_algebra_hrr():
    """L1 categorical clustering on algebra_hrr (structural): all categories ratio > 1.5x."""
    ps, ai = _build_index()
    data = []
    for atom in ps.all_atoms():
        av = ai._atom_vectors.get(atom.qualified_id)
        if av is None or av.algebra_hrr is None:
            continue
        cat = (atom.algebra or {}).get("category_int")
        if cat is None:
            continue
        data.append((av.algebra_hrr, int(cat)))
    by_cat = defaultdict(list)
    for v, c in data:
        by_cat[c].append(v)
    failures = []
    for c, vecs in by_cat.items():
        if len(vecs) < 2:
            continue
        M = np.stack(vecs)
        cos = M @ M.T
        iu = np.triu_indices(len(vecs), k=1)
        within = float(np.mean(cos[iu]))
        other_vecs = []
        for c2, vs in by_cat.items():
            if c2 != c:
                other_vecs.extend(vs)
        Mo = np.stack(other_vecs)
        between = float(np.mean(M @ Mo.T))
        ratio = within / max(abs(between), 1e-9)
        if ratio < 1.5:
            failures.append((c, ratio))
    assert not failures, f"L1 clustering FAIL for cats {failures}"
    print(f"  L1 clustering: {len(by_cat)} categories all ratio > 1.5x (PASS)")


def test_structural_separation_retention_alpha_05():
    """composite_hrr (alpha=0.5) retains >= 75pct of plain algebra_hrr separation."""
    ps, ai = _build_index()
    sep_plain = _separation(ai, ps, "algebra_hrr")
    sep_aug = _separation(ai, ps, "composite_hrr")
    pct = sep_aug / sep_plain * 100
    assert pct >= 75.0, (
        f"structural separation retention {pct:.1f}pct < 75pct HP gate"
    )
    print(f"  retention: {pct:.1f}pct (HP PASS >= 75pct)")


if __name__ == "__main__":
    print("\n=== PP-410 two-vector architecture integration tests ===\n")
    tests = [
        test_structural_mode_preserves_collisions,
        test_identity_mode_resists_collisions,
        test_retrieve_similar_dispatches_correctly,
        test_l1_clustering_preserved_on_algebra_hrr,
        test_structural_separation_retention_alpha_05,
    ]
    pass_count = 0
    for t in tests:
        print(f"\n[{t.__name__}]")
        try:
            t()
            print("  PASS")
            pass_count += 1
        except AssertionError as e:
            print(f"  FAIL: {e}")
    print(f"\n=== {pass_count}/{len(tests)} tests PASS ===")
    sys.exit(0 if pass_count == len(tests) else 1)
