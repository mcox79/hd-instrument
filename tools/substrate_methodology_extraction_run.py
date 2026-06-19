"""Run methodology rule extraction on solution-history graph.

Per Findings #12 Q4: substrate extracts transferable methodology rules from
cliff patterns. When the same (old -> new) replacement repeats across 3+
capabilities with avg lift >= 0.10, it becomes a meta rule.
"""
from __future__ import annotations

import json
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.solutions import methodology_rule_extraction

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s | %(message)s")
log = logging.getLogger("rule_extract")

DATA_ROOT = Path("data/substrate_index")


def main():
    pstore = PartitionedStore(DATA_ROOT)
    log.info("corpus: %d atoms", len(pstore.all_atoms()))

    print("\n=== HIGH CONFIDENCE (min_caps=3, min_lift=0.10) ===")
    rules_high = methodology_rule_extraction(pstore, min_capabilities=3, min_lift=0.10)
    for i, r in enumerate(rules_high, 1):
        print(f"{i}. {r.rule_text}")
        print(f"   confidence: {r.confidence:.2f}; n_caps: {r.n_capabilities}")

    print("\n=== MEDIUM CONFIDENCE (min_caps=2, lower threshold) ===")
    rules_medium = methodology_rule_extraction(pstore, min_capabilities=2, min_lift=0.10)
    rules_medium_only = [r for r in rules_medium if r.n_capabilities < 3]
    for i, r in enumerate(rules_medium_only, 1):
        print(f"{i}. {r.rule_text}")
        print(f"   confidence: {r.confidence:.2f}; n_caps: {r.n_capabilities}; capabilities: {[c.split('::')[-1] for c in r.capabilities]}")

    print("\n=== SINGLE-INSTANCE (min_caps=1; tracking only) ===")
    rules_single = methodology_rule_extraction(pstore, min_capabilities=1, min_lift=0.10)
    rules_single_only = [r for r in rules_single if r.n_capabilities < 2]
    for i, r in enumerate(rules_single_only[:10], 1):
        print(f"{i}. {r.rule_text}")
        print(f"   single: {r.capabilities[0].split('::')[-1] if r.capabilities else 'none'}")

    rules = rules_high  # keep original for save path
    print(f"\n{'='*80}")
    print(f"Substrate-extracted methodology rules from solution-history cliffs")
    print(f"{'='*80}")
    print(f"\n{len(rules)} rules surfaced (min_caps=3, min_lift=0.10):\n")
    for i, r in enumerate(rules, 1):
        print(f"{i}. {r.rule_text}")
        print(f"   confidence: {r.confidence:.2f}; capabilities: {[c.split('::')[-1] for c in r.capabilities]}")
        print()

    out = DATA_ROOT / "bench_reports" / f"methodology_rules_{int(time.time())}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "rules": [r.to_dict() for r in rules],
        "extraction_thresholds": {"min_capabilities": 3, "min_lift": 0.10},
    }, indent=2), encoding="utf-8")
    log.info("wrote rules report -> %s", out)


if __name__ == "__main__":
    main()
