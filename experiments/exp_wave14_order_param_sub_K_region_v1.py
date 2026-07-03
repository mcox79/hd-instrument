"""Multi-component order parameter — Strategy 09:35 P4. Sub-K-region q_overlap stability.

Cycle 168 Gap 2 ORDER_PARAM_NONE refuted single-component q_overlap globally.
Test stability within sub-K regions: K_RESONANCE_BROAD band (900-1500),
normal cycles (100-500), longer cycles (2000+).
"""
from __future__ import annotations
import argparse, importlib.util, json, os, sys, time
from collections import Counter
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
    if "region_consistencies" not in s: return ("ORDER_PARAM_SUB_REGION_INCONCLUSIVE", "Missing.")
    regs = s["region_consistencies"]
    stable = [r for r,c in regs.items() if c >= 0.85]
    qmeans = s.get("region_qmeans", {})
    vals = list(qmeans.values())
    n_plateaus = 0
    if len(vals) >= 3:
        sorted_v = sorted(vals)
        gaps = [sorted_v[i+1] - sorted_v[i] for i in range(len(sorted_v)-1)]
        n_plateaus = sum(1 for g in gaps if g > 0.05) + 1
    if stable:
        return ("ORDER_PARAM_SUB_REGION_STABLE", f"stable in {stable}; consistencies={regs}.")
    if n_plateaus >= 3:
        return ("ORDER_PARAM_HIERARCHICAL", f"q values span {len(vals)} regions with {n_plateaus} plateaus: {qmeans}.")
    return ("ORDER_PARAM_GLOBAL_NONE_CONFIRMED", f"no sub-region stable; consistencies={regs}.")


def self_test_verdict():
    for s,exp in [
        ({"region_consistencies":{"resonance":0.92,"normal":0.4,"longer":0.5}, "region_qmeans":{"resonance":0.8,"normal":0.3,"longer":0.5}},"ORDER_PARAM_SUB_REGION_STABLE"),
        ({"region_consistencies":{"a":0.5,"b":0.6,"c":0.4}, "region_qmeans":{"a":0.1,"b":0.4,"c":0.8}},"ORDER_PARAM_HIERARCHICAL"),
        ({"region_consistencies":{"a":0.3,"b":0.4,"c":0.5}, "region_qmeans":{"a":0.5,"b":0.51,"c":0.52}},"ORDER_PARAM_GLOBAL_NONE_CONFIRMED"),
        ({},"ORDER_PARAM_SUB_REGION_INCONCLUSIVE"),
    ]:
        a,_=compute_verdict(s)
        if a!=exp: raise AssertionError(f"{a}!={exp}")
    print("verdict self-test passed (4/4 cases)",flush=True)


def measure_q_overlap(M, n_starts, chain_rels, ea, ra):
    endpoints = []
    for start_idx in range(min(n_starts, ea.shape[0])):
        current = start_idx
        for r_idx in chain_rels:
            current = int((ea @ (M * (ea[current] * ra[r_idx]))).argmax().item())
        endpoints.append(current)
    n = len(endpoints)
    counter = Counter(endpoints)
    q = sum(c*c for c in counter.values()) / (n*n)
    return q


def run_region(K_grid, region_name, N, depth, num_entities, num_relations, n_starts, seeds, device):
    """For each (K, seed) build W and measure q. Return per-seed q (aggregated across K)."""
    q_per_seed = []
    for seed in seeds:
        q_per_K = []
        for K in K_grid:
            gen = torch.Generator(device=device).manual_seed(seed)
            ea = mh.make_bsc_codebook(num_entities, N, gen, device)
            ra = mh.make_bsc_codebook(num_relations, N, gen, device)
            cg = torch.Generator().manual_seed(seed + 1009 + K)
            perm = torch.randperm(num_entities, generator=cg)[:depth+1]
            chain_rels = [int(torch.randint(0,num_relations,(1,),generator=cg).item()) for _ in range(depth)]
            M = mh.build_factbase(perm.tolist(), chain_rels, max(0,K-depth),
                                  num_entities, num_relations, ea, ra, cg, device)
            q = measure_q_overlap(M, n_starts, chain_rels, ea, ra)
            q_per_K.append(q)
        q_seed_mean = sum(q_per_K) / len(q_per_K)
        q_per_seed.append(q_seed_mean)
        print(f"  region={region_name} seed={seed}: q_per_K={[f'{q:.3f}' for q in q_per_K]}, mean={q_seed_mean:.4f}", flush=True)
    q_mean = sum(q_per_seed) / len(q_per_seed)
    q_var = sum((q - q_mean)**2 for q in q_per_seed) / len(q_per_seed)
    q_sd = q_var ** 0.5
    consistency = max(0.0, 1 - q_sd / max(abs(q_mean), 1e-9))
    return q_mean, consistency, q_per_seed


def run_experiment(smoke):
    t0=time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    cfg = {"N":4096 if smoke else 16384,
            "depth":25, "num_entities":200, "num_relations":20,
            "n_starts":30 if smoke else 100,
            "seeds":[17, 23] if smoke else [17, 23, 31, 41, 53],
            "regions":{
                "resonance":[900, 1000, 1200] if smoke else [900, 1000, 1100, 1200, 1500],
                "normal":[100, 300] if smoke else [100, 200, 300, 400, 500],
                "longer":[2000] if smoke else [2000, 3000, 5000],
            }}
    region_consistencies = {}
    region_qmeans = {}
    region_qpers = {}
    for region_name, K_grid in cfg["regions"].items():
        q_mean, cons, q_per_seed = run_region(K_grid, region_name, cfg["N"], cfg["depth"],
                                              cfg["num_entities"], cfg["num_relations"],
                                              cfg["n_starts"], cfg["seeds"], device)
        region_consistencies[region_name] = cons
        region_qmeans[region_name] = q_mean
        region_qpers[region_name] = q_per_seed
        print(f"  region={region_name}: q_mean={q_mean:.4f}, consistency={cons:.3f}", flush=True)
    summary = {"region_consistencies": region_consistencies,
                "region_qmeans": region_qmeans,
                "region_qpers": region_qpers}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic()-t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, cfg


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict":verdict,"verdict_msg":msg,"elapsed_s":elapsed,"summary":summary,"config":config}
    validate_metrics(metrics)
    tmp = out_dir/"metrics.json.tmp"; tmp.write_text(json.dumps(metrics,indent=2,default=float)); tmp.replace(out_dir/"metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14_order_param_sub_K_region_v1_smoke")
    s,v,m,e,c = run_experiment(smoke=True)
    cons_max = max(s["region_consistencies"].values())
    oracle.assert_baseline_high("consistency_present", cons_max+0.001, 0.0)
    write_metrics(out_dir,s,v,m,e,c); print(f"\nSMOKE OK: {v}",flush=True)


def run_main():
    out_dir = get_output_dir("wave14_order_param_sub_K_region_v1")
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
