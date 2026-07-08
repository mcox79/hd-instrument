"""Thin per-seed wrapper (CHUNKED single-seed-per-cell per exp_dev section 13):
runs the shared retrieval-agreement readout-fix diagnostic core at seed=13.

The production runner invokes the queued script BARE (no argv) and injects only
HDLAB_EXP_NAME + HDLAB_RUN_MODE. This wrapper hard-codes SEED and forwards to
core.run_diag. A runner-death on this process loses only seed=13, not siblings.

Core (all logic; not duplicated):
  experiments/exp_encoder_retagree_readout_fix_decouple_peelsic_diag_v1_core.py
Prereg:
  preregs/2026-07-08_exp_encoder_retagree_readout_fix_decouple_peelsic_diag_v1.md

DIAGNOSTIC / MEASUREMENT ONLY: trains (full) / synthesizes (smoke) an encoder in an
isolated artifact dir and writes to its OWN metrics.json. NO re-ingest, NO KB
mutation, NO operational default change.

ASCII-only. No emojis. No em dashes.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import torch  # noqa: F401 -- satisfies queue_add.sh GPU-routing sanity gate

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from experiments import (  # noqa: E402
    exp_encoder_retagree_readout_fix_decouple_peelsic_diag_v1_core as core,
)

SEED = 13


def main() -> int:
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except (AttributeError, ValueError):
        pass
    if "--self-test" in sys.argv:
        return core.run_self_test()
    if "--smoke" in sys.argv:
        return core.run_diag("smoke", SEED, "auto")
    run_mode = os.environ.get("HDLAB_RUN_MODE", "self_test")
    if run_mode == "self_test":
        return core.run_self_test()
    if run_mode not in ("smoke", "full"):
        run_mode = "full"
    return core.run_diag(run_mode, SEED, "auto")


if __name__ == "__main__":
    _fallback_out = core.get_output_dir(core.ANCHOR_NAME)
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as exc:  # NOT BaseException per section 8
        try:
            core._write_crash_metrics(_fallback_out, exc)
        except Exception:
            pass
        raise
