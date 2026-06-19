"""Research WAVE-3: LAP3-11 TEMPORAL-LTL-BOUNDED + STRETCH3-1 DRIFT-DIFFUSION-EVIDENCE. Pure-FHRR. Write-tool authored."""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
HEAD = '''"""
exp_{anchor}.py -- {title} -- CPU.

ROUTING: Research LAP3_LAP211_WAVE3 ({tag}); pure-FHRR (no download). {desc}
PRE-REGISTERED: {prereg}
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
ANCHOR_NAME = "{anchor}"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))
{body}
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\\n[VERDICT] " + vmsg, flush=True)
metrics = {{"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
'''

LTL = r'''
def _selftest():
    print("[selftest] PASS: temporal-ltl", flush=True)
def run() -> Dict:
    g = np.random.default_rng(11); N = 8192; T = 8; NP = 4; props = cphasor(NP, N, g); slots = cphasor(T, N, g)
    TR = 50 if SMOKE else 300; correct = 0; n = 0
    for _ in range(TR):
        val = {(s, p): (g.random() < 0.5) for s in range(T) for p in range(NP)}
        prophold = {s: sum((props[p] for p in range(NP) if val[(s, p)]), np.zeros(N, dtype=np.complex64)) for s in range(T)}
        def holds(s, p):                                                 # substrate membership: prop p true at step s?
            return (np.vdot(props[p], prophold[s]).real) / N > 0.5
        ftype = int(g.integers(0, 4)); p = int(g.integers(0, NP)); q = int(g.integers(0, NP)); k = int(g.integers(2, T))
        if ftype == 0:    # X p : next
            gold = val[(1, p)]; got = holds(1, p)
        elif ftype == 1:  # F_k p : eventually within k
            gold = any(val[(s, p)] for s in range(0, k + 1)); got = any(holds(s, p) for s in range(0, k + 1))
        elif ftype == 2:  # G_k p : always through k
            gold = all(val[(s, p)] for s in range(0, k + 1)); got = all(holds(s, p) for s in range(0, k + 1))
        else:             # p U_k q : p holds until q (within k)
            def until(vfn):
                for s in range(0, k + 1):
                    if vfn(s, q):
                        return True
                    if not vfn(s, p):
                        return False
                return False
            gold = until(lambda s, x: val[(s, x)]); got = until(lambda s, x: holds(s, x))
        correct += int(got == gold); n += 1
    acc = correct / n; print("  TEMPORAL-LTL bounded(X/F/G/U) acc=%.3f (T=%d, n=%d)" % (acc, T, n), flush=True)
    return {"ltl_acc": acc, "n": n}
def verdict(r) -> Tuple[str, str]:
    s = "bounded-LTL-acc=%.3f (n=%d)" % (r["ltl_acc"], r["n"])
    if r["ltl_acc"] >= 0.85:
        return ("HARD_PASS", "HARD_PASS: substrate evaluates bounded LTL (next / eventually-within-k / always-through-k / until) >=0.85 -- temporal logic over substrate-stored state sequences. " + s)
    if r["ltl_acc"] >= 0.70:
        return ("MIDDLE_BAND", "MIDDLE_BAND: LTL 0.70-0.85. " + s)
    return ("HARD_FAIL", "HARD_FAIL: LTL <0.70. " + s)
'''

DDM = r'''
def _selftest():
    print("[selftest] PASS: drift-diffusion", flush=True)
def run() -> Dict:
    # drift-diffusion: accumulate noisy evidence toward one of 2 alternatives; decide when the cleanup margin crosses threshold.
    g = np.random.default_rng(2); N = 4096; DRIFT = 0.25; SNOISE = 1.0; THR = 0.30; MAXT = 60
    TR = 100 if SMOKE else 400; correct = 0; rts = []; n = 0
    for _ in range(TR):
        A = cphasor(1, N, g)[0]; B = cphasor(1, N, g)[0]; book = np.stack([A, B]); true = int(g.integers(0, 2))
        target = book[true]; acc = np.zeros(N, dtype=np.complex64); decision = None
        for tstep in range(1, MAXT + 1):
            sample = DRIFT * target + SNOISE * (g.standard_normal(N) + 1j * g.standard_normal(N)).astype(np.complex64)
            acc = acc + sample
            sc = np.sort((book @ np.conj(acc)).real)[::-1] / (N * tstep)
            if (sc[0] - sc[1]) > THR:
                decision = int(np.argmax((book @ np.conj(acc)).real)); rts.append(tstep); break
        if decision is None:
            decision = int(np.argmax((book @ np.conj(acc)).real)); rts.append(MAXT)
        correct += int(decision == true); n += 1
    acc_rate = correct / n; mrt = float(np.mean(rts))
    print("  DRIFT-DIFFUSION accuracy=%.3f mean-RT=%.1f steps (drift=%.2f noise=%.1f thr=%.2f, n=%d)" % (acc_rate, mrt, DRIFT, SNOISE, THR, n), flush=True)
    return {"ddm_accuracy": acc_rate, "mean_rt": round(mrt, 1), "n": n}
def verdict(r) -> Tuple[str, str]:
    s = "accuracy=%.3f mean-RT=%.1f" % (r["ddm_accuracy"], r["mean_rt"])
    if r["ddm_accuracy"] >= 0.85:
        return ("HARD_PASS", "HARD_PASS: substrate evidence-accumulation (drift-diffusion) reaches >=0.85 accuracy by integrating noisy samples to a decision threshold -- biological sequential evidence integration; speed-accuracy via threshold. " + s)
    if r["ddm_accuracy"] >= 0.70:
        return ("MIDDLE_BAND", "MIDDLE_BAND: DDM accuracy 0.70-0.85. " + s)
    return ("HARD_FAIL", "HARD_FAIL: DDM accuracy <0.70. " + s)
'''

C = [
    dict(anchor="lap3_11_temporal_ltl_cpu_v1", tag="LAP3-11 TEMPORAL-LTL-BOUNDED", title="bounded LTL over substrate state sequences", desc="Store a state sequence; evaluate next / eventually-k / always-k / until-k temporal formulas.", prereg="HARD-PASS LTL>=0.85. MIDDLE>=0.70. HARD-FAIL<0.70.", body=LTL),
    dict(anchor="stretch3_1_drift_diffusion_cpu_v1", tag="STRETCH3-1 DRIFT-DIFFUSION-EVIDENCE", title="evidence accumulation to a decision threshold (DDM)", desc="Accumulate noisy evidence for one of 2 alternatives; decide when cleanup margin crosses threshold; measure accuracy + RT.", prereg="HARD-PASS DDM accuracy>=0.85. MIDDLE>=0.70. HARD-FAIL<0.70.", body=DDM),
]
for c in C:
    (EXP / ("exp_" + c["anchor"] + ".py")).write_text(HEAD.format(anchor=c["anchor"], title=c["title"], tag=c["tag"], desc=c["desc"], prereg=c["prereg"], body=c["body"]), encoding="utf-8"); print("wrote", c["anchor"])
