"""substrate_binding_op_x_capacity_v1 sibling seed=7.

Cell #5 from Research 2026-07-01 phase-diagram gap analysis (axis D x O =
binding-op x capacity cross-product at WM regime). Tests whether binding-op
choice interacts with K_cliff-per-bank in WM multi-bank composition.

3 binding ops (Hadamard baseline + HRR-circular-conv + FHRR-complex-mul):
  HADAMARD_BIND / CIRCULAR_CONV_HRR / FHRR_COMPLEX_MUL

Regime: N_DIM=8192 fixed; B=16 banks; alpha sweep {0.1, 0.5, 0.9}
  M-per-bank = alpha * K_CLIFF_HADAMARD_REF (=500)
  -> M-per-bank in {50, 250, 450}
  n_q_full=30, n_q_smoke=5

CARDINALITY_OK_FULL: 9 phase points per seed (3 ops x 3 alpha)
CARDINALITY_OK_SMOKE: 3 phase points per seed (3 ops x 1 alpha=0.5)

CHUNKED architecture: one seed per sibling file. Sibling pair: seed_13, seed_19.

PRE-REG: preregs/2026-07-01_substrate_binding_op_x_capacity_v1.md

Defensive patterns (META_RULE §13 + canonical exp_dev.md):
  L1: start_marker (STARTED metrics before heavy work)
  L2: crash-diag with full traceback (except Exception, NOT BaseException)
  L3: per-seed checkpoint via _seed_checkpoint
  L4: periodic heartbeat via per-phase-point print-flush

PROT-018: no _n<N> suffix (all phase points at fixed N_DIM=8192).
PROT-019: no _n>=4096 suffix -> no timeout floor.

CPU-eligible: numpy + torch (CPU path OK per Research spec MEDIUM CG=0.30).

ASCII-only. No unicode. No em-dashes. No emojis.
Author: exp_dev 2026-07-01 (Opus 4.7 1M, agent-spawn) Cell #5 Research spec.
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

import torch  # noqa: F401  -- PROT-020 gate marker

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    resumable_seeds, write_partial_key, aggregate_partials,
)

SEED = 7
ANCHOR_NAME = f"substrate_binding_op_x_capacity_v1_seed_{SEED}"

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
    f"bindings=[HADAMARD_BIND,CIRCULAR_CONV_HRR,FHRR_COMPLEX_MUL],"
    f"N_DIM=8192,B_BANKS=16,SEED={SEED},mode={RUN_MODE},"
    f"K_CLIFF_HADAMARD_REF=1500,"
    f"ALPHA_FULL=[0.1,0.5,0.9],ALPHA_SMOKE=[0.5],"
    f"n_q_full=30,n_q_smoke=20,V_ITEMS=8000,V_POS=8000,beta=8.0,"
    f"expected_n_full=9,expected_n_smoke=3,"
    f"discriminator=K_cliff_shift_ge_15pct_from_hadamard_at_alpha_0p5,"
    f"bands=SAT0.90_MB[0.30,0.70]_FLOOR0.10,"
    f"hardening=L1startmarker+L2crashdiag_exceptException+L3perunitckpt+L4heartbeat+CHUNKED_PER_SEED"
)

_RESULTS_HOLDER: Dict[str, Any] = {"started_at": time.time()}
_LLM_CALL_COUNTER = [0]


def _write_minimal_metrics(out_dir: Path, verdict: str, verdict_msg: str,
                            extra: Dict[str, Any] = None) -> None:
    """Defensive pattern L1+L2: start_marker / intermediate phase markers."""
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
            "_hardening_marker": "v1_binding_op_x_capacity_chunked",
        }
        if extra:
            m.update(extra)
        (out_dir / "metrics.json").write_text(
            json.dumps(m, indent=2, default=str), encoding="utf-8")
    except Exception as e:
        print(f"[_write_minimal_metrics] FAIL: {e}", file=sys.stderr, flush=True)


def _write_import_crash_sentinel(exc: Exception) -> None:
    """Defensive pattern L2: crash-diag sentinel with full traceback.

    NOTE: signature uses Exception (not BaseException) per §8 of canonical
    instruction file -- never swallow SystemExit / KeyboardInterrupt.
    """
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
            "_hardening_marker": "v1_binding_op_x_capacity_import_crash",
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

    from experiments._substrate_binding_op_x_capacity_v1_core import (
        run_one_seed_binding_op_x_capacity, aggregate_and_verdict, selftest,
        get_backend_label, N_DIM, B_BANKS, ALPHA_FULL, ALPHA_SMOKE,
        K_CLIFF_HADAMARD_REF,
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

    # CPU-eligibility (Research spec: MEDIUM cell, CPU OK). No GPU mandate on
    # this cell; runs fine on either backend.

    # Per-seed checkpoint resume (PROT-021 config mismatch guard)
    seeds_list = [SEED]
    run_config = {"N": N_DIM, "run_mode": RUN_MODE, "anchor": ANCHOR_NAME}
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
        result = run_one_seed_binding_op_x_capacity(seed, run_mode=RUN_MODE)
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
    final["_hardening_marker"] = "v1_binding_op_x_capacity_chunked"
    final["backend"] = backend
    final["seed"] = SEED
    final["n_seeds"] = 1
    final["corpus_provenance"] = (
        "synthetic_substrate_3_binding_op_x_3_alpha_multibank_WM_v1_cell5_research_20260701")
    final["n_llm_calls"] = _LLM_CALL_COUNTER[0]
    final["cell_lineage"] = "research_2026_07_01_phase_diagram_gap_analysis_cell_5_axis_D_x_O"

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
        # §8 mandatory: except Exception (NOT BaseException) so SystemExit
        # and KeyboardInterrupt propagate normally to runner.
        _write_import_crash_sentinel(e)
        print(f"[main] OUTER_EXCEPTION: {e}", file=sys.stderr, flush=True)
        traceback.print_exc()
        rc = 1
    sys.exit(rc)
