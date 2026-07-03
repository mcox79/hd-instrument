"""Bet Q Facilitation-vs-Nucleation — substrate shows nucleation dynamics under perturbation.

Per cap_map v78 Bet Q: substrate exhibits glassy facilitation (nearby states
activate; cascading retrieval) vs random fluctuation (nucleation). Test:
perturb a stored state by k bits, measure retrieval probability as fn of k.
Facilitation: smooth recovery basin (high acc until threshold then sharp drop).
Nucleation: gradual decay (no clear threshold).

Substrate analog: stored key k_i; perturb to k_i' with Hamming distance d;
measure argmax recovery rate vs d. Plot d/N → recovery_rate; look for
sigmoid (facilitation) vs gradual (nucleation).

Pre-reg: preregs/2026-05-22_wave14_betQ_M4N.md
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

_v1 = importlib.util.spec_from_file_location("v1", REPO / "experiments" / "exp_wave14r_erase_orthkeys_v1.py")
v1 = importlib.util.module_from_spec(_v1); _v1.loader.exec_module(v1)


def get_output_dir(default_name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(default_name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def compute_verdict(summary):
    if "transition_sharpness" not in summary:
        return ("BET_Q_INCONCLUSIVE", "Missing.")
    sharp = summary["transition_sharpness"]
    if sharp >= 2.0:
        return ("BET_Q_FACILITATION",
                f"Sharp transition observed: sharpness={sharp:.2f}>=2.0. Substrate exhibits "
                f"glassy facilitation (sigmoid recovery curve).")
    if sharp < 1.0:
        return ("BET_Q_NUCLEATION",
                f"Gradual decay: sharpness={sharp:.2f}<1.0. Substrate exhibits nucleation "
                f"(no clear threshold). Random-fluctuation regime.")
    return ("BET_Q_INTERMEDIATE",
            f"Intermediate sharpness {sharp:.2f}. Neither facilitation nor pure nucleation.")


def self_test_verdict():
    cases = [
        ({"transition_sharpness": 3.5}, "BET_Q_FACILITATION"),
        ({"transition_sharpness": 0.5}, "BET_Q_NUCLEATION"),
        ({"transition_sharpness": 1.4}, "BET_Q_INTERMEDIATE"),
        ({}, "BET_Q_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run_one_seed(seed, config, device):
    N = config["N"]
    M = config["M"]
    gen = torch.Generator(device=device).manual_seed(seed)
    cpu_gen = torch.Generator().manual_seed(seed + 1009)
    keys = 2.0 * (torch.rand((M, N), generator=gen, device=device) > 0.5).float() - 1.0
    values = 2.0 * (torch.rand((M, N), generator=gen, device=device) > 0.5).float() - 1.0
    W = (values.T @ keys) / N
    # Sweep perturbation distance d
    fractions = [0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50]
    recovery = {}
    for frac in fractions:
        d_hamming = int(frac * N)
        n_test = min(50, M)
        correct = 0
        for i in range(n_test):
            k_perturbed = v1.hamming_perturb(keys[i:i+1], 1, d_hamming, cpu_gen, device)[0]
            retrieved = k_perturbed @ W.T
            pred = int((retrieved @ values.T).argmax().item())
            if pred == i:
                correct += 1
        recovery[frac] = correct / n_test
    # Sharpness: ratio of max derivative to mean derivative
    vals = [recovery[f] for f in fractions]
    diffs = [abs(vals[i+1] - vals[i]) for i in range(len(vals) - 1)]
    max_d = max(diffs) if diffs else 0
    mean_d = sum(diffs) / max(len(diffs), 1)
    sharpness = max_d / max(mean_d, 1e-9)
    return {"recovery_curve": {str(f): recovery[f] for f in fractions},
             "sharpness": sharpness}


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 1024 if smoke else 4096,
              "M": 256 if smoke else 16384,
              "seeds": [17] if smoke else [17, 23, 31]}
    sharp_list = []
    curves = []
    for s in config["seeds"]:
        r = run_one_seed(s, config, device)
        sharp_list.append(r["sharpness"])
        curves.append(r["recovery_curve"])
        print(f"  seed={s}: sharpness={r['sharpness']:.3f}", flush=True)
    summary = {"transition_sharpness": sum(sharp_list) / len(sharp_list),
                "per_seed_curves": curves}
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
    out_dir = get_output_dir("wave14_betQ_M4N_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("sharpness_present", summary["transition_sharpness"], 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_betQ_M4N")
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
