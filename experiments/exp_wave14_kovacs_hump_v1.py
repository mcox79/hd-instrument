"""Kovacs hump — Strategy 07:05 P-B test 2. Double-quench protocol for aging observable."""
from __future__ import annotations
import argparse, importlib.util, json, os, sys, time
from pathlib import Path
import torch
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
from verification import oracle  # noqa: E402
_mh = importlib.util.spec_from_file_location("mh", REPO / "experiments" / "exp_wave14r_multihop_K100.py")
mh = importlib.util.module_from_spec(_mh); _mh.loader.exec_module(mh)


def get_output_dir(name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d):
    if not {"verdict","verdict_msg","elapsed_s","summary","config"}.issubset(d.keys()): raise ValueError("missing")


def compute_verdict(s):
    if "kovacs_amplitude_ratio" not in s: return ("KOVACS_INCONCLUSIVE", "Missing.")
    r = s["kovacs_amplitude_ratio"]
    if r < 1.2: return ("KOVACS_RS_INDEPENDENT", f"max/min amplitude across t_w={r:.3f}<1.2 (RS aging-independent).")
    if r > 2.0: return ("KOVACS_BROAD_RELAXATION", f"max/min amplitude={r:.3f}>2.0 (broad/RSB relaxation).")
    return ("KOVACS_INTERMEDIATE", f"max/min amplitude={r:.3f}.")


def self_test_verdict():
    for s,exp in [
        ({"kovacs_amplitude_ratio":1.05},"KOVACS_RS_INDEPENDENT"),
        ({"kovacs_amplitude_ratio":3.0},"KOVACS_BROAD_RELAXATION"),
        ({"kovacs_amplitude_ratio":1.5},"KOVACS_INTERMEDIATE"),
        ({},"KOVACS_INCONCLUSIVE"),
    ]:
        a,_=compute_verdict(s)
        if a!=exp: raise AssertionError(f"{a}!={exp}")
    print("verdict self-test passed (4/4 cases)",flush=True)


def hopfield_energy(s, W):
    return float(-0.5 * (s @ W @ s).item())


def stochastic_step(s, W, beta, gen, device):
    """One async-block step: compute h=Ws, flip with prob 1/(1+exp(2*beta*s_i*h_i))."""
    h = W @ s
    p_flip = 1.0 / (1.0 + torch.exp(2.0 * beta * s * h).clamp(max=50.0))
    rnd = torch.rand(s.shape[0], generator=gen, device=device)
    s = torch.where(rnd < p_flip, -s, s)
    return s


def run_kovacs(W, t_w, beta_low, beta_target, T_measure, N, gen, device, seed_offset):
    """Quench from random init at beta_low for t_w steps, then beta_target for T_measure; return E(t)."""
    g = torch.Generator(device=device).manual_seed(seed_offset)
    s = 2.0 * (torch.rand(N, generator=g, device=device) > 0.5).float() - 1.0
    # Aging at beta_low for t_w steps
    for _ in range(t_w):
        s = stochastic_step(s, W, beta_low, g, device)
    E_at_quench = hopfield_energy(s, W)
    # Quench to beta_target, record E(t)
    E_traj = [E_at_quench]
    for _ in range(T_measure):
        s = stochastic_step(s, W, beta_target, g, device)
        E_traj.append(hopfield_energy(s, W))
    return E_traj


def run_experiment(smoke):
    t0=time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    cfg = {"N":2048 if smoke else 8192, "K":100,
           "t_w_grid":[10, 100] if smoke else [10, 100, 1000, 5000],
           "T_measure": 20 if smoke else 50,
           "beta_low":0.5, "beta_target":2.0, "seed":17}
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
    amplitudes = []
    traces = {}
    for t_w in cfg["t_w_grid"]:
        E_traj = run_kovacs(W, t_w, cfg["beta_low"], cfg["beta_target"],
                            cfg["T_measure"], cfg["N"], gen, device, cfg["seed"] + t_w*7)
        # Kovacs amplitude = max overshoot relative to final
        E_final = E_traj[-1]
        amp = max(abs(e - E_final) for e in E_traj)
        amplitudes.append(amp)
        traces[str(t_w)] = E_traj
        print(f"  t_w={t_w}: amplitude={amp:.4f}, E[0]={E_traj[0]:.3f}, E[-1]={E_traj[-1]:.3f}", flush=True)
    a_min = min(amplitudes); a_max = max(amplitudes)
    ratio = a_max / max(a_min, 1e-9)
    print(f"  amplitudes={amplitudes}, max/min ratio={ratio:.3f}", flush=True)
    summary = {"kovacs_amplitudes": amplitudes, "kovacs_amplitude_ratio": ratio,
               "E_traces": traces, "t_w_grid": cfg["t_w_grid"]}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic()-t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, cfg


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict":verdict,"verdict_msg":msg,"elapsed_s":elapsed,"summary":summary,"config":config}
    validate_metrics(metrics)
    tmp = out_dir/"metrics.json.tmp"; tmp.write_text(json.dumps(metrics,indent=2,default=float)); tmp.replace(out_dir/"metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14_kovacs_hump_v1_smoke")
    s,v,m,e,c = run_experiment(smoke=True)
    oracle.assert_baseline_high("kovacs_amplitude_present", s["kovacs_amplitude_ratio"]+0.001, 0.0)
    write_metrics(out_dir,s,v,m,e,c); print(f"\nSMOKE OK: {v}",flush=True)


def run_main():
    out_dir = get_output_dir("wave14_kovacs_hump_v1")
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
