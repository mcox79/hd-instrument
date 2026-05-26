"""WHT diffraction pattern with STRUCTURED keys (Hadamard rows) vs random.

wave14xrd_walsh_spectrum with random keys gave NO_PEAKS (SNR<2 everywhere).
This matches Agent 1's prediction: 'random +/-1 destroys spectral structure'.
The substrate is amorphous-in-Walsh with random keys, crystalline-in-Walsh
with structured (Hadamard) keys.

This experiment tests THAT specific claim: bundle K codewords drawn from
the Hadamard basis, build W = sum v_k k_k^T, compute WHT, look for K Bragg
peaks at specific Walsh frequencies (the rows of H_N dual to each k).

Substantially larger config to actually use the GPU.

Pre-reg: preregs/2026-05-20_wave14xrd_structured_keys.md
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
        raise ValueError("missing")
    if not d.get("verdict") or not d.get("verdict_msg"):
        raise ValueError("empty")


def compute_verdict(summary: dict) -> tuple[str, str]:
    by = summary.get("by_keys", {})
    if not by:
        return ("XRD2_INCONCLUSIVE", "No data.")
    rnd = by.get("random", {})
    had = by.get("hadamard", {})
    rnd_K_trans = rnd.get("transition_K")
    had_K_trans = had.get("transition_K")
    rnd_snr_max = rnd.get("max_snr", 0)
    had_snr_max = had.get("max_snr", 0)
    if had_snr_max >= 5.0 and rnd_snr_max < 2.0:
        return ("XRD2_STRUCTURED_WINS_CLEAR",
                f"Hadamard keys give Bragg peaks (max SNR={had_snr_max:.1f}); "
                f"random keys are amorphous (max SNR={rnd_snr_max:.1f}). "
                f"Crystallography analogy holds: structured keys = crystalline, "
                f"random = amorphous glass. Materials prediction validated.")
    if had_snr_max >= 2.0 and rnd_snr_max < 2.0:
        return ("XRD2_STRUCTURED_WINS",
                f"Hadamard keys give resolvable peaks (max SNR={had_snr_max:.1f}); "
                f"random doesn't ({rnd_snr_max:.1f}). Crystalline-vs-amorphous "
                f"distinction holds, but Hadamard peak prominence is modest.")
    if had_snr_max < 2.0 and rnd_snr_max < 2.0:
        return ("XRD2_BOTH_AMORPHOUS",
                f"Neither has SNR >= 2 (had={had_snr_max:.1f}, rnd={rnd_snr_max:.1f}). "
                f"The W matrix structure doesn't produce Walsh-domain Bragg peaks "
                f"under our test setup. Walsh basis may not be the right diffraction "
                f"basis for this substrate.")
    return ("XRD2_UNEXPECTED",
            f"random snr_max={rnd_snr_max:.1f}, hadamard snr_max={had_snr_max:.1f}.")


def self_test_verdict() -> None:
    cases = [
        ({"by_keys": {"random": {"max_snr": 1.2}, "hadamard": {"max_snr": 8.0}}},
         "XRD2_STRUCTURED_WINS_CLEAR"),
        ({"by_keys": {"random": {"max_snr": 1.2}, "hadamard": {"max_snr": 3.0}}},
         "XRD2_STRUCTURED_WINS"),
        ({"by_keys": {"random": {"max_snr": 1.2}, "hadamard": {"max_snr": 1.5}}},
         "XRD2_BOTH_AMORPHOUS"),
        ({"by_keys": {}}, "XRD2_INCONCLUSIVE"),
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


def measure_spectrum(N, K, key_source, n_trials, seeds, device, H=None):
    """For K random selections of keys + random values, build W, compute WHT
    spectrum, return mean and max SNR.
    """
    snrs = []
    peak_locs = []
    for trial in range(n_trials):
        for seed in seeds:
            gen = torch.Generator().manual_seed(seed * 17 + trial * 31 + K)
            if key_source == "random":
                keys = 2.0 * (torch.rand((K, N), generator=gen) > 0.5).float() - 1.0
            else:  # hadamard
                # Random selection of K rows from the Hadamard matrix
                row_idx = torch.randperm(N, generator=gen)[:K]
                keys = H[row_idx].clone()
            values = 2.0 * (torch.rand((K, N), generator=gen) > 0.5).float() - 1.0
            keys = keys.to(device)
            values = values.to(device)
            W = (values.T @ keys) / N
            W_walsh = fast_walsh_hadamard(W.clone())
            spec = W_walsh.abs()
            per_freq = spec.mean(dim=0)
            sorted_vals = per_freq.sort(descending=True).values
            peak_mean = sorted_vals[:K].mean().item()
            bg_mean = sorted_vals[K:].mean().item()
            snr = peak_mean / max(bg_mean, 1e-9)
            snrs.append(snr)
    return {"K": K, "N": N, "key_source": key_source,
            "mean_snr": sum(snrs) / len(snrs),
            "max_snr": max(snrs), "min_snr": min(snrs)}


def main(smoke: bool = False) -> None:
    self_test_verdict()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if smoke:
        config = {"mode": "smoke", "N": 512, "K_list": [50, 150, 300],
                  "n_trials": 3, "seeds": [17]}
    else:
        # Substantial: many K values, many seeds, multiple trials
        config = {"mode": "full", "N": 4096,
                  "K_list": [50, 100, 200, 400, 600, 900, 1300, 2000, 3000],
                  "n_trials": 10, "seeds": [17, 23, 31, 41, 53, 67, 79, 89]}
    print(f"wave14xrd_structured_keys. mode={config['mode']} device={device}", flush=True)
    print(f"  N={config['N']} K_list={config['K_list']} seeds={config['seeds']} "
          f"trials/seed={config['n_trials']}", flush=True)

    print(f"  Building Hadamard matrix N={config['N']}...", flush=True)
    H = hadamard_matrix(config["N"]).to(device)

    t0 = time.monotonic()
    by_keys = {"random": {"per_K": []}, "hadamard": {"per_K": []}}
    for source in ["random", "hadamard"]:
        print(f"  --- {source} ---", flush=True)
        for K in config["K_list"]:
            r = measure_spectrum(config["N"], K, source, config["n_trials"],
                                  config["seeds"], device, H=H)
            by_keys[source]["per_K"].append(r)
            print(f"    K={K:5d}  mean_snr={r['mean_snr']:.2f}  max_snr={r['max_snr']:.2f}",
                  flush=True)
        # transition_K and max_snr summary
        snrs = [(p["K"], p["mean_snr"]) for p in by_keys[source]["per_K"]]
        max_snr = max(p["max_snr"] for p in by_keys[source]["per_K"])
        transition_K = None
        for i in range(len(snrs) - 1):
            if snrs[i][1] >= 2.0 and snrs[i+1][1] < 2.0:
                transition_K = (snrs[i][0] + snrs[i+1][0]) / 2
                break
        by_keys[source]["transition_K"] = transition_K
        by_keys[source]["max_snr"] = max_snr
    elapsed = time.monotonic() - t0

    summary = {"by_keys": by_keys}
    verdict, msg = compute_verdict(summary)
    print(f"\n=== {verdict} ===\n{msg}", flush=True)
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
               "config": config, "device": str(device),
               "by_keys": by_keys, "summary": summary}
    validate_metrics(metrics)
    out_dir = get_output_dir("wave14xrd_structured_keys")
    tmp = (out_dir / "metrics.json").with_suffix(".tmp")
    tmp.write_text(json.dumps(metrics, indent=2))
    os.replace(tmp, out_dir / "metrics.json")
    print(f"wrote {out_dir / 'metrics.json'}", flush=True)


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test_verdict()
        sys.exit(0)
    main(smoke="--smoke" in sys.argv)
