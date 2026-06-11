"""Graph + relational analysis over the substrate self-index.

Pure-Python graph algorithms over the indexed Store. Used by:
- discover.py (pattern mining)
- meta.py (self-reflection)
- the CLI (operator + Research analysis commands)

Algorithms:
- shortest_path()        : BFS through typed edges
- k_hop_neighbors()      : depth-bounded reachability
- degree_centrality()    : in/out degree per atom
- betweenness_centrality(): how often atom sits on shortest paths (computed
                            on the un-filtered graph)
- communities()          : connected components within a relation-type subgraph
                           (Louvain would be better but adds a dep; CC is enough
                           for the pilot)
- gap_atoms()            : atoms with no incoming/outgoing of a given type
- relation_density()     : per-relation-type edge density
- cross_corpus_links()   : math-to-concept link enumeration
"""
from __future__ import annotations

from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from typing import Optional

from backend.substrate_index.schema import Corpus, RelationType, Tier
from backend.substrate_index.store import Store


# ============================================================
# Paths
# ============================================================


def shortest_path(
    store: Store,
    src_id: str,
    tgt_id: str,
    rel_types: Optional[set[RelationType]] = None,
    max_depth: int = 6,
) -> Optional[list[str]]:
    """BFS shortest path src_id -> tgt_id using the given relation types
    (or all types if None). Returns the list of atom ids in order, or None
    if no path within max_depth.
    """
    if src_id == tgt_id:
        return [src_id]
    if not store.has_atom(src_id) or not store.has_atom(tgt_id):
        return None

    queue = deque([(src_id, [src_id])])
    visited = {src_id}
    types_to_try = rel_types if rel_types else set(RelationType)

    while queue:
        node, path = queue.popleft()
        if len(path) > max_depth:
            continue
        for rt in types_to_try:
            for nxt in store.out_neighbors(node, rt):
                if nxt in visited:
                    continue
                if nxt == tgt_id:
                    return path + [nxt]
                visited.add(nxt)
                queue.append((nxt, path + [nxt]))
    return None


def k_hop_neighbors(
    store: Store,
    src_id: str,
    k: int,
    rel_types: Optional[set[RelationType]] = None,
    direction: str = "out",
) -> dict[int, set[str]]:
    """Atoms reachable from src_id within k hops, grouped by hop distance.

    direction = "out" or "in"
    Returns {1: set(...), 2: set(...), ..., k: set(...)}
    """
    types_to_try = rel_types if rel_types else set(RelationType)
    seen = {src_id}
    by_hop: dict[int, set[str]] = {h: set() for h in range(1, k + 1)}
    frontier = {src_id}
    for hop in range(1, k + 1):
        next_frontier = set()
        for node in frontier:
            for rt in types_to_try:
                neigh = (
                    store.out_neighbors(node, rt)
                    if direction == "out"
                    else store.in_neighbors(node, rt)
                )
                for nxt in neigh:
                    if nxt not in seen:
                        seen.add(nxt)
                        next_frontier.add(nxt)
        by_hop[hop] = next_frontier
        frontier = next_frontier
        if not frontier:
            break
    return by_hop


# ============================================================
# Centrality
# ============================================================


@dataclass(frozen=True)
class DegreeReport:
    atom_id: str
    in_degree: int
    out_degree: int
    total_degree: int

    @property
    def is_load_bearing(self) -> bool:
        return self.total_degree >= 5  # heuristic threshold


def degree_centrality(
    store: Store,
    rel_types: Optional[set[RelationType]] = None,
) -> list[DegreeReport]:
    """In/out degree per atom over the given relation types (or all if None)."""
    types_to_try = rel_types if rel_types else set(RelationType)
    out_deg: dict[str, int] = defaultdict(int)
    in_deg: dict[str, int] = defaultdict(int)
    for src, rt, tgt in store.iter_relations():
        if rt not in types_to_try:
            continue
        out_deg[src] += 1
        in_deg[tgt] += 1
    all_ids = store.all_atom_ids()
    reports = [
        DegreeReport(
            atom_id=aid,
            in_degree=in_deg.get(aid, 0),
            out_degree=out_deg.get(aid, 0),
            total_degree=in_deg.get(aid, 0) + out_deg.get(aid, 0),
        )
        for aid in all_ids
    ]
    return sorted(reports, key=lambda r: -r.total_degree)


