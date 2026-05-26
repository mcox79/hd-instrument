"""Crystallography for substrate forensics: WHT of W as diffraction pattern.

User's insight: in crystallography, X-ray diffraction reveals stored structure
without destroying it. Our substrate's Walsh-Hadamard transform of W is the
direct analog: each stored (v_k, k_k) outer product produces a "Bragg peak"
at the Walsh-frequency dual to k_k.

This experiment quantifies the analog:
  - Train W with K known patterns
  - Compute WHT of W (treated as N x N matrix - row-wise WHT)
  - Find the K largest spectral coefficients
  - Measure: peak SNR (signal vs background) vs K

Predictions:
  - K << alpha_c * N: K peaks visible above flat background
  - K ~ alpha_c * N: peaks broaden, background rises (glass transition signature)
  - K >> alpha_c * N: spectrum becomes random (no resolvable peaks)

Pre-reg: preregs/2026-05-20_wave14xrd_walsh_spectrum.md
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
from pathlib import Path

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))


def get_output_dir(default_name: str) -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d: dict) -> None:
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    if not all(k in d for k in required):
        raise ValueError("missing required fields")
    if not d.get("verdict") or not d.get("verdict_msg"):
        raise ValueError("empty verdict")


def compute_verdict(summary: dict) -> tuple[str, str]:
    rows = summary.get("per_K", [])
    if not rows:
        return ("XRD_INCONCLUSIVE", "No per-K data.")
    # Detect transition: K-range where peak_SNR drops below 2.0
    snrs = [(r["K"], r["peak_snr"]) for r in rows]
    snrs.sort()
    transition_K = None
    for i in range(len(snrs) - 1):
        if snrs[i][1] >= 2.0 and snrs[i+1][1] < 2.0:
            transition_K = (snrs[i][0] + snrs[i+1][0]) / 2
            break
    if transition_K is not None:
        N = rows[0]["N"]
        return ("XRD_TRANSITION_FOUND",
                f"Spectral SNR drops below 2.0 at K~{transition_K:.0f} (K/N={transition_K/N:.3f}). "
                f"This is the 'amorphous transition' in Walsh basis - substrate "
                f"loses crystalline diffraction pattern when load exceeds threshold. "
                f"Compare to alpha_c=0.138 (AGS) and measured 0.153 (wave14m).")
    all_high = all(r["peak_snr"] >= 2.0 for r in rows)
    all_low = all(r["peak_snr"] < 2.0 for r in rows)
    if all_high:
        return ("XRD_ALL_CRYSTALLINE",
                f"All tested K maintain SNR>=2.0. Substrate stays crystalline "
                f"throughout tested range; expand K-grid upward.")
    if all_low:
        return ("XRD_NO_PEAKS",
                f"No K shows SNR>=2.0. Substrate is amorphous from start - "
                f"unexpected. Test setup likely broken.")
    return ("XRD_NONMONOTONIC",
            f"SNR not monotonically decreasing. Per-K: " +
            ", ".join(f"K={r['K']}: snr={r['peak_snr']:.2f}" for r in rows[:5]))


def self_test_verdict() -> None:
    base_N = 4096
    cases = [
        ({"per_K": [{"K": 50, "N": base_N, "peak_snr": 5.0},
                    {"K": 200, "N": base_N, "peak_snr": 3.0},
                    {"K": 500, "N": base_N, "peak_snr": 1.5},
                    {"K": 1000, "N": base_N, "peak_snr": 1.0}]}, "XRD_TRANSITION_FOUND"),
        ({"per_K": [{"K": 50, "N": base_N, "peak_snr": 5.0}]}, "XRD_ALL_CRYSTALLINE"),
        ({"per_K": [{"K": 500, "N": base_N, "peak_snr": 0.5}]}, "XRD_NO_PEAKS"),
        ({"per_K": []}, "XRD_INCONCLUSIVE"),
    ]
    for s, expected in cases:
        actual, _ = compute_verdict(s)
        if actual != expected:
            raise AssertionError(f"FAIL: {actual} != {expected} for {s}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def fast_walsh_hadamard(x: torch.Tensor) -> torch.Tensor:
    """In-place FWHT along last dim. N must be power of 2."""
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


def measure_spectrum(N, K, seeds, device) -> dict:
    """For K random patterns, build W, compute WHT spectrum of W's rows.
    Return peak-SNR averaged over seeds.
    """
    snrs = []
    for seed in seeds:
        gen = torch.Generator().manual_seed(seed)
        keys = 2.0 * (torch.rand((K, N), generator=gen) > 0.5).float() - 1.0
        values = 2.0 * (torch.rand((K, N), generator=gen) > 0.5).float() - 1.0
        keys = keys.to(device)
        values = values.to(device)
        W = (values.T @ keys) / N

        # WHT of each row of W. W is (N, N) but for tractability we WHT all rows.
        W_walsh = fast_walsh_hadamard(W.clone())
        # Each "Bragg peak" in row r appears at the Walsh-frequency dual to k_j
        # if v_j[r] is nonzero. So spectrum magnitudes per (row, freq) cell.
        spec = W_walsh.abs()  # (N, N)
        # Aggregate: per-frequency mean magnitude across rows
        per_freq = spec.mean(dim=0)  # (N,) - mean spectral magnitude per Walsh frequency
        # Top-K peaks vs background
        sorted_vals = per_freq.sort(descending=True).values
        peak_mean = sorted_vals[:K].mean().item()
        bg_mean = sorted_vals[K:].mean().item()
        snr = peak_mean / max(bg_mean, 1e-9)
        snrs.append(snr)
    mean_snr = sum(snrs) / len(snrs)
    return {"K": K, "N": N, "peak_snr": mean_snr, "per_seed_snr": snrs}


def main(smoke: bool = False) -> None:
    self_test_verdict()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if smoke:
        config = {"mode": "smoke", "N": 512, "K_list": [20, 100, 300],
                  "seeds": [17]}
    else:
        config = {"mode": "full", "N": 4096,
                  "K_list": [50, 100, 200, 400, 600, 900, 1300, 2000, 3000],
                  "seeds": [17, 23, 31, 41, 53]}
    print(f"wave14xrd_walsh_spectrum. mode={config['mode']} device={device}", flush=True)
    print(f"  N={config['N']} K_list={config['K_list']} seeds={config['seeds']}", flush=True)

    t0 = time.monotonic()
    per_K = []
    for K in config["K_list"]:
        r = measure_spectrum(config["N"], K, config["seeds"], device)
        per_K.append(r)
        print(f"  K={K:5d} (K/N={K/config['N']:.3f})  peak_snr={r['peak_snr']:.3f}", flush=True)
    elapsed = time.monotonic() - t0

    summary = {"per_K": per_K}
    verdict, msg = compute_verdict(summary)
    print(f"\n=== {verdict} ===\n{msg}", flush=True)
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
               "config": config, "device": str(device),
               "per_K": per_K, "summary": summary}
    validate_metrics(metrics)
    out_dir = get_output_dir("wave14xrd_walsh_spectrum")
    tmp = (out_dir / "metrics.json").with_suffix(".tmp")
    tmp.write_text(json.dumps(metrics, indent=2))
    os.replace(tmp, out_dir / "metrics.json")
    print(f"wrote {out_dir / 'metrics.json'}", flush=True)


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test_verdict()
        sys.exit(0)
    main(smoke="--smoke" in sys.argv)
