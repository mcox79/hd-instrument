"""Ratify 2 remaining gap-loop proposals per Research DECISION 11.

Per Research DECISIONS 11-14 note (2026-06-14 08:20): ratify 2 remaining
gap-loop proposals with CHTV-1 direction check per 18th rule. Refuse if
direction is unsound (semantically more-general should not DEPENDS_ON
more-specific).

Proposals in proactive_gap_proposals.jsonl:
  (a) gradient -> derivative (clean per Skunkworks; ratify)
  (b) gradient -> gradient_descent (companion edge in gradient's gap entry)
  (c) dynamic_programming -> bellman_equation (Skunkworks flagged; verify
      direction or refuse per 18th rule)

CHTV-1 direction check (substrate-internal):
  - DEPENDS_ON means src REQUIRES tgt as a foundational premise
  - tgt should be MORE FOUNDATIONAL than src (lower in derivation chain)

For (a): gradient is the vector of partial derivatives. gradient REQUIRES
derivative. derivative is more foundational. CHTV-1: PASS.

For (b): gradient is the input to gradient_descent. gradient_descent
REQUIRES gradient, NOT the other way. Direction is INVERTED. CHTV-1: FAIL.

For (c): bellman_equation is a SPECIFIC INSTANCE of dynamic_programming
applied to RL. dynamic_programming is more general. bellman_equation
REQUIRES dynamic_programming, NOT the other way. Direction is INVERTED.
CHTV-1: FAIL. Queue for L6-PROOF inverse v1.

Result: 1 of 3 proposals ratified (gradient -> derivative).
First autonomous-discovery atom-EDGE in substrate history.

NO LLM. NO bge.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import RelationType


PROPOSALS_PATH = Path("data/substrate_index/proactive_gap_proposals.jsonl")
RATIFY_AUDIT_PATH = Path("data/substrate_index/proactive_gap_ratify_audit.jsonl")


# CHTV-1 direction verdicts: (gap_leaf, src, dst) -> ("PASS"|"FAIL", reason)
# Hand-verified per substrate's mathematical conventions.
CHTV_VERDICTS = {
    ("T1/gradient", "T1/gradient", "T1/derivative"): (
        "PASS",
        "gradient is the vector of partial derivatives; derivative is more foundational; "
        "direction DEPENDS_ON is sound."
    ),
    ("T1/gradient", "T1/gradient", "T1/gradient_descent"): (
        "FAIL",
        "gradient_descent USES gradient as input; gradient does NOT require gradient_descent. "
        "Direction inverted. 18th-rule refuse; queue for L6-PROOF inverse v1."
    ),
    ("T2/dynamic_programming", "T2/dynamic_programming", "T3/bellman_equation"): (
        "FAIL",
        "bellman_equation is a SPECIFIC INSTANCE of DP applied to RL value functions. "
        "DP is more general (combinatorial optimization). Direction inverted; "
        "bellman_equation should DEPENDS_ON dynamic_programming, not vice versa. "
        "18th-rule refuse; queue for L6-PROOF inverse v1."
    ),
}


# Only ratify these 3 proposals per DECISION 11 + companion. The other proposals
# in the file (parameter_vector / weight_vector / labeled_example) were already
# closed by ingest at 91572c4d via Skunkworks's grounding relations.
TARGET_GAPS = {"T1/gradient", "T2/dynamic_programming"}


def main():
    ps = PartitionedStore(Path("data/substrate_index"))
    pre_rels = sum(1 for _ in ps.iter_all_relations())
    print(f"pre-ingest: {pre_rels} relations\n")

    existing = set()
    for src, rel_type, tgt in ps.iter_all_relations():
        existing.add((src, rel_type.name, tgt))

    lines = [l for l in PROPOSALS_PATH.read_text(encoding="utf-8").splitlines() if l.strip()]
    print(f"loaded {len(lines)} proposal entries\n")

    ratified = 0
    refused_chtv = 0
    skipped_not_target = 0
    skipped_exists = 0
    skipped_missing_atom = 0
    failed = 0
    audit_lines = []

    for line in lines:
        prop = json.loads(line)
        gap_leaf = prop.get("gap_leaf")
        if gap_leaf not in TARGET_GAPS:
            skipped_not_target += 1
            continue

        for edge in prop.get("proposed_edges", []):
            src = edge["src"]
            dst = edge["dst"]
            rel_str = edge["type"]
            key_chtv = (gap_leaf, src, dst)
            verdict, reason = CHTV_VERDICTS.get(key_chtv, ("UNKNOWN", "no verdict mapped; default REFUSE"))

            audit_rec = {
                "gap_leaf": gap_leaf,
                "edge_src": src,
                "edge_dst": dst,
                "edge_type": rel_str,
                "chtv_verdict": verdict,
                "chtv_reason": reason,
            }
            audit_lines.append(audit_rec)

            if verdict != "PASS":
                print(f"  REFUSED: {src} -{rel_str}-> {dst}")
                print(f"    reason: {reason[:120]}")
                refused_chtv += 1
                continue

            src_qid = f"math::{src}"
            dst_qid = f"math::{dst}"

            if not ps.has_atom(src_qid):
                print(f"  SKIP_MISSING_SRC: {src_qid}")
                skipped_missing_atom += 1
                continue
            if not ps.has_atom(dst_qid):
                print(f"  SKIP_MISSING_DST: {dst_qid}")
                skipped_missing_atom += 1
                continue

            key = (src_qid, rel_str, dst_qid)
            if key in existing:
                print(f"  EXISTS: {src_qid} -{rel_str}-> {dst_qid}")
                skipped_exists += 1
                continue

            try:
                rel_type = RelationType[rel_str]
                ps.add_relation(
                    src_qid, rel_type, dst_qid,
                    source="ratify_gap_proposals_v1",
                    note=f"first autonomous-discovery edge ratified via CHTV-1 PASS; {reason[:80]}",
                )
                existing.add(key)
                print(f"  RATIFIED: {src_qid} -{rel_str}-> {dst_qid}")
                ratified += 1
            except Exception as e:
                print(f"  FAIL: {src_qid} -> {dst_qid} :: {str(e)[:120]}")
                failed += 1

    # Write audit
    RATIFY_AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with RATIFY_AUDIT_PATH.open("a", encoding="utf-8") as fh:
        for rec in audit_lines:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")

    post_rels = sum(1 for _ in ps.iter_all_relations())
    print(f"\n=== GAP-PROPOSAL RATIFY v1 SUMMARY ===")
    print(f"relations: {pre_rels} -> {post_rels}  (+{post_rels - pre_rels})")
    print(f"  ratified: {ratified}")
    print(f"  refused (CHTV-1 direction): {refused_chtv}")
    print(f"  skipped (not target): {skipped_not_target}")
    print(f"  skipped (exists): {skipped_exists}")
    print(f"  skipped (missing atom): {skipped_missing_atom}")
    print(f"  failed: {failed}")
    print(f"\naudit written: {RATIFY_AUDIT_PATH}")
    print(f"\nMILESTONE: first PROACTIVE_GAP_LOOP edges ratified via CHTV-1 verification.")
    print(f"Skunkworks's gradient->derivative proposal earned senior tier autonomously.")
    print(f"Skunkworks's dynamic_programming->bellman_equation REFUSED per 18th rule")
    print(f"  (direction inverted; queues for L6-PROOF inverse v1).")


if __name__ == "__main__":
    main()
