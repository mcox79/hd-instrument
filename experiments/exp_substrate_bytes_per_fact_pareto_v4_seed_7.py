"""Bytes-per-fact storage efficiency Pareto v4 M-ULTRA-EXTENDED, seed=7.

v4 vs v3:
  - M sweep extended [1000,4000,10000,40000,80000,160000] (+M=80k, +M=160k;
    dropped interior M=20k to keep 6 M-values at 42 units/seed).
  - N_DIM_DENSE reduced 4096 -> 2048; N_DIM_SPARSE 16384 -> 8192.
    At N=2048, Hopfield capacity ~287; M=160k is 558x overload.
  - v3 landed ceiling_saturation_ratio=0.7143 (META_RULE_Q trip) with N=4096
    and top-M=40k. v4 pushes both axes to force at least 3-4 arms below 0.85
    at top-M so per-arm crack-point ordering becomes visible (MM -> CG lift).

Discriminators (unchanged from v3):
  - Pareto separation within each M (>=1 pair differs by 2x bytes or 0.05 recall)
  - Monotonic recall decay per precision as M grows
  - FP16_range_safe recall >= 0.5 @ M=4000 (RANGE-fix rescues FP16)
  - INT4 recall >= 0.85 @ M=4000 (positive tier)
  - ceiling_saturation_ratio < 0.70 (META_RULE_Q strict; v4 escape target)

CHUNKED: one seed per file. Siblings: seed_13, seed_19.

PROT-020: torch import present; CPU-only regime; route to remote_cpu_queue.
PROT-018: anchor has no _n suffix (grid is precision x M).

ASCII-only.
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

import torch  # PROT-020

from experiments._seed_checkpoint import (
    resumable_seeds, write_partial_key, aggregate_partials,
)

SEED = 7
ANCHOR_NAME = f"substrate_bytes_per_fact_pareto_v4_seed_{SEED}"

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
    f"ANCHOR={ANCHOR_NAME},"
    f"arms=[FP32_DENSE,BFLOAT16_DENSE,FP16_DENSE_RANGE_SAFE,INT8_DENSE,INT4_QUANTIZED,BINARY_DENSE,SPARSE_BIPOLAR_0p05],"
    f"N_DIM_DENSE=2048,N_DIM_SPARSE=8192,"
    f"M_sweep_full=[1000,4000,10000,40000,80000,160000],M_sweep_smoke=[500,2000,8000,20000],"
    f"n_ent_full=5000,n_rel_full=100,query_frac=0.10,"
    f"recall_target_underload=0.85,fp16_range_safe_min=0.5,int4_min=0.85,topK=1,"
    f"SEED={SEED},mode={RUN_MODE},"
    f"discriminator=pareto_sep_per_M+monotone_decay+fp16_range_fix+int4_positive_tier+META_RULE_Q_strict,"
    f"cross_seed_cv_ceiling=0.15,mechanism_hash_distinct_required=True,"
    f"ceiling_saturation_ratio_max=0.70,"
    f"hardening=L1startmarker+L2crashdiag+L3perunitckpt+L4heartbeat+CHUNKED_PER_SEED"
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
            "summary": verdict_msg[:400],
            "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 2),
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "run_mode": RUN_MODE,
            "config_version": CONFIG_VERSION,
            "_hardening_marker": "v4_bytes_per_fact_pareto_M_ultra_extended_N2048_chunked",
        }
        if extra:
            m.update(extra)
        tmp = out_dir / "metrics.json.tmp"
        final = out_dir / "metrics.json"
        tmp.write_text(json.dumps(m, indent=2, default=str), encoding="utf-8")
        os.replace(tmp, final)
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
            "_hardening_marker": "v4_bytes_per_fact_import_crash",
        }
        tmp = out_dir / "metrics.json.tmp"
        final = out_dir / "metrics.json"
        tmp.write_text(json.dumps(s, indent=2), encoding="utf-8")
        os.replace(tmp, final)
        (out_dir / "import_crash.json").write_text(
            json.dumps(s, indent=2), encoding="utf-8")
    except Exception as e:
        print(f"[_write_import_crash_sentinel] FAIL: {e}",
              file=sys.stderr, flush=True)


def main() -> int:
    _RESULTS_HOLDER["started_at"] = time.time()
    env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    out_dir = REPO / "data" / ("exp_" + env_name)
    out_dir.mkdir(parents=True, exist_ok=True)

    _write_minimal_metrics(
        out_dir, "STARTED",
        f"STARTED: pid={os.getpid()} mode={RUN_MODE} seed={SEED}",
        extra={"_phase": "init"},
    )

    from experiments._substrate_bytes_per_fact_pareto_v4_core import (
        run_one_seed_all_units, aggregate_and_verdict, selftest,
        get_backend_label, _get_device, ARMS, FULL_M_SWEEP, SMOKE_M_SWEEP,
    )

    strict_gpu = False
    device = _get_device(strict_gpu=strict_gpu)
    backend = get_backend_label()
    print(f"[{ANCHOR_NAME}] mode={RUN_MODE} seed={SEED} backend={backend} "
          f"device={device}", flush=True)

    if SELF_TEST_MODE:
        try:
            ok, msg = selftest(SEED, device=device)
            verdict = "SELFTEST_OK" if ok else "SELFTEST_FAIL"
            _write_minimal_metrics(
                out_dir, verdict, msg,
                extra={"_phase": "selftest_done", "backend": backend},
            )
            print(f"[selftest] {verdict}: {msg}", flush=True)
            return 0 if ok else 1
        except Exception as e:
            _write_minimal_metrics(
                out_dir, "SELFTEST_FAIL", f"SELFTEST_FAIL: {e}",
                extra={"_traceback": traceback.format_exc()},
            )
            print(f"[selftest] FAIL: {e}", file=sys.stderr, flush=True)
            return 1

    seeds_list = [SEED]
    run_config = {"N": 2048, "run_mode": RUN_MODE, "anchor": ANCHOR_NAME,
                  "M_sweep": (SMOKE_M_SWEEP if SMOKE_MODE else FULL_M_SWEEP)}
    done, remaining = resumable_seeds(seeds_list, out_dir, run_config=run_config)
    print(f"[ckpt] {len(done)}/{len(seeds_list)} done; running {remaining}",
          flush=True)

    for seed in remaining:
        _write_minimal_metrics(
            out_dir, "RUNNING",
            f"RUNNING: seed={seed} mode={RUN_MODE}",
            extra={"_phase": "seed_running", "_current_seed": seed,
                   "backend": backend},
        )
        t0 = time.time()
        result = run_one_seed_all_units(seed, run_mode=RUN_MODE, device=device)
        result["anchor_name"] = ANCHOR_NAME
        result["config_version"] = CONFIG_VERSION
        write_partial_key(out_dir, seed, result)
        print(f"[seed={seed}] complete in {time.time()-t0:.1f}s "
              f"(units={len(result['per_unit'])})", flush=True)

    per_seed = aggregate_partials(out_dir, seeds_list, run_config=run_config)
    final = aggregate_and_verdict(per_seed, run_mode=RUN_MODE)
    final["anchor_name"] = ANCHOR_NAME
    final["elapsed_s"] = round(time.time() - _RESULTS_HOLDER["started_at"], 2)
    final["ts_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    final["pid"] = os.getpid()
    final["run_mode"] = RUN_MODE
    final["config_version"] = CONFIG_VERSION
    final["_hardening_marker"] = "v4_bytes_per_fact_pareto_M_ultra_extended_N2048_chunked"
    final["backend"] = backend
    final["seed"] = SEED
    final["n_seeds"] = 1
    final["corpus_provenance"] = (
        "synthetic_uniform_KG_5000ent_100rel_M_sweep_1k_4k_10k_40k_80k_160k_holdout_10pct_queries"
    )

    tmp = out_dir / "metrics.json.tmp"
    final_path = out_dir / "metrics.json"
    tmp.write_text(json.dumps(final, indent=2, default=str), encoding="utf-8")
    os.replace(tmp, final_path)
    print(f"[{ANCHOR_NAME}] DONE: {final['verdict_msg']}", flush=True)
    print(
        f"[{ANCHOR_NAME}] cardinality observed_per_seed="
        f"{final.get('observed_n_units_per_seed')} "
        f"expected={final.get('expected_n_units_per_seed')} "
        f"ok={final.get('cardinality_ok')}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    try:
        rc = main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_import_crash_sentinel(e)
        print(f"[main] OUTER_EXCEPTION: {e}", file=sys.stderr, flush=True)
        traceback.print_exc()
        rc = 1
    sys.exit(rc)
