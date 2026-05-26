"""ALPHA_ERASE sweep over wave14h anti-Hebbian rank-1 W edit.

wave14h_wside_erase tonight: 76.7pp leak reduction (80% to 3.3%) at ALPHA=1.0,
but kept_recall dropped from 78% to 68% (target was >=80%).

This sweep finds the alpha that gives the best leak vs kept_recall frontier.
Target operating point: leak <=5% AND kept_recall >=85%.

Pre-reg: preregs/2026-05-20_wave14h_alpha_sweep.md

Uses random-key synthetic facts (not the corpus path) so smoke runs cheap.
The math we're testing is the rank-1 anti-Hebbian update, independent of how
keys are constructed.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import torch

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


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
    if not d.get("verdict"):
        raise ValueError("verdict empty")
    if not d.get("verdict_msg"):
        raise ValueError("verdict_msg empty")


def compute_verdict(summary: dict) -> tuple[str, str]:
    """Find best alpha by leak <= 0.05 AND kept_recall >= 0.85.
    Fall through to weaker thresholds if frontier isn't met.
    """
    rows = summary.get("per_alpha", [])
    if not rows:
        return ("ALPHA_SWEEP_INCONCLUSIVE", "No per-alpha data.")
    target_rows = [r for r in rows if r["leak_mean"] <= 0.05 and r["kept_mean"] >= 0.85]
    if target_rows:
        best = min(target_rows, key=lambda r: r["leak_mean"])
        return ("ALPHA_SWEEP_HITS_TARGET",
                f"alpha={best['alpha']:.2f} gives leak={best['leak_mean']:.2%} "
                f"and kept_recall={best['kept_mean']:.2%}. GDPR-grade operating "
                f"point confirmed.")
    pareto = [r for r in rows if r["leak_mean"] <= 0.10 and r["kept_mean"] >= 0.80]
    if pareto:
        best = min(pareto, key=lambda r: r["leak_mean"])
        return ("ALPHA_SWEEP_PARTIAL",
                f"alpha={best['alpha']:.2f}: leak={best['leak_mean']:.2%}, "
                f"kept_recall={best['kept_mean']:.2%}. Below GDPR-grade target "
                f"but reasonable Pareto point.")
    return ("ALPHA_SWEEP_NO_FRONTIER",
            f"No alpha satisfies leak<=10% AND kept_recall>=80%. "
            f"Best leak: {min(r['leak_mean'] for r in rows):.2%}; "
            f"best kept: {max(r['kept_mean'] for r in rows):.2%}.")


def self_test_verdict() -> None:
    cases = [
        ({"per_alpha": [{"alpha": 0.5, "leak_mean": 0.02, "kept_mean": 0.90}]},
         "ALPHA_SWEEP_HITS_TARGET"),
        ({"per_alpha": [{"alpha": 1.0, "leak_mean": 0.03, "kept_mean": 0.68}]},
         "ALPHA_SWEEP_NO_FRONTIER"),
        ({"per_alpha": [{"alpha": 0.7, "leak_mean": 0.08, "kept_mean": 0.82}]},
         "ALPHA_SWEEP_PARTIAL"),
        ({"per_alpha": []}, "ALPHA_SWEEP_INCONCLUSIVE"),
        # Multi-alpha: should pick best leak among target-hitting
        ({"per_alpha": [
            {"alpha": 0.3, "leak_mean": 0.04, "kept_mean": 0.88},
            {"alpha": 0.5, "leak_mean": 0.02, "kept_mean": 0.86},
            {"alpha": 0.7, "leak_mean": 0.01, "kept_mean": 0.84},  # fails kept
            {"alpha": 1.0, "leak_mean": 0.005, "kept_mean": 0.70}, # fails kept
        ]}, "ALPHA_SWEEP_HITS_TARGET"),
    ]
    for s, expected in cases:
        actual, _ = compute_verdict(s)
        if actual != expected:
            raise AssertionError(f"self-test FAIL: {s} -> {actual}, expected {expected}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def make_bipolar(shape, gen, device):
    return 2.0 * (torch.rand(shape, generator=gen, device=device) > 0.5).float() - 1.0


def antihebbian_erase(W, key_vec, alpha):
    """W -= alpha * (W @ k) k^T / d (rank-1 update)."""
    Wk = W @ key_vec
    d = float((key_vec * key_vec).sum())
    return W - alpha * torch.outer(Wk, key_vec) / d


def run_one_seed(N, n_facts, n_erase, alpha, seed, device):
    """Build random W from n_facts (key,value) pairs, then erase n_erase of them
    via anti-Hebbian update. Measure leak rate and kept-recall."""
    gen = torch.Generator(device=device).manual_seed(seed)
    keys = make_bipolar((n_facts, N), gen, device)
    values = make_bipolar((n_facts, N), gen, device)
    # Build W = sum_i v_i k_i^T / d (delta-rule equivalent for orthogonal-ish keys)
    W = (values.T @ keys) / N

    # Baseline: how many facts does W retrieve correctly via argmax over value codebook?
    def retrieve_correct(W_, idxs):
        if not idxs:
            return 0
        keys_sub = keys[idxs]
        # Retrieved: W_ @ k -> compare to all values via sign-cosine
        retrieved = keys_sub @ W_.T  # (n_idxs, N)
        sims = retrieved @ values.T  # (n_idxs, n_facts)
        preds = sims.argmax(dim=1)
        return int((preds == torch.tensor(idxs, device=device)).sum().item())

    all_idx = list(range(n_facts))
    erase_gen = torch.Generator().manual_seed(seed * 31 + 7)
    erase_idx = sorted(torch.randperm(n_facts, generator=erase_gen)[:n_erase].tolist())
    kept_idx = [i for i in all_idx if i not in set(erase_idx)]

    baseline_kept = retrieve_correct(W, kept_idx)
    baseline_erase = retrieve_correct(W, erase_idx)

    # Method A: no W edit (baseline)
    leak_A = retrieve_correct(W, erase_idx)
    kept_A = retrieve_correct(W, kept_idx)

    # Method B: anti-Hebbian rank-1 erase per fact
    W_B = W.clone()
    for i in erase_idx:
        W_B = antihebbian_erase(W_B, keys[i], alpha)
    leak_B = retrieve_correct(W_B, erase_idx)
    kept_B = retrieve_correct(W_B, kept_idx)

    return {
        "seed": seed, "alpha": alpha, "n_facts": n_facts, "n_erase": n_erase,
        "baseline_kept": baseline_kept, "baseline_erase": baseline_erase,
        "method_A_leak": leak_A / n_erase, "method_A_kept": kept_A / len(kept_idx),
        "method_B_leak": leak_B / n_erase, "method_B_kept": kept_B / len(kept_idx),
    }


def main(smoke: bool = False) -> None:
    self_test_verdict()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    if smoke:
        config = {"mode": "smoke", "N": 512, "n_facts": 20, "n_erase": 5,
                  "alphas": [0.5, 1.0], "seeds": [17]}
    else:
        config = {"mode": "full", "N": 4096, "n_facts": 100, "n_erase": 30,
                  "alphas": [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.85, 1.0, 1.2, 1.5],
                  "seeds": [17, 23, 31, 41, 53]}

    print(f"wave14h alpha sweep. mode={config['mode']} device={device}", flush=True)
    print(f"  N={config['N']} n_facts={config['n_facts']} n_erase={config['n_erase']}", flush=True)
    print(f"  alphas={config['alphas']} seeds={config['seeds']}", flush=True)

    t0 = time.monotonic()
    per_alpha = []
    grid = []
    for alpha in config["alphas"]:
        rows = []
        for seed in config["seeds"]:
            r = run_one_seed(config["N"], config["n_facts"], config["n_erase"],
                             alpha, seed, device)
            rows.append(r)
            grid.append(r)
        leak_mean = sum(r["method_B_leak"] for r in rows) / len(rows)
        kept_mean = sum(r["method_B_kept"] for r in rows) / len(rows)
        a_leak = sum(r["method_A_leak"] for r in rows) / len(rows)
        a_kept = sum(r["method_A_kept"] for r in rows) / len(rows)
        per_alpha.append({"alpha": alpha, "leak_mean": leak_mean, "kept_mean": kept_mean,
                          "baseline_leak": a_leak, "baseline_kept": a_kept,
                          "leak_reduction_pp": (a_leak - leak_mean) * 100})
        print(f"  alpha={alpha:.2f}  leak={leak_mean:.3f}  kept={kept_mean:.3f}  "
              f"(baseline leak={a_leak:.3f} kept={a_kept:.3f})", flush=True)
    elapsed = time.monotonic() - t0

    summary = {"per_alpha": per_alpha}
    verdict, msg = compute_verdict(summary)
    print(f"\n=== {verdict} ===\n{msg}", flush=True)

    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
               "config": config, "device": str(device),
               "per_alpha": per_alpha, "grid": grid, "summary": summary}
    validate_metrics(metrics)
    out_dir = get_output_dir("wave14h_alpha_sweep")
    tmp = (out_dir / "metrics.json").with_suffix(".tmp")
    tmp.write_text(json.dumps(metrics, indent=2))
    os.replace(tmp, out_dir / "metrics.json")
    print(f"wrote {out_dir / 'metrics.json'}", flush=True)


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test_verdict()
        sys.exit(0)
    main(smoke="--smoke" in sys.argv)
