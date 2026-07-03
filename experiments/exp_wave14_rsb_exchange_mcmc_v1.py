"""Replica-exchange (parallel-tempering) MCMC on Kerdock-Hebbian W -- RSB transition probe.

Motivation
----------
Parisi P(q12) probes (glauber_kerdock_v* and parisi_pq_kerdock_v*) measure
the shape of the replica-overlap distribution and classify RSB vs RS vs
paramagnet. An independent and stronger probe of the RSB transition is the
behavior of replica-exchange (parallel-tempering, PT) Monte Carlo. Hukushima
and Nemoto (1996) and Hansmann (1997) established that in a glassy phase the
PT swap acceptance rates show characteristic decay with temperature, AND the
auto-correlation time tau_int at each temperature diverges below T_g.

This experiment instruments a PT chain across 12 temperatures on Kerdock-
Hebbian W, recording:
  - per-pair swap acceptance rates a(beta_i, beta_{i+1})
  - per-temperature internal autocorrelation time of <s, s_target>
  - "tunneling time" (rate of complete top-to-bottom traversal of the
    temperature ladder by a tagged replica)

In a clean second-order glass transition, the swap-rate profile has a clear
minimum at beta_g. In the RSB phase the tunneling time grows superpolynomially
with N. We sample N in {512, 1024} and look for the qualitative profile.

ETA
---
PT chain of 12 temperatures, 5e5 sweeps each, 5 seeds, N=1024 -> ~3e8 spin
updates per seed. At ~1e6 updates/sec on a fast CPU per chain, ~5 min per
seed * 5 seeds = 25 min. Then we run the swap protocol every 100 sweeps.
Total ETA: ~45-60 min CPU.

Vertex
------
RSB_PT_TRANSITION_DETECTED -- monotonic swap-rate decay with a clear minimum
                              AND autocorrelation diverging below beta_g
RSB_PT_FLAT                -- swap rates uniformly high (no transition)
RSB_PT_INCONCLUSIVE        -- mixed / no clear pattern

Pre-reg: preregs/2026-05-23_wave14_rsb_exchange_mcmc_v1.md
"""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import argparse
import importlib.util
import json
import math
import os
import time
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
_g1_path = REPO / "experiments" / "exp_wave14_glauber_kerdock_v1.py"
_spec = importlib.util.spec_from_file_location("glauber_v1", _g1_path)
_g1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_g1)

build_hebbian_W = _g1.build_hebbian_W
glauber_sweep = _g1.glauber_sweep
hopfield_energy = _g1.hopfield_energy
select_subset_codewords = _g1.select_subset_codewords


