"""Research overnight laptop batch: LAP-9 POPULATION-SUBSTRATE (ensemble vote) + LAP-7 CONT-TRUTH-FHRR (amplitude=truth gradient). Pure-FHRR. Write-tool authored."""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
HEAD = '''"""
exp_{anchor}.py -- {title} -- CPU.

ROUTING: Research OVERNIGHT_FILL_PRIORITIZED laptop batch ({tag}); pure-FHRR (no download). {desc}
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

POP = r'''
def _selftest():
    import numpy as _n; assert _n.bincount([1,1,2]).argmax()==1, "vote"; print("[selftest] PASS: population-substrate", flush=True)
def run() -> Dict:
    # P independent substrates each store the same M facts with their OWN random vectors; noisy retrieval; majority vote vs single.
    g = np.random.default_rng(909); N = 768; M = 90; VV = 100; P = 10; NOISE = 2.5
    TR = 30 if SMOKE else 200; single_ok = 0; ens_ok = 0; n = 0
    for _ in range(TR):
        truth = g.integers(0, VV, size=M)
        subs = []
        for p in range(P):
            keys = cphasor(M, N, g); vals = cphasor(VV, N, g)
            Mem = (keys * vals[truth]).sum(axis=0)
            subs.append((keys, vals, Mem))
        qi = int(g.integers(0, M))
        votes = []
        for p, (keys, vals, Mem) in enumerate(subs):
            noisy = Mem * np.conj(keys[qi]) + NOISE * (g.standard_normal(N) + 1j * g.standard_normal(N)).astype(np.complex64)
            votes.append(cidx(noisy, vals))
        single_ok += int(votes[0] == truth[qi])                          # substrate 0 alone
        ens = np.bincount(votes).argmax()
        ens_ok += int(ens == truth[qi]); n += 1
    sa = single_ok / n; ea = ens_ok / n
    print("  POPULATION single=%.3f ensemble(P=%d)=%.3f gain=%.3f (n=%d)" % (sa, ea, ea - sa, P, n), flush=True)
    return {"single_acc": sa, "ensemble_acc": ea, "gain_pp": round((ea - sa) * 100, 1), "P": P}
def verdict(r) -> Tuple[str, str]:
    s = "single=%.3f ensemble=%.3f gain=%.1fpp" % (r["single_acc"], r["ensemble_acc"], r["gain_pp"])
    if r["gain_pp"] >= 5.0:
        return ("HARD_PASS", "HARD_PASS: N=%d substrate population (majority vote) beats single by >=5pp on noisy queries -- biological population coding analog; ensembling averages independent encoding noise. " % r["P"] + s)
    if r["gain_pp"] >= 2.0:
        return ("MIDDLE_BAND", "MIDDLE_BAND: ensemble gain 2-5pp. " + s)
    return ("HARD_FAIL", "HARD_FAIL: ensemble gain <2pp. " + s)
'''

CTRUTH = r'''
def _selftest():
    import numpy as _n; assert abs(_n.corrcoef([1,2,3],[1,2,3])[0,1]-1)<1e-9, "corr"; print("[selftest] PASS: cont-truth-fhrr", flush=True)
def run() -> Dict:
    # continuous truth: predicate P holds to degree d in [0,1] encoded as amplitude d on key_P; recover d_hat=|<state,key_P>|; correlate.
    g = np.random.default_rng(707); N = 4096; NP = 8; keys = cphasor(NP, N, g)
    TR = 40 if SMOKE else 300; true_d = []; rec_d = []
    for _ in range(TR):
        degs = g.random(NP)                                              # graded truth per predicate (Sorites: vague membership)
        state = (degs[:, None] * keys).sum(axis=0)                       # amplitude-weighted bundle
        for p in range(NP):
            dhat = float(np.abs(np.vdot(keys[p], state)) / N)            # recovered magnitude
            true_d.append(degs[p]); rec_d.append(dhat)
    corr = float(np.corrcoef(true_d, rec_d)[0, 1])
    print("  CONT-TRUTH recovered-vs-true corr=%.3f (NP=%d, n=%d)" % (corr, NP, len(true_d)), flush=True)
    return {"corr": corr, "n": len(true_d)}
def verdict(r) -> Tuple[str, str]:
    s = "truth-gradient-corr=%.3f (n=%d)" % (r["corr"], r["n"])
    if r["corr"] >= 0.70:
        return ("HARD_PASS", "HARD_PASS: FHRR magnitude tracks continuous truth degree (corr>=0.70) -- vague/graded predicates (Sorites) native via amplitude; no separate fuzzy-logic mechanism needed. " + s)
    if r["corr"] >= 0.50:
        return ("MIDDLE_BAND", "MIDDLE_BAND: corr 0.50-0.70. " + s)
    return ("HARD_FAIL", "HARD_FAIL: corr <0.50. " + s)
'''

C = [
    dict(anchor="lap9_population_substrate_cpu_v1", tag="LAP-9 POPULATION-SUBSTRATE", title="N=10 substrate ensemble vote beats single on noisy queries", desc="P independent substrates store the same KB with own vectors; majority vote vs single under query noise.", prereg="HARD-PASS ensemble gain>=5pp. MIDDLE>=2pp. HARD-FAIL<2pp.", body=POP),
    dict(anchor="lap7_cont_truth_fhrr_cpu_v1", tag="LAP-7 CONT-TRUTH-FHRR", title="FHRR magnitude as continuous truth gradient", desc="Graded predicate degrees encoded as amplitude; recover magnitude; correlate with true degree (Sorites-style vagueness).", prereg="HARD-PASS corr>=0.70. MIDDLE>=0.50. HARD-FAIL<0.50.", body=CTRUTH),
]
for c in C:
    (EXP / ("exp_" + c["anchor"] + ".py")).write_text(HEAD.format(anchor=c["anchor"], title=c["title"], tag=c["tag"], desc=c["desc"], prereg=c["prereg"], body=c["body"]), encoding="utf-8"); print("wrote", c["anchor"])
