"""TESTBED-DISTILL-INTEGRATE-2 -- B' hybrid policy (Option iii per Research).

Per Research DECISIONS note 2026-06-14: B' v2 = Option (iii) hybrid.
  Rewrite LIVE substrate-state references (atoms.jsonl + relations.jsonl
    + audit.jsonl + verify/integrate reports) AND outgoing relation edges
    from T3 atoms before removal.
  KEEP notes/ historical references verbatim.

Concrete spec (per Research):
  1. ps.remove_atom(T3) after merge into T2 (current v1 behavior)
  2. Append audit record to data/substrate_index/distill_audit.jsonl
  3. Rewrite outgoing relations FROM T3 to FROM T2 canonical
     (and incoming relations TO T3 to TO T2 canonical, symmetric)
  4. Append redirect entry to canonical_alias_map.jsonl (v1 already does)
  5. Do NOT touch notes/

Implementation notes:
  - Store.remove_atom cascades + deletes all relations touching the atom.
    So edge rewrites must happen BEFORE remove_atom.
  - Skip SUPERSEDED_BY edges between T3 and T2 -- they become self-loops
    on rewrite; semantically they move to the audit log.
  - Skip any rewrite that would create a self-loop on T2.
  - Skip any rewrite that duplicates an existing T2-touching edge.

Sequencing per Research:
  F1 canonical+bge measurement FIRST
  F3 baseline under A SECOND
  B' v2 SHIPS THIRD (after F1 + F3 land)

Default mode is --dry-run (no writes). Explicit --execute required.

NO LLM. NO bge. Read-only by default.
"""
from __future__ import annotations
import sys
import json
import argparse
from pathlib import Path
from collections import Counter
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import RelationType


VERIFY_RESULTS_PATH = Path("data/substrate_index/bench_reports/distill_verify_1_operator_equivalence.json")
INTEGRATE_V1_REPORT = Path("data/substrate_index/bench_reports/distill_integrate_1_report.json")
DISTILL_AUDIT_PATH = Path("data/substrate_index/distill_audit.jsonl")
ALIAS_MAP_PATH = Path("data/substrate_index/canonical_alias_map.jsonl")
B_PRIME_REPORT_PATH = Path("data/substrate_index/bench_reports/distill_integrate_2_b_prime_report.json")

# Per Research policy: SUPERSEDED_BY edges move to audit log (not rewritten
# to self-loop). Skip these in the edge-rewrite step.
SKIP_REL_TYPES = {"SUPERSEDED_BY"}


