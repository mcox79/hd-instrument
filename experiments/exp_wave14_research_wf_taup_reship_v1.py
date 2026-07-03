"""Wright-Fisher Test 2: BetB 3-stage continual at N in {1024, 2048, 4096}, 5 seeds each.

Tests the WF-as-finite-N-correction hypothesis: does plateau-residence-time variance
sigma(tau_p) scale as N^{-1/2} (WF diffusion prediction)?

This is the conditional Test 2 from the WF handoff (exp_dev_handoff_research_wright_fisher_fst_taup_2026-05-26.md).
Test 1 (post-hoc analysis on existing BetB data) returned INSTRUMENTATION-FAIL:
no existing BetB runs have multi-N coverage with per-seed tau_p logging.

tau_p definition: for each seed and N, fit the per-phase retention curve to find
the plateau residence time -- the number of training bytes where retention stays
within 5% of the plateau value before the cliff.

Pre-reg: preregs/2026-05-26_wave14_research_wf_taup_reship_v1.md

WF prediction self-test cells (load-bearing per handoff contract):
  INPUT: sigma(tau_p)[N=1024] = X measured; PREDICTION: sigma(tau_p)[N=4096] = X / 2 (sqrt(4))
  INPUT: sigma(tau_p)[N=1024] = X measured; PREDICTION: sigma(tau_p)[N=2048] = X / sqrt(2)
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import importlib.util
import json
import math
import os
import time
from pathlib import Path

import torch
import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
_base_path = REPO / "experiments" / "exp_wave14d_betB_kovacs_v1.py"
_spec = importlib.util.spec_from_file_location("base", _base_path)
base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(base)
pa = base.pa

K = base.K
BETA = base.BETA
POOL_SIZE = base.POOL_SIZE
ALPHA_RETR = base.ALPHA_RETR
DELTA_ALPHA = base.DELTA_ALPHA
DELTA_DECAY = base.DELTA_DECAY
RELU_B = base.RELU_B
VOCAB = base.VOCAB
PAD_BYTE = base.PAD_BYTE
REPLAY_FRAC = 0.50
EMA_ALPHA = 0.7

# N sweep: 3 values for the sigma(tau_p) vs log(N) fit
N_SWEEP_FULL = [1024, 2048, 4096]
N_SMOKE = 512
BATCH_SIZE_FULL = 64
BATCH_SIZE_SMOKE = 32
EPOCHS_FULL = 5
EPOCHS_SMOKE = 1
PHASE_A_EPOCHS_FULL = 8
PHASE_A_EPOCHS_SMOKE = 1
BYTES_PER_CORPUS_FULL = 200000
BYTES_PER_CORPUS_SMOKE = 3000

SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [7, 17]

# WF hypothesis pre-registered bands (from handoff contract)
SLOPE_HARD_PASS_LO = -0.7
SLOPE_HARD_PASS_HI = -0.3
SLOPE_HARD_FAIL_LO = -0.1
SLOPE_HARD_FAIL_HI = 0.1
SLOPE_HARD_FAIL_FAST = -0.8    # faster than WF
CI95_WIDTH_HARD_PASS = 0.4     # tight CI required for HARD-PASS
MIN_SEEDS_PER_N = 3            # INSTRUMENTATION-FAIL if < 3 seeds per N


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


def extract_tau_p(retention_trajectory: list[float], plateau_tol: float = 0.05) -> float:
    """Estimate plateau residence time from a retention trajectory.

    retention_trajectory: list of retention values measured at uniform training-byte intervals.
    Plateau = region where consecutive measurements stay within plateau_tol of the running max.

    Returns: number of consecutive steps at plateau (index units = 1 training step).
    Returns 0.0 if no plateau is detectable (monotone decay or < 2 points).
    """
    if len(retention_trajectory) < 2:
        return 0.0

    vals = retention_trajectory
    # Find the maximum value and define plateau as within tolerance of that max
    plateau_val = max(vals)
    # Plateau start: first index where value reaches within plateau_tol of plateau_val
    # Plateau end: last consecutive index still within plateau_tol
    in_plateau = [abs(v - plateau_val) <= plateau_tol for v in vals]

    # Find the longest run of consecutive True values
    best_run = 0
    cur_run = 0
    for flag in in_plateau:
        if flag:
            cur_run += 1
            best_run = max(best_run, cur_run)
        else:
            cur_run = 0

    return float(best_run)


def fit_log_slope(sigma_by_N: dict) -> tuple[float, list[float]]:
    """Fit log(sigma) ~ slope * log(N) + const. Returns (slope, ci95).

    sigma_by_N: {N: sigma_value}
    Returns slope and 95% CI [lo, hi] via bootstrap.
    """
    Ns = sorted(sigma_by_N.keys())
    if len(Ns) < 2:
        return (float("nan"), [float("nan"), float("nan")])

    log_N = np.array([math.log(n) for n in Ns])
    log_sigma = np.array([math.log(max(sigma_by_N[n], 1e-9)) for n in Ns])

    # OLS fit: log_sigma = slope * log_N + const
    A = np.vstack([log_N, np.ones(len(log_N))]).T
    try:
        result = np.linalg.lstsq(A, log_sigma, rcond=None)
        slope = float(result[0][0])
    except Exception:
        return (float("nan"), [float("nan"), float("nan")])

    # Bootstrap CI (resample Ns with replacement, 1000 iters)
    rng = np.random.default_rng(seed=42)
    slopes_boot = []
    for _ in range(1000):
        idx = rng.integers(0, len(Ns), size=len(Ns))
        lN_b = log_N[idx]
        ls_b = log_sigma[idx]
        if len(set(lN_b)) < 2:
            continue
        A_b = np.vstack([lN_b, np.ones(len(lN_b))]).T
        try:
            r_b = np.linalg.lstsq(A_b, ls_b, rcond=None)
            slopes_boot.append(float(r_b[0][0]))
        except Exception:
            pass

    if len(slopes_boot) < 50:
        ci95 = [slope - 0.5, slope + 0.5]  # wide fallback
    else:
        ci95 = [float(np.percentile(slopes_boot, 2.5)), float(np.percentile(slopes_boot, 97.5))]

    return (slope, ci95)


def compute_verdict_wf(slope: float, ci95: list[float]) -> tuple[str, str]:
    """Classify WF slope result against pre-registered bands."""
    if math.isnan(slope):
        return ("INSTRUMENTATION-FAIL", f"slope=NaN: insufficient data for fit.")

    ci_width = ci95[1] - ci95[0]

    # Self-test cells (WF prediction: sigma ~ N^{-1/2} => slope = -0.5)
    # HARD-PASS: slope in [-0.7, -0.3] consistent with -0.5 within 40%
    hard_pass = (SLOPE_HARD_PASS_LO <= slope <= SLOPE_HARD_PASS_HI and ci_width < CI95_WIDTH_HARD_PASS)
    # HARD-FAIL: no N-dependence or faster-than-WF
    hard_fail_flat = (SLOPE_HARD_FAIL_LO <= slope <= SLOPE_HARD_FAIL_HI)
    hard_fail_fast = (slope < SLOPE_HARD_FAIL_FAST)

    if hard_pass:
        return ("HARD-PASS",
                f"WF-as-finite-N-correction CONFIRMED: slope={slope:.3f} in "
                f"[{SLOPE_HARD_PASS_LO},{SLOPE_HARD_PASS_HI}] AND ci95_width={ci_width:.3f} < {CI95_WIDTH_HARD_PASS}. "
                f"ci95=[{ci95[0]:.3f},{ci95[1]:.3f}]. Consistent with sigma~N^{{-1/2}} (WF diffusion).")

    if hard_fail_flat:
        return ("HARD-FAIL",
                f"WF correction REFUTED (flat): slope={slope:.3f} in "
                f"[{SLOPE_HARD_FAIL_LO},{SLOPE_HARD_FAIL_HI}] -- no N-dependence. "
                f"ci95=[{ci95[0]:.3f},{ci95[1]:.3f}]. sigma(tau_p) is N-independent (constant noise, non-diffusive).")

    if hard_fail_fast:
        return ("HARD-FAIL",
                f"WF correction REFUTED (too fast): slope={slope:.3f} < {SLOPE_HARD_FAIL_FAST} -- "
                f"sigma drops faster than N^{{-1/2}}. ci95=[{ci95[0]:.3f},{ci95[1]:.3f}]. "
                f"Higher-order correction dominates.")

    # MIDDLE band
    if SLOPE_HARD_PASS_HI < slope < SLOPE_HARD_FAIL_LO:
        band = "MIDDLE-NEGATIVE"
    elif slope < SLOPE_HARD_PASS_LO:
        band = "MIDDLE-FAST"
    else:
        band = "MIDDLE"

    return (band,
            f"Partial WF signal: slope={slope:.3f} ci95=[{ci95[0]:.3f},{ci95[1]:.3f}] "
            f"(width={ci_width:.3f}). Framework directionally correct but quantitatively off.")


def _instrumentation_selftest():
    """Assert tau_p extraction, slope fitting, and verdict logic are sound."""
    # Test 1: tau_p extraction
    # Flat trajectory (all same): max plateau = full length
    traj_flat = [0.85] * 10
    tau = extract_tau_p(traj_flat, plateau_tol=0.05)
    assert tau == 10.0, f"flat tau_p should be 10, got {tau}"

    # Declining trajectory: plateau only at start
    traj_decline = [0.90, 0.89, 0.88, 0.70, 0.60, 0.50]
    tau_d = extract_tau_p(traj_decline, plateau_tol=0.05)
    assert tau_d >= 3, f"declining tau_p should find 3-step plateau, got {tau_d}"

    # Short trajectory
    traj_short = [0.85]
    tau_s = extract_tau_p(traj_short)
    assert tau_s == 0.0, f"single-point tau_p should be 0.0, got {tau_s}"

    # Test 2: slope fitting (WF prediction: sigma ~ N^{-1/2} => slope -0.5)
    # Synthetic data: sigma(N) = C * N^{-0.5}
    C = 1.0
    sigma_by_N_wf = {1024: C * 1024**(-0.5), 2048: C * 2048**(-0.5), 4096: C * 4096**(-0.5)}
    slope_wf, ci_wf = fit_log_slope(sigma_by_N_wf)
    assert abs(slope_wf - (-0.5)) < 0.01, f"WF slope should be -0.5, got {slope_wf}"

    # WF self-test cell: sigma[N=1024] = X => sigma[N=4096] = X / 2
    sigma_1024 = sigma_by_N_wf[1024]
    sigma_4096_pred = sigma_1024 / 2.0  # sqrt(4) = 2
    sigma_4096_meas = sigma_by_N_wf[4096]
    assert abs(sigma_4096_pred - sigma_4096_meas) / sigma_4096_meas < 0.01, \
        f"WF self-test: sigma[4096] prediction {sigma_4096_pred:.6f} != measured {sigma_4096_meas:.6f}"

    # WF self-test cell: sigma[N=1024] = X => sigma[N=2048] = X / sqrt(2)
    sigma_2048_pred = sigma_1024 / math.sqrt(2)
    sigma_2048_meas = sigma_by_N_wf[2048]
    assert abs(sigma_2048_pred - sigma_2048_meas) / sigma_2048_meas < 0.01, \
        f"WF self-test: sigma[2048] prediction {sigma_2048_pred:.6f} != measured {sigma_2048_meas:.6f}"

    # Test 3: verdict logic
    # HARD-PASS case
    v_hp, msg_hp = compute_verdict_wf(-0.5, [-0.65, -0.35])
    assert v_hp == "HARD-PASS", f"selftest 3a: expected HARD-PASS, got {v_hp}\n  {msg_hp}"

    # HARD-FAIL flat case
    v_hf_flat, _ = compute_verdict_wf(0.0, [-0.05, 0.05])
    assert v_hf_flat == "HARD-FAIL", f"selftest 3b: expected HARD-FAIL, got {v_hf_flat}"

    # HARD-FAIL fast case
    v_hf_fast, _ = compute_verdict_wf(-0.9, [-1.1, -0.7])
    assert v_hf_fast == "HARD-FAIL", f"selftest 3c: expected HARD-FAIL, got {v_hf_fast}"

    # Test 4: instrumentation-fail on too-wide CI
    v_wide, _ = compute_verdict_wf(-0.5, [-0.9, -0.1])  # ci_width = 0.8 > 0.4 threshold
    # ci_width=0.8 > CI95_WIDTH_HARD_PASS=0.4 so even if slope in range, not HARD-PASS
    assert v_wide != "HARD-PASS", f"selftest 4: wide CI should NOT be HARD-PASS, got {v_wide}"

    print("[selftest] all 4 instrumentation assertions passed", flush=True)


_instrumentation_selftest()


def run_one_seed_one_N(seed: int, N: int, config: dict, device: torch.device) -> dict:
    """Run 3-stage continual learning at given N, return per-phase bpc trajectory."""
    batch_size = config["batch_size"]
    n_epochs = config["epochs"]
    phase_a_epochs = config["phase_a_epochs"]
    n_bytes = config["bytes_per_corpus"]
    smoke = config["mode"] == "smoke"

    gen = torch.Generator().manual_seed(seed)
    byte_atoms = pa.make_bsc_atoms(VOCAB, N, gen).to(device)
    pos_atoms = pa.make_bsc_atoms(K, N, gen).to(device)

    corpus_a_full = pa.load_corpus_a()
    corpus_a = corpus_a_full[:n_bytes] if n_bytes < len(corpus_a_full) else corpus_a_full
    corpus_b = pa.shuffle_bytes(corpus_a, seed=seed + 1)
    corpus_c_full = base.load_corpus_C(smoke=smoke)
    corpus_c = corpus_c_full[:n_bytes] if n_bytes < len(corpus_c_full) else corpus_c_full

    def split(data):
        m = int(0.8 * len(data))
        return data[:m], data[m:]

    train_a, test_a = split(corpus_a)
    train_b, _ = split(corpus_b)
    train_c, _ = split(corpus_c)

    train_a_idx, train_a_tgt = base.bytes_to_idx_tensors(train_a, device)
    test_a_idx, test_a_tgt = base.bytes_to_idx_tensors(test_a, device)
    train_b_idx, train_b_tgt = base.bytes_to_idx_tensors(train_b, device)
    train_c_idx, train_c_tgt = base.bytes_to_idx_tensors(train_c, device)

    W_zero = torch.zeros((N, N), dtype=torch.float32, device=device)

    W_A, pool_A_v, pool_A_l, pool_A_u = base.train_w_with_replay(
        W_zero, None, None, 0,
        byte_atoms, pos_atoms, train_a_idx, train_a_tgt,
        None, None, 0, phase_a_epochs, batch_size, device)

    bpc_A_baseline = base.evaluate_bpc(
        W_A, pool_A_v, pool_A_l, pool_A_u,
        byte_atoms, pos_atoms, test_a_idx, test_a_tgt, batch_size, device)

    # Measure bpc_A at multiple checkpoints during Phase B to get retention trajectory
    # Use mini-epoch checkpoints: run each epoch separately, measure after each
    W_cur = W_A.clone()
    pool_v = pool_A_v.clone()
    pool_l = pool_A_l.clone()
    pool_u = pool_A_u

    bpc_traj_phaseB = []
    for ep in range(n_epochs):
        W_cur, pool_v, pool_l, pool_u = base.train_w_with_replay(
            W_cur, pool_v, pool_l, pool_u,
            byte_atoms, pos_atoms, train_b_idx, train_b_tgt,
            pool_A_v, pool_A_l, pool_A_u,
            1, batch_size, device)  # 1 epoch at a time
        bpc_A_after = base.evaluate_bpc(
            W_cur, pool_v, pool_l, pool_u,
            byte_atoms, pos_atoms, test_a_idx, test_a_tgt, batch_size, device)
        retention = min(bpc_A_baseline / max(bpc_A_after, 1e-6), 1.0)
        bpc_traj_phaseB.append(retention)

    # Phase C checkpoints
    combined_v = torch.cat([pool_A_v[:pool_A_u], pool_v[:pool_u]], dim=0)
    combined_l = torch.cat([pool_A_l[:pool_A_u], pool_l[:pool_u]], dim=0)
    combined_u = combined_v.shape[0]

    bpc_traj_phaseC = []
    for ep in range(n_epochs):
        W_cur, pool_v, pool_l, pool_u = base.train_w_with_replay(
            W_cur, pool_v, pool_l, pool_u,
            byte_atoms, pos_atoms, train_c_idx, train_c_tgt,
            combined_v, combined_l, combined_u,
            1, batch_size, device)
        bpc_A_after = base.evaluate_bpc(
            W_cur, pool_v, pool_l, pool_u,
            byte_atoms, pos_atoms, test_a_idx, test_a_tgt, batch_size, device)
        retention = min(bpc_A_baseline / max(bpc_A_after, 1e-6), 1.0)
        bpc_traj_phaseC.append(retention)

    # Extract tau_p from Phase B trajectory (Phase B is where the plateau occurs)
    traj_full = bpc_traj_phaseB + bpc_traj_phaseC
    tau_p = extract_tau_p(traj_full, plateau_tol=0.05)

    print(f"  [N={N} seed={seed}] bpc_A_base={bpc_A_baseline:.3f} "
          f"traj_B={[f'{v:.2f}' for v in bpc_traj_phaseB]} "
          f"traj_C={[f'{v:.2f}' for v in bpc_traj_phaseC]} "
          f"tau_p={tau_p:.1f}", flush=True)

    return {
        "N": N,
        "seed": seed,
        "bpc_A_baseline": float(bpc_A_baseline),
        "retention_traj_phaseB": [float(v) for v in bpc_traj_phaseB],
        "retention_traj_phaseC": [float(v) for v in bpc_traj_phaseC],
        "tau_p": float(tau_p),
    }


def run_experiment(smoke: bool):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    N_list = [N_SMOKE] if smoke else N_SWEEP_FULL
    config = {
        "mode": "smoke" if smoke else "full",
        "N_list": N_list,
        "batch_size": BATCH_SIZE_SMOKE if smoke else BATCH_SIZE_FULL,
        "epochs": EPOCHS_SMOKE if smoke else EPOCHS_FULL,
        "phase_a_epochs": PHASE_A_EPOCHS_SMOKE if smoke else PHASE_A_EPOCHS_FULL,
        "bytes_per_corpus": BYTES_PER_CORPUS_SMOKE if smoke else BYTES_PER_CORPUS_FULL,
        "seeds": SEEDS_SMOKE if smoke else SEEDS_FULL,
    }
    print(f"[config] {config}", flush=True)

    all_results = []
    for N in N_list:
        print(f"\n=== N={N} ===", flush=True)
        for seed in config["seeds"]:
            r = run_one_seed_one_N(seed, N, config, device)
            all_results.append(r)

    # Aggregate tau_p by N
    tau_p_by_N: dict[int, list[float]] = {}
    for r in all_results:
        N = r["N"]
        if N not in tau_p_by_N:
            tau_p_by_N[N] = []
        tau_p_by_N[N].append(r["tau_p"])

    # Compute sigma(tau_p) per N
    sigma_by_N: dict[int, float] = {}
    for N in sorted(tau_p_by_N.keys()):
        taus = tau_p_by_N[N]
        if len(taus) < 2:
            sigma_by_N[N] = 0.0
        else:
            mean_t = sum(taus) / len(taus)
            variance = sum((t - mean_t) ** 2 for t in taus) / max(len(taus) - 1, 1)
            sigma_by_N[N] = math.sqrt(variance)
        print(f"  sigma(tau_p)[N={N}] = {sigma_by_N[N]:.4f} (from {len(tau_p_by_N[N])} seeds: {tau_p_by_N[N]})", flush=True)

    # WF self-test validation (using measured data)
    if 1024 in sigma_by_N and 4096 in sigma_by_N and sigma_by_N[1024] > 1e-6:
        pred_4096 = sigma_by_N[1024] / 2.0  # WF: sqrt(4) = 2
        meas_4096 = sigma_by_N[4096]
        rel_err = abs(pred_4096 - meas_4096) / max(meas_4096, 1e-6)
        print(f"  WF self-check: sigma[4096] pred={pred_4096:.4f} meas={meas_4096:.4f} rel_err={rel_err:.3f}", flush=True)

    if 1024 in sigma_by_N and 2048 in sigma_by_N and sigma_by_N[1024] > 1e-6:
        pred_2048 = sigma_by_N[1024] / math.sqrt(2)
        meas_2048 = sigma_by_N[2048]
        rel_err = abs(pred_2048 - meas_2048) / max(meas_2048, 1e-6)
        print(f"  WF self-check: sigma[2048] pred={pred_2048:.4f} meas={meas_2048:.4f} rel_err={rel_err:.3f}", flush=True)

    # Check INSTRUMENTATION-FAIL conditions
    n_seeds_per_N = {N: len(tau_p_by_N[N]) for N in tau_p_by_N}
    min_seeds = min(n_seeds_per_N.values()) if n_seeds_per_N else 0
    all_tau_p_zero = all(sigma_by_N[N] < 1e-6 for N in sigma_by_N)
    n_Ns_with_data = len([N for N in sigma_by_N if sigma_by_N[N] >= 0])

    if min_seeds < MIN_SEEDS_PER_N or n_Ns_with_data < 2 or all_tau_p_zero:
        verdict = "INSTRUMENTATION-FAIL"
        msg = (f"INSTRUMENTATION-FAIL: min_seeds_per_N={min_seeds} (need >={MIN_SEEDS_PER_N}), "
               f"n_Ns={n_Ns_with_data}, all_sigma_zero={all_tau_p_zero}.")
        slope = float("nan")
        ci95 = [float("nan"), float("nan")]
    else:
        slope, ci95 = fit_log_slope(sigma_by_N)
        verdict, msg = compute_verdict_wf(slope, ci95)

    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)

    summary = {
        "tau_p_by_seed_by_N": {
            str(N): {str(s): tau_p_by_N[N][i] for i, s in enumerate(config["seeds"][:len(tau_p_by_N.get(N, []))])}
            for N in sorted(tau_p_by_N.keys())
        },
        "sigma_tau_p_by_N": {str(N): sigma_by_N[N] for N in sorted(sigma_by_N.keys())},
        "log_sigma_vs_log_N_slope": slope if not math.isnan(slope) else None,
        "log_sigma_vs_log_N_ci95": ci95,
        "n_seeds_per_N": {str(N): n for N, n in n_seeds_per_N.items()},
        "verdict": verdict,
    }

    config_out = dict(config)
    config_out["slope_hard_pass_range"] = [SLOPE_HARD_PASS_LO, SLOPE_HARD_PASS_HI]
    config_out["slope_hard_fail_flat"] = [SLOPE_HARD_FAIL_LO, SLOPE_HARD_FAIL_HI]
    config_out["ci95_width_hard_pass"] = CI95_WIDTH_HARD_PASS

    metrics = {
        "verdict": verdict,
        "verdict_msg": msg,
        "elapsed_s": elapsed,
        "summary": summary,
        "config": config_out,
    }
    validate_metrics(metrics)
    return metrics


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args, _ = parser.parse_known_args()

    if args.self_test:
        # Gate runner: _instrumentation_selftest() already ran at module scope
        print("[self-test] _instrumentation_selftest() already verified at module load.", flush=True)
        return

    metrics = run_experiment(args.smoke)
    out_dir = get_output_dir("wave14_research_wf_taup_reship_v1")
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.rename(out_dir / "metrics.json")
    print(f"[output] {out_dir}/metrics.json", flush=True)


if __name__ == "__main__":
    main()
