"""find-relevant-knowledge v1: Stage 1+2 of RECURSIVE self-improvement loop.

Per research_to_testbed_exp_dev_RECURSIVE_SELF_IMPROVEMENT_LOOP_Stage_1_2_*.md
(MASTER PLAN Phase 2 R2.1). Polls substrate's OWN ingested knowledge for atoms +
edges relevant to a topic. Returns ranked candidates with substrate-provenance trail.

CPU-ONLY signals (no bge / no torch / no LLM):
  S1 algebra_dict_keyword: token match in atom.algebra dict values + name + description
  S2 alias_keyword_match:  token match in atom.aliases tuple
  S3 partition_match:      token match in atom.metadata.science_algebra_category
  S4 capability_keyword:   token match in atom.serves_capability identifiers
  S5 SHARES_MATH_expansion: when seed atom found, include its SHARES_MATH equivalence
                            class neighbors (orthogonal-mechanism expansion)
  S6 DEPENDS_ON_walk:      typed-graph reachability up to --max-depth via DEPENDS_ON
                            + USES + INSTANCE_OF + SPECIALIZES + DEFINED_OVER + SHARES_MATH

Composite relevance:
  relevance(A) = 0.4 * algebra_score
               + 0.2 * alias_score
               + 0.15 * partition_score
               + 0.15 * capability_score
               + 0.1 * (shares_math_or_walk_bonus)

Output: ranked top-K JSON (with full provenance) or stdout summary.

This is the CPU-only Stage 1 deliverable. Canonical-remote integration with bge
prefilter + L6-PROOF prove() scoring is a separate ~50 LOC augmentation when
the prove subcommand is wired into substrate_query.py.

Usage:
  python tools/substrate_find_relevant_knowledge_v1.py "cosine cleanup" --top-k 10 --max-depth 2
"""
from __future__ import annotations
import sys
import json
import argparse
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import RelationType


STOP_WORDS = {
    "the", "a", "an", "is", "are", "and", "or", "to", "of", "in", "for", "on", "with",
    "by", "be", "this", "that", "these", "those", "was", "were", "as", "at", "it",
    "from", "but", "not", "have", "has", "had", "do", "does", "did", "what", "how",
    "when", "where", "why", "which", "who", "can", "could", "should", "would",
}

# Edge types to walk for typed-inference reachability
WALK_EDGE_TYPES = (
    RelationType.DEPENDS_ON, RelationType.USES, RelationType.INSTANCE_OF,
    RelationType.SPECIALIZES, RelationType.DEFINED_OVER,
)
# SHARES_MATH not in enum yet (per spec); placeholder for forward-compat


def tokenize(text: str) -> set:
    if not text:
        return set()
    toks = []
    for raw in str(text).lower().split():
        clean = "".join(c if c.isalnum() else " " for c in raw).split()
        for t in clean:
            if len(t) > 2 and t not in STOP_WORDS:
                toks.append(t)
    return set(toks)


def algebra_token_set(atom) -> set:
    """Tokenize atom.algebra dict values."""
    toks = set()
    alg = atom.algebra or {}
    for k, v in alg.items():
        if isinstance(v, str):
            toks.update(tokenize(v))
        elif isinstance(v, (list, tuple)):
            for item in v:
                toks.update(tokenize(str(item)))
    return toks


def alias_token_set(atom) -> set:
    return set().union(*(tokenize(a) for a in (atom.aliases or ()))) if atom.aliases else set()


def name_desc_token_set(atom) -> set:
    return tokenize(atom.name) | tokenize(atom.description)


def category_token_set(atom) -> set:
    cat = (atom.metadata or {}).get("science_algebra_category")
    if isinstance(cat, (list, tuple)):
        cat = " ".join(str(c) for c in cat)
    return tokenize(cat)


def capability_token_set(atom) -> set:
    toks = set()
    for cap in (atom.serves_capability or ()):
        toks.update(tokenize(cap))
    return toks


def score_atom(atom, query_tokens: set):
    """Compute relevance score + sub-scores. Higher = more relevant."""
    alg_toks = algebra_token_set(atom) | name_desc_token_set(atom)
    alias_toks = alias_token_set(atom)
    cat_toks = category_token_set(atom)
    cap_toks = capability_token_set(atom)

    qn = max(len(query_tokens), 1)

    alg_overlap = query_tokens & alg_toks
    alias_overlap = query_tokens & alias_toks
    cat_overlap = query_tokens & cat_toks
    cap_overlap = query_tokens & cap_toks

    alg_score = len(alg_overlap) / qn
    alias_score = len(alias_overlap) / qn
    cat_score = len(cat_overlap) / qn
    cap_score = len(cap_overlap) / qn

    relevance = (
        0.40 * alg_score
        + 0.20 * alias_score
        + 0.15 * cat_score
        + 0.15 * cap_score
    )
    return {
        "relevance": relevance,
        "algebra_score": alg_score,
        "alias_score": alias_score,
        "category_score": cat_score,
        "capability_score": cap_score,
        "algebra_hits": sorted(alg_overlap),
        "alias_hits": sorted(alias_overlap),
        "category_hits": sorted(cat_overlap),
        "capability_hits": sorted(cap_overlap),
    }


def walk_reachable(ps: PartitionedStore, seed_qids: set, max_depth: int) -> set:
    """BFS over typed edges (DEPENDS_ON + USES + INSTANCE_OF + SPECIALIZES + DEFINED_OVER)
    in BOTH directions; returns set of qids reachable within max_depth hops."""
    reachable = set(seed_qids)
    frontier = set(seed_qids)
    for _ in range(max_depth):
        next_frontier = set()
        for q in frontier:
            for rt in WALK_EDGE_TYPES:
                try:
                    next_frontier.update(ps.out_neighbors(q, rt) or set())
                    next_frontier.update(ps.in_neighbors(q, rt) or set())
                except Exception:
                    pass
        next_frontier -= reachable
        if not next_frontier:
            break
        reachable.update(next_frontier)
        frontier = next_frontier
    return reachable


