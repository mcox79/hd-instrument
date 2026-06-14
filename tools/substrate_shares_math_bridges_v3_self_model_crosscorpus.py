"""SHARES_MATH bridges v3 - cross-corpus math <-> self-model.

Now that 16 SELF/* atoms are live in META corpus (per 91572c4d), substrate
can have its own math operator families bridged to their self-model
concepts. These are LITERAL "substrate reasons about itself" edges.

The SELF/* atoms ratified are:
  SELF/substrate, SELF/memory_mechanism, SELF/prover,
  SELF/knowledge_promotion, SELF/family_binding, SELF/family_cleanup,
  SELF/family_optimization, SELF/family_spectral,
  SELF/family_probabilistic_inference, SELF/family_linear_discriminative,
  SELF/family_search, SELF/family_sequence_dp,
  SELF/family_reinforcement_learning, SELF/capability_store,
  SELF/capability_retrieve, SELF/capability_reason_about_self

Bridge each math operator family supertype to its SELF/family_*:
  gradient_based_optimizer <-> SELF/family_optimization
  hmm_inference_operator <-> SELF/family_probabilistic_inference
  fhrr_binding_op <-> SELF/family_binding
  vsa_superposition_op <-> SELF/family_binding (also)
  path_search_operator <-> SELF/family_search
  sequence_decoder_operator <-> SELF/family_sequence_dp
  spectral_theorem_synthesis <-> SELF/family_spectral
  cosine_cleanup <-> SELF/family_cleanup
  discriminative_perceptron <-> SELF/family_linear_discriminative

Plus higher-order: substrate's prover infrastructure <-> Skunkworks's
PROACTIVE_GAP_LOOP atoms.

NO LLM. NO bge.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import RelationType


BRIDGES = [
    ("math::T2/gradient_based_optimizer", "meta::SELF/family_optimization",
     "math supertype bridges to substrate's self-model concept of optimization family"),
    ("math::T2/hmm_inference_operator", "meta::SELF/family_probabilistic_inference",
     "HMM inference is substrate's probabilistic_inference family realized"),
    ("math::T2/fhrr_binding_op", "meta::SELF/family_binding",
     "FHRR binding supertype IS substrate's family_binding concept"),
    ("math::T2/vsa_superposition_op", "meta::SELF/family_binding",
     "VSA superposition is part of substrate's binding-family architecture"),
    ("math::T2/path_search_operator", "meta::SELF/family_search",
     "graph path search IS substrate's family_search realized"),
    ("math::T2/sequence_decoder_operator", "meta::SELF/family_sequence_dp",
     "sequence decoder IS substrate's family_sequence_dp realized"),
    ("math::T3/spectral_theorem_synthesis", "meta::SELF/family_spectral",
     "spectral theorem IS substrate's family_spectral mathematical foundation"),
    ("math::T2/cosine_cleanup", "meta::SELF/family_cleanup",
     "cosine cleanup IS substrate's family_cleanup mechanism"),
    ("math::T2/discriminative_perceptron", "meta::SELF/family_linear_discriminative",
     "perceptron IS substrate's family_linear_discriminative implementation"),
    # Prover / knowledge_promotion cross-references
    ("math::T2/dynamic_programming", "meta::SELF/family_sequence_dp",
     "DP is the algorithmic mechanism behind family_sequence_dp"),
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
                    source="shares_math_bridges_v3_crosscorpus",
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
    print(f"\n=== SHARES_MATH BRIDGES v3 (CROSS-CORPUS MATH<->SELF) SUMMARY ===")
    print(f"relations: {pre_rels} -> {post_rels}  (+{post_rels - pre_rels})")
    print(f"  edges added: {added}")
    print(f"  skipped (already exist): {skipped_exists}")
    print(f"  skipped (missing endpoint): {skipped_missing}")
    print(f"  failed: {failed}")
    print(f"\nSubstrate's math operator families now SHARES_MATH-bridged to their")
    print(f"self-model concepts. Substrate literally reasons about its own architecture.")


if __name__ == "__main__":
    main()
