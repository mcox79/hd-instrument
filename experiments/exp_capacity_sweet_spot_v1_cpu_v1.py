"""
capacity_sweet_spot_v1_cpu_v1 -- LEVER #1.5 (v1 = f-SELECTION only, projection->v2 per Skunkworks NOD). A runtime
OPERATING-POINT SELECTOR that auto-selects value-sparsity f from MEASURED target_alpha via the cited sparse alpha_c(f)
curve (a3f473dd). Additive reversible flag (C1). MEASURE-validated on an AUTO-ASSOC sparse-recall regression-set. CPU.

NOD (Skunkworks): v1 = f-only. projection DEFERRED to v2 (mean-center DE-SPARSIFIES k-of-N patterns -> incompatible with
sparse auto-assoc; the smoke caught it; v2 needs #7 learned-projection on DENSE keys + a heteroassoc crowded-key harness).
4 CONDITIONS baked in:
  1. All 3 arms PROJECTION-FREE (apples-to-apples f): default=dense f=1.0; naive=fixed f=0.05; selector=f-by-load. CAN-fail = pure f-adaptivity.
  2. Genuine earn-keep = f-adaptivity at HIGH LOAD: full N=8192 includes a discriminating task where fixed-f=0.05 (alpha_c=1.0)
     FAILS but selector's load-matched f (e.g. 0.01, alpha_c>=6.0) SUCCEEDS. (N=1024 smoke can't show it -- confirms mechanics only.)
  3. TIER = data-decides-no-preempt (chain-grade-CANDIDATE; grade = whatever N=8192 earns).
  4. alpha_c_by_f from cited atom a3f473dd (capped = LOWER BOUND, used conservatively) + seed-CV note in the verdict.

honest_claim: "v1 auto-selects sparsity f from measured target_alpha via cited alpha_c(f) (a3f473dd); f-adaptivity beats a
fixed-f default at loads beyond the fixed-f's capacity; no-recall-degrade vs unflagged dense default; falls back
(INSUFFICIENT_INPUT) out-of-envelope. Projection-routing DEFERRED to v2. N-pinned."  C1 reversible flag. ASCII. CPU.
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

ANCHOR_NAME = "capacity_sweet_spot_v1_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 1024 if SMOKE else 8192
SEEDS = [1] if SMOKE else [1, 2, 3]
THRESH = 0.10                                          # selector must beat BOTH baselines by >=10% absolute recall (f-adaptivity earn-keep)
FLIP = 0.05
NAIVE_F = 0.05                                         # the naive fixed-sparsity heuristic (alpha_c(0.05)=1.0)
# CITED alpha_c(f) curve from sparse super-capacity atom a3f473dd (condition 4; capped = LOWER BOUND):
ALPHA_C_BY_F = {1.0: 0.02, 0.5: 0.05, 0.2: 0.2, 0.1: 0.4, 0.05: 1.0, 0.02: 3.0, 0.01: 6.0, 0.005: 6.0}
CAPPED_F = {0.01, 0.005}                              # alpha_c hit LOADS max -> lower bound (use conservatively)
F_CHOICES = [1.0, 0.5, 0.2, 0.1, 0.05, 0.02, 0.01]    # least->most sparse (selector picks LARGEST f meeting the margin)
ALPHA_ENVELOPE_MAX = 6.0                              # target_alpha beyond this -> INSUFFICIENT_INPUT (out of measured envelope)


def select_f(target_alpha):
    """f-only selector: pick LARGEST f (least sparse=simplest) whose cited alpha_c(f) gives >=2x margin over target_alpha.
    capped alpha_c = lower-bound -> still safe to require >=2x (conservative). INSUFFICIENT_INPUT beyond envelope -> default dense."""
    if target_alpha is None or target_alpha > ALPHA_ENVELOPE_MAX:
        return {"status": "INSUFFICIENT_INPUT", "f": 1.0}                     # fallback to DEFAULT (dense)
    f_sel = None
    for f in F_CHOICES:
        if ALPHA_C_BY_F[f] >= 2.0 * target_alpha:
            f_sel = f                                                        # keep largest f meeting margin (F_CHOICES descending)
    if f_sel is None:
        f_sel = min(F_CHOICES)
    return {"status": "OK", "f": f_sel}


def _sparse_pat(M, n, f, g):
    k = max(1, int(f * n)); P = np.zeros((M, n), np.float32)
    for i in range(M):
        idx = g.choice(n, k, replace=False); P[i, idx] = g.integers(0, 2, k) * 2 - 1
    return P


def recall_at(target_alpha, f, n, seed):
    """AUTO-ASSOC sparse recall at sparsity f, load target_alpha (matches cited atom a3f473dd; W-free non-zero recall, chunked)."""
    g = np.random.default_rng(seed); M = max(2, int(target_alpha * n))
    P = _sparse_pat(M, n, f, g)
    diag = (P * P).sum(0); s = P.copy()
    for i in range(M):
        nz = np.nonzero(P[i])[0]; fl = nz[g.random(len(nz)) < FLIP]; s[i, fl] *= -1
    correct = 0; CHUNK = 2048
    for a in range(0, M, CHUNK):
        b = min(a + CHUNK, M)
        rc = np.sign((s[a:b] @ P.T) @ P - s[a:b] * diag)
        for i in range(a, b):
            nz = np.nonzero(P[i])[0]
            if len(nz) and np.all(rc[i - a][nz] == P[i][nz]):
                correct += 1
    return correct / M


def _selftest():
    assert select_f(0.1)["f"] >= select_f(1.5)["f"], "higher load -> sparser (smaller f)"
    assert select_f(12.0)["status"] == "INSUFFICIENT_INPUT", "out-of-envelope -> fallback"
    assert recall_at(0.1, 0.05, 512, 0) >= 0.9, "sparse low-load (alpha 0.1 << alpha_c(0.05)=1.0) recalls"
    print("[selftest] PASS: f-only selector(load->f, envelope->fallback) + auto-assoc recall", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)

# Regression-set: vary target_alpha (load) so the selector must ADAPT f. + a fallback-trigger task (condition 3 R3).
# highload tasks (1.5, 3.0): fixed-f=0.05 (alpha_c=1.0) FAILS, selector's load-matched f SUCCEEDS (condition 2 -- needs N=8192).
TASKS = [
    {"name": "lowload", "target_alpha": 0.10},
    {"name": "midload", "target_alpha": 0.50},
    {"name": "highload_DISC", "target_alpha": 1.50},     # fixed-f0.05 fails (>alpha_c 1.0); selector picks f0.01 (alpha_c>=6) -> earn-keep
    {"name": "veryhigh_DISC", "target_alpha": 3.00},     # fixed-f0.05 fails harder; selector f0.01 (alpha_c>=6 >= 6) at the edge
    {"name": "out_of_envelope_FALLBACK", "target_alpha": 12.0},
]
if SMOKE:
    TASKS = [TASKS[0], TASKS[2], TASKS[4]]


def run_unit(task, seed):
    name, ta = task["name"], task["target_alpha"]
    eff_ta = ta if ta <= ALPHA_ENVELOPE_MAX else ALPHA_ENVELOPE_MAX
    rec_default = recall_at(eff_ta, 1.0, N, seed)                            # arm (a) known-bad-default: dense f=1.0, projection-free
    rec_naive = recall_at(eff_ta, NAIVE_F, N, seed)                          # arm (b) naive-fixed f=0.05, projection-free
    sel = select_f(ta); rec_sel = recall_at(eff_ta, sel["f"], N, seed)       # arm (c) selector f-by-load
    insufficient = sel["status"] == "INSUFFICIENT_INPUT"
    fallback_ok = (not insufficient) or (abs(rec_sel - rec_default) < 0.02)  # fallback -> selector==default config
    print("  [%s s=%d ta=%.2f] sel_f=%.3f(%s) | rec: default=%.3f naive(f%.2f)=%.3f SELECTOR=%.3f | fallback_ok=%s" %
          (name, seed, ta, sel["f"], sel["status"], rec_default, NAIVE_F, rec_naive, rec_sel, fallback_ok), flush=True)
    return {"task": name, "seed": seed, "target_alpha": ta, "sel_f": sel["f"], "status": sel["status"],
            "rec_default": round(rec_default, 4), "rec_naive": round(rec_naive, 4), "rec_selector": round(rec_sel, 4),
            "insufficient": bool(insufficient), "fallback_ok": bool(fallback_ok), "run_mode": RUN_MODE}


def compute_verdict(units) -> Tuple[str, str, Dict]:
    if not units: return ("HARD_FAIL", "no results", {})
    by = {}
    for u in units:
        by.setdefault(u["task"], []).append(u)
    per = {}; sel_cv = {}
    for t, us in by.items():
        rs = [u["rec_selector"] for u in us]
        per[t] = {"target_alpha": us[0]["target_alpha"], "sel_f": us[0]["sel_f"], "status": us[0]["status"],
                  "rec_default": float(np.mean([u["rec_default"] for u in us])), "rec_naive": float(np.mean([u["rec_naive"] for u in us])),
                  "rec_selector": float(np.mean(rs)), "fallback_ok": all(u["fallback_ok"] for u in us)}
        sel_cv[t] = float(np.std(rs) / (np.mean(rs) + 1e-9))                 # condition 4: seed-CV (HARD_PASS must not be seed-noise)
    no_degrade = all(d["rec_selector"] >= d["rec_default"] - 0.02 for d in per.values())
    fallback_demo = all(d["fallback_ok"] for d in per.values())
    disc = {t: d for t, d in per.items() if d["status"] == "OK"}
    beats_default = {t: d["rec_selector"] - d["rec_default"] for t, d in disc.items()}
    beats_naive = {t: d["rec_selector"] - d["rec_naive"] for t, d in disc.items()}
    n_beats_both = sum(1 for t in disc if beats_default[t] >= THRESH and beats_naive[t] >= THRESH)
    worst_cv = max(sel_cv.values()) if sel_cv else 0.0
    detail = {"per_task": per, "no_degrade": bool(no_degrade), "fallback_demonstrated": bool(fallback_demo),
              "n_tasks_selector_beats_both": n_beats_both, "beats_default": {t: round(v, 3) for t, v in beats_default.items()},
              "beats_naive": {t: round(v, 3) for t, v in beats_naive.items()}, "selector_seed_cv": {t: round(v, 3) for t, v in sel_cv.items()},
              "worst_seed_cv": round(worst_cv, 3),
              "honest_claim": "v1 f-only selector picks sparsity f from measured target_alpha via cited alpha_c(f) (a3f473dd); "
                              "f-adaptivity beats fixed-f=%.2f on %d task(s) by >=%.0f%%; no-degrade=%s; fallback-demonstrated=%s; "
                              "worst seed-CV=%.3f. Projection DEFERRED to v2. TIER=data-decides." % (NAIVE_F, n_beats_both, THRESH*100, no_degrade, fallback_demo, worst_cv)}
    summary = "beats_both %d/%d disc | beats_default=%s beats_naive=%s | no_degrade=%s fallback=%s worst_cv=%.3f" % (
        n_beats_both, len(disc), detail["beats_default"], detail["beats_naive"], no_degrade, fallback_demo, worst_cv)
    if not fallback_demo:
        return ("HARD_FAIL", "HARD_FAIL: fallback NOT demonstrated. " + summary, detail)
    if not no_degrade:
        return ("HARD_FAIL", "HARD_FAIL: selector DEGRADES vs unflagged dense default (C1 no-degrade violated). " + summary, detail)
    if n_beats_both >= 2 and worst_cv < 0.15:
        return ("HARD_PASS", "HARD_PASS (chain-grade candidate -> Skunkworks rules; data-decides): f-adaptivity beats BOTH dense-default AND fixed-f by >=10% on >=2 high-load tasks, no-degrade, fallback, seed-robust (CV<0.15). The cited alpha_c(f) selection EARNS its keep. " + summary, detail)
    if n_beats_both >= 1:
        return ("MIDDLE_BAND", "MIDDLE_BAND: f-adaptivity earns keep on 1 task (not >=2) or seed-CV high. " + summary, detail)
    return ("MEASURED_MECHANISM", "MEASURED_MECHANISM: selector no-degrades + falls back but does NOT beat fixed-f=%.2f by >=10% (a fixed sparse default suffices -- f-adaptivity adds little at these loads). Honest CAN-fail outcome. " % NAIVE_F + summary, detail)


print("[config] %s mode=%s N=%d tasks=%d seeds=%s (v1 f-only, projection->v2)" % (ANCHOR_NAME, RUN_MODE, N, len(TASKS), SEEDS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); run_config = {"run_mode": RUN_MODE}; t0 = time.time()
for task in TASKS:
    for seed in SEEDS:
        key = ("%s_s%d" % (task["name"], seed)).replace(".", "p")
        if key in aggregate_partials(out_dir, [key], run_config=run_config):
            print("[ckpt] %s done; skip" % key, flush=True); continue
        try:
            write_partial_key(out_dir, key, run_unit(task, seed))
        except Exception as e:
            print("[WARN] %s failed: %s" % (key, e), flush=True)
keys = [("%s_s%d" % (t["name"], sd)).replace(".", "p") for t in TASKS for sd in SEEDS]
units = list(aggregate_partials(out_dir, keys, run_config=run_config).values())
verdict, msg, detail = compute_verdict(units)
print("\n[VERDICT] " + msg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": msg, "run_mode": RUN_MODE, "N": N, "n_tasks": len(TASKS),
           "n_seeds": len(SEEDS), "detail": detail, "metrics_source": "measured_cpu_f_selection_operating_point_selector", "per_unit": units, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, units)
print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
