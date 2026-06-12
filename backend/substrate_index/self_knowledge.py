"""Substrate self-knowledge QA layer (FINDINGS #18 Gap 3 prototype).

Per USER question 2026-06-11 post-compaction:
    "after this massive ingestion - how will the substrate know what it has
    and how to use it?"

This module answers it. Substrate-on-substrate queries (no LLM-as-judge):

- what_do_you_know_about(topic_text)        : multi-index retrieval across all partitions
- what_serves(capability_qualified_id)      : atoms serving this capability (Gap 1 powered)
- what_have_you_not_tried(capability_qid)   : math atoms NOT serving this cap (sized by
                                              algebra-vec proximity to atoms that DO)
- universal_levers(min_caps)                : atoms serving N+ capabilities
- recent_lifts(min_metric)                  : solution_history entries above threshold
- composition_paths(src_atom_qid, tgt_qid)  : BFS over typed edges to find paths
- corpus_summary()                           : partition counts + top atoms per partition
- coverage_report(capability_qids)           : which caps have serves_capability populated

These are the primitives. An NL front-door / intent router (Gap 4) would route
plain-English questions to the right combination of these primitives.
"""
from __future__ import annotations

import logging
from collections import Counter, defaultdict, deque
from typing import Optional

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, RelationType

logger = logging.getLogger(__name__)


# ============================================================
# Query: what serves a capability
# ============================================================


def what_serves(pstore: PartitionedStore, capability_qid: str) -> list[Atom]:
    """Atoms with `capability_qid` in their serves_capability tuple.

    Powered by FINDINGS #18 Gap 1 (`serves_capability` field). Returns sorted
    by atom tier (T1 > T2 > T3 > T4) for prioritization.
    """
    out = []
    for atom in pstore.all_atoms():
        if capability_qid in atom.serves_capability:
            out.append(atom)
    # Sort by tier ordinal (more foundational first)
    tier_order = {"T1": 0, "T2": 1, "T3": 2, "T4": 3, "NA": 99}
    out.sort(key=lambda a: tier_order.get(a.tier.value, 99))
    return out


# ============================================================
# Query: what have I not tried for capability X
# ============================================================


def what_have_you_not_tried(pstore: PartitionedStore, capability_qid: str,
                             corpus: str = "math") -> list[Atom]:
    """Math/concept atoms NOT yet linked to this capability via serves_capability.

    These are candidates substrate has but hasn't applied. Useful for "what
    haven't I tried" introspection. Returns sorted by tier (foundational first).
    """
    untried = []
    for atom in pstore.all_atoms():
        if atom.corpus.value != corpus:
            continue
        if capability_qid not in atom.serves_capability:
            untried.append(atom)
    tier_order = {"T1": 0, "T2": 1, "T3": 2, "T4": 3, "NA": 99}
    untried.sort(key=lambda a: tier_order.get(a.tier.value, 99))
    return untried


# ============================================================
# Query: universal levers
# ============================================================


def universal_levers(pstore: PartitionedStore, min_caps: int = 3) -> list[tuple[Atom, int]]:
    """Atoms serving >= min_caps capabilities. Sorted by capability-count desc.

    Universal levers are the most reusable primitives. Per
    `cross_capability_best_overlap` finding: discriminative_perceptron at 92pct
    of caps surfaces here as the top lever.
    """
    out = []
    for atom in pstore.all_atoms():
        n = len(atom.serves_capability)
        if n >= min_caps:
            out.append((atom, n))
    out.sort(key=lambda t: -t[1])
    return out


# ============================================================
# Query: recent lifts
# ============================================================


def recent_lifts(pstore: PartitionedStore, min_metric: float = 0.05) -> list[dict]:
    """All solution_history entries with empirical_metric >= min_metric.

    Surfaces what's actually been working empirically across capabilities.
    Each entry includes capability + solution + metric + date for context.
    """
    out = []
    for atom in pstore.all_atoms():
        for entry in atom.solution_history:
            metric = entry.get("empirical_metric")
            if metric is None:
                continue
            try:
                m = float(metric)
            except (TypeError, ValueError):
                continue
            if m >= min_metric:
                out.append({
                    "capability": atom.qualified_id,
                    "capability_name": atom.name,
                    "solution": entry.get("solution_atom_id"),
                    "metric": m,
                    "date": entry.get("adopted_date"),
                    "reason": entry.get("replacement_reason", ""),
                    "status": entry.get("status", "current"),
                })
    out.sort(key=lambda d: -d["metric"])
    return out


# ============================================================
# Query: composition path search
# ============================================================


_COMPOSITION_EDGE_TYPES = {
    RelationType.USES,
    RelationType.COMPOSES,
    RelationType.DEPENDS_ON,
    RelationType.USES_SUBPROC,
}


def composition_paths(pstore: PartitionedStore, src_qid: str, tgt_qid: str,
                       max_depth: int = 4) -> list[list[str]]:
    """BFS over typed-edge graph from src to tgt up to max_depth.

    Returns all simple paths (no repeated atoms) up to depth. Edges considered:
    USES, COMPOSES, DEPENDS_ON, IMPLEMENTS. Direction: src -> tgt (outgoing).

    Per FINDINGS #18 Gap 2: prototype path-search; real version would weight
    edges by empirical evidence from solution_history.
    """
    if not pstore.has_atom(src_qid) or not pstore.has_atom(tgt_qid):
        return []
    paths = []
    queue = deque([(src_qid, [src_qid])])
    while queue:
        node, path = queue.popleft()
        if len(path) > max_depth:
            continue
        if node == tgt_qid and len(path) > 1:
            paths.append(path)
            continue
        for rel_type in _COMPOSITION_EDGE_TYPES:
            for tgt_atom_qid in pstore.out_neighbors(node, rel_type):
                if tgt_atom_qid not in path:
                    queue.append((tgt_atom_qid, path + [tgt_atom_qid]))
    return paths


