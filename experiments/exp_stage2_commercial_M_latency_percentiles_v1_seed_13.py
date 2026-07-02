"""stage2_commercial_M_latency_percentiles_v1 -- seed_13.

Per-query cleanup wall-time (p50/p95/p99) at commercial M scales
{100k, 500k, 1M} on N=8192 across backends {numpy, torch_cpu, torch_cuda}.

Delegates to shared core. CELL-TEMPLATE MANDATORY (see core module).
ASCII-only.
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

from experiments._stage2_commercial_M_latency_percentiles_v1_core import (
    run_seed,
    _write_crash_metrics,
    build_arm_plan,
    run_arm,
)
from experiments._seed_checkpoint import get_output_dir


ANCHOR_NAME = "stage2_commercial_M_latency_percentiles_v1_seed_13"
SEED_THIS_CHUNK = 13


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
        res = run_arm(
            arm_name="SELFTEST_M1000_N256_numpy",
            m_items=1000, n_dim=256, seed=SEED_THIS_CHUNK,
            n_queries=10, warmup_queries=2, backend="numpy",
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
