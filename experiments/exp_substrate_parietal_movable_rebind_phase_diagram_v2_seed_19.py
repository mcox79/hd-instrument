"""substrate_parietal_movable_rebind_phase_diagram_v2_seed_19

CHUNKED phase-diagram cell (seed=19). Thin wrapper around
experiments._parietal_phase_diagram_v2_base.run_one_seed(seed=19).

Pre-reg: preregs/2026-06-28_substrate_parietal_movable_rebind_phase_diagram_v2.md
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
    from experiments._parietal_phase_diagram_v2_base import run_one_seed
except Exception as e:
    import json
    import os
    import time
    print("IMPORT_CRASH:", e, file=sys.stderr)
    traceback.print_exc()
    env_name = os.environ.get(
        "HDLAB_EXP_NAME",
        "substrate_parietal_movable_rebind_phase_diagram_v2_seed_19")
    out_dir = REPO / "data" / ("exp_" + env_name)
    out_dir.mkdir(parents=True, exist_ok=True)
    sentinel = {
        "anchor_name": "substrate_parietal_movable_rebind_phase_diagram_v2_seed_19",
        "verdict": "UNKNOWN",
        "verdict_msg": "IMPORT_CRASH: %s: %s" % (type(e).__name__, str(e)),
        "summary": "IMPORT_CRASH",
        "elapsed_s": 0.0,
        "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "_traceback": traceback.format_exc(),
    }
    (out_dir / "metrics.json").write_text(
        json.dumps(sentinel, indent=2), encoding="utf-8")
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
        return run_one_seed(SEED, smoke=smoke, self_test=bool(args.self_test))
    except Exception as e:
        print("OUTER_CRASH seed=%d: %s" % (SEED, e), file=sys.stderr)
        traceback.print_exc()
        return 4


if __name__ == "__main__":
    sys.exit(main())
