"""sparsity_free_axis_v1 sibling seed=13.

Axis C sparsity as FREE axis at HRR-real chain-grade default; regime SWEPT
(PC single-bank + WM multi-bank K=500 B=16). Wave-2 gap analysis section 3
(CG=0.50, HIGH payoff, sparse-coding scope-expansion bonus).

Design:
    6 sparsity alpha x 2 regimes (PC + WM) x 3 seeds = 12 phase pts per seed FULL.
    Smoke: 6 alpha x PC only = 6 corner points per seed.

Sparsity levels (axis C):
    FULL:  {0.005, 0.010, 0.025, 0.050, 0.100, 0.200}
    SMOKE: same 6 (PC-only smoke)

Regimes:
    PC: M=100 items, c=0.485 (cliff-K MEASURED@2daf9b55), T=5
    WM: K=500 keys x B=16 banks, c=0.30, T=3

Fixed:
    N=8192, encoder=hrr_real (chain-grade default), binding=Hadamard

Discriminator (HP band; META_RULE_L band-floor MB):
    HP_A: sparsity_range >= 0.10 in >=1 regime
    HP_B: monotonicity |Spearman rho| >= 0.80 in >=1 regime (HP-critical)
    HP_C: 3-seed cv <= 0.10 per point
    HP_D: cardinality_ok
    HP_E: baseline_in_band

Positive control (META_RULE_BC):
    PC hrr_real @ alpha=0.10 M=100 c=0.485: top1 in [0.30, 0.90]
    WM hrr_real @ alpha=0.10 K=500 B=16 c=0.30: bank-avg top1 in [0.20, 0.80]

CHUNKED architecture (USER 2026-06-28): one seed per sibling file.
Sibling pair: seed_7, seed_19.

PRE-REG: preregs/2026-07-01_sparsity_free_axis_v1.md
CARDINALITY_OK_FULL: 12 phase points per seed
CARDINALITY_OK_SMOKE: 6 corner points per seed

PROT-018: anchor has _n8192 suffix (single-N cell).
PROT-019: _n8192 requires --timeout >= 3600s.

4 defensive patterns (USER 2026-06-28 hardening):
  1. start_marker: STARTED metrics written before any heavy work
  2. crash-diag: outer try -> import-crash sentinel with full traceback
  3. per-unit checkpoint: write_partial_key per seed via _seed_checkpoint
  4. heartbeat: per-phase-point flush print

ASCII-only. No unicode. No em-dashes. No emojis.
Author: hdi_exp_dev 2026-07-01 (Opus 4.7 1M, agent-spawn; wave-2 section 3)
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

import torch  # noqa: F401  PROT-020 GPU-eligibility scan

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    resumable_seeds, write_partial_key, aggregate_partials,
)

SEED = 13
ANCHOR_NAME = f"sparsity_free_axis_v1_n8192_seed_{SEED}"

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
    f"ANCHOR={ANCHOR_NAME},encoder=hrr_real,"
    f"sparsity=[0.005,0.010,0.025,0.050,0.100,0.200],"
    f"regimes=[PC,WM],N=8192,SEED={SEED},mode={RUN_MODE},"
    f"pc_M=100,pc_c=0.485,pc_T=5,wm_K=500,wm_B=16,wm_c=0.30,wm_T=3,beta=8.0,"
    f"arms=[MECHANISM,RANDOM_FLOOR],"
    f"expected_n_full=12,expected_n_smoke=6,"
    f"design_kind=SPARSITY_FREE_AXIS_REGIME_SWEPT,"
    f"parent_refs=[batch_A_x_C_v2_CG,PC_v2p2_dense_cliff_c0.485,WM_multibank_K500],"
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
            "_hardening_marker": "v1_sparsity_free_axis_chunked",
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
            "_hardening_marker": "v1_sparsity_free_axis_import_crash",
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

    from experiments._sparsity_free_axis_v1_core import (
        run_one_seed_phase_diagram, aggregate_and_verdict, selftest,
        get_backend_label,
        N_DIM_FULL,
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

    # GPU mandate NOT applied: this cell is CPU-eligible per wave-2 section 3
    # ("CPU-eligible (numpy)"). Route via remote_cpu_queue or local_cpu_queue.

    seeds_list = [SEED]
    run_config = {"N": N_DIM_FULL, "run_mode": RUN_MODE, "anchor": ANCHOR_NAME}
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
        result["N"] = N_DIM_FULL
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
    final["_hardening_marker"] = "v1_sparsity_free_axis_chunked"
    final["backend"] = backend
    final["seed"] = SEED
    final["n_seeds"] = 1
    final["N"] = N_DIM_FULL
    final["corpus_provenance"] = "synthetic_sparsity_free_axis_v1"
    final["n_llm_calls"] = _LLM_CALL_COUNTER[0]
    final["design_kind"] = "SPARSITY_FREE_AXIS_REGIME_SWEPT"

    assert _LLM_CALL_COUNTER[0] == 0, \
        "LLM_CALL_GATE_BREACH: substrate-only required"

    tmp_path = out_dir / "metrics.json.tmp"
    final_path = out_dir / "metrics.json"
    tmp_path.write_text(json.dumps(final, indent=2, default=str), encoding="utf-8")
    os.replace(tmp_path, final_path)
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
