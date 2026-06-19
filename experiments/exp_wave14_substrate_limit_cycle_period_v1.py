"""Limit cycle period characterization — Strategy 00:13 P1.

Substrate's psi has idempotence rate 0.000 (cycle 141 RETRACT_REFUTED). Implies
limit cycles. Measure cycle period per starting codeword.
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
    if "frac_with_cycle" not in s: return ("CYCLE_INCONCLUSIVE", "Missing.")
    f = s["frac_with_cycle"]; periods = s["periods"]
    short_periods = [p for p in periods if 2 <= p <= 100]
    frac_short = len(short_periods) / max(len(periods), 1)
    if f >= 0.5 and frac_short >= 0.5:
        return ("LIMIT_CYCLE_DETECTED", f"{f*100:.0f}% codewords show cycles; {frac_short*100:.0f}% in [2,100] range.")
    if f >= 0.5:
        return ("LIMIT_CYCLE_LONG", f"{f*100:.0f}% cycles but period >100.")
    if f < 0.1:
        return ("NO_LIMIT_CYCLES", f"Only {f*100:.0f}% codewords show cycles within max_depth.")
    return ("MIXED", f"{f*100:.0f}% codewords show cycles.")


def self_test_verdict():
    for s,exp in [
        ({"frac_with_cycle":0.8,"periods":[5,10,20,50]},"LIMIT_CYCLE_DETECTED"),
        ({"frac_with_cycle":0.6,"periods":[150,180,200]},"LIMIT_CYCLE_LONG"),
        ({"frac_with_cycle":0.05,"periods":[10]},"NO_LIMIT_CYCLES"),
        ({"frac_with_cycle":0.3,"periods":[20,50]},"MIXED"),
        ({},"CYCLE_INCONCLUSIVE"),
    ]:
        a,_=compute_verdict(s)
        if a!=exp: raise AssertionError(f"{a}!={exp}")
    print("verdict self-test passed (5/5 cases)",flush=True)


def measure_cycle(M, start_idx, rels, ea, ra, max_iter=200):
    """Run W*sign(codebook[winner]) iteratively (no rel rotation) to find argmax fixed point or cycle."""
    current = start_idx
    trajectory = [current]
    rel_idx = 0
    for hop in range(max_iter):
        rel = ra[rels[rel_idx % len(rels)]]
        probe = M * (ea[current] * rel)
        current = int((ea @ probe).argmax().item())
        if current in trajectory:
            cycle_start = trajectory.index(current)
            period = (hop + 1) - cycle_start
            return period, cycle_start
        trajectory.append(current)
        rel_idx += 1
    return 0, max_iter


def run_experiment(smoke):
    t0=time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    cfg = {"N":8192 if smoke else 65536, "K":100, "depth":25, "num_entities":200, "num_relations":20,
           "max_iter":50 if smoke else 200, "n_starts":50 if smoke else 200, "seed":17}
    gen = torch.Generator(device=device).manual_seed(cfg["seed"])
    ea = mh.make_bsc_codebook(cfg["num_entities"], cfg["N"], gen, device)
    ra = mh.make_bsc_codebook(cfg["num_relations"], cfg["N"], gen, device)
    cg = torch.Generator().manual_seed(cfg["seed"]+1009)
    perm = torch.randperm(cfg["num_entities"], generator=cg)[:cfg["depth"]+1]
    chain_ents = perm.tolist()
    chain_rels = [int(torch.randint(0,cfg["num_relations"],(1,),generator=cg).item()) for _ in range(cfg["depth"])]
    M = mh.build_factbase(chain_ents, chain_rels, max(0,cfg["K"]-cfg["depth"]), cfg["num_entities"], cfg["num_relations"], ea, ra, cg, device)
    periods = []
    cycle_count = 0
    for start_idx in range(min(cfg["n_starts"], cfg["num_entities"])):
        period, cycle_start = measure_cycle(M, start_idx, chain_rels, ea, ra, cfg["max_iter"])
        if period > 0:
            periods.append(period)
            cycle_count += 1
    n_starts = min(cfg["n_starts"], cfg["num_entities"])
    frac = cycle_count / n_starts
    period_counts = Counter(periods)
    print(f"  {cycle_count}/{n_starts} ({frac*100:.0f}%) starts show cycles", flush=True)
    print(f"  period distribution: {dict(period_counts.most_common(10))}", flush=True)
    summary = {"frac_with_cycle": frac, "periods": periods,
                "n_starts": n_starts, "period_counts": dict(period_counts.most_common(20))}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic()-t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, cfg


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict":verdict,"verdict_msg":msg,"elapsed_s":elapsed,"summary":summary,"config":config}
    validate_metrics(metrics)
    tmp = out_dir/"metrics.json.tmp"; tmp.write_text(json.dumps(metrics,indent=2,default=float)); tmp.replace(out_dir/"metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14_substrate_limit_cycle_period_v1_smoke")
    s,v,m,e,c = run_experiment(smoke=True)
    oracle.assert_baseline_high("any_cycle", float(s["frac_with_cycle"])+0.001, 0.0)
    write_metrics(out_dir,s,v,m,e,c); print(f"\nSMOKE OK: {v}",flush=True)


def run_main():
    out_dir = get_output_dir("wave14_substrate_limit_cycle_period_v1")
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
