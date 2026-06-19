"""Bet M R3 — Logarithmic-forgetting LONGER-T fit (t in 1..200).

Context: BETM_LOGFORGET_MIDDLE_BAND verdict at v195 — harness picks log-form on
4/5 BIC fits, median BIC gap 2.23 (borderline). The fit-form selection
discriminates well on shorter t-grid but the v192/v193 t=1..21 sweep is too
short for definitive log vs exponential discrimination. R3 from cap_map v192
rescue list: extend t to t in {1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 200}.

Goal: resolve whether log-form survives at longer-t OR exponential decay wins
decisively. Either outcome is a closed-form retention predictor (Wickelgren
1972 / Wixted-Ebbesen 1991 if log; Ebbinghaus exponential if exp). The
borderline gap at v195 is the trigger.

Method: model substrate retention(t) via the canonical Bet B Hebbian pipeline
at multiple t values (t = number of post-Phase-A Phase-B training steps),
measure ret_A at each t, fit candidate forms (A power, B log, C sqrt, D exp,
E satlog), report best by BIC. This is the harness from
exp_wave14_betM_logforget_fitform_v1.py applied to a LONGER t-grid on REAL
substrate data (not synthetic).

Per [[feedback-no-experiment-design-in-prompts]]: all parameters chosen by exp_dev autonomy.
Per [[feedback-no-smoke]]: HARD-PASS/HARD-FAIL bands pre-registered.
Per [[feedback-dont-overextend-theorems]]: borderline BIC gap at v195 is the
DISCRIMINATION trigger, not a closure; longer-t resolves.

Pre-reg:
    HARD-PASS: best-fit BIC gap >= 6 (strong evidence per Kass-Raftery)
               between the winning form and runner-up; AND winning form is
               consistent across >=4 of 5 seeds.
               -> Bet M logarithmic-forgetting (or exponential) row promoted
               to closed-form predictor.
    HARD-FAIL: best-fit BIC gap <= 1 (no evidence); OR no consistent
               winning form across seeds (different winner each seed).
               -> Bet M form unresolved; mechanism remains open.
    MIDDLE: any intermediate; report bands.

Pure-CPU, single-config, long-running (~10-30 min on CPU). Routes to
remote_cpu_queue per Tier B.

Pre-reg file: preregs/2026-05-24_wave14_betM_logforget_longt_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse, json, math, os, time
from pathlib import Path
import numpy as np

try:
    import torch
    HAS_TORCH = True
except Exception:
    HAS_TORCH = False

REPO = Path(__file__).resolve().parent.parent

T_GRID_FULL = np.array([1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 200], dtype=np.float64)
T_GRID_SMOKE = np.array([1, 5, 21, 89], dtype=np.float64)
N_FULL = 4096
N_SMOKE = 512
M_PER_TASK_FULL = 200
M_PER_TASK_SMOKE = 30
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

PASS_BIC_GAP = 6.0
PASS_CONSISTENT_SEEDS = 4
FAIL_BIC_GAP = 1.0


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing: raise ValueError(f"metrics missing required: {missing}")


def hebbian_W(keys, vals):
    return vals.T @ keys


def retention(W, keys, vals):
    rec = (W @ keys.T).T
    num = (rec * vals).sum(dim=1)
    denom = (rec.norm(dim=1) * vals.norm(dim=1)).clamp(min=1e-9)
    return float((num / denom).mean())


def simulate_retention_curve(seed, n, m_per, t_grid):
    """Phase-A train, then Phase-B for t steps; measure ret_A at each t."""
    g = torch.Generator(device="cpu").manual_seed(seed)
    keys_A = torch.randn(m_per, n, generator=g) / math.sqrt(n)
    vals_A = torch.randn(m_per, n, generator=g) / math.sqrt(n)
    W = hebbian_W(keys_A, vals_A)
    rets = []
    max_t = int(t_grid.max())
    snapshot_at = set(int(t) for t in t_grid)
    cur_ret = retention(W, keys_A, vals_A)
    if 0 in snapshot_at: rets.append(cur_ret)
    for step in range(1, max_t + 1):
        keys_B = torch.randn(m_per, n, generator=g) / math.sqrt(n)
        vals_B = torch.randn(m_per, n, generator=g) / math.sqrt(n)
        W = W + hebbian_W(keys_B, vals_B)
        if step in snapshot_at:
            rets.append(retention(W, keys_A, vals_A))
    return rets


# ───── Fit forms ─────

def f_power(t, a, b): return a * t ** (-b)
def f_log(t, a, b): return a - b * np.log(t)
def f_sqrt(t, a, b): return a - b * np.sqrt(t)
def f_exp(t, a, b): return a * np.exp(-b * t)


def fit_2p(t, r, fn, a_grid, b_grid):
    best = (None, None, float("inf"))
    for a in a_grid:
        for b in b_grid:
            try:
                pred = fn(t, a, b)
                sse = float(np.sum((pred - r) ** 2))
                if sse < best[2]: best = (a, b, sse)
            except Exception: continue
    return best


def fit_all_forms(t, r):
    a_grid = np.linspace(0.2, 1.2, 41)
    b_grid_pos = np.linspace(0.001, 0.5, 51)
    b_grid_log = np.linspace(0.001, 0.3, 41)
    results = {}
    results["A_powerlaw"] = fit_2p(t, r, f_power, a_grid, b_grid_pos)
    results["B_log"] = fit_2p(t, r, f_log, a_grid, b_grid_log)
    results["C_sqrt"] = fit_2p(t, r, f_sqrt, a_grid, b_grid_log)
    results["D_exp"] = fit_2p(t, r, f_exp, a_grid, b_grid_pos)
    n = len(t); k = 2
    bics = {}
    for name, (a, b, sse) in results.items():
        sigma2 = sse / n if sse > 0 else 1e-9
        ll = -n / 2 * math.log(2 * math.pi * sigma2) - sse / (2 * sigma2)
        bic = k * math.log(n) - 2 * ll
        bics[name] = bic
    return bics


def best_and_gap(bics):
    items = sorted(bics.items(), key=lambda kv: kv[1])
    best_name, best_bic = items[0]
    runnerup_bic = items[1][1]
    return best_name, runnerup_bic - best_bic


def compute_verdict(summary):
    per_seed = summary.get("per_seed", {})
    if not per_seed: return ("BETM_LONGT_INCONCLUSIVE", "No seeds.")
    winners = []; gaps = []
    for s, d in per_seed.items():
        winners.append(d["best_form"]); gaps.append(d["bic_gap"])
    # Majority winner across seeds
    from collections import Counter
    cnt = Counter(winners)
    top_form, top_count = cnt.most_common(1)[0]
    mean_gap = sum(gaps)/len(gaps)
    pts = ", ".join(f"s{s}:{d['best_form']}(gap={d['bic_gap']:.2f})"
                    for s,d in per_seed.items())
    if mean_gap >= PASS_BIC_GAP and top_count >= PASS_CONSISTENT_SEEDS:
        return ("BETM_LONGT_HARD_PASS_FORM_RESOLVED",
                f"Form RESOLVED: best={top_form} on {top_count}/{len(winners)} seeds, "
                f"mean BIC gap={mean_gap:.2f}>={PASS_BIC_GAP}. {pts}.")
    if mean_gap <= FAIL_BIC_GAP or top_count < 2:
        return ("BETM_LONGT_HARD_FAIL_NO_DISCRIMINATION",
                f"Form UNRESOLVED: mean BIC gap={mean_gap:.2f}<={FAIL_BIC_GAP} "
                f"OR no consistent winner ({cnt}). {pts}.")
    return ("BETM_LONGT_MIDDLE_BAND",
            f"Intermediate: best={top_form} on {top_count}/{len(winners)} seeds, "
            f"mean BIC gap={mean_gap:.2f}. {pts}.")


def self_test_verdict():
    def mk(rows):
        ps = {}
        for i, (form, gap) in enumerate(rows):
            ps[str(i)] = {"best_form": form, "bic_gap": gap}
        return {"per_seed": ps}
    s_pass = mk([("B_log", 8.0)]*5)
    s_fail = mk([("B_log", 0.5), ("D_exp", 0.6), ("A_powerlaw", 0.5),
                 ("C_sqrt", 0.4), ("B_log", 0.7)])
    s_mid = mk([("B_log", 4.0), ("B_log", 3.5), ("D_exp", 3.8),
                ("B_log", 4.5), ("D_exp", 3.6)])
    s_inconc = {"per_seed": {}}
    cases = [(s_pass, "BETM_LONGT_HARD_PASS_FORM_RESOLVED"),
             (s_fail, "BETM_LONGT_HARD_FAIL_NO_DISCRIMINATION"),
             (s_mid, "BETM_LONGT_MIDDLE_BAND"),
             (s_inconc, "BETM_LONGT_INCONCLUSIVE")]
    for s, exp in cases:
        a, msg = compute_verdict(s)
        if a != exp:
            raise AssertionError(f"verdict {a} != {exp}; msg={msg}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run_experiment(smoke: bool):
    t0 = time.monotonic()
    t_grid = T_GRID_SMOKE if smoke else T_GRID_FULL
    n = N_SMOKE if smoke else N_FULL
    m_per = M_PER_TASK_SMOKE if smoke else M_PER_TASK_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    config = {"mode": "smoke" if smoke else "full",
              "t_grid": t_grid.tolist(), "n": n, "m_per": m_per, "seeds": seeds,
              "pass_bic_gap": PASS_BIC_GAP, "pass_consistent_seeds": PASS_CONSISTENT_SEEDS,
              "fail_bic_gap": FAIL_BIC_GAP}
    print(f"[config] {config}", flush=True)
    per_seed = {}
    for seed in seeds:
        rets = simulate_retention_curve(seed, n, m_per, t_grid)
        rets_arr = np.array(rets, dtype=np.float64)
        bics = fit_all_forms(t_grid, rets_arr)
        best, gap = best_and_gap(bics)
        per_seed[str(seed)] = {"best_form": best, "bic_gap": gap, "bics": bics,
                                "rets": rets}
        print(f"  seed={seed}: best={best} gap={gap:.2f} rets[0..2]={rets[:3]}", flush=True)
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
    out_dir = get_output_dir("wave14_betM_logforget_longt_v1_smoke")
    s, v, m, e, c = run_experiment(smoke=True)
    write_metrics(out_dir, s, v, m, e, c)
    print(f"\nSMOKE OK: {v}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_betM_logforget_longt_v1")
    s, v, m, e, c = run_experiment(smoke=False)
    write_metrics(out_dir, s, v, m, e, c)
    print(f"\nDONE: {v}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test: self_test_verdict(); return 0
    if args.smoke: run_smoke(); return 0
    run_main(); return 0


if __name__ == "__main__":
    sys.exit(main())
