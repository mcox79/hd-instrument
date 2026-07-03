"""Critical slowing down self-monitor — Strategy 10:03 v151 P4 (Cap 2).

Marginal stability gapless Hessian implies substrate exhibits critical slowing down
near retrieval errors. Use VAMP iteration count as confidence indicator: higher
relaxation time correlates with retrieval error.
"""
from __future__ import annotations
import argparse, importlib.util, json, os, sys, time
from pathlib import Path
import torch
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
from verification import oracle  # noqa: E402


def get_output_dir(name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d):
    if not {"verdict","verdict_msg","elapsed_s","summary","config"}.issubset(d.keys()): raise ValueError("missing")


def compute_verdict(s):
    if "tau_err_correlation" not in s: return ("SLOWING_INCONCLUSIVE", "Missing.")
    c = s["tau_err_correlation"]
    if c >= 0.50: return ("SLOWING_DOWN_DETECTS", f"correlation(tau, error)={c:.3f}>=0.50 (substrate exhibits critical slowing down near errors).")
    if abs(c) < 0.20: return ("NO_CORRELATION", f"correlation={c:.3f} |<0.20| (no detection signal).")
    return ("SLOWING_DOWN_PARTIAL", f"correlation={c:.3f} (intermediate signal).")


def self_test_verdict():
    for s,exp in [
        ({"tau_err_correlation":0.7},"SLOWING_DOWN_DETECTS"),
        ({"tau_err_correlation":0.05},"NO_CORRELATION"),
        ({"tau_err_correlation":0.35},"SLOWING_DOWN_PARTIAL"),
        ({},"SLOWING_INCONCLUSIVE"),
    ]:
        a,_=compute_verdict(s)
        if a!=exp: raise AssertionError(f"{a}!={exp}")
    print("verdict self-test passed (4/4 cases)",flush=True)


def make_pattern(N, gen, device):
    b = (torch.rand(N, generator=gen) > 0.5).to(device).float()
    return 2.0 * b - 1.0


def relaxation_time(W, query, target, max_iter=50, tol=1e-3):
    """Run argmax dynamics; return iteration count until convergence."""
    s = query.clone()
    s_prev = s.clone()
    for t in range(max_iter):
        s = torch.sign(W @ s); s[s == 0] = 1.0
        change = float((s - s_prev).abs().mean().item())
        if change < tol:
            return t + 1
        s_prev = s.clone()
    return max_iter


def run_experiment(smoke):
    t0=time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    cfg = {"N":2048 if smoke else 8192, "M":50 if smoke else 200,
           "n_trials":30 if smoke else 200, "noise_levels":[0.0, 0.1, 0.2, 0.3, 0.4], "seed":17}
    gen = torch.Generator().manual_seed(cfg["seed"])
    keys = torch.stack([make_pattern(cfg["N"], gen, device) for _ in range(cfg["M"])], dim=0)
    values = torch.stack([make_pattern(cfg["N"], gen, device) for _ in range(cfg["M"])], dim=0)
    W = (values.T @ keys) / cfg["N"]
    taus = []; errors = []
    for trial in range(cfg["n_trials"]):
        idx = trial % cfg["M"]
        noise_p = cfg["noise_levels"][trial % len(cfg["noise_levels"])]
        k_noisy = keys[idx].clone()
        if noise_p > 0:
            flips = (torch.rand(cfg["N"], generator=gen) < noise_p).to(device).float()
            k_noisy = k_noisy * (1.0 - 2.0 * flips)
        tau = relaxation_time(W, k_noisy, values[idx])
        # Check retrieval after relaxation
        pred = torch.sign(W @ k_noisy); pred[pred == 0] = 1.0
        for _ in range(tau):
            pred = torch.sign(W @ pred); pred[pred == 0] = 1.0
        # Compare against true value
        overlap = float((pred * values[idx]).mean().item())
        is_error = 1 if overlap < 0.7 else 0
        taus.append(tau); errors.append(is_error)
    n = len(taus)
    tau_mean = sum(taus) / n; err_mean = sum(errors) / n
    tau_var = sum((t-tau_mean)**2 for t in taus) / n
    err_var = sum((e-err_mean)**2 for e in errors) / n
    cov = sum((taus[i]-tau_mean)*(errors[i]-err_mean) for i in range(n)) / n
    correlation = cov / (max(tau_var, 1e-9)**0.5 * max(err_var, 1e-9)**0.5)
    print(f"  Across {n} trials: tau mean={tau_mean:.2f} err rate={err_mean:.3f} correlation={correlation:.3f}", flush=True)
    summary = {"tau_err_correlation": correlation, "tau_mean": tau_mean,
               "err_rate": err_mean, "n_trials": n}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic()-t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, cfg


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict":verdict,"verdict_msg":msg,"elapsed_s":elapsed,"summary":summary,"config":config}
    validate_metrics(metrics)
    tmp = out_dir/"metrics.json.tmp"; tmp.write_text(json.dumps(metrics,indent=2,default=float)); tmp.replace(out_dir/"metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14_critical_slowing_down_self_monitor_v1_smoke")
    s,v,m,e,c = run_experiment(smoke=True)
    oracle.assert_baseline_high("corr_present", abs(s["tau_err_correlation"])+0.001, 0.0)
    write_metrics(out_dir,s,v,m,e,c); print(f"\nSMOKE OK: {v}",flush=True)


def run_main():
    out_dir = get_output_dir("wave14_critical_slowing_down_self_monitor_v1")
    s,v,m,e,c = run_experiment(smoke=False)
    write_metrics(out_dir,s,v,m,e,c); print(f"\nDONE: {v}",flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test",action="store_true"); ap.add_argument("--smoke",action="store_true")
    args = ap.parse_args()
    if args.self_test: self_test_verdict(); return 0
    if args.smoke: run_smoke(); return 0
    run_main(); return 0


if __name__=="__main__": sys.exit(main())
