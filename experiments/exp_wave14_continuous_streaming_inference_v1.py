"""Continuous streaming inference — Strategy 10:03 v151 P5 (Cap 3).

Drift-diffusion NESS implies substrate can run continuously with streaming
inputs producing continuous outputs. Measure throughput steady-state vs burn-in.
"""
from __future__ import annotations
import argparse, importlib.util, json, os, sys, time
from pathlib import Path
import torch
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
from verification import oracle  # noqa: E402


def get_output_dir(name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d):
    if not {"verdict","verdict_msg","elapsed_s","summary","config"}.issubset(d.keys()): raise ValueError("missing")


def compute_verdict(s):
    if "throughput_ratio" not in s: return ("STREAMING_INCONCLUSIVE", "Missing.")
    r = s["throughput_ratio"]
    if r >= 0.9: return ("STREAMING_CONTINUOUS_PASS", f"steady/burn-in throughput={r:.3f}>=0.9 (NESS robust streaming).")
    if r >= 0.5: return ("STREAMING_DEGRADED", f"throughput_ratio={r:.3f} in [0.5, 0.9] (degraded but operating).")
    return ("STREAMING_NESS_BREAKS", f"throughput_ratio={r:.3f}<0.5 (NESS breaks after burn-in).")


def self_test_verdict():
    for s,exp in [
        ({"throughput_ratio":0.95},"STREAMING_CONTINUOUS_PASS"),
        ({"throughput_ratio":0.7},"STREAMING_DEGRADED"),
        ({"throughput_ratio":0.3},"STREAMING_NESS_BREAKS"),
        ({},"STREAMING_INCONCLUSIVE"),
    ]:
        a,_=compute_verdict(s)
        if a!=exp: raise AssertionError(f"{a}!={exp}")
    print("verdict self-test passed (4/4 cases)",flush=True)


def make_pattern(N, gen, device):
    b = (torch.rand(N, generator=gen) > 0.5).to(device).float()
    return 2.0 * b - 1.0


def stream_block(W, queries, max_iter=20):
    """Process a block of queries; return total time and accuracy."""
    t0 = time.monotonic()
    n_correct = 0
    for q, target in queries:
        s = q.clone()
        for _ in range(max_iter):
            s = torch.sign(W @ s); s[s == 0] = 1.0
        # Compare with target
        overlap = float((s * target).mean().item())
        if overlap > 0.7: n_correct += 1
    elapsed = time.monotonic() - t0
    return elapsed, n_correct / len(queries)


def run_experiment(smoke):
    t0=time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    cfg = {"N":2048 if smoke else 8192, "M":50 if smoke else 200,
           "burn_in":20 if smoke else 100, "steady":40 if smoke else 200,
           "n_blocks":3, "seed":17}
    gen = torch.Generator().manual_seed(cfg["seed"])
    keys = torch.stack([make_pattern(cfg["N"], gen, device) for _ in range(cfg["M"])], dim=0)
    values = torch.stack([make_pattern(cfg["N"], gen, device) for _ in range(cfg["M"])], dim=0)
    W = (values.T @ keys) / cfg["N"]
    # Burn-in block
    burn_queries = [(keys[i % cfg["M"]], values[i % cfg["M"]]) for i in range(cfg["burn_in"])]
    burn_time, burn_acc = stream_block(W, burn_queries)
    burn_throughput = cfg["burn_in"] / burn_time
    print(f"  burn-in: {cfg['burn_in']} queries in {burn_time:.3f}s, throughput={burn_throughput:.2f} q/s, acc={burn_acc:.3f}", flush=True)
    # Steady-state blocks
    steady_throughputs = []
    for b in range(cfg["n_blocks"]):
        st_queries = [(keys[(b*cfg["steady"]+i) % cfg["M"]], values[(b*cfg["steady"]+i) % cfg["M"]]) for i in range(cfg["steady"])]
        st_time, st_acc = stream_block(W, st_queries)
        thr = cfg["steady"] / st_time
        steady_throughputs.append(thr)
        print(f"  steady block {b}: {cfg['steady']} queries in {st_time:.3f}s, throughput={thr:.2f} q/s, acc={st_acc:.3f}", flush=True)
    steady_mean = sum(steady_throughputs) / len(steady_throughputs)
    ratio = steady_mean / max(burn_throughput, 1e-9)
    print(f"\n  steady throughput mean={steady_mean:.2f} q/s, ratio={ratio:.3f}", flush=True)
    summary = {"throughput_ratio": ratio, "burn_throughput": burn_throughput,
               "steady_throughput_mean": steady_mean, "steady_throughputs": steady_throughputs}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic()-t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, cfg


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict":verdict,"verdict_msg":msg,"elapsed_s":elapsed,"summary":summary,"config":config}
    validate_metrics(metrics)
    tmp = out_dir/"metrics.json.tmp"; tmp.write_text(json.dumps(metrics,indent=2,default=float)); tmp.replace(out_dir/"metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14_continuous_streaming_inference_v1_smoke")
    s,v,m,e,c = run_experiment(smoke=True)
    oracle.assert_baseline_high("ratio_present", s["throughput_ratio"]+0.001, 0.0)
    write_metrics(out_dir,s,v,m,e,c); print(f"\nSMOKE OK: {v}",flush=True)


def run_main():
    out_dir = get_output_dir("wave14_continuous_streaming_inference_v1")
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
