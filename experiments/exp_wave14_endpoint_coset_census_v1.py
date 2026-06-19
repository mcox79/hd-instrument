"""Endpoint coset census — Strategy 10:16 v152 add-1.

Given RM1M_FAIL_LOW (substrate AVOIDS RM(1,16) linear coset), measure distribution
across 4 anchor cosets. Since our substrate uses random BSC codebook (not Kerdock
structurally), use proxy: 4 anchor codewords representing different code structures.
Assign each endpoint to nearest anchor by Hamming distance.

Coset 1: RM(1,16) projection via FWHT (linear coset; substrate AVOIDS)
Coset 2-4: random nonlinear anchors (proxy for nonlinear Kerdock cosets)
"""
from __future__ import annotations
import argparse, importlib.util, json, os, sys, time
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
    if "coset_fractions" not in s: return ("COSET_INCONCLUSIVE", "Missing.")
    fracs = s["coset_fractions"]
    rm = fracs.get("rm1m", 0.0)
    nonlinear = [v for k, v in fracs.items() if k != "rm1m"]
    if rm < 0.05 and nonlinear:
        nl_max = max(nonlinear); nl_min = min(nonlinear)
        if nl_max > 0.5:
            return ("COSET_BIASED_NONLINEAR", f"frac={fracs}; one nonlinear coset >50% (biased).")
        if nl_max - nl_min < 0.1:
            return ("COSET_UNIFORM_NONLINEAR", f"frac={fracs}; nonlinear cosets roughly uniform.")
        return ("COSET_RM_AVOIDED", f"frac={fracs}; RM(1,16) avoided; nonlinear mixed.")
    return ("COSET_RM_PRESENT", f"frac={fracs}; substrate doesn't avoid RM(1,16) at this scale.")


def self_test_verdict():
    for s,exp in [
        ({"coset_fractions":{"rm1m":0.02,"a":0.33,"b":0.33,"c":0.32}},"COSET_UNIFORM_NONLINEAR"),
        ({"coset_fractions":{"rm1m":0.01,"a":0.7,"b":0.15,"c":0.14}},"COSET_BIASED_NONLINEAR"),
        ({"coset_fractions":{"rm1m":0.02,"a":0.50,"b":0.25,"c":0.23}},"COSET_RM_AVOIDED"),
        ({"coset_fractions":{"rm1m":0.20,"a":0.27,"b":0.27,"c":0.26}},"COSET_RM_PRESENT"),
        ({},"COSET_INCONCLUSIVE"),
    ]:
        a,_=compute_verdict(s)
        if a!=exp: raise AssertionError(f"{a}!={exp}")
    print("verdict self-test passed (5/5 cases)",flush=True)


def fwht_batched(X):
    N = X.shape[-1]
    h = 1
    while h < N:
        X = X.view(*X.shape[:-1], -1, 2 * h)
        a = X[..., :h].clone()
        b = X[..., h:2*h].clone()
        X[..., :h] = a + b
        X[..., h:2*h] = a - b
        X = X.view(*X.shape[:-2], N)
        h *= 2
    return X


def collect_endpoints(M, chain_rels, ea, ra, n_starts):
    endpoints = []
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
           "n_starts":200 if smoke else 1000, "n_seeds":2 if smoke else 3,
           "n_nonlinear_anchors":3}
    if (cfg["N"] & (cfg["N"]-1)) != 0:
        raise ValueError(f"N={cfg['N']} must be power of 2")
    threshold_rm = cfg["N"] // 2  # within d/2 of RM(1,16)
    coset_totals = {"rm1m": 0, "anchor1": 0, "anchor2": 0, "anchor3": 0, "none": 0}
    total_endpoints = 0
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
        endpoints = collect_endpoints(M, chain_rels, ea, ra, cfg["n_starts"])
        # Build nonlinear anchors (random BSC codewords; proxy for nonlinear cosets)
        anchor_gen = torch.Generator(device=device).manual_seed(seed + 31337)
        anchors = mh.make_bsc_codebook(cfg["n_nonlinear_anchors"], cfg["N"], anchor_gen, device)
        # FWHT distance to RM(1,16): max(|H[y]|) >= N/2 means within d/2
        H = fwht_batched(endpoints.clone().float())
        max_inner_rm = H.abs().max(dim=-1).values  # (n_starts,)
        within_rm = max_inner_rm >= threshold_rm
        # Hamming distance to anchors: closer = higher inner product
        inner_anchors = endpoints @ anchors.T  # (n_starts, n_anchors)
        # For each endpoint NOT in RM(1,16), assign to anchor with max inner product
        for i in range(endpoints.shape[0]):
            total_endpoints += 1
            if within_rm[i].item():
                coset_totals["rm1m"] += 1
            else:
                best = int(inner_anchors[i].argmax().item())
                coset_totals[f"anchor{best+1}"] += 1
        print(f"  seed={seed}: rm1m={within_rm.sum().item()}/{endpoints.shape[0]}", flush=True)
    fractions = {k: v/total_endpoints for k, v in coset_totals.items() if v > 0 or k == "rm1m"}
    # rename for verdict mapping
    fractions_for_verdict = {"rm1m": fractions.get("rm1m", 0.0)}
    for i in range(1, cfg["n_nonlinear_anchors"]+1):
        fractions_for_verdict[f"anchor{i}"] = fractions.get(f"anchor{i}", 0.0)
    print(f"\n  coset fractions across {total_endpoints} endpoints: {fractions}", flush=True)
    summary = {"coset_fractions": fractions_for_verdict, "total_endpoints": total_endpoints,
               "raw_totals": coset_totals}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic()-t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, cfg


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict":verdict,"verdict_msg":msg,"elapsed_s":elapsed,"summary":summary,"config":config}
    validate_metrics(metrics)
    tmp = out_dir/"metrics.json.tmp"; tmp.write_text(json.dumps(metrics,indent=2,default=float)); tmp.replace(out_dir/"metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14_endpoint_coset_census_v1_smoke")
    s,v,m,e,c = run_experiment(smoke=True)
    oracle.assert_baseline_high("totals_present", float(s["total_endpoints"])+0.001, 0.0)
    write_metrics(out_dir,s,v,m,e,c); print(f"\nSMOKE OK: {v}",flush=True)


def run_main():
    out_dir = get_output_dir("wave14_endpoint_coset_census_v1")
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
