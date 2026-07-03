"""Endpoint RM(1,16) projection — Strategy 09:45 PRIORITY C.

Research hypothesis: ~25% of terminal endpoints fall inside RM(1,16) subcode
(Hamming radius d/2 = 2^15). Use Walsh-Hadamard transform to project each
endpoint onto the nearest RM(1,m) codeword and count fraction within d/2.
"""
from __future__ import annotations
import argparse, importlib.util, json, math, os, sys, time
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
    if "frac_within_d_half" not in s: return ("RM1M_INCONCLUSIVE", "Missing.")
    f = s["frac_within_d_half"]
    if 0.15 <= f <= 0.35: return ("RM1M_25_PASS", f"frac_within_d/2={f:.3f} in [0.15, 0.35] (~25% RM(1,16) hypothesis confirmed).")
    if f < 0.15: return ("RM1M_FAIL_LOW", f"frac_within_d/2={f:.3f}<0.15 (substrate avoids RM(1,16)).")
    return ("RM1M_FAIL_HIGH", f"frac_within_d/2={f:.3f}>0.35 (substrate concentrates on RM(1,16) more than 25%).")


def self_test_verdict():
    for s,exp in [
        ({"frac_within_d_half":0.25},"RM1M_25_PASS"),
        ({"frac_within_d_half":0.05},"RM1M_FAIL_LOW"),
        ({"frac_within_d_half":0.5},"RM1M_FAIL_HIGH"),
        ({},"RM1M_INCONCLUSIVE"),
    ]:
        a,_=compute_verdict(s)
        if a!=exp: raise AssertionError(f"{a}!={exp}")
    print("verdict self-test passed (4/4 cases)",flush=True)


def fwht_batched(X):
    """In-place batched Fast Walsh-Hadamard Transform over last dim.
    X shape (B, N) where N must be power of 2. Returns transformed X.
    """
    N = X.shape[-1]
    h = 1
    while h < N:
        # Pair up adjacent blocks of size h
        X = X.view(*X.shape[:-1], -1, 2 * h)
        a = X[..., :h].clone()
        b = X[..., h:2*h].clone()
        X[..., :h] = a + b
        X[..., h:2*h] = a - b
        X = X.view(*X.shape[:-2], N)
        h *= 2
    return X


def measure_endpoints(W, num_codewords, depth, ea, ra, chain_rels, n_starts, device):
    """For n_starts codewords, run forward chain to depth; return endpoint vectors."""
    endpoints = []
    M = W
    for start_idx in range(min(n_starts, ea.shape[0])):
        current = start_idx
        for r_idx in chain_rels:
            current = int((ea @ (M * (ea[current] * ra[r_idx]))).argmax().item())
        endpoints.append(ea[current])
    return torch.stack(endpoints, dim=0)


def run_experiment(smoke):
    t0=time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    cfg = {"N":4096 if smoke else 65536, "K":100, "depth":25 if smoke else 50,
           "num_entities":1000 if smoke else 1000, "num_relations":20,
           "n_starts":200 if smoke else 1000, "n_seeds":2 if smoke else 3}
    if (cfg["N"] & (cfg["N"]-1)) != 0:
        raise ValueError(f"N={cfg['N']} must be power of 2 for FWHT")
    threshold = cfg["N"] // 2  # max|H[y]| >= N/2 means within Hamming d/2 of nearest RM(1,m)
    frac_per_seed = []
    for seed_i in range(cfg["n_seeds"]):
        seed = 17 + seed_i * 101
        gen = torch.Generator(device=device).manual_seed(seed)
        ea = mh.make_bsc_codebook(cfg["num_entities"], cfg["N"], gen, device)
        ra = mh.make_bsc_codebook(cfg["num_relations"], cfg["N"], gen, device)
        cg = torch.Generator().manual_seed(seed + 1009)
        perm = torch.randperm(cfg["num_entities"], generator=cg)[:cfg["depth"]+1]
        chain_rels = [int(torch.randint(0,cfg["num_relations"],(1,),generator=cg).item()) for _ in range(cfg["depth"])]
        M = mh.build_factbase(perm.tolist(), chain_rels, max(0,cfg["K"]-cfg["depth"]),
                              cfg["num_entities"], cfg["num_relations"], ea, ra, cg, device)
        endpoints = measure_endpoints(M, cfg["num_entities"], cfg["depth"], ea, ra,
                                      chain_rels, cfg["n_starts"], device)
        # Walsh-Hadamard transform of endpoints (batched)
        H = fwht_batched(endpoints.clone().float())
        max_inner = H.abs().max(dim=-1).values  # max over Walsh basis: this is max inner product to RM(1,m) codeword
        within = (max_inner >= threshold).sum().item()
        frac = within / cfg["n_starts"]
        frac_per_seed.append(frac)
        max_mean = float(max_inner.mean().item())
        print(f"  seed={seed}: frac_within_d/2={frac:.4f} mean_max_inner={max_mean:.1f}/N={cfg['N']}", flush=True)
    frac_mean = sum(frac_per_seed) / len(frac_per_seed)
    print(f"\n  mean frac_within_d/2 across {len(frac_per_seed)} seeds = {frac_mean:.4f}", flush=True)
    summary = {"frac_within_d_half": frac_mean, "frac_per_seed": frac_per_seed,
               "N": cfg["N"], "threshold": threshold}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic()-t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, cfg


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict":verdict,"verdict_msg":msg,"elapsed_s":elapsed,"summary":summary,"config":config}
    validate_metrics(metrics)
    tmp = out_dir/"metrics.json.tmp"; tmp.write_text(json.dumps(metrics,indent=2,default=float)); tmp.replace(out_dir/"metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14_endpoint_RM1m_projection_v1_smoke")
    s,v,m,e,c = run_experiment(smoke=True)
    oracle.assert_baseline_high("frac_present", s["frac_within_d_half"]+0.001, 0.0)
    write_metrics(out_dir,s,v,m,e,c); print(f"\nSMOKE OK: {v}",flush=True)


def run_main():
    out_dir = get_output_dir("wave14_endpoint_RM1m_projection_v1")
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
