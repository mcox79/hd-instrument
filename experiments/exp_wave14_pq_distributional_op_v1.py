"""P(q) distributional order parameter — Strategy 09:45 PRIORITY A.

Research hypothesis: substrate has distributional P(q) order parameter, not scalar.
Cycle 168 ORDER_PARAM_NONE measured seed-consistency = 1 - sd/|mean| which kills
non-self-averaging signals. Instead, sample P(q) across 50 seeds, report mean +
std + skewness + bimodality.
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
    if "q_mean" not in s: return ("PQ_DIST_OP_INCONCLUSIVE", "Missing.")
    m = s["q_mean"]; sd = s["q_std"]; bimodal = s.get("bimodal", False)
    if bimodal:
        return ("PQ_DIST_OP_BIMODAL", f"P(q) bimodal mean={m:.3f} std={sd:.3f} (hidden symmetry breaking).")
    if m >= 0.85 and sd < 0.05:
        return ("PQ_DIST_OP_PASS", f"mean(P(q))={m:.3f}>=0.85 AND std={sd:.3f}<0.05; substrate HAS distributional OP.")
    if m >= 0.85:
        return ("PQ_DIST_OP_WIDE", f"mean(P(q))={m:.3f}>=0.85 but std={sd:.3f}>=0.05 (non-self-averaging high mean).")
    return ("PQ_DIST_OP_FAIL", f"mean(P(q))={m:.3f}<0.85; substrate genuinely lacks OP.")


def self_test_verdict():
    for s,exp in [
        ({"q_mean":0.9,"q_std":0.02},"PQ_DIST_OP_PASS"),
        ({"q_mean":0.9,"q_std":0.10},"PQ_DIST_OP_WIDE"),
        ({"q_mean":0.5,"q_std":0.05,"bimodal":True},"PQ_DIST_OP_BIMODAL"),
        ({"q_mean":0.3,"q_std":0.05},"PQ_DIST_OP_FAIL"),
        ({},"PQ_DIST_OP_INCONCLUSIVE"),
    ]:
        a,_=compute_verdict(s)
        if a!=exp: raise AssertionError(f"{a}!={exp}")
    print("verdict self-test passed (5/5 cases)",flush=True)


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


def detect_bimodal(samples, n_bins=20):
    """Return True if histogram shows a valley between two peaks (bimodal)."""
    if len(samples) < 20: return False
    t = torch.tensor(samples)
    lo, hi = t.min().item(), t.max().item()
    if hi - lo < 1e-6: return False
    hist = torch.histc(t, bins=n_bins, min=lo, max=hi).tolist()
    # Find peaks (local maxima with significant height)
    peaks = []
    for i in range(1, n_bins-1):
        if hist[i] > hist[i-1] and hist[i] > hist[i+1] and hist[i] >= max(hist) * 0.3:
            peaks.append(i)
    if len(peaks) < 2: return False
    # Check valley between two largest peaks
    sorted_peaks = sorted(peaks, key=lambda i: -hist[i])[:2]
    a, b = sorted(sorted_peaks)
    valley_min = min(hist[a+1:b])
    return valley_min < min(hist[a], hist[b]) * 0.5


def run_experiment(smoke):
    t0=time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    cfg = {"N":4096 if smoke else 65536, "K":100, "depth":25 if smoke else 50,
           "num_entities":200, "num_relations":20,
           "n_starts":30 if smoke else 100,
           "n_seeds":10 if smoke else 50}
    q_samples = []
    for seed in range(cfg["n_seeds"]):
        gen = torch.Generator(device=device).manual_seed(17 + seed * 101)
        ea = mh.make_bsc_codebook(cfg["num_entities"], cfg["N"], gen, device)
        ra = mh.make_bsc_codebook(cfg["num_relations"], cfg["N"], gen, device)
        cg = torch.Generator().manual_seed(17 + seed * 101 + 1009)
        perm = torch.randperm(cfg["num_entities"], generator=cg)[:cfg["depth"]+1]
        chain_rels = [int(torch.randint(0,cfg["num_relations"],(1,),generator=cg).item()) for _ in range(cfg["depth"])]
        M = mh.build_factbase(perm.tolist(), chain_rels, max(0,cfg["K"]-cfg["depth"]),
                              cfg["num_entities"], cfg["num_relations"], ea, ra, cg, device)
        q = measure_q_overlap(M, cfg["n_starts"], chain_rels, ea, ra)
        q_samples.append(q)
        if seed % 10 == 0 or seed < 3:
            print(f"  seed_index={seed}: q={q:.4f}", flush=True)
    n = len(q_samples)
    q_mean = sum(q_samples) / n
    q_var = sum((q - q_mean)**2 for q in q_samples) / n
    q_std = q_var ** 0.5
    # Skewness
    if q_std > 1e-9:
        q_skew = sum((q - q_mean)**3 for q in q_samples) / (n * q_std**3)
    else:
        q_skew = 0.0
    frac_above_85 = sum(1 for q in q_samples if q >= 0.85) / n
    bimodal = detect_bimodal(q_samples)
    print(f"\n  P(q) over {n} seeds: mean={q_mean:.4f} std={q_std:.4f} skew={q_skew:.3f} "
          f"frac>=0.85={frac_above_85:.3f} bimodal={bimodal}", flush=True)
    summary = {"q_mean": q_mean, "q_std": q_std, "q_skewness": q_skew,
               "frac_above_threshold": frac_above_85, "bimodal": bool(bimodal),
               "n_seeds": n, "q_samples": q_samples,
               "q_min": float(min(q_samples)), "q_max": float(max(q_samples))}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic()-t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, cfg


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict":verdict,"verdict_msg":msg,"elapsed_s":elapsed,"summary":summary,"config":config}
    validate_metrics(metrics)
    tmp = out_dir/"metrics.json.tmp"; tmp.write_text(json.dumps(metrics,indent=2,default=float)); tmp.replace(out_dir/"metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14_pq_distributional_op_v1_smoke")
    s,v,m,e,c = run_experiment(smoke=True)
    oracle.assert_baseline_high("q_present", s["q_mean"]+0.001, 0.0)
    write_metrics(out_dir,s,v,m,e,c); print(f"\nSMOKE OK: {v}",flush=True)


def run_main():
    out_dir = get_output_dir("wave14_pq_distributional_op_v1")
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
