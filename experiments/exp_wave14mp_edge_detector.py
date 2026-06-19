"""MP edge as substrate phase detector (from crystallography research finding).

Materials-science prediction: the Marchenko-Pastur edge of W's spectrum
distinguishes the substrate's phase regimes WITHOUT querying.
  rho = lambda_+_empirical / lambda_+_MP(gamma=K/N)
where lambda_+_MP = (1 + sqrt(K/N))^2.

Predictions per the research:
  - Paracrystalline (K << alpha_c*N): rho >> 1 (planted memory eigvals above bulk)
  - Glassy/amorphous (K ~ alpha_c*N): rho ~= 1 (perfect MP match)
  - Overloaded spin-glass (K >> alpha_c*N): rho < 1 (bulk softening)
  - Sigmoid transition midpoint should fall at K = alpha_c * N = 627 (for our N=4096)

This is a SUBSTRATE FORENSICS PRIMITIVE: detect phase without queries.

Pre-reg: preregs/2026-05-20_wave14mp_edge_detector.md
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
    rows = summary.get("per_K", [])
    if not rows:
        return ("MPEDGE_INCONCLUSIVE", "No data.")
    # Find sigmoid transition midpoint: K where rho crosses 1.0
    rhos = [(r["K"], r["rho"]) for r in rows]
    rhos.sort()
    transition_K = None
    for i in range(len(rhos) - 1):
        if rhos[i][1] >= 1.0 >= rhos[i+1][1]:
            if rhos[i][1] == rhos[i+1][1]:
                transition_K = float(rhos[i][0])
            else:
                frac = (rhos[i][1] - 1.0) / (rhos[i][1] - rhos[i+1][1])
                transition_K = rhos[i][0] + frac * (rhos[i+1][0] - rhos[i][0])
            break
    if transition_K is None:
        return ("MPEDGE_NO_TRANSITION",
                f"rho never crosses 1.0 in tested K range. " +
                ", ".join(f"K={r['K']}: rho={r['rho']:.2f}" for r in rows[:5]))
    N = rows[0]["N"]
    predicted_kc = 0.153 * N  # using our measured alpha_c
    deviation = (transition_K - predicted_kc) / predicted_kc
    if abs(deviation) < 0.15:
        return ("MPEDGE_PHASE_DETECTOR_VALIDATED",
                f"rho=1.0 transition at K~{transition_K:.0f} (K/N={transition_K/N:.3f}). "
                f"Predicted alpha_c*N = {predicted_kc:.0f} (deviation {deviation:+.1%}). "
                f"MP edge directly detects AGS phase transition - substrate "
                f"forensics primitive works.")
    return ("MPEDGE_DEVIATES",
            f"rho=1.0 at K~{transition_K:.0f} (K/N={transition_K/N:.3f}); "
            f"predicted {predicted_kc:.0f}. Deviation {deviation:+.1%} > 15%. "
            f"Either alpha_c is different or MP-edge analog needs refinement.")


def self_test_verdict() -> None:
    cases = [
        ({"per_K": [{"K": 100, "N": 4096, "rho": 5.0},
                    {"K": 627, "N": 4096, "rho": 1.0},
                    {"K": 2000, "N": 4096, "rho": 0.3}]},
         "MPEDGE_PHASE_DETECTOR_VALIDATED"),
        ({"per_K": [{"K": 100, "N": 4096, "rho": 5.0},
                    {"K": 1500, "N": 4096, "rho": 1.0},
                    {"K": 2000, "N": 4096, "rho": 0.3}]},
         "MPEDGE_DEVIATES"),
        ({"per_K": [{"K": 100, "N": 4096, "rho": 5.0}]},
         "MPEDGE_NO_TRANSITION"),
        ({"per_K": []}, "MPEDGE_INCONCLUSIVE"),
    ]
    for s, expected in cases:
        actual, _ = compute_verdict(s)
        if actual != expected:
            raise AssertionError(f"FAIL: {actual} != {expected} for {s}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def measure_rho(N, K, seeds, device):
    """For random ±1 keys + values at given (N, K), build W, compute SVD,
    measure rho = lambda_+_empirical / lambda_+_MP.
    """
    rhos = []
    lambda_plus_mps = []
    lambda_plus_empiricals = []
    gamma = K / N
    lambda_plus_mp = (1 + math.sqrt(gamma)) ** 2
    for seed in seeds:
        gen = torch.Generator().manual_seed(seed * 11 + K)
        keys = 2.0 * (torch.rand((K, N), generator=gen) > 0.5).float() - 1.0
        values = 2.0 * (torch.rand((K, N), generator=gen) > 0.5).float() - 1.0
        keys = keys.to(device)
        values = values.to(device)
        # MP analysis on W / sqrt(K) so empirical bulk matches MP gamma=K/N
        W = (values.T @ keys) / math.sqrt(K)  # normalize by sqrt(K) for MP scaling
        # Top eigenvalue of W^T W / N (which has MP spectrum)
        cov = (W @ W.T) / N  # (N, N)
        # Use eigvalsh for symmetric matrix; top eigenvalue
        eigs = torch.linalg.eigvalsh(cov)
        lambda_plus_emp = float(eigs.max())
        rho = lambda_plus_emp / lambda_plus_mp
        rhos.append(rho)
        lambda_plus_mps.append(lambda_plus_mp)
        lambda_plus_empiricals.append(lambda_plus_emp)
    return {"K": K, "N": N, "gamma": gamma,
            "lambda_plus_mp": lambda_plus_mp,
            "lambda_plus_empirical_mean": sum(lambda_plus_empiricals) / len(lambda_plus_empiricals),
            "rho": sum(rhos) / len(rhos),
            "per_seed_rho": rhos}


def main(smoke: bool = False) -> None:
    self_test_verdict()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if smoke:
        config = {"mode": "smoke", "N": 512,
                  "K_list": [50, 200, 500],
                  "seeds": [17]}
    else:
        # Substantial: many K values, many seeds for tight CIs
        config = {"mode": "full", "N": 4096,
                  "K_list": [50, 100, 200, 350, 500, 627, 800, 1200, 1800, 2500, 3500],
                  "seeds": [17, 23, 31, 41, 53, 67, 79, 89, 101, 113, 127, 137]}
    print(f"wave14mp_edge_detector. mode={config['mode']} device={device}", flush=True)
    print(f"  N={config['N']} K_list={config['K_list']}", flush=True)
    print(f"  seeds={len(config['seeds'])} replicates", flush=True)

    t0 = time.monotonic()
    per_K = []
    for K in config["K_list"]:
        r = measure_rho(config["N"], K, config["seeds"], device)
        per_K.append(r)
        print(f"  K={K:5d} (K/N={K/config['N']:.3f})  gamma={r['gamma']:.3f}  "
              f"lambda_+_MP={r['lambda_plus_mp']:.3f}  lambda_+_emp={r['lambda_plus_empirical_mean']:.3f}  "
              f"rho={r['rho']:.3f}", flush=True)
    elapsed = time.monotonic() - t0

    summary = {"per_K": per_K}
    verdict, msg = compute_verdict(summary)
    print(f"\n=== {verdict} ===\n{msg}", flush=True)
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
               "config": config, "device": str(device),
               "per_K": per_K, "summary": summary}
    validate_metrics(metrics)
    out_dir = get_output_dir("wave14mp_edge_detector")
    tmp = (out_dir / "metrics.json").with_suffix(".tmp")
    tmp.write_text(json.dumps(metrics, indent=2))
    os.replace(tmp, out_dir / "metrics.json")
    print(f"wrote {out_dir / 'metrics.json'}", flush=True)


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test_verdict()
        sys.exit(0)
    main(smoke="--smoke" in sys.argv)
