"""substrate_multihop_phase_diagram_depth_VC_NChains_v5_seed_13

CHUNKED phase-diagram cell (seed=13). Thin wrapper around
experiments._multihop_phase_diagram_v5_base.run_one_seed(seed=13).

V5 mechanism-class diversion (per v4 3/3 HARD_FAIL diagnosis):
  - sweep STORAGE_DENSITY not effective_V_C
  - 3 arms = HEBBIAN_W / DIRECT_ATTENTION / CHANCE
  - primary discriminator = Pareto-split on (top1_recall, wall_s)

Pre-reg: preregs/2026-06-29_substrate_multihop_phase_diagram_depth_VC_NChains_v5.md
Author: exp_dev 2026-06-29.
"""
from __future__ import annotations

import argparse
import sys
import traceback
from pathlib import Path

import torch  # noqa: F401  PROT-020 routing-gate

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

try:
    from experiments._multihop_phase_diagram_v5_base import run_one_seed
except Exception as e:
    import json
    import os
    import time
    print("IMPORT_CRASH:", e, file=sys.stderr)
    traceback.print_exc()
    env_name = os.environ.get(
        "HDLAB_EXP_NAME",
        "substrate_multihop_phase_diagram_depth_VC_NChains_v5_seed_13")
    out_dir = REPO / "data" / ("exp_" + env_name)
    out_dir.mkdir(parents=True, exist_ok=True)
    sentinel = {
        "anchor_name": "substrate_multihop_phase_diagram_depth_VC_NChains_v5_seed_13",
        "verdict": "UNKNOWN",
        "verdict_msg": "IMPORT_CRASH: %s: %s" % (type(e).__name__, str(e)),
        "summary": "IMPORT_CRASH",
        "elapsed_s": 0.0,
        "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "_traceback": traceback.format_exc(),
    }
    (out_dir / "metrics.json").write_text(json.dumps(sentinel, indent=2),
                                           encoding="utf-8")
    sys.exit(3)

SEED = 13


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    args, _ = ap.parse_known_args()
    import os
    env_name = os.environ.get("HDLAB_EXP_NAME", "")
    smoke = bool(args.smoke or ("_smoke" in env_name.lower()))
    try:
        return run_one_seed(SEED, smoke=smoke,
                              self_test=bool(args.self_test))
    except Exception as e:
        print("OUTER_CRASH seed=%d: %s" % (SEED, e), file=sys.stderr)
        traceback.print_exc()
        return 4


if __name__ == "__main__":
    sys.exit(main())
