"""Thin per-seed wrapper (CHUNKED single-seed-per-cell per exp_dev canonical
instruction file section 13): runs the shared carry-through core at seed=23.
The production runner invokes the queued script BARE (no argv) and injects only
HDLAB_EXP_NAME + HDLAB_RUN_MODE=full, so the core's own --seed argparse can
never receive a distinct seed. This wrapper hard-codes SEED=23 and forwards to
the core's run_carrythrough entry fn. A runner-death on this process loses only
seed=23, not the sibling seed runs (..._seed_7.py / _seed_13.py / _seed_29.py /
_seed_31.py).

Core (all training/eval/verdict logic lives here; not duplicated):
  experiments/exp_encoder_step2step3_inbatch_rkd_shipmetric_carrythrough_v1_core.py
Prereg:
  preregs/2026-07-05_exp_encoder_step2step3_inbatch_rkd_shipmetric_carrythrough_v1.md

Isolation note: the core's run_carrythrough(run_mode, seed, device_arg, n_dim,
teacher_cache_arg) takes NO run_tag/tag parameter, so no run_tag artifact-dir
isolation is used here. Per-seed metrics.json isolation is provided entirely by
the runner setting HDLAB_EXP_NAME to this queue entry's own name (see
experiments/_seed_checkpoint.get_output_dir). The core's intermediate artifact
dir (data/substrate_concept_encoder_carrythrough_v1{_smoke}_seed<SEED>/: mining
shards + training checkpoints + E_concept.pt) is SEED-NAMESPACED (fix
2026-07-05): each seed gets its own clean dir so a later seed never finds a
PRIOR seed's leftover _ckpt_INBATCH.pt and enters v3c's cross-seed resume branch
(that branch's gen.set_state hits a cuda-moved gen_state -> TypeError which v3c's
resume except clause does not catch -> ~0.0s crash on every seed after the
first). Same-seed resume (runner death then re-dispatch) is preserved.

Dispatch contract: the runner invokes this script BARE (no argv) and injects
HDLAB_RUN_MODE=full into the child env for production runs. This wrapper's
terminal tier IS literally "full" (no alias needed). The queue gate runs
--self-test on remote before dispatch; that path routes to core.run_self_test.

ASCII-only. No emojis. No em dashes.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import torch  # noqa: F401 -- satisfies queue_add.sh's GPU-routing sanity gate
              # (grep for 'import torch'/PROT-020); actual torch use lives in
              # the imported core module, this wrapper only forwards to it.

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from experiments import (  # noqa: E402
    exp_encoder_step2step3_inbatch_rkd_shipmetric_carrythrough_v1_core
    as core,
)

SEED = 23


def main() -> int:
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except (AttributeError, ValueError):
        pass
    # CLI flags take precedence over the HDLAB_RUN_MODE env default (both
    # queue_add.py's --self-test gate call and a bare `--smoke` local
    # invocation leave HDLAB_RUN_MODE unset, which defaults to "self_test" --
    # checking argv FIRST avoids silently running self-test when --smoke was
    # explicitly requested).
    if "--self-test" in sys.argv:
        return core.run_self_test()
    if "--smoke" in sys.argv:
        return core.run_carrythrough("smoke", SEED, "auto",
                                     core.v3.N_DIM_DEFAULT, None)
    run_mode = os.environ.get("HDLAB_RUN_MODE", "self_test")
    if run_mode == "self_test":
        return core.run_self_test()
    if run_mode not in ("smoke", "full"):
        run_mode = "full"
    return core.run_carrythrough(run_mode, SEED, "auto",
                                 core.v3.N_DIM_DEFAULT, None)


if __name__ == "__main__":
    _fallback_out = core.get_output_dir(core.ANCHOR_NAME)
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
