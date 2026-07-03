"""Cluster basin size — Hamming distance from absorbing codeword where chain still attracts."""
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
    if "basin_radius_frac" not in s: return ("BASIN_INCONCLUSIVE", "Missing.")
    r = s["basin_radius_frac"]
    if r >= 0.3: return ("BASIN_LARGE", f"radius={r:.2f}*N >= 0.3*N (large basin).")
    if r >= 0.1: return ("BASIN_MID", f"radius={r:.2f}*N in [0.1, 0.3] (medium basin).")
    return ("BASIN_SMALL", f"radius={r:.2f}*N < 0.1 (small basin).")


def self_test_verdict():
    for s,exp in [({"basin_radius_frac":0.4},"BASIN_LARGE"),({"basin_radius_frac":0.2},"BASIN_MID"),({"basin_radius_frac":0.05},"BASIN_SMALL"),({},"BASIN_INCONCLUSIVE")]:
        a,_=compute_verdict(s)
        if a!=exp: raise AssertionError(f"{a}!={exp}")
    print("verdict self-test passed (4/4 cases)",flush=True)


def run_experiment(smoke):
    t0=time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    cfg = {"N":8192 if smoke else 65536, "K":100, "depth":25, "num_entities":200, "num_relations":20,
           "d_flip_grid":[0.05,0.10] if smoke else [0.02,0.05,0.10,0.20,0.30,0.50],
           "n_trials":20 if smoke else 50, "seed":17}
    gen = torch.Generator(device=device).manual_seed(cfg["seed"])
    ea = mh.make_bsc_codebook(cfg["num_entities"], cfg["N"], gen, device)
    ra = mh.make_bsc_codebook(cfg["num_relations"], cfg["N"], gen, device)
    cg = torch.Generator().manual_seed(cfg["seed"]+1009)
    perm = torch.randperm(cfg["num_entities"], generator=cg)[:cfg["depth"]+1]
    chain = perm.tolist()
    rels = [int(torch.randint(0,cfg["num_relations"],(1,),generator=cg).item()) for _ in range(cfg["depth"])]
    M = mh.build_factbase(chain, rels, max(0,cfg["K"]-cfg["depth"]), cfg["num_entities"], cfg["num_relations"], ea, ra, cg, device)
    # Find absorbing codeword via 50 clean runs
    finals = []
    for _ in range(20):
        start = int(torch.randint(0,cfg["num_entities"],(1,),generator=cg).item())
        current = start
        for r_idx in rels:
            current = int((ea @ (M * (ea[current] * ra[r_idx]))).argmax().item())
        finals.append(current)
    from collections import Counter
    absorbing_idx = Counter(finals).most_common(1)[0][0]
    target_atom = ea[absorbing_idx]
    print(f"  absorbing codeword idx={absorbing_idx}", flush=True)
    # Test basin: perturb target by frac, see if chain still attracts to same codeword
    basin = 0.0
    recovery_per_d = {}
    for d_frac in cfg["d_flip_grid"]:
        d_flip = max(1, int(d_frac * cfg["N"]))
        correct = 0
        for _ in range(cfg["n_trials"]):
            flip_idx = torch.randperm(cfg["N"], generator=cg)[:d_flip].to(device)
            start_atom = target_atom.clone()
            start_atom[flip_idx] = -start_atom[flip_idx]
            start = int((ea @ start_atom).argmax().item())
            current = start
            for r_idx in rels:
                current = int((ea @ (M * (ea[current] * ra[r_idx]))).argmax().item())
            if current == absorbing_idx: correct += 1
        acc = correct / cfg["n_trials"]
        recovery_per_d[d_frac] = acc
        print(f"  d_flip={d_frac:.2f}*N: recovery={acc:.3f}", flush=True)
        if acc >= 0.5: basin = d_frac
    summary = {"basin_radius_frac": basin, "absorbing_idx": absorbing_idx, "recovery_per_d_frac": {str(k):v for k,v in recovery_per_d.items()}}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic()-t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, cfg


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict":verdict,"verdict_msg":msg,"elapsed_s":elapsed,"summary":summary,"config":config}
    validate_metrics(metrics)
    tmp = out_dir/"metrics.json.tmp"; tmp.write_text(json.dumps(metrics,indent=2,default=float)); tmp.replace(out_dir/"metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14_cluster_basin_size_v1_smoke")
    s,v,m,e,c = run_experiment(smoke=True)
    oracle.assert_baseline_high("any_recovery", float(max(s["recovery_per_d_frac"].values()))+0.001, 0.0)
    write_metrics(out_dir,s,v,m,e,c); print(f"\nSMOKE OK: {v}",flush=True)


def run_main():
    out_dir = get_output_dir("wave14_cluster_basin_size_v1")
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
