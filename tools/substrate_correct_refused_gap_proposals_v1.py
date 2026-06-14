"""Author the CORRECT direction of 2 refused gap proposals (Class A own-correction).

Per DECISION 11 ratify (commits in this batch): 2 proposals were REFUSED via
18th-rule CHTV-1 direction check because direction was inverted:

  T1/gradient -DEPENDS_ON-> T1/gradient_descent  (REFUSED; inverted)
  T2/dynamic_programming -DEPENDS_ON-> T3/bellman_equation (REFUSED; inverted)

The CORRECT directions (sound per same CHTV-1 logic):

  T1/gradient_descent -DEPENDS_ON-> T1/gradient   (gradient_descent USES gradient)
  T3/bellman_equation -DEPENDS_ON-> T2/dynamic_programming  (bellman IS specific case of DP)

These are substrate's adversarial self-correction (19th rule) in action --
substrate refused unsound edges, identified correct direction, and now
authors the sound versions. PROACTIVE_GAP_LOOP soundness preserved + gap
fully closed in correct direction.

NO LLM. NO bge.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import RelationType


# (src, dst, reason). CHTV-1 verdicts already hand-verified.
CORRECTED_EDGES = [
    ("math::T1/gradient_descent", "math::T1/gradient",
     "gradient_descent USES gradient as input each iteration; sound DEPENDS_ON direction"),
    ("math::T3/bellman_equation", "math::T2/dynamic_programming",
     "bellman_equation IS a specific case of DP applied to RL value functions; sound DEPENDS_ON direction"),
]


def main():
    ps = PartitionedStore(Path("data/substrate_index"))
    pre_rels = sum(1 for _ in ps.iter_all_relations())
    print(f"pre-ingest: {pre_rels} relations\n")

    existing = set()
    for src, rel_type, tgt in ps.iter_all_relations():
        existing.add((src, rel_type.name, tgt))

    added = 0
    skipped = 0
    failed = 0
    for src, dst, reason in CORRECTED_EDGES:
        if not ps.has_atom(src):
            print(f"  SKIP_MISSING_SRC: {src}")
            skipped += 1
            continue
        if not ps.has_atom(dst):
            print(f"  SKIP_MISSING_DST: {dst}")
            skipped += 1
            continue
        key = (src, "DEPENDS_ON", dst)
        if key in existing:
            print(f"  EXISTS: {src} -DEPENDS_ON-> {dst}")
            skipped += 1
            continue
        try:
            ps.add_relation(
                src, RelationType.DEPENDS_ON, dst,
                source="correct_refused_gap_proposals_v1",
                note=f"corrected direction of refused PROACTIVE_GAP_LOOP proposal; {reason[:80]}",
            )
            existing.add(key)
            print(f"  ADDED: {src} -DEPENDS_ON-> {dst}")
            print(f"    reason: {reason}")
            added += 1
        except Exception as e:
            print(f"  FAIL: {str(e)[:120]}")
            failed += 1

    post_rels = sum(1 for _ in ps.iter_all_relations())
    print(f"\n=== CORRECTED GAP PROPOSALS v1 SUMMARY ===")
    print(f"relations: {pre_rels} -> {post_rels}  (+{post_rels - pre_rels})")
    print(f"  added: {added}")
    print(f"  skipped (missing/exists): {skipped}")
    print(f"  failed: {failed}")
    print(f"\n19th-rule witness: substrate REFUSED unsound proposal -> IDENTIFIED")
    print(f"correct direction -> AUTHORED sound version. Self-correcting cycle complete.")


if __name__ == "__main__":
    main()
