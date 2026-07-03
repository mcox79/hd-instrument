"""P(q) shape introspection — Strategy 10:03 v151 P6 (Cap 4).

Substrate's P(q) shape changes across phases (K-resonance band, normal regime,
longer regime). Substrate can self-introspect phase from P(q) moments.
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
    if "moment_separation" not in s: return ("PQ_INTROSPECTION_INCONCLUSIVE", "Missing.")
    sep = s["moment_separation"]
    if sep >= 1.5: return ("PQ_INTROSPECTION_DETECTS", f"moment_separation={sep:.3f}>=1.5 (P(q) shape distinguishes phases).")
    if sep < 0.5: return ("PQ_NO_PHASE_SIGNATURE", f"moment_separation={sep:.3f}<0.5 (P(q) shape invariant across phases).")
    return ("PQ_INTROSPECTION_PARTIAL", f"moment_separation={sep:.3f} in [0.5, 1.5].")


def self_test_verdict():
    for s,exp in [
        ({"moment_separation":2.0},"PQ_INTROSPECTION_DETECTS"),
        ({"moment_separation":0.3},"PQ_NO_PHASE_SIGNATURE"),
        ({"moment_separation":1.0},"PQ_INTROSPECTION_PARTIAL"),
        ({},"PQ_INTROSPECTION_INCONCLUSIVE"),
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


def compute_moments(samples):
    """Return (mean, std, skewness, kurtosis)."""
    n = len(samples)
    m1 = sum(samples) / n
    m2 = sum((x-m1)**2 for x in samples) / n
    std = m2 ** 0.5
    if std < 1e-9: return m1, std, 0.0, 0.0
    m3 = sum((x-m1)**3 for x in samples) / n
    m4 = sum((x-m1)**4 for x in samples) / n
    skew = m3 / std**3
    kurt = m4 / std**4 - 3.0
    return m1, std, skew, kurt


def collect_pq_per_K(K, N, depth, num_entities, num_relations, n_starts, n_seeds, device):
    q_samples = []
    for s in range(n_seeds):
        seed = 17 + s * 37
        gen = torch.Generator(device=device).manual_seed(seed)
        ea = mh.make_bsc_codebook(num_entities, N, gen, device)
        ra = mh.make_bsc_codebook(num_relations, N, gen, device)
        cg = torch.Generator().manual_seed(seed + 1009 + K)
        perm = torch.randperm(num_entities, generator=cg)[:depth+1]
        chain_rels = [int(torch.randint(0,num_relations,(1,),generator=cg).item()) for _ in range(depth)]
        M = mh.build_factbase(perm.tolist(), chain_rels, max(0,K-depth),
                              num_entities, num_relations, ea, ra, cg, device)
        q = measure_q_overlap(M, n_starts, chain_rels, ea, ra)
        q_samples.append(q)
    return q_samples


def run_experiment(smoke):
    t0=time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    cfg = {"N":2048 if smoke else 8192,
            "phases":{"low_K":50, "K_resonance":1000, "high_K":3000} if smoke
                     else {"low_K":100, "K_resonance":1000, "high_K":3000},
            "depth":25, "num_entities":200, "num_relations":20,
            "n_starts":20 if smoke else 80,
            "n_seeds":5 if smoke else 20}
    phase_moments = {}
    phase_samples = {}
    for phase_name, K in cfg["phases"].items():
        q_samples = collect_pq_per_K(K, cfg["N"], cfg["depth"], cfg["num_entities"],
                                     cfg["num_relations"], cfg["n_starts"], cfg["n_seeds"], device)
        m, sd, sk, kr = compute_moments(q_samples)
        phase_moments[phase_name] = {"mean": m, "std": sd, "skew": sk, "kurt": kr, "K": K}
        phase_samples[phase_name] = q_samples
        print(f"  phase={phase_name} K={K}: mean={m:.4f} std={sd:.4f} skew={sk:.3f} kurt={kr:.3f}", flush=True)
    # Compute moment separation: pairwise distance between phase moment vectors,
    # normalized by pooled std.
    phase_names = list(phase_moments.keys())
    pooled_std = sum(phase_moments[p]["std"] for p in phase_names) / len(phase_names)
    seps = []
    for i in range(len(phase_names)):
        for j in range(i+1, len(phase_names)):
            mi = phase_moments[phase_names[i]]["mean"]
            mj = phase_moments[phase_names[j]]["mean"]
            seps.append(abs(mi - mj) / max(pooled_std, 1e-9))
    moment_separation = sum(seps) / len(seps) if seps else 0.0
    print(f"\n  moment_separation (mean-distance / pooled_std) = {moment_separation:.3f}", flush=True)
    summary = {"moment_separation": moment_separation, "phase_moments": phase_moments,
               "phase_names": phase_names}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic()-t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, cfg


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict":verdict,"verdict_msg":msg,"elapsed_s":elapsed,"summary":summary,"config":config}
    validate_metrics(metrics)
    tmp = out_dir/"metrics.json.tmp"; tmp.write_text(json.dumps(metrics,indent=2,default=float)); tmp.replace(out_dir/"metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14_pq_shape_introspection_v1_smoke")
    s,v,m,e,c = run_experiment(smoke=True)
    oracle.assert_baseline_high("sep_present", s["moment_separation"]+0.001, 0.0)
    write_metrics(out_dir,s,v,m,e,c); print(f"\nSMOKE OK: {v}",flush=True)


def run_main():
    out_dir = get_output_dir("wave14_pq_shape_introspection_v1")
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
