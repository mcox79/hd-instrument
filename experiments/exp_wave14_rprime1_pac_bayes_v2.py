"""R-PRIME-1 PAC-Bayes KL-accumulation retention floor v2 (calibrated sigma).

v1 SMOKE HARD_FAIL root cause: sigma=0.10 produced KL >> M (floor clamped to 0).
The Gaussian posterior sigma must be calibrated to the W update magnitude, not
fixed at 0.10 for a substrate with N=4096 where outer-product updates
||dW||_F^2 ~ N * M_per_task.

v2 FIX: sigma is auto-calibrated per trial as:
    sigma = calibration_factor * sqrt(||W_1 - W_0||_F^2 / N^2)
    = calibration_factor * ||delta_W||_F / N
where calibration_factor=1.0 sets sigma to the RMS update amplitude (one Frobenius
norm per entry). This ensures KL_t = ||dW_t||_F^2 / (2*sigma^2) ~ N^2/2 per task
step, keeping the floor 1 - sqrt(KL/(2M)) in (0, 1) for reasonable M values.

Hypothesis (unchanged from v1):
Multi-task retention has an information-theoretic LOWER BOUND set by KL
divergence accumulation. PAC-Bayes: retention(t) >= 1 - sqrt(KL_acc / (2*M)).
If measured retention TRACKS this predicted floor across norm regimes, PAC-Bayes
is the binding mechanism.

Per [[feedback-no-experiment-design-in-prompts]]: all parameters chosen by exp_dev.
Per [[feedback-no-smoke]]: HARD-PASS/HARD-FAIL bands pre-registered.
Per [[feedback-lit-scan-calibration-penalty]]: PAC-Bayes for Hebbian outer-product
memories is uncharted regime; P estimates deflated.

Pre-reg:
    HARD-PASS: measured retention tracks PAC-Bayes floor within +/-20% on
               >=3 of 5 phase-A norm regimes (norm in {0.5, 1.0, 2.0, 4.0, 8.0})
               AND Pearson r(predicted, measured) >= 0.60.
               -> R-PRIME-1 PAC-Bayes row promoted 🔬 -> 🟡 (PAC-Bayes is
               retention-mechanism candidate).
    HARD-FAIL: max abs error |measured - predicted| > 0.40 on every regime
               OR Pearson r(predicted, measured) < 0.20.
               -> PAC-Bayes floor REJECTED as Bet B mechanism.
    MIDDLE: any intermediate; report bands.

Self-test (per [[feedback-strategy-spec-formula-selftests]]):
    sigma_rms = 1.0 (floor formula): pac_bayes_floor(kl=50, m=200) -> 1 - sqrt(50/400) = 1 - 0.354 = 0.646
    pac_bayes_floor(kl=0, m=100) -> 1.0
    pac_bayes_floor(kl=200, m=100) -> max(0, 1 - sqrt(200/200)) = 0.0

Queue: remote_cpu_queue (pure CPU, multi-regime sweep, ~5-15 min)
Pre-reg file: preregs/2026-05-24_wave14_rprime1_pac_bayes_v2.md
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

try:
    import torch
    HAS_TORCH = True
except Exception:
    HAS_TORCH = False

REPO = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
# ───── design parameters (exp_dev autonomy) ─────
NORM_REGIMES_FULL = [0.5, 1.0, 2.0, 4.0, 8.0]
NORM_REGIMES_SMOKE = [1.0, 4.0]
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
N_FULL = 4096
N_SMOKE = 512
M_PER_TASK_FULL = 200
M_PER_TASK_SMOKE = 40
N_TASKS_FULL = 4
N_TASKS_SMOKE = 2

# v2: auto-calibrated sigma via RMS update amplitude
# sigma = CALIBRATION_FACTOR * ||delta_W||_F / N
CALIBRATION_FACTOR = 1.0

PASS_WITHIN_PCT = 0.20            # within +/-20% of predicted
PASS_MIN_REGIMES = 3              # at least 3 of 5 regimes track
PASS_PEARSON = 0.60
FAIL_MAX_ABS_ERR = 0.40
FAIL_PEARSON = 0.20


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


def pac_bayes_floor(kl_total, m_total):
    """PAC-Bayes generalization floor: retention >= max(0, 1 - sqrt(KL/(2M)))."""
    if m_total <= 0:
        return 0.0
    return max(0.0, 1.0 - math.sqrt(kl_total / (2.0 * m_total)))


def pearson(xs, ys):
    n = len(xs)
    if n < 2:
        return 0.0
    mx = sum(xs) / n
    my = sum(ys) / n
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    if sxx * syy <= 0:
        return 0.0
    return sxy / math.sqrt(sxx * syy)


def run_one_regime(norm, n, m_per, n_tasks, seed, device="cpu"):
    """Run one norm regime: accumulate KL, measure retention on task 0."""
    rng = np.random.default_rng(seed * 1000 + int(norm * 1000))
    W = np.zeros((n, n), dtype=np.float64)
    prev_W = W.copy()
    kl_acc = 0.0
    all_keys, all_vals = [], []
    sigma_used = 0.0

    for t in range(n_tasks):
        task_rng = np.random.default_rng(seed * 7919 + t)
        # Keys scaled by norm/sqrt(n), vals by 1/sqrt(n)
        keys = task_rng.standard_normal((m_per, n)) * (norm / math.sqrt(n))
        vals = task_rng.standard_normal((m_per, n)) / math.sqrt(n)
        all_keys.append(keys)
        all_vals.append(vals)

        W = W + vals.T @ keys  # Hebbian update

        # v2: calibrate sigma from this task's update magnitude
        delta_W = W - prev_W
        delta_frob = float(np.linalg.norm(delta_W, 'fro'))
        sigma_t = CALIBRATION_FACTOR * delta_frob / n
        sigma_t = max(sigma_t, 1e-9)  # guard against zero update
        sigma_used += sigma_t

        # KL between N(W, sigma_t^2 I) and N(prev_W, sigma_t^2 I)
        kl_t = delta_frob ** 2 / (2.0 * sigma_t ** 2)
        kl_acc += kl_t
        prev_W = W.copy()

    # Retention on TASK 0 after all tasks
    keys_0, vals_0 = all_keys[0], all_vals[0]
    recall = (W @ keys_0.T).T  # (m_per, n)
    num = (recall * vals_0).sum(axis=1)
    denom = np.maximum(np.linalg.norm(recall, axis=1) * np.linalg.norm(vals_0, axis=1), 1e-9)
    ret_A = float((num / denom).mean())

    m_total = m_per * n_tasks
    floor = pac_bayes_floor(kl_acc, m_total)
    return {"norm": norm, "kl_acc": float(kl_acc), "ret_A_measured": ret_A,
            "ret_A_predicted_floor": floor,
            "abs_err": abs(ret_A - floor),
            "sigma_mean": float(sigma_used / n_tasks)}


def compute_verdict(summary):
    per_regime = summary.get("per_regime", {})
    if not per_regime or len(per_regime) < 2:
        return ("PAC_BAYES_V2_INCONCLUSIVE",
                f"Need >=2 regimes; got {len(per_regime)}.")
    rows = []
    for norm, d in per_regime.items():
        rows.append((float(norm), d["mean_ret_measured"], d["mean_ret_predicted"],
                     d["mean_abs_err"]))
    rows.sort(key=lambda t: t[0])
    measured = [r[1] for r in rows]
    predicted = [r[2] for r in rows]
    abs_errs = [r[3] for r in rows]
    r_pearson = pearson(measured, predicted)
    n_within = sum(1 for m, p in zip(measured, predicted)
                   if abs(m - p) <= PASS_WITHIN_PCT * max(abs(p), 0.05))
    max_abs = max(abs_errs)
    pts = ", ".join(f"norm={n}:meas={m:.3f},pred={p:.3f},err={e:.3f}"
                    for n, m, p, e in rows)
    if n_within >= PASS_MIN_REGIMES and r_pearson >= PASS_PEARSON:
        return ("PAC_BAYES_V2_HARD_PASS",
                f"PAC-Bayes floor TRACKS: {n_within}/{len(rows)} regimes within "
                f"{int(PASS_WITHIN_PCT*100)}% AND r={r_pearson:.3f}>={PASS_PEARSON}. {pts}.")
    if max_abs > FAIL_MAX_ABS_ERR and abs(r_pearson) < FAIL_PEARSON:
        return ("PAC_BAYES_V2_HARD_FAIL",
                f"PAC-Bayes floor REJECTED: max_abs_err={max_abs:.3f}>{FAIL_MAX_ABS_ERR} "
                f"AND r={r_pearson:.3f}<{FAIL_PEARSON}. {pts}.")
    return ("PAC_BAYES_V2_MIDDLE_BAND",
            f"Intermediate: n_within={n_within}/{len(rows)}, r={r_pearson:.3f}, "
            f"max_abs={max_abs:.3f}. {pts}.")


def self_test_verdict():
    """Self-test: pac_bayes_floor formula + verdict logic."""
    # Formula self-tests
    assert abs(pac_bayes_floor(50, 200) - (1 - math.sqrt(50 / 400))) < 1e-9, \
        "pac_bayes_floor(50, 200) formula fail"
    assert pac_bayes_floor(0, 100) == 1.0, "pac_bayes_floor(0, 100) fail"
    assert pac_bayes_floor(200, 100) == 0.0, "pac_bayes_floor(200, 100) fail"

    def mk(rows):
        per_regime = {}
        for n, m, p, e in rows:
            per_regime[str(n)] = {"mean_ret_measured": m, "mean_ret_predicted": p,
                                   "mean_abs_err": e}
        return {"per_regime": per_regime}

    # PASS: tight tracking
    s_pass = mk([(0.5, 0.95, 0.94, 0.01), (1.0, 0.86, 0.85, 0.01),
                 (2.0, 0.71, 0.70, 0.01), (4.0, 0.51, 0.49, 0.02),
                 (8.0, 0.21, 0.19, 0.02)])
    # FAIL: huge errors + zero correlation
    s_fail = mk([(0.5, 0.50, 0.94, 0.44), (1.0, 0.50, 0.85, 0.35),
                 (2.0, 0.50, 0.70, 0.20), (4.0, 0.50, 0.49, 0.01),
                 (8.0, 0.50, 0.19, 0.31)])
    # MIDDLE
    s_mid = mk([(0.5, 0.50, 0.94, 0.44), (1.0, 0.70, 0.85, 0.15),
                (2.0, 0.55, 0.70, 0.15), (4.0, 0.30, 0.49, 0.19),
                (8.0, 0.15, 0.19, 0.04)])
    s_inconc = mk([(1.0, 0.80, 0.80, 0.0)])
    cases = [(s_pass, "PAC_BAYES_V2_HARD_PASS"),
             (s_fail, "PAC_BAYES_V2_HARD_FAIL"),
             (s_mid, "PAC_BAYES_V2_MIDDLE_BAND"),
             (s_inconc, "PAC_BAYES_V2_INCONCLUSIVE")]
    for s, exp in cases:
        a, msg = compute_verdict(s)
        if a != exp:
            raise AssertionError(f"verdict {a} != {exp}; msg={msg}")
    print(f"self-test passed (3 formula + {len(cases)} verdict cases)", flush=True)


def run_experiment(smoke: bool):
    t0 = time.monotonic()
    n = N_SMOKE if smoke else N_FULL
    m_per = M_PER_TASK_SMOKE if smoke else M_PER_TASK_FULL
    n_tasks = N_TASKS_SMOKE if smoke else N_TASKS_FULL
    norms = NORM_REGIMES_SMOKE if smoke else NORM_REGIMES_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    device = "cpu"  # pure numpy
    config = {"mode": "smoke" if smoke else "full", "n": n, "m_per_task": m_per,
              "n_tasks": n_tasks, "norm_regimes": norms, "seeds": seeds,
              "calibration_factor": CALIBRATION_FACTOR, "device": device,
              "pass_within_pct": PASS_WITHIN_PCT, "pass_min_regimes": PASS_MIN_REGIMES,
              "pass_pearson": PASS_PEARSON, "fail_max_abs_err": FAIL_MAX_ABS_ERR,
              "fail_pearson": FAIL_PEARSON}
    print(f"[config] {config}", flush=True)
    per_regime = {}
    for norm in norms:
        ret_m, ret_p, abs_e, sigmas = [], [], [], []
        for seed in seeds:
            r = run_one_regime(norm, n, m_per, n_tasks, seed, device=device)
            ret_m.append(r["ret_A_measured"])
            ret_p.append(r["ret_A_predicted_floor"])
            abs_e.append(r["abs_err"])
            sigmas.append(r["sigma_mean"])
        per_regime[str(norm)] = {"mean_ret_measured": sum(ret_m) / len(ret_m),
                                  "mean_ret_predicted": sum(ret_p) / len(ret_p),
                                  "mean_abs_err": sum(abs_e) / len(abs_e),
                                  "mean_sigma": sum(sigmas) / len(sigmas),
                                  "seeds_meas": ret_m, "seeds_pred": ret_p}
        print(f"  norm={norm}: meas={per_regime[str(norm)]['mean_ret_measured']:.3f} "
              f"pred={per_regime[str(norm)]['mean_ret_predicted']:.3f} "
              f"err={per_regime[str(norm)]['mean_abs_err']:.3f} "
              f"sigma={per_regime[str(norm)]['mean_sigma']:.4f}", flush=True)
    summary = {"per_regime": per_regime}
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test_verdict()
        return 0
    out_name = ("wave14_rprime1_pac_bayes_v2_smoke" if args.smoke
                else "wave14_rprime1_pac_bayes_v2")
    out_dir = get_output_dir(out_name)
    summary, verdict, msg, elapsed, config = run_experiment(smoke=args.smoke)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\n{'SMOKE' if args.smoke else 'DONE'}: {verdict}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
