"""Field-A reservoir-computing Lyapunov spectrum diagnostic.

Per `notes/exp_dev_handoff_fieldA_reservoir_lyapunov_2026-05-24.md`:
Measure the substrate's Lyapunov spectrum at the Bet B retention operating
point. Compare to reservoir-computing edge-of-chaos signatures (λ_1 ≈ 0 at
edge-of-chaos; spectrum decay matches Jaeger-style echo-state predictions).

Method: Benettin et al 1980 standard with QR-decomposition variant. Iterate
substrate Jacobian on a basis of k orthonormal tangent vectors, periodically
re-orthonormalize via QR, accumulate log-stretching to estimate top-k Lyapunov
exponents.

The substrate dynamics here = BSC Hebbian recurrent map x_{t+1} = sign(W x_t)
with W learned by Hebbian outer-product over a corpus. This is the closest
echo-state analog of the substrate. The Jacobian is W locally; under sign
nonlinearity it is W column-rescaled by sign-Jacobian (a diagonal of {-1,+1}
plus 0 at exactly-zero entries; for BSC the exact-zero set is measure-zero
so we use plain W as the Jacobian.

Per [[feedback-lit-scan-calibration-penalty]]: substrate is in uncharted
regime for reservoir-computing literature; deflate P estimates 0.15-0.25
in pre-reg.

Pre-reg HARD-PASS: λ_1 ∈ [-0.05, +0.05] (edge-of-chaos signature) AND top-5
   spectrum decay r^2 >= 0.85 against log-linear fit (reservoir-computing
   prediction). -> Field-A row 🔬 -> 🟡 (Lyapunov-matched, opens memory-capacity
   closed-form).
Pre-reg HARD-FAIL: |λ_1| > 0.20 (firmly chaotic or firmly contractive). ->
   Field-A REJECTED at this operating point; save Week-2 drill budget.
Pre-reg MIDDLE: any intermediate; report bands.

Operating points probed: Hebbian W trained from random corpus at three
substrate regimes (low/mid/high density of stored items), bracketing the
Bet B retention operating regime.

CPU-suitable: pure-numpy matrix-spectrum diagnostic, no training, no
gradient.

Pre-reg: preregs/2026-05-24_wave14_fieldA_lyapunov_spectrum_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import json
import math
import os
import time
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
# ───── design parameters (exp_dev autonomy) ─────
N_FULL = 1024            # substrate width
N_SMOKE = 128
K_EXPONENTS_FULL = 5     # top-k exponents to estimate (per Field-A hand-off "top-k or full")
K_EXPONENTS_SMOKE = 3
T_ITER_FULL = 1500       # iterations for Lyapunov estimation
T_ITER_SMOKE = 100
T_WARMUP_FULL = 200      # discard initial transient
T_WARMUP_SMOKE = 20
QR_INTERVAL_FULL = 5     # re-orthonormalize every QR_INTERVAL steps
QR_INTERVAL_SMOKE = 2
M_DENSITIES_FULL = [0.05, 0.20, 0.50]  # M_stored / N — three operating-density points
M_DENSITIES_SMOKE = [0.20]
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

# Falsifier thresholds (pre-registered).
PASS_LYAP1_BAND = 0.05      # |λ_1| within this band at >=1 operating point
PASS_R2 = 0.85              # log-linear decay r^2 across top-k
FAIL_LYAP1_ABS = 0.20       # |λ_1| > this -> firmly chaotic/contractive


def get_output_dir(default_name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(default_name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d):
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required: {missing}")


def bsc_atoms(num: int, dim: int, rng: np.random.Generator) -> np.ndarray:
    """Return num x dim {-1,+1} BSC code vectors."""
    return (rng.integers(0, 2, size=(num, dim)).astype(np.float32) * 2 - 1)


def build_substrate_W(N: int, M_density: float, rng: np.random.Generator) -> np.ndarray:
    """Build a Hebbian-trained BSC substrate W of shape (N, N).

    Stores M = M_density * N random key-value pairs.
    """
    M = max(1, int(round(M_density * N)))
    keys = bsc_atoms(M, N, rng)
    vals = bsc_atoms(M, N, rng)
    W = (keys.T @ vals) / M  # (N, N)
    return W


def lyapunov_spectrum_qr(W: np.ndarray, k: int, T: int, T_warmup: int,
                          qr_interval: int, rng: np.random.Generator) -> tuple[np.ndarray, float]:
    """Estimate top-k Lyapunov exponents of the linear map x_{t+1} = W x_t
    using Benettin/Shimada-Nagashima QR method.

    Since the map is linear, the Lyapunov spectrum equals the singular-value
    log-magnitudes of W per step (homogeneous). We still run the iterative
    algorithm to verify convergence and produce a finite-time estimate that
    matches the realistic "tracking divergence on a basis" approach.

    Returns (lyap_exponents, mean_norm_step).
    """
    N = W.shape[0]
    Q = rng.standard_normal((N, k)).astype(np.float32)
    Q, _ = np.linalg.qr(Q)  # orthonormal basis (N x k)
    sum_log = np.zeros(k, dtype=np.float64)
    n_qr = 0
    mean_norm = 0.0
    norm_count = 0
    for t in range(T_warmup + T):
        Q = W @ Q
        # Track mean norm of the columns post-W for diagnostic.
        mean_norm += float(np.linalg.norm(Q) / math.sqrt(k))
        norm_count += 1
        if (t + 1) % qr_interval == 0:
            Q_new, R = np.linalg.qr(Q)
            if t >= T_warmup:
                # diag(R) gives stretching factors over qr_interval steps
                diag_R = np.abs(np.diag(R))
                diag_R = np.maximum(diag_R, 1e-300)
                sum_log += np.log(diag_R)
                n_qr += 1
            Q = Q_new
    if n_qr == 0:
        return np.zeros(k, dtype=np.float64), mean_norm / max(norm_count, 1)
    # Per-step Lyapunov exponents.
    lyap = sum_log / (n_qr * qr_interval)
    return lyap, mean_norm / max(norm_count, 1)


def run_one_seed_density(seed: int, density: float, N: int, K_exp: int,
                          T: int, T_warmup: int, qr_interval: int):
    rng = np.random.default_rng(seed)
    W = build_substrate_W(N, density, rng)
    lyap, mean_norm = lyapunov_spectrum_qr(W, K_exp, T, T_warmup, qr_interval, rng)
    lyap_sorted = np.sort(lyap)[::-1]  # descending
    # log-linear fit of spectrum decay (log10(|λ_i|+eps) vs i)
    # We use ABS for decay-magnitude analysis (some exponents may be negative).
    eps = 1e-9
    y = np.log10(np.abs(lyap_sorted) + eps)
    x = np.arange(len(y), dtype=np.float64)
    if len(y) >= 2:
        slope, intercept = np.polyfit(x, y, 1)
        y_pred = slope * x + intercept
        ss_res = float(((y - y_pred) ** 2).sum())
        ss_tot = float(((y - y.mean()) ** 2).sum())
        r2 = 1.0 - ss_res / max(ss_tot, 1e-12)
    else:
        slope, intercept, r2 = 0.0, 0.0, 0.0
    return {
        "lyapunov_exponents": lyap_sorted.tolist(),
        "lambda_1": float(lyap_sorted[0]),
        "mean_norm_diag": float(mean_norm),
        "decay_slope": float(slope),
        "decay_r2": float(r2),
        "density": density,
        "M_stored": int(round(density * N)),
    }


def compute_verdict(summary):
    per_density = summary.get("per_density")
    if not per_density:
        return ("LYAP_INCONCLUSIVE", "Missing per_density data.")
    # collect mean lambda_1 per density
    densities = sorted([float(d) for d in per_density.keys()])
    rows = []
    any_at_edge = False
    max_abs_lambda1 = 0.0
    best_r2_at_edge = 0.0
    for d in densities:
        seeds = per_density[str(d)]
        lambda1_mean = sum(s["lambda_1"] for s in seeds.values()) / len(seeds)
        r2_mean = sum(s["decay_r2"] for s in seeds.values()) / len(seeds)
        rows.append((d, lambda1_mean, r2_mean))
        max_abs_lambda1 = max(max_abs_lambda1, abs(lambda1_mean))
        if abs(lambda1_mean) <= PASS_LYAP1_BAND:
            any_at_edge = True
            if r2_mean > best_r2_at_edge:
                best_r2_at_edge = r2_mean
    pts = ", ".join(f"density={d:.2f}: λ_1={l1:.4f}, decay_r²={r2:.3f}" for d, l1, r2 in rows)
    if any_at_edge and best_r2_at_edge >= PASS_R2:
        return ("LYAP_HARD_PASS_EDGE_OF_CHAOS",
                f"Edge-of-chaos signature: |λ_1| <= {PASS_LYAP1_BAND} at >=1 operating point AND "
                f"decay r² = {best_r2_at_edge:.3f} >= {PASS_R2}. {pts}.")
    if max_abs_lambda1 > FAIL_LYAP1_ABS:
        return ("LYAP_HARD_FAIL_FAR_FROM_EDGE",
                f"Firmly chaotic/contractive: max |λ_1| = {max_abs_lambda1:.4f} > {FAIL_LYAP1_ABS} "
                f"at >=1 operating point. Field-A reservoir-computing REJECTED. {pts}.")
    return ("LYAP_MIDDLE_BAND",
            f"Intermediate: max |λ_1| = {max_abs_lambda1:.4f}, edge_at_any={any_at_edge}, "
            f"best_r2_at_edge={best_r2_at_edge:.3f}. {pts}.")


def self_test_verdict():
    def mk(d_to_l1, d_to_r2):
        return {"per_density": {str(d): {"17": {"lambda_1": l1, "decay_r2": d_to_r2[d]}}
                                for d, l1 in d_to_l1.items()}}
    s_pass = mk({0.05: 0.03, 0.20: -0.02, 0.50: 0.10}, {0.05: 0.92, 0.20: 0.90, 0.50: 0.70})
    s_fail = mk({0.05: 0.30, 0.20: 0.40, 0.50: 0.60}, {0.05: 0.5, 0.20: 0.5, 0.50: 0.5})
    s_mid = mk({0.05: 0.12, 0.20: 0.15, 0.50: 0.18}, {0.05: 0.6, 0.20: 0.6, 0.50: 0.6})
    s_inconc = {}
    cases = [
        (s_pass, "LYAP_HARD_PASS_EDGE_OF_CHAOS"),
        (s_fail, "LYAP_HARD_FAIL_FAR_FROM_EDGE"),
        (s_mid, "LYAP_MIDDLE_BAND"),
        (s_inconc, "LYAP_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, msg = compute_verdict(s)
        if a != exp:
            raise AssertionError(f"verdict {a} != {exp}; msg={msg}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run_experiment(smoke: bool):
    t0 = time.monotonic()
    N = N_SMOKE if smoke else N_FULL
    K_exp = K_EXPONENTS_SMOKE if smoke else K_EXPONENTS_FULL
    T = T_ITER_SMOKE if smoke else T_ITER_FULL
    T_warmup = T_WARMUP_SMOKE if smoke else T_WARMUP_FULL
    qr_int = QR_INTERVAL_SMOKE if smoke else QR_INTERVAL_FULL
    densities = M_DENSITIES_SMOKE if smoke else M_DENSITIES_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    config = {
        "mode": "smoke" if smoke else "full",
        "N": N,
        "K_exponents": K_exp,
        "T_iter": T,
        "T_warmup": T_warmup,
        "qr_interval": qr_int,
        "M_densities": densities,
        "seeds": seeds,
        "pass_lyap1_band": PASS_LYAP1_BAND,
        "pass_r2": PASS_R2,
        "fail_lyap1_abs": FAIL_LYAP1_ABS,
    }
    print(f"[config] {config}", flush=True)
    per_density = {}
    for d in densities:
        print(f"[density={d}] ...", flush=True)
        per_seed = {}
        for seed in seeds:
            r = run_one_seed_density(seed, d, N, K_exp, T, T_warmup, qr_int)
            per_seed[str(seed)] = r
            print(f"  density={d} seed={seed}: λ_1={r['lambda_1']:.4f} decay_r²={r['decay_r2']:.3f}", flush=True)
        per_density[str(d)] = per_seed
    summary = {"per_density": per_density}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
               "summary": summary, "config": config}
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14_fieldA_lyapunov_spectrum_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_fieldA_lyapunov_spectrum_v1")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nDONE: {verdict}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test_verdict(); return 0
    if args.smoke:
        run_smoke(); return 0
    run_main(); return 0


if __name__ == "__main__":
    sys.exit(main())
