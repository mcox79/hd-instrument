"""Stage 2 INT2/BINARY Pareto probe v2 with asymmetric ternary, seed=7.

v1 smoke (2026-07-02 04:31 UTC) established at (N=4096,M=100k,sigma=0.28):
  FP32=0.683 INT8=0.683 INT4=0.674 INT2sym=0.205 BINARY=0.499
Symmetric ternary INT2 catastrophically fails (~1/3 of magnitudes zeroed).
Skunkworks batch 10 predicts asymmetric ternary {-2,-1,+1,+2} skip-zero
recovers the INT2 catastrophe by preserving non-zero magnitude everywhere.

v2 grid: 6 arms x 1 M x 4 sigma = 24 units/seed (N=8192 fixed, M=160k fixed).
  FULL_M_FIXED = 160000
  FULL_N_FIXED = 8192
  FULL_SIGMA_SWEEP = [0.20, 0.30, 0.35, 0.40]

Discriminator: (M=160k, best-sigma) auto-selected -- matches INT8 v3 CG regime.

HP gates:
  HP_META_RULE_Q_ATCLIFF, HP_INT2_ASYM_RECOVERS (<=0.10 v FP32; KEY),
  HP_BINARY_PARETO_CG (<=0.15 v FP32; lifts v1 MIDDLE_BAND to CG),
  HP_INT2_SYM_BREAKS_ROBUST (>=0.30 drop; reproduces v1 MM_TENTATIVE),
  HP_MEMORY_TIER_INT2, HP_MEMORY_TIER_BINARY

HF gates:
  HF_INT2_ASYM_ALSO_BREAKS (>=0.30 drop), HF_BINARY_BREAKS (>=0.35 drop)

CHUNKED: one seed per file. Siblings: seed_13, seed_19.
Composes hdlab.int8_dense.quantize_int8_dense; inline INT4/INT2sym/INT2asym/BINARY.

PROT-020: torch import present.
PROT-018: anchor has no _n suffix (N fixed 8192).
Route: overnight_queue (GPU); timeout 7200s.

CLI hardening (v2):
  --smoke      -> smoke mode
  --self-test  -> selftest mode
  --full       -> full mode (explicit; recommended for runner invocation)
  default env HDLAB_RUN_MODE (fallback "full")
  metrics.json includes explicit run_mode + startup args log for audit.

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
ANCHOR_NAME = f"stage2_int2_binary_pareto_at_cliff_v2_with_asymmetric_ternary_seed_{SEED}"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--full", action="store_true",
                 help="explicit full-mode flag; recommended for runner invocation")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _EXTRA_ARGV = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
_HDLAB_RUN_MODE_ENV = os.environ.get("HDLAB_RUN_MODE", "").lower()

# Precedence: explicit --smoke > env HDLAB_EXP_NAME contains _smoke > --self-test
#   > explicit --full > env HDLAB_RUN_MODE > default "full".
# This makes accidental selftest-only landings from a runner impossible unless
# the runner explicitly sets --self-test or HDLAB_RUN_MODE=selftest.
if _ARGS.smoke or _NAME_SAYS_SMOKE:
    RUN_MODE = "smoke"
elif _ARGS.self_test:
    RUN_MODE = "selftest"
elif _ARGS.full:
    RUN_MODE = "full"
elif _HDLAB_RUN_MODE_ENV:
    RUN_MODE = _HDLAB_RUN_MODE_ENV
else:
    RUN_MODE = "full"

SELF_TEST_MODE = (RUN_MODE == "selftest")
SMOKE_MODE = (RUN_MODE == "smoke")
FULL_MODE = (RUN_MODE == "full")

_STARTUP_ARGS_LOG = {
    "argv": sys.argv,
    "parsed_smoke": _ARGS.smoke,
    "parsed_full": _ARGS.full,
    "parsed_self_test": _ARGS.self_test,
    "env_HDLAB_EXP_NAME": _HDLAB_EXP_NAME,
    "env_HDLAB_RUN_MODE": _HDLAB_RUN_MODE_ENV,
    "resolved_RUN_MODE": RUN_MODE,
}

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},"
    f"arms=[FP32,INT8,INT4,INT2,INT2_ASYM,BINARY],"
    f"M_fixed_full=160000,M_fixed_smoke=100000,"
    f"N_fixed_full=8192,N_fixed_smoke=4096,"
    f"sigma_sweep_full=[0.20,0.30,0.35,0.40],sigma_sweep_smoke=[0.28],"
    f"n_ent=5000,n_rel=100,query_frac=0.10,topK=1,"
    f"SEED={SEED},mode={RUN_MODE},"
    f"discriminator=NOISE_CLIFF_AUTO_SELECT@M160k_bestsigma,"
    f"HP_META_RULE_Q_ARMS_RANGE_MIN=0.03,HP_META_RULE_Q_FP32_UPPER=0.98,"
    f"HP_INT2_ASYM_RECOVERS_TOL=0.10,HP_BINARY_PARETO_CG_TOL=0.15,"
    f"HP_INT2_SYM_BREAKS_DELTA=0.30,"
    f"HP_MEMORY_FACTOR_INT2_MAX=0.10,HP_MEMORY_FACTOR_BINARY_MAX=0.04,"
    f"HF_INT2_ASYM_ALSO_BREAKS_DELTA=0.30,HF_BINARY_BREAKS_DELTA=0.35,"
    f"cv_hp=0.08,cv_mb=0.15,"
    f"compose=hdlab.int8_dense.quantize_int8_dense+inline_int4_int2sym_int2asym_binary,"
    f"basis=v1_smoke_falsifies_symmetric_ternary_int2_asym_recovery_hypothesis,"
    f"hardening=L1startmarker+L2crashdiag+L3perunitckpt+CHUNKED_PER_SEED+CLI_MODE_LOG"
)

_RESULTS_HOLDER: Dict[str, Any] = {"started_at": time.time()}


def _write_minimal_metrics(out_dir, verdict, verdict_msg, extra=None):
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
            "startup_args_log": _STARTUP_ARGS_LOG,
            "config_version": CONFIG_VERSION,
            "_hardening_marker": "v2_stage2_int2_binary_asym_ternary_chunked",
        }
        if extra:
            m.update(extra)
        tmp = out_dir / "metrics.json.tmp"
        final = out_dir / "metrics.json"
        tmp.write_text(json.dumps(m, indent=2, default=str), encoding="utf-8")
        os.replace(tmp, final)
    except Exception as e:
        print(f"[_write_minimal_metrics] FAIL: {e}", file=sys.stderr, flush=True)


def _write_import_crash_sentinel(exc):
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
            "_hardening_marker": "v2_stage2_int2_binary_asym_ternary_import_crash",
        }
        tmp = out_dir / "metrics.json.tmp"
        final = out_dir / "metrics.json"
        tmp.write_text(json.dumps(s, indent=2), encoding="utf-8")
        os.replace(tmp, final)
    except Exception as e:
        print(f"[_write_import_crash_sentinel] FAIL: {e}", file=sys.stderr, flush=True)


def main():
    _RESULTS_HOLDER["started_at"] = time.time()
    env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    out_dir = REPO / "data" / ("exp_" + env_name)
    out_dir.mkdir(parents=True, exist_ok=True)

    _write_minimal_metrics(
        out_dir, "STARTED",
        f"STARTED: pid={os.getpid()} mode={RUN_MODE} seed={SEED} "
        f"argv={sys.argv} env_HDLAB_RUN_MODE={_HDLAB_RUN_MODE_ENV or 'unset'}",
        extra={"_phase": "init"},
    )

    from experiments._stage2_int2_binary_pareto_at_cliff_v2_with_asymmetric_ternary_core import (
        run_one_seed_all_units, aggregate_and_verdict, selftest,
        get_backend_label, _get_device, ARMS,
        FULL_M_FIXED, SMOKE_M_FIXED, FULL_N_FIXED, SMOKE_N_FIXED,
        FULL_SIGMA_SWEEP, SMOKE_SIGMA_SWEEP,
    )

    device = _get_device(strict_gpu=False)
    backend = get_backend_label()
    print(f"[{ANCHOR_NAME}] mode={RUN_MODE} seed={SEED} backend={backend} "
          f"device={device}", flush=True)
    print(f"[{ANCHOR_NAME}] startup_args_log={_STARTUP_ARGS_LOG}", flush=True)

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
                  "M_fixed": (SMOKE_M_FIXED if SMOKE_MODE else FULL_M_FIXED),
                  "N": (SMOKE_N_FIXED if SMOKE_MODE else FULL_N_FIXED),
                  "sigma_sweep": (SMOKE_SIGMA_SWEEP if SMOKE_MODE else FULL_SIGMA_SWEEP)}
    done, remaining = resumable_seeds(seeds_list, out_dir, run_config=run_config)
    print(f"[ckpt] {len(done)}/{len(seeds_list)} done; running {remaining}", flush=True)

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
    final["startup_args_log"] = _STARTUP_ARGS_LOG
    final["config_version"] = CONFIG_VERSION
    final["_hardening_marker"] = "v2_stage2_int2_binary_asym_ternary_chunked"
    final["backend"] = backend
    final["seed"] = SEED
    final["n_seeds"] = 1
    final["corpus_provenance"] = (
        "synthetic_uniform_KG_5000ent_100rel_N_fixed_8192_M_fixed_160k_"
        "sigma_sweep_0.20_0.30_0.35_0.40_holdout_10pct_queries_"
        "int2_binary_v2_asymmetric_ternary_extension_of_v1"
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
