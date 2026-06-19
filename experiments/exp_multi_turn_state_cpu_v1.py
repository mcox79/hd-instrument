"""
exp_multi_turn_state_cpu_v1.py -- dialogue slot-state accumulated across turns in a substrate bundle, recovered per slot -- CPU.

ROUTING: fast-cheap batch (TALKS-3 multi-turn conversation state). Conversation state as a single substrate bundle: each turn binds a SLOT role to its value and adds to the running state (later mentions of a slot supersede). After N turns, query each slot to recover its current value. Tests multi-turn state tracking. Pure numpy FHRR (sub-minute; all-or-nothing OK). CPU.
PRE-REGISTERED: HARD-PASS per-slot recall of current value >= 0.95 after multi-turn updates. MIDDLE >= 0.85. HARD-FAIL < 0.85.
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
ANCHOR_NAME = "multi_turn_state_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))
def topk(v, book, k):
    return set(np.argsort((book @ np.conj(v)).real)[::-1][:k].tolist())

def _selftest():
    g = np.random.default_rng(0); a = cphasor(1, 64, g)[0]; v = cphasor(1, 64, g)[0]; assert np.allclose(a*v*np.conj(a), v, atol=1e-3), "bind"; print("[selftest] PASS: multi-turn-state", flush=True)
def run() -> Dict:
    g = np.random.default_rng(801); N = 4096; NSLOT = 6; VV = 200; TR = 60 if SMOKE else 200
    slots = cphasor(NSLOT, N, g); vals = cphasor(VV, N, g); hit = 0; tot = 0
    for _ in range(TR):
        state = np.zeros(N, dtype=np.complex64); cur = {}
        turns = int(g.integers(6, 16))
        for _t in range(turns):
            sl = int(g.integers(0, NSLOT)); vv = int(g.integers(0, VV))
            if sl in cur:
                state = state - slots[sl] * vals[cur[sl]]          # supersede: remove old binding
            state = state + slots[sl] * vals[vv]; cur[sl] = vv
        for sl, vv in cur.items():
            hit += int(cidx(state * np.conj(slots[sl]), vals) == vv); tot += 1
    rec = hit / tot; print("  multi-turn slot recall=%.3f (n=%d slots queried)" % (rec, tot), flush=True)
    return {"recall": rec}
def verdict(r) -> Tuple[str, str]:
    s = "slot-recall=%.3f" % r["recall"]
    if r["recall"] >= 0.95: return ("HARD_PASS", "HARD_PASS: multi-turn conversation slot-state recovered >=0.95 (supersede-aware) -- dialogue state tracking works. " + s)
    if r["recall"] >= 0.85: return ("MIDDLE_BAND", "MIDDLE_BAND: slot-recall 0.85-0.95. " + s)
    return ("HARD_FAIL", "HARD_FAIL: slot-recall <0.85. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
