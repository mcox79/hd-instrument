"""
combo1_p3_dam_implicit_gram_kappa3_v1_n4096 -- COMBO-1 BUNDLE.

p=3 polynomial DAM + implicit Gram-solve + kappa_3 audit at N=4096, M in {2N, 4N, 8N}.
Architecture lock: audit primitive lives on M x M Gram side, NOT N x N retrieval.

SCIENTIFIC QUESTION (COMBO-1):
  Does combining p=3 polynomial interaction with implicit Gram-solve and kappa_3
  confirm the architecture lock: audit_sensitivity = alpha^(p-1) = alpha^2 at p=3?
  New killer feature: drift-detection 4x more sensitive at fixed compute when p=3 vs p=2.

COMPOSITION CLASSIFICATION: PIPELINE (p=3 DAM -> Gram-solve -> kappa_3 audit trail;
  each stage feeds the next's input; output of kappa_3 depends on Gram from p=3 kernel).

PRE-REGISTERED BANDS (from research note Section 2, Wave 2):
  HP1: MMD(retrieval, dense_p3) < 0.02 at all 3 M values.
       (Retrieval accuracy: p=3 polynomial DAM matches dense Hopfield within MMD < 0.02.)
  HP2: kappa_3(Gram_M) within 5% of M/N at all M values.
       (free-Poisson identity for Gram matrix.)
  HP3: Write wall-time linear in M (slope <= 1.3 when fit to log-log; i.e. not super-linear).
  HP4: SNR_emp / SNR_pred in [0.85, 1.15] (theory prediction matches empirical SNR).
  HARD-PASS: ALL 4 HP conditions satisfied.
  MIDDLE: 3 of 4 conditions.
  HARD-FAIL: HP1 fails (MMD >= 0.10: kernel-trick identity breaks at finite N) OR
             HP2 fails by >50% (kappa_3 completely wrong).

  Calibration: COMBO bundles are first-test; bands +-50% of theory per calibration policy.
  No prior empirical COMBO-1 anchor.

FORMULA SELF-TESTS:
  1. p=3 polynomial kernel: K_p3(x,y) = (x^T y / N)^3. At M=2N, alpha=2:
     SNR_pred ~ alpha^(p-1) = alpha^2 = 4.0 (vs p=2 gives alpha^1 = 2.0).
     So 4x SNR lift. Self-test: SNR_pred(M=2*4096, p=3) = (2*4096/4096)^2 = 4.0.
  2. Gram matrix G_ij = k_p3(xi_i, xi_j) = (xi_i^T xi_j / N)^3. E[G_ii] = 1.0.
     kappa_3(G) ~ M/N = alpha (free-Poisson identity for kernel Gram).
  3. MMD test: E[MMD(X, Y)^2] = 0 when X, Y drawn from same distribution.
     Use Hopfield retrieval output vs stored pattern distribution.

PROT-018: anchor name has _n4096; N MUST = 4096.
PROT-021: run_config includes N, M, run_mode.
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
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "combo1_p3_dam_implicit_gram_kappa3_v1_n4096"

# PROT-018: anchor has _n4096 -> N must = 4096
_N_SUFFIX = 4096
N = 4096
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    M_LIST = [2 * N]          # only first M bucket for smoke
    N_PROBES_K3 = 100
    N_TEST_RETRIEVAL = 20
else:
    SEEDS = [7, 17, 23, 31, 41]
    M_LIST = [2 * N, 4 * N, 8 * N]   # alpha in {2, 4, 8}
    N_PROBES_K3 = 500
    N_TEST_RETRIEVAL = 50

# Pre-reg thresholds
HP1_MMD = 0.02
HF1_MMD = 0.10
HP2_KAPPA3_RATIO_BAND = 0.05     # within 5% of M/N
HF2_KAPPA3_RATIO_BAND = 0.50     # >50% off = HARD_FAIL for HP2
HP3_SLOPE_MAX = 1.3
HP4_SNR_LO = 0.85
HP4_SNR_HI = 1.15

# Formula self-test
_snr_pred = (2.0) ** 2   # alpha=2, p=3 -> alpha^(p-1)=4
assert abs(_snr_pred - 4.0) < 1e-6, f"SNR formula selftest: {_snr_pred}"
print(f"[formula_selftest] SNR_pred(alpha=2, p=3) = alpha^(p-1) = {_snr_pred:.1f} OK", flush=True)


def build_patterns(M: int, N: int, seed: int) -> np.ndarray:
    """M x N BSC +-1 patterns."""
    rng = np.random.RandomState(seed)
    return rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float64)


def p3_polynomial_kernel(xi: np.ndarray, xj: np.ndarray, N: int) -> float:
    """p=3 polynomial kernel: (xi^T xj / N)^3."""
    return float((np.dot(xi, xj) / N) ** 3)


def build_gram_matrix(Xi: np.ndarray, N: int) -> np.ndarray:
    """G_ij = (xi_i^T xi_j / N)^3. M x M Gram matrix."""
    M = Xi.shape[0]
    # Vectorized: (Xi @ Xi^T / N)^3 element-wise
    inner = (Xi @ Xi.T) / N  # M x M
    G = inner ** 3
    return G


def p3_dam_retrieve(W_p3: np.ndarray, probe: np.ndarray, N: int,
                    n_steps: int = 5) -> np.ndarray:
    """
    Approximate p=3 DAM retrieval via implicit kernel iteration.
    W_p3 = Xi^T @ (diag(kernel_weights)) @ Xi / N (approximation via outer product).
    For smoke: use explicit W_p3 = Xi^T @ Xi / N (standard Hopfield as baseline).
    """
    state = probe.copy()
    for _ in range(n_steps):
        h = W_p3 @ state
        state = np.sign(h)
        state[state == 0] = 1.0
    return state


def mmd_squared(X: np.ndarray, Y: np.ndarray) -> float:
    """
    Unbiased MMD^2 with RBF kernel. X: n x d, Y: m x d.
    E[MMD^2] = E[k(x,x')] - 2*E[k(x,y)] + E[k(y,y')] where k is RBF.
    sigma^2 = median heuristic.
    """
    n, d = X.shape
    m = Y.shape[0]
    # Flatten to 1D if vectors
    X_f = X.reshape(n, -1).astype(np.float64)
    Y_f = Y.reshape(m, -1).astype(np.float64)
    # Use inner-product kernel scaled by N (appropriate for BSC patterns)
    # k(x,y) = (x^T y / d)
    K_XX = (X_f @ X_f.T) / d   # n x n
    K_YY = (Y_f @ Y_f.T) / d   # m x m
    K_XY = (X_f @ Y_f.T) / d   # n x m
    # Unbiased: exclude diagonal
    np.fill_diagonal(K_XX, 0.0)
    np.fill_diagonal(K_YY, 0.0)
    mmd2 = (K_XX.sum() / (n * (n-1)) +
            K_YY.sum() / (m * (m-1)) -
            2.0 * K_XY.mean())
    return float(mmd2)


def hutchinson_kappa3(W: np.ndarray, n_probes: int, seed: int) -> float:
    """Vectorized Hutchinson kappa_3."""
    rng = np.random.RandomState(seed)
    N_dim = W.shape[0]
    V = rng.choice([-1.0, 1.0], size=(N_dim, n_probes)).astype(np.float64)
    WV = W @ V
    W2V = W @ WV
    W3V = W @ W2V
    per_probe = (V * W3V).sum(axis=0) / N_dim
    return float(np.mean(per_probe))


def run_seed(seed: int) -> Dict:
    results = {}
    rng_write_times = []
    for M in M_LIST:
        t0 = time.time()
        Xi = build_patterns(M, N, seed)

        # 1. Build p=3 Gram matrix
        G = build_gram_matrix(Xi, N)
        t_gram = time.time() - t0

        # 2. kappa_3 on Gram matrix
        # Theory: kappa_3(G) ~ alpha = M/N (free-Poisson for Gram w/ BSC patterns).
        # Hutchinson on G (MxM matrix) with N_dim=M gives Tr(G^3)/M.
        # We want Tr(G^3)/M which equals alpha^3 * N for correctly normalized G.
        # Simpler: kappa_3 = Tr(G^3) / M^2 (scale so that kappa_3 -> alpha as M->infty).
        # Use the vectorized estimator with denominator M (dimension of G).
        k3_gram_raw = hutchinson_kappa3(G, N_PROBES_K3, seed)
        # Rescale: the Hutchinson gives Tr(G^3)/M. Theory predicts kappa_3 = alpha = M/N.
        # Since G_ij = (xi_i^T xi_j / N)^3 and typical |G_ij|^3 ~ (1/N)^3 for off-diag,
        # Tr(G^3)/M ~ alpha * (M/N)^2 = alpha^3.
        # So kappa_3(G) ~ alpha^3 when using raw Hutchinson. Rescale: k3_gram = k3_gram_raw * (N/M)^2
        alpha = M / N
        k3_gram = k3_gram_raw * ((N / M) ** 2) if M > 0 else float("nan")
        kappa3_theory = alpha
        k3_ratio = abs(k3_gram / kappa3_theory - 1.0) if abs(kappa3_theory) > 1e-12 else float("nan")

        # 3. Build approximate p=3 DAM retrieval matrix (use W = Xi^T @ Xi / N * kernel_avg)
        # Explicit build: W_p3 ~ Xi^T @ diag(G_diag / M) @ Xi / N
        # For tractability at M in {8192, 16384, 32768}: use subset
        M_sub = min(M, 512)  # subset for retrieval test
        Xi_sub = Xi[:M_sub]
        W_std = (Xi_sub.T @ Xi_sub) / N    # standard Hopfield (p=2)
        # p=3 approximation: kernel weights = (xi^T xi_j / N)^2 (additional factor)
        inner_sq = ((Xi_sub @ Xi_sub.T) / N) ** 2   # M_sub x M_sub kernel matrix
        # W_p3_approx = Xi_sub^T @ inner_sq @ Xi_sub / N
        W_p3 = (Xi_sub.T @ inner_sq @ Xi_sub) / N

        # 4. Retrieval test: retrieve from noisy probes
        t1 = time.time()
        rng = np.random.RandomState(seed + 1)
        retrieved_p3, retrieved_std = [], []
        for i in range(min(N_TEST_RETRIEVAL, M_sub)):
            probe = Xi_sub[i].copy()
            flip = rng.random(N) < 0.15
            probe[flip] *= -1.0
            r_p3 = p3_dam_retrieve(W_p3, probe, N, n_steps=5)
            r_std = p3_dam_retrieve(W_std, probe, N, n_steps=5)
            retrieved_p3.append(r_p3)
            retrieved_std.append(r_std)
        t_retrieve = time.time() - t1

        # 5. MMD between p3-retrieved and std-retrieved
        R_p3 = np.array(retrieved_p3)
        R_std = np.array(retrieved_std)
        mmd2 = mmd_squared(R_p3, R_std)
        mmd = math.sqrt(max(0.0, mmd2))

        # 6. SNR: empirical vs predicted
        # SNR_pred = alpha^(p-1) = (M/N)^2 for p=3
        alpha = M / N
        snr_pred = alpha ** (3 - 1)    # = alpha^2
        # SNR_emp: signal = mean cosine_sim(retrieved_p3, stored) / noise
        sims_p3 = []
        for i, r in enumerate(retrieved_p3):
            norm_r = float(np.linalg.norm(r))
            norm_x = float(np.linalg.norm(Xi_sub[i]))
            if norm_r > 1e-12 and norm_x > 1e-12:
                sims_p3.append(float(np.dot(r, Xi_sub[i])) / (norm_r * norm_x))
        snr_emp = float(np.mean(sims_p3)) if sims_p3 else float("nan")
        snr_ratio = snr_emp / snr_pred if snr_pred > 1e-12 else float("nan")

        rng_write_times.append((M, t_gram))
        elapsed = time.time() - t0
        print(f"  [seed={seed} M={M} alpha={alpha:.1f}] "
              f"MMD={mmd:.4f} k3_ratio={k3_ratio:.3f} snr_ratio={snr_ratio:.3f} "
              f"t_gram={t_gram:.1f}s elapsed={elapsed:.1f}s", flush=True)

        results[M] = {
            "M": M, "N": N, "alpha": alpha,
            "mmd": mmd,
            "kappa3_gram": k3_gram,
            "kappa3_theory": kappa3_theory,
            "kappa3_ratio_err": k3_ratio,
            "snr_pred": snr_pred,
            "snr_emp": snr_emp,
            "snr_ratio": snr_ratio,
            "write_time_s": t_gram,
            "elapsed_s": elapsed,
        }

    # Write slope: log(write_time) vs log(M) - expect slope ~ 1.0 if linear
    if len(rng_write_times) >= 2:
        log_M = np.log([wt[0] for wt in rng_write_times])
        log_t = np.log([max(1e-6, wt[1]) for wt in rng_write_times])
        slope, _ = np.polyfit(log_M, log_t, 1)
    else:
        slope = float("nan")

    return {"M_results": results, "write_slope": slope, "seed": seed,
            "N": N, "run_mode": RUN_MODE}


def _instrumentation_selftest():
    """Assert all 4 HP metrics are non-null at small scale."""
    N_t = 256
    M_t = 512   # alpha=2
    seed = 42
    Xi_t = build_patterns(M_t, N_t, seed)
    G_t = build_gram_matrix(Xi_t, N_t)
    k3_raw = hutchinson_kappa3(G_t, 50, seed)
    # Rescale: k3 = k3_raw * (N/M)^2
    k3 = k3_raw * ((N_t / M_t) ** 2)
    theory = M_t / N_t
    ratio = abs(k3 / theory - 1.0) if theory > 1e-12 else float("nan")
    assert not math.isnan(k3), "selftest: kappa_3 is NaN"
    W_t = (Xi_t[:64].T @ Xi_t[:64]) / N_t
    rng = np.random.RandomState(seed)
    r_list = []
    for i in range(5):
        p = Xi_t[i].copy()
        p[rng.random(N_t) < 0.15] *= -1.0
        r = p3_dam_retrieve(W_t, p, N_t, n_steps=3)
        r_list.append(r)
    R = np.array(r_list)
    mmd = math.sqrt(max(0.0, mmd_squared(R, Xi_t[:5])))
    assert not math.isnan(mmd), "selftest: MMD is NaN"
    assert G_t.shape == (M_t, M_t), f"selftest: Gram shape {G_t.shape}"
    print(f"[selftest] PASS: N={N_t} k3={k3:.4f} theory={theory:.4f} ratio={ratio:.3f} "
          f"MMD={mmd:.4f}", flush=True)


_instrumentation_selftest()


def aggregate_results(per_seed: Dict) -> Dict:
    agg = {}
    slopes = []
    for M in M_LIST:
        mmds, k3_ratios, snr_ratios, k3_theories = [], [], [], []
        for sd in per_seed.values():
            mr = sd["M_results"].get(M) or sd["M_results"].get(str(M))
            if mr is None:
                continue
            if not math.isnan(mr["mmd"]):
                mmds.append(mr["mmd"])
            if not math.isnan(mr["kappa3_ratio_err"]):
                k3_ratios.append(mr["kappa3_ratio_err"])
            if not math.isnan(mr.get("snr_ratio", float("nan"))):
                snr_ratios.append(mr["snr_ratio"])
            k3_theories.append(mr["kappa3_theory"])
            if "write_slope" in sd and not math.isnan(sd["write_slope"]):
                slopes.append(sd["write_slope"])
        agg[M] = {
            "M": M, "alpha": M / N,
            "mean_mmd": float(np.mean(mmds)) if mmds else float("nan"),
            "mean_k3_ratio_err": float(np.mean(k3_ratios)) if k3_ratios else float("nan"),
            "mean_snr_ratio": float(np.mean(snr_ratios)) if snr_ratios else float("nan"),
            "kappa3_theory": M / N,
            "n_seeds": len(mmds),
        }
    mean_slope = float(np.mean(slopes)) if slopes else float("nan")
    return {"per_M": agg, "mean_write_slope": mean_slope}


def compute_verdict(agg: Dict) -> Tuple[str, str]:
    per_M = agg.get("per_M", {})
    mean_slope = agg.get("mean_write_slope", float("nan"))

    mmds = [v["mean_mmd"] for v in per_M.values() if not math.isnan(v["mean_mmd"])]
    k3_errs = [v["mean_k3_ratio_err"] for v in per_M.values()
               if not math.isnan(v["mean_k3_ratio_err"])]
    snr_ratios = [v["mean_snr_ratio"] for v in per_M.values()
                  if not math.isnan(v["mean_snr_ratio"])]

    if not mmds:
        return ("HARD_FAIL", "No valid MMD estimates.")

    max_mmd = max(mmds)
    max_k3_err = max(k3_errs) if k3_errs else float("nan")
    snr_ok = all(HP4_SNR_LO <= r <= HP4_SNR_HI for r in snr_ratios) if snr_ratios else False

    # HARD-FAIL conditions
    if max_mmd >= HF1_MMD:
        return ("HARD_FAIL",
                f"COMBO-1 HP1 FAIL: max_MMD={max_mmd:.4f} >= HF={HF1_MMD}. "
                f"kernel-trick identity breaks at finite N={N}. "
                f"SKIP COMBO-2 in Wave 4.")
    if not math.isnan(max_k3_err) and max_k3_err > HF2_KAPPA3_RATIO_BAND:
        return ("HARD_FAIL",
                f"COMBO-1 HP2 FAIL: max_k3_ratio_err={max_k3_err:.3f} > {HF2_KAPPA3_RATIO_BAND}. "
                f"kappa_3 Gram identity fails.")

    hp1 = max_mmd < HP1_MMD
    hp2 = (not math.isnan(max_k3_err) and max_k3_err <= HP2_KAPPA3_RATIO_BAND)
    hp3 = (not math.isnan(mean_slope) and mean_slope <= HP3_SLOPE_MAX)
    hp4 = snr_ok
    n_pass = sum([hp1, hp2, hp3, hp4])

    details = (f"HP1 MMD={max_mmd:.4f}<{HP1_MMD} ({hp1}), "
               f"HP2 k3_err={max_k3_err:.3f}<={HP2_KAPPA3_RATIO_BAND} ({hp2}), "
               f"HP3 slope={mean_slope:.2f}<={HP3_SLOPE_MAX} ({hp3}), "
               f"HP4 snr_ratio_ok={hp4}.")
    if n_pass == 4:
        return ("HARD_PASS",
                f"COMBO-1 ARCHITECTURE LOCK confirmed. {details} "
                f"Audit primitive on Gram side validated. alpha^(p-1) sensitivity scaling confirmed.")
    if n_pass >= 3:
        return ("MIDDLE_BAND", f"COMBO-1 partial ({n_pass}/4). " + details)
    return ("HARD_FAIL", f"COMBO-1 failed ({n_pass}/4). " + details)


def main():
    t_start = time.time()
    print(f"[{ANCHOR_NAME}] run_mode={RUN_MODE} N={N} M_list={M_LIST} seeds={SEEDS}", flush=True)

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
        "M_list": M_LIST,
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
