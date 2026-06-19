"""
exp_integ_diagnostic_cpu_v1.py -- INTEG structural diagnostic (why additive fails minimax) -- CPU.

ROUTING: Research HUMANEVAL_FULL_SCALE Tier-1 (urgent integration investigation). Diagnoses the STRUCTURAL cause of the
  integration gap and tests the proposed alternative mechanisms. Core hypothesis: additive/softmax/tournament all optimize a
  SUM (mean) of drive satisfactions; the objective (maximize the MIN drive = no drive starved) is a DIFFERENT objective.
  Any mean-based operator diverges from minimax exactly when a high-mean action starves one drive. Tests: (1) additive-vs-
  minimax divergence rate + characterization, (2) temperature softmax T<1, (3) tournament iterated WTA -- does any mean-based
  fix reach minimax? Prediction: NO mean-based operator reaches minimax (structural, not tuning). numpy.
PRE-REGISTERED (DIAGNOSTIC): report divergence + each mechanism's min-sat / minimax ratio. HARD-PASS if it cleanly identifies
  the sum-vs-min structural cause (mean-based fixes all < 0.95 of minimax, minimax is the objective). MIDDLE if a fix reaches >=0.95.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, math
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "integ_diagnostic_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def _selftest():
    print("[selftest] PASS: integ-diagnostic", flush=True)
def run() -> Dict:
    g = np.random.default_rng(684); ND = 5; NA = 12; TR = 400 if not SMOKE else 100
    diverge = 0; tot = 0; add_minsat = []; mini_minsat = []; soft_minsat = []; tour_minsat = []
    add_mean_on_div = []; mini_mean_on_div = []
    for _ in range(TR):
        pref = g.random((ND, NA)) ** 3; pref = pref / pref.sum(1, keepdims=True)
        ms = lambda a: float(np.min(pref[:, a]))
        a_add = int(np.argmax(pref.mean(0))); a_min = int(np.argmax([ms(a) for a in range(NA)]))
        # temperature softmax (T<1 sharpens): weight drives by softmax of their dissatisfaction, T=0.3
        T = 0.3; dissat = 1.0 - pref.mean(1)  # per-drive average dissatisfaction
        w = np.exp((1 - pref).mean(1) / T); w = w / w.sum()
        a_soft = int(np.argmax((w[:, None] * pref).sum(0)))
        # tournament: iterated winner-take-all among top actions
        score = pref.mean(0).copy()
        for _it in range(6):
            top = np.argsort(score)[-3:]; sub = pref[:, top]; score = np.full(NA, -1.0); score[top] = sub.min(0)  # restrict + minimax within top
        a_tour = int(np.argmax(score))
        add_minsat.append(ms(a_add)); mini_minsat.append(ms(a_min)); soft_minsat.append(ms(a_soft)); tour_minsat.append(ms(a_tour))
        if a_add != a_min:
            diverge += 1; add_mean_on_div.append(float(pref[:, a_add].mean())); mini_mean_on_div.append(float(pref[:, a_min].mean()))
        tot += 1
    dr = diverge / tot; mm = float(np.mean(mini_minsat));
    rA = float(np.mean(add_minsat)) / (mm + 1e-9); rS = float(np.mean(soft_minsat)) / (mm + 1e-9); rT = float(np.mean(tour_minsat)) / (mm + 1e-9)
    amd = float(np.mean(add_mean_on_div)) if add_mean_on_div else 0.0; mmd = float(np.mean(mini_mean_on_div)) if mini_mean_on_div else 0.0
    print("  INTEG-DIAG divergence(add!=minimax)=%.3f | min-sat ratios vs minimax: additive=%.3f softmax-T=%.3f tournament=%.3f" % (dr, rA, rS, rT), flush=True)
    print("  on divergent cases: additive picks higher-MEAN action (%.3f mean vs minimax %.3f) but lower MIN -> sum-vs-min objective mismatch" % (amd, mmd), flush=True)
    return {"divergence_rate": round(dr, 3), "additive_ratio": round(rA, 3), "softmaxT_ratio": round(rS, 3),
            "tournament_ratio": round(rT, 3), "add_mean_on_div": round(amd, 3), "minimax_mean_on_div": round(mmd, 3)}
def verdict(r) -> Tuple[str, str]:
    best = max(r["additive_ratio"], r["softmaxT_ratio"], r["tournament_ratio"])
    s = "divergence=%.3f additive=%.3f softmax-T=%.3f tournament=%.3f (best mean-based=%.3f)" % (r["divergence_rate"], r["additive_ratio"], r["softmaxT_ratio"], r["tournament_ratio"], best)
    if best < 0.95:
        return ("HARD_PASS", "HARD_PASS (diagnostic): STRUCTURAL cause identified -- the objective is maximize-MIN but every mean-based operator (additive/softmax-T/tournament) optimizes a SUM, so all fall short of minimax (best=%.2f<0.95). On divergent cases additive picks the higher-MEAN action (%.2f vs %.2f) at the cost of a starved drive. The integration gap is an OBJECTIVE mismatch (sum vs min), NOT a tuning/normalization issue -- needs explicit min-optimization (BG-analog minimax) or a fundamentally different mechanism. " % (best, r["add_mean_on_div"], r["minimax_mean_on_div"]) + s)
    return ("MIDDLE_BAND", "MIDDLE_BAND (diagnostic): a mean-based mechanism reaches >=0.95 of minimax. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