def collect_edges(ps, atom_qid):
    """Return (out_edges, in_edges) for the given qualified atom id.

    out_edges = list of (rel_type, tgt_qualified_id) for src=atom_qid
    in_edges  = list of (src_qualified_id, rel_type) for tgt=atom_qid
    """
    out_edges = []
    in_edges = []
    for src, rel_type, tgt in ps.iter_all_relations():
        if src == atom_qid:
            out_edges.append((rel_type.name, tgt))
        if tgt == atom_qid:
            in_edges.append((src, rel_type.name))
    return out_edges, in_edges


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--execute", action="store_true",
                    help="Actually perform removes + rewrites. Default is dry-run.")
    ap.add_argument("--integrate-v1-report", default=str(INTEGRATE_V1_REPORT),
                    help="Path to integrate-v1 report listing PROVABLY_EQUIVALENT pairs.")
    args = ap.parse_args()

    if not args.execute:
        print("DRY-RUN MODE (default). Pass --execute to actually remove + rewrite.")
        print("Per Research sequencing: F1 + F3 must land before --execute.\n")

    integrate_path = Path(args.integrate_v1_report)
    if not integrate_path.exists():
        print(f"ERROR: integrate v1 report not found: {integrate_path}")
        sys.exit(2)

    integrate_report = json.loads(integrate_path.read_text(encoding="utf-8"))
    integrations = integrate_report.get("integrations", [])
    print(f"loaded {len(integrations)} integrated pairs from {integrate_path}\n")

    ps = PartitionedStore(Path("data/substrate_index"))

    # Filter to PROVABLY_EQUIVALENT only (Class A atom-removing); skip
    # EQUIVALENT_BY_CAPABILITY (weaker; deferred per Research B' spec
    # which targets the PROVABLY_EQUIVALENT pairs).
    eligible = [p for p in integrations if p.get("verdict") == "PROVABLY_EQUIVALENT"]
    print(f"eligible PROVABLY_EQUIVALENT pairs: {len(eligible)}")
    print(f"deferred EQUIVALENT_BY_CAPABILITY pairs: {sum(1 for p in integrations if p.get('verdict') == 'EQUIVALENT_BY_CAPABILITY')}\n")

    audit_records = []
    removed = 0
    edges_rewritten = 0
    edges_skipped_existing = 0
    edges_skipped_self_loop = 0
    edges_skipped_superseded_by = 0
    failed = 0

    # Pre-load existing relation set for duplicate-check during rewrites.
    existing = set()
    for src, rel_type, tgt in ps.iter_all_relations():
        existing.add((src, rel_type.name, tgt))

    for pair in eligible:
        canonical_qid = pair["canonical_qid"]
        for alias_qid in pair.get("alias_qids", []):
            if alias_qid == canonical_qid:
                continue
            if not ps.has_atom(alias_qid):
                # Already removed (or never present); skip silently
                continue

            out_edges, in_edges = collect_edges(ps, alias_qid)
            print(f"PAIR {alias_qid} -> {canonical_qid}: out={len(out_edges)} in={len(in_edges)}")

            # Edge rewrites: must happen BEFORE remove_atom (which cascades).
            for rel_name, tgt in out_edges:
                if rel_name in SKIP_REL_TYPES:
                    edges_skipped_superseded_by += 1
                    continue
                if tgt == canonical_qid:
                    edges_skipped_self_loop += 1
                    continue
                key = (canonical_qid, rel_name, tgt)
                if key in existing:
                    edges_skipped_existing += 1
                    continue
                if args.execute:
                    try:
                        ps.add_relation(
                            canonical_qid, RelationType[rel_name], tgt,
                            source="distill_integrate_v2_b_prime",
                            note=f"rewrite outgoing from removed alias {alias_qid}",
                        )
                        existing.add(key)
                        edges_rewritten += 1
                    except Exception as e:
                        print(f"  EDGE_REWRITE_FAIL out {alias_qid} -> {tgt}: {str(e)[:80]}")
                        failed += 1
                else:
                    print(f"  [DRY] would rewrite OUT: {canonical_qid} -{rel_name}-> {tgt}")
                    edges_rewritten += 1

            for src, rel_name in in_edges:
                if rel_name in SKIP_REL_TYPES:
                    edges_skipped_superseded_by += 1
                    continue
                if src == canonical_qid:
                    edges_skipped_self_loop += 1
                    continue
                key = (src, rel_name, canonical_qid)
                if key in existing:
                    edges_skipped_existing += 1
                    continue
                if args.execute:
                    try:
                        ps.add_relation(
                            src, RelationType[rel_name], canonical_qid,
                            source="distill_integrate_v2_b_prime",
                            note=f"rewrite incoming to removed alias {alias_qid}",
                        )
                        existing.add(key)
                        edges_rewritten += 1
                    except Exception as e:
                        print(f"  EDGE_REWRITE_FAIL in {src} -> {alias_qid}: {str(e)[:80]}")
                        failed += 1
                else:
                    print(f"  [DRY] would rewrite IN:  {src} -{rel_name}-> {canonical_qid}")
                    edges_rewritten += 1

            # Audit record (collect; flush at end if --execute)
            audit_records.append({
                "removed_qid": alias_qid,
                "canonical_qid": canonical_qid,
                "verdict": pair.get("verdict"),
                "shared_caps": pair.get("shared_caps", []),
                "out_edges_rewritten": [(r, t) for (r, t) in out_edges if r not in SKIP_REL_TYPES],
                "in_edges_rewritten": [(s, r) for (s, r) in in_edges if r not in SKIP_REL_TYPES],
                "policy": "B_prime_hybrid_option_iii",
            })

            # Remove the atom (cascade-deletes its old relations)
            if args.execute:
                try:
                    ok = ps.remove_atom(
                        alias_qid,
                        source="distill_integrate_v2_b_prime",
                        note=f"B' hybrid: T3 alias removed; canonical at {canonical_qid}",
                    )
                    if ok:
                        removed += 1
                        print(f"  REMOVED: {alias_qid}")
                    else:
                        failed += 1
                        print(f"  REMOVE_RETURNED_FALSE: {alias_qid}")
                except Exception as e:
                    print(f"  REMOVE_FAIL: {alias_qid} :: {str(e)[:80]}")
                    failed += 1
            else:
                print(f"  [DRY] would remove: {alias_qid}")
                removed += 1

    # Audit log
    if args.execute and audit_records:
        DISTILL_AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with DISTILL_AUDIT_PATH.open("a", encoding="utf-8") as fh:
            for rec in audit_records:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        print(f"\naudit log appended: {DISTILL_AUDIT_PATH}")

    # Final report
    report = {
        "mode": "execute" if args.execute else "dry_run",
        "policy": "B_prime_hybrid_option_iii",
        "research_decision_source": "research_to_testbed_exp_dev_DECISIONS_B_prime_option_iii_*_2026-06-14.md",
        "sequencing_note": "F1 + F3 must land before --execute per Research",
        "eligible_pairs": len(eligible),
        "removed_count": removed,
        "edges_rewritten": edges_rewritten,
        "edges_skipped_existing": edges_skipped_existing,
        "edges_skipped_self_loop": edges_skipped_self_loop,
        "edges_skipped_superseded_by": edges_skipped_superseded_by,
        "failed": failed,
    }
    if args.execute:
        B_PRIME_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        B_PRIME_REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"\nreport written: {B_PRIME_REPORT_PATH}")

    print(f"\n=== DISTILL-INTEGRATE-2 B' SUMMARY ({report['mode']}) ===")
    print(f"  eligible pairs: {len(eligible)}")
    print(f"  removed: {removed}")
    print(f"  edges rewritten: {edges_rewritten}")
    print(f"  edges skipped (already exist): {edges_skipped_existing}")
    print(f"  edges skipped (would self-loop): {edges_skipped_self_loop}")
    print(f"  edges skipped (SUPERSEDED_BY -> audit log): {edges_skipped_superseded_by}")
    print(f"  failed: {failed}")
    if not args.execute:
        print(f"\nDRY-RUN: no substrate state mutated. Run with --execute when F1+F3 land.")


if __name__ == "__main__":
    main()
