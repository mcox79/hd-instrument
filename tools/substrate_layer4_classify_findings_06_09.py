"""Classify substrate's prior findings (06, 09) via Layer 4 dialectic.

Findings #6 had 6 EQUIVALENT_UNDER candidates (Layer 3 archaeology).
Findings #9 had 39 atom candidates (Tier 3 generation).

Layer 4 dialectic classifies each as EXPECTED / SURPRISE / SECOND_ORDER.
"""
from __future__ import annotations

import json
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.dialectic import Finding, classify_all
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import RelationType

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s | %(message)s")
log = logging.getLogger("layer4_classify")

DATA_ROOT = Path("data/substrate_index")


def main():
    pstore = PartitionedStore(DATA_ROOT)
    log.info("corpus: %d atoms", len(pstore.all_atoms()))

    # Findings #6: 6 EQUIVALENT_UNDER candidates (Layer 3 archaeology output)
    findings_06 = [
        Finding(
            finding_id="F06_layer3_eq_01",
            cycle_type="E_unification",
            affected_atom_ids=("math::T3/hmm_emission", "math::T2_FAM/graph_traversal"),
            claim="hmm_emission and graph_traversal share algebra structure (probabilistic-DP via DAG)",
            proposed_relation=RelationType.EQUIVALENT_UNDER,
            proposed_target="math::T2_FAM/graph_traversal",
        ),
        Finding(
            finding_id="F06_layer3_eq_02",
            cycle_type="E_unification",
            affected_atom_ids=("math::T3/bayesian_inference", "math::T2_FAM/graph_traversal"),
            claim="bayesian_inference and graph_traversal share algebra",
            proposed_relation=RelationType.EQUIVALENT_UNDER,
            proposed_target="math::T2_FAM/graph_traversal",
        ),
        Finding(
            finding_id="F06_layer3_eq_03",
            cycle_type="E_unification",
            affected_atom_ids=("math::T1/shannon_entropy", "math::T3/answer_consistency_weak_labels"),
            claim="shannon_entropy and answer_consistency_weak_labels share information-theoretic structure",
            proposed_relation=RelationType.EQUIVALENT_UNDER,
            proposed_target="math::T3/answer_consistency_weak_labels",
        ),
        Finding(
            finding_id="F06_layer3_eq_04",
            cycle_type="E_unification",
            affected_atom_ids=("math::T3/em_algorithm", "math::T2_FAM/graph_traversal"),
            claim="em_algorithm and graph_traversal share algebra",
            proposed_relation=RelationType.EQUIVALENT_UNDER,
            proposed_target="math::T2_FAM/graph_traversal",
        ),
        Finding(
            finding_id="F06_layer3_eq_05",
            cycle_type="E_unification",
            affected_atom_ids=("math::T3/forward_algorithm", "math::T2_FAM/graph_traversal"),
            claim="forward_algorithm and graph_traversal share algebra",
            proposed_relation=RelationType.EQUIVALENT_UNDER,
            proposed_target="math::T2_FAM/graph_traversal",
        ),
    ]

    # Findings #9: atom candidates -- no proposed_relation since they're new-atom proposals
    findings_09 = [
        Finding(
            finding_id=f"F09_candidate_{i}",
            cycle_type="A_new_atoms",
            affected_atom_ids=(referenced_id,),
            claim=f"Math primitive {referenced_id} has no concept user; propose concept atom",
            proposed_relation=None,
            proposed_target=None,
        )
        for i, referenced_id in enumerate([
            "math::T1/convex_optimization",
            "math::T2/superposition",
            "math::T2/bundling",
            "math::T2/fhrr_bind",
            "math::T2/fhrr_unbind",
            "math::T3/viterbi_decoding",
            "math::T3/forward_algorithm",
            "math::T3/em_algorithm",
            "math::T3/bayesian_inference",
            "math::T3/hungarian_assignment",
            "math::T1/shannon_entropy",
            "math::T1/group_axioms",
        ])
    ]

    all_findings = findings_06 + findings_09
    log.info("classifying %d findings", len(all_findings))
    report = classify_all(all_findings, pstore)

    print(f"\n{'='*80}")
    print(f"Layer 4 dialectic classification on {report.total_findings} findings")
    print(f"{'='*80}\n")
    print(f"Classifications: {report.classifications}")
    print(f"Surprise rate: {report.surprise_rate:.3f}")
    print(f"Drill triggers: {len(report.drill_triggers)}")
    if report.drill_triggers:
        for t in report.drill_triggers:
            print(f"  -> {t}")
    print(f"\nPer-finding verdicts:")
    for v in report.verdicts:
        flag = " *DRILL*" if v.drill_trigger else ""
        print(f"  {v.classification:<14s}  conf={v.confidence:.2f}  {v.finding_id}{flag}")
        print(f"    -> {v.rationale}")

    out = DATA_ROOT / "bench_reports" / f"layer4_classify_{int(time.time())}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")
    log.info("wrote layer4 report -> %s", out)


if __name__ == "__main__":
    main()
