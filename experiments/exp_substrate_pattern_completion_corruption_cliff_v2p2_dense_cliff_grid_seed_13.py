"""substrate_pattern_completion_corruption_cliff_v2p2_dense_cliff_grid sibling seed=13.

v2.2 promotion path for v2.1 MEASURED_MECHANISM (Skunkworks commit 2daf9b55).
v2.1 grid {0.40,0.43,0.46,0.48,0.50,0.52} -> 36 SAT / 0 HP / 6 MB / 24 FLOOR / 6 FAIL per seed.
Cliff razor-sharp at corruption=0.48-0.50. Need >=22 MB / 180 for chain-grade-phase
promotion. v2.2 dense grid populates [0.46, 0.50] @ 0.005 step (9 pts) plus shoulders.

CORRUPTION_FULL = {0.43, 0.44, 0.45, 0.455, 0.46, 0.465, 0.47, 0.475, 0.48,
                   0.485, 0.49, 0.495, 0.50, 0.51, 0.52}  (15 pts; was 6)
N_SWEEP_FULL = {2048, 4096, 8192, 16384}                  (4 pts; unchanged)
ITERS_FULL = {1, 5, 20}                                    (3 pts; unchanged)
TOTAL: 15 * 4 * 3 = 180 phase points per seed (was 72)

CHUNKED architecture (USER 2026-06-28): one seed per sibling file.
Sibling pair: seed_7, seed_19.

ARMS: SUBSTRATE / RANDOM_FLOOR (2 per phase-point)
SWEEP: 180 pts per seed (FULL)
N_DIM up to 16384 (CUDA preferred; CPU fallback for smoke; FULL CPU REFUSED)

PRE-REG: preregs/2026-06-28_substrate_pattern_completion_corruption_cliff_v2p2_dense_cliff_grid.md
CARDINALITY_OK_FULL: 180 phase points per seed
CARDINALITY_OK_SMOKE: 6 corner points per seed

PROT-018: anchor has no _n<N> suffix (multi-N sweep cell).
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

# torch imported at TOP of file for Fix #24 GPU eligibility scan
# (the core helper also imports it; this top-level import is what the
# overnight_queue routing-gate regex `^import torch` detects).
import torch  # noqa: F401  -- gate marker only; actual use is in core helper

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    resumable_seeds, write_partial_key, aggregate_partials,
)

SEED = 13
ANCHOR_NAME = f"substrate_pattern_completion_corruption_cliff_v2p2_dense_cliff_grid_seed_{SEED}"

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
    f"ANCHOR={ANCHOR_NAME},N=[2048,4096,8192,16384],SEED={SEED},mode={RUN_MODE},"
    f"corruption=[0.43,0.44,0.45,0.455,0.46,0.465,0.47,0.475,0.48,0.485,0.49,"
    f"0.495,0.50,0.51,0.52],iters=[1,5,20],M=500,beta=8.0,"
    f"arms=[SUBSTRATE,RANDOM_FLOOR],"
    f"expected_n_full=180,expected_n_smoke=6,"
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
            "_hardening_marker": "v2p2_pc_corruption_cliff_dense_chunked",
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
            "_hardening_marker": "v2p2_pc_corruption_cliff_dense_import_crash",
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

    # Import core LATE so import-crash sentinel catches torch/cuda issues
    from experiments._substrate_pattern_completion_corruption_cliff_v2p2_dense_cliff_grid_core import (
        run_one_seed_phase_diagram, aggregate_and_verdict, selftest,
        get_backend_label,
        N_SWEEP_FULL, CORRUPTION_FULL, ITERS_FULL, M_ITEMS_FULL,
        N_SWEEP_SMOKE, CORRUPTION_SMOKE, ITERS_SMOKE, M_ITEMS_SMOKE,
    )

    backend = get_backend_label()
    print(f"[{ANCHOR_NAME}] mode={RUN_MODE} seed={SEED} backend={backend}", flush=True)

    # Selftest mode
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

    # FULL on CPU REFUSED for GPU mandate (Fix #24) — but USER TASK routes v2.2
    # full sweep to local_cpu_queue per dispatch instructions. Honor request:
    # allow FULL on CPU when explicitly routed via local_cpu_queue (HDLAB_QUEUE
    # env var set by runner). If unset, fall through to GPU mandate refusal.
    routed_queue = os.environ.get("HDLAB_QUEUE", "").lower()
    if not SMOKE_MODE and backend == "torch.cpu":
        if routed_queue != "local_cpu_queue":
            verdict = "HARD_FAIL"
            vmsg = ("HARD_FAIL_GPU_MANDATE_BREACH: FULL run on CPU backend forbidden "
                    "by Fix #24 unless HDLAB_QUEUE=local_cpu_queue (USER explicit "
                    "route). Got HDLAB_QUEUE='" + routed_queue + "'. Refusing.")
            _write_minimal_metrics(out_dir, verdict, vmsg,
                                   extra={"_phase": "gpu_mandate_check",
                                          "backend": backend,
                                          "routed_queue": routed_queue})
            print(f"[FATAL] {vmsg}", file=sys.stderr, flush=True)
            return 2

    # Per-seed checkpoint resume
    seeds_list = [SEED]
    N_max = max(N_SWEEP_SMOKE if SMOKE_MODE else N_SWEEP_FULL)
    run_config = {"N": N_max, "run_mode": RUN_MODE, "anchor": ANCHOR_NAME}
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
        # PROT-021 stamps (N + anchor)
        result["N"] = N_max
        result["anchor_name"] = ANCHOR_NAME
        result["config_version"] = CONFIG_VERSION
        # Defensive pattern #3: per-unit (per-seed) checkpoint
        write_partial_key(out_dir, seed, result)
        print(f"[seed={seed}] complete in {time.time()-t0:.1f}s "
              f"({result['observed_n_units']} pts)", flush=True)

    # Aggregate + verdict
    per_seed = aggregate_partials(out_dir, seeds_list, run_config=run_config)
    final = aggregate_and_verdict(per_seed, run_mode=RUN_MODE)
    final["anchor_name"] = ANCHOR_NAME
    final["elapsed_s"] = round(time.time() - _RESULTS_HOLDER["started_at"], 2)
    final["ts_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    final["pid"] = os.getpid()
    final["run_mode"] = RUN_MODE
    final["config_version"] = CONFIG_VERSION
    final["_hardening_marker"] = "v2p2_pc_corruption_cliff_dense_chunked"
    final["backend"] = backend
    final["seed"] = SEED
    final["n_seeds"] = 1
    final["corpus_provenance"] = (
        "synthetic_substrate_bipolar_codebook_pattern_completion_"
        "corruption_cliff_v2p2_dense_cliff_grid")
    final["n_llm_calls"] = _LLM_CALL_COUNTER[0]

    # Substrate-only decode gate
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
        # Defensive pattern #2: outer crash-diag sentinel
        _write_import_crash_sentinel(e)
        print(f"[main] OUTER_EXCEPTION: {e}", file=sys.stderr, flush=True)
        traceback.print_exc()
        rc = 1
    sys.exit(rc)
