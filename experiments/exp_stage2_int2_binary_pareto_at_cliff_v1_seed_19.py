"""Stage 2 INT2/binary Pareto probe at noise cliff, seed=7.

Extends INT8 v3 CG (HARD_PASS at N=8192, M=160k, sigma=0.35, FP32=0.529 INT8=0.530
INT4=0.524) downward: adds INT2 (2-bit ternary) and BINARY (sign()) arms.

AGS 1985 prediction: binary Hopfield 0.138N capacity vs analog 0.14N -- essentially
equivalent. Very likely INT2/binary also survive noise cliff. If confirmed, Pareto
memory-efficiency frontier extends 16x-32x below FP32.

v1 grid: 5 arms x 2 M x 4 sigma = 40 units/seed (N=8192 fixed).
  FULL_M_SWEEP = [100000, 160000]
  FULL_N_FIXED = 8192
  FULL_SIGMA_SWEEP = [0.20, 0.30, 0.35, 0.40]

Discriminator: best-discriminating (M=160k, sigma) point auto-selected.

HP gates: HP_META_RULE_Q_ATCLIFF; HP_INT2_PARETO (<=0.05 vs FP32); HP_BINARY_PARETO
(<=0.10 vs FP32); HP_MEMORY_TIER_INT2 (<=0.10x); HP_MEMORY_TIER_BINARY (<=0.04x)
HF gates: HF_INT2_BREAKS (>=0.20 drop); HF_BINARY_BREAKS (>=0.30 drop)

CHUNKED: one seed per file. Siblings: seed_13, seed_19.
Composes hdlab.int8_dense.quantize_int8_dense (unchanged); inline INT4/INT2/BINARY.

PROT-020: torch import present.
PROT-018: anchor has no _n suffix (N fixed 8192).
Route: overnight_queue (GPU); timeout 7200s.

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

SEED = 19
ANCHOR_NAME = f"stage2_int2_binary_pareto_at_cliff_v1_seed_{SEED}"

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
    f"arms=[FP32,INT8,INT4,INT2,BINARY],"
    f"M_sweep_full=[100000,160000],M_sweep_smoke=[100000],"
    f"N_fixed_full=8192,N_fixed_smoke=4096,"
    f"sigma_sweep_full=[0.20,0.30,0.35,0.40],sigma_sweep_smoke=[0.28],"
    f"n_ent=5000,n_rel=100,query_frac=0.10,topK=1,"
    f"SEED={SEED},mode={RUN_MODE},"
    f"discriminator=NOISE_CLIFF_AUTO_SELECT@M160k_bestsigma,"
    f"HP_META_RULE_Q_ARMS_RANGE_MIN=0.03,HP_META_RULE_Q_FP32_UPPER=0.98,"
    f"HP_INT2_PARETO_TOL=0.05,HP_BINARY_PARETO_TOL=0.10,"
    f"HP_MEMORY_FACTOR_INT2_MAX=0.10,HP_MEMORY_FACTOR_BINARY_MAX=0.04,"
    f"HF_INT2_BREAKS_DELTA=0.20,HF_BINARY_BREAKS_DELTA=0.30,"
    f"cv_hp=0.08,cv_mb=0.10,"
    f"compose=hdlab.int8_dense.quantize_int8_dense+inline_int4_int2_binary,"
    f"basis=AGS_1985_binary_analog_equivalence_0.138N_vs_0.14N,"
    f"hardening=L1startmarker+L2crashdiag+L3perunitckpt+CHUNKED_PER_SEED"
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
            "_hardening_marker": "v1_stage2_int2_binary_pareto_cliff_chunked",
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
            "_hardening_marker": "v1_stage2_int2_binary_pareto_cliff_import_crash",
        }
        tmp = out_dir / "metrics.json.tmp"
        final = out_dir / "metrics.json"
        tmp.write_text(json.dumps(s, indent=2), encoding="utf-8")
        os.replace(tmp, final)
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

    from experiments._stage2_int2_binary_pareto_at_cliff_v1_core import (
        run_one_seed_all_units, aggregate_and_verdict, selftest,
        get_backend_label, _get_device, ARMS,
        FULL_M_SWEEP, SMOKE_M_SWEEP, FULL_N_FIXED, SMOKE_N_FIXED,
        FULL_SIGMA_SWEEP, SMOKE_SIGMA_SWEEP,
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
    run_config = {"run_mode": RUN_MODE, "anchor": ANCHOR_NAME,
                  "M_sweep": (SMOKE_M_SWEEP if SMOKE_MODE else FULL_M_SWEEP),
                  "N": (SMOKE_N_FIXED if SMOKE_MODE else FULL_N_FIXED),
                  "sigma_sweep": (SMOKE_SIGMA_SWEEP if SMOKE_MODE else FULL_SIGMA_SWEEP)}
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
    final["_hardening_marker"] = "v1_stage2_int2_binary_pareto_cliff_chunked"
    final["backend"] = backend
    final["seed"] = SEED
    final["n_seeds"] = 1
    final["corpus_provenance"] = (
        "synthetic_uniform_KG_5000ent_100rel_N_fixed_8192_"
        "M_sweep_100k_160k_"
        "sigma_sweep_0.20_0.30_0.35_0.40_"
        "holdout_10pct_queries_int2_binary_extension_of_int8_v3_cg"
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
