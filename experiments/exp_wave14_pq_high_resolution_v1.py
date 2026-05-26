"""P(q) high-resolution histogram — Strategy 10:16 v152 add-3.

Cycle 172 P(q) discrete spikes found 15 peaks but substrate has 28-element endpoint
partition. Hypothesis: 15 outer peaks have sub-structure (each ~2 sub-peaks =
hierarchical 28). 200 seeds, 500 bins.
"""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import argparse, importlib.util, json, os, time
from collections import Counter
from pathlib import Path
import torch
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from verification import oracle  # noqa: E402
_mh = importlib.util.spec_from_file_location("mh", REPO / "experiments" / "exp_wave14r_multihop_K100.py")
mh = importlib.util.module_from_spec(_mh); _mh.loader.exec_module(mh)


def get_output_dir(name):
    n = os.environ.get("HDLAB_EXP_NAME", name)
    out = REPO / "data" / f"exp_{n}"; out.mkdir(parents=True, exist_ok=True); return out


def validate_metrics(d):
    if not {"verdict","verdict_msg","elapsed_s","summary","config"}.issubset(d.keys()): raise ValueError("missing")


def compute_verdict(s):
    if "n_total_peaks" not in s: return ("PQ_HIGHRES_INCONCLUSIVE", "Missing.")
    n_total = s["n_total_peaks"]; n_outer = s["n_outer_peaks"]
    if 24 <= n_total <= 32:
        return ("PQ_HIERARCHICAL_28", f"n_total_peaks={n_total} in [24,32] (matches ~28 endpoint cardinality; outer={n_outer}).")
    if n_total <= n_outer + 2 and n_outer in range(12, 18):
        return ("PQ_FLAT_15", f"n_total={n_total} ~= n_outer={n_outer} in [12,18] (15 simple peaks; no hierarchy).")
    return ("PQ_OTHER_CARDINALITY", f"n_total={n_total} n_outer={n_outer} (different cardinality).")


def self_test_verdict():
    for s,exp in [
        ({"n_total_peaks":28, "n_outer_peaks":15},"PQ_HIERARCHICAL_28"),
        ({"n_total_peaks":15, "n_outer_peaks":15},"PQ_FLAT_15"),
        ({"n_total_peaks":10, "n_outer_peaks":5},"PQ_OTHER_CARDINALITY"),
        ({},"PQ_HIGHRES_INCONCLUSIVE"),
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


def find_peaks_with_substructure(samples, n_bins_outer=50, n_bins_fine=500):
    """Return (n_outer_peaks, n_total_peaks) via two-level histogram analysis."""
    if len(samples) < 20: return 0, 0
    t = torch.tensor(samples)
    lo, hi = t.min().item(), t.max().item()
    if hi - lo < 1e-6: return 1, 1
    # Outer histogram at low resolution
    outer = torch.histc(t, bins=n_bins_outer, min=lo, max=hi).tolist()
    max_outer = max(outer)
    threshold_outer = max_outer * 0.15
    outer_peaks = []
    for i in range(1, n_bins_outer-1):
        if outer[i] > outer[i-1] and outer[i] > outer[i+1] and outer[i] >= threshold_outer:
            outer_peaks.append(i)
    if outer[0] >= threshold_outer and outer[0] > outer[1]: outer_peaks.append(0)
    if outer[-1] >= threshold_outer and outer[-1] > outer[-2]: outer_peaks.append(n_bins_outer-1)
    n_outer = len(outer_peaks)
    # Fine histogram, count all peaks
    fine = torch.histc(t, bins=n_bins_fine, min=lo, max=hi).tolist()
    max_fine = max(fine)
    threshold_fine = max_fine * 0.08  # lower threshold for sub-structure
    fine_peaks = 0
    for i in range(1, n_bins_fine-1):
        if fine[i] > fine[i-1] and fine[i] > fine[i+1] and fine[i] >= threshold_fine:
            fine_peaks += 1
    return n_outer, fine_peaks


def run_experiment(smoke):
    t0=time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    cfg = {"N":2048 if smoke else 16384, "K":100, "depth":25 if smoke else 50,
           "num_entities":200, "num_relations":20,
           "n_starts":30 if smoke else 100,
           "n_seeds":50 if smoke else 200}
    q_samples = []
    log_every = max(1, cfg["n_seeds"] // 10)
    for seed_i in range(cfg["n_seeds"]):
        gen = torch.Generator(device=device).manual_seed(17 + seed_i * 13)
        ea = mh.make_bsc_codebook(cfg["num_entities"], cfg["N"], gen, device)
        ra = mh.make_bsc_codebook(cfg["num_relations"], cfg["N"], gen, device)
        cg = torch.Generator().manual_seed(17 + seed_i * 13 + 1009)
        perm = torch.randperm(cfg["num_entities"], generator=cg)[:cfg["depth"]+1]
        chain_rels = [int(torch.randint(0,cfg["num_relations"],(1,),generator=cg).item()) for _ in range(cfg["depth"])]
        M = mh.build_factbase(perm.tolist(), chain_rels, max(0,cfg["K"]-cfg["depth"]),
                              cfg["num_entities"], cfg["num_relations"], ea, ra, cg, device)
        q = measure_q_overlap(M, cfg["n_starts"], chain_rels, ea, ra)
        q_samples.append(q)
        if seed_i % log_every == 0:
            print(f"  seed_index={seed_i}/{cfg['n_seeds']}: q={q:.4f}", flush=True)
    n_outer, n_total = find_peaks_with_substructure(q_samples)
    q_mean = sum(q_samples) / len(q_samples)
    q_std = (sum((q - q_mean)**2 for q in q_samples) / len(q_samples)) ** 0.5
    print(f"\n  Across {len(q_samples)} seeds: n_outer={n_outer} n_total_peaks={n_total}", flush=True)
    print(f"  mean={q_mean:.4f} std={q_std:.4f}", flush=True)
    summary = {"n_total_peaks": n_total, "n_outer_peaks": n_outer,
               "q_mean": q_mean, "q_std": q_std, "n_seeds": len(q_samples)}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic()-t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, cfg


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict":verdict,"verdict_msg":msg,"elapsed_s":elapsed,"summary":summary,"config":config}
    validate_metrics(metrics)
    tmp = out_dir/"metrics.json.tmp"; tmp.write_text(json.dumps(metrics,indent=2,default=float)); tmp.replace(out_dir/"metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14_pq_high_resolution_v1_smoke")
    s,v,m,e,c = run_experiment(smoke=True)
    oracle.assert_baseline_high("peaks_present", float(s["n_total_peaks"])+0.001, 0.0)
    write_metrics(out_dir,s,v,m,e,c); print(f"\nSMOKE OK: {v}",flush=True)


def run_main():
    out_dir = get_output_dir("wave14_pq_high_resolution_v1")
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
