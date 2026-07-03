"""Bet I 3rd envelope: depth-cliff BBP polylog-correction probe.

CONTEXT:
Bet I (free probability; R16) has 2/3 envelope predictions PASSED at v56:
  P1 (M/N capacity): PASS via modern-Hopfield reframing (R29 Candidate A)
  P2 (noise tolerance sigma_c=16): EXACT MATCH (BBP sigma_c = theta_eff * sqrt(K/N))
  P3 (depth cliff d_c=25): MISS -- naive RMT predicts 7.4; substrate gets 25 (factor 3.4x)

The R16 note proposed a resolution: per-hop denoising (cleanup operator) extends
d_c by a polylog factor. Specifically:
  d_c^denoised = d_c^naive * sqrt(log^2(N) / log(N)) = 7.4 * sqrt(log(N))

For N=4096: sqrt(log(4096)) = sqrt(12) = 3.46. Prediction: d_c^pred = 7.4 * 3.46 = 25.6.
This matches the empirical d=25 within <2%.

This probe tests the polylog correction formula across MULTIPLE N VALUES:
  d_c^pred(N) = (1/sqrt(K/N)) * sqrt(log(N))
  = sqrt(N/K) * sqrt(log(N))
  = sqrt(N * log(N) / K)

If the substrate depth-cliff tracks sqrt(N * log(N) / K) across N, the polylog
correction is confirmed (Bet I 3rd envelope CLOSED). If the cliff is instead
flat or tracks sqrt(N/K) (no polylog), the correction is an artifact.

DESIGN (exp_dev autonomy):
  N_sweep: {256, 512, 1024, 2048, 4096} (5 N values)
  K = 50 (fixed; substrate's typical K-gram context)
  For each N: find d_c empirically by sweeping d in {5, 10, 15, 20, 25, 30, 40}
    and measuring multi-hop retrieval accuracy. d_c = largest d where acc > 0.5.
  Compare empirical d_c(N) to prediction sqrt(N * log(N) / K).

METRIC: r-squared of log(d_c_empirical) vs log(d_c_predicted) across N values.
  If r^2 > 0.90: polylog correction CONFIRMED.
  If r^2 < 0.50: no polylog effect; flat or pure sqrt(N/K).

PRE-REGISTERED BANDS:
  HARD_PASS (Bet I 3rd envelope CLOSED):
    - r^2(log d_c_emp, log d_c_pred) > 0.90 across >= 4 N values AND
    - mean_relative_error(d_c_emp, d_c_pred) < 0.30 (30% tolerance, generous for
      the first empirical anchor)
    -> Bet I 3rd envelope CLOSED: polylog correction confirmed

  HARD_FAIL (polylog correction NOT supported):
    - r^2 < 0.50 AND
    - d_c is flat in N (max(d_c_N) - min(d_c_N) < 3 depth steps across all N)
    -> Depth cliff is N-independent; architecture rather than spectral explanation

  MIDDLE_BAND:
    - r^2 in [0.50, 0.90] OR mean_relative_error in [0.30, 0.60]
    - Sub-linear N-dependence: some polylog effect, not fully confirmed

  INSTRUMENTATION_FAIL:
    - Acc at ALL d values is 0.0 or 1.0 (degenerate) at any N
    - OR d_c cannot be extracted (cliff not visible in d sweep)

Calibration note (no prior empirical anchor for N-sweep of d_c):
  Bands widened to 30% mean relative error per calibration-probe policy.
  "No prior empirical anchor; bands widened per calibration-probe policy."

Self-tests (per [[feedback-strategy-spec-formula-selftests]]):
  1. polylog_d_c(N=4096, K=50) = sqrt(4096 * log(4096) / 50) = sqrt(4096 * 12 / 50) ~= 31.4
     (within 30% of empirical d=25: relative error = (31.4-25)/31.4 = 0.204. OK.)
  2. polylog_d_c(N=1024, K=50) = sqrt(1024 * 10 / 50) = sqrt(204.8) ~= 14.3
  3. r^2 computable from 2+ points
  4. multi_hop_acc_at_d is non-NaN non-sentinel at tiny N/d

Queue: overnight_queue (GPU; 5 N values x ~7 d values x 5 seeds; ~3-4 GPU-hrs)
Pre-reg: prereqs/2026-05-26_wave14_beti_depth_polylog_v1.md
Parent bet: Bet I (R16 free probability) at cap_map row "theoretical grounding"
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

import torch

REPO = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
# ─── design parameters (exp_dev autonomy) ───
K = 50                          # K-gram context length (substrate standard)
N_SWEEP_FULL = [256, 512, 1024, 2048, 4096]
N_SWEEP_SMOKE = [256, 512]
D_SWEEP_FULL = [5, 10, 15, 20, 25, 30, 40]
D_SWEEP_SMOKE = [5, 10, 20]
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
# Number of noise patterns stored per hop W: alpha * N where alpha = 0.12 (below alpha_c)
# This creates realistic interference that causes the depth cliff.
# At N=4096: M_per_hop = 0.12 * 4096 = 492 items -> load well-calibrated for depth cliff
ALPHA_LOAD = 0.12        # load fraction: M_per_hop = int(ALPHA_LOAD * N)
ACC_THRESHOLD = 0.50     # d_c defined as largest d where mean cosine > threshold
BATCH = 256

# Pre-registered thresholds
HP_R2_MIN = 0.90
HP_MRE_MAX = 0.30       # mean relative error
HF_R2_MAX = 0.50
HF_FLAT_MAX = 3         # max d_sweep steps between min/max d_c across N


def get_output_dir(default_name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(default_name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d: dict) -> None:
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required: {missing}")


def polylog_d_c_prediction(N: int, K_gram: int) -> float:
    """R16 polylog correction: d_c = sqrt(N * log(N) / K_gram)."""
    return math.sqrt(N * math.log(N) / max(K_gram, 1))


# ─── BSC atoms ───

def make_bsc_atoms(num: int, N: int, gen: torch.Generator, device) -> torch.Tensor:
    """num x N {-1, +1} BSC code vectors."""
    return 2.0 * torch.randint(0, 2, (num, N), generator=gen, device=device).float() - 1.0


# ─── Multi-hop chain ───

def build_heteroassoc_W(keys: torch.Tensor, vals: torch.Tensor) -> torch.Tensor:
    """W = (1/N) sum_i v_i k_i^T. keys/vals: (M, N)."""
    N = keys.shape[1]
    W = torch.zeros((N, N), dtype=torch.float32, device=keys.device)
    for s in range(0, keys.shape[0], BATCH):
        e = min(s + BATCH, keys.shape[0])
        W.add_(vals[s:e].T @ keys[s:e], alpha=1.0 / N)
    return W


def cleanup_sign(x: torch.Tensor) -> torch.Tensor:
    """BSC cleanup: sign(x). Zeros mapped to +1."""
    return torch.where(x >= 0, torch.ones_like(x), -torch.ones_like(x))


def multi_hop_recall(W_chain: list, q0: torch.Tensor, target: torch.Tensor) -> float:
    """Traverse d-hop chain starting from q0. Return cosine(q_d, target)."""
    q = q0.float()
    N = q.shape[0]
    for W in W_chain:
        y = W @ q
        q = cleanup_sign(y)
    cos = float((q * target).sum() / max(q.norm() * target.norm(), 1e-9))
    return cos


def run_one_N_d(N: int, d: int, seed: int, device) -> float:
    """Multi-hop accuracy for one (N, d, seed): cosine of final retrieved vs target.

    Each W_i stores int(ALPHA_LOAD * N) random noise (key, value) pairs PLUS the chain
    link (q_i, q_{i+1}). ALPHA_LOAD=0.12 gives realistic load near alpha_c for BSC
    heteroassoc, producing the depth cliff at large d.
    """
    gen = torch.Generator(device=device).manual_seed(seed)
    M_noise = max(int(ALPHA_LOAD * N), 1)

    # Build d-hop chain: q_0 -> q_1 -> ... -> q_d
    chain_vecs = [make_bsc_atoms(1, N, gen, device).squeeze(0) for _ in range(d + 1)]

    # Build W matrices for each hop
    W_chain = []
    for i in range(d):
        k_sig = chain_vecs[i].unsqueeze(0)
        v_sig = chain_vecs[i + 1].unsqueeze(0)
        k_noise = make_bsc_atoms(M_noise, N, gen, device)
        v_noise = make_bsc_atoms(M_noise, N, gen, device)
        k_all = torch.cat([k_sig, k_noise], dim=0)
        v_all = torch.cat([v_sig, v_noise], dim=0)
        W_chain.append(build_heteroassoc_W(k_all, v_all))

    # Traverse chain from q_0 to q_d
    q0 = chain_vecs[0]
    target = chain_vecs[d]
    cos = multi_hop_recall(W_chain, q0, target)
    return cos


def find_dc_empirical(N: int, d_sweep: list, seeds: list, device) -> dict:
    """Find empirical d_c for given N: largest d where mean cosine > ACC_THRESHOLD."""
    acc_per_d = {}
    for d in d_sweep:
        accs = []
        for seed in seeds:
            cos = run_one_N_d(N, d, seed, device)
            accs.append(cos)
        mu = sum(accs) / len(accs)
        acc_per_d[d] = round(mu, 4)
        print(f"  N={N} d={d}: mean_cos={mu:.4f} {'[PASS]' if mu > ACC_THRESHOLD else '[FAIL]'}", flush=True)

    # d_c: largest d where acc > threshold
    passing_ds = [d for d, acc in acc_per_d.items() if acc > ACC_THRESHOLD]
    d_c_empirical = max(passing_ds) if passing_ds else 0
    pred = polylog_d_c_prediction(N, K)
    rel_err = abs(d_c_empirical - pred) / max(pred, 1.0)

    # Check for instrumentation fail (all acc = 0 or all = 1)
    all_vals = list(acc_per_d.values())
    degenerate = all(abs(v) < 0.01 for v in all_vals) or all(abs(v - 1) < 0.01 for v in all_vals)

    return {
        "acc_per_d": acc_per_d,
        "d_c_empirical": d_c_empirical,
        "d_c_predicted": round(pred, 2),
        "relative_error": round(rel_err, 3),
        "degenerate": degenerate,
    }


# ─── Instrumentation self-test ───

def _instrumentation_selftest():
    """Assert metrics are non-null at smoke scale."""
    print("[selftest] running instrumentation self-test...", flush=True)
    device = torch.device("cpu")

    # 1. polylog prediction at N=4096
    pred_4096 = polylog_d_c_prediction(4096, K)
    assert math.isfinite(pred_4096) and pred_4096 > 0, f"Selftest 1 FAIL: pred={pred_4096}"
    print(f"[selftest] 1/5 polylog_d_c(N=4096, K={K}) = {pred_4096:.2f} (empirical d=25) OK")

    # 2. polylog prediction at N=1024
    pred_1024 = polylog_d_c_prediction(1024, K)
    assert math.isfinite(pred_1024) and pred_1024 > 0, f"Selftest 2 FAIL: pred={pred_1024}"
    print(f"[selftest] 2/5 polylog_d_c(N=1024, K={K}) = {pred_1024:.2f} OK")

    # 3. multi-hop at N=256 (M_noise=30), d=2 returns finite cosine
    cos_test = run_one_N_d(N=256, d=2, seed=42, device=device)
    assert math.isfinite(cos_test), f"Selftest 3 FAIL: cos={cos_test}"
    print(f"[selftest] 3/5 multi_hop_recall N=256 d=2 cos={cos_test:.4f} OK")

    # 4. r^2 computation: r^2([1,2,3,4], [1,2,3,4]) = 1.0
    xs = [1.0, 2.0, 3.0, 4.0]
    r2 = _compute_r2(xs, xs)
    assert abs(r2 - 1.0) < 0.01, f"Selftest 4 FAIL: r2={r2}"
    print(f"[selftest] 4/5 r2(perfect) = {r2:.4f} OK")

    # 5. find_dc_empirical runs at N=256 without NaN
    result = find_dc_empirical(N=256, d_sweep=[2, 5], seeds=[42], device=device)
    assert result["d_c_empirical"] >= 0, f"Selftest 5 FAIL: d_c={result['d_c_empirical']}"
    print(f"[selftest] 5/5 find_dc_empirical N=256 d_c={result['d_c_empirical']} OK")
    print("[selftest] instrumentation self-test PASSED", flush=True)


def _compute_r2(xs: list, ys: list) -> float:
    """R-squared of linear regression log(x) vs log(y)."""
    n = len(xs)
    if n < 2:
        return float("nan")
    lx = [math.log(max(x, 1e-9)) for x in xs]
    ly = [math.log(max(y, 1e-9)) for y in ys]
    mu_lx = sum(lx) / n
    mu_ly = sum(ly) / n
    ss_tot = sum((v - mu_ly) ** 2 for v in ly)
    if ss_tot < 1e-12:
        return 1.0
    num = sum((lx[i] - mu_lx) * (ly[i] - mu_ly) for i in range(n))
    den_x = sum((v - mu_lx) ** 2 for v in lx)
    den_y = ss_tot
    if den_x < 1e-12 or den_y < 1e-12:
        return 0.0
    r = num / math.sqrt(den_x * den_y)
    return r ** 2


_instrumentation_selftest()


# ─── Main run ───

def run(smoke: bool = False):
    t0 = time.time()
    print(f"[exp] wave14_beti_depth_polylog_v1 {'SMOKE' if smoke else 'FULL'}", flush=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[run] device={device}", flush=True)

    N_sweep = N_SWEEP_SMOKE if smoke else N_SWEEP_FULL
    d_sweep = D_SWEEP_SMOKE if smoke else D_SWEEP_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    out_dir = get_output_dir("wave14_beti_depth_polylog_v1")

    results_per_N = {}
    for N in N_sweep:
        print(f"\n[run] N={N}, d_sweep={d_sweep}, seeds={seeds}", flush=True)
        result = find_dc_empirical(N, d_sweep, seeds, device)
        results_per_N[N] = result
        print(f"  d_c_empirical={result['d_c_empirical']}, "
              f"d_c_predicted={result['d_c_predicted']}, "
              f"rel_err={result['relative_error']:.3f}", flush=True)

    # Multi-scale smoke check: run N_smoke[0] at d * 2 to check no overflow
    if smoke:
        N_check = N_SWEEP_SMOKE[0]
        d_check = D_SWEEP_SMOKE[-1] * 2
        print(f"\n[multi-scale smoke] N={N_check} d={d_check} (2x depth)", flush=True)
        cos_check = run_one_N_d(N_check, d_check, seeds[0], device)
        assert math.isfinite(cos_check), f"Multi-scale smoke FAIL: cos={cos_check}"
        print(f"[multi-scale smoke] PASS cos={cos_check:.4f}")

    # Check instrumentation fail
    degenerate_Ns = [N for N, r in results_per_N.items() if r["degenerate"]]
    if degenerate_Ns:
        verdict = "INSTRUMENTATION_FAIL"
        verdict_msg = (
            f"INSTRUMENTATION_FAIL: degenerate accuracy (all 0 or all 1) at N={degenerate_Ns}. "
            f"Multi-hop chain construction or retrieval is broken. "
            f"Check BSC dimensionality and d-range."
        )
        summary = {"degenerate_N": degenerate_Ns}
    else:
        # Compute r^2 across N values
        valid_Ns = [N for N, r in results_per_N.items() if r["d_c_empirical"] > 0]
        if len(valid_Ns) < 2:
            verdict = "INSTRUMENTATION_FAIL"
            verdict_msg = (
                f"INSTRUMENTATION_FAIL: d_c > 0 at only {len(valid_Ns)} N values. "
                f"Cannot compute N-scaling. d-sweep may not include the cliff region."
            )
            summary = {}
        else:
            emp_dc = [results_per_N[N]["d_c_empirical"] for N in valid_Ns]
            pred_dc = [results_per_N[N]["d_c_predicted"] for N in valid_Ns]
            r2 = _compute_r2(pred_dc, emp_dc)
            mre = sum(abs(e - p) / max(p, 1.0)
                      for e, p in zip(emp_dc, pred_dc)) / max(len(emp_dc), 1)
            dc_range = max(emp_dc) - min(emp_dc)

            summary = {
                "N_sweep": N_sweep,
                "d_c_empirical_per_N": {N: results_per_N[N]["d_c_empirical"] for N in N_sweep},
                "d_c_predicted_per_N": {N: results_per_N[N]["d_c_predicted"] for N in N_sweep},
                "relative_errors_per_N": {N: results_per_N[N]["relative_error"] for N in N_sweep},
                "r2_log_dc_vs_log_pred": round(r2, 4),
                "mean_relative_error": round(mre, 3),
                "d_c_range_across_N": round(dc_range, 1),
                "valid_N_count": len(valid_Ns),
                "calibration_note": "no prior empirical anchor; bands widened to 30% MRE per calibration-probe policy",
            }

            hard_pass = (
                r2 > HP_R2_MIN and
                mre < HP_MRE_MAX and
                len(valid_Ns) >= 4
            )
            hard_fail = (
                r2 < HF_R2_MAX and
                dc_range <= HF_FLAT_MAX
            )

            if hard_pass:
                verdict = "HARD_PASS"
                verdict_msg = (
                    f"HARD_PASS: Bet I 3rd envelope CLOSED. "
                    f"r2(log d_c_emp vs log d_c_pred) = {r2:.3f} > {HP_R2_MIN}, "
                    f"mean_relative_error = {mre:.3f} < {HP_MRE_MAX} "
                    f"across {len(valid_Ns)} N values. "
                    f"Polylog correction d_c = sqrt(N * log(N) / K) is CONFIRMED. "
                    f"Bet I free-probability framework closes all 3 envelopes."
                )
            elif hard_fail:
                verdict = "HARD_FAIL"
                verdict_msg = (
                    f"HARD_FAIL: Polylog correction NOT supported. "
                    f"r2 = {r2:.3f} < {HF_R2_MAX} AND d_c range = {dc_range:.1f} steps < {HF_FLAT_MAX}. "
                    f"Depth cliff is N-independent; polylog explanation is wrong. "
                    f"Bet I 3rd envelope remains OPEN; alternative explanation needed."
                )
            else:
                verdict = "MIDDLE_BAND"
                verdict_msg = (
                    f"MIDDLE_BAND: Partial polylog support. "
                    f"r2 = {r2:.3f}, mean_relative_error = {mre:.3f}, "
                    f"d_c range = {dc_range:.1f} across N values. "
                    f"Some N-dependence present but not cleanly polylog. "
                    f"Recommend higher N-resolution or larger d-sweep."
                )

    print(f"\nVerdict: {verdict}")
    print(f"Msg: {verdict_msg}")

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": round(time.time() - t0, 3),
        "summary": summary,
        "per_N_details": {str(N): results_per_N[N] for N in results_per_N},
        "config": {
            "K": K,
            "N_sweep": N_sweep,
            "d_sweep": d_sweep,
            "seeds": seeds,
            "ACC_THRESHOLD": ACC_THRESHOLD,
            "smoke": smoke,
            "hypothesis": "d_c = sqrt(N * log(N) / K) per R16 polylog correction",
            "parent_bet": "Bet I (R16 free probability) 3rd envelope",
        },
    }
    validate_metrics(metrics)

    out_file = out_dir / "metrics.json"
    with open(out_file, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Metrics saved to {out_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        # _instrumentation_selftest() already called at module level; just exit 0
        sys.exit(0)
    run(smoke=args.smoke)
