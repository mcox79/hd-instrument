"""substrate_routing_geometry_family_kg_ingest_v2 sibling seed=7.

USER 2026-07-01 Axis G fill (5 routing geometries at KG-ingest ConceptNet).
Replaces v1 storage-free synthetic (SATURATED 3/4 arms) with real ConceptNet
routing-then-retrieve discriminator.

Chunked per-seed (§13). Sibling pair: seed_13, seed_19.

Pre-reg: preregs/2026-07-01_substrate_routing_geometry_family_kg_ingest_v2.md
Core:    experiments/_substrate_routing_geometry_family_kg_ingest_v2_core.py

Discriminator: retrieval_acc for (s,p) -> {o} via routing-then-retrieve.
Chain-grade target: >=3 arms distinct at HARD_PASS >=0.55.

ASCII-only. No unicode. No em-dashes.

CELL-TEMPLATE MANDATORY:
- arms_differ_verified via routing_hash sha256 per arm
- final_metrics_atomicity: tmp_replace via os.replace
- except SystemExit: raise BEFORE except Exception
- crash-diag: outer try -> IMPORT_CRASH sentinel with full traceback
- start_marker: STARTED metrics written before any heavy work
- heartbeat: per-arm print at INFO level

Author: exp_dev 2026-07-01 (Opus 4.7 1M, agent-spawn)
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import os
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

import argparse
import json
import time
import traceback
from pathlib import Path
from typing import Any, Dict

import torch  # noqa: F401  -- PROT-020 GPU eligibility marker

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

SEED = 7
ANCHOR_NAME = f"substrate_routing_geometry_family_kg_ingest_v2_seed_{SEED}"

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
    f"geometries=[random_partition,learned_supervised,lsh_hash,hierarchical_tree,knn_softmax],"
    f"M_smoke=10000,N_smoke=512,M_full=100000,N_full=2048,P_smoke=256,P_full=128,"
    f"n_eval_smoke=200,n_eval_full=1024,"
    f"SEED={SEED},mode={RUN_MODE},"
    f"expected_n_arms=5,"
    f"HP_HARD_PASS_RA=0.55,HP_MIN_DISTINCT=3,"
    f"hardening=L1startmarker+L2crashdiag+L3atomicmetrics+L4heartbeat+CHUNKED_PER_SEED"
)

_STARTED_AT = [time.time()]


def _write_metrics_atomic(out_dir: Path, payload: Dict[str, Any]) -> None:
    """META_RULE_AH atomic write: tmp + os.replace."""
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        tmp = out_dir / "metrics.json.tmp"
        final = out_dir / "metrics.json"
        tmp.write_text(json.dumps(payload, indent=2, default=str),
                       encoding="utf-8")
        os.replace(str(tmp), str(final))
    except Exception as e:
        print(f"[_write_metrics_atomic] FAIL: {e}",
              file=sys.stderr, flush=True)


def _minimal(verdict: str, verdict_msg: str,
             extra: Dict[str, Any] = None) -> Dict[str, Any]:
    m = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "elapsed_s": round(time.time() - _STARTED_AT[0], 2),
        "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "pid": os.getpid(),
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "_hardening_marker": "v2_routing_geometry_kg_ingest_chunked",
        "seed": SEED,
        "n_seeds": 1,
    }
    if extra:
        m.update(extra)
    return m


def _write_start_marker(out_dir: Path) -> None:
    """§13B start-marker (proves cell was invoked)."""
    try:
        import platform
        out_dir.mkdir(parents=True, exist_ok=True)
        marker = {
            "pid": os.getpid(),
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "anchor_name": ANCHOR_NAME,
            "run_mode": RUN_MODE,
            "expected_n_units": 5,
            "host": platform.node(),
        }
        tmp = out_dir / "_start_marker.json.tmp"
        final = out_dir / "_start_marker.json"
        tmp.write_text(json.dumps(marker), encoding="utf-8")
        os.replace(str(tmp), str(final))
    except Exception as e:
        print(f"[_write_start_marker] FAIL: {e}",
              file=sys.stderr, flush=True)


def _write_crash_metrics(out_dir: Path, exc: BaseException) -> None:
    """§13C crash-diagnostic sentinel."""
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        diag = {
            "anchor_name": ANCHOR_NAME,
            "verdict": "CELL_CRASHED",
            "verdict_msg": f"CELL_CRASHED: {type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}",
            "elapsed_s": round(time.time() - _STARTED_AT[0], 2),
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "run_mode": RUN_MODE,
            "config_version": CONFIG_VERSION,
            "traceback": traceback.format_exc()[:5000],
            "seed": SEED,
        }
        tmp = out_dir / "metrics.json.tmp"
        final = out_dir / "metrics.json"
        tmp.write_text(json.dumps(diag, indent=2), encoding="utf-8")
        os.replace(str(tmp), str(final))
    except Exception as e:
        print(f"[_write_crash_metrics] FAIL: {e}",
              file=sys.stderr, flush=True)


def main() -> int:
    _STARTED_AT[0] = time.time()
    env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    out_dir = REPO / "data" / ("exp_" + env_name)
    out_dir.mkdir(parents=True, exist_ok=True)

    _write_start_marker(out_dir)
    _write_metrics_atomic(out_dir, _minimal(
        "STARTED", f"STARTED: pid={os.getpid()} mode={RUN_MODE} seed={SEED}",
        {"_phase": "init"}))

    from experiments._substrate_routing_geometry_family_kg_ingest_v2_core import (
        run_one_seed, selftest, get_backend_label,
    )

    backend = get_backend_label()
    print(f"[{ANCHOR_NAME}] mode={RUN_MODE} seed={SEED} backend={backend}",
          flush=True)

    if SELF_TEST_MODE:
        try:
            ok, msg = selftest(SEED)
            verdict = "SELFTEST_OK" if ok else "SELFTEST_FAIL"
            _write_metrics_atomic(out_dir, _minimal(
                verdict, msg,
                {"_phase": "selftest_done", "backend": backend}))
            print(f"[selftest] {verdict}: {msg}", flush=True)
            return 0 if ok else 1
        except Exception as e:
            _write_metrics_atomic(out_dir, _minimal(
                "SELFTEST_FAIL", f"SELFTEST_FAIL: {e}",
                {"_traceback": traceback.format_exc()[:5000],
                 "backend": backend}))
            print(f"[selftest] FAIL: {e}", file=sys.stderr, flush=True)
            return 1

    # GPU mandate (Fix #24)
    routed_queue = os.environ.get("HDLAB_QUEUE", "").lower()
    if not SMOKE_MODE and backend == "torch.cpu":
        if routed_queue != "local_cpu_queue":
            vmsg = ("HARD_FAIL_GPU_MANDATE_BREACH: FULL run on CPU backend forbidden "
                    "by Fix #24 unless HDLAB_QUEUE=local_cpu_queue. "
                    f"Got HDLAB_QUEUE='{routed_queue}'. Refusing.")
            _write_metrics_atomic(out_dir, _minimal(
                "HARD_FAIL", vmsg,
                {"_phase": "gpu_mandate_check", "backend": backend,
                 "routed_queue": routed_queue}))
            print(f"[FATAL] {vmsg}", file=sys.stderr, flush=True)
            return 2

    _write_metrics_atomic(out_dir, _minimal(
        "RUNNING", f"RUNNING: seed={SEED} mode={RUN_MODE}",
        {"_phase": "seed_running", "backend": backend}))

    t0 = time.time()
    result = run_one_seed(SEED, run_mode=RUN_MODE)
    result["anchor_name"] = ANCHOR_NAME
    result["config_version"] = CONFIG_VERSION
    result["_hardening_marker"] = "v2_routing_geometry_kg_ingest_chunked"
    result["backend"] = backend
    result["elapsed_s"] = round(time.time() - _STARTED_AT[0], 2)
    result["ts_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    result["pid"] = os.getpid()
    result["run_mode"] = RUN_MODE
    result["n_seeds"] = 1
    result["corpus_provenance"] = "conceptnet5_en_100k_5arm_routing_geometry"
    result["n_llm_calls"] = 0
    result["zero_llm_calls_at_inference"] = True

    _write_metrics_atomic(out_dir, result)
    print(f"[{ANCHOR_NAME}] DONE: {result['verdict_msg']}", flush=True)
    print(f"[{ANCHOR_NAME}] retrieval_acc_by_arm={result['retrieval_acc_by_arm']}",
          flush=True)
    return 0


if __name__ == "__main__":
    env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    out_dir = REPO / "data" / ("exp_" + env_name)
    try:
        rc = main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(out_dir, e)
        print(f"[main] OUTER_EXCEPTION: {type(e).__name__}: {e}",
              file=sys.stderr, flush=True)
        traceback.print_exc()
        rc = 1
    sys.exit(rc)
