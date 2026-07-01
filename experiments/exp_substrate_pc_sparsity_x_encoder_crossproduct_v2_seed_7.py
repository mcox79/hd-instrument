"""substrate_pc_sparsity_x_encoder_crossproduct_v2 sibling seed=7.

CAPACITY-LIFT 2x-DRILL of v1 per Skunkworks a7708cb2 tier MM_capacity_bound.
v1 result: 10/16 pts SATURATED at M=300 N=8192; only fhrr showed
per_encoder_sparsity_range=0.30. META_RULE_Q trip. v2 changes:
  - M_items 300 -> 600 (2x-drill per Skunkworks)
  - sparsity grid (0.01,0.05,0.10,0.25) -> (0.05,0.10,0.25,0.50)
    Rationale: s=0.01 always FLOOR in v1 (no signal); s=0.50 sits near
    v2 break edge (cap_ratio=1.87 vs empirical break ~1.67).
  - positive control shifted binary_bipolar s=0.10 -> s=0.25 (predicted to
    drop into discriminating band at M=600).

Grid: 4 encoders x 4 sparsity levels x fixed cliff-K corruption = 16 phase
points per seed FULL.
Smoke: 4 encoders x 2 sparsity levels (0.10, 0.50) = 8 points per seed.
Smoke uses SAME N=8192 as FULL + HALF M=300 (v1 full M) for speed.

Encoders (axis A):
    binary_bipolar / hrr_real / fhrr / sparse_bipolar

Sparsity levels (axis C):
    FULL:  {0.05, 0.10, 0.25, 0.50}
    SMOKE: {0.10, 0.50}

Fixed regime:
    N=8192; corruption=0.485 (cliff-K per PC v2.2 CG evidence
    MEASURED@data/exp_substrate_pattern_completion_corruption_cliff_v2p2_
    dense_cliff_grid_seed_7/metrics.json:phase_map c=0.485 N=8192 T=5);
    T=5 cleanup iters; M_items=600 FULL / 300 SMOKE.

Discriminator (verdict bands):
    HARD_PASS: 3+ encoders show per_encoder_sparsity_range >=0.15
               (v1 only fhrr; v2 target: binary_bipolar / sparse_bipolar /
                hrr_real ALSO show sparsity discrimination) AND
               >=2 encoder pairs show interaction delta >=0.15
    MIDDLE_BAND: main effects only OR interaction partial
    HARD_FAIL: cardinality breach / arms identical / positive control fail

Positive control (META_RULE_BC): binary_bipolar @ sparsity=0.25 top1 in
    [0.10, 0.95] band -- primary discriminator is per_encoder_sparsity_range
    not point-value.

CHUNKED architecture (USER 2026-06-28): one seed per sibling file.
Sibling pair: seed_13, seed_19.

PRE-REG: preregs/2026-07-01_substrate_pc_sparsity_x_encoder_crossproduct_v2.md
CARDINALITY_OK_FULL: 16 phase points per seed
CARDINALITY_OK_SMOKE: 8 corner points per seed

PROT-018: anchor has _n8192 suffix (single-N cell).
PROT-019: _n8192 requires --timeout >= 3600s.

4 defensive patterns (USER 2026-06-28 hardening):
  1. start_marker: STARTED metrics written before any heavy work
  2. crash-diag: outer try -> import-crash sentinel with full traceback
  3. per-unit checkpoint: write_partial_key per seed via _seed_checkpoint
  4. heartbeat: per-phase-point flush print

ASCII-only. No unicode. No em-dashes. No emojis.
Author: exp_dev 2026-07-01 (Opus 4.7 1M, agent-spawn; v2 capacity-lift 2x-drill)
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

# torch imported at TOP of file for PROT-020 GPU eligibility scan
import torch  # noqa: F401  -- gate marker only

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    resumable_seeds, write_partial_key, aggregate_partials,
)

SEED = 7
ANCHOR_NAME = f"substrate_pc_sparsity_x_encoder_crossproduct_v2_n8192_seed_{SEED}"

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
    f"ANCHOR={ANCHOR_NAME},encoders=[binary_bipolar,hrr_real,fhrr,sparse_bipolar],"
    f"sparsity=[0.05,0.10,0.25,0.50],N=8192,SEED={SEED},mode={RUN_MODE},"
    f"corruption=0.485,iters=5,M=600,beta=8.0,"
    f"arms=[MECHANISM,RANDOM_FLOOR],"
    f"expected_n_full=16,expected_n_smoke=8,"
    f"drill_kind=CAPACITY_LIFT_2X_DRILL,"
    f"parent_cell=v1_MM_capacity_bound_skunkworks_a7708cb2,"
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
            "_hardening_marker": "v2_pc_sparsity_x_encoder_crossproduct_chunked",
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
            "_hardening_marker": "v2_pc_sparsity_x_encoder_import_crash",
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

    from experiments._substrate_pc_sparsity_x_encoder_crossproduct_v2_core import (
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

    # GPU mandate (Fix #24)
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
    final["_hardening_marker"] = "v2_pc_sparsity_x_encoder_crossproduct_chunked"
    final["backend"] = backend
    final["seed"] = SEED
    final["n_seeds"] = 1
    final["N"] = N_DIM_FULL
    final["corpus_provenance"] = (
        "synthetic_substrate_pc_sparsity_x_encoder_crossproduct_v2_caplift")
    final["n_llm_calls"] = _LLM_CALL_COUNTER[0]
    final["drill_kind"] = "CAPACITY_LIFT_2X_DRILL"
    final["parent_cell"] = "v1_MM_capacity_bound_skunkworks_a7708cb2"

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