# ============================================================
# Query: corpus summary -- "what do I have"
# ============================================================


def corpus_summary(pstore: PartitionedStore) -> dict:
    """High-level summary: counts per partition + tiers + top atoms by
    serves_capability."""
    stats = pstore.stats()
    by_tier: Counter = Counter()
    by_kind: Counter = Counter()
    for atom in pstore.all_atoms():
        by_tier[atom.tier.value] += 1
        by_kind[atom.kind.value] += 1

    top_levers = universal_levers(pstore, min_caps=1)[:10]
    return {
        "total_atoms": stats["total_atoms"],
        "total_relations": stats["total_relations"],
        "partitions": stats["partitions"],
        "by_tier": dict(by_tier),
        "by_kind": dict(by_kind),
        "top_universal_levers": [
            {"atom": a.qualified_id, "name": a.name, "serves_n": n}
            for a, n in top_levers
        ],
    }


# ============================================================
# Query: coverage report (Gap 1 health check)
# ============================================================


def coverage_report(pstore: PartitionedStore,
                     capability_qids: Optional[list[str]] = None) -> dict:
    """For each capability atom (or supplied list), report how many solvers
    are serving it via serves_capability. Identifies caps with empty coverage."""
    if capability_qids is None:
        capability_qids = [
            a.qualified_id for a in pstore.all_atoms()
            if a.current_best_solution or a.solution_history
        ]
    coverage = {}
    for cap_qid in capability_qids:
        servers = what_serves(pstore, cap_qid)
        coverage[cap_qid] = {
            "n_servers": len(servers),
            "server_qids": [a.qualified_id for a in servers[:5]],
        }
    empty = [c for c, v in coverage.items() if v["n_servers"] == 0]
    return {
        "total_caps": len(capability_qids),
        "caps_with_coverage": len(capability_qids) - len(empty),
        "caps_empty": len(empty),
        "empty_cap_qids": empty,
        "coverage_per_cap": coverage,
    }


# ============================================================
# Query: atom-level provenance (Gap 5)
# ============================================================


def which_solutions_use_atom(pstore: PartitionedStore, atom_qid: str) -> list[dict]:
    """For atom_qid, return every solution_history entry across all capabilities
    that uses it either directly (solution_atom_id) or indirectly (atoms_used).
    Answers: "where has this atom been load-bearing?"
    """
    out = []
    for cap in pstore.all_atoms():
        for entry in cap.solution_history:
            sol_id = entry.get("solution_atom_id")
            atoms_used = entry.get("atoms_used", [])
            is_solver = (sol_id == atom_qid) or (sol_id and sol_id.endswith("::" + atom_qid))
            is_building_block = atom_qid in atoms_used
            if not (is_solver or is_building_block):
                continue
            metric = entry.get("empirical_metric")
            try:
                m = float(metric) if metric is not None else None
            except (TypeError, ValueError):
                m = None
            out.append({
                "capability": cap.qualified_id,
                "capability_name": cap.name,
                "solution": sol_id,
                "role": "solver" if is_solver else "building_block",
                "metric": m,
                "date": entry.get("adopted_date"),
                "status": entry.get("status", "current"),
            })
    out.sort(key=lambda d: -(d["metric"] or -1))
    return out


def atom_contribution_log(pstore: PartitionedStore, atom_qid: str) -> dict:
    """Aggregate contribution stats for atom_qid across all solution_history entries.

    Returns total lift sum, mean, occurrences, current/superseded counts.
    """
    entries = which_solutions_use_atom(pstore, atom_qid)
    metrics = [e["metric"] for e in entries if e["metric"] is not None]
    current = sum(1 for e in entries if e["status"] == "current")
    superseded = sum(1 for e in entries if e["status"] == "superseded")
    return {
        "atom": atom_qid,
        "n_appearances": len(entries),
        "total_lift_sum": sum(metrics) if metrics else 0.0,
        "mean_lift": (sum(metrics) / len(metrics)) if metrics else 0.0,
        "max_lift": max(metrics) if metrics else 0.0,
        "current_count": current,
        "superseded_count": superseded,
        "capabilities": list({e["capability"] for e in entries}),
    }


# ============================================================
# Query: what do you know about <topic>
# ============================================================


def what_do_you_know_about(retriever, topic: str, top_k: int = 8) -> list[dict]:
    """Semantic retrieval over all partitions for a topic probe.

    Calls Retriever.semantic() (which uses bge embeddings). Returns ranked
    list with corpus + tier + scores so caller can interpret.

    This is the "what do I know" primitive. NL front-door would wrap this
    with intent classification + composition (Gap 4).
    """
    candidates = retriever.semantic(topic, top_k=top_k)
    out = []
    for c in candidates:
        atom = retriever._pstore.get_atom(c.atom_id) if hasattr(retriever, "_pstore") else None
        out.append({
            "atom": c.atom_id,
            "score": float(c.score),
            "name": atom.name if atom else None,
            "corpus": atom.corpus.value if atom else None,
            "tier": atom.tier.value if atom else None,
            "description_head": (atom.description[:200] if atom else "") if atom else "",
        })
    return out
