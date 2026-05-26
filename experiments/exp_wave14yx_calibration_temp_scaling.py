"""Calibration via temperature scaling: sweep BETA, find lowest-ECE point.

yd tested at fixed BETA=8. yx sweeps BETA in {1, 2, 4, 8, 16, 32} and
finds the post-hoc calibration that minimizes ECE. Tests if temperature
scaling can rescue calibration.

Pre-reg: preregs/2026-05-21_wave14yx_calibration_temp_scaling.md
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

_v1 = importlib.util.spec_from_file_location("v1", REPO / "experiments" / "exp_wave14r_erase_orthkeys_v1.py")
v1 = importlib.util.module_from_spec(_v1); _v1.loader.exec_module(v1)
_v3 = importlib.util.spec_from_file_location("v3", REPO / "experiments" / "exp_wave14y_erase_kerdock_v3.py")
v3 = importlib.util.module_from_spec(_v3); _v3.loader.exec_module(v3)
_yd = importlib.util.spec_from_file_location("yd", REPO / "experiments" / "exp_wave14yd_calibration_fact_retrieval.py")
yd = importlib.util.module_from_spec(_yd); _yd.loader.exec_module(yd)


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def compute_verdict(summary):
    per_beta = summary.get("per_beta_ece")
    if not per_beta:
        return ("TEMPSCALE_INCONCLUSIVE", "Missing.")
    best_beta = min(per_beta.keys(), key=lambda b: per_beta[b])
    best_ece = per_beta[best_beta]
    if best_ece < 0.05:
        return (f"TEMPSCALE_RESCUES_AT_BETA_{best_beta}",
                f"Temperature scaling rescues calibration: best ECE={best_ece:.4f} "
                f"at BETA={best_beta}. Per-beta: " +
                ", ".join(f"b{b}={per_beta[b]:.3f}" for b in sorted(per_beta.keys())))
    if best_ece < 0.15:
        return (f"TEMPSCALE_MARGINAL_AT_BETA_{best_beta}",
                f"Best ECE={best_ece:.4f} at BETA={best_beta} - marginal calibration "
                f"after temperature scaling.")
    return ("TEMPSCALE_NO_RESCUE",
            f"All BETA values produce ECE > 0.15. Calibration cannot be rescued by "
            f"temperature scaling alone. Best={best_ece:.4f} at BETA={best_beta}.")


def self_test_verdict():
    cases = [
        ({"per_beta_ece": {1: 0.4, 2: 0.3, 4: 0.1, 8: 0.04, 16: 0.06, 32: 0.10}},
         "TEMPSCALE_RESCUES_AT_BETA_8"),
        ({"per_beta_ece": {1: 0.4, 2: 0.3, 4: 0.2, 8: 0.10, 16: 0.12, 32: 0.15}},
         "TEMPSCALE_MARGINAL_AT_BETA_8"),
        ({"per_beta_ece": {1: 0.5, 2: 0.45, 4: 0.40, 8: 0.35, 16: 0.30, 32: 0.25}},
         "TEMPSCALE_NO_RESCUE"),
        ({}, "TEMPSCALE_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed (4/4 cases)", flush=True)


def compute_ece_at_beta(W, keys, values, codebook, hamming_radii, beta, n_para, cpu_gen, device):
    """Single-shot ECE computation at a given BETA."""
    N = keys.size(-1)
    M = keys.size(0)
    all_confs, all_correct = [], []
    for h in hamming_radii:
        if h == 0:
            probe_keys = keys
        else:
            probe_keys = v1.hamming_perturb(keys, 1, h, cpu_gen, device)
        retrieved = probe_keys @ W.T
        sims = retrieved @ values.T / N
        scaled = sims * beta
        scaled = scaled - scaled.max(dim=1, keepdim=True).values
        exp_s = torch.exp(scaled)
        probs = exp_s / exp_s.sum(dim=1, keepdim=True)
        max_probs = probs.max(dim=1).values
        argmax = probs.argmax(dim=1)
        target = torch.arange(M, device=device)
        correct = (argmax == target)
        all_confs.extend(max_probs.tolist())
        all_correct.extend(correct.tolist())
    ece, _ = yd.compute_ece(all_confs, all_correct, n_bins=10)
    return ece, all_confs, all_correct


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 1024 if smoke else 4096,
              "M_stored": 256 if smoke else 4096,
              "betas": [1, 4, 16] if smoke else [1, 2, 4, 8, 16, 32],
              "hamming_radii": [0, 8] if smoke else [0, 4, 8, 16],
              "seeds": [17] if smoke else [17, 23, 31]}

    print(f"[config] {config}", flush=True)
    codebook, _ = v3.make_kerdock_4coset_codebook(config["N"], device)

    per_beta_ece = {b: [] for b in config["betas"]}
    for seed in config["seeds"]:
        gen = torch.Generator(device=device).manual_seed(seed)
        cpu_gen = torch.Generator().manual_seed(seed + 1009)
        keys = v3.sample_kerdock_keys(codebook, config["M_stored"], cpu_gen, device)
        values = 2.0 * (torch.rand((config["M_stored"], config["N"]), generator=gen,
                                       device=device) > 0.5).float() - 1.0
        W = (values.T @ keys) / config["N"]
        for beta in config["betas"]:
            ece, _, _ = compute_ece_at_beta(W, keys, values, codebook,
                                                config["hamming_radii"], beta, n_para=1,
                                                cpu_gen=cpu_gen, device=device)
            per_beta_ece[beta].append(ece)

    avg_per_beta = {b: sum(eces) / len(eces) for b, eces in per_beta_ece.items()}
    summary = {"per_beta_ece": avg_per_beta,
               "per_beta_ece_per_seed": per_beta_ece}
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
    out_dir = get_output_dir("wave14yx_calibration_temp_scaling_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14yx_calibration_temp_scaling")
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
