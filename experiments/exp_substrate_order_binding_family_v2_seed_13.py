"""substrate_order_binding_family_v2 sibling seed=7.

Research hand-off: `notes/research_axis_J_revival_drill_2026-07-01.md` candidate #1
Prereg: `preregs/2026-07-01_substrate_order_binding_family_v2.md`
Prior v1: `data/exp_substrate_order_binding_family_v1_seed_{13,19}/metrics.json`
          (v1 HF because K*-boundary metric collapsed 3.5x top1 spread at K=2000)

Axis J v2 REVIVAL -- interference-resilience under multi-sequence load.

DISCRIMINATOR PIVOT: at (L=4 sequences, K_per_seq=250), top1 recall differential
across 3 ops (CYCLIC_SHIFT / RANDOM_PERMUTATION / PHASE_ROTATION); predicted
ordering PERM > PHASE > CYCLIC per compressed-sensing basis-universality
(Puy et al 2012), HRR SNR=1/m (Plate), and Cowan WM chunk-limit theory.

Regime: N_DIM=8192 fixed; L in [1,2,4]; K_per_seq in [125,250]; n_q=60 FULL/8 SMOKE.
CARDINALITY_OK: 18 phase points per seed (3 ops x 3 L x 2 K).

CHUNKED architecture: one seed per sibling file (this seed=7). Sibling pair to
follow: seed_13, seed_19 (spawn only if smoke_7 discriminator fires).

Defensive patterns (canonical exp_dev.md §13):
  L1: start_marker (STARTED metrics before heavy work)
  L2: crash-diag with full traceback (except Exception -- NOT BaseException)
  L3: per-seed checkpoint via _seed_checkpoint (PROT-021 config guard)
  L4: periodic print-flush heartbeat

PROT-018: multi-L/K sweep anchor; no _n<N> suffix needed.
PROT-020: torch imported at top for GPU-eligibility scan; math is numpy.
PROT-021: run_config includes N + run_mode for checkpoint mismatch guard.

ASCII-only. No unicode. No em-dashes. No emojis.
Author: exp_dev 2026-07-01 (Opus 4.7 1M, agent-spawn).
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

import torch  # noqa: F401  -- PROT-020 GPU-eligibility marker (unused; numpy math)

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    resumable_seeds, write_partial_key, aggregate_partials,
)

SEED = 13
ANCHOR_NAME = f"substrate_order_binding_family_v2_seed_{SEED}"

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
    f"order_ops=[CYCLIC_SHIFT,RANDOM_PERMUTATION,PHASE_ROTATION],"
    f"N_DIM=8192,SEED={SEED},mode={RUN_MODE},"
    f"L_FULL=[1,2,4],L_SMOKE=[1,2,4],"
    f"K_PER_SEQ_FULL=[125,250],K_PER_SEQ_SMOKE=[125,250],"
    f"n_q_full=60,n_q_smoke=8,V_ITEMS=4000,V_POS=4000,"
    f"expected_n_full=18,expected_n_smoke=18,"
    f"discriminator=max_pair_diff_top1_at_L4_K250_min_0.15,"
    f"honest_abort=max_pair_diff_top1_at_L4_K250_le_0.03,"
    f"bands=SAT0.90_MB[0.30,0.70]_FLOOR0.10,"
    f"v2_salt=substrate_order_binding_family_v2_load_variant_2026-07-01,"
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
            "_hardening_marker": "v2_order_binding_family_chunked",
        }
        if extra:
            m.update(extra)
        (out_dir / "metrics.json").write_text(
            json.dumps(m, indent=2, default=str), encoding="utf-8")
    except Exception as e:
        print(f"[_write_minimal_metrics] FAIL: {e}", file=sys.stderr, flush=True)


def _write_import_crash_sentinel(exc: Exception) -> None:
    """Defensive pattern L2: crash-diag sentinel with full traceback.

    NOTE: signature uses Exception (not BaseException) per canonical §8.
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
            "_hardening_marker": "v2_order_binding_family_import_crash",
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

    from experiments._substrate_order_binding_family_v2_core import (
        run_one_seed_load_sweep, aggregate_and_verdict, selftest,
        get_backend_label, N_DIM, L_FULL, L_SMOKE, K_PER_SEQ_FULL, K_PER_SEQ_SMOKE,
    )

    backend = get_backend_label()
    print(f"[{ANCHOR_NAME}] mode={RUN_MODE} seed={SEED} backend={backend}",
          flush=True)

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

    # Per-seed checkpoint resume (PROT-021 config-mismatch guard)
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
        result = run_one_seed_load_sweep(seed, run_mode=RUN_MODE)
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
    final["_hardening_marker"] = "v2_order_binding_family_chunked"
    final["backend"] = backend
    final["seed"] = SEED
    final["n_seeds"] = 1
    final["corpus_provenance"] = "synthetic_substrate_3_order_binding_op_family_v2_multi_seq_load"
    final["n_llm_calls"] = _LLM_CALL_COUNTER[0]
    final["research_handoff"] = ("notes/research_axis_J_revival_drill_2026-07-01.md#candidate_1")

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
        # canonical §8: except Exception (NOT BaseException) so SystemExit
        # and KeyboardInterrupt propagate normally to the runner.
        _write_import_crash_sentinel(e)
        print(f"[main] OUTER_EXCEPTION: {e}", file=sys.stderr, flush=True)
        traceback.print_exc()
        rc = 1
    sys.exit(rc)
