"""Thin per-seed wrapper (CHUNKED single-seed-per-cell): runs the v11 Sparse-GSBC
graded-code cell for seed=13. A runner-death on this process loses only seed=13,
not the sibling seed=7 run.

Core:
  experiments/exp_encoder_v11_gsbc_graded_sparse_v1_core.py
Prereg:
  preregs/2026-07-04_exp_encoder_v11_gsbc_graded_sparse_v1.md

The explicit v3 sibling-core import below (noqa; the core imports it
transitively) forces queue_add.sh Pattern-6 import-parse to RE-SCP that core with
this dispatch, so the remote never runs against a stale sibling core (dep-parity
guard; SCRIPT_PRECONDITION_VIOLATION prevention).

run_tag="seed13" isolates this seed's checkpoints + metrics under
data/substrate_concept_encoder_v11_gsbc_seed13/ and the seed-suffixed dir.

Dispatch contract: queue_add.sh invokes this BARE (no argv) and injects
HDLAB_RUN_MODE=full; this wrapper aliases full -> the core's FULL tier.

ASCII-only. No emojis. No em dashes.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import torch  # noqa: F401 -- satisfies queue_add.sh's GPU-routing sanity gate

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from experiments import (  # noqa: E402
    exp_encoder_v11_gsbc_graded_sparse_v1_core as core,
)
# Force Pattern-6 re-SCP of the transitively-imported sibling core (dep parity).
from experiments import (  # noqa: E402,F401
    exp_encoder_migration_step1b_v3_global_objective_landmark_rkd_concept_encoder_v1_core,  # noqa: F401
)

SEED = 13
RUN_TAG = "seed13"


def main() -> int:
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except (AttributeError, ValueError):
        pass
    out_dir = core.get_output_dir(f"{core.ANCHOR_NAME}_{RUN_TAG}")
    try:
        if "--self-test" in sys.argv:
            return core.run_self_test()
        if "--smoke" in sys.argv:
            return core.run_gsbc_sweep("smoke", SEED, "auto", core.N_DIM,
                                       None, run_tag=RUN_TAG)
        run_mode = os.environ.get("HDLAB_RUN_MODE", "self_test")
        if run_mode == "self_test":
            return core.run_self_test()
        if run_mode not in ("smoke", "full"):
            run_mode = "full"
        return core.run_gsbc_sweep(run_mode, SEED, "auto", core.N_DIM,
                                   None, run_tag=RUN_TAG)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as exc:  # NOT BaseException; preserves SystemExit/KeyboardInterrupt
        core._write_crash_metrics(out_dir, exc)
        raise


if __name__ == "__main__":
    sys.exit(main())
