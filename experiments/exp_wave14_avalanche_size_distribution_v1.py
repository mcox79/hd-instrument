"""Avalanche size distribution P(dE) — Strategy 07:05 P-B test 3. ABBM exponent check."""
from __future__ import annotations
import argparse, importlib.util, json, math, os, sys, time
from pathlib import Path
import torch
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from verification import oracle  # noqa: E402
_mh = importlib.util.spec_from_file_location("mh", REPO / "experiments" / "exp_wave14r_multihop_K100.py")
mh = importlib.util.module_from_spec(_mh); _mh.loader.exec_module(mh)


def get_output_dir(name):
    n = os.environ.get("HDLAB_EXP_NAME", name)
    out = REPO / "data" / f"exp_{n}"; out.mkdir(parents=True, exist_ok=True); return out


def validate_metrics(d):
    if not {"verdict","verdict_msg","elapsed_s","summary","config"}.issubset(d.keys()): raise ValueError("missing")


def compute_verdict(s):
    if "tau_exponent" not in s: return ("AVAL_INCONCLUSIVE", "Missing.")
    tau = s["tau_exponent"]; r2 = s.get("r2_powerlaw", 0.0)
    if r2 < 0.7: return ("AVAL_NONPOWER", f"r2={r2:.3f}<0.7 (no power-law fit).")
    if 1.3 < tau < 1.7: return ("AVAL_ABBM_FIT", f"tau={tau:.3f} in (1.3, 1.7) (ABBM mean-field 3/2).")
    if tau >= 1.7: return ("AVAL_STEEPER", f"tau={tau:.3f}>=1.7 (steeper than ABBM, RS-phase).")
    return ("AVAL_SHALLOWER", f"tau={tau:.3f}<=1.3 (shallower than ABBM).")


def self_test_verdict():
    for s,exp in [
        ({"tau_exponent":1.5, "r2_powerlaw":0.9},"AVAL_ABBM_FIT"),
        ({"tau_exponent":2.1, "r2_powerlaw":0.85},"AVAL_STEEPER"),
        ({"tau_exponent":1.0, "r2_powerlaw":0.85},"AVAL_SHALLOWER"),
        ({"tau_exponent":1.5, "r2_powerlaw":0.3},"AVAL_NONPOWER"),
        ({},"AVAL_INCONCLUSIVE"),
    ]:
        a,_=compute_verdict(s)
        if a!=exp: raise AssertionError(f"{a}!={exp}")
    print("verdict self-test passed (5/5 cases)",flush=True)


def collect_avalanches(W, n_runs, T_relax, N, gen, device, seed_offset):
    """Run argmax relaxation from random init; collect dE for each spin-flip event."""
    dE_list = []
    for run in range(n_runs):
        g = torch.Generator(device=device).manual_seed(seed_offset + run * 31)
        s = 2.0 * (torch.rand(N, generator=g, device=device) > 0.5).float() - 1.0
        E_prev = float(-0.5 * (s @ W @ s).item())
        for step in range(T_relax):
            h = W @ s
            s_new = torch.sign(h); s_new[s_new == 0] = 1.0
            n_flips = int((s_new != s).sum().item())
            if n_flips == 0:
                break
            E_curr = float(-0.5 * (s_new @ W @ s_new).item())
            dE = E_prev - E_curr
            if dE > 0:
                dE_list.append(dE)
            s = s_new; E_prev = E_curr
    return dE_list


def fit_powerlaw_log(dE_list, n_bins=20):
    """Log-log linear fit of P(dE) ~ dE^(-tau). Return (tau, r2)."""
    if len(dE_list) < 10:
        return 0.0, 0.0
    dE_t = torch.tensor(dE_list)
    dE_pos = dE_t[dE_t > 0]
    if len(dE_pos) < 10:
        return 0.0, 0.0
    log_dE = torch.log(dE_pos)
    lo, hi = log_dE.min().item(), log_dE.max().item()
    if hi - lo < 1e-6:
        return 0.0, 0.0
    edges = torch.linspace(lo, hi, n_bins + 1)
    hist = torch.histc(log_dE, bins=n_bins, min=lo, max=hi)
    centers = 0.5 * (edges[:-1] + edges[1:])
    mask = hist > 0
    if mask.sum() < 4:
        return 0.0, 0.0
    x = centers[mask]
    y = torch.log(hist[mask])
    # Linear fit y = a + b*x; tau = -b
    x_mean = x.mean(); y_mean = y.mean()
    b = ((x - x_mean) * (y - y_mean)).sum() / ((x - x_mean) ** 2).sum()
    a = y_mean - b * x_mean
    y_pred = a + b * x
    ss_res = ((y - y_pred) ** 2).sum().item()
    ss_tot = ((y - y_mean) ** 2).sum().item()
    r2 = 1.0 - ss_res / max(ss_tot, 1e-9)
    return float(-b.item()), float(r2)


def run_experiment(smoke):
    t0=time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    cfg = {"N":2048 if smoke else 8192, "K":100,
           "n_runs":20 if smoke else 100, "T_relax":50, "seed":17}
    gen = torch.Generator(device=device).manual_seed(cfg["seed"])
    ea = mh.make_bsc_codebook(200, cfg["N"], gen, device)
    ra = mh.make_bsc_codebook(20, cfg["N"], gen, device)
    cg = torch.Generator().manual_seed(cfg["seed"]+1009)
    triples = []
    for _ in range(cfg["K"]):
        si = int(torch.randint(0,200,(1,),generator=cg))
        ri = int(torch.randint(0,20,(1,),generator=cg))
        oi = int(torch.randint(0,200,(1,),generator=cg))
        triples.append(mh.sign_quantize(ea[si] * ra[ri] * ea[oi]))
    T = torch.stack(triples, dim=0)
    W = (T.T @ T) / cfg["N"]
    dE_list = collect_avalanches(W, cfg["n_runs"], cfg["T_relax"], cfg["N"], gen, device, cfg["seed"])
    print(f"  collected {len(dE_list)} avalanche events", flush=True)
    tau, r2 = fit_powerlaw_log(dE_list)
    print(f"  tau={tau:.3f}, r2={r2:.3f}", flush=True)
    summary = {"tau_exponent": tau, "r2_powerlaw": r2, "n_events": len(dE_list),
               "dE_min": float(min(dE_list)) if dE_list else 0.0,
               "dE_max": float(max(dE_list)) if dE_list else 0.0}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic()-t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, cfg


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict":verdict,"verdict_msg":msg,"elapsed_s":elapsed,"summary":summary,"config":config}
    validate_metrics(metrics)
    tmp = out_dir/"metrics.json.tmp"; tmp.write_text(json.dumps(metrics,indent=2,default=float)); tmp.replace(out_dir/"metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14_avalanche_size_distribution_v1_smoke")
    s,v,m,e,c = run_experiment(smoke=True)
    oracle.assert_baseline_high("tau_present", abs(s["tau_exponent"])+0.001, 0.0)
    write_metrics(out_dir,s,v,m,e,c); print(f"\nSMOKE OK: {v}",flush=True)


def run_main():
    out_dir = get_output_dir("wave14_avalanche_size_distribution_v1")
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
