"""Bet R polynomial p-body coupling — finite-degree Krotov energy vs argmax.

Per Strategy forward direction #4 + R27 L.1 (Musa 2025 inspiration). Tests
whether closed-form polynomial Krotov cleanup at p in {2, 4, 8} gives a
capacity advantage over argmax with Kerdock 4-coset keys at N=4096.

Distinguishes from Bet Y (softmax = all p-bodies weighted by Taylor):
polynomial cleanup state_{t+1} = sum_mu (s . ξ_mu)^(p-1) * ξ_mu has finite
p-body coupling only. Tests whether finite p activates exp-capacity regime
that softmax could not (Bet Y Phase 2 ratio=1.0 across betas).

Cleanup iteration (Krotov-Demircigil polynomial energy E(s) = -sum_mu (s.ξ)^p):
  state_{t+1} = sum_mu p*(s_t . ξ_mu)^(p-1) * ξ_mu   (gradient step)
Normalized to unit-bipolar-ish via sign at the end for final readout.

Verdict thresholds:
  PBODY_PASS:     best ratio over p in {2,4,8} >= 1.5 (substrate-novel gain)
  PBODY_PARTIAL:  1.05 <= best ratio < 1.5 (small but real gain)
  PBODY_NOGAIN:   best ratio < 1.05 (no finite-p advantage over argmax)
  PBODY_INCONCLUSIVE

Pre-reg: preregs/2026-05-22_wave14_betR_pbody_polynomial_v1.md
"""
from __future__ import annotations
import argparse, importlib.util, json, math, os, sys, time
from pathlib import Path
import torch
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
from verification import oracle  # noqa: E402
try:
    from hdlab.session_log import log_event
except ImportError:
    def log_event(*a, **k): pass

_p2 = importlib.util.spec_from_file_location("p2",
    REPO / "experiments" / "exp_wave14_betY_phase2_kerdock_betacalibrated_v1.py")
p2 = importlib.util.module_from_spec(_p2); _p2.loader.exec_module(p2)


PASS_RATIO = 1.5
PARTIAL_RATIO = 1.05


def get_output_dir(default_name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(default_name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def compute_verdict(summary):
    if "best_ratio" not in summary:
        return ("PBODY_INCONCLUSIVE", "Missing best_ratio.")
    best = summary["best_ratio"]; best_p = summary["best_p"]
    bp = summary["ratio_per_p"]
    if best >= PASS_RATIO:
        return ("PBODY_PASS",
                f"Polynomial p-body cleanup beats argmax: best ratio={best:.2f} at p={best_p} "
                f"(>={PASS_RATIO}). Substrate finite p-body coupling activates exp-capacity. "
                f"ratio_per_p={bp}.")
    if best >= PARTIAL_RATIO:
        return ("PBODY_PARTIAL",
                f"Polynomial p-body cleanup gives small gain: best ratio={best:.2f} at p={best_p} "
                f"({PARTIAL_RATIO}<=ratio<{PASS_RATIO}). ratio_per_p={bp}.")
    return ("PBODY_NOGAIN",
            f"Polynomial p-body cleanup matches argmax: best ratio={best:.2f} at p={best_p} "
            f"(<{PARTIAL_RATIO}). Substrate finite p-body provides no gain over argmax with "
            f"Kerdock 4-coset keys. ratio_per_p={bp}.")


def self_test_verdict():
    cases = [
        ({"best_ratio": 1.8, "best_p": 4, "ratio_per_p": {}}, "PBODY_PASS"),
        ({"best_ratio": 1.2, "best_p": 4, "ratio_per_p": {}}, "PBODY_PARTIAL"),
        ({"best_ratio": 1.0, "best_p": 4, "ratio_per_p": {}}, "PBODY_NOGAIN"),
        ({}, "PBODY_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def capacity_polynomial_pbody(keys, values, N, p, n_iter):
    """Polynomial Krotov: state_{t+1} = sum_mu (s_t . key_mu)^(p-1) * value_mu."""
    M = keys.shape[0]
    W = (values.T @ keys) / N
    correct = 0
    for i in range(M):
        state = (keys[i] @ W.T).float()
        for _ in range(n_iter):
            sims = (values @ state)  # (M,) similarities
            # Gradient of E = -sum (s.v)^p with respect to s = p * sum (s.v)^(p-1) * v
            # Normalize sims to avoid overflow at large p
            sims_norm = sims / max(float(sims.abs().max()), 1e-9)
            w = sims_norm.pow(p - 1)
            state = w @ values
            # Renormalize state magnitude
            state = state / max(float(state.abs().max()), 1e-9) * math.sqrt(N)
        if int((values @ state).argmax().item()) == i:
            correct += 1
    return correct / M


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 1024 if smoke else 4096,
              "M_grid": [256, 512] if smoke else [1024, 4096, 8192, 16384],
              "seeds": 1 if smoke else 3,
              "p_values": [2, 4] if smoke else [2, 4, 8],
              "n_iter": 5,
              "key_family": "kerdock_4coset"}
    print(f"[config] {config}", flush=True)
    N = config["N"]
    argmax_cap = p2.find_max_passing_M(p2.capacity_argmax, p2.kerdock_keys, N, config["M_grid"],
                                          config["seeds"], device)
    print(f"  argmax capacity = {argmax_cap:.2f}*N", flush=True)
    poly_cap = {}
    for p in config["p_values"]:
        cap = p2.find_max_passing_M(capacity_polynomial_pbody, p2.kerdock_keys, N,
                                          config["M_grid"], config["seeds"], device,
                                          fn_kwargs={"p": p, "n_iter": config["n_iter"]})
        poly_cap[str(p)] = cap
        print(f"  p={p}: polynomial = {cap:.2f}*N", flush=True)
    ratio_per_p = {p_str: (poly_cap[p_str] / max(argmax_cap, 1e-9)) for p_str in poly_cap}
    best_p_str = max(ratio_per_p, key=ratio_per_p.get)
    best_ratio = ratio_per_p[best_p_str]
    summary = {"argmax_capacity": argmax_cap, "polynomial_capacity_per_p": poly_cap,
                "ratio_per_p": ratio_per_p, "best_p": int(best_p_str),
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
    out_dir = get_output_dir("wave14_betR_pbody_polynomial_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("argmax_present", summary["argmax_capacity"] + 0.1, 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_betR_pbody_polynomial_v1")
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
