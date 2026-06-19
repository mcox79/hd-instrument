"""Authoring priority queue v1: per Research drill 2 recipe.

priority_score(A) = (downstream_fanin(A) * cross_capability_breadth(A) * is_leaf(A))
                    / authoring_cost(A)
                  * SHARES_MATH_equivalence_class_amortization_factor

Where:
  downstream_fanin(A)         = # T2/T3/SCHOOL atoms with DEPENDS_ON edge -> A (in-degree)
  cross_capability_breadth(A) = # distinct serves_capability values across in-neighbors
  is_leaf(A)                  = 1.0 if A has no outgoing DEPENDS_ON, else 0.0
                                (leaf = needs upward deps authored to reach T1 axioms)
  authoring_cost(A)           = uniform 1.0 for smoke; refine via algebra_dict length later
  SHARES_MATH_amortization    = 1.0 + 0.2 * (size of SHARES_MATH equivalence class - 1)
                                authoring 1 edge transfers to N-1 SHARES_MATH peers

Output: data/authoring_priority_queue_v1.json with top-100 ranked atoms.

This is STAGE A of Cell L6_PROOF_DEPTH_LIFT_BATCH18_SMOKE. Stage B (simulation
of edge injection + L6-PROOF FINDER re-run) requires substrate_query.py prove
subcommand which lives on canonical remote; shipping Stage A as standalone
authoring input.

NO LLM. NO bge. Pure graph metrics; runs in seconds.
"""
from __future__ import annotations
import sys
import json
import time
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import RelationType


TOP_K_OUTPUT = 100
OUT_PATH = Path("data/authoring_priority_queue_v1.json")

# Atoms to consider as candidates: leaves needing upward DEPENDS_ON authoring.
# Skip provenance history corpora.
HISTORY_PREFIXES = (
    "decision_history::", "findings_history::", "research_history::",
    "exp_dev_history::", "testbed_history::", "session_history::",
)


def is_history(qid: str) -> bool:
    return any(qid.startswith(p) for p in HISTORY_PREFIXES)


