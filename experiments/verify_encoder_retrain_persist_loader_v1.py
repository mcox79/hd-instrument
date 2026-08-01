# WIRING VERIFICATION, not a scored exp_ cell (no pre-reg/queue dispatch needed): proves the
# hdlab/encoder_retrain_persist.py opt-in loader (integration for atom math seq 29596, the
# chain-graded generalizing encoder-lever capability) actually reaches a real consumer, and that
# the improved encoder loads through the standard eb.EncoderExtractor interface. Run directly:
#   python experiments/verify_encoder_retrain_persist_loader_v1.py
"""Consumer + smoke check for the OPT-IN improved-encoder loader (hdlab/encoder_retrain_persist.py).

This file is the deliberate WIRE point in the import graph (tools/integration_health.py /
tools/capability_registry_audit.py classify a hdlab-module as WIRED once it has >=1 real
consumer). It is NOT itself a scored experiment -- it has no metrics.json/pre-reg -- it exists
so `hdlab.encoder_retrain_persist` is genuinely imported+exercised from experiments/, proving the
capability is reachable, not just referenced in a docstring.
"""
from __future__ import annotations

import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.encoder_retrain_persist import CERTIFIED_SEEDS, load_improved_encoder


def main() -> int:
    ok = True
    for seed in CERTIFIED_SEEDS:
        ext = load_improved_encoder(seed=seed)
        good = hasattr(ext, "model") and hasattr(ext, "tok") and int(ext.d) > 0
        print("[verify] seed=%d load_improved_encoder OK=%s d_model=%s" % (seed, good, getattr(ext, "d", None)))
        ok = ok and good
    print("[verify] OVERALL %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
