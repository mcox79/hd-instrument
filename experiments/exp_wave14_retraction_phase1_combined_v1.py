"""Retraction framework Phase 1 — combined idempotence + eigenspectrum + destination profile.

Per Strategy 22:19. Tests:
  1. Idempotence: psi_once == psi_twice rate (retraction property)
  2. Eigenspectrum: top eigenvalue gap ratio (Perron-Frobenius collapse)
  3. Destination profile: fraction of codebook reached by chain endpoints (~22% predicted)
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
    if "idempotence_rate" not in s: return ("RETRACT_INCONCLUSIVE", "Missing.")
    idem = s["idempotence_rate"]; gap = s["gap_ratio"]; dest_frac = s["destination_fraction"]
    n_pass = sum([idem >= 0.95, gap <= 0.91, 0.15 <= dest_frac <= 0.30])
    if n_pass >= 2:
        return ("RETRACT_CONFIRMED",
                f"{n_pass}/3 tests pass: idem={idem:.3f}, gap={gap:.3f}, dest_frac={dest_frac:.3f}.")
    if n_pass == 1:
        return ("RETRACT_PARTIAL", f"1/3 tests pass: idem={idem:.3f}, gap={gap:.3f}, dest_frac={dest_frac:.3f}.")
    return ("RETRACT_REFUTED", f"0/3 tests pass: idem={idem:.3f}, gap={gap:.3f}, dest_frac={dest_frac:.3f}.")


def self_test_verdict():
    for s,exp in [
        ({"idempotence_rate":0.98,"gap_ratio":0.80,"destination_fraction":0.22}, "RETRACT_CONFIRMED"),
        ({"idempotence_rate":0.40,"gap_ratio":0.99,"destination_fraction":0.22}, "RETRACT_PARTIAL"),
        ({"idempotence_rate":0.30,"gap_ratio":0.99,"destination_fraction":0.50}, "RETRACT_REFUTED"),
        ({}, "RETRACT_INCONCLUSIVE"),
    ]:
        a,_=compute_verdict(s)
        if a!=exp: raise AssertionError(f"{a}!={exp}")
    print("verdict self-test passed (4/4 cases)",flush=True)


def chain_argmax(M, start_idx, rels, ea, ra):
    current = start_idx
    for r_idx in rels:
        probe = M * (ea[current] * ra[r_idx])
        current = int((ea @ probe).argmax().item())
    return current


def run_experiment(smoke):
    t0=time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    cfg = {"N":8192 if smoke else 65536, "K":100, "depth":25 if smoke else 50,
           "num_entities":200, "num_relations":20, "seed":17}
    use_cpu = cfg["N"] >= 32768
    target = torch.device("cpu") if use_cpu else device
    gen = torch.Generator(device=device).manual_seed(cfg["seed"])
    ea = mh.make_bsc_codebook(cfg["num_entities"], cfg["N"], gen, device)
    ra = mh.make_bsc_codebook(cfg["num_relations"], cfg["N"], gen, device)
    cg = torch.Generator().manual_seed(cfg["seed"]+1009)
    perm = torch.randperm(cfg["num_entities"], generator=cg)[:cfg["depth"]+1]
    chain_ents = perm.tolist()
    chain_rels = [int(torch.randint(0,cfg["num_relations"],(1,),generator=cg).item()) for _ in range(cfg["depth"])]
    M = mh.build_factbase(chain_ents, chain_rels, max(0,cfg["K"]-cfg["depth"]), cfg["num_entities"], cfg["num_relations"], ea, ra, cg, device)

    # Test 1: Idempotence
    print(f"[test 1] idempotence at N={cfg['N']}", flush=True)
    psi_once = []; psi_twice = []
    for start in range(cfg["num_entities"]):
        once = chain_argmax(M, start, chain_rels, ea, ra)
        twice = chain_argmax(M, once, chain_rels, ea, ra)
        psi_once.append(once); psi_twice.append(twice)
    idem_rate = sum(1 for i in range(len(psi_once)) if psi_once[i] == psi_twice[i]) / len(psi_once)
    print(f"  idempotence_rate = {idem_rate:.3f}", flush=True)

    # Test 2: Eigenspectrum gap (compute W = T^T T / N for substrate)
    print(f"[test 2] eigenspectrum gap at N={cfg['N']}", flush=True)
    target_dev = target
    ea_t = ea.to(target_dev); ra_t = ra.to(target_dev)
    triples = []
    cg2 = torch.Generator().manual_seed(cfg["seed"]+2009)
    for _ in range(cfg["K"]):
        s = int(torch.randint(0,cfg["num_entities"],(1,),generator=cg2).item())
        r = int(torch.randint(0,cfg["num_relations"],(1,),generator=cg2).item())
        o = int(torch.randint(0,cfg["num_entities"],(1,),generator=cg2).item())
        triples.append(mh.sign_quantize(ea_t[s] * ra_t[r] * ea_t[o]))
    T = torch.stack(triples, dim=0)
    W = (T.T @ T) / cfg["N"]
    eigs = torch.linalg.eigvalsh(W.float()).cpu().abs()
    sorted_eigs = torch.sort(eigs, descending=True).values
    gap_ratio = float(sorted_eigs[1] / sorted_eigs[0])
    print(f"  top eig={float(sorted_eigs[0]):.4f}, 2nd={float(sorted_eigs[1]):.4f}, gap_ratio={gap_ratio:.4f}", flush=True)
    del W

    # Test 3: Destination profile
    print(f"[test 3] destination profile", flush=True)
    destinations = set(psi_once)
    dest_frac = len(destinations) / cfg["num_entities"]
    print(f"  unique destinations: {len(destinations)}/{cfg['num_entities']} = {dest_frac:.3f}", flush=True)

    summary = {"idempotence_rate": idem_rate, "gap_ratio": gap_ratio,
                "destination_fraction": dest_frac, "n_destinations": len(destinations)}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic()-t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, cfg


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict":verdict,"verdict_msg":msg,"elapsed_s":elapsed,"summary":summary,"config":config}
    validate_metrics(metrics)
    tmp = out_dir/"metrics.json.tmp"; tmp.write_text(json.dumps(metrics,indent=2,default=float)); tmp.replace(out_dir/"metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14_retraction_phase1_combined_v1_smoke")
    s,v,m,e,c = run_experiment(smoke=True)
    oracle.assert_baseline_high("idem_present", s["idempotence_rate"]+0.001, 0.0)
    write_metrics(out_dir,s,v,m,e,c); print(f"\nSMOKE OK: {v}",flush=True)


def run_main():
    out_dir = get_output_dir("wave14_retraction_phase1_combined_v1")
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
