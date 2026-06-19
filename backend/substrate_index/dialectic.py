"""Layer 4 empirical-theoretical dialectic.

Per Research DEEP_SELF_EVALUATION_PROGRAM_ENDORSED priority 4:
classify each substrate-internal finding as
- EXPECTED: aligns with existing substrate structure / theoretical prior
- SURPRISE: contradicts existing structure (triggers drill per drill-defeatism rule)
- SECOND_ORDER: extends substrate into unstructured space (no contradiction
  but no prior either)

Drives the surprise-rate measurement for Tier 1 -> Tier 2 gate sustaining.
Surprises trigger Research drills; expected findings ratify the structure;
second-order findings get watch flags for potential structural extension.

Implementation: substrate's OWN existing relations form the "theoretical
prior." A finding's classification depends on whether its claim aligns with
what existing relations say.
"""
from __future__ import annotations

import logging
from collections import Counter
from dataclasses import dataclass, field
from typing import Optional

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import RelationType

logger = logging.getLogger(__name__)


# Map cycle type -> typical RelationType the finding implies
_TYPE_TO_RELATION = {
    "B_encoding": None,        # encoding-limit findings don't map to a relation type
    "E_unification": RelationType.EQUIVALENT_UNDER,
    "D_corpus_structure": None,
    "A_new_atoms": None,
    "C_architectures": None,
}


@dataclass(frozen=True)
class Finding:
    """One substrate-internal finding awaiting Layer 4 classification."""
    finding_id: str            # e.g., "FINDINGS_06_layer3_equiv_candidate_0"
    cycle_type: str            # one of A / B / C / D / E from taxonomy
    affected_atom_ids: tuple[str, ...]
    claim: str                 # short text claim
    proposed_relation: Optional[RelationType] = None
    proposed_target: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "finding_id": self.finding_id,
            "cycle_type": self.cycle_type,
            "affected_atom_ids": list(self.affected_atom_ids),
            "claim": self.claim,
            "proposed_relation": self.proposed_relation.value if self.proposed_relation else None,
            "proposed_target": self.proposed_target,
        }


@dataclass(frozen=True)
class DialecticVerdict:
    finding_id: str
    classification: str        # EXPECTED / SURPRISE / SECOND_ORDER
    confidence: float
    rationale: str
    drill_trigger: bool        # SURPRISE => True per drill-defeatism rule

    def to_dict(self) -> dict:
        return {
            "finding_id": self.finding_id,
            "classification": self.classification,
            "confidence": self.confidence,
            "rationale": self.rationale,
            "drill_trigger": self.drill_trigger,
        }


def classify_finding(finding: Finding, pstore: PartitionedStore) -> DialecticVerdict:
    """Classify one finding by inspecting substrate's existing relations.

    Logic:
    - If proposed_relation exists between same atoms in store -> EXPECTED
      (substrate already knows this; finding confirms)
    - If a CONTRADICTING relation exists -> SURPRISE
      (finding contradicts substrate; drill-defeatism rule fires)
    - If no relation between the atoms -> SECOND_ORDER
      (substrate has no prior; finding extends structure)

    Contradicting relations:
    - VALIDATES vs REFUTES
    - SPECIALIZES vs (atoms are siblings; SPECIALIZES is hierarchical)
    - DUAL vs same-as
    - EQUIVALENT_UNDER vs DUAL (subtle; both can hold)
    """
    if not finding.affected_atom_ids or finding.proposed_relation is None:
        return DialecticVerdict(
            finding_id=finding.finding_id,
            classification="SECOND_ORDER",
            confidence=0.3,
            rationale="No claim relation specified; defaulting to second-order (extending unstructured space)",
            drill_trigger=False,
        )

    proposed = finding.proposed_relation
    src = finding.affected_atom_ids[0]
    if not pstore.has_atom(src):
        return DialecticVerdict(
            finding_id=finding.finding_id,
            classification="SECOND_ORDER",
            confidence=0.3,
            rationale=f"Source atom {src} not in store; finding may propose new atom",
            drill_trigger=False,
        )

    if finding.proposed_target is None:
        return DialecticVerdict(
            finding_id=finding.finding_id,
            classification="SECOND_ORDER",
            confidence=0.4,
            rationale="No target atom proposed",
            drill_trigger=False,
        )

    tgt = finding.proposed_target
    existing_neighbors = pstore.out_neighbors(src, proposed)
    if tgt in existing_neighbors:
        return DialecticVerdict(
            finding_id=finding.finding_id,
            classification="EXPECTED",
            confidence=0.9,
            rationale=f"Substrate already has {proposed.value}({src}, {tgt})",
            drill_trigger=False,
        )

    # Check contradicting relations
    contradictions = []
    if proposed == RelationType.VALIDATES:
        contradictions = [RelationType.REFUTES]
    elif proposed == RelationType.REFUTES:
        contradictions = [RelationType.VALIDATES]
    for contra in contradictions:
        if tgt in pstore.out_neighbors(src, contra):
            return DialecticVerdict(
                finding_id=finding.finding_id,
                classification="SURPRISE",
                confidence=0.85,
                rationale=f"Substrate has {contra.value}({src}, {tgt}); finding proposes {proposed.value} (contradiction)",
                drill_trigger=True,
            )

    # Check any relation exists at all between the pair
    any_relation = False
    for rt in RelationType:
        if tgt in pstore.out_neighbors(src, rt):
            any_relation = True
            break

    if any_relation:
        return DialecticVerdict(
            finding_id=finding.finding_id,
            classification="EXPECTED",
            confidence=0.5,
            rationale=f"Substrate has some relation between {src} and {tgt}; proposed {proposed.value} consistent",
            drill_trigger=False,
        )

    return DialecticVerdict(
        finding_id=finding.finding_id,
        classification="SECOND_ORDER",
        confidence=0.6,
        rationale=f"No prior relation between {src} and {tgt}; finding extends substrate",
        drill_trigger=False,
    )


@dataclass(frozen=True)
class DialecticReport:
    total_findings: int
    classifications: dict      # {EXPECTED: N, SURPRISE: N, SECOND_ORDER: N}
    drill_triggers: tuple[str, ...]   # finding_ids that triggered drills
    verdicts: tuple[DialecticVerdict, ...]
    surprise_rate: float

    def to_dict(self) -> dict:
        return {
            "total_findings": self.total_findings,
            "classifications": dict(self.classifications),
            "drill_triggers": list(self.drill_triggers),
            "verdicts": [v.to_dict() for v in self.verdicts],
            "surprise_rate": self.surprise_rate,
        }


def classify_all(findings: list[Finding], pstore: PartitionedStore) -> DialecticReport:
    verdicts = [classify_finding(f, pstore) for f in findings]
    classifications: Counter = Counter(v.classification for v in verdicts)
    drill_triggers = tuple(v.finding_id for v in verdicts if v.drill_trigger)
    n = len(verdicts)
    surprise_rate = classifications.get("SURPRISE", 0) / max(1, n)
    return DialecticReport(
        total_findings=n,
        classifications=dict(classifications),
        drill_triggers=drill_triggers,
        verdicts=tuple(verdicts),
        surprise_rate=surprise_rate,
    )
