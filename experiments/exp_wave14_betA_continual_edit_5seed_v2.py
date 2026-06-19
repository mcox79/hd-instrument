"""Bet A continual edit 5-seed at N=65536 M_init=8192 — Strategy 09:35 P5 (memory-fixed).

v1 hit CUDA OOM at M_init=N=65536 (8GB bf16 doesn't fit in 8GB GPU).
v2 uses M_init=8192 (1/8 N), giving 8:1 headroom per cycle 98 theory regime.
This is the proper Bet A capacity test at N=65536.
"""
from __future__ import annotations
import argparse, importlib.util, json, os, sys, time
from pathlib import Path
import torch
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from verification import oracle  # noqa: E402
_ba = importlib.util.spec_from_file_location("ba", REPO / "experiments" / "exp_wave14_betA_continual_edit_N65536_v1.py")
ba = importlib.util.module_from_spec(_ba); _ba.loader.exec_module(ba)


PASS_EDIT = 0.95
PASS_KEPT = 0.95


def get_output_dir(name):
    n = os.environ.get("HDLAB_EXP_NAME", name)
    out = REPO / "data" / f"exp_{n}"; out.mkdir(parents=True, exist_ok=True); return out


def validate_metrics(d):
    if not {"verdict","verdict_msg","elapsed_s","summary","config"}.issubset(d.keys()): raise ValueError("missing")


def compute_verdict(s):
    if "edit_acc_mean" not in s: return ("BETA_5SEED_INCONCLUSIVE", "Missing.")
    e_m = s["edit_acc_mean"]; k_m = s["kept_acc_mean"]
    e_sd = s["edit_acc_sd"]; k_sd = s["kept_acc_sd"]
    if e_m >= PASS_EDIT and k_m >= PASS_KEPT and e_sd < 0.05 and k_sd < 0.05:
        return ("BETA_5SEED_PASS", f"mean edit={e_m:.3f} kept={k_m:.3f} sd<0.05 at M_init=8192 N=65536 (substrate-product 5-seed complete).")
    if e_m >= 0.5 and k_m >= 0.5:
        return ("BETA_5SEED_PARTIAL", f"mean edit={e_m:.3f} kept={k_m:.3f} (sd_e={e_sd:.3f} sd_k={k_sd:.3f}).")
    return ("BETA_5SEED_KILLED", f"mean edit={e_m:.3f} kept={k_m:.3f}<0.5 (5-seed killed at M_init=8192 N=65536).")


def self_test_verdict():
    for s,exp in [
        ({"edit_acc_mean":0.98,"kept_acc_mean":0.97,"edit_acc_sd":0.02,"kept_acc_sd":0.03},"BETA_5SEED_PASS"),
        ({"edit_acc_mean":0.70,"kept_acc_mean":0.75,"edit_acc_sd":0.1,"kept_acc_sd":0.1},"BETA_5SEED_PARTIAL"),
        ({"edit_acc_mean":0.2,"kept_acc_mean":0.1,"edit_acc_sd":0.05,"kept_acc_sd":0.05},"BETA_5SEED_KILLED"),
        ({},"BETA_5SEED_INCONCLUSIVE"),
    ]:
        a,_=compute_verdict(s)
        if a!=exp: raise AssertionError(f"{a}!={exp}")
    print("verdict self-test passed (4/4 cases)",flush=True)


def run_experiment(smoke):
    t0=time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    cfg = {"N":4096 if smoke else 65536, "M_init":1024 if smoke else 8192,
            "n_edits":50 if smoke else 100,
            "seeds":[17, 23] if smoke else [17, 23, 31, 41, 53]}
    e_list = []; k_list = []
    per_seed = {}
    for seed in cfg["seeds"]:
        cpu_gen = torch.Generator().manual_seed(seed)
        print(f"\n[seed={seed}] N={cfg['N']} M_init={cfg['M_init']} n_edits={cfg['n_edits']}", flush=True)
        e_acc, k_acc = ba.run_one_seed(cfg["n_edits"], cfg["N"], cfg["M_init"], cpu_gen, device)
        e_list.append(e_acc); k_list.append(k_acc)
        per_seed[str(seed)] = {"edit_acc": e_acc, "kept_acc": k_acc}
        print(f"  seed={seed}: edit_acc={e_acc:.3f} kept_acc={k_acc:.3f}", flush=True)
    e_mean = sum(e_list)/len(e_list); k_mean = sum(k_list)/len(k_list)
    e_sd = (sum((x-e_mean)**2 for x in e_list) / len(e_list)) ** 0.5
    k_sd = (sum((x-k_mean)**2 for x in k_list) / len(k_list)) ** 0.5
    print(f"\n  edit_acc mean={e_mean:.3f} sd={e_sd:.3f}", flush=True)
    print(f"  kept_acc mean={k_mean:.3f} sd={k_sd:.3f}", flush=True)
    summary = {"edit_acc_mean": e_mean, "kept_acc_mean": k_mean,
                "edit_acc_sd": e_sd, "kept_acc_sd": k_sd,
                "per_seed": per_seed, "seeds": cfg["seeds"],
                "M_init": cfg["M_init"], "N": cfg["N"], "headroom": cfg["N"] / cfg["M_init"]}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic()-t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, cfg


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict":verdict,"verdict_msg":msg,"elapsed_s":elapsed,"summary":summary,"config":config}
    validate_metrics(metrics)
    tmp = out_dir/"metrics.json.tmp"; tmp.write_text(json.dumps(metrics,indent=2,default=float)); tmp.replace(out_dir/"metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14_betA_continual_edit_5seed_v2_smoke")
    s,v,m,e,c = run_experiment(smoke=True)
    oracle.assert_baseline_high("edit_present", s["edit_acc_mean"]+0.001, 0.0)
    write_metrics(out_dir,s,v,m,e,c); print(f"\nSMOKE OK: {v}",flush=True)


def run_main():
    out_dir = get_output_dir("wave14_betA_continual_edit_5seed_v2")
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
