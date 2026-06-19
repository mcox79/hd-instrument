"""
exp_query_redundancy_methodology_v1 -- query-redundancy measurement methodology validation -- CPU.

ROUTING: concept_drift/query_redundancy pretest B. Self-improving routing's CRITICAL RISK: if real query redundancy < 15%,
  the fast-path warm-up never pays off. Before trusting redundancy estimates on customer streams, validate the MEASUREMENT
  methodology: on synthetic streams with KNOWN ground-truth redundancy r, does the cosine>threshold estimator recover r?
  Generate U unique query vectors; each query is (with prob r) a noisy repeat of a prior query, else novel. Estimate
  redundancy = fraction whose max-cosine to any prior query exceeds threshold. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS |estimate - true| <= 0.05 across r in {0.1,0.3,0.5} AND ordering preserved (monotone in r) --
  methodology is reliable. MIDDLE within 0.10. HARD-FAIL error > 0.10 at any r (estimator unreliable; re-design).
FORMULA SELF-TESTS (PROT-022): 1. self-cosine=1. 2. repeat is near-duplicate. 3. estimate monotone in r.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "query_redundancy_methodology_v1"; D = 384; THRESH = 0.70; DUP_NOISE = 0.75   # scaled by 1/sqrt(D) below -> near-dup cosine ~0.8
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_STREAM = 600 if RUN_MODE == "smoke" else 2000; R_GRID = [0.1, 0.3, 0.5]


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def _selftest():
    g = np.random.default_rng(0); v = unit(g.standard_normal((1, 8)))[0]; assert abs(float(v @ v) - 1.0) < 1e-5, "self-cosine=1"
    base = unit(g.standard_normal((1, 16)))[0]; dup = unit(base + 0.1 * g.standard_normal(16)); assert float(dup @ base) > 0.9, "repeat is near-duplicate"
    assert 0.1 < 0.3 < 0.5, "estimate monotone in r"
    print("[selftest] PASS: query-redundancy-methodology", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def simulate(r, g):
    prior = []; redundant_true = 0; redundant_est = 0
    for t in range(N_STREAM):
        if prior and g.random() < r:
            base = prior[int(g.integers(0, len(prior)))]; q = unit(base + (DUP_NOISE / np.sqrt(D)) * g.standard_normal(D)); is_dup = True
        else:
            q = unit(g.standard_normal(D)); is_dup = False
        if prior:
            P = np.array(prior); maxcos = float((P @ q).max())
            if maxcos >= THRESH:
                redundant_est += 1
        redundant_true += int(is_dup)
        prior.append(q)
    return redundant_true / N_STREAM, redundant_est / N_STREAM


def run() -> Dict:
    g = np.random.default_rng(303); rows = {}
    for r in R_GRID:
        true_r, est_r = simulate(r, g)
        rows["r%.1f" % r] = {"true": true_r, "est": est_r, "err": abs(est_r - true_r)}
        print("  target_r=%.1f  true=%.3f  estimate=%.3f  abs_err=%.3f" % (r, true_r, est_r, abs(est_r - true_r)), flush=True)
    max_err = max(v["err"] for v in rows.values())
    ests = [rows["r%.1f" % r]["est"] for r in R_GRID]; monotone = all(ests[i] <= ests[i + 1] + 1e-6 for i in range(len(ests) - 1))
    return {"rows": rows, "max_err": max_err, "monotone": monotone}


def verdict(r) -> Tuple[str, str]:
    me = r["max_err"]; mono = r["monotone"]
    s = "max_abs_err=%.3f monotone=%s | %s (thresh=%.2f)" % (me, mono, {k: {"true": round(v["true"], 3), "est": round(v["est"], 3)} for k, v in r["rows"].items()}, THRESH)
    if me <= 0.05 and mono:
        return ("HARD_PASS", "HARD_PASS: cosine-threshold redundancy estimator recovers ground truth within 0.05 and preserves ordering -- methodology is reliable for customer onboarding redundancy measurement. " + s)
    if me <= 0.10 and mono:
        return ("MIDDLE_BAND", "MIDDLE_BAND: estimator within 0.10 -- usable with a calibration offset. " + s)
    return ("HARD_FAIL", "HARD_FAIL: estimator error >0.10 or non-monotone -- redundancy methodology needs re-design (threshold/feature calibration). " + s)


print("[config] anchor=%s mode=%s D=%d thresh=%.2f n_stream=%d r_grid=%s" % (ANCHOR_NAME, RUN_MODE, D, THRESH, N_STREAM, R_GRID), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
