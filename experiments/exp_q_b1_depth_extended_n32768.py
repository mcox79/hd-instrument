"""
q_b1_depth_extended_n32768 -- Wave 5 Amendment ADD-1: heteroassoc chain depth-5 + 10 at N=32768.

SCIENTIFIC QUESTION:
  Does the substrate maintain production-grade fidelity on directed heteroassoc
  chains at depth 5 AND depth 10 at N=32768?

  Q-B1 v324: depth-3 = 0.986-0.993 at N={4096, 8192}. Per-hop ~0.995-0.998.
  Geometric extrapolation (per-hop independence confirmed by Q-B1 rho=0.0000):
    depth-5 prediction: 0.9953^5 to 0.9977^5 = 0.977-0.989
    depth-10 prediction: 0.9953^10 to 0.9977^10 = 0.954-0.977

PRE-REGISTERED BANDS (per Wave 5 amendment):
  HARD-PASS: depth-5 >= 0.95 AND depth-10 >= 0.90 across 5 seeds.
  HARD-FAIL: depth-5 < 0.85 OR depth-10 < 0.75 (per-hop independence breaks).
  MIDDLE: depth-5 [0.85, 0.95] OR depth-10 [0.75, 0.90].

ANCHOR / COST (per amendment):
  Cell construction: ONE chain at depth-10 with readout snapshots at
  depth-1/3/5/7/10. Single xi chain, multiple readout depths -- does not
  multiply cost. 5 seeds, R=200 random source patterns per seed.

PROT-018: anchor name has _n32768; N MUST = 32768.
PROT-021: run_config includes N, run_mode.
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
from typing import Dict, List

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir  # noqa: E402

ANCHOR_NAME = "q_b1_depth_extended_n32768"

# PROT-018: anchor has _n32768 -> N must = 32768
_N_SUFFIX = 32768
N_FULL = 32768
N_SMOKE = 4096

SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [7, 17]
N_CHAINS = 15      # number of distinct chains
M_BACKGROUND = 200 # background bindings (per amendment R=200)
CHAIN_DEPTH = 10
SNAPSHOT_DEPTHS = [1, 3, 5, 7, 10]

# Pre-reg bands
HP_D5 = 0.95
HP_D10 = 0.90
HF_D5 = 0.85
HF_D10 = 0.75


def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(np.dot(a, b)) / (na * nb)


def build_chain_H(chain_keys: List[np.ndarray], bg_keys: np.ndarray,
                  bg_vals: np.ndarray, N: int) -> np.ndarray:
    """Build H = sum_chains sum_hops val_h_k^T / N + sum_bg val_bg key_bg^T / N.

    For chain c: hop h binds chain_keys[c][h] -> chain_keys[c][h+1].
    """
    H = np.zeros((N, N), dtype=np.float32)
    for chain in chain_keys:
        for h in range(len(chain) - 1):
            H += np.outer(chain[h + 1], chain[h]) / N
    for i in range(bg_keys.shape[0]):
        H += np.outer(bg_vals[i], bg_keys[i]) / N
    return H


def _instrumentation_selftest():
    """Selftest: depth-10 chain on N=128 with single chain produces non-NaN cosine."""
    rng = np.random.default_rng(0)
    N_t = 128
    chain = [rng.choice([-1.0, 1.0], size=N_t).astype(np.float32)
             for _ in range(11)]  # depth 10 chain = 11 patterns
    H = build_chain_H([chain], np.zeros((0, N_t), dtype=np.float32),
                      np.zeros((0, N_t), dtype=np.float32), N_t)
    r = chain[0].copy()
    sims_t = []
    for d in range(10):
        r = H @ r
        sims_t.append(cosine_sim(r, chain[d + 1]))
    for s in sims_t:
        assert not math.isnan(s), "chain sim NaN"
        assert -1.0 <= s <= 1.0, f"chain sim out of range: {s}"
    print(f"[selftest] PASS: N={N_t} chain depth-10 sims: "
          f"{[round(s, 3) for s in sims_t[::2]]}", flush=True)


_instrumentation_selftest()


def _prot018_startup_check(n_actual: int) -> None:
    N_BOUND = 32768
    if n_actual != N_BOUND:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor name '{ANCHOR_NAME}' binds to "
            f"N={N_BOUND} but script is running at N={n_actual}.")


def main():
    t0 = time.time()
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    run_mode = os.environ.get("HDLAB_RUN_MODE", "full")
    seeds = SEEDS_FULL if run_mode == "full" else SEEDS_SMOKE
    N = N_FULL if run_mode == "full" else N_SMOKE
    if run_mode == "full":
        _prot018_startup_check(N)
    print(f"[{ANCHOR_NAME}] run_mode={run_mode} seeds={seeds} N={N} "
          f"n_chains={N_CHAINS} bg={M_BACKGROUND} depth={CHAIN_DEPTH}", flush=True)

    per_seed_results: List[Dict] = []
    for seed in seeds:
        rng = np.random.default_rng(seed)
        print(f"  seed={seed}: building chain H...", flush=True)
        t_cell = time.time()
        # N_CHAINS chains of depth-10 = 11 patterns each
        chain_keys = []
        for c in range(N_CHAINS):
            chain = [rng.choice([-1.0, 1.0], size=N).astype(np.float32)
                     for _ in range(CHAIN_DEPTH + 1)]
            chain_keys.append(chain)
        bg_keys = rng.choice([-1.0, 1.0], size=(M_BACKGROUND, N)).astype(np.float32)
        bg_vals = rng.choice([-1.0, 1.0], size=(M_BACKGROUND, N)).astype(np.float32)
        H = build_chain_H(chain_keys, bg_keys, bg_vals, N)

        # For each chain, walk depth-10 with snapshot fidelities
        depth_to_sims: Dict[int, List[float]] = {d: [] for d in SNAPSHOT_DEPTHS}
        for chain in chain_keys:
            r = chain[0].copy()
            for d in range(1, CHAIN_DEPTH + 1):
                r = H @ r
                if d in SNAPSHOT_DEPTHS:
                    sim = cosine_sim(r, chain[d])
                    depth_to_sims[d].append(sim)

        # Mean fidelity per snapshot depth
        depth_means = {f"depth_{d}": float(np.mean(depth_to_sims[d]))
                       for d in SNAPSHOT_DEPTHS}
        elapsed_cell = time.time() - t_cell
        print(f"    " + " ".join(f"d{d}={depth_means[f'depth_{d}']:.4f}"
                                 for d in SNAPSHOT_DEPTHS)
              + f" ({elapsed_cell:.1f}s)", flush=True)
        per_seed_results.append({
            "seed": seed,
            **depth_means,
            "elapsed_s": elapsed_cell,
        })

    # Aggregate: mean fidelity per depth across seeds
    depth_aggregate = {}
    for d in SNAPSHOT_DEPTHS:
        vals = [r[f"depth_{d}"] for r in per_seed_results]
        depth_aggregate[f"depth_{d}_mean"] = float(np.mean(vals))
        depth_aggregate[f"depth_{d}_min"] = float(np.min(vals))

    d5_mean = depth_aggregate["depth_5_mean"]
    d10_mean = depth_aggregate["depth_10_mean"]

    if d5_mean >= HP_D5 and d10_mean >= HP_D10:
        verdict = "HARD_PASS"
    elif d5_mean < HF_D5 or d10_mean < HF_D10:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    elapsed = time.time() - t0
    metrics = {
        "anchor": ANCHOR_NAME, "run_mode": run_mode,
        "N": N, "n_chains": N_CHAINS, "m_background": M_BACKGROUND,
        "chain_depth": CHAIN_DEPTH, "snapshot_depths": SNAPSHOT_DEPTHS,
        "n_seeds": len(seeds),
        "per_seed_results": per_seed_results,
        "depth_aggregate": depth_aggregate,
        "verdict": verdict,
        "elapsed_s": elapsed,
        "verdict_msg": (
            f"Q-B1 chain depth-extended at N={N}: "
            f"depth-5 mean={d5_mean:.4f}; depth-10 mean={d10_mean:.4f}. "
            f"Verdict: {verdict}."
        ),
    }
    mpath = out_dir / "metrics.json"
    with open(mpath, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[{ANCHOR_NAME}] verdict={verdict} elapsed={elapsed:.1f}s", flush=True)
    print(f"[{ANCHOR_NAME}] metrics -> {mpath}", flush=True)


if __name__ == "__main__":
    main()
