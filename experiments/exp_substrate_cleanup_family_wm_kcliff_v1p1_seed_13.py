"""substrate_cleanup_family_wm_kcliff_v1p1 sibling seed=13.

CLEANUP-FAMILY phase diagram in WM multi-bank K-cliff regime. 5 cleanup
primitives (no_cleanup, classical_hopfield, modern_hopfield_continuous,
iterative_attractor, k_NN_lookup) swept as OUTER axis over K_per_bank x
regime grid. Multi-bank: num_banks=8, N=4096 (full); N=4096 (smoke).

v1.1 memory-fit (2026-06-30): N_DIM 8192->4096, num_banks 16->8, chunked-K matmul
for cleanup_no_cleanup + k_NN_lookup, sequential per-arm GPU cache release.
Smoke at FULL N to verify DISCRIMINATOR-MUST-SURVIVE-SCALE.

Per Director spec: notes/director_cleanup_family_primitive_library_spec_2026-06-30.md

CHUNKED architecture (USER 2026-06-28): one seed per sibling file.
Sibling pair: seed_7, seed_19.

PRE-REG: preregs/2026-06-30_substrate_cleanup_family_wm_kcliff_v1p1.md
CARDINALITY_OK_FULL: 50 phase points per seed (5 cleanups x 5 K x 2 regimes)
CARDINALITY_OK_SMOKE: 15 corner points per seed (5 cleanups x 3 K x 1 regime)

PROT-018: anchor has no _n<N> suffix (multi-N config -- N=4096 full + smoke).
META_RULE_AY (proposed 2026-06-30 by Skunkworks): verdict-emitter HARD_FAILs
on self-reported distinctness=False. Prevents v1/v3 ANCHOR 4 dense-triplet
phantom-degeneracy pattern.

4 defensive patterns (USER 2026-06-28 hardening):
  1. start_marker: STARTED metrics written before any heavy work
  2. crash-diag: outer try -> import-crash sentinel with full traceback
  3. per-unit checkpoint: write_partial_key per seed via _seed_checkpoint
  4. heartbeat: per-phase-point flush print

GPU MANDATE (Fix #24): cuda required for full; matmul-bound (modern Hopfield
softmax-attention at N=4096 x M~8000 codebook); cell aborts to CPU only when
HDLAB_QUEUE=local_cpu_queue OR --smoke.

ASCII-only. No unicode. No em-dashes. No emojis.
Author: exp_dev 2026-06-30 (Opus 4.7 1M, agent-spawn).
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
ANCHOR_NAME = f"substrate_cleanup_family_wm_kcliff_v1p1_seed_{SEED}"

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
    f"cleanups=[no_cleanup,classical_hopfield,modern_hopfield_continuous,"
    f"iterative_attractor,k_NN_lookup],"
    f"encoder=bipolar,N_full=4096,N_smoke=4096,SEED={SEED},mode={RUN_MODE},"
    f"K_per_bank_full=[50,100,250,500,1000],K_per_bank_smoke=[50,100,250],"
    f"num_banks=8,regimes_full=[RANDOM,ADVERSARIAL],regimes_smoke=[RANDOM],"
    f"memory_fit=N4096_banks8_chunked_no_cleanup_perarm_release,"
    f"beta=8.0,hop_max_steps=4,"
    f"expected_n_full=50,expected_n_smoke=15,"
    f"META_RULE_AY=verdict_HARDFAIL_on_distinctness_false,"
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
            "_hardening_marker": "v1p1_cleanup_family_wm_kcliff_memory_fit",
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
            "_hardening_marker": "v1p1_cleanup_family_wm_kcliff_import_crash",
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

    from experiments._substrate_cleanup_family_wm_kcliff_v1p1_core import (
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

    # GPU mandate (Fix #24): full requires cuda; smoke + local_cpu_queue OK on CPU
    queue_name = os.environ.get("HDLAB_QUEUE", "").lower()
    if (not SMOKE_MODE) and (queue_name != "local_cpu_queue") and (backend == "torch.cpu"):
        _write_minimal_metrics(out_dir, "HARD_FAIL_NO_GPU",
                               f"HARD_FAIL_GPU_MANDATE: full requires cuda (backend={backend} "
                               f"queue={queue_name}); Fix #24")
        print(f"[gpu-mandate] HARD_FAIL: full requires cuda; backend={backend}",
              flush=True)
        return 1

    # Per-seed checkpoint resume
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
    final["_hardening_marker"] = "v1p1_cleanup_family_wm_kcliff_memory_fit"
    final["backend"] = backend
    final["seed"] = SEED
    final["n_seeds"] = 1
    final["corpus_provenance"] = "synthetic_substrate_bipolar_multibank_wm_kcliff"
    final["n_llm_calls"] = _LLM_CALL_COUNTER[0]

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
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_import_crash_sentinel(e)
        print(f"[main] OUTER_EXCEPTION: {e}", file=sys.stderr, flush=True)
        traceback.print_exc()
        rc = 1
    sys.exit(rc)
