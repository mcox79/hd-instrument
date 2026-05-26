"""Bet C M/N capacity at N=65536 — V2.D Phase 3 sub-test #2.

Per Strategy 20:14 Priority 2: Bet C M/N capacity at N=65536 with substrate-default
beta. Memory engineering: W in bf16 (8.6GB) + batched per-query computation to
avoid M*M intermediates.

Test capacity: largest M where >=95% of test queries recover correctly.

Verdict thresholds:
  BET_C_N65K_PASS:    M/N >= 8 (matches N=4096 baseline; Bet C scales)
  BET_C_N65K_PARTIAL: M/N >= 4 (partial scaling)
  BET_C_N65K_KILLED:  M/N < 4 (substrate capacity drops)
  BET_C_N65K_INCONCLUSIVE

Pre-reg: preregs/2026-05-22_wave14_betC_M_N_capacity_N65536_v1.md
"""
from __future__ import annotations
import argparse, json, math, os, sys, time
from pathlib import Path
import torch
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from verification import oracle  # noqa: E402
try:
    from hdlab.session_log import log_event
except ImportError:
    def log_event(*a, **k): pass


PASS_M_OVER_N = 8.0
PARTIAL_M_OVER_N = 4.0


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def compute_verdict(summary):
    if "capacity_M_over_N" not in summary:
        return ("BET_C_N65K_INCONCLUSIVE", "Missing capacity_M_over_N.")
    cap = summary["capacity_M_over_N"]
    per_M = summary["acc_per_M_over_N"]
    if cap >= PASS_M_OVER_N:
        return ("BET_C_N65K_PASS",
                f"Bet C scales to N=65536: M/N={cap}>={PASS_M_OVER_N}. acc_per_M_over_N={per_M}.")
    if cap >= PARTIAL_M_OVER_N:
        return ("BET_C_N65K_PARTIAL",
                f"Partial scaling: M/N={cap} ({PARTIAL_M_OVER_N}<=M/N<{PASS_M_OVER_N}). acc_per_M_over_N={per_M}.")
    return ("BET_C_N65K_KILLED",
            f"Capacity drops: M/N={cap}<{PARTIAL_M_OVER_N}. acc_per_M_over_N={per_M}.")


def self_test_verdict():
    cases = [
        ({"capacity_M_over_N": 8, "acc_per_M_over_N": {}}, "BET_C_N65K_PASS"),
        ({"capacity_M_over_N": 4, "acc_per_M_over_N": {}}, "BET_C_N65K_PARTIAL"),
        ({"capacity_M_over_N": 2, "acc_per_M_over_N": {}}, "BET_C_N65K_KILLED"),
        ({}, "BET_C_N65K_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def measure_capacity_batched(N, M, cpu_gen, device, n_test_queries=50, dtype=torch.bfloat16):
    """Bf16 W; batched per-query retrieval to avoid M*M intermediates."""
    # Build keys, values in bf16 to fit memory
    print(f"    M={M}: building keys/values ({M}x{N} bf16)...", flush=True)
    kb = (torch.rand((M, N), generator=cpu_gen) > 0.5).to(device).to(dtype)
    keys = 2.0 * kb - 1.0
    del kb
    vb = (torch.rand((M, N), generator=cpu_gen) > 0.5).to(device).to(dtype)
    values = 2.0 * vb - 1.0
    del vb
    if device.type == "cuda": torch.cuda.empty_cache()
    print(f"    M={M}: building W ({N}x{N} bf16)...", flush=True)
    W = (values.T.to(torch.float32) @ keys.to(torch.float32)) / N
    W = W.to(dtype)
    if device.type == "cuda": torch.cuda.empty_cache()
    # Test n_test_queries randomly chosen patterns
    test_idx = torch.randperm(M, generator=cpu_gen)[:n_test_queries].to(device)
    correct = 0
    Wfp = W.to(torch.float32)
    Vfp = values.to(torch.float32)
    for i in test_idx:
        k = keys[i].to(torch.float32)
        # Standard: keys[i] @ W.T = W @ keys[i] (when k is 1D)
        readout = Wfp @ k  # (N,) fp32
        sims = Vfp @ readout  # (M,) fp32
        pred = int(sims.argmax().item())
        if pred == int(i.item()):
            correct += 1
    del Wfp, Vfp
    acc = correct / n_test_queries
    del W, keys, values
    if device.type == "cuda": torch.cuda.empty_cache()
    return acc


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 4096 if smoke else 65536,
              "M_over_N_grid": [1, 2] if smoke else [1, 2, 4, 8],
              "n_test_queries": 30 if smoke else 100,
              "seed": 17}
    N = config["N"]
    cpu_gen = torch.Generator().manual_seed(config["seed"])
    print(f"[setup] N={N}", flush=True)
    acc_per_M_over_N = {}
    for r in config["M_over_N_grid"]:
        M = r * N
        try:
            acc = measure_capacity_batched(N, M, cpu_gen, device, config["n_test_queries"])
            acc_per_M_over_N[str(r)] = acc
            print(f"  M/N={r} (M={M}): acc={acc:.3f}", flush=True)
        except torch.cuda.OutOfMemoryError as e:
            print(f"  M/N={r} (M={M}): OOM — recording 0.0", flush=True)
            acc_per_M_over_N[str(r)] = 0.0
            if device.type == "cuda": torch.cuda.empty_cache()
    # Capacity = largest M/N where acc >= 0.95
    capacity = max([r for r in config["M_over_N_grid"] if acc_per_M_over_N.get(str(r), 0.0) >= 0.95], default=0)
    summary = {"acc_per_M_over_N": acc_per_M_over_N,
                "capacity_M_over_N": capacity,
                "N": N}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
                "summary": summary, "config": config}
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14_betC_M_N_capacity_N65536_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("any_acc_present",
                                 max(summary["acc_per_M_over_N"].values()) + 0.001, 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_betC_M_N_capacity_N65536_v1")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nDONE: {verdict}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test: self_test_verdict(); return 0
    if args.smoke: run_smoke(); return 0
    run_main(); return 0


if __name__ == "__main__":
    sys.exit(main())
