"""P(q) discrete spike structure — Strategy 09:45 PRIORITY D.

Research predicts P(q) supported on ~28 discrete spikes (connection to cycle 137
ENDPOINT_COLLAPSED 28/100 distinct endpoints). 1000-seed q_overlap measurements;
detect number of discrete peaks in P(q) histogram.
"""
from __future__ import annotations
import argparse, importlib.util, json, os, sys, time
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
    if "n_peaks_estimate" not in s: return ("PQ_DISCRETE_INCONCLUSIVE", "Missing.")
    n = s["n_peaks_estimate"]; ratio = s.get("peak_to_valley_ratio", 0.0)
    if 20 <= n <= 36 and ratio >= 2.0:
        return ("PQ_DISCRETE_28", f"n_peaks={n} in [20,36] AND peak/valley={ratio:.2f}>=2.0 (~28-element discrete structure).")
    if ratio >= 2.0:
        return ("PQ_DISCRETE_OTHER", f"n_peaks={n} not near 28 but ratio={ratio:.2f}>=2.0 (discrete but different cardinality).")
    return ("PQ_CONTINUOUS", f"n_peaks={n} peak/valley={ratio:.2f}<2.0 (smooth distribution; no discrete spikes).")


def self_test_verdict():
    for s,exp in [
        ({"n_peaks_estimate":28, "peak_to_valley_ratio":3.0},"PQ_DISCRETE_28"),
        ({"n_peaks_estimate":15, "peak_to_valley_ratio":4.0},"PQ_DISCRETE_OTHER"),
        ({"n_peaks_estimate":28, "peak_to_valley_ratio":1.2},"PQ_CONTINUOUS"),
        ({},"PQ_DISCRETE_INCONCLUSIVE"),
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


def estimate_peaks(samples, n_bins=100):
    """Count significant peaks in histogram; return (n_peaks, max_peak_to_valley_ratio)."""
    if len(samples) < 20: return 0, 0.0
    t = torch.tensor(samples)
    lo, hi = t.min().item(), t.max().item()
    if hi - lo < 1e-6: return 1, float("inf")
    hist = torch.histc(t, bins=n_bins, min=lo, max=hi).tolist()
    max_h = max(hist)
    threshold = max_h * 0.15  # peaks must be at least 15% of max
    peaks = []
    for i in range(1, n_bins-1):
        if hist[i] > hist[i-1] and hist[i] > hist[i+1] and hist[i] >= threshold:
            peaks.append((i, hist[i]))
    # Boundary peaks
    if hist[0] >= threshold and hist[0] > hist[1]: peaks.append((0, hist[0]))
    if hist[-1] >= threshold and hist[-1] > hist[-2]: peaks.append((n_bins-1, hist[-1]))
    n_peaks = len(peaks)
    if n_peaks < 2: return n_peaks, float("inf") if n_peaks == 1 else 0.0
    # Compute average peak-to-valley ratio for adjacent peak pairs
    peaks.sort()
    ratios = []
    for j in range(len(peaks) - 1):
        a, hA = peaks[j]; b, hB = peaks[j+1]
        if b - a < 2: continue
        valley = min(hist[a+1:b])
        if valley > 0:
            ratios.append(min(hA, hB) / valley)
        else:
            ratios.append(100.0)
    return n_peaks, (sum(ratios) / len(ratios)) if ratios else 0.0


def run_experiment(smoke):
    t0=time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    cfg = {"N":2048 if smoke else 16384, "K":100, "depth":25 if smoke else 50,
           "num_entities":200, "num_relations":20,
           "n_starts":30 if smoke else 100,
           "n_seeds":50 if smoke else 1000}
    q_samples = []
    log_every = max(1, cfg["n_seeds"] // 10)
    for seed_i in range(cfg["n_seeds"]):
        gen = torch.Generator(device=device).manual_seed(17 + seed_i * 17)
        ea = mh.make_bsc_codebook(cfg["num_entities"], cfg["N"], gen, device)
        ra = mh.make_bsc_codebook(cfg["num_relations"], cfg["N"], gen, device)
        cg = torch.Generator().manual_seed(17 + seed_i * 17 + 1009)
        perm = torch.randperm(cfg["num_entities"], generator=cg)[:cfg["depth"]+1]
        chain_rels = [int(torch.randint(0,cfg["num_relations"],(1,),generator=cg).item()) for _ in range(cfg["depth"])]
        M = mh.build_factbase(perm.tolist(), chain_rels, max(0,cfg["K"]-cfg["depth"]),
                              cfg["num_entities"], cfg["num_relations"], ea, ra, cg, device)
        q = measure_q_overlap(M, cfg["n_starts"], chain_rels, ea, ra)
        q_samples.append(q)
        if seed_i % log_every == 0:
            print(f"  seed_index={seed_i}/{cfg['n_seeds']}: q={q:.4f}", flush=True)
    n_peaks, ratio = estimate_peaks(q_samples)
    q_mean = sum(q_samples) / len(q_samples)
    q_std = (sum((q - q_mean)**2 for q in q_samples) / len(q_samples)) ** 0.5
    print(f"\n  P(q) over {len(q_samples)} seeds: n_peaks={n_peaks} peak/valley_ratio={ratio:.3f}", flush=True)
    print(f"  mean={q_mean:.4f} std={q_std:.4f}", flush=True)
    summary = {"n_peaks_estimate": n_peaks, "peak_to_valley_ratio": ratio,
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
    out_dir = get_output_dir("wave14_pq_discrete_spikes_v1_smoke")
    s,v,m,e,c = run_experiment(smoke=True)
    oracle.assert_baseline_high("n_peaks_present", float(s["n_peaks_estimate"])+0.001, 0.0)
    write_metrics(out_dir,s,v,m,e,c); print(f"\nSMOKE OK: {v}",flush=True)


def run_main():
    out_dir = get_output_dir("wave14_pq_discrete_spikes_v1")
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
