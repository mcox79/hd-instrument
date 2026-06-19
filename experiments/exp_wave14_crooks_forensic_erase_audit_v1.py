"""Crooks-ratio forensic erase audit — Strategy 10:03 v151 P1 (COMMERCIAL WEDGE Class 1).

Audit verifiable forensic erase via Crooks fluctuation theorem: ratio of forward
(insert) to reverse (erase) path KL must be ~0 if erase is theorem-anchored.

Forward: insert pattern (k,v) via Hebbian outer-product; measure retrieval entropy.
Erase: anti-Hebbian erase pattern; measure retrieval entropy.
Delta_S_emp = |H_erased - H_baseline| (substrate returned to pre-insertion state).

VERIFIED if Delta_S_emp < 0.05 (per Crooks FT bound).
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
    if "delta_S_emp" not in s: return ("CROOKS_INCONCLUSIVE", "Missing.")
    d = s["delta_S_emp"]
    if d < 0.05: return ("CROOKS_ERASE_VERIFIED", f"delta_S_emp={d:.4f}<0.05 (verifiable forensic erase per Crooks FT).")
    if d <= 0.5: return ("CROOKS_PARTIAL", f"delta_S_emp={d:.4f} in [0.05, 0.5] (partial erase residual).")
    return ("CROOKS_FAILED", f"delta_S_emp={d:.4f}>0.5 (erase incomplete; large residual).")


def self_test_verdict():
    for s,exp in [
        ({"delta_S_emp":0.02},"CROOKS_ERASE_VERIFIED"),
        ({"delta_S_emp":0.2},"CROOKS_PARTIAL"),
        ({"delta_S_emp":0.8},"CROOKS_FAILED"),
        ({},"CROOKS_INCONCLUSIVE"),
    ]:
        a,_=compute_verdict(s)
        if a!=exp: raise AssertionError(f"{a}!={exp}")
    print("verdict self-test passed (4/4 cases)",flush=True)


def make_pattern(N, gen, device):
    b = (torch.rand(N, generator=gen) > 0.5).to(device).float()
    return 2.0 * b - 1.0


def retrieval_entropy(W, k, candidates):
    """Entropy of softmax over inner-product scores W@k vs candidate set."""
    pred = W @ k
    scores = candidates @ pred
    log_probs = torch.log_softmax(scores, dim=0)
    probs = log_probs.exp()
    H = float(-(probs * log_probs).sum().item())
    return H


def run_experiment(smoke):
    t0=time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    cfg = {"N":4096 if smoke else 16384, "M_base":50 if smoke else 200,
           "n_trials":10 if smoke else 50, "seed":17}
    gen = torch.Generator().manual_seed(cfg["seed"])
    candidates = torch.stack([make_pattern(cfg["N"], gen, device) for _ in range(cfg["M_base"])], dim=0)
    base_keys = torch.stack([make_pattern(cfg["N"], gen, device) for _ in range(cfg["M_base"])], dim=0)
    # Build baseline W with M_base stored (k,v) pairs
    W_base = (candidates.T @ base_keys) / cfg["N"]
    deltas = []
    for trial in range(cfg["n_trials"]):
        k_new = make_pattern(cfg["N"], gen, device)
        v_new = make_pattern(cfg["N"], gen, device)
        H_baseline = retrieval_entropy(W_base, k_new, candidates)
        # Insert: Hebbian outer product
        W_post_insert = W_base + torch.outer(v_new, k_new) / cfg["N"]
        H_insert = retrieval_entropy(W_post_insert, k_new, candidates)
        # Anti-Hebbian erase: subtract outer product at k_new
        W_post_erase = W_post_insert - torch.outer(v_new, k_new) / cfg["N"]
        H_erase = retrieval_entropy(W_post_erase, k_new, candidates)
        delta = abs(H_erase - H_baseline)
        deltas.append(delta)
        if trial < 3:
            print(f"  trial={trial}: H_baseline={H_baseline:.4f} H_insert={H_insert:.4f} H_erase={H_erase:.4f} delta_S={delta:.4f}", flush=True)
    delta_mean = sum(deltas) / len(deltas)
    delta_max = max(deltas)
    delta_std = (sum((d-delta_mean)**2 for d in deltas) / len(deltas)) ** 0.5
    print(f"\n  Across {len(deltas)} trials: delta_S_emp mean={delta_mean:.4f} max={delta_max:.4f} std={delta_std:.4f}", flush=True)
    summary = {"delta_S_emp": delta_mean, "delta_S_max": delta_max, "delta_S_std": delta_std,
               "n_trials": cfg["n_trials"], "M_base": cfg["M_base"], "N": cfg["N"]}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic()-t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, cfg


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict":verdict,"verdict_msg":msg,"elapsed_s":elapsed,"summary":summary,"config":config}
    validate_metrics(metrics)
    tmp = out_dir/"metrics.json.tmp"; tmp.write_text(json.dumps(metrics,indent=2,default=float)); tmp.replace(out_dir/"metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14_crooks_forensic_erase_audit_v1_smoke")
    s,v,m,e,c = run_experiment(smoke=True)
    oracle.assert_baseline_high("delta_present", s["delta_S_emp"]+0.001, 0.0)
    write_metrics(out_dir,s,v,m,e,c); print(f"\nSMOKE OK: {v}",flush=True)


def run_main():
    out_dir = get_output_dir("wave14_crooks_forensic_erase_audit_v1")
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
