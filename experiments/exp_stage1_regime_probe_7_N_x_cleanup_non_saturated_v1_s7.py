"""stage1_regime_probe_7_N_x_cleanup_non_saturated_v1 sibling seed=7.

Non-saturated regime revival of Probe 2 (N x CLEANUP_MECHANISM).
Companion to Probe 6 (F x CLEANUP TOPOLOGY revival, same day).

Sweep FULL: 4 N x 3 mech x 3 M x 3 corr + 1 SATURATION_PC = 109 pts/seed.
Sweep SMOKE: 2 N x 3 mech x 1 M x 1 corr + 1 SATURATION_PC = 7 pts.

Hypotheses (band-restricted, [0.30, 0.95] non-saturated slice):
  H1: N_x_cleanup_max_abs_deviation_in_band >= 0.15 OR max_per_N_var >= 0.10 ->
      Probe 2 null was saturation artifact; N IS a moderator.
  H2: max_abs_dev < 0.05 AND max_per_N_var < 0.05 -> null holds at non-saturated;
      strengthens Probe 1 STORAGE_UNIQUELY_moderates thesis (CG_META revival).
  H3: mechanism ranking changes across N in band -> N-crossover (MM_TENTATIVE).

CHUNKED architecture: one seed per sibling file. Siblings: s13, s19.

PRE-REG: preregs/2026-07-03_stage1_regime_probe_7_N_x_cleanup_non_saturated_v1.md
CARDINALITY_OK_FULL: 109 phase points per seed
CARDINALITY_OK_SMOKE: 7 phase points per seed

Defensive patterns (USER 2026-06-28):
  1. start_marker
  2. crash-diag import-crash sentinel
  3. per-seed checkpoint via _seed_checkpoint
  4. heartbeat: per-phase-point flush print

ASCII-only. No unicode. No em-dashes. No emojis.
Author: exp_dev 2026-07-03 (Opus 4.7, agent-spawn)
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import os
# CUDA env before torch import (USER-LOCKED)
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
    get_output_dir,
)

SEED = 7
ANCHOR_NAME = f"stage1_regime_probe_7_N_x_cleanup_non_saturated_v1_s{SEED}"

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
    f"regime=sharded_FHRR_chain_composition_non_saturated_revival_of_probe2,"
    f"cleanup_mechanisms=[modern_hopfield,iterative_cosine,soft_energy_attractor],"
    f"N=[2048,4096,8192,16384],M=[800,3200,6400],corr=[0.88,0.90,0.92],F=1,L=8,"
    f"SATURATION_PC=(iterative_cosine,M=800,N=2048,corr=0.20),"
    f"SEED={SEED},mode={RUN_MODE},"
    f"beta=8.0,alpha_soft=0.5,"
    f"non_saturated_band=[0.30,0.95],"
    f"H1_thresh=(dev>=0.15|var>=0.10),H2_thresh=(dev<0.05&var<0.05),"
    f"expected_n_full=109,expected_n_smoke=7,"
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
            "_hardening_marker": "stage1_regime_probe_7_N_x_cleanup_non_saturated_v1_chunked",
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
        out_dir = get_output_dir(ANCHOR_NAME)
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
            "_hardening_marker": "stage1_regime_probe_7_N_x_cleanup_non_saturated_v1_import_crash",
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
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)

    _write_minimal_metrics(out_dir, "STARTED",
                           f"STARTED: pid={os.getpid()} mode={RUN_MODE} seed={SEED}",
                           extra={"_phase": "init"})

    from experiments._stage1_regime_probe_7_N_x_cleanup_non_saturated_v1_core import (
        run_one_seed, aggregate_and_verdict, selftest,
        N_GRID_FULL, N_GRID_SMOKE, DEVICE, GPU_NAME,
    )

    backend = "torch.cuda" if DEVICE == "cuda" else "torch.cpu"
    print(f"[{ANCHOR_NAME}] mode={RUN_MODE} seed={SEED} backend={backend} gpu={GPU_NAME}",
          flush=True)

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
    N_max = max(N_GRID_SMOKE if SMOKE_MODE else N_GRID_FULL)
    run_config = {"N": N_max, "run_mode": RUN_MODE, "anchor": ANCHOR_NAME}
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
    final["_hardening_marker"] = "stage1_regime_probe_7_N_x_cleanup_non_saturated_v1_chunked"
    final["backend"] = backend
    final["seed"] = SEED
    final["n_seeds"] = 1
    final["corpus_provenance"] = "synthetic_sharded_fhrr_chain_composition_non_saturated_revival_v1"
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
    except Exception as e:  # NOT BaseException (META_RULE §8)
        _write_import_crash_sentinel(e)
        print(f"[main] OUTER_EXCEPTION: {e}", file=sys.stderr, flush=True)
        traceback.print_exc()
        rc = 1
    sys.exit(rc)
