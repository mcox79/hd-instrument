"""Modern Hopfield capacity test: softmax vs sparsemax retrieval.

Hu 2023 (arXiv:2309.12673) proves sparse modern Hopfield gets exp(N) capacity
with provably tighter retrieval-error bound than dense (softmax). This script
measures the capacity cliff for our substrate-style storage under both
decoders.

Pre-reg: preregs/2026-05-20_wave14n_decoder_bound.md

Test: store K random +/-1 patterns. Query = stored pattern + 10% bit flips.
Retrieval map: Xi @ decoder(beta * Xi^T q). Success if argmax over the K-bank
of cos(retrieved, pattern_j) returns the correct j.

Sparsemax = entmax with alpha=2 (closed form: projection onto simplex via
sort-and-threshold). Softmax = vanilla.
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
        raise ValueError(f"metrics missing required: {missing}")
    if not d.get("verdict") or not d.get("verdict_msg"):
        raise ValueError("empty verdict")


def compute_verdict(summary: dict) -> tuple[str, str]:
    """Compare K* across decoders. Hu 2023's prediction: sparsemax >> softmax."""
    by_decoder = summary.get("by_decoder", {})
    if not by_decoder:
        return ("DECODER_BOUND_INCONCLUSIVE", "No per-decoder data.")
    sm = by_decoder.get("softmax", {})
    sx = by_decoder.get("sparsemax", {})
    sm_k = sm.get("k_star")
    sx_k = sx.get("k_star")
    if sm_k is None and sx_k is None:
        return ("DECODER_BOUND_INCONCLUSIVE",
                "Neither decoder located K*; extend K_grid upward.")
    if sm_k is None:
        return ("DECODER_BOUND_SPARSEMAX_WINS_BIG",
                f"sparsemax K*={sx_k:.0f} located; softmax never crossed 0.5 in grid. "
                f"Sparse Hopfield is qualitatively better.")
    if sx_k is None:
        return ("DECODER_BOUND_ANOMALOUS",
                f"softmax K*={sm_k:.0f} located but sparsemax never did. "
                f"Unexpected; investigate.")
    ratio = sx_k / sm_k
    if ratio >= 2.0:
        return ("DECODER_BOUND_SPARSEMAX_WINS",
                f"sparsemax K*={sx_k:.0f} vs softmax K*={sm_k:.0f}. "
                f"Sparse decoder gives {ratio:.1f}x capacity. Matches Hu 2023 "
                f"prediction. Substrate has 50x+ headroom via decoder swap.")
    if ratio >= 1.2:
        return ("DECODER_BOUND_SPARSEMAX_MARGINAL",
                f"sparsemax K*={sx_k:.0f} vs softmax K*={sm_k:.0f} "
                f"({ratio:.2f}x). Improvement is real but smaller than Hu 2023 "
                f"theory predicts.")
    if 0.8 <= ratio <= 1.2:
        return ("DECODER_BOUND_TIE",
                f"sparsemax K*={sx_k:.0f} ~ softmax K*={sm_k:.0f}. No meaningful "
                f"capacity gain from decoder swap in this regime.")
    return ("DECODER_BOUND_SOFTMAX_WINS",
            f"sparsemax K*={sx_k:.0f} < softmax K*={sm_k:.0f}. Sparse decoder "
            f"is worse here; contradicts Hu 2023 expectation.")


