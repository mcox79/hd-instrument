"""Combined test: pointer-chain at N=4096.

Takes the two best individual improvements from Track 0.1 follow-ups:
- Larger substrate N=4096 (gives 3.02 vs 3.16 baseline at N=1024)
- Pointer-chain memory with M=1024, alpha=0.3 (gives 2.91 vs 3.16 at N=1024)

Tests whether they combine roughly additively. Expected: ~2.77 if additive,
weaker if there's interference, stronger if synergistic.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from experiments.exp_pointerchain_charlm import (
    train_pointerchain_vsa, load_corpus, train_test_split,
)


SEED = 17


def main() -> None:
    print("Loading corpus...", flush=True)
    corpus = load_corpus()
    train, test = train_test_split(corpus, 0.8)
    print(f"  train={len(train)} bytes, test={len(test)} bytes", flush=True)

    configs = [
        # (N, K, arousal, beta, M, alpha, label)
        (4096, 4, 0.3, 8.0, 1024, 0.3, "N=4096 M=1024 alpha=0.3"),
        (4096, 4, 0.3, 8.0, 1024, 0.5, "N=4096 M=1024 alpha=0.5"),
        (4096, 4, 0.3, 8.0,  256, 0.3, "N=4096 M=256 alpha=0.3"),
    ]

    print(f"\nRunning {len(configs)} combined configs...", flush=True)
    results = []
    for N, K, arousal, beta, M, alpha, label in configs:
        print(f"\n  Starting {label}", flush=True)
        t0 = time.perf_counter()
        r = train_pointerchain_vsa(train, test, N, K, arousal, beta, M, alpha, SEED, label=label)
        r["wall_time_s"] = time.perf_counter() - t0
        r["config_label"] = label
        results.append(r)
        print(
            f"  DONE {label}  test_bpc={r['test_bpc']:.4f}  gap={r['train_test_gap']:+.3f}  "
            f"({r['wall_time_s']:.1f}s)",
            flush=True,
        )

    results.sort(key=lambda r: r["test_bpc"])
    best = results[0]
    print(f"\nBest: {best['config_label']}  test_bpc={best['test_bpc']:.4f}", flush=True)

    print(f"\nComparison table:", flush=True)
    print(f"  Hebbian baseline (N=1024, no pool)                   : 3.16", flush=True)
    print(f"  Larger N alone (N=4096, no pool)                     : 3.02", flush=True)
    print(f"  Pointer-chain alone (N=1024, M=1024, alpha=0.3)      : 2.91", flush=True)
    print(f"  Combined (N=4096 + pointer-chain) best               : {best['test_bpc']:.4f}", flush=True)
    print(f"  Tiny transformer (ceiling)                           : 2.39", flush=True)
    print(f"  Gap to transformer                                   : {best['test_bpc'] - 2.39:.4f}", flush=True)

    out = {
        "seed": SEED,
        "configs": [(c[0], c[1], c[2], c[3], c[4], c[5], c[6]) for c in configs],
        "sweep_results": results,
        "best": {
            "label": best["config_label"],
            "test_bpc": best["test_bpc"],
            "train_bpc": best["train_bpc"],
        },
        "reference": {
            "hebbian_baseline_N1024": 3.16,
            "larger_N4096_no_pool": 3.02,
            "pointer_chain_N1024_M1024_a03": 2.91,
            "tiny_transformer_best": 2.39,
        },
        "headline": f"Combined (N=4096 + pointer-chain) best test bpc = {best['test_bpc']:.3f}",
    }

    out_path = Path(__file__).resolve().parent.parent / "data" / "exp_combined_n4096_pointerchain"
    out_path.mkdir(parents=True, exist_ok=True)
    (out_path / "metrics.json").write_text(json.dumps(out, indent=2, default=str))
    print(f"\nWrote {out_path / 'metrics.json'}", flush=True)


if __name__ == "__main__":
    main()
