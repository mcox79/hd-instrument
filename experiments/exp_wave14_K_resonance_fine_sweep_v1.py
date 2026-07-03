"""K-resonance fine sweep — Strategy 06:49 P1. Find K=1000 anomaly boundary."""
from __future__ import annotations
import argparse, importlib.util, json, os, sys, time
from pathlib import Path
import torch
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
from verification import oracle
_lc = importlib.util.spec_from_file_location("lc", REPO / "experiments" / "exp_wave14_substrate_limit_cycle_period_v1.py")
lc = importlib.util.module_from_spec(_lc); _lc.loader.exec_module(lc)
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
    if "median_period_per_K" not in s: return ("KRES_INCONCLUSIVE", "Missing.")
    per = s["median_period_per_K"]
    fixed = [k for k, p in per.items() if p == 1]
    if len(fixed) == 1: return ("K_RESONANCE_NARROW", f"Only {fixed} shows period 1: {per}.")
    if len(fixed) >= 3: return ("K_RESONANCE_BROAD", f"Many K show period 1: {fixed} from {per}.")
    if len(fixed) >= 2: return ("K_RESONANCE_BAND", f"K range {fixed} shows period 1: {per}.")
    return ("K_RESONANCE_NONE", f"No period-1 region: {per}.")

def self_test_verdict():
    for s,exp in [
        ({"median_period_per_K":{"800":12,"1000":1,"1500":20}},"K_RESONANCE_NARROW"),
        ({"median_period_per_K":{"950":1,"1000":1,"1050":1,"1100":12}},"K_RESONANCE_BROAD"),
        ({"median_period_per_K":{"950":1,"1000":1,"1100":12}},"K_RESONANCE_BAND"),
        ({"median_period_per_K":{"800":12,"1000":15,"1200":20}},"K_RESONANCE_NONE"),
        ({},"KRES_INCONCLUSIVE"),
    ]:
        a,_=compute_verdict(s)
        if a!=exp: raise AssertionError(f"{a}!={exp}")
    print("verdict self-test passed (5/5 cases)",flush=True)

def median(lst):
    s=sorted(lst); n=len(s); return s[n//2] if n>0 else 0

def run_experiment(smoke):
    t0=time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    cfg = {"N":8192 if smoke else 65536,
           "K_grid":[900, 1000, 1100] if smoke else [800, 900, 950, 1000, 1050, 1100, 1200, 1500, 2000],
           "depth":25, "num_relations":20, "max_iter":50 if smoke else 200,
           "n_starts":30 if smoke else 100, "seed":17}
    med_per = {}
    for K in cfg["K_grid"]:
        nent = max(K, cfg["depth"]+10)
        gen = torch.Generator(device=device).manual_seed(cfg["seed"])
        ea = mh.make_bsc_codebook(nent, cfg["N"], gen, device)
        ra = mh.make_bsc_codebook(cfg["num_relations"], cfg["N"], gen, device)
        cg = torch.Generator().manual_seed(cfg["seed"]+K+1009)
        perm = torch.randperm(nent, generator=cg)[:cfg["depth"]+1]
        rels = [int(torch.randint(0,cfg["num_relations"],(1,),generator=cg).item()) for _ in range(cfg["depth"])]
        M = mh.build_factbase(perm.tolist(), rels, max(0,K-cfg["depth"]), nent, cfg["num_relations"], ea, ra, cg, device)
        periods=[]
        for s_idx in range(min(cfg["n_starts"], nent)):
            p,_ = lc.measure_cycle(M, s_idx, rels, ea, ra, cfg["max_iter"])
            if p>0: periods.append(p)
        med = median(periods)
        med_per[str(K)] = med
        print(f"  K={K}: median period={med}", flush=True)
    summary = {"median_period_per_K": med_per}
    verdict, msg = compute_verdict(summary)
    return summary, verdict, msg, time.monotonic()-t0, cfg

def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict":verdict,"verdict_msg":msg,"elapsed_s":elapsed,"summary":summary,"config":config}
    validate_metrics(metrics)
    tmp = out_dir/"metrics.json.tmp"; tmp.write_text(json.dumps(metrics,indent=2,default=float))
    tmp.replace(out_dir/"metrics.json")

def run_smoke():
    out_dir = get_output_dir("wave14_K_resonance_fine_sweep_v1_smoke")
    s,v,m,e,c = run_experiment(smoke=True)
    oracle.assert_baseline_high("median_present", float(max(s["median_period_per_K"].values()))+0.1, 0.0)
    write_metrics(out_dir,s,v,m,e,c); print(f"\nSMOKE OK: {v}",flush=True)

def run_main():
    out_dir = get_output_dir("wave14_K_resonance_fine_sweep_v1")
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
