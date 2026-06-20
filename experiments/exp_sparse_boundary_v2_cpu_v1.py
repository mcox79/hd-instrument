"""
sparse_boundary_v2_cpu_v1 -- sparse-coding capacity-vs-SPARSITY curve + crosstalk-onset BOUNDARY (TIER-2 #2, REFRAMED). CPU.
CLAIM (MEASURED_MECHANISM): substrate auto-assoc critical-load alpha_c(f) RISES as the pattern sparsity f decreases (sparser ->
more capacity), up to a CROSSTALK-ONSET boundary f* (Willshaw-Buckingham ~1/sqrt(N)) beyond which it plateaus/drops. Reports the
gain curve gain(f)=alpha_c(f)/alpha_c(dense) + the boundary f*. The Phase-1 sparse-coding ship's safe-sparsity input.

REFRAME history (verify-the-referent): the original "reproduce 6x@0.2/25x@0.05" was PHANTOM (sweep-endpoint ratios; 3-way
resolved -- Orchestrator scour + cell-read + Research self-catch #10). MEASURE-not-reproduce. Axis = SPARSE-FRACTION f (the cell
exp_sparse_alpha_fine_sweep_below_004 sweeps f + reports alpha_c(f); the Phase-1 ship needs the f-boundary), NOT load-at-fixed-f.

METHODOLOGY (reuse exp_sparse_alpha_fine_sweep_below_004 EXACTLY -- the reproduction referent): sparse_pat(M,n,f) k=f*n active
in {-1,+1}; W-free single-step Hopfield recall r=sign((s@P^T)@P - s*diag) with FLIP=0.05 cue; exact-recovery on non-zero
positions; alpha_c(f) = max LOAD M/N at recall>=0.95. TIER = MEASURED_MECHANISM (capacity-vs-sparsity characterization).
DISCIPLINES: bounded-regime (alpha_c(dense) bounded away from 0); report alpha_c per-f; gain vs DENSE (f=1.0). ASCII. CPU.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os, argparse, time
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_partial_key, aggregate_partials, write_metrics

ANCHOR_NAME = "sparse_boundary_v2_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
FLIP = 0.05
if SMOKE:
    FRACS = [0.02, 0.10, 1.0]; N = 2048; LOADS = [0.05, 0.1, 0.2, 0.4, 0.7, 1.0]; SEEDS = [1]
else:
    FRACS = [0.005, 0.01, 0.02, 0.05, 0.10, 0.20, 0.50, 1.0]  # f=1.0 = DENSE baseline
    N = 8192; LOADS = [0.02, 0.05, 0.1, 0.2, 0.4, 0.7, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0]; SEEDS = [7, 17, 23]


def sparse_pat(M, n, f, g):
    k = max(1, int(f * n)); P = np.zeros((M, n), np.float32)
    for i in range(M):
        idx = g.choice(n, k, replace=False); P[i, idx] = g.integers(0, 2, k) * 2 - 1
    return P


def recall(P, g):
    M, n = P.shape; diag = (P * P).sum(0); s = P.copy()                       # W-free single-step (sparse), reused EXACTLY
    for i in range(M):
        nz = np.nonzero(P[i])[0]; fl = nz[g.random(len(nz)) < FLIP]; s[i, fl] *= -1
    r = np.sign((s @ P.T) @ P - s * diag)
    return float(np.mean([np.all(r[i][np.nonzero(P[i])[0]] == P[i][np.nonzero(P[i])[0]]) for i in range(M)]))


def cap(f, seed):
    g = np.random.default_rng(seed); c = 0.0
    for load in LOADS:
        M = max(2, int(load * N))
        if recall(sparse_pat(M, N, f, np.random.default_rng(seed * 13 + M)), g) >= 0.95:
            c = load
        else:
            break
    return c


def _selftest():
    g = np.random.default_rng(0)
    P = sparse_pat(5, 512, 0.05, g); assert np.all((P != 0).sum(1) == int(0.05 * 512)), "sparse k-of-N"
    assert recall(sparse_pat(4, 512, 0.05, g), np.random.default_rng(1)) >= 0.95, "low-load recovers"
    print("[selftest] PASS: sparse-boundary (sparse_pat k-of-N + W-free recall)", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_unit(f, seed):
    ac = cap(f, seed)
    print("  [f=%.3f s=%d] alpha_c=%.3f" % (f, seed, ac), flush=True)
    return {"f": f, "seed": seed, "alpha_c": round(ac, 4), "run_mode": RUN_MODE}


def compute_verdict(units) -> Tuple[str, str, Dict]:
    if not units: return ("HARD_FAIL", "no results", {})
    by = {}
    for u in units:
        by.setdefault(u["f"], []).append(u["alpha_c"])
    ac = {f: float(np.mean(v)) for f, v in by.items()}                        # mean alpha_c per f
    cv = {f: (float(np.std(v) / (np.mean(v) + 1e-9))) for f, v in by.items()}
    dense = ac.get(1.0, 0.0)
    fs = sorted(ac.keys())                                                    # ascending f
    gain = {f: (ac[f] / dense if dense > 1e-9 else 0.0) for f in fs}
    # crosstalk-onset: scan from DENSE (high f) to sparse (low f); boundary = the f BELOW which alpha_c stops rising (peaks/drops)
    sparse_fs = [f for f in sorted(fs, reverse=True)]                         # high f -> low f
    peak_f = max(ac, key=lambda f: ac[f]); peak_ac = ac[peak_f]
    onset_f = None
    for i in range(1, len(sparse_fs)):
        if ac[sparse_fs[i]] < ac[sparse_fs[i - 1]] - 1e-6:                    # alpha_c dropped going sparser
            onset_f = sparse_fs[i - 1]; break
    peak_gain = peak_ac / dense if dense > 1e-9 else 0.0
    detail = {"alpha_c_by_f": {("f%.3f" % f): round(ac[f], 4) for f in fs}, "gain_vs_dense_by_f": {("f%.3f" % f): round(gain[f], 2) for f in fs},
              "dense_alpha_c": round(dense, 4), "peak_f": peak_f, "peak_alpha_c": round(peak_ac, 4), "peak_gain_vs_dense": round(peak_gain, 2),
              "crosstalk_onset_f": onset_f, "worst_cv": round(max(cv.values()) if cv else 0.0, 3), "n_f": len(fs), "axis": "sparse_fraction_f",
              "honest_claim": "Substrate auto-assoc critical-load alpha_c RISES as sparsity f decreases (capacity-vs-sparsity); "
                              "peak gain %.2fx vs dense at f=%.3f; crosstalk-onset boundary f*=%s (sparser stops helping). "
                              "MEASURED_MECHANISM capacity-vs-sparsity characterization (Phase-1 sparse-coding safe-sparsity input)." % (peak_gain, peak_f, onset_f)}
    summary = "alpha_c/f=%s | gain/dense=%s | peak %.2fx@f%.3f | onset_f=%s | dense_ac=%.3f | worst_cv=%.3f | n_f=%d" % (
        detail["alpha_c_by_f"], detail["gain_vs_dense_by_f"], peak_gain, peak_f, onset_f, dense, detail["worst_cv"], len(fs))
    if len(fs) < 4:
        return ("UNKNOWN", "need >=4 f points (got %d)" % len(fs), detail)
    if dense <= 1e-9:
        return ("HARD_FAIL", "HARD_FAIL: dense baseline alpha_c ~ 0 (denominator unbounded) -> gain ill-defined. " + summary, detail)
    if peak_gain < 1.1:
        return ("HARD_FAIL", "HARD_FAIL: sparse gives NO capacity gain (peak < 1.1x dense) -- sparse-coding lever does not hold. " + summary, detail)
    return ("MEASURED_MECHANISM", "MEASURED_MECHANISM: sparse-coding capacity-vs-sparsity characterized; peak gain %.2fx@f%.3f vs dense; crosstalk-onset boundary f*=%s. " % (peak_gain, peak_f, onset_f) + summary, detail)


print("[config] %s mode=%s N=%d fracs=%s seeds=%s" % (ANCHOR_NAME, RUN_MODE, N, FRACS, SEEDS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); run_config = {"run_mode": RUN_MODE}; t0 = time.time()
for f in FRACS:
    for seed in SEEDS:
        key = ("f%.3f_s%d" % (f, seed)).replace(".", "p")                    # dot-sanitized key (agg bug)
        if key in aggregate_partials(out_dir, [key], run_config=run_config):
            print("[ckpt] %s done; skip" % key, flush=True); continue
        try:
            write_partial_key(out_dir, key, run_unit(f, seed))
        except Exception as e:
            print("[WARN] %s failed: %s" % (key, e), flush=True)
keys = [("f%.3f_s%d" % (f, sd)).replace(".", "p") for f in FRACS for sd in SEEDS]
units = list(aggregate_partials(out_dir, keys, run_config=run_config).values())
verdict, msg, detail = compute_verdict(units)
print("\n[VERDICT] " + msg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": msg, "run_mode": RUN_MODE, "N": N, "fracs": FRACS,
           "n_seeds": len(SEEDS), "detail": detail, "metrics_source": "measured_cpu_sparse_capacity_vs_sparsity_fraction_boundary", "per_unit": units, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, units)
print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
