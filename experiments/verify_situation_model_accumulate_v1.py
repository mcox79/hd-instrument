# WIRING VERIFICATION, not a scored exp_ cell (no pre-reg/queue dispatch needed): proves the
# hdlab/situation_model_accumulate.py AccumulateRegister organ (integration for capability_
# registry.jsonl id situation_model_accumulate_register_organ, atom 29609) reaches a real
# consumer outside the module itself. Run directly:
#   python experiments/verify_situation_model_accumulate_v1.py
"""Consumer + smoke check for hdlab.situation_model_accumulate.AccumulateRegister.

This file is the deliberate WIRE point in the import graph (tools/integration_health.py /
tools/capability_registry_audit.py classify a hdlab-module as WIRED once it has >=1 real
consumer in experiments/ or hdlab/). It is NOT itself a scored experiment -- it has no
metrics.json/pre-reg -- it exists so `hdlab.situation_model_accumulate` is genuinely
imported + exercised from experiments/, proving the capability is reachable, not just
referenced in a docstring. The full correctness witness lives at
verification/verify_situation_model_accumulate.py (scaffold-free, tracing=False).
"""
from __future__ import annotations

import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import torch

from hdlab.situation_model_accumulate import AccumulateRegister

ROLE_VOCAB = ["agent", "patient", "theme", "recipient", "addressee", "speaker"]


def main() -> int:
    gen = torch.Generator().manual_seed(0)
    reg = AccumulateRegister(ROLE_VOCAB, d=1024, generator=gen, max_event_slots=8, overwrite=False)
    reg.add_event("e1", "agent", 0)
    reg.add_event("e1", "patient", 1)
    pred0, _ = reg.decode("e1", 0)
    pred1, _ = reg.decode("e1", 1)
    ok = pred0 == "agent" and pred1 == "patient"
    print(f"[verify] AccumulateRegister multi-event decode OK={ok} pred=({pred0}, {pred1})")
    print("[verify] OVERALL %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
