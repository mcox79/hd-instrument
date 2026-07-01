"""substrate_three_tier_generational_v1 sibling seed=7.

Axis P from Research 2026-07-01 phase-diagram gap analysis (CG=0.35, MEDIUM):
STM -> ITM -> LTM 3-tier generational W. Extends TWO_TIER CG primitive
(gap4_two_tier_generational_W_v1) with an intermediate tier per systems-
consolidation literature (Squire-Alvarez 1995; McClelland-McNaughton-O'Reilly
1995 CLS). Composes with NREM replay CG (META_RULE_AT).

Arms: 2 structures {TWO_TIER, THREE_TIER} x 3 replay counts {t=10, 50, 100}
  = 6 arms per seed (full); 2 arms per seed (smoke; t=100 discriminator only).

CARDINALITY_OK_FULL: 6 arms per seed
CARDINALITY_OK_SMOKE: 2 arms per seed (t=100 discriminator only)

CHUNKED architecture: one seed per sibling file. Siblings: seed_13, seed_19.

PRE-REG: preregs/2026-07-01_substrate_three_tier_generational_v1.md

Defensive patterns (canonical exp_dev.md §8, §13):
  L1: STARTED marker before heavy work
  L2: crash-diag with full traceback (except Exception, NOT BaseException)
  L3: per-seed + per-arm checkpoint via _seed_checkpoint
  L4: per-cycle checkpoint print-flush

PROT-018: no _n<N> suffix (fixed N=8192 across arms).
PROT-020: numpy-only substrate; import torch present to route via GPU-queue if
  desired but cell uses numpy substrate only (no cuda ops).

CPU-eligible: substrate is numpy Hopfield + sign() cleanup.

ASCII-only. No unicode. No em-dashes. No emojis.
Author: exp_dev 2026-07-01 (Opus 4.7 1M, agent-spawn) Cell #4 Research spec.
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

import torch  # noqa: F401  -- PROT-020 gate marker (cell uses numpy substrate only)

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    resumable_seeds, write_partial_key, aggregate_partials,
)

SEED = 13
ANCHOR_NAME = f"substrate_three_tier_generational_v1_seed_{SEED}"

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
    f"structures=[TWO_TIER,THREE_TIER],"
    f"N=8192,SEED={SEED},mode={RUN_MODE},"
    f"M_atoms_full=200,M_atoms_smoke=40,"
    f"T_list_full=[10,50,100],T_list_smoke=[100],"
    f"expected_n_full=6,expected_n_smoke=2,"
    f"discriminator=three_tier_retention_delta_ge_0p05_at_t100_cv_le_0p10,"
    f"bands=HP_delta0.05_HP_cv0.10_HP_itm_util0.05_HF_tol0.02,"
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
            "summary": verdict_msg[:400],
            "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 2),
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "run_mode": RUN_MODE,
            "config_version": CONFIG_VERSION,
            "_hardening_marker": "v1_three_tier_generational_chunked",
        }
        if extra:
            m.update(extra)
        (out_dir / "metrics.json").write_text(
            json.dumps(m, indent=2, default=str), encoding="utf-8")
    except Exception as e:
        print(f"[_write_minimal_metrics] FAIL: {e}", file=sys.stderr, flush=True)


def _write_import_crash_sentinel(exc: Exception) -> None:
    """Defensive pattern L2: crash-diag sentinel with full traceback."""
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
            "_hardening_marker": "v1_three_tier_generational_import_crash",
        }
        (out_dir / "metrics.json").write_text(json.dumps(s, indent=2),
                                              encoding="utf-8")
        (out_dir / "import_crash.json").write_text(json.dumps(s, indent=2),
                                                   encoding="utf-8")
    except Exception as e:
        print(f"[_write_import_crash_sentinel] FAIL: {e}",
              file=sys.stderr, flush=True)


def _run_selftest_and_return(out_dir: Path) -> int:
    """Run core self-tests by importing the core module with --self-test.

    The core module's _instrumentation_selftest() runs at import time and
    sys.exit(0)s if --self-test is set. Here we invoke the tests directly.
    """
    try:
        # Ensure the core module runs its selftests. We import functions from
        # the core module namespace; the module's top-level runs selftests then
        # exits if --self-test. To use as sub-module we call the tests directly.
        # However, the core module ALSO runs its main loop at import if
        # --self-test is not present. To keep this wrapper clean we set argv
        # to force self-test mode inside the child spawn (we import as script).
        import subprocess
        core_path = REPO / "experiments" / "_substrate_three_tier_generational_v1_core.py"
        result = subprocess.run(
            [sys.executable, str(core_path), "--self-test"],
            capture_output=True, text=True, timeout=60,
        )
        ok = (result.returncode == 0)
        msg = (result.stdout.strip().splitlines()[-1]
                if result.stdout else f"rc={result.returncode}")
        if not ok:
            msg = f"SELFTEST_FAIL rc={result.returncode}: {result.stderr[-500:]}"
        verdict = "SELFTEST_OK" if ok else "SELFTEST_FAIL"
        _write_minimal_metrics(out_dir, verdict, msg,
                               extra={"_phase": "selftest_done",
                                      "core_stdout_tail": result.stdout[-500:]})
        print(f"[selftest] {verdict}: {msg}", flush=True)
        return 0 if ok else 1
    except Exception as e:
        _write_minimal_metrics(out_dir, "SELFTEST_FAIL",
                               f"SELFTEST_FAIL: {e}",
                               extra={"_traceback": traceback.format_exc()})
        print(f"[selftest] FAIL: {e}", file=sys.stderr, flush=True)
        return 1


def _invoke_core_run(out_dir: Path) -> int:
    """Invoke core module as subprocess so its main loop runs to completion,
    then copy metrics.json into per-seed out_dir.

    The core module writes metrics to data/exp_substrate_three_tier_generational_v1/.
    We copy those metrics into this seed's data dir so the queue runner sees
    the per-seed metrics.json where it expects.
    """
    import subprocess

    core_path = REPO / "experiments" / "_substrate_three_tier_generational_v1_core.py"
    args = [sys.executable, str(core_path)]
    if SMOKE_MODE:
        args.append("--smoke")

    env = os.environ.copy()
    # Force core to write into THIS seed's out_dir so runner sees it directly.
    env["HDLAB_EXP_NAME"] = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)

    t0 = time.time()
    print(f"[{ANCHOR_NAME}] invoking core: {' '.join(args)} "
          f"HDLAB_EXP_NAME={env['HDLAB_EXP_NAME']}", flush=True)
    result = subprocess.run(args, env=env, capture_output=False, text=True)
    elapsed = time.time() - t0

    # BUGFIX 2026-07-01: core.get_output_dir(ANCHOR_NAME) uses HDLAB_EXP_NAME
    # from env (which the wrapper propagates), so core writes to the SAME
    # out_dir the wrapper writes STARTED/RUNNING markers to. No copy needed --
    # core's final metrics.json is already at out_dir/metrics.json. We just
    # inject seed-wrapper metadata in-place.
    #
    # The prior implementation looked at a hardcoded
    # data/exp_substrate_three_tier_generational_v1/ path (assuming core's
    # ANCHOR_NAME overrode HDLAB_EXP_NAME); that path was empty; and the
    # fallback CORE_METRICS_NOT_FOUND write clobbered core's real output.
    #
    # Recovery discipline: if metrics.json exists but was clobbered, we can
    # rebuild from partial_metrics_<seed>.json which core wrote atomically.
    metrics_path = out_dir / "metrics.json"
    if not metrics_path.exists():
        # Rebuild-from-partial fallback: core exited but never aggregated.
        partial_path = out_dir / f"partial_metrics_{SEED}.json"
        if partial_path.exists():
            print(f"[{ANCHOR_NAME}] metrics.json missing but partial exists; "
                  f"rebuilding from {partial_path}", flush=True)
            try:
                with open(partial_path, "r", encoding="utf-8") as f:
                    part = json.load(f)
                # Build a minimal verdict-carrying metrics from the seed partial
                arms = part.get("arms", {})
                m = {
                    "anchor_name": ANCHOR_NAME,
                    "verdict": "REBUILT_FROM_PARTIAL",
                    "verdict_msg": ("REBUILT_FROM_PARTIAL: seed partial recovered; "
                                    "arm-level metrics preserved but no aggregate"),
                    "summary": "REBUILT_FROM_PARTIAL from seed partial",
                    "run_mode": part.get("run_mode"),
                    "N": part.get("N"),
                    "M_atoms": part.get("M_atoms"),
                    "T_list": part.get("T_list"),
                    "arms_recovered": {al: {
                        "final_forget": ar.get("final_forget"),
                        "W_itm_utilization": ar.get("W_itm_utilization"),
                        "stm_hash": ar.get("stm_hash"),
                        "itm_hash": ar.get("itm_hash"),
                        "ltm_hash": ar.get("ltm_hash"),
                    } for al, ar in arms.items()},
                    "seed": SEED,
                }
                with open(metrics_path, "w", encoding="utf-8") as f:
                    json.dump(m, f, indent=2)
            except Exception as e:
                _write_minimal_metrics(
                    out_dir, "UNKNOWN",
                    f"CORE_METRICS_AND_PARTIAL_REBUILD_FAILED: rc={result.returncode} "
                    f"elapsed={elapsed:.1f}s exc={e}",
                    extra={"_phase": "core_run_no_metrics_no_partial_recovery",
                            "_traceback": traceback.format_exc()},
                )
                return 1
        else:
            _write_minimal_metrics(
                out_dir, "UNKNOWN",
                f"CORE_METRICS_NOT_FOUND_NO_PARTIAL: core exited rc={result.returncode} "
                f"elapsed={elapsed:.1f}s",
                extra={"_phase": "core_run_no_metrics"},
            )
            return 1

    # Inject seed-wrapper metadata in-place (metrics.json is core's output)
    try:
        with open(metrics_path, "r", encoding="utf-8") as f:
            m = json.load(f)
        m["seed"] = SEED
        m["seed_wrapper_anchor"] = ANCHOR_NAME
        m["seed_wrapper_elapsed_s"] = round(elapsed, 2)
        m["seed_wrapper_config_version"] = CONFIG_VERSION
        m["cell_lineage"] = ("research_2026_07_01_phase_diagram_gap_analysis_"
                              "cell_4_axis_P_three_tier_generational")
        m["compose_upstream"] = ["gap4_two_tier_generational_W_v1",
                                  "exp_substrate_continual_NREM_replay_v1"]
        m["n_llm_calls"] = _LLM_CALL_COUNTER[0]
        with open(metrics_path, "w", encoding="utf-8") as f:
            json.dump(m, f, indent=2, default=str)
    except Exception as e:
        print(f"[metrics_metadata_inject] FAIL: {e}", flush=True)

    return result.returncode


def main() -> int:
    _RESULTS_HOLDER["started_at"] = time.time()
    env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    out_dir = REPO / "data" / ("exp_" + env_name)
    out_dir.mkdir(parents=True, exist_ok=True)

    _write_minimal_metrics(out_dir, "STARTED",
                            f"STARTED: pid={os.getpid()} mode={RUN_MODE} seed={SEED}",
                            extra={"_phase": "init"})

    print(f"[{ANCHOR_NAME}] mode={RUN_MODE} seed={SEED}", flush=True)

    if SELF_TEST_MODE:
        return _run_selftest_and_return(out_dir)

    _write_minimal_metrics(out_dir, "RUNNING",
                            f"RUNNING: seed={SEED} mode={RUN_MODE}",
                            extra={"_phase": "seed_running",
                                    "_current_seed": SEED})

    rc = _invoke_core_run(out_dir)

    # Assert LLM gate (substrate-only)
    assert _LLM_CALL_COUNTER[0] == 0, \
        "LLM_CALL_GATE_BREACH: substrate-only required"

    print(f"[{ANCHOR_NAME}] DONE rc={rc}", flush=True)
    return rc


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
