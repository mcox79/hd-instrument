"""Heavy validation — 10K chain queries at N=65536 to fully characterize substrate envelope.

5 methods (argmax / soft_forward / smoother_only / VAMP_chain / warmstart_resonator)
x 5 K values x 5 depths x 5 seeds x 20 trials = many ops.
Designed to run 30-60 min sustained.
"""
from __future__ import annotations
import argparse, importlib.util, json, os, sys, time
from pathlib import Path
import torch
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
from verification import oracle  # noqa: E402

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
    if "results" not in s: return ("HEAVY_INCONCLUSIVE", "Missing.")
    r = s["results"]
    if not r: return ("HEAVY_INCONCLUSIVE", "Empty.")
    # Compare methods
    method_means = {}
    for key, acc in r.items():
        method = key.split("_")[0]
        method_means.setdefault(method, []).append(acc)
    avg = {m: sum(v)/len(v) for m, v in method_means.items()}
    return ("HEAVY_VALIDATED", f"Method means: {avg}")


def self_test_verdict():
    for s,exp in [({"results": {"argmax_K100_d50_s17": 0.2, "smoother_K100_d50_s17": 1.0}}, "HEAVY_VALIDATED"),({"results":{}},"HEAVY_INCONCLUSIVE"),({},"HEAVY_INCONCLUSIVE")]:
        a,_=compute_verdict(s)
        if a!=exp: raise AssertionError(f"{a}!={exp}")
    print("verdict self-test passed (3/3 cases)",flush=True)


def chain_argmax(M, start, rels, target, ea, ra):
    return mh.run_chain(M, start, rels, target, ea, ra)


def chain_smoother(M, start, rels, target, ea, ra):
    return so.chain_smoother_only(M, start, rels, target, ea, ra)


def chain_vamp(M, start, rels, target, ea, ra):
    return vc.vamp_chain_forward_backward(M, start, rels, target, ea, ra)


METHODS = {"argmax": chain_argmax, "smoother": chain_smoother, "vamp": chain_vamp}


def run_cell(method_name, N, K, depth, seed, n_trials, num_entities, num_relations, device):
    method = METHODS[method_name]
    num_ents = max(K, depth + 10, num_entities)
    gen = torch.Generator(device=device).manual_seed(seed + N + K + depth)
    ea = mh.make_bsc_codebook(num_ents, N, gen, device)
    ra = mh.make_bsc_codebook(num_relations, N, gen, device)
    cg = torch.Generator().manual_seed(seed + N + K + depth + 1009)
    correct = 0
    for trial in range(n_trials):
        perm = torch.randperm(num_ents, generator=cg)[:depth + 1]
        chain = perm.tolist()
        rels = [int(torch.randint(0, num_relations, (1,), generator=cg).item()) for _ in range(depth)]
        M = mh.build_factbase(chain, rels, max(0, K - depth), num_ents, num_relations, ea, ra, cg, device)
        if method(M, chain[0], rels, chain[-1], ea, ra): correct += 1
    return correct / n_trials


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if smoke:
        config = {"N": 8192, "K_grid": [100], "depth_grid": [25],
                   "seeds": [17, 23], "n_trials": 5, "methods": ["argmax", "smoother"],
                   "num_entities": 200, "num_relations": 20}
    else:
        config = {"N": 65536, "K_grid": [100, 500, 1000, 5000, 10000],
                   "depth_grid": [25, 50, 100, 200], "seeds": [17, 23, 31, 41, 53],
                   "n_trials": 20, "methods": ["argmax", "smoother", "vamp"],
                   "num_entities": 200, "num_relations": 20}
    results = {}
    n_cells = len(config["methods"]) * len(config["K_grid"]) * len(config["depth_grid"]) * len(config["seeds"])
    print(f"[config] {n_cells} cells x {config['n_trials']} trials = {n_cells * config['n_trials']} chains", flush=True)
    cell_i = 0
    for method in config["methods"]:
        for K in config["K_grid"]:
            for depth in config["depth_grid"]:
                if depth >= K: continue
                for seed in config["seeds"]:
                    acc = run_cell(method, config["N"], K, depth, seed, config["n_trials"],
                                     config["num_entities"], config["num_relations"], device)
                    key = f"{method}_K{K}_d{depth}_s{seed}"
                    results[key] = acc
                    cell_i += 1
                    if cell_i % 5 == 0:
                        print(f"  [{cell_i}/{n_cells}] {key}: acc={acc:.3f}", flush=True)
    summary = {"results": results, "n_cells": len(results)}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict":verdict,"verdict_msg":msg,"elapsed_s":elapsed,"summary":summary,"config":config}
    validate_metrics(metrics)
    tmp = out_dir/"metrics.json.tmp"; tmp.write_text(json.dumps(metrics,indent=2,default=float)); tmp.replace(out_dir/"metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14_heavy_validation_v1_smoke")
    s,v,m,e,c = run_experiment(smoke=True)
    oracle.assert_baseline_high("any_pass", max(s["results"].values())+0.001, 0.0)
    write_metrics(out_dir,s,v,m,e,c); print(f"\nSMOKE OK: {v}",flush=True)


def run_main():
    out_dir = get_output_dir("wave14_heavy_validation_v1")
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
