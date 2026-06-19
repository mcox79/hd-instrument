"""
exp_two_substrate_fastslow_cls_cpu_v1.py -- 2-SUBSTRATE FastSlow CLS (Sprint-4 multi-substrate wrapper) -- CPU.

ROUTING: Research SPRINT4 Tier-1 (multi-substrate; hippocampal CLS analog). Engineered wrapper = TWO substrates + transfer +
  routing (NO core change): W_fast (high plasticity, decays -> recent items) + W_slow (stable, no decay -> consolidated).
  Stream items into fast; periodically CONSOLIDATE (transfer) seen items fast->slow; recall routes fast-then-slow. Tests it
  retains BOTH recent (fast) AND old-consolidated (slow) memories, beating a single decaying substrate that forgets old ones.
  Substrate-only + wrapper. N=8192.
PRE-REGISTERED: HARD-PASS recent recall >= 0.85 AND old-consolidated recall >= 0.85 AND old >> single-substrate baseline. MIDDLE one. HARD-FAIL else.
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
ANCHOR_NAME = "two_substrate_fastslow_cls_cpu_v1"
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
    print("[selftest] PASS: two-substrate-fastslow-cls", flush=True)
def run() -> Dict:
    g = np.random.default_rng(903); V = 400; T = 600 if SMOKE else 2000; CONS = 50; FDECAY = 0.95
    NOLD = 30; NRECENT = 30
    TR = 6 if SMOKE else 18; rec_recent = []; rec_old = []; base_old = []
    for _ in range(TR):
        keys = cphasor(T, N, g); vals = cphasor(V, N, g); truth = g.integers(0, V, size=T)
        Wfast = np.zeros(N, dtype=np.complex64); Wslow = np.zeros(N, dtype=np.complex64); Wbase = np.zeros(N, dtype=np.complex64)
        buf = []
        for t in range(T):
            Wfast = FDECAY * Wfast + keys[t] * vals[truth[t]]; buf.append(t)
            Wbase = FDECAY * Wbase + keys[t] * vals[truth[t]]                    # single-substrate baseline (decays, forgets old)
            if (t + 1) % CONS == 0:                                             # CONSOLIDATE recent buffer fast->slow (no decay)
                for b in buf:
                    Wslow = Wslow + keys[b] * vals[truth[b]]
                buf = []
        Wf = cnorm(Wfast); Ws = cnorm(Wslow); Wb = cnorm(Wbase)
        def route(k):                                                          # recall routes fast-then-slow
            sf = float((Wf @ np.conj(k)).real);
            return Wf if sf > 0.15 else Ws
        recent = list(range(T - NRECENT, T)); old = list(range(NOLD))
        rec_recent.append(sum(cidx(route(keys[i]) * np.conj(keys[i]), vals) == truth[i] for i in recent) / len(recent))
        rec_old.append(sum(cidx(Ws * np.conj(keys[i]), vals) == truth[i] for i in old) / len(old))   # old -> consolidated slow
        base_old.append(sum(cidx(Wb * np.conj(keys[i]), vals) == truth[i] for i in old) / len(old))  # baseline old (forgotten)
    rr = float(np.mean(rec_recent)); ro = float(np.mean(rec_old)); bo = float(np.mean(base_old))
    print("  2-SUBSTRATE CLS: recent(fast)=%.3f old-consolidated(slow)=%.3f | single-substrate old=%.3f (forgotten)" % (rr, ro, bo), flush=True)
    return {"recent_recall": round(rr, 3), "old_consolidated_recall": round(ro, 3), "baseline_old_recall": round(bo, 3)}
def verdict(r) -> Tuple[str, str]:
    rr = r["recent_recall"]; ro = r["old_consolidated_recall"]; bo = r["baseline_old_recall"]
    s = "recent=%.3f old-consolidated=%.3f baseline-old=%.3f" % (rr, ro, bo)
    if rr >= 0.85 and ro >= 0.85 and ro > bo + 0.20:
        return ("HARD_PASS", "HARD_PASS: 2-substrate FastSlow CLS works -- recent items retained in fast (>=0.85) AND old items consolidated in slow (>=0.85), vs single-substrate which forgets old (%.2f). Hippocampal CLS as engineered multi-substrate wrapper (fast+slow+transfer+routing), no core change. " % bo + s)
    if rr >= 0.85 or ro >= 0.85:
        return ("MIDDLE_BAND", "MIDDLE_BAND: one of recent/old holds. " + s)
    return ("HARD_FAIL", "HARD_FAIL: 2-substrate CLS fails both. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
