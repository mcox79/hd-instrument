"""
capacity_sweet_spot_v1_cpu_v1 -- LEVER #1.5: a runtime OPERATING-POINT SELECTOR that auto-selects substrate config
(value-sparsity f, key-projection on/off) from MEASURED-and-cited inputs (target_alpha, crosstalk-moment c), consuming the
cycle's cert atoms. Additive reversible flag (C1 protocol). MEASURE-validated on a KV-recall regression-set. CPU.

CONSUMES (verify-the-referent -- each selector input traces to a cert atom):
- sparse super-capacity alpha_c(f) curve (a3f473dd MEASURED_MECHANISM): {f1.0:0.02, 0.5:0.05, 0.2:0.2, 0.1:0.4, 0.05:1.0,
  0.02:3.0, 0.01:>=6.0[capped/lower-bound], 0.005:>=6.0[capped]}. capped = LOWER BOUND -> use alpha_c directly, NOT gain-multiple (amendment).
- crosstalk-law (7315be3c): high crosstalk-moment c on raw keys -> route through projection (de-crowd).

4 REFINEMENTS (Skunkworks SCHEMA-VET prereg v2):
- R1 TIER = data-decides-no-preempt: the selector earns its OWN grade from its CAN-fail/no-degrade result; CANNOT inherit chain-grade from inputs.
- R2 3-ARM CAN-fail: (a) known-bad-default, (b) NAIVE-FIXED heuristic, (c) measurement-driven SELECTOR. Selector must beat BOTH (a) AND (b) by >=THRESH; else "a fixed default suffices" (MEASURED_MECHANISM at most).
- R3 FALLBACK demonstrated: regression-set includes a task that TRIGGERS INSUFFICIENT_INPUT (alpha beyond envelope) -> recall==default, flag set, no crash.
- R4 v1 SCOPE = (f, projection) ONLY; tau, encoder held at defaults.
C1: reversible flag use_capacity_sweet_spot (default OFF). ASCII. CPU.
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
N = 1024 if SMOKE else 4096
SEEDS = [1] if SMOKE else [1, 2, 3]
THRESH = 0.10                                          # selector must beat BOTH baselines by >=10% absolute recall (R2)
C_PROJ_THRESH = 0.05                                   # crosstalk-moment c above this -> route through projection (de-crowd)
# CITED alpha_c(f) curve from sparse super-capacity atom a3f473dd (capped = lower-bound):
ALPHA_C_BY_F = {1.0: 0.02, 0.5: 0.05, 0.2: 0.2, 0.1: 0.4, 0.05: 1.0, 0.02: 3.0, 0.01: 6.0, 0.005: 6.0}
F_CHOICES = [1.0, 0.5, 0.2, 0.1, 0.05, 0.02, 0.01]    # least->most sparse (selector picks LARGEST f meeting the margin)
ALPHA_ENVELOPE_MAX = 6.0                              # beyond this target_alpha -> INSUFFICIENT_INPUT (out of measured envelope)


def select_config(target_alpha, c):
    """Operating-point selector: (f, projection) from MEASURED (target_alpha, c). Returns config or INSUFFICIENT_INPUT."""
    if target_alpha is None or c is None or target_alpha > ALPHA_ENVELOPE_MAX:
        return {"status": "INSUFFICIENT_INPUT", "f": 1.0, "projection": False}  # fallback to DEFAULT (dense, no proj)
    # f: pick LARGEST f (least sparse = simplest) whose alpha_c(f) gives >=2x margin over target_alpha (capped = lower-bound -> safe)
    f_sel = None
    for f in F_CHOICES:
        if ALPHA_C_BY_F[f] >= 2.0 * target_alpha:
            f_sel = f                                  # keep the largest f that still meets margin (F_CHOICES is descending)
    if f_sel is None:
        f_sel = min(F_CHOICES)                         # even the sparsest doesn't give 2x -> use sparsest (best available)
    proj = c > C_PROJ_THRESH                           # route through projection when keys are crowded
    return {"status": "OK", "f": f_sel, "projection": bool(proj)}


def _bsc(m, n, g):
    return (g.integers(0, 2, (m, n)) * 2 - 1).astype(np.float32)


def _sparse_vals(V, n, f, g):
    k = max(1, int(f * n)); out = np.zeros((V, n), np.float32)
    for i in range(V):
        idx = g.choice(n, k, replace=False); out[i, idx] = g.integers(0, 2, k) * 2 - 1
    return out


def kv_recall(target_alpha, c_level, f, projection, n, seed):
    """KV-recall task at config (f, projection): store M=alpha*N (key,value) pairs, recall value via cleanup. Returns recall@1."""
    g = np.random.default_rng(seed); M = max(2, int(target_alpha * n)); V = max(M, 64)
    # keys: c_level controls crowding (shared-mean cone). high c -> keys crowded (low capacity unless projected).
    base = _bsc(1, n, g)
    keys = _bsc(M, n, g) + c_level * base               # c_level * shared base -> crowding (raises crosstalk-moment)
    if projection:                                      # de-crowding projection proxy (mean-center -> removes shared cone; #7 is the learned production version)
        keys = keys - keys.mean(0, keepdims=True)
    keys = keys / (np.linalg.norm(keys, axis=1, keepdims=True) + 1e-8)
    book = _sparse_vals(V, n, f, g) if f < 1.0 else _bsc(V, n, g)
    vi = g.integers(0, V, M)
    B = np.zeros((n, n), np.float32)
    for j in range(M):
        B += np.outer(book[vi[j]], keys[j])             # heteroassoc store value<-key
    cor = 0
    for j in range(0, M, 512):
        q = keys[j:j + 512]; R = (q @ B.T)              # recall value-estimates (chunked)
        pred = np.argmax(R @ book.T, axis=1)
        cor += int((pred == vi[j:j + 512]).sum())
    return cor / M


def run_unit(task, seed):
    """task = (name, target_alpha, c_level). 3 arms: known-bad-default / naive-fixed / measurement-driven selector."""
    name, ta, c = task["name"], task["target_alpha"], task["c_level"]
    # arm (a) known-bad-default: dense f=1.0, no projection (the current unflagged default)
    rec_default = kv_recall(ta if ta <= ALPHA_ENVELOPE_MAX else ALPHA_ENVELOPE_MAX, c, 1.0, False, N, seed)
    # arm (b) naive-fixed heuristic: fixed f=0.05 + projection ON (a reasonable fixed guess, no measurement)
    rec_naive = kv_recall(ta if ta <= ALPHA_ENVELOPE_MAX else ALPHA_ENVELOPE_MAX, c, 0.05, True, N, seed)
    # arm (c) measurement-driven selector
    cfg = select_config(ta, c)
    eff_ta = ta if ta <= ALPHA_ENVELOPE_MAX else ALPHA_ENVELOPE_MAX
    rec_sel = kv_recall(eff_ta, c, cfg["f"], cfg["projection"], N, seed)
    insufficient = cfg["status"] == "INSUFFICIENT_INPUT"
    # fallback demo: on INSUFFICIENT_INPUT, selector == default config -> recall must match default (no crash, flag set)
    fallback_ok = (not insufficient) or (abs(rec_sel - rec_default) < 0.02)
    print("  [%s s=%d ta=%.2f c=%.2f] sel_cfg=(f=%.3f,proj=%s,%s) | rec: default=%.3f naive=%.3f SELECTOR=%.3f | fallback_ok=%s" %
          (name, seed, ta, c, cfg["f"], cfg["projection"], cfg["status"], rec_default, rec_naive, rec_sel, fallback_ok), flush=True)
    return {"task": name, "seed": seed, "target_alpha": ta, "c_level": c, "sel_f": cfg["f"], "sel_proj": cfg["projection"],
            "status": cfg["status"], "rec_default": round(rec_default, 4), "rec_naive": round(rec_naive, 4),
            "rec_selector": round(rec_sel, 4), "insufficient": bool(insufficient), "fallback_ok": bool(fallback_ok), "run_mode": RUN_MODE}


# Regression-set: vary (target_alpha, c) so the selector must ADAPT (f to load, projection to crowding). + a fallback-trigger task (R3).
TASKS = [
    {"name": "lowload_lowc", "target_alpha": 0.10, "c_level": 0.0},
    {"name": "highload_lowc", "target_alpha": 1.5, "c_level": 0.0},
    {"name": "highload_highc", "target_alpha": 1.5, "c_level": 2.0},
    {"name": "midload_highc", "target_alpha": 0.5, "c_level": 2.0},
    {"name": "out_of_envelope_FALLBACK", "target_alpha": 12.0, "c_level": 0.0},   # > ALPHA_ENVELOPE_MAX -> INSUFFICIENT_INPUT (R3 fallback demo)
]
if SMOKE:
    TASKS = [TASKS[0], TASKS[2], TASKS[4]]


def _selftest():
    # selector picks sparser f for higher load; projection on for high c; INSUFFICIENT_INPUT beyond envelope
    c_lo = select_config(0.1, 0.0); c_hi = select_config(1.5, 0.0)
    assert c_lo["f"] >= c_hi["f"], "higher load -> sparser (smaller f): %.3f vs %.3f" % (c_lo["f"], c_hi["f"])
    assert select_config(0.5, 2.0)["projection"] and not select_config(0.5, 0.0)["projection"], "projection routes on high c"
    assert select_config(12.0, 0.0)["status"] == "INSUFFICIENT_INPUT", "out-of-envelope -> fallback"
    g = np.random.default_rng(0)
    assert kv_recall(0.05, 0.0, 1.0, False, 256, 0) >= 0.9, "low-load dense recall works"
    print("[selftest] PASS: selector(load->f, c->proj, envelope->fallback) + kv_recall", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def compute_verdict(units) -> Tuple[str, str, Dict]:
    if not units: return ("HARD_FAIL", "no results", {})
    by = {}
    for u in units:
        by.setdefault(u["task"], []).append(u)
    per = {}
    for t, us in by.items():
        per[t] = {"target_alpha": us[0]["target_alpha"], "c_level": us[0]["c_level"], "sel_f": us[0]["sel_f"], "sel_proj": us[0]["sel_proj"],
                  "status": us[0]["status"], "rec_default": float(np.mean([u["rec_default"] for u in us])),
                  "rec_naive": float(np.mean([u["rec_naive"] for u in us])), "rec_selector": float(np.mean([u["rec_selector"] for u in us])),
                  "fallback_ok": all(u["fallback_ok"] for u in us)}
    # no-degrade: selector >= default on EVERY task (C1 no-recall-degrade -- vs the unflagged default arm)
    no_degrade = all(d["rec_selector"] >= d["rec_default"] - 0.02 for d in per.values())
    # R3 fallback demonstrated: the INSUFFICIENT_INPUT task fell back to default cleanly
    fallback_demo = all(d["fallback_ok"] for d in per.values())
    # R2 3-arm CAN-fail: on the DISCRIMINATING tasks (status OK, non-fallback), selector beats BOTH default AND naive by THRESH
    disc = {t: d for t, d in per.items() if d["status"] == "OK"}
    beats_default = {t: d["rec_selector"] - d["rec_default"] for t, d in disc.items()}
    beats_naive = {t: d["rec_selector"] - d["rec_naive"] for t, d in disc.items()}
    n_beats_both = sum(1 for t in disc if beats_default[t] >= THRESH and beats_naive[t] >= THRESH)
    selector_earns_keep = n_beats_both >= 1 and min(beats_naive.values(), default=-1) >= -0.02  # beats naive somewhere + never materially worse
    detail = {"per_task": per, "no_degrade": bool(no_degrade), "fallback_demonstrated": bool(fallback_demo),
              "n_tasks_selector_beats_both": n_beats_both, "beats_default": {t: round(v, 3) for t, v in beats_default.items()},
              "beats_naive": {t: round(v, 3) for t, v in beats_naive.items()}, "selector_earns_keep": bool(selector_earns_keep),
              "honest_claim": "Operating-point selector auto-picks (f, projection) from measured (target_alpha, c) [cited atoms]; "
                              "no-recall-degrade=%s vs unflagged default; fallback-on-INSUFFICIENT_INPUT demonstrated=%s; "
                              "beats-both-baselines on %d discriminating task(s). TIER = data-decides (earns own grade, no inherit)." % (no_degrade, fallback_demo, n_beats_both)}
    summary = "no_degrade=%s fallback_demo=%s | beats_both on %d/%d disc tasks | beats_default=%s beats_naive=%s" % (
        no_degrade, fallback_demo, n_beats_both, len(disc), detail["beats_default"], detail["beats_naive"])
    if not fallback_demo:
        return ("HARD_FAIL", "HARD_FAIL: fallback NOT demonstrated (INSUFFICIENT_INPUT task did not match default). " + summary, detail)
    if not no_degrade:
        return ("HARD_FAIL", "HARD_FAIL: selector DEGRADES recall vs unflagged default on some task (C1 no-degrade violated). " + summary, detail)
    if selector_earns_keep and n_beats_both >= 2:
        return ("HARD_PASS", "HARD_PASS (chain-grade candidate -> Skunkworks rules; data-decides): selector beats BOTH known-bad-default AND naive-fixed by >=10% on >=2 discriminating tasks, no-degrade, fallback demonstrated. The cited-atom selection EARNS its keep. " + summary, detail)
    if n_beats_both >= 1:
        return ("MIDDLE_BAND", "MIDDLE_BAND: selector beats both baselines on 1 task (not >=2); partial earn-keep. " + summary, detail)
    return ("MEASURED_MECHANISM", "MEASURED_MECHANISM: selector no-degrades + falls back, but does NOT beat the naive-fixed heuristic by >=10% (a fixed sparse default suffices -- the cited-atom machinery adds little). Honest CAN-fail outcome. " + summary, detail)


print("[config] %s mode=%s N=%d tasks=%d seeds=%s" % (ANCHOR_NAME, RUN_MODE, N, len(TASKS), SEEDS), flush=True)
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
           "n_seeds": len(SEEDS), "detail": detail, "metrics_source": "measured_cpu_operating_point_selector_3arm_canfail", "per_unit": units, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, units)
print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
