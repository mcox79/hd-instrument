"""substrate_wm_routing_family_phase_diagram_v1 sibling seed=13.

FOURTH COMPONENT-SUBSTITUTION phase diagram (USER 2026-06-28 Research directive).
Encoder family + cleanup family + seqbind family already in flight; this cell
covers the ROUTING family for multi-bank WM.

Inner grid: 4 routings * 3 K * 2 regimes = 24 phase points per seed (FULL).
Smoke: 4 routings * 2 K * 1 regime = 8 corner points per seed.

CHUNKED architecture (USER 2026-06-28): one seed per sibling file.
Sibling pair: seed_7, seed_19.

PRE-REG: preregs/2026-06-28_substrate_wm_routing_family_phase_diagram_v1.md
CARDINALITY_OK_FULL: 24 phase points per seed
CARDINALITY_OK_SMOKE: 8 corner points per seed

PROT-018: anchor has no _n<N> suffix (multi-K sweep cell).
PROT-019: anchor uses no _n>=4096 suffix -> no timeout floor.

4 defensive patterns (USER 2026-06-28 hardening):
  1. start_marker: STARTED metrics written before any heavy work
  2. crash-diag: outer try -> import-crash sentinel with full traceback
  3. per-unit checkpoint: write_partial_key per seed via _seed_checkpoint
  4. heartbeat: per-phase-point flush print

ASCII-only. No unicode. No em-dashes. No emojis.
Author: exp_dev 2026-06-28 (Opus 4.7 1M, agent-spawn)
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

# torch imported at TOP of file for PROT-020 GPU eligibility scan
import torch  # noqa: F401  -- gate marker only

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    resumable_seeds, write_partial_key, aggregate_partials,
)

SEED = 13
ANCHOR_NAME = f"substrate_wm_routing_family_phase_diagram_v1_seed_{SEED}"

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
    f"routings=[partition,knn_softmax,softmax_attention,learned_hierarchical],"
    f"K_full=[1024,4096,8192],regimes_full=[RANDOM,ADVERSARIAL],"
    f"k_per_bank_full=64,N_full=8192,CB_full=16384,"
    f"K_smoke=[256,1024],regimes_smoke=[RANDOM],k_per_bank_smoke=32,"
    f"N_smoke=2048,CB_smoke=4096,"
    f"SEED={SEED},mode={RUN_MODE},"
    f"sigma=1.0,cue_cos=0.70,feat_overlap=0.20,beta_soft=8.0,group_size=4,"
    f"expected_n_full=24,expected_n_smoke=8,"
    f"hardening=L1startmarker+L2crashdiag+L3perunitckpt+L4heartbeat+CHUNKED_PER_SEED"
)

_RESULTS_HOLDER: Dict[str, Any] = {"started_at": time.time()}
_LLM_CALL_COUNTER = [0]


def _write_minimal_metrics(out_dir: Path, verdict: str, verdict_msg: str,
                            extra: Dict[str, Any] = None) -> None:
    """Defensive pattern #1: start_marker + intermediate phase markers."""
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
            "_hardening_marker": "v1_wm_routing_family_phase_diagram_chunked",
        }
        if extra:
            m.update(extra)
        (out_dir / "metrics.json").write_text(
            json.dumps(m, indent=2, default=str), encoding="utf-8")
    except Exception as e:
        print(f"[_write_minimal_metrics] FAIL: {e}", file=sys.stderr, flush=True)


def _write_import_crash_sentinel(exc: BaseException) -> None:
    """Defensive pattern #2: crash-diag sentinel with full traceback."""
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
            "_hardening_marker": "v1_wm_routing_family_import_crash",
        }
        (out_dir / "metrics.json").write_text(json.dumps(s, indent=2),
                                              encoding="utf-8")
        (out_dir / "import_crash.json").write_text(json.dumps(s, indent=2),
                                                   encoding="utf-8")
    except Exception as e:
        print(f"[_write_import_crash_sentinel] FAIL: {e}",
              file=sys.stderr, flush=True)


