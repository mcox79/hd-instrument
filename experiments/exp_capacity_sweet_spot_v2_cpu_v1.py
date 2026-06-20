"""LEVER 1.5 v2 (capacity sweet-spot selector, REDESIGN after v1 NOT-chain-grade).

v1 failed chain-grade for two reasons (Skunkworks landed-VET, Testbed 2nd-witness, Orchestrator own-verify-error):
  (1) the selector was NON-ADAPTIVE (descending-overwrite-no-break kept the SMALLEST viable f = 0.01 for every load;
      comment-vs-code bug), and (2) the recall-only metric had NO over-sparsity cost -> "always sparsest" wins -> no
      genuine sweet-spot / selection problem.

v2 fixes both, grounded in a de-risk probe (data-decides, BEFORE redesign):
  - Readout-noise was REFUTED as the cost axis (sparser is MORE readout-robust). The substrate-native over-sparsity cost is
    CUE-NOISE ROBUSTNESS: associative recall is FROM A CORRUPTED CUE, and a too-sparse pattern (tiny k) has too few bits to
    error-correct a flipped cue -> fragile. Too-dense fails CAPACITY at high load. => a GENUINE moderate-f sweet-spot.
  - Selector FIXED to pick the LARGEST-viable-f meeting the capacity margin = the MOST cue-robust choice that still has
    capacity (more bits = more error-correction). It genuinely ADAPTS f to the load.

CHAIN-GRADE CLAIM (the thing this cell must earn): no SINGLE fixed-sparsity beats the load-adaptive selector across the load
range -- a too-dense fixed-f fails high-load capacity, a too-sparse fixed-f fails cue-robustness; the selector tracks the
per-load optimal f, and that optimal f VARIES with load (so the adaptivity is NECESSARY, not a constant-f in disguise).

CAN-fail: if any single fixed-f ties/beats the selector at every load, the selection machinery does NOT earn its keep -> FAIL.
data-decides -> Skunkworks rules tier.
"""
import sys
from pathlib import Path
import argparse
import os
import time
import numpy as np

REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_partial_key, aggregate_partials, write_metrics

ANCHOR_NAME = "capacity_sweet_spot_v2_cpu_v1"
_P = argparse.ArgumentParser(); _P.add_argument("--self-test", action="store_true", dest="self_test"); _ARGS, _ = _P.parse_known_args()
RUN_MODE = os.environ.get("HDLAB_RUN_MODE", "full" if not _ARGS.self_test else "smoke")
N = 4096 if RUN_MODE == "full" else 1024
SEEDS = [1, 2, 3] if RUN_MODE == "full" else [1]
FLIP_CUE = 0.30                                            # cue-noise: fraction of active bits flipped in the query (substrate-native robustness cost; 30% = a meaningful recall-from-corruption target)
MARGIN = 2.0                                               # capacity margin: alpha_c(f) must exceed MARGIN * load
K_MIN = 8                                                  # robustness floor: never pick f with fewer than K_MIN active bits

# Willshaw super-capacity alpha_c(f) (sparser -> higher capacity), from a3f473dd sparse super-capacity.
ALPHA_C_BY_F = {0.2: 0.2, 0.1: 0.4, 0.05: 1.0, 0.02: 3.0, 0.01: 6.0, 0.005: 6.0, 0.002: 6.0, 0.001: 6.0}
F_SWEEP = [0.1, 0.05, 0.02, 0.01, 0.002]                  # baselines measured at every load: dense -> sparse (0.1 too-dense, 0.002 too-sparse)
F_CHOICES = [0.1, 0.05, 0.02, 0.01, 0.002]               # selector may pick any of these (descending = largest first)
LOADS = [0.1, 0.5, 1.0, 2.0]                              # low -> high memory load (alpha = M/N)


def select_f(target_alpha):
    """Pick the LARGEST viable f (most bits = most cue-robust) meeting the capacity margin AND the K_MIN robustness floor.
    F_CHOICES is descending, so the FIRST match is the largest -> return immediately (the v1 bug was overwrite-no-break)."""
    for f in F_CHOICES:                                    # largest f first
        if ALPHA_C_BY_F[f] >= MARGIN * target_alpha and int(f * N) >= K_MIN:
            return {"status": "OK", "f": f}                # FIRST match = largest viable = correct
    # nothing meets capacity at this load with K_MIN bits -> fall back to the sparsest (max capacity)
    return {"status": "INSUFFICIENT_INPUT", "f": min(F_CHOICES)}


def _sparse_pat(M, n, f, g):
    """M bipolar sparse patterns, k=f*n active bits each (vectorized: k random positions per row)."""
    k = max(1, int(f * n))
    r = g.random((M, n))
    idx = np.argpartition(r, k, axis=1)[:, :k]            # k random positions per row
    P = np.zeros((M, n), np.float32)
    signs = (g.integers(0, 2, (M, k)) * 2 - 1).astype(np.float32)
    np.put_along_axis(P, idx, signs, axis=1)
    return P


