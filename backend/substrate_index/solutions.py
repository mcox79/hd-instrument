"""Solution-history queries on substrate concept atoms.

Per user direction 2026-06-11 late evening: each capability has a current-best
mathematical solution. When a new solution replaces it, the old DOES NOT
disappear -- it's marked obsolete. This preserves substrate's progression
history without losing prior learnings.

This module reads capability atoms' solution_history field and exposes 7
analytical queries:

1. current_best_table(pstore)              -> {capability_id: current_solution_id}
2. solution_lineage(pstore, capability_id) -> ordered list of (solution, status)
3. cross_capability_best_overlap(pstore)   -> {solution_id: [capability_ids]}
                                              -- universal levers visible
4. stale_solutions(pstore, days)            -> capabilities with current-best
                                              not challenged in N days
5. revert_history(pstore)                   -> list of REVERTED entries with
                                              capability + reason; cross-capability
                                              pattern surfacing
6. cliff_detector(pstore)                   -> biggest single-step lifts in
                                              solution history (compositional
                                              cliff moments)
7. replacement_prediction(pstore, capability_id) -> based on cross-capability
                                              patterns, what solution likely
                                              supersedes the current-best next?
"""
from __future__ import annotations

import logging
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom

logger = logging.getLogger(__name__)


# ============================================================
# Helpers
# ============================================================


def _parse_date(s: Optional[str]) -> Optional[datetime]:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        try:
            return datetime.strptime(s, "%Y-%m-%d")
        except Exception:
            return None


def _capability_atoms(pstore: PartitionedStore) -> list[Atom]:
    """Return all atoms that could have a current_best_solution (concept or
    capability)."""
    out = []
    for atom in pstore.all_atoms():
        if atom.corpus.value == "concept" or atom.kind.value == "capability":
            out.append(atom)
    return out


# ============================================================
# Query 1: current_best_table
# ============================================================


def current_best_table(pstore: PartitionedStore) -> dict[str, Optional[str]]:
    """For every capability atom, return its current-best solution.

    Returns:
        {capability_qualified_id: current_best_solution_qualified_id or None}
    """
    out = {}
    for atom in _capability_atoms(pstore):
        out[atom.qualified_id] = atom.current_best_solution
    return out


# ============================================================
# Query 2: solution_lineage
# ============================================================


@dataclass(frozen=True)
class LineageEntry:
    """One entry in a capability's solution history."""
    solution_atom_id: str
    adopted_date: Optional[str]
    replaced_date: Optional[str]
    replacement_reason: Optional[str]
    empirical_metric: Optional[dict]
    source: Optional[str]
    status: str   # "current" | "superseded" | "reverted"

    def to_dict(self) -> dict:
        return {
            "solution_atom_id": self.solution_atom_id,
            "adopted_date": self.adopted_date,
            "replaced_date": self.replaced_date,
            "replacement_reason": self.replacement_reason,
            "empirical_metric": self.empirical_metric,
            "source": self.source,
            "status": self.status,
        }


def solution_lineage(pstore: PartitionedStore, capability_qualified_id: str) -> list[LineageEntry]:
    """Full ordered solution history for a capability (oldest first)."""
    atom = pstore.get_atom(capability_qualified_id)
    if atom is None or not atom.solution_history:
        return []
    out = []
    # Order by adopted_date ascending (oldest first)
    entries = list(atom.solution_history)
    entries.sort(key=lambda e: e.get("adopted_date") or "")
    for e in entries:
        out.append(LineageEntry(
            solution_atom_id=e.get("solution_atom_id", ""),
            adopted_date=e.get("adopted_date"),
            replaced_date=e.get("replaced_date"),
            replacement_reason=e.get("replacement_reason"),
            empirical_metric=e.get("empirical_metric"),
            source=e.get("source"),
            status=e.get("status", "superseded"),
        ))
    return out


# ============================================================
# Query 3: cross_capability_best_overlap (universal levers)
# ============================================================


