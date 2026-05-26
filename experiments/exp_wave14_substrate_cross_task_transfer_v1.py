"""Substrate cross-task transfer — multiple chains stored simultaneously in one bundle."""
from __future__ import annotations
import argparse, importlib.util, json, os, sys, time
from pathlib import Path
import torch
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from verification import oracle  # noqa: E402
_so = importlib.util.spec_from_file_location("so", REPO / "experiments" / "exp_wave14_chain_smoother_only_v1.py")
so = importlib.util.module_from_spec(_so); _so.loader.exec_module(so)
_mh = importlib.util.spec_from_file_location("mh", REPO / "experiments" / "exp_wave14r_multihop_K100.py")
mh = importlib.util.module_from_spec(_mh); _mh.loader.exec_module(mh)


def get_output_dir(name):
    n = os.environ.get("HDLAB_EXP_NAME", name)
    out = REPO / "data" / f"exp_{n}"; out.mkdir(parents=True, exist_ok=True); return out


def validate_metrics(d):
    if not {"verdict","verdict_msg","elapsed_s","summary","config"}.issubset(d.keys()): raise ValueError("missing")


def compute_verdict(s):
    if "acc_multi_task" not in s: return ("CROSSTASK_INCONCLUSIVE", "Missing.")
    a = s["acc_multi_task"]; b = s["acc_single_task"]
    if a >= 0.5 and a >= b * 0.7:
        return ("CROSSTASK_TRANSFERS", f"multi={a:.3f} (>=0.5 AND >=70% of single={b:.3f}).")
    if a >= 0.3:
        return ("CROSSTASK_PARTIAL", f"multi={a:.3f} vs single={b:.3f}.")
    return ("CROSSTASK_INTERFERES", f"multi={a:.3f} vs single={b:.3f}.")


def self_test_verdict():
    for s,exp in [({"acc_multi_task":0.8,"acc_single_task":1.0},"CROSSTASK_TRANSFERS"),({"acc_multi_task":0.4,"acc_single_task":1.0},"CROSSTASK_PARTIAL"),({"acc_multi_task":0.1,"acc_single_task":1.0},"CROSSTASK_INTERFERES"),({},"CROSSTASK_INCONCLUSIVE")]:
        a,_=compute_verdict(s)
        if a!=exp: raise AssertionError(f"{a}!={exp}")
    print("verdict self-test passed (4/4 cases)",flush=True)


def run_experiment(smoke):
    t0=time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    cfg = {"N":8192 if smoke else 65536, "K":100, "depth":25 if smoke else 50,
           "n_chains":3, "num_entities":400, "num_relations":20,
           "n_trials":5 if smoke else 15, "seed":17}
    gen = torch.Generator(device=device).manual_seed(cfg["seed"])
    ea = mh.make_bsc_codebook(cfg["num_entities"], cfg["N"], gen, device)
    ra = mh.make_bsc_codebook(cfg["num_relations"], cfg["N"], gen, device)
    cg = torch.Generator().manual_seed(cfg["seed"]+1009)
    # Single-task baseline
    correct_single = 0
    for trial in range(cfg["n_trials"]):
        perm = torch.randperm(cfg["num_entities"], generator=cg)[:cfg["depth"]+1]
        chain = perm.tolist()
        rels = [int(torch.randint(0,cfg["num_relations"],(1,),generator=cg).item()) for _ in range(cfg["depth"])]
        M = mh.build_factbase(chain, rels, max(0,cfg["K"]-cfg["depth"]), cfg["num_entities"], cfg["num_relations"], ea, ra, cg, device)
        if so.chain_smoother_only(M, chain[0], rels, chain[-1], ea, ra): correct_single += 1
    acc_single = correct_single / cfg["n_trials"]
    # Multi-task: store n_chains chains in ONE bundle M; test each
    correct_multi = 0; total = 0
    for trial in range(cfg["n_trials"]):
        chains = []
        all_facts = []
        for _ in range(cfg["n_chains"]):
            perm = torch.randperm(cfg["num_entities"], generator=cg)[:cfg["depth"]+1]
            chain = perm.tolist()
            rels = [int(torch.randint(0,cfg["num_relations"],(1,),generator=cg).item()) for _ in range(cfg["depth"])]
            chains.append((chain, rels))
            # Add facts from this chain
            for i in range(len(rels)):
                all_facts.append((chain[i], rels[i], chain[i+1]))
        # Add distractors to fill up to K total facts
        n_d = max(0, cfg["K"] - len(all_facts))
        triples = [mh.sign_quantize(ea[s] * ra[r] * ea[o]) for s,r,o in all_facts]
        for _ in range(n_d):
            s_i = int(torch.randint(0,cfg["num_entities"],(1,),generator=cg).item())
            r_i = int(torch.randint(0,cfg["num_relations"],(1,),generator=cg).item())
            o_i = int(torch.randint(0,cfg["num_entities"],(1,),generator=cg).item())
            triples.append(mh.sign_quantize(ea[s_i] * ra[r_i] * ea[o_i]))
        M = mh.sign_quantize(torch.stack(triples, dim=0).sum(dim=0))
        # Test each chain
        for chain, rels in chains:
            if so.chain_smoother_only(M, chain[0], rels, chain[-1], ea, ra): correct_multi += 1
            total += 1
    acc_multi = correct_multi / total
    print(f"  single-task acc={acc_single:.3f}, multi-task acc={acc_multi:.3f}", flush=True)
    summary = {"acc_single_task": acc_single, "acc_multi_task": acc_multi, "n_chains": cfg["n_chains"]}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic()-t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, cfg


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict":verdict,"verdict_msg":msg,"elapsed_s":elapsed,"summary":summary,"config":config}
    validate_metrics(metrics)
    tmp = out_dir/"metrics.json.tmp"; tmp.write_text(json.dumps(metrics,indent=2,default=float)); tmp.replace(out_dir/"metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14_substrate_cross_task_transfer_v1_smoke")
    s,v,m,e,c = run_experiment(smoke=True)
    oracle.assert_baseline_high("acc_present", s["acc_single_task"]+0.001, 0.0)
    write_metrics(out_dir,s,v,m,e,c); print(f"\nSMOKE OK: {v}",flush=True)


def run_main():
    out_dir = get_output_dir("wave14_substrate_cross_task_transfer_v1")
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
