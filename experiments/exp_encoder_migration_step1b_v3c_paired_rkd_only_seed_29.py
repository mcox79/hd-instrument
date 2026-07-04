"""Thin per-seed wrapper (CHUNKED single-seed-per-cell): runs the shared v3c
core at seed=29 to extend the in_batch-RKD-only-NCE-off robustness evidence
(seeds 7/13/23; this adds a 4th seed for the best-ckpt-stability audit). A
runner-death on this process loses only seed=29.

Core:
  experiments/exp_encoder_migration_step1b_v3c_full_paired_rkd_only_dense_recovery_v1_core.py
Prereg:
  preregs/2026-07-04_exp_encoder_migration_step1b_v3c_full_paired_rkd_only_dense_recovery_v1.md

run_tag="seed29" isolates this seed's mining shards + checkpoints + metrics
under data/substrate_concept_encoder_v1b_v3c_full_paired_seed29/.

Dispatch contract: queue_add.sh invokes this BARE (no argv) and injects
HDLAB_RUN_MODE=full; this wrapper's terminal tier IS literally "full".

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
    exp_encoder_migration_step1b_v3c_full_paired_rkd_only_dense_recovery_v1_core
    as core,
)

SEED = 29
RUN_TAG = "seed29"


def main() -> int:
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except (AttributeError, ValueError):
        pass
    if "--self-test" in sys.argv:
        return core.run_self_test()
    if "--smoke" in sys.argv:
        return core.run_full_paired("smoke", SEED, "auto", core.v3.N_DIM_DEFAULT,
                                    None, run_tag=RUN_TAG)
    run_mode = os.environ.get("HDLAB_RUN_MODE", "self_test")
    if run_mode == "self_test":
        return core.run_self_test()
    if run_mode not in ("smoke", "full"):
        run_mode = "full"
    return core.run_full_paired(run_mode, SEED, "auto", core.v3.N_DIM_DEFAULT,
                                None, run_tag=RUN_TAG)


if __name__ == "__main__":
    _fallback_out = core.get_output_dir(f"{core.ANCHOR_NAME}_{RUN_TAG}")
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as exc:  # NOT BaseException
        try:
            core._write_crash_metrics(_fallback_out, exc)
        except Exception:
            pass
        raise
