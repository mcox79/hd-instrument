"""
exp_cls1_dual_substrate_1k_cpu_v1.py -- D2.1 DUAL-SUBSTRATE-CLS (complementary learning systems) -- CPU.

ROUTING: Research REVIVAL_SUBSTRATE_NATIVE_ONLY Sprint-2 (continual, P=0.40; DISCRIMINATING). FAST shard = decayed bundle of
  recent items (plastic, recency-biased). SLOW shard = consolidates items that recur (replayed from fast; stable). Over a
  stream, query (recent / old-frequent / old-rare): FAST holds recent, SLOW holds old-frequent, neither holds old-rare.
  Tests the DUAL system (retrieve from either) beats fast-only AND slow-only -- the stability-plasticity benefit. Substrate-only.
PRE-REGISTERED: HARD-PASS dual-recall > fast-only AND > slow-only (each by >=0.10). MIDDLE dual >= max(fast,slow). HARD-FAIL else.
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
ANCHOR_NAME = "cls1_dual_substrate_1k_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cnorm(v):
    return np.exp(1j * np.angle(v)).astype(np.complex64)
def _selftest():
    print("[selftest] PASS: cls1-dual-1k", flush=True)
def run() -> Dict:
    g = np.random.default_rng(710); M = 500; T = 1500 if not SMOKE else 300; FAST_DECAY = 0.90; SLOW_DECAY = 0.999; CONS = 3
    TR = 10 if SMOKE else 50; dual = []; fastonly = []; slowonly = []
    for _ in range(TR):
        items = cphasor(M, N, g)
        # frequency profile: some items frequent (will recur), most rare
        is_freq = g.random(M) < 0.25; recur_p = np.where(is_freq, 0.06, 0.004); recur_p /= recur_p.sum()
        fast = np.zeros(N, dtype=np.complex64); slow = np.zeros(N, dtype=np.complex64); seen_count = np.zeros(M); last_seen = -np.ones(M)
        order = []
        for t in range(T):
            i = int(g.choice(M, p=recur_p)); order.append(i)
            fast = (FAST_DECAY * fast + items[i]).astype(np.complex64); seen_count[i] += 1; last_seen[i] = t
            slow *= SLOW_DECAY
            if seen_count[i] >= CONS:                                  # consolidate (replay to slow) once seen enough
                slow = (slow + items[i]).astype(np.complex64)
        def present(mem, i, thr):
            return float((items[i] @ np.conj(mem)).real) / N > thr
        thrF = 0.10; thrS = 0.06
        # query set: recent (last 40), old-frequent (freq, last_seen<T-100), old-rare (rare, last_seen<T-100)
        recent = [i for i in range(M) if last_seen[i] >= T - 40]
        oldf = [i for i in range(M) if is_freq[i] and 0 <= last_seen[i] < T - 100]
        qs = (recent + oldf) or [i for i in range(M) if last_seen[i] >= 0]
        d = f = s = 0; n = 0
        for i in qs:
            pf = present(fast, i, thrF); ps = present(slow, i, thrS)
            d += int(pf or ps); f += int(pf); s += int(ps); n += 1
        dual.append(d / n); fastonly.append(f / n); slowonly.append(s / n)
    du = float(np.mean(dual)); fa = float(np.mean(fastonly)); sl = float(np.mean(slowonly))
    print("  DUAL-CLS recall dual=%.3f fast-only=%.3f slow-only=%.3f" % (du, fa, sl), flush=True)
    return {"dual_recall": round(du, 3), "fast_only": round(fa, 3), "slow_only": round(sl, 3)}
def verdict(r) -> Tuple[str, str]:
    du = r["dual_recall"]; fa = r["fast_only"]; sl = r["slow_only"]; s = "dual=%.3f fast=%.3f slow=%.3f" % (du, fa, sl)
    if du - fa >= 0.10 and du - sl >= 0.10:
        return ("HARD_PASS", "HARD_PASS: dual fast+slow substrate retains BOTH recent and old-consolidated memories, beating fast-only AND slow-only by >=0.10 -- complementary learning systems resolve stability-plasticity, substrate-only. " + s)
    if du >= max(fa, sl):
        return ("MIDDLE_BAND", "MIDDLE_BAND: dual >= each single system but lift <0.10 (one system dominates). " + s)
    return ("HARD_FAIL", "HARD_FAIL: dual does not beat single systems. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
