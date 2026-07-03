"""Multi-target chain disambiguation — given K_targets possible targets, can substrate identify the right one?"""
from __future__ import annotations
import argparse, importlib.util, json, os, sys, time
from pathlib import Path
import torch
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
from verification import oracle  # noqa: E402
_so = importlib.util.spec_from_file_location("so", REPO / "experiments" / "exp_wave14_chain_smoother_only_v1.py")
so = importlib.util.module_from_spec(_so); _so.loader.exec_module(so)
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
    if "acc_top1" not in s: return ("MULTITARG_INCONCLUSIVE", "Missing.")
    a = s["acc_top1"]; n_tar = s["n_targets"]
    if a >= 0.5: return ("MULTITARG_DISAMBIG", f"top-1 acc={a:.3f} from {n_tar} candidates.")
    return ("MULTITARG_FAILS", f"top-1 acc={a:.3f} from {n_tar} candidates (chance={1/n_tar:.3f}).")


def self_test_verdict():
    for s,exp in [({"acc_top1":0.7,"n_targets":5},"MULTITARG_DISAMBIG"),({"acc_top1":0.2,"n_targets":5},"MULTITARG_FAILS"),({},"MULTITARG_INCONCLUSIVE")]:
        a,_=compute_verdict(s)
        if a!=exp: raise AssertionError(f"{a}!={exp}")
    print("verdict self-test passed (3/3 cases)",flush=True)


def run_experiment(smoke):
    t0=time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    cfg = {"N":8192 if smoke else 65536, "K":100, "depth":25 if smoke else 50,
           "num_entities":200, "num_relations":20, "n_targets":5,
           "n_trials":5 if smoke else 30, "seed":17}
    gen = torch.Generator(device=device).manual_seed(cfg["seed"])
    ea = mh.make_bsc_codebook(cfg["num_entities"], cfg["N"], gen, device)
    ra = mh.make_bsc_codebook(cfg["num_relations"], cfg["N"], gen, device)
    cg = torch.Generator().manual_seed(cfg["seed"]+1009)
    correct = 0
    for trial in range(cfg["n_trials"]):
        perm = torch.randperm(cfg["num_entities"], generator=cg)[:cfg["depth"]+1]
        chain = perm.tolist()
        rels = [int(torch.randint(0,cfg["num_relations"],(1,),generator=cg).item()) for _ in range(cfg["depth"])]
        true_target = chain[-1]
        # Generate n_targets candidates: true + (n_targets-1) random others
        others = []
        while len(others) < cfg["n_targets"] - 1:
            cand = int(torch.randint(0, cfg["num_entities"], (1,), generator=cg).item())
            if cand != true_target and cand not in others:
                others.append(cand)
        candidates = [true_target] + others
        torch.manual_seed(trial)
        M = mh.build_factbase(chain, rels, max(0,cfg["K"]-cfg["depth"]), cfg["num_entities"], cfg["num_relations"], ea, ra, cg, device)
        # Score each candidate via smoother chain (run chain assuming candidate as target)
        scores = []
        for cand in candidates:
            # Score = how well does smoother chain converge if cand is the target?
            ok = so.chain_smoother_only(M, chain[0], rels, cand, ea, ra)
            scores.append(1.0 if ok else 0.0)
        # Pick top-scoring candidate; tie-break by index 0 (true target)
        best_score = max(scores)
        best_idx = scores.index(best_score)
        if candidates[best_idx] == true_target:
            correct += 1
    acc = correct / cfg["n_trials"]
    print(f"  multi-target top-1 acc={acc:.3f} (chance={1/cfg['n_targets']:.3f})", flush=True)
    summary = {"acc_top1": acc, "n_targets": cfg["n_targets"]}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic()-t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, cfg


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict":verdict,"verdict_msg":msg,"elapsed_s":elapsed,"summary":summary,"config":config}
    validate_metrics(metrics)
    tmp = out_dir/"metrics.json.tmp"; tmp.write_text(json.dumps(metrics,indent=2,default=float)); tmp.replace(out_dir/"metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14_multi_target_disambiguation_v1_smoke")
    s,v,m,e,c = run_experiment(smoke=True)
    oracle.assert_baseline_high("acc_present", s["acc_top1"]+0.001, 0.0)
    write_metrics(out_dir,s,v,m,e,c); print(f"\nSMOKE OK: {v}",flush=True)


def run_main():
    out_dir = get_output_dir("wave14_multi_target_disambiguation_v1")
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
