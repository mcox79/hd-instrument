"""Ground 36 typed operators that still don't backward-chain to axiom.

Direct graph audit found 157/193 typed operators terminate; 36 don't.
This batch adds DEPENDS_ON edges to T1 foundations or T2 family supertypes
so the prover can backward-chain to axiom for these too.

Target axiom-termination metric: 193/193 = 100pct (substrate fully grounded).

NO LLM. NO bge. Schema authoring only.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import RelationType


# (operator, target). All targets must terminate at axiom (verified before ship).
GROUNDINGS = [
    # VSA / coding
    ("math::T2/hamming_distance", "math::T1/sequence"),  # bit sequences
    # Combinatorial optimization algorithms -> discrete_optimization
    ("math::T3/hungarian_assignment", "math::T1/discrete_optimization"),
    ("math::T3/hungarian_algorithm", "math::T1/discrete_optimization"),
    ("math::T3/jonker_volgenant", "math::T1/discrete_optimization"),
    ("math::T3/chu_liu_edmonds", "math::T1/discrete_optimization"),
    ("math::T3/chu_liu_edmonds_algo", "math::T1/discrete_optimization"),
    ("math::T3/prims_mst", "math::T1/discrete_optimization"),
    # Weak supervision
    ("math::T3/answer_consistency_weak_labels", "math::T1/probability_distribution"),
    ("math::T2_FAM/weak_supervision", "math::T1/probability_distribution"),
    # Learning rules
    ("math::T2/bcm_learning_rule", "math::T2/parameter_vector"),
    ("math::T2/complementary_learning_systems", "math::T1/probability_distribution"),
    ("math::T3/isotonic_regression", "math::T1/probability_distribution"),
    # Dimensionality reduction
    ("math::T3/principal_component_analysis", "math::T1/eigendecomposition"),
    # Neural net components
    ("math::T3/positional_encoding", "math::T1/sequence"),
    ("math::T3/dropout_regularization", "math::T2/parameter_vector"),
    ("math::T3/lstm_cell", "math::T2/parameter_vector"),
    ("math::T3/transformer_block", "math::T2/parameter_vector"),
    # Clustering
    ("math::T3/k_means_clustering", "math::T1/discrete_optimization"),
    ("math::T3/hierarchical_clustering", "math::T1/discrete_optimization"),
    # Tokenization
    ("math::T3/bpe_tokenization", "math::T1/sequence"),
    ("math::T3/sentencepiece_tokenizer", "math::T1/sequence"),
    # Hashing
    ("math::T3/locality_sensitive_hashing", "math::T1/vector"),
    ("math::T3/random_projection", "math::T1/vector"),
    ("math::T3/feature_hashing", "math::T1/vector"),
    # Numerical methods
    ("math::T3/runge_kutta", "math::T1/derivative"),
    ("math::T3/lbfgs_quasi_newton", "math::T1/derivative"),
    ("math::T3/wavelet_transform", "math::T2/parameter_vector"),
    ("math::T3/digital_filter_design", "math::T2/parameter_vector"),
    # Kernel methods
    ("math::T3/kernel_method", "math::T1/inner_product"),
    # Parsing / language
    ("math::T3/normal_form_NF", "math::T1/sequence"),
    ("math::T3/earley_parser", "math::T1/sequence"),
    ("math::T3/finite_state_transducer", "math::T1/sequence"),
    # IP lemmas (close their dependency chain)
    ("math::T3/inner_product_positive_semidefinite_lemma", "math::T1/inner_product"),
    ("math::T3/cauchy_schwarz_synthesis", "math::T1/inner_product"),
    ("math::T3/pythagoras_inner_product_synthesis", "math::T1/inner_product"),
    # Sequence decoding alias
    ("math::T2/viterbi_decoding", "math::T2/sequence_decoder_operator"),
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

    for src, tgt in GROUNDINGS:
        if not ps.has_atom(src):
            print(f"  SKIP_MISSING_SRC: {src}")
            skipped_missing += 1
            continue
        if not ps.has_atom(tgt):
            print(f"  SKIP_MISSING_TGT: {tgt}")
            skipped_missing += 1
            continue
        key = (src, "DEPENDS_ON", tgt)
        if key in existing:
            skipped_exists += 1
            continue
        try:
            ps.add_relation(
                src, RelationType.DEPENDS_ON, tgt,
                source="ground_36_ungrounded_operators_v1",
                note="close axiom-termination chain for previously-ungrounded typed operator",
            )
            existing.add(key)
            added += 1
        except Exception as e:
            print(f"  FAIL: {src} -> {tgt} :: {str(e)[:80]}")
            failed += 1

    post_rels = sum(1 for _ in ps.iter_all_relations())
    print(f"\n=== GROUND 36 OPERATORS v1 SUMMARY ===")
    print(f"relations: {pre_rels} -> {post_rels}  (+{post_rels - pre_rels})")
    print(f"  added: {added}")
    print(f"  skipped exists: {skipped_exists}")
    print(f"  skipped missing: {skipped_missing}")
    print(f"  failed: {failed}")


if __name__ == "__main__":
    main()
