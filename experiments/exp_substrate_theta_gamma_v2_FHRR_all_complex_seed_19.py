"""substrate_theta_gamma_v2_FHRR_all_complex sibling seed=19.

Theta-gamma phase binding v2: ALL-COMPLEX FHRR codebook end-to-end.

v1 honest-aborted at smoke (hybrid bipolar+phase semantics broke).
v2 redesign per design spec:
  notes/director_theta_gamma_v2_FHRR_all_complex_design_spec_2026-06-30.md

5 arms:
  - NO_POSITION             (chance baseline; bundle items only)
  - CYCLIC_SHIFT            (v1 bipolar real-valued baseline)
  - FHRR_FLAT_PHASE_8       (FHRR all-complex; 8 positions)
  - FHRR_FLAT_PHASE_32      (FHRR all-complex; 32 positions)
  - FHRR_NESTED_THETA_GAMMA (nested theta(8) x gamma(8) = 64 positions)

Regime (anti-saturation per v1 lessons):
  N_DIM = 4096, ITEM_VOCAB = 10000, NOISE_SIGMA = 0.05
  K_SEQ sweep = [50, 100, 200, 500, 1000, 2000]

Cardinality (per seed):
  FULL : 5 arms * 6 K_SEQ = 30 phase points
  SMOKE: 5 arms * 4 K_SEQ = 20 phase points

PROT-018: anchor has no _n suffix (sweep is along K_SEQ; N_DIM=4096 fixed).
PROT-020: `import torch` present; routed to overnight_queue (GPU runner).

Sibling pair: seed_7, seed_13.

CHUNKED architecture (USER 2026-06-28): one seed per sibling file.

4 defensive patterns (USER 2026-06-28):
  1. STARTED metrics written before any heavy work
  2. crash-diag: outer try -> import-crash sentinel
  3. per-seed checkpoint via _seed_checkpoint
  4. per-phase-point heartbeat

ASCII-only. No unicode. No em-dashes. No emojis.

Author: exp_dev 2026-06-30 (Opus 4.7 1M, agent-spawn)
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

SEED = 19
ANCHOR_NAME = f"substrate_theta_gamma_v2_FHRR_all_complex_seed_{SEED}"

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
    f"K_SEQ_full=[50,100,200,500,1000,2000],"
    f"K_SEQ_smoke=[50,100,200,500],"
    f"N_DIM=4096,ITEM_VOCAB=10000,POSITION_NESTED=64,NOISE_SIGMA=0.05,"
    f"SEED={SEED},mode={RUN_MODE},"
    f"expected_n_full=30,expected_n_smoke=20,"
    f"discriminator=fhrr_vs_cyclic_log2_delta_and_nested_vs_flat32_log2_delta,"
    f"HP_FHRR_VS_CYCLIC_LOG2_DELTA=0.3,HP_CROSS_ARM_LOG2_DELTA=0.1,"
    f"HP_PAIRS_DIFFER_full=9_of_10,smoke=4_of_10,"
    f"hardening=L1startmarker+L2crashdiag+L3perunitckpt+L4heartbeat+CHUNKED_PER_SEED"
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
            "_hardening_marker": "v2_theta_gamma_FHRR_all_complex_chunked",
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
            "_hardening_marker": "v2_theta_gamma_FHRR_all_complex_import_crash",
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

    from experiments._substrate_theta_gamma_v2_FHRR_all_complex_core import (
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
    final["_hardening_marker"] = "v2_theta_gamma_FHRR_all_complex_chunked"
    final["backend"] = backend
    final["seed"] = SEED
    final["n_seeds"] = 1
    final["corpus_provenance"] = (
        "synthetic_substrate_theta_gamma_FHRR_all_complex_v2_K_SEQ_phase_diagram"
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