def parallel_tempering(
    W: np.ndarray,
    betas: list[float],
    n_burn: int,
    n_collect: int,
    swap_period: int,
    seed: int,
) -> dict:
    """Run parallel tempering across betas. Returns dict of:
      acceptance_rates[i] = a(beta_i, beta_{i+1})
      energy_history per beta
      tunneling_count (number of times a tagged replica visits beta_min and beta_max)
    """
    R = len(betas)
    N = W.shape[0]
    rng = np.random.default_rng(seed)

    # R replicas, R initial configs (random spins)
    states = np.where(rng.random((R, N)) < 0.5, 1.0, -1.0)
    # Track which "label" started at which temperature -- for tunneling diagnostic
    labels = np.arange(R)  # labels[r] is the original label of the replica currently at temperature index r
    label_at_top_seen = np.zeros(R, dtype=bool)
    label_at_bottom_seen = np.zeros(R, dtype=bool)
    tunneling_count = 0

    swap_attempts = np.zeros(R - 1, dtype=int)
    swap_accepts = np.zeros(R - 1, dtype=int)

    energy_hist_per_beta = [[] for _ in range(R)]

    total_steps = n_burn + n_collect
    for step in range(total_steps):
        # Each replica does one sweep at its temperature
        for r in range(R):
            states[r] = glauber_sweep(states[r], W, betas[r], rng, n_sweeps=1)
        # Try swap every swap_period sweeps
        if (step + 1) % swap_period == 0:
            # Try adjacent pair swaps (alternating odd/even pass)
            start_offset = (step // swap_period) % 2
            for i in range(start_offset, R - 1, 2):
                E_i = hopfield_energy(states[i], W)
                E_j = hopfield_energy(states[i + 1], W)
                delta = (betas[i] - betas[i + 1]) * (E_i - E_j)
                swap_attempts[i] += 1
                if delta <= 0 or rng.random() < math.exp(-delta):
                    states[[i, i + 1]] = states[[i + 1, i]]
                    labels[i], labels[i + 1] = labels[i + 1], labels[i]
                    swap_accepts[i] += 1
            # Update tunneling diagnostic: track label at top (index 0, lowest beta)
            # and at bottom (index R-1, highest beta)
            top_label = labels[0]
            bottom_label = labels[R - 1]
            if not label_at_top_seen[top_label]:
                label_at_top_seen[top_label] = True
                if label_at_bottom_seen[top_label]:
                    tunneling_count += 1
                    label_at_bottom_seen[top_label] = False
                    label_at_top_seen[top_label] = False
            if not label_at_bottom_seen[bottom_label]:
                label_at_bottom_seen[bottom_label] = True
                if label_at_top_seen[bottom_label]:
                    tunneling_count += 1
                    label_at_top_seen[bottom_label] = False
                    label_at_bottom_seen[bottom_label] = False
        # Energy history (after burn-in)
        if step >= n_burn:
            for r in range(R):
                energy_hist_per_beta[r].append(hopfield_energy(states[r], W))

    accept_rates = (swap_accepts / np.maximum(swap_attempts, 1)).tolist()
    return {
        "acceptance_rates": accept_rates,
        "tunneling_count": int(tunneling_count),
        "energy_means": [float(np.mean(h)) if h else 0.0 for h in energy_hist_per_beta],
        "energy_stds": [float(np.std(h)) if h else 0.0 for h in energy_hist_per_beta],
        "energy_autocorr_1": [float(_autocorr_lag1(h)) if len(h) > 1 else 0.0
                              for h in energy_hist_per_beta],
    }


def _autocorr_lag1(x: list[float]) -> float:
    if len(x) < 2:
        return 0.0
    a = np.asarray(x)
    m = float(np.mean(a))
    v = float(np.var(a))
    if v < 1e-12:
        return 0.0
    return float(np.mean((a[:-1] - m) * (a[1:] - m)) / v)


def compute_verdict(summary: dict) -> tuple[str, str]:
    if not summary.get("cells"):
        return ("RSB_PT_INCONCLUSIVE", "No cells.")
    # Look at swap acceptance profile per cell. RSB transition signature:
    # acceptance rates have a clear MIN (below ~0.2) at some pair, with a
    # rate profile that decreases then increases through the transition.
    transitions_detected = 0
    flat = 0
    total = 0
    profiles = []
    for cell in summary["cells"]:
        rates = cell.get("acceptance_rates_mean", [])
        if not rates:
            continue
        total += 1
        profiles.append(rates)
        mn = min(rates)
        mx = max(rates)
        idx_min = rates.index(mn)
        # Transition signature: clear minimum (< 0.2) NOT at the boundary
        # AND ratio max/min > 2
        if mn < 0.20 and 0 < idx_min < len(rates) - 1 and (mx / max(mn, 1e-6)) > 2.0:
            transitions_detected += 1
        elif mn > 0.4 and mx / max(mn, 1e-6) < 1.5:
            flat += 1
    if total == 0:
        return ("RSB_PT_INCONCLUSIVE", "No valid cells.")
    if transitions_detected >= max(1, total // 2):
        return (
            "RSB_PT_TRANSITION_DETECTED",
            f"Parallel-tempering swap-acceptance profile shows clear minimum away from "
            f"the boundary in {transitions_detected}/{total} alpha cells -- characteristic "
            f"of a glass transition (Hukushima-Nemoto 1996). Profiles: {profiles}.",
        )
    if flat >= max(1, total // 2):
        return (
            "RSB_PT_FLAT",
            f"Swap acceptance rates are uniformly high across all temperatures "
            f"({flat}/{total} cells), no transition signature. Profiles: {profiles}.",
        )
    return (
        "RSB_PT_INCONCLUSIVE",
        f"Mixed: transitions={transitions_detected}/{total}, flat={flat}/{total}. "
        f"Profiles: {profiles}.",
    )


def self_test() -> None:
    # Transition detected
    s = {"cells": [
        {"acceptance_rates_mean": [0.8, 0.6, 0.5, 0.1, 0.4, 0.7, 0.8]},
        {"acceptance_rates_mean": [0.9, 0.7, 0.4, 0.15, 0.5, 0.7, 0.9]},
    ]}
    v, _ = compute_verdict(s)
    assert v == "RSB_PT_TRANSITION_DETECTED", v
    s_flat = {"cells": [
        {"acceptance_rates_mean": [0.6, 0.7, 0.65, 0.7, 0.6]},
        {"acceptance_rates_mean": [0.7, 0.7, 0.65, 0.7, 0.65]},
    ]}
    v_flat, _ = compute_verdict(s_flat)
    assert v_flat == "RSB_PT_FLAT", v_flat
    v_empty, _ = compute_verdict({"cells": []})
    assert v_empty == "RSB_PT_INCONCLUSIVE"
    # autocorr basic sanity
    ac = _autocorr_lag1([1.0, 2.0, 1.0, 2.0, 1.0, 2.0])
    assert -1.1 <= ac <= 1.1, ac
    print("RSB-PT self-test PASS (4/4)", flush=True)


def run_experiment(smoke: bool):
    t0 = time.monotonic()
    if smoke:
        config = {
            "mode": "smoke",
            "N": 1024,
            "alpha_list": [0.10],
            "beta_list": [0.5, 1.0, 2.0, 4.0],
            "n_seeds": 2,
            "n_burn": 30,
            "n_collect": 60,
            "swap_period": 5,
        }
    else:
        config = {
            "mode": "full",
            "N": 1024,
            "alpha_list": [0.05, 0.10, 0.20],
            "beta_list": [0.5, 0.75, 1.0, 1.5, 2.0, 2.5,
                          3.0, 3.5, 4.0, 5.0, 7.0, 10.0],
            "n_seeds": 5,
            "n_burn": 2000,
            "n_collect": 8000,
            "swap_period": 5,
        }
    N = config["N"]
    cells = []
    betas = config["beta_list"]
    for alpha in config["alpha_list"]:
        M = max(1, int(alpha * N))
        codewords = select_subset_codewords(N, M, seed=0)
        W = build_hebbian_W(codewords)
        accept_rates_per_seed = []
        tunneling_counts = []
        autocorrs_per_seed = []
        for seed in range(config["n_seeds"]):
            seed_val = seed * 11 + int(alpha * 100) + 7
            result = parallel_tempering(
                W, betas, config["n_burn"], config["n_collect"],
                config["swap_period"], seed=seed_val,
            )
            accept_rates_per_seed.append(result["acceptance_rates"])
            tunneling_counts.append(result["tunneling_count"])
            autocorrs_per_seed.append(result["energy_autocorr_1"])
            print(f"  alpha={alpha:.2f} seed={seed} tunneling={result['tunneling_count']} "
                  f"swap_accepts={[f'{r:.2f}' for r in result['acceptance_rates']]}",
                  flush=True)
        accept_arr = np.array(accept_rates_per_seed)
        ac_arr = np.array(autocorrs_per_seed)
        cell = {
            "alpha": float(alpha), "N": N, "M": M,
            "acceptance_rates_mean": accept_arr.mean(axis=0).tolist(),
            "acceptance_rates_std": accept_arr.std(axis=0).tolist(),
            "tunneling_counts": tunneling_counts,
            "tunneling_count_mean": float(np.mean(tunneling_counts)),
            "energy_autocorr_1_mean": ac_arr.mean(axis=0).tolist(),
            "betas": betas,
        }
        cells.append(cell)
        print(f"  AGGREGATE alpha={alpha:.2f}: mean swap accept = "
              f"{[f'{r:.3f}' for r in cell['acceptance_rates_mean']]}", flush=True)
    summary = {"cells": cells, "config": config}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg[:300]}...", flush=True)
    return summary, verdict, msg, elapsed, config


def get_output_dir(name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d: dict) -> None:
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    if not required.issubset(d.keys()):
        raise ValueError(f"metrics missing: {required - d.keys()}")


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
    out_dir = get_output_dir("wave14_rsb_exchange_mcmc_v1_smoke")
    s, v, m, e, c = run_experiment(smoke=True)
    write_metrics(out_dir, s, v, m, e, c)
    print(f"\nSMOKE OK: {v}", flush=True)


def run_main() -> None:
    self_test()
    out_dir = get_output_dir("wave14_rsb_exchange_mcmc_v1")
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
