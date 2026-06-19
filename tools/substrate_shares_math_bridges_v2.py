"""SHARES_MATH cross-domain bridges v2 - 8 more from Research Call X list.

Continues v1 (6c6cce05; 7 bridges/14 edges). Per Research DECISION 2
(Call X GO), additional bridges from their candidate list. Each only
shipped if both endpoints exist in substrate.

Candidates from Research SYNTHESIS-2/3 + Call X confirmation:
  3. fourier_transform_signal <-> fourier_transform_probability
  4. convolution_theorem <-> circular_convolution
  5. inner_product <-> bilinear_form
  6. measure_preserving_map <-> dynamical_system
  7. hilbert_space <-> bounded_linear_operator
  8. lie_group_type <-> group_action_type
  9. dynamical_system_type <-> measure_preserving_map
  10. random_variable_type <-> measurable_function

Plus 2 bonus bridges between self-model atoms now that they're live:
  SELF/distillation_proof <-> class_a_provenance_witness (same proof structure)
  SELF/provability_witness <-> derivation_artifact (same evidence object)

NO LLM. NO bge.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import RelationType


BRIDGES = [
    # Research Call X candidates
    ("math::T3/convolution_theorem_synthesis", "math::T2/circular_convolution",
     "convolution theorem expressed for substrate's circular_convolution VSA primitive"),
    ("math::T1/inner_product", "math::T1/bilinear_form",
     "inner_product is a specific positive-definite Hermitian bilinear_form"),
    ("math::T1/measure_preserving_map", "math::T1/dynamical_system_type",
     "measure-preserving map is a measure-theoretic dynamical_system; same evolution structure"),
    ("math::T1/hilbert_space", "math::T1/bounded_linear_operator",
     "hilbert_space provides the domain on which bounded_linear_operator is defined"),
    ("math::T1/lie_group_type", "math::T1/group_action_type",
     "lie_group_type is a smooth group_action_type; same group structure plus smoothness"),
    ("math::T1/random_variable_type", "math::T1/measurable_space",
     "random_variable_type is a measurable function defined on a measurable_space"),

    # Self-model bridges (now possible since self-model atoms exist)
    ("meta::SELF/distillation_proof", "meta::SELF/class_a_provenance_witness",
     "distillation_proof is a class_a_provenance_witness for substrate atom removal"),
    ("meta::SELF/provability_witness", "meta::SELF/derivation_artifact",
     "provability_witness IS a derivation_artifact in substrate's prover terminology"),

    # Math-self-model cross-corpus bridges
    ("math::T2/gradient_based_optimizer", "meta::SELF/cross_domain_abstraction",
     "gradient_based_optimizer family is a cross_domain_abstraction instance"),
    ("math::T2/hmm_inference_operator", "meta::SELF/cross_domain_abstraction",
     "hmm_inference_operator family is a cross_domain_abstraction instance"),
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
        if not ps.has_atom(left):
            print(f"  SKIP_MISSING_LEFT: {left}")
            skipped_missing += 1
            continue
        if not ps.has_atom(right):
            print(f"  SKIP_MISSING_RIGHT: {right}")
            skipped_missing += 1
            continue

        bridged_any = False
        for src, tgt in ((left, right), (right, left)):
            key = (src, "SHARES_MATH", tgt)
            if key in existing:
                skipped_exists += 1
                continue
            try:
                ps.add_relation(
                    src, RelationType.SHARES_MATH, tgt,
                    source="shares_math_bridges_v2",
                    note=note,
                )
                existing.add(key)
                added += 1
                bridged_any = True
            except Exception as e:
                print(f"  EDGE_FAIL {src} -> {tgt}: {str(e)[:80]}")
                failed += 1

        if bridged_any:
            print(f"  BRIDGED: {left} <-> {right}")

    post_rels = sum(1 for _ in ps.iter_all_relations())
    print(f"\n=== SHARES_MATH BRIDGES v2 SUMMARY ===")
    print(f"relations: {pre_rels} -> {post_rels}  (+{post_rels - pre_rels})")
    print(f"  edges added (symmetric pairs): {added}")
    print(f"  skipped (already exist): {skipped_exists}")
    print(f"  skipped (missing endpoint): {skipped_missing}")
    print(f"  failed: {failed}")
    print(f"\nBridges authored v2: {added // 2} (each = 2 symmetric edges)")
    print(f"Plus cross-corpus math-to-self-model bridges (substrate reasons about itself).")


if __name__ == "__main__":
    main()
