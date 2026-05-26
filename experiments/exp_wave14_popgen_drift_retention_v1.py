"""Population genetics field probe — Wright-Fisher drift model for Bet B retention.

Field probe per research_field_scope_update_2026-05-24.md: POPULATION GENETICS
is one of the 8 new Tier-1b fields added at v195. This applies Wright-Fisher
drift dynamics to Bet B retention as a closed-form predictor.

Hypothesis: substrate's stored memory traces evolve under Hebbian Phase-B
training as a population of "alleles" (representational features) under
multinomial sampling with finite effective population size N_e (the
substrate's effective capacity). Wright-Fisher drift predicts loss-of-allele
probability after t generations as 1 - exp(-t / (2 * N_e)), which gives an
EXPONENTIAL retention curve with a SUBSTRATE-DERIVED time constant.

This is testable: measure N_e from substrate dimension N + effective rank +
load M (Cap-formula candidate from R16+R23 frameworks), predict retention(t)
in CLOSED FORM, and compare to measured Bet B retention curves.

Per [[feedback-no-experiment-design-in-prompts]]: all parameters chosen by exp_dev autonomy.
Per [[feedback-no-smoke]]: HARD-PASS / HARD-FAIL bands pre-registered.
Per [[feedback-lit-scan-calibration-penalty]]: pop-genetics for VSA retention
is uncharted regime; P estimates deflated.

Pre-reg:
    HARD-PASS: Wright-Fisher closed-form prediction tracks measured retention
               within +/-10% across >=4 of 5 time points (t in {1,5,21,55,144})
               AND fitted N_e is within [N/4, N] range (substrate-consistent).
               -> R-PRIME-1-ADJ population-genetics framing PROMOTED 🔬 -> 🟡;
               closed-form retention predictor candidate.
    HARD-FAIL: predicted vs measured deviates by > 0.25 at >=3 of 5 time
               points OR fitted N_e falls outside [N/100, 10*N] range.
               -> Wright-Fisher drift framing REJECTED.
    MIDDLE: any intermediate; report bands.

Pure-CPU; remote_cpu_queue.

Pre-reg file: preregs/2026-05-24_wave14_popgen_drift_retention_v1.md
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

T_GRID_FULL = np.array([1, 5, 21, 55, 144], dtype=np.float64)
T_GRID_SMOKE = np.array([1, 21, 55], dtype=np.float64)
N_FULL = 4096
N_SMOKE = 512
M_PER_TASK_FULL = 200
M_PER_TASK_SMOKE = 30
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

PASS_WITHIN_PCT = 0.10
PASS_MIN_TIMES = 4
PASS_NE_LO_RATIO = 0.25     # N_e >= N/4
PASS_NE_HI_RATIO = 1.0      # N_e <= N
FAIL_DEV = 0.25
FAIL_TIMES = 3
FAIL_NE_LO = 0.01           # N_e < N/100
FAIL_NE_HI = 10.0           # N_e > 10*N


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
    g = torch.Generator(device="cpu").manual_seed(seed)
    keys_A = torch.randn(m_per, n, generator=g) / math.sqrt(n)
    vals_A = torch.randn(m_per, n, generator=g) / math.sqrt(n)
    W = hebbian_W(keys_A, vals_A)
    rets = []
    max_t = int(t_grid.max())
    snapshot_at = set(int(t) for t in t_grid)
    for step in range(1, max_t + 1):
        keys_B = torch.randn(m_per, n, generator=g) / math.sqrt(n)
        vals_B = torch.randn(m_per, n, generator=g) / math.sqrt(n)
        W = W + hebbian_W(keys_B, vals_B)
        if step in snapshot_at:
            rets.append(retention(W, keys_A, vals_A))
    return np.array(rets, dtype=np.float64)


def wright_fisher_retention(t, N_e):
    """Predicted retention under Wright-Fisher drift: exp(-t / (2 N_e))."""
    return np.exp(-t / (2.0 * N_e))


def fit_N_e(t_grid, retentions):
    """Fit N_e by grid search on SSE."""
    n_grid = np.geomspace(10, 1e5, 400)
    best = (None, float("inf"))
    for ne in n_grid:
        pred = wright_fisher_retention(t_grid, ne)
        sse = float(np.sum((pred - retentions) ** 2))
        if sse < best[1]: best = (ne, sse)
    return best[0]


def compute_verdict(summary):
    per_seed = summary.get("per_seed", {})
    if not per_seed: return ("POPGEN_DRIFT_INCONCLUSIVE", "No seeds.")
    n = summary.get("n", 4096)
    n_within_pass = 0
    n_outside_fail = 0
    ne_pass_range = 0
    ne_fail_range = 0
    n_total_seeds = len(per_seed)
    ne_list = []; max_devs = []
    for s, d in per_seed.items():
        ne = d["fitted_N_e"]
        ne_list.append(ne)
        # Per-time-point check
        t_grid = d["t_grid"]
        meas = d["measured_retention"]
        pred = d["predicted_retention"]
        n_within = sum(1 for m, p in zip(meas, pred) if abs(m - p) <= PASS_WITHIN_PCT)
        n_outside = sum(1 for m, p in zip(meas, pred) if abs(m - p) > FAIL_DEV)
        if n_within >= PASS_MIN_TIMES: n_within_pass += 1
        if n_outside >= FAIL_TIMES: n_outside_fail += 1
        max_devs.append(max(abs(m - p) for m, p in zip(meas, pred)))
        # N_e range check
        if PASS_NE_LO_RATIO * n <= ne <= PASS_NE_HI_RATIO * n: ne_pass_range += 1
        if ne < FAIL_NE_LO * n or ne > FAIL_NE_HI * n: ne_fail_range += 1
    mean_ne = sum(ne_list)/len(ne_list)
    mean_max_dev = sum(max_devs)/len(max_devs)
    pts = ", ".join(f"s{s}:N_e={d['fitted_N_e']:.1f}" for s,d in per_seed.items())
    n_pass = n_within_pass
    if n_pass >= max(1, n_total_seeds - 1) and ne_pass_range >= max(1, n_total_seeds - 1):
        return ("POPGEN_DRIFT_HARD_PASS",
                f"Wright-Fisher drift TRACKS: {n_within_pass}/{n_total_seeds} seeds "
                f"within-band, mean N_e={mean_ne:.1f} (n={n}). {pts}.")
    if n_outside_fail >= max(1, n_total_seeds - 1) or ne_fail_range >= max(1, n_total_seeds - 1):
        return ("POPGEN_DRIFT_HARD_FAIL",
                f"Wright-Fisher REJECTED: {n_outside_fail}/{n_total_seeds} seeds "
                f"outside-band, max_dev={mean_max_dev:.3f}. {pts}.")
    return ("POPGEN_DRIFT_MIDDLE_BAND",
            f"Intermediate: within={n_within_pass}/{n_total_seeds}, "
            f"mean N_e={mean_ne:.1f}, mean_max_dev={mean_max_dev:.3f}. {pts}.")


def self_test_verdict():
    def mk(rows, n):
        ps = {}
        for i, (ne, meas, pred) in enumerate(rows):
            ps[str(i)] = {"fitted_N_e": ne, "t_grid": [1, 5, 21, 55, 144],
                          "measured_retention": meas, "predicted_retention": pred}
        return {"per_seed": ps, "n": n}
    tight = [0.99, 0.96, 0.85, 0.66, 0.40]
    s_pass = mk([(2000, tight, [0.997, 0.985, 0.875, 0.685, 0.420])]*5, n=4096)
    far = [0.30, 0.20, 0.10, 0.05, 0.02]
    s_fail = mk([(50000, far, [0.99, 0.95, 0.80, 0.55, 0.20])]*5, n=4096)
    # MIDDLE: only 2 of 5 time points within tight band (under PASS_MIN_TIMES=4)
    mid_meas = [0.95, 0.70, 0.60, 0.45, 0.30]
    mid_pred = [0.99, 0.97, 0.55, 0.30, 0.15]
    s_mid = mk([(1800, mid_meas, mid_pred)]*5, n=4096)
    s_inconc = {"per_seed": {}, "n": 4096}
    cases = [(s_pass, "POPGEN_DRIFT_HARD_PASS"),
             (s_fail, "POPGEN_DRIFT_HARD_FAIL"),
             (s_mid, "POPGEN_DRIFT_MIDDLE_BAND"),
             (s_inconc, "POPGEN_DRIFT_INCONCLUSIVE")]
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
    config = {"mode": "smoke" if smoke else "full", "t_grid": t_grid.tolist(),
              "n": n, "m_per": m_per, "seeds": seeds,
              "pass_within_pct": PASS_WITHIN_PCT, "pass_min_times": PASS_MIN_TIMES,
              "pass_ne_lo_ratio": PASS_NE_LO_RATIO, "pass_ne_hi_ratio": PASS_NE_HI_RATIO,
              "fail_dev": FAIL_DEV, "fail_times": FAIL_TIMES}
    print(f"[config] {config}", flush=True)
    per_seed = {}
    for seed in seeds:
        meas = simulate_retention_curve(seed, n, m_per, t_grid)
        ne = fit_N_e(t_grid, meas)
        pred = wright_fisher_retention(t_grid, ne)
        per_seed[str(seed)] = {"fitted_N_e": float(ne),
                                "t_grid": t_grid.tolist(),
                                "measured_retention": meas.tolist(),
                                "predicted_retention": pred.tolist()}
        print(f"  seed={seed}: N_e={ne:.1f} meas[0..2]={meas[:3].tolist()} pred[0..2]={pred[:3].tolist()}", flush=True)
    summary = {"per_seed": per_seed, "n": n}
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
    out_dir = get_output_dir("wave14_popgen_drift_retention_v1_smoke")
    s, v, m, e, c = run_experiment(smoke=True)
    write_metrics(out_dir, s, v, m, e, c)
    print(f"\nSMOKE OK: {v}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_popgen_drift_retention_v1")
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
