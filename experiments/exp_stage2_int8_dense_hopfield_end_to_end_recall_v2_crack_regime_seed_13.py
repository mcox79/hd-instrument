"""Stage 2 opener v2: INT8 dense-Hopfield end-to-end recall crack-regime, seed=7.

v1 landed HARD_FAIL_META_RULE_Q_NON_DISCRIMINATING (all arms saturated at
recall=1.0 across USER's pre-crack grid). v2 amendment (Research approved
2026-07-01) extends M into crack region for N=8192:

  FULL_M_SWEEP = [1000, 10000, 40000, 80000, 160000, 320000]  (6 M-points)
  FULL_N_FIXED = 8192  (N-fixed, was N-sweep in v1)
  FULL_SIGMA_SWEEP = [0.0, 0.2, 0.5]  (3 sigma-points)
  4 precisions x 6 M x 3 sigma = 72 units/seed

Discriminator moves to (N=8192, M=160000, sigma=0.2) -- E v5-scaled crack midpoint.

4 HP gates (all must PASS for HARD_PASS):
  HP_INT8_PARETO_CG:      |INT8 - FP32| <= 0.05 at discriminator point
  HP_INT4_BREAKS:         (FP32 - INT4) >= 0.20 at discriminator point (documentation)
  HP_PRE_CRACK_FREE:      at M in {1000, 10000}, all 4 arms within 0.01
  HP_POST_CRACK_COLLAPSE: at M=320000, all 4 arms < 0.30 recall

CHUNKED: one seed per file. Siblings: seed_13, seed_19.

Composes hdlab.int8_dense.quantize_int8_dense (META_RULE_AT commit c3ca7dab).
Inline INT4 (extract to hdlab/int4_dense.py if v2 lands CG).

PROT-020: torch import present.
PROT-018: anchor has no _n suffix (N is fixed 8192 in v2).
Route: overnight_queue (GPU-heavy at M=320k); timeout 7200s per USER task.

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

SEED = 13
ANCHOR_NAME = f"stage2_int8_dense_hopfield_end_to_end_recall_v2_crack_regime_seed_{SEED}"

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
    f"arms=[FP32,FP16,INT8,INT4],"
    f"M_sweep_full=[1000,10000,40000,80000,160000,320000],"
    f"M_sweep_smoke=[40000],"
    f"N_fixed_full=8192,N_fixed_smoke=4096,"
    f"sigma_sweep_full=[0.0,0.2,0.5],sigma_sweep_smoke=[0.2],"
    f"n_ent_full=5000,n_rel_full=100,n_ent_smoke=5000,n_rel_smoke=100,"
    f"query_frac=0.10,topK=1,SEED={SEED},mode={RUN_MODE},"
    f"discriminator=4gate(INT8_PARETO_CG+INT4_BREAKS+PRE_CRACK_FREE+POST_CRACK_COLLAPSE)"
    f"@N8192_M160k_sigma0.2,"
    f"HP_INT8_PARETO_CG_TOL=0.05,HP_INT4_BREAKS_DELTA=0.20,"
    f"HP_PRE_CRACK_FREE_TOL=0.01,HP_POST_CRACK_COLLAPSE_MAX=0.30,"
    f"HP_MEMORY_FACTOR_MAX=0.35,"
    f"cv_hp=0.08,cv_mb=0.10,saturation_ceil=0.98,"
    f"compose=hdlab.int8_dense.quantize_int8_dense(commit c3ca7dab)+inline_int4,"
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
            "_hardening_marker": "v2_stage2_int8_pareto_crack_regime_chunked",
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
            "_hardening_marker": "v2_stage2_int8_pareto_crack_regime_import_crash",
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

    from experiments._stage2_int8_dense_hopfield_end_to_end_recall_v2_crack_regime_core import (
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
    final["_hardening_marker"] = "v2_stage2_int8_pareto_crack_regime_chunked"
    final["backend"] = backend
    final["seed"] = SEED
    final["n_seeds"] = 1
    final["corpus_provenance"] = (
        "synthetic_uniform_KG_5000ent_100rel_N_fixed_8192_"
        "M_sweep_1k_10k_40k_80k_160k_320k_"
        "sigma_sweep_0.0_0.2_0.5_"
        "holdout_10pct_queries_crack_regime_v2_amendment"
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