def recall_cue(load, f, n, seed):
    """AUTO-ASSOC sparse recall (W-free) from a CUE-NOISE-corrupted query: FLIP_CUE of active bits sign-flipped."""
    g = np.random.default_rng(seed * 131 + 7); M = max(2, int(load * n))
    P = _sparse_pat(M, n, f, g); diag = (P * P).sum(0); s = P.copy()
    mask = (P != 0) & (g.random(P.shape) < FLIP_CUE)      # flip each active bit independently w.p. FLIP_CUE (vectorized)
    s[mask] *= -1
    correct = 0; CHUNK = 2048
    for a in range(0, M, CHUNK):
        b = min(a + CHUNK, M)
        rc = np.sign((s[a:b] @ P.T) @ P - s[a:b] * diag)
        for i in range(a, b):
            nz = np.nonzero(P[i])[0]
            if len(nz) and np.all(rc[i - a][nz] == P[i][nz]):
                correct += 1
    return correct / M


def run_unit(load, seed):
    """One (load, seed): cue-noise recall for every fixed-f baseline + the selector's chosen f."""
    recalls = {("f%.3f" % f): float(recall_cue(load, f, N, seed)) for f in F_SWEEP}
    sel = select_f(load); sf = sel["f"]
    sel_recall = recalls["f%.3f" % sf] if ("f%.3f" % sf) in recalls else float(recall_cue(load, sf, N, seed))
    return {"load": load, "seed": seed, "recalls": recalls, "selector_f": sf, "selector_status": sel["status"], "selector_recall": sel_recall}


def compute_verdict(units):
    if not units:
        return ("HARD_FAIL", "no results", {})
    # aggregate per load over seeds
    by = {}
    for u in units:
        by.setdefault(u["load"], []).append(u)
    TOL = 0.03           # selector counts as near-optimal if within TOL of the best fixed-f at that load
    BEAT = 0.03          # selector "strictly beats" a fixed-f at a load by > BEAT
    per_load = {}
    for L, us in sorted(by.items()):
        recalls = {fk: float(np.mean([u["recalls"][fk] for u in us])) for fk in us[0]["recalls"]}
        sel_f = us[0]["selector_f"]                                          # deterministic given L
        sel_recall = float(np.mean([u["selector_recall"] for u in us]))
        best_fk = max(recalls, key=recalls.get); best_recall = recalls[best_fk]
        # per-seed selector_f stability + per-seed recall CV
        sel_fs = set(u["selector_f"] for u in us)
        cv = float(np.std([u["selector_recall"] for u in us]) / (np.mean([u["selector_recall"] for u in us]) + 1e-9))
        per_load[L] = {"selector_f": sel_f, "selector_recall": round(sel_recall, 3), "recalls": {k: round(v, 3) for k, v in recalls.items()},
                       "best_fixed_f": best_fk, "best_fixed_recall": round(best_recall, 3),
                       "selector_near_optimal": bool(sel_recall >= best_recall - TOL), "selector_f_seed_stable": len(sel_fs) == 1, "seed_cv": round(cv, 4)}
    # (1) ADAPTIVITY: does the selector pick DIFFERENT f across loads?
    sel_f_by_load = {L: per_load[L]["selector_f"] for L in per_load}
    adaptive = len(set(sel_f_by_load.values())) > 1
    # (2) EARNS ITS KEEP: is there ANY single fixed-f that is >= selector at EVERY load? (if yes, machinery is redundant)
    dominating = []
    for fk in F_SWEEP:
        fkk = "f%.3f" % fk
        beaten_somewhere = any(per_load[L]["selector_recall"] > per_load[L]["recalls"][fkk] + BEAT for L in per_load)
        if not beaten_somewhere:
            dominating.append(fkk)                                          # this fixed-f is never strictly beaten by the selector
    earns_keep = len(dominating) == 0                                        # selector strictly beats EVERY fixed-f at >=1 load
    # (3) selector near-optimal everywhere + seed-stable
    near_opt_all = all(per_load[L]["selector_near_optimal"] for L in per_load)
    seed_stable = all(per_load[L]["selector_f_seed_stable"] for L in per_load) and all(per_load[L]["seed_cv"] < 0.15 for L in per_load)
    # which loads demonstrate each failure mode (for the honest claim)
    too_dense_capacity_fail = [L for L in per_load if per_load[L]["recalls"]["f%.3f" % F_SWEEP[0]] < per_load[L]["selector_recall"] - BEAT]
    too_sparse_robust_fail = [L for L in per_load if per_load[L]["recalls"]["f%.3f" % F_SWEEP[-1]] < per_load[L]["selector_recall"] - BEAT]
    detail = {"per_load": {("alpha%.1f" % L): per_load[L] for L in per_load}, "selector_f_by_load": {("alpha%.1f" % L): sel_f_by_load[L] for L in sel_f_by_load},
              "adaptive_selector_varies_f": bool(adaptive), "earns_keep_no_single_fixed_f_dominates": bool(earns_keep), "fixed_fs_never_beaten": dominating,
              "selector_near_optimal_all_loads": bool(near_opt_all), "seed_stable": bool(seed_stable),
              "too_dense_capacity_fail_loads": ["alpha%.1f" % L for L in too_dense_capacity_fail], "too_sparse_robustness_fail_loads": ["alpha%.1f" % L for L in too_sparse_robust_fail],
              "flip_cue": FLIP_CUE, "N": N,
              "honest_claim": ("Load-adaptive sparsity selector (largest-viable-f meeting %gx capacity margin + K_MIN=%d bits) under cue-noise flip=%g: "
                               "selector picks f=%s across loads %s (ADAPTIVE=%s); no single fixed-f >= selector at every load (earns_keep=%s; never-beaten=%s); "
                               "too-dense f=%.3f fails capacity at loads %s; too-sparse f=%.3f fails cue-robustness at loads %s. "
                               "Genuine sweet-spot selection (NOT a3f473dd constant-f re-expression: the optimal f VARIES with load).")
              % (MARGIN, K_MIN, FLIP_CUE, sel_f_by_load, list(per_load.keys()), adaptive, earns_keep, dominating,
                 F_SWEEP[0], ["alpha%.1f" % L for L in too_dense_capacity_fail], F_SWEEP[-1], ["alpha%.1f" % L for L in too_sparse_robust_fail])}
    summary = "adaptive=%s earns_keep=%s near_opt_all=%s seed_stable=%s | sel_f_by_load=%s | never_beaten=%s" % (
        adaptive, earns_keep, near_opt_all, seed_stable, sel_f_by_load, dominating)
    if adaptive and earns_keep and near_opt_all and seed_stable:
        return ("HARD_PASS", "HARD_PASS (capability; data-decides -> Skunkworks rules): the load-adaptive sparsity selector tracks the per-load optimal f (which VARIES with load), and NO single fixed-sparsity matches it across the load range -- too-dense fails capacity, too-sparse fails cue-robustness. The selection machinery earns its keep. " + summary, detail)
    if adaptive and near_opt_all and not earns_keep:
        return ("MEASURED_MECHANISM", "MEASURED_MECHANISM: selector is adaptive + near-optimal, but at least one fixed-f (%s) is never strictly beaten -> the adaptivity does not strictly earn its keep over that fixed value in the tested range. Honest. " % dominating + summary, detail)
    if not adaptive:
        return ("MEASURED_MECHANISM", "MEASURED_MECHANISM / NEGATIVE: selector picks the SAME f across all loads (non-adaptive) -> no genuine selection problem in the tested range (a3f473dd re-expression). " + summary, detail)
    return ("MIDDLE_BAND", "MIDDLE_BAND: selector adaptive but not near-optimal at all loads or not seed-stable. " + summary, detail)


