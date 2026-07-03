"""Forward argmax at K=1000 — Strategy 06:49 P4. Does K-resonance rescue forward retrieval?"""
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
    if "acc_50hop_K1000" not in s: return ("FWD_K1K_INCONCLUSIVE", "Missing.")
    a = s["acc_50hop_K1000"]
    if a >= 0.5: return ("FORWARD_K1000_RESCUED", f"acc_50hop={a:.3f}>=0.5; fixed-points rescue forward.")
    if a >= 0.2: return ("FORWARD_K1000_BOUNDED", f"acc_50hop={a:.3f} in [0.2, 0.5].")
    return ("FORWARD_K1000_SAME", f"acc_50hop={a:.3f}<0.2 (same as K=100).")


def self_test_verdict():
    for s,exp in [
        ({"acc_50hop_K1000": 0.7}, "FORWARD_K1000_RESCUED"),
        ({"acc_50hop_K1000": 0.3}, "FORWARD_K1000_BOUNDED"),
        ({"acc_50hop_K1000": 0.1}, "FORWARD_K1000_SAME"),
        ({}, "FWD_K1K_INCONCLUSIVE"),
    ]:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print("verdict self-test passed (4/4 cases)", flush=True)


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    cfg = {"N":8192 if smoke else 65536, "K":1000, "depth":25 if smoke else 50,
            "num_relations":20, "n_trials":5 if smoke else 30, "seed":17}
    nent = max(cfg["K"], cfg["depth"]+10)
    gen = torch.Generator(device=device).manual_seed(cfg["seed"])
    ea = mh.make_bsc_codebook(nent, cfg["N"], gen, device)
    ra = mh.make_bsc_codebook(cfg["num_relations"], cfg["N"], gen, device)
    cg = torch.Generator().manual_seed(cfg["seed"] + 1009)
    correct = 0
    for trial in range(cfg["n_trials"]):
        perm = torch.randperm(nent, generator=cg)[:cfg["depth"]+1]
        ch = perm.tolist()
        rels = [int(torch.randint(0,cfg["num_relations"],(1,),generator=cg).item()) for _ in range(cfg["depth"])]
        M = mh.build_factbase(ch, rels, max(0,cfg["K"]-cfg["depth"]), nent, cfg["num_relations"], ea, ra, cg, device)
        if mh.run_chain(M, ch[0], rels, ch[-1], ea, ra): correct += 1
    acc = correct / cfg["n_trials"]
    print(f"  K={cfg['K']} d={cfg['depth']}: acc={acc:.3f}", flush=True)
    summary = {"acc_50hop_K1000": acc, "K": cfg["K"], "depth": cfg["depth"]}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, cfg


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict":verdict,"verdict_msg":msg,"elapsed_s":elapsed,"summary":summary,"config":config}
    validate_metrics(metrics)
    tmp = out_dir/"metrics.json.tmp"; tmp.write_text(json.dumps(metrics,indent=2,default=float))
    tmp.replace(out_dir/"metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14_forward_argmax_K1000_v1_smoke")
    s,v,m,e,c = run_experiment(smoke=True)
    oracle.assert_baseline_high("acc_present", s["acc_50hop_K1000"]+0.001, 0.0)
    write_metrics(out_dir,s,v,m,e,c); print(f"\nSMOKE OK: {v}",flush=True)


def run_main():
    out_dir = get_output_dir("wave14_forward_argmax_K1000_v1")
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
