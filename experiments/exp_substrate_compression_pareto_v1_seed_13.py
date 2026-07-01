"""substrate_compression_pareto_v1 sibling seed=13.

USER REQUEST 2026-07-01: Compression efficiency Pareto (facts per schema
centroid vs downstream recall). 4-arm cell:
  ARM_NO_COMPRESSION          (baseline; 1 fact/prototype)
  ARM_SCHEMA_EXEMPLAR_BAYES   (chain-grade v3 family; ~10 facts/schema)
  ARM_SCHEMA_HARDMAX_CENTROID (chain-grade v4 family; ~100 facts/schema)
  ARM_SCHEMA_HIERARCHICAL     (2-level coarse+fine; ~10 facts/schema)

CHUNKED architecture (USER 2026-06-28): one seed per sibling file.
Sibling pair: seed_13, seed_19.

FULL: n_facts=10000, N_DIM=8192, n_queries=100, 3 seeds.
SMOKE: n_facts=1000, N_DIM=2048, n_queries=30, 1 seed.

PRE-REG: preregs/2026-07-01_substrate_compression_pareto_v1.md

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
 - arms_differ_verified at smoke gate (META_RULE_AF; via _hash_preds per arm)
 - final_metrics_atomicity: per_iter | tmp_replace | iter_count (uses _seed_checkpoint)
 - except SystemExit: raise BEFORE except Exception (no BaseException in main)
 - cardinality_ok (META_RULE_H; per-arm result count == 4)
 - per-unit failure-class instrumentation (no bare except)
 - HP strictly above floor + 5% band-width (positive control >= 0.85 not >= 0.85 tie)
 - HP_SCOPE per-arm (see prereg)
 - CRLB/capacity-feasibility declared in prereg (recall ceiling at n_facts=10000/N=8192)
 - baseline_in_band at smoke (NO_COMPRESSION 0.60 <= recall <= 0.99 target)
 - discriminator survives scale (smoke at reduced N; full at target N)

ASCII-only. CPU-only (numpy + scipy.special.logsumexp); no GPU needed.

Author: exp_dev 2026-07-01 (Opus 4.7 1M, agent-spawn)
"""
# PRESERVE_ENV_VARS: HDLAB_QUEUE
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
import platform
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    resumable_seeds, write_partial_key, aggregate_partials,
)

SEED = 13
ANCHOR_NAME = f"substrate_compression_pareto_v1_seed_{SEED}"

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
    f"arms=[NO_COMPRESSION,SCHEMA_EXEMPLAR_BAYES,SCHEMA_HARDMAX_CENTROID,SCHEMA_HIERARCHICAL],"
    f"full_n_facts=10000,full_N=8192,full_n_q=100,"
    f"smoke_n_facts=1000,smoke_N=2048,smoke_n_q=30,"
    f"hardening=STARTED+SEED_CKPT+HEARTBEAT+CRASH_DIAG+SYS_EXIT_RAISE"
)

_RESULTS_HOLDER: Dict[str, Any] = {"started_at": time.time()}


def _write_start_marker(output_dir: Path) -> None:
    try:
        marker = {
            "pid": os.getpid(),
            "ts_iso": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "anchor_name": ANCHOR_NAME,
            "run_mode": RUN_MODE,
            "expected_n_units": 4 if RUN_MODE != "selftest" else 4,
            "host": platform.node(),
        }
        output_dir.mkdir(parents=True, exist_ok=True)
        tmp = output_dir / "_start_marker.json.tmp"
        final = output_dir / "_start_marker.json"
        tmp.write_text(json.dumps(marker, indent=2), encoding="utf-8")
        os.replace(tmp, final)
    except Exception as e:
        print(f"[_write_start_marker] FAIL: {e}", file=sys.stderr, flush=True)


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
            "_hardening_marker": "v1_compression_pareto_chunked",
        }
        if extra:
            m.update(extra)
        tmp = out_dir / "metrics.json.tmp"
        final = out_dir / "metrics.json"
        tmp.write_text(json.dumps(m, indent=2, default=str), encoding="utf-8")
        os.replace(tmp, final)
    except Exception as e:
        print(f"[_write_minimal_metrics] FAIL: {e}", file=sys.stderr, flush=True)


