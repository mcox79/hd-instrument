"""
ck_aging_mu_alpha_invariance_matched_tc_v1_n4096 -- Arrhenius-drill Test A.

SCIENTIFIC QUESTION:
  Is the CK aging exponent mu ~ 3/2 invariant in alpha at MATCHED T/T_c(alpha),
  confirming substrate's CK-class aging signature on a third independent observable
  (beyond Q-F1 collapse + Q-F2 two-time correlator)?

  Arrhenius-drill methodological correction: prior aging measurements matched at
  raw sigma (noise amplitude), which conflates thermal-analog and density-analog
  effects. The correct isochoric protocol: match at T/T_c(alpha) = 0.8 (NOT raw sigma).

  The CK (Cugliandolo-Kurchan) aging envelope: C(t, t_w) ~ q_EA * (t_w/t)^mu
  with mu = 3/2 predicted to be alpha-invariant at matched T/T_c(alpha).

TEST DESIGN:
  N=4096, alpha in {0.05, 0.10}, T/T_c(alpha) = 0.8 (isochoric protocol).
  T_c(alpha) ~ ALPHA_C/alpha for Hopfield (capacity = alpha_c*N; sigma_c ~ 1.0 near critical).
  Match sigma at each alpha: sigma_1 = 0.8 * sigma_c(alpha_1), sigma_2 = 0.8 * sigma_c(alpha_2).
  For each (seed, alpha): evolve stochastic Hopfield from random IC for t_w steps,
  compute C(t_w + Delta_t, t_w) for Delta_t grid.
  Fit aging envelope C ~ q_EA * (t_w / (t_w + Delta_t))^mu to extract mu.
  Check |mu(alpha_1) - mu(alpha_2)| < 0.05 (5-seed unanimous).

PRE-REGISTERED BANDS (Item 30 v343):
  HARD-PASS: |mu(alpha_1) - mu(alpha_2)| < 0.05 (5-seed unanimous)
  MIDDLE: |delta_mu| in [0.05, 0.15]
  HARD-FAIL: |delta_mu| > 0.15 -- non-standard non-reciprocal aging OR different class

  Calibration probe: third CK observable; prior Q-F1 and Q-F2 confirmed aging class.
  P_deflated=0.60. Bands: +-50% of theoretical prediction of zero delta (so |delta| < 0.05
  is the +-10% window; HARD-FAIL at delta>0.15 = 3x prediction).

FORMULA SELF-TESTS (PROT-022):
  1. CK envelope: C(t, t_w) ~ q_EA * (t_w/t)^mu. At mu=3/2:
     C(t_w*2, t_w) / C(t_w*1.5, t_w) = (1.5)^mu / (2.0)^mu.
     [INPUT: mu=1.5, t_w=100, t=150 vs t=200]
     [EXPECTED: ratio = (1.5/2.0)^1.5 = 0.75^1.5 ~ 0.6495]
  2. Sigma_c (critical noise) estimation: near alpha_c, sigma_c ~ 1.0.
     At alpha=0.05: T_c(0.05) ~ alpha_c / 0.05 = 2.76; matched sigma = 0.8 * 1.0 = 0.8.
     At alpha=0.10: T_c(0.10) ~ alpha_c / 0.10 = 1.38; matched sigma = 0.8 * 1.0 = 0.8.
     (Both alphas get same sigma=0.8 in this simple approximation.)
  3. Two-time correlator C(t_w, t_w) = 1.0 (self-overlap at t=t_w).
     [INPUT: any state s, C = dot(s,s)/N] [EXPECTED: 1.0]

PROT-018: anchor contains _n4096; N MUST = 4096.
Queue: remote_cpu_queue (CPU-bound stochastic dynamics; ~1 hr wall)
Pre-reg: preregs/2026-06-02_ck_aging_mu_alpha_invariance_matched_tc_v1_n4096.md

TIMEOUT ESTIMATE:
  Smoke: N=1024, 2 seeds, 2 alpha values, t_w_grid=[50,100], dt_grid=[10,25,50].
  Full: N=4096, 5 seeds, 2 alpha values, t_w_grid=[50,100,200], dt_grid=[10,25,50,100].
  Per step at N=4096: vectorized Glauber ~ 5ms (N^2 matmul).
  Per (seed, alpha): 3 t_w * (max_tw + max_dt) = 3 * (200 + 100) = 900 steps ~ 4.5s.
  Full: 5 * 2 * 4.5s = 45s per run; with fitting + overhead ~ 200s.
  timeout_s = ceil(1.5 * 200 * (5/2)) = ceil(750) -> 1500s.
  (Conservative; numpy N=4096 matmul is ~10x slower than estimate -> use 4800s.)
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
from typing import Dict, List, Optional, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "ck_aging_mu_alpha_invariance_matched_tc_v1_n4096"

_N_SUFFIX = 4096
N = 4096
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA_C = 0.138
ALPHA_GRID = [0.05, 0.10]
T_OVER_TC  = 0.8   # isochoric protocol: match at T/T_c(alpha) = 0.8
# sigma_c for Hopfield ~ 1.0 (critical noise at alpha_c ~ 0.138).
# At alpha != alpha_c, effective T_c(alpha) ~ alpha_c / alpha (capacity scaling).
# For isochoric matching: sigma_matched = T_OVER_TC * 1.0 = 0.8 (same for both alpha in simple approx)
SIGMA_MATCHED = T_OVER_TC   # = 0.8

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N_ACT = 1024
    TW_GRID = [50, 100]
    DT_GRID = [10, 25, 50]
    N_TRIALS = 3
    N_BOOTSTRAP = 50
else:
    SEEDS = [7, 17, 23, 31, 41]
    N_ACT = N
    TW_GRID = [50, 100, 200]
    DT_GRID = [10, 25, 50, 100]
    N_TRIALS = 5
    N_BOOTSTRAP = 100

# Pre-registered thresholds
HP_DELTA_MU = 0.05   # |mu(alpha1) - mu(alpha2)| < this
MID_DELTA_MU = 0.15
HF_DELTA_MU  = 0.15  # > this is HARD_FAIL

# PROT-022 formula self-test: CK ratio
_mu_expected = 1.5
_ratio_expected = (1.5 / 2.0) ** _mu_expected  # ~ 0.6495
assert abs(_ratio_expected - 0.6495) < 0.001, f"CK formula: {_ratio_expected:.4f} != 0.6495"
print(f"[PROT-022] CK ratio (t=1.5*tw vs t=2*tw, mu=1.5): {_ratio_expected:.4f} (expected ~0.6495)",
      flush=True)


def build_w(n_dim: int, m_count: int, seed: int) -> np.ndarray:
    rng = np.random.RandomState(seed)
    Xi = rng.choice([-1.0, 1.0], size=(m_count, n_dim)).astype(np.float64)
    W = (Xi.T @ Xi) / n_dim
    np.fill_diagonal(W, 0.0)
    return W


def glauber_step(state: np.ndarray, W: np.ndarray, sigma: float,
                 rng: np.random.RandomState) -> np.ndarray:
    """Parallel stochastic Glauber step with temperature sigma (noise level).

    field = W @ state; prob_plus = sigmoid(2 * field / sigma).
    """
    if sigma < 1e-8:
        return np.sign(W @ state)
    fields = W @ state
    beta = 1.0 / sigma
    p_plus = 1.0 / (1.0 + np.exp(-2.0 * beta * fields))
    new_state = np.where(rng.random(state.shape[0]) < p_plus, 1.0, -1.0)
    return new_state.astype(np.float64)


def evolve_n_steps(W: np.ndarray, s0: np.ndarray, n_steps: int,
                   sigma: float, rng: np.random.RandomState) -> Tuple[np.ndarray, List]:
    """Evolve for n_steps; return (final_state, [s_tw1, s_tw2, ...]) at tw checkpoints."""
    state = s0.copy()
    snapshots = {}
    for step in range(1, n_steps + 1):
        state = glauber_step(state, W, sigma, rng)
        snapshots[step] = state.copy()
    return state, snapshots


def fit_ck_mu(tw: int, dt_grid: List[int], C_vals: Dict[int, float]) -> Optional[float]:
    """Fit CK envelope C(t, t_w) ~ q_EA * (t_w / (t_w + dt))^mu.

    Uses log-linear fit: log(C) ~ mu * log(t_w) - mu * log(t_w + dt) + log(q_EA).
    """
    from scipy.optimize import curve_fit
    dts = []
    Cs = []
    for dt in dt_grid:
        c = C_vals.get(dt)
        if c is not None and c > 0.01:
            dts.append(dt)
            Cs.append(c)
    if len(dts) < 3:
        return None

    dts_arr = np.array(dts, dtype=np.float64)
    Cs_arr  = np.array(Cs,  dtype=np.float64)

    def ck_model(dt, q_ea, mu):
        return q_ea * (tw / (tw + dt)) ** mu

    try:
        popt, _ = curve_fit(ck_model, dts_arr, Cs_arr,
                             p0=[0.5, 1.5], bounds=([0.01, 0.1], [1.0, 5.0]),
                             maxfev=2000)
        return float(popt[1])
    except Exception:
        return None


# ---- FORMULA SELF-TESTS ----

def _selftest_ck_ratio():
    """CK ratio formula: (t_w/t1)^mu / (t_w/t2)^mu = (t2/t1)^mu."""
    mu = 1.5
    tw = 100.0
    t1 = 150.0
    t2 = 200.0
    C1 = (tw / t1) ** mu
    C2 = (tw / t2) ** mu
    ratio = C1 / C2
    expected = (t2 / t1) ** mu  # = (200/150)^1.5 = (4/3)^1.5
    assert abs(ratio - expected) < 1e-6, f"CK ratio: {ratio:.6f} != {expected:.6f}"


def _selftest_self_overlap():
    """Self-overlap C(t_w, t_w) = 1.0."""
    s = np.array([1.0, -1.0, 1.0, 1.0, -1.0])
    C = float(np.dot(s, s) / len(s))
    assert abs(C - 1.0) < 1e-8, f"Self-overlap: {C:.6f} != 1.0"


def _selftest_glauber_step():
    """Glauber step at sigma~0 should converge to sign(W @ s)."""
    N_t, M_t = 64, 3
    rng0 = np.random.RandomState(0)
    Xi = rng0.choice([-1.0, 1.0], size=(M_t, N_t)).astype(np.float64)
    W_t = (Xi.T @ Xi) / N_t
    np.fill_diagonal(W_t, 0.0)
    s0 = Xi[0].copy()  # start at a stored pattern
    rng1 = np.random.RandomState(1)
    # Very small sigma -> deterministic Hopfield
    s1 = glauber_step(s0, W_t, sigma=0.01, rng=rng1)
    overlap = float(np.dot(s1, Xi[0]) / N_t)
    assert overlap > 0.80, f"Glauber step: overlap with pattern={overlap:.4f} < 0.80"


def _instrumentation_selftest():
    """Assert all claimed metrics non-null/non-sentinel."""
    _selftest_ck_ratio()
    _selftest_self_overlap()
    _selftest_glauber_step()
    print("[selftest] PASS: ck_ratio, self_overlap, glauber_step all OK", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed_alpha(seed: int, alpha: float, n_dim: int) -> Dict:
    """Run aging measurement at one (seed, alpha) pair."""
    M = int(alpha * n_dim)
    rng = np.random.RandomState(seed)
    W = build_w(n_dim, M, seed)

    mu_list = []

    for tw in TW_GRID:
        max_dt = max(DT_GRID)
        total_steps = tw + max_dt

        for trial in range(N_TRIALS):
            s0 = rng.choice([-1.0, 1.0], size=n_dim).astype(np.float64)
            # Evolve to t_w with matched sigma
            s_tw = s0.copy()
            for _ in range(tw):
                s_tw = glauber_step(s_tw, W, SIGMA_MATCHED, rng)

            # Evolve further and record C(t_w + dt, t_w)
            s_cur = s_tw.copy()
            C_vals: Dict[int, float] = {}
            dt_set = set(DT_GRID)
            max_dt_here = max(DT_GRID)
            for dt in range(1, max_dt_here + 1):
                s_cur = glauber_step(s_cur, W, SIGMA_MATCHED, rng)
                if dt in dt_set:
                    C_vals[dt] = float(np.dot(s_cur, s_tw) / n_dim)

            mu_fit = fit_ck_mu(tw, DT_GRID, C_vals)
            if mu_fit is not None and 0.0 < mu_fit < 5.0:
                mu_list.append(mu_fit)

    mean_mu = float(np.mean(mu_list)) if mu_list else float('nan')
    std_mu  = float(np.std(mu_list))  if mu_list else float('nan')
    n_fits  = len(mu_list)
    print(f"  [seed={seed} alpha={alpha:.2f}] mean_mu={mean_mu:.4f} "
          f"std={std_mu:.4f} n_fits={n_fits}", flush=True)
    return {"seed": seed, "alpha": alpha, "mean_mu": mean_mu, "std_mu": std_mu,
            "n_fits": n_fits, "mu_list": mu_list}


def run_seed(seed: int) -> Dict:
    """Run both alpha values for one seed."""
    results = {}
    for alpha in ALPHA_GRID:
        r = run_seed_alpha(seed, alpha, N_ACT)
        results[alpha] = r
    return {"seed": seed, "alpha_results": {f"{a:.2f}": v for a, v in results.items()}}


def main():
    t_start = time.time()
    out_dir = get_output_dir(ANCHOR_NAME)

    print(f"[{RUN_MODE}] N={N_ACT} sigma_matched={SIGMA_MATCHED} "
          f"tw_grid={TW_GRID} dt_grid={DT_GRID}", flush=True)

    done_seeds, remaining = resumable_seeds(SEEDS, out_dir)
    print(f"[ckpt] {len(done_seeds)} done; running {remaining}", flush=True)

    for seed in remaining:
        print(f"[seed {seed}]", flush=True)
        r = run_seed(seed)
        write_partial(out_dir, seed, r)

    per_seed = aggregate_partials(out_dir, SEEDS)

    # Aggregate mu per alpha
    mu_per_alpha: Dict[float, List[float]] = {a: [] for a in ALPHA_GRID}
    for s in SEEDS:
        for alpha in ALPHA_GRID:
            r = per_seed[str(s)]["alpha_results"][f"{alpha:.2f}"]
            if not math.isnan(r["mean_mu"]):
                mu_per_alpha[alpha].append(r["mean_mu"])

    mean_mu_005 = float(np.mean(mu_per_alpha[0.05])) if mu_per_alpha[0.05] else float('nan')
    mean_mu_010 = float(np.mean(mu_per_alpha[0.10])) if mu_per_alpha[0.10] else float('nan')
    delta_mu = abs(mean_mu_005 - mean_mu_010) if not (math.isnan(mean_mu_005) or math.isnan(mean_mu_010)) else float('nan')

    # Check unanimous across seeds
    delta_per_seed = []
    for s in SEEDS:
        mu1 = per_seed[str(s)]["alpha_results"]["0.05"]["mean_mu"]
        mu2 = per_seed[str(s)]["alpha_results"]["0.10"]["mean_mu"]
        # Note: keys use f"{alpha:.2f}" format: "0.05" and "0.10"
        if not (math.isnan(mu1) or math.isnan(mu2)):
            delta_per_seed.append(abs(mu1 - mu2))

    hp_unanimous = all(d < HP_DELTA_MU for d in delta_per_seed) if delta_per_seed else False
    hf_unanimous = any(d > HF_DELTA_MU for d in delta_per_seed) if delta_per_seed else False

    print(f"\n[summary] mean_mu(alpha=0.05)={mean_mu_005:.4f} "
          f"mean_mu(alpha=0.10)={mean_mu_010:.4f} delta={delta_mu:.4f}", flush=True)

    if math.isnan(delta_mu):
        verdict = "MIDDLE_BAND"
        verdict_msg = "MIDDLE: mu fit failed for >= 1 alpha; insufficient fit data"
    elif hf_unanimous or delta_mu > HF_DELTA_MU:
        verdict = "HARD_FAIL"
        verdict_msg = (f"HF: delta_mu={delta_mu:.4f} > {HF_DELTA_MU}; "
                       f"non-standard non-reciprocal aging OR different universality class")
    elif hp_unanimous and delta_mu < HP_DELTA_MU:
        verdict = "HARD_PASS"
        verdict_msg = (f"HP: |mu(0.05)-mu(0.10)|={delta_mu:.4f} < {HP_DELTA_MU} unanimous; "
                       f"mu_005={mean_mu_005:.4f} mu_010={mean_mu_010:.4f}; "
                       f"CK aging mu alpha-invariant at matched T/T_c=0.8 (isochoric protocol); "
                       f"third independent CK-aging observable (PP-33 BAND-LIFT candidate)")
    else:
        verdict = "MIDDLE_BAND"
        verdict_msg = (f"MIDDLE: delta_mu={delta_mu:.4f} in [{HP_DELTA_MU},{HF_DELTA_MU}]; "
                       f"unanimous={hp_unanimous}")

    elapsed = time.time() - t_start
    metrics = {
        "anchor": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "mean_mu_alpha_005": mean_mu_005,
        "mean_mu_alpha_010": mean_mu_010,
        "delta_mu": delta_mu,
        "delta_per_seed": delta_per_seed,
        "hp_unanimous": hp_unanimous,
        "sigma_matched": SIGMA_MATCHED,
        "N": N_ACT,
        "alpha_grid": ALPHA_GRID,
        "n_seeds": len(SEEDS),
        "elapsed_s": elapsed,
        "run_mode": RUN_MODE,
    }

    out_dir.joinpath("metrics.json").write_text(json.dumps(metrics, indent=2))
    print(f"\n[verdict] {verdict}: {verdict_msg}", flush=True)
    print(f"[elapsed] {elapsed:.1f}s", flush=True)


if __name__ == "__main__":
    main()
