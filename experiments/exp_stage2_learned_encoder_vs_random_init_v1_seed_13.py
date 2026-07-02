"""Stage 2/3 boundary cell v1: learned-encoder vs random-init, seed=7.

First substrate empirical test of trainable-pre-write encoding.
2 arms x 3 alpha x 2 noise = 12 units/seed at N=8192.
  ARMS = [RANDOM_INIT, LEARNED_CONTRASTIVE]
  FULL_ALPHA_SWEEP = [0.5, 1.5, 3.0]
  FULL_NOISE_SWEEP = [0.0, 0.30]

Symmetric HP/HF (per spawn prompt):
  HP_LEARNED_HIGHER_CAPACITY:   delta(top1) at (alpha=1.5, f=0.0) >= 0.10
  HP_LEARNED_HIGHER_NOISE_TOL:  delta(top1) at (alpha=0.5, f=0.30) >= 0.15
  HP_ORTHOGONALITY:             LEARNED_max_cos <= 0.20
  HF_LEARNED_WORSE:             LEARNED < RANDOM on >= 4/6 gates
  HF_LEARNED_EQUIVALENT:        |delta| < 0.03 on all gates

Prior work (R21_cross_modal_binding C.4): naive-CLIP-on-substrate declined
at P=5%; this cell probes the subtly-different pre-write-orthogonalization
path. HF_WORSE/EQUIVALENT closes R21's prediction positively with data;
HP opens gradient-through-write as Stage 2/3 pivot for M3.

CHUNKED: one seed per file. Siblings: seed_13, seed_19.
PROT-020: torch import present.
PROT-018: anchor _n8192 suffix binds to script FULL_N=8192.
Route: overnight_queue (GPU); timeout 7200s per USER spawn task.

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
ANCHOR_NAME = f"stage2_learned_encoder_vs_random_init_v1_n4096_seed_{SEED}"

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
    f"arms=[RANDOM_INIT,LEARNED_CONTRASTIVE],"
    f"M_sweep_full=[4000,8000,12000,16000],M_sweep_smoke=[8000],"
    f"discriminator_metric=cos05_at_M8000_f0.00,"
    f"noise_sweep_full=[0.0,0.30],noise_sweep_smoke=[0.0],"
    f"N_full=4096,N_smoke=4096,"
    f"metric_gates=[top1,top5,top10,top50,cos05,cos08],"
    f"SEED={SEED},mode={RUN_MODE},"
    f"learned_n_steps_full=500,learned_n_steps_smoke=100,"
    f"learned_lr=0.01,learned_margin=0.10,learned_lambda_pos=0.5,"
    f"learned_aug_flip=0.01,"
    f"HP_LEARNED_HIGHER_CAPACITY_DELTA=0.10,"
    f"HP_LEARNED_HIGHER_NOISE_TOL_DELTA=0.15,"
    f"HP_ORTHOGONALITY_MAX_COS=0.20,"
    f"HF_LEARNED_WORSE_GATE_COUNT=4/6,"
    f"HF_LEARNED_EQUIVALENT_DELTA=0.03,"
    f"cv_hp=0.10,cv_mb=0.15,"
    f"compose=inline_hebbian_W+encoder_only_contrastive_SGD,"
    f"hardening=L1startmarker+L2crashdiag+CHUNKED_PER_SEED+arms_must_differ+atomic_metrics"
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
            "_hardening_marker": "v1_stage2_learned_encoder_vs_random_init_chunked",
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
            "_hardening_marker": "v1_stage2_learned_encoder_vs_random_init_import_crash",
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

    from experiments._stage2_learned_encoder_vs_random_init_v1_core import (
        run_one_seed_all_units, aggregate_and_verdict, selftest,
        _get_device, ARMS,
        FULL_M_SWEEP, SMOKE_M_SWEEP, FULL_NOISE_SWEEP, SMOKE_NOISE_SWEEP,
        FULL_N, SMOKE_N,
    )

    device = _get_device(strict_gpu=False)
    backend = "cuda" if device.type == "cuda" else "cpu"
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
                  "N": (SMOKE_N if SMOKE_MODE else FULL_N),
                  "M_sweep": (SMOKE_M_SWEEP if SMOKE_MODE else FULL_M_SWEEP),
                  "noise_sweep": (SMOKE_NOISE_SWEEP if SMOKE_MODE else FULL_NOISE_SWEEP)}
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
    final["_hardening_marker"] = "v1_stage2_learned_encoder_vs_random_init_chunked"
    final["backend"] = backend
    final["seed"] = SEED
    final["n_seeds"] = 1
    final["corpus_provenance"] = (
        "synthetic_bipolar_M_sweep_N4096_v1_"
        "M_sweep_4000_8000_12000_16000_noise_sweep_0.0_0.30_"
        "arms_RANDOM_INIT_and_LEARNED_CONTRASTIVE_encoder_only"
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
