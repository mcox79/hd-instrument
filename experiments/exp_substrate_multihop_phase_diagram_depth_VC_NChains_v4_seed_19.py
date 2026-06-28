"""substrate_multihop_phase_diagram_depth_VC_NChains_v4_seed_19

CHUNKED phase-diagram cell (seed=19). Thin wrapper around
experiments._multihop_phase_diagram_v4_base.run_one_seed(seed=19).

V4 fixes (per Skunkworks v3 atomization commit eb7cfc4c; atom 0bfdac9e73a27ed5):
  1. Sweep effective_V_C directly (not nominal V_C); N_PARTITIONS=4 fixed
  2. Empirical p_step bands back-solved from v3 data
  3. sample_gpu_util_safe() no-silent-except (META_RULE_J)
  4. 3 arms: SUBSTRATE_BASELINE / PARTITION_ORACLE / RANDOM_PARTITION

Pre-reg: preregs/2026-06-28_substrate_multihop_phase_diagram_depth_VC_NChains_v4.md
Author: exp_dev 2026-06-28.
"""
from __future__ import annotations

import argparse
import sys
import traceback
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

try:
    from experiments._multihop_phase_diagram_v4_base import run_one_seed
except Exception as e:
    import json
    import os
    import time
    print("IMPORT_CRASH:", e, file=sys.stderr)
    traceback.print_exc()
    env_name = os.environ.get(
        "HDLAB_EXP_NAME",
        "substrate_multihop_phase_diagram_depth_VC_NChains_v4_seed_19")
    out_dir = REPO / "data" / ("exp_" + env_name)
    out_dir.mkdir(parents=True, exist_ok=True)
    sentinel = {
        "anchor_name": "substrate_multihop_phase_diagram_depth_VC_NChains_v4_seed_19",
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

SEED = 19


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
