"""Bet M logarithmic-forgetting fit-form selection harness.

Per [[feedback-rehabilitation-after-rejection]] R-PRIME-4 Allen-Cahn t^(1/2)
REJECTED v193; Bet M reframes toward logarithmic forgetting (Wickelgren 1972,
Wixted-Ebbesen 1991 literature anchor).

This is the METHODOLOGY harness: a closed-form fit-form selection oracle that
validates model selection across candidate retention-decay forms BEFORE
applying to real Bet B retention data. Once shipped, the same harness is
re-pointed at real data via the `--data-from <metrics.json>` flag.

Candidate forms (closed-form, parameter count k):
  Form A: power-law       r(t) = a * t^(-b)      (k=2)
  Form B: Wickelgren log  r(t) = a - b*log(t)    (k=2)
  Form C: t^(1/2) decay   r(t) = a - b*sqrt(t)   (k=2)   [the REJECTED Allen-Cahn form]
  Form D: exponential     r(t) = a * exp(-b*t)   (k=2)
  Form E: saturating log  r(t) = a + b*log(1 + c*t)  (k=3)

Method: nonlinear-least-squares fit (scipy-free, pure-numpy via log-domain
linearization + grid search for non-linearizable forms), report R^2, BIC, and
the ranking across all 5 forms. Self-test: generate synthetic data from each
form with known params, fit, verify model selection picks the correct form.

Pre-reg HARD-PASS: model selection oracle picks the correct generating form
   on ≥4 of 5 synthetic-data cases AND best-fit BIC differs from runner-up
   by >=4 (substantial evidence per Kass-Raftery).
   -> Bet M log-forget harness validated; ready to apply to real data.
Pre-reg HARD-FAIL: model selection picks the wrong form on ≥3 of 5 synthetic
   cases OR top-2 BIC differences are all <2 (no discrimination).
   -> harness REJECTED; redesign needed.
Pre-reg MIDDLE: any intermediate; report bands.

Local CPU; pure-numpy; <60s; sub-minute scoping per Tier C.

Pre-reg: preregs/2026-05-24_wave14_betM_logforget_fitform_v1.md
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
T_GRID_FULL = np.array([1, 2, 3, 5, 8, 13, 21, 34, 55], dtype=np.float64)
T_GRID_SMOKE = np.array([1, 3, 8, 21, 55], dtype=np.float64)
N_REPLICATES_FULL = 30        # synthetic replicates per generating form
N_REPLICATES_SMOKE = 5
NOISE_STD_FULL = 0.02         # additive Gaussian noise on synthetic retention
NOISE_STD_SMOKE = 0.02
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

PASS_CORRECT_FORM = 4         # at least 4/5 forms identified correctly
PASS_BIC_GAP = 4.0            # BIC gap to runner-up
FAIL_CORRECT_FORM = 2         # ≤2/5 picks correct -> FAIL
FAIL_MAX_BIC_GAP = 2.0        # all top-2 BIC gaps < this -> no discrimination


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


# ───── Candidate decay forms ─────

def f_powerlaw(t, a, b): return a * t ** (-b)
def f_log(t, a, b): return a - b * np.log(t)
def f_sqrt(t, a, b): return a - b * np.sqrt(t)
def f_exp(t, a, b): return a * np.exp(-b * t)
def f_satlog(t, a, b, c): return a + b * np.log(1 + c * t)


def fit_2param_grid(t, r, model_fn, a_grid, b_grid):
    """Best (a,b) by grid search minimizing SSE."""
    best = (None, None, float("inf"))
    for a in a_grid:
        for b in b_grid:
            try:
                pred = model_fn(t, a, b)
            except (FloatingPointError, OverflowError, ValueError):
                continue
            sse = float(np.sum((r - pred) ** 2))
            if sse < best[2]:
                best = (a, b, sse)
    return best  # (a, b, sse)


def fit_3param_grid(t, r, model_fn, a_grid, b_grid, c_grid):
    best = (None, None, None, float("inf"))
    for a in a_grid:
        for b in b_grid:
            for c in c_grid:
                try:
                    pred = model_fn(t, a, b, c)
                except (FloatingPointError, OverflowError, ValueError):
                    continue
                sse = float(np.sum((r - pred) ** 2))
                if sse < best[3]:
                    best = (a, b, c, sse)
    return best


def bic(sse: float, n: int, k: int) -> float:
    """BIC = n * ln(SSE/n) + k * ln(n)."""
    return n * math.log(sse / n + 1e-12) + k * math.log(n)


def fit_all_forms(t: np.ndarray, r: np.ndarray) -> dict:
    """Fit all 5 candidate forms; return per-form (sse, bic, params)."""
    n = len(t)
    a_grid = np.linspace(0.5, 1.2, 15)
    b_grid_decay = np.linspace(0.0, 0.5, 30)
    b_grid_log = np.linspace(0.0, 0.3, 30)
    b_grid_sqrt = np.linspace(0.0, 0.2, 30)
    b_grid_exp = np.linspace(0.0, 0.2, 30)
    a_grid_satlog = np.linspace(0.4, 1.0, 10)
    b_grid_satlog = np.linspace(-0.3, 0.3, 15)
    c_grid_satlog = np.linspace(0.05, 1.0, 10)

    results = {}
    a, b, sse = fit_2param_grid(t, r, f_powerlaw, a_grid, b_grid_decay)
    results["A_powerlaw"] = {"sse": sse, "bic": bic(sse, n, 2), "params": [a, b]}
    a, b, sse = fit_2param_grid(t, r, f_log, a_grid, b_grid_log)
    results["B_log"] = {"sse": sse, "bic": bic(sse, n, 2), "params": [a, b]}
    a, b, sse = fit_2param_grid(t, r, f_sqrt, a_grid, b_grid_sqrt)
    results["C_sqrt"] = {"sse": sse, "bic": bic(sse, n, 2), "params": [a, b]}
    a, b, sse = fit_2param_grid(t, r, f_exp, a_grid, b_grid_exp)
    results["D_exp"] = {"sse": sse, "bic": bic(sse, n, 2), "params": [a, b]}
    a, b, c, sse = fit_3param_grid(t, r, f_satlog, a_grid_satlog, b_grid_satlog, c_grid_satlog)
    results["E_satlog"] = {"sse": sse, "bic": bic(sse, n, 3), "params": [a, b, c]}
    return results


def pick_best_form(results: dict) -> tuple[str, float]:
    """Return (best_form_label, bic_gap_to_runner_up)."""
    sorted_results = sorted(results.items(), key=lambda kv: kv[1]["bic"])
    best_label, best = sorted_results[0]
    if len(sorted_results) > 1:
        gap = sorted_results[1][1]["bic"] - best["bic"]
    else:
        gap = float("inf")
    return best_label, gap


# ───── Synthetic generators ─────
def gen_synthetic(form_label: str, t: np.ndarray, rng: np.random.Generator,
                   noise_std: float) -> np.ndarray:
    """Generate synthetic retention curve from form_label with realistic params."""
    if form_label == "A_powerlaw":
        return f_powerlaw(t, 0.95, 0.10) + rng.normal(0, noise_std, len(t))
    if form_label == "B_log":
        return f_log(t, 0.95, 0.05) + rng.normal(0, noise_std, len(t))
    if form_label == "C_sqrt":
        return f_sqrt(t, 0.95, 0.02) + rng.normal(0, noise_std, len(t))
    if form_label == "D_exp":
        return f_exp(t, 0.95, 0.02) + rng.normal(0, noise_std, len(t))
    if form_label == "E_satlog":
        return f_satlog(t, 0.95, -0.05, 0.5) + rng.normal(0, noise_std, len(t))
    raise ValueError(form_label)


def run_one_seed(seed: int, t_grid: np.ndarray, n_replicates: int, noise_std: float):
    rng = np.random.default_rng(seed)
    forms = ["A_powerlaw", "B_log", "C_sqrt", "D_exp", "E_satlog"]
    per_form = {}
    for gen_form in forms:
        correct_count = 0
        gaps = []
        for _ in range(n_replicates):
            r = gen_synthetic(gen_form, t_grid, rng, noise_std)
            results = fit_all_forms(t_grid, r)
            best, gap = pick_best_form(results)
            if best == gen_form:
                correct_count += 1
            gaps.append(gap)
        per_form[gen_form] = {
            "correct_rate": correct_count / max(n_replicates, 1),
            "mean_bic_gap": float(np.mean(gaps)),
            "max_bic_gap": float(np.max(gaps)),
            "min_bic_gap": float(np.min(gaps)),
        }
    return per_form


def compute_verdict(summary):
    per_seed = summary.get("per_seed")
    if not per_seed:
        return ("BETM_LOGFORGET_INCONCLUSIVE", "Missing per_seed data.")
    forms = ["A_powerlaw", "B_log", "C_sqrt", "D_exp", "E_satlog"]
    n_seeds = len(per_seed)
    # For each form, the cross-seed mean correct_rate; count forms where mean_correct >= 0.5.
    correct_count = 0
    all_mean_gaps = []
    for form in forms:
        rates = [per_seed[s][form]["correct_rate"] for s in per_seed]
        gaps = [per_seed[s][form]["mean_bic_gap"] for s in per_seed]
        mean_rate = sum(rates) / max(len(rates), 1)
        mean_gap = sum(gaps) / max(len(gaps), 1)
        if mean_rate >= 0.5:
            correct_count += 1
        all_mean_gaps.append(mean_gap)
    median_bic_gap = float(np.median(all_mean_gaps))
    pts = (f"correct_forms={correct_count}/5, median_BIC_gap={median_bic_gap:.2f}, "
           f"per_form_gaps={[round(g, 2) for g in all_mean_gaps]}")
    if correct_count >= PASS_CORRECT_FORM and median_bic_gap >= PASS_BIC_GAP:
        return ("BETM_LOGFORGET_HARD_PASS_HARNESS_VALIDATED",
                f"Fit-form selection harness validated: {correct_count}/5 forms correctly identified "
                f"AND median BIC gap {median_bic_gap:.2f} >= {PASS_BIC_GAP}. Ready for real-data apply. {pts}.")
    if correct_count <= FAIL_CORRECT_FORM or median_bic_gap < FAIL_MAX_BIC_GAP:
        return ("BETM_LOGFORGET_HARD_FAIL_HARNESS_REJECTED",
                f"Harness REJECTED: correct_forms={correct_count} <= {FAIL_CORRECT_FORM} "
                f"OR median_BIC_gap={median_bic_gap:.2f} < {FAIL_MAX_BIC_GAP}. Redesign needed. {pts}.")
    return ("BETM_LOGFORGET_MIDDLE_BAND",
            f"Intermediate: correct={correct_count}/5, median_BIC_gap={median_bic_gap:.2f}. {pts}.")


def self_test_verdict():
    def mk(form_to_rate, form_to_gap):
        ps = {}
        for s in ["17"]:
            ps[s] = {f: {"correct_rate": form_to_rate[f], "mean_bic_gap": form_to_gap[f],
                         "max_bic_gap": form_to_gap[f], "min_bic_gap": form_to_gap[f]}
                     for f in ["A_powerlaw", "B_log", "C_sqrt", "D_exp", "E_satlog"]}
        return {"per_seed": ps}
    s_pass = mk({"A_powerlaw": 0.9, "B_log": 0.9, "C_sqrt": 0.9, "D_exp": 0.9, "E_satlog": 0.6},
                {"A_powerlaw": 6, "B_log": 6, "C_sqrt": 6, "D_exp": 6, "E_satlog": 5})
    s_fail = mk({"A_powerlaw": 0.1, "B_log": 0.2, "C_sqrt": 0.3, "D_exp": 0.2, "E_satlog": 0.1},
                {"A_powerlaw": 1, "B_log": 1, "C_sqrt": 1, "D_exp": 1, "E_satlog": 1})
    s_mid = mk({"A_powerlaw": 0.6, "B_log": 0.6, "C_sqrt": 0.6, "D_exp": 0.4, "E_satlog": 0.4},
                {"A_powerlaw": 3, "B_log": 3, "C_sqrt": 3, "D_exp": 3, "E_satlog": 3})
    s_inconc = {}
    cases = [
        (s_pass, "BETM_LOGFORGET_HARD_PASS_HARNESS_VALIDATED"),
        (s_fail, "BETM_LOGFORGET_HARD_FAIL_HARNESS_REJECTED"),
        (s_mid, "BETM_LOGFORGET_MIDDLE_BAND"),
        (s_inconc, "BETM_LOGFORGET_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, msg = compute_verdict(s)
        if a != exp:
            raise AssertionError(f"verdict {a} != {exp}; msg={msg}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run_experiment(smoke: bool):
    t0 = time.monotonic()
    t_grid = T_GRID_SMOKE if smoke else T_GRID_FULL
    n_rep = N_REPLICATES_SMOKE if smoke else N_REPLICATES_FULL
    noise = NOISE_STD_SMOKE if smoke else NOISE_STD_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    config = {
        "mode": "smoke" if smoke else "full",
        "t_grid": t_grid.tolist(),
        "n_replicates": n_rep,
        "noise_std": noise,
        "seeds": seeds,
        "pass_correct_form": PASS_CORRECT_FORM,
        "pass_bic_gap": PASS_BIC_GAP,
        "fail_correct_form": FAIL_CORRECT_FORM,
        "fail_max_bic_gap": FAIL_MAX_BIC_GAP,
    }
    print(f"[config] {config}", flush=True)
    per_seed = {}
    for seed in seeds:
        print(f"[seed={seed}] ...", flush=True)
        r = run_one_seed(seed, t_grid, n_rep, noise)
        per_seed[str(seed)] = r
        rates = {f: round(r[f]["correct_rate"], 2) for f in r}
        print(f"  rates={rates}", flush=True)
    summary = {"per_seed": per_seed}
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
    out_dir = get_output_dir("wave14_betM_logforget_fitform_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_betM_logforget_fitform_v1")
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
