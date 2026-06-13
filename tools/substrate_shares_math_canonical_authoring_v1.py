"""SHARES_MATH canonical authoring from Exp-Dev's 9 math groups seed.

Per Research PERIODIC_VERIFICATION_FINDINGS routing note + Exp-Dev commit ab2c2efe.
The 9 math groups in `data/substrate_index/bench_reports/shares_math_auto_discovery_candidates.json`
were structurally rediscovered by Exp-Dev with 5 signals + history-excluded; READY
for canonical authoring as SHARES_MATH edges.

Strategy:
  - Groups 2-9 (sizes 3-11): clean equivalence classes; author all intra-group pairs as
    SHARES_MATH edges. ~111 edges total.
  - Group 1 (size 72): TOO BROAD for clean equivalence class; SKIP by default; --include-mega
    flag to override (would add ~2,556 edges). Recommended: Research review and subdivide.

Authoring: SHARES_MATH RelationType added to enum at backend/substrate_index/schema.py
(this session). Edges tagged with metadata.source="exp_dev_auto_discovery_ab2c2efe".

NO LLM. NO bge. Pure graph authoring. Tolerant of missing atoms (warn + skip).
"""
from __future__ import annotations
import sys
import json
import argparse
from pathlib import Path
from itertools import combinations
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import RelationType


CANDIDATES_PATH = Path("data/substrate_index/bench_reports/shares_math_auto_discovery_candidates.json")


def normalize_qid(member: str, ps: PartitionedStore) -> str | None:
    """Resolve a bare atom-id (e.g. 'BIO/basal_ganglia') to a qualified id."""
    if "::" in member:
        return member if ps.has_atom(member) else None
    # Try each corpus prefix
    for corpus in ("math", "concept", "science", "school", "meta"):
        qid = f"{corpus}::{member}"
        if ps.has_atom(qid):
            return qid
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--candidates-path", default=str(CANDIDATES_PATH))
    ap.add_argument("--include-mega", action="store_true",
                    help="Include group 1 (size 72; too broad by default)")
    ap.add_argument("--skip-groups", nargs="*", default=[],
                    help="Group indices (1-based) to skip explicitly")
    ap.add_argument("--dry-run", action="store_true",
                    help="Print planned edges; do not write")
    args = ap.parse_args()

    cp = Path(args.candidates_path)
    if not cp.exists():
        print(f"ERROR: candidates JSON not found at {cp}")
        sys.exit(2)
    data = json.loads(cp.read_text(encoding="utf-8"))
    groups = data.get("groups", [])
    print(f"loaded {len(groups)} groups from {cp}")

    # Determine which groups to author
    skip_set = {int(x) for x in args.skip_groups}
    selected = []
    for i, g in enumerate(groups, 1):
        if i in skip_set:
            print(f"  group {i} (size {g['size']}): SKIPPED (--skip-groups)")
            continue
        if i == 1 and not args.include_mega:
            print(f"  group {i} (size {g['size']}): SKIPPED (mega-cluster; use --include-mega to override)")
            continue
        selected.append((i, g))

    print(f"\nselected {len(selected)} groups for authoring:")
    for i, g in selected:
        print(f"  group {i}: size={g['size']} signal={g['dominant_signal']}")
        print(f"    members: {g['members'][:5]}" + ("..." if len(g['members']) > 5 else ""))

    if args.dry_run:
        total_edges = sum(g["size"] * (g["size"] - 1) // 2 for _, g in selected)
        print(f"\n[DRY RUN] would author {total_edges} intra-group SHARES_MATH edges")
        return

    # Connect to substrate
    ps = PartitionedStore(Path("data/substrate_index"))
    pre_rels = sum(1 for _ in ps.iter_all_relations())
    print(f"\npre-ingest relations: {pre_rels}")

    # Build existing edge set for duplicate detection
    existing = set()
    for r in ps.iter_all_relations():
        try:
            existing.add((r.src_qualified_id, r.rel_type.name, r.tgt_qualified_id))
        except AttributeError:
            pass

    # Author SHARES_MATH edges (symmetric: both directions)
    added = 0
    skipped_miss = 0
    skipped_dup = 0
    failed = 0

    for group_idx, g in selected:
        # Resolve all members to qids
        member_qids = []
        for m in g["members"]:
            qid = normalize_qid(m, ps)
            if qid:
                member_qids.append(qid)
            else:
                print(f"  group {group_idx} miss: {m!r} not resolvable")
                skipped_miss += 1
        # Author all intra-group pairs (symmetric SHARES_MATH; emit both directions)
        for a, b in combinations(member_qids, 2):
            for src, tgt in ((a, b), (b, a)):
                key = (src, "SHARES_MATH", tgt)
                if key in existing:
                    skipped_dup += 1
                    continue
                try:
                    ps.add_relation(
                        src, RelationType.SHARES_MATH, tgt,
                        source="exp_dev_auto_discovery_ab2c2efe",
                        note=f"BATCH 26 SHARES_MATH canonical authoring; group_{group_idx} dominant={g['dominant_signal']}",
                    )
                    added += 1
                    existing.add(key)
                except Exception as e:
                    msg = str(e)[:120]
                    if any(k in msg.lower() for k in ("already", "duplicate")):
                        skipped_dup += 1
                    else:
                        print(f"  FAIL: {src} -> {tgt}: {msg}")
                        failed += 1

    post_rels = sum(1 for _ in ps.iter_all_relations())
    print(f"\n=== SHARES_MATH AUTHORING SUMMARY ===")
    print(f"groups authored: {len(selected)}")
    print(f"relations: {pre_rels} -> {post_rels} (+{post_rels - pre_rels})")
    print(f"  edges added (both directions): {added}")
    print(f"  member-resolve misses: {skipped_miss}")
    print(f"  duplicate edges skipped: {skipped_dup}")
    print(f"  failures: {failed}")
    print(f"\nDownstream unblocks (per Research):")
    print(f"  - KP P3 SHARES_MATH bisimulation cell (Exp-Dev queue-ready)")
    print(f"  - canonical CELL-AAA-3 (1.33x -> 1.4x HARD-PASS)")
    print(f"  - Pi/Sigma id-type subcommand")
    print(f"  - CHTV-2 alpha-equivalence")


if __name__ == "__main__":
    main()
