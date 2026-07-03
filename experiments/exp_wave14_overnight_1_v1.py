"""Overnight experiment variant 1 — heavy multi-condition smoother sweep with high trial count."""
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
_vc = importlib.util.spec_from_file_location("vc", REPO / "experiments" / "exp_wave14_multihop_vamp_chain_N65536_v1.py")
vc = importlib.util.module_from_spec(_vc); _vc.loader.exec_module(vc)
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
    if "results" not in s: return ("ON_INCONCLUSIVE","Missing")
    r = s["results"]
    n_pass = sum(1 for v in r.values() if v >= 0.5)
    return ("ON_ENVELOPE", f"{n_pass}/{len(r)} cells pass >=0.5")

def self_test_verdict():
    for a,b in [({"results":{"a":1.0,"b":0.6}},"ON_ENVELOPE"),({},"ON_INCONCLUSIVE")]:
        v,_ = compute_verdict(a)
        if v!=b: raise AssertionError(f"{v}!={b}")
    print("verdict self-test passed (2/2 cases)", flush=True)

def run_experiment(smoke):
    t0=time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    seed = 1 * 100 + 7
    # Variant 1 varies: smaller N, different K and depth combos
    Ns = [4096, 16384, 65536]
    if smoke: Ns = [4096, 8192]
    Ks = [200, 1000]
    depths = [25, 100]
    methods = ["smoother", "vamp"]
    results = {}
    n_trials = 3 if smoke else 30
    for N in Ns:
        for K in Ks:
            for d in depths:
                if d >= K: continue
                for m in methods:
                    nent = max(K, d+10)
                    gen = torch.Generator(device=device).manual_seed(seed + N + K + d)
                    ea = mh.make_bsc_codebook(nent, N, gen, device)
                    ra = mh.make_bsc_codebook(20, N, gen, device)
                    cg = torch.Generator().manual_seed(seed + N + K + d + 1009)
                    correct = 0
                    for tr in range(n_trials):
                        perm = torch.randperm(nent, generator=cg)[:d+1]
                        ch = perm.tolist()
                        rels = [int(torch.randint(0,20,(1,),generator=cg).item()) for _ in range(d)]
                        M = mh.build_factbase(ch, rels, max(0,K-d), nent, 20, ea, ra, cg, device)
                        fn = so.chain_smoother_only if m == "smoother" else vc.vamp_chain_forward_backward
                        if fn(M, ch[0], rels, ch[-1], ea, ra): correct += 1
                    key = f"{m}_N{N}_K{K}_d{d}"
                    results[key] = correct / n_trials
                    print(f"  {key}: {results[key]:.3f}", flush=True)
    summary = {"results": results, "seed": seed, "variant": 1}
    verdict, msg = compute_verdict(summary)
    return summary, verdict, msg, time.monotonic()-t0, {"smoke":smoke,"seed":seed,"variant":1}

def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict":verdict,"verdict_msg":msg,"elapsed_s":elapsed,"summary":summary,"config":config}
    validate_metrics(metrics)
    tmp = out_dir/"metrics.json.tmp"; tmp.write_text(json.dumps(metrics,indent=2,default=float))
    tmp.replace(out_dir/"metrics.json")

def run_smoke():
    out_dir = get_output_dir("wave14_overnight_1_v1_smoke")
    s,v,m,e,c = run_experiment(smoke=True)
    oracle.assert_baseline_high("any_pass", max(s["results"].values())+0.001, 0.0)
    write_metrics(out_dir,s,v,m,e,c); print(f"\nSMOKE OK: {v}",flush=True)

def run_main():
    out_dir = get_output_dir("wave14_overnight_1_v1")
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
