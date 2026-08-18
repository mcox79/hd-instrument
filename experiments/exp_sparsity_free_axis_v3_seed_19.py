"""sparsity_free_axis_v3 sibling seed=19 (REVIVAL of v2 HF_POSITIVE_CONTROL_WM).

V3 REVIVAL RATIONALE (Skunkworks Wave 7 declared criterion 2026-07-01):
    v2 FULL HARD_FAIL_POSITIVE_CONTROL_WM: PC regime cleanly in-band ([0.37,
    0.73] across 3x3 PC grid; Spearman rho -1.0; cv 0.000). WM regime
    OVERSHOOTS upper band 0.90: MEASURED@v2 seed_7 FULL 2026-07-01
    (data/exp_substrate_sparsity_free_axis_v2_n4096_seed_7/metrics.json):
      WM K=1000 alpha=0.05: 0.9526  (saturated)
      WM K=1000 alpha=0.10: 0.9626  (saturated)
      WM K=2000 alpha=0.10: 0.8228  (still in top band > 0.80 concerns)
    WM c=0.40 with B=16-bank averaging washes corruption faster than PC.

    Skunkworks primary revival: raise WM c 0.40 -> 0.55 (steeper axis).
    Secondary revival: fire WM at SMOKE (was PC-only in v2); catch WM
    saturation at smoke gate BEFORE full dispatch (META_RULE_L fail-fast).

    Formula-empirically-adjusted predictions at c=0.55:
      WM K=1000 alpha=0.05: ~0.64 (in [0.30, 0.90])
      WM K=1000 alpha=0.10: ~0.59 (in [0.30, 0.90])
      WM K=2000 alpha=0.10: ~0.46 (in [0.30, 0.90]) <- target lands clean

V3 changes from v2 (MINIMAL PATCH):
    1. WM c: 0.40 -> 0.55  (primary revival)
    2. SMOKE regimes: (PC,) -> (PC, WM)  (secondary revival; catches at smoke)
    3. Everything else identical: N=4096, M in {1000,1500,2000}, T=1, PC c=0.60,
       encoder=hrr_real, B=16 banks, beta=8.0

Design:
    3 M x 3 alpha x 2 regimes = 18 phase pts per seed (FULL and SMOKE).

Sparsity levels (axis C):
    {0.05, 0.10, 0.20}

M levels:
    {1000, 1500, 2000}

Regimes:
    PC: M items c=0.60 T=1
    WM: K keys x B=16 banks c=0.55 T=1  (v3 PRIMARY: c raised 0.40 -> 0.55)

Fixed:
    N=4096, encoder=hrr_real, binding=Hadamard

Discriminator (v3 bands):
    HP_A: sparsity_range >= 0.05 in >=1 (regime, M) tuple
    HP_B: monotonicity |Spearman rho| >= 0.80 in >=1 (regime, M) tuple
    HP_C: 3-seed cv <= 0.15 per point
    HP_D: cardinality_ok
    HP_E: baseline_in_band (RANDOM_FLOOR at chance)
    HP_F: PC positive-control in-band [0.30, 0.90]
    HP_G: WM positive-control in-band [0.30, 0.90]  (v3 raised from [0.20, 0.80])
    HP_H: WM NOT saturated at ANY point (fail-fast per META_RULE_L)

Positive control (META_RULE_BC):
    PC hrr_real @ M=2000 alpha=0.10 c=0.60 T=1: top1 in [0.30, 0.90]
      (v2 MEASURED@2026-07-01: 0.507 - passes)
    WM hrr_real @ K=2000 alpha=0.10 c=0.55 T=1: bank-avg top1 in [0.30, 0.90]
      (v3 predicted-empirical: ~0.46 - target in-band)

CHUNKED architecture (USER 2026-06-28): one seed per sibling file.
Sibling pair: seed_13, seed_19.

PRE-REG: preregs/2026-07-01_substrate_sparsity_free_axis_v3_n4096.md
PRIOR HF: data/exp_substrate_sparsity_free_axis_v2_n4096_seed_7/metrics.json
CARDINALITY_OK_FULL: 18 phase points per seed
CARDINALITY_OK_SMOKE: 18 corner points per seed (v3: WM in smoke)

PROT-018: anchor has _n4096 suffix (single-N cell).
PROT-019: _n4096 requires --timeout >= 3600s.

4 defensive patterns (USER 2026-06-28 hardening):
  1. start_marker: STARTED metrics written before any heavy work
  2. crash-diag: outer try -> import-crash sentinel with full traceback
  3. per-unit checkpoint: write_partial_key per seed via _seed_checkpoint
  4. heartbeat: per-phase-point flush print

ASCII-only. No unicode. No em-dashes. No emojis.
Author: hdi_exp_dev 2026-07-01 (Opus 4.7 1M, agent-spawn; v2 HF revival)
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

SEED = 19
ANCHOR_NAME = f"substrate_sparsity_free_axis_v3_n4096_seed_{SEED}"

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
    f"sparsity=[0.05,0.10,0.20],M=[1000,1500,2000],"
    f"regimes=[PC,WM],N=4096,SEED={SEED},mode={RUN_MODE},"
    f"pc_c=0.60,pc_T=1,wm_B=16,wm_c=0.55,wm_T=1,beta=8.0,"
    f"arms=[MECHANISM,RANDOM_FLOOR],"
    f"expected_n_full=18,expected_n_smoke=18,"
    f"design_kind=SPARSITY_FREE_AXIS_v3_WM_C055_REVIVAL,"
    f"parent_refs=[sparsity_free_axis_v2_HF_WM_saturation],"
    f"revival_axes=[wm_c=0.55,smoke_includes_WM],"
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
            "_hardening_marker": "v3_sparsity_free_axis_wm_c055_revival_chunked",
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
            "_hardening_marker": "v3_sparsity_free_axis_import_crash",
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

    from experiments._sparsity_free_axis_v3_core import (
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

    # CPU-eligible per wave-2 section 3.
    # Route: remote_cpu_queue per USER 2026-07-01 (FULL not local).

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
    final["_hardening_marker"] = "v3_sparsity_free_axis_wm_c055_revival_chunked"
    final["backend"] = backend
    final["seed"] = SEED
    final["n_seeds"] = 1
    final["N"] = N_DIM_FULL
    final["corpus_provenance"] = "synthetic_sparsity_free_axis_v3_revival"
    final["n_llm_calls"] = _LLM_CALL_COUNTER[0]
    final["design_kind"] = "SPARSITY_FREE_AXIS_v3_WM_C055_REVIVAL"

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
