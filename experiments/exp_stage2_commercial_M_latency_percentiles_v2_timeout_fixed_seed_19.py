"""stage2_commercial_M_latency_percentiles_v2_timeout_fixed -- seed_19.

v2 forks v1 with shared-W + per-arm incremental checkpoint. See core.
ASCII-only. CELL-TEMPLATE MANDATORY.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
except Exception:
    pass

import argparse
import os
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

try:
    import torch  # noqa: F401
except Exception:
    pass

from experiments._stage2_commercial_M_latency_percentiles_v2_timeout_fixed_core import (
    run_seed,
    _write_crash_metrics,
    build_arm_plan,
    build_shared_W_for_M,
    run_arm_with_shared_W,
)
from experiments._seed_checkpoint import get_output_dir


ANCHOR_NAME = "stage2_commercial_M_latency_percentiles_v2_timeout_fixed_seed_19"
SEED_THIS_CHUNK = 19


def main() -> int:
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--self-test", dest="self_test", action="store_true")
    args, _ = ap.parse_known_args()

    if args.self_test:
        smoke_plan = build_arm_plan("smoke")
        assert len(smoke_plan) == 3, \
            f"smoke plan expected 3 arms; got {len(smoke_plan)}"
        full_plan = build_arm_plan("full")
        assert len(full_plan) == 9, \
            f"full plan expected 9 arms; got {len(full_plan)}"
        out_dir = Path(get_output_dir(ANCHOR_NAME + "_selftest"))
        shared_W = build_shared_W_for_M(
            seed=SEED_THIS_CHUNK, m_items=1000, n_dim=256,
            n_queries=10, log_prefix="[self-test] ",
        )
        res = run_arm_with_shared_W(
            arm_name="SELFTEST_M1000_N256_numpy",
            m_items=1000, n_dim=256, backend="numpy",
            shared_W=shared_W, n_queries=10, warmup_queries=2,
            out_dir=out_dir, log_prefix="[self-test] ",
        )
        assert res["arm_status"] == "OK", f"self-test arm failed: {res}"
        print(f"[self-test] arm p50={res['p50_s']*1e6:.2f}us OK", flush=True)
        return 0

    run_mode = ("smoke" if args.smoke
                else os.environ.get("HDLAB_RUN_MODE", "full").lower())

    output_dir = get_output_dir(ANCHOR_NAME)
    try:
        return run_seed(SEED_THIS_CHUNK, ANCHOR_NAME, run_mode)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(str(output_dir), ANCHOR_NAME, e)
        raise


if __name__ == "__main__":
    sys.exit(main())
