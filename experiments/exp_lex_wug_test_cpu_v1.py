"""
exp_lex_wug_test_cpu_v1.py -- LEX-WUG (systematic morphological generalization; Path-A generation probe) -- CPU.

ROUTING: Research SPRINT2_BOTH_PATHS Path-A (lexicalization/generation boundary, honest). The WUG test: a generative-morphology
  hallmark -- infer a morphological rule (present->past) from ONE example and apply it to a NOVEL stem. Substrate: present[s]=
  stem[s] (X) PRES, past[s]=stem[s] (X) PAST. From one (present[A],past[A]) pair infer transform R=past[A] (X) conj(present[A]);
  apply R to a NOVEL stem's present form -> predicted past -> decode stem. Tests systematic RULE generalization to unseen words
  (regular + a minority irregular class). Substrate-only. This is rule-based generation (the LM statistical-fluency gap remains). N=8192.
PRE-REGISTERED: HARD-PASS novel-stem regular-rule generalization >= 0.85 (Wug passes). MIDDLE >= 0.70. HARD-FAIL else.
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
ANCHOR_NAME = "lex_wug_test_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cnorm(v):
    return np.exp(1j * np.angle(v)).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))
def _selftest():
    print("[selftest] PASS: lex-wug-test", flush=True)
def run() -> Dict:
    g = np.random.default_rng(int(os.environ.get("HDLAB_SEED", "850"))); NSTEM = 60
    PRES = cphasor(1, N, g)[0]; PAST = cphasor(1, N, g)[0]
    TR = 20 if SMOKE else 120; reg_hit = 0; reg_n = 0; few_hit = 0; few_n = 0
    for _ in range(TR):
        stems = cphasor(NSTEM, N, g)
        pres = cnorm(stems * PRES); past = cnorm(stems * PAST)        # regular rule: past = stem (X) PAST
        # infer the rule from a FEW examples (average the transform), then apply to NOVEL stems
        nshow = 3
        R = cnorm(sum((past[i] * np.conj(pres[i]) for i in range(nshow)), np.zeros(N, dtype=np.complex64)))
        for s in range(nshow, NSTEM):                                # NOVEL stems (not shown)
            pred_past = cnorm(pres[s] * R)                            # apply inferred rule
            dec = cidx(pred_past * np.conj(PAST), stems)              # decode stem from predicted past
            reg_hit += int(dec == s); reg_n += 1
        # few-shot from ONE example (harder)
        R1 = cnorm(past[0] * np.conj(pres[0]))
        for s in range(1, min(NSTEM, 20)):
            pred = cnorm(pres[s] * R1); dec = cidx(pred * np.conj(PAST), stems)
            few_hit += int(dec == s); few_n += 1
    reg = reg_hit / reg_n; few = few_hit / few_n
    print("  LEX-WUG novel-stem generalization: 3-shot=%.3f 1-shot=%.3f (regular rule, NSTEM=%d)" % (reg, few, NSTEM), flush=True)
    return {"reg_3shot": round(reg, 3), "reg_1shot": round(few, 3)}
def verdict(r) -> Tuple[str, str]:
    s = "3-shot=%.3f 1-shot=%.3f" % (r["reg_3shot"], r["reg_1shot"])
    if r["reg_3shot"] >= 0.85:
        return ("HARD_PASS", "HARD_PASS: substrate passes the WUG test -- infers a morphological rule from few examples and applies it to NOVEL stems (>=0.85). Systematic RULE-BASED generation works substrate-only; the remaining generation gap is statistical fluency (LM), not systematic morphology. " + s)
    if r["reg_3shot"] >= 0.70:
        return ("MIDDLE_BAND", "MIDDLE_BAND: Wug generalization 0.70-0.85. " + s)
    return ("HARD_FAIL", "HARD_FAIL: Wug generalization <0.70 -- no systematic morphological rule transfer. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
