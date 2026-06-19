"""SHARES_MATH cross-domain bridges between newly-typed atoms (batch v1).

Per direction request default (Call X) while B' v2 holds for F1+F3.
Now that 460 math atoms carry algebra metadata + 28 composite types are
shipped + 6 abstraction families wired, several cross-domain mathematical
identities are authorable as SHARES_MATH edges (symmetric).

Each bridge encodes: same mathematical structure appears across two
distinct domains. Distinct from SHARED_ABSTRACTION (which unifies
operators with a shared SUPERTYPE output type). SHARES_MATH bridges
peer-level structural equivalence rather than parent-child specialization.

Bridges this batch:

  Information theory <-> Convex analysis:
    gibbs_inequality SHARES_MATH jensen_inequality
    (Jensen on concave log gives Gibbs)

  Information theory <-> Supervised learning:
    kl_divergence SHARES_MATH cross_entropy_loss
    (cross-entropy is KL plus self-entropy)

  Linear algebra <-> Numerical analysis:
    spectral_theorem_synthesis SHARES_MATH SVD
    (SVD generalizes spectral theorem to non-square)

  Probability <-> Signal processing:
    characteristic_function SHARES_MATH discrete_fourier_transform
    (char function is Fourier transform of probability measure)

  Calculus <-> Probability:
    chain_rule_calculus SHARES_MATH chain_rule_probability
    (same factorization structure across product rule families)

  Convex optimization <-> Nonsmooth optimization:
    gradient SHARES_MATH subgradient
    (subgradient generalizes gradient at nonsmooth points)

  Probability <-> Linear algebra:
    variance SHARES_MATH inner_product
    (variance is inner product of (X-EX) with itself)

NO LLM. NO bge. Symmetric SHARES_MATH edge additions only.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import RelationType


# (left, right, note). SHARES_MATH is symmetric -- we add both directions.
BRIDGES = [
    ("math::T1/gibbs_inequality", "math::T1/jensen_inequality",
     "Jensen on concave log gives Gibbs; same convex-analysis identity"),
    ("math::T1/kl_divergence", "math::T3/cross_entropy_loss",
     "cross_entropy_loss(y,p) = KL(y,p) + H(y); same information-theoretic structure"),
    ("math::T3/spectral_theorem_synthesis", "math::T1/SVD",
     "SVD generalizes spectral decomposition to non-square; same orthonormal-bases-from-operators structure"),
    ("math::T1/characteristic_function", "math::T3/discrete_fourier_transform",
     "characteristic function is Fourier transform of probability measure; same Fourier-domain identity"),
    ("math::T3/chain_rule_calculus", "math::T1/chain_rule_probability",
     "df(g)/dx = f'(g)g'; P(X1..n) = prod P(Xi|X<i); same factorization-chain identity"),
    ("math::T2/gradient", "math::T1/subgradient",
     "subgradient set generalizes gradient at nonsmooth points; same first-order-approximation structure"),
    ("math::T1/variance", "math::T1/inner_product",
     "Var(X) = <X-EX, X-EX>; variance is inner product over centered random variables"),
    # Bonus bridge -- VSA family operators share Fourier structure
    ("math::T2/fhrr_bind", "math::T3/discrete_fourier_transform",
     "FHRR bind is pointwise product in Fourier domain; same DFT-pointwise-product identity as convolution_theorem"),
    # Bonus -- HMM and graph algorithms share DP structure
    ("math::T3/viterbi_decoding", "math::T2/dynamic_programming",
     "Viterbi is DP over trellis; same optimal-substructure memoization identity"),
]


def main():
    ps = PartitionedStore(Path("data/substrate_index"))
    pre_rels = sum(1 for _ in ps.iter_all_relations())
    print(f"pre-ingest: {pre_rels} relations\n")

    existing = set()
    for src, rel_type, tgt in ps.iter_all_relations():
        existing.add((src, rel_type.name, tgt))

    added = 0
    skipped_exists = 0
    skipped_missing = 0
    failed = 0

    for left, right, note in BRIDGES:
        # Verify both atoms exist
        if not ps.has_atom(left):
            print(f"  SKIP_MISSING_LEFT: {left}")
            skipped_missing += 1
            continue
        if not ps.has_atom(right):
            print(f"  SKIP_MISSING_RIGHT: {right}")
            skipped_missing += 1
            continue

        # Add both directions (symmetric)
        for src, tgt in ((left, right), (right, left)):
            key = (src, "SHARES_MATH", tgt)
            if key in existing:
                skipped_exists += 1
                continue
            try:
                ps.add_relation(
                    src, RelationType.SHARES_MATH, tgt,
                    source="shares_math_bridges_v1",
                    note=note,
                )
                existing.add(key)
                added += 1
            except Exception as e:
                print(f"  EDGE_FAIL {src} -> {tgt}: {str(e)[:80]}")
                failed += 1

        print(f"  BRIDGED: {left} <-> {right}")

    post_rels = sum(1 for _ in ps.iter_all_relations())
    print(f"\n=== SHARES_MATH BRIDGES v1 SUMMARY ===")
    print(f"relations: {pre_rels} -> {post_rels}  (+{post_rels - pre_rels})")
    print(f"  edges added (symmetric pairs): {added}")
    print(f"  skipped (already exist): {skipped_exists}")
    print(f"  skipped (missing endpoint): {skipped_missing}")
    print(f"  failed: {failed}")
    print(f"\nCross-domain bridges authored: {added // 2} (each = 2 symmetric edges)")
    print(f"Domains bridged this batch: info_theory + convex + supervised + linear_algebra +")
    print(f"  numerical + probability + signal_processing + calculus + convex_opt + nonsmooth_opt")


if __name__ == "__main__":
    main()