def cross_capability_best_overlap(pstore: PartitionedStore) -> dict[str, list[str]]:
    """Group capabilities by their current-best solution.

    A solution that's current-best for >= 3 capabilities is a UNIVERSAL LEVER.

    Returns:
        {solution_qualified_id: [capability_qualified_id, ...]} sorted by
        cluster size descending.
    """
    by_solution: dict[str, list[str]] = defaultdict(list)
    for atom in _capability_atoms(pstore):
        if atom.current_best_solution:
            by_solution[atom.current_best_solution].append(atom.qualified_id)
    # Sort by cluster size desc
    return dict(sorted(by_solution.items(), key=lambda x: -len(x[1])))


# ============================================================
# Query 4: stale_solutions
# ============================================================


@dataclass(frozen=True)
class StaleSolution:
    capability_qualified_id: str
    current_best: str
    adopted_date: Optional[str]
    days_since_adopted: Optional[int]

    def to_dict(self) -> dict:
        return {
            "capability_qualified_id": self.capability_qualified_id,
            "current_best": self.current_best,
            "adopted_date": self.adopted_date,
            "days_since_adopted": self.days_since_adopted,
        }


def stale_solutions(pstore: PartitionedStore, days_threshold: int = 30,
                    reference_date: Optional[datetime] = None) -> list[StaleSolution]:
    """Capabilities whose current-best hasn't been challenged in N days.

    Candidates for fresh adversarial probe or replacement attempt.
    """
    if reference_date is None:
        reference_date = datetime.now(timezone.utc)
    out = []
    for atom in _capability_atoms(pstore):
        if not atom.current_best_solution:
            continue
        # Find the "current" entry in solution_history
        current_entry = None
        for e in atom.solution_history:
            if e.get("status") == "current" or e.get("replaced_date") in (None, ""):
                current_entry = e
                break
        if current_entry is None:
            continue
        adopted = _parse_date(current_entry.get("adopted_date"))
        if adopted is None:
            continue
        # Make tz-aware if naive
        if adopted.tzinfo is None:
            adopted = adopted.replace(tzinfo=timezone.utc)
        days = (reference_date - adopted).days
        if days >= days_threshold:
            out.append(StaleSolution(
                capability_qualified_id=atom.qualified_id,
                current_best=atom.current_best_solution,
                adopted_date=current_entry.get("adopted_date"),
                days_since_adopted=days,
            ))
    return sorted(out, key=lambda s: -(s.days_since_adopted or 0))


# ============================================================
# Query 5: revert_history
# ============================================================


@dataclass(frozen=True)
class RevertEntry:
    capability_qualified_id: str
    reverted_solution: str
    reason: Optional[str]
    metric: Optional[dict]
    source: Optional[str]

    def to_dict(self) -> dict:
        return {
            "capability_qualified_id": self.capability_qualified_id,
            "reverted_solution": self.reverted_solution,
            "reason": self.reason,
            "metric": self.metric,
            "source": self.source,
        }


def revert_history(pstore: PartitionedStore) -> list[RevertEntry]:
    """All REVERTED entries across capabilities.

    Cross-capability patterns surface methodology rule candidates:
    when multiple capabilities revert for the same root cause (eval
    contamination, method overclaim, etc.), that's a methodology rule
    waiting to be promoted.
    """
    out = []
    for atom in _capability_atoms(pstore):
        for e in atom.solution_history:
            if e.get("status") == "reverted":
                out.append(RevertEntry(
                    capability_qualified_id=atom.qualified_id,
                    reverted_solution=e.get("solution_atom_id", ""),
                    reason=e.get("replacement_reason"),
                    metric=e.get("empirical_metric"),
                    source=e.get("source"),
                ))
    return out


# ============================================================
# Query 6: cliff_detector
# ============================================================


