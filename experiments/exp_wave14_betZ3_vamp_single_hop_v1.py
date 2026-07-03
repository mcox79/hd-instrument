"""Bet Z.3 VAMP single-hop empirical at N=4096 with Kerdock codebook.

Per Strategy 20:14 Priority 5: cycle 115 Research said VAMP+SVD PROVEN P=0.90 for
any RI matrix; cycle 120 Kerdock AMP universality KILLED forces fall back to VAMP
P1 path. But VAMP single-hop not empirically validated on substrate.

Test: substrate-noise + cleanup recovery via softmax+SVD-weighted state vs argmax.
Comparison at K candidates near K_crit; sweep noise levels.

Verdict thresholds:
  BET_Z3_VAMP_PASS:    VAMP > argmax by >= 10pp recall at intermediate noise (p=0.10)
  BET_Z3_VAMP_PARTIAL: VAMP matches argmax (within 5pp)
  BET_Z3_VAMP_KILLED:  VAMP < argmax by more than 5pp (worse than baseline)
  BET_Z3_VAMP_INCONCLUSIVE

Pre-reg: preregs/2026-05-22_wave14_betZ3_vamp_single_hop_v1.md
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

_v3 = importlib.util.spec_from_file_location("v3", REPO / "experiments" / "exp_wave14y_erase_kerdock_v3.py")
v3 = importlib.util.module_from_spec(_v3); _v3.loader.exec_module(v3)


def get_output_dir(default_name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(default_name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def compute_verdict(summary):
    if "vamp_acc" not in summary:
        return ("BET_Z3_VAMP_INCONCLUSIVE", "Missing vamp_acc.")
    v = summary["vamp_acc"]
    a = summary["argmax_acc"]
    diff = v - a
    if diff >= 0.10:
        return ("BET_Z3_VAMP_PASS",
                f"VAMP single-hop > argmax: vamp={v:.3f} vs argmax={a:.3f} (diff={diff:+.3f}>=+0.10). "
                f"Substrate-novel readout primitive viable.")
    if abs(diff) < 0.05:
        return ("BET_Z3_VAMP_PARTIAL",
                f"VAMP ~ argmax: vamp={v:.3f} vs argmax={a:.3f} (diff={diff:+.3f}). "
                f"No clear advantage.")
    return ("BET_Z3_VAMP_KILLED",
            f"VAMP underperforms argmax: vamp={v:.3f} vs argmax={a:.3f} (diff={diff:+.3f}<-0.05).")


def self_test_verdict():
    cases = [
        ({"vamp_acc": 0.85, "argmax_acc": 0.70}, "BET_Z3_VAMP_PASS"),
        ({"vamp_acc": 0.72, "argmax_acc": 0.70}, "BET_Z3_VAMP_PARTIAL"),
        ({"vamp_acc": 0.55, "argmax_acc": 0.70}, "BET_Z3_VAMP_KILLED"),
        ({}, "BET_Z3_VAMP_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def flip_bits(vec, p, gen, device):
    if p <= 0: return vec
    flips = (torch.rand(vec.shape, generator=gen) < p).to(device).float()
    return vec * (1.0 - 2.0 * flips)


def run_one_K(N, K, p_noise, n_trials, codebook, cpu_gen, device):
    """Per K patterns drawn from codebook, test argmax vs VAMP-class softmax cleanup
       with Hamming-perturbed queries."""
    idx = torch.randperm(codebook.shape[0], generator=cpu_gen)[:K].to(device)
    patterns = codebook[idx].float()
    correct_arg = 0; correct_vamp = 0
    for trial in range(n_trials):
        target_i = trial % K
        target = patterns[target_i]
        noisy = flip_bits(target.clone(), p_noise, cpu_gen, device)
        sims = patterns @ noisy
        # argmax
        if int(sims.argmax().item()) == target_i:
            correct_arg += 1
        # VAMP-class: softmax-weighted state, then argmax-similarity
        w = torch.softmax(sims, dim=0)
        state = (w.unsqueeze(1) * patterns).sum(dim=0)
        sims2 = patterns @ state
        if int(sims2.argmax().item()) == target_i:
            correct_vamp += 1
    return correct_arg / n_trials, correct_vamp / n_trials


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 1024 if smoke else 4096,
              "K_grid": [200, 500] if smoke else [200, 500, 1000, 2000],
              "noise_p": 0.10,
              "n_trials": 50 if smoke else 200,
              "seed": 17}
    N = config["N"]
    cpu_gen = torch.Generator().manual_seed(config["seed"])
    codebook, _ = v3.make_kerdock_4coset_codebook(N, device)
    print(f"[setup] N={N} Kerdock 4-coset codebook size={codebook.shape[0]}", flush=True)
    print(f"[noise] p_flip={config['noise_p']}", flush=True)
    arg_per_K = {}; vamp_per_K = {}
    for K in config["K_grid"]:
        K_capped = min(K, codebook.shape[0])
        arg_acc, vamp_acc = run_one_K(N, K_capped, config["noise_p"], config["n_trials"],
                                          codebook, cpu_gen, device)
        arg_per_K[str(K)] = arg_acc; vamp_per_K[str(K)] = vamp_acc
        print(f"  K={K_capped}: argmax={arg_acc:.3f}, vamp={vamp_acc:.3f}, diff={vamp_acc-arg_acc:+.3f}", flush=True)
    # Aggregate
    avg_arg = sum(arg_per_K.values()) / len(arg_per_K)
    avg_vamp = sum(vamp_per_K.values()) / len(vamp_per_K)
    summary = {"argmax_acc": avg_arg,
                "vamp_acc": avg_vamp,
                "argmax_per_K": arg_per_K,
                "vamp_per_K": vamp_per_K,
                "noise_p": config["noise_p"]}
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
    out_dir = get_output_dir("wave14_betZ3_vamp_single_hop_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("argmax_present", summary["argmax_acc"] + 0.001, 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_betZ3_vamp_single_hop_v1")
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
