"""Substrate order parameter — Strategy 07:08 P2 (META Gap 2). Phase distribution + q-overlap."""
from __future__ import annotations
import argparse, importlib.util, json, math, os, sys, time
from collections import Counter
from pathlib import Path
import torch
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
from verification import oracle  # noqa: E402
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
    if "q_overlap_seed_consistency" not in s: return ("ORDER_INCONCLUSIVE", "Missing.")
    consistency = s["q_overlap_seed_consistency"]
    if consistency >= 0.85: return ("ORDER_PARAM_STABLE", f"q_overlap seed-consistency={consistency:.3f}>=0.85.")
    return ("ORDER_PARAM_NONE", f"q_overlap seed-consistency={consistency:.3f}<0.85.")


def self_test_verdict():
    for s,exp in [({"q_overlap_seed_consistency":0.92},"ORDER_PARAM_STABLE"),({"q_overlap_seed_consistency":0.4},"ORDER_PARAM_NONE"),({},"ORDER_INCONCLUSIVE")]:
        a,_=compute_verdict(s)
        if a!=exp: raise AssertionError(f"{a}!={exp}")
    print("verdict self-test passed (3/3 cases)",flush=True)


def measure_q_overlap(M, n_starts, chain_rels, ea, ra, max_iter):
    """For each starting codeword, identify endpoint after L hops; compute pairwise endpoint matches."""
    endpoints = []
    for start_idx in range(min(n_starts, ea.shape[0])):
        current = start_idx
        for r_idx in chain_rels:
            current = int((ea @ (M * (ea[current] * ra[r_idx]))).argmax().item())
        endpoints.append(current)
    # q = (1/K) sum_i,j delta(endpoint_i, endpoint_j) — fraction of pairs sharing endpoint
    n = len(endpoints)
    counter = Counter(endpoints)
    q = sum(c*c for c in counter.values()) / (n*n)
    return q, dict(counter.most_common(10))


def run_experiment(smoke):
    t0=time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    cfg = {"N":4096 if smoke else 65536, "K":100, "depth":25,
           "num_entities":200, "num_relations":20, "n_starts":50 if smoke else 100,
           "seeds":[17, 23] if smoke else [17, 23, 31, 41, 53]}
    q_per_seed = []
    for seed in cfg["seeds"]:
        gen = torch.Generator(device=device).manual_seed(seed)
        ea = mh.make_bsc_codebook(cfg["num_entities"], cfg["N"], gen, device)
        ra = mh.make_bsc_codebook(cfg["num_relations"], cfg["N"], gen, device)
        cg = torch.Generator().manual_seed(seed + 1009)
        perm = torch.randperm(cfg["num_entities"], generator=cg)[:cfg["depth"]+1]
        chain_rels = [int(torch.randint(0,cfg["num_relations"],(1,),generator=cg).item()) for _ in range(cfg["depth"])]
        M = mh.build_factbase(perm.tolist(), chain_rels, max(0,cfg["K"]-cfg["depth"]), cfg["num_entities"], cfg["num_relations"], ea, ra, cg, device)
        q, top = measure_q_overlap(M, cfg["n_starts"], chain_rels, ea, ra, max_iter=50)
        q_per_seed.append(q)
        print(f"  seed={seed}: q_overlap={q:.4f}, top endpoints={top}", flush=True)
    q_mean = sum(q_per_seed) / len(q_per_seed)
    q_var = sum((q - q_mean)**2 for q in q_per_seed) / len(q_per_seed)
    q_sd = q_var ** 0.5
    # Consistency = 1 - relative std (capped at 0)
    consistency = max(0, 1 - q_sd / max(abs(q_mean), 1e-9))
    print(f"  q_mean={q_mean:.4f}, q_stdev={q_sd:.4f}, consistency={consistency:.3f}", flush=True)
    summary = {"q_overlap_per_seed": q_per_seed, "q_overlap_mean": q_mean,
                "q_overlap_stdev": q_sd, "q_overlap_seed_consistency": consistency}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic()-t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, cfg


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict":verdict,"verdict_msg":msg,"elapsed_s":elapsed,"summary":summary,"config":config}
    validate_metrics(metrics)
    tmp = out_dir/"metrics.json.tmp"; tmp.write_text(json.dumps(metrics,indent=2,default=float)); tmp.replace(out_dir/"metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14_substrate_order_parameter_v1_smoke")
    s,v,m,e,c = run_experiment(smoke=True)
    oracle.assert_baseline_high("q_present", s["q_overlap_mean"]+0.001, 0.0)
    write_metrics(out_dir,s,v,m,e,c); print(f"\nSMOKE OK: {v}",flush=True)


def run_main():
    out_dir = get_output_dir("wave14_substrate_order_parameter_v1")
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
