"""TOOL-TOOL SHARES_MATH authoring -- 4 mathematical families per Exp-Dev AAA-3 unblock.

Per Research routing note (KP_P3_MIDDLE + AAA3_canonical_needs_TOOL_TOOL):
Exp-Dev's canonical Reservation-C test found 0/33 curated TOOLS in current SHARES_MATH
graph (Testbed authored only material-material edges via auto-discovery candidates).
Canonical AAA-3 (TOOLS:MATERIALS out-degree >=1.4x) is BLOCKED until TOOL-TOOL edges
are authored.

Exp-Dev proposed 4 families with strong mathematical equivalence semantics:
  Family 1 BINDING: 11 atoms sharing convolution/VSA binding algebra
  Family 2 METRIC: 5 atoms sharing inner-product-space geometry
  Family 3 ATTRACTOR: 6 atoms sharing cleanup/attractor dynamics
  Family 4 SPECTRAL: 4 atoms sharing spectral observability

Total ~86 intra-family pairwise edges (symmetric both directions = ~172 directed).
Composes with the existing SHARES_MATH RelationType enum (added this session).

Tolerant of missing atoms (warn + skip). Local laptop substrate may not have all atoms;
canonical-remote has them per Cycle 51 close substrate state.

NO LLM. NO bge. Pure graph authoring.
"""
from __future__ import annotations
import sys
from pathlib import Path
from itertools import combinations
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import RelationType


# Exp-Dev's 4 proposed TOOL-TOOL SHARES_MATH families.
# Family name -> list of bare atom-ids (will be resolved to qualified ids).
FAMILIES = {
    "BINDING": [
        "T2/fhrr_bind",
        "T2/fhrr_unbind",
        "T2/circular_convolution",
        "T2/ghrr_noncommutative_bind",
        "T3/permutation_indexed_binding",
        "T2/role_filler_binding",
        "T2_FAM/algebraic_binding",
        "T2/context_binding",
        "T2/superposition",
        "T2/bundling",
        "T2/superposition_aggregation",
    ],
    "METRIC": [
        "T1/cosine_similarity",
        "T1/inner_product",
        "T1/metric_space",
        "T2/cosine_cleanup",
        "T1/vector_space",
    ],
    "ATTRACTOR": [
        "hopfield_family",
        "T2/modern_hopfield_ramsauer",
        "T2/cleanup",
        "T2/cleanup_retrieval",
        "T3/resonator_network_decoder",
        "T2_FAM/unbinders",
    ],
    "SPECTRAL": [
        "T2/spectral_gap",
        "T1/tracy_widom_distribution",
        "T3/kappa_4_free",
        "T3/mp_bulk_kl",
    ],
}


def resolve_qid(member: str, ps: PartitionedStore) -> str | None:
    if "::" in member:
        return member if ps.has_atom(member) else None
    for corpus in ("math", "concept", "science", "school", "meta"):
        qid = f"{corpus}::{member}"
        if ps.has_atom(qid):
            return qid
    return None


def main():
    ps = PartitionedStore(Path("data/substrate_index"))
    pre_rels = sum(1 for _ in ps.iter_all_relations())
    print(f"pre-ingest relations: {pre_rels}\n")

    # Build existing edge set
    existing = set()
    for r in ps.iter_all_relations():
        try:
            existing.add((r.src_qualified_id, r.rel_type.name, r.tgt_qualified_id))
        except AttributeError:
            pass

    total_added = 0
    total_miss = 0
    total_dup = 0
    total_fail = 0
    per_family_report = {}

    for fam_name, members in FAMILIES.items():
        print(f"=== Family {fam_name} ({len(members)} atoms) ===")
        resolved = []
        for m in members:
            qid = resolve_qid(m, ps)
            if qid:
                resolved.append(qid)
            else:
                print(f"  MISS: {m!r} not found")
                total_miss += 1
        print(f"  resolved {len(resolved)}/{len(members)}")

        added = 0
        dup = 0
        fail = 0
        for a, b in combinations(resolved, 2):
            for src, tgt in ((a, b), (b, a)):
                key = (src, "SHARES_MATH", tgt)
                if key in existing:
                    dup += 1
                    continue
                try:
                    ps.add_relation(
                        src, RelationType.SHARES_MATH, tgt,
                        source=f"shares_math_tool_tool_family_{fam_name.lower()}",
                        note=f"AAA-3 unblock; TOOL-TOOL {fam_name} family per Exp-Dev proposal + Research routing",
                    )
                    added += 1
                    existing.add(key)
                except Exception as e:
                    msg = str(e)[:120]
                    if any(k in msg.lower() for k in ("already", "duplicate")):
                        dup += 1
                    else:
                        print(f"  FAIL: {src} -> {tgt}: {msg}")
                        fail += 1

        per_family_report[fam_name] = {
            "resolved_count": len(resolved),
            "pairs_added_directed": added,
            "pairs_skipped_dup": dup,
            "pairs_failed": fail,
        }
        total_added += added
        total_dup += dup
        total_fail += fail
        print(f"  edges added (directed): {added}; dup skipped: {dup}; failed: {fail}\n")

    post_rels = sum(1 for _ in ps.iter_all_relations())
    print(f"=== TOOL-TOOL SHARES_MATH SUMMARY ===")
    print(f"relations: {pre_rels} -> {post_rels} (+{post_rels - pre_rels})")
    print(f"  total edges added (both directions): {total_added}")
    print(f"  total miss (atoms not found): {total_miss}")
    print(f"  total duplicate skipped: {total_dup}")
    print(f"  total failed: {total_fail}")
    print(f"\nPer-family breakdown:")
    for fam, r in per_family_report.items():
        n = r["resolved_count"]
        expected_pairs = n * (n - 1)  # both directions
        print(f"  {fam}: resolved={n} expected_pairs_directed={expected_pairs} added={r['pairs_added_directed']}")
    print(f"\nUnblocks: canonical AAA-3 (TOOLS:MATERIALS out-degree >=1.4x HARD-PASS test)")


if __name__ == "__main__":
    main()
