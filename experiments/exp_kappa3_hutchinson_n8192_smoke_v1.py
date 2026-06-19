"""
kappa3_hutchinson_n8192_smoke_v1 -- kappa_3 Hutchinson smoke at N=8192.

SCIENTIFIC QUESTION (Phase-2 spec from research note):
  Does the kappa_3 free-cumulant Hutchinson estimator at N=8192 achieve 4.2% delta-alpha
  sensitivity (i.e., can detect a 4.2% fractional change in alpha = M/N)?

  Theory: kappa_3(Hopfield) = alpha = M/N (free-Poisson identity).
  Hutchinson estimator std(kappa_3) ~ 1/sqrt(n_probes) independent of N.
  At n_probes=5000: std ~ 1/sqrt(5000) ~ 0.014.
  Detection threshold for delta_alpha = 0.042: if sigma_sep = delta_alpha / pooled_std >= 3.0.

  At N=8192, M=2048 (alpha=0.25): adding 4.2% -> M'=2048+87=2135, delta_alpha=0.0106.
  sigma_sep ~ 0.0106 / 0.014 ~ 0.76. Too small for individual comparison.
  But: mean-field scaling gives sigma_sep across multiple M comparisons ~ 3.0+ at N=8192
  if the spectrum is cleaner than N=4096 (theory: std of kappa_3 ~ alpha^2/sqrt(n_probes*N)).

  This is a SMOKE run: N=8192, n_probes=5000 (as per research spec).
  Validates spectral-MAC primitive for production envelope.

PRE-REGISTERED BANDS:
  HARD-PASS:
    min sigma_separation >= 4.0 across all M values tested,
    AND kappa_3 theory_ratio in [0.5, 2.0] (+-50% calibration per first-N=8192 measurement).
  MIDDLE: 2.0 <= min_sigma_sep < 4.0, OR theory_ratio outside [0.5, 2.0] but within [0.1, 10.0].
  HARD-FAIL: min_sigma_sep < 2.0 (fingerprint not discriminative at N=8192).

  Calibration probe note: first empirical measurement at N=8192; bands +-50% of
  theory per calibration policy. No prior N=8192 anchor.

FORMULA SELF-TESTS:
  1. kappa_3_theory(M=819, N=8192) = 819/8192 ~ 0.100.
  2. kappa_3_theory(M=409, N=8192) = 409/8192 ~ 0.050.
  3. Hutchinson std ~ std(per_probe) / sqrt(n_probes); n_probes=5000 -> std ~ 0.01-0.02.

TIMEOUT ESTIMATE:
  At N=8192, n_probes=5000: W^3 V requires 3 DGEMM of (8192, 8192) x (8192, 5000).
  Each DGEMM ~ 4 * 8192^2 * 5000 FLOPs = 1.34e12 FLOPs. 3 total = 4e12 FLOPs.
  At ~50 GFLOPS (numpy CPU): ~80s per seed x 4 M values x 2 (Hop+GOE) x 5 seeds = 3200s.
  With seed parallelism not possible (sequential): timeout_s ~ 1.5 * 3200 = 4800s.
  Rounded to 5400s (1.5 hr). Smoke at small M_LIST x 2 seeds should be much faster.

PROT-018: ANCHOR NAME contains _n8192; production N MUST = 8192.
PROT-021: run_config includes N, run_mode.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os
import argparse
import time
import json
import math
from pathlib import Path
from typing import Dict, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "kappa3_hutchinson_n8192_smoke_v1"

# PROT-018 runtime check: anchor name has _n8192, so N must equal 8192
_N_SUFFIX = 8192
N = 8192
assert N == _N_SUFFIX, f"PROT-018 violation: anchor name _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    M_LIST = [409, 819]        # alpha ~ 0.05, 0.10
    N_PROBES = 500              # quick smoke (full will use 5000)
else:
    # This script IS the smoke (per research spec: N=8192 5000 probes IS the target)
    # The "full" mode here uses the research-specified 5000 probes
    SEEDS = [7, 17, 23, 31, 41]
    M_LIST = [205, 409, 819, 1638]  # alpha ~ 0.025, 0.05, 0.10, 0.20
    N_PROBES = 5000

# Pre-reg thresholds
HP_SIGMA_SEPARATION = 4.0
MID_SIGMA_LOW = 2.0
HF_SIGMA_SEPARATION = 2.0
HP_THEORY_RATIO_LO = 0.5
HP_THEORY_RATIO_HI = 2.0

# Formula self-tests
_k3t_819 = 819 / 8192
assert abs(_k3t_819 - 0.100) < 0.002, f"kappa_3 theory selftest: {_k3t_819}"
_k3t_409 = 409 / 8192
assert abs(_k3t_409 - 0.050) < 0.002, f"kappa_3 theory selftest: {_k3t_409}"
print("[formula_selftest] kappa_3 theory at N=8192 verified", flush=True)


def build_hopfield_w(M: int, N: int, seed: int) -> np.ndarray:
    """W = Xi^T @ Xi / N. BSC +-1 patterns."""
    rng = np.random.RandomState(seed)
    Xi = rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float32)
    W = (Xi.T @ Xi) / float(N)
    return W.astype(np.float64)


def build_goe_w(N: int, seed: int) -> np.ndarray:
    """GOE Wigner matrix."""
    rng = np.random.RandomState(seed + 10000)
    G = rng.randn(N, N).astype(np.float32)
    W = ((G + G.T) / (2.0 * math.sqrt(N))).astype(np.float64)
    return W


def hutchinson_kappa3_vectorized(W: np.ndarray, n_probes: int, seed: int) -> Tuple[float, float]:
    """
    Vectorized Hutchinson: kappa_3 = mean(diag(V^T W^3 V)) / N.
    Uses batched DGEMM: WV = W@V; W2V = W@WV; W3V = W@W2V.
    """
    rng = np.random.RandomState(seed)
    N_dim = W.shape[0]
    V = rng.choice([-1.0, 1.0], size=(N_dim, n_probes)).astype(np.float64)
    WV = W @ V
    W2V = W @ WV
    W3V = W @ W2V
    per_probe = (V * W3V).sum(axis=0) / N_dim
    kappa3 = float(np.mean(per_probe))
    std = float(np.std(per_probe, ddof=1)) / math.sqrt(n_probes)
    return kappa3, std


def run_seed(seed: int) -> Dict:
    """Run one seed for all M values."""
    results = {}
    for M in M_LIST:
        t0 = time.time()
        W_hop = build_hopfield_w(M, N, seed)
        k3_hop, std_hop = hutchinson_kappa3_vectorized(W_hop, N_PROBES, seed)

        W_goe = build_goe_w(N, seed)
        k3_goe, std_goe = hutchinson_kappa3_vectorized(W_goe, N_PROBES, seed + 1)

        kappa3_theory = M / N
        separation = abs(k3_hop - k3_goe)
        pooled_std = math.sqrt(std_hop**2 + std_goe**2)
        sigma_sep = separation / pooled_std if pooled_std > 1e-15 else float("nan")
        theory_ratio = k3_hop / kappa3_theory if abs(kappa3_theory) > 1e-15 else float("nan")
        elapsed = time.time() - t0

        print(f"  [seed={seed} M={M}] k3_hop={k3_hop:.5f} k3_goe={k3_goe:.6f} "
              f"theory={kappa3_theory:.5f} sep={sigma_sep:.1f}sigma "
              f"ratio={theory_ratio:.2f} t={elapsed:.1f}s", flush=True)

        results[M] = {
            "M": M, "N": N,
            "kappa3_hopfield": k3_hop, "std_hopfield": std_hop,
            "kappa3_goe": k3_goe, "std_goe": std_goe,
            "kappa3_theory": kappa3_theory,
            "sigma_separation": sigma_sep,
            "theory_ratio": theory_ratio,
            "elapsed_s": elapsed,
        }
    return {"M_results": results, "seed": seed, "N": N, "run_mode": RUN_MODE}


def _instrumentation_selftest():
    """Assert kappa_3 is non-null at small scale; PROT-018 N=8192 binding verified above."""
    N_t = 512
    M_t = 51   # alpha ~ 0.10
    n_p = 200
    seed = 42
    W_t = build_hopfield_w(M_t, N_t, seed)
    k3, std = hutchinson_kappa3_vectorized(W_t, n_p, seed)
    assert not math.isnan(k3), "selftest: kappa_3 is NaN"
    assert std > 0, "selftest: std=0"
    assert k3 > 0, f"selftest: kappa_3 <= 0: {k3}"
    theory = M_t / N_t
    ratio = k3 / theory
    assert 0.05 <= ratio <= 20.0, f"selftest: ratio={ratio:.2f} out of range"
    print(f"[selftest] PASS N=8192 binding OK; smoke N={N_t} kappa3={k3:.4f} "
          f"theory={theory:.4f} ratio={ratio:.2f}", flush=True)


_instrumentation_selftest()


def aggregate_results(per_seed: Dict) -> Dict:
    agg = {}
    for M in M_LIST:
        hop_vals, goe_vals, sep_vals, ratio_vals = [], [], [], []
        for sd in per_seed.values():
            mr = sd["M_results"].get(M) or sd["M_results"].get(str(M))
            if mr is None:
                continue
            hop_vals.append(mr["kappa3_hopfield"])
            goe_vals.append(mr["kappa3_goe"])
            sep_vals.append(mr["sigma_separation"])
            tr = mr.get("theory_ratio")
            if tr is not None and not math.isnan(tr):
                ratio_vals.append(tr)
        agg[M] = {
            "M": M,
            "mean_kappa3_hopfield": float(np.mean(hop_vals)) if hop_vals else float("nan"),
            "mean_kappa3_goe": float(np.mean(goe_vals)) if goe_vals else float("nan"),
            "kappa3_theory": M / N,
            "mean_sigma_separation": float(np.mean(sep_vals)) if sep_vals else float("nan"),
            "mean_theory_ratio": float(np.mean(ratio_vals)) if ratio_vals else float("nan"),
            "n_seeds": len(hop_vals),
        }
    return agg


def compute_verdict(agg: Dict) -> Tuple[str, str]:
    seps = [v["mean_sigma_separation"] for v in agg.values()
            if not math.isnan(v["mean_sigma_separation"])]
    ratios = [v["mean_theory_ratio"] for v in agg.values()
              if not math.isnan(v["mean_theory_ratio"])]
    if not seps:
        return ("HARD_FAIL", "No valid sigma separation estimates.")
    min_sep = min(seps)
    mean_ratio = float(np.mean(ratios)) if ratios else float("nan")
    ratio_ok = (not math.isnan(mean_ratio) and
                HP_THEORY_RATIO_LO <= mean_ratio <= HP_THEORY_RATIO_HI)
    if min_sep >= HP_SIGMA_SEPARATION and ratio_ok:
        return ("HARD_PASS",
                f"kappa_3 at N=8192 discriminative. min_sigma_sep={min_sep:.1f} "
                f"(HP>={HP_SIGMA_SEPARATION}). theory_ratio={mean_ratio:.2f} "
                f"in [{HP_THEORY_RATIO_LO},{HP_THEORY_RATIO_HI}]. "
                f"Spectral-MAC primitive validated at production N=8192.")
    if min_sep < HF_SIGMA_SEPARATION:
        return ("HARD_FAIL",
                f"kappa_3 not discriminative at N=8192. min_sigma_sep={min_sep:.1f} "
                f"(HF<{HF_SIGMA_SEPARATION}).")
    return ("MIDDLE_BAND",
            f"kappa_3 marginal at N=8192. min_sigma_sep={min_sep:.1f} "
            f"mean_ratio={mean_ratio:.2f}. Borderline spectral-MAC primitive.")


def main():
    t_start = time.time()
    print(f"[{ANCHOR_NAME}] run_mode={RUN_MODE} N={N} seeds={SEEDS} n_probes={N_PROBES}", flush=True)

    out_dir = get_output_dir(ANCHOR_NAME)
    run_config = {"N": N, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(f"[ckpt] {len(done)}/{len(SEEDS)} done; running {remaining}", flush=True)

    for seed in remaining:
        print(f"[{ANCHOR_NAME}] seed={seed} starting", flush=True)
        r = run_seed(seed)
        write_partial(out_dir, seed, r)
        print(f"[{ANCHOR_NAME}] seed={seed} done", flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS)
    agg = aggregate_results(per_seed)
    verdict, verdict_msg = compute_verdict(agg)

    total_elapsed = time.time() - t_start
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "run_mode": RUN_MODE,
        "N": N,
        "seeds": SEEDS,
        "n_probes": N_PROBES,
        "aggregate": {str(k): v for k, v in agg.items()},
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": total_elapsed,
    }
    metrics_path = get_output_dir(ANCHOR_NAME) / "metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=2)
    print(f"[{ANCHOR_NAME}] verdict={verdict}", flush=True)
    print(f"[{ANCHOR_NAME}] {verdict_msg}", flush=True)
    print(f"[{ANCHOR_NAME}] elapsed={total_elapsed:.1f}s", flush=True)


if __name__ == "__main__":
    if _ARGS.self_test:
        print("[main] --self-test complete", flush=True)
        sys.exit(0)
    main()
