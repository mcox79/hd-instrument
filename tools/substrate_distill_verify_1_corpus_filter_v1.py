"""DISTILL-VERIFY-1 corpus-filter post-processor v1.

The pre-registered experiment exp_substrate_distill_verify_1_*.py groups
atoms by short_id across ALL corpora, which surfaces non-operator atoms
(routing notes, methodology rules) as false duplicate groups. These false
positives are intentionally bucketed as UNDECIDABLE_BY_PROVER (bare).

This post-processor produces a CLEANED verdict report that excludes those
false-positive groups, yielding the algorithm-only distillation ratio.

Filter:
  - Exclude groups whose names start with research_drill_ / research_to_
    (routing-note files mis-registered as duplicate atoms).
  - Exclude groups whose names start with rule_ / RULE_ (methodology rules,
    not operator atoms).

Pre-reg semantics PRESERVED: the original report is left untouched.
Output is a separate file documenting the algorithm-only ratio.

NO LLM. NO bge. Read-only over the pre-reg JSON.
"""
from __future__ import annotations
import json
import sys
from collections import Counter
from pathlib import Path


SRC = Path("data/substrate_index/bench_reports/distill_verify_1_operator_equivalence.json")
DST = Path("data/substrate_index/bench_reports/distill_verify_1_operator_equivalence_algorithm_only.json")


NOISE_PREFIXES = (
    "research_drill_",
    "research_to_",
    "rule_",  # case-insensitive in lowered short_id
)


def is_noise(name: str) -> bool:
    n = name.lower()
    return any(n.startswith(p) for p in NOISE_PREFIXES)


def main():
    if not SRC.exists():
        print(f"ERROR: source report not found: {SRC}")
        sys.exit(2)
    src = json.loads(SRC.read_text(encoding="utf-8"))
    raw_results = src.get("results", [])
    print(f"raw groups: {len(raw_results)}")

    noise_groups = [r for r in raw_results if is_noise(r["name"])]
    print(f"noise groups (filtered out): {len(noise_groups)}")
    for r in noise_groups:
        print(f"  EXCLUDE: {r['name']:55s}  verdict={r['verdict']}")

    clean = [r for r in raw_results if not is_noise(r["name"])]
    print(f"\nalgorithm-only groups: {len(clean)}")

    vc = Counter(r["verdict"] for r in clean)
    prov_or_cap = vc.get("PROVABLY_EQUIVALENT", 0) + vc.get("EQUIVALENT_BY_CAPABILITY", 0)
    distill = round(prov_or_cap / len(clean), 4) if clean else 0.0

    print(f"\nalgorithm-only verdicts: {dict(vc)}")
    print(f"algorithm-only distillation ratio: {prov_or_cap}/{len(clean)} = {distill}")
    print(f"  (raw report had {len(raw_results)} groups, ratio {src.get('distillation_ratio')})")

    out = {
        "source_report": str(SRC),
        "filter_policy": "exclude names starting with research_drill_ / research_to_ / rule_",
        "raw_group_count": len(raw_results),
        "raw_distillation_ratio": src.get("distillation_ratio"),
        "filtered_noise_groups": [r["name"] for r in noise_groups],
        "results": clean,
        "verdict_counts": dict(vc),
        "distillation_ratio_algorithm_only": distill,
    }
    DST.parent.mkdir(parents=True, exist_ok=True)
    DST.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nwrote: {DST}")


if __name__ == "__main__":
    main()
