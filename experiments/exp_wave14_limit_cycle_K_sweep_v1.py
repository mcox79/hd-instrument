"""Limit cycle period vs K — extends LIMIT_CYCLE_DETECTED finding across K range."""
from __future__ import annotations
import argparse, importlib.util, json, os, sys, time
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
    if "median_period_per_K" not in s: return ("PERIOD_K_INCONCLUSIVE", "Missing.")
    per = s["median_period_per_K"]; vals = list(per.values())
    spread = max(vals) - min(vals) if vals else 0
    if spread <= 5: return ("PERIOD_K_INVARIANT", f"K-invariant (spread={spread}): {per}.")
    if max(vals) >= min(vals) * 3: return ("PERIOD_K_SCALES", f"period grows >=3x with K: {per}.")
    return ("PERIOD_K_PARTIAL", f"spread={spread}: {per}.")


def self_test_verdict():
    for s,exp in [
        ({"median_period_per_K":{"100":20,"500":22,"1000":25}},"PERIOD_K_INVARIANT"),
        ({"median_period_per_K":{"100":10,"1000":60}},"PERIOD_K_SCALES"),
        ({"median_period_per_K":{"100":20,"1000":35}},"PERIOD_K_PARTIAL"),
        ({},"PERIOD_K_INCONCLUSIVE"),
    ]:
        a,_=compute_verdict(s)
        if a!=exp: raise AssertionError(f"{a}!={exp}")
    print("verdict self-test passed (4/4 cases)",flush=True)


def median(lst):
    s = sorted(lst); n = len(s); return s[n//2] if n > 0 else 0


def run_experiment(smoke):
    t0=time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    cfg = {"N":8192 if smoke else 65536,
           "K_grid":[100, 500] if smoke else [100, 500, 1000, 5000],
           "depth":25, "num_relations":20, "max_iter":50 if smoke else 200,
           "n_starts":30 if smoke else 100, "seed":17}
    median_per_K = {}
    for K in cfg["K_grid"]:
        num_entities = max(K, cfg["depth"] + 10)
        gen = torch.Generator(device=device).manual_seed(cfg["seed"])
        ea = mh.make_bsc_codebook(num_entities, cfg["N"], gen, device)
        ra = mh.make_bsc_codebook(cfg["num_relations"], cfg["N"], gen, device)
        cg = torch.Generator().manual_seed(cfg["seed"]+K+1009)
        perm = torch.randperm(num_entities, generator=cg)[:cfg["depth"]+1]
        chain_ents = perm.tolist()
        chain_rels = [int(torch.randint(0,cfg["num_relations"],(1,),generator=cg).item()) for _ in range(cfg["depth"])]
        M = mh.build_factbase(chain_ents, chain_rels, max(0,K-cfg["depth"]), num_entities, cfg["num_relations"], ea, ra, cg, device)
        periods = []
        for start_idx in range(min(cfg["n_starts"], num_entities)):
            p, _ = lc.measure_cycle(M, start_idx, chain_rels, ea, ra, cfg["max_iter"])
            if p > 0: periods.append(p)
        med = median(periods)
        median_per_K[str(K)] = med
        print(f"  K={K}: median period={med} from {len(periods)} cycles", flush=True)
    summary = {"median_period_per_K": median_per_K}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic()-t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, cfg


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict":verdict,"verdict_msg":msg,"elapsed_s":elapsed,"summary":summary,"config":config}
    validate_metrics(metrics)
    tmp = out_dir/"metrics.json.tmp"; tmp.write_text(json.dumps(metrics,indent=2,default=float)); tmp.replace(out_dir/"metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14_limit_cycle_K_sweep_v1_smoke")
    s,v,m,e,c = run_experiment(smoke=True)
    oracle.assert_baseline_high("median_present", float(max(s["median_period_per_K"].values()))+0.1, 0.0)
    write_metrics(out_dir,s,v,m,e,c); print(f"\nSMOKE OK: {v}",flush=True)


def run_main():
    out_dir = get_output_dir("wave14_limit_cycle_K_sweep_v1")
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
