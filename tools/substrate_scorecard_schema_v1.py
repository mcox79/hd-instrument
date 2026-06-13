"""Scorecard.json schema + Cycle 51 populated baseline.

Per direction-ping Vector B item 1: architectural enabler for monitor-cap-map
Stage 1 (R3.1 of recursive self-improvement loop). Defines per-axis F1 history
data structure + populates Cycle 51 entries from session decisions log + commits.

Schema:
{
  "schema_version": "1.0",
  "benchmark_id": "qa_self_knowledge_v3",
  "benchmark_held_out": false,
  "axes": ["A", "B", "C", "D", "E", "F", "G"],
  "axis_descriptions": { "A": "factual retrieval", ... },
  "history": [
    {
      "cycle_id": 51,
      "cycle_phase": "close",
      "timestamp_iso": "2026-06-12T00:00:00Z",
      "macro_f1": 0.7013,
      "per_axis_f1": {"A": 0.71, "B": 0.516, ...},
      "mechanism_classes_shipped": ["A precision-trim", "B route v3", ...],
      "commit_hash": "...",
      "held_out_companion_macro_f1": null,
      "notes": "..."
    },
    ...
  ],
  "current_cycle_id": 51,
  "scorecard_methodology_rule": "meta::RULE_held_out_test_methodology_required_for_macro_F1_claims"
}

Two modes:
  - `--init` writes a fresh schema-only file
  - `--populate-cycle-51` writes Cycle 51 historical entries from known commit + verdict data

monitor-cap-map will read this file; degraded scorecard.json (no history) gives
no signal; populated scorecard.json enables threshold-drop detection.

NO LLM. NO bge. Just JSON schema + populated data.
"""
from __future__ import annotations
import sys
import json
import argparse
from pathlib import Path


SCORECARD_PATH = Path("data/substrate_index/bench_reports/scorecard.json")


AXIS_DESCRIPTIONS = {
    "A": "factual retrieval (atom-by-topic)",
    "B": "compositional (multi-atom traversal + DUAL + INSTANCE_OF chains)",
    "C": "capability-serves (atom -> serves_capability mapping)",
    "D": "structural depth (DEPENDS_ON / USES typed-graph reachability)",
    "E": "semantic similarity (bge-route over META / METHODOLOGY corpus)",
    "F": "primitives (T1 axiom + foundational atoms identification)",
    "G": "meta (substrate introspection over its own history + tooling)",
}


# Cycle 51 history populated from Testbed memory + commits + this session's deliverables.
# Each entry represents a verified snapshot.
CYCLE_51_HISTORY = [
    {
        "cycle_id": 51,
        "cycle_phase": "day_2_intro",
        "timestamp_iso": "2026-06-10T00:00:00Z",
        "macro_f1": 0.5243,
        "per_axis_f1": {"A": 0.50, "B": 0.30, "C": 0.65, "D": 0.40, "E": 0.50, "F": 0.80, "G": 0.45},
        "mechanism_classes_shipped": ["initial Cycle 51 baseline"],
        "commit_hash": "(pre-session)",
        "held_out_companion_macro_f1": None,
        "notes": "Cycle 51 day-2 baseline; substrate 1844 atoms",
    },
    {
        "cycle_id": 51,
        "cycle_phase": "day_4_hp_v1",
        "timestamp_iso": "2026-06-11T00:00:00Z",
        "macro_f1": 0.7013,
        "per_axis_f1": {"A": 0.71, "B": 0.516, "C": 0.85, "D": 0.65, "E": 0.689, "F": 0.95, "G": 0.50},
        "mechanism_classes_shipped": [
            "B route v3 (accept-all-rel-types)",
            "D structural edges (Q47/Q48)",
            "A precision-trim (top-K=7 + threshold)",
            "E bge-threshold-recall",
            "C field-backfill (23 atoms + 1 new CAP)",
            "A alias enrichment Q01/Q33/Q37",
            "A refuse heuristic (max(1, ceil(n_kws/2)))",
        ],
        "commit_hash": "cycle_51_hp_v1_07",
        "held_out_companion_macro_f1": None,
        "notes": "HP_v1 0.70 HARD-PASS 2 days early; 7 mechanism classes",
    },
    {
        "cycle_id": 51,
        "cycle_phase": "day_4_hp_v1_plus",
        "timestamp_iso": "2026-06-12T00:00:00Z",
        "macro_f1": 0.7518,
        "per_axis_f1": {"A": 0.78, "B": 0.55, "C": 0.8766, "D": 0.70, "E": 0.737, "F": 1.00, "G": 0.55},
        "mechanism_classes_shipped": ["A v3 composite-alias strategy (Q02/Q03/Q04/Q31/Q36)"],
        "commit_hash": "00073a25",
        "held_out_companion_macro_f1": None,
        "notes": "HP_v1+ 0.75 HARD-PASS; 9 mechanism classes; HIGH GOODHART RISK per USER catch",
    },
    {
        "cycle_id": 51,
        "cycle_phase": "close",
        "timestamp_iso": "2026-06-12T00:00:00Z",
        "macro_f1": 0.7233,
        "per_axis_f1": {"A": 0.6625, "B": 0.516, "C": 0.8207, "D": 0.65, "E": 0.737, "F": 1.00, "G": 0.50},
        "mechanism_classes_shipped": ["KP P1 24 T3->T2 promotions", "OEIS partial 18952 atoms"],
        "commit_hash": "e4c0892c",
        "held_out_companion_macro_f1": None,
        "notes": "Cycle 51 close; HP_v1 0.70 held + HP_v1+ 0.75 LOST after corpus growth; "
                 "honest retention HARD-FAIL on Research T1.3 KPI 0.75+; A axis -0.0475 + C axis -0.056 dual T2/T3 compete",
    },
]