@dataclass(frozen=True)
class CliffEntry:
    capability_qualified_id: str
    from_solution: str
    to_solution: str
    lift: float
    metric_name: str
    source: Optional[str]
    cliff_score: float

    def to_dict(self) -> dict:
        return {
            "capability_qualified_id": self.capability_qualified_id,
            "from_solution": self.from_solution,
            "to_solution": self.to_solution,
            "lift": self.lift,
            "metric_name": self.metric_name,
            "source": self.source,
            "cliff_score": self.cliff_score,
        }


def cliff_detector(pstore: PartitionedStore, min_lift: float = 0.10) -> list[CliffEntry]:
    """Single-step replacements with > min_lift improvement.

    These are substrate's architectural breakthroughs -- v3.0 compositional
    cliff (L5 recall 0.000 -> 1.000) would surface here.
    """
    out = []
    for atom in _capability_atoms(pstore):
        if not atom.solution_history:
            continue
        # Order by adopted date ascending
        entries = list(atom.solution_history)
        entries.sort(key=lambda e: e.get("adopted_date") or "")
        for i in range(1, len(entries)):
            prev = entries[i - 1]
            curr = entries[i]
            prev_metric = prev.get("empirical_metric") or {}
            curr_metric = curr.get("empirical_metric") or {}
            prev_val = prev_metric.get("value")
            curr_val = curr_metric.get("value")
            if prev_val is None or curr_val is None:
                continue
            try:
                lift = float(curr_val) - float(prev_val)
            except Exception:
                continue
            if lift >= min_lift:
                # cliff_score = lift * (1 + I(lift > 0.5)) -- compositional cliffs
                # near-1.0 lifts get bonus
                cliff_score = lift * (1.0 + (1.0 if lift > 0.5 else 0.0))
                out.append(CliffEntry(
                    capability_qualified_id=atom.qualified_id,
                    from_solution=prev.get("solution_atom_id", ""),
                    to_solution=curr.get("solution_atom_id", ""),
                    lift=lift,
                    metric_name=curr_metric.get("name", "unknown"),
                    source=curr.get("source"),
                    cliff_score=cliff_score,
                ))
    return sorted(out, key=lambda c: -c.cliff_score)


# ============================================================
# Query 7: replacement_prediction
# ============================================================


@dataclass(frozen=True)
class ReplacementPrediction:
    capability_qualified_id: str
    current_best: str
    predicted_replacement: str
    pattern_strength: float    # fraction of past replacements that followed this pattern
    pattern_evidence: tuple[str, ...]  # other capabilities where this replacement happened

    def to_dict(self) -> dict:
        return {
            "capability_qualified_id": self.capability_qualified_id,
            "current_best": self.current_best,
            "predicted_replacement": self.predicted_replacement,
            "pattern_strength": self.pattern_strength,
            "pattern_evidence": list(self.pattern_evidence),
        }


def replacement_prediction(pstore: PartitionedStore, capability_qualified_id: str) -> Optional[ReplacementPrediction]:
    """Predict the next likely replacement for a capability's current-best.

    Logic: look across all capabilities for replacement pairs (old -> new);
    when (current_best, X) appears as a past replacement on >= 2 other
    capabilities, predict X.
    """
    atom = pstore.get_atom(capability_qualified_id)
    if atom is None or not atom.current_best_solution:
        return None
    current = atom.current_best_solution

    # Build replacement-pair counts across all capabilities
    pair_counts: Counter = Counter()
    pair_evidence: dict[tuple[str, str], list[str]] = defaultdict(list)
    for other in _capability_atoms(pstore):
        if other.qualified_id == capability_qualified_id:
            continue
        entries = list(other.solution_history)
        entries.sort(key=lambda e: e.get("adopted_date") or "")
        for i in range(1, len(entries)):
            old = entries[i - 1].get("solution_atom_id", "")
            new = entries[i].get("solution_atom_id", "")
            if old and new:
                pair_counts[(old, new)] += 1
                pair_evidence[(old, new)].append(other.qualified_id)

    # Find pairs starting with `current`
    candidates = [(new, n, pair_evidence[(current, new)])
                  for (old, new), n in pair_counts.items() if old == current]
    if not candidates:
        return None
    # Pick the new with highest count
    best = max(candidates, key=lambda c: c[1])
    new_sol, n, evidence = best
    total_with_current = sum(n for _, n, _ in candidates)
    pattern_strength = n / max(1, total_with_current)
    return ReplacementPrediction(
        capability_qualified_id=capability_qualified_id,
        current_best=current,
        predicted_replacement=new_sol,
        pattern_strength=pattern_strength,
        pattern_evidence=tuple(evidence),
    )


