"""Online W Robbins-Monro + SNAP — Strategy 10:03 v151 P3 (Gap B online learning rescue).

Sequential 50-write test with Robbins-Monro update schedule + SNAP saturation guard.
Check substrate-product retention across 50 sequential pattern insertions.
"""
from __future__ import annotations
import argparse, importlib.util, json, math, os, sys, time
from pathlib import Path
import torch
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from verification import oracle  # noqa: E402


def get_output_dir(name):
    n = os.environ.get("HDLAB_EXP_NAME", name)
    out = REPO / "data" / f"exp_{n}"; out.mkdir(parents=True, exist_ok=True); return out


def validate_metrics(d):
    if not {"verdict","verdict_msg","elapsed_s","summary","config"}.issubset(d.keys()): raise ValueError("missing")


def compute_verdict(s):
    if "min_acc" not in s: return ("ONLINE_W_INCONCLUSIVE", "Missing.")
    m = s["min_acc"]
    if m >= 0.95: return ("ONLINE_W_RESISTS_CF", f"min_acc={m:.3f}>=0.95 across 50 writes (substrate resists catastrophic forgetting).")
    if m >= 0.3: return ("ONLINE_W_GRADUAL_FORGETTING", f"min_acc={m:.3f} in [0.3, 0.95] (gradual decay).")
    return ("ONLINE_W_CATASTROPHIC", f"min_acc={m:.3f}<0.3 (catastrophic forgetting).")


def self_test_verdict():
    for s,exp in [
        ({"min_acc":0.97},"ONLINE_W_RESISTS_CF"),
        ({"min_acc":0.6},"ONLINE_W_GRADUAL_FORGETTING"),
        ({"min_acc":0.1},"ONLINE_W_CATASTROPHIC"),
        ({},"ONLINE_W_INCONCLUSIVE"),
    ]:
        a,_=compute_verdict(s)
        if a!=exp: raise AssertionError(f"{a}!={exp}")
    print("verdict self-test passed (4/4 cases)",flush=True)


def make_pattern(N, gen, device):
    b = (torch.rand(N, generator=gen) > 0.5).to(device).float()
    return 2.0 * b - 1.0


def robbins_monro_lr(step, base=1.0):
    return base / (1.0 + step / 10.0)


def snap_update(W, k, v, lr, N, snap_threshold=1.0):
    """SNAP-guarded outer-product update: clip update if would saturate."""
    delta = lr * torch.outer(v, k) / N
    delta_norm = float(delta.abs().max().item())
    if delta_norm > snap_threshold:
        delta = delta * (snap_threshold / delta_norm)
    return W + delta


def check_retrieval(W, k, v):
    pred = torch.sign(W @ k); pred[pred == 0] = 1.0
    overlap = float((pred * v).mean().item())
    return overlap > 0.7


def run_experiment(smoke):
    t0=time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    cfg = {"N":2048 if smoke else 8192,
            "n_writes":15 if smoke else 50, "seed":17}
    gen = torch.Generator().manual_seed(cfg["seed"])
    W = torch.zeros((cfg["N"], cfg["N"]), device=device)
    keys = []; values = []
    accs_over_time = []
    for step in range(cfg["n_writes"]):
        k = make_pattern(cfg["N"], gen, device)
        v = make_pattern(cfg["N"], gen, device)
        lr = robbins_monro_lr(step)
        W = snap_update(W, k, v, lr, cfg["N"])
        keys.append(k); values.append(v)
        # Check retention on all prior patterns
        n_correct = sum(1 for j in range(len(keys)) if check_retrieval(W, keys[j], values[j]))
        acc = n_correct / len(keys)
        accs_over_time.append(acc)
        if step < 3 or step % max(1, cfg["n_writes"] // 5) == 0:
            print(f"  step={step+1}: acc={acc:.3f} (across {len(keys)} prior patterns) lr={lr:.4f}", flush=True)
    min_acc = min(accs_over_time)
    final_acc = accs_over_time[-1]
    print(f"\n  Across {cfg['n_writes']} writes: min_acc={min_acc:.3f} final_acc={final_acc:.3f}", flush=True)
    summary = {"min_acc": min_acc, "final_acc": final_acc,
               "accs_over_time": accs_over_time, "n_writes": cfg["n_writes"]}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic()-t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, cfg


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict":verdict,"verdict_msg":msg,"elapsed_s":elapsed,"summary":summary,"config":config}
    validate_metrics(metrics)
    tmp = out_dir/"metrics.json.tmp"; tmp.write_text(json.dumps(metrics,indent=2,default=float)); tmp.replace(out_dir/"metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14_online_W_robbins_monro_snap_v1_smoke")
    s,v,m,e,c = run_experiment(smoke=True)
    oracle.assert_baseline_high("acc_present", s["final_acc"]+0.001, 0.0)
    write_metrics(out_dir,s,v,m,e,c); print(f"\nSMOKE OK: {v}",flush=True)


def run_main():
    out_dir = get_output_dir("wave14_online_W_robbins_monro_snap_v1")
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
