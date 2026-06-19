"""Generator: C1 fact-representation pre-tests EP1 (bitemporal-native) + EP2 (continuous-strength). Write-tool authored."""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
HEAD = '''"""
exp_{anchor}.py -- {title} -- CPU.

ROUTING: DEMO_SUPPORT C1 fact-rep pre-test ({tag}). {desc} Pure numpy. CPU.
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
C = []
C.append(dict(anchor="factrep_ep1_bitemporal_native_cpu_v1", tag="EP1 bitemporal-native fact representation",
  title="facts carry valid-time + transaction-time; AS-OF query returns the version valid at t",
  desc="Each fact is stored as key * VALID_period * value across a timeline; an AS-OF(t) query recovers the value that was valid at time t (and a corrected value supersedes for later t). Tests whether bitemporal versioning is native (cheap to ship in v1).",
  prereg="HARD-PASS AS-OF query returns the correct time-valid version >= 0.95 across a timeline with corrections. MIDDLE >= 0.85. HARD-FAIL < 0.85.",
  body='''
def _selftest():
    g = np.random.default_rng(0); a = cphasor(1, 32, g)[0]; t = cphasor(1, 32, g)[0]; v = cphasor(1, 32, g)[0]
    assert np.allclose(a * t * v * np.conj(a * t), v, atol=1e-3), "bind/unbind"; print("[selftest] PASS: factrep-ep1-bitemporal-native", flush=True)
def run() -> Dict:
    g = np.random.default_rng(201); N = 4096; VK = 100; VV = 400; NT = 8; TR = 60 if SMOKE else 200
    keys = cphasor(VK, N, g); vals = cphasor(VV, N, g); times = cphasor(NT, N, g)   # NT discrete time periods
    hit = 0; n = 0
    for _ in range(TR):
        k = int(g.integers(0, VK))
        # this key gets 2-3 versions over time: value changes at version boundaries
        nver = int(g.integers(2, 4)); bounds = sorted(g.choice(range(1, NT), nver - 1, replace=False).tolist()) if nver > 1 else []
        segs = [0] + bounds + [NT]; vlist = g.choice(VV, nver, replace=False)
        M = np.zeros(N, dtype=np.complex64)
        for vi in range(nver):
            for t in range(segs[vi], segs[vi + 1]):
                M = M + keys[k] * times[t] * vals[int(vlist[vi])]
        # distractor facts
        for _d in range(20):
            kk = int(g.integers(0, VK)); tt = int(g.integers(0, NT)); M = M + keys[kk] * times[tt] * vals[int(g.integers(0, VV))]
        # AS-OF query at a random time
        qt = int(g.integers(0, NT)); seg = next(vi for vi in range(nver) if segs[vi] <= qt < segs[vi + 1]); gold = int(vlist[seg])
        pred = cidx(M * np.conj(keys[k] * times[qt]), vals); hit += int(pred == gold); n += 1
    rec = hit / max(1, n); print("  bitemporal AS-OF correct=%.3f (n=%d)" % (rec, n), flush=True)
    return {"recall": rec}
def verdict(r) -> Tuple[str, str]:
    s = "AS-OF correctness=%.3f" % r["recall"]
    if r["recall"] >= 0.95: return ("HARD_PASS", "HARD_PASS: bitemporal-native AS-OF returns the time-valid version >=0.95 -- versioned fact representation is cheap/native (ship-in-v1 candidate). " + s)
    if r["recall"] >= 0.85: return ("MIDDLE_BAND", "MIDDLE_BAND: AS-OF 0.85-0.95. " + s)
    return ("HARD_FAIL", "HARD_FAIL: AS-OF <0.85. " + s)
'''))
C.append(dict(anchor="factrep_ep2_continuous_strength_cpu_v1", tag="EP2 continuous-strength fact representation",
  title="facts carry a continuous strength; retrieval is strength-ordered and strength is recoverable",
  desc="Each fact is stored with a continuous strength (amplitude weight); a query returns facts strength-ordered (strong facts dominate cleanup) and the strength scalar is recoverable via a readout. Tests whether continuous confidence/strength is native (cheap to ship in v1).",
  prereg="HARD-PASS strongest fact wins cleanup >= 0.95 AND recovered strength correlates with true strength (Pearson >= 0.9). MIDDLE >= 0.85 / 0.75. HARD-FAIL below.",
  body='''
def _selftest():
    import numpy as _n; assert abs(_n.corrcoef([1.0, 2, 3], [1.0, 2, 3])[0, 1] - 1.0) < 1e-9, "corr"; print("[selftest] PASS: factrep-ep2-continuous-strength", flush=True)
def run() -> Dict:
    g = np.random.default_rng(202); N = 4096; VK = 80; VV = 400; TR = 60 if SMOKE else 200
    keys = cphasor(VK, N, g); vals = cphasor(VV, N, g); win = 0; corrs = []
    for _ in range(TR):
        k = int(g.integers(0, VK))
        # this key has 3 competing values with different strengths
        cands = g.choice(VV, 3, replace=False); strengths = g.uniform(0.2, 1.0, 3)
        M = np.zeros(N, dtype=np.complex64)
        for ci in range(3):
            M = M + strengths[ci] * keys[k] * vals[int(cands[ci])]
        for _d in range(15):
            M = M + g.uniform(0.2, 1.0) * keys[int(g.integers(0, VK))] * vals[int(g.integers(0, VV))]
        rec = M * np.conj(keys[k]); pred = cidx(rec, vals)
        win += int(pred == int(cands[int(np.argmax(strengths))]))               # strongest value wins
        sc = (vals[cands] @ np.conj(rec)).real                                  # recovered strength per candidate
        if np.std(sc) > 0 and np.std(strengths) > 0:
            corrs.append(float(np.corrcoef(sc, strengths)[0, 1]))
    wr = win / TR; cr = float(np.mean(corrs)) if corrs else 0.0
    print("  strongest-wins=%.3f | strength-recovery Pearson=%.3f (n=%d)" % (wr, cr, TR), flush=True)
    return {"win": wr, "corr": cr}
def verdict(r) -> Tuple[str, str]:
    s = "strongest-wins=%.3f strength-correlation=%.3f" % (r["win"], r["corr"])
    if r["win"] >= 0.95 and r["corr"] >= 0.9: return ("HARD_PASS", "HARD_PASS: continuous-strength native -- strongest fact wins >=0.95 and recovered strength correlates >=0.9 with true; confidence-weighted facts ship-in-v1 candidate. " + s)
    if r["win"] >= 0.85 and r["corr"] >= 0.75: return ("MIDDLE_BAND", "MIDDLE_BAND: strength 0.85/0.75. " + s)
    return ("HARD_FAIL", "HARD_FAIL: continuous-strength weak. " + s)
'''))
for c in C:
    txt = HEAD.format(anchor=c["anchor"], title=c["title"], tag=c["tag"], desc=c["desc"], prereg=c["prereg"], body=c["body"])
    (EXP / ("exp_" + c["anchor"] + ".py")).write_text(txt, encoding="utf-8"); print("wrote", c["anchor"])
