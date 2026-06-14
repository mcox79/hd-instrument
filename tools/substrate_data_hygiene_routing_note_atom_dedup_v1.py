"""Data hygiene: dedupe routing-note + methodology-rule atoms across corpora.

Per Research POLICY DECISION (2026-06-13 B' hybrid + 4 reservations):
data hygiene cleanup comes BEFORE B' v2 ship. Independent step.

Substrate has 12 atoms across 4 corpora that surface as 6 false-positive
duplicate groups in DISTILL-VERIFY-1:
  4 routing-note files (research_drill_* / research_to_exp_dev_*) ingested
    into METHODOLOGY + RESEARCH_HISTORY + (one into DECISION_HISTORY)
  2 methodology rules (RULE_count_nb_*, rule_drill_defeatism) in META
    corpus duplicated across tier=METHODOLOGY and tier=NA

Cleanup policy:
  Routing-note files: canonical home is RESEARCH_HISTORY (archival of
    routing decisions/research drills). Remove METHODOLOGY and
    DECISION_HISTORY copies.
  Methodology rules: canonical tier is TIER_METHODOLOGY in META corpus.
    Remove the TIER_NA tier copies.

After cleanup, DISTILL-VERIFY-1 should naturally read 1.00 distillation
ratio (no false-positive UNDECIDABLE groups). Verifier change unnecessary.

Audit: each removal logged via ps.remove_atom (audit.jsonl trail).

NO LLM. NO bge.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore


ROUTING_NOTE_SHORT_IDS = {
    "research_drill_1bit_depth_verify_2x_2026-06-10",
    "research_drill_20_ambitious_ideas_1x_plus_3_deep_dives_2x_2026-06-05",
    "research_drill_8_channel_orchestration_architecture_2026-06-03",
    "research_to_exp_dev_1bit_depth_verification_2026-06-10",
}

METHODOLOGY_RULE_SHORT_IDS = {
    "rule_count_nb_to_discriminative_perceptron",
    "rule_drill_defeatism",
}


def main():
    ps = PartitionedStore(Path("data/substrate_index"))
    atoms = ps.all_atoms()
    pre_count = len(atoms)
    print(f"pre-hygiene total atoms: {pre_count}\n")

    # Identify all atoms by short_id (case-insensitive)
    by_short = {}
    for a in atoms:
        short = str(a.id).split("::")[-1].split("/")[-1].strip().lower()
        by_short.setdefault(short, []).append(a)

    to_remove = []

    # Routing notes: keep RESEARCH_HISTORY copy, remove others
    for short in ROUTING_NOTE_SHORT_IDS:
        members = by_short.get(short, [])
        if len(members) < 2:
            continue
        # Find the RESEARCH_HISTORY copy (canonical)
        canonical = next((a for a in members if a.corpus.name == "RESEARCH_HISTORY"), None)
        if canonical is None:
            print(f"  WARN: {short} has no RESEARCH_HISTORY canonical; skipping")
            continue
        for a in members:
            if a is canonical:
                continue
            to_remove.append((a, f"routing-note cross-corpus dup; canonical at {canonical.id} corpus=RESEARCH_HISTORY"))

    # Methodology rules: keep TIER_METHODOLOGY copy, remove TIER_NA copy
    for short in METHODOLOGY_RULE_SHORT_IDS:
        members = by_short.get(short, [])
        if len(members) < 2:
            continue
        canonical = next((a for a in members if a.tier.name == "TIER_METHODOLOGY"), None)
        if canonical is None:
            print(f"  WARN: {short} has no TIER_METHODOLOGY canonical; skipping")
            continue
        for a in members:
            if a is canonical:
                continue
            to_remove.append((a, f"methodology-rule tier dup; canonical at {canonical.id} tier=TIER_METHODOLOGY"))

    print(f"\nplanned removals: {len(to_remove)}\n")
    removed = 0
    failed = 0
    audit_lines = []
    for a, reason in to_remove:
        try:
            qid = f"{a.corpus.name.lower()}::{a.id}"
            ok = ps.remove_atom(qid, source="data_hygiene_v1", note=reason)
            if ok:
                print(f"  REMOVED: {qid}  ({reason})")
                audit_lines.append({"removed_qid": qid, "reason": reason})
                removed += 1
            else:
                print(f"  REMOVE_RETURNED_FALSE: {qid}")
                failed += 1
        except Exception as e:
            print(f"  REMOVE_FAIL: {a.id} :: {str(e)[:120]}")
            failed += 1

    # Write audit stub
    audit_path = Path("data/substrate_index/data_hygiene_audit.jsonl")
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    import json
    with audit_path.open("a", encoding="utf-8") as fh:
        for line in audit_lines:
            fh.write(json.dumps(line, ensure_ascii=False) + "\n")

    post_atoms = len(ps.all_atoms())
    print(f"\n=== DATA HYGIENE v1 SUMMARY ===")
    print(f"atoms: {pre_count} -> {post_atoms}  ({post_atoms - pre_count:+d})")
    print(f"  removed: {removed}")
    print(f"  failed: {failed}")
    print(f"audit written: {audit_path}")
    print(f"\nNext: re-run DISTILL-VERIFY-1 -- expect 6 false-positive UNDECIDABLE groups to drop.")
    print(f"Algorithm-only distillation ratio should read 1.00 natively (no post-processor needed).")


if __name__ == "__main__":
    main()