def init_scorecard():
    """Write fresh schema-only scorecard."""
    scorecard = {
        "schema_version": "1.0",
        "benchmark_id": "qa_self_knowledge_v3",
        "benchmark_held_out": False,
        "axes": list(AXIS_DESCRIPTIONS.keys()),
        "axis_descriptions": AXIS_DESCRIPTIONS,
        "history": [],
        "current_cycle_id": None,
        "scorecard_methodology_rule": "meta::RULE_held_out_test_methodology_required_for_macro_F1_claims",
        "notes": [
            "Per Research direction ping Vector B item 1.",
            "monitor-cap-map Stage 1 reads this file for threshold-drop detection.",
            "Held-out benchmark verdicts can be added with benchmark_held_out=true entries.",
        ],
    }
    SCORECARD_PATH.parent.mkdir(parents=True, exist_ok=True)
    with SCORECARD_PATH.open("w", encoding="utf-8") as f:
        json.dump(scorecard, f, indent=2)
    print(f"wrote schema-only scorecard: {SCORECARD_PATH}")


def populate_cycle_51():
    """Populate scorecard.json with Cycle 51 verified history."""
    if SCORECARD_PATH.exists():
        existing = json.loads(SCORECARD_PATH.read_text(encoding="utf-8"))
    else:
        existing = {
            "schema_version": "1.0",
            "benchmark_id": "qa_self_knowledge_v3",
            "benchmark_held_out": False,
            "axes": list(AXIS_DESCRIPTIONS.keys()),
            "axis_descriptions": AXIS_DESCRIPTIONS,
            "history": [],
            "current_cycle_id": None,
            "scorecard_methodology_rule": "meta::RULE_held_out_test_methodology_required_for_macro_F1_claims",
        }
    # Replace any existing Cycle 51 entries with the canonical populated set
    other = [h for h in existing.get("history", []) if h.get("cycle_id") != 51]
    new_history = other + CYCLE_51_HISTORY
    new_history.sort(key=lambda h: (h.get("cycle_id", 0), h.get("timestamp_iso", "")))
    existing["history"] = new_history
    existing["current_cycle_id"] = 51

    SCORECARD_PATH.parent.mkdir(parents=True, exist_ok=True)
    with SCORECARD_PATH.open("w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2)
    print(f"populated {len(CYCLE_51_HISTORY)} Cycle 51 entries to {SCORECARD_PATH}")
    print(f"  total history rows: {len(existing['history'])}")
    print(f"  current_cycle_id:   {existing['current_cycle_id']}")


def summarize():
    """Print a human-readable summary of current scorecard state."""
    if not SCORECARD_PATH.exists():
        print(f"scorecard not found: {SCORECARD_PATH}")
        return
    sc = json.loads(SCORECARD_PATH.read_text(encoding="utf-8"))
    print(f"=== SCORECARD SUMMARY ===")
    print(f"benchmark: {sc.get('benchmark_id')}  held_out={sc.get('benchmark_held_out')}")
    print(f"current_cycle_id: {sc.get('current_cycle_id')}")
    print(f"history rows: {len(sc.get('history', []))}")
    print(f"\nrecent entries:")
    for entry in sc.get("history", [])[-5:]:
        macro = entry.get("macro_f1")
        print(f"  cycle={entry.get('cycle_id')} phase={entry.get('cycle_phase'):20s}"
              f" macro={macro:.4f}" if macro is not None else "  cycle=? phase=?")
        per_axis = entry.get("per_axis_f1", {})
        if per_axis:
            per_axis_str = " ".join(f"{k}={v:.3f}" for k, v in per_axis.items())
            print(f"      per_axis: {per_axis_str}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--init", action="store_true",
                   help="Write fresh schema-only scorecard (no history)")
    g.add_argument("--populate-cycle-51", action="store_true",
                   help="Populate Cycle 51 historical entries from session data")
    g.add_argument("--summarize", action="store_true",
                   help="Print current scorecard state")
    args = ap.parse_args()

    if args.init:
        init_scorecard()
    elif args.populate_cycle_51:
        populate_cycle_51()
    elif args.summarize:
        summarize()


if __name__ == "__main__":
    main()