def main() -> int:
    _RESULTS_HOLDER["started_at"] = time.time()
    env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    out_dir = REPO / "data" / ("exp_" + env_name)
    out_dir.mkdir(parents=True, exist_ok=True)

    _write_minimal_metrics(out_dir, "STARTED",
                           f"STARTED: pid={os.getpid()} mode={RUN_MODE} seed={SEED}",
                           extra={"_phase": "init"})

    from experiments._substrate_wm_routing_family_phase_diagram_v1_core import (
        run_one_seed_phase_diagram, aggregate_and_verdict, selftest,
        get_backend_label,
        N_DIM_SMOKE, N_DIM_FULL,
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

    # GPU mandate (Fix #24) — FULL on CPU REFUSED unless HDLAB_QUEUE=local_cpu_queue
    routed_queue = os.environ.get("HDLAB_QUEUE", "").lower()
    if not SMOKE_MODE and backend == "torch.cpu":
        if routed_queue != "local_cpu_queue":
            verdict = "HARD_FAIL"
            vmsg = ("HARD_FAIL_GPU_MANDATE_BREACH: FULL run on CPU backend forbidden "
                    "by Fix #24 unless HDLAB_QUEUE=local_cpu_queue. "
                    f"Got HDLAB_QUEUE='{routed_queue}'. Refusing.")
            _write_minimal_metrics(out_dir, verdict, vmsg,
                                   extra={"_phase": "gpu_mandate_check",
                                          "backend": backend,
                                          "routed_queue": routed_queue})
            print(f"[FATAL] {vmsg}", file=sys.stderr, flush=True)
            return 2

    # Per-seed checkpoint resume
    seeds_list = [SEED]
    N_stamp = N_DIM_SMOKE if SMOKE_MODE else N_DIM_FULL
    run_config = {"N": N_stamp, "run_mode": RUN_MODE, "anchor": ANCHOR_NAME}
    done, remaining = resumable_seeds(seeds_list, out_dir, run_config=run_config)
    print(f"[ckpt] {len(done)}/{len(seeds_list)} done; running {remaining}",
          flush=True)

    for seed in remaining:
        _write_minimal_metrics(out_dir, "RUNNING",
                               f"RUNNING: seed={seed} mode={RUN_MODE}",
                               extra={"_phase": "seed_running",
                                      "_current_seed": seed,
                                      "backend": backend})
        t0 = time.time()
        result = run_one_seed_phase_diagram(seed, run_mode=RUN_MODE)
        result["N"] = N_stamp
        result["anchor_name"] = ANCHOR_NAME
        result["config_version"] = CONFIG_VERSION
        write_partial_key(out_dir, seed, result)
        print(f"[seed={seed}] complete in {time.time()-t0:.1f}s "
              f"({result['observed_n_units']} pts)", flush=True)

    per_seed = aggregate_partials(out_dir, seeds_list, run_config=run_config)
    final = aggregate_and_verdict(per_seed, run_mode=RUN_MODE)
    final["anchor_name"] = ANCHOR_NAME
    final["elapsed_s"] = round(time.time() - _RESULTS_HOLDER["started_at"], 2)
    final["ts_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    final["pid"] = os.getpid()
    final["run_mode"] = RUN_MODE
    final["config_version"] = CONFIG_VERSION
    final["_hardening_marker"] = "v1_wm_routing_family_phase_diagram_chunked"
    final["backend"] = backend
    final["seed"] = SEED
    final["n_seeds"] = 1
    final["corpus_provenance"] = "synthetic_substrate_4_routing_family_multibank_wm"
    final["n_llm_calls"] = _LLM_CALL_COUNTER[0]
    final["zero_llm_calls_at_inference"] = (_LLM_CALL_COUNTER[0] == 0)

    assert _LLM_CALL_COUNTER[0] == 0, \
        "LLM_CALL_GATE_BREACH: substrate-only required"

    (out_dir / "metrics.json").write_text(
        json.dumps(final, indent=2, default=str), encoding="utf-8")
    print(f"[{ANCHOR_NAME}] DONE: {final['verdict_msg']}", flush=True)
    print(f"[{ANCHOR_NAME}] cardinality observed={final.get('observed_n_units')} "
          f"expected={final.get('expected_n_units')} "
          f"ok={final.get('cardinality_ok')}", flush=True)
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
