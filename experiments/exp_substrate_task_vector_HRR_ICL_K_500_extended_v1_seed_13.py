# PRESERVE_ENV_VARS: HDLAB_QUEUE
"""substrate_task_vector_HRR_ICL_K_500_extended_v1 sibling seed=13.

Refined-K probe of TASK_VECTOR HRR ICL K-cliff (Stage 3, M3 concern #4).
Referent: substrate_task_vector_K_extended_v1 (2026-06-30 extended-K
reach with K in {50,100,200,500,1000}). THIS cell refines the K axis by
inserting K=350 and dropping K=1000 to characterize cliff shape more
clearly in K in [100..500].

CHUNKED per-seed architecture. Sibling seeds: 7 / 13 / 19.

ARMS: TASK_VECTOR / RANDOM_VECTOR / ORACLE
SWEEP: K in {50, 200, 500, 1000, 2000} at V=10, ov=0.0 = 5 pts
N_DIM=8192. V_ENTS_POOL=2200. N_QUERIES_FULL=100. N_QUERIES_SMOKE=100.

PRE-REG: preregs/2026-07-01_substrate_task_vector_HRR_ICL_K_500_extended_v1.md
CARDINALITY_OK_FULL: 1500 records per seed (5 pts x 3 arms x 100 q)
CARDINALITY_OK_SMOKE: 300 records per seed (1 pt x 3 arms x 100 q)

ASCII-only.
Author: exp_dev 2026-07-01 (Opus 4.7 1M, agent-spawn) K_500_extended refinement
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

SEED = 13
ANCHOR_NAME = f"substrate_task_vector_HRR_ICL_K_500_extended_v1_seed_{SEED}"

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
    f"K=[50,200,500,1000,2000],V=10,ov=0.0,"
    f"V_ENTS_POOL=2200,n_queries_full=100,n_queries_smoke=100,"
    f"arms=[TASK_VECTOR,RANDOM_VECTOR,ORACLE],"
    f"expected_n_full=1500,expected_n_smoke=300,"
    f"referent=extended_v1_2026-06-30,"
    f"lever=K_axis_refined_add_350_drop_1000,"
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
            "_hardening_marker": "v1_taskvec_K_500_extended_chunked",
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
            "_hardening_marker": "v1_taskvec_K_500_extended_import_crash",
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

    from experiments._substrate_task_vector_HRR_ICL_K_500_extended_v1_core import (
        run_one_seed_K500_extended, aggregate_and_verdict, selftest,
        get_backend_label, K_VALUES, N_QUERIES_FULL, N_QUERIES_SMOKE,
        SMOKE_K, smoke_discriminator_check,
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
        result = run_one_seed_K500_extended(seed, run_mode=RUN_MODE)
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
    final["_hardening_marker"] = "v1_taskvec_K_500_extended_chunked"
    final["backend"] = backend
    final["seed"] = SEED

    if SMOKE_MODE:
        expected_n = 1 * 3 * N_QUERIES_SMOKE
    else:
        expected_n = len(K_VALUES) * 3 * N_QUERIES_FULL
    observed_n = 0
    for body in per_seed.values():
        for pt in body.get("phase_map", []):
            observed_n += 3 * pt.get("n_queries", 0)
    final["expected_n"] = expected_n
    final["observed_n"] = observed_n
    final["cardinality_ok"] = (observed_n == expected_n)

    if SMOKE_MODE:
        all_smoke_pts = []
        for body in per_seed.values():
            all_smoke_pts.extend(body.get("phase_map", []))
        disc_ok, disc_msg = smoke_discriminator_check(all_smoke_pts)
        final["smoke_discriminator_fired"] = disc_ok
        final["smoke_discriminator_msg"] = disc_msg
        if not disc_ok:
            final["verdict"] = "HARD_FAIL"
            final["verdict_msg"] = (f"SMOKE_DISCRIMINATOR_FAILED | {disc_msg} | "
                                    f"original_aggregate: {final.get('verdict_msg', '')}")
            final["summary"] = final["verdict_msg"]

    (out_dir / "metrics.json").write_text(json.dumps(final, indent=2, default=str),
                                          encoding="utf-8")
    print(f"[{ANCHOR_NAME}] DONE: {final['verdict_msg']}", flush=True)
    print(f"[{ANCHOR_NAME}] cardinality observed={observed_n} expected={expected_n} "
          f"ok={final['cardinality_ok']}", flush=True)
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