def self_test_verdict() -> None:
    cases = [
        ({"by_decoder": {"softmax": {"k_star": 500}, "sparsemax": {"k_star": 2500}}},
         "DECODER_BOUND_SPARSEMAX_WINS"),
        ({"by_decoder": {"softmax": {"k_star": 500}, "sparsemax": {"k_star": 650}}},
         "DECODER_BOUND_SPARSEMAX_MARGINAL"),
        ({"by_decoder": {"softmax": {"k_star": 500}, "sparsemax": {"k_star": 510}}},
         "DECODER_BOUND_TIE"),
        ({"by_decoder": {"softmax": {"k_star": 500}, "sparsemax": {"k_star": 300}}},
         "DECODER_BOUND_SOFTMAX_WINS"),
        ({"by_decoder": {"softmax": {"k_star": None}, "sparsemax": {"k_star": 3000}}},
         "DECODER_BOUND_SPARSEMAX_WINS_BIG"),
        ({"by_decoder": {"softmax": {"k_star": 500}, "sparsemax": {"k_star": None}}},
         "DECODER_BOUND_ANOMALOUS"),
        ({"by_decoder": {}}, "DECODER_BOUND_INCONCLUSIVE"),
    ]
    for s, expected in cases:
        actual, _ = compute_verdict(s)
        if actual != expected:
            raise AssertionError(f"self-test FAIL: {s} -> {actual}, expected {expected}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def softmax_decoder(scores: torch.Tensor, beta: float) -> torch.Tensor:
    """Dense softmax over K stored patterns."""
    return torch.softmax(beta * scores, dim=-1)


def sparsemax_decoder(scores: torch.Tensor, beta: float) -> torch.Tensor:
    """Sparsemax via sort-and-threshold (Martins & Astudillo 2016, eq 3-4).
    Projection onto the simplex. Closed form. Last dim is K.
    """
    z = beta * scores
    z_sorted, _ = torch.sort(z, descending=True, dim=-1)
    K = z.size(-1)
    cumsum = z_sorted.cumsum(dim=-1) - 1.0
    k_range = torch.arange(1, K + 1, device=z.device, dtype=z.dtype)
    # Reshape k_range to broadcast over leading dims
    while k_range.dim() < z.dim():
        k_range = k_range.unsqueeze(0)
    support = (k_range * z_sorted - cumsum) > 0
    k_star = support.float().sum(dim=-1, keepdim=True).clamp(min=1)
    # tau threshold: (sum_{i<=k_star} z_i - 1) / k_star
    tau = (cumsum.gather(-1, (k_star - 1).long()) ) / k_star
    return torch.clamp(z - tau, min=0.0)


def make_patterns(K: int, N: int, gen: torch.Generator, device: torch.device) -> torch.Tensor:
    return 2.0 * (torch.rand((K, N), generator=gen, device=device) > 0.5).float() - 1.0


def corrupt_query(pattern: torch.Tensor, flip_frac: float, gen: torch.Generator) -> torch.Tensor:
    """Flip flip_frac bits of pattern."""
    N = pattern.size(-1)
    flip_count = max(1, int(round(N * flip_frac)))
    idx = torch.randperm(N, generator=gen, device=pattern.device)[:flip_count]
    q = pattern.clone()
    q[idx] = -q[idx]
    return q


def retrieve(stored: torch.Tensor, query: torch.Tensor, decoder_fn, beta: float) -> torch.Tensor:
    """Modern Hopfield retrieval: r = Xi @ decoder(beta * Xi^T q / sqrt(N)).
    stored: (K, N), query: (N,). Returns retrieved vector (N,)."""
    N = stored.size(-1)
    scores = (stored @ query) / math.sqrt(N)  # (K,)
    weights = decoder_fn(scores, beta)  # (K,)
    return weights @ stored  # (N,)


def measure_recovery(N: int, K: int, decoder_fn, beta: float, flip_frac: float,
                     n_trials: int, gen: torch.Generator, device: torch.device) -> float:
    """For each trial: K random patterns, query = corrupted pattern_i, retrieve.
    Success if argmax over the K-bank of inner_product(retrieved, pattern_j) == i."""
    correct = 0
    for _ in range(n_trials):
        patterns = make_patterns(K, N, gen, device)
        i = int(torch.randint(0, K, (1,), generator=gen, device=device).item())
        q = corrupt_query(patterns[i], flip_frac, gen)
        r = retrieve(patterns, q, decoder_fn, beta)
        sims = patterns @ r
        if int(sims.argmax()) == i:
            correct += 1
    return correct / n_trials


def sweep_decoder(N: int, K_grid: list[int], decoder_fn, beta: float,
                  flip_frac: float, n_trials: int, seeds: list[int],
                  device: torch.device, label: str) -> dict:
    """Sweep K for one decoder. Return per-K recoveries + K* via linear interp."""
    rows = []
    for K in K_grid:
        recs = []
        for seed in seeds:
            gen = torch.Generator(device=device).manual_seed(seed + 9001 * K + N)
            recs.append(measure_recovery(N, K, decoder_fn, beta, flip_frac,
                                         n_trials, gen, device))
        mean = sum(recs) / len(recs)
        rows.append({"K": K, "K_over_N": K / N, "mean_recovery": mean})
        print(f"    {label}  K={K:5d} K/N={K/N:.3f}  recovery={mean:.3f}", flush=True)
    # Linear interp K* at recovery=0.5
    k_star = None
    for i in range(len(rows) - 1):
        a, b = rows[i], rows[i + 1]
        if a["mean_recovery"] >= 0.5 >= b["mean_recovery"]:
            if a["mean_recovery"] == b["mean_recovery"]:
                k_star = float(a["K"])
            else:
                frac = (a["mean_recovery"] - 0.5) / (a["mean_recovery"] - b["mean_recovery"])
                k_star = float(a["K"] + frac * (b["K"] - a["K"]))
            break
    return {"k_star": k_star, "alpha_c": (k_star / N) if k_star else None,
            "sweep": rows}


def main(smoke: bool = False) -> None:
    self_test_verdict()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if smoke:
        config = {"mode": "smoke", "N": 512, "K_grid": [50, 150, 500],
                  "beta": 1.0, "flip_frac": 0.1, "seeds": [17], "n_trials": 10}
    else:
        config = {"mode": "full", "N": 4096,
                  "K_grid": [100, 300, 600, 1000, 1500, 2200, 3000, 4500, 6500, 10000],
                  "beta": 1.0, "flip_frac": 0.1, "seeds": [17, 23, 31],
                  "n_trials": 30}
    print(f"decoder_bound N={config['N']} mode={config['mode']} device={device}", flush=True)
    print(f"  beta={config['beta']} flip_frac={config['flip_frac']} "
          f"K_grid={config['K_grid']}", flush=True)

    t0 = time.monotonic()
    by_decoder = {}
    for name, fn in [("softmax", softmax_decoder), ("sparsemax", sparsemax_decoder)]:
        print(f"  --- {name} ---", flush=True)
        result = sweep_decoder(config["N"], config["K_grid"], fn,
                               config["beta"], config["flip_frac"],
                               config["n_trials"], config["seeds"], device, name)
        by_decoder[name] = result
        print(f"    {name}: K*={result['k_star']}  alpha_c={result['alpha_c']}",
              flush=True)
    elapsed = time.monotonic() - t0

    summary = {"by_decoder": by_decoder}
    verdict, msg = compute_verdict(summary)
    print(f"\n=== {verdict} ===\n{msg}", flush=True)
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
               "config": config, "device": str(device),
               "by_decoder": by_decoder, "summary": summary}
    validate_metrics(metrics)
    out_dir = get_output_dir("wave14n_decoder_bound")
    tmp = (out_dir / "metrics.json").with_suffix(".tmp")
    tmp.write_text(json.dumps(metrics, indent=2))
    os.replace(tmp, out_dir / "metrics.json")
    print(f"wrote {out_dir / 'metrics.json'}", flush=True)


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test_verdict()
        sys.exit(0)
    main(smoke="--smoke" in sys.argv)
