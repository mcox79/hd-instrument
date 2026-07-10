"""Thin per-seed wrapper (CHUNKED single-seed-per-cell): structure-aware encoder
sharpness (M3/M5 diagnostic + downstream held-out reasoning) for seed=13. A
runner-death on this process loses only seed=13.

Core:
  experiments/exp_encoder_structure_aware_sharpness_v1_core.py
Prereg:
  preregs/2026-07-09_exp_encoder_structure_aware_sharpness_v1.md

The explicit sibling imports below (noqa) force queue_add.sh Pattern-6
import-parse to RE-SCP the transitively-required cores with this dispatch, so the
remote never runs against a stale sibling (dep-parity; SCRIPT_PRECONDITION_
VIOLATION prevention). Pattern-6 parses only the WRAPPER's DIRECT imports.

Dispatch contract: queue_add.sh invokes this BARE (no argv), sets HDLAB_EXP_NAME
to the queued name, and injects HDLAB_RUN_MODE=full; this wrapper aliases full ->
core.run('full', SEED). device default auto -> cuda on the GPU box.

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

from experiments import exp_encoder_structure_aware_sharpness_v1_core as core  # noqa: E402
# Force Pattern-6 re-SCP of transitively-imported sibling cores (dep parity).
from experiments import exp_teacher_free_relational_encoder_cn_subgraph_v1  # noqa: E402,F401
from experiments import exp_grounding_snowball_transitive_inheritance_v1  # noqa: E402,F401
from experiments import exp_grounding_binding_structured_encoder_multihop_v1  # noqa: E402,F401
from experiments import exp_grounding_multihop_perhop_cleanup_gate_v1  # noqa: E402,F401

SEED = 13
RUN_TAG = "seed13"


def main() -> int:
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except (AttributeError, ValueError):
        pass
    out_dir = core.get_output_dir("%s_%s" % (core.ANCHOR_NAME, RUN_TAG))
    try:
        if "--self-test" in sys.argv:
            return core.run_self_test("auto")
        if "--smoke" in sys.argv:
            return core.run("smoke", SEED, "auto", run_tag=RUN_TAG)
        run_mode = os.environ.get("HDLAB_RUN_MODE", "self_test")
        if run_mode == "self_test":
            return core.run_self_test("auto")
        if run_mode not in ("smoke", "full"):
            run_mode = "full"
        return core.run(run_mode, SEED, "auto", run_tag=RUN_TAG)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as exc:  # NOT BaseException; preserves SystemExit / KeyboardInterrupt
        core._write_crash_metrics(out_dir, exc)
        raise


if __name__ == "__main__":
    sys.exit(main())
