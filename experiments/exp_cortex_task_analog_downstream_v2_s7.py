"""exp_cortex_task_analog_downstream_v2_s7 -- seed=7 chunked wrapper.

Per §13 chunked single-seed-per-cell architecture. Sibling wrappers _s13/_s19
authored independently for FULL 3-seed coverage; SMOKE uses this s7 wrapper only.

Prereg: preregs/2026-07-04_exp_cortex_task_analog_downstream_v2.md
Core: experiments/exp_cortex_task_analog_downstream_v2_core.py
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from experiments.exp_cortex_task_analog_downstream_v2_core import (
    ANCHOR_BASE,
    _run_one_seed_wrapper,
    _selftest_basic_pipeline,
)

ANCHOR_NAME = f"{ANCHOR_BASE}_s7"
SEED = 7


def main(argv=None) -> int:
    import argparse
    p = argparse.ArgumentParser(description=ANCHOR_NAME)
    p.add_argument("--run-mode", choices=["smoke", "full", "self_test"],
                   default="smoke")
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args(argv)
    if args.self_test:
        _selftest_basic_pipeline()
        print("SELFTEST_OK", flush=True)
        return 0
    return _run_one_seed_wrapper(SEED, args.run_mode, ANCHOR_NAME)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception:
        raise
