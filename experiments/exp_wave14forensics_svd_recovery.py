"""Substrate forensics: can we recover stored (v_k, k_k) pairs from W alone?

Crystallography research agent finding: at K < N/(2 log N) ~ 170 for N=4096,
SVD + sign-quantization should recover stored keys/values from W. Above that
threshold, recovery is information-theoretically ambiguous.

This is BOTH a capability (memory dump from W) AND a security finding
(adversary with W can read out stored data at low load).

Method (simplified vs charge-flipping):
  1. Build W = sum_k v_k k_k^T / N with random bipolar (v, k) pairs
  2. SVD: W = U Sigma V^T
  3. Take top-K columns of U as candidate values, top-K rows of V^T as candidate keys
  4. Sign-quantize
  5. Match against true (v, k) - need to solve assignment (Hungarian) due to
     permutation/sign ambiguity. Simplified: report max-over-perms cosine.

Pre-reg: preregs/2026-05-20_wave14forensics_svd_recovery.md
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
from pathlib import Path

import torch


def get_output_dir(default_name: str) -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    repo_root = Path(__file__).resolve().parent.parent
    out = repo_root / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d: dict) -> None:
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    if not all(k in d for k in required):
        raise ValueError("missing")
    if not d.get("verdict") or not d.get("verdict_msg"):
        raise ValueError("empty")


def compute_verdict(summary: dict) -> tuple[str, str]:
    rows = summary.get("per_K", [])
    if not rows:
        return ("FORENSICS_INCONCLUSIVE", "No data.")
    # Predicted threshold K* = N / (2 log N)
    N = rows[0]["N"]
    K_star = N / (2 * math.log(N))  # ~ 170 at N=4096
    low_K = [r for r in rows if r["K"] < K_star]
    high_K = [r for r in rows if r["K"] > 3 * K_star]
    if low_K and high_K:
        low_rec = max(r["max_cos_match"] for r in low_K)
        high_rec = max(r["max_cos_match"] for r in high_K)
        gap = low_rec - high_rec
        if low_rec >= 0.5 and high_rec < 0.3:
            return ("FORENSICS_RECOVERY_AT_LOW_K",
                    f"At K < {K_star:.0f}: max cos match = {low_rec:.2f}. "
                    f"At K > {3*K_star:.0f}: {high_rec:.2f}. "
                    f"Information-theoretic threshold confirmed - substrate "
                    f"forensics works below K* = N/(2 log N), fails above.")
        if low_rec >= 0.3 and gap >= 0.2:
            return ("FORENSICS_PARTIAL",
                    f"Low K cos = {low_rec:.2f}, high K = {high_rec:.2f}. "
                    f"Gap {gap:.2f} confirms threshold trend but recovery is "
                    f"weaker than predicted.")
        if low_rec < 0.3:
            return ("FORENSICS_NO_RECOVERY",
                    f"Even at K < K* = {K_star:.0f}, max cos = {low_rec:.2f}. "
                    f"SVD+sign alone insufficient; would need iterative "
                    f"charge-flipping refinement.")
    return ("FORENSICS_GRID_TOO_NARROW",
            f"K range doesn't bracket K* = {K_star:.0f}. Per-K results: " +
            ", ".join(f"K={r['K']}: cos={r['max_cos_match']:.2f}" for r in rows[:5]))


def self_test_verdict() -> None:
    cases = [
        ({"per_K": [{"K": 50, "N": 4096, "max_cos_match": 0.85},
                    {"K": 1000, "N": 4096, "max_cos_match": 0.10}]},
         "FORENSICS_RECOVERY_AT_LOW_K"),
        ({"per_K": [{"K": 50, "N": 4096, "max_cos_match": 0.40},
                    {"K": 1000, "N": 4096, "max_cos_match": 0.15}]},
         "FORENSICS_PARTIAL"),
        ({"per_K": [{"K": 50, "N": 4096, "max_cos_match": 0.10},
                    {"K": 1000, "N": 4096, "max_cos_match": 0.05}]},
         "FORENSICS_NO_RECOVERY"),
        ({"per_K": [{"K": 200, "N": 4096, "max_cos_match": 0.5}]},
         "FORENSICS_GRID_TOO_NARROW"),
        ({"per_K": []}, "FORENSICS_INCONCLUSIVE"),
    ]
    for s, expected in cases:
        actual, _ = compute_verdict(s)
        if actual != expected:
            raise AssertionError(f"FAIL: {actual} != {expected} for {s}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def max_cos_match(candidates, truth):
    """Greedy assignment: for each truth row, find best-matching candidate via
    max |cosine| (allow sign flip). Return mean."""
    K, N = truth.shape
    M = candidates.size(0)
    sims = (candidates @ truth.T).abs() / (
        candidates.norm(dim=1, keepdim=True) * truth.norm(dim=1, keepdim=True).T)
    # Greedy: for each truth col, take best remaining candidate
    matched = []
    used = set()
    sims_cpu = sims.cpu()
    for t in range(K):
        best_score = -1.0
        best_idx = -1
        for c in range(M):
            if c in used:
                continue
            s = float(sims_cpu[c, t])
            if s > best_score:
                best_score = s
                best_idx = c
        if best_idx >= 0:
            matched.append(best_score)
            used.add(best_idx)
    return sum(matched) / max(1, len(matched))


def run_one_K(N, K, seeds, device):
    cos_per_seed = []
    for seed in seeds:
        gen = torch.Generator().manual_seed(seed)
        keys = 2.0 * (torch.rand((K, N), generator=gen) > 0.5).float() - 1.0
        values = 2.0 * (torch.rand((K, N), generator=gen) > 0.5).float() - 1.0
        keys = keys.to(device)
        values = values.to(device)
        W = (values.T @ keys) / N
        # SVD
        U, S, Vh = torch.linalg.svd(W, full_matrices=False)
        # Take top K
        cand_values = torch.sign(U[:, :K].T)  # (K, N)
        cand_keys = torch.sign(Vh[:K, :])  # (K, N)
        # Match candidates to truth via best |cos|
        v_cos = max_cos_match(cand_values, values)
        k_cos = max_cos_match(cand_keys, keys)
        cos_per_seed.append((v_cos + k_cos) / 2)
    return {"K": K, "N": N,
            "mean_cos_match": sum(cos_per_seed) / len(cos_per_seed),
            "max_cos_match": max(cos_per_seed),
            "per_seed_cos": cos_per_seed}


def main(smoke: bool = False) -> None:
    self_test_verdict()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if smoke:
        config = {"mode": "smoke", "N": 512, "K_list": [20, 80, 200],
                  "seeds": [17]}
    else:
        # Bracket K* = N/(2 log N) ~ 170 at N=4096
        config = {"mode": "full", "N": 4096,
                  "K_list": [30, 60, 100, 150, 200, 300, 500, 800, 1500, 3000],
                  "seeds": [17, 23, 31, 41, 53]}
    print(f"wave14forensics_svd_recovery. mode={config['mode']} device={device}", flush=True)
    K_star = config["N"] / (2 * math.log(config["N"]))
    print(f"  N={config['N']} K_star (predicted) = {K_star:.0f}", flush=True)

    t0 = time.monotonic()
    per_K = []
    for K in config["K_list"]:
        r = run_one_K(config["N"], K, config["seeds"], device)
        per_K.append(r)
        print(f"  K={K:5d} (K/K_star={K/K_star:.2f})  mean_cos={r['mean_cos_match']:.3f} "
              f"max_cos={r['max_cos_match']:.3f}", flush=True)
    elapsed = time.monotonic() - t0

    summary = {"per_K": per_K}
    verdict, msg = compute_verdict(summary)
    print(f"\n=== {verdict} ===\n{msg}", flush=True)
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
               "config": config, "device": str(device),
               "per_K": per_K, "summary": summary}
    validate_metrics(metrics)
    out_dir = get_output_dir("wave14forensics_svd_recovery")
    tmp = (out_dir / "metrics.json").with_suffix(".tmp")
    tmp.write_text(json.dumps(metrics, indent=2))
    os.replace(tmp, out_dir / "metrics.json")
    print(f"wrote {out_dir / 'metrics.json'}", flush=True)


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test_verdict()
        sys.exit(0)
    main(smoke="--smoke" in sys.argv)