def _write_crash_metrics(out_dir: Path, exc: BaseException) -> None:
    """META_RULE_AH atomic crash write; runner-required fields at top."""
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        diag = {
            "anchor_name": ANCHOR_NAME,
            "verdict": "CELL_CRASHED",
            "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}",
            "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 2),
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "run_mode": RUN_MODE,
            "_hardening_marker": "v1_compression_pareto_crash",
        }
        tmp = out_dir / "metrics.json.tmp"
        final = out_dir / "metrics.json"
        tmp.write_text(json.dumps(diag, indent=2), encoding="utf-8")
        os.replace(tmp, final)
    except Exception as e:
        print(f"[_write_crash_metrics] FAIL: {e}", file=sys.stderr, flush=True)


def main() -> int:
    _RESULTS_HOLDER["started_at"] = time.time()
    env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    out_dir = REPO / "data" / ("exp_" + env_name)
    out_dir.mkdir(parents=True, exist_ok=True)

    _write_start_marker(out_dir)
    _write_minimal_metrics(out_dir, "STARTED",
                           f"STARTED: pid={os.getpid()} mode={RUN_MODE} seed={SEED}",
                           extra={"_phase": "init"})

    from experiments._substrate_compression_pareto_v1_core import (
        run_one_seed, aggregate_and_verdict, selftest,
        get_backend_label, ARMS,
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
        result = run_one_seed(seed, run_mode=RUN_MODE)
        result["anchor_name"] = ANCHOR_NAME
        result["config_version"] = CONFIG_VERSION
        write_partial_key(out_dir, seed, result)
        print(f"[seed={seed}] complete in {time.time()-t0:.1f}s "
              f"({len(result['arms'])} arms; n_facts={result['n_facts']} N={result['N_DIM']})",
              flush=True)

    per_seed = aggregate_partials(out_dir, seeds_list, run_config=run_config)
    final = aggregate_and_verdict(per_seed, run_mode=RUN_MODE)
    final["anchor_name"] = ANCHOR_NAME
    final["elapsed_s"] = round(time.time() - _RESULTS_HOLDER["started_at"], 2)
    final["ts_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    final["pid"] = os.getpid()
    final["run_mode"] = RUN_MODE
    final["config_version"] = CONFIG_VERSION
    final["_hardening_marker"] = "v1_compression_pareto_chunked"
    final["backend"] = backend
    final["seed"] = SEED

    # Cardinality (META_RULE_H): 4 arms per seed
    expected_n = 4
    observed_n = 0
    for body in per_seed.values():
        observed_n += len(body.get("arms", {}))
    final["expected_n"] = expected_n
    final["observed_n"] = observed_n
    final["cardinality_ok"] = (observed_n == expected_n)

    # Write final metrics atomically
    tmp = out_dir / "metrics.json.tmp"
    final_path = out_dir / "metrics.json"
    tmp.write_text(json.dumps(final, indent=2, default=str), encoding="utf-8")
    os.replace(tmp, final_path)

    print(f"[{ANCHOR_NAME}] DONE: {final['verdict_msg']}", flush=True)
    print(f"[{ANCHOR_NAME}] cardinality observed={observed_n} "
          f"expected={expected_n} ok={final['cardinality_ok']}", flush=True)
    return 0


if __name__ == "__main__":
    try:
        rc = main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
        out_dir = REPO / "data" / ("exp_" + env_name)
        _write_crash_metrics(out_dir, e)
        print(f"[main] OUTER_EXCEPTION: {e}", file=sys.stderr, flush=True)
        traceback.print_exc()
        rc = 1
    sys.exit(rc)
