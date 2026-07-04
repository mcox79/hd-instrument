"""Thin per-seed wrapper (CHUNKED single-seed-per-cell): runs the shared
objective-swap core at seed=13 (matches v3e/v3c's seed_13 for direct
before/after comparability). A runner-death on this process loses only
seed=13, not the sibling seed=7 run.

Core:
  experiments/exp_encoder_objective_swap_kl_rank_v1_core.py
Prereg:
  preregs/2026-07-04_exp_encoder_objective_swap_kl_rank_v1.md

run_tag="seed13" isolates this seed's mining shards + checkpoints + metrics
under data/substrate_concept_encoder_objswap_kl_seed13/.

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
    exp_encoder_objective_swap_kl_rank_v1_core as core,
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
        return core.run_swap("smoke", SEED, "auto", core.v3.N_DIM_DEFAULT,
                             None, run_tag=RUN_TAG)
    run_mode = os.environ.get("HDLAB_RUN_MODE", "self_test")
    if run_mode == "self_test":
        return core.run_self_test()
    if run_mode not in ("smoke", "full"):
        run_mode = "full"
    return core.run_swap(run_mode, SEED, "auto", core.v3.N_DIM_DEFAULT,
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
