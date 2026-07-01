"""theta_gamma_v4_extended_seeds_gpu sibling seed=7.

Theta-gamma v4 revival (2x-drill negative recovery per USER 2026-07-01).
v3 (2026-07-01) tiered MEASURED_MECHANISM: FLAT_32 seed 7 broke unanimity
gate (nested_vs_flat32_log2_delta=0.0 because FLAT_32 cliff hit K=100 like
NESTED, while seeds 13/19 had FLAT_32 cliff K=50).

v4 revives with:
  1. 7 seeds {7, 13, 19, 23, 29, 31, 37} (extends v3's 3 seeds).
  2. Finer K-grid around cliff: K in {50, 75, 100, 125, 150, 175, 200,
     500, 1000, 2000, 5000}.
  3. Relaxed HP: NESTED_vs_FLAT32 >=0.1 required at >=5/7 seeds (majority,
     not unanimity).
  4. HP_FLAT_32_CLIFF_DISTRIBUTION: cv <= 0.15 OR bimodal-atomized (accept
     either as HP).

5 arms (same as v3): NO_POSITION, CYCLIC_SHIFT, FHRR_FLAT_PHASE_8,
FHRR_FLAT_PHASE_32, FHRR_NESTED_THETA_GAMMA.

Regime (LOCKED, same as v3):
  N_DIM = 16384, ITEM_VOCAB = 10000, NOISE_SIGMA = 0.05
  K_SEQ_FULL = [50, 75, 100, 125, 150, 175, 200, 500, 1000, 2000, 5000]
  K_SEQ_SMOKE = [50, 100, 200]

Cardinality (per seed):
  FULL : 5 * 11 = 55 phase points
  SMOKE: 5 * 3 = 15 phase points

PROT-018: anchor has _N16384 suffix (uppercase N; matches v3 convention).
PROT-020: `import torch` present; routed to overnight_queue (GPU runner).

Sibling pair: seed_13, seed_19, seed_23, seed_29, seed_31, seed_37.

CHUNKED architecture (USER 2026-06-28): one seed per sibling file.

4 defensive patterns (USER 2026-06-28):
  1. STARTED metrics written before any heavy work
  2. crash-diag: outer try -> import-crash sentinel
  3. per-seed checkpoint via _seed_checkpoint
  4. per-phase-point heartbeat

ASCII-only. No unicode. No em-dashes. No emojis.

Author: exp_dev 2026-07-01 (Opus 4.7 1M, agent-spawn).
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

import torch  # PROT-020 GPU-queue routing gate

from experiments._seed_checkpoint import (
    resumable_seeds, write_partial_key, aggregate_partials,
)

SEED = 13
ANCHOR_NAME = f"theta_gamma_v4_extended_seeds_gpu_seed_{SEED}_N16384"

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
    f"arms=[NO_POSITION,CYCLIC_SHIFT,FHRR_FLAT_8,FHRR_FLAT_32,FHRR_NESTED_8x8],"
    f"K_SEQ_full=[50,75,100,125,150,175,200,500,1000,2000,5000],"
    f"K_SEQ_smoke=[50,100,200],"
    f"N_DIM=16384,ITEM_VOCAB=10000,POSITION_NESTED=64,NOISE_SIGMA=0.05,"
    f"SEED={SEED},mode={RUN_MODE},"
    f"expected_n_full=55,expected_n_smoke=15,"
    f"discriminator=fhrr_vs_cyclic_and_nested_vs_flat32_and_flat32_cliff_dist_across_7_seeds,"
    f"HP_FHRR_VS_CYCLIC_LOG2_DELTA=1.5,HP_CROSS_ARM_LOG2_DELTA=0.1,"
    f"HP_NESTED_VS_FLAT32_MAJORITY=5_of_7,HP_FLAT_32_CV_TIGHT=0.15,"
    f"HP_PAIRS_DIFFER_full=9_of_10,smoke=4_of_10,"
    f"hardening=L1startmarker+L2crashdiag+L3perunitckpt+L4heartbeat+CHUNKED_PER_SEED,"
    f"revival_of=theta_gamma_v3_N16384_gpu"
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
            "_hardening_marker": "v4_theta_gamma_extended_seeds_gpu_chunked",
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
            "_hardening_marker": "v4_theta_gamma_extended_seeds_gpu_import_crash",
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

    from experiments._substrate_theta_gamma_v4_extended_seeds_gpu_core import (
        run_one_seed_phase_diagram, aggregate_and_verdict, selftest,
        get_backend_label, N_DIM, _get_device,
    )

    strict_gpu = (RUN_MODE == "full")
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
    run_config = {"N": N_DIM, "run_mode": RUN_MODE, "anchor": ANCHOR_NAME}
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
        result = run_one_seed_phase_diagram(
            seed, run_mode=RUN_MODE, device=device,
        )
        result["N"] = N_DIM
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
    final["_hardening_marker"] = "v4_theta_gamma_extended_seeds_gpu_chunked"
    final["backend"] = backend
    final["seed"] = SEED
    final["n_seeds"] = 1
    final["corpus_provenance"] = (
        "synthetic_theta_gamma_v4_extended_seeds_gpu_K_SEQ_phase_diagram"
    )
    final["n_llm_calls"] = _LLM_CALL_COUNTER[0]

    if _LLM_CALL_COUNTER[0] != 0:
        raise RuntimeError(
            f"LLM_CALL_GATE_BREACH: substrate-only required; "
            f"n_llm_calls={_LLM_CALL_COUNTER[0]}"
        )

    tmp = out_dir / "metrics.json.tmp"
    final_path = out_dir / "metrics.json"
    tmp.write_text(json.dumps(final, indent=2, default=str), encoding="utf-8")
    os.replace(tmp, final_path)
    print(f"[{ANCHOR_NAME}] DONE: {final['verdict_msg']}", flush=True)
    print(
        f"[{ANCHOR_NAME}] cardinality observed={final.get('observed_n_units')} "
        f"expected={final.get('expected_n_units')} "
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
