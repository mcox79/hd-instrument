# PRESERVE_ENV_VARS: HDLAB_QUEUE
"""substrate_task_vector_K_cliff_phase_diagram_v2 sibling seed=7.

v2 REVISION (2026-06-28): Fixes v1 K_cliff metric artifact (low-K cue degeneracy
mis-classified as high-K saturation cliff). See core docstring for details.

CHUNKED architecture: one seed per sibling file.
Sibling pair: seed_13, seed_19.

ARMS: TASK_VECTOR / RANDOM_VECTOR / ORACLE (3 per phase-point)
SWEEP: K in {1,3,5,10,20,50,100,200} x V in {10,20,50} x ov in {0.0,0.3,0.6} = 72 pts
N_DIM=8192. V_ENTS_POOL=200.

PRE-REG: preregs/2026-06-28_substrate_task_vector_K_cliff_phase_diagram_v2.md
CARDINALITY_OK_FULL: 2160 records per seed (72 pts x 3 arms x 10 queries)
CARDINALITY_OK_SMOKE: 36 records per seed (6 corners x 3 arms x 2 queries)

ASCII-only.
Author: exp_dev 2026-06-28 (Opus 4.7 1M, agent-spawn) v2 artifact-fix
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import json
import os
import time
import traceback
from pathlib import Path
from typing import Any, Dict

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    resumable_seeds, write_partial_key, aggregate_partials,
)

SEED = 7
ANCHOR_NAME = f"substrate_task_vector_K_cliff_phase_diagram_v2_seed_{SEED}"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _NAME_SAYS_SMOKE)
            else ("selftest" if _ARGS.self_test
                  else os.environ.get("HDLAB_RUN_MODE", "full").lower()))
SELF_TEST_MODE = bool(_ARGS.self_test)
SMOKE_MODE = (RUN_MODE == "smoke")

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},N=8192,SEED={SEED},mode={RUN_MODE},"
    f"K=[1,3,5,10,20,50,100,200],V=[10,20,50],ov=[0.0,0.3,0.6],"
    f"V_ENTS_POOL=200,"
    f"arms=[TASK_VECTOR,RANDOM_VECTOR,ORACLE],"
    f"expected_n_full=2160,expected_n_smoke=180,"
    f"v2_metric=monotonic_decay_from_saturation,"
    f"hardening=L1early+L2perarm+L3outertry+L4importsentinel+CHUNKED_PER_SEED"
)

_RESULTS_HOLDER: Dict[str, Any] = {"started_at": time.time()}


def _write_minimal_metrics(out_dir: Path, verdict: str, verdict_msg: str,
                            extra: Dict[str, Any] = None) -> None:
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        m = {
            "anchor_name": ANCHOR_NAME,
            "verdict": verdict,
            "verdict_msg": verdict_msg,
            "summary": verdict_msg,
            "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 2),
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "run_mode": RUN_MODE,
            "config_version": CONFIG_VERSION,
            "_hardening_marker": "v2_taskvec_Kcliff_phase_diagram_chunked",
        }
        if extra:
            m.update(extra)
        (out_dir / "metrics.json").write_text(
            json.dumps(m, indent=2, default=str), encoding="utf-8")
    except Exception as e:
        print(f"[_write_minimal_metrics] FAIL: {e}", file=sys.stderr, flush=True)


def _write_import_crash_sentinel(exc: BaseException) -> None:
    try:
        env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
        out_dir = REPO / "data" / ("exp_" + env_name)
        out_dir.mkdir(parents=True, exist_ok=True)
        s = {
            "anchor_name": ANCHOR_NAME,
            "verdict": "UNKNOWN",
            "verdict_msg": f"IMPORT_CRASH: {type(exc).__name__}: {exc}",
            "summary": f"IMPORT_CRASH: {type(exc).__name__}: {exc}",
            "elapsed_s": 0.0,
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "_traceback": traceback.format_exc(),
            "_hardening_marker": "v2_taskvec_Kcliff_phase_diagram_import_crash",
        }
        (out_dir / "metrics.json").write_text(json.dumps(s, indent=2),
                                              encoding="utf-8")
        (out_dir / "import_crash.json").write_text(json.dumps(s, indent=2),
                                                   encoding="utf-8")
    except Exception as e:
        print(f"[_write_import_crash_sentinel] FAIL: {e}", file=sys.stderr, flush=True)


def main() -> int:
    _RESULTS_HOLDER["started_at"] = time.time()
    env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    out_dir = REPO / "data" / ("exp_" + env_name)
    out_dir.mkdir(parents=True, exist_ok=True)

    _write_minimal_metrics(out_dir, "STARTED",
                           f"STARTED: pid={os.getpid()} mode={RUN_MODE} seed={SEED}",
                           extra={"_phase": "init"})

    from experiments._substrate_task_vector_K_cliff_phase_diagram_v2_core import (
        run_one_seed_phase_diagram, aggregate_and_verdict, selftest,
        get_backend_label, K_VALUES, N_TASKS_VALUES, OVERLAP_VALUES,
        N_QUERIES_FULL, N_QUERIES_SMOKE, SMOKE_CORNERS, ARMS,
        smoke_discriminator_check,
    )

    backend = get_backend_label()
    print(f"[{ANCHOR_NAME}] mode={RUN_MODE} seed={SEED} backend={backend}", flush=True)

    if SELF_TEST_MODE:
        try:
            ok, msg = selftest(SEED)
            verdict = "SELFTEST_OK" if ok else "SELFTEST_FAIL"
            _write_minimal_metrics(out_dir, verdict, msg,
                                   extra={"_phase": "selftest_done",
                                          "backend": backend})
            print(f"[selftest] {verdict}: {msg}", flush=True)
            return 0 if ok else 1
        except Exception as e:
            _write_minimal_metrics(out_dir, "SELFTEST_FAIL",
                                   f"SELFTEST_FAIL: {e}",
                                   extra={"_traceback": traceback.format_exc()})
            print(f"[selftest] FAIL: {e}", file=sys.stderr, flush=True)
            return 1

    # SMOKE or FULL
    seeds_list = [SEED]
    run_config = {"N": 8192, "run_mode": RUN_MODE, "anchor": ANCHOR_NAME}
    done, remaining = resumable_seeds(seeds_list, out_dir, run_config=run_config)
    print(f"[ckpt] {len(done)}/{len(seeds_list)} done; running {remaining}", flush=True)

    for seed in remaining:
        _write_minimal_metrics(out_dir, "RUNNING",
                               f"RUNNING: seed={seed} mode={RUN_MODE}",
                               extra={"_phase": "seed_running",
                                      "_current_seed": seed,
                                      "backend": backend})
        t0 = time.time()
        result = run_one_seed_phase_diagram(seed, run_mode=RUN_MODE,
                                             smoke_corners=SMOKE_MODE)
        result["N"] = result["N_DIM"]
        result["anchor_name"] = ANCHOR_NAME
        result["config_version"] = CONFIG_VERSION
        write_partial_key(out_dir, seed, result)
        print(f"[seed={seed}] complete in {time.time()-t0:.1f}s "
              f"({result['n_phase_points']} pts x {result['n_queries_per_point']} q)",
              flush=True)

    per_seed = aggregate_partials(out_dir, seeds_list, run_config=run_config)
    final = aggregate_and_verdict(per_seed, run_mode=RUN_MODE)
    final["anchor_name"] = ANCHOR_NAME
    final["elapsed_s"] = round(time.time() - _RESULTS_HOLDER["started_at"], 2)
    final["ts_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    final["pid"] = os.getpid()
    final["run_mode"] = RUN_MODE
    final["config_version"] = CONFIG_VERSION
    final["_hardening_marker"] = "v2_taskvec_Kcliff_phase_diagram_chunked"
    final["backend"] = backend
    final["seed"] = SEED

    # cardinality_ok
    if SMOKE_MODE:
        expected_n = len(SMOKE_CORNERS) * 3 * N_QUERIES_SMOKE   # 6 corners x 3 arms x 2 queries
    else:
        expected_n = len(K_VALUES) * len(N_TASKS_VALUES) * len(OVERLAP_VALUES) * 3 * N_QUERIES_FULL
    observed_n = 0
    for body in per_seed.values():
        for pt in body.get("phase_map", []):
            observed_n += 3 * pt.get("n_queries", 0)
    final["expected_n"] = expected_n
    final["observed_n"] = observed_n
    final["cardinality_ok"] = (observed_n == expected_n)

    # Smoke discriminator-survives-scale check
    if SMOKE_MODE:
        all_smoke_pts = []
        for body in per_seed.values():
            all_smoke_pts.extend(body.get("phase_map", []))
        disc_ok, disc_msg = smoke_discriminator_check(all_smoke_pts)
        final["smoke_discriminator_fired"] = disc_ok
        final["smoke_discriminator_msg"] = disc_msg
        if not disc_ok:
            # OVERRIDE verdict: smoke discriminator failed = BLOCK full dispatch
            final["verdict"] = "HARD_FAIL"
            final["verdict_msg"] = (f"SMOKE_DISCRIMINATOR_FAILED | {disc_msg} | "
                                    f"original_aggregate: {final.get('verdict_msg', '')}")
            final["summary"] = final["verdict_msg"]

    (out_dir / "metrics.json").write_text(json.dumps(final, indent=2, default=str),
                                          encoding="utf-8")
    print(f"[{ANCHOR_NAME}] DONE: {final['verdict_msg']}", flush=True)
    print(f"[{ANCHOR_NAME}] cardinality observed={observed_n} expected={expected_n} ok={final['cardinality_ok']}",
          flush=True)
    return 0


if __name__ == "__main__":
    try:
        rc = main()
    except SystemExit:
        raise
    except BaseException as e:
        _write_import_crash_sentinel(e)
        print(f"[main] OUTER_EXCEPTION: {e}", file=sys.stderr, flush=True)
        traceback.print_exc()
        rc = 1
    sys.exit(rc)
