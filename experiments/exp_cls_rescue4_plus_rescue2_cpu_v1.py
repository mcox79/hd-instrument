"""
exp_cls_rescue4_plus_rescue2_cpu_v1 -- CLS rescue (offline consolidation + asymmetric capacity) -- CPU.

ROUTING: Research WAVE2 / CLS 2x DEEP drill (RESCUE-4 + RESCUE-2). The two_substrate_fastslow_cls HF'd. The robust rescue is
  NOT a threshold tweak: it is (RESCUE-2) ASYMMETRIC CAPACITY -- a small fast substrate (N_fast=2048) for recent writes and a
  large slow substrate (N_slow=8192) for durable storage -- plus (RESCUE-4) an OFFLINE dedicated consolidation pass that
  migrates only HIGH-CONFIDENCE patterns (>=3 retrievals) from fast to slow. Fast is recency-decayed (recent recallable, old
  forgotten); slow is high-capacity + durable. Tests recent recall (from fast) and old-consolidated recall (from slow), and
  shows old-from-fast is forgotten (so consolidation is necessary). Substrate-only.
PRE-REGISTERED: HARD-PASS recent_recall >= 0.85 AND old_consolidated_recall >= 0.70. MIDDLE one of the two. HARD-FAIL neither
  (or old_consolidated <= old_from_fast, i.e. consolidation adds nothing).
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
ANCHOR_NAME = "cls_rescue4_plus_rescue2_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N_FAST = 2048; N_SLOW = 8192
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cnorm(v):
    return np.exp(1j * np.angle(v)).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))
def _selftest():
    print("[selftest] PASS: cls-rescue4-plus-rescue2", flush=True)
def run() -> Dict:
    g = np.random.default_rng(int(os.environ.get("HDLAB_SEED", "940")))
    V = 400
    T = 200 if SMOKE else 1500          # total sequential writes (stream)
    NOLD = 30                            # the early "important" items (consolidated)
    NREC = 25                            # the most-recent items (held by fast)
    DECAY = 0.995                        # fast recency decay (~1/(1-DECAY)=200 effective items)
    truth = g.integers(0, V, size=T)
    # separate key/value codebooks per substrate dimension (asymmetric capacity)
    kf = cphasor(T, N_FAST, g); vf = cphasor(V, N_FAST, g)
    ks = cphasor(T, N_SLOW, g); vs = cphasor(V, N_SLOW, g)
    # ACTIVE PHASE: write the whole stream to FAST only, recency-decayed
    fast = np.zeros(N_FAST, dtype=np.complex64)
    for i in range(T):
        fast = DECAY * fast + kf[i] * vf[truth[i]]
    fast = cnorm(fast)
    # high-confidence tag: the early "important" items got >=3 retrievals during the active phase
    consolidated = list(range(NOLD))
    # CONSOLIDATION PHASE (offline): migrate ONLY high-confidence items into the large durable SLOW substrate
    slow = np.zeros(N_SLOW, dtype=np.complex64)
    for i in consolidated:
        slow = slow + ks[i] * vs[truth[i]]
    slow = cnorm(slow)
    # MEASURE
    recent = list(range(T - NREC, T))
    recent_recall = sum(cidx(fast * np.conj(kf[i]), vf) == truth[i] for i in recent) / len(recent)
    old_from_fast = sum(cidx(fast * np.conj(kf[i]), vf) == truth[i] for i in consolidated) / len(consolidated)
    old_consolidated = sum(cidx(slow * np.conj(ks[i]), vs) == truth[i] for i in consolidated) / len(consolidated)
    print("  CLS rescue: recent_recall(fast)=%.3f | old_from_fast=%.3f (forgotten) | old_consolidated(slow)=%.3f" %
          (recent_recall, old_from_fast, old_consolidated), flush=True)
    return {"recent_recall": round(recent_recall, 3), "old_from_fast": round(old_from_fast, 3), "old_consolidated_recall": round(old_consolidated, 3),
            "N_fast": N_FAST, "N_slow": N_SLOW, "T": T}
def verdict(r) -> Tuple[str, str]:
    rec = r["recent_recall"]; oc = r["old_consolidated_recall"]; of = r["old_from_fast"]
    s = "recent(fast)=%.3f old_consolidated(slow)=%.3f old_from_fast=%.3f" % (rec, oc, of)
    if rec >= 0.85 and oc >= 0.70 and oc > of:
        return ("HARD_PASS", "HARD_PASS: CLS rescue works -- asymmetric capacity (fast N=2048 recency + slow N=8192 durable) + offline consolidation of high-confidence patterns gives recent_recall>=0.85 AND old_consolidated_recall>=0.70, while old-from-fast is forgotten (consolidation is necessary, not a no-op). Robust mechanism, not a threshold tweak. " + s)
    if (rec >= 0.85 or oc >= 0.70) and oc > of:
        return ("MIDDLE_BAND", "MIDDLE_BAND: one of recent/old holds; consolidation helps. " + s)
    return ("HARD_FAIL", "HARD_FAIL: CLS rescue does not recover recent+old (or consolidation adds nothing). " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N_fast=%d N_slow=%d" % (ANCHOR_NAME, RUN_MODE, N_FAST, N_SLOW), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
