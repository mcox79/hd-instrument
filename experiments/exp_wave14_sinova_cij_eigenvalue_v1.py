"""Sinova C_ij extensive-eigenvalue probe -- RSB discriminator at FULL scale.

Sinova-Houdayer-Martin (Phys Rev Lett 82, 1999) analysis:
  C_ij = <s_i s_j>_T - <s_i>_T <s_j>_T   (connected time-correlation matrix)

The eigenvalue spectrum of C_ij distinguishes phases:
  RS / paramagnet: all eigenvalues intensive (lambda_k / N -> 0 as N -> inf)
  RSB:             a few eigenvalues are EXTENSIVE (lambda_k / N stays finite)

This probe is cleaner than scalar Parisi P(q) at finite N because:
  - No q-binning artifact
  - Direct linear-algebra quantity: single eigvalsh call
  - Extensive count is a discrete, hard-to-fake integer

Protocol:
  1. Build Hopfield W from alpha*N random BSC codewords (Hebbian rule)
  2. Run Glauber MC at beta=2.0 (below T_c but in substrate operating regime)
  3. Collect n_seeds independent MC chains (each seeded differently)
  4. Compute per-seed C_ij; average them; extract eigvalsh
  5. Count eigenvalues with lambda/N > threshold_rel
  6. Subtract W-inherited extensive count to get EXCESS extensive count
  7. Sweep K in [50, 100, 200, 400, 800] (the substrate's operating K-grid)

Verdicts:
  SINOVA_RS_PARAMAGNET:  excess extensive eigvals == 0 across all K -> RS phase
  SINOVA_RSB_DETECTED:   excess extensive eigvals >= 2 at any K -> RSB signature
  SINOVA_INCONCLUSIVE:   excess == 1 at all K (boundary case) or noisy

Pre-reg: preregs/2026-05-23_wave14_sinova_cij_eigenvalue_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import argparse, json, math, os, time
from pathlib import Path

import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from verification import oracle  # noqa: E402
try:
    from hdlab.session_log import log_event
except ImportError:
    def log_event(*a, **k): pass


# ---- config helpers ----------------------------------------------------------

def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required keys: {missing}")


# ---- verdict logic -----------------------------------------------------------

def compute_verdict(summary):
    """Classify RSB phase from per-K extensive eigenvalue counts."""
    by_K = summary.get("by_K", {})
    if not by_K:
        return ("SINOVA_INCONCLUSIVE", "No by_K data -- experiment did not run.")

    # Collect excess counts across K values
    excesses = []
    for k_str, d in by_K.items():
        excesses.append(d.get("excess_extensive", 0))

    max_excess = max(excesses)
    min_excess = min(excesses)
    n_rsb = sum(1 for e in excesses if e >= 2)
    n_rs = sum(1 for e in excesses if e == 0)
    total_K = len(excesses)

    # Hard PASS: RSB (excess >= 2 at >= half the K points)
    if n_rsb >= max(1, total_K // 2):
        return (
            "SINOVA_RSB_DETECTED",
            f"RSB signature detected: {n_rsb}/{total_K} K values have excess extensive "
            f"eigenvalues >= 2 (max_excess={max_excess}). Substrate has hidden RSB at "
            f"finite N; NOT purely RS/paramagnetic. "
            f"by_K excess counts: " + ", ".join(
                f"K={k}:excess={d['excess_extensive']}"
                for k, d in sorted(by_K.items(), key=lambda x: int(x[0]))
            )
        )

    # Hard PASS: RS / paramagnet (excess == 0 at >= 2/3 K points)
    if n_rs >= (2 * total_K) // 3:
        return (
            "SINOVA_RS_PARAMAGNET",
            f"RS paramagnet confirmed: {n_rs}/{total_K} K values have excess extensive "
            f"eigenvalues == 0. Purely intensive spectrum -- substrate is RS at finite N. "
            f"Consistent with cycle-122 4-anchor RS certification. "
            f"by_K excess counts: " + ", ".join(
                f"K={k}:excess={d['excess_extensive']}"
                for k, d in sorted(by_K.items(), key=lambda x: int(x[0]))
            )
        )

    # Boundary / inconclusive
    return (
        "SINOVA_INCONCLUSIVE",
        f"Boundary case: max_excess={max_excess} min_excess={min_excess} "
        f"n_rsb={n_rsb}/{total_K} n_rs={n_rs}/{total_K}. "
        f"Excess==1 at boundary; increase N or n_samples for resolution. "
        f"by_K excess counts: " + ", ".join(
            f"K={k}:excess={d['excess_extensive']}"
            for k, d in sorted(by_K.items(), key=lambda x: int(x[0]))
        )
    )


def self_test_verdict():
    """Self-test verdict logic: 6 cases."""
    cases = [
        # RSB: excess >= 2 at >= half K points
        ({"by_K": {"50": {"excess_extensive": 3}, "100": {"excess_extensive": 4},
                   "200": {"excess_extensive": 2}, "400": {"excess_extensive": 1},
                   "800": {"excess_extensive": 3}}},
         "SINOVA_RSB_DETECTED"),
        # RS: excess == 0 at >= 2/3 K points
        ({"by_K": {"50": {"excess_extensive": 0}, "100": {"excess_extensive": 0},
                   "200": {"excess_extensive": 0}, "400": {"excess_extensive": 0},
                   "800": {"excess_extensive": 1}}},
         "SINOVA_RS_PARAMAGNET"),
        # Inconclusive: excess==1 everywhere
        ({"by_K": {"50": {"excess_extensive": 1}, "100": {"excess_extensive": 1},
                   "200": {"excess_extensive": 1}}},
         "SINOVA_INCONCLUSIVE"),
        # RSB detected even with one K missing
        ({"by_K": {"100": {"excess_extensive": 5}, "200": {"excess_extensive": 4}}},
         "SINOVA_RSB_DETECTED"),
        # RS with all zeros
        ({"by_K": {"100": {"excess_extensive": 0}, "200": {"excess_extensive": 0},
                   "400": {"excess_extensive": 0}}},
         "SINOVA_RS_PARAMAGNET"),
        # Empty -> INCONCLUSIVE
        ({},
         "SINOVA_INCONCLUSIVE"),
    ]
    for s, expected in cases:
        got, _ = compute_verdict(s)
        if got != expected:
            raise AssertionError(f"self_test FAIL: expected {expected} got {got}\n  summary={s}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


# ---- substrate / MC primitives -----------------------------------------------

def build_hopfield_W(K, N, rng):
    """Hebbian W from K random BSC codewords. Shape (N, N) float32. Diagonal=0."""
    bits = (rng.random((K, N)) > 0.5)
    patterns = 2.0 * bits.astype(np.float32) - 1.0  # {-1, +1}
    W = (patterns.T @ patterns) / N
    np.fill_diagonal(W, 0.0)
    return W.astype(np.float32)


def glauber_sweep(s, W, beta, rng):
    """One full Glauber sweep over all N spins (random order). In-place."""
    N = len(s)
    order = rng.permutation(N)
    u = rng.random(N).astype(np.float32)
    for idx_pos, idx in enumerate(order):
        h_i = float(W[idx] @ s)
        p_plus = 1.0 / (1.0 + math.exp(-2.0 * beta * h_i))
        s[idx] = 1.0 if u[idx_pos] < p_plus else -1.0
    return s


def run_mc_chain(W, N, beta, n_burn, n_sample, sample_interval, rng):
    """Burn-in + collect samples. Returns array (n_sample, N) float32."""
    s = (2.0 * (rng.random(N) > 0.5).astype(np.float32) - 1.0)
    for _ in range(n_burn):
        s = glauber_sweep(s, W, beta, rng)
    samples = np.empty((n_sample, N), dtype=np.float32)
    for i in range(n_sample * sample_interval):
        s = glauber_sweep(s, W, beta, rng)
        if (i + 1) % sample_interval == 0:
            samples[(i + 1) // sample_interval - 1] = s
    return samples


# ---- C_ij probe --------------------------------------------------------------

def compute_cij_probe(W, N, beta, n_seeds, n_burn, n_sample, sample_interval,
                       threshold_rel, base_seed):
    """Compute C_ij averaged over n_seeds MC chains; extract extensive eigvals.

    Returns dict with:
      n_extensive_C: eigvals of C with lambda/N > threshold_rel
      n_extensive_W: eigvals of W with lambda/N > threshold_rel
      excess_extensive: n_extensive_C - n_extensive_W
      top_eigvals_C: top-5 eigenvalues of C (for diagnostics)
      top_eigvals_W: top-5 eigenvalues of W (for diagnostics)
    """
    # Accumulate C_ij = E[s_i s_j] - E[s_i] E[s_j] across seeds
    C_sum = np.zeros((N, N), dtype=np.float64)
    for seed_offset in range(n_seeds):
        rng = np.random.default_rng(base_seed + seed_offset * 1009)
        samples = run_mc_chain(W, N, beta, n_burn, n_sample, sample_interval, rng)
        # connected correlation
        mean_s = samples.mean(axis=0)  # (N,)
        C_seed = (samples.T @ samples).astype(np.float64) / n_sample
        C_seed -= np.outer(mean_s, mean_s)
        C_sum += C_seed

    C_avg = (C_sum / n_seeds).astype(np.float32)

    # Eigenvalues (symmetric matrix; ascending order)
    eigvals_C = np.linalg.eigvalsh(C_avg)  # (N,) ascending
    eigvals_W = np.linalg.eigvalsh(W.astype(np.float32))

    n_extensive_C = int(((eigvals_C / N) > threshold_rel).sum())
    n_extensive_W = int(((eigvals_W / N) > threshold_rel).sum())
    excess = n_extensive_C - n_extensive_W

    return {
        "n_extensive_C": n_extensive_C,
        "n_extensive_W": n_extensive_W,
        "excess_extensive": excess,
        "top_eigvals_C": eigvals_C[-5:].tolist(),
        "top_eigvals_W": eigvals_W[-5:].tolist(),
        "eigval_C_max_scaled": float(eigvals_C[-1] / N),
        "eigval_C_min_scaled": float(eigvals_C[0] / N),
    }


# ---- main experiment ----------------------------------------------------------

def run_experiment(smoke):
    t0 = time.monotonic()
    config = {
        "mode": "smoke" if smoke else "full",
        "N": 256 if smoke else 4096,
        "K_grid": [10, 25] if smoke else [50, 100, 200, 400, 800],
        "beta": 2.0,
        "n_seeds": 2 if smoke else 5,
        "n_burn": 10 if smoke else 100,
        "n_sample": 20 if smoke else 200,
        "sample_interval": 3 if smoke else 20,
        "threshold_rel": 0.1,
        "base_seed": 42,
    }

    N = config["N"]
    print(f"[config] N={N} K_grid={config['K_grid']} n_seeds={config['n_seeds']} "
          f"n_sample={config['n_sample']} sample_interval={config['sample_interval']}",
          flush=True)

    # Memory estimate
    # W: N*N float32 = N^2 * 4 bytes
    # C_avg: same
    # samples per seed: n_sample * N * 4 bytes
    w_mb = N * N * 4 / 1e6
    samples_mb = config["n_sample"] * N * 4 / 1e6
    print(f"[memory] W={w_mb:.1f} MB per K, samples per seed={samples_mb:.1f} MB", flush=True)

    by_K = {}
    for K in config["K_grid"]:
        t_K = time.monotonic()
        print(f"\n[K={K}] building W (alpha={K/N:.3f})...", flush=True)

        # Build W using seed derived from K to ensure independent draws per K
        w_rng = np.random.default_rng(config["base_seed"] + K * 31)
        W = build_hopfield_W(K, N, w_rng)

        print(f"[K={K}] running C_ij probe (n_seeds={config['n_seeds']})...", flush=True)
        result = compute_cij_probe(
            W, N,
            beta=config["beta"],
            n_seeds=config["n_seeds"],
            n_burn=config["n_burn"],
            n_sample=config["n_sample"],
            sample_interval=config["sample_interval"],
            threshold_rel=config["threshold_rel"],
            base_seed=config["base_seed"] + K * 7,
        )
        result["K"] = K
        result["alpha"] = K / N
        elapsed_K = time.monotonic() - t_K
        print(f"[K={K}] n_extensive_C={result['n_extensive_C']} "
              f"n_extensive_W={result['n_extensive_W']} "
              f"excess={result['excess_extensive']} "
              f"top_C_scaled={[f'{v/N:.4f}' for v in result['top_eigvals_C']]} "
              f"elapsed={elapsed_K:.1f}s",
              flush=True)
        by_K[str(K)] = result

    summary = {
        "by_K": by_K,
        "N": N,
        "n_K_tested": len(by_K),
        "excess_counts": {k: v["excess_extensive"] for k, v in by_K.items()},
    }
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0

    print(f"\nVERDICT: {verdict}", flush=True)
    print(f"  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
               "summary": summary, "config": config}
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14_sinova_cij_eigenvalue_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    # Oracle: we must have computed at least one K successfully
    n_K = summary.get("n_K_tested", 0)
    oracle.assert_baseline_high("k_points_computed", float(n_K), 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_sinova_cij_eigenvalue_v1")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nDONE: {verdict}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test_verdict()
        return 0
    if args.smoke:
        run_smoke()
        return 0
    run_main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
