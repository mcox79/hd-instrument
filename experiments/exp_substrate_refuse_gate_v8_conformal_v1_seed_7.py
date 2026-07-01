"""substrate_refuse_gate_v8_conformal_v1 sibling seed=7.

v8 SURGICAL FIX from v7 (commit family; see prereg):

  Root cause diagnosed by 2x-drill (2026-07-01): in-KB max_sim at N=8192 bipolar
  is a POINT MASS by LLN concentration of measure. All quantiles of a single-regime
  cal collapse to the same tau (v7 empirical: P5=P10=P25=P50=0.699951 exactly
  bit-identical). Widening alpha on same source is degenerate.

  V8 SURGICAL FIX: vary the cal SOURCE (regime), not alpha on same source.

Arms:
- ARM_FIXED_BASELINE:       tau=0.40 (unchanged; positive control)
- ARM_CONFORMAL_CLEAN:      tau=P5 of CLEAN cal in-KB    (analytical ~1.000)
- ARM_CONFORMAL_MODERATE:   tau=P5 of MODERATE cal in-KB (analytical ~0.700)
- ARM_CONFORMAL_MID:        tau=midpoint(P10_in_kb, P90_ood) of MODERATE cal (~0.367)

Also builds cal PER REGIME at cell startup (v7 only did per-regime for MID arm).

NEW HF gate: HARD_FAIL_CAL_SOURCE_NOT_DISTINCT catches cal construction bugs early.

Phase axes: 4 arms x 3 regimes x 3 bands = 36 units.
FULL: 36 x 60 = 2160 records/seed.
SMOKE: 36 x 20 = 720 records/seed. SMOKE at full-N=8192 (Check A path per
DISCRIMINATOR-MUST-SURVIVE-SCALE Fix #C).

CHUNKED single-seed-per-cell. SEED=7 pinned.

PRE-REG: preregs/2026-07-01_refuse_gate_v8_conformal_v1.md

4 defensive patterns (cell-template S13):
  1. start_marker (STARTED metrics before heavy work)
  2. crash-diag (outer try with import-crash sentinel)
  3. per-unit checkpoint (write_partial_key per seed)
  4. heartbeat (per-phase-point flush print)

ASCII-only. numpy-only (no torch); CPU-native.
Author: exp_dev 2026-07-01 (Opus 4.7 1M, agent-spawn).
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import json
import os
import time
import traceback
from pathlib import Path
from typing import Any, Dict

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    resumable_seeds, write_partial_key, aggregate_partials,
)

# Pinned seed for this sibling
SEED = 7
ANCHOR_NAME = "substrate_refuse_gate_v8_conformal_v1_seed_%d" % SEED

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ap.add_argument("--mode", type=str, default=None,
                 help="explicit mode: selftest | smoke | full")
_ap.add_argument("--timeout", type=int, default=1800,
                 help="per-cell timeout seconds (for runner enforcement)")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()

# Precedence: --mode > --smoke/--self-test flags > env name > HDLAB_RUN_MODE > "full"
if _ARGS.mode:
    RUN_MODE = _ARGS.mode.lower()
elif _ARGS.smoke or _NAME_SAYS_SMOKE:
    RUN_MODE = "smoke"
elif _ARGS.self_test:
    RUN_MODE = "selftest"
else:
    RUN_MODE = os.environ.get("HDLAB_RUN_MODE", "full").lower()

SELF_TEST_MODE = (RUN_MODE == "selftest")
SMOKE_MODE = (RUN_MODE == "smoke")

CONFIG_VERSION = (
    "ANCHOR=%s,arms=[FIXED_BASELINE,CONFORMAL_CLEAN,CONFORMAL_MODERATE,CONFORMAL_MID],"
    "regimes=[clean,moderate,heavy],bands=[in_kb,borderline,ood],"
    "cal_size_per_regime=100(50in+50ood),V_REL=256,SEED=%d,mode=%s,"
    "N=8192(smoke==full,CheckA),V_C_per_cat=200,V_C_IN=600,"
    "n_queries_per_unit=[20|60],"
    "expected_units=36,expected_records_full=2160,expected_records_smoke=720,"
    "HP=(moderate,borderline),HP_floor=0.85,"
    "v8_surgical_fix=cal_source_variation_not_alpha,"
    "hardening=L1startmarker+L2crashdiag+L3perunitckpt+L4heartbeat+CHUNKED_PER_SEED"
) % (ANCHOR_NAME, SEED, RUN_MODE)

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
            "_hardening_marker": "v8_refuse_gate_conformal_chunked",
        }
        if extra:
            m.update(extra)
        tmp_path = out_dir / "metrics.json.tmp"
        final_path = out_dir / "metrics.json"
        tmp_path.write_text(json.dumps(m, indent=2, default=str),
                            encoding="utf-8")
        os.replace(str(tmp_path), str(final_path))
    except Exception as e:
        print("[_write_minimal_metrics] FAIL: %s" % e,
              file=sys.stderr, flush=True)


def _write_import_crash_sentinel(exc: BaseException) -> None:
    try:
        env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
        out_dir = REPO / "data" / ("exp_" + env_name)
        out_dir.mkdir(parents=True, exist_ok=True)
        s = {
            "anchor_name": ANCHOR_NAME,
            "verdict": "UNKNOWN",
            "verdict_msg": "IMPORT_CRASH: %s: %s" % (type(exc).__name__, exc),
            "summary": "IMPORT_CRASH: %s: %s" % (type(exc).__name__, exc),
            "elapsed_s": 0.0,
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "_traceback": traceback.format_exc(),
            "_hardening_marker": "v8_refuse_gate_conformal_import_crash",
        }
        (out_dir / "metrics.json").write_text(json.dumps(s, indent=2),
                                              encoding="utf-8")
        (out_dir / "import_crash.json").write_text(json.dumps(s, indent=2),
                                                   encoding="utf-8")
    except Exception as e:
        print("[_write_import_crash_sentinel] FAIL: %s" % e,
              file=sys.stderr, flush=True)


def main() -> int:
    _RESULTS_HOLDER["started_at"] = time.time()
    env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    out_dir = REPO / "data" / ("exp_" + env_name)
    out_dir.mkdir(parents=True, exist_ok=True)

    _write_minimal_metrics(out_dir, "STARTED",
                           "STARTED: pid=%d mode=%s seed=%d"
                           % (os.getpid(), RUN_MODE, SEED),
                           extra={"_phase": "init"})

    from experiments._substrate_refuse_gate_v8_conformal_v1_core import (
        run_one_seed_conformal, aggregate_and_verdict, selftest,
        get_backend_label, N_FULL, N_SMOKE,
    )

    backend = get_backend_label()
    print("[%s] mode=%s seed=%d backend=%s"
          % (ANCHOR_NAME, RUN_MODE, SEED, backend), flush=True)

    if SELF_TEST_MODE:
        try:
            ok, msg = selftest(SEED)
            verdict = "SELFTEST_OK" if ok else "SELFTEST_FAIL"
            _write_minimal_metrics(out_dir, verdict, msg,
                                   extra={"_phase": "selftest_done",
                                          "backend": backend})
            print("[selftest] %s: %s" % (verdict, msg), flush=True)
            return 0 if ok else 1
        except SystemExit:
            raise
        except Exception as e:
            _write_minimal_metrics(out_dir, "SELFTEST_FAIL",
                                   "SELFTEST_FAIL: %s" % e,
                                   extra={"_traceback": traceback.format_exc()})
            print("[selftest] FAIL: %s" % e, file=sys.stderr, flush=True)
            return 1

    seeds_list = [SEED]
    N_used = N_SMOKE if SMOKE_MODE else N_FULL
    run_config = {"N": N_used, "run_mode": RUN_MODE, "anchor": ANCHOR_NAME}
    done, remaining = resumable_seeds(seeds_list, out_dir, run_config=run_config)
    print("[ckpt] %d/%d done; running %s" % (len(done), len(seeds_list),
                                              remaining), flush=True)

    for seed in remaining:
        _write_minimal_metrics(out_dir, "RUNNING",
                               "RUNNING: seed=%d mode=%s" % (seed, RUN_MODE),
                               extra={"_phase": "seed_running",
                                      "_current_seed": seed,
                                      "backend": backend})
        t0 = time.time()
        result = run_one_seed_conformal(seed, run_mode=RUN_MODE)
        result["N"] = N_used
        result["anchor_name"] = ANCHOR_NAME
        result["config_version"] = CONFIG_VERSION
        write_partial_key(out_dir, seed, result)
        print("[seed=%d] complete in %.1fs (%s units, %s records)"
              % (seed, time.time() - t0,
                 result.get("observed_n_units", "NA"),
                 result.get("observed_n_records", "NA")), flush=True)

    per_seed = aggregate_partials(out_dir, seeds_list, run_config=run_config)
    final = aggregate_and_verdict(per_seed, run_mode=RUN_MODE)
    final["anchor_name"] = ANCHOR_NAME
    final["elapsed_s"] = round(time.time() - _RESULTS_HOLDER["started_at"], 2)
    final["ts_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    final["pid"] = os.getpid()
    final["run_mode"] = RUN_MODE
    final["config_version"] = CONFIG_VERSION
    final["_hardening_marker"] = "v8_refuse_gate_conformal_chunked"
    final["backend"] = backend
    final["seed"] = SEED
    final["n_seeds"] = 1
    final["corpus_provenance"] = ("synthetic_substrate_refuse_gate_v8_conformal_"
                                   "4_arm_3_regime_3_band_calpersubstrate_v1")
    final["n_llm_calls"] = _LLM_CALL_COUNTER[0]

    assert _LLM_CALL_COUNTER[0] == 0, \
        "LLM_CALL_GATE_BREACH: substrate-only required"

    tmp_path = out_dir / "metrics.json.tmp"
    final_path = out_dir / "metrics.json"
    tmp_path.write_text(json.dumps(final, indent=2, default=str),
                         encoding="utf-8")
    os.replace(str(tmp_path), str(final_path))

    print("[%s] DONE: %s" % (ANCHOR_NAME, final["verdict_msg"]), flush=True)
    print("[%s] cardinality observed_units=%s expected_units=%s "
          "observed_records=%s expected_records=%s ok=%s"
          % (ANCHOR_NAME, final.get("observed_n_units"),
             final.get("expected_n_units"),
             final.get("observed_n_records"),
             final.get("expected_n_records"),
             final.get("cardinality_ok")), flush=True)
    return 0


if __name__ == "__main__":
    try:
        rc = main()
    except SystemExit:
        raise
    except Exception as e:
        _write_import_crash_sentinel(e)
        print("[main] OUTER_EXCEPTION: %s" % e, file=sys.stderr, flush=True)
        traceback.print_exc()
        rc = 1
    sys.exit(rc)
