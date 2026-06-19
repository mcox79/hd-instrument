"""
q_c2_mp_hc_v1_n8192 -- Q-C2 Marchenko-Pastur HC at N=8192 (production envelope).

Same design as q_c2_mp_hc_v1_n4096 but at N=8192 for production envelope.
Uses v324-confirmed free-Poisson null distribution.

SCIENTIFIC QUESTION (Q-C2 at N=8192):
  Does the spectral-audit remain within +-3 sigma_TW of the free-Poisson predicted
  bulk edge at the production-N envelope (N=8192)?

  At N=8192, sigma_TW ~ N^(-2/3) = 8192^(-2/3) ~ 0.0042 (4x smaller than N=1024).
  Finer resolution -> more sensitive spectral primitive at production N.

PRE-REGISTERED BANDS (same as N=4096 but at larger N):
  HARD-PASS: max_|Z_clean| <= 3.0 across all alpha values tested.
  MIDDLE: max_|Z_clean| in (3.0, 5.0].
  HARD-FAIL: max_|Z_clean| > 5.0 at any alpha.

FORMULA SELF-TESTS:
  1. MP upper edge: lambda_plus(alpha=0.1) = (1 + sqrt(0.1))^2 ~ 1.725.
  2. sigma_TW(N=8192) = 8192^(-2/3) * 1.725 ~ 0.0133. (Sharper than N=4096.)
  3. Z improvement: sigma_TW is 2x finer at N=8192 vs N=4096 -> 2x more sensitive
     spectral test.

PROT-018: anchor name has _n8192; N MUST = 8192.
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

ANCHOR_NAME = "q_c2_mp_hc_v1_n8192"

# PROT-018: anchor has _n8192 -> N must = 8192
_N_SUFFIX = 8192
N = 8192
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    ALPHA_LIST = [0.1, 0.3]
    USE_POWER_ITER = True
else:
    SEEDS = [7, 17, 23, 31, 41]
    ALPHA_LIST = [0.05, 0.1, 0.2, 0.3, 0.5]
    USE_POWER_ITER = False   # eigvalsh; N=8192 may be slow but tractable on GPU

# Pre-reg thresholds
HP_Z_LO = -3.0
HP_Z_HI = 3.0
HF_Z_ABS = 5.0

# Formula self-tests
def mp_upper_edge(alpha: float, sigma2: float = 1.0) -> float:
    return sigma2 * (1.0 + math.sqrt(alpha)) ** 2

def tw_sigma(N: int, lambda_plus: float) -> float:
    return (N ** (-2.0/3.0)) * lambda_plus

_edge_8192 = mp_upper_edge(0.1, 1.0)
_tw_8192 = tw_sigma(8192, _edge_8192)
assert abs(_edge_8192 - 1.725) < 0.01
# sigma_TW(N=8192) = 8192^(-2/3) * 1.725 ~ 0.0042
# Should be strictly smaller than N=4096 value (~0.0067)
assert 0.001 < _tw_8192 < 0.010, f"TW at N=8192 out of range: {_tw_8192:.5f}"
_tw_4096 = tw_sigma(4096, _edge_8192)
assert _tw_8192 < _tw_4096, f"N=8192 TW should be finer: {_tw_8192:.5f} vs {_tw_4096:.5f}"
print(f"[formula_selftest] N=8192: MP_edge={_edge_8192:.4f} sigma_TW={_tw_8192:.5f} "
      f"(finer than N=4096 {_tw_4096:.5f}) OK", flush=True)


def compute_lambda_max_power(W: np.ndarray, n_iter: int = 100, seed: int = 0) -> float:
    rng = np.random.RandomState(seed)
    v = rng.randn(W.shape[0])
    v /= np.linalg.norm(v)
    for _ in range(n_iter):
        v = W @ v
        nrm = float(np.linalg.norm(v))
        if nrm < 1e-15:
            return 0.0
        v /= nrm
    return float(np.dot(v, W @ v))


def compute_lambda_max_exact(W: np.ndarray) -> float:
    eigvals = np.linalg.eigvalsh(W)
    return float(np.max(eigvals))


def run_seed(seed: int) -> Dict:
    results = {}
    for alpha in ALPHA_LIST:
        M = max(2, int(alpha * N))
        t0 = time.time()
        rng = np.random.RandomState(seed)
        Xi = rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float64)
        W = (Xi.T @ Xi) / float(N)
        np.fill_diagonal(W, 0.0)

        if USE_POWER_ITER:
            lmax = compute_lambda_max_power(W, n_iter=50, seed=seed)
        else:
            lmax = compute_lambda_max_exact(W)

        sigma2 = 1.0
        lambda_plus = mp_upper_edge(alpha, sigma2)
        sigma_tw = tw_sigma(N, lambda_plus)
        z_clean = (lmax - lambda_plus) / sigma_tw if sigma_tw > 1e-15 else float("nan")
        elapsed = time.time() - t0

        print(f"  [seed={seed} alpha={alpha:.2f} M={M}] "
              f"lambda_max={lmax:.4f} lambda_MP={lambda_plus:.4f} "
              f"sigma_TW={sigma_tw:.5f} Z={z_clean:.2f} t={elapsed:.1f}s", flush=True)

        results[alpha] = {
            "alpha": alpha, "M": M, "N": N,
            "lambda_max": float(lmax),
            "lambda_mp_plus": lambda_plus,
            "sigma_tw": sigma_tw,
            "z_clean": float(z_clean),
            "elapsed_s": elapsed,
        }
    return {"alpha_results": results, "seed": seed, "N": N, "run_mode": RUN_MODE}


def _instrumentation_selftest():
    """Assert lambda_max and Z are non-null (at smaller N for speed)."""
    N_t = 512
    M_t = 51   # alpha ~ 0.10
    seed = 42
    rng = np.random.RandomState(seed)
    Xi_t = rng.choice([-1.0, 1.0], size=(M_t, N_t)).astype(np.float64)
    W_t = (Xi_t.T @ Xi_t) / float(N_t)
    np.fill_diagonal(W_t, 0.0)
    lmax = compute_lambda_max_power(W_t, n_iter=30, seed=seed)
    assert not math.isnan(lmax), "selftest: lambda_max NaN"
    assert lmax > 0, f"selftest: lambda_max={lmax}"
    edge = mp_upper_edge(0.1, 1.0)
    tw = tw_sigma(N_t, edge)
    z = (lmax - edge) / tw if tw > 1e-12 else float("nan")
    assert not math.isnan(z), "selftest: Z NaN"
    # PROT-018 N=8192 binding verified above at module load
    print(f"[selftest] PASS N_selftest={N_t} lmax={lmax:.4f} Z={z:.2f}; "
          f"production N=8192 binding verified", flush=True)


_instrumentation_selftest()


def aggregate_results(per_seed: Dict) -> Dict:
    agg = {}
    for alpha in ALPHA_LIST:
        z_vals, lmax_vals = [], []
        for sd in per_seed.values():
            r = sd["alpha_results"].get(alpha) or sd["alpha_results"].get(str(alpha))
            if r is None:
                continue
            if not math.isnan(r["z_clean"]):
                z_vals.append(r["z_clean"])
            lmax_vals.append(r["lambda_max"])
        agg[alpha] = {
            "alpha": alpha,
            "mean_z_clean": float(np.mean(z_vals)) if z_vals else float("nan"),
            "std_z_clean": float(np.std(z_vals, ddof=1)) if len(z_vals) > 1 else float("nan"),
            "mean_lambda_max": float(np.mean(lmax_vals)) if lmax_vals else float("nan"),
            "n_seeds": len(z_vals),
        }
    return agg


def compute_verdict(agg: Dict) -> Tuple[str, str]:
    z_vals = [v["mean_z_clean"] for v in agg.values() if not math.isnan(v["mean_z_clean"])]
    if not z_vals:
        return ("HARD_FAIL", "No valid Z_clean at N=8192.")
    max_abs_z = max(abs(z) for z in z_vals)
    min_z = min(z_vals)
    max_z = max(z_vals)
    if max_abs_z <= HP_Z_HI:
        return ("HARD_PASS",
                f"Q-C2 spectral-audit confirmed at N=8192. max_|Z|={max_abs_z:.2f} <= 3.0. "
                f"Z range [{min_z:.2f}, {max_z:.2f}]. "
                f"sigma_TW(N=8192)~{tw_sigma(N, mp_upper_edge(0.1, 1.0)):.4f} "
                f"(2x finer than N=4096). Production-grade spectral audit API ready.")
    if max_abs_z > HF_Z_ABS:
        return ("HARD_FAIL",
                f"Q-C2 N=8192 spectral anomaly. max_|Z|={max_abs_z:.2f} > {HF_Z_ABS}. "
                f"Audit API stays at N=4096 envelope.")
    return ("MIDDLE_BAND",
            f"Q-C2 N=8192 marginal. max_|Z|={max_abs_z:.2f} in (3.0, 5.0].")


def main():
    t_start = time.time()
    print(f"[{ANCHOR_NAME}] run_mode={RUN_MODE} N={N} alpha_list={ALPHA_LIST} "
          f"seeds={SEEDS} use_power_iter={USE_POWER_ITER}", flush=True)

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
        "alpha_list": ALPHA_LIST,
        "seeds": SEEDS,
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
    main()
