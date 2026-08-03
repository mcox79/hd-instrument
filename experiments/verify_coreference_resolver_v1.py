# WIRING VERIFICATION, not a scored exp_ cell (no pre-reg/queue dispatch needed): proves the
# hdlab/coreference_resolver.py canonical coref resolver (integration for capability_registry.jsonl
# id coreference_resolver_match_or_allocate_strict_cb_principle_b, atoms 29613/29614/29616/29618/
# 29621) reaches a real consumer outside the module itself. Run directly:
#   python experiments/verify_coreference_resolver_v1.py
"""Consumer + smoke check for hdlab.coreference_resolver.

This file is the deliberate WIRE point in the import graph (tools/integration_health.py /
tools/capability_registry_audit.py classify a hdlab-module as WIRED once it has >=1 real
consumer in experiments/ or hdlab/ -- verification/ is NOT scanned by the import graph, so a
scaffold-free witness alone does not satisfy WIRED). It is NOT itself a scored experiment -- it
has no metrics.json/pre-reg -- it exists so `hdlab.coreference_resolver` is genuinely imported +
exercised from experiments/, proving the capability is reachable, not just referenced in a
docstring. The full correctness witness lives at verification/verify_coreference_resolver.py
(scaffold-free, tracing=False).
"""
from __future__ import annotations

import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.coreference_resolver import (
    bcubed,
    build_mention_stream,
    run_principle_b,
    run_recency_floor,
)


def main() -> int:
    passage = {
        "passage_id": "wire_check",
        "clauses": ["Alice went to the store.", "She bought bread.", "Bob saw her there."],
        "entities": {
            "Alice": [
                {"clause": 0, "mention": "Alice", "role": "agent"},
                {"clause": 1, "mention": "She", "role": "agent"},
                {"clause": 2, "mention": "her", "role": "patient"},
            ],
            "Bob": [{"clause": 2, "mention": "Bob", "role": "agent"}],
        },
    }
    stream = build_mention_stream(passage)
    pred, _actions = run_principle_b(stream)
    f1 = bcubed([(stream, pred)])["f1"]
    floor_f1 = bcubed([(stream, run_recency_floor(stream))])["f1"]
    ok = f1 == 1.0 and floor_f1 < f1
    print(f"[verify] coreference_resolver.run_principle_b B3-F1={f1} recency_floor_f1={floor_f1}")
    print("[verify] OVERALL %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
