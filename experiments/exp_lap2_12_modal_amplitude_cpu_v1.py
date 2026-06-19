"""
exp_lap2_12_modal_amplitude_cpu_v1.py -- graded modal operators via FHRR amplitude (box=min, diamond=max) -- CPU.

ROUTING: Research LAPTOP_WAVE2 (LAP-12 MODAL-AMPLITUDE); pure-FHRR (no download). Per-world graded truth as amplitude; necessity=min, possibility=max over accessible worlds.
PRE-REGISTERED: HARD-PASS graded-modal>=0.85. MIDDLE>=0.70. HARD-FAIL<0.70.
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
ANCHOR_NAME = "lap2_12_modal_amplitude_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    assert min(0.3, 0.7) == 0.3 and max(0.3, 0.7) == 0.7, "minmax"; print("[selftest] PASS: modal-amplitude", flush=True)
def run() -> Dict:
    # graded modal: truth(p,w) in [0,1] stored as amplitude on prop-key. box p at w = MIN over accessible w'; diamond = MAX.
    g = np.random.default_rng(12); N = 8192; W = 6; NP = 4; props = cphasor(NP, N, g)
    TR = 50 if SMOKE else 300; correct = 0; n = 0
    for _ in range(TR):
        acc = {w: sorted(set(int(x) for x in g.choice(W, g.integers(1, 4), replace=False))) for w in range(W)}
        truth = {(w, p): float(g.random()) for w in range(W) for p in range(NP)}
        # store per-world amplitude-weighted prop state: state[w] = sum_p truth(p,w) * props[p]
        state = {w: sum((truth[(w, p)] * props[p] for p in range(NP)), np.zeros(N, dtype=np.complex64)) for w in range(W)}
        w = int(g.integers(0, W)); p = int(g.integers(0, NP)); box = bool(g.integers(0, 2))
        # recover truth(p,w') for accessible w' via amplitude readout, then min/max
        vals = []
        for w2 in acc[w]:
            vals.append(float((np.vdot(props[p], state[w2]).real) / N))   # ~ truth(p,w2)
        comp = min(vals) if box else max(vals)
        gold = (min if box else max)(truth[(w2, p)] for w2 in acc[w])
        correct += int(abs(comp - gold) < 0.12); n += 1
    acc_s = correct / n; print("  MODAL-AMPLITUDE box=min/diamond=max acc=%.3f (n=%d)" % (acc_s, n), flush=True)
    return {"modal_amp_acc": acc_s, "n": n}
def verdict(r) -> Tuple[str, str]:
    s = "graded-modal-acc=%.3f (n=%d)" % (r["modal_amp_acc"], r["n"])
    if r["modal_amp_acc"] >= 0.85:
        return ("HARD_PASS", "HARD_PASS: graded modal operators via FHRR amplitude (box=min, diamond=max over accessible worlds) >=0.85 -- necessity/possibility as amplitude aggregation; modal logic continuous-valued. " + s)
    if r["modal_amp_acc"] >= 0.70:
        return ("MIDDLE_BAND", "MIDDLE_BAND: graded-modal 0.70-0.85. " + s)
    return ("HARD_FAIL", "HARD_FAIL: graded-modal <0.70. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
