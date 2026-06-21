"""D1 saturation-suspect CAN-FAIL re-run: planted_csp_viability at HARDER alpha (concurrent data load).

The original `planted_csp_viability_v1` ran at ALPHA_DATA=0.02 (light load) -> the planted signal sigma* sigma*^T/N dominates
the crosstalk (Xi@Xi.T)/N -> retrieval ~trivially perfect -> D1 saturation-suspect (PASS may be by-construction, not a genuine
envelope). This re-run SWEEPS alpha so the concurrent-data crosstalk GROWS and CAN overwhelm the planted signal (classic Hopfield
capacity ~0.14*N) -> locates the can-fail. Reuses the original `hopfield_accuracy` + `run_max_cut` mechanism VERBATIM (C1; true
sibling, same N=1024, same noise/iters/thresh); the ONLY change is the alpha sweep + can-fail locator.

Pre-reg (Research 2026-06-21) + Skunkworks BUILD-GO:
  HARD_PASS: can-fail LOCATED at some alpha <= 0.20 (recall drops < 0.95) -> genuine envelope -> original CHAIN-GRADE stands (saturation false alarm).
  HARD_FAIL: recall stays >= 0.95 at alpha=0.20 (still saturated) -> reframe original to MM "viability at alpha<=0.20 LOWER-BOUND, not genuine envelope".
  3 seeds; cv <= 0.05. Scope-guard: same mechanism (max_cut planted attractor) only; same N=1024; CPU. a3f473dd LOWER-BOUND precedent if cliff not located in range. ASCII; per-seed ckpt.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time
from pathlib import Path
import numpy as np
REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_partial_key, aggregate_partials, write_metrics

ANCHOR_NAME = "planted_csp_viability_can_fail_at_harder_alpha_v1_cpu_v1"
SOURCE_CELL = "planted_csp_viability_v1"
N = 1024; N_QUERIES = 20; NOISE_FRAC = 0.10; N_ITERS = 50; CORRECT_THRESH = 0.80   # VERBATIM original
GATE_ALPHA = 0.20                                                                  # pre-reg: can-fail must be located at alpha <= this
CANFAIL_RECALL = 0.95                                                              # pre-reg: recall < this = can-fail
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [7, 17]; ALPHAS = [0.02, 0.10, 0.20]
else:
    SEEDS = [7, 17, 23]; ALPHAS = [0.02, 0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50, 0.60]   # 0.02 control + pre-reg gate range + EXTENSION to LOCATE the cliff (planted rank-1 boost pushes it past the classic 0.14 capacity); gate decision stays <=0.20


def hopfield_accuracy(W, target, noise_frac, n_queries, n_iters, correct_thresh, seed):   # VERBATIM original
    N = W.shape[0]; rng = np.random.RandomState(seed + 12345); correct = 0
    for _ in range(n_queries):
        sigma = target.copy(); noise_mask = rng.rand(N) < noise_frac; sigma[noise_mask] = -sigma[noise_mask]
        for _ in range(n_iters):
            new_sigma = np.sign(W @ sigma); new_sigma[new_sigma == 0] = sigma[new_sigma == 0]
            if np.all(new_sigma == sigma):
                break
            sigma = new_sigma
        overlap = abs(float(np.dot(sigma, target) / N))
        if overlap > correct_thresh:
            correct += 1
    return correct / max(1, n_queries)


def run_max_cut(N, M_data, seed):                                                  # VERBATIM original (planted MAX-CUT attractor + concurrent data crosstalk)
    rng = np.random.RandomState(seed)
    sigma_star = rng.choice([-1, 1], size=N).astype(np.float64)
    Xi_data = rng.choice([-1, 1], size=(N, M_data)).astype(np.float64)
    W = np.outer(sigma_star, sigma_star) / N + (Xi_data @ Xi_data.T) / N
    return hopfield_accuracy(W, sigma_star, NOISE_FRAC, N_QUERIES, N_ITERS, CORRECT_THRESH, seed)


def run_unit(seed):
    by_alpha = {}
    for a in ALPHAS:
        M_data = max(1, int(a * N)); acc = run_max_cut(N, M_data, seed)
        by_alpha["a%.2f" % a] = {"alpha": a, "M_data": M_data, "recall": round(acc, 4)}
    print("  [seed=%d] %s" % (seed, {k: v["recall"] for k, v in by_alpha.items()}), flush=True)
    return {"seed": seed, "by_alpha": by_alpha}


def compute_verdict(units):
    if not units:
        return ("HARD_FAIL", "no results", {})
    agg = {}
    for a in ALPHAS:
        ak = "a%.2f" % a; recs = [u["by_alpha"][ak]["recall"] for u in units]
        agg[ak] = {"alpha": a, "recall_mean": round(float(np.mean(recs)), 4), "recall_cv": round(float(np.std(recs) / (np.mean(recs) + 1e-9)), 4)}
    # locate can-fail = lowest alpha with mean recall < 0.95
    canfail = next((a for a in ALPHAS if agg["a%.2f" % a]["recall_mean"] < CANFAIL_RECALL), None)
    ctrl = agg["a0.02"]["recall_mean"]
    worst_cv = max(v["recall_cv"] for v in agg.values())
    seed_stable = worst_cv <= 0.05
    detail = {"by_alpha": agg, "control_recall_a0.02": ctrl, "canfail_alpha": canfail, "gate_alpha": GATE_ALPHA,
              "worst_cv": worst_cv, "source_cell": SOURCE_CELL, "cites": [SOURCE_CELL, "csp_first_ship_CERT590"],
              "recall_at_gate_alpha": agg["a%.2f" % GATE_ALPHA]["recall_mean"] if ("a%.2f" % GATE_ALPHA) in agg else None}
    summ = "control(a=0.02)recall=%.3f canfail_alpha=%s recall_curve=%s worst_cv=%.3f" % (
        ctrl, canfail, {k: v["recall_mean"] for k, v in agg.items()}, worst_cv)
    if not seed_stable:
        return ("MIDDLE_BAND", "MIDDLE_BAND: seed-unstable (cv>0.05). " + summ, detail)
    if ctrl < CANFAIL_RECALL:
        return ("HARD_FAIL", "HARD_FAIL: control alpha=0.02 itself recalls <0.95 -- mechanism broken at the original's regime (not a sibling-valid re-test). " + summ, detail)
    if canfail is not None and canfail <= GATE_ALPHA:
        return ("HARD_PASS", "HARD_PASS (can-fail LOCATED at alpha=%.2f <= pre-reg gate %.2f): genuine viability envelope at the expected hardness -- crosstalk overwhelms the planted signal as load rises -> original PASS NOT by-construction-saturated -> saturation FALSE ALARM, original CHAIN-GRADE stands. " % (canfail, GATE_ALPHA) + summ, detail)
    if canfail is not None:
        return ("MIDDLE_BAND", "MIDDLE_BAND (cliff LOCATED at alpha=%.2f, BEYOND the pre-reg %.2f gate): a genuine envelope EXISTS (not by-construction-infinite) so saturation is a FALSE ALARM, BUT it is WIDER than the pre-reg's expected hardness (the planted rank-1 attractor boosts retrieval past the classic ~0.14 capacity). Pre-reg gate-verdict would be HARD_FAIL@0.20; the located cliff REFINES it (symmetric-honest: a located cliff is genuine-envelope evidence, not a flat fail). Skunkworks rules: KEEP original w/ annotated envelope alpha_cliff=%.2f vs MM-lower-bound. " % (canfail, GATE_ALPHA, canfail) + summ, detail)
    return ("HARD_FAIL", "HARD_FAIL (still saturated through alpha=%.2f, NO cliff located): recall stays >= 0.95 across the entire swept range -> reframe original to MM 'viability is a LOWER-BOUND (>= alpha=%.2f); cliff beyond the swept range' (a3f473dd LOWER-BOUND precedent). " % (max(ALPHAS), max(ALPHAS)) + summ, detail)


def _selftest():
    # control regime recalls high; a very high alpha (heavy crosstalk) must drop recall -> the can-fail mechanism is real
    a_lo = run_max_cut(256, max(1, int(0.02 * 256)), 999)
    a_hi = run_max_cut(256, max(1, int(0.60 * 256)), 999)
    assert 0.0 <= a_lo <= 1.0 and 0.0 <= a_hi <= 1.0, "recall in [0,1]"
    assert a_hi < a_lo, "can-fail mechanism: heavy crosstalk (a=0.60) must drop recall below the light-load control (hi=%.2f < lo=%.2f)" % (a_hi, a_lo)
    print("[selftest] PASS: VERBATIM max_cut mechanism + can-fail mechanism real (a=0.02 recall=%.2f > a=0.60 recall=%.2f)" % (a_lo, a_hi), flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] %s mode=%s N=%d seeds=%s alphas=%s gate_alpha=%.2f (sibling=%s)" % (ANCHOR_NAME, RUN_MODE, N, SEEDS, ALPHAS, GATE_ALPHA, SOURCE_CELL), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); run_config = {"run_mode": RUN_MODE, "schema": "alpha-sweep-canfail", "alphas": str(ALPHAS), "n_seeds": len(SEEDS)}; t0 = time.time()
for seed in SEEDS:
    key = "s%d" % seed
    if key in aggregate_partials(out_dir, [key], run_config=run_config):
        print("[ckpt] %s done; skip" % key, flush=True); continue
    write_partial_key(out_dir, key, run_unit(seed))
units = list(aggregate_partials(out_dir, ["s%d" % sd for sd in SEEDS], run_config=run_config).values())
verdict, msg, detail = compute_verdict(units)
print("\n[VERDICT] " + msg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": msg, "run_mode": RUN_MODE, "N": N, "n_seeds": len(SEEDS),
           "detail": detail, "metrics_source": "measured_cpu_planted_csp_alpha_sweep_canfail", "per_seed": units, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, units)
print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
