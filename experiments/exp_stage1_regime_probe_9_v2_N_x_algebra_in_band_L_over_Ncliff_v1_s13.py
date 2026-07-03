"""stage1_regime_probe_9_v2_N_x_algebra_in_band_L_over_Ncliff_v1 sibling seed=13.

Research-authority-directed cheap decisive test (2x-drill NEG1 2026-07-03).
Tests N x ALGEBRA (chain-depth L) cross-term at BUNDLED modern_hopfield
near-capacity regime. This is the theoretically-interesting crossover zone
that Probe 9 v1 (SMOKE HP) did NOT test — v1 only tested pinned endpoints.

Sweep FULL:  3 N x 4 L = 12 BUNDLED_main + 1 SATURATION_PC + 4 DEEP_SAT = 17 pts/seed.
Sweep SMOKE: 2 N x 2 L =  4 BUNDLED_main + 1 SATURATION_PC              =  5 pts/seed.

Fixed: STORAGE=BUNDLED, MECH=modern_hopfield, M=10, F=1, corr=0.10.
N grid: {1024, 2048, 4096} = {0.5x, 1x, 2x} N_cliff (MEASURED@bracket_scout2).

CHUNKED architecture: one seed per sibling file. Siblings: s13, s19 pending FULL.

PRE-REG: preregs/2026-07-03_stage1_regime_probe_9_v2_N_x_algebra_in_band_L_over_Ncliff_v1.md
CARDINALITY_OK_FULL: 17 phase points per seed
CARDINALITY_OK_SMOKE: 5 phase points per seed

Defensive patterns (USER 2026-06-28):
  1. start_marker
  2. crash-diag import-crash sentinel
  3. per-seed checkpoint via _seed_checkpoint
  4. heartbeat: per-phase-point flush print

ASCII-only. No unicode. No em-dashes. No emojis.
Author: exp_dev 2026-07-03 (Opus 4.7, agent-spawn). Research-authority-directed.
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
    resumable_seeds, write_partial_key, aggregate_partials,
)

SEED = 13
ANCHOR_NAME = f"stage1_regime_probe_9_v2_N_x_algebra_in_band_L_over_Ncliff_v1_s{SEED}"

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
    f"regime=bundled_FHRR_chain_composition_near_capacity_N_x_L_CROSS_TERM_v2,"
    f"mech=modern_hopfield(fixed),storage=BUNDLED(fixed),"
    f"N=[1024,2048,4096](0.5x1x2x_Ncliff),L=[2,4,8,16],"
    f"M=10(fixed_near_capacity),F=1(fixed),corr=0.10(fixed),"
    f"N_cliff=2048(MEASURED@bracket_scout2),"
    f"SEED={SEED},mode={RUN_MODE},"
    f"SATURATION_PC_regime=fixed_SHARDED_F1_M800_N2048_L4_corr0.20_modern_hopfield,"
    f"DEEP_SAT_regime=fixed_BUNDLED_N8192_M100_corr0.60_modern_hopfield_across_L,"
    f"non_saturated_band=[0.30,0.95],"
    f"beta=8.0,alpha_soft=0.5,"
    f"expected_n_full=17,expected_n_smoke=5,"
    f"H1_high_bucket_threshold=0.15,H1_low_bucket_threshold=0.05,"
    f"H1_ALT_overall_threshold=0.10,H2_null_threshold=0.05,"
    f"hardening=L1startmarker+L2crashdiag+L3perseedckpt+L4heartbeat+CHUNKED_PER_SEED"
)

_RESULTS_HOLDER: Dict[str, Any] = {"started_at": time.time()}
_LLM_CALL_COUNTER = [0]


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
            "_hardening_marker": "stage1_regime_probe_9_v2_N_x_algebra_in_band_chunked",
        }
        if extra:
            m.update(extra)
        tmp = out_dir / "metrics.json.tmp"
        final = out_dir / "metrics.json"
        tmp.write_text(json.dumps(m, indent=2, default=str), encoding="utf-8")
        os.replace(tmp, final)  # atomic per META_RULE_AH
    except Exception as e:
        print(f"[_write_minimal_metrics] FAIL: {e}", file=sys.stderr, flush=True)


def _write_import_crash_sentinel(exc: Exception) -> None:
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
            "_hardening_marker": "stage1_regime_probe_9_v2_N_x_algebra_in_band_import_crash",
        }
        tmp = out_dir / "metrics.json.tmp"
        final = out_dir / "metrics.json"
        tmp.write_text(json.dumps(s, indent=2), encoding="utf-8")
        os.replace(tmp, final)
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

    from experiments._stage1_regime_probe_9_v2_N_x_algebra_in_band_L_over_Ncliff_v1_core import (
        run_one_seed, aggregate_and_verdict, selftest,
        DEVICE, GPU_NAME,
    )

    backend = "torch.cuda" if DEVICE == "cuda" else "torch.cpu"
    print(f"[{ANCHOR_NAME}] mode={RUN_MODE} seed={SEED} backend={backend} "
          f"gpu={GPU_NAME}", flush=True)

    if SELF_TEST_MODE:
        try:
            ok, msg = selftest()
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
    run_config = {"run_mode": RUN_MODE, "anchor": ANCHOR_NAME}
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
        result = run_one_seed(seed, run_mode=RUN_MODE)
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
    final["_hardening_marker"] = "stage1_regime_probe_9_v2_N_x_algebra_in_band_chunked"
    final["backend"] = backend
    final["seed"] = SEED
    final["n_seeds"] = 1
    final["corpus_provenance"] = ("synthetic_bundled_fhrr_chain_composition_"
                                   "near_capacity_N_x_L_CROSS_TERM_probe9_v2")
    final["n_llm_calls"] = _LLM_CALL_COUNTER[0]

    assert _LLM_CALL_COUNTER[0] == 0, \
        "LLM_CALL_GATE_BREACH: substrate-only required"

    tmp = out_dir / "metrics.json.tmp"
    final_path = out_dir / "metrics.json"
    tmp.write_text(json.dumps(final, indent=2, default=str), encoding="utf-8")
    os.replace(tmp, final_path)  # atomic per META_RULE_AH
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
    except Exception as e:  # NOT BaseException (META_RULE section 8; SystemExit ordered first)
        _write_import_crash_sentinel(e)
        print(f"[main] OUTER_EXCEPTION: {e}", file=sys.stderr, flush=True)
        traceback.print_exc()
        rc = 1
    sys.exit(rc)
