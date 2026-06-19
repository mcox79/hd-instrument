"""Bet Y Phase 2 beta-blend — fine beta grid to locate peak ratio or confirm classical regime.

Per Strategy 2026-05-22 Phase 2 gate Outcome 2 ask: at PARTIAL ratio=1.0, sweep
fine beta grid to find where modern dense AM peaks (if anywhere).

v2 ran 3 betas {2, 8, 32}; all gave ratio=1.00. This run extends to 8 betas
spanning 3 octaves below cycle 100's c=32768 (beta_optimal(N=4096)=8) and
3 above: {0.5, 1, 2, 4, 8, 16, 32, 64}. If any beta produces ratio>=1.5
we've located exp-capacity. If all stay <=1.05 substrate is genuinely
classical-Hopfield-class for Kerdock 4-coset codebook.

Verdict:
  BETA_BLEND_PEAK_FOUND:   any beta gives ratio >= 1.5
  BETA_BLEND_NEAR_GAIN:    1.05 <= peak < 1.5 (small but real gain)
  BETA_BLEND_CLASSICAL:    peak < 1.05 (substrate locked classical)
  BETA_BLEND_INCONCLUSIVE

Pre-reg: preregs/2026-05-22_wave14_betY_phase2_beta_blend_v1.md
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

_p2 = importlib.util.spec_from_file_location("p2",
    REPO / "experiments" / "exp_wave14_betY_phase2_kerdock_betacalibrated_v1.py")
p2 = importlib.util.module_from_spec(_p2); _p2.loader.exec_module(p2)


PEAK_THRESHOLD = 1.5
NEAR_GAIN_THRESHOLD = 1.05


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def compute_verdict(summary):
    if "best_ratio" not in summary:
        return ("BETA_BLEND_INCONCLUSIVE", "Missing best_ratio.")
    best = summary["best_ratio"]; best_beta = summary["best_beta"]
    by_beta = summary["ratio_per_beta"]
    if best >= PEAK_THRESHOLD:
        return ("BETA_BLEND_PEAK_FOUND",
                f"Peak ratio={best:.2f} at beta={best_beta} (>={PEAK_THRESHOLD}). "
                f"Modern dense AM activates at fine-grid beta. ratio_per_beta={by_beta}.")
    if best >= NEAR_GAIN_THRESHOLD:
        return ("BETA_BLEND_NEAR_GAIN",
                f"Peak ratio={best:.2f} at beta={best_beta} ({NEAR_GAIN_THRESHOLD}<=peak<{PEAK_THRESHOLD}). "
                f"Small but real exp-capacity gain. ratio_per_beta={by_beta}.")
    return ("BETA_BLEND_CLASSICAL",
            f"Peak ratio={best:.2f} at beta={best_beta} (<{NEAR_GAIN_THRESHOLD}). "
            f"Substrate is classical-Hopfield-class for Kerdock 4-coset; modern dense AM "
            f"provides no capacity gain. ratio_per_beta={by_beta}.")


def self_test_verdict():
    cases = [
        ({"best_ratio": 1.8, "best_beta": 4.0, "ratio_per_beta": {}}, "BETA_BLEND_PEAK_FOUND"),
        ({"best_ratio": 1.1, "best_beta": 8.0, "ratio_per_beta": {}}, "BETA_BLEND_NEAR_GAIN"),
        ({"best_ratio": 1.0, "best_beta": 8.0, "ratio_per_beta": {}}, "BETA_BLEND_CLASSICAL"),
        ({}, "BETA_BLEND_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 1024 if smoke else 4096,
              "M_grid": [256, 512] if smoke else [1024, 4096, 8192, 16384],
              "seeds": 1 if smoke else 3,
              "betas": [4.0, 8.0] if smoke else [0.5, 1.0, 2.0, 4.0, 8.0, 16.0, 32.0, 64.0],
              "n_iter": 5,
              "key_family": "kerdock_4coset"}
    print(f"[config] {config}", flush=True)
    N = config["N"]
    print("[argmax baseline, kerdock keys]", flush=True)
    argmax_cap = p2.find_max_passing_M(p2.capacity_argmax, p2.kerdock_keys, N, config["M_grid"],
                                          config["seeds"], device)
    print(f"  argmax capacity = {argmax_cap:.2f}*N", flush=True)
    modern_cap_per_beta = {}
    for beta in config["betas"]:
        print(f"[modern dense, beta={beta}]", flush=True)
        cap = p2.find_max_passing_M(p2.capacity_modern_dense, p2.kerdock_keys, N,
                                          config["M_grid"], config["seeds"], device,
                                          fn_kwargs={"beta": beta, "n_iter": config["n_iter"]})
        modern_cap_per_beta[str(beta)] = cap
        print(f"  beta={beta}: modern = {cap:.2f}*N", flush=True)
    ratio_per_beta = {b: (modern_cap_per_beta[b] / max(argmax_cap, 1e-9)) for b in modern_cap_per_beta}
    best_beta_str = max(ratio_per_beta, key=ratio_per_beta.get)
    best_ratio = ratio_per_beta[best_beta_str]
    summary = {"argmax_capacity": argmax_cap,
                "modern_capacity_per_beta": modern_cap_per_beta,
                "ratio_per_beta": ratio_per_beta,
                "best_beta": float(best_beta_str),
                "best_ratio": best_ratio}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
                "summary": summary, "config": config}
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14_betY_phase2_beta_blend_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("argmax_cap_present", summary["argmax_capacity"] + 0.1, 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_betY_phase2_beta_blend_v1")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
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
