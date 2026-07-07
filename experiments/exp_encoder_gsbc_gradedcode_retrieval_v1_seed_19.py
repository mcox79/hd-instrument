"""Thin per-seed wrapper (CHUNKED single-seed-per-cell): runs the paired
hard-block-STE vs graded-GSBC ship-metric cell for seed=19. A runner-death on
this process loses only seed=19, not the sibling seed=7 / seed=13 runs.

Core:
  experiments/exp_encoder_gsbc_gradedcode_retrieval_v1_core.py
Prereg:
  preregs/2026-07-05_exp_encoder_gsbc_gradedcode_retrieval_v1.md

The explicit v3-core AND v11-core sibling imports below force queue_add.sh
Pattern-6 import-parse to RE-SCP those cores (dep-parity guard). Pattern-6 parses
only the WRAPPER's direct imports (non-transitive), so all three must be named.

run_tag="seed19" isolates this seed's metrics under
data/exp_encoder_gsbc_gradedcode_retrieval_v1_seed19/.

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
    exp_encoder_gsbc_gradedcode_retrieval_v1_core as core,
)
from experiments import (  # noqa: E402,F401
    exp_encoder_v11_gsbc_graded_sparse_v1_core,  # noqa: F401
)
from experiments import (  # noqa: E402,F401
    exp_encoder_migration_step1b_v3_global_objective_landmark_rkd_concept_encoder_v1_core,  # noqa: F401
)

SEED = 19
RUN_TAG = "seed19"


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
            return core.run_paired("smoke", SEED, "auto", core.v3.N_DIM_DEFAULT,
                                   None, run_tag=RUN_TAG)
        run_mode = os.environ.get("HDLAB_RUN_MODE", "self_test")
        if run_mode == "self_test":
            return core.run_self_test()
        if run_mode not in ("smoke", "full"):
            run_mode = "full"
        return core.run_paired(run_mode, SEED, "auto", core.v3.N_DIM_DEFAULT,
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
