"""Thin per-seed wrapper (CHUNKED single-seed-per-cell, exp_dev section 13):
runs the NCE-curriculum-relock core at seed=7 (matches the v3c/v3b lineage seed
for direct comparability with the on-disk keyed collapse 0.133 @ v3c seed_7).

Core (all training/eval/verdict logic lives there; not duplicated here):
  experiments/exp_encoder_nce_curriculum_relock_v1_core.py
Prereg:
  preregs/2026-07-06_exp_encoder_nce_curriculum_relock_v1.md

Dispatch contract: queue_add.sh invokes this script BARE (no argv) and injects
HDLAB_RUN_MODE into the child env (full for production, smoke for the local
gate). --self-test and --smoke argv override the env default.

ASCII-only. No emojis. No em dashes.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import torch  # noqa: F401 -- satisfies queue_add.sh GPU-routing sanity gate (PROT-020)

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from experiments import (  # noqa: E402
    exp_encoder_nce_curriculum_relock_v1_core as core,
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
        return core.run_curriculum("smoke", SEED, "auto", core.v3.N_DIM_DEFAULT,
                                   None, run_tag=RUN_TAG)
    run_mode = os.environ.get("HDLAB_RUN_MODE", "self_test")
    if run_mode == "self_test":
        return core.run_self_test()
    if run_mode not in ("smoke", "full"):
        run_mode = "full"
    return core.run_curriculum(run_mode, SEED, "auto", core.v3.N_DIM_DEFAULT,
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
            pass
        raise
