"""sparsity_free_axis_v5_wm_fixed sibling seed=7.

V5 RATIONALE:
    v3 cell-author identified an ARCHITECTURAL BUG in v2/v3 shared core
    (_sparsity_free_axis_v2_core.py::_eval_wm_point): `vals_corr` computed
    at line 419 but NEVER used in readout; readout uses clean `bank_trace`.
    WM top1 insensitive to CORRUPTION_WM by construction.

    v5 FIX (Option A per prior cell-author): corrupt COMPOSED bank_trace
    before unbind so corruption enters retrieval pathway. Symmetric to PC
    regime (query corrupted; storage clean).

    v5 SCOPE: WM regime ONLY (PC already CG'd via v4). Provides symmetric
    characterization of WM sparsity axis + closes Atom 17 HF via
    architectural fix.

Design (LOCKED):
    3 M (1000, 1500, 2000) x 3 alpha (0.05, 0.10, 0.20) x 3 c (0.30, 0.45,
    0.55) x WM-only = 27 phase points per seed. SMOKE == FULL grid
    (DISCRIMINATOR-SURVIVES-SCALE).

Fixed:
    N=4096, encoder=hrr_real, B=16, T_cleanup=1, beta=8.0

Discriminator (v5 HP bands; META_RULE_L):
    HP_WM_MECHANISM_DISCRIMINATES: Spearman rho(c, top1) <= -0.60 at EVERY (M, alpha)
    HP_WM_IN_BAND_MID_C: top1 in [0.30, 0.90] at ALL 9 (M, alpha) at c=0.45
    HP_WM_CRUMBLE_AT_HIGH_C: top1 < 0.40 at >=5/9 (M, alpha) at c=0.55
    HP_CROSS_SEED_TIGHT: cross-seed cv < 0.15 per point
    HP_RANDOM_FLOOR: chance (< 0.05)
    HP_CARDINALITY: 27 points per seed
    HP_ARMS_DIFFER: mechanism vs random hash per point (META_RULE_AF)

Hard-fail classes:
    HF_STILL_SATURATED: fix didn't work (any (M, alpha) all c > 0.90)
    HF_ALL_CRUMBLE: c=0.30 top1 < 0.10 (base regime broken)
    HF_CARDINALITY_BREACH: observed < expected
    HF_POSITIVE_CONTROL: WM at (M=2000, alpha=0.10, c=0.45) outside [0.30, 0.90]
    HF_ARMS_IDENTICAL: arm bug

Positive control (META_RULE_BC):
    WM hrr_real @ M=2000 alpha=0.10 c=0.45 T=1 B=16 N=4096:
      THEORETICAL@formula pred~0.36
      HYPOTHESIZED@lift [0.00, 0.20] under fix
      HP band [0.30, 0.90]

CHUNKED architecture (USER 2026-06-28): one seed per sibling file.
Sibling pair: seed_13, seed_19.

PRE-REG: preregs/2026-07-01_substrate_sparsity_free_axis_v5_wm_fixed_n4096.md
PRIOR REFS:
  v2 HF: data/exp_substrate_sparsity_free_axis_v2_n4096_seed_7/metrics.json (WM saturation)
  v3 arch bug: notes/wm_readout_architectural_bug_deferred_v5_2026-07-01.md
  v4 PC CG: data/exp_substrate_sparsity_free_axis_v4_pc_only_n4096_seed_7/ (PC regime CG)

PROT-018: anchor has _n4096 suffix (single-N cell).
PROT-019: _n4096 requires --timeout >= 3600s.

4 defensive patterns (USER 2026-06-28 hardening):
  1. start_marker: STARTED metrics written before any heavy work
  2. crash-diag: outer try -> import-crash sentinel with full traceback
  3. per-unit checkpoint: write_partial_key per seed via _seed_checkpoint
  4. heartbeat: per-phase-point flush print

ASCII-only. No unicode. No em-dashes. No emojis.
Author: hdi_exp_dev 2026-07-01 (Opus 4.7 1M, agent-spawn; Option A fix)
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
ANCHOR_NAME = f"substrate_sparsity_free_axis_v5_wm_fixed_n4096_seed_{SEED}"

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
    f"sparsity=[0.05,0.10,0.20],M=[1000,1500,2000],c=[0.30,0.45,0.55],"
    f"regimes=[WM],N=4096,SEED={SEED},mode={RUN_MODE},"
    f"wm_B=16,wm_T=1,beta=8.0,"
    f"arms=[MECHANISM,RANDOM_FLOOR],"
    f"expected_n_full=27,expected_n_smoke=27,"
    f"design_kind=SPARSITY_FREE_AXIS_V5_WM_FIXED_OPTION_A,"
    f"parent_refs=[v2_HF_WM_saturation,v3_arch_bug_finding,v4_PC_CG],"
    f"fix_type=OPTION_A_corrupt_bank_trace_before_unbind,"
    f"WM_STATUS=FIXED_v5_bank_trace_corruption_enters_readout,"
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
            "_hardening_marker": "v5_sparsity_free_axis_wm_fixed_chunked",
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
            "_hardening_marker": "v5_sparsity_free_axis_wm_fixed_import_crash",
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

    from experiments._sparsity_free_axis_v5_wm_fixed_core import (
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
    final["_hardening_marker"] = "v5_sparsity_free_axis_wm_fixed_chunked"
    final["backend"] = backend
    final["seed"] = SEED
    final["n_seeds"] = 1
    final["N"] = N_DIM_FULL
    final["corpus_provenance"] = "synthetic_sparsity_free_axis_v5_wm_fixed"
    final["n_llm_calls"] = _LLM_CALL_COUNTER[0]
    final["design_kind"] = "SPARSITY_FREE_AXIS_V5_WM_FIXED_OPTION_A"

    assert _LLM_CALL_COUNTER[0] == 0, \
        "LLM_CALL_GATE_BREACH: substrate-only required"

    tmp_path = out_dir / "metrics.json.tmp"
    final_path = out_dir / "metrics.json"
    tmp_path.write_text(json.dumps(final, indent=2, default=str), encoding="utf-8")
    os.replace(tmp_path, final_path)
    print(f"[{ANCHOR_NAME}] DONE: {final['verdict_msg']}", flush=True)
    print(f"[{ANCHOR_NAME}] cardinality observed={final.get('observed_n_units')} "
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
