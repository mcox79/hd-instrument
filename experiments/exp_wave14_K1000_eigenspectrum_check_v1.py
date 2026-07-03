"""K=1000 eigenspectrum check — Strategy 07:05 Priority A. Arnold-tongue test."""
from __future__ import annotations
import argparse, importlib.util, json, os, sys, time
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
    if "ratio_2_to_1" not in s: return ("K1K_EIG_INCONCLUSIVE", "Missing.")
    r = s["ratio_2_to_1"]
    rationals = [(1,2),(2,3),(1,3),(3,4),(1,4),(3,5),(2,5)]
    for m, n in rationals:
        if abs(r - m/n) < 0.01:
            return ("K1000_RATIONAL_COMMENSURABLE", f"ratio={r:.4f} matches {m}/{n}={m/n:.4f} (within 0.01).")
    closest = min(rationals, key=lambda p: abs(r - p[0]/p[1]))
    if abs(r - closest[0]/closest[1]) < 0.05:
        return ("K1000_IRRATIONAL_NEAR", f"ratio={r:.4f} within 0.05 of {closest[0]}/{closest[1]} but not 0.01.")
    return ("K1000_IRRATIONAL_FAR", f"ratio={r:.4f} not near any tested rational.")


def self_test_verdict():
    for s,exp in [
        ({"ratio_2_to_1":0.500},"K1000_RATIONAL_COMMENSURABLE"),
        ({"ratio_2_to_1":0.520},"K1000_IRRATIONAL_NEAR"),
        ({"ratio_2_to_1":0.123},"K1000_IRRATIONAL_FAR"),
        ({},"K1K_EIG_INCONCLUSIVE"),
    ]:
        a,_=compute_verdict(s)
        if a!=exp: raise AssertionError(f"{a}!={exp}")
    print("verdict self-test passed (4/4 cases)",flush=True)


def run_experiment(smoke):
    t0=time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    cfg = {"N":4096 if smoke else 65536, "K":1000, "num_entities":1010, "num_relations":20, "seed":17}
    use_cpu = cfg["N"] >= 32768
    target = torch.device("cpu") if use_cpu else device
    cpu_gen = torch.Generator().manual_seed(cfg["seed"])
    gen = torch.Generator(device=device).manual_seed(cfg["seed"])
    ea = mh.make_bsc_codebook(cfg["num_entities"], cfg["N"], gen, device).to(target)
    ra = mh.make_bsc_codebook(cfg["num_relations"], cfg["N"], gen, device).to(target)
    # Build W = T^T T / N where T = K stored triples
    triples = []
    for _ in range(cfg["K"]):
        s = int(torch.randint(0, cfg["num_entities"], (1,), generator=cpu_gen))
        r = int(torch.randint(0, cfg["num_relations"], (1,), generator=cpu_gen))
        o = int(torch.randint(0, cfg["num_entities"], (1,), generator=cpu_gen))
        triples.append(mh.sign_quantize(ea[s] * ra[r] * ea[o]))
    T = torch.stack(triples, dim=0)
    print(f"[setup] W = T.T @ T / N at N={cfg['N']} K={cfg['K']} on {target}", flush=True)
    W = (T.T @ T) / cfg["N"]
    eigs = torch.linalg.eigvalsh(W.float()).cpu().abs()
    sorted_eigs = torch.sort(eigs, descending=True).values
    top10 = sorted_eigs[:10].tolist()
    print(f"  top10 eigenvalues: {[round(e,4) for e in top10]}", flush=True)
    ratio = float(sorted_eigs[1] / sorted_eigs[0])
    print(f"  lambda_2/lambda_1 = {ratio:.6f}", flush=True)
    summary = {"top10_eigenvalues": top10, "ratio_2_to_1": ratio,
                "lambda_1": float(sorted_eigs[0]), "lambda_2": float(sorted_eigs[1])}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic()-t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, cfg


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict":verdict,"verdict_msg":msg,"elapsed_s":elapsed,"summary":summary,"config":config}
    validate_metrics(metrics)
    tmp = out_dir/"metrics.json.tmp"; tmp.write_text(json.dumps(metrics,indent=2,default=float)); tmp.replace(out_dir/"metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14_K1000_eigenspectrum_check_v1_smoke")
    s,v,m,e,c = run_experiment(smoke=True)
    oracle.assert_baseline_high("ratio_present", s["ratio_2_to_1"]+0.001, 0.0)
    write_metrics(out_dir,s,v,m,e,c); print(f"\nSMOKE OK: {v}",flush=True)


def run_main():
    out_dir = get_output_dir("wave14_K1000_eigenspectrum_check_v1")
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
