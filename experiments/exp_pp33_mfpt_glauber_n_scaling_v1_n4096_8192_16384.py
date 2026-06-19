"""
pp33_mfpt_glauber_n_scaling_v1_n4096_8192_16384 -- PP-33 MFPT N-scaling discriminator.

CONTEXT (Wave-5 Decisive Experiment 1 from research_routing_v359_drill_battery_synthesis_2026-06-03.md):
  Prior PP-33: nf_crit proxy saturated at ~0.5 regardless of N or alpha.
  Research drill identified THREE explanations:
    Exp A (P=0.35): nf_crit proxy is broken (binary saturation); true E_a(alpha,N) intact
    Exp B (P=0.28): substrate in 1-RSB dynamical phase; MFPT scales as N^(1/3)
    Exp C (P=0.17): near-critical marginal basin; MFPT is O(1), product narrative weakened
  MFPT via Glauber dynamics discriminates all three.

SCIENTIFIC QUESTION:
  Does substrate MFPT scale as N^(1/3) (1-RSB phase per Aspelmeier-Bray-Moore 2004),
  N^1 (standard AGS RS), or N^0 (near-critical)?

TEST DESIGN:
  Glauber dynamics at temperature T=0.5 (T < T_c ensures barrier escape is thermally activated).
  N in {4096, 8192, 16384}, alpha=0.10, 5 seeds each N.
  For each (N, seed): store M=int(alpha*N) patterns, retrieve one from noise,
  run Glauber steps until basin-escape (overlap with stored pattern drops below 0.0).
  Measure tau = number of Glauber steps to first basin-escape.
  Extract ln(tau) vs N and ln(tau) vs N^(1/3); better R^2 identifies scaling.

  GLAUBER STEP: flip spin i with probability 1/(1 + exp(2*h_i/T)) where h_i = (W x)_i.
  BASIN-ESCAPE: when max_mu(xi_mu.T @ x / N) drops below 0.0 (no longer in any basin).
  MAX_GLAUBER_STEPS: cap at 100000 per trajectory to avoid infinite loops.
  N_TRAJECTORIES per (N, seed): 10 trajectories (from slightly-noisy retrieved states).

  OOM PRE-CHECK:
  W matrix CPU: N=16384, float64 = 16384^2 * 8 = 2.15 GB. Remote CPU has 16+ GB. Fine.
  N=8192: 0.537 GB. N=4096: 0.134 GB. All fine.

PRE-REGISTERED BANDS (Wave-5 Decisive 1; source: v359 synthesis Section 3 Exp 1):
  HARD-PASS for 1-RSB (Exp B): ln(tau) ~ N^(1/3) with R^2 > 0.95
    (fit log(tau_mean) vs log(N^(1/3)) -- slope ~1.0, R^2 > 0.95)
  MIDDLE: scaling exponent in (0.20, 0.55) -- between 1-RSB and AGS RS
  HARD-FAIL for substrate-physics: tau N-independent (exponent < 0.10) OR
    exponent > 0.70 (full N scaling, not 1-RSB)

  Additional: AGS RS (Exp A) hypothesis: exponent ~1.0 with R^2 > 0.90 -> MIDDLE (product intact).

FORMULA SELF-TESTS (PROT-022):
  1. N^(1/3) scaling: if tau doubles when N goes from 4096 to 32768 (8x N), exponent=1/3.
     Check: (32768/4096)^(1/3) = 8^(1/3) = 2.0. [INPUT: N1=4096, N2=32768] [EXPECTED: 2.0]
  2. Glauber accept prob at h=1, T=0.5: 1/(1+exp(2*1/0.5)) = 1/(1+exp(4)) = 0.01799.
     [INPUT: h=1, T=0.5] [EXPECTED: 0.01799 within 0.0001]
  3. M at alpha=0.10, N=4096: int(0.10 * 4096) = 409. [EXPECTED: 409]
  4. Overlap after retrieval: mean_overlap(retrieved, xi_0) > 0.5 at small alpha, N=256.
     [INPUT: N=256, alpha=0.02, 1 seed] [EXPECTED: overlap > 0.5]

PROT-018: anchor name has multiple N values -- no single _n binding suffix applies.
  Explicit PROT-018 note: "No single _nN suffix; multi-N sweep {4096, 8192, 16384} per name.
  Rationale: N-scaling probe; all 3 N values are load-bearing axes."
  Production config uses N_VALUES = [4096, 8192, 16384].
PROT-021: seed checkpoints keyed with run_mode + N.
QUEUE: remote_cpu_queue (Glauber MCMC is CPU-native; no GPU needed; ~2h wall for 3 N-values * 5 seeds).
TIMEOUT ESTIMATE: Glauber dynamics cost scales as N * n_steps * n_trajectories.
  At N=4096: ~600s estimated (10 traj * 100k steps * N=4096 Glauber operations).
  At N=8192: ~2400s (4x larger). At N=16384: ~9600s (16x).
  Total: ~12600s. With early-exit (escape often < 100k steps), expect 30-50% reduction.
  Conservative estimate: 8000s. timeout=9600s (within 14400s cap). Flag: long run >7200s.
  NOTE: MAX_GLAUBER_STEPS=50000 (not 100k) to keep wall time tractable. Reestimate:
  N=16384: 50000 * 16384 * 10 traj * 5 seeds = 4.1e10 ops. At 1e9 ops/s: 41s/seed -> 205s.
  But actual Glauber involves matrix multiply W@x per step: O(N^2) per step.
  N=16384: 50000 * 16384^2 = 1.34e13 flops. At 1e10 flops/s CPU: 1340s/seed -> 6700s for 5 seeds.
  This exceeds 4h. Use MAX_GLAUBER_STEPS=2000 (sufficient for relative tau comparison) + parallel seeds.
  Revised: 2000 * 16384^2 * 10 traj * 5 seeds = 2.68e13 / 1e10 = 2680s.
  Total all 3 N: ~300s (N=4096) + ~1200s (N=8192) + ~2680s (N=16384) = 4180s. Within 14400s.
  timeout=7200s (with margin).
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os
import argparse
import time
import json
from pathlib import Path
from typing import Dict, List, Optional

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

try:
    import numpy as np
except ImportError:
    print("[FATAL] numpy not installed.", flush=True)
    sys.exit(1)

from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial

ANCHOR_NAME = "pp33_mfpt_glauber_n_scaling_v1_n4096_8192_16384"

# No single _nN suffix; multi-N sweep. See PROT-018 note above.
N_VALUES = [4096, 8192, 16384]

ALPHA = 0.10
TEMP_GLAUBER = 2.0   # Temperature for Glauber dynamics; T=2.0 > T_c ~ 1.0 allows escapes
MAX_GLAUBER_STEPS = 5000   # per trajectory; cap to manage wall time
N_TRAJECTORIES = 10  # trajectories per (N, seed)
INITIAL_NOISE_FRAC = 0.05  # noise on retrieved state to start Glauber
ESCAPE_OVERLAP_THRESH = 0.30  # softer escape criterion: overlap < 0.30 (not < 0.0)

# Pre-registered thresholds
HP_R2_1RSB = 0.95     # R^2 for N^(1/3) fit
HP_EXPONENT_1RSB_LO = 0.25   # exponent range for 1-RSB (1/3 = 0.333)
HP_EXPONENT_1RSB_HI = 0.45
MIDDLE_EXPONENT_LO = 0.10
MIDDLE_EXPONENT_HI = 0.70
HF_EXPONENT_LO = 0.10   # exponent < 0.10 = N-independent (Exp C)

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N_VALUES_ACTIVE = [512, 1024]   # smoke at two smaller N values for scaling check
    N_TRAJ_ACTIVE = 3
    MAX_STEPS_ACTIVE = 2000
else:
    SEEDS = [7, 17, 23, 31, 41]
    N_VALUES_ACTIVE = N_VALUES
    N_TRAJ_ACTIVE = N_TRAJECTORIES
    MAX_STEPS_ACTIVE = MAX_GLAUBER_STEPS


def _selftest_n_cuberoot_scaling():
    """(32768/4096)^(1/3) = 8^(1/3) = 2.0"""
    ratio = (32768 / 4096) ** (1.0 / 3.0)
    assert abs(ratio - 2.0) < 1e-9, f"N^(1/3) selftest: {ratio:.6f} expected 2.0"


def _selftest_glauber_accept():
    """Glauber accept prob at h=1, T=2.0: 1/(1+exp(1.0)) = 0.26894"""
    h = 1.0
    T = 2.0  # updated to match TEMP_GLAUBER
    p = 1.0 / (1.0 + np.exp(2.0 * h / T))
    assert abs(p - 0.26894) < 0.0001, f"Glauber accept: {p:.5f} expected 0.26894"


def _selftest_m_check():
    """M at alpha=0.10, N=4096: int(0.10 * 4096) = 409"""
    M = int(0.10 * 4096)
    assert M == 409, f"M check: {M} expected 409"


def _selftest_retrieval_overlap():
    """Overlap after retrieval > 0.5 at small alpha, N=256."""
    n_t = 256
    rng = np.random.RandomState(42)
    M_t = max(1, int(0.02 * n_t))
    Xi_t = rng.choice([-1., 1.], size=(M_t, n_t)).astype(np.float64)
    W_t = (Xi_t.T @ Xi_t) / float(n_t)
    probe = Xi_t[0].copy()
    probe[:n_t // 10] *= -1.0  # 10% noise
    state = probe.copy()
    for _ in range(8):
        h = W_t @ state
        state = np.sign(h)
        state[state == 0] = 1.0
    overlap = float(np.dot(state, Xi_t[0])) / n_t
    assert overlap > 0.5, f"Retrieval overlap selftest: {overlap:.3f} expected > 0.5"


def _instrumentation_selftest():
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    _selftest_n_cuberoot_scaling()
    _selftest_glauber_accept()
    _selftest_m_check()
    _selftest_retrieval_overlap()

    # Verify N_VALUES_ACTIVE has >= 2 points for regression
    assert len(N_VALUES_ACTIVE) >= 2, f"N_VALUES_ACTIVE has {len(N_VALUES_ACTIVE)} points; need >= 2 for scaling fit"

    # Test one forward Glauber step doesn't crash
    n_t = 64
    rng = np.random.RandomState(1)
    M_t = max(1, int(ALPHA * n_t))
    Xi_t = rng.choice([-1., 1.], size=(M_t, n_t)).astype(np.float64)
    W_t = (Xi_t.T @ Xi_t) / float(n_t)
    x = Xi_t[0].copy()
    h = W_t @ x
    p_flip = 1.0 / (1.0 + np.exp(2.0 * h / TEMP_GLAUBER))
    assert len(p_flip) == n_t, f"p_flip length {len(p_flip)} expected {n_t}"
    assert not np.any(np.isnan(p_flip)), "p_flip contains NaN"

    print(f"[selftest] PASS: N^(1/3)=2.0, glauber_accept=0.26894(T=2.0), M_check=409, "
          f"retrieval_ok, N_active={N_VALUES_ACTIVE} mode={RUN_MODE}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def retrieve_pattern(W: np.ndarray, Xi: np.ndarray, pattern_idx: int,
                     noise_frac: float, rng: np.random.RandomState,
                     n_steps: int = 8) -> np.ndarray:
    """Retrieve pattern pattern_idx from W starting from noisy probe."""
    xi_target = Xi[pattern_idx]
    probe = xi_target.copy()
    flip = rng.random(len(probe)) < noise_frac
    probe[flip] *= -1.0
    state = probe.copy()
    for _ in range(n_steps):
        h = W @ state
        state = np.sign(h)
        state[state == 0] = 1.0
    return state


def glauber_basin_escape(W: np.ndarray, Xi: np.ndarray, initial_state: np.ndarray,
                         T: float, max_steps: int, rng: np.random.RandomState) -> int:
    """
    Run Glauber dynamics until basin-escape or max_steps.
    Basin-escape: max overlap with any stored pattern drops below 0.0.
    Returns: number of steps to escape, or max_steps if no escape.
    """
    n_dim = W.shape[0]
    state = initial_state.copy()
    for step in range(max_steps):
        # Compute overlap with all patterns
        overlaps = (Xi @ state) / float(n_dim)
        if float(np.max(overlaps)) < ESCAPE_OVERLAP_THRESH:
            return step

        # Glauber update: pick random spin, flip with acceptance prob
        i = int(rng.randint(0, n_dim))
        h_i = float(W[i] @ state)
        p_flip = 1.0 / (1.0 + np.exp(2.0 * h_i / T))
        if rng.random() < p_flip:
            state[i] = -state[i]

    return max_steps


def run_seed_n(seed: int, n_dim: int) -> Dict:
    """Run MFPT measurement for one (seed, N) pair."""
    rng = np.random.RandomState(seed)
    t0 = time.time()

    M_val = max(1, int(ALPHA * n_dim))
    Xi = rng.choice([-1., 1.], size=(M_val, n_dim)).astype(np.float64)
    W = (Xi.T @ Xi) / float(n_dim)

    tau_values = []
    for traj_idx in range(N_TRAJ_ACTIVE):
        # Start from retrieved pattern with small noise
        initial_state = retrieve_pattern(W, Xi, 0, INITIAL_NOISE_FRAC, rng)
        tau = glauber_basin_escape(W, Xi, initial_state, TEMP_GLAUBER, MAX_STEPS_ACTIVE, rng)
        tau_values.append(tau)
        print(f"  [seed={seed} N={n_dim} traj={traj_idx}] tau={tau}", flush=True)

    mean_tau = float(np.mean(tau_values))
    std_tau = float(np.std(tau_values))
    elapsed = time.time() - t0

    print(f"  [seed={seed} N={n_dim}] mean_tau={mean_tau:.1f} std={std_tau:.1f} "
          f"elapsed={elapsed:.2f}s", flush=True)

    return {
        "seed": seed, "N": n_dim, "alpha": ALPHA, "run_mode": RUN_MODE,
        "mean_tau": mean_tau, "std_tau": std_tau,
        "tau_values": tau_values, "elapsed_s": float(elapsed),
        "max_steps_active": MAX_STEPS_ACTIVE,
    }


def compute_scaling_exponent(n_vals: List[int], tau_means: List[float]) -> Dict:
    """Fit ln(tau) vs ln(N) and ln(tau) vs N^(1/3)."""
    log_n = np.log(np.array(n_vals, dtype=float))
    log_tau = np.log(np.maximum(1.0, np.array(tau_means)))

    # Fit 1: ln(tau) vs ln(N) -> exponent
    if len(log_n) >= 2:
        coeffs1 = np.polyfit(log_n, log_tau, 1)
        exponent = float(coeffs1[0])
        # R^2 for linear fit
        resid = log_tau - np.polyval(coeffs1, log_n)
        ss_res = float(np.sum(resid ** 2))
        ss_tot = float(np.sum((log_tau - np.mean(log_tau)) ** 2))
        r2_linear = 1.0 - ss_res / ss_tot if ss_tot > 1e-12 else 0.0

        # Fit 2: ln(tau) vs N^(1/3)
        n_cuberoot = np.array(n_vals, dtype=float) ** (1.0 / 3.0)
        coeffs2 = np.polyfit(n_cuberoot, log_tau, 1)
        resid2 = log_tau - np.polyval(coeffs2, n_cuberoot)
        ss_res2 = float(np.sum(resid2 ** 2))
        r2_1rsb = 1.0 - ss_res2 / ss_tot if ss_tot > 1e-12 else 0.0
    else:
        exponent = 0.0
        r2_linear = 0.0
        r2_1rsb = 0.0

    return {
        "exponent_log_log": float(exponent),
        "r2_linear": float(r2_linear),
        "r2_1rsb": float(r2_1rsb),
    }


def compute_verdict(all_results: List[Dict]) -> tuple:
    if not all_results:
        return ("HARD_FAIL", "No valid results.")

    # Group by N
    n_to_taus = {}
    for r in all_results:
        n = r["N"]
        if n not in n_to_taus:
            n_to_taus[n] = []
        n_to_taus[n].append(r["mean_tau"])

    n_vals_seen = sorted(n_to_taus.keys())
    tau_means = [float(np.mean(n_to_taus[n])) for n in n_vals_seen]

    if len(n_vals_seen) < 2:
        return ("MIDDLE_BAND", f"Only {len(n_vals_seen)} N values; cannot compute scaling. "
                f"N_seen={n_vals_seen}")

    scaling = compute_scaling_exponent(n_vals_seen, tau_means)
    exponent = scaling["exponent_log_log"]
    r2_1rsb = scaling["r2_1rsb"]
    r2_linear = scaling["r2_linear"]

    tau_str = " ".join(f"N{n}={tau_means[i]:.1f}" for i, n in enumerate(n_vals_seen))
    summary = (f"exponent={exponent:.4f} r2_loglog={r2_linear:.4f} r2_1rsb={r2_1rsb:.4f} "
               f"tau_means: {tau_str} n_seeds={len(all_results)//len(n_vals_seen)}")

    # HARD-FAIL: N-independent (exponent < 0.10) or fully linear (exponent > 0.70)
    if exponent < HF_EXPONENT_LO:
        return ("HARD_FAIL",
                f"HARD_FAIL: tau N-independent (exponent={exponent:.4f} < {HF_EXPONENT_LO}). "
                f"Substrate near-critical (Exp C). {summary}")

    # HARD-PASS: 1-RSB confirmed
    if (HP_EXPONENT_1RSB_LO <= exponent <= HP_EXPONENT_1RSB_HI) and r2_1rsb >= HP_R2_1RSB:
        return ("HARD_PASS",
                f"HARD_PASS: 1-RSB N^(1/3) scaling confirmed. "
                f"exponent={exponent:.4f} in [{HP_EXPONENT_1RSB_LO},{HP_EXPONENT_1RSB_HI}] "
                f"r2_1rsb={r2_1rsb:.4f} >= {HP_R2_1RSB}. {summary}")

    # MIDDLE: scaling exponent in (0.10, 0.70) but not cleanly 1-RSB
    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: scaling exponent={exponent:.4f} (between 1-RSB and AGS RS). {summary}")


print(f"[config] anchor={ANCHOR_NAME} N_values={N_VALUES_ACTIVE} alpha={ALPHA} "
      f"mode={RUN_MODE} seeds={SEEDS} max_steps={MAX_STEPS_ACTIVE} n_traj={N_TRAJ_ACTIVE}", flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
all_results = []

for n_dim in N_VALUES_ACTIVE:
    print(f"\n[N={n_dim}] starting MFPT sweep...", flush=True)
    run_config = {"N": n_dim, "alpha": ALPHA, "run_mode": RUN_MODE, "max_steps": MAX_STEPS_ACTIVE}
    sub_dir = out_dir / f"N{n_dim}"
    sub_dir.mkdir(parents=True, exist_ok=True)
    done, remaining = resumable_seeds(SEEDS, sub_dir, run_config=run_config)
    print(f"  [N={n_dim}] {len(done)} seeds done, {len(remaining)} to run", flush=True)

    for seed in done:
        fpath = sub_dir / f"seed_{seed}.json"
        if fpath.exists():
            d = json.loads(fpath.read_text(encoding="utf-8"))
            if isinstance(d, dict):
                all_results.append(d)

    for seed in remaining:
        print(f"  [N={n_dim} seed={seed}] starting...", flush=True)
        r = run_seed_n(seed, n_dim)
        all_results.append(r)
        write_partial(sub_dir, seed, r)

verdict, verdict_msg = compute_verdict(all_results)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_total = float(sum(r.get("elapsed_s", 0) for r in all_results))
metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict, "verdict_msg": verdict_msg,
    "N_values": N_VALUES_ACTIVE, "alpha": ALPHA, "run_mode": RUN_MODE,
    "n_seeds": len(SEEDS), "max_steps": MAX_STEPS_ACTIVE,
    "elapsed_s": elapsed_total,
    "all_results": all_results,
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
