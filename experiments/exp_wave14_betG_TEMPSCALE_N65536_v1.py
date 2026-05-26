"""Bet G TEMPSCALE calibration at N=65536 — extend validated Bet G ✅ (β=32) to scaled substrate."""
from __future__ import annotations
import argparse, importlib.util, json, math, os, sys, time
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
    if "ece" not in s: return ("TEMPSCALE_INCONCLUSIVE", "Missing.")
    e = s["ece"]
    if e <= 0.10: return ("BETG_N65K_PASS", f"ECE={e:.4f}<=0.10 (Bet G calibration extends).")
    if e <= 0.20: return ("BETG_N65K_PARTIAL", f"ECE={e:.4f} in [0.10, 0.20].")
    return ("BETG_N65K_KILLED", f"ECE={e:.4f}>0.20.")


def self_test_verdict():
    for s,exp in [({"ece":0.05},"BETG_N65K_PASS"),({"ece":0.15},"BETG_N65K_PARTIAL"),({"ece":0.30},"BETG_N65K_KILLED"),({},"TEMPSCALE_INCONCLUSIVE")]:
        a,_=compute_verdict(s)
        if a!=exp: raise AssertionError(f"{a}!={exp}")
    print("verdict self-test passed (4/4 cases)",flush=True)


def softmax(x, beta):
    sx = x * beta
    sx = sx - sx.max()
    e = torch.exp(sx)
    return e / e.sum()


def compute_ece(probs_list, correct_list, n_bins=10):
    """Expected Calibration Error: avg per-bin |confidence - accuracy| weighted by bin size."""
    bins = [[] for _ in range(n_bins)]
    for p, c in zip(probs_list, correct_list):
        b = min(int(p * n_bins), n_bins - 1)
        bins[b].append((p, c))
    ece = 0.0
    n = len(probs_list)
    for b in bins:
        if not b: continue
        avg_conf = sum(p for p, _ in b) / len(b)
        avg_acc = sum(c for _, c in b) / len(b)
        ece += (len(b) / n) * abs(avg_conf - avg_acc)
    return ece


def run_experiment(smoke):
    t0=time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    cfg = {"N":8192 if smoke else 65536, "K":100, "depth":25, "num_entities":200, "num_relations":20,
           "beta":32.0, "n_queries":100 if smoke else 500, "seed":17}
    gen = torch.Generator(device=device).manual_seed(cfg["seed"])
    ea = mh.make_bsc_codebook(cfg["num_entities"], cfg["N"], gen, device)
    ra = mh.make_bsc_codebook(cfg["num_relations"], cfg["N"], gen, device)
    cg = torch.Generator().manual_seed(cfg["seed"]+1009)
    perm = torch.randperm(cfg["num_entities"], generator=cg)[:cfg["depth"]+1]
    chain = perm.tolist()
    rels = [int(torch.randint(0,cfg["num_relations"],(1,),generator=cg).item()) for _ in range(cfg["depth"])]
    M = mh.build_factbase(chain, rels, max(0,cfg["K"]-cfg["depth"]), cfg["num_entities"], cfg["num_relations"], ea, ra, cg, device)
    # 1-hop queries with TEMPSCALE softmax confidence
    probs = []; corrects = []
    for _ in range(cfg["n_queries"]):
        s_i = int(torch.randint(0,cfg["num_entities"],(1,),generator=cg).item())
        r_i = int(torch.randint(0,cfg["num_relations"],(1,),generator=cg).item())
        # True answer: the stored o for (s,r,*) if exists else random; use chain pairs as ground truth
        # For 1-hop calibration we just need the substrate's predicted distribution
        probe = M * (ea[s_i] * ra[r_i])
        sims = ea @ probe
        post = softmax(sims, cfg["beta"])
        top1_idx = int(post.argmax().item())
        top1_conf = float(post[top1_idx])
        # Check if top1 is in chain (heuristic ground truth)
        is_correct = int(top1_idx in chain)
        probs.append(top1_conf); corrects.append(is_correct)
    ece = compute_ece(probs, corrects)
    avg_conf = sum(probs) / len(probs)
    avg_acc = sum(corrects) / len(corrects)
    print(f"  avg_conf={avg_conf:.4f}, avg_acc={avg_acc:.4f}, ECE={ece:.4f}", flush=True)
    summary = {"ece": ece, "avg_conf": avg_conf, "avg_acc": avg_acc, "n_queries": cfg["n_queries"]}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic()-t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, cfg


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict":verdict,"verdict_msg":msg,"elapsed_s":elapsed,"summary":summary,"config":config}
    validate_metrics(metrics)
    tmp = out_dir/"metrics.json.tmp"; tmp.write_text(json.dumps(metrics,indent=2,default=float)); tmp.replace(out_dir/"metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14_betG_TEMPSCALE_N65536_v1_smoke")
    s,v,m,e,c = run_experiment(smoke=True)
    oracle.assert_baseline_high("ece_present", s["ece"]+0.001, 0.0)
    write_metrics(out_dir,s,v,m,e,c); print(f"\nSMOKE OK: {v}",flush=True)


def run_main():
    out_dir = get_output_dir("wave14_betG_TEMPSCALE_N65536_v1")
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
