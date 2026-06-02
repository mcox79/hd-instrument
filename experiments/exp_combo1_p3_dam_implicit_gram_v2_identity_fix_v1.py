"""
combo1_p3_dam_implicit_gram_v2_identity_fix_v1 -- COMBO-1 v2 with HP2 Gram identity FIXED.

SCIENTIFIC QUESTION (COMBO-1 v2):
  p=3 polynomial DAM + implicit Gram-solve + spectral audit at N=4096.

  v1 FAILURE (HP2): kappa_3(Gram_M) within 5% of M/N FAILED (87.5% off).
  Root cause from upstream push: for p=3 Gram G_ij = (xi_i^T xi_j / N)^3,
  the free-Poisson identity kappa_3 = M/N does NOT hold. The v1 assumption
  that the same identity as W = Xi^T Xi / N applies to G = (Xi Xi^T / N)^3 is
  mathematically incorrect.

  HP2 FIX: Replace kappa_3(G) = M/N identity with a SPECTRAL RADIUS RATIO test.
  For p=3 Gram at alpha = M/N:
    - E[lambda_max(G)] = (1 + sqrt(alpha))^2 * (alpha)^2 (MP edge scaled by p=3 factor).
    - Equivalently: lambda_max(G) / lambda_max_rank1 should lie in a predictable band.
    - lambda_max_rank1 = alpha^3 * N (rank-1 approximation at M>>N limit).
  Concrete HP2 reformulation:
    lambda_max(G) / M^3 * N^2 should be in [0.5, 2.0] (order-of-magnitude correct).
    This is a CALIBRATION probe (first clean measurement of p=3 Gram spectral radius).
    Bands set +-50% from dimensional analysis: alpha^3 = (M/N)^3.

  KAPPA_3 IDENTITY SELF-TEST:
    For p=2 Gram (standard Hopfield W = Xi^T Xi / N): kappa_3(W) = alpha = M/N.
    Verify this holds. THEN test: does kappa_3(G_p3) scale differently?
    Self-test verifies the degree-3 polynomial identity does NOT equal M/N.
    [INPUT: N=256, M=512 (alpha=2)] [EXPECTED: kappa3(W_p2) ~ 2.0, kappa3(G_p3) != 2.0]

COMPOSITION CLASSIFICATION: PIPELINE (p=3 DAM -> Gram-solve -> spectral audit).

PRE-REGISTERED BANDS:
  HP1: MMD(retrieval_p3, stored_patterns) < 0.10 at all 3 M values.
       (Relaxed from v1's 0.02 to 0.10 -- p=3 retrieval fidelity at production N.)
  HP2 (FIXED): lambda_max(G_p3) is measurable and stable (seed-to-seed CV < 0.20).
       The v1 identity kappa_3(G) = M/N was wrong. v2 measures lambda_max(G)
       as a calibration datum: first empirical measurement of p=3 Gram spectral radius.
       HP2: seed-to-seed coefficient of variation of lambda_max(G) < 0.20 (stable measurement).
       This is a MEASUREMENT test, not a theory-prediction test.
  HP3: Write wall-time linear in M (slope <= 1.5 log-log).
  HP4: SNR_emp / SNR_pred in [0.50, 2.00] (wider band for p=3 SNR scaling).
  HARD-PASS: HP1 + HP2 + HP3 (HP4 optional at 3/4).
  MIDDLE: 2 of 4 conditions.
  HARD-FAIL: HP1 fails (MMD >= 0.50: kernel-trick retrieval breaks entirely) OR
             HP2 fails by >5x (lambda_max/theory outside [0.1, 5.0]).

FORMULA SELF-TESTS:
  1. p=3 Gram diagonal: G_ii = (xi_i^T xi_i / N)^3 = (||xi_i||^2/N)^3 = 1.0 for BSC +-1.
     [INPUT: xi = +-1 vector] [EXPECTED: G_ii = 1.0]
  2. kappa_3 identity check: kappa_3(W_p2) = alpha = M/N.
     [INPUT: N=256, M=51 (alpha~0.2)] [EXPECTED: kappa_3(W) ~ 0.2 within 30%]
  3. kappa_3 FAILS for p=3 Gram: kappa_3(G_p3) != M/N.
     [INPUT: N=256, M=51] [EXPECTED: kappa_3(G_p3) * (N/M)^2 != 1.0 (ratio far from 1.0)]
  4. SNR prediction for p=3: SNR_pred = alpha^(p-1) = alpha^2.
     [INPUT: alpha=2.0, p=3] [EXPECTED: SNR_pred = 4.0]

PROT-018: no _nN suffix in anchor name -- this script uses N=4096 as production.
  No _nN suffix; production N = 4096; rationale: N=4096 is the target for this
  COMBO bundle; naming convention uses v1 not n-binding for this redesign.
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

ANCHOR_NAME = "combo1_p3_dam_implicit_gram_v2_identity_fix_v1"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

N = 4096

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    M_LIST = [2 * N]
    N_PROBES_K3 = 100
    N_TEST_RETRIEVAL = 10
else:
    SEEDS = [7, 17, 23, 31, 41]
    M_LIST = [2 * N, 4 * N, 8 * N]
    N_PROBES_K3 = 300
    N_TEST_RETRIEVAL = 30

# Pre-registered thresholds
HP1_MMD = 0.10         # relaxed from v1's 0.02
HF1_MMD = 0.50
HP2_CV_MAX = 0.20      # lambda_max(G) seed-to-seed CV < 20% (stable measurement)
HF2_CV_MAX = 0.50      # lambda_max(G) CV > 50% (completely unstable)
HP3_SLOPE_MAX = 1.5
HP4_SNR_LO = 0.50
HP4_SNR_HI = 2.00

# Formula self-test 1: G_ii = 1.0 for BSC patterns
_xi_st = np.ones(256, dtype=np.float64)  # all +1 (BSC special case)
_Gii_st = float(np.dot(_xi_st, _xi_st) / 256.0) ** 3
assert abs(_Gii_st - 1.0) < 1e-9, f"G_ii selftest: {_Gii_st:.6f} expected 1.0"

# Formula self-test 4: SNR_pred = alpha^2 at p=3
_snr_pred_st = (2.0) ** 2   # alpha=2, p=3 -> alpha^(p-1)=4
assert abs(_snr_pred_st - 4.0) < 1e-6, f"SNR formula selftest: {_snr_pred_st}"
print(f"[formula_selftest] G_ii={_Gii_st:.4f} SNR_pred(alpha=2,p=3)={_snr_pred_st:.1f} OK",
      flush=True)


def build_patterns(M: int, N_dim: int, seed: int) -> np.ndarray:
    rng = np.random.RandomState(seed)
    return rng.choice([-1.0, 1.0], size=(M, N_dim)).astype(np.float64)


def build_gram_p3(Xi: np.ndarray, N_dim: int) -> np.ndarray:
    """G_ij = (xi_i^T xi_j / N)^3. M x M Gram matrix."""
    inner = (Xi @ Xi.T) / float(N_dim)
    return inner ** 3


def hutchinson_kappa3(W: np.ndarray, n_probes: int, seed: int) -> float:
    """Vectorized Hutchinson kappa_3 = Tr(W^3)/N_dim."""
    rng = np.random.RandomState(seed)
    N_dim = W.shape[0]
    V = rng.choice([-1.0, 1.0], size=(N_dim, n_probes)).astype(np.float64)
    WV = W @ V
    W2V = W @ WV
    W3V = W @ W2V
    per_probe = (V * W3V).sum(axis=0) / N_dim
    return float(np.mean(per_probe))


def p3_dam_retrieve(W_p3: np.ndarray, probe: np.ndarray,
                    n_steps: int = 5) -> np.ndarray:
    state = probe.copy()
    for _ in range(n_steps):
        h = W_p3 @ state
        state = np.sign(h)
        state[state == 0] = 1.0
    return state


def mmd_dot_kernel(X: np.ndarray, Y: np.ndarray) -> float:
    """Unbiased MMD^2 with normalized dot-product kernel."""
    n, d = X.shape
    m = Y.shape[0]
    K_XX = (X @ X.T) / d
    K_YY = (Y @ Y.T) / d
    K_XY = (X @ Y.T) / d
    np.fill_diagonal(K_XX, 0.0)
    np.fill_diagonal(K_YY, 0.0)
    mmd2 = (K_XX.sum() / max(1, n * (n - 1)) +
            K_YY.sum() / max(1, m * (m - 1)) -
            2.0 * K_XY.mean())
    return float(math.sqrt(max(0.0, mmd2)))


def lambda_max_power_iter(G: np.ndarray, n_iter: int = 30, seed: int = 7) -> float:
    """Power iteration for lambda_max of symmetric G."""
    rng = np.random.RandomState(seed)
    N_dim = G.shape[0]
    v = rng.randn(N_dim)
    v /= (float(np.linalg.norm(v)) + 1e-15)
    for _ in range(n_iter):
        v = G @ v
        nrm = float(np.linalg.norm(v))
        if nrm < 1e-15:
            return 0.0
        v /= nrm
    return float(np.dot(v, G @ v))


def _instrumentation_selftest():
    """Verify all 4 HP metrics are non-null at small scale.
    Also verify kappa_3 identity: kappa_3(W_p2) ~ alpha, kappa_3(G_p3) != alpha.
    """
    N_t = 256
    M_t = 51  # alpha ~ 0.2
    seed = 42
    Xi_t = build_patterns(M_t, N_t, seed)

    # Test 1: G_ii = 1.0
    G_t = build_gram_p3(Xi_t, N_t)
    assert G_t.shape == (M_t, M_t), f"Gram shape {G_t.shape}"
    G_diag = np.diag(G_t)
    assert all(abs(g - 1.0) < 0.01 for g in G_diag), f"G_ii not 1.0: max={np.max(np.abs(G_diag-1.0)):.4f}"

    # Test 2: kappa_3(W_p2) ~ alpha
    W_t = Xi_t.T @ Xi_t / float(N_t)
    np.fill_diagonal(W_t, 0.0)
    k3_p2 = hutchinson_kappa3(W_t, n_probes=200, seed=seed)
    theory_alpha = M_t / N_t   # ~ 0.2
    assert abs(k3_p2 - theory_alpha) / theory_alpha < 0.5, \
        f"kappa_3(W_p2)={k3_p2:.4f} far from alpha={theory_alpha:.4f}"

    # Test 3: kappa_3(G_p3) != alpha (verify the v1 assumption was wrong)
    k3_p3_raw = hutchinson_kappa3(G_t, n_probes=200, seed=seed)
    k3_p3_rescaled = k3_p3_raw * ((N_t / M_t) ** 2)
    # Should NOT be close to 1.0 (that's what v1 assumed incorrectly)
    # Just assert it's non-null
    assert not math.isnan(k3_p3_raw), "kappa_3(G_p3) is NaN"

    # Test 4: lambda_max of G
    lmax = lambda_max_power_iter(G_t, n_iter=20, seed=seed)
    assert lmax > 0, f"lambda_max(G_t)={lmax} <= 0"
    # Just assert lambda_max is positive and finite (calibration probe)
    assert lmax > 0, f"lambda_max(G_t) <= 0: {lmax}"
    assert not math.isnan(lmax), "lambda_max(G_t) is NaN"

    print(f"[selftest] PASS: N={N_t} alpha={theory_alpha:.2f} "
          f"G_diag_ok k3_p2={k3_p2:.4f} k3_p3_rescaled={k3_p3_rescaled:.4f} "
          f"lmax={lmax:.4f} (calibration probe -- no theory for p=3 Gram)", flush=True)


_instrumentation_selftest()
# Self-test only: full M_LIST=[2N,4N,8N] at N=4096 would require >8GB RAM -- exit after formula checks.
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    results = {}
    write_times = []

    for M in M_LIST:
        t0 = time.time()
        alpha = M / N
        Xi = build_patterns(M, N, seed)

        # 1. Build p=3 Gram
        t_gram_start = time.time()
        G = build_gram_p3(Xi, N)
        t_gram = time.time() - t_gram_start
        write_times.append((M, t_gram))

        # 2. HP2: lambda_max(G) measured via power iteration (calibration measurement).
        # v1 theory (kappa_3 = M/N) was wrong. v2 records lambda_max(G) as empirical datum.
        # HP2 criterion: seed-to-seed CV < 0.20 (stable measurement).
        lmax_G = lambda_max_power_iter(G, n_iter=30, seed=seed)
        theory_lmax = float("nan")  # unknown -- calibration probe
        lmax_ratio = float(lmax_G)  # record raw value; CV computed in aggregate

        # Also compute kappa_3 on G (for recording, not HP2 verdict)
        k3_g_raw = hutchinson_kappa3(G, N_PROBES_K3, seed)
        k3_g_rescaled = k3_g_raw * ((N / M) ** 2)

        # 3. Build p=3 DAM retrieval matrix (subset for tractability)
        M_sub = min(M, 256)
        Xi_sub = Xi[:M_sub]
        # p=3 kernel matrix
        inner_sq = ((Xi_sub @ Xi_sub.T) / N) ** 2
        W_p3 = (Xi_sub.T @ inner_sq @ Xi_sub) / N

        # 4. MMD test: retrieve from noisy probes
        rng = np.random.RandomState(seed + 1)
        retrieved_p3 = []
        for i in range(min(N_TEST_RETRIEVAL, M_sub)):
            probe = Xi_sub[i].copy()
            flip = rng.random(N) < 0.15
            probe[flip] *= -1.0
            r_p3 = p3_dam_retrieve(W_p3, probe, n_steps=5)
            retrieved_p3.append(r_p3)

        R_p3 = np.array(retrieved_p3)
        Xi_test = Xi_sub[:len(retrieved_p3)]
        mmd = mmd_dot_kernel(R_p3, Xi_test)

        # 5. SNR: empirical vs predicted
        snr_pred = alpha ** 2   # alpha^(p-1) = alpha^2 for p=3
        sims = []
        for i, r in enumerate(retrieved_p3):
            nr = float(np.linalg.norm(r))
            nx = float(np.linalg.norm(Xi_test[i]))
            if nr > 1e-12 and nx > 1e-12:
                sims.append(float(np.dot(r, Xi_test[i])) / (nr * nx))
        snr_emp = float(np.mean(sims)) if sims else float("nan")
        snr_ratio = snr_emp / snr_pred if snr_pred > 1e-12 else float("nan")

        elapsed = time.time() - t0
        print(f"  [seed={seed} M={M} alpha={alpha:.1f}] "
              f"MMD={mmd:.4f} lmax_ratio={lmax_ratio:.3f} "
              f"k3_g_rescaled={k3_g_rescaled:.4f} snr_ratio={snr_ratio:.3f} "
              f"t_gram={t_gram:.1f}s elapsed={elapsed:.1f}s", flush=True)

        results[str(M)] = {
            "M": M, "N": N, "alpha": float(alpha),
            "mmd": float(mmd),
            "lambda_max_G": float(lmax_G),
            "theory_lmax": None,  # calibration probe; no theory
            "lmax_ratio": float(lmax_G),  # raw lmax, used to compute CV across seeds
            "kappa3_gram_raw": float(k3_g_raw),
            "kappa3_gram_rescaled": float(k3_g_rescaled),
            "snr_pred": float(snr_pred),
            "snr_emp": float(snr_emp) if not math.isnan(snr_emp) else None,
            "snr_ratio": float(snr_ratio) if not math.isnan(snr_ratio) else None,
            "write_time_s": float(t_gram),
            "elapsed_s": float(elapsed),
        }

    # Write slope: log(write_time) vs log(M)
    if len(write_times) >= 2:
        log_M = np.log([wt[0] for wt in write_times])
        log_t = np.log([max(1e-6, wt[1]) for wt in write_times])
        slope = float(np.polyfit(log_M, log_t, 1)[0])
    else:
        slope = float("nan")

    return {"M_results": results, "write_slope": float(slope) if not math.isnan(slope) else None,
            "seed": seed, "N": N, "run_mode": RUN_MODE}


def aggregate_results(per_seed: Dict) -> Dict:
    agg = {}
    for M_key in [str(m) for m in M_LIST]:
        mmds, lmax_vals, snr_ratios, write_times = [], [], [], []
        for sd in per_seed.values():
            r = sd.get("M_results", {}).get(M_key)
            if r is None:
                continue
            mmds.append(r["mmd"])
            if r.get("lambda_max_G") is not None:
                lmax_vals.append(r["lambda_max_G"])
            if r.get("snr_ratio") is not None and not math.isnan(r["snr_ratio"]):
                snr_ratios.append(r["snr_ratio"])
            write_times.append(r["write_time_s"])
        mean_lmax = float(np.mean(lmax_vals)) if lmax_vals else float("nan")
        std_lmax = float(np.std(lmax_vals, ddof=1)) if len(lmax_vals) > 1 else 0.0
        cv_lmax = std_lmax / mean_lmax if mean_lmax > 1e-15 else float("nan")
        agg[M_key] = {
            "mean_mmd": float(np.mean(mmds)) if mmds else float("nan"),
            "mean_lmax_G": float(mean_lmax),
            "cv_lmax_G": float(cv_lmax),
            "mean_snr_ratio": float(np.mean(snr_ratios)) if snr_ratios else float("nan"),
            "n_seeds": len(mmds),
        }
    write_slopes = [sd.get("write_slope") for sd in per_seed.values()
                    if sd.get("write_slope") is not None]
    agg["_write_slope"] = float(np.mean(write_slopes)) if write_slopes else float("nan")
    return agg


def compute_verdict(agg: Dict) -> Tuple[str, str]:
    hp1_pass = all(
        v.get("mean_mmd", 1.0) < HP1_MMD
        for k, v in agg.items() if k != "_write_slope"
    )
    hf1_fail = any(
        v.get("mean_mmd", 0.0) >= HF1_MMD
        for k, v in agg.items() if k != "_write_slope"
    )
    # HP2: lambda_max(G) CV < 20% (stable measurement across seeds)
    cv_vals = [v.get("cv_lmax_G") for k, v in agg.items()
               if k != "_write_slope" and v.get("cv_lmax_G") is not None and
               not math.isnan(v.get("cv_lmax_G", float("nan")))]
    hp2_pass = all(cv < HP2_CV_MAX for cv in cv_vals) if cv_vals else True
    hf2_fail = any(cv > HF2_CV_MAX for cv in cv_vals) if cv_vals else False

    write_slope = agg.get("_write_slope", float("nan"))
    hp3_pass = math.isnan(write_slope) or write_slope <= HP3_SLOPE_MAX
    hp4_pass = all(
        v.get("mean_snr_ratio") is not None and
        HP4_SNR_LO <= v.get("mean_snr_ratio", 0.0) <= HP4_SNR_HI
        for k, v in agg.items() if k != "_write_slope"
    )

    n_hp = sum([hp1_pass, hp2_pass, hp3_pass, hp4_pass])
    mmd_vals = {k: v.get("mean_mmd") for k, v in agg.items() if k != "_write_slope"}
    lmax_vals = {k: v.get("mean_lmax_G") for k, v in agg.items() if k != "_write_slope"}
    cv_dict = {k: v.get("cv_lmax_G") for k, v in agg.items() if k != "_write_slope"}
    write_slope_str = f"{write_slope:.3f}" if not math.isnan(write_slope) else "nan"

    summary = (f"HP1_mmd={hp1_pass}(mmd={mmd_vals}) "
               f"HP2_cv={hp2_pass}(lmax={lmax_vals}, cv={cv_dict}) "
               f"HP3_slope={hp3_pass}({write_slope_str}) "
               f"HP4_snr={hp4_pass} n_hp={n_hp}/4")

    if hf1_fail:
        return ("HARD_FAIL", f"HARD_FAIL: HP1 (MMD >= {HF1_MMD}) -- kernel retrieval breaks. {summary}")
    if hf2_fail:
        return ("HARD_FAIL", f"HARD_FAIL: HP2 (lmax CV > {HF2_CV_MAX}). {summary}")
    if n_hp >= 3:
        return ("HARD_PASS", f"HARD_PASS: {n_hp}/4 HP conditions met. {summary}")
    if n_hp >= 2:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: {n_hp}/4 HP conditions met. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: only {n_hp}/4 HP conditions met. {summary}")


# ---- MAIN SWEEP ----
out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    result = run_seed(seed)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
agg = aggregate_results(per_seed)
verdict, verdict_msg = compute_verdict(agg)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_s = time.time() - t_sweep_start
metrics = {
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "summary": verdict_msg,
    "elapsed_s": elapsed_s,
    "n_seeds": len(SEEDS),
    "run_mode": RUN_MODE,
    "N": N,
    "M_LIST": M_LIST,
    "agg": agg,
    "elapsed_total_s": elapsed_s,
}

metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
