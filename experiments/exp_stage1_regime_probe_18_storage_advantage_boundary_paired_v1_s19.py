"""stage1_regime_probe_18_storage_advantage_boundary_paired_v1 sibling seed=19.

PAIRED STORAGE-advantage regime-boundary map (Director memo Experiment 1). For
each (N, F, corr) cell, evaluate SHARDED and BUNDLED on BIT-IDENTICAL items +
corruption (pre-drawn shared state). delta = acc_SHARDED - acc_BUNDLED is a
within-item paired gap. Discriminator = the boundary corr where delta crosses
0.5, and whether that boundary MOVES with N / F above a binomial noise-floor
null. NO mechanism axis (the READOUT-DEGENERATE comparison that collapsed 4/4 on
2026-07-04). Cannot re-manufacture the mechanism cross-term artifact.

Grid (SMOKE=FULL structure; TR differs): 3 N x 2 F x 5 corr x 2 storage + 1 PC
  = 61 phase points. corr grid per N (cliff moves with N; empirically bracketed):
  N=512 {0.80,0.84,0.87,0.90,0.93}; N=2048 {0.88,0.91,0.93,0.95,0.97};
  N=8192 {0.93,0.95,0.96,0.97,0.98}. M=4800 fixed. MECH=modern_hopfield L=2.
  SATURATION_PC (Gate D): iterative_cosine M=800 N=2048 F=1 L=2 corr=0.20 SHARDED.

Bands:
  HARD_PASS  : all (N,F) straddle + (N or F boundary moves > null q95) + cv<0.15.
  HARD_PASS_NULL : boundaries well-defined but scale-free (BOUNDED_NULL, like P9v2).
  MIDDLE_BAND: one of two scaling axes fires.
  HARD_FAIL  : straddle fail / PAIRING_VALID fail / SATURATION_PC<0.95 / cardinality.

Smoke gate (null-hypothesis-safe): infra + PAIRING_VALID + SHARDED-straddles-all-6
  + SATURATION_PC. NOT gated on the scaling discriminator firing.

CHUNKED architecture: one seed per sibling file (s7, s13, s19). 3-seed FULL via
  Orchestrator for MM_STANDARD cv<0.15.

PRE-REG: preregs/2026-07-04_stage1_regime_probe_18_storage_advantage_boundary_paired_v1.md
CARDINALITY_OK: 61 phase points per seed (SMOKE and FULL).

Defensive patterns (USER 2026-06-28): start_marker; crash-diag sentinel;
  per-seed checkpoint; per-phase-point flush prints.

ASCII-only. No unicode. No em-dashes. No emojis.
Author: exp_dev 2026-07-04 (Opus 4.8, agent-spawn)
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

import torch  # noqa: F401  -- PROT-020 GPU-eligibility scan marker

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    resumable_seeds, write_partial_key, aggregate_partials, get_output_dir,
)

SEED = 19
ANCHOR_NAME = f"stage1_regime_probe_18_storage_advantage_boundary_paired_v1_s{SEED}"

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

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},"
    f"regime=PAIRED_sharded_vs_bundled_FHRR_chain_storage_advantage_boundary,"
    f"mech=modern_hopfield,L=2,M_fixed=4800,"
    f"N_grid=[512,2048,8192],F_grid=[1,4],"
    f"corr_N512=[0.80,0.84,0.87,0.90,0.93],"
    f"corr_N2048=[0.88,0.91,0.93,0.95,0.97],"
    f"corr_N8192=[0.93,0.95,0.96,0.97,0.98],"
    f"storage=PAIRED(SHARDED,BUNDLED)_shared_salt_identical_items_corruption,"
    f"discriminator=boundary_corr_delta_cross_0.5_and_scaling_vs_binomial_null,"
    f"SATURATION_PC=(iterative_cosine,M=800,N=2048,F=1,L=2,corr=0.20,SHARDED),"
    f"SEED={SEED},mode={RUN_MODE},beta=8.0,alpha_soft=0.5,"
    f"boundary_level=0.50,straddle=[<=0.30,>=0.90],"
    f"MC_null=two_stage_binomial_ndraw=200000_seed=20260704,"
    f"HP=(all_straddle+scaleN>q95_or_scaleF>q95+cv<0.15),"
    f"HP_NULL=(all_straddle+scale_free_both_axes),"
    f"HF=(straddle_fail|pairing_invalid|PC<0.95|cardinality_breach),"
    f"expected_n_smoke=61,expected_n_full=61,"
    f"hardening=L1startmarker+L2crashdiag+L3perseedckpt+L4heartbeat+CHUNKED_PER_SEED"
)

_RESULTS_HOLDER: Dict[str, Any] = {"started_at": time.time()}
_LLM_CALL_COUNTER = [0]


def _write_minimal_metrics(out_dir: Path, verdict: str, verdict_msg: str,
                           extra: Dict[str, Any] = None) -> None:
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        m = {
            "anchor_name": ANCHOR_NAME, "verdict": verdict,
            "verdict_msg": verdict_msg, "summary": verdict_msg,
            "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 2),
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(), "run_mode": RUN_MODE,
            "config_version": CONFIG_VERSION,
            "_hardening_marker": "stage1_regime_probe_18_storage_advantage_boundary_paired_v1_chunked",
        }
        if extra:
            m.update(extra)
        tmp = out_dir / "metrics.json.tmp"
        final = out_dir / "metrics.json"
        tmp.write_text(json.dumps(m, indent=2, default=str), encoding="utf-8")
        os.replace(tmp, final)
    except Exception as e:
        print(f"[_write_minimal_metrics] FAIL: {e}", file=sys.stderr, flush=True)


def _write_import_crash_sentinel(exc: Exception) -> None:
    try:
        out_dir = get_output_dir(ANCHOR_NAME)
        out_dir.mkdir(parents=True, exist_ok=True)
        s = {
            "anchor_name": ANCHOR_NAME, "verdict": "UNKNOWN",
            "verdict_msg": f"IMPORT_CRASH: {type(exc).__name__}: {exc}",
            "summary": f"IMPORT_CRASH: {type(exc).__name__}: {exc}",
            "elapsed_s": 0.0,
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(), "_traceback": traceback.format_exc(),
            "_hardening_marker": "stage1_regime_probe_18_storage_advantage_boundary_paired_v1_import_crash",
        }
        tmp = out_dir / "metrics.json.tmp"
        final = out_dir / "metrics.json"
        tmp.write_text(json.dumps(s, indent=2), encoding="utf-8")
        os.replace(tmp, final)
        (out_dir / "import_crash.json").write_text(json.dumps(s, indent=2),
                                                   encoding="utf-8")
    except Exception as e:
        print(f"[_write_import_crash_sentinel] FAIL: {e}", file=sys.stderr, flush=True)


def main() -> int:
    _RESULTS_HOLDER["started_at"] = time.time()
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)

    _write_minimal_metrics(out_dir, "STARTED",
                           f"STARTED: pid={os.getpid()} mode={RUN_MODE} seed={SEED}",
                           extra={"_phase": "init"})

    from experiments.exp_stage1_regime_probe_18_storage_advantage_boundary_paired_v1_core import (
        run_one_seed, aggregate_and_verdict, selftest, DEVICE, GPU_NAME, N_GRID,
    )

    backend = "torch.cuda" if DEVICE == "cuda" else "torch.cpu"
    print(f"[{ANCHOR_NAME}] mode={RUN_MODE} seed={SEED} backend={backend} gpu={GPU_NAME}",
          flush=True)

    if SELF_TEST_MODE:
        try:
            ok, msg = selftest()
            verdict = "SELFTEST_OK" if ok else "SELFTEST_FAIL"
            _write_minimal_metrics(out_dir, verdict, msg,
                                   extra={"_phase": "selftest_done", "backend": backend})
            print(f"[selftest] {verdict}: {msg}", flush=True)
            return 0 if ok else 1
        except Exception as e:
            _write_minimal_metrics(out_dir, "SELFTEST_FAIL", f"SELFTEST_FAIL: {e}",
                                   extra={"_traceback": traceback.format_exc()})
            print(f"[selftest] FAIL: {e}", file=sys.stderr, flush=True)
            return 1

    seeds_list = [SEED]
    N_max = max(N_GRID)
    run_config = {"N": N_max, "run_mode": RUN_MODE, "anchor": ANCHOR_NAME}
    done, remaining = resumable_seeds(seeds_list, out_dir, run_config=run_config)
    print(f"[ckpt] {len(done)}/{len(seeds_list)} done; running {remaining}", flush=True)

    for seed in remaining:
        _write_minimal_metrics(out_dir, "RUNNING",
                               f"RUNNING: seed={seed} mode={RUN_MODE}",
                               extra={"_phase": "seed_running", "_current_seed": seed,
                                      "backend": backend})
        t0 = time.time()
        result = run_one_seed(seed, run_mode=RUN_MODE)
        result["N"] = N_max
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
    final["_hardening_marker"] = "stage1_regime_probe_18_storage_advantage_boundary_paired_v1_chunked"
    final["backend"] = backend
    final["seed"] = SEED
    final["n_seeds"] = 1
    final["corpus_provenance"] = "synthetic_paired_sharded_vs_bundled_fhrr_chain_storage_boundary_v1"
    final["n_llm_calls"] = _LLM_CALL_COUNTER[0]

    assert _LLM_CALL_COUNTER[0] == 0, "LLM_CALL_GATE_BREACH: substrate-only required"

    tmp = out_dir / "metrics.json.tmp"
    final_path = out_dir / "metrics.json"
    tmp.write_text(json.dumps(final, indent=2, default=str), encoding="utf-8")
    os.replace(tmp, final_path)
    print(f"[{ANCHOR_NAME}] DONE: {final['verdict_msg']}", flush=True)
    print(f"[{ANCHOR_NAME}] cardinality observed={final.get('observed_n_units')} "
          f"expected={final.get('expected_n_units')} ok={final.get('cardinality_ok')}",
          flush=True)
    return 0


if __name__ == "__main__":
    try:
        rc = main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException (META_RULE Section 8)
        _write_import_crash_sentinel(e)
        print(f"[main] OUTER_EXCEPTION: {e}", file=sys.stderr, flush=True)
        traceback.print_exc()
        rc = 1
    sys.exit(rc)
