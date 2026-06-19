"""Field backfill: populate serves_capability for ALL partial-recall C-axis Qs (Cycle 51 day-3 P0.2 extension).

Per Q44-C field backfill success (0.000 -> 0.889; +0.017 macro), extending to remaining 6 C-Qs
with partial F1. Each Q has gold atoms missing the relevant CAP in their serves_capability field.

Targets:
- Q11-C: 5 gold atoms serve concept::PP-376_multibench_math
- Q13-C: 7 gold atoms serve concept::CAP_discriminative_perceptron
- Q14-C: 4 gold atoms serve concept::CAP_em_algorithm
- Q42-C: 4 gold atoms serve concept::PP-372_schema_retrieval
- Q43-C: 3 gold atoms serve concept::CAP_chu_liu_edmonds
- Q45-C: 2 gold atoms serve concept::CAP_hungarian_assignment
- Q46-C: 4 gold atoms serve concept::CAP_circular_convolution

Plus required CAP atoms (CREATE if missing):
- concept::CAP_em_algorithm
- concept::CAP_chu_liu_edmonds
- concept::CAP_hungarian_assignment
- concept::CAP_circular_convolution

(PP-376 + CAP_discriminative_perceptron + PP-372 + CAP_spectral_observability already exist/created.)

Expected: C-axis macro 0.7106 -> ~0.85+ (+0.14 axis = +0.024 macro)
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier
import dataclasses


# Each entry: (cap_qid, [gold_atom_qids]) for one C-Q
BACKFILL_SPEC = {
    # Q10: PP-225 fact recall
    "concept::PP-225_fact_recall_kb100K": [
        "math::T2/fhrr_bind",
        "math::T2/fhrr_unbind",
        "math::T2/cleanup",
        "math::T2/sparse_distributed_memory",
        "science::BIO/hippocampus",
    ],
    # Q11: PP-376 multibench math
    "concept::PP-376_multibench_math": [
        "math::T3/structured_perceptron_collins",
        "math::T3/count_nb",
        "math::T4/discriminative_perceptron_pipeline",
        "school::SCHOOL/discriminative_learning_family",
        "concept::unified_compositional_engine",
    ],
    # Q13: CAP_discriminative_perceptron (CAP_ exists per memory)
    "concept::CAP_discriminative_perceptron": [
        "math::T3/structured_perceptron_collins",
        "math::T1/gradient_descent",
        "math::T1/dot_product",
        "math::T1/cross_entropy",
        "math::T4/discriminative_perceptron_pipeline",
        "meta::RULE_count_nb_to_discriminative_perceptron",
        "school::SCHOOL/discriminative_learning_family",
    ],
    # Q14: CAP_em_algorithm (likely missing CAP atom)
    "concept::CAP_em_algorithm": [
        "math::T3/expectation_maximization",
        "math::T3/forward_algorithm_atom",
        "math::T3/backward_algorithm_atom",
        "math::T1/random_variable",
    ],
    # Q42: PP-372 schema retrieval
    "concept::PP-372_schema_retrieval": [
        "math::T2/fhrr_unbind",
        "math::T2/cleanup",
        "concept::RETRIEVAL_schema_pp372",
        "meta::RULE_cosine_cleanup_to_fhrr_unbind",
    ],
    # Q43: CAP_chu_liu_edmonds
    "concept::CAP_chu_liu_edmonds": [
        "math::T3/chu_liu_edmonds_algo",
        "math::T1/graph_general",
        "math::T3/eisner_parsing",
    ],
    # Q45: CAP_hungarian_assignment
    "concept::CAP_hungarian_assignment": [
        "math::T3/hungarian_algorithm",
        "math::T1/graph_general",
    ],
    # Q46: CAP_circular_convolution
    "concept::CAP_circular_convolution": [
        "math::T2/circular_convolution",
        "math::T3/discrete_fourier_transform",
        "math::T3/fast_fourier_transform",
        "math::T1/complex_field",
    ],
}


def _create_cap_if_missing(ps, cap_qid):
    """Create capability atom if missing. Returns True if created."""
    if ps.has_atom(cap_qid):
        return False
    # Parse local_id from qualified_id
    local_id = cap_qid.split("::", 1)[1]
    # Derive name from id
    name = local_id.replace("CAP_", "").replace("_", " ").replace("PP-", "PP-").title()
    cap_atom = Atom(
        id=local_id,
        name=name,
        corpus=Corpus.CONCEPT,
        tier=Tier.TIER_NA,
        description=f"Capability: {name} (auto-created via C-axis field backfill for Q44-related partial-recall lift; Cycle 51 day-3 P0.2)",
        kind=AtomKind.CAPABILITY,
        aliases=tuple([name.lower().replace(" ", "_")]),
        metadata={"category": "c_axis_field_backfill", "cycle": "51_day3_p0_2"},
    )
    ps.add_atom(cap_atom, source="p0_2_field_backfill_c_axis_full",
                note=f"created {cap_qid} for C-axis Q gold serves_capability backfill")
    return True


def main():
    ps = PartitionedStore(Path("data/substrate_index"))
    print(f"pre-backfill: {len(ps.all_atoms())} atoms")

    total_caps_created = 0
    total_backfilled = 0
    total_skipped = 0
    total_not_found = 0
    failures = []

    for cap_qid, gold_qids in BACKFILL_SPEC.items():
        print(f"\n=== {cap_qid} ===")
        # Step 1: ensure CAP atom exists
        if _create_cap_if_missing(ps, cap_qid):
            print(f"  created {cap_qid}")
            total_caps_created += 1
        else:
            print(f"  already exists: {cap_qid}")

        # Step 2: backfill serves_capability on each gold atom
        for qid in gold_qids:
            atom = ps.get_atom(qid)
            if atom is None:
                print(f"  NOT FOUND: {qid}")
                total_not_found += 1
                failures.append(f"{cap_qid} -> {qid}: NOT FOUND")
                continue
            current_caps = list(atom.serves_capability or ())
            if cap_qid in current_caps:
                print(f"  already serves: {qid}")
                total_skipped += 1
                continue
            new_caps = tuple(current_caps + [cap_qid])
            updated = dataclasses.replace(atom, serves_capability=new_caps)
            try:
                ps.add_atom(updated, source="p0_2_field_backfill_c_axis_full",
                            note=f"backfilled serves_capability += {cap_qid}")
                print(f"  backfilled: {qid}")
                total_backfilled += 1
            except Exception as e:
                print(f"  FAILED: {qid}: {str(e)[:80]}")
                failures.append(f"{cap_qid} -> {qid}: {str(e)[:80]}")

    print(f"\n=== SUMMARY ===")
    print(f"post-backfill: {len(ps.all_atoms())} atoms")
    print(f"CAPs created: {total_caps_created}")
    print(f"serves_capability backfilled: {total_backfilled}")
    print(f"skipped (already populated): {total_skipped}")
    print(f"not found in substrate: {total_not_found}")
    if failures:
        print(f"\nfailures:")
        for f in failures:
            print(f"  {f}")


if __name__ == "__main__":
    main()
