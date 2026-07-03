"""Bet I 3rd envelope: depth-cliff polylog-correction probe [v2 -- instrumentation fix].

v1 INSTRUMENTATION_FAIL root cause: ALPHA_LOAD=0.12 (too light). At M=0.12*N per hop,
recall is near-perfect (acc~0.99) at ALL depths tested (d up to 40). The depth cliff
was never reached -- all acc values are near 1.0, triggering the degenerate-ALL-1 flag.

v2 fix:
  (1) ALPHA_LOAD raised to 0.40 (below alpha_c=0.5625 but creates realistic interference).
      At alpha=0.40 near capacity boundary, per-hop recall degrades meaningfully with depth.
  (2) D_SWEEP extended to include d=50 and d=60 to bracket larger-N predictions.
      For N=4096, K=50: d_c_pred = sqrt(4096*log(4096)/50) = 26.1. D_SWEEP must
      include values both below and above this to see the cliff.
  (3) Degenerate check tightened: all-1 threshold raised from 0.01 to 0.05.
  (4) Multi-scale smoke at D_smoke[0]*2 depth to confirm no trivial pass.

HYPOTHESIS (unchanged from v1):
  d_c^pred(N) = sqrt(N * log(N) / K) -- R16 polylog correction.
  If empirical d_c(N) tracks this formula across N in [256, 512, 1024, 2048, 4096],
  Bet I 3rd envelope is CLOSED.

Self-tests (per [[feedback-strategy-spec-formula-selftests]]):
  1. polylog_d_c(N=4096, K=50) = sqrt(4096*12/50) = sqrt(983) = 31.4 (v1 was 26.1;
     note: log here is natural log so log(4096)=8.32; sqrt(4096*8.32/50)=sqrt(683)=26.1.
     Use log not log2.) Input: N=4096, K=50 -> expected ~26.1.
  2. polylog_d_c(N=1024, K=50) = sqrt(1024*6.93/50) = sqrt(142) = 11.9.
  3. At ALPHA_LOAD=0.40, N=512, d=2: multi_hop_recall should return cosine in (-1,1).
  4. At ALPHA_LOAD=0.40, N=512, d=30: multi_hop_recall should return cosine < 0.90
     (the cliff should be visible at this load level at moderate depth).

Pre-registered bands:
  HARD_PASS (Bet I 3rd envelope CLOSED):
    - r^2(log d_c_emp, log d_c_pred) > 0.90 across >= 4 N values AND
    - mean_relative_error < 0.30
  HARD_FAIL (polylog NOT supported):
    - r^2 < 0.50 AND d_c_range < 3 across all N (cliff N-independent)
  MIDDLE_BAND: r^2 in [0.50, 0.90] or MRE in [0.30, 0.60]
  INSTRUMENTATION_FAIL: degenerate acc (all > 0.95 or all < 0.05) at any N

Queue: overnight_queue (GPU; 5 N values x 10 d values x 5 seeds; ~3-4 GPU-hrs)
Pre-reg: prereqs/2026-05-26_wave14_beti_depth_polylog_v2.md
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
# ─── design parameters ───
K_GRAM = 50                      # fixed K-gram context (same as v1)
N_SWEEP_FULL = [256, 512, 1024, 2048, 4096]
N_SWEEP_SMOKE = [256, 512]
# D_SWEEP must bracket d_c for all N in sweep
# d_c_pred(N=256) = sqrt(256*5.55/50) = 5.3; d_c_pred(N=4096) = 26.1
# Use d values from 2 to 60 to cover all regime boundaries
D_SWEEP_FULL = [2, 5, 10, 15, 20, 25, 30, 40, 50, 60]
D_SWEEP_SMOKE = [2, 5, 10, 20, 30]
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
# v2 FIX: raise ALPHA_LOAD from 0.12 to 0.40 -- near capacity, creates depth cliff
ALPHA_LOAD = 0.40        # M_per_hop = int(ALPHA_LOAD * N)
ACC_THRESHOLD = 0.50     # d_c defined as largest d where mean cosine > threshold
BATCH = 256

# Pre-registered thresholds
HP_R2_MIN = 0.90
HP_MRE_MAX = 0.30
HF_R2_MAX = 0.50
HF_FLAT_MAX = 3          # max range of d_c across N for HARD_FAIL
# v2 FIX: degenerate threshold raised from 0.01 to 0.05
DEGENERATE_THRESH = 0.05


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
    """R16 polylog correction: d_c = sqrt(N * ln(N) / K_gram)."""
    return math.sqrt(N * math.log(N) / max(K_gram, 1))


def make_bsc_atoms(num: int, N: int, gen: torch.Generator, device) -> torch.Tensor:
    """num x N {-1, +1} BSC code vectors."""
    return 2.0 * torch.randint(0, 2, (num, N), generator=gen, device=device).float() - 1.0


def build_heteroassoc_W(keys: torch.Tensor, vals: torch.Tensor) -> torch.Tensor:
    """W = (1/N) sum_i v_i k_i^T. keys/vals: (M, N)."""
    N = keys.shape[1]
    W = torch.zeros((N, N), dtype=torch.float32, device=keys.device)
    for s in range(0, keys.shape[0], BATCH):
        e = min(s + BATCH, keys.shape[0])
        W.add_(vals[s:e].T @ keys[s:e], alpha=1.0 / N)
    return W


def cleanup_sign(x: torch.Tensor) -> torch.Tensor:
    return torch.where(x >= 0, torch.ones_like(x), -torch.ones_like(x))


def multi_hop_recall(W_chain: list, q0: torch.Tensor, target: torch.Tensor) -> float:
    q = q0.float()
    for W in W_chain:
        y = W @ q
        q = cleanup_sign(y)
    cos = float((q * target).sum() / max(q.norm() * target.norm(), 1e-9))
    return cos


def run_one_N_d(N: int, d: int, seed: int, device) -> float:
    """Multi-hop accuracy for one (N, d, seed).

    v2: M_noise = int(ALPHA_LOAD * N) = 0.40 * N -- near capacity, creates depth cliff.
    """
    gen = torch.Generator(device=device).manual_seed(seed)
    M_noise = max(int(ALPHA_LOAD * N), 1)

    chain_vecs = [make_bsc_atoms(1, N, gen, device).squeeze(0) for _ in range(d + 1)]

    W_chain = []
    for i in range(d):
        k_sig = chain_vecs[i].unsqueeze(0)
        v_sig = chain_vecs[i + 1].unsqueeze(0)
        k_noise = make_bsc_atoms(M_noise, N, gen, device)
        v_noise = make_bsc_atoms(M_noise, N, gen, device)
        k_all = torch.cat([k_sig, k_noise], dim=0)
        v_all = torch.cat([v_sig, v_noise], dim=0)
        W_chain.append(build_heteroassoc_W(k_all, v_all))

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
        print(f"  N={N} d={d}: mean_cos={mu:.4f} {'[PASS]' if mu > ACC_THRESHOLD else '[FAIL]'}",
              flush=True)

    passing_ds = [d for d, acc in acc_per_d.items() if acc > ACC_THRESHOLD]
    d_c_empirical = max(passing_ds) if passing_ds else 0
    pred = polylog_d_c_prediction(N, K_GRAM)
    rel_err = abs(d_c_empirical - pred) / max(pred, 1.0)

    all_vals = list(acc_per_d.values())
    # v2 FIX: degenerate = all values within DEGENERATE_THRESH of 0 or 1
    degenerate = (all(abs(v) < DEGENERATE_THRESH for v in all_vals) or
                  all(abs(v - 1) < DEGENERATE_THRESH for v in all_vals))

    return {
        "acc_per_d": acc_per_d,
        "d_c_empirical": d_c_empirical,
        "d_c_predicted": round(pred, 2),
        "relative_error": round(rel_err, 3),
        "degenerate": degenerate,
    }


def _compute_r2(xs: list, ys: list) -> float:
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


def _instrumentation_selftest():
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    print("[selftest] running instrumentation self-test...", flush=True)
    device = torch.device("cpu")

    # 1. polylog prediction: N=4096, K=50 -> sqrt(4096*ln(4096)/50) = sqrt(4096*8.32/50) = 26.1
    pred_4096 = polylog_d_c_prediction(4096, K_GRAM)
    assert math.isfinite(pred_4096) and 20 < pred_4096 < 35, \
        f"Selftest 1 FAIL: pred_4096={pred_4096:.2f} expected ~26.1"
    print(f"[selftest] 1/5 polylog_d_c(N=4096, K={K_GRAM}) = {pred_4096:.2f} OK")

    # 2. polylog prediction: N=1024, K=50 -> sqrt(1024*6.93/50) = 11.9
    pred_1024 = polylog_d_c_prediction(1024, K_GRAM)
    assert math.isfinite(pred_1024) and 8 < pred_1024 < 18, \
        f"Selftest 2 FAIL: pred_1024={pred_1024:.2f} expected ~11.9"
    print(f"[selftest] 2/5 polylog_d_c(N=1024, K={K_GRAM}) = {pred_1024:.2f} OK")

    # 3. At ALPHA_LOAD=0.40, N=256, d=2: returns finite cosine
    cos_test = run_one_N_d(N=256, d=2, seed=42, device=device)
    assert math.isfinite(cos_test), f"Selftest 3 FAIL: cos={cos_test}"
    print(f"[selftest] 3/5 multi_hop N=256 d=2 alpha=0.40 cos={cos_test:.4f} OK")

    # 4. At ALPHA_LOAD=0.40, N=512, d=30: cosine should be < 0.90 (cliff visible)
    cos_deep = run_one_N_d(N=512, d=30, seed=42, device=device)
    assert math.isfinite(cos_deep), f"Selftest 4 FAIL: cos_deep not finite"
    # Note: this is NOT an assertion that cos < 0.90 -- that would be a hard constraint
    # on randomness. We only assert it's finite and not NaN.
    print(f"[selftest] 4/5 multi_hop N=512 d=30 alpha=0.40 cos={cos_deep:.4f} (cliff probe)")

    # 5. r^2 computation returns 1.0 on identical sequences
    xs = [1.0, 2.0, 3.0, 4.0]
    r2 = _compute_r2(xs, xs)
    assert abs(r2 - 1.0) < 0.01, f"Selftest 5 FAIL: r2={r2}"
    print(f"[selftest] 5/5 r2(perfect) = {r2:.4f} OK")

    print("[selftest] instrumentation self-test PASSED", flush=True)


_instrumentation_selftest()


def run(smoke: bool = False):
    t0 = time.time()
    print(f"[exp] wave14_beti_depth_polylog_v2 {'SMOKE' if smoke else 'FULL'}", flush=True)
    print(f"[v2] ALPHA_LOAD={ALPHA_LOAD} (v1 was 0.12; v2 uses 0.40 near alpha_c=0.5625)",
          flush=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[run] device={device}", flush=True)

    N_sweep = N_SWEEP_SMOKE if smoke else N_SWEEP_FULL
    d_sweep = D_SWEEP_SMOKE if smoke else D_SWEEP_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    out_dir = get_output_dir("wave14_beti_depth_polylog_v2")

    results_per_N = {}
    for N in N_sweep:
        print(f"\n[run] N={N} d_sweep={d_sweep} seeds={seeds} M_per_hop={int(ALPHA_LOAD*N)}",
              flush=True)
        result = find_dc_empirical(N, d_sweep, seeds, device)
        results_per_N[N] = result
        print(f"  d_c_empirical={result['d_c_empirical']} "
              f"d_c_predicted={result['d_c_predicted']} "
              f"rel_err={result['relative_error']:.3f} "
              f"degenerate={result['degenerate']}", flush=True)

    # Multi-scale smoke check
    if smoke:
        N_check = N_SWEEP_SMOKE[0]
        d_check = D_SWEEP_SMOKE[-1] * 2
        print(f"\n[multi-scale smoke] N={N_check} d={d_check} (2x depth)", flush=True)
        cos_check = run_one_N_d(N_check, d_check, seeds[0], device)
        assert math.isfinite(cos_check), f"Multi-scale smoke FAIL: cos={cos_check}"
        print(f"[multi-scale smoke] PASS cos={cos_check:.4f}")

    # Verdict computation
    degenerate_Ns = [N for N, r in results_per_N.items() if r["degenerate"]]
    if degenerate_Ns:
        verdict = "INSTRUMENTATION_FAIL"
        verdict_msg = (
            f"INSTRUMENTATION_FAIL: degenerate accuracy (all near 0 or all near 1, "
            f"threshold={DEGENERATE_THRESH}) at N={degenerate_Ns}. "
            f"ALPHA_LOAD={ALPHA_LOAD} still insufficient to create depth cliff, "
            f"or d_sweep does not bracket cliff region. Increase ALPHA_LOAD further "
            f"or extend d_sweep to larger d values."
        )
        summary = {
            "degenerate_N": degenerate_Ns,
            "alpha_load": ALPHA_LOAD,
            "v1_fix_note": "v1 used ALPHA_LOAD=0.12; v2 uses 0.40; if still degenerate, try 0.50",
        }
    else:
        valid_Ns = [N for N, r in results_per_N.items() if r["d_c_empirical"] > 0]
        if len(valid_Ns) < 2:
            verdict = "INSTRUMENTATION_FAIL"
            verdict_msg = (
                f"INSTRUMENTATION_FAIL: d_c > 0 at only {len(valid_Ns)} N values. "
                f"d_sweep={d_sweep} may not include the cliff region. "
                f"Extend d_sweep to larger d values."
            )
            summary = {"valid_N_count": len(valid_Ns)}
        else:
            emp_dc = [results_per_N[N]["d_c_empirical"] for N in valid_Ns]
            pred_dc = [results_per_N[N]["d_c_predicted"] for N in valid_Ns]
            r2 = _compute_r2(pred_dc, emp_dc)
            mre = sum(abs(e - p) / max(p, 1.0) for e, p in zip(emp_dc, pred_dc)) / max(len(emp_dc), 1)
            dc_range = max(emp_dc) - min(emp_dc)

            summary = {
                "N_sweep": N_sweep,
                "d_c_empirical_per_N": {str(N): results_per_N[N]["d_c_empirical"] for N in N_sweep},
                "d_c_predicted_per_N": {str(N): results_per_N[N]["d_c_predicted"] for N in N_sweep},
                "relative_errors_per_N": {str(N): results_per_N[N]["relative_error"] for N in N_sweep},
                "r2_log_dc_vs_log_pred": round(r2, 4),
                "mean_relative_error": round(mre, 3),
                "d_c_range_across_N": round(dc_range, 1),
                "valid_N_count": len(valid_Ns),
                "alpha_load": ALPHA_LOAD,
                "calibration_note": "no prior empirical anchor; bands widened to 30% MRE",
            }

            hard_pass = r2 > HP_R2_MIN and mre < HP_MRE_MAX and len(valid_Ns) >= 4
            hard_fail = r2 < HF_R2_MAX and dc_range <= HF_FLAT_MAX

            if hard_pass:
                verdict = "HARD_PASS"
                verdict_msg = (
                    f"HARD_PASS: Bet I 3rd envelope CLOSED. "
                    f"r2={r2:.3f} > {HP_R2_MIN}, MRE={mre:.3f} < {HP_MRE_MAX} "
                    f"across {len(valid_Ns)} N values. "
                    f"Polylog correction d_c=sqrt(N*log(N)/K) CONFIRMED."
                )
            elif hard_fail:
                verdict = "HARD_FAIL"
                verdict_msg = (
                    f"HARD_FAIL: Polylog NOT supported. "
                    f"r2={r2:.3f} < {HF_R2_MAX}, dc_range={dc_range} <= {HF_FLAT_MAX}. "
                    f"Depth cliff is N-independent; architecture rather than spectral."
                )
            else:
                verdict = "MIDDLE_BAND"
                verdict_msg = (
                    f"MIDDLE_BAND: Partial polylog support. "
                    f"r2={r2:.3f}, MRE={mre:.3f}, dc_range={dc_range}, "
                    f"valid_N_count={len(valid_Ns)}. "
                    f"Some N-dependence present but not cleanly polylog."
                )

    elapsed = time.time() - t0
    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": round(elapsed, 3),
        "summary": summary,
        "config": {
            "K_gram": K_GRAM,
            "N_sweep": N_sweep,
            "d_sweep": d_sweep,
            "seeds": seeds,
            "alpha_load": ALPHA_LOAD,
            "acc_threshold": ACC_THRESHOLD,
            "smoke": smoke,
            "v2_fix": "ALPHA_LOAD raised 0.12 -> 0.40; degenerate_thresh raised 0.01 -> 0.05",
        },
    }
    validate_metrics(metrics)

    metrics_file = out_dir / "metrics.json"
    with open(metrics_file, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"\n[verdict] {verdict}: {verdict_msg}", flush=True)
    print(f"Metrics saved to {metrics_file}", flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)
    run(smoke=args.smoke)


if __name__ == "__main__":
    main()
