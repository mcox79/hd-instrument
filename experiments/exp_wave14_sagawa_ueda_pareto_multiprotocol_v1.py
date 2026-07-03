"""Cap 1 Sagawa-Ueda Pareto-front multi-protocol erase experiment.

Motivation
----------
Existing Cap 1 work (CROOKS_NOISE_ENVELOPE_PARTIAL) establishes that the
substrate's anti-Hebbian erase satisfies delta_S < 0.05 under modest noise.
The next step is to map the FULL Pareto-front of the erase: vary BOTH the
noise rate p AND the noise injection point (forward only / reverse only /
both phases) at 10 seeds across alpha = M_base / N. This produces a clean
multi-protocol Pareto curve that can be cited as the Cap 1 operating envelope.

Sagawa-Ueda (2008) gives the second-law-like inequality for measurement
feedback systems. The Crooks-FT delta_S_emp is the empirical proxy for the
relative entropy term in the Sagawa-Ueda bound. Sweeping protocols at 10
seeds at N=4096 with M_base in {50, 100, 200, 400} maps out where the
substrate sits relative to the bound.

Scientific question
-------------------
For each protocol P in {fwd_only, rev_only, both_phases} and each noise rate
p in {0.0, 0.05, 0.10, 0.20}, does delta_S_emp stay under 0.05? Map the
Pareto front (M_base, p) -> delta_S_emp per protocol. Verdict counts how
many (M_base, p, protocol) triples pass.

ETA
---
N=4096 is small for the runner GPU; 10 seeds * 4 alpha * 4 p * 3 protocols
* 30 trials = ~14,400 inner trials. Each trial is ~6 GPU matmul calls at
N=4096 x M_base (M_base up to 400). Estimated total: ~30-45 min on GPU.

Vertex
------
CAP1_PARETO_PASS  -- pass rate >= 0.7 across all triples
CAP1_PARETO_MIXED -- pass rate in [0.4, 0.7]
CAP1_PARETO_KILL  -- pass rate < 0.4
CAP1_PARETO_INCONCLUSIVE -- structural failure

Pre-reg: preregs/2026-05-23_wave14_sagawa_ueda_pareto_multiprotocol_v1.md
"""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import argparse
import json
import math
import os
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
import torch


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

def get_output_dir(name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d: dict) -> None:
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    if not required.issubset(d.keys()):
        raise ValueError(f"metrics missing keys: {required - d.keys()}")


# ---------------------------------------------------------------------------
# Pareto verdict
# ---------------------------------------------------------------------------

PASS_THRESHOLD = 0.05

def compute_verdict(per_triple: dict) -> tuple[str, str]:
    """per_triple: dict { (M_base, p, protocol) : delta_S_emp_mean }.
    Pass if delta_S_emp < 0.05.
    """
    if not per_triple:
        return ("CAP1_PARETO_INCONCLUSIVE", "No triples evaluated.")
    pass_n = sum(1 for v in per_triple.values() if v < PASS_THRESHOLD)
    total = len(per_triple)
    rate = pass_n / total
    if rate >= 0.7:
        return ("CAP1_PARETO_PASS",
                f"Sagawa-Ueda Pareto: {pass_n}/{total} = {rate:.2%} triples "
                f"satisfy delta_S < {PASS_THRESHOLD}. Cap 1 envelope spans broad "
                f"protocol/noise/M_base region.")
    if rate >= 0.4:
        return ("CAP1_PARETO_MIXED",
                f"Sagawa-Ueda Pareto MIXED: {pass_n}/{total} = {rate:.2%} pass. "
                f"Cap 1 envelope partial; identifies favorable protocol/M region.")
    return ("CAP1_PARETO_KILL",
            f"Sagawa-Ueda Pareto KILL: {pass_n}/{total} = {rate:.2%} pass. "
            f"Cap 1 envelope is narrow.")


def self_test() -> None:
    # Mock triples
    triples = {("50", "0.05", "fwd_only"): 0.01,
               ("50", "0.10", "fwd_only"): 0.02,
               ("100", "0.05", "fwd_only"): 0.04,
               ("100", "0.10", "rev_only"): 0.06,
               ("200", "0.20", "both_phases"): 0.30}
    v, _ = compute_verdict(triples)
    assert v in ("CAP1_PARETO_PASS", "CAP1_PARETO_MIXED"), v
    # all fail
    v_fail, _ = compute_verdict({"a": 0.5, "b": 0.6, "c": 0.7})
    assert v_fail == "CAP1_PARETO_KILL", v_fail
    # empty
    v_e, _ = compute_verdict({})
    assert v_e == "CAP1_PARETO_INCONCLUSIVE"
    # all pass
    v_p, _ = compute_verdict({"a": 0.01, "b": 0.02, "c": 0.03, "d": 0.04})
    assert v_p == "CAP1_PARETO_PASS", v_p
    print("Pareto verdict self-test PASS (4/4)", flush=True)


# ---------------------------------------------------------------------------
# Experiment primitives (closely mirror crooks_noise_envelope_v1)
# ---------------------------------------------------------------------------

def make_pattern(N: int, gen: torch.Generator, device: torch.device) -> torch.Tensor:
    b = (torch.rand(N, generator=gen) > 0.5).to(device)
    return (2.0 * b.float() - 1.0).to(torch.bfloat16)


