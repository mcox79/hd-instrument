"""substrate_sequence_binding_K_cliff_phase_diagram_full_v2 sibling seed=7.

Stage 1 phase-diagram coverage promotion (MID -> HIGH) for sequence_binding
chain-grade primitive. Sweeps (K, N, Q_noise) over 72 grid points with 3 arms
(SUBSTRATE / RANDOM / SHUFFLE) and 100 queries per point.

DIFFERENCES vs v1:
  - K starts at 20 (cert anchor), not 10
  - Q noise levels {1,2,4} replace tag_density {0.1,0.3,0.5}
  - N_QUERIES_FULL = 100 (drives band precision)
  - Bands SAT/MB/FLOOR per task spec
  - Local-CPU dispatch (laptop idle); numpy primary, torch optional

CHUNKED architecture: one seed per sibling.
Sibling pair: seed_13, seed_19.

PRE-REG: preregs/2026-06-28_substrate_sequence_binding_K_cliff_phase_diagram_full_v2.md
CARDINALITY_OK_FULL: 72 phase points x 3 arms x 100 queries = 21600 records per seed
CARDINALITY_OK_SMOKE: 6 corners x 3 arms x 4 queries = 72 records per seed

ASCII-only.
Author: exp_dev 2026-06-28 (Opus 4.7 1M, agent-spawn) Stage 1 phase-coverage promotion
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

SEED = 13
ANCHOR_NAME = f"substrate_sequence_binding_K_cliff_phase_diagram_full_v2_seed_{SEED}"

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
    f"ANCHOR={ANCHOR_NAME},SEED={SEED},mode={RUN_MODE},"
    f"K=[20,50,100,200,500,1000],N=[2048,4096,8192,16384],"
    f"Q=[1,2,4],arms=[SUBSTRATE,RANDOM,SHUFFLE],"
    f"V_ITEMS=1200,V_POS=1200,n_queries_full=100,n_queries_smoke=4,"
    f"expected_n_full=72,expected_n_smoke=6,"
    f"bands=SAT0.90_MB[0.30,0.70]_FLOOR0.10,"
    f"hardening=L1early+L2perpt+L3outertry+L4importsentinel+CHUNKED_PER_SEED"
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
            "_hardening_marker": "v2_seqbind_Kcliff_phase_diagram_full_chunked",
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
            "_hardening_marker": "v2_seqbind_Kcliff_phase_diagram_full_import_crash",
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

    # Late import so import-crash sentinel catches any issue
    from experiments._seed_checkpoint import (
        resumable_seeds, write_partial_key, aggregate_partials,
    )
    from experiments._substrate_sequence_binding_K_cliff_phase_diagram_full_v2_core import (
        run_one_seed_phase_diagram, aggregate_and_verdict, selftest,
        get_backend_label, K_VALUES, N_VALUES, Q_VALUES,
        N_QUERIES_FULL, N_QUERIES_SMOKE, SMOKE_CORNERS, ARMS,
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
    run_config = {"run_mode": RUN_MODE, "anchor": ANCHOR_NAME}
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
    final["_hardening_marker"] = "v2_seqbind_Kcliff_phase_diagram_full_chunked"
    final["backend"] = backend
    final["seed"] = SEED

    # cardinality_ok: count phase points (NOT records). Records reported separately.
    if SMOKE_MODE:
        expected_pts = len(SMOKE_CORNERS)
        expected_records = expected_pts * 3 * N_QUERIES_SMOKE
    else:
        expected_pts = len(K_VALUES) * len(N_VALUES) * len(Q_VALUES)
        expected_records = expected_pts * 3 * N_QUERIES_FULL
    observed_pts = 0
    observed_records = 0
    for body in per_seed.values():
        for pt in body.get("phase_map", []):
            observed_pts += 1
            observed_records += 3 * pt.get("n_queries", 0)
    final["expected_n_phase_points"] = expected_pts
    final["observed_n_phase_points"] = observed_pts
    final["expected_n_records"] = expected_records
    final["observed_n_records"] = observed_records
    final["cardinality_ok"] = (observed_pts == expected_pts
                                and observed_records == expected_records)

    (out_dir / "metrics.json").write_text(json.dumps(final, indent=2, default=str),
                                          encoding="utf-8")
    print(f"[{ANCHOR_NAME}] DONE: {final['verdict_msg']}", flush=True)
    print(f"[{ANCHOR_NAME}] cardinality pts observed={observed_pts} "
          f"expected={expected_pts} records observed={observed_records} "
          f"expected={expected_records} ok={final['cardinality_ok']}", flush=True)
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
