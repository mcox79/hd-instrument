"""Stage 2/3 boundary v2 (incremental checkpoint): learned vs random-init encoder, seed=7.

v1 (commit 48737275) TIMED OUT at 7200s on remote seed_7. v2 fixes:
FIX 1 -- per-arm incremental metrics.json checkpoint (SALVAGE_PARTIAL until
         complete; never lose completed arms).
FIX 2 -- grid reduced 2 arms x 3 M x 1 noise = 6 units/seed (down from 16).
FIX 3 -- SGD steps 500 -> 200 (empirical convergence flat by step 100).
FIX 4 -- timeout budget 14400s per USER course-correction.

Discriminator preserved: cos05 at M=12000 (mid-band 0.661 for RANDOM MEASURED@).

CHUNKED: one seed per file. Siblings: seed_13, seed_19.
PROT-020: torch import at top (Fix #24).
PROT-018: anchor _n4096 suffix binds to script FULL_N=4096.

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

SEED = 19
ANCHOR_NAME = f"stage2_learned_encoder_vs_random_init_v2_incremental_checkpoint_n4096_seed_{SEED}"

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
    f"M_sweep_full=[4000,8000,12000],M_sweep_smoke=[4000],"
    f"noise_sweep_full=[0.0],noise_sweep_smoke=[0.0],"
    f"N_full=4096,N_smoke=4096,"
    f"discriminator_metric=cos05_at_M12000_f0.00,"
    f"SEED={SEED},mode={RUN_MODE},"
    f"learned_n_steps_full=200,learned_n_steps_smoke=100,"
    f"learned_lr=0.02,learned_margin=0.05,learned_lambda_pos=0.5,"
    f"HP_LEARNED_HIGHER_CAPACITY_DELTA=0.10,"
    f"HP_ORTHOGONALITY_MAX_COS=0.20,"
    f"HF_LEARNED_WORSE_GATE_COUNT=4/6,"
    f"HF_LEARNED_EQUIVALENT_DELTA=0.03,"
    f"cv_hp=0.10,cv_mb=0.15,"
    f"hardening=L1startmarker+L2crashdiag+CHUNKED_PER_SEED+FIX1_per_arm_incremental_checkpoint+FIX2_reduced_grid+FIX3_200_sgd_steps+FIX4_14400s_timeout"
)

_RESULTS_HOLDER: Dict[str, Any] = {"started_at": time.time()}


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
            "_hardening_marker": "v2_incremental_checkpoint_import_crash",
        }
        tmp = out_dir / "metrics.json.tmp"
        final = out_dir / "metrics.json"
        tmp.write_text(json.dumps(s, indent=2), encoding="utf-8")
        os.replace(tmp, final)
    except Exception as e:
        print(f"[_write_import_crash_sentinel] FAIL: {e}",
              file=sys.stderr, flush=True)


def _write_start_marker(out_dir: Path, run_mode: str, expected_n_units: int) -> None:
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        marker = {
            "pid": os.getpid(),
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "anchor_name": ANCHOR_NAME,
            "run_mode": run_mode,
            "expected_n_units": expected_n_units,
            "seed": SEED,
        }
        tmp = out_dir / "_start_marker.json.tmp"
        final = out_dir / "_start_marker.json"
        tmp.write_text(json.dumps(marker), encoding="utf-8")
        os.replace(tmp, final)
    except Exception as e:
        print(f"[_write_start_marker] FAIL: {e}", file=sys.stderr, flush=True)


def main() -> int:
    _RESULTS_HOLDER["started_at"] = time.time()
    env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    out_dir = REPO / "data" / ("exp_" + env_name)
    out_dir.mkdir(parents=True, exist_ok=True)

    from experiments._stage2_learned_encoder_vs_random_init_v2_incremental_checkpoint_core import (
        run_one_seed_all_units, aggregate_and_verdict, selftest,
        _get_device, ARMS, get_backend_label,
        FULL_M_SWEEP, SMOKE_M_SWEEP, FULL_NOISE_SWEEP, SMOKE_NOISE_SWEEP,
        FULL_N, SMOKE_N,
    )

    device = _get_device(strict_gpu=False)
    backend = get_backend_label()
    N = SMOKE_N if SMOKE_MODE else FULL_N
    M_sweep = SMOKE_M_SWEEP if SMOKE_MODE else FULL_M_SWEEP
    noise_sweep = SMOKE_NOISE_SWEEP if SMOKE_MODE else FULL_NOISE_SWEEP
    expected_n_units = len(ARMS) * len(M_sweep) * len(noise_sweep)

    _write_start_marker(out_dir, RUN_MODE, expected_n_units)

    print(f"[{ANCHOR_NAME}] mode={RUN_MODE} seed={SEED} backend={backend} "
          f"device={device} expected_n_units={expected_n_units}", flush=True)

    if SELF_TEST_MODE:
        try:
            ok, msg = selftest(SEED, device=device)
            verdict = "SELFTEST_OK" if ok else "SELFTEST_FAIL"
            m = {
                "anchor_name": ANCHOR_NAME, "verdict": verdict,
                "verdict_msg": msg, "summary": msg[:400],
                "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 2),
                "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "pid": os.getpid(), "run_mode": RUN_MODE,
                "config_version": CONFIG_VERSION,
                "_hardening_marker": "v2_incremental_checkpoint_selftest",
                "backend": backend, "seed": SEED,
            }
            tmp = out_dir / "metrics.json.tmp"
            final = out_dir / "metrics.json"
            tmp.write_text(json.dumps(m, indent=2, default=str), encoding="utf-8")
            os.replace(tmp, final)
            print(f"[selftest] {verdict}: {msg}", flush=True)
            return 0 if ok else 1
        except Exception as e:
            print(f"[selftest] FAIL: {e}", file=sys.stderr, flush=True)
            traceback.print_exc()
            return 1

    # FULL/SMOKE run: incremental checkpoint after each arm
    t_start = _RESULTS_HOLDER["started_at"]
    result = run_one_seed_all_units(
        SEED, run_mode=RUN_MODE, device=device,
        out_dir=out_dir, anchor_name=ANCHOR_NAME,
        config_version=CONFIG_VERSION, backend=backend,
        t_start=t_start,
    )
    result["anchor_name"] = ANCHOR_NAME
    result["config_version"] = CONFIG_VERSION

    # Final aggregate + verdict write (final_complete)
    per_seed = [result]
    final = aggregate_and_verdict(per_seed, run_mode=RUN_MODE)
    final["anchor_name"] = ANCHOR_NAME
    final["elapsed_s"] = round(time.time() - _RESULTS_HOLDER["started_at"], 2)
    final["ts_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    final["pid"] = os.getpid()
    final["run_mode"] = RUN_MODE
    final["config_version"] = CONFIG_VERSION
    final["_hardening_marker"] = "v2_incremental_checkpoint_final_complete"
    final["backend"] = backend
    final["seed"] = SEED
    final["cell_version"] = "v2_incremental_checkpoint"
    final["checkpoint_kind"] = "final_complete"
    final["corpus_provenance"] = (
        "synthetic_bipolar_M_sweep_N4096_v2_"
        "M_sweep_4000_8000_12000_noise_0.0_"
        "arms_RANDOM_INIT_and_LEARNED_CONTRASTIVE_encoder_only"
    )

    tmp = out_dir / "metrics.json.tmp"
    final_path = out_dir / "metrics.json"
    tmp.write_text(json.dumps(final, indent=2, default=str), encoding="utf-8")
    os.replace(tmp, final_path)
    print(f"[{ANCHOR_NAME}] DONE: {final['verdict_msg']}", flush=True)
    print(f"[{ANCHOR_NAME}] cardinality observed={final.get('observed_n_units_per_seed')} "
          f"expected={final.get('expected_n_units_per_seed')} "
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
