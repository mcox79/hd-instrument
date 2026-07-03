"""Parisi-style replica overlap P(q12) on substrate's Kerdock-Hebbian W.

Motivation
----------
The Parisi overlap distribution P(q12) between two INDEPENDENT thermal replicas
is the canonical spin-glass order parameter:

  q12 = (1/N) sum_i s_i^(1) s_i^(2)

For an Ising model in the:
  - paramagnetic phase: P(q12) is a single delta at q=0
  - ferromagnetic / Mattis phase: two deltas at q = +-m^2 (m = magnetization)
  - replica-symmetric (RS) spin-glass: P(q12) is two deltas at q = +-q_EA (Edwards-Anderson)
  - replica-symmetry-broken (RSB): P(q12) is CONTINUOUS with a nontrivial spectrum
    of overlaps (Parisi 1979, 1980, 1983). Full RSB has support on a continuous
    interval; 1-step RSB has support on two intervals.

The Sinova C_ij eigenvalue probe (wave14_sinova_cij_eigenvalue_v1) already tested
RSB structure on RANDOM BSC codewords. THIS experiment is the direct Parisi P(q12)
probe on Kerdock-Hebbian W -- the substrate's actual measurement matrix -- and is
complementary in two ways:

  1. Different probe family (replica-overlap distribution vs eigenvalue extensivity)
  2. Different codebook (4-coset Kerdock vs random BSC) -- so we test whether the
     Kerdock algebraic structure changes the RSB story

If we observe a nontrivial (continuous) P(q12) on Kerdock-Hebbian W: this is the
substrate-internal Hopfield-on-Kerdock spin-glass phase, complementary evidence
for the AMP_SE_DIVERGES finding (Kerdock matrix sustains glassy dynamics that an
AMP-universal matrix would not).

Protocol
--------
  1. Build Hebbian W from M Kerdock 4-coset codewords (M = alpha * N).
  2. Run 2 INDEPENDENT Glauber MC chains at the same temperature, both starting
     from fully random initial states (NOT from a stored codeword -- we want
     thermal sampling of the Boltzmann measure, not retrieval from a perturbed
     target).
  3. After burn-in, collect (s^(1), s^(2)) at every step and record q12.
  4. Histogram q12 to get P(q12).
  5. Classify shape: delta-at-zero, two-deltas, continuous-support.

Note this differs structurally from wave14_glauber_kerdock_v* which measures
overlap with a STORED CODEWORD (q = (1/N)<s, xi_mu>), not between replicas.
That is a "retrieval" probe; P(q12) is a "glass-order-parameter" probe.

Vertex: PARISI_RSB_KERDOCK / PARISI_RS_KERDOCK / PARISI_PARAMAGNET_KERDOCK /
        PARISI_INCONCLUSIVE.

Pre-reg: preregs/2026-05-23_wave14_parisi_pq_kerdock_v1.md
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
# Reuse Kerdock builder + Glauber sweep
_v1_path = REPO / "experiments" / "exp_wave14_glauber_kerdock_v1.py"
_spec = importlib.util.spec_from_file_location("glauber_v1", _v1_path)
_v1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_v1)

build_hebbian_W = _v1.build_hebbian_W
glauber_sweep = _v1.glauber_sweep
select_subset_codewords = _v1.select_subset_codewords


# ---------------------------------------------------------------------------
# Replica simulation
# ---------------------------------------------------------------------------

def simulate_replica_pair(
    W: np.ndarray,
    beta: float,
    n_burn: int,
    n_collect: int,
    seed: int,
) -> np.ndarray:
    """Two independent Glauber chains on shared W at temperature 1/beta.

    Both start from fully RANDOM +-1 spin configurations (independent seeds).
    After burn-in, collect q12 = (1/N) <s1, s2> at every sweep.

    Returns array of q12 samples, shape (n_collect,).
    """
    N = W.shape[0]
    rng1 = np.random.default_rng(seed * 2 + 0)
    rng2 = np.random.default_rng(seed * 2 + 1)

    s1 = np.where(rng1.random(N) < 0.5, 1.0, -1.0)
    s2 = np.where(rng2.random(N) < 0.5, 1.0, -1.0)

    for _ in range(n_burn):
        s1 = glauber_sweep(s1, W, beta, rng1, n_sweeps=1)
        s2 = glauber_sweep(s2, W, beta, rng2, n_sweeps=1)

    q12 = np.empty(n_collect, dtype=np.float64)
    for i in range(n_collect):
        s1 = glauber_sweep(s1, W, beta, rng1, n_sweeps=1)
        s2 = glauber_sweep(s2, W, beta, rng2, n_sweeps=1)
        q12[i] = float(np.dot(s1, s2)) / N
    return q12


# ---------------------------------------------------------------------------
# Shape classifier for P(q12)
# ---------------------------------------------------------------------------

def classify_pq_shape(q_samples: np.ndarray) -> dict:
    """Classify shape of P(q12). Returns dict with structural metrics.

    Metrics:
      - q_abs_mean, q_var, q_skew, q_kurtosis
      - support_width: fraction of 41-bin histogram with density > 5% of peak
        (counts contiguous and non-contiguous mass)
      - support_continuous_fraction: longest contiguous run of "supported" bins
        (those with density > 5% of peak) / total supported bins
      - n_peaks: number of local maxima with density > 10% of peak (with min
        spacing of 3 bins to avoid jitter)
      - delta_at_zero_frac: density mass in central 3 bins (q in [-0.075, 0.075])
        relative to total mass (1.0)
    """
    q = np.asarray(q_samples)
    n = q.shape[0]
    if n == 0:
        return {}

    bins = np.linspace(-1.0, 1.0, 42)
    hist, edges = np.histogram(q, bins=bins, density=True)
    bin_width = edges[1] - edges[0]
    peak = float(hist.max())
    if peak < 1e-9:
        peak = 1e-9

    supported = hist > 0.05 * peak

    # support_width: count of supported bins / total bins
    support_width = float(supported.sum()) / float(len(hist))

    # longest contiguous run
    runs = []
    run_len = 0
    for sup in supported:
        if sup:
            run_len += 1
        else:
            if run_len > 0:
                runs.append(run_len)
            run_len = 0
    if run_len > 0:
        runs.append(run_len)
    longest_run = max(runs) if runs else 0
    total_sup = max(int(supported.sum()), 1)
    cont_frac = longest_run / total_sup

    # n_peaks: local maxima with min spacing 3 and density > 0.1*peak
    peak_thresh = 0.10 * peak
    peaks = []
    for i in range(1, len(hist) - 1):
        if hist[i] >= hist[i - 1] and hist[i] >= hist[i + 1] and hist[i] > peak_thresh:
            if not peaks or (i - peaks[-1]) >= 3:
                peaks.append(i)
    n_peaks = len(peaks)

    # delta-at-zero fraction: fraction of total density mass in central bins
    # Central 5 bins (q in [-0.10, +0.10] approx) for tolerance
    center_idx = len(hist) // 2
    central_mass = float(hist[center_idx - 2 : center_idx + 3].sum()) * bin_width
    delta_at_zero_frac = central_mass  # since density integrates to 1

    return {
        "q_mean": float(np.mean(q)),
        "q_abs_mean": float(np.mean(np.abs(q))),
        "q_var": float(np.var(q)),
        "support_width": float(support_width),
        "support_continuous_fraction": float(cont_frac),
        "n_peaks": int(n_peaks),
        "delta_at_zero_frac": float(delta_at_zero_frac),
        "peak_density": float(peak),
        "histogram": hist.tolist(),
        "bin_edges": edges.tolist(),
    }


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------

def compute_verdict(summary: dict) -> tuple[str, str]:
    """Per-cell shape classification aggregated to global verdict.

    Per-cell shape (decided from classification metrics at beta>=4 low-T cells):
      paramagnet: delta_at_zero_frac > 0.6 AND n_peaks <= 1 AND support_width < 0.3
      two-deltas (RS / Mattis): n_peaks == 2 AND delta_at_zero_frac < 0.3 AND support_width < 0.4
      continuous (RSB): support_width > 0.5 AND support_continuous_fraction > 0.5
                        AND (n_peaks >= 3 OR (support_width > 0.7 AND n_peaks >= 2))
      undetermined: else

    Global:
      RSB if any low-T cell is "continuous"
      RS  if all low-T cells are "two-deltas" or "paramagnet" with majority paramagnet=False
      PARAMAGNET if all low-T cells are "paramagnet"
      INCONCLUSIVE otherwise
    """
    if not summary.get("cells"):
        return ("PARISI_INCONCLUSIVE", "No cells computed.")

    shapes = {"continuous": 0, "two_deltas": 0, "paramagnet": 0, "undetermined": 0}
    low_T_cells = []
    for cell in summary["cells"]:
        beta = cell.get("beta", 0.0)
        if beta < 4.0:
            continue
        low_T_cells.append(cell)
        dz = cell.get("delta_at_zero_frac", 0.0)
        np_ = cell.get("n_peaks", 0)
        sw = cell.get("support_width", 0.0)
        scf = cell.get("support_continuous_fraction", 0.0)

        if sw > 0.5 and scf > 0.5 and (np_ >= 3 or (sw > 0.7 and np_ >= 2)):
            shapes["continuous"] += 1
            cell["shape"] = "continuous"
        elif np_ == 2 and dz < 0.3 and sw < 0.4:
            shapes["two_deltas"] += 1
            cell["shape"] = "two_deltas"
        elif dz > 0.6 and np_ <= 1 and sw < 0.3:
            shapes["paramagnet"] += 1
            cell["shape"] = "paramagnet"
        else:
            shapes["undetermined"] += 1
            cell["shape"] = "undetermined"

    n_low = len(low_T_cells)
    if n_low == 0:
        return ("PARISI_INCONCLUSIVE", "No low-T (beta>=4) cells in sweep.")

    if shapes["continuous"] >= 1:
        return (
            "PARISI_RSB_KERDOCK",
            f"Parisi P(q12) on Kerdock-Hebbian W shows CONTINUOUS support at low T "
            f"({shapes['continuous']}/{n_low} low-T cells classified as continuous; "
            f"shape counts: {shapes}). Substrate's Kerdock-Hopfield model supports a "
            f"replica-symmetry-broken thermal phase -- consistent with a glassy "
            f"free-energy landscape; complements AMP_SE_DIVERGES (Kerdock matrix "
            f"sustains glassy dynamics that AMP-universal matrices do not).",
        )
    if shapes["paramagnet"] == n_low:
        return (
            "PARISI_PARAMAGNET_KERDOCK",
            f"All {n_low} low-T cells show paramagnetic P(q12) (single delta at q=0). "
            f"Glauber dynamics on Kerdock-Hebbian W does not enter an ordered phase "
            f"at beta in [4, ...]. Either T_c is higher than tested, or substrate-"
            f"internal Hopfield-on-Kerdock has unusually high transition temperature, "
            f"or the W structure does not support ordering at all. Inconsistent with "
            f"naive AGS theory for Hebbian-on-orthogonal-ish codewords; flag.",
        )
    if shapes["two_deltas"] >= max(1, n_low // 2) and shapes["continuous"] == 0:
        return (
            "PARISI_RS_KERDOCK",
            f"P(q12) shows two-delta shape at low T ({shapes['two_deltas']}/{n_low}), "
            f"consistent with REPLICA-SYMMETRIC retrieval phase (Edwards-Anderson "
            f"q_EA != 0 with no RSB). Substrate-Kerdock-Hopfield is RS-like; no glassy "
            f"complexity. Counter-evidence to RSB; AMP_SE_DIVERGES must originate "
            f"elsewhere (free-cumulants / eigenvector mechanism).",
        )

    return (
        "PARISI_INCONCLUSIVE",
        f"Mixed low-T shapes: {shapes}. Need longer chains or finer T grid.",
    )


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

def self_test() -> None:
    """Test shape classifier on synthetic q12 samples + verdict branches."""
    rng = np.random.default_rng(0)

    # Test 1: paramagnetic Gaussian at q=0
    q = rng.normal(0.0, 0.02, size=5000)
    q = np.clip(q, -1.0, 1.0)
    cls = classify_pq_shape(q)
    assert cls["delta_at_zero_frac"] > 0.6, f"paramagnet test: dz={cls['delta_at_zero_frac']}"
    assert cls["n_peaks"] <= 1, f"paramagnet test: n_peaks={cls['n_peaks']}"
    assert cls["support_width"] < 0.3

    # Test 2: two-delta (q ~ +-0.7)
    q = np.concatenate([
        rng.normal(0.7, 0.03, size=2500),
        rng.normal(-0.7, 0.03, size=2500),
    ])
    q = np.clip(q, -1.0, 1.0)
    cls = classify_pq_shape(q)
    assert cls["n_peaks"] == 2, f"two-delta test: n_peaks={cls['n_peaks']}"
    assert cls["delta_at_zero_frac"] < 0.3

    # Test 3: continuous RSB-like (uniform on [-0.8, 0.8])
    q = rng.uniform(-0.8, 0.8, size=5000)
    cls = classify_pq_shape(q)
    assert cls["support_width"] > 0.5, f"continuous test: sw={cls['support_width']}"
    assert cls["support_continuous_fraction"] > 0.5

    # Test 4: verdict RSB
    summary = {"cells": [
        {"beta": 4.0, "support_width": 0.8, "support_continuous_fraction": 0.9,
         "n_peaks": 4, "delta_at_zero_frac": 0.1},
    ]}
    v, _ = compute_verdict(summary)
    assert v == "PARISI_RSB_KERDOCK", f"expected RSB got {v}"

    # Test 5: verdict PARAMAGNET
    summary = {"cells": [
        {"beta": 4.0, "support_width": 0.2, "support_continuous_fraction": 1.0,
         "n_peaks": 1, "delta_at_zero_frac": 0.8},
        {"beta": 8.0, "support_width": 0.15, "support_continuous_fraction": 1.0,
         "n_peaks": 1, "delta_at_zero_frac": 0.85},
    ]}
    v, _ = compute_verdict(summary)
    assert v == "PARISI_PARAMAGNET_KERDOCK", f"expected PARAMAGNET got {v}"

    # Test 6: verdict RS (two_deltas)
    summary = {"cells": [
        {"beta": 4.0, "support_width": 0.3, "support_continuous_fraction": 0.5,
         "n_peaks": 2, "delta_at_zero_frac": 0.1},
        {"beta": 8.0, "support_width": 0.3, "support_continuous_fraction": 0.5,
         "n_peaks": 2, "delta_at_zero_frac": 0.05},
    ]}
    v, _ = compute_verdict(summary)
    assert v == "PARISI_RS_KERDOCK", f"expected RS got {v}"

    # Test 7: verdict INCONCLUSIVE (no low-T cells)
    summary = {"cells": [
        {"beta": 1.0, "support_width": 0.3, "support_continuous_fraction": 0.5,
         "n_peaks": 1, "delta_at_zero_frac": 0.5},
    ]}
    v, _ = compute_verdict(summary)
    assert v == "PARISI_INCONCLUSIVE", f"expected INCONCLUSIVE got {v}"

    # Test 8: empty
    v, _ = compute_verdict({"cells": []})
    assert v == "PARISI_INCONCLUSIVE", f"expected INCONCLUSIVE got {v}"

    print("Parisi self-test passed (8/8 cases)", flush=True)


# ---------------------------------------------------------------------------
# Main experiment
# ---------------------------------------------------------------------------

def run_experiment(smoke: bool) -> tuple[dict, str, str, float, dict]:
    t0 = time.monotonic()

    if smoke:
        config = {
            "mode": "smoke",
            "N": 1024,
            "alpha_list": [0.10],
            "beta_list": [2.0, 6.0],
            "n_seeds": 2,
            "n_burn": 50,
            "n_collect": 100,
        }
    else:
        config = {
            "mode": "full",
            "N": 1024,
            "alpha_list": [0.05, 0.10, 0.20],
            "beta_list": [1.0, 2.0, 4.0, 6.0, 8.0, 12.0],
            "n_seeds": 5,
            "n_burn": 300,
            "n_collect": 500,
        }

    N = config["N"]
    cells = []

    for alpha in config["alpha_list"]:
        M = max(1, int(alpha * N))
        for beta in config["beta_list"]:
            shapes_per_seed = []
            q12_means = []
            q12_abs_means = []
            support_widths = []
            n_peaks_list = []
            cont_fracs = []
            dz_fracs = []

            for seed in range(config["n_seeds"]):
                seed_val = seed * 1000 + int(alpha * 1000) + int(beta * 13)
                codewords = select_subset_codewords(N, M, seed=seed_val)
                W = build_hebbian_W(codewords)
                q12 = simulate_replica_pair(
                    W, beta,
                    n_burn=config["n_burn"],
                    n_collect=config["n_collect"],
                    seed=seed_val + 777,
                )
                cls = classify_pq_shape(q12)
                q12_means.append(cls["q_mean"])
                q12_abs_means.append(cls["q_abs_mean"])
                support_widths.append(cls["support_width"])
                n_peaks_list.append(cls["n_peaks"])
                cont_fracs.append(cls["support_continuous_fraction"])
                dz_fracs.append(cls["delta_at_zero_frac"])
                print(
                    f"  alpha={alpha:.3f} beta={beta:.2f} seed={seed} "
                    f"q12_mean={cls['q_mean']:+.3f} q12_abs={cls['q_abs_mean']:.3f} "
                    f"sw={cls['support_width']:.2f} n_peaks={cls['n_peaks']} "
                    f"dz={cls['delta_at_zero_frac']:.2f} cont_frac={cls['support_continuous_fraction']:.2f}",
                    flush=True,
                )

            cell = {
                "alpha": float(alpha),
                "beta": float(beta),
                "N": N, "M": M,
                "q12_mean": float(np.mean(q12_means)),
                "q12_abs_mean": float(np.mean(q12_abs_means)),
                "support_width": float(np.mean(support_widths)),
                "support_width_std": float(np.std(support_widths)),
                "n_peaks": float(np.mean(n_peaks_list)),
                "support_continuous_fraction": float(np.mean(cont_fracs)),
                "delta_at_zero_frac": float(np.mean(dz_fracs)),
                "n_seeds": config["n_seeds"],
            }
            cells.append(cell)
            print(
                f"  AGGREGATE alpha={alpha:.3f} beta={beta:.2f}: "
                f"sw={cell['support_width']:.2f} n_peaks={cell['n_peaks']:.1f} "
                f"dz={cell['delta_at_zero_frac']:.2f} cont={cell['support_continuous_fraction']:.2f}",
                flush=True,
            )

    summary = {"cells": cells, "config": config}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


def get_output_dir(name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d: dict) -> None:
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required fields: {missing}")
    if not d.get("verdict"):
        raise ValueError("empty verdict")


def write_metrics(out_dir: Path, summary: dict, verdict: str, msg: str,
                  elapsed: float, config: dict) -> None:
    metrics = {
        "verdict": verdict,
        "verdict_msg": msg,
        "elapsed_s": elapsed,
        "summary": summary,
        "config": config,
    }
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")
    print(f"wrote {out_dir / 'metrics.json'}", flush=True)


def run_smoke() -> None:
    self_test()
    out_dir = get_output_dir("wave14_parisi_pq_kerdock_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    assert len(summary["cells"]) >= 1, "smoke FAIL: no cells"
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main() -> None:
    self_test()
    out_dir = get_output_dir("wave14_parisi_pq_kerdock_v1")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nDONE: {verdict}", flush=True)


def main() -> int:
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
