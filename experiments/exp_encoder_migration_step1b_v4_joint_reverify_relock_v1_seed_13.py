"""Thin per-seed wrapper (CHUNKED single-seed-per-cell per exp_dev canonical
instruction file section 13): runs the shared v4 core at seed=13 (matching the
v3c FULL seed=13 checkpoint this cell reloads for both Phase 1 reverify and
Phase 2 relock). A runner-death on this process loses only seed=13, not the
sibling seed=7 run (exp_encoder_migration_step1b_v4_joint_reverify_relock_v1_seed_7.py).

Core (all reverify/relock/eval/verdict logic lives here; not duplicated):
  experiments/exp_encoder_migration_step1b_v4_joint_reverify_relock_v1_core.py
Prereg:
  preregs/2026-07-07_exp_encoder_migration_step1b_v4_joint_reverify_relock_v1.md

run_tag="seed13" resolves the READ-ONLY source checkpoint directory
(data/substrate_concept_encoder_v1b_v3c_full_paired_seed13/, the ALREADY-
LANDED v3c FULL seed=13 run's _ckpt_best_{GLOBAL,INBATCH}.pt) via
v3c._artifact_dir("full", "seed13") -- same convention v3c's own seed_13.py
wrapper used to WRITE those checkpoints. This cell only READS them (Phase 1)
and forks a SEPARATE relock artifact directory for Phase 2's own checkpoints
(data/substrate_concept_encoder_v1b_v4_reverify_relock_seed13/), never
overwriting the v3c source files.

Dispatch contract: queue_add.sh invokes this script BARE (no argv) and
injects HDLAB_RUN_MODE=full into the child env for production runs. This
wrapper's terminal tier IS literally "full" (no alias needed).

ASCII-only. No emojis. No em dashes.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import torch  # noqa: F401 -- satisfies queue_add.sh's GPU-routing sanity gate
              # (grep for 'import torch'/PROT-020); actual torch use lives in
              # the imported core module, this wrapper only forwards to it.

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from experiments import (  # noqa: E402
    exp_encoder_migration_step1b_v4_joint_reverify_relock_v1_core as core,
)

SEED = 13
RUN_TAG = "seed13"


def main() -> int:
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except (AttributeError, ValueError):
        pass
    if "--self-test" in sys.argv:
        return core.run_self_test()
    if "--smoke" in sys.argv:
        return core.run_v4("smoke", SEED, "auto", core.v3.N_DIM_DEFAULT,
                           None, run_tag=RUN_TAG)
    run_mode = os.environ.get("HDLAB_RUN_MODE", "self_test")
    if run_mode == "self_test":
        return core.run_self_test()
    if run_mode not in ("smoke", "full"):
        run_mode = "full"
    return core.run_v4(run_mode, SEED, "auto", core.v3.N_DIM_DEFAULT,
                       None, run_tag=RUN_TAG)


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
