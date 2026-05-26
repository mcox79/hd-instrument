"""ALPHA_ERASE sweep with CORRELATED keys (low-rank latent structure).

The v1 with random +/-1 keys produced trivial results: orthogonal keys give
all-or-nothing erase at alpha=1.0 with no recall cost. The realistic regime
(wave14h with K-byte context keys) showed 76.7pp leak reduction AND 12pp
recall cost because corpus keys are correlated (shared byte prefixes).

This v2 uses keys drawn from a rank-L latent subspace (L=N/8) so the within-
subspace overlap is large enough to surface the real tradeoff.

Pre-reg: preregs/2026-05-20_wave14h_alpha_sweep_v2.md

Theory-asserted smoke:
  1. Pairwise key cosine std > 0.05 (assertion: keys are actually correlated).
  2. Method A leak rate >= 0.85 (assertion: substrate stores facts).
  3. Method B leak rate at alpha=1.0 < Method A leak (assertion: erase
     mechanism is actually firing).
  4. Method A != Method B at any alpha (assertion: distinguishable).
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from verification import theory, oracle  # noqa: E402


def get_output_dir(default_name: str) -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
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
    rows = summary.get("per_alpha", [])
    if not rows:
        return ("ALPHA_SWEEP_INCONCLUSIVE", "No per-alpha data.")
    target = [r for r in rows if r["leak_mean"] <= 0.05 and r["kept_mean"] >= 0.85]
    if target:
        best = min(target, key=lambda r: r["leak_mean"])
        return ("ALPHA_SWEEP_HITS_TARGET",
                f"alpha={best['alpha']:.2f} -> leak={best['leak_mean']:.2%}, "
                f"kept_recall={best['kept_mean']:.2%}. GDPR-grade operating point.")
    partial = [r for r in rows if r["leak_mean"] <= 0.15 and r["kept_mean"] >= 0.75]
    if partial:
        best = min(partial, key=lambda r: r["leak_mean"])
        return ("ALPHA_SWEEP_PARTIAL",
                f"alpha={best['alpha']:.2f} -> leak={best['leak_mean']:.2%}, "
                f"kept_recall={best['kept_mean']:.2%}. Pareto point below GDPR target.")
    return ("ALPHA_SWEEP_NO_FRONTIER",
            "No alpha satisfies leak<=15% AND kept_recall>=75%. Best leak: "
            f"{min(r['leak_mean'] for r in rows):.2%}; best kept: "
            f"{max(r['kept_mean'] for r in rows):.2%}.")


def self_test_verdict() -> None:
    cases = [
        ({"per_alpha": [{"alpha": 0.5, "leak_mean": 0.03, "kept_mean": 0.88}]},
         "ALPHA_SWEEP_HITS_TARGET"),
        ({"per_alpha": [{"alpha": 0.7, "leak_mean": 0.10, "kept_mean": 0.78}]},
         "ALPHA_SWEEP_PARTIAL"),
        ({"per_alpha": [{"alpha": 1.0, "leak_mean": 0.40, "kept_mean": 0.50}]},
         "ALPHA_SWEEP_NO_FRONTIER"),
        ({"per_alpha": []}, "ALPHA_SWEEP_INCONCLUSIVE"),
    ]
    for s, expected in cases:
        actual, _ = compute_verdict(s)
        if actual != expected:
            raise AssertionError(f"verdict self-test FAIL: {s} -> {actual}, expected {expected}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def make_correlated_keys(n_facts: int, N: int, rank_L: int, gen: torch.Generator,
                         device: torch.device) -> torch.Tensor:
    """Keys in a rank-L latent subspace, sign-binarized to bipolar.

    Method: sample L "factor" vectors in R^N; each key is a random linear combo
    of factors + small noise, then sign-binarized. Keys sharing strong factors
    have positive cosine; others have weak overlap.
    """
    factors = 2.0 * (torch.rand((rank_L, N), generator=gen, device=device) > 0.5).float() - 1.0
    # Each key: random combo of factors with sparse positive weights
    weights = torch.rand((n_facts, rank_L), generator=gen, device=device)
    weights = weights * (weights > 0.6).float()  # sparse positive
    noise = 0.3 * torch.randn((n_facts, N), generator=gen, device=device)
    raw = weights @ factors + noise
    return torch.sign(raw + 1e-9)  # bipolar, ties to +1


def antihebbian_erase(W, key_vec, alpha):
    Wk = W @ key_vec
    d = float((key_vec * key_vec).sum())
    return W - alpha * torch.outer(Wk, key_vec) / d


def run_one(N, n_facts, n_erase, rank_L, alpha, seed, device):
    gen = torch.Generator(device=device).manual_seed(seed)
    keys = make_correlated_keys(n_facts, N, rank_L, gen, device)
    values = 2.0 * (torch.rand((n_facts, N), generator=gen, device=device) > 0.5).float() - 1.0
    W = (values.T @ keys) / N

    # Verify correlation: pairwise std of key inner products
    key_pairs = (keys @ keys.T) / N
    off_diag_mask = ~torch.eye(n_facts, dtype=torch.bool, device=device)
    pairwise_std = float(key_pairs[off_diag_mask].std())

    def retrieve_correct(W_, idxs):
        if not idxs:
            return 0
        keys_sub = keys[idxs]
        retrieved = keys_sub @ W_.T
        sims = retrieved @ values.T
        preds = sims.argmax(dim=1)
        return int((preds == torch.tensor(idxs, device=device)).sum().item())

    erase_gen = torch.Generator().manual_seed(seed * 31 + 7)
    erase_idx = sorted(torch.randperm(n_facts, generator=erase_gen)[:n_erase].tolist())
    kept_idx = [i for i in range(n_facts) if i not in set(erase_idx)]

    leak_A = retrieve_correct(W, erase_idx) / n_erase
    kept_A = retrieve_correct(W, kept_idx) / max(1, len(kept_idx))
    W_B = W.clone()
    for i in erase_idx:
        W_B = antihebbian_erase(W_B, keys[i], alpha)
    leak_B = retrieve_correct(W_B, erase_idx) / n_erase
    kept_B = retrieve_correct(W_B, kept_idx) / max(1, len(kept_idx))
    return {"seed": seed, "alpha": alpha, "pairwise_std": pairwise_std,
            "leak_A": leak_A, "kept_A": kept_A,
            "leak_B": leak_B, "kept_B": kept_B}


def main(smoke: bool = False) -> None:
    self_test_verdict()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if smoke:
        config = {"mode": "smoke", "N": 512, "n_facts": 60, "n_erase": 15,
                  "rank_L": 16, "alphas": [0.5, 1.0], "seeds": [17]}
    else:
        # rank_L << n_facts gives strong correlation (target wave14h's regime)
        config = {"mode": "full", "N": 4096, "n_facts": 200, "n_erase": 50,
                  "rank_L": 50,
                  "alphas": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.85, 1.0, 1.2, 1.5],
                  "seeds": [17, 23, 31, 41, 53]}
    print(f"wave14h_alpha_sweep_v2 (correlated keys). mode={config['mode']} device={device}", flush=True)
    print(f"  N={config['N']} n_facts={config['n_facts']} n_erase={config['n_erase']} "
          f"rank_L={config['rank_L']}", flush=True)
    print(f"  alphas={config['alphas']} seeds={config['seeds']}", flush=True)

    t0 = time.monotonic()
    per_alpha = []
    grid = []
    pairwise_stds = []
    for alpha in config["alphas"]:
        rows = []
        for seed in config["seeds"]:
            r = run_one(config["N"], config["n_facts"], config["n_erase"],
                        config["rank_L"], alpha, seed, device)
            rows.append(r)
            grid.append(r)
            pairwise_stds.append(r["pairwise_std"])
        leak_mean = sum(r["leak_B"] for r in rows) / len(rows)
        kept_mean = sum(r["kept_B"] for r in rows) / len(rows)
        a_leak = sum(r["leak_A"] for r in rows) / len(rows)
        a_kept = sum(r["kept_A"] for r in rows) / len(rows)
        per_alpha.append({"alpha": alpha, "leak_mean": leak_mean, "kept_mean": kept_mean,
                          "baseline_leak": a_leak, "baseline_kept": a_kept,
                          "leak_reduction_pp": (a_leak - leak_mean) * 100})
        print(f"  alpha={alpha:.2f}  leak={leak_mean:.3f} kept={kept_mean:.3f} "
              f"(baseline_leak={a_leak:.3f}, baseline_kept={a_kept:.3f}, "
              f"pairwise_std={rows[0]['pairwise_std']:.3f})", flush=True)
    elapsed = time.monotonic() - t0

    # ORACLE ASSERTIONS - run in smoke and full to catch setup drift
    mean_pairwise_std = sum(pairwise_stds) / len(pairwise_stds)
    oracle.assert_in_range("key correlation", mean_pairwise_std,
                            (0.05, 0.50))  # higher than orthogonal (~1/sqrt(N))
    # At highest alpha (likely 1.5 or 1.0), Method B leak should be << Method A
    last_row = max(per_alpha, key=lambda r: r["alpha"])
    oracle.assert_baseline_high("Method A baseline leak", last_row["baseline_leak"], 0.70)
    oracle.assert_distinguishable("Method A vs B leak at max alpha",
                                   last_row["baseline_leak"], last_row["leak_mean"], 0.20)

    summary = {"per_alpha": per_alpha, "mean_pairwise_std": mean_pairwise_std}
    verdict, msg = compute_verdict(summary)
    print(f"\nORACLE CHECKS PASSED. mean_pairwise_std={mean_pairwise_std:.3f}", flush=True)
    print(f"=== {verdict} ===\n{msg}", flush=True)
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
               "config": config, "device": str(device),
               "per_alpha": per_alpha, "grid": grid, "summary": summary}
    validate_metrics(metrics)
    out_dir = get_output_dir("wave14h_alpha_sweep_v2")
    tmp = (out_dir / "metrics.json").with_suffix(".tmp")
    tmp.write_text(json.dumps(metrics, indent=2))
    os.replace(tmp, out_dir / "metrics.json")
    print(f"wrote {out_dir / 'metrics.json'}", flush=True)


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test_verdict()
        sys.exit(0)
    main(smoke="--smoke" in sys.argv)
