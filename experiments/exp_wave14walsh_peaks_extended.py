"""Operational substrate forensics: read out WHICH keys were stored from WHT peaks.

wave14xrd_structured_keys confirmed: with Hadamard keys, the substrate's W
matrix has crisp Bragg peaks in WHT (SNR ~ 10^7). This experiment asks the
operational question:

  Given W built with structured (Hadamard) keys + random values, can we
  recover the IDENTITY of which keys were stored just by reading the WHT peaks?

Method:
  1. Build Hadamard codebook H of size N x N (4096 keys available)
  2. Randomly select K keys (subset of H rows); store as W = sum_k v_k * h_k^T / N
  3. Compute WHT of W (which spectrally separates each h_k as a peak)
  4. Identify K largest spectral peak frequencies
  5. Compare to the actual stored key indices
  6. Recall = fraction of stored keys correctly identified

Pre-reg: preregs/2026-05-20_wave14forensics_walsh_peaks.md
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
        return ("PEAKS_INCONCLUSIVE", "No data.")
    # Identify regime: high recall at low K, degrades at high K
    low_K_rows = [r for r in rows if r["K"] <= 200]
    high_K_rows = [r for r in rows if r["K"] >= 1500]
    low_recall = max((r["recall"] for r in low_K_rows), default=None)
    high_recall = max((r["recall"] for r in high_K_rows), default=None)
    if low_recall is not None and high_recall is not None:
        if low_recall >= 0.95 and high_recall < 0.5:
            return ("PEAKS_FORENSICS_VALIDATED",
                    f"At K<=200: recall={low_recall:.2%} (substrate forensics WORKS). "
                    f"At K>=1500: recall={high_recall:.2%} (degrades as predicted). "
                    f"Capability confirmed: read out which keys were stored from W alone.")
    if low_recall is not None and low_recall >= 0.95:
        return ("PEAKS_FORENSICS_LIMITED",
                f"Recall={low_recall:.2%} at low K. High-K test inconclusive.")
    if low_recall is not None and low_recall < 0.5:
        return ("PEAKS_NO_FORENSICS",
                f"Even at K<=200, recall={low_recall:.2%}. WHT-peak-id doesn't work.")
    return ("PEAKS_PARTIAL",
            "Per-K: " + ", ".join(f"K={r['K']}: rec={r['recall']:.2f}" for r in rows[:5]))


def self_test_verdict() -> None:
    cases = [
        ({"per_K": [{"K": 100, "recall": 0.99}, {"K": 2000, "recall": 0.20}]},
         "PEAKS_FORENSICS_VALIDATED"),
        ({"per_K": [{"K": 100, "recall": 0.20}, {"K": 2000, "recall": 0.05}]},
         "PEAKS_NO_FORENSICS"),
        ({"per_K": [{"K": 100, "recall": 0.96}]}, "PEAKS_FORENSICS_LIMITED"),
        ({"per_K": []}, "PEAKS_INCONCLUSIVE"),
    ]
    for s, expected in cases:
        actual, _ = compute_verdict(s)
        if actual != expected:
            raise AssertionError(f"FAIL: {actual} != {expected} for {s}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def hadamard_matrix(n: int) -> torch.Tensor:
    assert (n & (n - 1)) == 0
    H = torch.tensor([[1.0]])
    while H.size(0) < n:
        H = torch.cat([torch.cat([H, H], dim=1), torch.cat([H, -H], dim=1)], dim=0)
    return H


def fast_walsh_hadamard(x: torch.Tensor) -> torch.Tensor:
    N = x.size(-1)
    h = 1
    while h < N:
        for i in range(0, N, h * 2):
            a = x[..., i:i+h].clone()
            b = x[..., i+h:i+2*h].clone()
            x[..., i:i+h] = a + b
            x[..., i+h:i+2*h] = a - b
        h *= 2
    return x / math.sqrt(N)


def recover_keys_via_wht(W, K, H_codebook):
    """For W = sum_k v_k h_k^T / N where h_k are Hadamard rows, the WHT of W
    has support concentrated at the Walsh frequencies dual to those h_k.

    Specifically: WHT_col(W) has rows that are v_k * delta_freq(h_k).
    Computing column-WHT then row-magnitudes per column gives peak locations.
    """
    N = W.size(0)
    # Apply WHT along rows (so each row is now in Walsh-frequency basis)
    W_walsh = fast_walsh_hadamard(W.clone())  # (N, N)
    # Each column j of W_walsh corresponds to Walsh frequency j of the keys.
    # Magnitude of column j = sum over k of |v_k| if h_k corresponds to freq j.
    # Power per column = how many stored keys map to that freq.
    col_power = (W_walsh ** 2).sum(dim=0)  # (N,)
    # Top-K column indices = predicted stored key frequencies
    top_K_freqs = torch.topk(col_power, K).indices.tolist()
    return set(top_K_freqs)


def run_one_seed(N, K, seed, H, device):
    gen = torch.Generator().manual_seed(seed)
    # Random K-subset of Hadamard rows as keys
    key_idx = torch.randperm(N, generator=gen)[:K].tolist()
    key_idx_set = set(key_idx)
    # Random ±1 values
    values = 2.0 * (torch.rand((K, N), generator=gen) > 0.5).float() - 1.0
    values = values.to(device)
    keys = H[key_idx].to(device)  # (K, N)
    W = (values.T @ keys) / N  # (N, N)
    # Recover via WHT
    predicted = recover_keys_via_wht(W, K, H)
    # Recall: fraction of stored keys correctly predicted
    correct = len(predicted & key_idx_set)
    recall = correct / K
    return recall


def main(smoke: bool = False) -> None:
    self_test_verdict()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if smoke:
        config = {"mode": "smoke", "N": 512, "K_list": [20, 100, 300], "seeds": [17]}
    else:
        # Push to N to find where forensics fully degrades. Many seeds for tight CI.
        config = {"mode": "full", "N": 4096,
                  "K_list": [50, 200, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000],
                  "seeds": [17, 23, 31, 41, 53, 67, 79, 89, 101, 113]}
    print(f"wave14walsh_peaks_extended. mode={config['mode']} device={device}", flush=True)
    print(f"  Building Hadamard matrix...", flush=True)
    H = hadamard_matrix(config["N"])
    print(f"  H shape: {H.shape}", flush=True)

    t0 = time.monotonic()
    per_K = []
    for K in config["K_list"]:
        recalls = []
        for seed in config["seeds"]:
            r = run_one_seed(config["N"], K, seed, H, device)
            recalls.append(r)
        mean_recall = sum(recalls) / len(recalls)
        per_K.append({"K": K, "recall": mean_recall, "per_seed_recall": recalls})
        print(f"  K={K:5d} (K/N={K/config['N']:.3f})  recall={mean_recall:.3f}",
              flush=True)
    elapsed = time.monotonic() - t0

    summary = {"per_K": per_K}
    verdict, msg = compute_verdict(summary)
    print(f"\n=== {verdict} ===\n{msg}", flush=True)
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
               "config": config, "device": str(device),
               "per_K": per_K, "summary": summary}
    validate_metrics(metrics)
    out_dir = get_output_dir("wave14walsh_peaks_extended")
    tmp = (out_dir / "metrics.json").with_suffix(".tmp")
    tmp.write_text(json.dumps(metrics, indent=2))
    os.replace(tmp, out_dir / "metrics.json")
    print(f"wrote {out_dir / 'metrics.json'}", flush=True)


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test_verdict()
        sys.exit(0)
    main(smoke="--smoke" in sys.argv)
