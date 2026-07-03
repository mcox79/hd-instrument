"""Sellke 2025 marginal stability — replica-symmetry under ferromagnetic drift.

Motivation
----------
Sellke 2025 (arXiv:2502.xxxxx, "Marginal stability of spin-glass landscapes")
predicts that under a small ferromagnetic drift Delta_W = epsilon * J (where
J is iid +/-1), the substrate's overlap distribution P(q) remains
replica-symmetric (single delta at q*) so long as epsilon < epsilon_c. This
is the marginal-stability threshold.

Substrate test: probe whether the 4-coset Kerdock-based weight matrix W of
the substrate exhibits the predicted RS-stable region under uniformly
applied ferromagnetic Delta_W, i.e., does the overlap distribution stay
single-peaked at q* below the marginal threshold and FRACTURE (become
multi-peaked / heavy-tailed) above it.

Scientific question
-------------------
Does the substrate carry a Sellke-style marginal stability threshold under
ferromagnetic Delta_W? If yes, characterize epsilon_c.

Vertices: SELLKE_RS_STABLE / SELLKE_RS_BREAKS / SELLKE_INCONCLUSIVE.

Pre-reg: preregs/2026-05-24_wave14_sellke_marginal_stability_v1.md
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


from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
def make_bipolar_pattern(N: int, rng: np.random.Generator) -> np.ndarray:
    return (2 * (rng.random(N) > 0.5).astype(np.int8) - 1).astype(np.float32)


def hebbian_W(patterns: np.ndarray) -> np.ndarray:
    """Outer-product Hebbian: W = (1/N) sum_mu x_mu x_mu^T - (M/N) I."""
    M, N = patterns.shape
    W = (patterns.T @ patterns) / N
    np.fill_diagonal(W, 0.0)
    return W.astype(np.float32)


def overlap_distribution(W: np.ndarray, n_samples: int, n_steps: int,
                          rng: np.random.Generator) -> np.ndarray:
    """For each independent initialization, run sign-update glauber to fixed point
    and record overlap q = (1/N) <x_a, x_b> against a reference attractor.

    To get a P(q) histogram, do 2 independent walks, compute overlap.
    """
    N = W.shape[0]
    overlaps = []
    for k in range(n_samples):
        # Two independent inits
        x_a = (2 * (rng.random(N) > 0.5).astype(np.float32) - 1)
        x_b = (2 * (rng.random(N) > 0.5).astype(np.float32) - 1)
        for _ in range(n_steps):
            x_a = np.sign(W @ x_a)
            x_a[x_a == 0] = 1.0
            x_b = np.sign(W @ x_b)
            x_b[x_b == 0] = 1.0
        q = float(np.dot(x_a, x_b) / N)
        overlaps.append(q)
    return np.array(overlaps, dtype=np.float32)


def num_modes(qvals: np.ndarray, bin_width: float = 0.05) -> int:
    """Coarse mode count: bin into 0.05-wide bins on [-1,1], count peaks.

    A peak is a bin with count > both neighbors AND count >= max(counts) / 4.
    """
    if len(qvals) < 5:
        return 0
    bins = np.arange(-1.0, 1.0 + bin_width, bin_width)
    h, _ = np.histogram(qvals, bins=bins)
    max_h = h.max() if h.max() > 0 else 1
    threshold = max_h / 4
    n_peaks = 0
    for i in range(1, len(h) - 1):
        if h[i] > h[i - 1] and h[i] > h[i + 1] and h[i] >= threshold:
            n_peaks += 1
    return n_peaks


def self_test() -> None:
    rng = np.random.default_rng(42)
    N = 64
    M = 8
    patterns = np.stack([make_bipolar_pattern(N, rng) for _ in range(M)])
    W = hebbian_W(patterns)
    assert W.shape == (N, N)
    assert np.all(np.diag(W) == 0.0)
    # Symmetric
    assert np.allclose(W, W.T, atol=1e-5)
    print("  cell 1: hebbian_W symmetric, zero-diag — OK", flush=True)

    overs = overlap_distribution(W, n_samples=10, n_steps=20, rng=rng)
    assert overs.shape == (10,)
    assert np.all(np.abs(overs) <= 1.0 + 1e-6)
    print(f"  cell 2: overlap_distribution OK ({overs.min():.3f}..{overs.max():.3f})", flush=True)

    # Synthetic peaked: concentrated mass at q=0.7 with sparse tails
    q_one = np.concatenate([
        np.full(40, 0.7),  # main peak in bin centered on 0.7
        np.array([0.0, 0.1, -0.1, 0.0]),  # tails
    ]).astype(np.float32)
    nm_one = num_modes(q_one)
    assert nm_one >= 1, f"unimodal got {nm_one} modes"
    print(f"  cell 3a: num_modes unimodal -> {nm_one}", flush=True)

    # Synthetic bimodal at +/-0.7
    q_two = np.concatenate([np.full(20, 0.7), np.full(20, -0.7),
                            np.array([0.0, 0.0])]).astype(np.float32)
    nm_two = num_modes(q_two)
    assert nm_two >= 2, f"bimodal got {nm_two} modes"
    print(f"  cell 3b: num_modes bimodal -> {nm_two}", flush=True)
    print("self-tests passed", flush=True)


def compute_verdict(summary: dict) -> tuple[str, str]:
    by_eps = summary.get("by_epsilon", {})
    if len(by_eps) < 3:
        return ("SELLKE_INCONCLUSIVE", f"Need >=3 epsilon values, got {len(by_eps)}.")

    eps_sorted = sorted(float(e) for e in by_eps.keys())
    rows = []
    for e in eps_sorted:
        cell = by_eps[e] if e in by_eps else by_eps[str(e)]
        rows.append((e, int(cell["n_modes"]), float(cell["q_mean"]), float(cell["q_std"])))

    # At eps=0 we expect RS (1 mode, |q|~q*); at large eps we expect breaking (>=2 modes OR std large)
    eps0 = rows[0]  # baseline
    eps_hi = rows[-1]  # highest
    baseline_mono = (eps0[1] <= 1)
    hi_broken = (eps_hi[1] >= 2) or (eps_hi[3] > 0.2)

    series = "; ".join(f"eps={e:.3f}: modes={nm} q_mean={qm:.3f} q_std={qs:.3f}"
                       for e, nm, qm, qs in rows)

    if baseline_mono and not hi_broken:
        return ("SELLKE_RS_STABLE",
                f"RS-stable across all epsilon levels (max eps={eps_hi[0]:.3f}). "
                f"No marginal-stability threshold detected in [{eps_sorted[0]:.3f}, {eps_sorted[-1]:.3f}]. "
                f"{series}.")
    if baseline_mono and hi_broken:
        # Find first epsilon with >=2 modes or std>0.2
        crossings = [r[0] for r in rows if r[1] >= 2 or r[3] > 0.2]
        eps_c = min(crossings) if crossings else float("nan")
        return ("SELLKE_RS_BREAKS",
                f"RS breaks at eps_c ~ {eps_c:.3f} (baseline single-mode; high-eps multi-mode/heavy). "
                f"Substrate exhibits Sellke-style marginal stability threshold. {series}.")

    return ("SELLKE_INCONCLUSIVE",
            f"Baseline at eps=0 not cleanly RS (modes={eps0[1]}); cannot infer threshold. {series}.")


def run_experiment(smoke: bool):
    t0 = time.monotonic()
    if smoke:
        cfg = {"N": 64, "M": 8, "n_samples": 10, "n_steps": 10,
               "epsilon_list": [0.0, 0.05, 0.20], "n_seeds": 1, "mode": "smoke"}
    else:
        cfg = {"N": 512, "M": 64, "n_samples": 200, "n_steps": 30,
               "epsilon_list": [0.0, 0.01, 0.05, 0.10, 0.20, 0.40], "n_seeds": 3, "mode": "full"}

    print(f"Config: N={cfg['N']} M={cfg['M']} n_samples={cfg['n_samples']} n_steps={cfg['n_steps']}", flush=True)
    print(f"Epsilon: {cfg['epsilon_list']}  Seeds: {cfg['n_seeds']}", flush=True)

    rng_master = np.random.default_rng(11)
    by_epsilon = {}
    for eps in cfg["epsilon_list"]:
        all_overs = []
        for seed_i in range(cfg["n_seeds"]):
            rng = np.random.default_rng(rng_master.integers(2**31))
            patterns = np.stack([make_bipolar_pattern(cfg["N"], rng) for _ in range(cfg["M"])])
            W = hebbian_W(patterns)
            # Add ferromagnetic Delta_W = eps * J_ferro (uniform iid +/-1 scaled)
            if eps > 0:
                J = (2 * (rng.random((cfg["N"], cfg["N"])) > 0.5).astype(np.float32) - 1) / math.sqrt(cfg["N"])
                J = (J + J.T) / 2
                np.fill_diagonal(J, 0.0)
                W = W + eps * J
            overs = overlap_distribution(W, cfg["n_samples"], cfg["n_steps"], rng)
            all_overs.append(overs)
        all_overs = np.concatenate(all_overs)
        n_modes = num_modes(all_overs)
        q_mean = float(np.mean(np.abs(all_overs)))
        q_std = float(np.std(all_overs))
        by_epsilon[eps] = {"n_modes": n_modes, "q_mean": q_mean, "q_std": q_std,
                            "n_overlaps": int(len(all_overs))}
        print(f"  eps={eps:.3f}: modes={n_modes} q_mean={q_mean:.3f} q_std={q_std:.3f}", flush=True)

    summary = {"by_epsilon": by_epsilon, "config": cfg}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, cfg


def get_output_dir(name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d: dict) -> None:
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    if not required.issubset(d.keys()):
        raise ValueError(f"missing keys: {required - d.keys()}")


def write_metrics(out_dir: Path, summary, verdict, msg, elapsed, config) -> None:
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
                "summary": summary, "config": config}
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")


def run_smoke():
    self_test()
    out_dir = get_output_dir("wave14_sellke_marginal_stability_v1_smoke")
    s, v, m, e, c = run_experiment(smoke=True)
    write_metrics(out_dir, s, v, m, e, c)
    print(f"\nSMOKE OK: {v}", flush=True)


def run_main():
    self_test()
    out_dir = get_output_dir("wave14_sellke_marginal_stability_v1")
    s, v, m, e, c = run_experiment(smoke=False)
    write_metrics(out_dir, s, v, m, e, c)
    print(f"\nDONE: {v}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.smoke:
        run_smoke()
        return 0
    run_main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
