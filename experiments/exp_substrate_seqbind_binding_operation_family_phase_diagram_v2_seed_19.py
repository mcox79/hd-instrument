"""substrate_seqbind_binding_operation_family_phase_diagram_v2 sibling seed=7.

2x-DRILL of substrate_pc_binding_operation_family_phase_diagram_v1 (MIDDLE_BAND;
n_disc=8/48). Mechanism-class diversion: PC regime -> SEQUENCE BINDING regime.

5 binding ops (4 from v1 + SUM_MOD_N positive control per META_RULE_BC):
  HADAMARD_BIND / CIRCULAR_CONV_HRR / TENSOR_PRODUCT / XOR_BSC / SUM_MOD_N

Regime: N_DIM=8192 fixed; K_SEQ sweep [50,100,200,500,1000]; n_q=50/point.
CARDINALITY_OK_FULL: 25 phase points per seed (5 ops x 5 K_SEQ)
CARDINALITY_OK_SMOKE: 15 phase points (5 ops x 3 K_SEQ [50,200,1000])

CHUNKED architecture: one seed per sibling file. Sibling pair: seed_13, seed_19.

PRE-REG: preregs/2026-06-30_substrate_seqbind_binding_operation_family_phase_diagram_v2.md

Defensive patterns (META_RULE §13 + canonical exp_dev.md):
  L1: start_marker (STARTED metrics before heavy work)
  L2: crash-diag with full traceback (except Exception -- NOT BaseException
      per §8 of canonical instruction file)
  L3: per-seed checkpoint via _seed_checkpoint
  L4: periodic heartbeat

PROT-018: anchor multi-K sweep; no _n<N> suffix needed.
PROT-019: anchor uses no _n>=4096 suffix -> no timeout floor.

ASCII-only. No unicode. No em-dashes. No emojis.
Author: exp_dev 2026-06-30 (Opus 4.7 1M, agent-spawn) 2x-drill PC v1 MB.
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

import torch  # noqa: F401  -- PROT-020 gate marker (overnight_queue routing)

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    resumable_seeds, write_partial_key, aggregate_partials,
)

SEED = 19
ANCHOR_NAME = f"substrate_seqbind_binding_operation_family_phase_diagram_v2_seed_{SEED}"

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
    f"bindings=[HADAMARD_BIND,CIRCULAR_CONV_HRR,TENSOR_PRODUCT,XOR_BSC,SUM_MOD_N],"
    f"N_DIM=8192,SEED={SEED},mode={RUN_MODE},"
    f"K_SEQ_FULL=[50,100,200,500,1000],K_SEQ_SMOKE=[50,200,1000],"
    f"n_q_full=50,n_q_smoke=5,V_ITEMS=1200,V_POS=1200,beta=8.0,"
    f"expected_n_full=25,expected_n_smoke=15,"
    f"discriminator=K_cliff_log2_sep_min0.3,"
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
            "_hardening_marker": "v2_seqbind_binding_op_family_phase_diagram_chunked",
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
            "_hardening_marker": "v2_seqbind_binding_op_family_import_crash",
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

    from experiments._substrate_seqbind_binding_operation_family_phase_diagram_v2_core import (
        run_one_seed_phase_diagram, aggregate_and_verdict, selftest,
        get_backend_label, N_DIM, K_SEQ_FULL, K_SEQ_SMOKE,
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

    # GPU mandate (Fix #24): FULL on CPU forbidden unless explicit local route
    routed_queue = os.environ.get("HDLAB_QUEUE", "").lower()
    if not SMOKE_MODE and backend == "torch.cpu":
        if routed_queue != "local_cpu_queue":
            verdict = "HARD_FAIL"
            vmsg = ("HARD_FAIL_GPU_MANDATE_BREACH: FULL run on CPU backend forbidden "
                    "by Fix #24 unless HDLAB_QUEUE=local_cpu_queue. "
                    f"Got HDLAB_QUEUE='{routed_queue}'. Refusing.")
            _write_minimal_metrics(out_dir, verdict, vmsg,
                                   extra={"_phase": "gpu_mandate_check",
                                          "backend": backend,
                                          "routed_queue": routed_queue})
            print(f"[FATAL] {vmsg}", file=sys.stderr, flush=True)
            return 2

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
        result = run_one_seed_phase_diagram(seed, run_mode=RUN_MODE)
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
    final["_hardening_marker"] = "v2_seqbind_binding_op_family_phase_diagram_chunked"
    final["backend"] = backend
    final["seed"] = SEED
    final["n_seeds"] = 1
    final["corpus_provenance"] = "synthetic_substrate_5_binding_op_family_seqbind_v2_2x_drill_PC_v1"
    final["n_llm_calls"] = _LLM_CALL_COUNTER[0]
    final["drill_lineage"] = "2x_drill_of_substrate_pc_binding_operation_family_phase_diagram_v1_MB"

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
