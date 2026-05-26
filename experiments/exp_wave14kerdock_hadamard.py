"""Crystalline vs amorphous codebooks: Hadamard (orthogonal) vs random +/-1.

Direct test of the materials science prediction (Agent 1):
  Random +/-1 codebook = "amorphous glass" (coherence ~ 1/sqrt(N))
  Hadamard matrix codebook = "crystalline orthogonal frame" (coherence = 0)

For M=N codewords, Hadamard is the SIMPLEST possible Welch-bound-meeting
codebook. This is a lower-bound test of Agent 1's full Kerdock claim.

Test: store K codewords as a bundle; query each; measure top-K recovery
against the full codebook. Sweep K.

Predicted: Hadamard gives 2x higher K* than random +/-1 at fixed recall.

Pre-reg: preregs/2026-05-20_wave14kerdock_hadamard.md
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
    by = summary.get("by_codebook", {})
    if not by:
        return ("CODEBOOK_INCONCLUSIVE", "No data.")
    rnd = by.get("random", {})
    had = by.get("hadamard", {})
    rnd_k = rnd.get("k_star")
    had_k = had.get("k_star")
    if rnd_k is None and had_k is None:
        return ("CODEBOOK_INCONCLUSIVE", "Neither codebook located K*.")
    if rnd_k is None:
        return ("CODEBOOK_HADAMARD_DOMINATES",
                f"Hadamard K*={had_k:.0f}; random never crossed 0.5 threshold.")
    if had_k is None:
        return ("CODEBOOK_ANOMALOUS",
                f"Random K*={rnd_k:.0f} but Hadamard never crossed 0.5. Unexpected.")
    ratio = had_k / rnd_k
    if ratio >= 1.5:
        return ("CODEBOOK_HADAMARD_WINS",
                f"Hadamard K*={had_k:.0f} vs random K*={rnd_k:.0f} ({ratio:.2f}x). "
                f"Crystalline codebook gives meaningful capacity gain. "
                f"Materials prediction holds.")
    if 0.85 <= ratio <= 1.15:
        return ("CODEBOOK_TIE",
                f"Hadamard K*={had_k:.0f} ~ random K*={rnd_k:.0f}. No capacity "
                f"gain from orthogonality at this scale.")
    if ratio >= 1.1:
        return ("CODEBOOK_HADAMARD_MARGINAL",
                f"Hadamard K*={had_k:.0f} vs random K*={rnd_k:.0f} ({ratio:.2f}x). "
                f"Small win.")
    return ("CODEBOOK_RANDOM_WINS",
            f"Random K*={rnd_k:.0f} > Hadamard K*={had_k:.0f} ({ratio:.2f}x). "
            f"Counter to prediction; investigate.")


def self_test_verdict() -> None:
    cases = [
        ({"by_codebook": {"random": {"k_star": 100}, "hadamard": {"k_star": 200}}},
         "CODEBOOK_HADAMARD_WINS"),
        ({"by_codebook": {"random": {"k_star": 100}, "hadamard": {"k_star": 105}}},
         "CODEBOOK_TIE"),
        ({"by_codebook": {"random": {"k_star": 100}, "hadamard": {"k_star": 120}}},
         "CODEBOOK_HADAMARD_MARGINAL"),
        ({"by_codebook": {"random": {"k_star": 200}, "hadamard": {"k_star": 100}}},
         "CODEBOOK_RANDOM_WINS"),
        ({"by_codebook": {}}, "CODEBOOK_INCONCLUSIVE"),
    ]
    for s, expected in cases:
        actual, _ = compute_verdict(s)
        if actual != expected:
            raise AssertionError(f"FAIL: {actual} != {expected} for {s}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def hadamard_matrix(n: int) -> torch.Tensor:
    """Sylvester construction of n x n Hadamard matrix. n must be power of 2."""
    assert (n & (n - 1)) == 0, "n must be power of 2"
    H = torch.tensor([[1.0]])
    while H.size(0) < n:
        H = torch.cat([torch.cat([H, H], dim=1), torch.cat([H, -H], dim=1)], dim=0)
    return H


def random_codebook(M: int, N: int, gen) -> torch.Tensor:
    return 2.0 * (torch.rand((M, N), generator=gen) > 0.5).float() - 1.0


def measure_recovery(codebook, K, n_trials, gen):
    """Bundle first K codewords; rank all M by similarity to bundle; recall = top-K hits."""
    M, N = codebook.shape
    device = codebook.device
    total_recall = 0.0
    for _ in range(n_trials):
        # Random subset of K codewords from the codebook
        idx = torch.randperm(M, generator=gen)[:K].tolist()
        idx_set = set(idx)
        bundle_raw = codebook[idx].sum(dim=0)
        bundle = torch.sign(bundle_raw)
        bundle = torch.where(bundle == 0, torch.ones_like(bundle), bundle)
        scores = codebook @ bundle
        top_k = torch.topk(scores, K).indices.tolist()
        recovered = sum(1 for i in top_k if i in idx_set)
        total_recall += recovered / K
    return total_recall / n_trials


def sweep_codebook(label, codebook, K_grid, n_trials, seeds, device):
    rows = []
    for K in K_grid:
        recs = []
        for seed in seeds:
            gen = torch.Generator().manual_seed(seed * 9001 + K)
            recs.append(measure_recovery(codebook, K, n_trials, gen))
        m = sum(recs) / len(recs)
        rows.append({"K": K, "mean_recovery": m})
        print(f"    {label}  K={K:5d}  recovery={m:.3f}", flush=True)
    k_star = None
    for i in range(len(rows) - 1):
        a, b = rows[i], rows[i+1]
        if a["mean_recovery"] >= 0.5 >= b["mean_recovery"]:
            if a["mean_recovery"] == b["mean_recovery"]:
                k_star = float(a["K"])
            else:
                frac = (a["mean_recovery"] - 0.5) / (a["mean_recovery"] - b["mean_recovery"])
                k_star = float(a["K"] + frac * (b["K"] - a["K"]))
            break
    return {"k_star": k_star, "sweep": rows}


def main(smoke: bool = False) -> None:
    self_test_verdict()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if smoke:
        config = {"mode": "smoke", "N": 256, "M": 256,
                  "K_list": [10, 50, 100, 200],
                  "n_trials": 5, "seeds": [17]}
    else:
        config = {"mode": "full", "N": 4096, "M": 4096,
                  "K_list": [50, 100, 200, 400, 600, 900, 1300, 2000, 3000],
                  "n_trials": 20, "seeds": [17, 23, 31, 41, 53]}
    print(f"wave14kerdock_hadamard. mode={config['mode']} device={device}", flush=True)

    t0 = time.monotonic()
    # Build codebooks
    print(f"  Building Hadamard codebook M={config['M']} N={config['N']}...", flush=True)
    H = hadamard_matrix(config["N"]).to(device)
    print(f"  Hadamard shape: {H.shape}", flush=True)
    print(f"  Building random +/-1 codebook M={config['M']} N={config['N']}...", flush=True)
    rand_gen = torch.Generator().manual_seed(99)
    R = random_codebook(config["M"], config["N"], rand_gen).to(device)

    by_codebook = {}
    print(f"  --- random ---", flush=True)
    by_codebook["random"] = sweep_codebook("random", R, config["K_list"],
                                            config["n_trials"], config["seeds"], device)
    print(f"  --- hadamard ---", flush=True)
    by_codebook["hadamard"] = sweep_codebook("hadamard", H, config["K_list"],
                                              config["n_trials"], config["seeds"], device)
    elapsed = time.monotonic() - t0

    summary = {"by_codebook": by_codebook}
    verdict, msg = compute_verdict(summary)
    print(f"\n=== {verdict} ===\n{msg}", flush=True)
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
               "config": config, "device": str(device),
               "by_codebook": by_codebook, "summary": summary}
    validate_metrics(metrics)
    out_dir = get_output_dir("wave14kerdock_hadamard")
    tmp = (out_dir / "metrics.json").with_suffix(".tmp")
    tmp.write_text(json.dumps(metrics, indent=2))
    os.replace(tmp, out_dir / "metrics.json")
    print(f"wrote {out_dir / 'metrics.json'}", flush=True)


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test_verdict()
        sys.exit(0)
    main(smoke="--smoke" in sys.argv)
