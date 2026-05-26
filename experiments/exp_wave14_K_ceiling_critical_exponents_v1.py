"""K-ceiling critical exponents — Strategy 07:08 Priority 1 (META Gap 1)."""
from __future__ import annotations
import argparse, importlib.util, json, math, os, sys, time
from pathlib import Path
import torch
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from verification import oracle  # noqa: E402
_bs = importlib.util.spec_from_file_location("bs", REPO / "experiments" / "exp_wave14_betS_pattern_completion_v1.py")
bs = importlib.util.module_from_spec(_bs); _bs.loader.exec_module(bs)


def get_output_dir(name):
    n = os.environ.get("HDLAB_EXP_NAME", name)
    out = REPO / "data" / f"exp_{n}"; out.mkdir(parents=True, exist_ok=True); return out


def validate_metrics(d):
    if not {"verdict","verdict_msg","elapsed_s","summary","config"}.issubset(d.keys()): raise ValueError("missing")


def compute_verdict(s):
    if "powerlaw_r2" not in s: return ("CRIT_INCONCLUSIVE", "Missing.")
    r2_p = s["powerlaw_r2"]; r2_e = s["exponential_r2"]
    if r2_p > 0.85 and r2_p > r2_e + 0.05:
        return ("CRIT_EXPONENT_POWERLAW", f"power-law r2={r2_p:.3f}; beta={s['fitted_beta']:.3f}; K_c={s['fitted_K_c']:.1f}.")
    if r2_e > 0.85:
        return ("CRIT_EXPONENT_EXPONENTIAL", f"exponential r2={r2_e:.3f}.")
    return ("CRIT_EXPONENT_INCONCLUSIVE", f"power-law r2={r2_p:.3f}, exp r2={r2_e:.3f}.")


def self_test_verdict():
    for s,exp in [
        ({"powerlaw_r2":0.95,"exponential_r2":0.5,"fitted_beta":0.5,"fitted_K_c":205},"CRIT_EXPONENT_POWERLAW"),
        ({"powerlaw_r2":0.5,"exponential_r2":0.92,"fitted_beta":0,"fitted_K_c":0},"CRIT_EXPONENT_EXPONENTIAL"),
        ({"powerlaw_r2":0.5,"exponential_r2":0.6,"fitted_beta":0,"fitted_K_c":0},"CRIT_EXPONENT_INCONCLUSIVE"),
        ({},"CRIT_INCONCLUSIVE"),
    ]:
        a,_=compute_verdict(s)
        if a!=exp: raise AssertionError(f"{a}!={exp}")
    print("verdict self-test passed (4/4 cases)",flush=True)


def fit_powerlaw_decay(Ks, accs, K_c_guess=205):
    """Fit acc(K) = A * (K_c - K)^beta for K < K_c. Linear in log space."""
    pts = [(K, a) for K, a in zip(Ks, accs) if K < K_c_guess and a > 0.01]
    if len(pts) < 3: return 0, 0, 0
    xs = [math.log(K_c_guess - K) for K, _ in pts]
    ys = [math.log(a) for _, a in pts]
    n = len(xs)
    sx = sum(xs); sy = sum(ys); sxx = sum(x*x for x in xs); sxy = sum(xs[i]*ys[i] for i in range(n))
    slope = (n*sxy - sx*sy) / max(n*sxx - sx*sx, 1e-9)
    intercept = (sy - slope*sx)/n
    mean_y = sy / n
    ss_tot = sum((y-mean_y)**2 for y in ys)
    ss_res = sum((ys[i] - (slope*xs[i] + intercept))**2 for i in range(n))
    r2 = 1.0 - ss_res / max(ss_tot, 1e-9)
    return slope, r2, math.exp(intercept)


def fit_exponential(Ks, accs):
    pts = [(K, a) for K, a in zip(Ks, accs) if a > 0.01]
    if len(pts) < 3: return 0
    xs = [K for K, _ in pts]
    ys = [math.log(a) for _, a in pts]
    n = len(xs); sx = sum(xs); sy = sum(ys); sxx = sum(x*x for x in xs); sxy = sum(xs[i]*ys[i] for i in range(n))
    slope = (n*sxy - sx*sy) / max(n*sxx - sx*sx, 1e-9)
    intercept = (sy - slope*sx)/n
    mean_y = sy / n
    ss_tot = sum((y-mean_y)**2 for y in ys)
    ss_res = sum((ys[i] - (slope*xs[i] + intercept))**2 for i in range(n))
    r2 = 1.0 - ss_res / max(ss_tot, 1e-9)
    return r2


def run_experiment(smoke):
    t0=time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    cfg = {"N":1024 if smoke else 4096,
           "K_grid":[50, 100, 175] if smoke else [25, 50, 100, 150, 175, 190, 200, 210, 220, 250],
           "num_entities":200, "num_relations":20, "n_trials":20 if smoke else 50,
           "seeds":[17, 23] if smoke else [17, 23, 31, 41, 53]}
    K_means = {}
    for K in cfg["K_grid"]:
        accs_seeds = []
        for seed in cfg["seeds"]:
            r = bs.run_one_K(K, cfg["num_entities"], cfg["num_relations"],
                                cfg["N"], cfg["n_trials"], seed, device)
            accs_seeds.append(r["subject"])
        mean_acc = sum(accs_seeds) / len(accs_seeds)
        K_means[K] = mean_acc
        print(f"  K={K}: mean acc={mean_acc:.3f} per_seed={[round(a,3) for a in accs_seeds]}", flush=True)
    # Fit
    Ks = sorted(K_means.keys()); accs = [K_means[K] for K in Ks]
    beta, r2_p, A = fit_powerlaw_decay(Ks, accs)
    r2_e = fit_exponential(Ks, accs)
    print(f"  power-law beta={beta:.3f}, r2={r2_p:.3f}; exp r2={r2_e:.3f}", flush=True)
    summary = {"K_to_acc": K_means, "powerlaw_r2": r2_p, "fitted_beta": beta,
                "fitted_K_c": 205, "exponential_r2": r2_e}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic()-t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, cfg


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict":verdict,"verdict_msg":msg,"elapsed_s":elapsed,"summary":summary,"config":config}
    validate_metrics(metrics)
    tmp = out_dir/"metrics.json.tmp"; tmp.write_text(json.dumps(metrics,indent=2,default=float)); tmp.replace(out_dir/"metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14_K_ceiling_critical_exponents_v1_smoke")
    s,v,m,e,c = run_experiment(smoke=True)
    oracle.assert_baseline_high("acc_present", float(max(s["K_to_acc"].values()))+0.001, 0.0)
    write_metrics(out_dir,s,v,m,e,c); print(f"\nSMOKE OK: {v}",flush=True)


def run_main():
    out_dir = get_output_dir("wave14_K_ceiling_critical_exponents_v1")
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
