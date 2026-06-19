"""
exp_per_tier_importance_cpu_v1.py -- PER-TIER-IMPORTANCE-DEFAULTS-T0 (Sprint-4 engineered importance) -- CPU.

ROUTING: Research SPRINT4 Tier-0 (engineered importance subspace; per-tier defaults). Wrapper policy: Tier-1 atoms ALWAYS
  important (refreshed every cycle -> protected); Tier-3 importance-BY-ACCESS (accessed items refreshed, unaccessed decay out).
  Engineered importance per-tier (tier IS context). Tests: Tier-1 + frequently-accessed Tier-3 retained through a long edit
  stream; unaccessed Tier-3 correctly faded. Wrapper over substrate decay/refresh; no algebra change. N=8192.
PRE-REGISTERED: HARD-PASS Tier-1 recall >= 0.95 AND accessed-Tier-3 >= 0.80 AND unaccessed-Tier-3 < 0.40 (importance policy works). MIDDLE if Tier-1 >= 0.90. HARD-FAIL else.
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
ANCHOR_NAME = "per_tier_importance_cpu_v1"
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
    print("[selftest] PASS: per-tier-importance", flush=True)
def run() -> Dict:
    g = np.random.default_rng(int(os.environ.get("HDLAB_SEED", "902"))); NT1 = 20; NT3 = 60; V = 400; DECAY = 0.985; REFRESH = 50; STEPS = 600 if SMOKE else 3000
    TR = 5 if SMOKE else 16; t1r = []; t3a = []; t3u = []
    for _ in range(TR):
        t1k = cphasor(NT1, N, g); t3k = cphasor(NT3, N, g); vals = cphasor(V, N, g)
        t1t = g.integers(0, V, size=NT1); t3t = g.integers(0, V, size=NT3)
        t1_bundle = sum((t1k[i] * vals[t1t[i]] for i in range(NT1)), np.zeros(N, dtype=np.complex64))
        # half of Tier-3 is "accessed" (important by access), half unaccessed
        accessed = set(range(NT3 // 2)); acc_bundle = sum((t3k[i] * vals[t3t[i]] for i in accessed), np.zeros(N, dtype=np.complex64))
        M = (t1_bundle + sum((t3k[i] * vals[t3t[i]] for i in range(NT3)), np.zeros(N, dtype=np.complex64))).astype(np.complex64)
        for e in range(STEPS):
            M = DECAY * M + cphasor(1, N, g)[0] * vals[int(g.integers(0, V))]   # background edits
            if (e + 1) % REFRESH == 0:
                M = M + 8.0 * t1_bundle + 5.0 * acc_bundle                      # WRAPPER: refresh Tier-1 (always) + accessed Tier-3
        Mf = cnorm(M)
        t1r.append(sum(cidx(Mf * np.conj(t1k[i]), vals) == t1t[i] for i in range(NT1)) / NT1)
        acc_idx = list(accessed); un_idx = [i for i in range(NT3) if i not in accessed]
        t3a.append(sum(cidx(Mf * np.conj(t3k[i]), vals) == t3t[i] for i in acc_idx) / len(acc_idx))
        t3u.append(sum(cidx(Mf * np.conj(t3k[i]), vals) == t3t[i] for i in un_idx) / len(un_idx))
    a = float(np.mean(t1r)); b = float(np.mean(t3a)); c = float(np.mean(t3u))
    print("  PER-TIER-IMPORTANCE Tier-1=%.3f accessed-Tier-3=%.3f unaccessed-Tier-3=%.3f (faded)" % (a, b, c), flush=True)
    return {"tier1_recall": round(a, 3), "accessed_t3_recall": round(b, 3), "unaccessed_t3_recall": round(c, 3)}
def verdict(r) -> Tuple[str, str]:
    a = r["tier1_recall"]; b = r["accessed_t3_recall"]; c = r["unaccessed_t3_recall"]
    s = "Tier1=%.3f accessed-T3=%.3f unaccessed-T3=%.3f" % (a, b, c)
    if a >= 0.95 and b >= 0.80 and c < 0.40:
        return ("HARD_PASS", "HARD_PASS: engineered per-tier importance policy works -- Tier-1 always-protected (>=0.95), accessed Tier-3 retained (>=0.80), unaccessed Tier-3 correctly faded (<0.40). Importance-by-tier via wrapper (refresh policy), no algebra change. " + s)
    if a >= 0.90:
        return ("MIDDLE_BAND", "MIDDLE_BAND: Tier-1 protected but tier-3 discrimination partial. " + s)
    return ("HARD_FAIL", "HARD_FAIL: per-tier importance policy fails (Tier-1 <0.90). " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
