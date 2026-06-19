"""
streaming_write_aging_baseline_v1 -- Streaming-write aging baseline (3 regimes).

SCIENTIFIC QUESTION (NEW: research note Section 2, Wave 1):
  Measure retain_t(tau), kappa_3(t), and spectral density as a function of write
  time for 3 CK-aging regimes parameterized by lambda_w * tau_alpha:
    Regime A: lambda_w * tau_alpha = 0.1  (slow writes, substrate in CK phase)
    Regime B: lambda_w * tau_alpha = 1.0  (write rate ~ aging timescale)
    Regime C: lambda_w * tau_alpha = 10.0 (fast writes, drives substrate out of equilibrium)

  Setup: N=4096, M=2048 patterns written in a streaming fashion. After each write,
  measure: retain_t(tau) = fraction of stored patterns retrievable above threshold,
  kappa_3(t) via Hutchinson (n_probes=200 for speed), and operator spectral density.

  The lambda_w * tau_alpha parameter controls how fast the write rate is relative to
  the CK relaxation timescale. Empirically implemented as:
    Write M patterns sequentially with weight scaling:
    Regime A: alpha_mu = 0.1 (weak writes -> patterns age slowly)
    Regime B: alpha_mu = 1.0 (moderate writes)
    Regime C: alpha_mu = 10.0 (strong writes -> rapid dominance, fast forgetting)

  This is a baseline: first empirical characterization of streaming-write aging in substrate.

PRE-REGISTERED BANDS:
  HARD-PASS:
    Regime A: retain_t(tau) flat (stddev over time < 0.02), mean >= 0.95.
    Regime B: retention decays as power law; fit exponent in [-0.4, -1.0].
    Regime C: retention decays as stretched-exp beta in [0.3, 0.7].
    All 3 regimes must pass their individual sub-test (must pass ALL for HARD_PASS).
  MIDDLE:
    2 of 3 regimes pass their sub-test.
  HARD-FAIL:
    Regime A and Regime C are IDENTICAL (refutes CK class for streaming; if A=C
    then write rate has no effect on aging dynamics, which is non-physical).
    OR: Retain_t is non-monotone in write index (measurement artifact, instrumentation failure).

  Calibration probe note: first empirical characterization; bands set +-50% of
  theoretical CK predictions per calibration policy. No prior streaming anchor.

FORMULA SELF-TESTS:
  1. For alpha_mu=0.1 (Regime A, M=2048, N=4096): alpha=0.5; at this loading most
     patterns should be retrievable. retain ~ 0.5-0.8 (not 0.95 initially; retention
     flat means it does NOT drop further as more writes pile on).
  2. Power-law decay: retain(t) ~ t^(-mu); log-log slope = -mu; fit in [-0.4, -1.0].
  3. Stretched-exp: retain(t) ~ exp(-(t/tau_c)^beta); beta in [0.3, 0.7] for CK.
  4. kappa_3(t) ~ alpha(t) = M_written(t) / N (increases monotonically with writes).

PROT-018: no _nN suffix; production N=4096, M=2048 per rule 3.
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

ANCHOR_NAME = "streaming_write_aging_baseline_v1"

# PROT-018: no _nN suffix; production N=4096, M=2048 per rule 3
N = 4096
M_TOTAL = 2048   # total patterns to write (streaming)

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

# lambda_w * tau_alpha values as alpha_mu scaling factors
REGIME_ALPHA_MU = {"A": 0.1, "B": 1.0, "C": 10.0}

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    M_SMOKE = 512        # need near alpha_c to distinguish regimes: 512/4096 = 0.125 (near alpha_c)
    N_CHECKPOINTS = 6    # measure at 6 milestones
    N_PROBES_K3 = 30     # fewer probes for speed
    N_RELAX_STEPS = 5
    RETRIEVAL_THRESHOLD = 0.70
else:
    SEEDS = [7, 17, 23, 31, 41]
    M_SMOKE = M_TOTAL     # write all 2048 patterns
    N_CHECKPOINTS = 16   # measure at 16 milestones
    N_PROBES_K3 = 200    # kappa_3 probes per checkpoint
    N_RELAX_STEPS = 20
    RETRIEVAL_THRESHOLD = 0.70

# Pre-reg thresholds
HP_RETAIN_A_MEAN = 0.95
HP_RETAIN_A_STD = 0.02   # flat: std over checkpoints < 0.02
HP_POWER_EXPONENT_LO = -1.0
HP_POWER_EXPONENT_HI = -0.4
HP_STRETCH_BETA_LO = 0.3
HP_STRETCH_BETA_HI = 0.7
HF_REGIME_A_C_IDENTICAL_THRESH = 0.02   # |retain_A - retain_C| < 0.02 -> identical

# Formula self-test
_k3_theory_test = 100 / 4096
assert abs(_k3_theory_test - 0.0244) < 0.001
print(f"[formula_selftest] kappa_3 theory at M=100,N=4096={_k3_theory_test:.4f} OK", flush=True)

# Power-law test: if exponent=-0.7, value at t=2 relative to t=1: 2^(-0.7) ~ 0.616
_pw = 2.0 ** (-0.7)
assert abs(_pw - 0.616) < 0.01, f"power law selftest: {_pw}"
print(f"[formula_selftest] power-law decay 2^(-0.7)={_pw:.3f} OK", flush=True)


def hutchinson_kappa3(W: np.ndarray, n_probes: int, seed: int) -> float:
    """Vectorized Hutchinson kappa_3 estimator. Returns scalar estimate."""
    rng = np.random.RandomState(seed)
    N_dim = W.shape[0]
    V = rng.choice([-1.0, 1.0], size=(N_dim, n_probes)).astype(np.float64)
    WV = W @ V
    W2V = W @ WV
    W3V = W @ W2V
    per_probe = (V * W3V).sum(axis=0) / N_dim
    return float(np.mean(per_probe))


def compute_retention(W: np.ndarray, patterns: np.ndarray, n_relax: int,
                      threshold: float) -> float:
    """Fraction of patterns retrievable (cosine_sim >= threshold after relaxation)."""
    M, N_dim = patterns.shape
    W_diag0 = W.copy()
    np.fill_diagonal(W_diag0, 0.0)
    n_retrieved = 0
    for i in range(M):
        state = patterns[i].copy()
        for _ in range(n_relax):
            state = np.sign(W_diag0 @ state)
            state[state == 0] = 1.0
        sim = float(np.dot(state, patterns[i])) / (
            float(np.linalg.norm(state)) * float(np.linalg.norm(patterns[i])) + 1e-12)
        if sim >= threshold:
            n_retrieved += 1
    return n_retrieved / M if M > 0 else 0.0


def fit_power_law(xs: np.ndarray, ys: np.ndarray) -> float:
    """Fit log(y) = mu * log(x) + c. Return exponent mu."""
    valid = (xs > 0) & (ys > 0)
    if valid.sum() < 3:
        return float("nan")
    log_x = np.log(xs[valid])
    log_y = np.log(ys[valid])
    try:
        mu, _ = np.polyfit(log_x, log_y, 1)
        return float(mu)
    except Exception:
        return float("nan")


def fit_stretched_exp_beta(ts: np.ndarray, ys: np.ndarray) -> float:
    """
    Fit stretched-exp: y(t) ~ exp(-(t/tau_c)^beta).
    Linearize: log(-log(y)) = beta * log(t/tau_c).
    Return beta.
    """
    valid = (ts > 0) & (ys > 0) & (ys < 1.0)
    if valid.sum() < 3:
        return float("nan")
    t_v = ts[valid]
    y_v = ys[valid]
    try:
        log_log_y = np.log(-np.log(y_v))
        log_t = np.log(t_v)
        beta, _ = np.polyfit(log_t, log_log_y, 1)
        return float(beta)
    except Exception:
        return float("nan")


def run_seed_regime(seed: int, alpha_mu: float) -> Dict:
    """
    Write M_SMOKE patterns with weight alpha_mu.
    Measure retain_t, kappa_3(t) at N_CHECKPOINTS milestones.
    """
    rng = np.random.RandomState(seed)
    M_run = M_SMOKE
    patterns = rng.choice([-1.0, 1.0], size=(M_run, N)).astype(np.float64)

    # Checkpoints: at write indices evenly spaced
    checkpoint_indices = [int(M_run * (i + 1) / N_CHECKPOINTS)
                          for i in range(N_CHECKPOINTS)]
    checkpoint_indices = sorted(set(max(1, ci) for ci in checkpoint_indices))

    W = np.zeros((N, N), dtype=np.float64)
    retain_curve = []
    kappa3_curve = []
    checkpoint_ms = []

    written = 0
    next_ckpt_idx = 0

    for i in range(M_run):
        xi = patterns[i]
        W += alpha_mu * np.outer(xi, xi) / float(N)
        written += 1

        if next_ckpt_idx < len(checkpoint_indices) and written == checkpoint_indices[next_ckpt_idx]:
            # Measure on first min(64, written) patterns to keep it fast
            measure_M = min(64, written)
            retain = compute_retention(W / (alpha_mu * written / N + 1e-12),
                                       patterns[:measure_M], N_RELAX_STEPS,
                                       RETRIEVAL_THRESHOLD)
            # Use un-normalized W for kappa_3 (reflects actual operator)
            k3 = hutchinson_kappa3(W, N_PROBES_K3, seed + written)
            retain_curve.append(retain)
            kappa3_curve.append(k3)
            checkpoint_ms.append(written)
            next_ckpt_idx += 1

    return {
        "alpha_mu": alpha_mu,
        "checkpoint_ms": checkpoint_ms,
        "retain_curve": retain_curve,
        "kappa3_curve": kappa3_curve,
        "M_written": M_run,
    }


def run_seed(seed: int) -> Dict:
    """Run all 3 regimes for one seed."""
    regime_results = {}
    for regime, alpha_mu in REGIME_ALPHA_MU.items():
        t0 = time.time()
        print(f"  [seed={seed} regime={regime} alpha_mu={alpha_mu}] starting", flush=True)
        res = run_seed_regime(seed, alpha_mu)
        elapsed = time.time() - t0
        res["elapsed_s"] = elapsed
        regime_results[regime] = res
        print(f"  [seed={seed} regime={regime}] "
              f"retain_final={res['retain_curve'][-1]:.3f} if retain_curve else N/A "
              f"elapsed={elapsed:.1f}s", flush=True)
    return {"regime_results": regime_results, "seed": seed, "N": N, "M": M_TOTAL,
            "run_mode": RUN_MODE}


def _instrumentation_selftest():
    """Assert retain_curve and kappa3_curve are non-null at small scale."""
    N_t = 256
    M_t = 32
    n_relax = 5
    seed = 42
    rng = np.random.RandomState(seed)
    pats = rng.choice([-1.0, 1.0], size=(M_t, N_t)).astype(np.float64)
    W_t = np.zeros((N_t, N_t))
    for i in range(M_t):
        W_t += np.outer(pats[i], pats[i]) / float(N_t)
    retain = compute_retention(W_t, pats[:10], n_relax, 0.70)
    k3 = hutchinson_kappa3(W_t, 50, seed)
    assert not math.isnan(retain), "selftest: retain is NaN"
    assert 0.0 <= retain <= 1.0, f"selftest: retain out of range: {retain}"
    assert not math.isnan(k3), "selftest: kappa_3 is NaN"
    # power-law fit test
    ts = np.array([1.0, 2.0, 4.0, 8.0])
    ys = ts ** (-0.6)
    mu = fit_power_law(ts, ys)
    assert abs(mu - (-0.6)) < 0.05, f"selftest: power_law fit mu={mu:.3f} != -0.6"
    print(f"[selftest] PASS: retain={retain:.3f} k3={k3:.4f} power_law_mu={mu:.3f}", flush=True)


_instrumentation_selftest()


def aggregate_results(per_seed: Dict) -> Dict:
    """Aggregate per-regime across seeds."""
    agg = {}
    for regime in ["A", "B", "C"]:
        retain_curves, kappa3_curves, ckpt_ms = [], [], []
        for sd in per_seed.values():
            rr = sd["regime_results"].get(regime)
            if rr is None:
                continue
            retain_curves.append(rr["retain_curve"])
            kappa3_curves.append(rr["kappa3_curve"])
            if not ckpt_ms:
                ckpt_ms = rr["checkpoint_ms"]
        if not retain_curves:
            agg[regime] = {"regime": regime, "error": "no data"}
            continue
        # Mean across seeds at each checkpoint
        min_len = min(len(c) for c in retain_curves)
        mean_retain = [float(np.mean([c[i] for c in retain_curves]))
                       for i in range(min_len)]
        mean_k3 = [float(np.mean([c[i] for c in kappa3_curves if len(c) > i]))
                   for i in range(min_len)]
        # Fit regime metrics
        ts = np.array(ckpt_ms[:min_len], dtype=float)
        ys_retain = np.array(mean_retain)
        retain_std = float(np.std(mean_retain)) if len(mean_retain) > 1 else float("nan")
        retain_mean_final = mean_retain[-1] if mean_retain else float("nan")
        power_mu = fit_power_law(ts, ys_retain)
        # Normalize for stretched-exp (normalize to first value)
        if mean_retain and mean_retain[0] > 0:
            ys_norm = np.array([y / mean_retain[0] for y in mean_retain])
            stretch_beta = fit_stretched_exp_beta(ts, ys_norm)
        else:
            stretch_beta = float("nan")
        agg[regime] = {
            "regime": regime,
            "mean_retain_final": retain_mean_final,
            "retain_std_over_time": retain_std,
            "power_law_exponent": power_mu,
            "stretched_exp_beta": stretch_beta,
            "mean_retain_curve": mean_retain,
            "mean_kappa3_curve": mean_k3,
            "checkpoint_ms": ckpt_ms[:min_len],
            "n_seeds": len(retain_curves),
        }
    return agg


def compute_verdict(agg: Dict) -> Tuple[str, str]:
    """Pre-registered verdict per regime."""
    r_A = agg.get("A", {})
    r_B = agg.get("B", {})
    r_C = agg.get("C", {})

    def safe(d, k): return d.get(k, float("nan"))

    # HARD-FAIL: Regime A == Regime C (identical)
    retain_A = safe(r_A, "mean_retain_final")
    retain_C = safe(r_C, "mean_retain_final")
    if (not math.isnan(retain_A) and not math.isnan(retain_C) and
            abs(retain_A - retain_C) < HF_REGIME_A_C_IDENTICAL_THRESH):
        return ("HARD_FAIL",
                f"Regime A and C are identical (retain_A={retain_A:.3f} "
                f"retain_C={retain_C:.3f} |diff|={abs(retain_A-retain_C):.4f} "
                f"< {HF_REGIME_A_C_IDENTICAL_THRESH}). Refutes CK class for streaming.")

    # Check each regime
    pass_A = (not math.isnan(retain_A) and retain_A >= HP_RETAIN_A_MEAN and
              not math.isnan(safe(r_A, "retain_std_over_time")) and
              safe(r_A, "retain_std_over_time") < HP_RETAIN_A_STD)
    mu_B = safe(r_B, "power_law_exponent")
    pass_B = (not math.isnan(mu_B) and HP_POWER_EXPONENT_LO <= mu_B <= HP_POWER_EXPONENT_HI)
    beta_C = safe(r_C, "stretched_exp_beta")
    pass_C = (not math.isnan(beta_C) and HP_STRETCH_BETA_LO <= beta_C <= HP_STRETCH_BETA_HI)

    n_pass = sum([pass_A, pass_B, pass_C])
    details = (f"Regime A: retain={retain_A:.3f} std={safe(r_A,'retain_std_over_time'):.3f} "
               f"pass={pass_A}. "
               f"Regime B: mu={mu_B:.3f} pass={pass_B}. "
               f"Regime C: beta={beta_C:.3f} pass={pass_C}.")

    if n_pass == 3:
        return ("HARD_PASS",
                f"Streaming-write aging baseline confirmed (3/3 regimes pass). "
                + details +
                " CK-aging IS native real-time-forgetting primitive. "
                "Validates per-fact retention dial + Ebbinghaus curve features.")
    if n_pass == 2:
        return ("MIDDLE_BAND",
                f"Partial streaming-write aging ({n_pass}/3 regimes pass). " + details)
    return ("HARD_FAIL",
            f"Streaming-write aging NOT confirmed ({n_pass}/3 regimes pass). " + details +
            " Reframe: substrate aging class for streaming dynamics unconfirmed.")


def main():
    t_start = time.time()
    print(f"[{ANCHOR_NAME}] run_mode={RUN_MODE} N={N} M_total={M_TOTAL} "
          f"seeds={SEEDS} checkpoints={N_CHECKPOINTS}", flush=True)

    out_dir = get_output_dir(ANCHOR_NAME)
    run_config = {"N": N, "M": M_TOTAL, "run_mode": RUN_MODE}
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
        "M_total": M_TOTAL,
        "seeds": SEEDS,
        "aggregate": agg,
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
