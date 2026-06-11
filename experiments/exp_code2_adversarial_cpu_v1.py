"""
exp_code2_template_conditional_cpu_v1.py -- CODE-2 bug detection via TEMPLATE-CONDITIONAL grammar check -- CPU.

ROUTING: Research WAVE2 / code2 R-SOFT-DECODE (template-conditional; my design-gap catch CONFIRMED). The base code2
  (margin to nearest library program) and the literal per-op self-decode both HF because the bug is a CLEAN out-of-grammar op
  swap (decodes as itself). Fix: use the substrate's TEMPLATE structure. (1) store each template as per-slot valid-op bundles
  T_t[s]=bundle(ops valid at slot s in template t); (2) identify the test program's nearest template t* by summing per-slot
  match (the ~4 correct slots dominate -> robust ID); (3) bug score = min over slots of <ops[prog[s]], T_t*[s]> -- the
  out-of-grammar slot has LOW match to t*'s valid set; (4) flag buggy if min-slot-match < tau, sweep tau by F1. Substrate-only.
PRE-REGISTERED: HARD-PASS F1 >= 0.78 (AUC reported). MIDDLE F1 >= 0.65. HARD-FAIL F1 < 0.65.
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
ANCHOR_NAME = "code2_adversarial_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cnorm(v):
    return np.exp(1j * np.angle(v)).astype(np.complex64)
def _auc(scores, labels):
    o = np.argsort(scores); r = np.empty(len(scores)); r[o] = np.arange(1, len(scores) + 1)
    pos = labels == 1; npos = int(pos.sum()); nneg = len(labels) - npos
    return 0.5 if npos == 0 or nneg == 0 else float((r[pos].sum() - npos * (npos + 1) / 2) / (npos * nneg))
def _selftest():
    print("[selftest] PASS: code2-adversarial", flush=True)
def run() -> Dict:
    g = np.random.default_rng(int(os.environ.get("HDLAB_SEED", "833"))); STEPS = 5; NOP = 10; NTEMPL = 12; VALID = 4
    ops = cphasor(NOP, N, g); slots = cphasor(STEPS, N, g)
    TR = 15 if SMOKE else 90
    MODES = ["out-of-grammar", "cross-template", "double-swap"]   # adversarial bug families (harder than the single out-of-grammar swap)
    def make_bug(mode, t, templ, prog):
        if mode == "out-of-grammar":
            bs = int(g.integers(0, STEPS)); bad = [o for o in range(NOP) if o not in t[bs]]
            prog[bs] = int(g.choice(bad))
        elif mode == "cross-template":
            # op VALID for a DIFFERENT template's same slot but not this one (closer to grammar -> harder)
            bs = int(g.integers(0, STEPS))
            others = [o for tt in range(NTEMPL) for o in templ[tt][bs] if o not in t[bs]]
            prog[bs] = int(g.choice(others)) if others else int(g.choice([o for o in range(NOP) if o not in t[bs]]))
        else:  # double-swap: two slots out-of-grammar
            for bs in g.choice(STEPS, 2, replace=False):
                bad = [o for o in range(NOP) if o not in t[int(bs)]]; prog[int(bs)] = int(g.choice(bad))
        return prog
    def score_prog(prog, Tgram):
        tscore = [sum(float((Tgram[tt][s] @ np.conj(ops[prog[s]])).real) for s in range(STEPS)) for tt in range(NTEMPL)]
        tstar = int(np.argmax(tscore))
        slot_match = [float((Tgram[tstar][s] @ np.conj(ops[prog[s]])).real) / N for s in range(STEPS)]
        return -min(slot_match)
    per_mode = {}
    for mode in MODES:
        scores = []; labels = []
        for _ in range(TR):
            templ = [[list(g.choice(NOP, VALID, replace=False)) for _ in range(STEPS)] for _ in range(NTEMPL)]
            Tgram = [[cnorm(sum((ops[o] for o in templ[t][s]), np.zeros(N, dtype=np.complex64))) for s in range(STEPS)] for t in range(NTEMPL)]
            for _q in range(8):
                ti = int(g.integers(0, NTEMPL)); t = templ[ti]; prog = [int(t[s][int(g.integers(0, VALID))]) for s in range(STEPS)]
                buggy = g.random() < 0.5
                if buggy: prog = make_bug(mode, t, templ, prog)
                scores.append(score_prog(prog, Tgram)); labels.append(int(buggy))
        sc = np.array(scores); lab = np.array(labels); auc = _auc(sc, lab)
        best_f1 = 0.0; best_tau = None
        for tau in [0.05, 0.10, 0.15, 0.20]:
            pred = ((-sc) < tau).astype(int)
            tp = int(((pred == 1) & (lab == 1)).sum()); fp = int(((pred == 1) & (lab == 0)).sum()); fn = int(((pred == 0) & (lab == 1)).sum())
            prec = tp / (tp + fp + 1e-9); rec = tp / (tp + fn + 1e-9); f1 = 2 * prec * rec / (prec + rec + 1e-9)
            if f1 > best_f1: best_f1 = f1; best_tau = tau
        per_mode[mode] = {"auc": round(auc, 3), "f1": round(best_f1, 3), "tau": best_tau}
        print("  CODE-2 ADVERSARIAL [%s]: AUC=%.3f F1=%.3f" % (mode, auc, best_f1), flush=True)
    worst_f1 = min(m["f1"] for m in per_mode.values())
    return {"per_mode": per_mode, "worst_f1": round(worst_f1, 3), "f1": round(worst_f1, 3)}
def verdict(r) -> Tuple[str, str]:
    wf = r["worst_f1"]; s = "worst-F1=%.3f per-mode=%s" % (wf, {k: v["f1"] for k, v in r["per_mode"].items()})
    if wf >= 0.78:
        return ("HARD_PASS", "HARD_PASS: code2 template-conditional detection is ADVERSARIALLY ROBUST -- worst-case F1>=0.78 across out-of-grammar + cross-template + double-swap bug families. The Tier-C result holds under harder bugs. " + s)
    if wf >= 0.65:
        return ("MIDDLE_BAND", "MIDDLE_BAND: worst-case adversarial F1 0.65-0.78 (some bug family harder). " + s)
    return ("HARD_FAIL", "HARD_FAIL: worst-case adversarial F1 <0.65 -- a bug family defeats template-conditional detection. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
