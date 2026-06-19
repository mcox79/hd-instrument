"""Substrate noise injection robustness - sweep sigma noise added to W elements.

Real deployment includes float noise, quantization, partial updates. Test how
much gaussian noise sigma (in units of W's element std) W can absorb while
keeping argmax retrieval correct. Compare Kerdock vs correlated keys.

Pre-reg: preregs/2026-05-21_wave14zm_noise_robust.md
"""
from __future__ import annotations
import argparse, importlib.util, json, os, sys, time
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

PASS_ACC = 0.95


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def first_fail_sigma(per_sigma, key, threshold):
    for s in sorted(per_sigma.keys()):
        if per_sigma[s].get(key, 1.0) < threshold:
            return s
    return None


def largest_pass_sigma(per_sigma, key, threshold):
    passing = [s for s in sorted(per_sigma.keys()) if per_sigma[s].get(key, 0.0) >= threshold]
    return max(passing) if passing else None


def compute_verdict(summary):
    arms = summary.get("by_arm", {})
    if "kerdock" not in arms:
        return ("NOISE_ROBUST_INCONCLUSIVE", "Missing.")
    k = arms["kerdock"]
    c = arms.get("correlated", {})
    if not k.get("per_sigma"):
        return ("NOISE_ROBUST_INCONCLUSIVE", "Missing per_sigma.")
    k_pass = largest_pass_sigma(k["per_sigma"], "argmax_acc", PASS_ACC)
    c_pass = largest_pass_sigma(c.get("per_sigma", {}), "argmax_acc", PASS_ACC)
    k_fail = first_fail_sigma(k["per_sigma"], "argmax_acc", PASS_ACC)
    if k_pass is None:
        return ("NOISE_ROBUST_BOTH_FAIL_IMMEDIATELY",
                f"Kerdock fails at smallest sigma. Substrate has no noise tolerance.")
    if k_fail is None:
        return (f"NOISE_ROBUST_KERDOCK_TOLERATES_SIGMA_{k_pass}",
                f"Kerdock argmax holds at all sigmas up to {k_pass}, correlated up to "
                f"{c_pass}. Substrate has noise budget for quantization.")
    if k_pass is not None and c_pass is not None and abs(k_pass - c_pass) < 1e-6:
        return ("NOISE_ROBUST_BOTH_TOLERATE",
                f"Both arms tolerate up to sigma={k_pass}. Noise tolerance is key-"
                f"structure-independent.")
    return (f"NOISE_ROBUST_KERDOCK_FAILS_AT_SIGMA_{k_fail}",
            f"Kerdock holds up to sigma={k_pass}; fails at sigma={k_fail}. "
            f"Correlated tops at sigma={c_pass}.")


def self_test_verdict():
    def mk(largest_ok=2.0, sigmas=(0.1, 0.5, 1.0, 2.0, 4.0)):
        per_sigma = {}
        for s in sigmas:
            per_sigma[s] = {"argmax_acc": 1.0 if s <= largest_ok else 0.5}
        return {"per_sigma": per_sigma}
    cases = [
        ({"by_arm": {"kerdock": mk(largest_ok=4.0), "correlated": mk(largest_ok=0.5)}},
         "NOISE_ROBUST_KERDOCK_TOLERATES_SIGMA_4.0"),
        ({"by_arm": {"kerdock": mk(largest_ok=2.0), "correlated": mk(largest_ok=2.0)}},
         "NOISE_ROBUST_BOTH_TOLERATE"),
        ({"by_arm": {"kerdock": mk(largest_ok=1.0), "correlated": mk(largest_ok=0.5)}},
         "NOISE_ROBUST_KERDOCK_FAILS_AT_SIGMA_2.0"),
        ({"by_arm": {"kerdock": mk(largest_ok=0.0), "correlated": mk(largest_ok=0.0)}},
         "NOISE_ROBUST_BOTH_FAIL_IMMEDIATELY"),
        ({}, "NOISE_ROBUST_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}\n  got: {a}")
    print(f"verdict self-test passed (5/5 cases)", flush=True)


def run_arm(arm_name, codebook, config, device):
    N = config["N"]
    M = config["M_stored"]
    sigmas = config["sigmas"]
    seeds = config["seeds"]
    per_seed = []
    for seed in seeds:
        gen = torch.Generator(device=device).manual_seed(seed)
        cpu_gen = torch.Generator().manual_seed(seed + 1009)
        if codebook is not None:
            keys = v3.sample_kerdock_keys(codebook, M, cpu_gen, device)
        else:
            rank_L = max(2, int(M * 0.25))
            keys = v1.make_correlated_keys(M, N, rank_L, gen, device)
        values = 2.0 * (torch.rand((M, N), generator=gen, device=device) > 0.5).float() - 1.0
        W = (values.T @ keys) / N
        w_std = float(W.std())
        target = torch.arange(M, device=device)

        per_sigma = {}
        for sigma in sigmas:
            noise_gen = torch.Generator(device=device).manual_seed(seed * 17 + int(sigma * 1000))
            W_noisy = W + sigma * w_std * torch.randn(W.shape, generator=noise_gen, device=device)
            retrieved = keys @ W_noisy.T
            sims = retrieved @ values.T
            pred = sims.argmax(dim=1)
            acc = float((pred == target).float().mean())
            per_sigma[sigma] = {"argmax_acc": acc}
        per_seed.append({"seed": seed, "per_sigma": per_sigma})

    agg_sigma = {}
    for sigma in sigmas:
        accs = [s["per_sigma"][sigma]["argmax_acc"] for s in per_seed]
        agg_sigma[sigma] = {"argmax_acc": sum(accs) / len(accs)}
    return {"per_sigma": agg_sigma, "per_seed": per_seed}


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 1024 if smoke else 4096,
              "M_stored": 256 if smoke else 2048,
              "sigmas": [0.0, 1.0] if smoke else [0.0, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0],
              "seeds": [17] if smoke else [17, 23, 31, 41, 53]}
    codebook, _ = v3.make_kerdock_4coset_codebook(config["N"], device)
    arm_k = run_arm("kerdock", codebook, config, device)
    arm_c = run_arm("correlated", None, config, device)
    summary = {"by_arm": {"kerdock": arm_k, "correlated": arm_c}}
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
    out_dir = get_output_dir("wave14zm_noise_robust_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    sigma0 = config["sigmas"][0]
    acc0 = summary["by_arm"]["kerdock"]["per_sigma"][sigma0]["argmax_acc"]
    oracle.assert_baseline_high("kerdock_sigma0", acc0, 0.50)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14zm_noise_robust")
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