HISTORY_PREFIXES = (
    "decision_history::", "findings_history::", "research_history::",
    "exp_dev_history::", "testbed_history::", "session_history::",
)


def is_history(qid: str) -> bool:
    return any(qid.startswith(p) for p in HISTORY_PREFIXES)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("about", help="Free-text topic to find relevant substrate knowledge about")
    ap.add_argument("--top-k", type=int, default=10)
    ap.add_argument("--max-depth", type=int, default=2,
                    help="DEPENDS_ON/USES/INSTANCE_OF/SPECIALIZES/DEFINED_OVER walk depth from seed atoms")
    ap.add_argument("--min-relevance", type=float, default=0.1,
                    help="Minimum direct relevance to count as a seed atom (pre-walk)")
    ap.add_argument("--include-history", action="store_true",
                    help="Include decision/findings/research history corpora (default: skip)")
    ap.add_argument("--json-output", type=str, default=None,
                    help="If set, write full result JSON to this path")
    args = ap.parse_args()

    query_tokens = tokenize(args.about)
    if not query_tokens:
        print(f"ERROR: no usable tokens in query '{args.about}' after stop-word filter")
        sys.exit(2)

    print(f"query: {args.about!r}")
    print(f"query tokens: {sorted(query_tokens)}")

    ps = PartitionedStore(Path("data/substrate_index"))
    all_atoms = ps.all_atoms()
    if not args.include_history:
        all_atoms = [a for a in all_atoms if not is_history(a.qualified_id)]
    print(f"atoms in scope: {len(all_atoms)}")

    # --- Stage 1: direct token-overlap scoring across all atoms ---
    direct_hits = []
    for atom in all_atoms:
        sc = score_atom(atom, query_tokens)
        if sc["relevance"] >= args.min_relevance:
            direct_hits.append((atom, sc))
    direct_hits.sort(key=lambda t: -t[1]["relevance"])
    print(f"\ndirect token-overlap hits (relevance >= {args.min_relevance}): {len(direct_hits)}")

    # --- Stage 2: typed-graph walk from top seeds ---
    seed_qids = {a.qualified_id for a, _ in direct_hits[: max(5, args.top_k)]}
    if args.max_depth > 0 and seed_qids:
        reachable = walk_reachable(ps, seed_qids, args.max_depth)
    else:
        reachable = set(seed_qids)
    if not args.include_history:
        reachable = {q for q in reachable if not is_history(q)}
    print(f"reachable (depth={args.max_depth}): {len(reachable)} atoms")

    # --- Stage 3: re-score reachable atoms, bump walk-only finds ---
    seen_qids = {a.qualified_id for a, _ in direct_hits}
    walk_only = reachable - seen_qids
    qid_to_atom = {a.qualified_id: a for a in all_atoms}
    walk_hits = []
    for q in walk_only:
        a = qid_to_atom.get(q)
        if a is None:
            continue
        sc = score_atom(a, query_tokens)
        sc["walk_only_bonus"] = 0.1
        sc["relevance"] += 0.1
        walk_hits.append((a, sc))
    walk_hits.sort(key=lambda t: -t[1]["relevance"])

    # --- Combine + dedupe ---
    combined = direct_hits + walk_hits
    combined.sort(key=lambda t: -t[1]["relevance"])

    top = combined[: args.top_k]

    print(f"\n=== TOP {len(top)} RELEVANT ATOMS for '{args.about}' ===")
    for i, (atom, sc) in enumerate(top, 1):
        tier = atom.tier.value if hasattr(atom.tier, "value") else str(atom.tier)
        hits_summary = []
        if sc["algebra_hits"]:
            hits_summary.append(f"alg={sc['algebra_hits'][:3]}")
        if sc["capability_hits"]:
            hits_summary.append(f"cap={sc['capability_hits'][:2]}")
        if sc.get("walk_only_bonus"):
            hits_summary.append("via-walk")
        print(f"  {i:2d}. {atom.qualified_id:55s} [{tier:5s}] rel={sc['relevance']:.3f}  {' '.join(hits_summary)}")

    out = {
        "about": args.about,
        "query_tokens": sorted(query_tokens),
        "atoms_in_scope": len(all_atoms),
        "direct_hits": len(direct_hits),
        "walk_reachable": len(reachable),
        "max_depth": args.max_depth,
        "min_relevance_seed": args.min_relevance,
        "top_k": [
            {
                "qid": atom.qualified_id,
                "name": atom.name,
                "tier": atom.tier.value if hasattr(atom.tier, "value") else str(atom.tier),
                "corpus": atom.corpus.value if hasattr(atom.corpus, "value") else str(atom.corpus),
                "relevance": round(sc["relevance"], 4),
                "algebra_score": round(sc["algebra_score"], 3),
                "alias_score": round(sc["alias_score"], 3),
                "category_score": round(sc["category_score"], 3),
                "capability_score": round(sc["capability_score"], 3),
                "walk_only_bonus": sc.get("walk_only_bonus", 0.0),
                "algebra_hits": sc["algebra_hits"],
                "alias_hits": sc["alias_hits"],
                "category_hits": sc["category_hits"],
                "capability_hits": sc["capability_hits"],
                "description_snippet": (atom.description or "")[:200],
            }
            for atom, sc in top
        ],
    }
    if args.json_output:
        Path(args.json_output).parent.mkdir(parents=True, exist_ok=True)
        with open(args.json_output, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2, default=str)
        print(f"\nfull JSON: {args.json_output}")


if __name__ == "__main__":
    main()
