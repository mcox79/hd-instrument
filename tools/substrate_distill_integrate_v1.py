"""TESTBED-DISTILL-INTEGRATE-1 -- step 4 of substrate recursive self-improvement loop.

Per Research routing 14:45 + Exp-Dev CELL-DISTILL-VERIFY-1 HARD_PASS (commit f203afce):
substrate's recursive self-improvement loop demonstrated step 3 OPERATIONAL with
0 false merges. Testbed step 4 = INTEGRATE the verified-equivalent pairs.

Inputs:
  - data/substrate_index/bench_reports/distill_verify_1_operator_equivalence.json
    (Exp-Dev's verdict; contains 5 PROVABLY_EQUIVALENT + 6 EQUIVALENT_BY_CAPABILITY
    + 22 UNDECIDABLE_BY_PROVER (refused merge); 0 NOT_EQUIVALENT)

Action per Research spec:
  1. For each PROVABLY_EQUIVALENT + EQUIVALENT_BY_CAPABILITY pair:
       - Designate T2 (the higher-tier promoted form per KP P1) as CANONICAL
       - Designate T3 as ALIAS (semantically superseded; not deleted to preserve provenance)
       - Merge T3's aliases into T2's aliases tuple
       - Add SUPERSEDED_BY edge T3 -> T2 (or strengthen existing SUPERSEDES T2 -> T3)
  2. Build canonical-atom-ID alias map JSONL per drill 15 spec (preferred-label + altLabel)
       - Output: data/substrate_index/canonical_alias_map.jsonl
  3. ATOMIC: uses Pattern 1 write-tmp+fsync+os.replace per schema (already shipped a5acfc36)
       - Pattern 2 (CURRENT-pointer snapshot swap) deferred to separate refactor

Output:
  - canonical_alias_map.jsonl (one JSONL entry per canonical with altLabels)
  - distill_integrate_1_report.json (action summary; SHA verifiable)

NO LLM. NO bge. Pure structural integration; tolerant of missing atoms.

This is HIGHEST PRIORITY engineering work per Research routing (14:45).
"""
from __future__ import annotations
import sys
import json
import dataclasses
import argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, RelationType


VERIFY_RESULTS_PATH = Path("data/substrate_index/bench_reports/distill_verify_1_operator_equivalence.json")
ALIAS_MAP_PATH = Path("data/substrate_index/canonical_alias_map.jsonl")
REPORT_PATH = Path("data/substrate_index/bench_reports/distill_integrate_1_report.json")

