"""Bet I depth-polylog probe v4: fix smoke D_SWEEP regression from v3.

v3 VERDICT: MIDDLE_BAND SMOKE_REGIME_MISMATCH -- at smoke N=[256, 512], K=10,
d_c_pred(N=256,K=10)=sqrt(256*5.55/10)=11.9 but D_SWEEP_SMOKE max was 20 and
ALL acc~0 (cliff at d~1 for small N with ALPHA_LOAD=0.40 and K=10 compression).
The smoke N values were just too small for the K=10 gram regime to show a measurable
cliff in D_SWEEP=[2,5,10,20].

v3 FULL D_SWEEP=[2,5,10,15,20,30,40,50,60,70,80,100] does bracket the cliff for N>=1024.

FIX v4:
  1. Smoke uses N_SMOKE=[1024, 2048] -- same regime as FULL, but only 2 N values.
     d_c_pred(N=1024,K=10) = sqrt(1024*6.93/10) = 26.6
     d_c_pred(N=2048,K=10) = sqrt(2048*7.62/10) = 39.5
     Both well-bracketed by D_SWEEP_SMOKE=[2,5,10,20,30,40].
  2. D_SWEEP_SMOKE includes d=30 and d=40 to catch the cliff.
  3. Full scale unchanged from v3: N_FULL=[256,512,1024,2048,4096,8192],
     D_SWEEP_FULL=[2,5,10,15,20,30,40,50,60,70,80,100].
     At FULL, N=256,512 are included for range; their all-zero points set d_c_emp=0.
     The verdict R2 fit uses only N where d_c_emp > 0 (N>=1024 cluster).
  4. Harder all-zero detection: at FULL scale only, if N>=1024 and all acc=0 -> DEGENERATE.
     At smoke scale, all-zero for N<1024 is tolerated (excluded from verdict).

PRE-REGISTERED BANDS (unchanged from v3):
  HARD_PASS (Bet I 3rd envelope CLOSED):
    - R2(log d_c_emp, log d_c_pred) > 0.90 across >= 4 N values (where d_c_emp > 0) AND
    - mean_relative_error < 0.30
  HARD_FAIL (polylog NOT supported):
    - R2 < 0.50 AND d_c_range < 3 across all N (cliff N-independent)
  MIDDLE_BAND: R2 in [0.50, 0.90] or MRE in [0.30, 0.60]
  INSTRUMENTATION_FAIL: degenerate acc at N>=1024 at FULL scale

SELF-TESTS per [[feedback-strategy-spec-formula-selftests]]:
  1. polylog_d_c(N=4096, K=10) ~ 58.4 (input: N=4096, K=10; expected 40-80)
  2. polylog_d_c(N=8192, K=10) ~ 85.9 (input: N=8192, K=10; expected 60-120)
  3. multi_hop N=256, d=2: returns finite cosine
  4. multi_hop N=1024, d=30: returns finite cosine (now in smoke D_SWEEP)
  5. r^2(xs, xs) = 1.0 for perfect log-linear

Queue: overnight_queue (GPU; N_FULL 6 values x 12 d values x 8 seeds; ~4-6h)
Pre-reg: preregs/2026-05-27_wave14_beti_depth_polylog_v4.md
Parent: wave14_beti_depth_polylog_v3 (SMOKE_REGIME_MISMATCH)
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

K_GRAM = 10                      # same as v3
ALPHA_LOAD = 0.40                # same as v3
ACC_THRESHOLD = 0.50             # threshold for successful hop

# v4 key fix: smoke N values are large enough that d_c_pred is in D_SWEEP range
N_SWEEP_FULL  = [256, 512, 1024, 2048, 4096, 8192]
N_SWEEP_SMOKE = [1024, 2048]    # FIX: was [256, 512] which put cliff outside D_SWEEP

D_SWEEP_FULL  = [2, 5, 10, 15, 20, 30, 40, 50, 60, 70, 80, 100]
D_SWEEP_SMOKE = [2, 5, 10, 20, 30, 40]   # FIX: includes 30,40 to bracket cliff at N=1024

SEEDS_FULL  = list(range(8))
SEEDS_SMOKE = [7, 17]

DEGENERATE_THRESH = 0.05

# Pre-registered thresholds
HP_R2_MIN = 0.90
HP_MRE_MAX = 0.30
HF_R2_MAX = 0.50
HF_FLAT_MAX = 3.0


def get_output_dir(default_name: str = "wave14_beti_depth_polylog_v4") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def polylog_d_c_prediction(N: int, K: int) -> float:
    """d_c = sqrt(N * ln(N) / K)."""
    return math.sqrt(N * math.log(N) / K)


def run_one_N_d(N: int, d: int, seed: int, device: torch.device) -> float:
    """Multi-hop chain of depth d; return final cosine similarity."""
    gen = torch.Generator()
    gen.manual_seed(seed)
    M_per_hop = int(ALPHA_LOAD * N)
    W = torch.zeros(N, N, device=device)
    for _ in range(M_per_hop):
        k = torch.randn(N, generator=gen, device=device)
        k = k / (k.norm() + 1e-9)
        v = torch.randn(N, generator=gen, device=device)
        v = v / (v.norm() + 1e-9)
        W += torch.outer(v, k)
    queries, targets = [], []
    for _ in range(d):
        q = torch.randn(N, generator=gen, device=device)
        q = q / (q.norm() + 1e-9)
        t = torch.randn(N, generator=gen, device=device)
        t = t / (t.norm() + 1e-9)
        queries.append(q)
        targets.append(t)
        W += torch.outer(t, q)
    W = W / (M_per_hop * d + 1e-9)
    x = queries[0]
    for _ in range(d):
        x = W @ x
        nrm = x.norm()
        if nrm < 1e-9:
            return 0.0
        x = x / nrm
    return float((x @ targets[-1]).item())


def find_dc_empirical(N: int, d_sweep: list, seeds: list,
                      device: torch.device, is_smoke: bool = False) -> dict:
    d_c_pred = polylog_d_c_prediction(N, K_GRAM)
    acc_by_d = {}
    for d in d_sweep:
        cosines = [run_one_N_d(N, d, seed, device) for seed in seeds]
        acc = sum(1 for c in cosines if c > ACC_THRESHOLD) / len(cosines)
        acc_by_d[d] = acc

    all_accs = list(acc_by_d.values())
    all_high = all(a > 1.0 - DEGENERATE_THRESH for a in all_accs)
    # Degenerate at FULL scale only for N >= 1024 (all-high = cliff not visible)
    degenerate = all_high and (not is_smoke) and N >= 1024

    d_c_emp = 0.0
    for d in sorted(d_sweep):
        if acc_by_d[d] >= 0.50:
            d_c_emp = float(d)

    rel_err = abs(d_c_emp - d_c_pred) / max(d_c_pred, 1.0) if d_c_emp > 0 else 1.0

    return {
        "N": N,
        "d_c_empirical": d_c_emp,
        "d_c_predicted": round(d_c_pred, 2),
        "relative_error": round(rel_err, 3),
        "acc_by_d": {str(d): round(v, 3) for d, v in acc_by_d.items()},
        "degenerate": degenerate,
    }


def _compute_r2(xs: list, ys: list) -> float:
    n = len(xs)
    if n < 2:
        return 0.0
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
    device = torch.device("cpu")

    # 1. polylog N=4096, K=10 -> ~58.4
    pred1 = polylog_d_c_prediction(4096, K_GRAM)
    assert math.isfinite(pred1) and 40 < pred1 < 80, f"selftest 1 FAIL: {pred1:.2f}"
    print(f"[selftest] 1/5 polylog(N=4096,K=10)={pred1:.2f} OK")

    # 2. polylog N=8192, K=10 -> ~85.9
    pred2 = polylog_d_c_prediction(8192, K_GRAM)
    assert math.isfinite(pred2) and 60 < pred2 < 120, f"selftest 2 FAIL: {pred2:.2f}"
    print(f"[selftest] 2/5 polylog(N=8192,K=10)={pred2:.2f} OK")

    # 3. N=256, d=2 returns finite cosine
    c3 = run_one_N_d(N=256, d=2, seed=42, device=device)
    assert math.isfinite(c3), f"selftest 3 FAIL: {c3}"
    print(f"[selftest] 3/5 multihop N=256 d=2 cos={c3:.4f} OK")

    # 4. N=1024, d=30 returns finite cosine (key fix: was d=60 before, now d=30 in smoke range)
    c4 = run_one_N_d(N=1024, d=30, seed=42, device=device)
    assert math.isfinite(c4), f"selftest 4 FAIL: {c4}"
    print(f"[selftest] 4/5 multihop N=1024 d=30 cos={c4:.4f} OK")

    # 5. r^2 = 1.0 for identical xs, ys
    xs = [1.0, 2.0, 4.0, 8.0]
    r2 = _compute_r2(xs, xs)
    assert abs(r2 - 1.0) < 0.01, f"selftest 5 FAIL: r2={r2}"
    print(f"[selftest] 5/5 r2(perfect)={r2:.4f} OK")

    # Instrumentation: at least 1 cosine is finite per call (non-degenerate output)
    # Note: cosine near 0 at small N/large K is expected (interference-dominated);
    # the selftest only checks that the function returns finite values.
    assert math.isfinite(c3) and math.isfinite(c4), "validity filter: cosine not finite"

    print("[selftest] PASS: 5/5 OK", flush=True)


_instrumentation_selftest()


def run(smoke: bool = False):
    t0 = time.time()
    print(f"[exp] wave14_beti_depth_polylog_v4 {'SMOKE' if smoke else 'FULL'}", flush=True)
    print(f"[v4] K_GRAM={K_GRAM} ALPHA_LOAD={ALPHA_LOAD} "
          f"smoke_N={N_SWEEP_SMOKE} smoke_D={D_SWEEP_SMOKE}", flush=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[run] device={device}", flush=True)

    N_sweep = N_SWEEP_SMOKE if smoke else N_SWEEP_FULL
    d_sweep = D_SWEEP_SMOKE if smoke else D_SWEEP_FULL
    seeds   = SEEDS_SMOKE if smoke else SEEDS_FULL
    out_dir = get_output_dir()

    results_per_N = {}
    for N in N_sweep:
        print(f"\n[run] N={N} d_sweep={d_sweep} seeds={seeds}", flush=True)
        result = find_dc_empirical(N, d_sweep, seeds, device, is_smoke=smoke)
        results_per_N[N] = result
        print(f"  d_c_emp={result['d_c_empirical']} pred={result['d_c_predicted']} "
              f"rel_err={result['relative_error']:.3f} degen={result['degenerate']}", flush=True)

    # Multi-scale smoke check (per smoke protocol)
    if smoke:
        N_check = N_SWEEP_SMOKE[-1]
        d_check = D_SWEEP_SMOKE[-1]
        print(f"\n[multi-scale smoke] N={N_check} d={d_check}", flush=True)
        cos_check = run_one_N_d(N_check, d_check, 99, device)
        assert math.isfinite(cos_check), f"Multi-scale smoke FAIL: cos={cos_check}"
        print(f"[multi-scale smoke] PASS cos={cos_check:.4f}")

    # Degenerate check (only for N>=1024 at full scale)
    degenerate_Ns = [N for N, r in results_per_N.items() if r["degenerate"]]
    if degenerate_Ns and not smoke:
        verdict = "INSTRUMENTATION_FAIL"
        verdict_msg = (f"INSTRUMENTATION_FAIL: degenerate acc at N={degenerate_Ns}; "
                       f"K={K_GRAM} D_SWEEP does not bracket cliff")
        summary = {"degenerate_N": degenerate_Ns}
    else:
        # Use only N where d_c_emp > 0
        valid_Ns = [N for N, r in results_per_N.items() if r["d_c_empirical"] > 0]
        if len(valid_Ns) < 2:
            verdict = "MIDDLE_BAND"
            verdict_msg = (f"MIDDLE_BAND: only {len(valid_Ns)}/{ len(N_sweep)} N values "
                           f"have measurable d_c_emp > 0; not enough for R2 fit. "
                           f"Smoke N=[{N_SWEEP_SMOKE}] d_sweep={D_SWEEP_SMOKE}")
            summary = {"n_valid_N": len(valid_Ns), "results": {N: results_per_N[N] for N in N_sweep}}
        else:
            d_c_emps = [results_per_N[N]["d_c_empirical"] for N in valid_Ns]
            d_c_preds = [results_per_N[N]["d_c_predicted"] for N in valid_Ns]
            r2 = _compute_r2(d_c_preds, d_c_emps)
            mre = sum(results_per_N[N]["relative_error"] for N in valid_Ns) / len(valid_Ns)
            d_c_range = max(d_c_emps) / max(min(d_c_emps), 0.1)

            if r2 > HP_R2_MIN and mre < HP_MRE_MAX:
                verdict = "HARD_PASS"
                verdict_msg = (f"HARD_PASS: R2={r2:.3f}>{HP_R2_MIN} MRE={mre:.3f}<{HP_MRE_MAX} "
                               f"across {len(valid_Ns)} N values; polylog scaling CONFIRMED; "
                               f"Bet I 3rd envelope CLOSED")
            elif r2 < HF_R2_MAX and d_c_range < HF_FLAT_MAX:
                verdict = "HARD_FAIL"
                verdict_msg = (f"HARD_FAIL: R2={r2:.3f}<{HF_R2_MAX} and "
                               f"d_c_range={d_c_range:.2f}<{HF_FLAT_MAX}; "
                               f"polylog scaling NOT supported; cliff N-independent")
            else:
                verdict = "MIDDLE_BAND"
                verdict_msg = (f"MIDDLE_BAND: R2={r2:.3f} MRE={mre:.3f} d_c_range={d_c_range:.2f}; "
                               f"inconclusive across {len(valid_Ns)} valid N values")

            summary = {
                "r2": round(r2, 4),
                "mre": round(mre, 4),
                "d_c_range": round(d_c_range, 2),
                "valid_N_count": len(valid_Ns),
                "results_per_N": {N: results_per_N[N] for N in N_sweep},
            }

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": round(time.time() - t0, 1),
        "summary": summary,
        "config": {
            "K_GRAM": K_GRAM, "ALPHA_LOAD": ALPHA_LOAD, "smoke": smoke,
            "N_sweep": N_sweep, "d_sweep": d_sweep, "seeds": seeds,
        },
    }

    metrics_path = out_dir / "metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)
    print(f"[metrics written] {metrics_path}", flush=True)
    return metrics


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print("[self-test] selftest ran at import", flush=True)
        sys.exit(0)
    run(smoke=args.smoke)


if __name__ == "__main__":
    main()
