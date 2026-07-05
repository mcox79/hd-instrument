"""Thin per-seed wrapper (CHUNKED single-seed-per-cell per exp_dev canonical
instruction file section 13): runs the shared v9 minimum-density-PIN core at
seed=7 (matches the whole v3/v3c/v3e/v4/v5/v6/v7/v8 lineage's primary seed for
direct comparability).

Core (all training/eval/verdict logic lives here; not duplicated):
  experiments/exp_encoder_v9_k455_mindensity_paired_v1_core.py
Prereg:
  preregs/2026-07-04_exp_encoder_v9_k455_mindensity_paired_v1.md

The explicit v3 + v3c sibling-core imports below (noqa; the core imports them
transitively) force queue_add.sh Pattern-6 import-parse to RE-SCP those cores
with this dispatch, so the remote never runs against a stale sibling core
(dep-parity guard; SCRIPT_PRECONDITION_VIOLATION prevention).

run_tag="seed7" isolates this seed's mining shards + training checkpoints
under a distinct artifact directory so it never collides with seed=13's
artifacts even though both wrappers import the SAME core module.

Dispatch contract: queue_add.sh invokes this script BARE (no argv) and
injects HDLAB_RUN_MODE=full into the child env for production runs.

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
    exp_encoder_v9_k455_mindensity_paired_v1_core as core,
)
# Force Pattern-6 re-SCP of the transitively-imported sibling cores (dep parity).
from experiments import (  # noqa: E402,F401
    exp_encoder_migration_step1b_v3_global_objective_landmark_rkd_concept_encoder_v1_core,  # noqa: F401
)
from experiments import (  # noqa: E402,F401
    exp_encoder_migration_step1b_v3c_full_paired_rkd_only_dense_recovery_v1_core,  # noqa: F401
)

SEED = 7
RUN_TAG = "seed7"


def main() -> int:
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except (AttributeError, ValueError):
        pass
    if "--self-test" in sys.argv:
        return core.run_self_test()
    if "--smoke" in sys.argv:
        return core.run_mindensity("smoke", SEED, "auto", None, run_tag=RUN_TAG)
    run_mode = os.environ.get("HDLAB_RUN_MODE", "self_test")
    if run_mode == "self_test":
        return core.run_self_test()
    if run_mode not in ("smoke", "full"):
        run_mode = "full"
    return core.run_mindensity(run_mode, SEED, "auto", None, run_tag=RUN_TAG)


if __name__ == "__main__":
    _fallback_out = core.get_output_dir(f"{core.ANCHOR_NAME}_{RUN_TAG}")
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as exc:  # NOT BaseException per META_RULE section 8
        try:
            core._write_crash_metrics(_fallback_out, exc)
        except Exception:
            pass  # crash-writer failure is not fatal
        raise
