"""substrate_cleanup_family_wm_kcliff_v2_arm4_b3k3 sibling seed=13.

CLEANUP-FAMILY phase diagram at WM K-cliff regime, ARM4 design:
  4 cleanups (classical_hopfield / modern_hopfield_continuous /
              iterative_attractor / wta_baseline)
  x 3 num_banks {4, 16, 64}
  x 3 K per B (K_cliff/2, K_cliff, 2*K_cliff)  where K_cliff(B) = 256*B
  N=8192, 3 seeds x 36 pts

Per Research phase-diagram gap analysis (a36917be, notes/research_phase_diagram_
gap_analysis_next_cells_2026-07-01.md sec 1). CG=0.55, HIGH, 5x-drill-eligible
if HP.

PRE-REG: preregs/2026-07-01_substrate_cleanup_family_WM_K_cliff_v1.md
CARDINALITY_OK_FULL:  36 per seed
CARDINALITY_OK_SMOKE:  8 per seed

Task literal name "v1"; anchor slug uses "v2_arm4_b3k3" to avoid data-dir
collision with prior:
  * v1 (2026-06-30, N=8192 num_banks=16, OOM'd on GPU)
  * v1p1 (2026-06-30, N=4096 num_banks=8, MIDDLE_BAND with 5-arm no_cleanup+kNN set)

CHUNKED architecture: one seed per sibling file. Sibling pair: seed_7, seed_19.

4 defensive patterns (USER 2026-06-28):
  1. start_marker: STARTED metrics before any heavy work
  2. crash-diag: outer try -> import-crash sentinel with full traceback
  3. per-unit checkpoint: write_partial_key per seed
  4. heartbeat: per-phase-point flush print

GPU MANDATE (Fix #24): torch.cuda required for full; smoke + local_cpu_queue OK on CPU.

ASCII-only.
Author: exp_dev 2026-07-01 (Opus 4.7 1M).
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

import torch  # noqa: F401  -- PROT-020 GPU-eligibility scan marker

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    resumable_seeds, write_partial_key, aggregate_partials,
)

SEED = 13
ANCHOR_NAME = f"substrate_cleanup_family_wm_kcliff_v2_arm4_b3k3_seed_{SEED}"

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
    f"cleanups=[classical_hopfield,modern_hopfield_continuous,"
    f"iterative_attractor,wta_baseline],"
    f"encoder=bipolar,N=8192,SEED={SEED},mode={RUN_MODE},"
    f"num_banks_full=[4,16,64],num_banks_smoke=[4],"
    f"K_design=Kcliff_relative_over2_1_times2_per_B,"
    f"K_cliff_formula=256*B,beta=8.0,hop_max_steps=4,"
    f"expected_n_full=36,expected_n_smoke=8,"
    f"discriminator=K_2xKcliff_lift_gte_0p10_over_wta_cv_lt_0p08,"
    f"META_RULE_AX_all_6_pairs_distinct,"
    f"META_RULE_Q_suspect_1p000_at_Kcliff,"
    f"META_RULE_AT_compose_multi_bank_alpha_K"
)

_RESULTS_HOLDER: Dict[str, Any] = {"started_at": time.time()}
_LLM_CALL_COUNTER = [0]


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
            "_hardening_marker": "v2_arm4_b3k3_cleanup_family_wm_kcliff",
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
            "_hardening_marker": "v2_arm4_b3k3_import_crash",
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

    from experiments._substrate_cleanup_family_wm_kcliff_v2_arm4_b3k3_core import (
        run_one_seed_phase_diagram, aggregate_and_verdict, selftest,
        get_backend_label, N_DIM_FULL, N_DIM_SMOKE,
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

    queue_name = os.environ.get("HDLAB_QUEUE", "").lower()
    if (not SMOKE_MODE) and (queue_name != "local_cpu_queue") and (backend == "torch.cpu"):
        _write_minimal_metrics(out_dir, "HARD_FAIL_NO_GPU",
                               f"HARD_FAIL_GPU_MANDATE: full requires cuda (backend={backend} "
                               f"queue={queue_name}); Fix #24")
        print(f"[gpu-mandate] HARD_FAIL: full requires cuda; backend={backend}",
              flush=True)
        return 1

    seeds_list = [SEED]
    N_max = N_DIM_SMOKE if SMOKE_MODE else N_DIM_FULL
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
        result["N"] = N_max
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
    final["_hardening_marker"] = "v2_arm4_b3k3_cleanup_family_wm_kcliff"
    final["backend"] = backend
    final["seed"] = SEED
    final["n_seeds"] = 1
    final["corpus_provenance"] = "synthetic_substrate_bipolar_multibank_wm_kcliff_arm4"
    final["n_llm_calls"] = _LLM_CALL_COUNTER[0]

    assert _LLM_CALL_COUNTER[0] == 0, \
        "LLM_CALL_GATE_BREACH: substrate-only required"

    (out_dir / "metrics.json").write_text(
        json.dumps(final, indent=2, default=str), encoding="utf-8")
    print(f"[{ANCHOR_NAME}] DONE: {final['verdict_msg']}", flush=True)
    print(f"[{ANCHOR_NAME}] cardinality observed={final.get('observed_n_units_per_seed')} "
          f"expected={final.get('expected_n_units_per_seed')} "
          f"ok={final.get('cardinality_ok_per_seed')}", flush=True)
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
