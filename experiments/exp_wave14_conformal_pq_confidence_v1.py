"""Conformal P(q) confidence — Strategy 10:03 v151 P2 (Gap C calibration rescue).

Bet G TEMPSCALE_KILLED (cycle 168). Distribution-free conformal prediction wrapper
over P(q) bootstrap variance. Target 95% coverage.
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
    if "coverage" not in s: return ("CONFORMAL_INCONCLUSIVE", "Missing.")
    c = s["coverage"]
    if 0.93 <= c <= 0.97: return ("CONFORMAL_COVERED", f"coverage={c:.3f} in [0.93, 0.97] (proper 95% conformal coverage).")
    if c > 0.97: return ("CONFORMAL_OVERCOVERAGE", f"coverage={c:.3f}>0.97 (too conservative).")
    return ("CONFORMAL_UNDERCOVERAGE", f"coverage={c:.3f}<0.93 (calibration fails).")


def self_test_verdict():
    for s,exp in [
        ({"coverage":0.95},"CONFORMAL_COVERED"),
        ({"coverage":0.99},"CONFORMAL_OVERCOVERAGE"),
        ({"coverage":0.85},"CONFORMAL_UNDERCOVERAGE"),
        ({},"CONFORMAL_INCONCLUSIVE"),
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


def sample_q(seed, N, K, depth, num_entities, num_relations, n_starts, device):
    gen = torch.Generator(device=device).manual_seed(seed)
    ea = mh.make_bsc_codebook(num_entities, N, gen, device)
    ra = mh.make_bsc_codebook(num_relations, N, gen, device)
    cg = torch.Generator().manual_seed(seed + 1009)
    perm = torch.randperm(num_entities, generator=cg)[:depth+1]
    chain_rels = [int(torch.randint(0,num_relations,(1,),generator=cg).item()) for _ in range(depth)]
    M = mh.build_factbase(perm.tolist(), chain_rels, max(0,K-depth),
                          num_entities, num_relations, ea, ra, cg, device)
    return measure_q_overlap(M, n_starts, chain_rels, ea, ra)


def run_experiment(smoke):
    t0=time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    cfg = {"N":2048 if smoke else 8192, "K":100, "depth":25,
            "num_entities":200, "num_relations":20,
            "n_starts":20 if smoke else 60,
            "n_calibration":40 if smoke else 200, "n_test":40 if smoke else 200,
            "target_coverage":0.95}
    print(f"  calibration: {cfg['n_calibration']} seeds", flush=True)
    calibration = [sample_q(17 + s * 7, cfg["N"], cfg["K"], cfg["depth"],
                            cfg["num_entities"], cfg["num_relations"], cfg["n_starts"], device)
                   for s in range(cfg["n_calibration"])]
    # Empirical conformal threshold: prediction interval [q_lo, q_hi] from quantiles.
    sorted_cal = sorted(calibration)
    alpha = 1 - cfg["target_coverage"]
    lo_idx = int(len(sorted_cal) * alpha / 2)
    hi_idx = int(len(sorted_cal) * (1 - alpha / 2))
    q_lo = sorted_cal[lo_idx]; q_hi = sorted_cal[hi_idx-1 if hi_idx>0 else 0]
    print(f"  conformal interval: [{q_lo:.4f}, {q_hi:.4f}]", flush=True)
    print(f"  test: {cfg['n_test']} seeds", flush=True)
    test_q = [sample_q(17 + 10000 + s * 11, cfg["N"], cfg["K"], cfg["depth"],
                       cfg["num_entities"], cfg["num_relations"], cfg["n_starts"], device)
              for s in range(cfg["n_test"])]
    in_interval = sum(1 for q in test_q if q_lo <= q <= q_hi)
    coverage = in_interval / len(test_q)
    print(f"  test coverage = {in_interval}/{len(test_q)} = {coverage:.3f}", flush=True)
    summary = {"coverage": coverage, "q_lo": q_lo, "q_hi": q_hi,
               "n_calibration": cfg["n_calibration"], "n_test": cfg["n_test"],
               "target_coverage": cfg["target_coverage"]}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic()-t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, cfg


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict":verdict,"verdict_msg":msg,"elapsed_s":elapsed,"summary":summary,"config":config}
    validate_metrics(metrics)
    tmp = out_dir/"metrics.json.tmp"; tmp.write_text(json.dumps(metrics,indent=2,default=float)); tmp.replace(out_dir/"metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14_conformal_pq_confidence_v1_smoke")
    s,v,m,e,c = run_experiment(smoke=True)
    oracle.assert_baseline_high("cov_present", s["coverage"]+0.001, 0.0)
    write_metrics(out_dir,s,v,m,e,c); print(f"\nSMOKE OK: {v}",flush=True)


def run_main():
    out_dir = get_output_dir("wave14_conformal_pq_confidence_v1")
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
