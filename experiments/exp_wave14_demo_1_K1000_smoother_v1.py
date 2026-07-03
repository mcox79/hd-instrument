"""Demo 1 at K=1000 — Strategy 06:49 P3. Does K-resonance affect Lane D E2E?"""
from __future__ import annotations
import argparse, importlib.util, json, os, sys, time
from pathlib import Path
import torch
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
from verification import oracle  # noqa: E402
_e2e = importlib.util.spec_from_file_location("e2e", REPO / "experiments" / "exp_wave14_lane_D_end_to_end_N65536_smoother_v1.py")
e2e = importlib.util.module_from_spec(_e2e); _e2e.loader.exec_module(e2e)


def get_output_dir(name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d):
    if not {"verdict","verdict_msg","elapsed_s","summary","config"}.issubset(d.keys()): raise ValueError("missing")


def compute_verdict(s):
    if "composed_acc" not in s: return ("D1K1K_INCONCLUSIVE", "Missing.")
    c = s["composed_acc"]
    if c > 0.95: return ("DEMO_1_K1000_BETTER", f"composed_acc={c:.3f}>0.95.")
    if c >= 0.95: return ("DEMO_1_K1000_PASS", f"composed_acc={c:.3f}.")
    if c < 0.95: return ("DEMO_1_K1000_DEGRADED", f"composed_acc={c:.3f}<0.95.")
    return ("D1K1K_INCONCLUSIVE", "Missing path.")


def self_test_verdict():
    for s,exp in [
        ({"composed_acc": 0.99}, "DEMO_1_K1000_BETTER"),
        ({"composed_acc": 0.5}, "DEMO_1_K1000_DEGRADED"),
        ({}, "D1K1K_INCONCLUSIVE"),
    ]:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print("verdict self-test passed (3/3 cases)", flush=True)


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    cfg = {"N": 8192 if smoke else 65536, "K_hypotheses": 3, "F_facts_per_hyp": 333,
            "skill_len": 4, "skill_alphabet": 5,
            "n_trials": 5 if smoke else 30, "seeds": [17] if smoke else [17, 23, 31]}
    all_results = []
    for seed in cfg["seeds"]:
        for trial in range(cfg["n_trials"]):
            r = e2e.run_one_trial(seed * 1000 + trial, cfg, device)
            all_results.append(r)
        n = len(all_results)
        c_acc = sum(r["composed"] for r in all_results) / n
        print(f"  seed={seed} cum: composed={c_acc:.3f}", flush=True)
    n = len(all_results)
    c_acc = sum(r["composed"] for r in all_results) / n
    summary = {"composed_acc": c_acc, "n": n, "K_total": cfg["K_hypotheses"] * cfg["F_facts_per_hyp"]}
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
    out_dir = get_output_dir("wave14_demo_1_K1000_smoother_v1_smoke")
    s,v,m,e,c = run_experiment(smoke=True)
    oracle.assert_baseline_high("acc_present", s["composed_acc"]+0.001, 0.0)
    write_metrics(out_dir,s,v,m,e,c); print(f"\nSMOKE OK: {v}",flush=True)


def run_main():
    out_dir = get_output_dir("wave14_demo_1_K1000_smoother_v1")
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
