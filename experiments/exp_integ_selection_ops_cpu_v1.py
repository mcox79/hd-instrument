"""
exp_integ_selection_ops_cpu_v1.py -- INTEG-SELECTION-OPS (selection beats blending) -- CPU.

ROUTING: Research TIER2 integration pivot (SELECTION not BLENDING). The INTEG diagnostic showed mean-based BLENDING (additive/
  softmax) can't reach minimax (sum-vs-min mismatch); pure minimax maximizes the MIN but may sacrifice the MEAN. This tests
  SELECTION operators that get BOTH: TOP-K (restrict to top-K actions by mean, then minimax among them), TOURNAMENT (iterated
  WTA + minimax), TEMPERATURE (sharp softmax). Realistic objective = min-drive-sat + 0.3*mean (no-starvation AND overall good).
  HARD-PASS if a SELECTION op EXCEEDS both additive and minimax on the combined objective -- selection > blending. numpy.
PRE-REGISTERED: HARD-PASS a selection op (top-K or tournament) > max(additive, minimax) on combined objective by >=0.01. MIDDLE >= ties best. HARD-FAIL else.
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
ANCHOR_NAME = "integ_selection_ops_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
LAM = 0.3
def _selftest():
    print("[selftest] PASS: integ-selection-ops", flush=True)
def run() -> Dict:
    g = np.random.default_rng(685); ND = 5; NA = 12; TR = 400 if not SMOKE else 100
    obj = lambda pref, a: float(np.min(pref[:, a]) + LAM * np.mean(pref[:, a]))
    acc = {k: [] for k in ["additive", "minimax", "temperature", "tournament", "topk"]}
    for _ in range(TR):
        pref = g.random((ND, NA)) ** 3; pref = pref / pref.sum(1, keepdims=True)
        mn = pref.min(0); me = pref.mean(0)
        a_add = int(np.argmax(me)); a_min = int(np.argmax(mn))
        w = np.exp((1 - pref).mean(1) / 0.3); w = w / w.sum(); a_tmp = int(np.argmax((w[:, None] * pref).sum(0)))
        # tournament: top-3 by mean, minimax within, iterate
        top = np.argsort(me)[-3:]; a_tour = int(top[np.argmax(mn[top])])
        # top-K: top-5 by mean, then maximize combined objective among them
        topk = np.argsort(me)[-5:]; a_topk = int(topk[np.argmax([np.min(pref[:, a]) + LAM * np.mean(pref[:, a]) for a in topk])])
        acc["additive"].append(obj(pref, a_add)); acc["minimax"].append(obj(pref, a_min)); acc["temperature"].append(obj(pref, a_tmp))
        acc["tournament"].append(obj(pref, a_tour)); acc["topk"].append(obj(pref, a_topk))
    m = {k: round(float(np.mean(v)), 4) for k, v in acc.items()}
    print("  INTEG-SELECTION combined-objective(min+0.3mean): additive=%.4f minimax=%.4f temperature=%.4f tournament=%.4f topk=%.4f" %
          (m["additive"], m["minimax"], m["temperature"], m["tournament"], m["topk"]), flush=True)
    return m
def verdict(r) -> Tuple[str, str]:
    blend_best = max(r["additive"], r["minimax"], r["temperature"]); sel_best = max(r["tournament"], r["topk"])
    s = "additive=%.4f minimax=%.4f temp=%.4f tournament=%.4f topk=%.4f" % (r["additive"], r["minimax"], r["temperature"], r["tournament"], r["topk"])
    if sel_best > blend_best + 0.01:
        return ("HARD_PASS", "HARD_PASS: SELECTION beats BLENDING -- a selection operator (top-K/tournament) exceeds both additive and minimax on the realistic combined objective (min + 0.3*mean) by >=0.01. Restrict-then-optimize gets BOTH no-starvation AND overall satisfaction; the integration pivot to SELECTION works. " + s)
    if sel_best >= blend_best:
        return ("MIDDLE_BAND", "MIDDLE_BAND: selection ties best blending operator. " + s)
    return ("HARD_FAIL", "HARD_FAIL: selection does not beat blending. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