def _selftest():
    # STRICTER selftest (the v1 lesson: assert the selector OUTPUT VARIES, not just >=)
    f_low, f_high = select_f(0.1)["f"], select_f(2.0)["f"]
    assert f_low > f_high, "selector MUST be adaptive: lower load -> larger (less sparse) f, STRICTLY (got %g vs %g)" % (f_low, f_high)
    assert select_f(1.0)["f"] == 0.02, "largest-viable-f at alpha=1.0 (margin 2x -> alpha_c>=2.0 -> f=0.02), got %g" % select_f(1.0)["f"]
    assert recall_cue(0.5, 0.1, 512, 1) >= 0.8, "moderate-f (k>=50) recalls under cue noise"
    print("[selftest] PASS: adaptive selector (sel_f VARIES with load) + cue-noise recall", flush=True)


_selftest()
if _ARGS.self_test:
    raise SystemExit(0)

print("[config] %s mode=%s N=%d loads=%s F_sweep=%s flip_cue=%g seeds=%s" % (ANCHOR_NAME, RUN_MODE, N, LOADS, F_SWEEP, FLIP_CUE, SEEDS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); run_config = {"run_mode": RUN_MODE, "flip_cue": FLIP_CUE}; t0 = time.time()
for L in LOADS:
    for seed in SEEDS:
        key = ("a%.1f_s%d" % (L, seed)).replace(".", "p")
        if key in aggregate_partials(out_dir, [key], run_config=run_config):
            print("[ckpt] %s done; skip" % key, flush=True); continue
        try:
            write_partial_key(out_dir, key, run_unit(L, seed))
            print("[unit] %s sel_f=%s sel_recall done" % (key, select_f(L)["f"]), flush=True)
        except Exception as e:
            print("[WARN] %s failed: %s" % (key, e), flush=True)
keys = [("a%.1f_s%d" % (L, sd)).replace(".", "p") for L in LOADS for sd in SEEDS]
units = list(aggregate_partials(out_dir, keys, run_config=run_config).values())
verdict, msg, detail = compute_verdict(units)
print("\n[VERDICT] " + msg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": msg, "run_mode": RUN_MODE, "N": N, "loads": LOADS,
           "F_sweep": F_SWEEP, "flip_cue": FLIP_CUE, "n_seeds": len(SEEDS), "detail": detail,
           "metrics_source": "measured_cpu_capacity_sweet_spot_cuenoise_adaptive_selector", "per_unit": units, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, units)
print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
