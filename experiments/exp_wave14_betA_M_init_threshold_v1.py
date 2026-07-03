"""Bet A M_init threshold sweep — Strategy 10:16 v152 add-2.

Cycle 172 v2 5-seed PASS at M_init=8192. v1 KILL at M_init=N=65536 (OOM).
Sweep M_init in {1024, 2048, 4096, 8192, 16384, 32768} (cap at 32768 to fit
8GB VRAM) at N=65536, 5 seeds, n_edits=100. Find KILL -> PASS threshold.
"""
from __future__ import annotations
import argparse, importlib.util, json, os, sys, time
from pathlib import Path
import torch
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
from verification import oracle  # noqa: E402
_ba = importlib.util.spec_from_file_location("ba", REPO / "experiments" / "exp_wave14_betA_continual_edit_N65536_v1.py")
ba = importlib.util.module_from_spec(_ba); _ba.loader.exec_module(ba)


def get_output_dir(name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d):
    if not {"verdict","verdict_msg","elapsed_s","summary","config"}.issubset(d.keys()): raise ValueError("missing")


def compute_verdict(s):
    if "threshold_M_init" not in s: return ("BETA_M_INIT_INCONCLUSIVE", "Missing.")
    th = s["threshold_M_init"]; per = s.get("per_M_init", {})
    if th is None and all(v.get("mean_kept", 0) >= 0.85 for v in per.values()):
        return ("BETA_M_INIT_UNIFORM_PASS", f"all M_init pass: {per}.")
    if th is None and all(v.get("mean_kept", 0) < 0.5 for v in per.values()):
        return ("BETA_M_INIT_UNIFORM_KILL", f"all M_init kill: {per}.")
    if th is not None:
        return ("BETA_M_INIT_BOUND_FOUND", f"threshold M_init={th}; per_M_init={per}.")
    return ("BETA_M_INIT_MIXED", f"intermediate; per_M_init={per}.")


def self_test_verdict():
    cases = [
        ({"threshold_M_init":4096,"per_M_init":{"1024":{"mean_kept":0.95},"8192":{"mean_kept":0.2}}},"BETA_M_INIT_BOUND_FOUND"),
        ({"threshold_M_init":None,"per_M_init":{"1024":{"mean_kept":0.95},"8192":{"mean_kept":0.95}}},"BETA_M_INIT_UNIFORM_PASS"),
        ({"threshold_M_init":None,"per_M_init":{"1024":{"mean_kept":0.2},"8192":{"mean_kept":0.1}}},"BETA_M_INIT_UNIFORM_KILL"),
        ({},"BETA_M_INIT_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a,_=compute_verdict(s)
        if a!=exp: raise AssertionError(f"{a}!={exp}")
    print("verdict self-test passed (4/4 cases)",flush=True)


def run_experiment(smoke):
    t0=time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    cfg = {"N":4096 if smoke else 65536,
           "M_init_grid":[256, 1024] if smoke else [1024, 2048, 4096, 8192, 16384, 32768],
           "n_edits":50 if smoke else 100,
           "seeds":[17, 23] if smoke else [17, 23, 31, 41, 53]}
    per_M_init = {}
    for M_init in cfg["M_init_grid"]:
        print(f"\n[M_init={M_init}] N={cfg['N']} n_edits={cfg['n_edits']}", flush=True)
        kept_accs = []
        for seed in cfg["seeds"]:
            cpu_gen = torch.Generator().manual_seed(seed)
            try:
                e_acc, k_acc = ba.run_one_seed(cfg["n_edits"], cfg["N"], M_init, cpu_gen, device)
                kept_accs.append(k_acc)
                print(f"  seed={seed}: kept_acc={k_acc:.3f}", flush=True)
            except torch.OutOfMemoryError:
                print(f"  seed={seed}: CUDA OOM (skipped)", flush=True)
                if device.type == "cuda": torch.cuda.empty_cache()
        if not kept_accs:
            per_M_init[str(M_init)] = {"mean_kept": 0.0, "n_seeds": 0, "oom": True}
            continue
        m = sum(kept_accs) / len(kept_accs)
        sd = (sum((x-m)**2 for x in kept_accs) / len(kept_accs)) ** 0.5
        per_M_init[str(M_init)] = {"mean_kept": m, "sd_kept": sd, "n_seeds": len(kept_accs)}
        print(f"  M_init={M_init}: mean_kept={m:.3f} sd={sd:.3f}", flush=True)
    # Find threshold: smallest M_init where mean_kept transitions from <0.5 (KILL) to >=0.85 (PASS)
    threshold = None
    sorted_keys = sorted([int(k) for k in per_M_init.keys()])
    for i in range(len(sorted_keys) - 1):
        a = per_M_init[str(sorted_keys[i])].get("mean_kept", 0)
        b = per_M_init[str(sorted_keys[i+1])].get("mean_kept", 0)
        if a < 0.5 and b >= 0.85:
            threshold = sorted_keys[i+1]
            break
    print(f"\n  threshold M_init = {threshold}", flush=True)
    summary = {"threshold_M_init": threshold, "per_M_init": per_M_init,
               "M_init_grid": cfg["M_init_grid"], "seeds": cfg["seeds"]}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic()-t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, cfg


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict":verdict,"verdict_msg":msg,"elapsed_s":elapsed,"summary":summary,"config":config}
    validate_metrics(metrics)
    tmp = out_dir/"metrics.json.tmp"; tmp.write_text(json.dumps(metrics,indent=2,default=float)); tmp.replace(out_dir/"metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14_betA_M_init_threshold_v1_smoke")
    s,v,m,e,c = run_experiment(smoke=True)
    oracle.assert_baseline_high("grid_present", float(len(s["per_M_init"]))+0.001, 0.0)
    write_metrics(out_dir,s,v,m,e,c); print(f"\nSMOKE OK: {v}",flush=True)


def run_main():
    out_dir = get_output_dir("wave14_betA_M_init_threshold_v1")
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