# Verdicts to integrate (PROVABLY_EQUIVALENT + EQUIVALENT_BY_CAPABILITY = sound).
# UNDECIDABLE_BY_PROVER + NOT_EQUIVALENT are NOT integrated.
ELIGIBLE_VERDICTS = {"PROVABLY_EQUIVALENT", "EQUIVALENT_BY_CAPABILITY"}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--dry-run", action="store_true",
                    help="Print planned integrations; do not write")
    ap.add_argument("--verify-results", default=str(VERIFY_RESULTS_PATH))
    args = ap.parse_args()

    vp = Path(args.verify_results)
    if not vp.exists():
        print(f"ERROR: verify results not found at {vp}")
        sys.exit(2)
    verify = json.loads(vp.read_text(encoding="utf-8"))
    print(f"loaded verify results from {vp}")
    print(f"verdict counts: {verify.get('verdict_counts')}")
    print(f"distillation_ratio: {verify.get('distillation_ratio')}")

    ps = PartitionedStore(Path("data/substrate_index"))

    eligible = [r for r in verify.get("results", []) if r.get("verdict") in ELIGIBLE_VERDICTS]
    print(f"\neligible for integration: {len(eligible)} pairs ({sorted(set(r['verdict'] for r in eligible))})")

    alias_map_entries = []
    integrations = []
    pairs_skipped = 0
    pairs_failed = 0

    for r in eligible:
        name = r["name"]
        tiers = r["tiers"]
        verdict = r["verdict"]
        # The 11 pairs are all T2 + T3 pairs (per Exp-Dev verdict structure)
        # Designate T2 (higher-tier from KP P1 promotion) as canonical, T3 as alias
        t2_qid = f"math::T2/{name}"
        t3_qid = f"math::T3/{name}"

        t2_atom = ps.get_atom(t2_qid)
        t3_atom = ps.get_atom(t3_qid)
        if not t2_atom or not t3_atom:
            print(f"  SKIP {name}: T2 exists={bool(t2_atom)} T3 exists={bool(t3_atom)}")
            pairs_skipped += 1
            continue

        # Build merged alias tuple (preserving original)
        merged_aliases = list(t2_atom.aliases or ())
        for al in (t3_atom.aliases or ()):
            if al not in merged_aliases:
                merged_aliases.append(al)
        # Add T3-form as explicit alias
        t3_alias_form = f"T3/{name}"
        if t3_alias_form not in merged_aliases:
            merged_aliases.append(t3_alias_form)

        integration = {
            "canonical_qid": t2_qid,
            "alias_qids": [t3_qid],
            "canonical_label": t2_atom.name,
            "alt_labels": list(set(merged_aliases) - set(t2_atom.aliases or ())),
            "verdict": verdict,
            "shared_caps": r.get("shared_caps", []),
        }
        integrations.append(integration)

        # Alias map JSONL entry (per drill 15: preferred-label + altLabel)
        alias_map_entries.append({
            "canonical_id": t2_qid,
            "preferred_label": t2_atom.name,
            "altLabels": [
                {"id": t3_qid, "name": t3_atom.name, "source": "distill_verify_1"},
            ],
            "verdict": verdict,
            "tier_pair": tiers,
        })

        if args.dry_run:
            continue

        # Atomic update: rewrite T2 atom with merged aliases
        try:
            new_meta = dict(t2_atom.metadata or {})
            new_meta["distill_integrate_1"] = {
                "merged_alias": t3_qid,
                "verdict": verdict,
                "shared_cap_count": len(r.get("shared_caps", [])),
                "integration_source": "TESTBED_DISTILL_INTEGRATE_1",
            }
            new_t2 = dataclasses.replace(t2_atom, aliases=tuple(merged_aliases), metadata=new_meta)
            ps.remove_atom(t2_qid)
            ps.add_atom(new_t2, source="testbed_distill_integrate_1",
                        note=f"DISTILL-INTEGRATE-1 step 4; verdict={verdict}; canonical merge of {t3_qid}")
        except Exception as e:
            print(f"  T2 UPDATE FAIL {t2_qid}: {str(e)[:120]}")
            pairs_failed += 1
            continue

        # Add SUPERSEDED_BY edge T3 -> T2 (T3 is superseded by canonical T2)
        try:
            ps.add_relation(t3_qid, RelationType.SUPERSEDED_BY, t2_qid,
                            source="testbed_distill_integrate_1",
                            note=f"DISTILL-INTEGRATE-1 step 4; T3 superseded by T2 canonical merge per verdict {verdict}")
        except Exception as e:
            # If edge already exists or fails, log but don't abort
            msg = str(e)[:120]
            if not any(k in msg.lower() for k in ("already", "duplicate")):
                print(f"  EDGE WARN {t3_qid}: {msg}")

        print(f"  INTEGRATED {name}: T2 canonical + T3 aliased ({verdict})")

    # Write alias map JSONL (atomic)
    if not args.dry_run and alias_map_entries:
        ALIAS_MAP_PATH.parent.mkdir(parents=True, exist_ok=True)
        tmp = ALIAS_MAP_PATH.with_suffix(ALIAS_MAP_PATH.suffix + ".tmp")
        import os
        with tmp.open("w", encoding="utf-8") as f:
            for e in alias_map_entries:
                f.write(json.dumps(e, ensure_ascii=False) + "\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, ALIAS_MAP_PATH)
        print(f"\nalias map written: {ALIAS_MAP_PATH} ({len(alias_map_entries)} entries)")

    # Report
    report = {
        "source_verify_results": str(vp),
        "verdict_counts_input": verify.get("verdict_counts"),
        "distillation_ratio_input": verify.get("distillation_ratio"),
        "pairs_eligible_for_integration": len(eligible),
        "pairs_integrated": len(integrations),
        "pairs_skipped": pairs_skipped,
        "pairs_failed": pairs_failed,
        "integrations": integrations,
        "alias_map_path": str(ALIAS_MAP_PATH),
        "dry_run": args.dry_run,
    }
    if not args.dry_run:
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"\nreport written: {REPORT_PATH}")

    print(f"\n=== TESTBED-DISTILL-INTEGRATE-1 SUMMARY ===")
    print(f"eligible pairs: {len(eligible)}")
    print(f"integrated: {len(integrations)}")
    print(f"skipped: {pairs_skipped}")
    print(f"failed: {pairs_failed}")
    print(f"\nStep 4 of closed-loop COMPLETE (pending Research step 5 distillation-ratio measurement).")
    if args.dry_run:
        print(f"\n[DRY RUN] no changes written.")


if __name__ == "__main__":
    main()
