#!/usr/bin/env python3
"""Query interface for data/capability_registry.jsonl (the WIRE/SHELVE capability
gate-decision registry -- see tools/capability_registry_audit.py for how it's kept
current).

WHY THIS EXISTS AS A SEPARATE TOOL (not just "grep the jsonl"): the USER's ask was
explicit -- "what's the latest WIRED encoder / what's islanded / what serves need X"
must be ANSWERABLE BY QUERY. This tool answers that today, with zero dependencies
and no KB rebuild required.

It is also declared as a director_kb source class (config/director_kb_schema.json
"capability_registry") so `python tools/director_kb_query.py --source-class=capability_registry
"<question>"` answers the same questions via cosine search once the next FULL
`python tools/director_kb_ingest.py` (--wipe, all classes) runs. A full re-ingest
wipes+rebuilds the ENTIRE multi-source unified KB (wordnet/framenet/math/concept/...)
-- too disruptive to trigger casually from a small-infra-refinement pass, so THIS
tool is the guaranteed-working query surface in the meantime.

CLI:
  python tools/capability_registry_query.py --wired                  # all WIRED rows
  python tools/capability_registry_query.py --islanded                # ISLAND + TRAPPED_SHARED rows
  python tools/capability_registry_query.py --serves "encoder"        # current_best_for substring match
  python tools/capability_registry_query.py --id gated_fusion_relation_inference
  python tools/capability_registry_query.py --gate VET_PENDING
  python tools/capability_registry_query.py --kind hdlab-module
  python tools/capability_registry_query.py --json                    # emit JSON instead of table
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "data" / "capability_registry.jsonl"

ISLANDED_STATUSES = {"ISLAND", "TRAPPED_SHARED", "UNKNOWN"}


def load_rows() -> list[dict]:
    if not REGISTRY.exists():
        return []
    rows = []
    with open(REGISTRY, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def _print_row(r: dict) -> None:
    print(f"  {r.get('id')}")
    print(f"    name:               {r.get('name')}")
    print(f"    kind:               {r.get('kind')}")
    print(f"    gate_decision:      {r.get('gate_decision')}"
          + (f"  -> {r['gate_decision_target']}" if r.get("gate_decision_target") else ""))
    print(f"    integration_status: {r.get('integration_status')}")
    if r.get("used_by"):
        print(f"    used_by:            {', '.join(r['used_by'][:5])}"
              + (" ..." if len(r["used_by"]) > 5 else ""))
    if r.get("current_best_for"):
        print(f"    serves:             {r.get('current_best_for')}")
    if r.get("revival_criteria"):
        print(f"    revival_criteria:   {r.get('revival_criteria')}")
    print(f"    last_audit_utc:     {r.get('last_audit_utc')}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--wired", action="store_true", help="rows with integration_status == WIRED")
    ap.add_argument("--islanded", action="store_true", help="rows with integration_status in {ISLAND, TRAPPED_SHARED, UNKNOWN}")
    ap.add_argument("--gate", help="filter by gate_decision (e.g. WIRE, SHELVE, VET_PENDING, WIRED)")
    ap.add_argument("--kind", help="filter by kind (hdlab-module, exp-cell, primitive)")
    ap.add_argument("--serves", help="substring match against current_best_for + name (case-insensitive)")
    ap.add_argument("--id", help="exact id lookup")
    ap.add_argument("--json", action="store_true", help="emit JSON list instead of a human table")
    args = ap.parse_args()

    rows = load_rows()
    if not rows:
        print(f"[capability_registry_query] registry empty or missing at {REGISTRY}", file=sys.stderr)
        return 1

    out = rows
    if args.id:
        out = [r for r in out if r.get("id") == args.id]
    if args.wired:
        out = [r for r in out if r.get("integration_status") == "WIRED"]
    if args.islanded:
        out = [r for r in out if r.get("integration_status") in ISLANDED_STATUSES]
    if args.gate:
        out = [r for r in out if r.get("gate_decision") == args.gate]
    if args.kind:
        out = [r for r in out if r.get("kind") == args.kind]
    if args.serves:
        needle = args.serves.lower()
        out = [r for r in out
               if needle in (r.get("current_best_for") or "").lower()
               or needle in (r.get("name") or "").lower()]

    if args.json:
        print(json.dumps(out, indent=2))
        return 0

    print(f"[capability_registry_query] {len(out)} / {len(rows)} rows match")
    for r in out:
        _print_row(r)
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