def betweenness_centrality(
    store: Store,
    rel_types: Optional[set[RelationType]] = None,
    sample_size: Optional[int] = None,
) -> dict[str, float]:
    """Approximate betweenness centrality.

    Counts how often each atom appears on shortest paths between random pairs
    (Brandes-like). Sample_size limits work for large indices; None = all pairs.
    """
    types_to_try = rel_types if rel_types else set(RelationType)
    all_ids = sorted(store.all_atom_ids())
    if sample_size is not None and sample_size < len(all_ids):
        import random
        all_ids = random.sample(all_ids, sample_size)

    counts: dict[str, float] = defaultdict(float)
    for src in all_ids:
        for tgt in all_ids:
            if src == tgt:
                continue
            path = shortest_path(store, src, tgt, types_to_try, max_depth=6)
            if path is None:
                continue
            for mid in path[1:-1]:
                counts[mid] += 1.0
    # Normalize
    n = max(1, len(all_ids))
    factor = 1.0 / max(1.0, n * (n - 1))
    return {aid: c * factor for aid, c in counts.items()}


# ============================================================
# Communities (connected components)
# ============================================================


def communities(
    store: Store,
    rel_types: Optional[set[RelationType]] = None,
) -> list[set[str]]:
    """Connected components within the subgraph induced by rel_types.

    Treats the subgraph as undirected for community membership purposes.
    """
    types_to_try = rel_types if rel_types else set(RelationType)
    adj: dict[str, set[str]] = defaultdict(set)
    for src, rt, tgt in store.iter_relations():
        if rt not in types_to_try:
            continue
        adj[src].add(tgt)
        adj[tgt].add(src)

    visited: set[str] = set()
    components: list[set[str]] = []
    for start in adj:
        if start in visited:
            continue
        comp = set()
        stack = [start]
        while stack:
            node = stack.pop()
            if node in visited:
                continue
            visited.add(node)
            comp.add(node)
            stack.extend(adj[node] - visited)
        if comp:
            components.append(comp)
    return sorted(components, key=lambda c: -len(c))


# ============================================================
# Gap detection
# ============================================================


@dataclass(frozen=True)
class GapReport:
    atom_id: str
    gap_kind: str            # "no_outgoing_<rel>" / "no_incoming_<rel>" / "no_users_cross_corpus"
    rel_type: Optional[RelationType] = None


def gap_atoms(
    store: Store,
    rel_type: RelationType,
    direction: str = "out",
    corpus_filter: Optional[Corpus] = None,
    tier_filter: Optional[Tier] = None,
) -> list[GapReport]:
    """Atoms missing edges of a given type and direction.

    Common use:
        gap_atoms(store, RelationType.HAS_USERS, direction="out", corpus_filter=Corpus.MATH)
            -> math atoms with no concept users (signal: candidate next-build primitive)
        gap_atoms(store, RelationType.USES, direction="out", corpus_filter=Corpus.CONCEPT)
            -> concepts with no documented math foundation (signal: gap in concept-math link)
    """
    gaps = []
    for atom in store.iter_atoms():
        if corpus_filter is not None and atom.corpus != corpus_filter:
            continue
        if tier_filter is not None and atom.tier != tier_filter:
            continue
        if direction == "out":
            neighbors = store.out_neighbors(atom.id, rel_type)
        else:
            neighbors = store.in_neighbors(atom.id, rel_type)
        if not neighbors:
            gaps.append(GapReport(
                atom_id=atom.id,
                gap_kind=f"no_{direction}going_{rel_type.value}",
                rel_type=rel_type,
            ))
    return gaps


# ============================================================
# Relation density
# ============================================================


def relation_density(store: Store) -> dict[str, dict]:
    """Per-relation-type edge density + atom coverage.

    Returns {rel_type_value: {n_edges, n_sources, n_targets, density}}.
    density = n_edges / (n_atoms * (n_atoms - 1))   (per type)
    """
    n_atoms = len(store.all_atom_ids())
    per_type = defaultdict(lambda: {"n_edges": 0, "sources": set(), "targets": set()})
    for src, rt, tgt in store.iter_relations():
        per_type[rt.value]["n_edges"] += 1
        per_type[rt.value]["sources"].add(src)
        per_type[rt.value]["targets"].add(tgt)

    out = {}
    for rt_value, d in per_type.items():
        denom = max(1, n_atoms * (n_atoms - 1))
        out[rt_value] = {
            "n_edges": d["n_edges"],
            "n_sources": len(d["sources"]),
            "n_targets": len(d["targets"]),
            "density": d["n_edges"] / denom,
        }
    return out


# ============================================================
# Cross-corpus links enumeration
# ============================================================


def cross_corpus_links(store: Store) -> list[tuple[str, str]]:
    """All (concept_id, math_id) pairs linked by USES relations.

    Useful for inspection. Reports the *forward* direction (concept -> math).
    """
    pairs = []
    for src, rt_str, tgt in store._all_relations:  # internal access for speed
        if rt_str != RelationType.USES.value:
            continue
        src_atom = store.get_atom(src)
        tgt_atom = store.get_atom(tgt)
        if src_atom is None or tgt_atom is None:
            continue
        if src_atom.corpus == Corpus.CONCEPT and tgt_atom.corpus == Corpus.MATH:
            pairs.append((src, tgt))
    return sorted(pairs)
