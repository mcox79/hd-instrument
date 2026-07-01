"""substrate_seqbind_N_dim_scaling_law_v1 sibling seed=13.

USER 2026-07-01 overnight priority: N dimensionality free-axis chain-grade
attempt (axis B). Sweep K-cliff at N in {2048, 4096, 8192, 16384};
verify linear scaling law K_cliff(N) = alpha * N.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
  - arms_differ_verified at smoke gate (META_RULE_AF)
  - final_metrics_atomicity = tmp_replace (META_RULE_AH)
  - except SystemExit: raise BEFORE except Exception (no BaseException; §8)
  - discriminator survives scale (smoke includes N=16384 preview; pattern C;
    v1.6 capped from N=32768 due to Windows-PyTorch allocator limit)
  - HARD_PASS strictly above floor (R2>=0.95 slope in [0.85,1.15]; META_RULE_L)
  - cardinality_ok for sweep-axis cell (META_RULE_H; N*K*arms)
  - per-unit failure-class via specific exception classes (META_RULE_J)
  - calibration_check = default_ok (inherits theta-gamma v2 regime)
  - positive control at N=8192 matches CG (META_RULE_BC + Gate D)
  - start_marker_written / crash_diagnostic_present / heartbeat_present (§13)

CHUNKED architecture: one seed per sibling file.
Sibling pair: seed_7, seed_19.

PROT-020: import torch present; routed to overnight_queue (GPU runner).
PROT-021: import _seed_checkpoint present (long-timeout compat).

PRE-REG: preregs/2026-06-30_substrate_seqbind_N_dim_scaling_law_v1.md

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

# v1.6: PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True is INERT on Windows
# (runtime UserWarning: expandable_segments not supported on this platform;
# our GPU host is RTX 4060 Ti / Windows). v1.3/1.5 chased a Linux fix on a
# Windows target. v1.6 caps N at 16384 in _core.py instead. Keeping this line
# commented for historical trail; do not re-enable without platform check.
# os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

import torch  # PROT-020 GPU-queue routing gate

from experiments._seed_checkpoint import (
    resumable_seeds, write_partial_key, aggregate_partials,
)
from experiments._cell_heartbeat import CellHeartbeat

SEED = 13
ANCHOR_NAME = f"substrate_seqbind_N_dim_scaling_law_v1_seed_{SEED}"

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
    f"arms=[SUBSTRATE,RANDOM],"
    f"N_sweep_full=[2048,4096,8192,16384],"
    f"N_sweep_smoke=[2048,8192,16384],"
    f"K_SEQ_full=[50,100,200,500,1000,2000,4000],"
    f"K_SEQ_smoke=[200,1000,4000],"
    f"ITEM_VOCAB=10000,POSITION_SLOTS=4096,NOISE_SIGMA=0.05,"
    f"SEED={SEED},mode={RUN_MODE},"
    f"expected_n_full=56,expected_n_smoke=18,"
    f"discriminator=log2_K_cliff_vs_log2_N_linear_fit,"
    f"HP_R2_FLOOR=0.95,HP_SLOPE=[0.85,1.15],MB_R2=0.80,MB_SLOPE=[0.70,1.30],"
    f"posctrl_N=8192,posctrl_log2_K_center=log2(1000),posctrl_tol=0.5,"
    f"hardening=L1startmarker+L2crashdiag+L3perseedckpt+L4heartbeat+CHUNKED_PER_SEED"
)

_RESULTS_HOLDER: Dict[str, Any] = {"started_at": time.time()}


def _atomic_write_metrics(out_dir: Path, payload: Dict[str, Any]) -> None:
    """Atomic tmp+os.replace write (META_RULE_AH)."""
    tmp = out_dir / "metrics.json.tmp"
    final = out_dir / "metrics.json"
    tmp.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    os.replace(tmp, final)


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
            "_hardening_marker": "v1_6_seqbind_N_dim_scaling_law_chunked_Ncap16384",
        }
        if extra:
            m.update(extra)
        _atomic_write_metrics(out_dir, m)
    except Exception as e:
        print(f"[_write_minimal_metrics] FAIL: {e}", file=sys.stderr, flush=True)


def _write_import_crash_sentinel(exc: BaseException) -> None:
    """§13.C crash diagnostic (Exception path; SystemExit / KI raised at outer)."""
    try:
        env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
        out_dir = REPO / "data" / ("exp_" + env_name)
        out_dir.mkdir(parents=True, exist_ok=True)
        s = {
            "anchor_name": ANCHOR_NAME,
            "verdict": "CELL_CRASHED",
            "verdict_msg": f"CELL_CRASHED: {type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}",
            "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 2),
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "traceback": traceback.format_exc()[:5000],
            "_hardening_marker": "v1_seqbind_N_dim_scaling_law_crash",
        }
        _atomic_write_metrics(out_dir, s)
        (out_dir / "import_crash.json").write_text(
            json.dumps(s, indent=2), encoding="utf-8")
    except Exception as e:
        print(f"[_write_import_crash_sentinel] FAIL: {e}",
              file=sys.stderr, flush=True)


def _write_start_marker(out_dir: Path, expected_n_units: int) -> None:
    """§13.B start marker."""
    try:
        import platform
        marker = {
            "pid": os.getpid(),
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "anchor_name": ANCHOR_NAME,
            "run_mode": RUN_MODE,
            "expected_n_units": expected_n_units,
            "host": platform.node(),
        }
        tmp = out_dir / "_start_marker.json.tmp"
        final = out_dir / "_start_marker.json"
        tmp.write_text(json.dumps(marker), encoding="utf-8")
        os.replace(tmp, final)
    except Exception as e:
        print(f"[_write_start_marker] FAIL: {e}", file=sys.stderr, flush=True)


def main() -> int:
    _RESULTS_HOLDER["started_at"] = time.time()
    # v1.6 diagnostic: PYTORCH_CUDA_ALLOC_CONF is now expected UNSET (Windows
    # does not support expandable_segments; v1.6 caps N at 16384 instead).
    # Keep the print so any future re-enable is visible in the log.
    print(
        f"[v1.6] PYTORCH_CUDA_ALLOC_CONF="
        f"{os.environ.get('PYTORCH_CUDA_ALLOC_CONF', '<unset>')} "
        f"(expected <unset> on Windows; v1.6 caps N at 16384)",
        flush=True,
    )
    env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    out_dir = REPO / "data" / ("exp_" + env_name)
    out_dir.mkdir(parents=True, exist_ok=True)

    from experiments._substrate_seqbind_N_dim_scaling_law_v1_core import (
        run_one_seed_scaling_sweep, aggregate_and_verdict, selftest,
        get_backend_label, _get_device,
        EXPECTED_N_UNITS_FULL, EXPECTED_N_UNITS_SMOKE,
    )

    expected_n = (EXPECTED_N_UNITS_SMOKE if SMOKE_MODE
                  else EXPECTED_N_UNITS_FULL)
    _write_start_marker(out_dir, expected_n)
    _write_minimal_metrics(
        out_dir, "STARTED",
        f"STARTED: pid={os.getpid()} mode={RUN_MODE} seed={SEED}",
        extra={"_phase": "init"},
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
    run_config = {"run_mode": RUN_MODE, "anchor": ANCHOR_NAME}
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
        with CellHeartbeat(out_dir, total_units=expected_n,
                           interval_s=30) as hb:
            result = run_one_seed_scaling_sweep(
                seed, run_mode=RUN_MODE, device=device, heartbeat=hb,
            )
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
    final["_hardening_marker"] = "v1_6_seqbind_N_dim_scaling_law_chunked_Ncap16384"
    final["backend"] = backend
    final["seed"] = SEED
    final["n_seeds"] = 1
    final["corpus_provenance"] = "synthetic_substrate_seqbind_N_dim_scaling_v1"

    _atomic_write_metrics(out_dir, final)
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
