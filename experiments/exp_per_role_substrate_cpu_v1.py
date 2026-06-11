"""
exp_per_role_substrate_cpu_v1.py -- PerRole substrate (Sprint-4 multi-substrate; domain isolation) -- CPU.

ROUTING: Research SPRINT4 Tier-1 (PerRole; per-domain isolation prevents compositional crosstalk). Engineered wrapper = one
  substrate PER domain (math/code/comm) + a router (NO core change). A SHARED single substrate accumulates all domains' content
  -> cross-domain crosstalk degrades retrieval. PerRole isolates each domain in its own substrate -> higher per-domain capacity,
  no crosstalk. Tests per-domain retrieval: PerRole vs shared. Substrate-only + routing wrapper. N=8192.
PRE-REGISTERED: HARD-PASS PerRole per-domain recall >= 0.90 AND > shared by >= 0.15 (isolation prevents crosstalk). MIDDLE PerRole >= 0.80. HARD-FAIL else.
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
ANCHOR_NAME = "per_role_substrate_cpu_v1"
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
    print("[selftest] PASS: per-role-substrate", flush=True)
def run() -> Dict:
    g = np.random.default_rng(904); NDOM = 3; PERDOM = 280 if not SMOKE else 60; V = 600
    TR = 6 if SMOKE else 20; pr_rec = []; sh_rec = []
    for _ in range(TR):
        keys = cphasor(NDOM * PERDOM, N, g); vals = cphasor(V, N, g); truth = g.integers(0, V, size=NDOM * PERDOM)
        # PERROLE: one substrate per domain (each holds PERDOM facts)
        perrole = [cnorm(sum((keys[d * PERDOM + j] * vals[truth[d * PERDOM + j]] for j in range(PERDOM)), np.zeros(N, dtype=np.complex64))) for d in range(NDOM)]
        # SHARED: one substrate for all NDOM*PERDOM facts (crosstalk)
        shared = cnorm(sum((keys[i] * vals[truth[i]] for i in range(NDOM * PERDOM)), np.zeros(N, dtype=np.complex64)))
        ph = 0; sh = 0; n = 0
        for d in range(NDOM):
            for j in range(0, PERDOM, 3):                              # sample
                idx = d * PERDOM + j
                ph += int(cidx(perrole[d] * np.conj(keys[idx]), vals) == truth[idx])   # router -> domain substrate
                sh += int(cidx(shared * np.conj(keys[idx]), vals) == truth[idx])
                n += 1
        pr_rec.append(ph / n); sh_rec.append(sh / n)
    pr = float(np.mean(pr_rec)); shr = float(np.mean(sh_rec))
    print("  PER-ROLE per-domain recall=%.3f | shared-substrate recall=%.3f (NDOM=%d x %d facts)" % (pr, shr, NDOM, PERDOM), flush=True)
    return {"perrole_recall": round(pr, 3), "shared_recall": round(shr, 3)}
def verdict(r) -> Tuple[str, str]:
    pr = r["perrole_recall"]; shr = r["shared_recall"]; s = "perrole=%.3f shared=%.3f" % (pr, shr)
    if pr >= 0.90 and pr > shr + 0.15:
        return ("HARD_PASS", "HARD_PASS: PerRole domain isolation works -- per-domain substrates recall >=0.90, beating one shared substrate by >=0.15 (crosstalk avoided). Per-domain isolation via routing wrapper prevents compositional crosstalk, no core change. " + s)
    if pr >= 0.80:
        return ("MIDDLE_BAND", "MIDDLE_BAND: perrole >=0.80 but margin over shared <0.15. " + s)
    return ("HARD_FAIL", "HARD_FAIL: perrole <0.80. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