def retrieval_entropy(W: torch.Tensor, k: torch.Tensor,
                      candidates: torch.Tensor) -> float:
    pred = W @ k
    scores = candidates @ pred
    log_probs = torch.log_softmax(scores.float(), dim=0)
    probs = log_probs.exp()
    H = float(-(probs * log_probs).sum().item())
    return H


def apply_bit_flip_noise(W: torch.Tensor, p: float,
                         gen: torch.Generator) -> torch.Tensor:
    if p == 0.0:
        return W
    mask = torch.rand(W.shape, generator=gen, device=W.device) < p
    return torch.where(mask, -W, W)


PROTOCOLS = ("fwd_only", "rev_only", "both_phases")


def run_cell(N: int, M_base: int, n_trials: int, seed: int,
             p_noise: float, protocol: str, device: torch.device) -> list[float]:
    gen = torch.Generator(device="cpu").manual_seed(seed)
    gpu_gen = torch.Generator(device=device).manual_seed(seed + 100000)

    candidates = torch.stack([make_pattern(N, gen, device) for _ in range(M_base)], dim=0)
    base_keys = torch.stack([make_pattern(N, gen, device) for _ in range(M_base)], dim=0)
    W_base = (candidates.T.float() @ base_keys.float() / N).to(torch.bfloat16)

    deltas = []
    for _ in range(n_trials):
        k_new = make_pattern(N, gen, device)
        v_new = make_pattern(N, gen, device)
        H_base = retrieval_entropy(W_base, k_new, candidates)
        delta_W = (torch.outer(v_new, k_new) / N).to(torch.bfloat16)

        # Insert
        W_inserted = W_base + delta_W
        # Noise on forward step
        if protocol in ("fwd_only", "both_phases"):
            W_inserted = apply_bit_flip_noise(W_inserted, p_noise, gpu_gen)
        # Reverse: anti-Hebbian
        W_erased = W_inserted - delta_W
        # Noise on reverse step
        if protocol in ("rev_only", "both_phases"):
            W_erased = apply_bit_flip_noise(W_erased, p_noise, gpu_gen)

        H_erased = retrieval_entropy(W_erased, k_new, candidates)
        deltas.append(abs(H_erased - H_base))
        del W_inserted, W_erased

    del W_base, candidates, base_keys
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return deltas


def run_experiment(smoke: bool):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    if smoke:
        config = {
            "mode": "smoke",
            "N": 1024,
            "M_base_list": [50, 100],
            "p_list": [0.05, 0.10],
            "protocols": ["fwd_only", "both_phases"],
            "seeds": [17, 18],
            "n_trials": 10,
        }
    else:
        config = {
            "mode": "full",
            "N": 4096,
            "M_base_list": [50, 100, 200, 400],
            "p_list": [0.0, 0.05, 0.10, 0.20],
            "protocols": ["fwd_only", "rev_only", "both_phases"],
            "seeds": [11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
            "n_trials": 30,
        }

    N = config["N"]
    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(device)

    triples_mean: dict = {}
    cells_all = []
    for M_base in config["M_base_list"]:
        for p in config["p_list"]:
            for protocol in config["protocols"]:
                deltas_all_seeds = []
                for seed in config["seeds"]:
                    deltas = run_cell(N, M_base, config["n_trials"], seed,
                                      p, protocol, device)
                    deltas_all_seeds.extend(deltas)
                mean = sum(deltas_all_seeds) / max(1, len(deltas_all_seeds))
                triples_mean[(str(M_base), str(p), protocol)] = mean
                cells_all.append({
                    "M_base": M_base, "p": p, "protocol": protocol,
                    "mean": mean,
                    "max": max(deltas_all_seeds),
                    "n_trials": len(deltas_all_seeds),
                })
                print(f"  M={M_base} p={p:.2f} {protocol}: "
                      f"mean delta_S={mean:.4f}", flush=True)

    if device.type == "cuda":
        peak_mb = torch.cuda.max_memory_allocated(device) / (1024 ** 2)
    else:
        peak_mb = None

    verdict, msg = compute_verdict(triples_mean)
    elapsed = time.monotonic() - t0
    summary = {
        "cells": cells_all,
        "per_triple_mean": {f"{k[0]}|{k[1]}|{k[2]}": v
                            for k, v in triples_mean.items()},
        "peak_vram_mb": peak_mb,
    }
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


def write_metrics(out_dir, summary, verdict, msg, elapsed, config) -> None:
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
               "summary": summary, "config": config}
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")
    print(f"wrote {out_dir / 'metrics.json'}", flush=True)


def run_smoke() -> None:
    self_test()
    out_dir = get_output_dir("wave14_sagawa_ueda_pareto_multiprotocol_v1_smoke")
    s, v, m, e, c = run_experiment(smoke=True)
    write_metrics(out_dir, s, v, m, e, c)
    print(f"\nSMOKE OK: {v}", flush=True)


def run_main() -> None:
    self_test()
    out_dir = get_output_dir("wave14_sagawa_ueda_pareto_multiprotocol_v1")
    s, v, m, e, c = run_experiment(smoke=False)
    write_metrics(out_dir, s, v, m, e, c)
    print(f"\nDONE: {v}", flush=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test(); return 0
    if args.smoke:
        run_smoke(); return 0
    run_main(); return 0


if __name__ == "__main__":
    sys.exit(main())