def main():
    t0 = time.time()
    ps = PartitionedStore(Path("data/substrate_index"))
    atoms = ps.all_atoms()
    n = len(atoms)
    print(f"loaded {n} atoms")

    # --- Pre-compute per-qid graph metrics ---
    qids = [a.qualified_id for a in atoms if not is_history(a.qualified_id)]
    qid_set = set(qids)
    print(f"non-history atoms: {len(qids)}")

    # DEPENDS_ON adjacency (filtered)
    deps_in = {}   # qid -> set of qids that DEPENDS_ON it (predecessors)
    deps_out = {}  # qid -> set of qids it DEPENDS_ON (successors)
    atom_by_qid = {a.qualified_id: a for a in atoms}

    for q in qids:
        try:
            raw_in = ps.in_neighbors(q, RelationType.DEPENDS_ON) or set()
            deps_in[q] = {x for x in raw_in if not is_history(x)}
        except Exception:
            deps_in[q] = set()
        try:
            raw_out = ps.out_neighbors(q, RelationType.DEPENDS_ON) or set()
            deps_out[q] = {x for x in raw_out if not is_history(x)}
        except Exception:
            deps_out[q] = set()

    t_pre = time.time() - t0
    print(f"pre-compute done in {t_pre:.1f}s")

    # --- SHARES_MATH equivalence-class index (if any edges exist) ---
    # Map qid -> equivalence class id (canonical representative)
    # Union-find over SHARES_MATH edges
    parent = {q: q for q in qids}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        rx, ry = find(x), find(y)
        if rx != ry:
            parent[rx] = ry

    shares_math_edge_count = 0
    for rel in ps.iter_all_relations():
        try:
            if rel.rel_type == RelationType.RELATES and "shares_math" in (rel.note or "").lower():
                # SHARES_MATH stored as RELATES with note
                pass
            elif rel.rel_type.name == "SHARES_MATH":
                if rel.src_qualified_id in parent and rel.tgt_qualified_id in parent:
                    union(rel.src_qualified_id, rel.tgt_qualified_id)
                    shares_math_edge_count += 1
        except (AttributeError, KeyError):
            pass

    # Build equivalence class size lookup
    class_size = defaultdict(int)
    for q in qids:
        class_size[find(q)] += 1
    print(f"SHARES_MATH edges: {shares_math_edge_count}; equivalence classes != 1: {sum(1 for k,v in class_size.items() if v > 1)}")

    # --- Score each candidate atom ---
    # Candidate = non-history atom that is referenced (has fanin) AND missing upward deps
    # (zero or low deps_out -> "leaf" needing upward authoring).
    scored = []
    for q in qids:
        fanin = deps_in[q]
        if not fanin:
            continue  # nothing depends on this atom; no proof-depth value to lifting it
        downstream_fanin = len(fanin)

        # cross_capability_breadth: # distinct serves_capability across in-neighbors
        caps = set()
        for src_q in fanin:
            src_atom = atom_by_qid.get(src_q)
            if src_atom and src_atom.serves_capability:
                caps.update(src_atom.serves_capability)
        cross_capability_breadth = len(caps)

        # is_leaf: 1.0 if atom has no outgoing DEPENDS_ON edges
        is_leaf = 1.0 if not deps_out[q] else 0.0

        # SHARES_MATH amortization
        eq_size = class_size[find(q)]
        shares_math_amort = 1.0 + 0.2 * (eq_size - 1)

        authoring_cost = 1.0

        # priority score
        # Avoid is_leaf=0 zeroing out non-leaf atoms entirely; give them 25pct weight
        # so authoring extra depth onto interior atoms still counts.
        leaf_factor = is_leaf if is_leaf > 0 else 0.25
        score = (
            downstream_fanin
            * max(cross_capability_breadth, 1)
            * leaf_factor
            / authoring_cost
            * shares_math_amort
        )

        atom = atom_by_qid[q]
        scored.append({
            "qid": q,
            "name": atom.name,
            "tier": atom.tier.value if hasattr(atom.tier, "value") else str(atom.tier),
            "corpus": atom.corpus.value if hasattr(atom.corpus, "value") else str(atom.corpus),
            "downstream_fanin": downstream_fanin,
            "cross_capability_breadth": cross_capability_breadth,
            "is_leaf": is_leaf,
            "deps_out_count": len(deps_out[q]),
            "shares_math_class_size": eq_size,
            "shares_math_amortization": round(shares_math_amort, 3),
            "priority_score": round(score, 3),
        })

    scored.sort(key=lambda x: -x["priority_score"])
    t_total = time.time() - t0

    # --- Summary stats ---
    print(f"\n=== AUTHORING PRIORITY QUEUE v1 SUMMARY ===")
    print(f"total atoms scored: {len(scored)} (atoms with at least one in-neighbor)")
    print(f"  leaves (deps_out=0): {sum(1 for s in scored if s['is_leaf'] == 1.0)}")
    print(f"  interior: {sum(1 for s in scored if s['is_leaf'] == 0.0)}")
    print(f"wall: {t_total:.1f}s")

    # Tier distribution in top-50
    tier_dist = defaultdict(int)
    for s in scored[:50]:
        tier_dist[s["tier"]] += 1
    print(f"\ntier distribution in top-50:")
    for k, v in sorted(tier_dist.items(), key=lambda kv: -kv[1]):
        print(f"  {k}: {v}")

    print(f"\ntop-15 ranked atoms:")
    for i, s in enumerate(scored[:15], 1):
        print(f"  {i:2d}. {s['qid']:55s}  score={s['priority_score']:7.2f}  fanin={s['downstream_fanin']:3d}  cap_breadth={s['cross_capability_breadth']:3d}  leaf={int(s['is_leaf'])}")

    # --- Write report ---
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    output = {
        "recipe": "priority_score(A) = (downstream_fanin * cross_capability_breadth * is_leaf_weight) / authoring_cost * SHARES_MATH_amortization",
        "leaf_weight": "1.0 for leaf (deps_out=0); 0.25 for interior",
        "shares_math_amortization": "1.0 + 0.2 * (equivalence_class_size - 1)",
        "history_filter_applied": True,
        "atom_count": n,
        "scored_count": len(scored),
        "shares_math_edges_found": shares_math_edge_count,
        "wall_time_seconds": round(t_total, 2),
        "top_k": TOP_K_OUTPUT,
        "queue": scored[:TOP_K_OUTPUT],
    }
    with OUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\nwrote top-{TOP_K_OUTPUT} priority queue to {OUT_PATH}")


if __name__ == "__main__":
    main()
