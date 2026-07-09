"""Thin per-seed wrapper (CHUNKED single-seed-per-cell): native encoder measured ON
THE GRAPH TASK (held-out link-prediction Hits@10 vs ConceptNet graph ground truth)
vs BGE + char-trigram; reframe of ret_agree10-vs-BGE. seed=17.
A runner-death on this process loses only seed=17, not the sibling seeds.

Core:
  experiments/exp_encoder_native_graph_task_retrieval_reframe_v1.py
Prereg:
  preregs/2026-07-08_exp_encoder_native_graph_task_retrieval_reframe_v1.md

The explicit native-encoder parent import below (noqa) forces queue_add.sh Pattern-6
import-parse to RE-SCP that parent with this dispatch (dep-parity guard;
SCRIPT_PRECONDITION_VIOLATION prevention). NOTE: the core also imports
hdlab.gsbc_graded_encoder, which is NOT covered by queue_add.sh sibling auto-SCP --
the orchestrator must ensure hdlab/gsbc_graded_encoder.py AND the BGE cache npz are
present on remote before dispatch.

Dispatch contract: queue_add.sh invokes this BARE (no argv) and injects
HDLAB_RUN_MODE=full; this wrapper aliases full -> the core FULL tier for seed 17.

ASCII-only. No emojis. No em dashes.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import torch  # noqa: F401 -- satisfies queue_add.sh GPU-routing sanity gate

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from experiments import (  # noqa: E402
    exp_encoder_native_graph_task_retrieval_reframe_v1 as core,
)
# Force Pattern-6 re-SCP of the transitively-imported native-encoder parent (dep parity).
from experiments import (  # noqa: E402,F401
    exp_teacher_free_relational_encoder_cn_subgraph_v1,  # noqa: F401
)

SEED = 17


def main() -> int:
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except (AttributeError, ValueError):
        pass
    out_dir = core.get_output_dir("%s_seed%d" % (core.ANCHOR_NAME, SEED))
    try:
        if "--self-test" in sys.argv:
            return core.run_self_test()
        if "--smoke" in sys.argv:
            return core.run("smoke", SEED)
        run_mode = os.environ.get("HDLAB_RUN_MODE", "self_test")
        if run_mode == "self_test":
            return core.run_self_test()
        if run_mode not in ("smoke", "full"):
            run_mode = "full"
        return core.run(run_mode, SEED)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as exc:  # NOT BaseException; preserves SystemExit/KeyboardInterrupt
        core._write_crash_metrics(str(out_dir), exc)
        raise


if __name__ == "__main__":
    sys.exit(main())
