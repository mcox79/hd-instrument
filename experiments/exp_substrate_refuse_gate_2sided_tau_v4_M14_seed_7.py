"""substrate_refuse_gate_2sided_tau_v4_M14 sibling seed=7.

v4 revival per research drill notes/research_M14_v4_revival_drill_2026-07-01.md
sec (a). Highest-CG revival path (P=0.55; 5x-drill eligible with 4 cross-domain
support: SDT + tail-conformal + TOST + unequal-var SDT).

v3 HF root-cause (Skunkworks 7a89856d landing on seed_7_smoke):
    FIXED @ moderate refuse_precision = 0.667
    BAYESIAN_CI:      lift = -0.193  (actively HURTS)
    PERCENTILE:       lift = -0.076
    SLIDING_WINDOW:   lift =  0.000
One-sided tau trades recall for precision loss (net structural loss). SDT
literature predicts exactly this failure mode for one-sided criterion against
signal-plus-noise with unequal variances.

v4 mechanism class swap: 2-SIDED TAU BAND.
    tau_low + tau_high adapted SEPARATELY on partitioned history streams
    Refuse if score <= tau_high (either tail-refuse or ambiguity-band-refuse)
    Accept if score > tau_high

Composes with M1.3 NoiseChannel CG (c5e5e66a); reuses v3 additive_gaussian wiring
(proven regime-monotonic).

4 ARMS (arms-must-differ):
    FIXED_V_REL_256 / TWO_SIDED_PERCENTILE / TWO_SIDED_BAYESIAN_CI /
    TWO_SIDED_SLIDING_WINDOW

Phase axes: 3 NoiseChannel regimes (clean/moderate/heavy) x 3 difficulty bands
(in_KB/borderline/OOD) x 4 arms = 36 phase points per seed.

CHUNKED single-seed-per-cell. SEED=7 pinned.

PRE-REG: preregs/2026-07-01_substrate_refuse_gate_2sided_tau_v4_M14.md
PROT-018: anchor has no _n<N> suffix (multi-regime x multi-band sweep).

4 defensive patterns (cell-template S13): start_marker + crash-diag +
per-unit checkpoint + heartbeat.

ASCII-only. numpy + torch (NoiseChannel is torch); CPU-native.
Author: exp_dev 2026-07-01 (Opus 4.7 1M, agent-spawn).

MILESTONE SIGNIFICANCE: if HP fires, closes M3 M1.4 (glass-box conversational
calibration primitive; M3-blocking).
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

SEED = 7
ANCHOR_NAME = "substrate_refuse_gate_2sided_tau_v4_M14_seed_%d" % SEED

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ap.add_argument("--timeout", type=int, default=1800,
                 help="per-cell timeout seconds (runner enforcement)")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _NAME_SAYS_SMOKE)
            else ("selftest" if _ARGS.self_test
                  else os.environ.get("HDLAB_RUN_MODE", "full").lower()))
SELF_TEST_MODE = bool(_ARGS.self_test)
SMOKE_MODE = (RUN_MODE == "smoke")

CONFIG_VERSION = (
    "ANCHOR=%s,arms=[FIXED_V_REL_256,TWO_SIDED_PERCENTILE,"
    "TWO_SIDED_BAYESIAN_CI,TWO_SIDED_SLIDING_WINDOW],"
    "regimes=[clean,moderate,heavy],bands=[in_KB,borderline,OOD],V_REL=256,"
    "SEED=%d,mode=%s,N=8192,V_C_per_cat=200,n_queries_per_band=[30|80],"
    "expected_units=36,expected_records_full=2880,expected_records_smoke=1080,"
    "noise_channel_mode=additive_gaussian,cortex_seed=seed*10007+42,"
    "mechanism_class=2sided_tau_low_plus_tau_high_median_split_history,"
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
            "_hardening_marker": "v4_refuse_gate_2sided_tau_noisechannel_M14_chunked",
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
            "_hardening_marker": "v4_refuse_gate_2sided_tau_noisechannel_M14_import_crash",
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

    from experiments._substrate_refuse_gate_2sided_tau_v4_M14_core import (
        run_one_seed_v4, aggregate_and_verdict, selftest,
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
        result = run_one_seed_v4(seed, run_mode=RUN_MODE)
        result["N"] = N_used
        result["anchor_name"] = ANCHOR_NAME
        result["config_version"] = CONFIG_VERSION
        write_partial_key(out_dir, seed, result)
        print("[seed=%d] complete in %.1fs (%d units, %d records)"
              % (seed, time.time() - t0, result["observed_n_units"],
                 result["observed_n_records"]), flush=True)

    per_seed = aggregate_partials(out_dir, seeds_list, run_config=run_config)
    final = aggregate_and_verdict(per_seed, run_mode=RUN_MODE)
    final["anchor_name"] = ANCHOR_NAME
    final["elapsed_s"] = round(time.time() - _RESULTS_HOLDER["started_at"], 2)
    final["ts_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    final["pid"] = os.getpid()
    final["run_mode"] = RUN_MODE
    final["config_version"] = CONFIG_VERSION
    final["_hardening_marker"] = "v4_refuse_gate_2sided_tau_noisechannel_M14_chunked"
    final["backend"] = backend
    final["seed"] = SEED
    final["n_seeds"] = 1
    final["corpus_provenance"] = ("synthetic_substrate_refuse_gate_v4_M14_"
                                  "cortex_noisechannel_additive_gaussian_2sided_tau")
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
