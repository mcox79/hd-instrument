"""VAMP-on-chain vs backward-smoother head-to-head — Strategy 06:33 P4."""
from __future__ import annotations
import argparse, importlib.util, json, os, sys, time
from pathlib import Path
import torch
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from verification import oracle  # noqa: E402
_so = importlib.util.spec_from_file_location("so", REPO / "experiments" / "exp_wave14_chain_smoother_only_v1.py")
so = importlib.util.module_from_spec(_so); _so.loader.exec_module(so)
_vc = importlib.util.spec_from_file_location("vc", REPO / "experiments" / "exp_wave14_multihop_vamp_chain_N65536_v1.py")
vc = importlib.util.module_from_spec(_vc); _vc.loader.exec_module(vc)
_mh = importlib.util.spec_from_file_location("mh", REPO / "experiments" / "exp_wave14r_multihop_K100.py")
mh = importlib.util.module_from_spec(_mh); _mh.loader.exec_module(mh)


def get_output_dir(name):
    n = os.environ.get("HDLAB_EXP_NAME", name)
    out = REPO / "data" / f"exp_{n}"; out.mkdir(parents=True, exist_ok=True); return out


def validate_metrics(d):
    if not {"verdict","verdict_msg","elapsed_s","summary","config"}.issubset(d.keys()): raise ValueError("missing")


def compute_verdict(s):
    if "smoother_mean" not in s: return ("HTH_INCONCLUSIVE", "Missing.")
    sm = s["smoother_mean"]; vm = s["vamp_mean"]
    if sm >= 0.95 and vm >= 0.95:
        return ("HEADTOHEAD_EQUIVALENT", f"both >=0.95: smoother={sm:.3f}, vamp={vm:.3f}.")
    if sm > vm + 0.10:
        return ("HEADTOHEAD_SMOOTHER_BETTER", f"smoother={sm:.3f}, vamp={vm:.3f}.")
    if vm > sm + 0.10:
        return ("HEADTOHEAD_VAMP_BETTER", f"vamp={vm:.3f}, smoother={sm:.3f}.")
    return ("HEADTOHEAD_CONFIG_SPLIT", f"smoother={sm:.3f}, vamp={vm:.3f}.")


def self_test_verdict():
    for s,exp in [
        ({"smoother_mean":0.98,"vamp_mean":0.98},"HEADTOHEAD_EQUIVALENT"),
        ({"smoother_mean":0.95,"vamp_mean":0.5},"HEADTOHEAD_SMOOTHER_BETTER"),
        ({"smoother_mean":0.5,"vamp_mean":0.95},"HEADTOHEAD_VAMP_BETTER"),
        ({"smoother_mean":0.7,"vamp_mean":0.75},"HEADTOHEAD_CONFIG_SPLIT"),
        ({},"HTH_INCONCLUSIVE"),
    ]:
        a,_=compute_verdict(s)
        if a!=exp: raise AssertionError(f"{a}!={exp}")
    print("verdict self-test passed (5/5 cases)",flush=True)


def run_experiment(smoke):
    t0=time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    cfg = {"N":8192 if smoke else 65536,
           "configs":[("K100","d25",100,25),("K500","d50",500,50)] if smoke else
                     [("K100","d50",100,50),("K500","d50",500,50),("K1000","d50",1000,50),("K100","d100",100,100),("K100","d25",100,25)],
           "num_relations":20, "n_trials":5 if smoke else 25, "seed":17}
    sm_accs = []; vm_accs = []
    for tag1, tag2, K, d in cfg["configs"]:
        nent = max(K, d+10)
        gen = torch.Generator(device=device).manual_seed(cfg["seed"]+K+d)
        ea = mh.make_bsc_codebook(nent, cfg["N"], gen, device)
        ra = mh.make_bsc_codebook(cfg["num_relations"], cfg["N"], gen, device)
        cg = torch.Generator().manual_seed(cfg["seed"]+K+d+1009)
        sm_correct = 0; vm_correct = 0
        for tr in range(cfg["n_trials"]):
            perm = torch.randperm(nent, generator=cg)[:d+1]
            ch = perm.tolist()
            rels = [int(torch.randint(0,cfg["num_relations"],(1,),generator=cg).item()) for _ in range(d)]
            M = mh.build_factbase(ch, rels, max(0,K-d), nent, cfg["num_relations"], ea, ra, cg, device)
            if so.chain_smoother_only(M, ch[0], rels, ch[-1], ea, ra): sm_correct += 1
            if vc.vamp_chain_forward_backward(M, ch[0], rels, ch[-1], ea, ra): vm_correct += 1
        sm_acc = sm_correct / cfg["n_trials"]; vm_acc = vm_correct / cfg["n_trials"]
        sm_accs.append(sm_acc); vm_accs.append(vm_acc)
        print(f"  {tag1}_{tag2}: smoother={sm_acc:.3f}, vamp={vm_acc:.3f}", flush=True)
    sm_mean = sum(sm_accs)/len(sm_accs); vm_mean = sum(vm_accs)/len(vm_accs)
    summary = {"smoother_mean": sm_mean, "vamp_mean": vm_mean,
                "smoother_per_config": sm_accs, "vamp_per_config": vm_accs}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic()-t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, cfg


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict":verdict,"verdict_msg":msg,"elapsed_s":elapsed,"summary":summary,"config":config}
    validate_metrics(metrics)
    tmp = out_dir/"metrics.json.tmp"; tmp.write_text(json.dumps(metrics,indent=2,default=float)); tmp.replace(out_dir/"metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14_vamp_vs_smoother_head_to_head_v1_smoke")
    s,v,m,e,c = run_experiment(smoke=True)
    oracle.assert_baseline_high("smoother_present", s["smoother_mean"]+0.001, 0.0)
    write_metrics(out_dir,s,v,m,e,c); print(f"\nSMOKE OK: {v}",flush=True)


def run_main():
    out_dir = get_output_dir("wave14_vamp_vs_smoother_head_to_head_v1")
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
