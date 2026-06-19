"""Limit cycle period vs N — extend LIMIT_CYCLE_DETECTED finding across N range.

Per cycle 142 LIMIT_CYCLE_DETECTED (100% codewords cycle, 66% period in [2,100]):
test if cycle period is N-invariant (substrate-novel structural property) or N-scaling.
"""
from __future__ import annotations
import argparse, importlib.util, json, os, sys, time
from collections import Counter
from pathlib import Path
import torch
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from verification import oracle  # noqa: E402
_lc = importlib.util.spec_from_file_location("lc", REPO / "experiments" / "exp_wave14_substrate_limit_cycle_period_v1.py")
lc = importlib.util.module_from_spec(_lc); _lc.loader.exec_module(lc)
_mh = importlib.util.spec_from_file_location("mh", REPO / "experiments" / "exp_wave14r_multihop_K100.py")
mh = importlib.util.module_from_spec(_mh); _mh.loader.exec_module(mh)


def get_output_dir(name):
    n = os.environ.get("HDLAB_EXP_NAME", name)
    out = REPO / "data" / f"exp_{n}"; out.mkdir(parents=True, exist_ok=True); return out


def validate_metrics(d):
    if not {"verdict","verdict_msg","elapsed_s","summary","config"}.issubset(d.keys()): raise ValueError("missing")


def compute_verdict(s):
    if "median_period_per_N" not in s: return ("PERIOD_N_INCONCLUSIVE", "Missing.")
    per = s["median_period_per_N"]
    vals = list(per.values())
    spread = max(vals) - min(vals) if vals else 0
    if spread <= 5:
        return ("PERIOD_N_INVARIANT", f"median period N-invariant (spread={spread}): {per}.")
    if max(vals) >= min(vals) * 3:
        return ("PERIOD_N_SCALES", f"median period grows >=3x with N: {per}.")
    return ("PERIOD_N_PARTIAL", f"median period spread={spread}: {per}.")


def self_test_verdict():
    for s,exp in [
        ({"median_period_per_N":{"4096":20,"65536":22}},"PERIOD_N_INVARIANT"),
        ({"median_period_per_N":{"4096":10,"65536":50}},"PERIOD_N_SCALES"),
        ({"median_period_per_N":{"4096":20,"65536":35}},"PERIOD_N_PARTIAL"),
        ({},"PERIOD_N_INCONCLUSIVE"),
    ]:
        a,_=compute_verdict(s)
        if a!=exp: raise AssertionError(f"{a}!={exp}")
    print("verdict self-test passed (4/4 cases)",flush=True)


def median(lst):
    s = sorted(lst); n = len(s)
    return s[n//2] if n > 0 else 0


def run_experiment(smoke):
    t0=time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    cfg = {"N_grid":[4096, 8192] if smoke else [4096, 16384, 65536],
           "K":100, "depth":25, "num_entities":200, "num_relations":20,
           "max_iter":50 if smoke else 200, "n_starts":30 if smoke else 100, "seed":17}
    median_per_N = {}; all_periods_per_N = {}
    for N in cfg["N_grid"]:
        gen = torch.Generator(device=device).manual_seed(cfg["seed"])
        ea = mh.make_bsc_codebook(cfg["num_entities"], N, gen, device)
        ra = mh.make_bsc_codebook(cfg["num_relations"], N, gen, device)
        cg = torch.Generator().manual_seed(cfg["seed"]+1009+N)
        perm = torch.randperm(cfg["num_entities"], generator=cg)[:cfg["depth"]+1]
        chain_ents = perm.tolist()
        chain_rels = [int(torch.randint(0,cfg["num_relations"],(1,),generator=cg).item()) for _ in range(cfg["depth"])]
        M = mh.build_factbase(chain_ents, chain_rels, max(0,cfg["K"]-cfg["depth"]), cfg["num_entities"], cfg["num_relations"], ea, ra, cg, device)
        periods = []
        for start_idx in range(min(cfg["n_starts"], cfg["num_entities"])):
            p, _ = lc.measure_cycle(M, start_idx, chain_rels, ea, ra, cfg["max_iter"])
            if p > 0: periods.append(p)
        med = median(periods)
        median_per_N[str(N)] = med
        all_periods_per_N[str(N)] = periods
        print(f"  N={N}: {len(periods)}/{cfg['n_starts']} cycles, median period={med}", flush=True)
    summary = {"median_period_per_N": median_per_N, "all_periods_per_N": all_periods_per_N}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic()-t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, cfg


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict":verdict,"verdict_msg":msg,"elapsed_s":elapsed,"summary":summary,"config":config}
    validate_metrics(metrics)
    tmp = out_dir/"metrics.json.tmp"; tmp.write_text(json.dumps(metrics,indent=2,default=float)); tmp.replace(out_dir/"metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14_limit_cycle_N_sweep_v1_smoke")
    s,v,m,e,c = run_experiment(smoke=True)
    oracle.assert_baseline_high("median_present", float(max(s["median_period_per_N"].values()))+0.1, 0.0)
    write_metrics(out_dir,s,v,m,e,c); print(f"\nSMOKE OK: {v}",flush=True)


def run_main():
    out_dir = get_output_dir("wave14_limit_cycle_N_sweep_v1")
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
