"""Author D-axis HIGH-confidence edge + Q47/Q48 plausibles per Exp-Dev's CANDIDATE_RELATIONS proposal.

Per exp_dev_to_testbed_CANDIDATE_RELATIONS_PROPOSAL_B_AND_D_AXIS_GAPS_WITH_JUSTIFICATIONS_FOR_MEDIATED_INGEST_2026-06-12.md:
- HIGH (textbook-true, ship): PP-364_pos_tagger DEPENDS_ON T3/discriminative_perceptron
- PLAUSIBLE (ship; if Research wants to reject, easy to remove):
  - Q47: PP-376_multibench_math DEPENDS_ON T1/gradient_descent
  - Q48: unified_compositional_engine DEPENDS_ON T1/category

Q17 BIO/theta_gamma_binding -> resonator_network_decoder DEFERRED pending rel-type
disambiguation (GROUNDS vs BIOLOGICAL_INSPIRATION_FOR; Research/Exp-Dev call).
Q40 SUPERSEDES DEFERRED (likely benchmark error per Exp-Dev assessment).
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import RelationType


def main():
    ps = PartitionedStore(Path("data/substrate_index"))
    print(f"pre-author: {len(ps.all_atoms())} atoms")

    edges = [
        # HIGH-confidence D-axis path-existence enabler
        ("concept::PP-364_pos_tagger", RelationType.DEPENDS_ON,
         "math::T3/discriminative_perceptron",
         "d_axis_authoring_per_exp_dev_high_conf_spec",
         "PP-364 POS tagger composes discriminative-perceptron primitive (Q16 path_exists target)"),
        # PLAUSIBLE Q47
        ("concept::PP-376_multibench_math", RelationType.DEPENDS_ON,
         "math::T1/gradient_descent",
         "d_axis_authoring_per_exp_dev_plausible_spec",
         "Q47: MWP solvers compose gradient-based optimization primitives"),
        # PLAUSIBLE Q48
        ("concept::unified_compositional_engine", RelationType.DEPENDS_ON,
         "math::T1/category",
         "d_axis_authoring_per_exp_dev_plausible_spec",
         "Q48: unified compositional engine relies on category-theoretic structure for composition laws"),
    ]

    added = 0
    skipped = 0
    failed = 0
    for src, rel, tgt, source, note in edges:
        try:
            ps.add_relation(src, rel, tgt, source=source, note=note)
            print(f"added {src} --{rel.name}--> {tgt}")
            added += 1
        except Exception as e:
            msg = str(e)[:120]
            if "already" in msg.lower() or "exists" in msg.lower() or "duplicate" in msg.lower():
                print(f"skip (exists): {src} --{rel.name}--> {tgt}")
                skipped += 1
            else:
                print(f"FAIL {src} {rel.name}: {msg}")
                failed += 1

    print(f"\npost-author: {len(ps.all_atoms())} atoms; added={added} skipped={skipped} failed={failed}")


if __name__ == "__main__":
    main()
