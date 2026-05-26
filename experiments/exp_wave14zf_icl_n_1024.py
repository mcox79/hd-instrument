"""ICL saturation at N=1024 - smallest substrate width tested.

yq tested N=2048, yw tested N=4096. zf at N=1024 completes the N-scaling
story for ICL saturation.

Pre-reg: preregs/2026-05-21_wave14zf_icl_n_1024.md
"""
from __future__ import annotations
import argparse, importlib.util, json, math, os, sys, time
from pathlib import Path
import torch
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from verification import oracle  # noqa: E402
try:
    from hdlab.session_log import log_event
except ImportError:
    def log_event(*a, **k): pass

_yw = importlib.util.spec_from_file_location("yw", REPO / "experiments" / "exp_wave14w_icl_extended.py")
yw = importlib.util.module_from_spec(_yw); _yw.loader.exec_module(yw)


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def compute_verdict(summary):
    verdict, msg = yw.compute_verdict(summary)
    for prefix in ("ICL_EXTENDED_", "ICL_POOL_COLLAPSE_", "ICL_CORPUS_"):
        if verdict.startswith(prefix):
            return ("ICL_N1024_" + verdict[len(prefix):], msg)
    return (verdict, msg)


def self_test_verdict():
    cases = [
        # Strong scaling: gains grow fast enough that yw's full slope > 0.10 threshold
        ({"ictx_list": [1024, 4096, 16384, 32768],
          "mean_gain": [0.4, 0.7, 1.0, 1.3],
          "std_gain": [0.05, 0.05, 0.05, 0.05],
          "mean_entropy_per_ictx": [2.0, 2.5, 2.7, 3.0],
          "distinct_chunks_floor_ok": True},
         "ICL_N1024_NO_SATURATION"),
        ({}, "ICL_N1024_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed (2/2 cases)", flush=True)


def run_experiment(smoke):
    # Override yw module-level constants directly (yw was loaded via spec
    # so it's not in sys.modules - can't reload, but can mutate)
    yw.N_FULL = 1024
    yw.N_SMOKE = 256
    yw.ICTX_FULL = [512, 2048, 8192, 16384]
    yw.ICTX_SMOKE = [64, 256]
    yw.SEEDS_FULL = [17, 23, 31]
    yw.SEEDS_SMOKE = [17]
    summary, verdict, msg, elapsed, per_seed = yw.run_full(smoke=smoke)
    # Rename verdict prefix
    for prefix in ("ICL_EXTENDED_", "ICL_POOL_COLLAPSE_", "ICL_CORPUS_"):
        if verdict.startswith(prefix):
            verdict = "ICL_N1024_" + verdict[len(prefix):]
            break
    return summary, verdict, msg, elapsed, per_seed


def write_metrics(out_dir, summary, verdict, msg, elapsed, per_seed, config):
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
                "summary": summary, "config": config, "per_seed": per_seed}
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14zf_icl_n_1024_smoke")
    summary, verdict, msg, elapsed, per_seed = run_experiment(smoke=True)
    write_metrics(out_dir, summary, verdict, msg, elapsed, per_seed, {"mode": "smoke", "N": 256})
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14zf_icl_n_1024")
    summary, verdict, msg, elapsed, per_seed = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, per_seed, {"mode": "full", "N": 1024})
    print(f"\nDONE: {verdict}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test: self_test_verdict(); return 0
    if args.smoke: run_smoke(); return 0
    run_main(); return 0


if __name__ == "__main__":
    sys.exit(main())
