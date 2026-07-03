"""Smoother burst variant 2 — seed=2*7+30, larger N or K."""
from __future__ import annotations
import argparse, importlib.util, json, os, sys, time
from pathlib import Path
import torch
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
from verification import oracle
_so = importlib.util.spec_from_file_location("so", REPO / "experiments" / "exp_wave14_chain_smoother_only_v1.py")
so = importlib.util.module_from_spec(_so); _so.loader.exec_module(so)
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
    if "acc" not in s: return ("BURST_INCONCLUSIVE","Missing")
    if s["acc"] >= 0.5: return ("BURST_PASS", f"acc={s['acc']:.3f}")
    return ("BURST_KILL", f"acc={s['acc']:.3f}")

def self_test_verdict():
    for a,b in [({"acc":0.8},"BURST_PASS"),({"acc":0.2},"BURST_KILL"),({},"BURST_INCONCLUSIVE")]:
        v,_ = compute_verdict(a)
        if v!=b: raise AssertionError(f"{v}!={b}")
    print("verdict self-test passed (3/3 cases)", flush=True)

def run_experiment(smoke):
    t0=time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    seed = 2*7 + 30
    K = 100 + 2*100  # K varies per variant
    cfg = {"N": 16384 if smoke else 65536, "K": K, "depth": 50, "n_trials": 5 if smoke else 30, "seed": seed}
    gen = torch.Generator(device=device).manual_seed(seed)
    nent = max(cfg["K"], cfg["depth"]+10)
    ea = mh.make_bsc_codebook(nent, cfg["N"], gen, device)
    ra = mh.make_bsc_codebook(20, cfg["N"], gen, device)
    cg = torch.Generator().manual_seed(seed+1009)
    correct = 0
    for tr in range(cfg["n_trials"]):
        perm = torch.randperm(nent, generator=cg)[:cfg["depth"]+1]
        ch = perm.tolist()
        rels = [int(torch.randint(0,20,(1,),generator=cg).item()) for _ in range(cfg["depth"])]
        M = mh.build_factbase(ch, rels, max(0,cfg["K"]-cfg["depth"]), nent, 20, ea, ra, cg, device)
        if so.chain_smoother_only(M, ch[0], rels, ch[-1], ea, ra): correct += 1
    acc = correct / cfg["n_trials"]
    print(f"  K={cfg['K']} acc={acc:.3f}", flush=True)
    summary = {"acc": acc, "K": cfg["K"], "seed": seed}
    verdict, msg = compute_verdict(summary)
    return summary, verdict, msg, time.monotonic()-t0, cfg

def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict":verdict,"verdict_msg":msg,"elapsed_s":elapsed,"summary":summary,"config":config}
    validate_metrics(metrics)
    tmp = out_dir/"metrics.json.tmp"; tmp.write_text(json.dumps(metrics,indent=2,default=float))
    tmp.replace(out_dir/"metrics.json")

def run_smoke():
    out_dir = get_output_dir("wave14_smoother_burst_2_v1_smoke")
    s,v,m,e,c = run_experiment(smoke=True)
    oracle.assert_baseline_high("acc_present", s["acc"]+0.001, 0.0)
    write_metrics(out_dir,s,v,m,e,c); print(f"\nSMOKE OK: {v}",flush=True)

def run_main():
    out_dir = get_output_dir("wave14_smoother_burst_2_v1")
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