# ============================================================
# Query 8: methodology_rule_extraction
# Extract transferable methodology rules from cliff patterns.
# Per Findings #12 Q4: each cliff > threshold becomes a candidate rule
# "When X-current-best, try Y" if the same replacement repeats across
# 3+ capabilities.
# ============================================================


@dataclass(frozen=True)
class MethodologyRule:
    rule_text: str               # human-readable rule
    from_solution: str
    to_solution: str
    n_capabilities: int          # how many capabilities exhibited this transition
    avg_lift: float              # average lift across instances
    capabilities: tuple[str, ...]
    confidence: float            # n_capabilities / 12 (rough fraction of corpus)

    def to_dict(self) -> dict:
        return {
            "rule_text": self.rule_text,
            "from_solution": self.from_solution,
            "to_solution": self.to_solution,
            "n_capabilities": self.n_capabilities,
            "avg_lift": self.avg_lift,
            "capabilities": list(self.capabilities),
            "confidence": self.confidence,
        }


def methodology_rule_extraction(pstore: PartitionedStore,
                                min_capabilities: int = 3,
                                min_lift: float = 0.10) -> list[MethodologyRule]:
    """Extract transferable methodology rules from repeating cliff patterns.

    Logic: same (from -> to) replacement appearing across >= min_capabilities
    capabilities with avg lift >= min_lift becomes a rule.

    Output is substrate-proposed meta atoms ready for meta partition (rule 8
    us-or-substrate compliant: substrate proposes; Research validates).
    """
    # Collect transitions per replacement pair
    transitions: dict[tuple[str, str], list[tuple[str, float, str]]] = defaultdict(list)
    for atom in _capability_atoms(pstore):
        entries = list(atom.solution_history)
        entries.sort(key=lambda e: e.get("adopted_date") or "")
        for i in range(1, len(entries)):
            prev = entries[i - 1]
            curr = entries[i]
            old = prev.get("solution_atom_id", "")
            new = curr.get("solution_atom_id", "")
            if not (old and new and old != new):
                continue
            prev_m = (prev.get("empirical_metric") or {}).get("value")
            curr_m = (curr.get("empirical_metric") or {}).get("value")
            if prev_m is None or curr_m is None:
                continue
            try:
                lift = float(curr_m) - float(prev_m)
            except Exception:
                continue
            if lift < 0:
                continue  # only positive transitions
            transitions[(old, new)].append((atom.qualified_id, lift, curr.get("source", "")))

    # Total capability count for confidence denominator
    total_capabilities = len(_capability_atoms(pstore))

    rules: list[MethodologyRule] = []
    for (old, new), instances in transitions.items():
        n = len(instances)
        if n < min_capabilities:
            continue
        avg_lift = sum(l for _, l, _ in instances) / max(1, n)
        if avg_lift < min_lift:
            continue
        old_short = old.split("/")[-1] if "/" in old else old.split("::")[-1]
        new_short = new.split("/")[-1] if "/" in new else new.split("::")[-1]
        rule_text = f"When {old_short} is current-best, try {new_short} (observed +{avg_lift:.3f} avg lift across {n} capabilities)"
        rules.append(MethodologyRule(
            rule_text=rule_text,
            from_solution=old,
            to_solution=new,
            n_capabilities=n,
            avg_lift=avg_lift,
            capabilities=tuple(c for c, _, _ in instances),
            confidence=n / max(1, total_capabilities),
        ))
    return sorted(rules, key=lambda r: -(r.n_capabilities * r.avg_lift))
