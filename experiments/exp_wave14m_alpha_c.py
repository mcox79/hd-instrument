"""Substrate alpha_c characterization — what's our actual critical capacity?

Three research agents independently converged on the diagnosis: multiple
"negatives" from waves 14i/j/k are partly explained by operating above the
critical Hopfield capacity alpha_c. AGS (1985) predicts alpha_c ~= 0.138 for
random patterns + Hebbian outer-product. Our system uses sum-bundling + cosine
cleanup, which has a different (lower) alpha_c set by the binomial SNR floor.

This experiment measures K* (the K at which recovery probability crosses 0.5)
across N, then estimates alpha_c = K*/N and its scaling. The whole synthesis
of negatives depends on knowing this number for OUR substrate.

Pre-registration: preregs/2026-05-20_wave14m_alpha_c.md

Rigor protocol (this script is the template for future experiments):
  - Output dir resolved from HDLAB_EXP_NAME env var (no hardcoded names)
  - Verdict logic has a self-test that runs before the experiment
  - metrics.json is schema-validated before write
  - --smoke flag runs smallest config in ~15s to verify infra end-to-end
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
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required fields: {missing}")
    if d["verdict"] is None or d["verdict"] == "":
        raise ValueError("verdict must not be empty")
    if not isinstance(d["verdict_msg"], str) or not d["verdict_msg"]:
        raise ValueError("verdict_msg must be non-empty string")


def compute_verdict(summary: dict) -> tuple[str, str]:
    """Verdict logic separated for testability.

    Returns (verdict, message). Decision rules:
      - If NO N found K*: INCONCLUSIVE
      - Otherwise, use the LARGEST N where K* was located. Label by where
        alpha_c sits AND by the trend across N.
    """
    by_N = summary.get("alpha_c_all_N", [])
    found = [(p["N"], p["alpha_c"]) for p in by_N if p["alpha_c"] is not None]
    if not found:
        return ("ALPHA_C_INCONCLUSIVE",
                "Could not locate K* (50% recovery) at ANY N. Grid was too narrow "
                "for the cliff at every tested N. Extend K_factor_grid upward.")
    largest_N_found, alpha_c = found[-1]
    largest_N_overall = by_N[-1]["N"]
    coverage = f"K* located at {len(found)}/{len(by_N)} N values (largest with K*: N={largest_N_found})."
    if largest_N_found < largest_N_overall:
        coverage += f" Larger N={largest_N_overall} did not cross 0.5 in grid."
    slope = summary.get("scaling_slope_loglog")
    # Detect trend in alpha_c across N
    if len(found) >= 2:
        first_alpha = found[0][1]
        trend = "rising" if alpha_c > first_alpha * 1.15 else (
                "falling" if alpha_c < first_alpha * 0.85 else "flat")
    else:
        trend = "single-point"
    trend_note = (f" alpha_c trend across N: {trend} "
                  f"({[f'{p[1]:.3f}' for p in found]}).")

    if alpha_c > 0.25:
        return ("ALPHA_C_ANOMALOUS_HIGH",
                f"alpha_c={alpha_c:.4f} > 0.25 at N={largest_N_found}, above AGS "
                f"Hopfield 0.138. Likely codebook-too-small or test too easy. "
                f"{coverage}{trend_note}")
    if 0.10 <= alpha_c <= 0.18:
        return ("ALPHA_C_AGS_LIKE",
                f"alpha_c={alpha_c:.4f} at N={largest_N_found}, in AGS Hopfield "
                f"range [0.10, 0.18]. Spin-glass theory applies directly. "
                f"Slope={slope}. {coverage}{trend_note}")
    if 0.01 <= alpha_c < 0.10:
        regime = "SNR_LIMITED" if (slope is not None and 0.85 <= slope <= 1.15) else "BUNDLE"
        return (f"ALPHA_C_{regime}",
                f"alpha_c={alpha_c:.4f} at N={largest_N_found} (below AGS 0.138). "
                f"Slope={slope}. Bundle-cleanup regime; cleanup is the bottleneck, "
                f"not pattern storage. {coverage}{trend_note}")
    return ("ALPHA_C_ANOMALOUS_LOW",
            f"alpha_c={alpha_c:.4f} at N={largest_N_found}, < 0.01. Suspiciously "
            f"low. {coverage}{trend_note}")


def self_test_verdict() -> None:
    """Run before the real experiment. If verdict logic is buggy, abort early.

    Each case provides the by-N alpha_c list (mimicking summary["alpha_c_all_N"]).
    Includes the failure mode found in production: smaller N's had K*, largest
    N didn't, old logic crashed to INCONCLUSIVE hiding the data.
    """
    def mk(*pairs):
        return {"alpha_c_all_N": [{"N": n, "alpha_c": a} for n, a in pairs]}
    cases = [
        # SNR_LIMITED: small alpha_c, slope ~ 1
        ({**mk((1024, 0.04), (2048, 0.038), (4096, 0.037)), "scaling_slope_loglog": 1.0},
         "ALPHA_C_SNR_LIMITED"),
        # BUNDLE: small alpha_c, non-linear slope
        ({**mk((1024, 0.03), (4096, 0.03)), "scaling_slope_loglog": 0.4},
         "ALPHA_C_BUNDLE"),
        # AGS_LIKE: alpha_c in [0.10, 0.18]
        ({**mk((4096, 0.122)), "scaling_slope_loglog": 0.6}, "ALPHA_C_AGS_LIKE"),
        # ANOMALOUS_HIGH
        ({**mk((512, 0.78)), "scaling_slope_loglog": 0.3}, "ALPHA_C_ANOMALOUS_HIGH"),
        # ANOMALOUS_LOW
        ({**mk((4096, 0.003)), "scaling_slope_loglog": 0.9}, "ALPHA_C_ANOMALOUS_LOW"),
        # INCONCLUSIVE: no N found K*
        ({"alpha_c_all_N": [{"N": 1024, "alpha_c": None}, {"N": 2048, "alpha_c": None}]},
         "ALPHA_C_INCONCLUSIVE"),
        # Production bug: largest N didn't find K*, smaller N's did. Old logic
        # crashed to INCONCLUSIVE. New logic uses largest N WHERE K* was found.
        ({"alpha_c_all_N": [
            {"N": 1024, "alpha_c": 0.082},
            {"N": 2048, "alpha_c": 0.107},
            {"N": 4096, "alpha_c": 0.153},
            {"N": 8192, "alpha_c": None},
         ], "scaling_slope_loglog": None},
         "ALPHA_C_AGS_LIKE"),
    ]
    for summary, expected in cases:
        actual, _ = compute_verdict(summary)
        if actual != expected:
            raise AssertionError(
                f"verdict self-test FAILED: input {summary} -> {actual}, expected {expected}"
            )
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def measure_recovery(N: int, K: int, n_trials: int, gen: torch.Generator,
                     device: torch.device, M: int = 4096) -> float:
    """Canonical bundle-cleanup capacity test (Plate / Kanerva).

    Build a FIXED-SIZE codebook of M random +/-1 atoms. Bundle the first K of
    them (signed sum). Rank all M atoms by inner product with bundle; take
    top-K; measure |top-K intersect stored| / K. K* is where mean recall
    crosses 0.5.

    M must be fixed (not scaling with K) so the noise floor stays constant
    across the K-sweep. Plate's prediction: K* ~= N / (2 ln(2M / delta)).
    """
    if M < 2 * K:
        # K too large for this codebook; recovery is trivially limited.
        return 0.0
    total_recall = 0.0
    for _ in range(n_trials):
        codebook = (2.0 * (torch.rand((M, N), generator=gen, device=device) > 0.5).float() - 1.0)
        bundle = codebook[:K].sum(dim=0)
        bundle = torch.sign(bundle)
        bundle = torch.where(bundle == 0, torch.ones_like(bundle), bundle)
        scores = codebook @ bundle  # length M
        top_k_idx = torch.topk(scores, K).indices.tolist()
        recovered = sum(1 for i in top_k_idx if i < K)
        total_recall += recovered / K
    return total_recall / n_trials


def find_k_star(N: int, K_grid: list[int], seeds: list[int], n_trials: int,
                device: torch.device, M: int, verbose: bool = False
                ) -> tuple[float | None, list[dict]]:
    """Sweep K_grid for given N. Return K* via linear interp at p=0.5, plus per-K data."""
    rows = []
    for K in K_grid:
        recoveries = []
        for seed in seeds:
            gen = torch.Generator(device=device).manual_seed(seed + 1000 * K + 7919 * N)
            recoveries.append(measure_recovery(N, K, n_trials, gen, device, M=M))
        mean_recovery = sum(recoveries) / len(recoveries)
        rows.append({"K": K, "K_over_N": K / N, "mean_recovery": mean_recovery,
                     "per_seed": recoveries})
        if verbose:
            print(f"    N={N} K={K:5d} (K/N={K/N:.3f})  recovery={mean_recovery:.3f}", flush=True)
    # linear interp K at recovery=0.5
    k_star = None
    for i in range(len(rows) - 1):
        a, b = rows[i], rows[i + 1]
        if a["mean_recovery"] >= 0.5 >= b["mean_recovery"]:
            # interp
            if a["mean_recovery"] == b["mean_recovery"]:
                k_star = float(a["K"])
            else:
                frac = (a["mean_recovery"] - 0.5) / (a["mean_recovery"] - b["mean_recovery"])
                k_star = float(a["K"] + frac * (b["K"] - a["K"]))
            break
    return k_star, rows


def main(smoke: bool = False) -> None:
    self_test_verdict()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    if smoke:
        config = {
            "mode": "smoke",
            "N_list": [256, 512],
            "K_factor_grid": [0.005, 0.01, 0.02, 0.04, 0.08, 0.15, 0.30],
            "seeds": [17],
            "n_trials": 5,
            "M": 1024,
        }
    else:
        config = {
            "mode": "full",
            "N_list": [1024, 2048, 4096, 8192],
            "K_factor_grid": [0.005, 0.01, 0.02, 0.03, 0.04, 0.06, 0.08, 0.10,
                              0.13, 0.16, 0.20, 0.25, 0.30, 0.40],
            "seeds": [17, 23, 31, 41, 53],
            "n_trials": 20,
            "M": 16384,
        }
    print(f"alpha_c characterization. mode={config['mode']}, device={device}", flush=True)
    print(f"  N_list={config['N_list']}", flush=True)
    print(f"  K_factor_grid={config['K_factor_grid']}", flush=True)
    print(f"  seeds={config['seeds']}, n_trials={config['n_trials']}", flush=True)

    t0 = time.monotonic()
    per_N = []
    for N in config["N_list"]:
        K_grid = sorted({max(2, int(round(N * f))) for f in config["K_factor_grid"]})
        print(f"  N={N}, K_grid={K_grid}", flush=True)
        k_star, rows = find_k_star(N, K_grid, config["seeds"], config["n_trials"],
                                   device, M=config["M"], verbose=True)
        per_N.append({"N": N, "K_grid": K_grid, "k_star": k_star,
                      "alpha_c": (k_star / N) if k_star is not None else None,
                      "sweep": rows})
        print(f"  -> K*(N={N}) = {k_star}, alpha_c = "
              f"{(k_star/N if k_star else None)}", flush=True)
    elapsed = time.monotonic() - t0

    # Estimate scaling: log K* vs log N
    valid = [(p["N"], p["k_star"]) for p in per_N if p["k_star"] is not None]
    if len(valid) >= 2:
        xs = [math.log(n) for n, _ in valid]
        ys = [math.log(k) for _, k in valid]
        n_pts = len(xs)
        x_mean = sum(xs) / n_pts
        y_mean = sum(ys) / n_pts
        num = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
        den = sum((x - x_mean) ** 2 for x in xs)
        slope = num / den if den > 0 else None
    else:
        slope = None

    alpha_c_largest = per_N[-1]["alpha_c"] if per_N else None
    summary = {
        "alpha_c_largest_N": alpha_c_largest,
        "alpha_c_all_N": [{"N": p["N"], "alpha_c": p["alpha_c"]} for p in per_N],
        "scaling_slope_loglog": slope,
        "ags_prediction": 0.138,
        "snr_floor_prediction": (
            f"K* ~= N / (2 ln(2N/0.01)); at N=4096 -> "
            f"{4096 / (2 * math.log(2*4096/0.01)):.1f}"
        ),
    }

    verdict, msg = compute_verdict(summary)
    print(f"\n=== {verdict} ===\n{msg}", flush=True)

    metrics = {
        "verdict": verdict,
        "verdict_msg": msg,
        "elapsed_s": elapsed,
        "config": config,
        "device": str(device),
        "per_N": per_N,
        "summary": summary,
    }
    validate_metrics(metrics)

    out_dir = get_output_dir("wave14m_alpha_c")
    metrics_path = out_dir / "metrics.json"
    tmp = metrics_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(metrics, indent=2))
    os.replace(tmp, metrics_path)
    print(f"\nwrote {metrics_path}", flush=True)


if __name__ == "__main__":
    smoke = "--smoke" in sys.argv
    if "--self-test" in sys.argv:
        self_test_verdict()
        sys.exit(0)
    main(smoke=smoke)
