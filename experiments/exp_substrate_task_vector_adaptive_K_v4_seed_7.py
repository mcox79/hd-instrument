# PRESERVE_ENV_VARS: HDLAB_QUEUE
"""substrate_task_vector_adaptive_K_v4 sibling seed=7.

v4 REVISION (2026-06-30): mechanism-class diversion from v3.

v3 (2026-06-28) MM_SEED_UNSTABLE: K_cliff differed per seed ([5, 3, 3]).
Skunkworks audit (a65f731f): seed-instability is a substrate-scale stochastic
threshold, NOT a mechanism-class failure. v4 mechanism = let the substrate
SELF-SELECT K per query via attractor (cleanup) convergence (CRP-style).

ARMS (5; arms-must-differ per META_RULE_AF):
  FIXED_K_v3 (K in {3,5,10}) -- baseline reproducer
  ADAPTIVE_THRESH_LOW (tau=0.11; empirically calibrated p25)
  ADAPTIVE_THRESH_MID (tau=0.14; empirically calibrated p50)
  ADAPTIVE_THRESH_HIGH (tau=0.19; empirically calibrated p75)
  RANDOM_K_CONTROL (K_used drawn uniform from {1,3,5,10,20,50,100,150})

CHUNKED architecture: one seed per sibling file.
Sibling pair: seed_13, seed_19. Final cross-seed cv(K_used) aggregation is
post-hoc across the 3 partials.

SWEEP per seed: 3 V x 3 ov = 9 phase points;
  FIXED_K_v3: 3 K x 9 pts x 50 q = 1350 records
  4 other arms: 9 pts x 50 q each = 4 * 450 = 1800 records
  Per-seed cardinality: 3150 records.

SMOKE: 1 corner (V=20, ov=0.3) at full N_DIM=8192, n_q=50, FIXED_K_v3 at K=5
only; 5 arms x 50 queries = 250 records.

DISCRIMINATOR (META_RULE_AC + DISCRIMINATOR-MUST-SURVIVE-SCALE):
  At smoke corner, ADAPTIVE_MID must show std(K_used) > 0.5 AND acc > 0.20.
  Verified all 3 seeds at smoke before dispatch.

PRE-REG: preregs/2026-06-30_substrate_task_vector_adaptive_K_v4.md
CARDINALITY_OK_FULL: 3150 records per seed
CARDINALITY_OK_SMOKE: 250 records per seed (1 corner x 5 arms x 50 queries;
                       FIXED_K_v3 single K at smoke)

ASCII-only.
Author: exp_dev 2026-06-30 (Opus 4.7 1M, agent-spawn) v4 adaptive-K CRP
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
ANCHOR_NAME = f"substrate_task_vector_adaptive_K_v4_seed_{SEED}"

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
    f"V=[10,20,50],ov=[0.0,0.3,0.6],FIXED_K=[3,5,10],"
    f"V_ENTS_POOL=200,n_queries_full=50,"
    f"arms=[FIXED_K_v3,ADAPTIVE_THRESH_LOW,ADAPTIVE_THRESH_MID,ADAPTIVE_THRESH_HIGH,RANDOM_K_CONTROL],"
    f"tau=[0.11,0.14,0.19],ADAPTIVE_K_MAX=150,RANDOM_K_SUPPORT=[1,3,5,10,20,50,100,150],"
    f"expected_n_full=3150,expected_n_smoke=250,"
    f"v4_mechanism=endogenous_K_attractor_convergence_CRP_style,"
    f"v4_calibration=empirical_p25_p50_p75_cleanup_cosine_2026-06-30,"
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
            "_hardening_marker": "v4_taskvec_adaptive_K_chunked",
        }
        if extra:
            m.update(extra)
        tmp = out_dir / "metrics.json.tmp"
        tmp.write_text(json.dumps(m, indent=2, default=str), encoding="utf-8")
        os.replace(str(tmp), str(out_dir / "metrics.json"))
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
            "_hardening_marker": "v4_taskvec_adaptive_K_import_crash",
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

    from experiments._substrate_task_vector_adaptive_K_v4_core import (
        run_one_seed_phase_diagram, aggregate_and_verdict_single_seed, selftest,
        get_backend_label, N_TASKS_VALUES, OVERLAP_VALUES, FIXED_K_VALUES,
        N_QUERIES_FULL, N_QUERIES_SMOKE, ARMS, ADAPTIVE_ARMS,
        smoke_discriminator_check, arms_differ_check,
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
        except SystemExit:
            raise
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
        result = run_one_seed_phase_diagram(seed, run_mode=RUN_MODE,
                                             smoke_corner=SMOKE_MODE)
        result["N"] = result["N_DIM"]
        result["anchor_name"] = ANCHOR_NAME
        result["config_version"] = CONFIG_VERSION
        write_partial_key(out_dir, seed, result)
        print(f"[seed={seed}] complete in {time.time()-t0:.1f}s "
              f"({result['n_phase_points']} pts x {result['n_queries_per_point']} q)",
              flush=True)

    per_seed = aggregate_partials(out_dir, seeds_list, run_config=run_config)
    final = aggregate_and_verdict_single_seed(per_seed, run_mode=RUN_MODE)
    final["anchor_name"] = ANCHOR_NAME
    final["elapsed_s"] = round(time.time() - _RESULTS_HOLDER["started_at"], 2)
    final["ts_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    final["pid"] = os.getpid()
    final["run_mode"] = RUN_MODE
    final["config_version"] = CONFIG_VERSION
    final["_hardening_marker"] = "v4_taskvec_adaptive_K_chunked"
    final["backend"] = backend
    final["seed"] = SEED

    # Cardinality (META_RULE_H): observed = sum across phase points of
    #   FIXED_K(per K count * 1 q) + 4 arms * 1 q  per query slot.
    if SMOKE_MODE:
        # 1 corner * (1 FIXED_K_v3_K + 4 other arms) * N_QUERIES_SMOKE
        expected_n = 1 * (1 + 4) * N_QUERIES_SMOKE  # = 250
    else:
        n_fixed_K = len(FIXED_K_VALUES)
        n_other = 4  # 3 ADAPTIVE + 1 RANDOM_K_CONTROL
        n_pts = len(N_TASKS_VALUES) * len(OVERLAP_VALUES)
        expected_n = n_pts * (n_fixed_K + n_other) * N_QUERIES_FULL  # = 9 * 7 * 50 = 3150
    observed_n = 0
    for body in per_seed.values():
        fixed_K_list = body.get("fixed_K_values", [5] if SMOKE_MODE else list(FIXED_K_VALUES))
        for pt in body.get("phase_map", []):
            nq = pt.get("n_queries", 0)
            for K in fixed_K_list:
                k_key = f"FIXED_K_v3_K{K}_per_query_correct"
                observed_n += len(pt.get(k_key, []))
            for arm in (*ADAPTIVE_ARMS, "RANDOM_K_CONTROL"):
                observed_n += len(pt.get(arm + "_per_query_correct", []))
    final["expected_n"] = expected_n
    final["observed_n"] = observed_n
    final["cardinality_ok"] = (observed_n == expected_n)
    if not final["cardinality_ok"]:
        final["verdict"] = "HARD_FAIL"
        final["verdict_msg"] = (f"CARDINALITY_BREACH: observed={observed_n} "
                                f"expected={expected_n} | "
                                f"original: {final.get('verdict_msg', '')}")
        final["summary"] = final["verdict_msg"]

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
                                    f"original: {final.get('verdict_msg', '')}")
            final["summary"] = final["verdict_msg"]

    # Atomic final write (META_RULE_AH)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(final, indent=2, default=str), encoding="utf-8")
    os.replace(str(tmp), str(out_dir / "metrics.json"))
    print(f"[{ANCHOR_NAME}] DONE: {final['verdict_msg']}", flush=True)
    print(f"[{ANCHOR_NAME}] cardinality observed={observed_n} expected={expected_n} ok={final['cardinality_ok']}",
          flush=True)
    return 0


if __name__ == "__main__":
    try:
        rc = main()
    except SystemExit:
        raise
    except Exception as e:
        _write_import_crash_sentinel(e)
        print(f"[main] OUTER_EXCEPTION: {e}", file=sys.stderr, flush=True)
        traceback.print_exc()
        rc = 1
    sys.exit(rc)
