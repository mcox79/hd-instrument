"""Thin per-seed wrapper (CHUNKED single-seed-per-cell): GSBC graded-code
retrieval DENSITY SWEEP (finer-resolution continuation of marginpush) for
seed=7. A runner-death on this process loses only seed=19.

Finer density grid m in {3,4,5,6,7,8,10,12} (set in the shared core's
GRADED_M_SWEEP) to LOCATE the retrieval peak on the density axis + map the
cliff. Machinery is IDENTICAL to marginpush (m is already a first-class param
of v11._train_student_v11 / _gsbc_code_from_z); this is a PARAMETER CHANGE, not
new machinery.

Core:
  experiments/exp_encoder_gsbc_gradedcode_marginpush_v1_core.py
Prereg:
  preregs/2026-07-07_exp_encoder_gsbc_gradedcode_densitysweep_v1.md

run_tag="seed19_v050k" isolates this run's metrics under
data/exp_encoder_gsbc_gradedcode_marginpush_v1_seed19_v050k/, so the landed
3-point marginpush metrics at data/..._seed19/ are NOT clobbered.

The explicit sibling-core imports below (noqa) force queue_add.sh Pattern-6
import-parse to RE-SCP those cores with this dispatch (dep-parity guard;
SCRIPT_PRECONDITION_VIOLATION prevention). Pattern-6 parses only the WRAPPER's
DIRECT imports (non-transitive), so all four cores must be named here.

Dispatch contract: queue_add.sh invokes this BARE (no argv) and injects
HDLAB_RUN_MODE=full; this wrapper aliases full -> the core's FULL tier; device
default auto -> cuda on the GPU box.

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
    exp_encoder_gsbc_gradedcode_marginpush_v1_core as core,
)
# Force Pattern-6 re-SCP of the transitively-imported sibling cores (dep parity).
from experiments import (  # noqa: E402,F401
    exp_encoder_gsbc_gradedcode_retrieval_v1_core,  # noqa: F401 (base)
)
from experiments import (  # noqa: E402,F401
    exp_encoder_v11_gsbc_graded_sparse_v1_core,  # noqa: F401
)
from experiments import (  # noqa: E402,F401
    exp_encoder_migration_step1b_v3_global_objective_landmark_rkd_concept_encoder_v1_core,  # noqa: F401
)

SEED = 19
RUN_TAG = "seed19_v050k"
V_CAP = 50000  # 50K corpus subsample (density x SCALE trajectory rung)


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
            return core.run_marginpush("smoke", SEED, "auto",
                                       core.v3.N_DIM_DEFAULT, None, run_tag=RUN_TAG,
                                       v_cap=V_CAP)
        run_mode = os.environ.get("HDLAB_RUN_MODE", "self_test")
        if run_mode == "self_test":
            return core.run_self_test()
        if run_mode not in ("smoke", "full"):
            run_mode = "full"
        return core.run_marginpush(run_mode, SEED, "auto", core.v3.N_DIM_DEFAULT,
                                   None, run_tag=RUN_TAG, v_cap=V_CAP)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as exc:  # NOT BaseException; preserves SystemExit/KeyboardInterrupt
        core.base._write_crash_metrics(out_dir, exc)
        raise


if __name__ == "__main__":
    sys.exit(main())
