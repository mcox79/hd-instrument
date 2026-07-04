"""Thin per-seed wrapper (CHUNKED single-seed-per-cell): runs the shared v6
K256-plateau-followup core at seed=7 (matches the whole lineage's primary
seed; also matches the v5 seed7 landing this cell's COSINE arm reproduces
as a Gate-D positive control).

Core: experiments/exp_encoder_v6_k256_plateau_followup_v1_core.py
Prereg: preregs/2026-07-04_exp_encoder_v6_k256_plateau_followup_v1.md

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
    exp_encoder_v6_k256_plateau_followup_v1_core as core,
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
        return core.run_k256_plateau("smoke", SEED, "auto", core.v3.N_DIM_DEFAULT,
                                     None, run_tag=RUN_TAG)
    run_mode = os.environ.get("HDLAB_RUN_MODE", "self_test")
    if run_mode == "self_test":
        return core.run_self_test()
    if run_mode not in ("smoke", "full"):
        run_mode = "full"
    return core.run_k256_plateau(run_mode, SEED, "auto", core.v3.N_DIM_DEFAULT,
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
